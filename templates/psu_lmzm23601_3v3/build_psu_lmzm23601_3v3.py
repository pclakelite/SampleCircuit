"""
Build psu_lmzm23601_3v3.kicad_sch - LMZM23601SILR 12V-to-3.3V buck regulator
template with input protection diode and all components placed/wired.

Run: python build_psu_lmzm23601_3v3.py
"""

import json
import os
import re
import uuid


def uid():
    return str(uuid.uuid4())


# Fixed root UUID so instance paths stay stable between generations
ROOT_UUID = "7a6fd472-71e4-4f31-b6fe-f7300bc4d95f"


def snap(val, grid=1.27):
    """Snap value to nearest 1.27mm (50 mil) grid."""
    return round(round(val / grid) * grid, 2)


def check_status():
    """Prevent regeneration when template is locked."""
    status_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "status.json")
    if os.path.exists(status_path):
        with open(status_path, "r", encoding="utf-8") as f:
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
# LAYOUT (all points on 1.27mm grid)
# ============================================================
U5_X, U5_Y = snap(150), snap(100)  # (149.86, 100.33)

# LMZM23601 pin endpoints using endpoint = (sx + px, sy - py)
U5_PINS = {
    "GND": (round(U5_X - 13.97, 2), round(U5_Y - 3.81, 2)),       # (135.89, 96.52)
    "MODE_SYNC": (round(U5_X - 13.97, 2), round(U5_Y - 1.27, 2)), # (135.89, 99.06)
    "VIN": (round(U5_X - 13.97, 2), round(U5_Y + 1.27, 2)),       # (135.89, 101.60)
    "EN": (round(U5_X - 13.97, 2), round(U5_Y + 3.81, 2)),        # (135.89, 104.14)
    "PGOOD": (round(U5_X - 13.97, 2), round(U5_Y + 6.35, 2)),     # (135.89, 106.68)
    "VOUT": (round(U5_X + 13.97, 2), round(U5_Y + 6.35, 2)),      # (163.83, 106.68)
    "FB": (round(U5_X + 13.97, 2), round(U5_Y + 3.81, 2)),        # (163.83, 104.14)
    "DNC8": (round(U5_X + 13.97, 2), round(U5_Y + 1.27, 2)),      # (163.83, 101.60)
    "DNC9": (round(U5_X + 13.97, 2), round(U5_Y - 1.27, 2)),      # (163.83, 99.06)
    "DNC10": (round(U5_X + 13.97, 2), round(U5_Y - 3.81, 2)),     # (163.83, 96.52)
    "EP": (round(U5_X + 13.97, 2), round(U5_Y - 6.35, 2)),        # (163.83, 93.98)
}

# D8 PMEG6030EVPX at angle=180 so anode is left (+12V) and cathode is right (VIN rail)
D8_X, D8_Y = 99.06, 101.60
D8_K = (104.14, 101.60)  # pin 1
D8_A = (93.98, 101.60)   # pin 2

# C11 EEEFT1V681UP at angle=270 => pin1 top, pin2 bottom
C11_X, C11_Y = 114.30, 106.68
C11_P1 = (114.30, 101.60)  # pin 1 (+)
C11_P2 = (114.30, 111.76)  # pin 2 (-)

# C34 GRM32ER7YA106KA12L vertical default
C34_X, C34_Y = 125.73, 106.68
C34_P2 = (125.73, 101.60)  # pin 2 top
C34_P1 = (125.73, 111.76)  # pin 1 bottom

# Feedback divider and output cap
R31_X, R31_Y = 170.18, 118.11          # 10k, angle=270
R31_P1 = (170.18, 113.03)              # top (to VOUT)
R31_P2 = (170.18, 123.19)              # bottom (FB node)

R32_X, R32_Y = 185.42, 124.46          # 4.22k, angle=270
R32_P1 = (185.42, 119.38)              # top (FB node)
R32_P2 = (185.42, 129.54)              # bottom (GND)

C35_X, C35_Y = 198.12, 124.46          # 47uF, angle=270
C35_P1 = (198.12, 119.38)              # top (VOUT)
C35_P2 = (198.12, 129.54)              # bottom (GND)

# Power symbols
V12_X, V12_Y = 91.44, 93.98
V33_X, V33_Y = 193.04, 100.33

GND_IC_X, GND_IC_Y = 133.35, 88.90
GND_IC_ANGLE = 180
GND_EP_X, GND_EP_Y = 167.64, 93.98
GND_EP_ANGLE = 90
GND_IN1_X, GND_IN1_Y = 114.30, 116.84
GND_IN2_X, GND_IN2_Y = 125.73, 116.84
GND_OUT_X, GND_OUT_Y = 190.50, 132.08

# Routing helper points from reviewed schematic
VIN_RAIL_Y = 101.60
IC_GND_CORNER = (133.35, 96.52)
VOUT_JUNCTION = (170.18, 106.68)
FB_JUNCTION = (176.53, 104.14)
FB_VERTICAL_TOP = (176.53, 123.19)
OUT_GND_RAIL_Y = 129.54


def extract_symbol(content, sym_name):
    """Extract one complete (symbol ...) block from a .kicad_sym file."""
    marker = f'(symbol "{sym_name}"'
    start = content.find(marker)
    if start == -1:
        return None
    depth = 0
    i = start
    while i < len(content):
        if content[i] == "(":
            depth += 1
        elif content[i] == ")":
            depth -= 1
            if depth == 0:
                break
        i += 1
    return content[start : i + 1]


def read_lib_symbols():
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    jlc_path = os.path.join(project_root, "JLCImport.kicad_sym")

    # (symbol_name, hide_pin_names)
    needed_symbols = [
        ("LMZM23601SILR", False),       # keep IC pin names visible
        ("PMEG6030EVPX", True),
        ("EEEFT1V681UP", True),
        ("GRM32ER7YA106KA12L", True),
        ("0805W8F1002T5E", True),
        ("0805W8F4221T5E", True),
        ("GRM32EC81C476KE15L", True),
    ]

    with open(jlc_path, "r", encoding="utf-8") as f:
        content = f.read()

    extracted = {}
    for sym_name, hide_names in needed_symbols:
        sym_text = extract_symbol(content, sym_name)
        if sym_text is None:
            raise ValueError(f"Symbol {sym_name} not found in {jlc_path}")

        sym_text = sym_text.replace(
            f'(symbol "{sym_name}"',
            f'(symbol "JLCImport:{sym_name}"',
            1,
        )

        # Always hide pin numbers at symbol level
        if "(pin_numbers" in sym_text:
            sym_text = re.sub(r"\(pin_numbers[^)]*\)", "(pin_numbers (hide yes))", sym_text, count=1)
        else:
            sym_text = sym_text.replace(
                f'(symbol "JLCImport:{sym_name}"',
                f'(symbol "JLCImport:{sym_name}"\n    (pin_numbers (hide yes))',
                1,
            )

        # Hide pin names for passives/diode/caps
        if hide_names:
            if re.search(r"\(pin_names\s*\([^)]*\)\)", sym_text):
                sym_text = re.sub(
                    r"\(pin_names\s*\([^)]*\)\)",
                    "(pin_names (offset 1.016) (hide yes))",
                    sym_text,
                    count=1,
                )
            elif "(pin_names" in sym_text:
                sym_text = re.sub(
                    r"\(pin_names[^)]*\)",
                    "(pin_names (offset 1.016) (hide yes))",
                    sym_text,
                    count=1,
                )

        # Electrolytic symbol in JLCImport uses pin type "input", which triggers
        # unnecessary ERC drive errors for this passive template context.
        if sym_name == "EEEFT1V681UP":
            sym_text = sym_text.replace("(pin input line", "(pin unspecified line")

        extracted[sym_name] = sym_text

    return extracted


def build_schematic():
    try:
        jlc_symbols = read_lib_symbols()
    except Exception as e:
        print(f"Warning: Could not read JLCImport.kicad_sym: {e}")
        print("Using placeholder lib_symbols - schematic will show red boxes.")
        jlc_symbols = {}

    lib_parts = [f"    {sym_text}" for sym_text in jlc_symbols.values()]

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

    def make_power(ref, lib_id, value, x, y, angle=0, ref_pos=None, val_pos=None):
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
    symbols.append(make_component("U5", "JLCImport:LMZM23601SILR", U5_X, U5_Y, "LMZM23601SILR",
                                  footprint="JLCImport:LMZM23601SILR", lcsc="C2685821",
                                  ref_offset=(0, -12.7), val_offset=(0, 12.7)))
    symbols.append(make_component("D8", "JLCImport:PMEG6030EVPX", D8_X, D8_Y, "PMEG6030EVPX",
                                  footprint="JLCImport:PMEG6030EVPX", lcsc="C489223", angle=180,
                                  ref_offset=(0, -3.81), val_offset=(0, 3.81)))
    symbols.append(make_component("C11", "JLCImport:EEEFT1V681UP", C11_X, C11_Y, "680uF 35V",
                                  footprint="JLCImport:EEEFT1V681UP", lcsc="C542257", angle=270,
                                  ref_offset=(-3.81, 0), val_offset=(3.81, 0)))
    symbols.append(make_component("C34", "JLCImport:GRM32ER7YA106KA12L", C34_X, C34_Y, "10uF 35V",
                                  footprint="JLCImport:GRM32ER7YA106KA12L", lcsc="C97973",
                                  ref_offset=(-3.81, 0), val_offset=(3.81, 0)))
    symbols.append(make_component("R31", "JLCImport:0805W8F1002T5E", R31_X, R31_Y, "10k",
                                  footprint="JLCImport:0805W8F1002T5E", lcsc="C17414", angle=270,
                                  ref_offset=(3.81, 0), val_offset=(-3.81, 0)))
    symbols.append(make_component("R32", "JLCImport:0805W8F4221T5E", R32_X, R32_Y, "4.22k",
                                  footprint="JLCImport:0805W8F4221T5E", lcsc="C17665", angle=270,
                                  ref_offset=(3.81, 0), val_offset=(-3.81, 0)))
    symbols.append(make_component("C35", "JLCImport:GRM32EC81C476KE15L", C35_X, C35_Y, "47uF 16V",
                                  footprint="JLCImport:GRM32EC81C476KE15L", lcsc="C162512", angle=270,
                                  ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    symbols.append(make_power("#PWR01", "power:+12V", "+12V", V12_X, V12_Y,
                              ref_pos=(V12_X, round(V12_Y + 3.81, 2)),
                              val_pos=(V12_X, round(V12_Y - 4.32, 2))))
    symbols.append(make_power("#PWR08", "power:+3.3V", "+3.3V", V33_X, V33_Y,
                              ref_pos=(V33_X, round(V33_Y + 3.81, 2)),
                              val_pos=(V33_X, round(V33_Y - 3.56, 2))))
    symbols.append(make_power("#PWR02", "power:GND", "GND", GND_IC_X, GND_IC_Y,
                              angle=GND_IC_ANGLE,
                              ref_pos=(GND_IC_X, round(GND_IC_Y + 6.35, 2)),
                              val_pos=(GND_IC_X, 112.78)))
    symbols.append(make_power("#PWR03", "power:GND", "GND", GND_EP_X, GND_EP_Y,
                              angle=GND_EP_ANGLE,
                              ref_pos=(174.24, GND_EP_Y),
                              val_pos=(171.70, GND_EP_Y)))
    symbols.append(make_power("#PWR04", "power:GND", "GND", GND_IN1_X, GND_IN1_Y,
                              ref_pos=(GND_IN1_X, round(GND_IN1_Y + 6.35, 2)),
                              val_pos=(GND_IN1_X, round(GND_IN1_Y + 3.81, 2))))
    symbols.append(make_power("#PWR05", "power:GND", "GND", GND_IN2_X, GND_IN2_Y,
                              ref_pos=(GND_IN2_X, round(GND_IN2_Y + 6.35, 2)),
                              val_pos=(GND_IN2_X, round(GND_IN2_Y + 3.81, 2))))
    symbols.append(make_power("#PWR06", "power:GND", "GND", GND_OUT_X, GND_OUT_Y,
                              ref_pos=(GND_OUT_X, round(GND_OUT_Y + 6.35, 2)),
                              val_pos=(GND_OUT_X, round(GND_OUT_Y + 3.81, 2))))

    symbols_str = "\n\n".join(symbols)

    # No-connects: PGOOD and 3x DNC
    nc_pins = [U5_PINS["PGOOD"], U5_PINS["DNC8"], U5_PINS["DNC9"], U5_PINS["DNC10"]]
    no_connects = "\n".join(
        f"""  (no_connect (at {px} {py})
    (uuid "{uid()}")
  )"""
        for (px, py) in nc_pins
    )

    def wire(x1, y1, x2, y2):
        return f"""  (wire (pts (xy {x1} {y1}) (xy {x2} {y2}))
    (stroke (width 0) (type default))
    (uuid "{uid()}")
  )"""

    wires = []

    # Exact wire set from reviewed KiCad schematic
    wire_points = [
        (125.73, 111.76, 125.73, 116.84),
        (125.73, 101.60, 135.89, 101.60),
        (91.44, 101.60, 93.98, 101.60),
        (104.14, 101.60, 114.30, 101.60),
        (135.89, 96.52, 133.35, 96.52),
        (198.12, 119.38, 198.12, 106.68),
        (170.18, 106.68, 170.18, 113.03),
        (185.42, 129.54, 190.50, 129.54),
        (114.30, 101.60, 125.73, 101.60),
        (135.89, 99.06, 133.35, 99.06),
        (190.50, 129.54, 190.50, 132.08),
        (176.53, 104.14, 185.42, 104.14),
        (91.44, 93.98, 91.44, 101.60),
        (176.53, 123.19, 176.53, 104.14),
        (163.83, 104.14, 176.53, 104.14),
        (163.83, 106.68, 170.18, 106.68),
        (133.35, 88.90, 133.35, 96.52),
        (114.30, 111.76, 114.30, 116.84),
        (198.12, 106.68, 193.04, 106.68),
        (193.04, 100.33, 193.04, 106.68),
        (198.12, 129.54, 190.50, 129.54),
        (135.89, 104.14, 135.89, 101.60),
        (170.18, 106.68, 193.04, 106.68),
        (170.18, 123.19, 176.53, 123.19),
        (163.83, 93.98, 167.64, 93.98),
        (185.42, 119.38, 185.42, 104.14),
        (133.35, 96.52, 133.35, 99.06),
    ]
    for x1, y1, x2, y2 in wire_points:
        wires.append(wire(x1, y1, x2, y2))

    wires_str = "\n\n".join(wires)

    junction_points = [
        (135.89, 101.60),
        (190.50, 129.54),
        (125.73, 101.60),
        (133.35, 96.52),
        (170.18, 106.68),
        (193.04, 106.68),
        (114.30, 101.60),
        (176.53, 104.14),
    ]
    junctions = "\n".join(
        f"""  (junction (at {jx} {jy})
    (diameter 0)
    (color 0 0 0 0)
    (uuid "{uid()}")
  )"""
        for (jx, jy) in junction_points
    )

    schematic = f"""(kicad_sch
  (version 20250114)
  (generator "build_psu_lmzm23601_3v3.py")
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
        raise SystemExit(1)

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "psu_lmzm23601_3v3.kicad_sch")
    content = build_schematic()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Written: {output_path}")
    print("Components: U5, D8, C11, C34, R31, R32, C35")
    print("Power symbols: +12V, +3.3V, 5x GND")
    print("No-connects: PGOOD, DNC x3")
    print("All positions on 1.27mm grid")
