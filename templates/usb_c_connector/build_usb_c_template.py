"""
Build usb_c_connector.kicad_sch — USB-C connector template with data lines.

Components: J1 (USB-C 16-pin), R30/R31 (4.7k pull-downs), C39 (100nF VBUS decoupling)
Power: +5V (from VBUS), GND
Ports: UD+, UD-

Run: python build_usb_c_template.py
"""

import uuid
import os
import re
import json

def uid():
    return str(uuid.uuid4())

ROOT_UUID = "c5a3b2d4-0f6e-4c7a-be81-9d4e5f6a7b8c"

def snap(val, grid=1.27):
    return round(round(val / grid) * grid, 2)

# ============================================================
# LAYOUT — all positions on 1.27mm grid
# ============================================================
# J1 center (USB-C connector, angle=0)
J1_X, J1_Y = snap(150), snap(105)

# J1 pin endpoints (TYPE-C_16PIN_2MD_073, angle=0)
# Pin local (at px py angle): schematic endpoint = (sym_x + px, sym_y - py)
J1_PINS = {
    'GND_1':  (round(J1_X - 11.43, 2), round(J1_Y - 13.97, 2)),  # pin 1
    'VBUS_1': (round(J1_X - 11.43, 2), round(J1_Y - 11.43, 2)),  # pin 2
    'SBU2':   (round(J1_X - 11.43, 2), round(J1_Y - 8.89, 2)),   # pin 3 NC
    'CC1':    (round(J1_X - 11.43, 2), round(J1_Y - 6.35, 2)),   # pin 4 NC
    'DN2':    (round(J1_X - 11.43, 2), round(J1_Y - 3.81, 2)),   # pin 5
    'DP1':    (round(J1_X - 11.43, 2), round(J1_Y - 1.27, 2)),   # pin 6
    'DN1':    (round(J1_X - 11.43, 2), round(J1_Y + 1.27, 2)),   # pin 7
    'DP2':    (round(J1_X - 11.43, 2), round(J1_Y + 3.81, 2)),   # pin 8
    'SBU1':   (round(J1_X - 11.43, 2), round(J1_Y + 6.35, 2)),   # pin 9 NC
    'CC2':    (round(J1_X - 11.43, 2), round(J1_Y + 8.89, 2)),   # pin 10 NC
    'VBUS_2': (round(J1_X - 11.43, 2), round(J1_Y + 11.43, 2)),  # pin 11
    'GND_2':  (round(J1_X - 11.43, 2), round(J1_Y + 13.97, 2)),  # pin 12
    'SHELL1': (round(J1_X + 10.16, 2), round(J1_Y + 13.97, 2)),  # pin 13
    'SHELL2': (round(J1_X + 10.16, 2), round(J1_Y - 13.97, 2)),  # pin 14
}

# VBUS rail X (left of connector, vertical bus)
VBUS_X = snap(125)
# D+ net: DP1 and DP2 merge, then go to R30 and UD+ port
# D- net: DN1 and DN2 merge, then go to R31 and UD- port
DP_MERGE_X = snap(128)
DM_MERGE_X = snap(131)

# DP1 Y and DP2 Y
DP1_Y = J1_PINS['DP1'][1]  # pin 6
DP2_Y = J1_PINS['DP2'][1]  # pin 8
DP_MID_Y = snap((DP1_Y + DP2_Y) / 2)  # midpoint for merged D+ wire

DN1_Y = J1_PINS['DN1'][1]  # pin 7
DN2_Y = J1_PINS['DN2'][1]  # pin 5
DM_MID_Y = snap((DN1_Y + DN2_Y) / 2)  # midpoint for merged D- wire

# R30 (4.7k, vertical angle=90) — UD+ pull-down
R30_X = snap(115)
R30_Y = snap(DP_MID_Y)
R30_P1 = (R30_X, round(R30_Y - 3.81, 2))  # top
R30_P2 = (R30_X, round(R30_Y + 3.81, 2))  # bottom = GND

# R31 (4.7k, vertical angle=90) — UD- pull-down
R31_X = snap(110)
R31_Y = snap(DM_MID_Y)
R31_P1 = (R31_X, round(R31_Y - 3.81, 2))  # top
R31_P2 = (R31_X, round(R31_Y + 3.81, 2))  # bottom = GND

# C39 (100nF, vertical angle=90) — VBUS decoupling
C39_X = VBUS_X
C39_Y = snap(J1_PINS['VBUS_1'][1] + 5.08)
C39_P1 = (C39_X, round(C39_Y - 5.08, 2))  # top = VBUS
C39_P2 = (C39_X, round(C39_Y + 5.08, 2))  # bottom = GND

# Power symbols
VCC5_X, VCC5_Y = VBUS_X, snap(85)          # +5V above VBUS rail
GND1_X, GND1_Y = J1_PINS['GND_1'][0], snap(J1_PINS['GND_1'][1] - 3.81)  # above GND_1
GND2_X, GND2_Y = J1_PINS['GND_2'][0], snap(J1_PINS['GND_2'][1] + 3.81)  # below GND_2
GND3_X, GND3_Y = J1_PINS['SHELL1'][0], snap(J1_PINS['SHELL1'][1] + 3.81) # below SHELL1
GND4_X, GND4_Y = J1_PINS['SHELL2'][0], snap(J1_PINS['SHELL2'][1] - 3.81) # above SHELL2
GND5_X, GND5_Y = C39_X, snap(C39_P2[1] + 3.81)  # below C39
GND6_X, GND6_Y = R30_X, snap(R30_P2[1] + 3.81)   # below R30
GND7_X, GND7_Y = R31_X, snap(R31_P2[1] + 3.81)   # below R31

# Port symbols (left side)
PORT_DP_X = snap(100)
PORT_DM_X = snap(100)
PORT_DP_Y = R30_P1[1]
PORT_DM_Y = R31_P1[1]

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
    for port_name in ['UD+', 'UD-']:
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
        ("TYPE-C_16PIN_2MD_073", False),     # USB-C connector — keep pin names
        ("0805W8F4701T5E", True),            # 4.7k resistor — hide pin names
        ("CC0805KRX7R9BB104", True),         # 100nF cap — hide pin names
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
    jlc_symbols = read_lib_symbols()

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

    # J1 — USB-C connector
    symbols.append(make_component("J1", "JLCImport:TYPE-C_16PIN_2MD_073",
        J1_X, J1_Y, "USB-C",
        footprint="JLCImport:TYPE-C_16PIN_2MD_073",
        lcsc="C2765186",
        ref_offset=(0, -17.78), val_offset=(0, 17.78)))

    # R30 — 4.7k UD+ pull-down (vertical angle=90)
    symbols.append(make_component("R30", "JLCImport:0805W8F4701T5E",
        R30_X, R30_Y, "4.7k", angle=90,
        footprint="JLCImport:0805W8F4701T5E", lcsc="C17673",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # R31 — 4.7k UD- pull-down (vertical angle=90)
    symbols.append(make_component("R31", "JLCImport:0805W8F4701T5E",
        R31_X, R31_Y, "4.7k", angle=90,
        footprint="JLCImport:0805W8F4701T5E", lcsc="C17673",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # C39 — 100nF VBUS decoupling (vertical angle=90)
    symbols.append(make_component("C39", "JLCImport:CC0805KRX7R9BB104",
        C39_X, C39_Y, "100nF", angle=90,
        footprint="JLCImport:CC0805KRX7R9BB104", lcsc="C49678",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # Power symbols
    symbols.append(make_power("#PWR01", "power:+5V", "+5V", VCC5_X, VCC5_Y))

    gnd_positions = [
        (GND1_X, GND1_Y), (GND2_X, GND2_Y), (GND3_X, GND3_Y),
        (GND4_X, GND4_Y), (GND5_X, GND5_Y), (GND6_X, GND6_Y),
        (GND7_X, GND7_Y)
    ]
    for i, (gx, gy) in enumerate(gnd_positions, start=2):
        symbols.append(make_power(f"#PWR{i:02d}", "power:GND", "GND", gx, gy,
                                   ref_pos=(gx, round(gy + 6.35, 2)),
                                   val_pos=(gx, round(gy + 3.81, 2))))

    # Port symbols (left side)
    PORT_PIN_OFFSET = 2.54
    symbols.append(make_port("#PORT01", "Ports:UD+", "UD+", PORT_DP_X, PORT_DP_Y))
    symbols.append(make_port("#PORT02", "Ports:UD-", "UD-", PORT_DM_X, PORT_DM_Y))

    symbols_str = "\n\n".join(symbols)

    # ============================================================
    # NO-CONNECTS
    # ============================================================
    def no_connect(x, y):
        return f"""  (no_connect (at {x} {y})
    (uuid "{uid()}")
  )"""

    nc_list = [
        no_connect(J1_PINS['SBU2'][0], J1_PINS['SBU2'][1]),
        no_connect(J1_PINS['CC1'][0], J1_PINS['CC1'][1]),
        no_connect(J1_PINS['SBU1'][0], J1_PINS['SBU1'][1]),
        no_connect(J1_PINS['CC2'][0], J1_PINS['CC2'][1]),
    ]
    no_connects_str = "\n\n".join(nc_list)

    # ============================================================
    # WIRES
    # ============================================================
    def wire(x1, y1, x2, y2):
        if x1 == x2 and y1 == y2:
            return None
        return f"""  (wire (pts (xy {x1} {y1}) (xy {x2} {y2}))
    (stroke (width 0) (type default))
    (uuid "{uid()}")
  )"""

    wires_raw = []

    # --- VBUS ---
    VBUS_1_Y = J1_PINS['VBUS_1'][1]
    VBUS_2_Y = J1_PINS['VBUS_2'][1]
    # VBUS pin 2 → left to VBUS_X
    wires_raw.append(wire(J1_PINS['VBUS_1'][0], VBUS_1_Y, VBUS_X, VBUS_1_Y))
    # VBUS pin 11 → left to VBUS_X
    wires_raw.append(wire(J1_PINS['VBUS_2'][0], VBUS_2_Y, VBUS_X, VBUS_2_Y))
    # Vertical VBUS bus
    wires_raw.append(wire(VBUS_X, VBUS_1_Y, VBUS_X, VBUS_2_Y))
    # +5V symbol → VBUS bus top
    wires_raw.append(wire(VCC5_X, VCC5_Y, VBUS_X, VBUS_1_Y))
    # C39 connects on VBUS bus
    # (C39_P1 is at VBUS_X, should be on the VBUS vertical wire)

    # --- GND ---
    # GND pin 1 → GND1
    wires_raw.append(wire(J1_PINS['GND_1'][0], J1_PINS['GND_1'][1], GND1_X, GND1_Y))
    # GND pin 12 → GND2
    wires_raw.append(wire(J1_PINS['GND_2'][0], J1_PINS['GND_2'][1], GND2_X, GND2_Y))
    # SHELL pin 13 → GND3
    wires_raw.append(wire(J1_PINS['SHELL1'][0], J1_PINS['SHELL1'][1], GND3_X, GND3_Y))
    # SHELL pin 14 → GND4
    wires_raw.append(wire(J1_PINS['SHELL2'][0], J1_PINS['SHELL2'][1], GND4_X, GND4_Y))
    # C39 bottom → GND5
    wires_raw.append(wire(C39_P2[0], C39_P2[1], GND5_X, GND5_Y))

    # --- D+ (DP1 pin 6 and DP2 pin 8 merge) ---
    # DP1 → left to merge X
    wires_raw.append(wire(J1_PINS['DP1'][0], J1_PINS['DP1'][1], DP_MERGE_X, DP1_Y))
    # DP2 → left to merge X
    wires_raw.append(wire(J1_PINS['DP2'][0], J1_PINS['DP2'][1], DP_MERGE_X, DP2_Y))
    # Vertical merge
    wires_raw.append(wire(DP_MERGE_X, DP1_Y, DP_MERGE_X, DP2_Y))
    # Merged D+ → R30 top
    wires_raw.append(wire(DP_MERGE_X, R30_P1[1], R30_P1[0], R30_P1[1]))
    # R30 bottom → GND6
    wires_raw.append(wire(R30_P2[0], R30_P2[1], GND6_X, GND6_Y))
    # UD+ port → R30 top
    wires_raw.append(wire(round(PORT_DP_X + 2.54, 2), PORT_DP_Y, R30_P1[0], R30_P1[1]))

    # --- D- (DN1 pin 7 and DN2 pin 5 merge) ---
    # DN2 → left to merge X
    wires_raw.append(wire(J1_PINS['DN2'][0], J1_PINS['DN2'][1], DM_MERGE_X, DN2_Y))
    # DN1 → left to merge X
    wires_raw.append(wire(J1_PINS['DN1'][0], J1_PINS['DN1'][1], DM_MERGE_X, DN1_Y))
    # Vertical merge
    wires_raw.append(wire(DM_MERGE_X, DN2_Y, DM_MERGE_X, DN1_Y))
    # Merged D- → R31 top
    wires_raw.append(wire(DM_MERGE_X, R31_P1[1], R31_P1[0], R31_P1[1]))
    # R31 bottom → GND7
    wires_raw.append(wire(R31_P2[0], R31_P2[1], GND7_X, GND7_Y))
    # UD- port → R31 top
    wires_raw.append(wire(round(PORT_DM_X + 2.54, 2), PORT_DM_Y, R31_P1[0], R31_P1[1]))

    wires = [w for w in wires_raw if w is not None]
    wires_str = "\n\n".join(wires)

    # ============================================================
    # JUNCTIONS
    # ============================================================
    def junction(x, y):
        return f"""  (junction (at {x} {y})
    (diameter 0)
    (color 0 0 0 0)
    (uuid "{uid()}")
  )"""

    junctions_list = []
    # VBUS bus junctions at pin connection points
    junctions_list.append(junction(VBUS_X, VBUS_1_Y))
    junctions_list.append(junction(VBUS_X, C39_P1[1]))
    # D+ merge junction
    junctions_list.append(junction(DP_MERGE_X, R30_P1[1]))
    # D- merge junction
    junctions_list.append(junction(DM_MERGE_X, R31_P1[1]))
    # R30 top (port + resistor)
    junctions_list.append(junction(R30_P1[0], R30_P1[1]))
    # R31 top (port + resistor)
    junctions_list.append(junction(R31_P1[0], R31_P1[1]))

    junctions_str = "\n\n".join(junctions_list)

    # ============================================================
    # ASSEMBLE
    # ============================================================
    schematic = f"""(kicad_sch
  (version 20250114)
  (generator "build_usb_c_template.py")
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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    status_path = os.path.join(script_dir, "status.json")
    if os.path.exists(status_path):
        with open(status_path, 'r') as f:
            status = json.load(f)
        if status.get("status") == "locked":
            print("ERROR: Template is LOCKED. Cannot regenerate.")
            exit(1)

    output_path = os.path.join(script_dir, "usb_c_connector.kicad_sch")
    content = build_schematic()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    if os.path.exists(status_path):
        with open(status_path, 'r') as f:
            status = json.load(f)
        old_status = status.get("status", "draft")
        status["status"] = "review"
        if "changelog" not in status:
            status["changelog"] = []
        status["changelog"].append({
            "date": "2026-03-07",
            "from": old_status,
            "to": "review",
            "by": "ai"
        })
        with open(status_path, 'w') as f:
            json.dump(status, f, indent=2)

    print(f"Written: {output_path}")
    print(f"Components: J1, R30, R31, C39")
    print(f"Power symbols: +5V, 7x GND")
    print(f"Ports: UD+, UD-")
    print(f"No-connects: SBU1, SBU2, CC1, CC2")
