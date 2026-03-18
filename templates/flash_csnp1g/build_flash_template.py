"""
Build flash_csnp1g.kicad_sch — CSNP1GCR01-BOW 1Gbit NAND Flash template (SPI mode).
Reference design: EV4-PDS schematic page 1 (Mem1).

Pin endpoint formula (VERIFIED):
  The (at x y) in a KiCad lib_symbol pin definition IS the wire connection point.
  Schematic endpoint = (sym_x + pin_at_x, sym_y - pin_at_y)

Run: python build_flash_template.py
"""

import uuid
import os
import re
import json

def uid():
    return str(uuid.uuid4())

# Fixed root UUID so instance paths don't change on regeneration
ROOT_UUID = "b4f8c2d3-6e5a-4b90-af7d-2g3e4f5a6b7c"


def snap(val, grid=1.27):
    """Snap a value to the nearest 1.27mm grid point."""
    return round(round(val / grid) * grid, 2)


# ============================================================
# LAYOUT — all positions on 1.27mm grid
# ============================================================
# Mem1 center
MEM_X, MEM_Y = 149.86, 100.33

# Pin endpoints: endpoint = (sym_x + pin_at_x, sym_y - pin_at_y)
# Pin local coords from JLCImport symbol:
#   Pin 1 SDD2:    at (-13.970028, 3.810008)
#   Pin 2 CD/SDD3: at (-13.970028, 1.270003)
#   Pin 3 SCLK:    at (-13.970028, -1.270003)
#   Pin 4 VSS:     at (-13.970028, -3.810008)
#   Pin 5 CMD:     at (13.970028, -3.810008)
#   Pin 6 SDD0:    at (13.970028, -1.270003)
#   Pin 7 SDD1:    at (13.970028, 1.270003)
#   Pin 8 VCC:     at (13.970028, 3.810008)
MEM_PINS = {
    'SDD2':    (round(MEM_X - 13.97, 2), round(MEM_Y - 3.81, 2)),   # (135.89, 96.52)
    'CD_SDD3': (round(MEM_X - 13.97, 2), round(MEM_Y - 1.27, 2)),   # (135.89, 99.06)
    'SCLK':    (round(MEM_X - 13.97, 2), round(MEM_Y + 1.27, 2)),   # (135.89, 101.60)
    'VSS':     (round(MEM_X - 13.97, 2), round(MEM_Y + 3.81, 2)),   # (135.89, 104.14)
    'CMD':     (round(MEM_X + 13.97, 2), round(MEM_Y + 3.81, 2)),   # (163.83, 104.14)
    'SDD0':    (round(MEM_X + 13.97, 2), round(MEM_Y + 1.27, 2)),   # (163.83, 101.60)
    'SDD1':    (round(MEM_X + 13.97, 2), round(MEM_Y - 1.27, 2)),   # (163.83, 99.06)
    'VCC':     (round(MEM_X + 13.97, 2), round(MEM_Y - 3.81, 2)),   # (163.83, 96.52)
}

# C1 (1uF, vertical angle=270, pin1=top, pin2=bottom)
C1_X, C1_Y = 175.26, 91.44
C1_P1 = (C1_X, round(C1_Y - 5.08, 2))   # (175.26, 86.36) = VCC bus
C1_P2 = (C1_X, round(C1_Y + 5.08, 2))   # (175.26, 96.52) = GND bus

# C3 (100nF, vertical angle=270, pin1=top, pin2=bottom)
C3_X, C3_Y = 182.88, 91.44
C3_P1 = (C3_X, round(C3_Y - 5.08, 2))   # (182.88, 86.36) = VCC bus
C3_P2 = (C3_X, round(C3_Y + 5.08, 2))   # (182.88, 96.52) = GND bus

# Power symbols
VCC_X, VCC_Y = 175.26, 82.55             # +3.3V above VCC bus
GND_VSS_X, GND_VSS_Y = 135.89, 111.76   # GND below Mem1.VSS
GND_CAP_X, GND_CAP_Y = 175.26, 99.06    # GND below cap GND bus

# VCC bus Y coordinate
VCC_BUS_Y = 86.36
# Cap GND bus Y coordinate
CAP_GND_BUS_Y = 96.52

# Port symbols (left side, angle=0)
CS_FLASH_PORT_X, CS_FLASH_PORT_Y = 120.65, 99.06
CS_FLASH_PIN_X = round(CS_FLASH_PORT_X + 2.54, 2)    # 123.19

SD_CLK_PORT_X, SD_CLK_PORT_Y = 120.65, 101.60
SD_CLK_PIN_X = round(SD_CLK_PORT_X + 2.54, 2)  # 123.19

# Port symbols (right side, angle=180)
SD_MOSI_PORT_X, SD_MOSI_PORT_Y = 180.34, 104.14
SD_MOSI_PIN_X = round(SD_MOSI_PORT_X - 2.54, 2)  # 177.80

SD_MISO_PORT_X, SD_MISO_PORT_Y = 180.34, 101.60
SD_MISO_PIN_X = round(SD_MISO_PORT_X - 2.54, 2)  # 177.80


# ============================================================
# LIB_SYMBOLS — read from project libraries
# ============================================================

def extract_symbol(content, sym_name):
    """Extract a single (symbol ...) block from a .kicad_sym file content."""
    marker = f'(symbol "{sym_name}"'
    start = content.find(marker)
    if start == -1:
        return None
    depth = 0
    i = start
    while i < len(content):
        if content[i] == '(':
            depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                break
        i += 1
    return content[start:i+1]


def read_port_symbols():
    """Read port symbol definitions from Ports.kicad_sym at project root."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    ports_path = os.path.join(project_root, "Ports.kicad_sym")

    with open(ports_path, 'r', encoding='utf-8') as f:
        content = f.read()

    extracted = {}
    for port_name in ['CS_FLASH', 'SD_CLK', 'SD_MOSI', 'SD_MISO']:
        sym_text = extract_symbol(content, port_name)
        if sym_text is None:
            raise ValueError(f"Symbol {port_name} not found in {ports_path}")
        sym_text = sym_text.replace(
            f'(symbol "{port_name}"',
            f'(symbol "Ports:{port_name}"',
            1
        )
        extracted[port_name] = sym_text

    return extracted


def read_lib_symbols():
    """Read the lib_symbols section from the project's JLCImport library."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    jlc_path = os.path.join(project_root, "JLCImport.kicad_sym")

    needed_symbols = [
        ("CSNP1GCR01-BOW", False),      # IC — keep pin names visible
        ("CL21B105KBFNNNE", True),       # 1uF cap — hide names
        ("CC0805KRX7R9BB104", True),     # 100nF cap — hide names
    ]

    with open(jlc_path, 'r', encoding='utf-8') as f:
        content = f.read()

    extracted = {}
    for sym_name, hide_names in needed_symbols:
        sym_text = extract_symbol(content, sym_name)
        if sym_text is None:
            raise ValueError(f"Symbol {sym_name} not found in {jlc_path}")

        # Add JLCImport: prefix to top-level symbol name only
        sym_text = sym_text.replace(
            f'(symbol "{sym_name}"',
            f'(symbol "JLCImport:{sym_name}"',
            1
        )

        # Hide pin numbers on all symbols
        if '(pin_numbers' in sym_text:
            sym_text = re.sub(
                r'\(pin_numbers[^)]*\)',
                '(pin_numbers (hide yes))',
                sym_text,
                count=1
            )
        else:
            sym_text = sym_text.replace(
                f'(symbol "JLCImport:{sym_name}"',
                f'(symbol "JLCImport:{sym_name}"\n    (pin_numbers (hide yes))',
                1
            )

        # Optionally hide pin names (for passives)
        if hide_names:
            if re.search(r'\(pin_names\s*\([^)]*\)\)', sym_text):
                sym_text = re.sub(
                    r'\(pin_names\s*\([^)]*\)\)',
                    '(pin_names (offset 1.016) (hide yes))',
                    sym_text,
                    count=1
                )
            elif '(pin_names' in sym_text:
                sym_text = re.sub(
                    r'\(pin_names[^)]*\)',
                    '(pin_names (offset 1.016) (hide yes))',
                    sym_text,
                    count=1
                )

        extracted[sym_name] = sym_text

    return extracted


def build_schematic():
    # Check lock status
    status_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "status.json")
    if os.path.exists(status_path):
        with open(status_path, 'r') as f:
            status = json.load(f)
        if status.get("status") == "locked":
            print(f"ERROR: Template is LOCKED. Cannot regenerate.")
            print(f"Reason: {status.get('description', 'No reason given')}")
            return None

    try:
        jlc_symbols = read_lib_symbols()
    except Exception as e:
        print(f"Warning: Could not read JLCImport.kicad_sym: {e}")
        jlc_symbols = {}

    lib_parts = []
    for sym_text in jlc_symbols.values():
        lib_parts.append(f"    {sym_text}")

    # +3.3V power symbol
    lib_parts.append("""    (symbol "power:+3.3V"
      (power)
      (pin_numbers (hide yes))
      (pin_names (offset 0) (hide yes))
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "#PWR"
        (at 0 -3.81 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "Value" "+3.3V"
        (at 0 3.556 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" ""
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "Datasheet" ""
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "Description" "Power symbol creates a global label with name \\"+3.3V\\""
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "ki_keywords" "global power"
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (symbol "+3.3V_0_1"
        (polyline
          (pts (xy -0.762 1.27) (xy 0 2.54))
          (stroke (width 0) (type default))
          (fill (type none))
        )
        (polyline
          (pts (xy 0 2.54) (xy 0.762 1.27))
          (stroke (width 0) (type default))
          (fill (type none))
        )
        (polyline
          (pts (xy 0 0) (xy 0 2.54))
          (stroke (width 0) (type default))
          (fill (type none))
        )
      )
      (symbol "+3.3V_1_1"
        (pin power_in line
          (at 0 0 90)
          (length 0)
          (name "~" (effects (font (size 1.27 1.27))))
          (number "1" (effects (font (size 1.27 1.27))))
        )
      )
      (embedded_fonts no)
    )""")

    # GND power symbol
    lib_parts.append("""    (symbol "power:GND"
      (power)
      (pin_numbers (hide yes))
      (pin_names (offset 0) (hide yes))
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "#PWR"
        (at 0 -6.35 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "Value" "GND"
        (at 0 -3.81 0)
        (effects (font (size 1.27 1.27)))
      )
      (property "Footprint" ""
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "Datasheet" ""
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "Description" "Power symbol creates a global label with name \\"GND\\" , ground"
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "ki_keywords" "global power"
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (symbol "GND_0_1"
        (polyline
          (pts (xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27))
          (stroke (width 0) (type default))
          (fill (type none))
        )
      )
      (symbol "GND_1_1"
        (pin power_in line
          (at 0 0 270)
          (length 0)
          (name "~" (effects (font (size 1.27 1.27))))
          (number "1" (effects (font (size 1.27 1.27))))
        )
      )
      (embedded_fonts no)
    )""")

    # Port symbols
    try:
        port_symbols = read_port_symbols()
        for sym_text in port_symbols.values():
            lib_parts.append(f"    {sym_text}")
    except Exception as e:
        raise RuntimeError(f"Could not read Ports.kicad_sym: {e}")

    lib_symbols_str = "\n".join(lib_parts)

    # ============================================================
    # SYMBOL INSTANCES
    # ============================================================
    def make_component(ref, lib_id, x, y, value, footprint="", lcsc="",
                       angle=0, in_bom="yes", on_board="yes",
                       ref_offset=(2.54, -3.81), val_offset=(2.54, 3.81)):
        rx, ry = round(x + ref_offset[0], 2), round(y + ref_offset[1], 2)
        vx, vy = round(x + val_offset[0], 2), round(y + val_offset[1], 2)
        props = f"""    (property "Reference" "{ref}"
      (at {rx} {ry} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "{value}"
      (at {vx} {vy} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "{footprint}"
      (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )"""
        if lcsc:
            props += f"""
    (property "LCSC" "{lcsc}"
      (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )"""

        return f"""  (symbol
    (lib_id "{lib_id}")
    (at {x} {y} {angle})
    (unit 1)
    (exclude_from_sim no)
    (in_bom {in_bom})
    (on_board {on_board})
    (dnp no)
    (uuid "{uid()}")
{props}
    (instances
      (project "AITestProject"
        (path "/{ROOT_UUID}"
          (reference "{ref}")
          (unit 1)
        )
      )
    )
  )"""

    def make_power(ref, lib_id, value, x, y, angle=0,
                   ref_pos=None, val_pos=None):
        if ref_pos is None:
            ref_pos = (x, round(y + 6.35, 2))
        if val_pos is None:
            val_pos = (x, round(y - 3.56, 2))
        return f"""  (symbol
    (lib_id "{lib_id}")
    (at {x} {y} {angle})
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{uid()}")
    (property "Reference" "{ref}"
      (at {ref_pos[0]} {ref_pos[1]} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Value" "{value}"
      (at {val_pos[0]} {val_pos[1]} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" ""
      (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (instances
      (project "AITestProject"
        (path "/{ROOT_UUID}"
          (reference "{ref}")
          (unit 1)
        )
      )
    )
  )"""

    def make_port(ref, lib_id, value, x, y, angle=0, val_pos=None):
        if val_pos is None:
            if angle == 180:
                val_pos = (round(x + 1.905, 2), y)
            else:
                val_pos = (round(x - 1.905, 2), y)
        return f"""  (symbol
    (lib_id "{lib_id}")
    (at {x} {y} {angle})
    (unit 1)
    (exclude_from_sim no)
    (in_bom no)
    (on_board no)
    (dnp no)
    (uuid "{uid()}")
    (property "Reference" "{ref}"
      (at {x} {round(y + 2.54, 2)} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Value" "{value}"
      (at {val_pos[0]} {val_pos[1]} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" ""
      (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (instances
      (project "AITestProject"
        (path "/{ROOT_UUID}"
          (reference "{ref}")
          (unit 1)
        )
      )
    )
  )"""

    symbols = []

    # Mem1 — CSNP1GCR01-BOW
    symbols.append(make_component("Mem1", "JLCImport:CSNP1GCR01-BOW",
        MEM_X, MEM_Y, "CSNP1GCR01-BOW",
        footprint="JLCImport:CSNP1GCR01-BOW", lcsc="C2691593",
        ref_offset=(0, -10.16), val_offset=(0, 10.16)))

    # C1 — 1uF bulk decoupling (angle=270, pin1=top)
    symbols.append(make_component("C1", "JLCImport:CL21B105KBFNNNE",
        C1_X, C1_Y, "1uF", angle=270,
        footprint="JLCImport:CL21B105KBFNNNE", lcsc="C28323",
        ref_offset=(3.81, 0), val_offset=(5.08, 0)))

    # C3 — 100nF bypass decoupling (angle=270, pin1=top)
    symbols.append(make_component("C3", "JLCImport:CC0805KRX7R9BB104",
        C3_X, C3_Y, "100nF", angle=270,
        footprint="JLCImport:CC0805KRX7R9BB104", lcsc="C49678",
        ref_offset=(3.81, 0), val_offset=(5.08, 0)))

    # Power — +3.3V
    symbols.append(make_power("#PWR01", "power:+3.3V", "+3.3V",
        VCC_X, VCC_Y, angle=0))

    # Power — GND (below VSS)
    symbols.append(make_power("#PWR02", "power:GND", "GND",
        GND_VSS_X, GND_VSS_Y, angle=0))

    # Power — GND (below cap bus)
    symbols.append(make_power("#PWR03", "power:GND", "GND",
        GND_CAP_X, GND_CAP_Y, angle=0))

    # Ports — CS_FLASH and SD_CLK on left (angle=0)
    symbols.append(make_port("#PORT01", "Ports:CS_FLASH", "CS_FLASH",
        CS_FLASH_PORT_X, CS_FLASH_PORT_Y, angle=0))
    symbols.append(make_port("#PORT02", "Ports:SD_CLK", "SD_CLK",
        SD_CLK_PORT_X, SD_CLK_PORT_Y, angle=0))

    # Ports — SD_MOSI and SD_MISO on right (angle=180)
    symbols.append(make_port("#PORT03", "Ports:SD_MOSI", "SD_MOSI",
        SD_MOSI_PORT_X, SD_MOSI_PORT_Y, angle=180))
    symbols.append(make_port("#PORT04", "Ports:SD_MISO", "SD_MISO",
        SD_MISO_PORT_X, SD_MISO_PORT_Y, angle=180))

    symbols_str = "\n\n".join(symbols)

    # ============================================================
    # NO-CONNECTS (pins 1 SDD2, pin 7 SDD1 — unused in SPI mode)
    # ============================================================
    nc_pins = ['SDD2', 'SDD1']
    nc_parts = []
    for nc in nc_pins:
        px, py = MEM_PINS[nc]
        nc_parts.append(f"""  (no_connect (at {px} {py})
    (uuid "{uid()}")
  )""")
    no_connects = "\n".join(nc_parts)

    # ============================================================
    # WIRES
    # ============================================================
    def wire(x1, y1, x2, y2):
        return f"""  (wire (pts (xy {x1} {y1}) (xy {x2} {y2}))
    (stroke (width 0) (type default))
    (uuid "{uid()}")
  )"""

    wires = []

    # --- CS_FLASH: port → pin 2 (CD/SDD3) ---
    wires.append(wire(CS_FLASH_PIN_X, CS_FLASH_PORT_Y,
                      MEM_PINS['CD_SDD3'][0], MEM_PINS['CD_SDD3'][1]))

    # --- SD_CLK: port → pin 3 (SCLK) ---
    wires.append(wire(SD_CLK_PIN_X, SD_CLK_PORT_Y,
                      MEM_PINS['SCLK'][0], MEM_PINS['SCLK'][1]))

    # --- SD_MOSI: pin 5 (CMD) → port ---
    wires.append(wire(MEM_PINS['CMD'][0], MEM_PINS['CMD'][1],
                      SD_MOSI_PIN_X, SD_MOSI_PORT_Y))

    # --- SD_MISO: pin 6 (SDD0) → port ---
    wires.append(wire(MEM_PINS['SDD0'][0], MEM_PINS['SDD0'][1],
                      SD_MISO_PIN_X, SD_MISO_PORT_Y))

    # --- VCC: pin 8 → vertical up to VCC bus ---
    wires.append(wire(MEM_PINS['VCC'][0], MEM_PINS['VCC'][1],
                      MEM_PINS['VCC'][0], VCC_BUS_Y))

    # --- VCC bus: IC entry → C1.pin1 junction ---
    wires.append(wire(MEM_PINS['VCC'][0], VCC_BUS_Y,
                      C1_P1[0], VCC_BUS_Y))

    # --- VCC bus: C1.pin1 → C3.pin1 ---
    wires.append(wire(C1_P1[0], VCC_BUS_Y,
                      C3_P1[0], VCC_BUS_Y))

    # --- +3.3V → VCC bus junction ---
    wires.append(wire(VCC_X, VCC_Y,
                      VCC_X, VCC_BUS_Y))

    # --- Cap GND bus: C1.pin2 → C3.pin2 ---
    wires.append(wire(C1_P2[0], CAP_GND_BUS_Y,
                      C3_P2[0], CAP_GND_BUS_Y))

    # --- Cap GND bus → GND symbol ---
    wires.append(wire(C1_P2[0], CAP_GND_BUS_Y,
                      GND_CAP_X, GND_CAP_Y))

    # --- VSS: pin 4 → GND ---
    wires.append(wire(MEM_PINS['VSS'][0], MEM_PINS['VSS'][1],
                      GND_VSS_X, GND_VSS_Y))

    wires_str = "\n\n".join(wires)

    # ============================================================
    # JUNCTIONS
    # ============================================================
    junctions = []
    # VCC bus junction at C1.pin1 (where IC wire meets cap bus)
    junctions.append(f"""  (junction (at {C1_P1[0]} {VCC_BUS_Y})
    (diameter 0)
    (color 0 0 0 0)
    (uuid "{uid()}")
  )""")
    # Cap GND bus junction at C1.pin2 (where GND wire tees off)
    junctions.append(f"""  (junction (at {C1_P2[0]} {CAP_GND_BUS_Y})
    (diameter 0)
    (color 0 0 0 0)
    (uuid "{uid()}")
  )""")

    junctions_str = "\n".join(junctions)

    # ============================================================
    # ASSEMBLE
    # ============================================================
    schematic = f"""(kicad_sch
  (version 20250114)
  (generator "build_flash_template.py")
  (generator_version "9.0")
  (uuid "{ROOT_UUID}")
  (paper "A4")

  (lib_symbols
{lib_symbols_str}
  )

{junctions_str}

{no_connects}

{wires_str}

{symbols_str}

  (sheet_instances
    (path "/"
      (page "1")
    )
  )
  (embedded_fonts no)
)
"""
    return schematic


if __name__ == "__main__":
    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "flash_csnp1g.kicad_sch"
    )
    content = build_schematic()
    if content is None:
        exit(1)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Written: {output_path}")
    print(f"Components: Mem1 (CSNP1GCR01-BOW), C1 (1uF), C3 (100nF)")
    print(f"Port symbols: CS_FLASH, SD_CLK (left), SD_MOSI, SD_MISO (right)")
    print(f"Power symbols: 1x +3.3V, 2x GND")
    print(f"No-connects: pins 1 (SDD2), 7 (SDD1)")
    print(f"\nLayout:")
    print(f"  Mem1 at ({MEM_X}, {MEM_Y})")
    print(f"  C1   at ({C1_X}, {C1_Y}) angle=270 — 1uF bulk decoupling")
    print(f"  C3   at ({C3_X}, {C3_Y}) angle=270 — 100nF bypass")

    # Update status to review
    status_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "status.json")
    if os.path.exists(status_path):
        with open(status_path, 'r') as f:
            status = json.load(f)
        status["status"] = "review"
        status["description"] = "Build script ran successfully, awaiting human review in KiCad"
        status["changelog"].append(
            {"date": "2026-03-06", "from": "draft", "to": "review", "by": "ai"}
        )
        with open(status_path, 'w') as f:
            json.dump(status, f, indent=2)
        print(f"\nStatus updated to 'review'")
