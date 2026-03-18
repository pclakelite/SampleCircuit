"""
Validate a KiCad 9 template schematic (.kicad_sch) for common format issues.

Usage:
  python validate_template.py <path_to_kicad_sch>
  python validate_template.py                       # validates ALL templates

Checks:
  1. Parentheses balance
  2. Symbol (at) has 3 numbers (x y angle)
  3. No duplicate UUIDs
  4. Every placed symbol has (instances) block
  5. Every referenced lib_id exists in lib_symbols
  6. (embedded_fonts no) present
  7. (sheet_instances) present
  8. File format version is 20250114 (KiCad 9.0)
  9. No empty lib_symbols section
"""
import re
import sys
import os
import collections
import json
import glob


def validate_schematic(path):
    """Validate a single .kicad_sch file. Returns (errors, warnings)."""
    errors = []
    warnings = []

    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    content = ''.join(lines)

    # 1. Parentheses balance
    depth = 0
    for i, line in enumerate(lines, 1):
        for ch in line:
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth < 0:
                    errors.append(f"Line {i}: Extra closing parenthesis (depth went negative)")
    if depth != 0:
        errors.append(f"End of file: Unbalanced parentheses (depth={depth})")

    # 2. Symbol (at ...) must have 3 numbers: x y angle
    in_symbol = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if '(lib_id ' in stripped:
            in_symbol = True
        if in_symbol and stripped.startswith('(at '):
            m2 = re.match(r'\(at\s+([\d.\-]+)\s+([\d.\-]+)\s*\)', stripped)
            m3 = re.match(r'\(at\s+([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)\)', stripped)
            if m2 and not m3:
                errors.append(f"Line {i}: Symbol (at) missing angle parameter: {stripped}")
            in_symbol = False

    # 3. Duplicate UUIDs
    uuids = []
    for i, line in enumerate(lines, 1):
        for m in re.finditer(r'\(uuid "([^"]+)"\)', line):
            uuids.append((m.group(1), i))
    uuid_counts = collections.Counter(u for u, _ in uuids)
    for uuid_val, count in uuid_counts.items():
        if count > 1:
            locs = [str(ln) for u, ln in uuids if u == uuid_val]
            errors.append(f"Duplicate UUID '{uuid_val[:16]}...' on lines: {', '.join(locs)}")

    # 4. Every placed symbol has (instances) block
    placed_symbols = list(re.finditer(r'\(symbol\s*\n\s*\(lib_id "([^"]+)"\)', content))
    for m in placed_symbols:
        start = m.start()
        d = 0
        j = start
        while j < len(content):
            if content[j] == '(':
                d += 1
            elif content[j] == ')':
                d -= 1
                if d == 0:
                    block = content[start:j+1]
                    if '(instances' not in block:
                        line_num = content[:start].count('\n') + 1
                        warnings.append(f"Line {line_num}: Symbol '{m.group(1)}' missing (instances) block")
                    break
            j += 1

    # 5. Every referenced lib_id exists in lib_symbols
    lib_sym_start = content.find('(lib_symbols')
    if lib_sym_start >= 0:
        # Use bracket-matching to find the full lib_symbols section
        d = 0
        j = lib_sym_start
        lib_sym_text = None
        while j < len(content):
            if content[j] == '(':
                d += 1
            elif content[j] == ')':
                d -= 1
                if d == 0:
                    lib_sym_text = content[lib_sym_start:j+1]
                    break
            j += 1
        if lib_sym_text is None:
            errors.append("lib_symbols section has unbalanced parentheses")
        elif len(lib_sym_text.strip()) < 20:
            errors.append("lib_symbols section is empty — symbols will render as red boxes")
        else:
            for m in placed_symbols:
                lib_id = m.group(1)
                if f'"{lib_id}"' not in lib_sym_text:
                    line_num = content[:m.start()].count('\n') + 1
                    errors.append(f"Line {line_num}: lib_id '{lib_id}' not found in lib_symbols")
    else:
        errors.append("No lib_symbols section found")

    # 6. (embedded_fonts no) present
    if '(embedded_fonts no)' not in content:
        warnings.append("Missing (embedded_fonts no) — required for KiCad 9.0")

    # 7. (sheet_instances) present
    if '(sheet_instances' not in content:
        warnings.append("Missing (sheet_instances) section")

    # 8. File format version
    ver_match = re.search(r'\(version (\d+)\)', content)
    if ver_match:
        ver = ver_match.group(1)
        if ver != '20250114':
            warnings.append(f"Version is {ver}, expected 20250114 (KiCad 9.0)")
    else:
        errors.append("No (version) found in file")

    # 9. Count summary
    wire_count = len(re.findall(r'\(wire\b', content))
    nc_count = len(re.findall(r'\(no_connect\b', content))
    junc_count = len(re.findall(r'\(junction\b', content))
    sym_count = len(placed_symbols)

    return errors, warnings, {
        'lines': len(lines),
        'uuids': len(uuids),
        'symbols': sym_count,
        'wires': wire_count,
        'no_connects': nc_count,
        'junctions': junc_count,
    }


def find_all_templates():
    """Find all .kicad_sch files in template subdirectories."""
    templates_dir = os.path.dirname(os.path.abspath(__file__))
    results = []
    for entry in sorted(os.listdir(templates_dir)):
        subdir = os.path.join(templates_dir, entry)
        if os.path.isdir(subdir):
            for f in os.listdir(subdir):
                if f.endswith('.kicad_sch'):
                    results.append(os.path.join(subdir, f))
    return results


def main():
    if len(sys.argv) > 1:
        paths = [sys.argv[1]]
    else:
        paths = find_all_templates()
        if not paths:
            print("No .kicad_sch files found in template subdirectories.")
            sys.exit(1)
        print(f"Found {len(paths)} template schematic(s) to validate.\n")

    total_errors = 0
    total_warnings = 0

    for path in paths:
        name = os.path.basename(os.path.dirname(path)) + '/' + os.path.basename(path)

        # Check lock status
        status_path = os.path.join(os.path.dirname(path), 'status.json')
        lock_status = '?'
        if os.path.exists(status_path):
            with open(status_path, 'r') as f:
                status = json.load(f)
            lock_status = status.get('status', '?')

        errors, warnings, stats = validate_schematic(path)
        total_errors += len(errors)
        total_warnings += len(warnings)

        status_icon = {
            'locked': 'LOCKED',
            'review': 'REVIEW',
            'draft': 'DRAFT',
        }.get(lock_status, lock_status.upper())

        result = 'PASS' if not errors else 'FAIL'
        print(f"[{result}] [{status_icon}] {name}")
        print(f"       {stats['lines']} lines, {stats['uuids']} UUIDs, "
              f"{stats['symbols']} symbols, {stats['wires']} wires, "
              f"{stats['no_connects']} NCs, {stats['junctions']} junctions")

        if errors:
            for e in errors:
                print(f"       ERROR: {e}")
        if warnings:
            for w in warnings:
                print(f"       WARN:  {w}")
        print()

    # Summary
    if len(paths) > 1:
        print(f"{'='*60}")
        print(f"Total: {len(paths)} templates, {total_errors} error(s), {total_warnings} warning(s)")

    sys.exit(1 if total_errors else 0)


if __name__ == '__main__':
    main()
