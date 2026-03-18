"""
Build audio_max98357.kicad_sch — MAX98357A I2S audio amplifier template.
Matches human-reviewed schematic v3.0:
  R7=100k GAIN_SLOT→GND (6dB), R6=1M SD_MODE→+5V (L/2+R/2 mixed), +5V rail.
  I2S ports (BCLK, LRCLK) on right side (angle=180).
  DIN port on left-top (angle=0), routes vertically down to pin 1.

Pin endpoint formula (VERIFIED):
  The (at x y) in a KiCad lib_symbol pin definition IS the wire connection point.
  Schematic endpoint = (sym_x + pin_at_x, sym_y - pin_at_y)

Run: python build_audio_template.py
"""

import uuid
import os
import re


def uid():
    return str(uuid.uuid4())

# Fixed root UUID so instance paths don't change on regeneration
ROOT_UUID = "a3e7b1c2-5d4f-4a89-9e6c-1f2d3a4b5c6d"


def snap(val, grid=1.27):
    """Snap a value to the nearest 1.27mm grid point."""
    return round(round(val / grid) * grid, 2)


# ============================================================
# LAYOUT — all positions on 1.27mm grid, matching human-reviewed schematic
# ============================================================
# U4 center
U4_X, U4_Y = 153.67, 101.6

# Pin endpoints: endpoint = (sym_x + pin_at_x, sym_y - pin_at_y)
U4_PINS = {
    'DIN':       (round(U4_X - 16.51, 2), round(U4_Y - 8.89, 2)),   # pin 1  = (137.16, 92.71)
    'GAIN_SLOT': (round(U4_X - 16.51, 2), round(U4_Y - 6.35, 2)),   # pin 2  = (137.16, 95.25)
    'GND_3':     (round(U4_X - 16.51, 2), round(U4_Y - 3.81, 2)),   # pin 3  = (137.16, 97.79)
    'SD_MODE':   (round(U4_X - 16.51, 2), round(U4_Y - 1.27, 2)),   # pin 4  = (137.16, 100.33)
    'NC_5':      (round(U4_X - 16.51, 2), round(U4_Y + 1.27, 2)),   # pin 5  = (137.16, 102.87)
    'NC_6':      (round(U4_X - 16.51, 2), round(U4_Y + 3.81, 2)),   # pin 6  = (137.16, 105.41)
    'VDD_7':     (round(U4_X - 16.51, 2), round(U4_Y + 6.35, 2)),   # pin 7  = (137.16, 107.95)
    'VDD_8':     (round(U4_X - 16.51, 2), round(U4_Y + 8.89, 2)),   # pin 8  = (137.16, 110.49)
    'OUTP':      (round(U4_X + 16.51, 2), round(U4_Y + 8.89, 2)),   # pin 9  = (170.18, 110.49)
    'OUTN':      (round(U4_X + 16.51, 2), round(U4_Y + 6.35, 2)),   # pin 10 = (170.18, 107.95)
    'GND_11':    (round(U4_X + 16.51, 2), round(U4_Y + 3.81, 2)),   # pin 11 = (170.18, 105.41)
    'NC_12':     (round(U4_X + 16.51, 2), round(U4_Y - 1.27, 2)),   # pin 12 = (170.18, 100.33)
    'NC_13':     (round(U4_X + 16.51, 2), round(U4_Y + 1.27, 2)),   # pin 13 = (170.18, 102.87)
    'LRCLK':     (round(U4_X + 16.51, 2), round(U4_Y - 3.81, 2)),   # pin 14 = (170.18, 97.79)
    'GND_15':    (round(U4_X + 16.51, 2), round(U4_Y - 6.35, 2)),   # pin 15 = (170.18, 95.25)
    'BCLK':      (round(U4_X + 16.51, 2), round(U4_Y - 8.89, 2)),   # pin 16 = (170.18, 92.71)
    'EP':        (round(U4_X, 2),          round(U4_Y + 13.97, 2)),  # pin 17 = (153.67, 115.57)
}

# R7 (100k, horizontal) — GAIN_SLOT pull-down to GND (6dB gain)
R7_X, R7_Y = 119.38, 87.63
R7_P1 = (round(R7_X - 5.08, 2), R7_Y)            # (114.3, 87.63) → GND
R7_P2 = (round(R7_X + 5.08, 2), R7_Y)            # (124.46, 87.63) → GAIN_SLOT

# R6 (1M, horizontal) — SD_MODE pull-up to +5V (L/2+R/2 mixed)
R6_X, R6_Y = 119.38, 100.33
R6_P1 = (round(R6_X - 5.08, 2), R6_Y)            # (114.3, 100.33) → +5V
R6_P2 = (round(R6_X + 5.08, 2), R6_Y)            # (124.46, 100.33) → SD_MODE

# C15 (10uF, vertical angle=270)
C15_X, C15_Y = 125.73, 113.03
C15_P1 = (C15_X, round(C15_Y - 5.08, 2))         # (125.73, 107.95) = VDD
C15_P2 = (C15_X, round(C15_Y + 5.08, 2))         # (125.73, 118.11) = GND

# C16 (100nF, vertical angle=270)
C16_X, C16_Y = 119.38, 113.03
C16_P1 = (C16_X, round(C16_Y - 5.08, 2))         # (119.38, 107.95) = VDD
C16_P2 = (C16_X, round(C16_Y + 5.08, 2))         # (119.38, 118.11) = GND

# Power symbols
VCC_R6_X, VCC_R6_Y = 106.68, 100.33              # +5V for R6 (sideways, angle=90)
VCC_VDD_X, VCC_VDD_Y = 123.19, 106.68            # +5V for VDD bus (angle=0)

# GND junction point shared by R7.P1 and GND pin 3 routing
GND_JUNC_X, GND_JUNC_Y = 114.3, 92.71

GND_R7_X, GND_R7_Y = 111.76, 92.71               # GND symbol (angle=270, sideways left)
GND_CAP_X, GND_CAP_Y = 123.19, 120.65            # GND below caps (angle=0)
GND_11_X, GND_11_Y = 180.34, 105.41              # GND right of pin 11 (angle=90)
GND_15_X, GND_15_Y = 176.53, 95.25               # GND right of pin 15 (angle=90)
GND_EP_X, GND_EP_Y = 153.67, 119.38              # GND below EP (angle=0)

# Port symbols
DIN_PORT_X, DIN_PORT_Y = 121.92, 78.74           # DIN (angle=0, left side)
DIN_PIN_X = round(DIN_PORT_X + 2.54, 2)          # 124.46

BCLK_PORT_X, BCLK_PORT_Y = 187.96, 91.44         # BCLK (angle=180, right side)
BCLK_PIN_X = round(BCLK_PORT_X - 2.54, 2)        # 185.42

LRCLK_PORT_X, LRCLK_PORT_Y = 187.96, 97.79       # LRCLK (angle=180, right side)
LRCLK_PIN_X = round(LRCLK_PORT_X - 2.54, 2)      # 185.42

OUTP_PORT_X, OUTP_PORT_Y = 189.23, 111.76         # OUTP (angle=180, right side)
OUTP_PIN_X = round(OUTP_PORT_X - 2.54, 2)         # 186.69

OUTN_PORT_X, OUTN_PORT_Y = 189.23, 107.95         # OUTN (angle=180, right side)
OUTN_PIN_X = round(OUTN_PORT_X - 2.54, 2)         # 186.69

# Routing waypoints
BCLK_JOG_X = 181.61                               # BCLK vertical jog x


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
    for port_name in ['DIN', 'BCLK', 'LRCLK', 'OUTP', 'OUTN']:
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
        ("MAX98357AETE_T", False),
        ("CC0805KRX7R9BB104", True),
        ("CL21A106KAYNNNE", True),
        ("0805W8F1003T5E", True),
        ("0805W8F1004T5E", True),
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
    try:
        jlc_symbols = read_lib_symbols()
    except Exception as e:
        print(f"Warning: Could not read JLCImport.kicad_sym: {e}")
        jlc_symbols = {}

    lib_parts = []
    for sym_text in jlc_symbols.values():
        lib_parts.append(f"    {sym_text}")

    # +5V power symbol
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

    # U4 — MAX98357AETE_T
    symbols.append(make_component("U4", "JLCImport:MAX98357AETE_T",
        U4_X, U4_Y, "MAX98357A",
        footprint="JLCImport:MAX98357AETE_T", lcsc="C910544",
        ref_offset=(0, -12.95), val_offset=(0, -15.24)))

    # R7 — 100k GAIN_SLOT to GND (6dB)
    symbols.append(make_component("R7", "JLCImport:0805W8F1003T5E",
        R7_X, R7_Y, "100k",
        footprint="JLCImport:0805W8F1003T5E", lcsc="C17407",
        ref_offset=(0, -2.54), val_offset=(0.76, -4.57)))

    # R6 — 1M SD_MODE to +5V (L/2+R/2 mixed)
    symbols.append(make_component("R6", "JLCImport:0805W8F1004T5E",
        R6_X, R6_Y, "1.0M",
        footprint="JLCImport:0805W8F1004T5E", lcsc="C17514",
        ref_offset=(0, -2.54), val_offset=(0, 2.54)))

    # C15 — 10uF bulk cap (angle=270)
    symbols.append(make_component("C15", "JLCImport:CL21A106KAYNNNE",
        C15_X, C15_Y, "10uF", angle=270,
        footprint="JLCImport:CL21A106KAYNNNE", lcsc="C15850",
        ref_offset=(5.08, -0.25), val_offset=(3.3, 0)))

    # C16 — 100nF decoupling (angle=270)
    symbols.append(make_component("C16", "JLCImport:CC0805KRX7R9BB104",
        C16_X, C16_Y, "100nF", angle=270,
        footprint="JLCImport:CC0805KRX7R9BB104", lcsc="C49678",
        ref_offset=(-3.81, 0), val_offset=(-6.35, 0)))

    # Power — +5V
    symbols.append(make_power("#PWR01", "power:+5V", "+5V",
        VCC_R6_X, VCC_R6_Y, angle=90))
    symbols.append(make_power("#PWR02", "power:+5V", "+5V",
        VCC_VDD_X, VCC_VDD_Y, angle=0))

    # Power — GND
    symbols.append(make_power("#PWR03", "power:GND", "GND",
        GND_R7_X, GND_R7_Y, angle=270))
    symbols.append(make_power("#PWR04", "power:GND", "GND",
        GND_CAP_X, GND_CAP_Y, angle=0))
    symbols.append(make_power("#PWR05", "power:GND", "GND",
        GND_11_X, GND_11_Y, angle=90))
    symbols.append(make_power("#PWR06", "power:GND", "GND",
        GND_15_X, GND_15_Y, angle=90))
    symbols.append(make_power("#PWR07", "power:GND", "GND",
        GND_EP_X, GND_EP_Y, angle=0))

    # Ports — DIN on left (angle=0)
    symbols.append(make_port("#PORT01", "Ports:DIN", "DIN",
        DIN_PORT_X, DIN_PORT_Y, angle=0))

    # Ports — BCLK, LRCLK on right (angle=180)
    symbols.append(make_port("#PORT02", "Ports:BCLK", "BCLK",
        BCLK_PORT_X, BCLK_PORT_Y, angle=180))
    symbols.append(make_port("#PORT03", "Ports:LRCLK", "LRCLK",
        LRCLK_PORT_X, LRCLK_PORT_Y, angle=180))

    # Ports — speaker outputs on right (angle=180)
    symbols.append(make_port("#PORT04", "Ports:OUTP", "OUTP",
        OUTP_PORT_X, OUTP_PORT_Y, angle=180))
    symbols.append(make_port("#PORT05", "Ports:OUTN", "OUTN",
        OUTN_PORT_X, OUTN_PORT_Y, angle=180))

    symbols_str = "\n\n".join(symbols)

    # ============================================================
    # NO-CONNECTS (pins 5, 6, 12, 13)
    # ============================================================
    nc_pins = ['NC_5', 'NC_6', 'NC_12', 'NC_13']
    nc_parts = []
    for nc in nc_pins:
        px, py = U4_PINS[nc]
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

    # --- DIN: port → horizontal → vertical down → pin 1 ---
    wires.append(wire(DIN_PIN_X, DIN_PORT_Y,
                      U4_PINS['DIN'][0], DIN_PORT_Y))         # horizontal
    wires.append(wire(U4_PINS['DIN'][0], DIN_PORT_Y,
                      U4_PINS['DIN'][0], U4_PINS['DIN'][1]))  # vertical down

    # --- BCLK: pin 16 → horizontal → jog up → port ---
    wires.append(wire(U4_PINS['BCLK'][0], U4_PINS['BCLK'][1],
                      BCLK_JOG_X, U4_PINS['BCLK'][1]))        # horizontal
    wires.append(wire(BCLK_JOG_X, U4_PINS['BCLK'][1],
                      BCLK_JOG_X, BCLK_PORT_Y))               # vertical jog
    wires.append(wire(BCLK_JOG_X, BCLK_PORT_Y,
                      BCLK_PIN_X, BCLK_PORT_Y))               # horizontal to port

    # --- LRCLK: pin 14 → straight horizontal → port ---
    wires.append(wire(U4_PINS['LRCLK'][0], U4_PINS['LRCLK'][1],
                      LRCLK_PIN_X, LRCLK_PORT_Y))

    # --- OUTP: pin 9 → vertical jog → horizontal → port ---
    wires.append(wire(U4_PINS['OUTP'][0], U4_PINS['OUTP'][1],
                      U4_PINS['OUTP'][0], OUTP_PORT_Y))       # vertical jog
    wires.append(wire(U4_PINS['OUTP'][0], OUTP_PORT_Y,
                      OUTP_PIN_X, OUTP_PORT_Y))               # horizontal to port

    # --- OUTN: pin 10 → straight horizontal → port ---
    wires.append(wire(U4_PINS['OUTN'][0], U4_PINS['OUTN'][1],
                      OUTN_PIN_X, OUTN_PORT_Y))

    # --- R7: GAIN_SLOT to GND ---
    # R7.P1 → vertical down → junction → GND
    wires.append(wire(R7_P1[0], R7_P1[1],
                      GND_JUNC_X, GND_JUNC_Y))
    wires.append(wire(GND_JUNC_X, GND_JUNC_Y,
                      GND_R7_X, GND_R7_Y))
    # R7.P2 → vertical down → horizontal → GAIN_SLOT
    wires.append(wire(R7_P2[0], R7_P2[1],
                      R7_P2[0], U4_PINS['GAIN_SLOT'][1]))     # vertical
    wires.append(wire(R7_P2[0], U4_PINS['GAIN_SLOT'][1],
                      U4_PINS['GAIN_SLOT'][0], U4_PINS['GAIN_SLOT'][1]))  # horizontal

    # --- R6: SD_MODE to +5V ---
    # +5V → horizontal → R6.P1
    wires.append(wire(VCC_R6_X, VCC_R6_Y,
                      R6_P1[0], R6_P1[1]))
    # R6.P2 → horizontal → SD_MODE
    wires.append(wire(R6_P2[0], R6_P2[1],
                      U4_PINS['SD_MODE'][0], U4_PINS['SD_MODE'][1]))

    # --- GND pin 3: routed from shared junction ---
    # Junction → horizontal waypoint → vertical → pin 3
    waypoint_x = 121.92
    wires.append(wire(GND_JUNC_X, GND_JUNC_Y,
                      waypoint_x, GND_JUNC_Y))                # horizontal from junction
    wires.append(wire(waypoint_x, GND_JUNC_Y,
                      waypoint_x, U4_PINS['GND_3'][1]))       # vertical down
    wires.append(wire(waypoint_x, U4_PINS['GND_3'][1],
                      U4_PINS['GND_3'][0], U4_PINS['GND_3'][1]))  # horizontal to pin

    # --- VDD power bus ---
    # +5V → vertical down to cap bus
    cap_bus_y = C15_P1[1]  # 107.95
    wires.append(wire(VCC_VDD_X, VCC_VDD_Y,
                      VCC_VDD_X, cap_bus_y))
    # Cap bus: C16 → junction → C15 → VDD pins
    wires.append(wire(C16_P1[0], cap_bus_y,
                      VCC_VDD_X, cap_bus_y))
    wires.append(wire(VCC_VDD_X, cap_bus_y,
                      C15_P1[0], cap_bus_y))
    wires.append(wire(C15_P1[0], cap_bus_y,
                      U4_PINS['VDD_7'][0], cap_bus_y))
    # VDD pin 7 → pin 8
    wires.append(wire(U4_PINS['VDD_7'][0], U4_PINS['VDD_7'][1],
                      U4_PINS['VDD_8'][0], U4_PINS['VDD_8'][1]))

    # --- Cap GND ---
    wires.append(wire(C16_P2[0], C16_P2[1],
                      GND_CAP_X, C16_P2[1]))                  # C16 bottom → junction
    wires.append(wire(GND_CAP_X, C16_P2[1],
                      C15_P2[0], C15_P2[1]))                  # junction → C15 bottom
    wires.append(wire(GND_CAP_X, C16_P2[1],
                      GND_CAP_X, GND_CAP_Y))                  # junction → GND symbol

    # --- Right-side GND ---
    wires.append(wire(U4_PINS['GND_11'][0], U4_PINS['GND_11'][1],
                      GND_11_X, GND_11_Y))
    wires.append(wire(U4_PINS['GND_15'][0], U4_PINS['GND_15'][1],
                      GND_15_X, GND_15_Y))

    # --- EP GND ---
    wires.append(wire(U4_PINS['EP'][0], U4_PINS['EP'][1],
                      GND_EP_X, GND_EP_Y))

    wires_str = "\n\n".join(wires)

    # ============================================================
    # JUNCTIONS
    # ============================================================
    junctions = []
    # R7.P1 / GND pin 3 shared junction
    junctions.append(f"""  (junction (at {GND_JUNC_X} {GND_JUNC_Y})
    (diameter 0)
    (color 0 0 0 0)
    (uuid "{uid()}")
  )""")
    # VDD bus junction at +5V entry
    junctions.append(f"""  (junction (at {VCC_VDD_X} {cap_bus_y})
    (diameter 0)
    (color 0 0 0 0)
    (uuid "{uid()}")
  )""")
    # VDD bus junction at C15
    junctions.append(f"""  (junction (at {C15_P1[0]} {cap_bus_y})
    (diameter 0)
    (color 0 0 0 0)
    (uuid "{uid()}")
  )""")
    # VDD bus junction at VDD pin 7 (vertical to pin 8)
    junctions.append(f"""  (junction (at {U4_PINS['VDD_7'][0]} {cap_bus_y})
    (diameter 0)
    (color 0 0 0 0)
    (uuid "{uid()}")
  )""")
    # Cap GND junction
    junctions.append(f"""  (junction (at {GND_CAP_X} {C16_P2[1]})
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
  (generator "build_audio_template.py")
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
        "audio_max98357.kicad_sch"
    )
    content = build_schematic()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Written: {output_path}")
    print(f"Components: U4, R7 (100k to GND), R6 (1M to +5V), C15, C16")
    print(f"Port symbols: DIN (left), BCLK/LRCLK (right), OUTP/OUTN (right)")
    print(f"Power symbols: 2x +5V, 5x GND")
    print(f"No-connects: pins 5, 6, 12, 13")
    print(f"\nLayout:")
    print(f"  U4  at ({U4_X}, {U4_Y})")
    print(f"  R7  at ({R7_X}, {R7_Y}) — 100k GAIN_SLOT to GND (6dB)")
    print(f"  R6  at ({R6_X}, {R6_Y}) — 1M SD_MODE to +5V")
    print(f"  C15 at ({C15_X}, {C15_Y}) angle=270")
    print(f"  C16 at ({C16_X}, {C16_Y}) angle=270")
