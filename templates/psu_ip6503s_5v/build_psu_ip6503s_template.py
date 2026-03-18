"""
Build psu_ip6503s_5v.kicad_sch — IP6503S 12V to 5V buck regulator template.
TVS protection, external inductor, bootstrap cap, input/output electrolytics.

Run: python build_psu_ip6503s_template.py
"""

import uuid
import os
import re

def uid():
    return str(uuid.uuid4())

ROOT_UUID = "c5e0a3b2-9d4f-6c1a-d7e5-f3a4b6c8d9e0"

def snap(val, grid=1.27):
    return round(round(val / grid) * grid, 2)

# ============================================================
# LAYOUT
# ============================================================
U10_X, U10_Y = snap(150), snap(100)

# IP6503S pin endpoints (angle=0)
# Pin local (at px py) → schematic (U10_X + px, U10_Y - py)
U10_PINS = {
    'VIN':  (round(U10_X - 10.16, 2), round(U10_Y - 2.54, 2)),   # pin 1, left
    'NC':   (round(U10_X - 10.16, 2), round(U10_Y, 2)),            # pin 2, left
    'DP':   (round(U10_X - 10.16, 2), round(U10_Y + 2.54, 2)),   # pin 3, left
    'DM':   (round(U10_X - 10.16, 2), round(U10_Y + 5.08, 2)),   # pin 4, left
    'VOUT': (round(U10_X + 10.16, 2), round(U10_Y + 5.08, 2)),   # pin 5, right
    'GND6': (round(U10_X + 10.16, 2), round(U10_Y + 2.54, 2)),   # pin 6, right
    'SW':   (round(U10_X + 10.16, 2), round(U10_Y, 2)),            # pin 7, right
    'BST':  (round(U10_X + 10.16, 2), round(U10_Y - 2.54, 2)),   # pin 8, right
    'EP':   (round(U10_X + 10.16, 2), round(U10_Y - 5.08, 2)),   # pin 9, right
}

# D3 TVS diode — vertical stub off VIN rail to GND
D3_X = snap(U10_PINS['VIN'][0] - 10.16)
D3_VIN_Y = U10_PINS['VIN'][1]             # VIN rail Y level
D3_Y = snap(D3_VIN_Y + 5.08)             # center below VIN rail
# angle=90: pin1(K) at bottom (sym_y+5.08), pin2(A) at top (sym_y-5.08)
D3_P1 = (D3_X, round(D3_Y + 5.08, 2))   # pin 1 bottom -> GND
D3_P2 = (D3_X, round(D3_Y - 5.08, 2))   # pin 2 top -> VIN rail

# C34 input bulk 100uF — vertical, at left end of VIN rail
# Electrolytic: pin1(+) at top (y - 3.81), pin2(-) at bottom (y + 3.81)
C34_X = snap(U10_PINS['VIN'][0] - 20.32)
C34_Y = snap(D3_VIN_Y + 10.16)
C34_P1 = (C34_X, round(C34_Y - 3.81, 2))  # + top
C34_P2 = (C34_X, round(C34_Y + 3.81, 2))  # - bottom

# L4 inductor — horizontal, to the right of SW pin
L4_X = snap(U10_PINS['SW'][0] + 12.7)
L4_Y = U10_PINS['SW'][1]
L4_P1 = (round(L4_X - 5.08, 2), L4_Y)  # pin 1 -> SW
L4_P2 = (round(L4_X + 5.08, 2), L4_Y)  # pin 2 -> VOUT

# C29 bootstrap cap — vertical (angle=90), between BST and SW
# Ceramic cap at angle=90: pin1 at bottom (y+5.08), pin2 at top (y-5.08)
C29_X = L4_P1[0]  # align with L4 pin 1 on SW wire
C29_Y = snap(U10_PINS['BST'][1] + 1.27)  # between BST and SW
C29_P1 = (C29_X, round(C29_Y - 5.08, 2))  # top -> BST
C29_P2 = (C29_X, round(C29_Y + 5.08, 2))  # bottom -> SW

# VOUT rail junction — where L4 output meets VOUT wire
VOUT_X = L4_P2[0]
VOUT_Y = L4_Y

# C30 output bulk 470uF — vertical, at VOUT
C30_X = VOUT_X
C30_Y = snap(VOUT_Y + 10.16)
C30_P1 = (C30_X, round(C30_Y - 3.81, 2))  # + top
C30_P2 = (C30_X, round(C30_Y + 3.81, 2))  # - bottom

# Power symbols
VIN_PWR_X = C34_X
VIN_PWR_Y = snap(D3_VIN_Y - 5.08)

VOUT_PWR_X = VOUT_X
VOUT_PWR_Y = snap(VOUT_Y - 5.08)

# GND symbols
GND1_X, GND1_Y = C34_X, snap(C34_P2[1] + 3.81)         # below C34
GND2_X, GND2_Y = D3_X, snap(D3_P1[1] + 3.81)            # below D3 bottom (TVS to GND)
GND3_X, GND3_Y = U10_PINS['GND6'][0], snap(U10_PINS['GND6'][1] + 5.08)  # below pin 6
GND4_X, GND4_Y = U10_PINS['EP'][0], snap(U10_PINS['EP'][1] - 5.08)      # above EP (pin 9)
GND5_X, GND5_Y = C30_X, snap(C30_P2[1] + 3.81)          # below C30

# Wait — EP is at top-right (y - 5.08 from center). Let me recalculate.
# EP pin endpoint is at (U10_X + 10.16, U10_Y - 5.08) which is above center.
# GND should go UP from EP or to the right. Let's put GND to the right (rotated 90).
GND4_X = snap(U10_PINS['EP'][0] + 5.08)
GND4_Y = U10_PINS['EP'][1]


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


def read_lib_symbols():
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    jlc_path = os.path.join(project_root, "JLCImport.kicad_sym")

    needed_symbols = [
        ("IP6503S-3_1A", False),           # Buck controller — keep pin names
        ("SMBJ16CA_C284001", True),        # TVS diode
        ("L_10uH_C408335", True),          # Inductor
        ("ECAP_100uF_50V_C2992088", True), # Input electrolytic
        ("ECAP_470uF_6V3_C2891466", True), # Output electrolytic
        ("CC0805KRX7R9BB104", True),       # 100nF bootstrap cap
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
    try:
        jlc_symbols = read_lib_symbols()
    except Exception as e:
        print(f"Error reading symbols: {e}")
        raise

    lib_parts = []
    for sym_text in jlc_symbols.values():
        lib_parts.append(f"    {sym_text}")

    # Power symbols: +12V, +5V, GND
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
    # HELPERS
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

    symbols = []

    # U10 — IP6503S
    symbols.append(make_component("U10", "JLCImport:IP6503S-3_1A",
        U10_X, U10_Y, "IP6503S",
        footprint="JLCImport:IP6503S-3_1A", lcsc="C432571",
        ref_offset=(0, -12.7), val_offset=(0, 12.7)))

    # D3 — SMBJ16CA TVS (vertical stub)
    symbols.append(make_component("D3", "JLCImport:SMBJ16CA_C284001",
        D3_X, D3_Y, "SMBJ16CA", angle=90,
        footprint="JLCImport:SMBJ16CA_C284001", lcsc="C284001",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # L4 — 10uH inductor (horizontal)
    symbols.append(make_component("L4", "JLCImport:L_10uH_C408335",
        L4_X, L4_Y, "10uH",
        footprint="JLCImport:PNLS6045-330", lcsc="C408335",
        ref_offset=(0, -3.81), val_offset=(0, 3.81)))

    # C29 — 100nF bootstrap (vertical, angle=90)
    symbols.append(make_component("C29", "JLCImport:CC0805KRX7R9BB104",
        C29_X, C29_Y, "100nF", angle=90,
        footprint="JLCImport:CC0805KRX7R9BB104", lcsc="C49678",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # C34 — 100uF input electrolytic (vertical, angle=0)
    # Electrolytic pins: pin1(+) at (0, 3.81) top, pin2(-) at (0, -3.81) bottom
    # With angle=0: pin1 at (x, y-3.81), pin2 at (x, y+3.81)
    symbols.append(make_component("C34", "JLCImport:ECAP_100uF_50V_C2992088",
        C34_X, C34_Y, "100uF",
        footprint="JLCImport:HV221M025F105R", lcsc="C2992088",
        ref_offset=(3.81, 0), val_offset=(0, 5.08)))

    # C30 — 470uF output electrolytic (vertical, angle=0)
    symbols.append(make_component("C30", "JLCImport:ECAP_470uF_6V3_C2891466",
        C30_X, C30_Y, "470uF",
        footprint="JLCImport:EEEFT1V681UP", lcsc="C2891466",
        ref_offset=(3.81, 0), val_offset=(0, 5.08)))

    # Power symbols
    symbols.append(make_power("#PWR01", "power:+12V", "+12V", VIN_PWR_X, VIN_PWR_Y))
    symbols.append(make_power("#PWR02", "power:+5V", "+5V", VOUT_PWR_X, VOUT_PWR_Y))
    symbols.append(make_power("#PWR03", "power:GND", "GND", GND1_X, GND1_Y))
    symbols.append(make_power("#PWR04", "power:GND", "GND", GND2_X, GND2_Y))
    symbols.append(make_power("#PWR05", "power:GND", "GND", GND3_X, GND3_Y))
    symbols.append(make_power("#PWR06", "power:GND", "GND", GND4_X, GND4_Y, angle=90))
    symbols.append(make_power("#PWR07", "power:GND", "GND", GND5_X, GND5_Y))

    symbols_str = "\n\n".join(symbols)

    # ============================================================
    # NO-CONNECTS
    # ============================================================
    def no_connect(x, y):
        return f"""  (no_connect (at {x} {y})
    (uuid "{uid()}")
  )"""

    nc_list = [
        no_connect(U10_PINS['NC'][0], U10_PINS['NC'][1]),
        no_connect(U10_PINS['DP'][0], U10_PINS['DP'][1]),
        no_connect(U10_PINS['DM'][0], U10_PINS['DM'][1]),
    ]
    nc_str = "\n\n".join(nc_list)

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

    # --- VIN rail ---
    # +12V -> down to VIN rail level
    VIN_JCT_Y = D3_VIN_Y
    wires.append(wire(VIN_PWR_X, VIN_PWR_Y, VIN_PWR_X, VIN_JCT_Y))
    # Junction at VIN rail for C34 tee
    junctions.append(junction(VIN_PWR_X, VIN_JCT_Y))
    # C34+ -> VIN junction
    wires.append(wire(C34_P1[0], C34_P1[1], VIN_PWR_X, VIN_JCT_Y))
    # C34- -> GND1
    wires.append(wire(C34_P2[0], C34_P2[1], GND1_X, GND1_Y))

    # VIN rail: horizontal from junction to U10.VIN
    # D3 vertical stub tees off this wire
    wires.append(wire(VIN_PWR_X, VIN_JCT_Y, U10_PINS['VIN'][0], U10_PINS['VIN'][1]))
    # D3.P2 (top) sits on VIN rail — junction for tee
    junctions.append(junction(D3_P2[0], D3_P2[1]))
    # D3.P1 (bottom) -> GND2
    wires.append(wire(D3_P1[0], D3_P1[1], GND2_X, GND2_Y))

    # --- SW node ---
    # U10.SW -> L4.P1
    wires.append(wire(U10_PINS['SW'][0], U10_PINS['SW'][1], L4_P1[0], L4_P1[1]))

    # --- Bootstrap ---
    # U10.BST -> horizontal to C29 top area
    BST_WIRE_X = C29_X
    wires.append(wire(U10_PINS['BST'][0], U10_PINS['BST'][1], BST_WIRE_X, U10_PINS['BST'][1]))
    # C29 top (pin1) -> BST wire
    wires.append(wire(C29_P1[0], C29_P1[1], BST_WIRE_X, U10_PINS['BST'][1]))

    # C29 bottom (pin2) -> SW node
    # SW node is at U10_PINS['SW'] Y level
    SW_WIRE_Y = U10_PINS['SW'][1]
    wires.append(wire(C29_P2[0], C29_P2[1], C29_X, SW_WIRE_Y))
    # Junction at L4.P1 where C29 bottom tees into SW wire
    junctions.append(junction(C29_X, SW_WIRE_Y))

    # --- VOUT rail ---
    # L4.P2 -> VOUT junction -> +5V
    wires.append(wire(VOUT_PWR_X, VOUT_PWR_Y, VOUT_X, VOUT_Y))
    # Junction at VOUT for C30 tee
    junctions.append(junction(VOUT_X, VOUT_Y))
    # C30+ -> VOUT
    wires.append(wire(C30_P1[0], C30_P1[1], VOUT_X, VOUT_Y))
    # C30- -> GND5
    wires.append(wire(C30_P2[0], C30_P2[1], GND5_X, GND5_Y))

    # U10.VOUT (pin 5) -> VOUT rail
    # Wire from VOUT pin to VOUT_X at VOUT_Y. VOUT pin is at different Y.
    # VOUT pin is at (U10_X+10.16, U10_Y+5.08), VOUT junction at (L4_P2)
    # Route: VOUT pin -> horizontal right to VOUT_X -> vertical up to VOUT_Y
    wires.append(wire(U10_PINS['VOUT'][0], U10_PINS['VOUT'][1], VOUT_X, U10_PINS['VOUT'][1]))
    wires.append(wire(VOUT_X, U10_PINS['VOUT'][1], VOUT_X, VOUT_Y))

    # --- GND pins ---
    # U10.GND (pin 6) -> GND3
    wires.append(wire(U10_PINS['GND6'][0], U10_PINS['GND6'][1], GND3_X, GND3_Y))
    # U10.EP (pin 9) -> GND4 (rotated 90, to the right)
    wires.append(wire(U10_PINS['EP'][0], U10_PINS['EP'][1], GND4_X, GND4_Y))

    wires_str = "\n\n".join(wires)
    junctions_str = "\n\n".join(junctions) if junctions else ""

    # ============================================================
    # ASSEMBLE
    # ============================================================
    sections = []
    if junctions_str:
        sections.append(junctions_str)
    sections.append(nc_str)
    sections.append(wires_str)
    sections.append(symbols_str)

    schematic = f"""(kicad_sch
  (version 20250114)
  (generator "build_psu_ip6503s_template.py")
  (generator_version "9.0")
  (uuid "{ROOT_UUID}")
  (paper "A4")

  (lib_symbols
{lib_symbols_str}
  )

{chr(10).join(sections)}

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
        "psu_ip6503s_5v.kicad_sch"
    )
    content = build_schematic()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Written: {output_path}")
    print(f"Components: U10, D3, L4, C29, C34, C30")
    print(f"Power symbols: +12V, +5V, 5x GND")
    print(f"No-connects: NC (pin 2), DP (pin 3), DM (pin 4)")
