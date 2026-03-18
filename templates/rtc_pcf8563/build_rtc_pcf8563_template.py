"""
Build rtc_pcf8563.kicad_sch — PCF8563 I2C RTC with external 32.768kHz crystal,
load capacitors, coin cell backup. All components on 1.27mm grid.

Run: python build_rtc_pcf8563_template.py
"""

import uuid
import os
import re

def uid():
    return str(uuid.uuid4())

ROOT_UUID = "a3c8e1f0-7b2d-4a9e-b5c3-d1e2f3a4b5c6"

def snap(val, grid=1.27):
    return round(round(val / grid) * grid, 2)

# ============================================================
# LAYOUT — all positions on 1.27mm grid
# ============================================================
# U16 center
U16_X, U16_Y = snap(150), snap(100)

# U16 pin endpoints (PCF8563 SO-8, angle=0)
# Pin local (at px py) → schematic (U16_X + px, U16_Y - py)
U16_PINS = {
    'OSCI':    (round(U16_X - 12.7, 2), round(U16_Y - 5.08, 2)),   # pin 1, left
    'OSCO':    (round(U16_X - 12.7, 2), round(U16_Y - 2.54, 2)),   # pin 2, left
    'INT':     (round(U16_X - 12.7, 2), round(U16_Y, 2)),           # pin 3, left
    'VSS':     (round(U16_X - 12.7, 2), round(U16_Y + 2.54, 2)),   # pin 4, left
    'SDA':     (round(U16_X + 12.7, 2), round(U16_Y + 2.54, 2)),   # pin 5, right
    'SCL':     (round(U16_X + 12.7, 2), round(U16_Y, 2)),           # pin 6, right
    'CLKOUT':  (round(U16_X + 12.7, 2), round(U16_Y - 2.54, 2)),   # pin 7, right
    'VDD':     (round(U16_X + 12.7, 2), round(U16_Y - 5.08, 2)),   # pin 8, right
}

# X3 crystal — horizontal, to the left of U16, between OSCI and OSCO
# Place crystal so pin2 aligns with OSCI Y, pin1 extends further left
X3_X = snap(120)
X3_Y = round((U16_PINS['OSCI'][1] + U16_PINS['OSCO'][1]) / 2, 2)
X3_Y = snap(X3_Y)  # snap to grid
X3_P1 = (round(X3_X - 5.08, 2), X3_Y)   # left pin (pin 1 -> OSCI)
X3_P2 = (round(X3_X + 5.08, 2), X3_Y)   # right pin (pin 2 -> OSCO)

# C49 (18pF) — vertical, below X3 pin1, OSCI load cap
C49_X = X3_P1[0]
C49_Y = snap(X3_Y + 10.16)
C49_P1 = (C49_X, round(C49_Y - 5.08, 2))  # top
C49_P2 = (C49_X, round(C49_Y + 5.08, 2))  # bottom

# C50 (18pF) — vertical, below X3 pin2, OSCO load cap
C50_X = X3_P2[0]
C50_Y = snap(X3_Y + 10.16)
C50_P1 = (C50_X, round(C50_Y - 5.08, 2))  # top
C50_P2 = (C50_X, round(C50_Y + 5.08, 2))  # bottom

# C48 (100nF) — vertical, VDD decoupling, right of U16
C48_X = snap(175)
C48_Y = snap(U16_PINS['VDD'][1] + 7.62)
C48_P1 = (C48_X, round(C48_Y - 5.08, 2))  # top -> VDD
C48_P2 = (C48_X, round(C48_Y + 5.08, 2))  # bottom -> GND

# BT1 coin cell — horizontal, right of C48
BT1_X = snap(195)
BT1_Y = U16_PINS['VDD'][1]
BT1_P1 = (round(BT1_X - 5.08, 2), BT1_Y)  # left pin (POS) -> +3.3V
BT1_P2 = (round(BT1_X + 5.08, 2), BT1_Y)  # right pin (NEG) -> GND

# Power symbols
VCC_X, VCC_Y = snap(168), snap(88)          # +3.3V above VDD
GND1_X, GND1_Y = U16_PINS['VSS'][0], snap(108)   # below VSS
GND2_X, GND2_Y = C49_X, snap(C49_P2[1] + 3.81)   # below C49
GND3_X, GND3_Y = C50_X, snap(C50_P2[1] + 3.81)   # below C50
GND4_X, GND4_Y = C48_X, snap(C48_P2[1] + 3.81)   # below C48
GND5_X, GND5_Y = BT1_P2[0], snap(BT1_Y + 7.62)   # below BT1

# Port symbols — SCL and SDA to the right
PORT_SYM_X = snap(175)
PORT_PIN_X = round(PORT_SYM_X + 2.54, 2)
SCL_PORT_Y = U16_PINS['SCL'][1]
SDA_PORT_Y = U16_PINS['SDA'][1]


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
    for port_name in ['SCL', 'SDA']:
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
        ("PCF8563", False),              # RTC IC — keep pin names
        ("X32768_C32346", True),         # crystal — hide pin names
        ("C0805_18pF_C1808", True),      # 18pF cap — hide pin names
        ("CC0805KRX7R9BB104", True),     # 100nF cap — hide pin names
        ("CR2032-BS-2-1", True),         # coin cell — hide pin names
    ]

    with open(jlc_path, 'r', encoding='utf-8') as f:
        content = f.read()

    extracted = {}
    for sym_name, hide_names in needed_symbols:
        sym_text = extract_symbol(content, sym_name)
        if sym_text is None:
            raise ValueError(f"Symbol {sym_name} not found in {jlc_path}")

        # Add JLCImport: prefix
        sym_text = sym_text.replace(
            f'(symbol "{sym_name}"',
            f'(symbol "JLCImport:{sym_name}"',
            1
        )

        # Force pin_numbers hidden
        sym_text = re.sub(
            r'\(pin_numbers[^)]*\)',
            '(pin_numbers (hide yes))',
            sym_text,
            count=1
        )

        # Hide pin_names on passives
        if hide_names:
            sym_text = re.sub(
                r'\(pin_names\s*\([^)]*\)\)',
                '(pin_names (offset 1.016) (hide yes))',
                sym_text,
                count=1
            )

        extracted[sym_name] = sym_text

    return extracted


def build_schematic():
    try:
        jlc_symbols = read_lib_symbols()
    except Exception as e:
        print(f"Warning: Could not read JLCImport.kicad_sym: {e}")
        jlc_symbols = {}

    lib_parts = []
    for sym_text in jlc_symbols.values():
        lib_parts.append(f"    {sym_text}")

    # Power symbols
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

    def make_port(ref, lib_id, value, x, y, val_pos=None):
        if val_pos is None:
            val_pos = (round(x - 1.905, 2), y)
        return f"""  (symbol
    (lib_id "{lib_id}")
    (at {x} {y} 0)
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

    # U16 — PCF8563 (ref above, value below)
    symbols.append(make_component("U16", "JLCImport:PCF8563",
        U16_X, U16_Y, "PCF8563",
        footprint="JLCImport:PCF8563",
        lcsc="C5795601",
        ref_offset=(0, -10.16), val_offset=(0, 10.16)))

    # X3 — 32.768kHz crystal (horizontal)
    symbols.append(make_component("X3", "JLCImport:X32768_C32346",
        X3_X, X3_Y, "32.768kHz",
        footprint="JLCImport:X32768_C32346", lcsc="C32346",
        ref_offset=(0, -3.81), val_offset=(0, 3.81)))

    # C49 — 18pF OSCI load cap (vertical, angle=90)
    symbols.append(make_component("C49", "JLCImport:C0805_18pF_C1808",
        C49_X, C49_Y, "18pF", angle=90,
        footprint="JLCImport:CC0805KRX7R9BB104", lcsc="C1808",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # C50 — 18pF OSCO load cap (vertical, angle=90)
    symbols.append(make_component("C50", "JLCImport:C0805_18pF_C1808",
        C50_X, C50_Y, "18pF", angle=90,
        footprint="JLCImport:CC0805KRX7R9BB104", lcsc="C1808",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # C48 — 100nF VDD decoupling (vertical, angle=90)
    symbols.append(make_component("C48", "JLCImport:CC0805KRX7R9BB104",
        C48_X, C48_Y, "100nF", angle=90,
        footprint="JLCImport:CC0805KRX7R9BB104", lcsc="C49678",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # BT1 — coin cell holder (horizontal)
    symbols.append(make_component("BT1", "JLCImport:CR2032-BS-2-1",
        BT1_X, BT1_Y, "CR1220",
        footprint="JLCImport:CR2032-BS-2-1", lcsc="C70376",
        ref_offset=(0, -3.81), val_offset=(0, 3.81)))

    # Power symbols
    symbols.append(make_power("#PWR01", "power:+3.3V", "+3.3V", VCC_X, VCC_Y))
    symbols.append(make_power("#PWR02", "power:GND", "GND", GND1_X, GND1_Y))
    symbols.append(make_power("#PWR03", "power:GND", "GND", GND2_X, GND2_Y))
    symbols.append(make_power("#PWR04", "power:GND", "GND", GND3_X, GND3_Y))
    symbols.append(make_power("#PWR05", "power:GND", "GND", GND4_X, GND4_Y))
    symbols.append(make_power("#PWR06", "power:GND", "GND", GND5_X, GND5_Y))

    # Port symbols — SCL and SDA
    symbols.append(make_port("#PORT01", "Ports:SCL", "SCL", PORT_SYM_X, SCL_PORT_Y))
    symbols.append(make_port("#PORT02", "Ports:SDA", "SDA", PORT_SYM_X, SDA_PORT_Y))

    symbols_str = "\n\n".join(symbols)

    # ============================================================
    # NO-CONNECTS
    # ============================================================
    def no_connect(x, y):
        return f"""  (no_connect (at {x} {y})
    (uuid "{uid()}")
  )"""

    no_connects_list = [
        no_connect(U16_PINS['INT'][0], U16_PINS['INT'][1]),
        no_connect(U16_PINS['CLKOUT'][0], U16_PINS['CLKOUT'][1]),
    ]
    no_connects_str = "\n\n".join(no_connects_list)

    # ============================================================
    # WIRES
    # ============================================================
    def wire(x1, y1, x2, y2):
        return f"""  (wire (pts (xy {x1} {y1}) (xy {x2} {y2}))
    (stroke (width 0) (type default))
    (uuid "{uid()}")
  )"""

    def junction(x, y):
        return f"""  (junction (at {x} {y})
    (diameter 0)
    (color 0 0 0 0)
    (uuid "{uid()}")
  )"""

    wires = []
    junctions = []

    # --- Crystal wiring ---
    # OSCI (pin 1) -> horizontal left to corner -> vertical to X3.P1
    OSCI_CORNER_X = X3_P1[0]
    wires.append(wire(U16_PINS['OSCI'][0], U16_PINS['OSCI'][1],
                       OSCI_CORNER_X, U16_PINS['OSCI'][1]))
    wires.append(wire(OSCI_CORNER_X, U16_PINS['OSCI'][1],
                       OSCI_CORNER_X, X3_Y))
    # X3.P1 is at OSCI_CORNER_X, X3_Y — junction where C49 tees off
    junctions.append(junction(OSCI_CORNER_X, X3_Y))

    # OSCO (pin 2) -> horizontal left to corner -> vertical to X3.P2
    OSCO_CORNER_X = X3_P2[0]
    wires.append(wire(U16_PINS['OSCO'][0], U16_PINS['OSCO'][1],
                       OSCO_CORNER_X, U16_PINS['OSCO'][1]))
    wires.append(wire(OSCO_CORNER_X, U16_PINS['OSCO'][1],
                       OSCO_CORNER_X, X3_Y))
    # X3.P2 is at OSCO_CORNER_X, X3_Y — junction where C50 tees off
    junctions.append(junction(OSCO_CORNER_X, X3_Y))

    # C49 top (pin1) connects to OSCI net at X3.P1
    wires.append(wire(C49_P1[0], C49_P1[1], X3_P1[0], X3_Y))
    # C49 bottom (pin2) -> GND2
    wires.append(wire(C49_P2[0], C49_P2[1], GND2_X, GND2_Y))

    # C50 top (pin1) connects to OSCO net at X3.P2
    wires.append(wire(C50_P1[0], C50_P1[1], X3_P2[0], X3_Y))
    # C50 bottom (pin2) -> GND3
    wires.append(wire(C50_P2[0], C50_P2[1], GND3_X, GND3_Y))

    # --- VDD wiring ---
    # +3.3V -> horizontal to VDD pin
    VDD_WIRE_Y = U16_PINS['VDD'][1]
    wires.append(wire(VCC_X, VCC_Y, VCC_X, VDD_WIRE_Y))
    wires.append(wire(VCC_X, VDD_WIRE_Y, U16_PINS['VDD'][0], VDD_WIRE_Y))
    # Junction at VCC_X, VDD_WIRE_Y for C48 tee
    junctions.append(junction(VCC_X, VDD_WIRE_Y))

    # C48 top -> vertical down to VDD wire Y level
    wires.append(wire(C48_P1[0], C48_P1[1], C48_P1[0], VDD_WIRE_Y))
    # Junction where C48 meets the BT1-to-VCC horizontal wire
    junctions.append(junction(C48_P1[0], VDD_WIRE_Y))
    # C48 bottom -> GND4
    wires.append(wire(C48_P2[0], C48_P2[1], GND4_X, GND4_Y))

    # --- BT1 wiring ---
    # BT1.POS (pin1) connects to VDD wire
    wires.append(wire(BT1_P1[0], BT1_P1[1], VCC_X, VDD_WIRE_Y))
    # BT1.NEG (pin2) -> GND5 (vertical down)
    wires.append(wire(BT1_P2[0], BT1_P2[1], GND5_X, GND5_Y))

    # --- VSS wiring ---
    wires.append(wire(U16_PINS['VSS'][0], U16_PINS['VSS'][1], GND1_X, GND1_Y))

    # --- SCL port wiring ---
    wires.append(wire(PORT_PIN_X, SCL_PORT_Y, U16_PINS['SCL'][0], U16_PINS['SCL'][1]))

    # --- SDA port wiring ---
    wires.append(wire(PORT_PIN_X, SDA_PORT_Y, U16_PINS['SDA'][0], U16_PINS['SDA'][1]))

    wires_str = "\n\n".join(wires)
    junctions_str = "\n\n".join(junctions)

    # ============================================================
    # ASSEMBLE
    # ============================================================
    schematic = f"""(kicad_sch
  (version 20250114)
  (generator "build_rtc_pcf8563_template.py")
  (generator_version "9.0")
  (uuid "{ROOT_UUID}")
  (paper "A4")

  (lib_symbols
{lib_symbols_str}
  )

{junctions_str}

{no_connects_str}

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
        "rtc_pcf8563.kicad_sch"
    )
    content = build_schematic()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Written: {output_path}")
    print(f"Components: U16, X3, C49, C50, C48, BT1")
    print(f"Power symbols: +3.3V, 5x GND")
    print(f"Ports: SCL, SDA")
    print(f"No-connects: INT# (pin 3), CLKOUT (pin 7)")
