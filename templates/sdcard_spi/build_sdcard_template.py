"""
Build sdcard_spi.kicad_sch — Micro SD card SPI interface template.

Components: U6 (Micro SD socket), C11 (100nF VCC decoupling)
Power: +3.3V, GND
Ports: SD_MISO, SD_MOSI, SD_CLK, CS_SD
No ESD diodes in this first pass (optional per spec).

NOTE: Footprint JLCImport:Micro_SD_Card_C585354 must be imported from JLCPCB
plugin separately. The symbol is created but footprint is a placeholder.

Run: python build_sdcard_template.py
"""

import uuid
import os
import re
import json

def uid():
    return str(uuid.uuid4())

ROOT_UUID = "d6b4c3e5-1a7f-4d8b-cf92-0e5f6a7b8c9d"

def snap(val, grid=1.27):
    return round(round(val / grid) * grid, 2)

# ============================================================
# LAYOUT
# ============================================================
U6_X, U6_Y = snap(165), snap(100)

# U6 pin endpoints (Micro_SD_Card_C585354, angle=0)
U6_PINS = {
    'DAT2':    (round(U6_X - 22.86, 2), round(U6_Y - 7.62, 2)),   # pin 1 NC
    'DAT3_CD': (round(U6_X - 22.86, 2), round(U6_Y - 5.08, 2)),   # pin 2 CS_SD
    'CMD':     (round(U6_X - 22.86, 2), round(U6_Y - 2.54, 2)),   # pin 3 SD_MOSI
    'VDD':     (round(U6_X - 22.86, 2), round(U6_Y, 2)),           # pin 4 +3.3V
    'CLK':     (round(U6_X - 22.86, 2), round(U6_Y + 2.54, 2)),   # pin 5 SD_CLK
    'VSS':     (round(U6_X - 22.86, 2), round(U6_Y + 5.08, 2)),   # pin 6 GND
    'DAT0':    (round(U6_X - 22.86, 2), round(U6_Y + 7.62, 2)),   # pin 7 SD_MISO
    'DAT1':    (round(U6_X - 22.86, 2), round(U6_Y + 10.16, 2)),  # pin 8 NC
    'SHIELD':  (round(U6_X + 20.32, 2), round(U6_Y + 15.24, 2)),  # pin 9 GND
}

# C11 (100nF, vertical angle=90) — VCC decoupling
C11_X = snap(135)
VDD_Y = U6_PINS['VDD'][1]
C11_Y = round(VDD_Y + 5.08, 2)
C11_P1 = (C11_X, round(C11_Y - 5.08, 2))  # top = VCC rail
C11_P2 = (C11_X, round(C11_Y + 5.08, 2))  # bottom = GND

# Power symbols
VCC33_X, VCC33_Y = snap(133), snap(92)      # +3.3V above VDD rail
GND1_X, GND1_Y = U6_PINS['VSS'][0], snap(U6_PINS['VSS'][1] + 3.81)  # below VSS pin
GND2_X, GND2_Y = C11_X, snap(C11_P2[1] + 3.81)  # below C11
GND3_X, GND3_Y = U6_PINS['SHIELD'][0], snap(U6_PINS['SHIELD'][1] + 3.81)  # below SHIELD

# Port symbols (left side)
PORT_X = snap(125)
PORT_PIN_X = round(PORT_X + 2.54, 2)

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
    for port_name in ['SD_MISO', 'SD_MOSI', 'SD_CLK', 'CS_SD']:
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
        ("Micro_SD_Card_C585354", False),    # SD socket — keep pin names
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

    # +3.3V
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

    # GND
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

    # U6 — Micro SD Card socket
    symbols.append(make_component("U6", "JLCImport:Micro_SD_Card_C585354",
        U6_X, U6_Y, "MicroSD",
        footprint="JLCImport:Micro_SD_Card_C585354",
        lcsc="C585354",
        ref_offset=(0, -13.97), val_offset=(0, 19.05)))

    # C11 — 100nF VCC decoupling (vertical angle=90)
    symbols.append(make_component("C11", "JLCImport:CC0805KRX7R9BB104",
        C11_X, C11_Y, "100nF", angle=90,
        footprint="JLCImport:CC0805KRX7R9BB104", lcsc="C49678",
        ref_offset=(-3.81, 0), val_offset=(3.81, 0)))

    # Power symbols
    symbols.append(make_power("#PWR01", "power:+3.3V", "+3.3V", VCC33_X, VCC33_Y))
    for i, (gx, gy) in enumerate([
        (GND1_X, GND1_Y), (GND2_X, GND2_Y), (GND3_X, GND3_Y)
    ], start=2):
        symbols.append(make_power(f"#PWR{i:02d}", "power:GND", "GND", gx, gy,
                                   ref_pos=(gx, round(gy + 6.35, 2)),
                                   val_pos=(gx, round(gy + 3.81, 2))))

    # Port symbols
    symbols.append(make_port("#PORT01", "Ports:CS_SD", "CS_SD", PORT_X, U6_PINS['DAT3_CD'][1]))
    symbols.append(make_port("#PORT02", "Ports:SD_MOSI", "SD_MOSI", PORT_X, U6_PINS['CMD'][1]))
    symbols.append(make_port("#PORT03", "Ports:SD_CLK", "SD_CLK", PORT_X, U6_PINS['CLK'][1]))
    symbols.append(make_port("#PORT04", "Ports:SD_MISO", "SD_MISO", PORT_X, U6_PINS['DAT0'][1]))

    symbols_str = "\n\n".join(symbols)

    # ============================================================
    # NO-CONNECTS
    # ============================================================
    def no_connect(x, y):
        return f"""  (no_connect (at {x} {y})
    (uuid "{uid()}")
  )"""

    nc_list = [
        no_connect(U6_PINS['DAT2'][0], U6_PINS['DAT2'][1]),
        no_connect(U6_PINS['DAT1'][0], U6_PINS['DAT1'][1]),
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

    # Port → pin wires (horizontal, same Y)
    # CS_SD port → DAT3/CD pin
    wires_raw.append(wire(PORT_PIN_X, U6_PINS['DAT3_CD'][1],
                          U6_PINS['DAT3_CD'][0], U6_PINS['DAT3_CD'][1]))
    # SD_MOSI port → CMD pin
    wires_raw.append(wire(PORT_PIN_X, U6_PINS['CMD'][1],
                          U6_PINS['CMD'][0], U6_PINS['CMD'][1]))
    # SD_CLK port → CLK pin
    wires_raw.append(wire(PORT_PIN_X, U6_PINS['CLK'][1],
                          U6_PINS['CLK'][0], U6_PINS['CLK'][1]))
    # SD_MISO port → DAT0 pin
    wires_raw.append(wire(PORT_PIN_X, U6_PINS['DAT0'][1],
                          U6_PINS['DAT0'][0], U6_PINS['DAT0'][1]))

    # VDD pin → C11 top → +3.3V (horizontal rail at VDD_Y)
    wires_raw.append(wire(U6_PINS['VDD'][0], VDD_Y, C11_P1[0], VDD_Y))
    wires_raw.append(wire(VCC33_X, VCC33_Y, VCC33_X, VDD_Y))
    wires_raw.append(wire(VCC33_X, VDD_Y, C11_P1[0], VDD_Y))

    # C11 bottom → GND2
    wires_raw.append(wire(C11_P2[0], C11_P2[1], GND2_X, GND2_Y))

    # VSS pin → GND1
    wires_raw.append(wire(U6_PINS['VSS'][0], U6_PINS['VSS'][1],
                          GND1_X, GND1_Y))

    # SHIELD pin → GND3
    wires_raw.append(wire(U6_PINS['SHIELD'][0], U6_PINS['SHIELD'][1],
                          GND3_X, GND3_Y))

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
    # VCC rail: at C11 top
    junctions_list.append(junction(C11_P1[0], VDD_Y))

    junctions_str = "\n\n".join(junctions_list)

    # ============================================================
    # ASSEMBLE
    # ============================================================
    schematic = f"""(kicad_sch
  (version 20250114)
  (generator "build_sdcard_template.py")
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

    output_path = os.path.join(script_dir, "sdcard_spi.kicad_sch")
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
    print(f"Components: U6, C11")
    print(f"Power symbols: +3.3V, 3x GND")
    print(f"Ports: CS_SD, SD_MOSI, SD_CLK, SD_MISO")
    print(f"No-connects: DAT2 (pin 1), DAT1 (pin 8)")
    print(f"NOTE: Footprint JLCImport:Micro_SD_Card_C585354 must be imported from JLCPCB")
