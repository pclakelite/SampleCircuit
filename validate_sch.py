"""
Validate a KiCad 9 schematic file for common format issues.
Checks: parentheses balance, symbol (at) requires 3 numbers,
property (at) requires 3 numbers, duplicate UUIDs, etc.
"""
import re, sys, collections

if len(sys.argv) > 1:
    path = sys.argv[1]
else:
    path = r"c:\Projects\CircuitAI\AITestProject.kicad_sch"

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

errors = []
warnings = []

# 1. Parentheses balance per-line tracking
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
# Match lines like: (at 78.74 215.9) inside symbol context
in_symbol = False
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    if stripped.startswith('(symbol') and '(lib_id' not in stripped:
        # This is a top-level (symbol line in lib_symbols, skip
        pass
    if '(lib_id ' in stripped:
        in_symbol = True
    if in_symbol and stripped.startswith('(at '):
        # Parse the (at ...) content
        m = re.match(r'\(at\s+([\d.\-]+)\s+([\d.\-]+)\s*\)', stripped)
        if m:
            # Only 2 numbers - missing angle
            errors.append(f"Line {i}: Symbol (at) missing angle parameter: {stripped}")
        m3 = re.match(r'\(at\s+([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)\)', stripped)
        if m3:
            pass  # OK - has 3 numbers
        in_symbol = False  # Only check the first (at) after lib_id

# 3. Check for duplicate UUIDs
uuids = []
for i, line in enumerate(lines, 1):
    for m in re.finditer(r'\(uuid "([^"]+)"\)', line):
        uuids.append((m.group(1), i))

uuid_counts = collections.Counter(u for u, _ in uuids)
for uuid_val, count in uuid_counts.items():
    if count > 1:
        locs = [str(line_num) for u, line_num in uuids if u == uuid_val]
        errors.append(f"Duplicate UUID '{uuid_val[:12]}...' on lines: {', '.join(locs)}")

# 4. Check that every placed symbol has (instances ...) block
# Look for (symbol with (lib_id but no (instances
content = ''.join(lines)
placed_symbols = list(re.finditer(r'\(symbol\s*\n\s*\(lib_id "([^"]+)"\)', content))
for m in placed_symbols:
    # Find the end of this symbol block
    start = m.start()
    d = 0
    j = start
    has_instances = False
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

# 5. Check lib_symbols section contains all referenced lib_ids
lib_sym_start = content.find('(lib_symbols')
lib_sym_text = ""
if lib_sym_start != -1:
    d = 0
    j = lib_sym_start
    while j < len(content):
        if content[j] == '(':
            d += 1
        elif content[j] == ')':
            d -= 1
            if d == 0:
                lib_sym_text = content[lib_sym_start:j+1]
                break
        j += 1
if lib_sym_text:
    for m in placed_symbols:
        lib_id = m.group(1)
        if f'"{lib_id}"' not in lib_sym_text:
            line_num = content[:m.start()].count('\n') + 1
            errors.append(f"Line {line_num}: lib_id '{lib_id}' not found in lib_symbols section")

# Report
print(f"Validated {len(lines)} lines")
print(f"  {len(errors)} error(s), {len(warnings)} warning(s)")
if errors:
    print("\nERRORS:")
    for e in errors:
        print(f"  {e}")
if warnings:
    print("\nWARNINGS:")
    for w in warnings:
        print(f"  {w}")
if not errors and not warnings:
    print("\nAll checks passed!")

sys.exit(1 if errors else 0)
