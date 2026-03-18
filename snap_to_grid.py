"""
snap_to_grid.py — Snap all body coordinates in a .kicad_sch to 2.54mm grid.

Operates on the existing schematic in-place, preserving UUIDs and structure.
Only snaps coordinates in placed elements (symbols, wires, junctions, etc.),
NOT in lib_symbols definitions.

Usage:
    python snap_to_grid.py SampleCircuit.kicad_sch
"""

import re
import shutil
import subprocess
import sys
import os

GRID = 2.54


def snap(val):
    """Snap a coordinate value to the 2.54mm grid."""
    return round(round(val / GRID) * GRID, 2)


def snap_coords(text):
    """Snap all (at ...) and (xy ...) coordinates in text to 2.54mm grid."""

    def snap_at(m):
        x = snap(float(m.group(1)))
        y = snap(float(m.group(2)))
        a = m.group(3) or ""
        return f"(at {x} {y}{a})"

    def snap_xy(m):
        x = snap(float(m.group(1)))
        y = snap(float(m.group(2)))
        return f"(xy {x} {y})"

    text = re.sub(r"\(at (-?[\d.]+) (-?[\d.]+)(\s+-?[\d.]+)?\)", snap_at, text)
    text = re.sub(r"\(xy (-?[\d.]+) (-?[\d.]+)\)", snap_xy, text)
    return text


def find_matching_paren(text, start):
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


def main():
    if len(sys.argv) < 2:
        print("Usage: python snap_to_grid.py <file.kicad_sch>")
        sys.exit(1)

    path = sys.argv[1]

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Backup
    bak_path = path + ".bak"
    shutil.copy2(path, bak_path)
    print(f"Backup: {bak_path}")

    # Find lib_symbols section — DO NOT snap these (they're component definitions)
    ls_start = content.find("(lib_symbols")
    ls_end = find_matching_paren(content, ls_start)

    # Find footer
    si_start = content.find("(sheet_instances", ls_end)
    if si_start == -1:
        si_start = content.rfind("(embedded_fonts")

    # Split into: header + lib_symbols | body | footer
    header_and_lib = content[:ls_end + 1]
    body = content[ls_end + 1:si_start]
    footer = content[si_start:]

    # Count off-grid coords before
    before_count = 0
    for m in re.finditer(r'\((?:at|xy)\s+(-?[\d.]+)\s+(-?[\d.]+)', body):
        x, y = float(m.group(1)), float(m.group(2))
        x_ok = abs(x % 2.54) < 0.01 or abs(x % 2.54 - 2.54) < 0.01
        y_ok = abs(y % 2.54) < 0.01 or abs(y % 2.54 - 2.54) < 0.01
        if not x_ok or not y_ok:
            before_count += 1

    # Snap body coordinates
    snapped_body = snap_coords(body)

    # Count off-grid after
    after_count = 0
    for m in re.finditer(r'\((?:at|xy)\s+(-?[\d.]+)\s+(-?[\d.]+)', snapped_body):
        x, y = float(m.group(1)), float(m.group(2))
        x_ok = abs(x % 2.54) < 0.01 or abs(x % 2.54 - 2.54) < 0.01
        y_ok = abs(y % 2.54) < 0.01 or abs(y % 2.54 - 2.54) < 0.01
        if not x_ok or not y_ok:
            after_count += 1

    result = header_and_lib + snapped_body + footer

    with open(path, 'w', encoding='utf-8') as f:
        f.write(result)

    print(f"\nSnapped: {path}")
    print(f"  Off-grid coords before: {before_count}")
    print(f"  Off-grid coords after:  {after_count}")

    # Validate
    print("\nValidating...")
    python = sys.executable
    validate = os.path.join(os.path.dirname(os.path.abspath(__file__)), "validate_sch.py")
    if os.path.exists(validate):
        result = subprocess.run([python, validate, path], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print("VALIDATION FAILED — restoring backup")
            shutil.copy2(bak_path, path)
            sys.exit(1)
    else:
        print("  (validate_sch.py not found, skipping)")


if __name__ == "__main__":
    main()
