"""
Build buttons_adc_ladder.kicad_sch — 6-button ADC resistor ladder template.

Components: R12(100k), R22(51k), R3(30k), R2(20k), R25(10k), R26(4.7k) ladder,
            R1(10k) ADC series, C4(100nF) filter, SW1-SW6 tactile switches
Power: +3.3V, GND
Port: KEY_ADC

Layout: Vertical resistor ladder on left, buttons branch right to GND.
ADC tap at top through R1 to KEY_ADC port.

Run: python build_buttons_template.py
"""

import uuid
import os
import re
import json

def uid():
    return str(uuid.uuid4())

ROOT_UUID = "f8d6e5a7-3c9b-4f0d-e1b4-2a7b8c9d0e1f"

def snap(val, grid=1.27):
    return round(round(val / grid) * grid, 2)

# ============================================================
# LAYOUT — vertical ladder, left side
# ============================================================
# Ladder resistors: vertical chain, each at angle=90 (vertical)
# R/C pin offset = 5.08mm for 0805 passives at angle=90
# Switch pin offset = 5.08mm (TS665WS) at angle=0 (horizontal)

LADDER_X = snap(140)  # X for all ladder resistors
START_Y = snap(70)     # Top of ladder (+3.3V connection)

# Ladder resistors spaced 10.16mm apart vertically (enough room for switches)
SPACING = 10.16

# Resistor definitions: (ref, symbol, value, lcsc)
LADDER_RESISTORS = [
    ("R12", "0805W8F1003T5E", "100k", "C17407"),
    ("R22", "0805W8F5102T5E", "51k", "C17737"),
    ("R3",  "0805W8F3002T5E", "30k", "C17621"),
    ("R2",  "0805W8F2002T5E", "20k", "C4328"),
    ("R25", "0805W8F1002T5E", "10k", "C17414"),
    ("R26", "0805W8F4701T5E", "4.7k", "C17673"),
]

# Calculate ladder node Y positions (junctions between resistors)
# Node 0 = top of R12 (= +3.3V)
# Node 1 = bottom of R12 / top of R22  (SW5 tap)
# Node 2 = bottom of R22 / top of R3   (SW1 tap)
# etc.
ladder_nodes = []
for i in range(len(LADDER_RESISTORS) + 1):
    ladder_nodes.append(snap(START_Y + i * SPACING))

# Resistor centers (midpoint between adjacent nodes)
resistor_positions = []
for i in range(len(LADDER_RESISTORS)):
    cy = snap((ladder_nodes[i] + ladder_nodes[i+1]) / 2)
    resistor_positions.append((LADDER_X, cy))

# Switch positions: horizontal, branching from ladder nodes to GND
# SW5 at node 1, SW1 at node 2, SW2 at node 3, SW3 at node 4, SW4 at node 5, SW6 at node 6
# Switches are placed to the right of the ladder
SW_X = snap(165)  # center of switches
SWITCH_DEFS = [
    ("SW5", 1),  # node 1
    ("SW1", 2),  # node 2
    ("SW2", 3),  # node 3
    ("SW3", 4),  # node 4
    ("SW4", 5),  # node 5
    ("SW6", 6),  # node 6 (bottom)
]

switch_positions = []
for sw_ref, node_idx in SWITCH_DEFS:
    sy = ladder_nodes[node_idx]
    switch_positions.append((sw_ref, SW_X, sy, node_idx))

# R1 (10k series to ADC) — horizontal, right of ladder top
R1_X = snap(155)
R1_Y = ladder_nodes[0]
R1_P1 = (round(R1_X - 5.08, 2), R1_Y)  # left = ladder top
R1_P2 = (round(R1_X + 5.08, 2), R1_Y)  # right = ADC tap

# C4 (100nF filter, vertical angle=90) — at ADC tap
C4_X = round(R1_P2[0] + 5.08, 2)
C4_Y = snap(R1_Y + 5.08)
C4_P1 = (C4_X, round(C4_Y - 5.08, 2))  # top = ADC tap
C4_P2 = (C4_X, round(C4_Y + 5.08, 2))  # bottom = GND

# Power symbols
VCC33_X, VCC33_Y = LADDER_X, snap(START_Y - 5.08)
GND_LADDER_X, GND_LADDER_Y = LADDER_X, snap(ladder_nodes[-1] + 3.81)
GND_C4_X, GND_C4_Y = C4_X, snap(C4_P2[1] + 3.81)

# GND for switches (right side of each switch)
SW_GND_X = snap(SW_X + 10.16)

# Port symbol
PORT_X = snap(C4_X + 5.08)
PORT_Y = C4_P1[1]

# ============================================================
# LIB_SYMBOLS
# ============================================================
def extract_symbol(content, sym_name):
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
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    ports_path = os.path.join(project_root, "Ports.kicad_sym")
    with open(ports_path, 'r', encoding='utf-8') as f:
        content = f.read()
    extracted = {}
    for port_name in ['KEY_ADC']:
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
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    jlc_path = os.path.join(project_root, "JLCImport.kicad_sym")

    needed_symbols = [
        ("0805W8F1003T5E", True),
        ("0805W8F5102T5E", True),
        ("0805W8F3002T5E", True),
        ("0805W8F2002T5E", True),
        ("0805W8F1002T5E", True),
        ("0805W8F4701T5E", True),
        ("CC0805KRX7R9BB104", True),
        ("TS665WS_C2686403", False),
    ]

    with open(jlc_path, 'r', encoding='utf-8') as f:
        content = f.read()

    extracted = {}
    for sym_name, hide_names in needed_symbols:
        sym_text = extract_symbol(content, sym_name)
        if sym_text is None:
            raise ValueError(f"Symbol {sym_name} not found in {jlc_path}")
        sym_text = sym_text.replace(
            f'(symbol "{sym_name}"',
            f'(symbol "JLCImport:{sym_name}"',
            1
        )
        sym_text = re.sub(
            r'\(pin_numbers[^)]*\)',
            '(pin_numbers (hide yes))',
            sym_text, count=1
        )
        if hide_names:
            sym_text = re.sub(
                r'\(pin_names\s*\([^)]*\)\)',
                '(pin_names (offset 1.016) (hide yes))',
                sym_text, count=1
            )
        extracted[sym_name] = sym_text

    return extracted


def build_schematic():
    jlc_symbols = read_lib_symbols()

    lib_parts = []
    for sym_text in jlc_symbols.values():
        lib_parts.append(f"    {sym_text}")

    # +3.3V
    lib_parts.append("""    (symbol "power:+3.3V"
      (power)
      (pin_numbers (hide yes))
      (pin_names (offset 0) (hide yes))
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "+3.3V" (at 0 3.556 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Description" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "ki_keywords" "global power" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "+3.3V_0_1"
        (polyline (pts (xy -0.762 1.27) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none)))
        (polyline (pts (xy 0 2.54) (xy 0.762 1.27)) (stroke (width 0) (type default)) (fill (type none)))
        (polyline (pts (xy 0 0) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none)))
      )
      (symbol "+3.3V_1_1"
        (pin power_in line (at 0 0 90) (length 0)
          (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27))))))
      (embedded_fonts no)
    )""")

    # GND
    lib_parts.append("""    (symbol "power:GND"
      (power)
      (pin_numbers (hide yes))
      (pin_names (offset 0) (hide yes))
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "#PWR" (at 0 -6.35 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "GND" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Description" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "ki_keywords" "global power" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "GND_0_1"
        (polyline (pts (xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27))
          (stroke (width 0) (type default)) (fill (type none))))
      (symbol "GND_1_1"
        (pin power_in line (at 0 0 270) (length 0)
          (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27))))))
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
                       angle=0, ref_offset=(2.54, -3.81), val_offset=(2.54, 3.81)):
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
    (in_bom yes)
    (on_board yes)
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

    def make_power(ref, lib_id, value, x, y, angle=0, ref_pos=None, val_pos=None):
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
    (property "Reference" "{ref}" (at {ref_pos[0]} {ref_pos[1]} 0) (effects (font (size 1.27 1.27)) hide))
    (property "Value" "{value}" (at {val_pos[0]} {val_pos[1]} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide))
    (instances
      (project "AITestProject"
        (path "/{ROOT_UUID}" (reference "{ref}") (unit 1))))
  )"""

    def make_port(ref, lib_id, value, x, y, angle=0, val_pos=None):
        if val_pos is None:
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
    (property "Reference" "{ref}" (at {x} {round(y + 2.54, 2)} 0) (effects (font (size 1.27 1.27)) hide))
    (property "Value" "{value}" (at {val_pos[0]} {val_pos[1]} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at {x} {y} 0) (effects (font (size 1.27 1.27)) hide))
    (instances
      (project "AITestProject"
        (path "/{ROOT_UUID}" (reference "{ref}") (unit 1))))
  )"""

    symbols = []

    # Ladder resistors (all vertical angle=90)
    for i, (ref, sym, value, lcsc) in enumerate(LADDER_RESISTORS):
        rx, ry = resistor_positions[i]
        symbols.append(make_component(ref, f"JLCImport:{sym}",
            rx, ry, value, angle=90,
            footprint=f"JLCImport:{sym}", lcsc=lcsc,
            ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # Switches (horizontal angle=0)
    for sw_ref, sx, sy, node_idx in switch_positions:
        symbols.append(make_component(sw_ref, "JLCImport:TS665WS_C2686403",
            sx, sy, "SW",
            footprint="JLCImport:TS665WS_C2686403", lcsc="C318884",
            ref_offset=(0, -3.81), val_offset=(0, 3.81)))

    # R1 — 10k ADC series (horizontal angle=0)
    symbols.append(make_component("R1", "JLCImport:0805W8F1002T5E",
        R1_X, R1_Y, "10k",
        footprint="JLCImport:0805W8F1002T5E", lcsc="C17414",
        ref_offset=(0, -2.54), val_offset=(0, 2.54)))

    # C4 — 100nF filter (vertical angle=90)
    symbols.append(make_component("C4", "JLCImport:CC0805KRX7R9BB104",
        C4_X, C4_Y, "100nF", angle=90,
        footprint="JLCImport:CC0805KRX7R9BB104", lcsc="C49678",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # Power symbols
    symbols.append(make_power("#PWR01", "power:+3.3V", "+3.3V", VCC33_X, VCC33_Y))
    # GND at bottom of ladder
    symbols.append(make_power("#PWR02", "power:GND", "GND", GND_LADDER_X, GND_LADDER_Y,
                               ref_pos=(GND_LADDER_X, round(GND_LADDER_Y + 6.35, 2)),
                               val_pos=(GND_LADDER_X, round(GND_LADDER_Y + 3.81, 2))))
    # GND below C4
    symbols.append(make_power("#PWR03", "power:GND", "GND", GND_C4_X, GND_C4_Y,
                               ref_pos=(GND_C4_X, round(GND_C4_Y + 6.35, 2)),
                               val_pos=(GND_C4_X, round(GND_C4_Y + 3.81, 2))))

    # GND for each switch (right side)
    pwr_idx = 4
    for sw_ref, sx, sy, node_idx in switch_positions:
        sw_gnd_x = round(sx + 5.08, 2)
        gnd_y = sy
        symbols.append(make_power(f"#PWR{pwr_idx:02d}", "power:GND", "GND",
                                   round(sw_gnd_x + 3.81, 2), gnd_y,
                                   angle=90,
                                   ref_pos=(round(sw_gnd_x + 10.16, 2), gnd_y),
                                   val_pos=(round(sw_gnd_x + 7.62, 2), round(gnd_y - 0.254, 2))))
        pwr_idx += 1

    # KEY_ADC port (right side, using angle=180)
    symbols.append(make_port("#PORT01", "Ports:KEY_ADC", "KEY_ADC", PORT_X, PORT_Y,
                              angle=180,
                              val_pos=(round(PORT_X + 1.905, 2), PORT_Y)))

    symbols_str = "\n\n".join(symbols)

    # ============================================================
    # WIRES
    # ============================================================
    def wire(x1, y1, x2, y2):
        if x1 == x2 and y1 == y2:
            return None
        return f"""  (wire (pts (xy {x1} {y1}) (xy {x2} {y2}))
    (stroke (width 0) (type default))
    (uuid "{uid()}")
  )"""

    wires_raw = []

    # +3.3V to top of ladder
    wires_raw.append(wire(VCC33_X, VCC33_Y, LADDER_X, ladder_nodes[0]))

    # Ladder chain: connect each resistor in series
    # Each resistor at angle=90: P1 at (cx, cy-5.08)=top, P2 at (cx, cy+5.08)=bottom
    for i in range(len(LADDER_RESISTORS)):
        rx, ry = resistor_positions[i]
        p1_y = round(ry - 5.08, 2)
        p2_y = round(ry + 5.08, 2)
        # Wire from node above to resistor top
        wires_raw.append(wire(LADDER_X, ladder_nodes[i], LADDER_X, p1_y))
        # Wire from resistor bottom to node below
        wires_raw.append(wire(LADDER_X, p2_y, LADDER_X, ladder_nodes[i+1]))

    # Bottom of ladder to GND
    wires_raw.append(wire(LADDER_X, ladder_nodes[-1], GND_LADDER_X, GND_LADDER_Y))

    # Switch wires: from ladder node horizontally to switch left pin
    for sw_ref, sx, sy, node_idx in switch_positions:
        sw_left = round(sx - 5.08, 2)
        sw_right = round(sx + 5.08, 2)
        # Horizontal from ladder to switch left pin
        wires_raw.append(wire(LADDER_X, sy, sw_left, sy))
        # Switch right pin to GND (short wire to GND symbol)
        wires_raw.append(wire(sw_right, sy, round(sw_right + 3.81, 2), sy))

    # R1: from ladder top node to R1 left pin
    wires_raw.append(wire(LADDER_X, ladder_nodes[0], R1_P1[0], R1_P1[1]))
    # R1 right to ADC tap (C4 top)
    wires_raw.append(wire(R1_P2[0], R1_P2[1], C4_P1[0], C4_P1[1]))
    # C4 bottom to GND
    wires_raw.append(wire(C4_P2[0], C4_P2[1], GND_C4_X, GND_C4_Y))
    # KEY_ADC port to ADC tap
    wires_raw.append(wire(round(PORT_X - 2.54, 2), PORT_Y, C4_P1[0], C4_P1[1]))

    wires = [w for w in wires_raw if w is not None]
    wires_str = "\n\n".join(wires)

    # ============================================================
    # JUNCTIONS
    # ============================================================
    def junction(x, y):
        return f"""  (junction (at {x} {y})
    (diameter 0)
    (color 0 0 0 0)
    (uuid "{uid()}")
  )"""

    junctions_list = []
    # Junction at each switch tap node on the ladder
    for sw_ref, sx, sy, node_idx in switch_positions:
        junctions_list.append(junction(LADDER_X, ladder_nodes[node_idx]))
    # Junction at R1/ladder top
    junctions_list.append(junction(LADDER_X, ladder_nodes[0]))
    # Junction at ADC tap (C4 top + port)
    junctions_list.append(junction(C4_P1[0], C4_P1[1]))

    junctions_str = "\n\n".join(junctions_list)

    # ============================================================
    # ASSEMBLE
    # ============================================================
    schematic = f"""(kicad_sch
  (version 20250114)
  (generator "build_buttons_template.py")
  (generator_version "9.0")
  (uuid "{ROOT_UUID}")
  (paper "A4")

  (lib_symbols
{lib_symbols_str}
  )

{junctions_str}

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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    status_path = os.path.join(script_dir, "status.json")
    if os.path.exists(status_path):
        with open(status_path, 'r') as f:
            status = json.load(f)
        if status.get("status") == "locked":
            print("ERROR: Template is LOCKED. Cannot regenerate.")
            exit(1)

    output_path = os.path.join(script_dir, "buttons_adc_ladder.kicad_sch")
    content = build_schematic()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    if os.path.exists(status_path):
        with open(status_path, 'r') as f:
            status = json.load(f)
        old_status = status.get("status", "draft")
        status["status"] = "review"
        if "changelog" not in status:
            status["changelog"] = []
        status["changelog"].append({
            "date": "2026-03-07",
            "from": old_status,
            "to": "review",
            "by": "ai"
        })
        with open(status_path, 'w') as f:
            json.dump(status, f, indent=2)

    print(f"Written: {output_path}")
    print(f"Components: R12, R22, R3, R2, R25, R26 (ladder), R1 (ADC), C4, SW1-SW6")
    print(f"Power symbols: +3.3V, 8x GND")
    print(f"Port: KEY_ADC")
