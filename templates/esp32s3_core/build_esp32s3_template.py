"""
Build esp32s3_core.kicad_sch — ESP32-S3-WROOM-1 MCU core template.
Decoupling caps, EN port, GPIO port symbols for all bus connections.

Run: python build_esp32s3_template.py
"""

import uuid
import os
import re

def uid():
    return str(uuid.uuid4())

ROOT_UUID = "b4d9f2a1-8c3e-5b0f-c6d4-e2f3a5b6c7d8"

def snap(val, grid=1.27):
    return round(round(val / grid) * grid, 2)

# ============================================================
# LAYOUT — all positions on 1.27mm grid
# ============================================================
# U2 center — large module, place with room for wires
U2_X, U2_Y = snap(150), snap(120)

# ESP32-S3-WROOM-1_N16R8 pin endpoints
# Pin local (at px py angle) → schematic coords:
#   angle=0 (left):   endpoint = (U2_X + px, U2_Y - py)
#   angle=180 (right): endpoint = (U2_X + px, U2_Y - py)
#   angle=90 (bottom): endpoint = (U2_X + px, U2_Y - py)
# All pins point outward from the body.

# Left side pins (angle=0, at -21.59)
# Schematic X = U2_X + (-21.59) = 128.27 (approx)
LEFT_X = round(U2_X - 21.59, 2)
def left_pin(py):
    return (LEFT_X, round(U2_Y - py, 2))

# Right side pins (angle=180, at 21.59)
RIGHT_X = round(U2_X + 21.59, 2)
def right_pin(py):
    return (RIGHT_X, round(U2_Y - py, 2))

# Bottom pins (angle=90, at y=-35.56)
BOT_Y = round(U2_Y + 35.56, 2)
def bot_pin(px):
    return (round(U2_X + px, 2), BOT_Y)

U2_PINS = {
    # Left side
    'GND_1':  left_pin(11.43),    # pin 1
    '3V3':    left_pin(8.89),     # pin 2
    'EN':     left_pin(6.35),     # pin 3
    'IO4':    left_pin(3.81),     # pin 4
    'IO5':    left_pin(1.27),     # pin 5
    'IO6':    left_pin(-1.27),    # pin 6
    'IO7':    left_pin(-3.81),    # pin 7
    'IO15':   left_pin(-6.35),    # pin 8
    'IO16':   left_pin(-8.89),    # pin 9
    'IO17':   left_pin(-11.43),   # pin 10
    'IO18':   left_pin(-13.97),   # pin 11
    'IO8':    left_pin(-16.51),   # pin 12
    'IO19':   left_pin(-19.05),   # pin 13
    'IO20':   left_pin(-21.59),   # pin 14
    # Bottom
    'IO3':    bot_pin(-12.7),     # pin 15
    'IO46':   bot_pin(-10.16),    # pin 16
    'IO9':    bot_pin(-7.62),     # pin 17
    'IO10':   bot_pin(-5.08),     # pin 18
    'IO11':   bot_pin(-2.54),     # pin 19
    'IO12':   bot_pin(0),         # pin 20
    'IO13':   bot_pin(2.54),      # pin 21
    'IO14':   bot_pin(5.08),      # pin 22
    'IO21':   bot_pin(7.62),      # pin 23
    'IO47':   bot_pin(10.16),     # pin 24
    'IO48':   bot_pin(12.7),      # pin 25
    'IO45':   bot_pin(15.24),     # pin 26
    # Right side
    'IO0':    right_pin(-21.59),  # pin 27
    'IO35':   right_pin(-19.05),  # pin 28
    'IO36':   right_pin(-16.51),  # pin 29
    'IO37':   right_pin(-13.97),  # pin 30
    'IO38':   right_pin(-11.43),  # pin 31
    'IO39':   right_pin(-8.89),   # pin 32
    'IO40':   right_pin(-6.35),   # pin 33
    'IO41':   right_pin(-3.81),   # pin 34
    'IO42':   right_pin(-1.27),   # pin 35
    'RXD0':   right_pin(1.27),    # pin 36
    'TXD0':   right_pin(3.81),    # pin 37
    'IO2':    right_pin(6.35),    # pin 38
    'IO1':    right_pin(8.89),    # pin 39
    'GND_40': right_pin(11.43),   # pin 40
    'GND_41': right_pin(15.24),   # pin 41
}

# --- GPIO to port mapping (from spec) ---
# These GPIO get port symbols wired to them
GPIO_PORT_MAP = {
    # Left side GPIO with ports
    'EN':   ('Enable', 'Ports:Enable'),
    'IO19': ('UD-',    'Ports:UD-'),
    'IO20': ('UD+',    'Ports:UD+'),
    # Right side GPIO with ports
    'TXD0': ('TX',     'Ports:TX'),
    'RXD0': ('RX',     'Ports:RX'),
}

# GPIO that are no-connect (unused in this template)
# All bottom pins and remaining right-side GPIO become NC
NC_PINS = [
    'IO0', 'IO1', 'IO2', 'IO3', 'IO4', 'IO5', 'IO6', 'IO7', 'IO8',
    'IO9', 'IO10', 'IO11', 'IO12', 'IO13', 'IO14', 'IO15', 'IO16',
    'IO17', 'IO18', 'IO21',
    'IO35', 'IO36', 'IO37', 'IO38', 'IO39', 'IO40', 'IO41', 'IO42',
    'IO45', 'IO46', 'IO47', 'IO48',
]

# Decoupling caps — vertical, above U2 near 3V3 pin
# C1 (10uF bulk) and C2 (100nF bypass)
VDD_WIRE_Y = U2_PINS['3V3'][1]
C1_X = snap(U2_PINS['3V3'][0] - 12.7)
C1_Y = snap(VDD_WIRE_Y - 7.62)
C1_P1 = (C1_X, round(C1_Y - 5.08, 2))  # top
C1_P2 = (C1_X, round(C1_Y + 5.08, 2))  # bottom

C2_X = snap(U2_PINS['3V3'][0] - 20.32)
C2_Y = C1_Y
C2_P1 = (C2_X, round(C2_Y - 5.08, 2))  # top
C2_P2 = (C2_X, round(C2_Y + 5.08, 2))  # bottom

# Power symbols
VCC_X, VCC_Y = snap((C1_X + C2_X) / 2), snap(C1_P1[1] - 3.81)

# GND symbols — one below each cap, one for each GND pin
GND_C1_X, GND_C1_Y = C1_X, snap(C1_P2[1] + 3.81)
GND_C2_X, GND_C2_Y = C2_X, snap(C2_P2[1] + 3.81)
GND_PIN1_X, GND_PIN1_Y = U2_PINS['GND_1'][0], snap(U2_PINS['GND_1'][1] - 5.08)
GND_PIN40_X, GND_PIN40_Y = snap(U2_PINS['GND_40'][0] + 5.08), U2_PINS['GND_40'][1]
GND_PIN41_X, GND_PIN41_Y = snap(U2_PINS['GND_41'][0] + 5.08), U2_PINS['GND_41'][1]

# Port positions — extend wires from pin endpoints
# Left-side ports: place to the left of the pin
LEFT_PORT_X = snap(LEFT_X - 10.16)
LEFT_PORT_PIN_X = round(LEFT_PORT_X + 2.54, 2)

# Right-side ports: place to the right of the pin (angle=180, pin extends left)


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

    port_names = ['Enable', 'TX', 'RX', 'UD+', 'UD-']
    extracted = {}
    for port_name in port_names:
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
        ("ESP32-S3-WROOM-1_N16R8", False),  # MCU — keep pin names
        ("CL21A106KAYNNNE", True),           # 10uF cap
        ("CC0805KRX7R9BB104", True),         # 100nF cap
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
        print(f"Warning: Could not read JLCImport.kicad_sym: {e}")
        jlc_symbols = {}

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

    # U2 — ESP32-S3-WROOM-1
    symbols.append(make_component("U2", "JLCImport:ESP32-S3-WROOM-1_N16R8",
        U2_X, U2_Y, "ESP32-S3-WROOM-1",
        footprint="JLCImport:ESP32-S3-WROOM-1_N16R8",
        lcsc="C2913202",
        ref_offset=(0, -40.64), val_offset=(0, 40.64)))

    # C1 — 10uF bulk (vertical, angle=90)
    symbols.append(make_component("C1", "JLCImport:CL21A106KAYNNNE",
        C1_X, C1_Y, "10uF", angle=90,
        footprint="JLCImport:CL21A106KAYNNNE", lcsc="C15850",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # C2 — 100nF bypass (vertical, angle=90)
    symbols.append(make_component("C2", "JLCImport:CC0805KRX7R9BB104",
        C2_X, C2_Y, "100nF", angle=90,
        footprint="JLCImport:CC0805KRX7R9BB104", lcsc="C49678",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # Power symbols
    symbols.append(make_power("#PWR01", "power:+3.3V", "+3.3V", VCC_X, VCC_Y))
    symbols.append(make_power("#PWR02", "power:GND", "GND", GND_C1_X, GND_C1_Y))
    symbols.append(make_power("#PWR03", "power:GND", "GND", GND_C2_X, GND_C2_Y))
    symbols.append(make_power("#PWR04", "power:GND", "GND", GND_PIN1_X, GND_PIN1_Y))
    # GND for pin 40 — rotated 90 to go right
    symbols.append(make_power("#PWR05", "power:GND", "GND", GND_PIN40_X, GND_PIN40_Y, angle=90))
    # GND for pin 41 — rotated 90 to go right
    symbols.append(make_power("#PWR06", "power:GND", "GND", GND_PIN41_X, GND_PIN41_Y, angle=90))

    # Port symbols
    port_num = 1
    # Left-side ports (EN, IO19=UD-, IO20=UD+)
    for gpio_name, (port_value, port_lib) in GPIO_PORT_MAP.items():
        pin_pos = U2_PINS[gpio_name]
        if pin_pos[0] == LEFT_X:
            # Left side — port goes further left
            px = LEFT_PORT_X
            py = pin_pos[1]
        else:
            # Right side — port faces left (angle=180) so pin extends toward IC
            # angle=180: pin at (2.54, 0) → schematic (sym_x - 2.54, sym_y)
            px = snap(RIGHT_X + 7.62)
            py = pin_pos[1]
        if pin_pos[0] == LEFT_X:
            symbols.append(make_port(f"#PORT{port_num:02d}", port_lib, port_value, px, py))
        else:
            symbols.append(make_port(f"#PORT{port_num:02d}", port_lib, port_value, px, py,
                angle=180, val_pos=(round(px + 1.905, 2), py)))
        port_num += 1

    symbols_str = "\n\n".join(symbols)

    # ============================================================
    # NO-CONNECTS
    # ============================================================
    def no_connect(x, y):
        return f"""  (no_connect (at {x} {y})
    (uuid "{uid()}")
  )"""

    nc_list = []
    for pin_name in NC_PINS:
        pos = U2_PINS[pin_name]
        nc_list.append(no_connect(pos[0], pos[1]))
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

    # --- Power wiring ---
    # +3.3V -> vertical down to VDD wire Y -> horizontal to 3V3 pin
    wires.append(wire(VCC_X, VCC_Y, VCC_X, VDD_WIRE_Y))
    # Horizontal from VCC_X to 3V3 pin
    wires.append(wire(VCC_X, VDD_WIRE_Y, U2_PINS['3V3'][0], VDD_WIRE_Y))

    # C1 top -> VCC_X, VDD_WIRE_Y (horizontal wire)
    wires.append(wire(C1_P1[0], C1_P1[1], C1_X, VDD_WIRE_Y))
    wires.append(wire(C1_X, VDD_WIRE_Y, VCC_X, VDD_WIRE_Y))
    junctions.append(junction(VCC_X, VDD_WIRE_Y))

    # C2 top -> C2_X, VDD_WIRE_Y
    wires.append(wire(C2_P1[0], C2_P1[1], C2_X, VDD_WIRE_Y))
    wires.append(wire(C2_X, VDD_WIRE_Y, C1_X, VDD_WIRE_Y))
    junctions.append(junction(C1_X, VDD_WIRE_Y))

    # C1 bottom -> GND_C1
    wires.append(wire(C1_P2[0], C1_P2[1], GND_C1_X, GND_C1_Y))
    # C2 bottom -> GND_C2
    wires.append(wire(C2_P2[0], C2_P2[1], GND_C2_X, GND_C2_Y))

    # GND pin 1 -> GND symbol (wire down from pin)
    wires.append(wire(U2_PINS['GND_1'][0], U2_PINS['GND_1'][1], GND_PIN1_X, GND_PIN1_Y))
    # GND pin 40 -> GND symbol (wire right)
    wires.append(wire(U2_PINS['GND_40'][0], U2_PINS['GND_40'][1], GND_PIN40_X, GND_PIN40_Y))
    # GND pin 41 -> GND symbol (wire right)
    wires.append(wire(U2_PINS['GND_41'][0], U2_PINS['GND_41'][1], GND_PIN41_X, GND_PIN41_Y))

    # --- Port wiring ---
    for gpio_name, (port_value, port_lib) in GPIO_PORT_MAP.items():
        pin_pos = U2_PINS[gpio_name]
        if pin_pos[0] == LEFT_X:
            # Left side — wire from pin to port pin endpoint
            port_pin = (LEFT_PORT_PIN_X, pin_pos[1])
            wires.append(wire(pin_pos[0], pin_pos[1], port_pin[0], port_pin[1]))
        else:
            # Right side — wire from pin to port (angle=180, pin at sym_x - 2.54)
            port_pin_x = round(snap(RIGHT_X + 7.62) - 2.54, 2)
            wires.append(wire(pin_pos[0], pin_pos[1], port_pin_x, pin_pos[1]))

    wires_str = "\n\n".join(wires)
    junctions_str = "\n\n".join(junctions) if junctions else ""

    # ============================================================
    # ASSEMBLE
    # ============================================================
    extra_sections = []
    if junctions_str:
        extra_sections.append(junctions_str)
    extra_sections.append(nc_str)
    extra_sections.append(wires_str)
    extra_sections.append(symbols_str)

    schematic = f"""(kicad_sch
  (version 20250114)
  (generator "build_esp32s3_template.py")
  (generator_version "9.0")
  (uuid "{ROOT_UUID}")
  (paper "A3")

  (lib_symbols
{lib_symbols_str}
  )

{chr(10).join(extra_sections)}

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
        "esp32s3_core.kicad_sch"
    )
    content = build_schematic()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Written: {output_path}")
    print(f"Components: U2, C1 (10uF), C2 (100nF)")
    print(f"Power symbols: +3.3V, 5x GND")
    print(f"Ports: Enable, TX, RX, UD+, UD-")
    print(f"No-connects: {len(NC_PINS)} unused GPIO")
