"""
Build rs485_sp3485.kicad_sch — SP3485EN RS-485 transceiver template with all
components placed on 1.27mm grid, port symbols, power symbols, wires, junctions.

Run: python build_rs485_template.py
"""

import uuid
import os
import re

def uid():
    return str(uuid.uuid4())

# Fixed root UUID so instance paths don't change on regeneration
ROOT_UUID = "a3e2f8b1-7c4d-4e9a-b5f6-1a2b3c4d5e6f"

def snap(val, grid=1.27):
    """Snap a value to the nearest 1.27mm grid point."""
    return round(round(val / grid) * grid, 2)

# ============================================================
# LAYOUT — all positions on 1.27mm grid
# ============================================================
# U1 center
U1_X, U1_Y = snap(150), snap(100)  # (149.86, 100.33)

# U1 pin endpoints (SP3485EN, angle=0)
# Pin local positions from lib_symbol:
#   RO:  (-8.89, 3.81)   RE#: (-8.89, 1.27)
#   DE:  (-8.89, -1.27)  DI:  (-8.89, -3.81)
#   GND: (8.89, -3.81)   A:   (8.89, -1.27)
#   B:   (8.89, 1.27)    VCC: (8.89, 3.81)
# Transform: endpoint = (sx + local_x, sy - local_y)
U1_PINS = {
    'RO':  (round(U1_X - 8.89, 2), round(U1_Y - 3.81, 2)),   # pin 1, left top
    'RE':  (round(U1_X - 8.89, 2), round(U1_Y - 1.27, 2)),   # pin 2, left
    'DE':  (round(U1_X - 8.89, 2), round(U1_Y + 1.27, 2)),   # pin 3, left
    'DI':  (round(U1_X - 8.89, 2), round(U1_Y + 3.81, 2)),   # pin 4, left bottom
    'GND': (round(U1_X + 8.89, 2), round(U1_Y + 3.81, 2)),   # pin 5, right bottom
    'A':   (round(U1_X + 8.89, 2), round(U1_Y + 1.27, 2)),   # pin 6, right
    'B':   (round(U1_X + 8.89, 2), round(U1_Y - 1.27, 2)),   # pin 7, right
    'VCC': (round(U1_X + 8.89, 2), round(U1_Y - 3.81, 2)),   # pin 8, right top
}

# C1 (100nF, vertical angle=270) — VCC decoupling
# angle=270: pin1 at (cx, cy-5.08)=TOP, pin2 at (cx, cy+5.08)=BOTTOM
C1_X = snap(168)                                # (167.64)
C1_Y = snap(102)                                # (101.6) — center
C1_P1 = (C1_X, round(C1_Y - 5.08, 2))         # top = (167.64, 96.52)
C1_P2 = (C1_X, round(C1_Y + 5.08, 2))         # bottom = (167.64, 106.68)

# R2 (120R termination, vertical angle=270) — between A and B buses
R2_X = snap(185)                                # (185.42)
R2_Y = U1_Y                                    # (100.33) — centered between A and B
R2_P1 = (R2_X, round(R2_Y - 5.08, 2))         # top = (185.42, 95.25)
R2_P2 = (R2_X, round(R2_Y + 5.08, 2))         # bottom = (185.42, 105.41)

# Power symbols
VCC_X, VCC_Y = C1_X, snap(91)                  # (167.64, 91.44) above C1
GND2_X, GND2_Y = C1_X, snap(109)               # (167.64, 109.22) below C1
GND3_X, GND3_Y = U1_PINS['GND'][0], snap(109)  # (158.75, 109.22) below IC GND

# Port symbols — left side
PORT_SYM_X = snap(128)                          # (128.27)
PORT_PIN_X = round(PORT_SYM_X + 2.54, 2)       # (130.81)
RX_PORT_Y = U1_PINS['RO'][1]                   # 96.52 (matches RO pin Y)
DE_PORT_Y = U1_Y                               # 100.33 (between RE# and DE)
TX_PORT_Y = U1_PINS['DI'][1]                   # 104.14 (matches DI pin Y)

# Port symbols — right side (angle=180, pin at x-2.54)
PORT_R_SYM_X = snap(178)                        # (177.8)
PORT_R_PIN_X = round(PORT_R_SYM_X - 2.54, 2)   # (175.26)
RS485_B_PORT_Y = U1_PINS['B'][1]               # 99.06
RS485_A_PORT_Y = U1_PINS['A'][1]               # 101.6

# DE/RE# fork point
FORK_X = snap(140)                              # (139.7)


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
    for port_name in ['TX', 'RX', 'RS485_DE', 'RS485_A', 'RS485_B']:
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
    """Read the lib_symbols from JLCImport.kicad_sym."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    jlc_path = os.path.join(project_root, "JLCImport.kicad_sym")

    # (symbol_name, hide_pin_names)
    needed_symbols = [
        ("SP3485EN-L_TR", False),        # IC — keep pin names visible
        ("CC0805KRX7R9BB104", True),     # capacitor — hide "1"/"2"
        ("0805W8F1200T5E", True),        # resistor — hide "1"/"2"
    ]

    with open(jlc_path, 'r', encoding='utf-8') as f:
        content = f.read()

    extracted = {}
    for sym_name, hide_names in needed_symbols:
        sym_text = extract_symbol(content, sym_name)
        if sym_text is None:
            raise ValueError(f"Symbol {sym_name} not found in {jlc_path}")

        # Add JLCImport: prefix to top-level symbol name
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

        # Force hide pin_names on passives
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
    jlc_symbols = read_lib_symbols()

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

    # Port symbols — read from Ports.kicad_sym
    port_symbols = read_port_symbols()
    for sym_text in port_symbols.values():
        lib_parts.append(f"    {sym_text}")

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

    # U1 — SP3485EN (ref above body, value below body)
    symbols.append(make_component("U1", "JLCImport:SP3485EN-L_TR",
        U1_X, U1_Y, "SP3485EN",
        footprint="JLCImport:SP3485EN-L_TR",
        lcsc="C8963",
        ref_offset=(0, -10.16), val_offset=(0, 10.16)))

    # C1 — 100nF VCC decoupling (vertical angle=270, ref left, value right)
    symbols.append(make_component("C1", "JLCImport:CC0805KRX7R9BB104",
        C1_X, C1_Y, "100nF", angle=270,
        footprint="JLCImport:CC0805KRX7R9BB104", lcsc="C49678",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # R2 — 120R termination (vertical angle=270, ref left, value right)
    symbols.append(make_component("R2", "JLCImport:0805W8F1200T5E",
        R2_X, R2_Y, "120R", angle=270,
        footprint="JLCImport:0805W8F1200T5E", lcsc="C17437",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # Power symbols
    symbols.append(make_power("#PWR01", "power:+3.3V", "+3.3V", VCC_X, VCC_Y,
                               ref_pos=(VCC_X, round(VCC_Y + 3.81, 2)),
                               val_pos=(VCC_X, round(VCC_Y - 3.56, 2))))
    symbols.append(make_power("#PWR02", "power:GND", "GND", GND2_X, GND2_Y,
                               ref_pos=(GND2_X, round(GND2_Y + 6.35, 2)),
                               val_pos=(GND2_X, round(GND2_Y + 3.81, 2))))
    symbols.append(make_power("#PWR03", "power:GND", "GND", GND3_X, GND3_Y,
                               ref_pos=(GND3_X, round(GND3_Y + 6.35, 2)),
                               val_pos=(GND3_X, round(GND3_Y + 3.81, 2))))

    # Port symbols — left side (angle=0, pin at x+2.54)
    symbols.append(make_port("#PORT01", "Ports:RX", "RX",
                              PORT_SYM_X, RX_PORT_Y))
    symbols.append(make_port("#PORT02", "Ports:RS485_DE", "RS485_DE",
                              PORT_SYM_X, DE_PORT_Y))
    symbols.append(make_port("#PORT03", "Ports:TX", "TX",
                              PORT_SYM_X, TX_PORT_Y))

    # Port symbols — right side (angle=180, pin at x-2.54)
    # At angle=180, the Value text position needs adjustment
    symbols.append(make_port("#PORT04", "Ports:RS485_B", "RS485_B",
                              PORT_R_SYM_X, RS485_B_PORT_Y, angle=180,
                              val_pos=(round(PORT_R_SYM_X + 1.905, 2), RS485_B_PORT_Y)))
    symbols.append(make_port("#PORT05", "Ports:RS485_A", "RS485_A",
                              PORT_R_SYM_X, RS485_A_PORT_Y, angle=180,
                              val_pos=(round(PORT_R_SYM_X + 1.905, 2), RS485_A_PORT_Y)))

    symbols_str = "\n\n".join(symbols)

    # ============================================================
    # WIRES
    # ============================================================
    def wire(x1, y1, x2, y2):
        # Skip zero-length wires
        if x1 == x2 and y1 == y2:
            return None
        return f"""  (wire (pts (xy {x1} {y1}) (xy {x2} {y2}))
    (stroke (width 0) (type default))
    (uuid "{uid()}")
  )"""

    wires = []

    # RX port → U1.RO (straight horizontal)
    wires.append(wire(PORT_PIN_X, RX_PORT_Y, U1_PINS['RO'][0], U1_PINS['RO'][1]))

    # TX port → U1.DI (straight horizontal)
    wires.append(wire(PORT_PIN_X, TX_PORT_Y, U1_PINS['DI'][0], U1_PINS['DI'][1]))

    # RS485_DE port → fork → RE# and DE
    wires.append(wire(PORT_PIN_X, DE_PORT_Y, FORK_X, DE_PORT_Y))           # horizontal to fork
    wires.append(wire(FORK_X, DE_PORT_Y, FORK_X, U1_PINS['RE'][1]))       # vertical up to RE# Y
    wires.append(wire(FORK_X, U1_PINS['RE'][1], U1_PINS['RE'][0], U1_PINS['RE'][1]))  # horizontal to RE#
    wires.append(wire(FORK_X, DE_PORT_Y, FORK_X, U1_PINS['DE'][1]))       # vertical down to DE Y
    wires.append(wire(FORK_X, U1_PINS['DE'][1], U1_PINS['DE'][0], U1_PINS['DE'][1]))  # horizontal to DE

    # +3.3V → C1 top (vertical)
    wires.append(wire(VCC_X, VCC_Y, C1_P1[0], C1_P1[1]))
    # U1.VCC → C1 top (horizontal)
    wires.append(wire(U1_PINS['VCC'][0], U1_PINS['VCC'][1], C1_P1[0], C1_P1[1]))
    # C1 bottom → GND (vertical)
    wires.append(wire(C1_P2[0], C1_P2[1], GND2_X, GND2_Y))
    # U1.GND → GND (vertical)
    wires.append(wire(U1_PINS['GND'][0], U1_PINS['GND'][1], GND3_X, GND3_Y))

    # B bus: U1.B → port RS485_B pin
    wires.append(wire(U1_PINS['B'][0], U1_PINS['B'][1],
                       PORT_R_PIN_X, RS485_B_PORT_Y))
    # A bus: U1.A → port RS485_A pin
    wires.append(wire(U1_PINS['A'][0], U1_PINS['A'][1],
                       PORT_R_PIN_X, RS485_A_PORT_Y))

    # Termination R2 wiring: B junction → R2 pin1 (L-route)
    wires.append(wire(PORT_R_PIN_X, RS485_B_PORT_Y, R2_X, RS485_B_PORT_Y))  # horizontal
    wires.append(wire(R2_X, RS485_B_PORT_Y, R2_P1[0], R2_P1[1]))            # vertical up
    # Termination R2 wiring: A junction → R2 pin2 (L-route)
    wires.append(wire(PORT_R_PIN_X, RS485_A_PORT_Y, R2_X, RS485_A_PORT_Y))  # horizontal
    wires.append(wire(R2_X, RS485_A_PORT_Y, R2_P2[0], R2_P2[1]))            # vertical down

    # Filter out None (zero-length wires)
    wires = [w for w in wires if w is not None]
    wires_str = "\n\n".join(wires)

    # ============================================================
    # JUNCTIONS
    # ============================================================
    junction_points = [
        (FORK_X, DE_PORT_Y),              # DE/RE# fork
        (C1_P1[0], C1_P1[1]),             # VCC rail meets cap top
        (PORT_R_PIN_X, RS485_B_PORT_Y),   # B bus fork to port and R2
        (PORT_R_PIN_X, RS485_A_PORT_Y),   # A bus fork to port and R2
    ]

    junctions = []
    for jx, jy in junction_points:
        junctions.append(f"""  (junction (at {jx} {jy})
    (diameter 0)
    (color 0 0 0 0)
    (uuid "{uid()}")
  )""")
    junctions_str = "\n\n".join(junctions)

    # ============================================================
    # ASSEMBLE
    # ============================================================
    schematic = f"""(kicad_sch
  (version 20250114)
  (generator "build_rs485_template.py")
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
        "rs485_sp3485.kicad_sch"
    )
    content = build_schematic()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Written: {output_path}")
    print(f"Components: U1 (SP3485EN), C1 (100nF), R2 (120R)")
    print(f"Port symbols: RX, TX, RS485_DE, RS485_A, RS485_B")
    print(f"Power symbols: +3.3V, 2x GND")
    print(f"All positions on 1.27mm grid")
    print(f"\nLayout:")
    print(f"  U1  at ({U1_X}, {U1_Y})")
    print(f"  C1  at ({C1_X}, {C1_Y}) angle=270")
    print(f"  R2  at ({R2_X}, {R2_Y}) angle=270")
