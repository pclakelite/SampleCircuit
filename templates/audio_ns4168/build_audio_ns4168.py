"""
Build audio_ns4168.kicad_sch -- NS4168 I2S audio amplifier template.
Follows datasheet recommendations:
  R20=100k CTRL pull-down to GND (shutdown at boot, GPIO enables right channel).
  100uF+1uF VDD bypass caps (per datasheet section 10.4).
  I2S ports (LRCLK, BCLK, DIN) on left side (angle=0).
  Speaker ports (OUTP, OUTN) on right side (angle=180).
  AMP_EN port on left side for GPIO shutdown control.

Pin endpoint formula (VERIFIED):
  The (at x y) in a KiCad lib_symbol pin definition IS the wire connection point.
  Schematic endpoint = (sym_x + px, sym_y - py) for angle=0.
  For rotated symbols, rotate (px, py) first, then apply.

Pin offsets per component:
  Resistor 0805W8F1003T5E: pins at ±5.08mm (horizontal)
  Capacitor CL21B105KBFNNNE: pins at ±3.81mm (horizontal)
  Electrolytic ECAP_100uF: pins at (0, ±3.81mm) (vertical)
  NS4168: see pin table below

Run: python build_audio_ns4168.py
"""

import uuid
import os
import re


def uid():
    return str(uuid.uuid4())

# Fixed root UUID so instance paths don't change on regeneration
ROOT_UUID = "b4f8a2d1-6e3c-4b97-ae5d-2g3h4i5j6k7l"


def snap(val, grid=1.27):
    """Snap a value to the nearest 1.27mm grid point."""
    return round(round(val / grid) * grid, 2)


# ============================================================
# LAYOUT -- all positions on 1.27mm grid
# ============================================================
# U5 center
U5_X, U5_Y = 152.40, 101.60

# Pin endpoints: endpoint = (sym_x + pin_at_x, sym_y - pin_at_y)
U5_PINS = {
    'CTRL':   (round(U5_X - 11.43, 2), round(U5_Y - 2.54, 2)),   # pin 1 = (140.97, 99.06)
    'LRCLK':  (round(U5_X - 11.43, 2), round(U5_Y - 0, 2)),      # pin 2 = (140.97, 101.60)
    'BCLK':   (round(U5_X - 11.43, 2), round(U5_Y + 2.54, 2)),   # pin 3 = (140.97, 104.14)
    'SDATA':  (round(U5_X - 11.43, 2), round(U5_Y + 5.08, 2)),   # pin 4 = (140.97, 106.68)
    'VON':    (round(U5_X + 11.43, 2), round(U5_Y + 5.08, 2)),   # pin 5 = (163.83, 106.68)
    'VDD':    (round(U5_X + 11.43, 2), round(U5_Y + 2.54, 2)),   # pin 6 = (163.83, 104.14)
    'GND':    (round(U5_X + 11.43, 2), round(U5_Y + 0, 2)),      # pin 7 = (163.83, 101.60)
    'VOP':    (round(U5_X + 11.43, 2), round(U5_Y - 2.54, 2)),   # pin 8 = (163.83, 99.06)
    'EP':     (round(U5_X + 11.43, 2), round(U5_Y - 5.08, 2)),   # pin 9 = (163.83, 96.52)
}

# R20 (100k, vertical angle=90) -- CTRL pull-down to GND (shutdown at boot)
# At angle=90: Pin2 (top) at (sym_x, sym_y - 5.08), Pin1 (bottom) at (sym_x, sym_y + 5.08)
# Pin2 must connect to CTRL wire at y=99.06 → sym_y = 99.06 + 5.08 = 104.14
R20_X, R20_Y = 132.08, 104.14
R20_P2 = (R20_X, round(R20_Y - 5.08, 2))   # (132.08, 99.06) -> CTRL wire [top]
R20_P1 = (R20_X, round(R20_Y + 5.08, 2))   # (132.08, 109.22) -> GND [bottom]

# C17 (1uF ceramic, angle=270)
# At angle=270: Pin1 at (sym_x, sym_y - 3.81), Pin2 at (sym_x, sym_y + 3.81)
# Pin1 must connect to VDD bus at y=104.14 → sym_y = 104.14 + 3.81 = 107.95
C17_X, C17_Y = 172.72, 107.95
C17_P1 = (C17_X, round(C17_Y - 3.81, 2))   # (172.72, 104.14) = VDD bus
C17_P2 = (C17_X, round(C17_Y + 3.81, 2))   # (172.72, 111.76) = GND side

# C18 (100uF electrolytic, already vertical, angle=0)
# Electrolytic pins: P1 at (0, 3.81) → top, P2 at (0, -3.81) → bottom
# endpoint P1 = (sym_x, sym_y - 3.81), P2 = (sym_x, sym_y + 3.81)
C18_X, C18_Y = 180.34, 107.95
C18_P1 = (C18_X, round(C18_Y - 3.81, 2))   # (180.34, 104.14) = VDD bus
C18_P2 = (C18_X, round(C18_Y + 3.81, 2))   # (180.34, 111.76) = GND side

# Power symbols
VCC_VDD_X, VCC_VDD_Y = 176.53, 101.60      # +5V for VDD bus

GND_7_X, GND_7_Y = 170.18, 101.60          # GND right of pin 7 (angle=90)
GND_EP_X, GND_EP_Y = 170.18, 96.52         # GND right of EP (angle=90)
GND_R20_X, GND_R20_Y = 132.08, 111.76      # GND below R20 (angle=0)
GND_C17_X, GND_C17_Y = 172.72, 114.30      # GND below C17 (angle=0)
GND_C18_X, GND_C18_Y = 180.34, 114.30      # GND below C18 (angle=0)

# Port symbols
AMP_EN_PORT_X, AMP_EN_PORT_Y = 121.92, 99.06   # AMP_EN (angle=0, left side)
AMP_EN_PIN_X = round(AMP_EN_PORT_X + 2.54, 2)  # 124.46

DIN_PORT_X, DIN_PORT_Y = 121.92, 106.68         # DIN (angle=0, left side)
DIN_PIN_X = round(DIN_PORT_X + 2.54, 2)         # 124.46

BCLK_PORT_X, BCLK_PORT_Y = 121.92, 104.14      # BCLK (angle=0, left side)
BCLK_PIN_X = round(BCLK_PORT_X + 2.54, 2)      # 124.46

LRCLK_PORT_X, LRCLK_PORT_Y = 121.92, 101.60    # LRCLK (angle=0, left side)
LRCLK_PIN_X = round(LRCLK_PORT_X + 2.54, 2)    # 124.46

OUTP_PORT_X, OUTP_PORT_Y = 187.96, 99.06        # OUTP (angle=180, right side)
OUTP_PIN_X = round(OUTP_PORT_X - 2.54, 2)       # 185.42

OUTN_PORT_X, OUTN_PORT_Y = 187.96, 106.68       # OUTN (angle=180, right side)
OUTN_PIN_X = round(OUTN_PORT_X - 2.54, 2)       # 185.42


# ============================================================
# LIB_SYMBOLS -- read from project libraries
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
    for port_name in ['AMP_EN', 'DIN', 'BCLK', 'LRCLK', 'OUTP', 'OUTN']:
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
        ("NS4168_C910588", False),          # IC -- keep pin names visible
        ("0805W8F1003T5E", True),            # 100K resistor
        ("CL21B105KBFNNNE", True),           # 1uF ceramic cap
        ("ECAP_100uF_50V_C2992088", True),   # 100uF electrolytic cap
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

    # U5 -- NS4168
    symbols.append(make_component("U5", "JLCImport:NS4168_C910588",
        U5_X, U5_Y, "NS4168",
        footprint="JLCImport:NS4168_C910588", lcsc="C910588",
        ref_offset=(0, -10.16), val_offset=(0, -12.70)))

    # R20 -- 100k CTRL pull-down to GND (shutdown at boot, GPIO enables)
    symbols.append(make_component("R20", "JLCImport:0805W8F1003T5E",
        R20_X, R20_Y, "100k", angle=90,
        footprint="JLCImport:0805W8F1003T5E", lcsc="C17407",
        ref_offset=(-3.81, 0), val_offset=(-6.35, 0)))

    # C17 -- 1uF ceramic decoupling (angle=270)
    symbols.append(make_component("C17", "JLCImport:CL21B105KBFNNNE",
        C17_X, C17_Y, "1uF", angle=270,
        footprint="JLCImport:CL21B105KBFNNNE", lcsc="C28323",
        ref_offset=(-3.81, 0), val_offset=(-6.35, 0)))

    # C18 -- 100uF electrolytic bulk cap (angle=0, already vertical)
    symbols.append(make_component("C18", "JLCImport:ECAP_100uF_50V_C2992088",
        C18_X, C18_Y, "100uF", angle=0,
        footprint="JLCImport:HV221M025F105R", lcsc="C2992088",
        ref_offset=(3.81, 0), val_offset=(3.81, 2.54)))

    # Power -- +5V (only one now, for VDD bus)
    symbols.append(make_power("#PWR01", "power:+5V", "+5V",
        VCC_VDD_X, VCC_VDD_Y, angle=0))

    # Power -- GND
    symbols.append(make_power("#PWR02", "power:GND", "GND",
        GND_7_X, GND_7_Y, angle=90))
    symbols.append(make_power("#PWR03", "power:GND", "GND",
        GND_EP_X, GND_EP_Y, angle=90))
    symbols.append(make_power("#PWR04", "power:GND", "GND",
        GND_R20_X, GND_R20_Y, angle=0))
    symbols.append(make_power("#PWR05", "power:GND", "GND",
        GND_C17_X, GND_C17_Y, angle=0))
    symbols.append(make_power("#PWR06", "power:GND", "GND",
        GND_C18_X, GND_C18_Y, angle=0))

    # Ports -- AMP_EN on left (angle=0)
    symbols.append(make_port("#PORT01", "Ports:AMP_EN", "AMP_EN",
        AMP_EN_PORT_X, AMP_EN_PORT_Y, angle=0))

    # Ports -- I2S on left (angle=0)
    symbols.append(make_port("#PORT02", "Ports:DIN", "DIN",
        DIN_PORT_X, DIN_PORT_Y, angle=0))
    symbols.append(make_port("#PORT03", "Ports:BCLK", "BCLK",
        BCLK_PORT_X, BCLK_PORT_Y, angle=0))
    symbols.append(make_port("#PORT04", "Ports:LRCLK", "LRCLK",
        LRCLK_PORT_X, LRCLK_PORT_Y, angle=0))

    # Ports -- speaker outputs on right (angle=180)
    symbols.append(make_port("#PORT05", "Ports:OUTP", "OUTP",
        OUTP_PORT_X, OUTP_PORT_Y, angle=180))
    symbols.append(make_port("#PORT06", "Ports:OUTN", "OUTN",
        OUTN_PORT_X, OUTN_PORT_Y, angle=180))

    symbols_str = "\n\n".join(symbols)

    # ============================================================
    # WIRES
    # ============================================================
    def wire(x1, y1, x2, y2):
        return f"""  (wire (pts (xy {x1} {y1}) (xy {x2} {y2}))
    (stroke (width 0) (type default))
    (uuid "{uid()}")
  )"""

    wires = []

    # --- AMP_EN -> CTRL: port pin -> straight horizontal -> U5.CTRL ---
    wires.append(wire(AMP_EN_PIN_X, AMP_EN_PORT_Y,
                      U5_PINS['CTRL'][0], U5_PINS['CTRL'][1]))

    # --- R20 pull-down: R20.P1 -> GND ---
    wires.append(wire(R20_P1[0], R20_P1[1],
                      GND_R20_X, GND_R20_Y))

    # --- LRCLK: port -> straight horizontal -> pin 2 ---
    wires.append(wire(LRCLK_PIN_X, LRCLK_PORT_Y,
                      U5_PINS['LRCLK'][0], U5_PINS['LRCLK'][1]))

    # --- BCLK: port -> straight horizontal -> pin 3 ---
    wires.append(wire(BCLK_PIN_X, BCLK_PORT_Y,
                      U5_PINS['BCLK'][0], U5_PINS['BCLK'][1]))

    # --- DIN -> SDATA: port -> straight horizontal -> pin 4 ---
    wires.append(wire(DIN_PIN_X, DIN_PORT_Y,
                      U5_PINS['SDATA'][0], U5_PINS['SDATA'][1]))

    # --- VOP -> OUTP: straight horizontal ---
    wires.append(wire(U5_PINS['VOP'][0], U5_PINS['VOP'][1],
                      OUTP_PIN_X, OUTP_PORT_Y))

    # --- VON -> OUTN: straight horizontal ---
    wires.append(wire(U5_PINS['VON'][0], U5_PINS['VON'][1],
                      OUTN_PIN_X, OUTN_PORT_Y))

    # --- GND pin 7 ---
    wires.append(wire(U5_PINS['GND'][0], U5_PINS['GND'][1],
                      GND_7_X, GND_7_Y))

    # --- EP GND ---
    wires.append(wire(U5_PINS['EP'][0], U5_PINS['EP'][1],
                      GND_EP_X, GND_EP_Y))

    # --- VDD power bus ---
    # VDD pin -> C17 top (both at y=104.14)
    wires.append(wire(U5_PINS['VDD'][0], U5_PINS['VDD'][1],
                      C17_P1[0], C17_P1[1]))
    # C17 top -> C18 top (both at y=104.14)
    wires.append(wire(C17_P1[0], C17_P1[1],
                      C18_P1[0], C18_P1[1]))
    # +5V down to VDD bus
    wires.append(wire(VCC_VDD_X, VCC_VDD_Y,
                      VCC_VDD_X, U5_PINS['VDD'][1]))

    # --- Cap GND ---
    # C17 bottom -> GND
    wires.append(wire(C17_P2[0], C17_P2[1],
                      GND_C17_X, GND_C17_Y))
    # C18 bottom -> GND
    wires.append(wire(C18_P2[0], C18_P2[1],
                      GND_C18_X, GND_C18_Y))

    wires_str = "\n\n".join(wires)

    # ============================================================
    # JUNCTIONS
    # ============================================================
    junctions = []
    # C17 top meets VDD bus
    junctions.append(f"""  (junction (at {C17_P1[0]} {C17_P1[1]})
    (diameter 0)
    (color 0 0 0 0)
    (uuid "{uid()}")
  )""")
    # +5V vertical meets VDD bus
    junctions.append(f"""  (junction (at {VCC_VDD_X} {U5_PINS['VDD'][1]})
    (diameter 0)
    (color 0 0 0 0)
    (uuid "{uid()}")
  )""")
    # R20 top meets AMP_EN->CTRL wire
    junctions.append(f"""  (junction (at {R20_P2[0]} {R20_P2[1]})
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
  (generator "build_audio_ns4168.py")
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
    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "audio_ns4168.kicad_sch"
    )
    content = build_schematic()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Written: {output_path}")
    print(f"Components: U5 (NS4168), R20 (100k pull-down), C17 (1uF), C18 (100uF)")
    print(f"Port symbols: AMP_EN/DIN/BCLK/LRCLK (left), OUTP/OUTN (right)")
    print(f"Power symbols: 1x +5V, 5x GND")
    print(f"\nLayout:")
    print(f"  U5  at ({U5_X}, {U5_Y})")
    print(f"  R20 at ({R20_X}, {R20_Y}) angle=90 -- 100k CTRL pull-down to GND")
    print(f"  C17 at ({C17_X}, {C17_Y}) angle=270 -- 1uF ceramic (pins at ±3.81)")
    print(f"  C18 at ({C18_X}, {C18_Y}) -- 100uF electrolytic (pins at ±3.81)")
    print(f"\nPin verification:")
    print(f"  C17_P1 = {C17_P1} (should be 104.14 = VDD bus)")
    print(f"  C17_P2 = {C17_P2} (should be 111.76 = GND side)")
    print(f"  C18_P1 = {C18_P1} (should be 104.14 = VDD bus)")
    print(f"  C18_P2 = {C18_P2} (should be 111.76 = GND side)")
    print(f"  R20_P2 = {R20_P2} (should be 99.06 = CTRL wire)")
    print(f"  R20_P1 = {R20_P1} (should be 109.22 = GND side)")
