"""
Build rs485_max485.kicad_sch — MAX485ESA+T RS-485 transceiver with auto-direction.

Components: U7 (MAX485), Q1 (SS8050 NPN), R11 (1k pull-up), R13 (4.7k base),
            R14 (4.7k B-bias), C14 (100nF VCC decoupling)
Power: +5V, GND
Ports: RX, TX, RS485_A, RS485_B

Run: python build_rs485_max485_template.py
"""

import uuid
import os
import re
import json

def uid():
    return str(uuid.uuid4())

ROOT_UUID = "e7c5d4f6-2b8a-4e9c-d0a3-1f6a7b8c9d0e"

def snap(val, grid=1.27):
    return round(round(val / grid) * grid, 2)

# ============================================================
# LAYOUT
# ============================================================
U7_X, U7_Y = snap(150), snap(100)

# U7 pin endpoints (MAX485ESA_T, angle=0)
U7_PINS = {
    'RO':  (round(U7_X - 10.16, 2), round(U7_Y - 3.81, 2)),   # pin 1, left
    'RE':  (round(U7_X - 10.16, 2), round(U7_Y - 1.27, 2)),   # pin 2, left
    'DE':  (round(U7_X - 10.16, 2), round(U7_Y + 1.27, 2)),   # pin 3, left
    'DI':  (round(U7_X - 10.16, 2), round(U7_Y + 3.81, 2)),   # pin 4, left
    'GND': (round(U7_X + 10.16, 2), round(U7_Y + 3.81, 2)),   # pin 5, right
    'A':   (round(U7_X + 10.16, 2), round(U7_Y + 1.27, 2)),   # pin 6, right
    'B':   (round(U7_X + 10.16, 2), round(U7_Y - 1.27, 2)),   # pin 7, right
    'VCC': (round(U7_X + 10.16, 2), round(U7_Y - 3.81, 2)),   # pin 8, right
}

# DE/RE# junction point — where RE#, DE, Q1.C, and R11 all meet
DE_RE_X = snap(U7_PINS['DE'][0] - 5.08)  # left of U7, between RE and DE
DE_RE_Y = snap((U7_PINS['RE'][1] + U7_PINS['DE'][1]) / 2)  # midpoint

# Q1 (SS8050 NPN, angle=0): C at top (0, 5.08), B at left (-5.08, 0), E at bottom (0, -5.08)
# Place Q1 below the DE/RE junction
Q1_X = DE_RE_X
Q1_Y = snap(DE_RE_Y + 10.16)
Q1_PINS = {
    'C': (round(Q1_X, 2), round(Q1_Y - 5.08, 2)),     # collector = top
    'B': (round(Q1_X - 5.08, 2), round(Q1_Y, 2)),      # base = left
    'E': (round(Q1_X, 2), round(Q1_Y + 5.08, 2)),      # emitter = bottom
}

# R13 (4.7k, horizontal) — TX to Q1 base
R13_X = snap(Q1_PINS['B'][0] - 7.62)
R13_Y = Q1_PINS['B'][1]
R13_P1 = (round(R13_X - 3.81, 2), R13_Y)  # left = TX net
R13_P2 = (round(R13_X + 3.81, 2), R13_Y)  # right = Q1.B

# R11 (1k, vertical angle=90) — +5V pull-up to DE/RE# junction
R11_X = DE_RE_X
R11_Y = snap(DE_RE_Y - 7.62)
R11_P1 = (R11_X, round(R11_Y - 3.81, 2))  # top = +5V
R11_P2 = (R11_X, round(R11_Y + 3.81, 2))  # bottom = DE/RE junction

# R14 (4.7k, vertical angle=90) — B line pull-down to GND
R14_X = snap(U7_PINS['B'][0] + 7.62)
R14_Y = snap(U7_PINS['B'][1] + 5.08)
R14_P1 = (R14_X, round(R14_Y - 3.81, 2))  # top = B net
R14_P2 = (R14_X, round(R14_Y + 3.81, 2))  # bottom = GND

# C14 (100nF, vertical angle=90) — VCC decoupling
C14_X = snap(U7_PINS['VCC'][0] + 7.62)
C14_Y = snap(U7_PINS['VCC'][1] + 5.08)
C14_P1 = (C14_X, round(C14_Y - 5.08, 2))  # top = VCC
C14_P2 = (C14_X, round(C14_Y + 5.08, 2))  # bottom = GND

# Power symbols
VCC5_X, VCC5_Y = R11_X, snap(R11_P1[1] - 3.81)  # +5V above R11
GND1_X, GND1_Y = U7_PINS['GND'][0], snap(U7_PINS['GND'][1] + 5.08)  # below U7.GND
GND2_X, GND2_Y = Q1_PINS['E'][0], snap(Q1_PINS['E'][1] + 3.81)  # below Q1.E
GND3_X, GND3_Y = R14_X, snap(R14_P2[1] + 3.81)  # below R14
GND4_X, GND4_Y = C14_X, snap(C14_P2[1] + 3.81)  # below C14

# Port symbols
PORT_LEFT_X = snap(115)
PORT_LEFT_PIN_X = round(PORT_LEFT_X + 2.54, 2)
PORT_RIGHT_X = snap(185)
PORT_RIGHT_PIN_X = round(PORT_RIGHT_X - 2.54, 2)

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
    for port_name in ['RX', 'TX', 'RS485_A', 'RS485_B']:
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
        ("MAX485ESA_T", False),
        ("SS8050_C2150", False),
        ("0805W8F1001T5E", True),
        ("0805W8F4701T5E", True),
        ("CC0805KRX7R9BB104", True),
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

    # +5V
    lib_parts.append("""    (symbol "power:+5V"
      (power)
      (pin_numbers (hide yes))
      (pin_names (offset 0) (hide yes))
      (exclude_from_sim no)
      (in_bom yes)
      (on_board yes)
      (property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide))
      (property "Value" "+5V" (at 0 3.556 0) (effects (font (size 1.27 1.27))))
      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "Description" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (property "ki_keywords" "global power" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
      (symbol "+5V_0_1"
        (polyline (pts (xy -0.762 1.27) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none)))
        (polyline (pts (xy 0 2.54) (xy 0.762 1.27)) (stroke (width 0) (type default)) (fill (type none)))
        (polyline (pts (xy 0 0) (xy 0 2.54)) (stroke (width 0) (type default)) (fill (type none)))
      )
      (symbol "+5V_1_1"
        (pin power_in line (at 0 0 90) (length 0)
          (name "~" (effects (font (size 1.27 1.27))))
          (number "1" (effects (font (size 1.27 1.27))))
        )
      )
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
          (stroke (width 0) (type default)) (fill (type none)))
      )
      (symbol "GND_1_1"
        (pin power_in line (at 0 0 270) (length 0)
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
        (path "/{ROOT_UUID}"
          (reference "{ref}")
          (unit 1)
        )
      )
    )
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
        (path "/{ROOT_UUID}"
          (reference "{ref}")
          (unit 1)
        )
      )
    )
  )"""

    symbols = []

    # U7 — MAX485ESA_T
    symbols.append(make_component("U7", "JLCImport:MAX485ESA_T",
        U7_X, U7_Y, "MAX485",
        footprint="JLCImport:MAX485ESA_T", lcsc="C19738",
        ref_offset=(0, -7.62), val_offset=(0, 7.62)))

    # Q1 — SS8050 NPN (angle=0)
    symbols.append(make_component("Q1", "JLCImport:SS8050_C2150",
        Q1_X, Q1_Y, "SS8050",
        footprint="JLCImport:SS8050_C2150", lcsc="C2150",
        ref_offset=(3.81, -2.54), val_offset=(3.81, 2.54)))

    # R11 — 1k DE/RE# pull-up (vertical angle=90)
    symbols.append(make_component("R11", "JLCImport:0805W8F1001T5E",
        R11_X, R11_Y, "1k", angle=90,
        footprint="JLCImport:0805W8F1001T5E", lcsc="C17513",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # R13 — 4.7k TX to Q1 base (horizontal angle=0)
    symbols.append(make_component("R13", "JLCImport:0805W8F4701T5E",
        R13_X, R13_Y, "4.7k",
        footprint="JLCImport:0805W8F4701T5E", lcsc="C17673",
        ref_offset=(0, -2.54), val_offset=(0, 2.54)))

    # R14 — 4.7k B line pull-down (vertical angle=90)
    symbols.append(make_component("R14", "JLCImport:0805W8F4701T5E",
        R14_X, R14_Y, "4.7k", angle=90,
        footprint="JLCImport:0805W8F4701T5E", lcsc="C17673",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # C14 — 100nF VCC decoupling (vertical angle=90)
    symbols.append(make_component("C14", "JLCImport:CC0805KRX7R9BB104",
        C14_X, C14_Y, "100nF", angle=90,
        footprint="JLCImport:CC0805KRX7R9BB104", lcsc="C49678",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # Power symbols
    symbols.append(make_power("#PWR01", "power:+5V", "+5V", VCC5_X, VCC5_Y))
    for i, (gx, gy) in enumerate([
        (GND1_X, GND1_Y), (GND2_X, GND2_Y), (GND3_X, GND3_Y), (GND4_X, GND4_Y)
    ], start=2):
        symbols.append(make_power(f"#PWR{i:02d}", "power:GND", "GND", gx, gy,
                                   ref_pos=(gx, round(gy + 6.35, 2)),
                                   val_pos=(gx, round(gy + 3.81, 2))))

    # Port symbols — left side: RX, TX; right side: RS485_A, RS485_B (angle=180)
    symbols.append(make_port("#PORT01", "Ports:RX", "RX", PORT_LEFT_X, U7_PINS['RO'][1]))
    symbols.append(make_port("#PORT02", "Ports:TX", "TX", PORT_LEFT_X, U7_PINS['DI'][1]))
    symbols.append(make_port("#PORT03", "Ports:RS485_A", "RS485_A", PORT_RIGHT_X, U7_PINS['A'][1],
                              angle=180, val_pos=(round(PORT_RIGHT_X + 1.905, 2), U7_PINS['A'][1])))
    symbols.append(make_port("#PORT04", "Ports:RS485_B", "RS485_B", PORT_RIGHT_X, U7_PINS['B'][1],
                              angle=180, val_pos=(round(PORT_RIGHT_X + 1.905, 2), U7_PINS['B'][1])))

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

    # RX port → U7.RO
    wires_raw.append(wire(PORT_LEFT_PIN_X, U7_PINS['RO'][1],
                          U7_PINS['RO'][0], U7_PINS['RO'][1]))

    # TX port → U7.DI (also connects to R13 for auto-direction)
    # TX port pin → horizontal to a branch point, then to DI and to R13
    TX_BRANCH_X = R13_P1[0]
    wires_raw.append(wire(PORT_LEFT_PIN_X, U7_PINS['DI'][1],
                          TX_BRANCH_X, U7_PINS['DI'][1]))
    wires_raw.append(wire(TX_BRANCH_X, U7_PINS['DI'][1],
                          U7_PINS['DI'][0], U7_PINS['DI'][1]))
    # TX branch down to R13.P1
    wires_raw.append(wire(TX_BRANCH_X, U7_PINS['DI'][1],
                          TX_BRANCH_X, R13_P1[1]))

    # R13.P2 → Q1.B
    wires_raw.append(wire(R13_P2[0], R13_P2[1], Q1_PINS['B'][0], Q1_PINS['B'][1]))

    # DE/RE# junction: connect RE#, DE, Q1.C, R11.P2
    # U7.RE# → left to DE_RE_X
    wires_raw.append(wire(U7_PINS['RE'][0], U7_PINS['RE'][1],
                          DE_RE_X, U7_PINS['RE'][1]))
    # U7.DE → left to DE_RE_X
    wires_raw.append(wire(U7_PINS['DE'][0], U7_PINS['DE'][1],
                          DE_RE_X, U7_PINS['DE'][1]))
    # Vertical connecting RE and DE at DE_RE_X
    wires_raw.append(wire(DE_RE_X, U7_PINS['RE'][1],
                          DE_RE_X, U7_PINS['DE'][1]))
    # R11.P2 → DE/RE junction (R11 bottom to DE_RE_Y)
    wires_raw.append(wire(R11_P2[0], R11_P2[1], DE_RE_X, DE_RE_Y))
    # Q1.C → DE/RE junction
    wires_raw.append(wire(Q1_PINS['C'][0], Q1_PINS['C'][1], DE_RE_X, DE_RE_Y))

    # R11.P1 → +5V
    wires_raw.append(wire(R11_P1[0], R11_P1[1], VCC5_X, VCC5_Y))

    # Q1.E → GND2
    wires_raw.append(wire(Q1_PINS['E'][0], Q1_PINS['E'][1], GND2_X, GND2_Y))

    # U7.VCC → C14.P1 (horizontal + VCC rail)
    VCC_Y = U7_PINS['VCC'][1]
    wires_raw.append(wire(U7_PINS['VCC'][0], VCC_Y, C14_P1[0], VCC_Y))
    # C14 bottom → GND4
    wires_raw.append(wire(C14_P2[0], C14_P2[1], GND4_X, GND4_Y))

    # U7.GND → GND1
    wires_raw.append(wire(U7_PINS['GND'][0], U7_PINS['GND'][1], GND1_X, GND1_Y))

    # RS485_A port → U7.A
    wires_raw.append(wire(PORT_RIGHT_PIN_X, U7_PINS['A'][1],
                          U7_PINS['A'][0], U7_PINS['A'][1]))

    # RS485_B port → U7.B with R14 tee
    wires_raw.append(wire(PORT_RIGHT_PIN_X, U7_PINS['B'][1],
                          U7_PINS['B'][0], U7_PINS['B'][1]))
    # R14.P1 connects to B wire at R14_X
    wires_raw.append(wire(R14_P1[0], R14_P1[1], R14_X, U7_PINS['B'][1]))
    # R14 bottom → GND3
    wires_raw.append(wire(R14_P2[0], R14_P2[1], GND3_X, GND3_Y))

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
    # TX branch point
    junctions_list.append(junction(TX_BRANCH_X, U7_PINS['DI'][1]))
    # DE/RE junction
    junctions_list.append(junction(DE_RE_X, DE_RE_Y))
    # B wire at R14 tee
    junctions_list.append(junction(R14_X, U7_PINS['B'][1]))

    junctions_str = "\n\n".join(junctions_list)

    # ============================================================
    # ASSEMBLE
    # ============================================================
    schematic = f"""(kicad_sch
  (version 20250114)
  (generator "build_rs485_max485_template.py")
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

    output_path = os.path.join(script_dir, "rs485_max485.kicad_sch")
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
    print(f"Components: U7, Q1, R11, R13, R14, C14")
    print(f"Power symbols: +5V, 4x GND")
    print(f"Ports: RX, TX, RS485_A, RS485_B")
