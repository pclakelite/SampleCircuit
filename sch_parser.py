"""
sch_parser.py — Parse KiCad 9 schematic (.kicad_sch) into structured sections.

Supports round-trip: parse → reassemble → validate with no functional diff.
Preserves all UUIDs, positions, and formatting of existing elements.

Usage as module:
    from sch_parser import parse_schematic, reassemble

Usage as CLI (round-trip test):
    python sch_parser.py SampleCircuit.kicad_sch
"""

import re
import sys


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
    """Extract (symbol ...) defs from (lib_symbols ...) as {name: raw_text}."""
    ls_start = content.find("(lib_symbols")
    if ls_start == -1:
        return {}, -1, -1

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

    return symbols, ls_start, ls_end


def identify_element(raw_text):
    """Return (elem_type, identity_key) for a body element.

    Identity keys:
      symbol  → ("symbol", reference_designator)  e.g. ("symbol", "U1")
      wire    → ("wire", ((x1,y1), (x2,y2)))
      junction → ("junction", (x, y))
      no_connect → ("no_connect", (x, y))
      label   → ("label", name)
      global_label → ("global_label", name)
      text    → ("text", first_20_chars)
    """
    stripped = raw_text.strip()

    if stripped.startswith("(symbol"):
        ref_m = re.search(r'\(property "Reference" "([^"]+)"', raw_text)
        ref = ref_m.group(1) if ref_m else "UNKNOWN"
        lib_m = re.search(r'\(lib_id "([^"]+)"\)', raw_text)
        lib_id = lib_m.group(1) if lib_m else ""
        return ("symbol", ref, lib_id)

    if stripped.startswith("(wire"):
        coords = re.findall(r'\(xy ([\d.\-]+) ([\d.\-]+)\)', raw_text)
        pts = tuple((c[0], c[1]) for c in coords)
        return ("wire", pts, "")

    if stripped.startswith("(junction"):
        m = re.search(r'\(at ([\d.\-]+) ([\d.\-]+)\)', raw_text)
        if m:
            return ("junction", (m.group(1), m.group(2)), "")
        return ("junction", None, "")

    if stripped.startswith("(no_connect"):
        m = re.search(r'\(at ([\d.\-]+) ([\d.\-]+)\)', raw_text)
        if m:
            return ("no_connect", (m.group(1), m.group(2)), "")
        return ("no_connect", None, "")

    if stripped.startswith("(label"):
        m = re.match(r'\s*\(label "([^"]+)"', raw_text)
        name = m.group(1) if m else "UNKNOWN"
        return ("label", name, "")

    if stripped.startswith("(global_label"):
        m = re.match(r'\s*\(global_label "([^"]+)"', raw_text)
        name = m.group(1) if m else "UNKNOWN"
        return ("global_label", name, "")

    if stripped.startswith("(text"):
        return ("text", stripped[:40], "")

    return ("unknown", stripped[:40], "")


def extract_body_elements(content, body_start, body_end):
    """Extract individual top-level elements from the body section.

    Returns list of dicts with type, key, lib_id, raw, start, end.
    start/end are character positions in the original content.
    """
    elements = []
    i = body_start

    while i < body_end:
        # Skip whitespace
        if content[i] in ' \t\n\r':
            i += 1
            continue

        if content[i] == '(':
            # Find matching close paren
            end = find_matching_paren(content, i)
            raw = content[i:end + 1]
            elem_type, key, lib_id = identify_element(raw)
            elements.append({
                "type": elem_type,
                "key": key,
                "lib_id": lib_id,
                "raw": raw,
                "start": i,
                "end": end + 1,
            })
            i = end + 1
        else:
            i += 1

    return elements


def parse_schematic(content):
    """Parse a .kicad_sch file into structured sections.

    Returns dict with:
      header:       text before lib_symbols
      lib_symbols:  {name: raw_text}
      elements:     [{type, key, lib_id, raw}, ...]
      footer:       sheet_instances + embedded_fonts + closing paren
    """
    # Extract lib_symbols
    lib_symbols, ls_start, ls_end = extract_lib_symbols(content)

    # Header = everything before lib_symbols
    header = content[:ls_start].rstrip() + "\n\n"

    # Find footer markers
    si_start = content.find("(sheet_instances", ls_end)
    ef_start = content.find("(embedded_fonts", ls_end)

    # Footer starts at whichever comes first
    footer_start = len(content)
    if si_start != -1:
        footer_start = min(footer_start, si_start)
    if ef_start != -1:
        footer_start = min(footer_start, ef_start)

    # Walk back to find the "  " indentation before footer
    while footer_start > 0 and content[footer_start - 1] in ' \t\n\r':
        footer_start -= 1
    footer_start += 1  # Keep one newline

    footer = content[footer_start:]

    # Body = between lib_symbols end and footer start
    body_start = ls_end + 1
    body_end = footer_start
    body_raw = content[body_start:body_end]

    elements = extract_body_elements(content, body_start, body_end)

    return {
        "header": header,
        "lib_symbols": lib_symbols,
        "lib_symbols_raw": content[ls_start:ls_end + 1],
        "elements": elements,
        "body_raw": body_raw,
        "body_start": body_start,
        "body_end": body_end,
        "footer": footer,
        "original": content,
    }


def reassemble(parsed):
    """Reassemble parsed sections into a .kicad_sch string.

    Strategy: rebuild from original content, only modifying
    the lib_symbols section and body elements that changed.
    """
    original = parsed.get("original")
    lib_symbols = parsed["lib_symbols"]
    elements = parsed["elements"]

    if original:
        # Surgical approach: rebuild using original text
        # Find lib_symbols section boundaries
        ls_start = original.find("(lib_symbols")
        ls_end = find_matching_paren(original, ls_start)

        # Rebuild lib_symbols section
        lib_entries = "\n".join(f"    {text}" for text in lib_symbols.values())
        new_lib_section = f"(lib_symbols\n{lib_entries}\n  )"

        # Build new body from elements (preserving original raw text)
        body_start = parsed["body_start"]
        body_end = parsed["body_end"]

        # Collect elements that were in the original (have start/end)
        # and new elements (no start/end)
        original_elements = [e for e in elements if "start" in e and e["start"] is not None]
        new_elements = [e for e in elements if "start" not in e or e["start"] is None]

        # Build body by keeping original text structure
        # Remove deleted elements by replacing their spans with empty
        # Keep all other text (whitespace, comments) between elements

        # Create a set of spans to keep
        keep_spans = set()
        for e in original_elements:
            keep_spans.add((e["start"], e["end"]))

        # Get all original element spans
        orig_elements = extract_body_elements(parsed["original"],
                                               parsed["body_start"],
                                               parsed["body_end"])
        orig_spans = [(e["start"], e["end"]) for e in orig_elements]

        # Build body: walk through original body, keeping/removing spans
        body_parts = []
        pos = body_start
        for orig_start, orig_end in orig_spans:
            # Add whitespace between elements
            if pos < orig_start:
                body_parts.append(original[pos:orig_start])
            # Check if this span is kept
            if (orig_start, orig_end) in keep_spans:
                # Find the possibly-modified element
                for e in original_elements:
                    if e.get("start") == orig_start and e.get("end") == orig_end:
                        body_parts.append(e["raw"])
                        break
                else:
                    body_parts.append(original[orig_start:orig_end])
            # else: element was removed, skip it
            pos = orig_end

        # Add trailing whitespace
        if pos < body_end:
            body_parts.append(original[pos:body_end])

        body_text = "".join(body_parts)

        # Add new elements at end of body
        if new_elements:
            new_parts = []
            for elem in new_elements:
                new_parts.append(f"\n\n  {elem['raw']}")
            body_text += "".join(new_parts)

        # Assemble: header + lib_symbols + body + footer
        result = (original[:ls_start] + new_lib_section +
                  body_text + parsed["footer"])
        return result
    else:
        # Fallback: build from scratch
        header = parsed.get("header", "(kicad_sch\n")
        footer = parsed.get("footer", ")")
        lib_entries = "\n".join(f"    {text}" for text in lib_symbols.values())
        lib_section = f"  (lib_symbols\n{lib_entries}\n  )\n"
        body_parts = [f"  {elem['raw']}" for elem in elements]
        body = "\n\n".join(body_parts)
        return f"{header}{lib_section}\n{body}\n\n  {footer}"


def find_element_by_ref(elements, ref):
    """Find element index by reference designator (e.g. 'U1', 'R3')."""
    for i, elem in enumerate(elements):
        if elem["type"] == "symbol" and elem["key"] == ref:
            return i
    return -1


def find_elements_by_type(elements, elem_type):
    """Find all element indices of a given type."""
    return [i for i, elem in enumerate(elements) if elem["type"] == elem_type]


def get_max_ref_number(elements, prefix):
    """Get highest reference number for a prefix (e.g. 'U' → max of U1,U2,...).

    Also checks #PWR and #PORT prefixes.
    """
    max_num = 0
    pat = re.compile(rf'^{re.escape(prefix)}(\d+)$')
    for elem in elements:
        if elem["type"] == "symbol":
            m = pat.match(elem["key"])
            if m:
                max_num = max(max_num, int(m.group(1)))
    return max_num


# ── CLI: round-trip test ──────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sch_parser.py <file.kicad_sch>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, 'r', encoding='utf-8') as f:
        original = f.read()

    parsed = parse_schematic(original)

    print(f"Parsed: {path}")
    print(f"  lib_symbols: {len(parsed['lib_symbols'])} entries")
    print(f"  body elements: {len(parsed['elements'])}")

    # Count by type
    by_type = {}
    for elem in parsed["elements"]:
        by_type[elem["type"]] = by_type.get(elem["type"], 0) + 1
    for t, c in sorted(by_type.items()):
        print(f"    {t}: {c}")

    # Find max refs
    for prefix in ["U", "R", "C", "J", "D", "Q", "#PWR", "#PORT"]:
        mx = get_max_ref_number(parsed["elements"], prefix)
        if mx > 0:
            print(f"  max {prefix}: {mx}")

    # Round-trip test
    reassembled = reassemble(parsed)

    # Write to temp for comparison
    out_path = path.replace(".kicad_sch", "_roundtrip.kicad_sch")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(reassembled)
    print(f"\nRound-trip written to: {out_path}")
    print("Compare with: diff or validate_sch.py")
