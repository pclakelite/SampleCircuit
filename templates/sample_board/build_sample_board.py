"""
build_sample_board.py — Combine 4 reviewed templates into one flat schematic.

Layout on A3 sheet:
  Top-left:      PSU 12V->5V  (LMZM23601)
  Top-right:     PSU 12V->3.3V (LMZM23601 + PMEG6030)
  Bottom-left:   RTC (RV-3028-C7)
  Bottom-right:  Audio (MAX98357A)

Run: python build_sample_board.py
"""

import importlib.util
import os
import re
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

COMBINED_UUID = "e1a2b3c4-d5e6-7f89-0a1b-c2d3e4f5a6b7"

# Template root UUIDs (from each build script)
TEMPLATE_ROOT_UUIDS = {
    "psu_5v":  "a3e7c1d4-8f2b-4a6e-9c5d-1b3e7f9a2c4d",
    "psu_3v3": "7a6fd472-71e4-4f31-b6fe-f7300bc4d95f",
    "rtc":     "57cbccc0-4dfd-4b96-9673-3939a22818a6",
    "audio":   "a3e7b1c2-5d4f-4a89-9e6c-1f2d3a4b5c6d",
}

# Layout: each template gets an X/Y offset so they don't overlap on A3
# pwr_off/port_off shift #PWR/#PORT numbers to avoid collisions
TEMPLATES = [
    {"key": "psu_5v",  "script": "templates/psu_lmzm23601_5v/build_psu_lmzm23601_5v.py",
     "dx": 0, "dy": 0, "pwr_off": 0, "port_off": -1},
    {"key": "psu_3v3", "script": "templates/psu_lmzm23601_3v3/build_psu_lmzm23601_3v3.py",
     "dx": 130, "dy": 0, "pwr_off": 10, "port_off": -1},
    {"key": "rtc",     "script": "templates/rtc_rv3028/build_rtc_template.py",
     "dx": 0, "dy": 80, "pwr_off": 20, "port_off": 0},
    {"key": "audio",   "script": "templates/audio_max98357/build_audio_template.py",
     "dx": 130, "dy": 80, "pwr_off": 30, "port_off": 10},
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
    # Scan inside lib_symbols for top-level (symbol ...) blocks at depth 0
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


def regenerate_uuids(body, keep=None):
    """Replace all UUIDs with fresh ones, preserving 'keep' UUID if specified."""
    pat = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    return re.sub(pat, lambda m: m.group(0) if m.group(0) == keep else uid(), body)


def main():
    all_lib = {}
    bodies = []

    for t in TEMPLATES:
        path = os.path.join(ROOT, t["script"])
        print(f"  Loading {t['key']} from {t['script']}...")

        # Load module and call build_schematic() directly (bypasses lock check)
        mod = load_module(path, f"build_{t['key']}")
        sch = mod.build_schematic()

        # Collect lib_symbols (deduplicate by name across templates)
        for name, text in extract_lib_symbols(sch).items():
            if name not in all_lib:
                all_lib[name] = text

        # Extract body (symbols, wires, junctions, no_connects)
        body = extract_body(sch)

        # Replace template root UUID with combined root UUID
        body = body.replace(TEMPLATE_ROOT_UUIDS[t["key"]], COMBINED_UUID)

        # Update project name
        body = body.replace('(project "AITestProject"', '(project "SampleBoard"')

        # Apply coordinate offsets
        body = offset_body(body, t["dx"], t["dy"])

        # Renumber #PWR and #PORT to avoid collisions
        body = renumber_refs(body, t["pwr_off"], t["port_off"])

        # Regenerate UUIDs (preserve combined root UUID)
        body = regenerate_uuids(body, keep=COMBINED_UUID)

        bodies.append(body)

    # Build combined lib_symbols section
    lib_sym_entries = "\n".join(f"    {text}" for text in all_lib.values())

    # Assemble the combined schematic
    combined = f"""(kicad_sch
  (version 20250114)
  (generator "build_sample_board.py")
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

    output_path = os.path.join(OUT_DIR, "SampleBoard.kicad_sch")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(combined)

    print(f"\nWritten: {output_path}")
    print("Paper: A3")
    print("Subcircuits:")
    print("  Top-left:     PSU 12V->5V  (U6, R3, R4, C31-C33)")
    print("  Top-right:    PSU 12V->3.3V (U5, D8, C11, C34-C35, R31-R32)")
    print("  Bottom-left:  RTC (U8, R41, R46, C10, B3)")
    print("  Bottom-right: Audio (U4, R6-R7, C15-C16)")


if __name__ == "__main__":
    main()
