"""
Build psu_lmzm23601_12v.kicad_sch — LMZM23601SILR 24V-to-12V buck regulator template
with all components placed on 1.27mm grid, power symbols, wires, and junctions.

Cloned from psu_lmzm23601_5v with:
  - Input: +24V (was +12V)
  - Output: +12V (was +5V)
  - R1: 110k (was 10k)  — feedback upper
  - R2: 10k  (was 2.49k) — feedback lower
  - Vout = 1.0 * (1 + 110k/10k) = 12.0V

Input protection:
  - D1: SS34 Schottky in series for reverse polarity protection
  - D2: SMBJ26CA bidirectional TVS across VIN and GND for transient suppression

Run: python build_psu_lmzm23601_12v.py
"""

import uuid
import os
import re
import json

def uid():
    return str(uuid.uuid4())

# Fixed root UUID so instance paths don't change on regeneration
ROOT_UUID = "c5d6e7f8-a1b2-4c3d-9e0f-1a2b3c4d5e6f"

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
# (same topology as 5V template)
# ============================================================
# U1 center
U1_X, U1_Y = snap(150), snap(100)  # (149.86, 100.33)

# U1 pin endpoints (corrected formula: endpoint = (sx + px, sy - py))
U1_PINS = {
    'GND':       (round(U1_X - 13.97, 2), round(U1_Y - 3.81, 2)),
    'MODE_SYNC': (round(U1_X - 13.97, 2), round(U1_Y - 1.27, 2)),
    'VIN':       (round(U1_X - 13.97, 2), round(U1_Y + 1.27, 2)),
    'EN':        (round(U1_X - 13.97, 2), round(U1_Y + 3.81, 2)),
    'PGOOD':     (round(U1_X - 13.97, 2), round(U1_Y + 6.35, 2)),
    'VOUT':      (round(U1_X + 13.97, 2), round(U1_Y + 6.35, 2)),
    'FB':        (round(U1_X + 13.97, 2), round(U1_Y + 3.81, 2)),
    'DNC8':      (round(U1_X + 13.97, 2), round(U1_Y + 1.27, 2)),
    'DNC9':      (round(U1_X + 13.97, 2), round(U1_Y - 1.27, 2)),
    'DNC10':     (round(U1_X + 13.97, 2), round(U1_Y - 3.81, 2)),
    'EP':        (round(U1_X + 13.97, 2), round(U1_Y - 6.35, 2)),
}

# Input caps — vertical (GRM32ER7YA106KA12L default orientation)
C1_X, C1_Y = 105.41, 111.76
C1_P1 = (C1_X, round(C1_Y + 5.08, 2))
C1_P2 = (C1_X, round(C1_Y - 5.08, 2))

C2_X, C2_Y = 116.84, 109.22
C2_P1 = (C2_X, round(C2_Y + 5.08, 2))
C2_P2 = (C2_X, round(C2_Y - 5.08, 2))

# R1 (110k, horizontal) — feedback top resistor
R1_X, R1_Y = 173.99, 109.22
R1_P1 = (round(R1_X - 5.08, 2), R1_Y)
R1_P2 = (round(R1_X + 5.08, 2), R1_Y)

# R2 (10k, vertical angle=270, pin1=top) — feedback bottom resistor
R2_X, R2_Y = 186.69, 124.46
R2_P1 = (R2_X, round(R2_Y - 5.08, 2))
R2_P2 = (R2_X, round(R2_Y + 5.08, 2))

# C3 (47uF, angle=270 vertical, pin1=top) — output decoupling
C3_X, C3_Y = 167.64, 124.46
C3_P1 = (C3_X, round(C3_Y - 5.08, 2))
C3_P2 = (C3_X, round(C3_Y + 5.08, 2))

# D1 — SS34 Schottky (series reverse polarity protection, angle=270 vertical)
# Current flows: +24V (top) → anode (top) → cathode (bottom) → VIN rail
D1_X, D1_Y = 102.87, 93.98
D1_P2_A = (D1_X, round(D1_Y - 5.08, 2))   # Anode at (102.87, 88.9) — +24V side
D1_P1_K = (D1_X, round(D1_Y + 5.08, 2))   # Cathode at (102.87, 99.06) — VIN side

# D2 — SMBJ26CA TVS (transient suppression, angle=270 vertical)
# Placed to the left of input caps, between VIN rail and GND
D2_X, D2_Y = 96.52, 109.22
D2_P2_A = (D2_X, round(D2_Y - 5.08, 2))   # Pin 2 at (96.52, 104.14) — VIN side
D2_P1_K = (D2_X, round(D2_Y + 5.08, 2))   # Pin 1 at (96.52, 114.3) — GND side

# Power symbols
V24_X, V24_Y = 102.87, 88.9        # +24V input (moved up for D1)
V12_X, V12_Y = 170.18, 100.33      # +12V output (was +5V)

# GND symbols
GND_INPUT_X, GND_INPUT_Y = 116.84, 123.19
GND_IC1_X, GND_IC1_Y = 128.27, 96.52
GND_IC1_ANGLE = 270
GND_EP_X, GND_EP_Y = 173.99, 93.98
GND_EP_ANGLE = 90
GND_OUT_X, GND_OUT_Y = 175.26, 132.08
GND_D2_X, GND_D2_Y = 96.52, 116.84    # GND for TVS diode

# Wire routing intermediate points
VIN_RAIL_Y = 102.87
GND_MODE_CORNER = (130.81, 96.52)
FB_JUNCTION = (180.34, 104.14)
VOUT_JUNCTION = (167.64, 106.68)
OUT_GND_RAIL_Y = 129.54


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
        ("0805W8F1104T5E", True),        # 110k resistor (upper feedback)
        ("0805W8F1002T5E", True),        # 10k resistor (lower feedback)
        ("GRM32ER7YA106KA12L", True),    # 10uF 35V cap
        ("GRM32EC81E476KE15L", True),    # 47uF 25V cap (upgraded from 16V for 12V rail derating)
        ("SS34_C8678", True),            # Schottky diode (reverse polarity)
        ("SMBJ26CA_C89651", True),       # TVS diode (transient suppression)
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

    # Power symbol: +24V (input)
    lib_parts.append("""    (symbol "power:+24V"
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
      (property "Value" "+24V"
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
      (property "Description" "Power symbol creates a global label with name \\"+24V\\""
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (symbol "+24V_0_1"
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
      (symbol "+24V_1_1"
        (pin power_in line
          (at 0 0 90)
          (length 0)
          (name "~" (effects (font (size 1.27 1.27))))
          (number "1" (effects (font (size 1.27 1.27))))
        )
      )
      (embedded_fonts no)
    )""")

    # Power symbol: +12V (output)
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

    # Power symbol: GND
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
      (project "SampleCircuit"
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
      (project "SampleCircuit"
        (path "/{ROOT_UUID}"
          (reference "{ref}")
          (unit 1)
        )
      )
    )
  )"""

    symbols = []

    # U1 — LMZM23601SILR
    symbols.append(make_component("U1", "JLCImport:LMZM23601SILR",
        U1_X, U1_Y, "LMZM23601SILR",
        footprint="JLCImport:LMZM23601SILR",
        lcsc="C2685821",
        ref_offset=(0, -12.7), val_offset=(0, 12.7)))

    # R1 — 110k (feedback top, horizontal)
    symbols.append(make_component("R1", "JLCImport:0805W8F1104T5E",
        R1_X, R1_Y, "110k",
        footprint="JLCImport:0805W8F1104T5E", lcsc="C17436",
        ref_offset=(0, -2.54), val_offset=(0, 2.54)))

    # R2 — 10k (feedback bottom, vertical angle=270)
    symbols.append(make_component("R2", "JLCImport:0805W8F1002T5E",
        R2_X, R2_Y, "10k", angle=270,
        footprint="JLCImport:0805W8F1002T5E", lcsc="C17414",
        ref_offset=(3.81, 0), val_offset=(-3.81, 0)))

    # C1 — 10uF 35V input cap #1 (vertical default)
    symbols.append(make_component("C1", "JLCImport:GRM32ER7YA106KA12L",
        C1_X, C1_Y, "10uF 35V",
        footprint="JLCImport:GRM32ER7YA106KA12L", lcsc="C97973",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # C2 — 10uF 35V input cap #2 (vertical default)
    symbols.append(make_component("C2", "JLCImport:GRM32ER7YA106KA12L",
        C2_X, C2_Y, "10uF 35V",
        footprint="JLCImport:GRM32ER7YA106KA12L", lcsc="C97973",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # C3 — 47uF 25V output cap (angle=270, vertical, pin1 top)
    # Upgraded from 16V to 25V for proper derating on 12V rail (2.08x vs 1.33x)
    symbols.append(make_component("C3", "JLCImport:GRM32EC81E476KE15L",
        C3_X, C3_Y, "47uF 25V", angle=270,
        footprint="JLCImport:GRM32EC81C476KE15L", lcsc="C86211",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # D1 — SS34 Schottky (series reverse polarity, vertical angle=270)
    symbols.append(make_component("D1", "JLCImport:SS34_C8678",
        D1_X, D1_Y, "SS34", angle=270,
        footprint="JLCImport:SS34_C8678", lcsc="C8678",
        ref_offset=(3.81, 0), val_offset=(-3.81, 0)))

    # D2 — SMBJ26CA TVS (transient suppression, vertical angle=270)
    symbols.append(make_component("D2", "JLCImport:SMBJ26CA_C89651",
        D2_X, D2_Y, "SMBJ26CA", angle=270,
        footprint="JLCImport:SMBJ26CA_C89651", lcsc="C89651",
        ref_offset=(3.81, 0), val_offset=(-3.81, 0)))

    # Power symbols — +24V input, +12V output
    symbols.append(make_power("#PWR01", "power:+24V", "+24V", V24_X, V24_Y,
                               ref_pos=(V24_X, round(V24_Y + 3.81, 2)),
                               val_pos=(V24_X, round(V24_Y - 4.32, 2))))
    symbols.append(make_power("#PWR08", "power:+12V", "+12V", V12_X, V12_Y,
                               ref_pos=(V12_X, round(V12_Y + 3.81, 2)),
                               val_pos=(V12_X, 96.77)))

    # GND symbols
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
    symbols.append(make_power("#PWR06", "power:GND", "GND", GND_D2_X, GND_D2_Y,
                               ref_pos=(GND_D2_X, round(GND_D2_Y + 6.35, 2)),
                               val_pos=(GND_D2_X, round(GND_D2_Y + 3.81, 2))))

    symbols_str = "\n\n".join(symbols)

    # ============================================================
    # NO-CONNECTS
    # ============================================================
    nc_pins = [
        U1_PINS['PGOOD'],
        U1_PINS['DNC8'],
        U1_PINS['DNC9'],
        U1_PINS['DNC10'],
    ]
    nc_parts = []
    for px, py in nc_pins:
        nc_parts.append(f"""  (no_connect (at {px} {py})
    (uuid "{uid()}")
  )""")
    no_connects = "\n".join(nc_parts)

    # ============================================================
    # WIRES (same topology as 5V template)
    # ============================================================
    def wire(x1, y1, x2, y2):
        return f"""  (wire (pts (xy {x1} {y1}) (xy {x2} {y2}))
    (stroke (width 0) (type default))
    (uuid "{uid()}")
  )"""

    wires = []

    # --- Input power: +24V → D1 (Schottky) → VIN rail → IC ---
    # +24V symbol at (102.87, 88.9) connects directly to D1 anode at same point
    # D1 cathode at (102.87, 99.06) → VIN rail at (102.87, 102.87)
    wires.append(wire(102.87, 99.06, 102.87, 102.87))
    wires.append(wire(102.87, 102.87, 105.41, 102.87))

    # --- D2 (TVS) connections: VIN rail → D2 anode, D2 cathode → GND ---
    wires.append(wire(96.52, 102.87, 96.52, 104.14))    # vertical to D2 pin 2
    wires.append(wire(96.52, 102.87, 102.87, 102.87))   # horizontal to VIN rail
    wires.append(wire(96.52, 114.3, 96.52, 116.84))     # D2 pin 1 to GND symbol
    wires.append(wire(105.41, 106.68, 105.41, 102.87))
    wires.append(wire(105.41, 102.87, 116.84, 102.87))
    wires.append(wire(116.84, 104.14, 116.84, 102.87))
    wires.append(wire(116.84, 102.87, 135.89, 102.87))
    wires.append(wire(135.89, 102.87, 135.89, 101.6))
    wires.append(wire(135.89, 104.14, 135.89, 102.87))

    # --- GND + MODE/SYNC ---
    wires.append(wire(128.27, 96.52, 130.81, 96.52))
    wires.append(wire(130.81, 96.52, 135.89, 96.52))
    wires.append(wire(130.81, 96.52, 130.81, 99.06))
    wires.append(wire(135.89, 99.06, 130.81, 99.06))

    # --- EP ground ---
    wires.append(wire(173.99, 93.98, 163.83, 93.98))

    # --- Input cap GND ---
    wires.append(wire(116.84, 114.3, 116.84, 116.84))
    wires.append(wire(105.41, 116.84, 116.84, 116.84))
    wires.append(wire(116.84, 116.84, 116.84, 123.19))

    # --- Output: VOUT → +12V rail ---
    wires.append(wire(163.83, 106.68, 167.64, 106.68))
    wires.append(wire(170.18, 106.68, 167.64, 106.68))
    wires.append(wire(170.18, 100.33, 170.18, 106.68))
    wires.append(wire(167.64, 109.22, 167.64, 106.68))
    wires.append(wire(168.91, 109.22, 167.64, 109.22))
    wires.append(wire(167.64, 119.38, 167.64, 109.22))

    # --- Feedback divider ---
    wires.append(wire(163.83, 104.14, 180.34, 104.14))
    wires.append(wire(179.07, 109.22, 180.34, 109.22))
    wires.append(wire(180.34, 109.22, 180.34, 104.14))
    wires.append(wire(186.69, 104.14, 180.34, 104.14))
    wires.append(wire(186.69, 104.14, 186.69, 119.38))

    # --- Output GND rail ---
    wires.append(wire(167.64, 129.54, 175.26, 129.54))
    wires.append(wire(175.26, 129.54, 186.69, 129.54))
    wires.append(wire(175.26, 129.54, 175.26, 132.08))

    wires_str = "\n\n".join(wires)

    # ============================================================
    # JUNCTIONS
    # ============================================================
    junction_points = [
        (102.87, 102.87),   # D1/D2/VIN rail T-junction
        (105.41, 102.87),
        (116.84, 102.87),
        (135.89, 102.87),
        (130.81, 96.52),
        (116.84, 116.84),
        (167.64, 106.68),
        (167.64, 109.22),
        (180.34, 104.14),
        (175.26, 129.54),
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
  (generator "build_psu_lmzm23601_12v.py")
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
        "psu_lmzm23601_12v.kicad_sch"
    )
    content = build_schematic()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Written: {output_path}")
    print(f"Components: U1, R1, R2, C1, C2, C3, D1 (SS34), D2 (SMBJ26CA)")
    print(f"Power symbols: +24V, +12V, 5x GND")
    print(f"Feedback: Vout = 1.0 * (1 + 110k/10k) = 12.0V")
    print(f"Input protection: D1 reverse polarity, D2 TVS transient")
