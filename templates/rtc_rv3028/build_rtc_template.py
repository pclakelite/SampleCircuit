"""
Build rtc_rv3028.kicad_sch — RV-3028-C7 RTC template with all components
placed on 1.27mm grid, port symbols, power symbols, wires, and junctions.

Run: python build_rtc_template.py
"""

import uuid
import os

def uid():
    return str(uuid.uuid4())

# Fixed root UUID so instance paths don't change on regeneration
ROOT_UUID = "57cbccc0-4dfd-4b96-9673-3939a22818a6"

def snap(val, grid=1.27):
    """Snap a value to the nearest 1.27mm grid point."""
    return round(round(val / grid) * grid, 2)

# ============================================================
# LAYOUT — all positions on 1.27mm grid
# ============================================================
# U8 center
U8_X, U8_Y = snap(150), snap(100)  # (149.86, 100.33)

# U8 pin endpoints (JLCImport RV-3028, angle=0)
# Pin local positions from lib_symbol, transformed to schematic coords
U8_PINS = {
    'CLKOUT': (round(U8_X - 15.24, 2), round(U8_Y - 3.81, 2)),  # pin 1, left
    'INT':    (round(U8_X - 15.24, 2), round(U8_Y - 1.27, 2)),  # pin 2, left
    'SCL':    (round(U8_X - 15.24, 2), round(U8_Y + 1.27, 2)),  # pin 3, left
    'SDA':    (round(U8_X - 15.24, 2), round(U8_Y + 3.81, 2)),  # pin 4, left
    'VSS':    (round(U8_X + 15.24, 2), round(U8_Y + 3.81, 2)),  # pin 5, right
    'VBACKUP':(round(U8_X + 15.24, 2), round(U8_Y + 1.27, 2)),  # pin 6, right
    'VDD':    (round(U8_X + 15.24, 2), round(U8_Y - 1.27, 2)),  # pin 7, right
    'EVI':    (round(U8_X + 15.24, 2), round(U8_Y - 3.81, 2)),  # pin 8, right
}

# R41 (10k, horizontal) — EVI pull-down, same Y as EVI pin
R41_X, R41_Y = snap(180), U8_PINS['EVI'][1]   # (180.34, 96.52)
R41_P1 = (round(R41_X - 5.08, 2), R41_Y)      # left pin
R41_P2 = (round(R41_X + 5.08, 2), R41_Y)      # right pin

# C10 (100nF, vertical angle=90) — VBACKUP decoupling
# angle=90: pin1 at (cx, cy-5.08)=TOP, pin2 at (cx, cy+5.08)=BOTTOM
C10_X = snap(175)                               # (175.26)
VBACKUP_Y = U8_PINS['VBACKUP'][1]              # 101.60
C10_Y = round(VBACKUP_Y + 5.08, 2)            # (106.68) — pin1 lands on VBACKUP wire
C10_P1 = (C10_X, round(C10_Y - 5.08, 2))      # top = (175.26, 101.60)
C10_P2 = (C10_X, round(C10_Y + 5.08, 2))      # bottom = (175.26, 111.76)

# R46 (1k, horizontal) — VBACKUP to battery
R46_X, R46_Y = snap(193), VBACKUP_Y            # (193.04, 101.60)
R46_P1 = (round(R46_X - 5.08, 2), R46_Y)      # left pin
R46_P2 = (round(R46_X + 5.08, 2), R46_Y)      # right pin

# B3 (CR1220, horizontal) — coin cell holder
B3_X, B3_Y = snap(211), VBACKUP_Y              # (210.82, 101.60)
B3_P1 = (round(B3_X - 5.08, 2), B3_Y)         # left pin (POS)
B3_P2 = (round(B3_X + 5.08, 2), B3_Y)         # right pin (NEG)

# Power symbols — positions from user's manual layout
VCC_X, VCC_Y = snap(169), snap(91)              # (168.91, 91.44) above VDD
GND2_X, GND2_Y = U8_PINS['VSS'][0], snap(109)  # (165.10, 109.22) below VSS
GND3_X, GND3_Y = R46_X, R41_Y                   # (193.04, 96.52) angle=90, beside R41
GND3_ANGLE = 90                                  # rotated sideways
GND4_X, GND4_Y = C10_X, snap(114)               # (175.26, 114.30) below C10
GND5_X, GND5_Y = B3_P2[0], snap(107)            # (215.90, 106.68) below B3

# Port symbols — positions from user's manual layout
PORT_SYM_X = snap(128)                           # (128.27)
PORT_PIN_X = round(PORT_SYM_X + 2.54, 2)        # (130.81)
SCL_PORT_Y = U8_PINS['SCL'][1] - 1.27           # 100.33 (moved up to align with wire routing)
SDA_PORT_Y = snap(105)                           # 105.41 (moved down for cleaner routing)

# ============================================================
# LIB_SYMBOLS (read from existing schematic — these are stable)
# ============================================================
# We read the lib_symbols from the JLCImport.kicad_sym and power libraries.
# For the build script, we embed them directly.

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
    for port_name in ['SCL', 'SDA']:
        sym_text = extract_symbol(content, port_name)
        if sym_text is None:
            raise ValueError(f"Symbol {port_name} not found in {ports_path}")
        # Add Ports: prefix to top-level symbol name only
        sym_text = sym_text.replace(
            f'(symbol "{port_name}"',
            f'(symbol "Ports:{port_name}"',
            1
        )
        extracted[port_name] = sym_text

    return extracted


def read_lib_symbols():
    """Read the lib_symbols section from the project's libraries."""
    # Path to JLCImport library
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    jlc_path = os.path.join(project_root, "JLCImport.kicad_sym")

    # Read JLCImport symbols we need
    # Tuple: (symbol_name, hide_pin_names)
    # hide_pin_names=True for passives/battery (no useful pin names)
    # hide_pin_names=False for ICs with named pins (SCL, SDA, VDD, etc.)
    needed_symbols = [
        ("CC0805KRX7R9BB104", True),    # capacitor — hide "1"/"2"
        ("0805W8F1001T5E", True),        # resistor — hide "1"/"2"
        ("0805W8F1002T5E", True),        # resistor — hide "1"/"2"
        ("RV-3028-C7_32_768KHZ_1PPM_TA_QC", False),  # RTC — keep SCL/SDA/VDD
        ("CR2032-BS-2-1", True),         # battery — hide "1"/"2"
    ]

    with open(jlc_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract each symbol block
    extracted = {}
    for sym_name, hide_names in needed_symbols:
        marker = f'(symbol "{sym_name}"'
        start = content.find(marker)
        if start == -1:
            raise ValueError(f"Symbol {sym_name} not found in {jlc_path}")

        # Find the matching closing paren
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

        sym_text = content[start:i+1]
        # Add JLCImport: prefix to the top-level symbol name
        sym_text = sym_text.replace(
            f'(symbol "{sym_name}"',
            f'(symbol "JLCImport:{sym_name}"',
            1  # only first occurrence
        )

        # Force (pin_numbers (hide yes)) on ALL symbols
        import re
        sym_text = re.sub(
            r'\(pin_numbers[^)]*\)',
            '(pin_numbers (hide yes))',
            sym_text,
            count=1
        )

        # Force (pin_names (offset 1.016) (hide yes)) on passives/battery
        # Keep pin_names visible on ICs with named pins
        # NOTE: original text is "(pin_names (offset 1.016))" — two closing parens
        # The regex must match the FULL expression including nested parens
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

    # Power symbols (hardcoded from KiCad power.kicad_sym)
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

    # Port symbols — read from Ports.kicad_sym (see TemplateCreation.spec §7D)
    # Always read from the actual library so edits in KiCad Symbol Editor are picked up.
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
        """Place a power symbol. ref_pos/val_pos are (x,y) tuples for label positions."""
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
        """Place a port symbol. val_pos overrides the default Value label position."""
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

    # U8 — RV-3028-C7 (ref above, value below)
    symbols.append(make_component("U8", "JLCImport:RV-3028-C7_32_768KHZ_1PPM_TA_QC",
        U8_X, U8_Y, "RV-3028-C7",
        footprint="JLCImport:RV-3028-C7_32_768KHZ_1PPM_TA_QC",
        lcsc="C3019759",
        ref_offset=(0, -10.16), val_offset=(0, 10.16)))

    # R41 — 10k (EVI pull-down, ref above, value below — manually adjusted in KiCad)
    symbols.append(make_component("R41", "JLCImport:0805W8F1002T5E",
        R41_X, R41_Y, "10k",
        footprint="JLCImport:0805W8F1002T5E", lcsc="C17414",
        ref_offset=(0, -2.032), val_offset=(0.254, 2.54)))

    # C10 — 100nF (VBACKUP decoupling, vertical angle=90, ref left, value right)
    symbols.append(make_component("C10", "JLCImport:CC0805KRX7R9BB104",
        C10_X, C10_Y, "100nF", angle=90,
        footprint="JLCImport:CC0805KRX7R9BB104", lcsc="C49678",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # R46 — 1k (VBACKUP to battery, ref above, value below — val x nudged in KiCad)
    symbols.append(make_component("R46", "JLCImport:0805W8F1001T5E",
        R46_X, R46_Y, "1k",
        footprint="JLCImport:0805W8F1001T5E", lcsc="C17513",
        ref_offset=(0, -2.54), val_offset=(-0.254, 2.794)))

    # B3 — CR1220 coin cell holder (ref above, value below)
    symbols.append(make_component("B3", "JLCImport:CR2032-BS-2-1",
        B3_X, B3_Y, "CR1220",
        footprint="JLCImport:CR2032-BS-2-1", lcsc="C70376",
        ref_offset=(0, -3.81), val_offset=(0, 3.81)))

    # Power symbols — property positions from user's manual layout in KiCad
    symbols.append(make_power("#PWR01", "power:+3.3V", "+3.3V", VCC_X, VCC_Y,
                               ref_pos=(168.91, 97.79), val_pos=(168.91, 87.88)))
    symbols.append(make_power("#PWR02", "power:GND", "GND", GND2_X, GND2_Y,
                               ref_pos=(165.1, 115.57), val_pos=(165.1, 113.03)))
    symbols.append(make_power("#PWR03", "power:GND", "GND", GND3_X, GND3_Y,
                               angle=GND3_ANGLE,
                               ref_pos=(199.39, 96.52), val_pos=(196.85, 96.266)))
    symbols.append(make_power("#PWR04", "power:GND", "GND", GND4_X, GND4_Y,
                               ref_pos=(175.26, 120.65), val_pos=(175.514, 118.618)))
    symbols.append(make_power("#PWR05", "power:GND", "GND", GND5_X, GND5_Y,
                               ref_pos=(215.9, 113.03), val_pos=(215.9, 110.744)))

    # Port symbols — SDA Value manually nudged in KiCad
    symbols.append(make_port("#PORT01", "Ports:SCL", "SCL", PORT_SYM_X, SCL_PORT_Y,
                              val_pos=(126.36, 100.33)))
    symbols.append(make_port("#PORT02", "Ports:SDA", "SDA", PORT_SYM_X, SDA_PORT_Y,
                              val_pos=(126.492, 105.664)))

    symbols_str = "\n\n".join(symbols)

    # ============================================================
    # NO-CONNECTS
    # ============================================================
    nc_clkout = U8_PINS['CLKOUT']
    nc_int = U8_PINS['INT']
    no_connects = f"""  (no_connect (at {nc_clkout[0]} {nc_clkout[1]})
    (uuid "{uid()}")
  )
  (no_connect (at {nc_int[0]} {nc_int[1]})
    (uuid "{uid()}")
  )"""

    # ============================================================
    # WIRES
    # ============================================================
    def wire(x1, y1, x2, y2):
        return f"""  (wire (pts (xy {x1} {y1}) (xy {x2} {y2}))
    (stroke (width 0) (type default))
    (uuid "{uid()}")
  )"""

    wires = []
    # SCL port pin → corner point (L-route via 133.35)
    WIRE_CORNER_X = 133.35
    wires.append(wire(PORT_PIN_X, SCL_PORT_Y, WIRE_CORNER_X, SCL_PORT_Y))
    wires.append(wire(WIRE_CORNER_X, SCL_PORT_Y, WIRE_CORNER_X, U8_PINS['SCL'][1]))
    wires.append(wire(WIRE_CORNER_X, U8_PINS['SCL'][1], U8_PINS['SCL'][0], U8_PINS['SCL'][1]))
    # SDA port pin → corner point (L-route via 133.35)
    wires.append(wire(PORT_PIN_X, SDA_PORT_Y, WIRE_CORNER_X, SDA_PORT_Y))
    wires.append(wire(WIRE_CORNER_X, SDA_PORT_Y, WIRE_CORNER_X, U8_PINS['SDA'][1]))
    wires.append(wire(WIRE_CORNER_X, U8_PINS['SDA'][1], U8_PINS['SDA'][0], U8_PINS['SDA'][1]))
    # +3.3V → corner → U8.VDD (L-route)
    wires.append(wire(VCC_X, VCC_Y, VCC_X, U8_PINS['VDD'][1]))
    wires.append(wire(VCC_X, U8_PINS['VDD'][1], U8_PINS['VDD'][0], U8_PINS['VDD'][1]))
    # U8.VSS → GND (vertical down)
    wires.append(wire(U8_PINS['VSS'][0], U8_PINS['VSS'][1], GND2_X, GND2_Y))
    # U8.EVI → R41.pin1
    wires.append(wire(U8_PINS['EVI'][0], U8_PINS['EVI'][1], R41_P1[0], R41_P1[1]))
    # R41.pin2 → GND3 (GND3 is at R41.pin2 position, rotated 90)
    wires.append(wire(R41_P2[0], R41_P2[1], GND3_X, GND3_Y))
    # U8.VBACKUP → junction → R46.pin1 (long horizontal wire, C10 tees off)
    wires.append(wire(U8_PINS['VBACKUP'][0], U8_PINS['VBACKUP'][1],
                       C10_P1[0], C10_P1[1]))
    wires.append(wire(C10_P1[0], C10_P1[1], R46_P1[0], R46_P1[1]))
    # C10.pin2 → GND4
    wires.append(wire(C10_P2[0], C10_P2[1], GND4_X, GND4_Y))
    # R46.pin2 → B3.pin1
    wires.append(wire(R46_P2[0], R46_P2[1], B3_P1[0], B3_P1[1]))
    # B3.pin2 → GND5 (vertical down)
    wires.append(wire(B3_P2[0], B3_P2[1], B3_P2[0], GND5_Y))

    wires_str = "\n\n".join(wires)

    # ============================================================
    # JUNCTIONS
    # ============================================================
    junctions = f"""  (junction (at {C10_P1[0]} {C10_P1[1]})
    (diameter 0)
    (color 0 0 0 0)
    (uuid "{uid()}")
  )"""

    # ============================================================
    # ASSEMBLE
    # ============================================================
    schematic = f"""(kicad_sch
  (version 20250114)
  (generator "build_rtc_template.py")
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
    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "rtc_rv3028.kicad_sch"
    )
    content = build_schematic()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Written: {output_path}")
    print(f"Components: U8, C10, B3, R46, R41")
    print(f"Port symbols: SCL, SDA")
    print(f"Power symbols: +3.3V, 4x GND")
    print(f"All positions on 1.27mm grid")
    print(f"\nLayout:")
    print(f"  U8  at ({U8_X}, {U8_Y})")
    print(f"  R41 at ({R41_X}, {R41_Y})")
    print(f"  C10 at ({C10_X}, {C10_Y}) angle=90")
    print(f"  R46 at ({R46_X}, {R46_Y})")
    print(f"  B3  at ({B3_X}, {B3_Y})")
