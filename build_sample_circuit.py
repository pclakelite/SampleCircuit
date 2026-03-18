"""
build_sample_circuit.py — Combine templates into one flat SampleCircuit schematic.

Layout on A3 sheet:
  Row 1 (power):    PSU 24V->12V | PSU 12V->5V | PSU 12V->3.3V
  Row 2 (core):     ESP32-S3     | Audio NS4168
  Row 3 (peripherals): Flash CSNP1G | SD Card | Terminal Blocks

Power chain: 24V → 12V → 5V (audio) and 12V → 3.3V (ESP32, SD, flash)

Run: python build_sample_circuit.py
"""

import importlib.util
import os
import re
import uuid

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = ROOT

COMBINED_UUID = "f1a2b3c4-d5e6-7f89-0a1b-c2d3e4f5a6b7"

# Template root UUIDs (from each build script)
TEMPLATE_ROOT_UUIDS = {
    "psu_12v":  "c5d6e7f8-a1b2-4c3d-9e0f-1a2b3c4d5e6f",
    "psu_5v":   "a3e7c1d4-8f2b-4a6e-9c5d-1b3e7f9a2c4d",
    "psu_3v3":  "7a6fd472-71e4-4f31-b6fe-f7300bc4d95f",
    "esp32":    "b4d9f2a1-8c3e-5b0f-c6d4-e2f3a5b6c7d8",
    "audio":    "b4f8a2d1-6e3c-4b97-ae5d-2g3h4i5j6k7l",
    "flash":    "b4f8c2d3-6e5a-4b90-af7d-2g3e4f5a6b7c",
    "sdcard":   "d6b4c3e5-1a7f-4d8b-cf92-0e5f6a7b8c9d",
}

# Layout: each template gets an X/Y offset so they don't overlap on A3
TEMPLATES = [
    {"key": "psu_12v", "script": "templates/psu_lmzm23601_12v/build_psu_lmzm23601_12v.py",
     "dx": 0, "dy": 0, "pwr_off": 0, "port_off": -1},
    {"key": "psu_5v",  "script": "templates/psu_lmzm23601_5v/build_psu_lmzm23601_5v.py",
     "dx": 120, "dy": 0, "pwr_off": 10, "port_off": -1},
    {"key": "psu_3v3", "script": "templates/psu_lmzm23601_3v3/build_psu_lmzm23601_3v3.py",
     "dx": 240, "dy": 0, "pwr_off": 20, "port_off": -1},
    {"key": "esp32",   "script": "templates/esp32s3_core/build_esp32s3_template.py",
     "dx": 0, "dy": 100, "pwr_off": 30, "port_off": 0},
    {"key": "audio",   "script": "templates/audio_ns4168/build_audio_ns4168.py",
     "dx": 200, "dy": 100, "pwr_off": 40, "port_off": 10},
    {"key": "flash",   "script": "templates/flash_csnp1g/build_flash_template.py",
     "dx": 0, "dy": 210, "pwr_off": 50, "port_off": 20},
    {"key": "sdcard",  "script": "templates/sdcard_spi/build_sdcard_template.py",
     "dx": 140, "dy": 210, "pwr_off": 60, "port_off": 30},
]


def uid():
    return str(uuid.uuid4())


def load_module(path, name):
    """Dynamically load a Python module from file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def find_matching_paren(text, start):
    """Return index of closing ')' matching '(' at position start."""
    depth = 0
    i = start
    while i < len(text):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError(f"Unmatched paren at {start}")


def extract_lib_symbols(content):
    """Extract top-level (symbol ...) defs from (lib_symbols ...) as {name: text}."""
    ls_start = content.find("(lib_symbols")
    if ls_start == -1:
        return {}
    ls_end = find_matching_paren(content, ls_start)

    symbols = {}
    i = ls_start + len("(lib_symbols")
    depth = 0
    while i < ls_end:
        c = content[i]
        if c == "(" and depth == 0 and content[i:i + 9] == '(symbol "':
            sym_end = find_matching_paren(content, i)
            sym_text = content[i:sym_end + 1]
            m = re.match(r'\(symbol "([^"]+)"', sym_text)
            if m:
                symbols[m.group(1)] = sym_text
            i = sym_end + 1
            continue
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        i += 1
    return symbols


def extract_body(content):
    """Get body elements between lib_symbols end and sheet_instances start."""
    ls_start = content.find("(lib_symbols")
    ls_end = find_matching_paren(content, ls_start)
    si_start = content.find("(sheet_instances")
    if si_start == -1:
        si_start = content.rfind("(embedded_fonts")
    return content[ls_end + 1:si_start].strip()


def offset_body(body, dx, dy):
    """Apply X/Y coordinate offsets to all (at ...) and (xy ...) in body text."""
    if dx == 0 and dy == 0:
        return body

    def off_at(m):
        x = round(float(m.group(1)) + dx, 3)
        y = round(float(m.group(2)) + dy, 3)
        a = m.group(3) or ""
        return f"(at {x} {y}{a})"

    def off_xy(m):
        x = round(float(m.group(1)) + dx, 3)
        y = round(float(m.group(2)) + dy, 3)
        return f"(xy {x} {y})"

    body = re.sub(r"\(at (-?[\d.]+) (-?[\d.]+)(\s+-?[\d.]+)?\)", off_at, body)
    body = re.sub(r"\(xy (-?[\d.]+) (-?[\d.]+)\)", off_xy, body)
    return body


def renumber_refs(body, pwr_off, port_off):
    """Renumber #PWR and #PORT references to avoid cross-template collisions."""
    if pwr_off != 0:
        body = re.sub(
            r"#PWR(\d+)",
            lambda m: f"#PWR{int(m.group(1)) + pwr_off:02d}",
            body,
        )
    if port_off >= 0 and port_off != 0:
        body = re.sub(
            r"#PORT(\d+)",
            lambda m: f"#PORT{int(m.group(1)) + port_off:02d}",
            body,
        )
    return body


def renumber_component_refs(body, prefix_map):
    """Renumber component references (U, R, C, J, etc.) to avoid collisions."""
    for prefix, offset in prefix_map.items():
        if offset != 0:
            body = re.sub(
                rf'(?<!")({prefix})(\d+)(?!")',
                lambda m, p=prefix, o=offset: f"{p}{int(m.group(2)) + o}",
                body,
            )
    return body


def regenerate_uuids(body, keep=None):
    """Replace all UUIDs with fresh ones, preserving 'keep' UUID if specified."""
    pat = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    return re.sub(pat, lambda m: m.group(0) if m.group(0) == keep else uid(), body)


def extract_symbol_from_file(content, sym_name):
    """Extract a single (symbol ...) block from a .kicad_sym file."""
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


def build_terminal_blocks():
    """Generate terminal block symbols, power symbols, and wires."""
    # Read terminal block lib_symbol from JLCImport
    jlc_path = os.path.join(ROOT, "JLCImport.kicad_sym")
    with open(jlc_path, 'r', encoding='utf-8') as f:
        jlc_content = f.read()

    tb_sym = extract_symbol_from_file(jlc_content, "WJ500V-5_08-2P-14-00A")
    if tb_sym is None:
        raise ValueError("WJ500V-5_08-2P-14-00A not found in JLCImport.kicad_sym")

    # Add JLCImport: prefix
    tb_sym = tb_sym.replace(
        '(symbol "WJ500V-5_08-2P-14-00A"',
        '(symbol "JLCImport:WJ500V-5_08-2P-14-00A"',
        1
    )

    # Read Ports.kicad_sym for OUTP/OUTN
    ports_path = os.path.join(ROOT, "Ports.kicad_sym")
    with open(ports_path, 'r', encoding='utf-8') as f:
        ports_content = f.read()

    outp_sym = extract_symbol_from_file(ports_content, "OUTP")
    outn_sym = extract_symbol_from_file(ports_content, "OUTN")

    if outp_sym:
        outp_sym = outp_sym.replace('(symbol "OUTP"', '(symbol "Ports:OUTP"', 1)
    if outn_sym:
        outn_sym = outn_sym.replace('(symbol "OUTN"', '(symbol "Ports:OUTN"', 1)

    # Build lib_symbols
    lib_parts = [f"    {tb_sym}"]

    # Power symbols needed for terminal blocks
    power_syms = {
        "+24V": "+24V", "+12V": "+12V", "+5V": "+5V", "+3.3V": "+3.3V"
    }

    for net_name, display in power_syms.items():
        safe_name = net_name.replace(".", "_")
        lib_parts.append(f"""    (symbol "power:{net_name}"
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
      (property "Value" "{display}"
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
      (property "Description" "Power symbol creates a global label with name \\"{display}\\""
        (at 0 0 0)
        (effects (font (size 1.27 1.27)) hide)
      )
      (symbol "{net_name}_0_1"
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
      (symbol "{net_name}_1_1"
        (pin power_in line
          (at 0 0 90)
          (length 0)
          (name "~" (effects (font (size 1.27 1.27))))
          (number "1" (effects (font (size 1.27 1.27))))
        )
      )
      (embedded_fonts no)
    )""")

    # GND symbol
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

    # Add OUTP/OUTN port symbols
    if outp_sym:
        lib_parts.append(f"    {outp_sym}")
    if outn_sym:
        lib_parts.append(f"    {outn_sym}")

    lib_symbols_str = "\n".join(lib_parts)

    # Terminal block layout — vertical column, 25mm spacing
    # WJ500V-5_08-2P pin positions (local coords):
    #   Pin 1: (-1.27, -5.08) angle=90 → endpoint at (sx - 1.27, sy + 5.08)
    #   Pin 2: (1.27, -5.08) angle=90  → endpoint at (sx + 1.27, sy + 5.08)
    BASE_X = 120
    BASE_Y = 100
    SPACING = 25

    terminals = [
        {"ref": "J1", "label": "24V INPUT",  "power": "+24V",  "x": BASE_X, "y": BASE_Y},
        {"ref": "J2", "label": "12V TEST",   "power": "+12V",  "x": BASE_X, "y": BASE_Y + SPACING},
        {"ref": "J3", "label": "5V TEST",    "power": "+5V",   "x": BASE_X, "y": BASE_Y + 2*SPACING},
        {"ref": "J4", "label": "3.3V TEST",  "power": "+3.3V", "x": BASE_X, "y": BASE_Y + 3*SPACING},
        {"ref": "J5", "label": "SPEAKER",    "power": None,    "x": BASE_X, "y": BASE_Y + 4*SPACING},
    ]

    symbols = []
    wires = []
    pwr_idx = 1

    def wire(x1, y1, x2, y2):
        return f"""  (wire (pts (xy {x1} {y1}) (xy {x2} {y2}))
    (stroke (width 0) (type default))
    (uuid "{uid()}")
  )"""

    for t in terminals:
        x, y = t["x"], t["y"]
        ref = t["ref"]
        # Pin endpoints (connector pins point downward from body)
        pin1_x, pin1_y = round(x - 1.27, 2), round(y + 5.08, 2)
        pin2_x, pin2_y = round(x + 1.27, 2), round(y + 5.08, 2)

        # Terminal block symbol
        symbols.append(f"""  (symbol
    (lib_id "JLCImport:WJ500V-5_08-2P-14-00A")
    (at {x} {y} 0)
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{uid()}")
    (property "Reference" "{ref}"
      (at {x} {round(y - 8.89, 2)} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "{t['label']}"
      (at {x} {round(y + 8.89, 2)} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "JLCImport:WJ500V-5_08-2P-14-00A"
      (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "LCSC" "C8465"
      (at {x} {y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (instances
      (project "SampleCircuit"
        (path "/{COMBINED_UUID}"
          (reference "{ref}")
          (unit 1)
        )
      )
    )
  )""")

        if t["power"] is not None:
            # Power terminal: pin1 = power rail, pin2 = GND
            pwr_sym_y = round(pin1_y + 5.08, 2)
            gnd_sym_y = round(pin2_y + 5.08, 2)

            # Power symbol above pin 1
            symbols.append(f"""  (symbol
    (lib_id "power:{t['power']}")
    (at {pin1_x} {pwr_sym_y} 180)
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{uid()}")
    (property "Reference" "#PWR{pwr_idx:02d}"
      (at {pin1_x} {round(pwr_sym_y + 3.81, 2)} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Value" "{t['power']}"
      (at {pin1_x} {round(pwr_sym_y + 3.56, 2)} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" ""
      (at {pin1_x} {pwr_sym_y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (instances
      (project "SampleCircuit"
        (path "/{COMBINED_UUID}"
          (reference "#PWR{pwr_idx:02d}")
          (unit 1)
        )
      )
    )
  )""")
            pwr_idx += 1

            # Wire from pin1 down to power symbol
            wires.append(wire(pin1_x, pin1_y, pin1_x, pwr_sym_y))

            # GND symbol below pin 2
            symbols.append(f"""  (symbol
    (lib_id "power:GND")
    (at {pin2_x} {gnd_sym_y} 0)
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{uid()}")
    (property "Reference" "#PWR{pwr_idx:02d}"
      (at {pin2_x} {round(gnd_sym_y + 6.35, 2)} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Value" "GND"
      (at {pin2_x} {round(gnd_sym_y + 3.81, 2)} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" ""
      (at {pin2_x} {gnd_sym_y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (instances
      (project "SampleCircuit"
        (path "/{COMBINED_UUID}"
          (reference "#PWR{pwr_idx:02d}")
          (unit 1)
        )
      )
    )
  )""")
            pwr_idx += 1

            # Wire from pin2 down to GND symbol
            wires.append(wire(pin2_x, pin2_y, pin2_x, gnd_sym_y))

        else:
            # Speaker terminal: pin1 = OUTP, pin2 = OUTN
            port_y = round(pin1_y + 5.08, 2)

            # OUTP port on pin 1
            # Port symbol pin at local (2.54, 0), so connection = (sx + 2.54, sy)
            # Place port so its pin lands on pin1_x: sx = pin1_x - 2.54
            outp_sx = round(pin1_x - 2.54, 2)
            symbols.append(f"""  (symbol
    (lib_id "Ports:OUTP")
    (at {outp_sx} {port_y} 90)
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{uid()}")
    (property "Reference" "#PORT01"
      (at {outp_sx} {port_y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Value" "OUTP"
      (at {round(outp_sx - 3.81, 2)} {port_y} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" ""
      (at {outp_sx} {port_y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (instances
      (project "SampleCircuit"
        (path "/{COMBINED_UUID}"
          (reference "#PORT01")
          (unit 1)
        )
      )
    )
  )""")

            # Wire from pin1 down to port
            wires.append(wire(pin1_x, pin1_y, pin1_x, port_y))

            # OUTN port on pin 2
            outn_sx = round(pin2_x - 2.54, 2)
            symbols.append(f"""  (symbol
    (lib_id "Ports:OUTN")
    (at {outn_sx} {port_y} 90)
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{uid()}")
    (property "Reference" "#PORT02"
      (at {outn_sx} {port_y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (property "Value" "OUTN"
      (at {round(outn_sx + 5.08, 2)} {port_y} 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" ""
      (at {outn_sx} {port_y} 0)
      (effects (font (size 1.27 1.27)) hide)
    )
    (instances
      (project "SampleCircuit"
        (path "/{COMBINED_UUID}"
          (reference "#PORT02")
          (unit 1)
        )
      )
    )
  )""")

            # Wire from pin2 down to port
            wires.append(wire(pin2_x, pin2_y, pin2_x, port_y))

    symbols_str = "\n\n".join(symbols)
    wires_str = "\n\n".join(wires)

    # Build a fake schematic string in the same format as template outputs
    schematic = f"""(kicad_sch
  (version 20250114)
  (generator "build_terminal_blocks")
  (generator_version "9.0")
  (uuid "{COMBINED_UUID}")
  (paper "A4")

  (lib_symbols
{lib_symbols_str}
  )

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


def main():
    all_lib = {}
    bodies = []

    # Process circuit templates
    for t in TEMPLATES:
        path = os.path.join(ROOT, t["script"])
        print(f"  Loading {t['key']} from {t['script']}...")

        mod = load_module(path, f"build_{t['key']}")
        sch = mod.build_schematic()

        # If build_schematic() returned None (locked template), read the
        # pre-built .kicad_sch file directly from the template directory
        if sch is None:
            template_dir = os.path.dirname(path)
            sch_files = [f for f in os.listdir(template_dir) if f.endswith('.kicad_sch')]
            if sch_files:
                sch_path = os.path.join(template_dir, sch_files[0])
                print(f"    (locked — reading pre-built {sch_files[0]})")
                with open(sch_path, 'r', encoding='utf-8') as f:
                    sch = f.read()
            else:
                print(f"    ERROR: No .kicad_sch file found in {template_dir}")
                continue

        for name, text in extract_lib_symbols(sch).items():
            if name not in all_lib:
                all_lib[name] = text

        body = extract_body(sch)

        # Replace template root UUID with combined root UUID
        body = body.replace(TEMPLATE_ROOT_UUIDS[t["key"]], COMBINED_UUID)

        # Update project name
        body = body.replace('(project "AITestProject"', '(project "SampleCircuit"')
        body = body.replace('(project "SampleBoard"', '(project "SampleCircuit"')

        # Apply coordinate offsets
        body = offset_body(body, t["dx"], t["dy"])

        # Renumber #PWR and #PORT to avoid collisions
        body = renumber_refs(body, t["pwr_off"], t["port_off"])

        # Regenerate UUIDs
        body = regenerate_uuids(body, keep=COMBINED_UUID)

        bodies.append(body)

    # Process terminal blocks
    print("  Building terminal blocks...")
    tb_sch = build_terminal_blocks()

    for name, text in extract_lib_symbols(tb_sch).items():
        if name not in all_lib:
            all_lib[name] = text

    tb_body = extract_body(tb_sch)
    # Terminal blocks already use COMBINED_UUID and "SampleCircuit" project name
    # Apply offset to bottom-right area
    tb_body = offset_body(tb_body, 280, 210)
    # Renumber #PWR to avoid collisions (terminal blocks use #PWR01-#PWR10)
    tb_body = renumber_refs(tb_body, 70, 40)
    tb_body = regenerate_uuids(tb_body, keep=COMBINED_UUID)
    bodies.append(tb_body)

    # Build combined lib_symbols section
    lib_sym_entries = "\n".join(f"    {text}" for text in all_lib.values())

    # Assemble the combined schematic
    combined = f"""(kicad_sch
  (version 20250114)
  (generator "build_sample_circuit.py")
  (generator_version "9.0")
  (uuid "{COMBINED_UUID}")
  (paper "A3")

  (lib_symbols
{lib_sym_entries}
  )

{chr(10).join(bodies)}

  (sheet_instances
    (path "/"
      (page "1")
    )
  )
  (embedded_fonts no)
)
"""

    output_path = os.path.join(OUT_DIR, "SampleCircuit.kicad_sch")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(combined)

    print(f"\nWritten: {output_path}")
    print("Paper: A3")
    print("Subcircuits:")
    print("  Row 1: PSU 24V->12V | PSU 12V->5V | PSU 12V->3.3V")
    print("  Row 2: ESP32-S3     | Audio NS4168")
    print("  Row 3: Flash CSNP1G | SD Card     | Terminal Blocks")
    print("\nTerminal Blocks:")
    print("  J1: 24V INPUT  (power input)")
    print("  J2: 12V TEST   (test point)")
    print("  J3: 5V TEST    (test point)")
    print("  J4: 3.3V TEST  (test point)")
    print("  J5: SPEAKER    (OUTP/OUTN)")


if __name__ == "__main__":
    main()
