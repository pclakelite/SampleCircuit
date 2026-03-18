"""
Build receiver_433mhz.kicad_sch — SYN480R 433MHz ASK/OOK receiver with
LC matching network and antenna connector.

Run: python build_receiver_433mhz_template.py
"""

import uuid
import os
import re

def uid():
    return str(uuid.uuid4())

ROOT_UUID = "d6f1b4c3-ae50-7d2b-e8f6-a4b5c7d9e0f1"

def snap(val, grid=1.27):
    return round(round(val / grid) * grid, 2)

# ============================================================
# LAYOUT
# ============================================================
U1_X, U1_Y = snap(160), snap(100)

# SYN480R pin endpoints (angle=0)
# Pin local (at px py) → schematic (U1_X + px, U1_Y - py)
U1_PINS = {
    'VSSRF': (round(U1_X - 20.32, 2), round(U1_Y - 3.81, 2)),  # pin 1, GND
    'ANT':   (round(U1_X - 20.32, 2), round(U1_Y - 1.27, 2)),  # pin 2, antenna input
    'VDDRF': (round(U1_X - 20.32, 2), round(U1_Y + 1.27, 2)),  # pin 3, VDD
    'CTH':   (round(U1_X - 20.32, 2), round(U1_Y + 3.81, 2)),  # pin 4, NC
    'DO':    (round(U1_X + 20.32, 2), round(U1_Y + 3.81, 2)),  # pin 5, data out
    'SHUT':  (round(U1_X + 20.32, 2), round(U1_Y + 1.27, 2)),  # pin 6, shutdown
    'CAGC':  (round(U1_X + 20.32, 2), round(U1_Y - 1.27, 2)),  # pin 7, NC (SQ)
    'REFOSC':(round(U1_X + 20.32, 2), round(U1_Y - 3.81, 2)),  # pin 8, NC (RO)
}

# Matching network: RF1 -> C12 (1.8pF) -> L2 (27nH) -> L3 (47nH) -> ANT pin
# All horizontal, to the left of U1

# L3 — closest to ANT pin (horizontal)
L3_X = snap(U1_PINS['ANT'][0] - 12.7)
L3_Y = U1_PINS['ANT'][1]
L3_P1 = (round(L3_X - 5.08, 2), L3_Y)  # pin 1, left (from L2)
L3_P2 = (round(L3_X + 5.08, 2), L3_Y)  # pin 2, right (to ANT)

# L2 — next in chain (horizontal)
L2_X = snap(L3_P1[0] - 12.7)
L2_Y = L3_Y
L2_P1 = (round(L2_X - 5.08, 2), L2_Y)  # pin 1, left (from C12)
L2_P2 = (round(L2_X + 5.08, 2), L2_Y)  # pin 2, right (to L3)

# C12 coupling cap — horizontal, before L2
C12_X = snap(L2_P1[0] - 12.7)
C12_Y = L2_Y
C12_P1 = (round(C12_X - 5.08, 2), C12_Y)  # pin 1, left (from antenna)
C12_P2 = (round(C12_X + 5.08, 2), C12_Y)  # pin 2, right (to L2)

# RF1 antenna — to the left of C12
# Antenna SIG pin at bottom (y + 2.54 from center), GND at left (x - 2.54)
RF1_X = snap(C12_P1[0] - 5.08)
RF1_Y = snap(C12_Y - 2.54)  # center above signal line
# RF1 SIG pin at (RF1_X, RF1_Y + 2.54) = same Y as C12_Y
RF1_SIG = (RF1_X, round(RF1_Y + 2.54, 2))
RF1_GND = (round(RF1_X - 2.54, 2), RF1_Y)

# C9 shunt cap — vertical, at L2/L3 junction, down to GND
C9_JUNCTION_X = L2_P2[0]  # = L3_P1[0] — they connect here
C9_X = C9_JUNCTION_X
C9_Y = snap(L2_Y + 10.16)
C9_P1 = (C9_X, round(C9_Y - 5.08, 2))  # top -> junction
C9_P2 = (C9_X, round(C9_Y + 5.08, 2))  # bottom -> GND

# C13 bypass cap — vertical, on VDD line
C13_X = snap(U1_PINS['VDDRF'][0] - 7.62)
C13_Y = snap(U1_PINS['VDDRF'][1] + 7.62)
C13_P1 = (C13_X, round(C13_Y - 5.08, 2))  # top -> VDD
C13_P2 = (C13_X, round(C13_Y + 5.08, 2))  # bottom -> GND

# Power symbols
VCC_X, VCC_Y = C13_X, snap(C13_P1[1] - 3.81)  # +3.3V above C13

# GND symbols
GND1_X, GND1_Y = U1_PINS['VSSRF'][0], snap(U1_PINS['VSSRF'][1] - 5.08)  # above pin 1 (GND goes up)
# Wait - VSSRF is at top-left. GND symbol should go down or to the left.
# Actually let's reconsider: VSSRF pin 1 is at (U1_X-20.32, U1_Y-3.81) which is top-left
# GND symbol goes down, so place below
GND1_X = U1_PINS['VSSRF'][0]
GND1_Y = snap(U1_PINS['VSSRF'][1] + 5.08)  # Wait this would go INTO the IC.
# Pin 1 points LEFT from IC. The wire endpoint is at LEFT_X. GND should go further left or down.
# Let me route: VSSRF pin -> wire down -> GND
# Actually let's place GND to the left, rotated
GND1_X = snap(U1_PINS['VSSRF'][0] - 5.08)
GND1_Y = U1_PINS['VSSRF'][1]

GND2_X, GND2_Y = C9_X, snap(C9_P2[1] + 3.81)          # below C9
GND3_X, GND3_Y = C13_X, snap(C13_P2[1] + 3.81)         # below C13
GND4_X, GND4_Y = U1_PINS['SHUT'][0], snap(U1_PINS['SHUT'][1] + 5.08)  # below SHUT (pull to GND)
# SHUT pin is right side. GND should go further right or down.
# Let's put it to the right, rotated 90
GND4_X = snap(U1_PINS['SHUT'][0] + 5.08)
GND4_Y = U1_PINS['SHUT'][1]

GND5_X = RF1_GND[0]
GND5_Y = snap(RF1_Y + 5.08)  # below RF1

# Port symbol — DATA_433
PORT_X = snap(U1_PINS['DO'][0] + 7.62)
PORT_Y = U1_PINS['DO'][1]


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
    for port_name in ['DATA_433']:
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
        ("SYN480R-FS24", False),       # receiver IC — keep pin names
        ("L_27nH_C76665", True),       # RF inductor
        ("L_47nH_C76668", True),       # RF inductor
        ("C_6p8_C106245", True),       # RF cap
        ("C_1p8_C106233", True),       # RF coupling cap
        ("C_1uF_C28323", True),        # VDD bypass cap
        ("ANT_433_C496550", True),     # antenna
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

    # U1 — SYN480R
    symbols.append(make_component("U1", "JLCImport:SYN480R-FS24",
        U1_X, U1_Y, "SYN480R",
        footprint="JLCImport:SYN480R-FS24", lcsc="C15561",
        ref_offset=(0, -10.16), val_offset=(0, 10.16)))

    # L3 — 47nH (horizontal)
    symbols.append(make_component("L3", "JLCImport:L_47nH_C76668",
        L3_X, L3_Y, "47nH",
        footprint="JLCImport:0402WGF3301TCE", lcsc="C76668",
        ref_offset=(0, -3.81), val_offset=(0, 3.81)))

    # L2 — 27nH (horizontal)
    symbols.append(make_component("L2", "JLCImport:L_27nH_C76665",
        L2_X, L2_Y, "27nH",
        footprint="JLCImport:0402WGF3301TCE", lcsc="C76665",
        ref_offset=(0, -3.81), val_offset=(0, 3.81)))

    # C12 — 1.8pF coupling (horizontal)
    symbols.append(make_component("C12", "JLCImport:C_1p8_C106233",
        C12_X, C12_Y, "1.8pF",
        footprint="JLCImport:0402WGF3301TCE", lcsc="C106233",
        ref_offset=(0, -3.81), val_offset=(0, 3.81)))

    # C9 — 6.8pF shunt (vertical, angle=90)
    symbols.append(make_component("C9", "JLCImport:C_6p8_C106245",
        C9_X, C9_Y, "6.8pF", angle=90,
        footprint="JLCImport:0402WGF3301TCE", lcsc="C106245",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # C13 — 1uF VDD bypass (vertical, angle=90)
    symbols.append(make_component("C13", "JLCImport:C_1uF_C28323",
        C13_X, C13_Y, "1uF", angle=90,
        footprint="JLCImport:CC0805KRX7R9BB104", lcsc="C28323",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # RF1 — Antenna connector
    symbols.append(make_component("RF1", "JLCImport:ANT_433_C496550",
        RF1_X, RF1_Y, "433MHz",
        footprint="", lcsc="C496550",
        ref_offset=(0, -5.08), val_offset=(0, 7.62)))

    # Power symbols
    symbols.append(make_power("#PWR01", "power:+3.3V", "+3.3V", VCC_X, VCC_Y))
    symbols.append(make_power("#PWR02", "power:GND", "GND", GND1_X, GND1_Y, angle=270))
    symbols.append(make_power("#PWR03", "power:GND", "GND", GND2_X, GND2_Y))
    symbols.append(make_power("#PWR04", "power:GND", "GND", GND3_X, GND3_Y))
    symbols.append(make_power("#PWR05", "power:GND", "GND", GND4_X, GND4_Y, angle=90))
    symbols.append(make_power("#PWR06", "power:GND", "GND", GND5_X, GND5_Y))

    # Port symbol — DATA_433
    symbols.append(make_port("#PORT01", "Ports:DATA_433", "DATA_433", PORT_X, PORT_Y))

    symbols_str = "\n\n".join(symbols)

    # ============================================================
    # NO-CONNECTS
    # ============================================================
    def no_connect(x, y):
        return f"""  (no_connect (at {x} {y})
    (uuid "{uid()}")
  )"""

    nc_list = [
        no_connect(U1_PINS['CTH'][0], U1_PINS['CTH'][1]),      # pin 4
        no_connect(U1_PINS['CAGC'][0], U1_PINS['CAGC'][1]),    # pin 7
        no_connect(U1_PINS['REFOSC'][0], U1_PINS['REFOSC'][1]),# pin 8
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

    # --- Matching network chain ---
    # RF1 SIG -> C12 pin1
    wires.append(wire(RF1_SIG[0], RF1_SIG[1], C12_P1[0], C12_P1[1]))
    # C12 pin2 -> L2 pin1
    wires.append(wire(C12_P2[0], C12_P2[1], L2_P1[0], L2_P1[1]))
    # L2 pin2 -> L3 pin1 (junction for C9)
    wires.append(wire(L2_P2[0], L2_P2[1], L3_P1[0], L3_P1[1]))
    junctions.append(junction(L2_P2[0], L2_P2[1]))
    # L3 pin2 -> ANT pin
    wires.append(wire(L3_P2[0], L3_P2[1], U1_PINS['ANT'][0], U1_PINS['ANT'][1]))

    # C9 top -> L2/L3 junction
    wires.append(wire(C9_P1[0], C9_P1[1], C9_JUNCTION_X, L2_Y))
    # C9 bottom -> GND2
    wires.append(wire(C9_P2[0], C9_P2[1], GND2_X, GND2_Y))

    # --- VDD wiring ---
    VDDRF_Y = U1_PINS['VDDRF'][1]
    # +3.3V -> vertical down to VDDRF Y level
    wires.append(wire(VCC_X, VCC_Y, VCC_X, VDDRF_Y))
    # Junction at tee point (VCC vertical, horizontal to VDDRF, vertical to C13)
    junctions.append(junction(VCC_X, VDDRF_Y))
    # Horizontal to VDDRF pin
    wires.append(wire(VCC_X, VDDRF_Y, U1_PINS['VDDRF'][0], VDDRF_Y))
    # Vertical down to C13 top
    wires.append(wire(VCC_X, VDDRF_Y, C13_P1[0], C13_P1[1]))
    # C13 bottom -> GND3
    wires.append(wire(C13_P2[0], C13_P2[1], GND3_X, GND3_Y))

    # --- VSSRF (GND pin 1) -> GND1 ---
    wires.append(wire(U1_PINS['VSSRF'][0], U1_PINS['VSSRF'][1], GND1_X, GND1_Y))

    # --- SHUT pin -> GND4 (pull to GND for normal operation) ---
    wires.append(wire(U1_PINS['SHUT'][0], U1_PINS['SHUT'][1], GND4_X, GND4_Y))

    # --- DO pin -> DATA_433 port ---
    PORT_PIN_X = round(PORT_X + 2.54, 2)
    wires.append(wire(U1_PINS['DO'][0], U1_PINS['DO'][1], PORT_PIN_X, PORT_Y))

    # --- RF1 GND -> GND5 ---
    wires.append(wire(RF1_GND[0], RF1_GND[1], RF1_GND[0], GND5_Y))

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
  (generator "build_receiver_433mhz_template.py")
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
        "receiver_433mhz.kicad_sch"
    )
    content = build_schematic()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Written: {output_path}")
    print(f"Components: U1, L2, L3, C9, C12, C13, RF1")
    print(f"Power symbols: +3.3V, 5x GND")
    print(f"Port: DATA_433")
    print(f"No-connects: CTH (pin 4), CAGC (pin 7), REFOSC (pin 8)")
