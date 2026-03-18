"""
Build led_driver_sgm2523a.kicad_sch — SGM2523A current-limited LED driver template.

Components: U1 (SGM2523B), R1 (100k ILIM), C1 (100nF input), C2 (100nF output), C3 (100nF SS)
Power: +12V input, GND
Port: LED+ output

Run: python build_led_driver_template.py
"""

import uuid
import os
import re
import json

def uid():
    return str(uuid.uuid4())

ROOT_UUID = "b4f2a1d3-9e5c-4b6f-ad70-8c3e4f5a6b7c"

def snap(val, grid=1.27):
    return round(round(val / grid) * grid, 2)

# ============================================================
# LAYOUT — all positions on 1.27mm grid
# ============================================================
U1_X, U1_Y = snap(150), snap(100)

# U1 pin endpoints (SGM2523BXN6G_TR, angle=0)
# Pin local (at px py angle): schematic endpoint = (sym_x + px, sym_y - py)
U1_PINS = {
    'IN':       (round(U1_X - 15.24, 2), round(U1_Y - 2.54, 2)),   # pin 1, left
    'GND':      (round(U1_X - 15.24, 2), round(U1_Y, 2)),           # pin 2, left
    'EN_FAULT': (round(U1_X - 15.24, 2), round(U1_Y + 2.54, 2)),   # pin 3, left
    'SS':       (round(U1_X + 15.24, 2), round(U1_Y + 2.54, 2)),   # pin 4, right
    'ILIM':     (round(U1_X + 15.24, 2), round(U1_Y, 2)),           # pin 5, right
    'OUT':      (round(U1_X + 15.24, 2), round(U1_Y - 2.54, 2)),   # pin 6, right
}

IN_Y = U1_PINS['IN'][1]   # VIN rail Y
OUT_Y = U1_PINS['OUT'][1] # VOUT rail Y

# --- INPUT SIDE ---
# C1 (100nF input decoupling, vertical angle=90) left of U1
C1_X = snap(128)
C1_Y = round(IN_Y + 5.08, 2)
C1_P1 = (C1_X, round(C1_Y - 5.08, 2))  # top = VIN rail
C1_P2 = (C1_X, round(C1_Y + 5.08, 2))  # bottom = GND

# EN tied to IN: wire from EN pin back up to VIN rail
EN_CORNER_X = round(U1_PINS['EN_FAULT'][0] - 2.54, 2)

# --- OUTPUT SIDE ---
# R1 (100k ILIM, vertical angle=90) — ILIM pin to GND
R1_X = snap(175)
R1_Y = round(U1_PINS['ILIM'][1] + 3.81, 2)
R1_P1 = (R1_X, round(R1_Y - 3.81, 2))  # top = ILIM net
R1_P2 = (R1_X, round(R1_Y + 3.81, 2))  # bottom = GND

# C3 (100nF soft-start, vertical angle=90) — SS pin to GND
C3_X = snap(180)
C3_Y = round(U1_PINS['SS'][1] + 5.08, 2)
C3_P1 = (C3_X, round(C3_Y - 5.08, 2))  # top = SS net
C3_P2 = (C3_X, round(C3_Y + 5.08, 2))  # bottom = GND

# C2 (100nF output decoupling, vertical angle=90)
C2_X = snap(185)
C2_Y = round(OUT_Y + 5.08, 2)
C2_P1 = (C2_X, round(C2_Y - 5.08, 2))  # top = OUT rail
C2_P2 = (C2_X, round(C2_Y + 5.08, 2))  # bottom = GND

# --- Power symbols ---
VCC12_X, VCC12_Y = snap(126), snap(92)      # +12V above input
GND1_X, GND1_Y = C1_X, snap(112)            # below C1
GND2_X, GND2_Y = U1_PINS['GND'][0], snap(112)  # below U1.GND
GND3_X, GND3_Y = R1_X, snap(112)            # below R1
GND4_X, GND4_Y = C3_X, snap(112)            # below C3
GND5_X, GND5_Y = C2_X, snap(112)            # below C2

# --- Port symbol ---
PORT_X = snap(193)
PORT_PIN_X = round(PORT_X + 2.54, 2)

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
    for port_name in ['LED+']:
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
        ("SGM2523BXN6G_TR", False),          # LED driver IC — keep pin names
        ("0805W8F1003T5E", True),            # 100k resistor — hide pin names
        ("CC0805KRX7R9BB104", True),         # 100nF cap — hide pin names
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

    # +12V power symbol
    lib_parts.append("""    (symbol "power:+12V"
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
      (property "Value" "+12V"
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
      (property "Description" "Power symbol creates a global label with name \\"+12V\\""
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "ki_keywords" "global power"
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (symbol "+12V_0_1"
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
      (symbol "+12V_1_1"
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

    # U1 — SGM2523BXN6G_TR
    symbols.append(make_component("U1", "JLCImport:SGM2523BXN6G_TR",
        U1_X, U1_Y, "SGM2523B",
        footprint="JLCImport:SGM2523BXN6G_TR",
        lcsc="C5153397",
        ref_offset=(0, -8.89), val_offset=(0, 8.89)))

    # R1 — 100k ILIM (vertical angle=90)
    symbols.append(make_component("R1", "JLCImport:0805W8F1003T5E",
        R1_X, R1_Y, "100k", angle=90,
        footprint="JLCImport:0805W8F1003T5E", lcsc="C17407",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # C1 — 100nF input decoupling (vertical angle=90)
    symbols.append(make_component("C1", "JLCImport:CC0805KRX7R9BB104",
        C1_X, C1_Y, "100nF", angle=90,
        footprint="JLCImport:CC0805KRX7R9BB104", lcsc="C49678",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # C2 — 100nF output decoupling (vertical angle=90)
    symbols.append(make_component("C2", "JLCImport:CC0805KRX7R9BB104",
        C2_X, C2_Y, "100nF", angle=90,
        footprint="JLCImport:CC0805KRX7R9BB104", lcsc="C49678",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # C3 — 100nF soft-start (vertical angle=90)
    symbols.append(make_component("C3", "JLCImport:CC0805KRX7R9BB104",
        C3_X, C3_Y, "100nF", angle=90,
        footprint="JLCImport:CC0805KRX7R9BB104", lcsc="C49678",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # Power symbols
    symbols.append(make_power("#PWR01", "power:+12V", "+12V", VCC12_X, VCC12_Y,
                               ref_pos=(VCC12_X, round(VCC12_Y + 6.35, 2)),
                               val_pos=(VCC12_X, round(VCC12_Y - 3.56, 2))))
    for i, (gx, gy) in enumerate([
        (GND1_X, GND1_Y), (GND2_X, GND2_Y), (GND3_X, GND3_Y),
        (GND4_X, GND4_Y), (GND5_X, GND5_Y)
    ], start=2):
        symbols.append(make_power(f"#PWR{i:02d}", "power:GND", "GND", gx, gy,
                                   ref_pos=(gx, round(gy + 6.35, 2)),
                                   val_pos=(gx, round(gy + 3.81, 2))))

    # LED+ port symbol (right side, using angle=180 so pin faces left)
    symbols.append(make_port("#PORT01", "Ports:LED+", "LED+", PORT_X, OUT_Y,
                              angle=180,
                              val_pos=(round(PORT_X + 1.905, 2), OUT_Y)))

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

    # --- INPUT SIDE ---
    # +12V down to VIN rail
    wires_raw.append(wire(VCC12_X, VCC12_Y, VCC12_X, IN_Y))
    # VIN rail: +12V → C1 top → U1.IN
    wires_raw.append(wire(VCC12_X, IN_Y, C1_P1[0], IN_Y))
    wires_raw.append(wire(C1_P1[0], IN_Y, U1_PINS['IN'][0], IN_Y))

    # EN tied to VIN: L-route from EN pin to VIN rail
    wires_raw.append(wire(U1_PINS['EN_FAULT'][0], U1_PINS['EN_FAULT'][1],
                          EN_CORNER_X, U1_PINS['EN_FAULT'][1]))
    wires_raw.append(wire(EN_CORNER_X, U1_PINS['EN_FAULT'][1],
                          EN_CORNER_X, IN_Y))

    # U1.GND down to GND
    wires_raw.append(wire(U1_PINS['GND'][0], U1_PINS['GND'][1],
                          GND2_X, GND2_Y))

    # C1 bottom to GND
    wires_raw.append(wire(C1_P2[0], C1_P2[1], GND1_X, GND1_Y))

    # --- OUTPUT SIDE ---
    # U1.OUT → output rail → C2 top → LED+ port
    wires_raw.append(wire(U1_PINS['OUT'][0], U1_PINS['OUT'][1],
                          C2_P1[0], OUT_Y))
    wires_raw.append(wire(C2_P1[0], OUT_Y, round(PORT_X - 2.54, 2), OUT_Y))

    # U1.ILIM → R1 top
    wires_raw.append(wire(U1_PINS['ILIM'][0], U1_PINS['ILIM'][1],
                          R1_P1[0], R1_P1[1]))
    # R1 bottom → GND
    wires_raw.append(wire(R1_P2[0], R1_P2[1], GND3_X, GND3_Y))

    # U1.SS → C3 top
    wires_raw.append(wire(U1_PINS['SS'][0], U1_PINS['SS'][1],
                          C3_P1[0], C3_P1[1]))
    # C3 bottom → GND
    wires_raw.append(wire(C3_P2[0], C3_P2[1], GND4_X, GND4_Y))

    # C2 bottom → GND
    wires_raw.append(wire(C2_P2[0], C2_P2[1], GND5_X, GND5_Y))

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
    # VIN rail: at C1 top
    junctions_list.append(junction(C1_P1[0], IN_Y))
    # EN tie on VIN rail
    junctions_list.append(junction(EN_CORNER_X, IN_Y))
    # OUT rail: at C2 top
    junctions_list.append(junction(C2_P1[0], OUT_Y))

    junctions_str = "\n\n".join(junctions_list)

    # ============================================================
    # ASSEMBLE
    # ============================================================
    schematic = f"""(kicad_sch
  (version 20250114)
  (generator "build_led_driver_template.py")
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

    output_path = os.path.join(script_dir, "led_driver_sgm2523a.kicad_sch")
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
    print(f"Components: U1, R1, C1, C2, C3")
    print(f"Power symbols: +12V, 5x GND")
    print(f"Port: LED+")
