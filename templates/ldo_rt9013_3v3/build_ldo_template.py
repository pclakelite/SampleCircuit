"""
Build ldo_rt9013_3v3.kicad_sch — RT9013-33GB 5V to 3.3V LDO template.

Components: U15 (RT9013-33GB), D5 (1SMA4729A Zener), C40-C43 (decoupling)
Power: +5V input, +3.3V output, GND
No signal ports — pure power supply module.

Run: python build_ldo_template.py
"""

import uuid
import os
import re
import json

def uid():
    return str(uuid.uuid4())

ROOT_UUID = "a3e1f0c2-8d4b-4a5e-9c6f-7b2d3e4f5a6b"

def snap(val, grid=1.27):
    """Snap a value to the nearest 1.27mm grid point."""
    return round(round(val / grid) * grid, 2)

# ============================================================
# LAYOUT — all positions on 1.27mm grid
# ============================================================
# U15 center
U15_X, U15_Y = snap(150), snap(100)  # (149.86, 100.33)

# U15 pin endpoints (RT9013-33GB, angle=0)
# Pin local (at px py angle): schematic endpoint = (sym_x + px, sym_y - py)
U15_PINS = {
    'VIN':  (round(U15_X - 11.43, 2), round(U15_Y - 5.08, 2)),   # pin 1, left
    'GND':  (round(U15_X - 11.43, 2), round(U15_Y, 2)),           # pin 2, left
    'EN':   (round(U15_X - 11.43, 2), round(U15_Y + 5.08, 2)),   # pin 3, left
    'NC':   (round(U15_X + 11.43, 2), round(U15_Y + 2.54, 2)),   # pin 4, right
    'VOUT': (round(U15_X + 11.43, 2), round(U15_Y - 2.54, 2)),   # pin 5, right
}

# --- INPUT SIDE (left of U15) ---
# Input caps: C42 (10uF) and C43 (100nF), vertical, stacked on VIN rail
# VIN rail runs horizontally at U15_PINS['VIN'] Y level
VIN_Y = U15_PINS['VIN'][1]  # 95.25

# C42 (10uF, vertical angle=90) — input bulk cap
# pin1=top (VIN), pin2=bottom (GND)
C42_X = snap(130)
C42_Y = round(VIN_Y + 5.08, 2)  # center offset so pin1 lands on VIN rail
C42_P1 = (C42_X, round(C42_Y - 5.08, 2))  # top = VIN rail
C42_P2 = (C42_X, round(C42_Y + 5.08, 2))  # bottom = GND

# C43 (100nF, vertical angle=90) — input decoupling
C43_X = snap(135)
C43_Y = C42_Y
C43_P1 = (C43_X, round(C43_Y - 5.08, 2))  # top = VIN rail
C43_P2 = (C43_X, round(C43_Y + 5.08, 2))  # bottom = GND

# --- OUTPUT SIDE (right of U15) ---
VOUT_Y = U15_PINS['VOUT'][1]  # 97.79

# D5 (1SMA4729A Zener, horizontal angle=0)
# Pin 1 = K (cathode) at left (-5.08), Pin 2 = A (anode) at right (+5.08)
# Cathode on VOUT rail, Anode down to GND
# Place diode vertical (angle=90): pin1=top(cathode=VOUT), pin2=bottom(anode=GND)
D5_X = snap(175)
D5_Y = round(VOUT_Y + 5.08, 2)
D5_P1 = (D5_X, round(D5_Y - 5.08, 2))  # cathode = VOUT rail
D5_P2 = (D5_X, round(D5_Y + 5.08, 2))  # anode = GND

# C41 (10uF, vertical angle=90) — output bulk cap
C41_X = snap(180)
C41_Y = round(VOUT_Y + 5.08, 2)
C41_P1 = (C41_X, round(C41_Y - 5.08, 2))  # top = VOUT rail
C41_P2 = (C41_X, round(C41_Y + 5.08, 2))  # bottom = GND

# C40 (100nF, vertical angle=90) — output decoupling
C40_X = snap(185)
C40_Y = C41_Y
C40_P1 = (C40_X, round(C40_Y - 5.08, 2))  # top = VOUT rail
C40_P2 = (C40_X, round(C40_Y + 5.08, 2))  # bottom = GND

# --- EN tie to VIN ---
# EN (pin 3) needs to wire back up to VIN rail
EN_CORNER_X = U15_PINS['EN'][0]  # same X as EN pin

# --- Power symbols ---
VCC5_X, VCC5_Y = snap(128), snap(90)        # +5V above input caps
VCC33_X, VCC33_Y = snap(187), snap(92)      # +3.3V above output caps
GND1_X, GND1_Y = C42_X, snap(112)           # GND below C42
GND2_X, GND2_Y = C43_X, snap(112)           # GND below C43
GND3_X, GND3_Y = U15_PINS['GND'][0], snap(112)  # GND below U15.GND
GND4_X, GND4_Y = D5_X, snap(112)            # GND below D5
GND5_X, GND5_Y = C41_X, snap(112)           # GND below C41
GND6_X, GND6_Y = C40_X, snap(112)           # GND below C40

# ============================================================
# LIB_SYMBOLS
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


def read_lib_symbols():
    """Read the lib_symbols section from the project's libraries."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    jlc_path = os.path.join(project_root, "JLCImport.kicad_sym")

    needed_symbols = [
        ("RT9013-33GB", False),              # LDO — keep pin names
        ("1SMA4729A", True),                 # Zener diode — hide pin names
        ("CL21A106KAYNNNE", True),           # 10uF cap — hide pin names
        ("CC0805KRX7R9BB104", True),         # 100nF cap — hide pin names
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

        # Force (pin_numbers (hide yes)) on ALL symbols
        sym_text = re.sub(
            r'\(pin_numbers[^)]*\)',
            '(pin_numbers (hide yes))',
            sym_text,
            count=1
        )

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
    jlc_symbols = read_lib_symbols()

    lib_parts = []
    for sym_text in jlc_symbols.values():
        lib_parts.append(f"    {sym_text}")

    # Power symbols
    lib_parts.append("""    (symbol "power:+5V"
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
      (property "Value" "+5V"
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
      (property "Description" "Power symbol creates a global label with name \\"+5V\\""
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (property "ki_keywords" "global power"
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (symbol "+5V_0_1"
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
      (symbol "+5V_1_1"
        (pin power_in line
          (at 0 0 90)
          (length 0)
          (name "~" (effects (font (size 1.27 1.27))))
          (number "1" (effects (font (size 1.27 1.27))))
        )
      )
      (embedded_fonts no)
    )""")

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

    symbols = []

    # U15 — RT9013-33GB LDO (ref above, value below)
    symbols.append(make_component("U15", "JLCImport:RT9013-33GB",
        U15_X, U15_Y, "RT9013-33GB",
        footprint="JLCImport:RT9013-33GB",
        lcsc="C47773",
        ref_offset=(0, -10.16), val_offset=(0, 10.16)))

    # D5 — 1SMA4729A Zener (vertical angle=90, cathode=top=VOUT, anode=bottom=GND)
    # For diode at angle=90: pin1(K) at top (cx, cy-5.08), pin2(A) at bottom (cx, cy+5.08)
    symbols.append(make_component("D5", "JLCImport:1SMA4729A",
        D5_X, D5_Y, "3.6V",
        footprint="JLCImport:1SMA4729A",
        lcsc="C145089", angle=90,
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # C42 — 10uF input bulk (vertical angle=90)
    symbols.append(make_component("C42", "JLCImport:CL21A106KAYNNNE",
        C42_X, C42_Y, "10uF", angle=90,
        footprint="JLCImport:CL21A106KAYNNNE", lcsc="C15850",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # C43 — 100nF input decoupling (vertical angle=90)
    symbols.append(make_component("C43", "JLCImport:CC0805KRX7R9BB104",
        C43_X, C43_Y, "100nF", angle=90,
        footprint="JLCImport:CC0805KRX7R9BB104", lcsc="C49678",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # C41 — 10uF output bulk (vertical angle=90)
    symbols.append(make_component("C41", "JLCImport:CL21A106KAYNNNE",
        C41_X, C41_Y, "10uF", angle=90,
        footprint="JLCImport:CL21A106KAYNNNE", lcsc="C15850",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # C40 — 100nF output decoupling (vertical angle=90)
    symbols.append(make_component("C40", "JLCImport:CC0805KRX7R9BB104",
        C40_X, C40_Y, "100nF", angle=90,
        footprint="JLCImport:CC0805KRX7R9BB104", lcsc="C49678",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # Power symbols
    symbols.append(make_power("#PWR01", "power:+5V", "+5V", VCC5_X, VCC5_Y,
                               ref_pos=(VCC5_X, round(VCC5_Y + 6.35, 2)),
                               val_pos=(VCC5_X, round(VCC5_Y - 3.56, 2))))
    symbols.append(make_power("#PWR02", "power:+3.3V", "+3.3V", VCC33_X, VCC33_Y,
                               ref_pos=(VCC33_X, round(VCC33_Y + 6.35, 2)),
                               val_pos=(VCC33_X, round(VCC33_Y - 3.56, 2))))
    # GND symbols (one under each cap pair column, one under U15.GND, one under D5)
    for i, (gx, gy) in enumerate([
        (GND1_X, GND1_Y), (GND2_X, GND2_Y), (GND3_X, GND3_Y),
        (GND4_X, GND4_Y), (GND5_X, GND5_Y), (GND6_X, GND6_Y)
    ], start=3):
        symbols.append(make_power(f"#PWR{i:02d}", "power:GND", "GND", gx, gy,
                                   ref_pos=(gx, round(gy + 6.35, 2)),
                                   val_pos=(gx, round(gy + 3.81, 2))))

    symbols_str = "\n\n".join(symbols)

    # ============================================================
    # NO-CONNECTS
    # ============================================================
    nc_pin = U15_PINS['NC']
    no_connects = f"""  (no_connect (at {nc_pin[0]} {nc_pin[1]})
    (uuid "{uid()}")
  )"""

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
    # +5V symbol down to VIN rail Y
    wires_raw.append(wire(VCC5_X, VCC5_Y, VCC5_X, VIN_Y))
    # VIN rail: +5V position → C42 top → C43 top → U15.VIN
    wires_raw.append(wire(VCC5_X, VIN_Y, C42_P1[0], VIN_Y))
    wires_raw.append(wire(C42_P1[0], VIN_Y, C43_P1[0], VIN_Y))
    wires_raw.append(wire(C43_P1[0], VIN_Y, U15_PINS['VIN'][0], VIN_Y))

    # EN tied to VIN: wire from U15.EN up to VIN rail
    # L-route: EN pin left → corner → up to VIN rail
    EN_CORNER_X2 = round(U15_PINS['EN'][0] - 2.54, 2)
    wires_raw.append(wire(U15_PINS['EN'][0], U15_PINS['EN'][1],
                          EN_CORNER_X2, U15_PINS['EN'][1]))
    wires_raw.append(wire(EN_CORNER_X2, U15_PINS['EN'][1],
                          EN_CORNER_X2, VIN_Y))

    # U15.GND → GND3 (vertical down)
    wires_raw.append(wire(U15_PINS['GND'][0], U15_PINS['GND'][1],
                          GND3_X, GND3_Y))

    # Input cap GND: C42 bottom → GND1
    wires_raw.append(wire(C42_P2[0], C42_P2[1], GND1_X, GND1_Y))
    # C43 bottom → GND2
    wires_raw.append(wire(C43_P2[0], C43_P2[1], GND2_X, GND2_Y))

    # --- OUTPUT SIDE ---
    # U15.VOUT → VOUT rail: horizontal right to output components
    wires_raw.append(wire(U15_PINS['VOUT'][0], U15_PINS['VOUT'][1],
                          U15_PINS['VOUT'][0], VOUT_Y))
    wires_raw.append(wire(U15_PINS['VOUT'][0], VOUT_Y, D5_P1[0], VOUT_Y))
    wires_raw.append(wire(D5_P1[0], VOUT_Y, C41_P1[0], VOUT_Y))
    wires_raw.append(wire(C41_P1[0], VOUT_Y, C40_P1[0], VOUT_Y))

    # +3.3V symbol down to VOUT rail
    wires_raw.append(wire(VCC33_X, VCC33_Y, VCC33_X, VOUT_Y))

    # Output cap/diode GND
    wires_raw.append(wire(D5_P2[0], D5_P2[1], GND4_X, GND4_Y))
    wires_raw.append(wire(C41_P2[0], C41_P2[1], GND5_X, GND5_Y))
    wires_raw.append(wire(C40_P2[0], C40_P2[1], GND6_X, GND6_Y))

    wires = [w for w in wires_raw if w is not None]
    wires_str = "\n\n".join(wires)

    # ============================================================
    # JUNCTIONS (where wires T-connect on the rails)
    # ============================================================
    def junction(x, y):
        return f"""  (junction (at {x} {y})
    (diameter 0)
    (color 0 0 0 0)
    (uuid "{uid()}")
  )"""

    junctions_list = []
    # VIN rail junctions: at C42, C43 tops
    junctions_list.append(junction(C42_P1[0], VIN_Y))
    junctions_list.append(junction(C43_P1[0], VIN_Y))
    # EN tie junction on VIN rail
    junctions_list.append(junction(EN_CORNER_X2, VIN_Y))
    # VOUT rail junctions: at D5, C41 tops
    junctions_list.append(junction(D5_P1[0], VOUT_Y))
    junctions_list.append(junction(C41_P1[0], VOUT_Y))
    # +3.3V junction on VOUT rail
    junctions_list.append(junction(VCC33_X, VOUT_Y))

    junctions_str = "\n\n".join(junctions_list)

    # ============================================================
    # ASSEMBLE
    # ============================================================
    schematic = f"""(kicad_sch
  (version 20250114)
  (generator "build_ldo_template.py")
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
    # Check status.json
    script_dir = os.path.dirname(os.path.abspath(__file__))
    status_path = os.path.join(script_dir, "status.json")
    if os.path.exists(status_path):
        with open(status_path, 'r') as f:
            status = json.load(f)
        if status.get("status") == "locked":
            print(f"ERROR: Template is LOCKED. Cannot regenerate.")
            exit(1)

    output_path = os.path.join(script_dir, "ldo_rt9013_3v3.kicad_sch")
    content = build_schematic()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    # Update status to review
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
    print(f"Components: U15, D5, C40, C41, C42, C43")
    print(f"Power symbols: +5V, +3.3V, 6x GND")
    print(f"No-connect: pin 4 (NC)")
    print(f"All positions on 1.27mm grid")
    print(f"\nLayout:")
    print(f"  U15 at ({U15_X}, {U15_Y})")
    print(f"  C42 at ({C42_X}, {C42_Y}) angle=90")
    print(f"  C43 at ({C43_X}, {C43_Y}) angle=90")
    print(f"  D5  at ({D5_X}, {D5_Y}) angle=90")
    print(f"  C41 at ({C41_X}, {C41_Y}) angle=90")
    print(f"  C40 at ({C40_X}, {C40_Y}) angle=90")
