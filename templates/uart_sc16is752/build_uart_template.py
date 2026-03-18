"""
Build uart_sc16is752.kicad_sch — SC16IS752 I2C-to-dual-UART bridge template.
Minimal version: Channel A TX/RX + I2C (SCL/SDA). All other pins NC.

Layout matches nebkat/i2c_uart_board_reference_design schematic:
- U1 centered, pins left/right
- Crystal below XTAL1/XTAL2 pins, R3 (1M feedback) below crystal,
  C1 below-left, C2 below-right, single GND at bottom center
- Pull-up resistors (R1 RESET, R2 IRQ) stacked horizontally upper-left of U1
  with +3.3V on left end, signal labels dropping from junction
- Port symbols (TX, RX, SCL, SDA) on the left at their respective pins

Pin endpoint formula (VERIFIED):
  The (at x y) in a KiCad lib_symbol pin definition IS the wire connection point.
  Schematic endpoint = (sym_x + pin_at_x, sym_y - pin_at_y)

Run: python build_uart_template.py
"""

import uuid
import os
import re


def uid():
    return str(uuid.uuid4())

# Fixed root UUID so instance paths don't change on regeneration
ROOT_UUID = "d7e8f9a0-1b2c-3d4e-5f6a-7b8c9d0e1f2a"


def snap(val, grid=1.27):
    """Snap a value to the nearest 1.27mm grid point."""
    return round(round(val / grid) * grid, 2)


# ============================================================
# LAYOUT — all positions on 1.27mm grid
# Matches reference schematic: i2c-uart.png
# ============================================================
# U1 center — positioned to give room for crystal area below-left
U1_X, U1_Y = 149.86, 100.33

# U1 pin endpoints: endpoint = (sym_x + pin_at_x, sym_y - pin_at_y)
LX = round(U1_X - 20.32, 2)   # 129.54  (left pins)
RX = round(U1_X + 20.32, 2)   # 170.18  (right pins)

U1_PINS = {
    'RTSA':    (LX, round(U1_Y - 16.51, 2)),   # pin 1  = (129.54, 83.82)
    'CTSA':    (LX, round(U1_Y - 13.97, 2)),   # pin 2  = (129.54, 86.36)
    'TXA':     (LX, round(U1_Y - 11.43, 2)),   # pin 3  = (129.54, 88.90)
    'RXA':     (LX, round(U1_Y - 8.89, 2)),    # pin 4  = (129.54, 91.44)
    'RESET':   (LX, round(U1_Y - 6.35, 2)),    # pin 5  = (129.54, 93.98)
    'XTAL1':   (LX, round(U1_Y - 3.81, 2)),    # pin 6  = (129.54, 96.52)
    'XTAL2':   (LX, round(U1_Y - 1.27, 2)),    # pin 7  = (129.54, 99.06)
    'VDD':     (LX, round(U1_Y + 1.27, 2)),    # pin 8  = (129.54, 101.60)
    'I2CSPI':  (LX, round(U1_Y + 3.81, 2)),    # pin 9  = (129.54, 104.14)
    'A0':      (LX, round(U1_Y + 6.35, 2)),    # pin 10 = (129.54, 106.68)
    'A1':      (LX, round(U1_Y + 8.89, 2)),    # pin 11 = (129.54, 109.22)
    'NC12':    (LX, round(U1_Y + 11.43, 2)),   # pin 12 = (129.54, 111.76)
    'SCL':     (LX, round(U1_Y + 13.97, 2)),   # pin 13 = (129.54, 114.30)
    'SDA':     (LX, round(U1_Y + 16.51, 2)),   # pin 14 = (129.54, 116.84)
    'IRQ':     (RX, round(U1_Y + 16.51, 2)),   # pin 15 = (170.18, 116.84)
    'CTSB':    (RX, round(U1_Y + 13.97, 2)),   # pin 16 = (170.18, 114.30)
    'RTSB':    (RX, round(U1_Y + 11.43, 2)),   # pin 17 = (170.18, 111.76)
    'GPIO0':   (RX, round(U1_Y + 8.89, 2)),    # pin 18 = (170.18, 109.22)
    'GPIO1':   (RX, round(U1_Y + 6.35, 2)),    # pin 19 = (170.18, 106.68)
    'GPIO2':   (RX, round(U1_Y + 3.81, 2)),    # pin 20 = (170.18, 104.14)
    'GPIO3':   (RX, round(U1_Y + 1.27, 2)),    # pin 21 = (170.18, 101.60)
    'VSS':     (RX, round(U1_Y - 1.27, 2)),    # pin 22 = (170.18, 99.06)
    'TXB':     (RX, round(U1_Y - 3.81, 2)),    # pin 23 = (170.18, 96.52)
    'RXB':     (RX, round(U1_Y - 6.35, 2)),    # pin 24 = (170.18, 93.98)
    'GPIO4':   (RX, round(U1_Y - 8.89, 2)),    # pin 25 = (170.18, 91.44)
    'GPIO5':   (RX, round(U1_Y - 11.43, 2)),   # pin 26 = (170.18, 88.90)
    'GPIO6':   (RX, round(U1_Y - 13.97, 2)),   # pin 27 = (170.18, 86.36)
    'GPIO7':   (RX, round(U1_Y - 16.51, 2)),   # pin 28 = (170.18, 83.82)
}

# ============================================================
# Crystal area — reference style: crystal, then feedback R below, caps below that
# All centered below XTAL1(96.52)/XTAL2(99.06) pins
# ============================================================
# Two vertical wires drop from XTAL1 and XTAL2 to the crystal.
# In the reference, XTAL1 goes to the left side, XTAL2 to the right side.
# XTAL1 wire drops at x=119.38 (left column), XTAL2 wire drops at x=124.46 (right column)

# X1 crystal center: between the two drop wires, below XTAL pins
# Crystal pin layout for 7U14745AE12UCG (angle=0):
#   Pin 1 (OSC1): exits LEFT  at local (-7.62, -2.54) → endpoint (X-7.62, Y+2.54)
#   Pin 2 (GND):  exits RIGHT at local (7.62, -2.54)  → endpoint (X+7.62, Y+2.54)
#   Pin 3 (OSC2): exits RIGHT at local (7.62, 2.54)   → endpoint (X+7.62, Y-2.54)
#   Pin 4 (GND):  exits LEFT  at local (-7.62, 2.54)  → endpoint (X-7.62, Y-2.54)
#
# We want OSC1 (left) at x≈119.38 and OSC2 (right) at x≈124.46
# OSC1 endpoint x = X1_X - 7.62, so X1_X = 119.38 + 7.62 = 127.00
# OSC2 endpoint x = X1_X + 7.62 = 127.00 + 7.62 = 134.62 — too far right
#
# Actually let's position crystal so that wires from XTAL1/XTAL2 reach it cleanly.
# Reference has crystal below-left with XTAL1 on left, XTAL2 on right.
# Let's use drop wires at the same x as XTAL pins, then route to crystal.
#
# Simpler approach matching reference: two vertical drop wires from XTAL1/XTAL2,
# crystal horizontally between them with short horizontal stubs.

# Drop wire columns (from XTAL1 and XTAL2 pins going down)
XTAL1_DROP_X = 119.38   # column for XTAL1 net
XTAL2_DROP_X = 124.46   # column for XTAL2 net

# Crystal at center between drop columns
X1_X = round((XTAL1_DROP_X + XTAL2_DROP_X) / 2, 2)  # 121.92
X1_Y = 104.14   # below XTAL pins

# Crystal pin endpoints
X1_OSC1 = (round(X1_X - 7.62, 2), round(X1_Y + 2.54, 2))   # left pin  (114.30, 106.68)
X1_GND2 = (round(X1_X + 7.62, 2), round(X1_Y + 2.54, 2))   # right gnd (129.54, 106.68)
X1_OSC2 = (round(X1_X + 7.62, 2), round(X1_Y - 2.54, 2))   # right pin (129.54, 101.60)
X1_GND4 = (round(X1_X - 7.62, 2), round(X1_Y - 2.54, 2))   # left gnd  (114.30, 101.60)

# R3 (1M feedback) — below crystal, horizontal, centered same as crystal
# Reference: R5 is directly below Y1
R3_X = X1_X      # 121.92
R3_Y = 110.49    # below crystal
R3_P1 = (round(R3_X - 5.08, 2), R3_Y)   # (116.84, 110.49) — XTAL1 net side
R3_P2 = (round(R3_X + 5.08, 2), R3_Y)   # (127.00, 110.49) — XTAL2 net side

# C1 (15pF XTAL1 load cap) — below R3, left side (under R3.P1)
# Vertical cap, angle=270
C1_X = R3_P1[0]   # 116.84
C1_Y = 116.84
C1_P1 = (C1_X, round(C1_Y - 5.08, 2))   # (116.84, 111.76) — XTAL1 net
C1_P2 = (C1_X, round(C1_Y + 5.08, 2))   # (116.84, 121.92) — GND

# C2 (15pF XTAL2 load cap) — below R3, right side (under R3.P2)
# Vertical cap, angle=270
C2_X = R3_P2[0]   # 127.00
C2_Y = 116.84
C2_P1 = (C2_X, round(C2_Y - 5.08, 2))   # (127.00, 111.76) — XTAL2 net
C2_P2 = (C2_X, round(C2_Y + 5.08, 2))   # (127.00, 121.92) — GND

# Single GND symbol at bottom center (reference style)
GND_XTAL_X = X1_X   # 121.92
GND_XTAL_Y = 124.46

# ============================================================
# Pull-up resistors — reference style: upper-left of U1, horizontal
# R1 = RESET pull-up (1k in ref, 10k for us), R2 = IRQ pull-up (1k)
# Stacked: R2 (IRQ) on top row, R1 (RESET) below
# +3.3V on left end, signal to right into U1
# ============================================================

# R2 (IRQ pull-up, 1k) — top row, horizontal
# In reference: R6 is at upper-left. IRQ (pin 15, right side) wraps around top.
# For our sub-circuit: IRQ wire goes from pin 15 up and over to upper-left area
R2_X = 113.03
R2_Y = 82.55
R2_P1 = (round(R2_X - 5.08, 2), R2_Y)   # (107.95, 82.55) — +3.3V end
R2_P2 = (round(R2_X + 5.08, 2), R2_Y)   # (118.11, 82.55) — IRQ net

# R1 (RESET pull-up, 10k) — below R2, horizontal
R1_X = 113.03
R1_Y = 85.09
R1_P1 = (round(R1_X - 5.08, 2), R1_Y)   # (107.95, 85.09) — +3.3V end
R1_P2 = (round(R1_X + 5.08, 2), R1_Y)   # (118.11, 85.09) — RESET net

# +3.3V for pull-ups — single symbol, left of both resistors
VCC_PULLUP_X = 105.41
VCC_PULLUP_Y = 83.82  # between R1 and R2

# Junction where both resistor P1 ends meet the +3.3V vertical wire
# R2.P1 at (107.95, 82.55), R1.P1 at (107.95, 85.09)
# Vertical +3.3V wire at x=107.95 from y=82.55 to y=85.09

# IRQ routing: pin 15 (170.18, 116.84) → up to top → left to R2.P2
# We'll route: right from pin → up → left across top → down to R2.P2
IRQ_TURN_X = 172.72   # just right of U1
IRQ_TURN_Y = 80.01    # above U1
IRQ_LEFT_X = R2_P2[0] # 118.11

# RESET routing: pin 5 (129.54, 93.98) → left to R1.P2 x → up to R1.P2
RESET_TURN_X = R1_P2[0]  # 118.11

# ============================================================
# Port symbols — reference style: labels on the left at pin level
# Port pin exits right at (port_x + 2.54, port_y)
# ============================================================
TX_PORT_X = 119.38
TX_PORT_Y = U1_PINS['TXA'][1]    # 88.90

RX_PORT_X = 119.38
RX_PORT_Y = U1_PINS['RXA'][1]    # 91.44

SCL_PORT_X = 119.38
SCL_PORT_Y = U1_PINS['SCL'][1]   # 114.30

SDA_PORT_X = 119.38
SDA_PORT_Y = U1_PINS['SDA'][1]   # 116.84

TX_PIN = (round(TX_PORT_X + 2.54, 2), TX_PORT_Y)
RX_PIN = (round(RX_PORT_X + 2.54, 2), RX_PORT_Y)
SCL_PIN = (round(SCL_PORT_X + 2.54, 2), SCL_PORT_Y)
SDA_PIN = (round(SDA_PORT_X + 2.54, 2), SDA_PORT_Y)

# ============================================================
# Power symbols
# ============================================================
# +3.3V for VDD (above U1, reference style)
VCC_VDD_X = U1_X     # 149.86  centered above U1
VCC_VDD_Y = 78.74    # above U1

# +3.3V for pull-ups (left of R1/R2)
# Already defined: VCC_PULLUP_X, VCC_PULLUP_Y

# C3 (100nF VDD decoupling) — near VDD, right side of U1 body
C3_X = U1_X      # 149.86 (centered on U1)
C3_Y = 124.46    # below U1
C3_P1 = (C3_X, round(C3_Y - 5.08, 2))   # (149.86, 119.38) — VDD net
C3_P2 = (C3_X, round(C3_Y + 5.08, 2))   # (149.86, 129.54) — GND

# GND symbols
GND_VSS_X = U1_PINS['VSS'][0]    # 170.18 — right side, below VSS
GND_VSS_Y = round(U1_PINS['VSS'][1] + 5.08, 2)  # 104.14

GND_C3_X = C3_X                   # 149.86
GND_C3_Y = round(C3_P2[1] + 2.54, 2)  # 132.08

# GND for A0/A1 — small GND symbols sideways off the pins
GND_A0_X = round(U1_PINS['A0'][0] - 5.08, 2)   # 124.46
GND_A0_Y = U1_PINS['A0'][1]                      # 106.68

GND_A1_X = round(U1_PINS['A1'][0] - 5.08, 2)   # 124.46
GND_A1_Y = U1_PINS['A1'][1]                      # 109.22

# GND for crystal pins (X1 has 2 GND pins)
# Pin 4 GND at (114.30, 101.60) — left side
# Pin 2 GND at (129.54, 106.68) — right side
GND_X1_P4_X = X1_GND4[0]   # 114.30
GND_X1_P4_Y = round(X1_GND4[1] - 2.54, 2)   # 99.06

GND_X1_P2_X = X1_GND2[0]   # 129.54
GND_X1_P2_Y = round(X1_GND2[1] + 2.54, 2)   # 109.22


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
    for port_name in ['SCL', 'SDA', 'TX', 'RX']:
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
    """Read JLCImport symbol definitions needed for this template."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    jlc_path = os.path.join(project_root, "JLCImport.kicad_sym")

    # (symbol_name, hide_pin_names)
    needed_symbols = [
        ("SC16IS752IPW_112", False),    # IC — keep pin names visible
        ("7U14745AE12UCG", True),       # 14.7456MHz Crystal — hide names
        ("CL21C150JBANNNC", True),      # 15pF cap — hide names
        ("CC0805KRX7R9BB104", True),    # 100nF cap — hide names
        ("0805W8F1002T5E", True),       # 10k resistor — hide names
        ("0805W8F1001T5E", True),       # 1k resistor — hide names
        ("0805W8F1004T5E", True),       # 1M resistor — hide names
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

        # Hide pin numbers on all symbols
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

        # Hide pin names on passives/crystal
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
        print(f"ERROR: Could not read JLCImport.kicad_sym: {e}")
        raise

    lib_parts = []
    for sym_text in jlc_symbols.values():
        lib_parts.append(f"    {sym_text}")

    # +3.3V power symbol
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
    # HELPER FUNCTIONS
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

    def wire(x1, y1, x2, y2):
        if x1 == x2 and y1 == y2:
            return None  # skip zero-length wires
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

    def no_connect(x, y):
        return f"""  (no_connect (at {x} {y})
    (uuid "{uid()}")
  )"""

    # ============================================================
    # SYMBOL INSTANCES
    # ============================================================
    symbols = []

    # U1 — SC16IS752
    symbols.append(make_component("U1", "JLCImport:SC16IS752IPW_112",
        U1_X, U1_Y, "SC16IS752",
        footprint="JLCImport:SC16IS752IPW_112", lcsc="C57156",
        ref_offset=(0, -22.86), val_offset=(0, 22.86)))

    # X1 — 14.7456MHz Crystal
    symbols.append(make_component("X1", "JLCImport:7U14745AE12UCG",
        X1_X, X1_Y, "14.7456MHz",
        footprint="JLCImport:7U14745AE12UCG", lcsc="C557185",
        ref_offset=(0, -8.89), val_offset=(0, 8.89)))

    # C1 — 15pF XTAL1 load cap (angle=270, vertical)
    symbols.append(make_component("C1", "JLCImport:CL21C150JBANNNC",
        C1_X, C1_Y, "15pF", angle=270,
        footprint="JLCImport:CL21C150JBANNNC", lcsc="C1794",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # C2 — 15pF XTAL2 load cap (angle=270, vertical)
    symbols.append(make_component("C2", "JLCImport:CL21C150JBANNNC",
        C2_X, C2_Y, "15pF", angle=270,
        footprint="JLCImport:CL21C150JBANNNC", lcsc="C1794",
        ref_offset=(3.81, 0), val_offset=(-3.81, 0)))

    # C3 — 100nF VDD decoupling (angle=270, vertical, below U1)
    symbols.append(make_component("C3", "JLCImport:CC0805KRX7R9BB104",
        C3_X, C3_Y, "100nF", angle=270,
        footprint="JLCImport:CC0805KRX7R9BB104", lcsc="C49678",
        ref_offset=(3.81, 0), val_offset=(-3.81, 0)))

    # R1 — 10k #RESET pull-up (horizontal, upper-left)
    symbols.append(make_component("R1", "JLCImport:0805W8F1002T5E",
        R1_X, R1_Y, "10k",
        footprint="JLCImport:0805W8F1002T5E", lcsc="C17414",
        ref_offset=(0, -2.54), val_offset=(0, 2.54)))

    # R2 — 1k IRQ# pull-up (horizontal, upper-left, above R1)
    symbols.append(make_component("R2", "JLCImport:0805W8F1001T5E",
        R2_X, R2_Y, "1k",
        footprint="JLCImport:0805W8F1001T5E", lcsc="C17513",
        ref_offset=(0, -2.54), val_offset=(0, 2.54)))

    # R3 — 1M Crystal feedback resistor (horizontal, below crystal)
    symbols.append(make_component("R3", "JLCImport:0805W8F1004T5E",
        R3_X, R3_Y, "1M",
        footprint="JLCImport:0805W8F1004T5E", lcsc="C17514",
        ref_offset=(0, -2.54), val_offset=(0, 2.54)))

    # Power — +3.3V (VDD above U1)
    symbols.append(make_power("#PWR01", "power:+3.3V", "+3.3V",
        VCC_VDD_X, VCC_VDD_Y))

    # Power — +3.3V (pull-up resistors, sideways pointing left)
    symbols.append(make_power("#PWR02", "power:+3.3V", "+3.3V",
        VCC_PULLUP_X, VCC_PULLUP_Y, angle=90,
        ref_pos=(VCC_PULLUP_X, round(VCC_PULLUP_Y - 2.54, 2)),
        val_pos=(VCC_PULLUP_X, round(VCC_PULLUP_Y + 2.54, 2))))

    # Power — GND (VSS, right side)
    symbols.append(make_power("#PWR03", "power:GND", "GND",
        GND_VSS_X, GND_VSS_Y))

    # Power — GND (crystal caps, single bottom center)
    symbols.append(make_power("#PWR04", "power:GND", "GND",
        GND_XTAL_X, GND_XTAL_Y))

    # Power — GND (C3 decoupling)
    symbols.append(make_power("#PWR05", "power:GND", "GND",
        GND_C3_X, GND_C3_Y))

    # Power — GND (A0 sideways)
    symbols.append(make_power("#PWR06", "power:GND", "GND",
        GND_A0_X, GND_A0_Y, angle=90))

    # Power — GND (A1 sideways)
    symbols.append(make_power("#PWR07", "power:GND", "GND",
        GND_A1_X, GND_A1_Y, angle=90))

    # Power — GND (X1 pin 4, left GND)
    symbols.append(make_power("#PWR08", "power:GND", "GND",
        GND_X1_P4_X, GND_X1_P4_Y))

    # Power — GND (X1 pin 2, right GND)
    symbols.append(make_power("#PWR09", "power:GND", "GND",
        GND_X1_P2_X, GND_X1_P2_Y))

    # Port symbols
    symbols.append(make_port("#PORT01", "Ports:TX", "TX",
        TX_PORT_X, TX_PORT_Y))
    symbols.append(make_port("#PORT02", "Ports:RX", "RX",
        RX_PORT_X, RX_PORT_Y))
    symbols.append(make_port("#PORT03", "Ports:SCL", "SCL",
        SCL_PORT_X, SCL_PORT_Y))
    symbols.append(make_port("#PORT04", "Ports:SDA", "SDA",
        SDA_PORT_X, SDA_PORT_Y))

    symbols_str = "\n\n".join(symbols)

    # ============================================================
    # NO-CONNECTS (15 pins)
    # ============================================================
    nc_pins = ['RTSA', 'CTSA', 'NC12', 'CTSB', 'RTSB',
               'GPIO0', 'GPIO1', 'GPIO2', 'GPIO3',
               'TXB', 'RXB', 'GPIO4', 'GPIO5', 'GPIO6', 'GPIO7']
    nc_parts = []
    for nc in nc_pins:
        px, py = U1_PINS[nc]
        nc_parts.append(no_connect(px, py))
    no_connects_str = "\n".join(nc_parts)

    # ============================================================
    # WIRES
    # ============================================================
    wires_list = []

    def add_wire(x1, y1, x2, y2):
        w = wire(x1, y1, x2, y2)
        if w:
            wires_list.append(w)

    # --- Signal ports to IC ---
    add_wire(TX_PIN[0], TX_PIN[1], U1_PINS['TXA'][0], U1_PINS['TXA'][1])
    add_wire(RX_PIN[0], RX_PIN[1], U1_PINS['RXA'][0], U1_PINS['RXA'][1])
    add_wire(SCL_PIN[0], SCL_PIN[1], U1_PINS['SCL'][0], U1_PINS['SCL'][1])
    add_wire(SDA_PIN[0], SDA_PIN[1], U1_PINS['SDA'][0], U1_PINS['SDA'][1])

    # --- Crystal wiring (reference design style) ---
    # XTAL1 net: U1.XTAL1 pin → left to drop column → down to crystal OSC1 area
    add_wire(U1_PINS['XTAL1'][0], U1_PINS['XTAL1'][1],
             XTAL1_DROP_X, U1_PINS['XTAL1'][1])               # horizontal left
    add_wire(XTAL1_DROP_X, U1_PINS['XTAL1'][1],
             XTAL1_DROP_X, X1_OSC1[1])                         # vertical down to OSC1 y

    # Crystal OSC1 pin → right to drop column
    add_wire(X1_OSC1[0], X1_OSC1[1],
             XTAL1_DROP_X, X1_OSC1[1])                         # (114.30→119.38, 106.68)

    # Continue XTAL1 net down from crystal OSC1 level to R3.P1
    add_wire(XTAL1_DROP_X, X1_OSC1[1],
             R3_P1[0], X1_OSC1[1])                             # horizontal to R3.P1 x
    add_wire(R3_P1[0], X1_OSC1[1],
             R3_P1[0], R3_P1[1])                               # vertical down to R3.P1

    # Continue XTAL1 net down from R3.P1 to C1.P1
    add_wire(R3_P1[0], R3_P1[1],
             C1_P1[0], R3_P1[1])                               # horizontal (same x, skip if equal)
    add_wire(C1_P1[0], R3_P1[1],
             C1_P1[0], C1_P1[1])                               # vertical down to C1.P1

    # XTAL2 net: U1.XTAL2 pin → left to drop column → down to crystal OSC2 area
    add_wire(U1_PINS['XTAL2'][0], U1_PINS['XTAL2'][1],
             XTAL2_DROP_X, U1_PINS['XTAL2'][1])               # horizontal left
    add_wire(XTAL2_DROP_X, U1_PINS['XTAL2'][1],
             XTAL2_DROP_X, X1_OSC2[1])                         # vertical down (99.06→101.60)

    # Crystal OSC2 pin → left to drop column
    add_wire(X1_OSC2[0], X1_OSC2[1],
             XTAL2_DROP_X, X1_OSC2[1])                         # (129.54→124.46, 101.60)

    # Continue XTAL2 net down from OSC2 level to R3.P2
    add_wire(XTAL2_DROP_X, X1_OSC2[1],
             XTAL2_DROP_X, X1_OSC1[1])                         # vertical (101.60→106.68)
    add_wire(XTAL2_DROP_X, X1_OSC1[1],
             R3_P2[0], X1_OSC1[1])                             # horizontal to R3.P2 x
    add_wire(R3_P2[0], X1_OSC1[1],
             R3_P2[0], R3_P2[1])                               # vertical down to R3.P2

    # Continue XTAL2 net down from R3.P2 to C2.P1
    add_wire(R3_P2[0], R3_P2[1],
             C2_P1[0], R3_P1[1])                               # horizontal (same x, skip if equal)
    add_wire(C2_P1[0], R3_P2[1],
             C2_P1[0], C2_P1[1])                               # vertical down to C2.P1

    # Crystal GND pins
    add_wire(X1_GND4[0], X1_GND4[1], GND_X1_P4_X, GND_X1_P4_Y)   # pin 4 → GND (up)
    add_wire(X1_GND2[0], X1_GND2[1], GND_X1_P2_X, GND_X1_P2_Y)   # pin 2 → GND (down)

    # C1 GND → horizontal to center → GND
    add_wire(C1_P2[0], C1_P2[1], GND_XTAL_X, C1_P2[1])        # horizontal to center x
    # C2 GND → horizontal to center → GND
    add_wire(C2_P2[0], C2_P2[1], GND_XTAL_X, C2_P2[1])        # horizontal to center x
    # Center vertical to GND symbol
    add_wire(GND_XTAL_X, C1_P2[1], GND_XTAL_X, GND_XTAL_Y)   # down to GND

    # --- Power wiring (VDD) ---
    # +3.3V above U1 → down to VDD pin
    add_wire(VCC_VDD_X, VCC_VDD_Y, VCC_VDD_X, U1_PINS['VDD'][1])
    # Horizontal from U1 center to VDD pin
    add_wire(VCC_VDD_X, U1_PINS['VDD'][1],
             U1_PINS['VDD'][0], U1_PINS['VDD'][1])

    # I2C mode: U1.I2C/SPI tied to VDD
    add_wire(U1_PINS['VDD'][0], U1_PINS['VDD'][1],
             U1_PINS['I2CSPI'][0], U1_PINS['I2CSPI'][1])

    # C3 decoupling: VDD net down to C3, then C3 to GND
    add_wire(VCC_VDD_X, U1_PINS['VDD'][1],
             VCC_VDD_X, C3_P1[1])                               # vertical to C3 top
    add_wire(C3_P2[0], C3_P2[1], GND_C3_X, GND_C3_Y)

    # VSS → GND
    add_wire(U1_PINS['VSS'][0], U1_PINS['VSS'][1],
             GND_VSS_X, GND_VSS_Y)

    # A0 → GND (sideways left)
    add_wire(U1_PINS['A0'][0], U1_PINS['A0'][1], GND_A0_X, GND_A0_Y)
    # A1 → GND (sideways left)
    add_wire(U1_PINS['A1'][0], U1_PINS['A1'][1], GND_A1_X, GND_A1_Y)

    # --- Pull-up resistors (reference style: upper-left) ---
    # +3.3V sideways → vertical wire connecting R2.P1 and R1.P1
    add_wire(VCC_PULLUP_X, VCC_PULLUP_Y, R2_P1[0], VCC_PULLUP_Y)
    # Vertical wire from R2.P1 down to R1.P1
    add_wire(R2_P1[0], R2_P1[1], R1_P1[0], R1_P1[1])
    # +3.3V tee to vertical wire
    add_wire(R2_P1[0], VCC_PULLUP_Y, R2_P1[0], R2_P1[1])

    # IRQ routing: U1.IRQ (170.18, 116.84) → right → up → left → R2.P2
    add_wire(U1_PINS['IRQ'][0], U1_PINS['IRQ'][1],
             IRQ_TURN_X, U1_PINS['IRQ'][1])                    # right to turn x
    add_wire(IRQ_TURN_X, U1_PINS['IRQ'][1],
             IRQ_TURN_X, IRQ_TURN_Y)                            # up to turn y
    add_wire(IRQ_TURN_X, IRQ_TURN_Y,
             IRQ_LEFT_X, IRQ_TURN_Y)                            # left across top
    add_wire(IRQ_LEFT_X, IRQ_TURN_Y,
             R2_P2[0], R2_P2[1])                                # down to R2.P2

    # RESET routing: U1.RESET (129.54, 93.98) → left to R1.P2 x → up to R1.P2
    add_wire(U1_PINS['RESET'][0], U1_PINS['RESET'][1],
             RESET_TURN_X, U1_PINS['RESET'][1])                # horizontal left
    add_wire(RESET_TURN_X, U1_PINS['RESET'][1],
             R1_P2[0], R1_P2[1])                                # vertical up to R1.P2

    wires_str = "\n\n".join(wires_list)

    # ============================================================
    # JUNCTIONS
    # ============================================================
    junctions_list = []

    # XTAL1 net: where OSC1 horizontal meets drop column (119.38, 106.68)
    junctions_list.append(junction(XTAL1_DROP_X, X1_OSC1[1]))
    # XTAL1 net: where R3.P1 vertical meets horizontal (116.84, 106.68) — only if different x
    # Actually R3.P1 x = 116.84, drop x = 119.38, so junction at (119.38, 106.68) for the T

    # XTAL2 net: where OSC2 horizontal meets drop column (124.46, 101.60)
    junctions_list.append(junction(XTAL2_DROP_X, X1_OSC2[1]))
    # XTAL2 net: where drop column meets horizontal at 106.68 level
    junctions_list.append(junction(XTAL2_DROP_X, X1_OSC1[1]))

    # R3.P1 junction (116.84, 110.49) — where vertical from XTAL1 meets R3
    junctions_list.append(junction(R3_P1[0], R3_P1[1]))
    # R3.P2 junction (127.00, 110.49) — where vertical from XTAL2 meets R3
    junctions_list.append(junction(R3_P2[0], R3_P2[1]))

    # Cap GND junction at center (121.92, 121.92) where C1 and C2 GND wires meet
    junctions_list.append(junction(GND_XTAL_X, C1_P2[1]))

    # VDD junction at pin (129.54, 101.60) — where horizontal meets vertical to I2C/SPI
    junctions_list.append(junction(U1_PINS['VDD'][0], U1_PINS['VDD'][1]))
    # VDD junction at U1_X (149.86, 101.60) — where vertical to C3 branches
    junctions_list.append(junction(VCC_VDD_X, U1_PINS['VDD'][1]))

    # Pull-up +3.3V junction at (107.95, 82.55) — where R2.P1 meets vertical
    junctions_list.append(junction(R2_P1[0], R2_P1[1]))

    junctions_str = "\n".join(junctions_list)

    # ============================================================
    # ASSEMBLE
    # ============================================================
    schematic = f"""(kicad_sch
  (version 20250114)
  (generator "build_uart_template.py")
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
        "uart_sc16is752.kicad_sch"
    )

    # Check status.json
    status_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "status.json"
    )
    if os.path.exists(status_path):
        import json
        with open(status_path, 'r') as f:
            status = json.load(f)
        if status.get("status") == "locked":
            print(f"ERROR: Template is LOCKED. Cannot regenerate.")
            print(f"  Unlock by changing status.json 'status' to 'revision'.")
            exit(1)

    content = build_schematic()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Written: {output_path}")
    print(f"Components: U1 (SC16IS752), X1 (14.7456MHz), C1/C2 (15pF), C3 (100nF)")
    print(f"            R1 (10k), R2 (1k), R3 (1M feedback)")
    print(f"Ports: TX, RX, SCL, SDA")
    print(f"Power: 2x +3.3V, 7x GND")
    print(f"No-connects: 15 pins (RTSA, CTSA, NC12, CTSB, RTSB, GPIO0-7, TXB, RXB)")
