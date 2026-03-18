"""
Build psu_lmzm23601_5v.kicad_sch — LMZM23601SILR 12V-to-5V buck regulator template
with all components placed on 1.27mm grid, power symbols, wires, and junctions.

Run: python build_psu_lmzm23601_5v.py
"""

import uuid
import os
import re
import json

def uid():
    return str(uuid.uuid4())

# Fixed root UUID so instance paths don't change on regeneration
ROOT_UUID = "a3e7c1d4-8f2b-4a6e-9c5d-1b3e7f9a2c4d"

def snap(val, grid=1.27):
    """Snap a value to the nearest 1.27mm grid point."""
    return round(round(val / grid) * grid, 2)


# ============================================================
# CHECK TEMPLATE LOCK STATUS
# ============================================================
def check_status():
    status_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "status.json")
    if os.path.exists(status_path):
        with open(status_path, 'r') as f:
            status = json.load(f)
        if status.get("status") == "locked":
            print(f"ERROR: Template '{status.get('template')}' is LOCKED.")
            print(f"  Locked by: {status.get('locked_by')}")
            print(f"  Date: {status.get('locked_date')}")
            print(f"  Reason: {status.get('description')}")
            print("  Will NOT regenerate. Change status to 'revision' to unlock.")
            return False
    return True


# ============================================================
# LAYOUT — all positions on 1.27mm grid
# ============================================================
# U6 center
U6_X, U6_Y = snap(150), snap(100)  # (149.86, 100.33)

# U6 pin endpoints (corrected formula: endpoint = (sx + px, sy - py))
# Pin local positions from lib_symbol:
#   Pin 1 GND:       (-13.97, 3.81)    Pin 6 VOUT:  (13.97, -6.35)
#   Pin 2 MODE/SYNC: (-13.97, 1.27)    Pin 7 FB:    (13.97, -3.81)
#   Pin 3 VIN:       (-13.97, -1.27)   Pin 8 DNC:   (13.97, -1.27)
#   Pin 4 EN:        (-13.97, -3.81)   Pin 9 DNC:   (13.97, 1.27)
#   Pin 5 PGOOD:     (-13.97, -6.35)   Pin 10 DNC:  (13.97, 3.81)
#                                        Pin 11 EP:   (13.97, 6.35)
U6_PINS = {
    'GND':       (round(U6_X - 13.97, 2), round(U6_Y - 3.81, 2)),   # (135.89, 96.52)
    'MODE_SYNC': (round(U6_X - 13.97, 2), round(U6_Y - 1.27, 2)),   # (135.89, 99.06)
    'VIN':       (round(U6_X - 13.97, 2), round(U6_Y + 1.27, 2)),   # (135.89, 101.60)
    'EN':        (round(U6_X - 13.97, 2), round(U6_Y + 3.81, 2)),   # (135.89, 104.14)
    'PGOOD':     (round(U6_X - 13.97, 2), round(U6_Y + 6.35, 2)),   # (135.89, 106.68)
    'VOUT':      (round(U6_X + 13.97, 2), round(U6_Y + 6.35, 2)),   # (163.83, 106.68)
    'FB':        (round(U6_X + 13.97, 2), round(U6_Y + 3.81, 2)),   # (163.83, 104.14)
    'DNC8':      (round(U6_X + 13.97, 2), round(U6_Y + 1.27, 2)),   # (163.83, 101.60)
    'DNC9':      (round(U6_X + 13.97, 2), round(U6_Y - 1.27, 2)),   # (163.83, 99.06)
    'DNC10':     (round(U6_X + 13.97, 2), round(U6_Y - 3.81, 2)),   # (163.83, 96.52)
    'EP':        (round(U6_X + 13.97, 2), round(U6_Y - 6.35, 2)),   # (163.83, 93.98)
}

# Input caps — vertical (GRM32ER7YA106KA12L default orientation)
# Pin 1 at bottom (cy + 5.08), Pin 2 at top (cy - 5.08) in schematic
# Positions from user's KiCad layout review
C31_X, C31_Y = 105.41, 111.76                # user moved left+down
C31_P1 = (C31_X, round(C31_Y + 5.08, 2))    # bottom (105.41, 116.84)
C31_P2 = (C31_X, round(C31_Y - 5.08, 2))    # top (105.41, 106.68)

C33_X, C33_Y = 116.84, 109.22                # user moved left+down, staggered Y
C33_P1 = (C33_X, round(C33_Y + 5.08, 2))    # bottom (116.84, 114.30)
C33_P2 = (C33_X, round(C33_Y - 5.08, 2))    # top (116.84, 104.14)

# R3 (10k, horizontal) — feedback top resistor, slightly below VOUT rail
R3_X, R3_Y = 173.99, 109.22                  # user moved to (173.99, 109.22)
R3_P1 = (round(R3_X - 5.08, 2), R3_Y)       # left (168.91, 109.22)
R3_P2 = (round(R3_X + 5.08, 2), R3_Y)       # right (179.07, 109.22)

# R4 (2.49k, vertical angle=270, pin1=top) — feedback bottom resistor
R4_X, R4_Y = 186.69, 124.46                  # user moved far right+down
R4_P1 = (R4_X, round(R4_Y - 5.08, 2))       # top (186.69, 119.38)
R4_P2 = (R4_X, round(R4_Y + 5.08, 2))       # bottom (186.69, 129.54)

# C32 (47uF, angle=270 vertical, pin1=top) — output decoupling
C32_X, C32_Y = 167.64, 124.46                # user moved way down
C32_P1 = (C32_X, round(C32_Y - 5.08, 2))    # top (167.64, 119.38)
C32_P2 = (C32_X, round(C32_Y + 5.08, 2))    # bottom (167.64, 129.54)

# Power symbols — positions from user's KiCad layout
V12_X, V12_Y = 102.87, 99.06                 # user moved far left
V5_X, V5_Y = 170.18, 100.33                  # user moved to R3 pin1 X

# GND symbols — positions from user's KiCad layout
GND_INPUT_X, GND_INPUT_Y = 116.84, 123.19    # below input caps
GND_IC1_X, GND_IC1_Y = 128.27, 96.52         # IC GND pin 1 — angle=270 (sideways)
GND_IC1_ANGLE = 270
GND_EP_X, GND_EP_Y = 173.99, 93.98           # EP ground — angle=90 (sideways)
GND_EP_ANGLE = 90
GND_OUT_X, GND_OUT_Y = 175.26, 132.08        # below output section

# Wire routing intermediate points from user's layout
VIN_RAIL_Y = 102.87                           # user's VIN rail runs at Y=102.87
GND_MODE_CORNER = (130.81, 96.52)             # GND/MODE_SYNC routing corner
FB_JUNCTION = (180.34, 104.14)                # FB divider junction point
VOUT_JUNCTION = (167.64, 106.68)              # VOUT/C32/+5V junction
OUT_GND_RAIL_Y = 129.54                       # output GND rail


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


def read_lib_symbols():
    """Read JLCImport symbol definitions needed for this template."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    jlc_path = os.path.join(project_root, "JLCImport.kicad_sym")

    # (symbol_name, hide_pin_names)
    needed_symbols = [
        ("LMZM23601SILR", False),       # IC — keep pin names visible
        ("0805W8F1002T5E", True),        # 10k resistor
        ("0805W8F2491T5E", True),        # 2.49k resistor
        ("GRM32ER7YA106KA12L", True),    # 10uF 35V cap
        ("1206X476M160NT", True),        # 47uF 16V cap
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
        if '(pin_numbers' in sym_text:
            sym_text = re.sub(
                r'\(pin_numbers[^)]*\)',
                '(pin_numbers (hide yes))',
                sym_text,
                count=1
            )
        else:
            # Add pin_numbers hide after the opening symbol line
            sym_text = sym_text.replace(
                f'(symbol "JLCImport:{sym_name}"',
                f'(symbol "JLCImport:{sym_name}"\n    (pin_numbers (hide yes))',
                1
            )

        # Hide pin_names on passives
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
    # Read lib symbols from project
    try:
        jlc_symbols = read_lib_symbols()
    except Exception as e:
        print(f"Warning: Could not read JLCImport.kicad_sym: {e}")
        print("Using placeholder lib_symbols — schematic will show red boxes.")
        jlc_symbols = {}

    # Build lib_symbols section
    lib_parts = []
    for sym_text in jlc_symbols.values():
        lib_parts.append(f"    {sym_text}")

    # Power symbols (hardcoded — they rarely change)
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

    # U6 — LMZM23601SILR (ref above, value below)
    symbols.append(make_component("U6", "JLCImport:LMZM23601SILR",
        U6_X, U6_Y, "LMZM23601SILR",
        footprint="JLCImport:LMZM23601SILR",
        lcsc="C2685821",
        ref_offset=(0, -12.7), val_offset=(0, 12.7)))

    # R3 — 10k (feedback top, horizontal)
    symbols.append(make_component("R3", "JLCImport:0805W8F1002T5E",
        R3_X, R3_Y, "10k",
        footprint="JLCImport:0805W8F1002T5E", lcsc="C17414",
        ref_offset=(0, -2.54), val_offset=(0, 2.54)))

    # R4 — 2.49k (feedback bottom, vertical angle=270)
    symbols.append(make_component("R4", "JLCImport:0805W8F2491T5E",
        R4_X, R4_Y, "2.49k", angle=270,
        footprint="JLCImport:0805W8F2491T5E", lcsc="C21237",
        ref_offset=(3.81, 0), val_offset=(-3.81, 0)))

    # C31 — 10uF 35V input cap #1 (vertical default)
    symbols.append(make_component("C31", "JLCImport:GRM32ER7YA106KA12L",
        C31_X, C31_Y, "10uF 35V",
        footprint="JLCImport:GRM32ER7YA106KA12L", lcsc="C97973",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # C33 — 10uF 35V input cap #2 (vertical default)
    symbols.append(make_component("C33", "JLCImport:GRM32ER7YA106KA12L",
        C33_X, C33_Y, "10uF 35V",
        footprint="JLCImport:GRM32ER7YA106KA12L", lcsc="C97973",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # C32 — 47uF 16V output cap (angle=270, vertical, pin1 top)
    symbols.append(make_component("C32", "JLCImport:1206X476M160NT",
        C32_X, C32_Y, "47uF 16V", angle=270,
        footprint="JLCImport:1206X476M160NT", lcsc="C172351",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # Power symbols — positions and offsets matched to user's KiCad layout
    symbols.append(make_power("#PWR01", "power:+12V", "+12V", V12_X, V12_Y,
                               ref_pos=(V12_X, round(V12_Y + 3.81, 2)),
                               val_pos=(102.362, 94.742)))
    symbols.append(make_power("#PWR08", "power:+5V", "+5V", V5_X, V5_Y,
                               ref_pos=(V5_X, round(V5_Y + 3.81, 2)),
                               val_pos=(V5_X, 96.77)))

    # GND symbols — angles for sideways placement on horizontal wires
    symbols.append(make_power("#PWR02", "power:GND", "GND", GND_INPUT_X, GND_INPUT_Y,
                               ref_pos=(GND_INPUT_X, round(GND_INPUT_Y + 6.35, 2)),
                               val_pos=(GND_INPUT_X, 127.0)))
    symbols.append(make_power("#PWR03", "power:GND", "GND", GND_IC1_X, GND_IC1_Y,
                               angle=GND_IC1_ANGLE,
                               ref_pos=(121.92, GND_IC1_Y),
                               val_pos=(124.714, 96.266)))
    symbols.append(make_power("#PWR04", "power:GND", "GND", GND_EP_X, GND_EP_Y,
                               angle=GND_EP_ANGLE,
                               ref_pos=(180.34, GND_EP_Y),
                               val_pos=(177.8, GND_EP_Y)))
    symbols.append(make_power("#PWR05", "power:GND", "GND", GND_OUT_X, GND_OUT_Y,
                               ref_pos=(GND_OUT_X, round(GND_OUT_Y + 6.35, 2)),
                               val_pos=(GND_OUT_X, 135.89)))

    symbols_str = "\n\n".join(symbols)

    # ============================================================
    # NO-CONNECTS (4 pins — MODE/SYNC is wired to GND for forced PWM)
    # ============================================================
    nc_pins = [
        U6_PINS['PGOOD'],      # pin 5
        U6_PINS['DNC8'],       # pin 8
        U6_PINS['DNC9'],       # pin 9
        U6_PINS['DNC10'],      # pin 10
    ]
    nc_parts = []
    for px, py in nc_pins:
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

    # --- Input power: +12V → VIN rail → IC ---
    # +12V symbol down to VIN rail at Y=102.87
    wires.append(wire(102.87, 99.06, 102.87, 102.87))
    # VIN rail segment: +12V junction → C31 top
    wires.append(wire(102.87, 102.87, 105.41, 102.87))
    # C31 pin2 (top, 106.68) up to VIN rail
    wires.append(wire(105.41, 106.68, 105.41, 102.87))
    # VIN rail segment: C31 top → C33 top
    wires.append(wire(105.41, 102.87, 116.84, 102.87))
    # C33 pin2 (top, 104.14) up to VIN rail
    wires.append(wire(116.84, 104.14, 116.84, 102.87))
    # VIN rail segment: C33 top → IC VIN area
    wires.append(wire(116.84, 102.87, 135.89, 102.87))
    # VIN rail down to VIN pin (101.60)
    wires.append(wire(135.89, 102.87, 135.89, 101.6))
    # EN pin (104.14) up to VIN rail (102.87)
    wires.append(wire(135.89, 104.14, 135.89, 102.87))

    # --- GND + MODE/SYNC: tied to GND via corner ---
    # GND pin1 endpoint → corner
    wires.append(wire(128.27, 96.52, 130.81, 96.52))
    # Corner → GND pin (horizontal to IC)
    wires.append(wire(130.81, 96.52, 135.89, 96.52))
    # Corner vertical down to MODE/SYNC level
    wires.append(wire(130.81, 96.52, 130.81, 99.06))
    # MODE/SYNC pin → corner
    wires.append(wire(135.89, 99.06, 130.81, 99.06))

    # --- EP ground (sideways) ---
    wires.append(wire(173.99, 93.98, 163.83, 93.98))

    # --- Input cap GND ---
    # C33 pin1 (bottom, 114.30) down to GND junction (116.84)
    wires.append(wire(116.84, 114.3, 116.84, 116.84))
    # C31 pin1 (bottom, 116.84) horizontal to C33 GND junction
    wires.append(wire(105.41, 116.84, 116.84, 116.84))
    # GND junction down to GND symbol
    wires.append(wire(116.84, 116.84, 116.84, 123.19))

    # --- Output: VOUT → +5V rail ---
    # VOUT pin to output junction
    wires.append(wire(163.83, 106.68, 167.64, 106.68))
    # +5V rail connection at junction
    wires.append(wire(170.18, 106.68, 167.64, 106.68))
    # +5V symbol down to output rail
    wires.append(wire(170.18, 100.33, 170.18, 106.68))
    # C32 area (109.22) down to VOUT junction (106.68)
    wires.append(wire(167.64, 109.22, 167.64, 106.68))
    # R3 pin1 (168.91) to C32/VOUT junction
    wires.append(wire(168.91, 109.22, 167.64, 109.22))
    # C32 pin1 (119.38) up to VOUT junction area (109.22)
    wires.append(wire(167.64, 119.38, 167.64, 109.22))

    # --- Feedback divider ---
    # U6.FB → FB junction (horizontal)
    wires.append(wire(163.83, 104.14, 180.34, 104.14))
    # R3 pin2 (179.07) → FB vertical wire (180.34)
    wires.append(wire(179.07, 109.22, 180.34, 109.22))
    # FB vertical: R3 area down to FB junction
    wires.append(wire(180.34, 109.22, 180.34, 104.14))
    # R4 at FB level → FB junction (horizontal)
    wires.append(wire(186.69, 104.14, 180.34, 104.14))
    # R4 FB level down to R4 pin1
    wires.append(wire(186.69, 104.14, 186.69, 119.38))

    # --- Output GND rail ---
    # C32 pin2 (bottom) → output GND junction
    wires.append(wire(167.64, 129.54, 175.26, 129.54))
    # Output GND junction → R4 pin2 (bottom)
    wires.append(wire(175.26, 129.54, 186.69, 129.54))
    # Output GND junction down to GND symbol
    wires.append(wire(175.26, 129.54, 175.26, 132.08))

    wires_str = "\n\n".join(wires)

    # ============================================================
    # JUNCTIONS
    # ============================================================
    junction_points = [
        (105.41, 102.87),            # +12V rail meets C31 top
        (116.84, 102.87),            # C33 top on VIN rail
        (135.89, 102.87),            # EN/VIN meet on VIN rail
        (130.81, 96.52),             # GND/MODE_SYNC corner junction
        (116.84, 116.84),            # Input cap GND rail junction
        (167.64, 106.68),            # VOUT pin meets output rail
        (167.64, 109.22),            # C32 top / R3.pin1 junction
        (180.34, 104.14),            # FB divider junction
        (175.26, 129.54),            # Output GND rail junction
    ]
    junc_parts = []
    for jx, jy in junction_points:
        junc_parts.append(f"""  (junction (at {jx} {jy})
    (diameter 0)
    (color 0 0 0 0)
    (uuid "{uid()}")
  )""")
    junctions = "\n".join(junc_parts)

    # ============================================================
    # ASSEMBLE
    # ============================================================
    schematic = f"""(kicad_sch
  (version 20250114)
  (generator "build_psu_lmzm23601_5v.py")
  (generator_version "9.0")
  (uuid "{ROOT_UUID}")
  (paper "A4")

  (lib_symbols
{lib_symbols_str}
  )

{junctions}

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
    if not check_status():
        exit(1)

    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "psu_lmzm23601_5v.kicad_sch"
    )
    content = build_schematic()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Written: {output_path}")
    print(f"Components: U6, R3, R4, C31, C33, C32")
    print(f"Power symbols: +12V, +5V, 4x GND")
    print(f"No-connects: PGOOD, DNC x3 (MODE/SYNC wired to GND)")
    print(f"All positions on 1.27mm grid")
    print(f"\nLayout:")
    print(f"  U6  at ({U6_X}, {U6_Y})")
    print(f"  C31 at ({C31_X}, {C31_Y}) vertical")
    print(f"  C33 at ({C33_X}, {C33_Y}) vertical")
    print(f"  R3  at ({R3_X}, {R3_Y}) horizontal")
    print(f"  R4  at ({R4_X}, {R4_Y}) angle=270")
    print(f"  C32 at ({C32_X}, {C32_Y}) angle=270")
