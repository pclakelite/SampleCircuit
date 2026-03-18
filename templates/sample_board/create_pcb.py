"""
create_pcb.py — Build SampleBoard.kicad_pcb using pcbnew standalone Python.

Loads footprints from JLCImport.pretty, assigns nets from the exported netlist,
places components in functional groups on a 4" x 4" board.

Run with KiCad's Python:
  "C:/Program Files/KiCad/9.0/bin/python.exe" create_pcb.py
"""

import os
import re
import sys

# Must import pcbnew from KiCad's Python
import pcbnew

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
FP_LIB = os.path.join(PROJECT_ROOT, "JLCImport.pretty")
NETLIST_PATH = os.path.join(SCRIPT_DIR, "SampleBoard.net")
PCB_PATH = os.path.join(SCRIPT_DIR, "SampleBoard.kicad_pcb")

# Board dimensions: 4" x 4" = 101.6mm x 101.6mm
BOARD_ORIGIN_X = 100.0  # mm
BOARD_ORIGIN_Y = 50.0   # mm
BOARD_W = 101.6          # mm
BOARD_H = 101.6          # mm


def mm_to_nm(mm_val):
    """Convert mm to nanometers (KiCad internal unit)."""
    return int(mm_val * 1e6)


def parse_netlist(path):
    """Parse kicad sexpr netlist to extract components and nets.
    Returns:
      components: {ref: {value, footprint, tstamp}}
      nets: {net_name: [(ref, pin), ...]}
    """
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract components
    components = {}
    comp_pattern = re.compile(
        r'\(comp \(ref "([^"]+)"\)\s*'
        r'\(value "([^"]+)"\)\s*'
        r'\(footprint "([^"]+)"\)',
        re.DOTALL
    )
    for m in comp_pattern.finditer(content):
        ref, value, footprint = m.group(1), m.group(2), m.group(3)
        # Extract tstamp
        block_start = m.start()
        tstamp_m = re.search(r'\(tstamps "([^"]+)"\)', content[block_start:block_start+2000])
        tstamp = tstamp_m.group(1) if tstamp_m else ""
        components[ref] = {
            'value': value,
            'footprint': footprint,
            'tstamp': tstamp,
        }

    # Extract nets section
    nets = {}
    nets_section = content.find('(nets')
    if nets_section != -1:
        net_pattern = re.compile(
            r'\(net \(code "(\d+)"\) \(name "([^"]*)"\)\s*(.*?)\)',
            re.DOTALL
        )
        # Find all net blocks
        pos = nets_section
        while True:
            nm = re.search(r'\(net \(code "(\d+)"\) \(name "([^"]*)"\)', content[pos:])
            if not nm:
                break
            net_code = int(nm.group(1))
            net_name = nm.group(2)
            # Find all nodes in this net
            block_start = pos + nm.start()
            # Find end of this net block
            depth = 0
            i = block_start
            while i < len(content):
                if content[i] == '(':
                    depth += 1
                elif content[i] == ')':
                    depth -= 1
                    if depth == 0:
                        break
                i += 1
            net_block = content[block_start:i+1]

            nodes = []
            for node_m in re.finditer(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', net_block):
                nodes.append((node_m.group(1), node_m.group(2)))

            if net_name:
                nets[net_name] = {'code': net_code, 'nodes': nodes}

            pos = block_start + len(net_block)

    return components, nets


# Component placements: ref -> (x_mm, y_mm, angle_deg)
# 4 functional groups on 4x4" board
PLACEMENTS = {
    # PSU 5V — top-left quadrant
    "U6":  (125.0,  72.0,  0),
    "C31": (112.0,  72.0,  0),
    "C33": (112.0,  80.0,  0),
    "C32": (140.0,  80.0,  0),
    "R3":  (140.0,  66.0, 90),
    "R4":  (146.0,  80.0, 90),
    # PSU 3.3V — top-right quadrant
    "U5":  (175.0,  72.0,  0),
    "D8":  (160.0,  72.0,  0),
    "C11": (162.0,  84.0,  0),
    "C34": (168.0,  84.0,  0),
    "C35": (190.0,  84.0,  0),
    "R31": (190.0,  66.0, 90),
    "R32": (196.0,  78.0, 90),
    # RTC — bottom-left quadrant
    "U8":  (118.0, 118.0,  0),
    "C10": (132.0, 118.0,  0),
    "R41": (134.0, 110.0,  0),
    "R46": (140.0, 118.0, 90),
    "B3":  (112.0, 132.0,  0),
    # Audio — bottom-right quadrant
    "U4":  (175.0, 120.0,  0),
    "R7":  (160.0, 112.0, 90),
    "R6":  (160.0, 120.0, 90),
    "C15": (160.0, 132.0,  0),
    "C16": (166.0, 132.0,  0),
}


def main():
    print("Parsing netlist...")
    components, nets = parse_netlist(NETLIST_PATH)
    print(f"  Found {len(components)} components, {len(nets)} nets")

    print(f"\nLoading PCB: {PCB_PATH}")
    board = pcbnew.LoadBoard(PCB_PATH)

    # ============================================================
    # 1. SET UP NETS
    # ============================================================
    print("\nSetting up nets...")
    netinfo = board.GetNetInfo()

    # Create all nets on the board
    net_map = {}  # net_name -> NETINFO_ITEM
    for net_name, net_data in nets.items():
        ni = pcbnew.NETINFO_ITEM(board, net_name)
        board.Add(ni)
        net_map[net_name] = ni

    # Build pin-to-net lookup: (ref, pin) -> net_name
    pin_net = {}
    for net_name, net_data in nets.items():
        for ref, pin in net_data['nodes']:
            pin_net[(ref, pin)] = net_name

    # ============================================================
    # 2. LOAD AND PLACE FOOTPRINTS
    # ============================================================
    print("\nLoading footprints from JLCImport.pretty...")

    placed = 0
    errors = []

    for ref, comp_data in components.items():
        fp_full = comp_data['footprint']  # e.g. "JLCImport:CR2032-BS-2-1"
        # Extract footprint name (after colon)
        if ':' in fp_full:
            fp_name = fp_full.split(':', 1)[1]
        else:
            fp_name = fp_full

        fp_path = os.path.join(FP_LIB, fp_name + ".kicad_mod")
        if not os.path.exists(fp_path):
            errors.append(f"  {ref}: footprint file not found: {fp_name}.kicad_mod")
            continue

        # Load footprint
        try:
            fp = pcbnew.FootprintLoad(FP_LIB, fp_name)
        except Exception as e:
            errors.append(f"  {ref}: failed to load {fp_name}: {e}")
            continue

        # Set reference and value
        fp.SetReference(ref)
        fp.SetValue(comp_data['value'])

        # Set position and angle
        if ref in PLACEMENTS:
            x_mm, y_mm, angle_deg = PLACEMENTS[ref]
        else:
            # Components not in placement plan go to a staging area
            x_mm = BOARD_ORIGIN_X + BOARD_W + 10
            y_mm = BOARD_ORIGIN_Y + placed * 8
            angle_deg = 0

        pos = pcbnew.VECTOR2I(mm_to_nm(x_mm), mm_to_nm(y_mm))
        fp.SetPosition(pos)

        if angle_deg != 0:
            fp.SetOrientationDegrees(float(angle_deg))

        # Assign nets to pads
        for pad in fp.Pads():
            pad_num = pad.GetNumber()
            net_name = pin_net.get((ref, str(pad_num)))
            if net_name and net_name in net_map:
                pad.SetNet(net_map[net_name])

        board.Add(fp)
        placed += 1

    print(f"  Placed {placed} footprints")
    if errors:
        print("  Errors:")
        for e in errors:
            print(e)

    # ============================================================
    # 3. BOARD OUTLINE (4" x 4")
    # ============================================================
    print(f"\nCreating board outline: {BOARD_W}mm x {BOARD_H}mm")

    # Remove existing Edge.Cuts
    to_remove = []
    for drawing in board.GetDrawings():
        if drawing.GetLayer() == pcbnew.Edge_Cuts:
            to_remove.append(drawing)
    for item in to_remove:
        board.Remove(item)

    # Create rectangle outline
    rect = pcbnew.PCB_SHAPE(board)
    rect.SetShape(pcbnew.SHAPE_T_RECT)
    rect.SetLayer(pcbnew.Edge_Cuts)
    rect.SetStart(pcbnew.VECTOR2I(mm_to_nm(BOARD_ORIGIN_X), mm_to_nm(BOARD_ORIGIN_Y)))
    rect.SetEnd(pcbnew.VECTOR2I(mm_to_nm(BOARD_ORIGIN_X + BOARD_W),
                                 mm_to_nm(BOARD_ORIGIN_Y + BOARD_H)))
    rect.SetWidth(mm_to_nm(0.1))  # 0.1mm line width
    board.Add(rect)

    # ============================================================
    # 4. SAVE
    # ============================================================
    print(f"\nSaving: {PCB_PATH}")
    pcbnew.SaveBoard(PCB_PATH, board)

    print(f"\n=== PCB created successfully ===")
    print(f"Board: {BOARD_W}mm x {BOARD_H}mm ({BOARD_W/25.4:.0f}\" x {BOARD_H/25.4:.0f}\")")
    print(f"Components: {placed}")
    print(f"Nets: {len(nets)}")
    print(f"\nOpen {PCB_PATH} in KiCad PCB editor to see the layout.")
    print("The ratsnest (unrouted connections) should be visible.")


if __name__ == "__main__":
    main()
