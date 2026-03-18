"""
Build supervisor_tlv803s.kicad_sch — TLV803S voltage supervisor template with
all components placed on 1.27mm grid, port symbols, power symbols, wires,
and junctions.

Run: python build_supervisor_template.py
"""

import uuid
import os
import re
import json

def uid():
    return str(uuid.uuid4())

# Fixed root UUID so instance paths don't change on regeneration
ROOT_UUID = "b7e3a1d2-5f49-4c8e-9a6b-1d2e3f4a5b6c"

def snap(val, grid=1.27):
    """Snap a value to the nearest 1.27mm grid point."""
    return round(round(val / grid) * grid, 2)

# ============================================================
# LAYOUT — all positions on 1.27mm grid (REVIEWED 2026-03-06)
# ============================================================
# U9 center
U9_X, U9_Y = 153.67, 100.33

# U9 pin endpoints (TLV803SDBZR, angle=0)
# Pin 1 GND:    local (-11.43, 1.27) → schematic (sx-11.43, sy-1.27)
# Pin 2 RESET#: local (-11.43, -1.27) → schematic (sx-11.43, sy+1.27)
# Pin 3 VDD:    local (11.43, 0) → schematic (sx+11.43, sy)
U9_PINS = {
    'GND':    (round(U9_X - 11.43, 2), round(U9_Y - 1.27, 2)),   # (142.24, 99.06)
    'RESET':  (round(U9_X - 11.43, 2), round(U9_Y + 1.27, 2)),   # (142.24, 101.60)
    'VDD':    (round(U9_X + 11.43, 2), U9_Y),                      # (165.10, 100.33)
}

# R16 (10k, vertical angle=270) — pull-up from +3.3V to Enable junction
R16_X, R16_Y = 128.27, 90.17
R16_P1 = (R16_X, round(R16_Y - 5.08, 2))  # top = (128.27, 85.09) → +3.3V
R16_P2 = (R16_X, round(R16_Y + 5.08, 2))  # bottom = (128.27, 95.25) → Enable junction

# C59 (100nF, vertical angle=270) — Enable output filter
C59_X, C59_Y = 140.97, 111.76
C59_P1 = (C59_X, round(C59_Y - 5.08, 2))  # top = (140.97, 106.68) → Enable junction
C59_P2 = (C59_X, round(C59_Y + 5.08, 2))  # bottom = (140.97, 116.84) → GND

# C58 (10uF GRM32, vertical angle=180) — bulk decoupling
# GRM32 has native vertical pins at (0, ±5.08). At angle=180: P1=top, P2=bottom.
C58_X, C58_Y = 172.72, 99.06
C58_P1 = (C58_X, round(C58_Y - 5.08, 2))  # top = (172.72, 93.98) → +3.3V rail
C58_P2 = (C58_X, round(C58_Y + 5.08, 2))  # bottom = (172.72, 104.14) → GND

# C4 (100nF, vertical angle=270) — bypass decoupling
C4_X, C4_Y = 187.96, 99.06
C4_P1 = (C4_X, round(C4_Y - 5.08, 2))  # top = (187.96, 93.98) → +3.3V rail
C4_P2 = (C4_X, round(C4_Y + 5.08, 2))  # bottom = (187.96, 104.14) → GND

# Power symbols
VCC1_X, VCC1_Y = 128.27, 78.74             # above R16 (moved with R16)
VCC2_X, VCC2_Y = 172.72, 88.90             # above VDD rail
GND1_X, GND1_Y = 135.89, 99.06             # U9.GND — sideways (angle=270)
GND1_ANGLE = 270                            # rotated to point left
GND2_X, GND2_Y = 140.97, 119.38            # below C59
GND3_X, GND3_Y = 172.72, 106.68            # below C58
GND4_X, GND4_Y = 187.96, 106.68            # below C4

# Enable port symbol
PORT_X, PORT_Y = 121.92, 101.60
PORT_PIN_X = round(PORT_X + 2.54, 2)       # (124.46)

# Junction coordinates
JUNC_ENABLE1_X, JUNC_ENABLE1_Y = 128.27, 101.60   # R16.P2 wire meets Enable horizontal
JUNC_ENABLE2_X, JUNC_ENABLE2_Y = 140.97, 101.60   # C59.P1 wire meets Enable horizontal
JUNC_RAIL_X, JUNC_RAIL_Y = 172.72, 93.98           # +3.3V rail at C58.P1

# +3.3V rail Y level
RAIL_Y = C58_P1[1]  # 93.98


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
    for port_name in ['Enable']:
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
    """Read the lib_symbols section from the project's libraries."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    jlc_path = os.path.join(project_root, "JLCImport.kicad_sym")

    # Tuple: (symbol_name, hide_pin_names)
    needed_symbols = [
        ("TLV803SDBZR", False),          # IC — keep pin names (GND, RESET#, VDD)
        ("0805W8F1002T5E", True),         # 10k resistor — hide "1"/"2"
        ("GRM32ER7YA106KA12L", True),     # 10uF cap — hide "1"/"2"
        ("CC0805KRX7R9BB104", True),      # 100nF cap — hide "1"/"2"
    ]

    with open(jlc_path, 'r', encoding='utf-8') as f:
        content = f.read()

    extracted = {}
    for sym_name, hide_names in needed_symbols:
        sym_text = extract_symbol(content, sym_name)
        if sym_text is None:
            raise ValueError(f"Symbol {sym_name} not found in {jlc_path}")

        # Add JLCImport: prefix to the top-level symbol name
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

        # Force (pin_names ... (hide yes)) on passives
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
    # Check lock status
    status_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "status.json")
    if os.path.exists(status_path):
        with open(status_path, 'r') as f:
            status = json.load(f)
        if status.get("status") == "locked":
            print(f"ERROR: Template is LOCKED. Cannot regenerate.")
            print(f"  Locked by: {status.get('locked_by')}")
            print(f"  Date: {status.get('locked_date')}")
            return None

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

    # Port symbols — read from Ports.kicad_sym
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
                       ref_offset=(2.54, -3.81), val_offset=(2.54, 3.81),
                       ref_angle=0, val_angle=0):
        rx, ry = round(x + ref_offset[0], 2), round(y + ref_offset[1], 2)
        vx, vy = round(x + val_offset[0], 2), round(y + val_offset[1], 2)
        props = f"""    (property "Reference" "{ref}"
      (at {rx} {ry} {ref_angle})
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "{value}"
      (at {vx} {vy} {val_angle})
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

    # U9 — TLV803SDBZR (ref above-left, value below)
    symbols.append(make_component("U9", "JLCImport:TLV803SDBZR",
        U9_X, U9_Y, "TLV803S",
        footprint="JLCImport:TLV803SDBZR",
        lcsc="C132016",
        ref_offset=(-0.254, -5.588), val_offset=(0, 6.096)))

    # R16 — 10k (pull-up, vertical, ref left, value right)
    symbols.append(make_component("R16", "JLCImport:0805W8F1002T5E",
        R16_X, R16_Y, "10k", angle=270,
        footprint="JLCImport:0805W8F1002T5E", lcsc="C17414",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # C59 — 100nF (Enable filter, vertical, ref left, value right)
    symbols.append(make_component("C59", "JLCImport:CC0805KRX7R9BB104",
        C59_X, C59_Y, "100nF", angle=270,
        footprint="JLCImport:CC0805KRX7R9BB104", lcsc="C49678",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # C58 — 10uF (bulk decoupling, GRM32 vertical, angle=180, ref/val rotated 90)
    symbols.append(make_component("C58", "JLCImport:GRM32ER7YA106KA12L",
        C58_X, C58_Y, "10uF", angle=180,
        footprint="JLCImport:GRM32ER7YA106KA12L", lcsc="C97973",
        ref_offset=(-4.064, 0.508), val_offset=(3.81, 0.508),
        ref_angle=90, val_angle=90))

    # C4 — 100nF (bypass decoupling, vertical, ref left, value right)
    symbols.append(make_component("C4", "JLCImport:CC0805KRX7R9BB104",
        C4_X, C4_Y, "100nF", angle=270,
        footprint="JLCImport:CC0805KRX7R9BB104", lcsc="C49678",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # Power symbols
    symbols.append(make_power("#PWR01", "power:+3.3V", "+3.3V", VCC1_X, VCC1_Y,
                               ref_pos=(VCC1_X, round(VCC1_Y + 3.81, 2)),
                               val_pos=(VCC1_X, round(VCC1_Y - 3.56, 2))))
    symbols.append(make_power("#PWR02", "power:+3.3V", "+3.3V", VCC2_X, VCC2_Y,
                               ref_pos=(VCC2_X, round(VCC2_Y + 3.81, 2)),
                               val_pos=(VCC2_X, round(VCC2_Y - 3.56, 2))))
    symbols.append(make_power("#PWR03", "power:GND", "GND", GND1_X, GND1_Y,
                               angle=GND1_ANGLE,
                               ref_pos=(round(GND1_X - 6.35, 2), GND1_Y),
                               val_pos=(round(GND1_X - 3.81, 2), GND1_Y)))
    symbols.append(make_power("#PWR04", "power:GND", "GND", GND2_X, GND2_Y,
                               ref_pos=(GND2_X, round(GND2_Y + 6.35, 2)),
                               val_pos=(GND2_X, round(GND2_Y + 3.81, 2))))
    symbols.append(make_power("#PWR05", "power:GND", "GND", GND3_X, GND3_Y,
                               ref_pos=(GND3_X, round(GND3_Y + 6.35, 2)),
                               val_pos=(GND3_X, round(GND3_Y + 3.81, 2))))
    symbols.append(make_power("#PWR06", "power:GND", "GND", GND4_X, GND4_Y,
                               ref_pos=(GND4_X, round(GND4_Y + 6.35, 2)),
                               val_pos=(GND4_X, round(GND4_Y + 3.81, 2))))

    # Enable port symbol
    symbols.append(make_port("#PORT01", "Ports:Enable", "Enable", PORT_X, PORT_Y,
                              val_pos=(round(PORT_X - 1.905, 2), PORT_Y)))

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
    # +3.3V(1) → R16.P1 (vertical down)
    wires.append(wire(VCC1_X, VCC1_Y, R16_P1[0], R16_P1[1]))
    # R16.P2 → Enable junction at 128.27 (vertical down)
    wires.append(wire(R16_P2[0], R16_P2[1], JUNC_ENABLE1_X, JUNC_ENABLE1_Y))
    # Enable port pin → junction at 128.27 (horizontal)
    wires.append(wire(PORT_PIN_X, PORT_Y, JUNC_ENABLE1_X, JUNC_ENABLE1_Y))
    # Enable junction 128.27 → junction 140.97 (horizontal)
    wires.append(wire(JUNC_ENABLE1_X, JUNC_ENABLE1_Y, JUNC_ENABLE2_X, JUNC_ENABLE2_Y))
    # Junction 140.97 → U9.RESET# (horizontal stub)
    wires.append(wire(JUNC_ENABLE2_X, JUNC_ENABLE2_Y, U9_PINS['RESET'][0], U9_PINS['RESET'][1]))
    # C59.P1 → Enable junction at 140.97 (vertical up)
    wires.append(wire(C59_P1[0], C59_P1[1], JUNC_ENABLE2_X, JUNC_ENABLE2_Y))
    # C59.P2 → GND2 (vertical down)
    wires.append(wire(GND2_X, GND2_Y, C59_P2[0], C59_P2[1]))
    # GND1 → U9.GND (horizontal, GND symbol at 270 feeds right)
    wires.append(wire(GND1_X, GND1_Y, U9_PINS['GND'][0], U9_PINS['GND'][1]))
    # +3.3V(2) → rail (vertical down)
    wires.append(wire(VCC2_X, VCC2_Y, VCC2_X, RAIL_Y))
    # VDD stub (vertical from rail down to VDD pin)
    wires.append(wire(U9_PINS['VDD'][0], RAIL_Y, U9_PINS['VDD'][0], U9_PINS['VDD'][1]))
    # Rail segment 1: VDD stub → C58 junction (horizontal)
    wires.append(wire(U9_PINS['VDD'][0], RAIL_Y, JUNC_RAIL_X, JUNC_RAIL_Y))
    # Rail segment 2: C58 junction → C4 (horizontal)
    wires.append(wire(JUNC_RAIL_X, JUNC_RAIL_Y, C4_P1[0], C4_P1[1]))
    # C58.P2 → GND3 (vertical down)
    wires.append(wire(C58_P2[0], C58_P2[1], GND3_X, GND3_Y))
    # C4.P2 → GND4 (vertical down)
    wires.append(wire(C4_P2[0], C4_P2[1], GND4_X, GND4_Y))

    wires_str = "\n\n".join(wires)

    # ============================================================
    # JUNCTIONS
    # ============================================================
    junctions = []
    # +3.3V rail junction at C58 — rail passes through, C58.P1 + +3.3V wire
    junctions.append(f"""  (junction (at {JUNC_RAIL_X} {JUNC_RAIL_Y})
    (diameter 0)
    (color 0 0 0 0)
    (uuid "{uid()}")
  )""")
    # Enable junction at 128.27 — R16.P2 wire meets Enable horizontal
    junctions.append(f"""  (junction (at {JUNC_ENABLE1_X} {JUNC_ENABLE1_Y})
    (diameter 0)
    (color 0 0 0 0)
    (uuid "{uid()}")
  )""")
    # Enable junction at 140.97 — C59.P1 wire meets Enable horizontal + U9.RESET# stub
    junctions.append(f"""  (junction (at {JUNC_ENABLE2_X} {JUNC_ENABLE2_Y})
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
  (generator "build_supervisor_template.py")
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
    content = build_schematic()
    if content is None:
        exit(1)

    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "supervisor_tlv803s.kicad_sch"
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    # Update status to review
    status_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "status.json")
    if os.path.exists(status_path):
        with open(status_path, 'r') as f:
            status = json.load(f)
        if status.get("status") == "draft":
            status["status"] = "review"
            status["description"] = "Build script ran successfully, awaiting human review"
            status["changelog"].append({
                "date": "2026-03-06",
                "from": "draft",
                "to": "review",
                "by": "ai"
            })
            with open(status_path, 'w') as f:
                json.dump(status, f, indent=2)

    print(f"Written: {output_path}")
    print(f"Components: U9, R16, C58, C4, C59")
    print(f"Port symbols: Enable")
    print(f"Power symbols: 2x +3.3V, 4x GND")
    print(f"All positions on 1.27mm grid")
    print(f"\nLayout:")
    print(f"  U9  at ({U9_X}, {U9_Y})")
    print(f"  R16 at ({R16_X}, {R16_Y}) angle=270")
    print(f"  C59 at ({C59_X}, {C59_Y}) angle=270")
    print(f"  C58 at ({C58_X}, {C58_Y}) angle=180")
    print(f"  C4  at ({C4_X}, {C4_Y}) angle=270")
