"""
patch_schematic.py — Surgically patch a KiCad 9 schematic without losing manual edits.

Applies a JSON patch manifest to an existing .kicad_sch file.
Only touches the specific elements listed in the patch — everything
else (positions, wires, UUIDs) is preserved exactly as-is.

Usage:
    python patch_schematic.py SampleCircuit.kicad_sch patch.json

Patch manifest format (all fields optional):
{
    "add_lib_symbols": {"SymName": "<s-expr>", ...},
    "remove_lib_symbols": ["SymName", ...],
    "add_elements": ["<s-expr>", ...],
    "remove_elements": [
        {"type": "symbol", "ref": "U3"},
        {"type": "wire", "endpoints": [[x1,y1], [x2,y2]]},
        {"type": "junction", "at": [x, y]},
        {"type": "no_connect", "at": [x, y]}
    ],
    "replace_elements": [
        {"match": {"type": "symbol", "ref": "R5"}, "with": "<new s-expr>"}
    ]
}
"""

import json
import os
import shutil
import subprocess
import sys

from sch_parser import parse_schematic, reassemble, identify_element


def coords_match(a, b, eps=0.02):
    """Compare two coordinate values (strings or floats) with epsilon."""
    return abs(float(a) - float(b)) < eps


def find_element_index(elements, match_spec):
    """Find index of element matching the spec dict.

    match_spec keys:
      type: "symbol" | "wire" | "junction" | "no_connect" | "label"
      ref:  reference designator (for symbols)
      at:   [x, y] (for junctions, no_connect)
      endpoints: [[x1,y1],[x2,y2]] (for wires)
      name: label name (for labels/global_labels)
    """
    m_type = match_spec.get("type")

    for i, elem in enumerate(elements):
        if elem["type"] != m_type:
            continue

        if m_type == "symbol":
            if elem["key"] == match_spec.get("ref"):
                return i

        elif m_type == "wire":
            eps_pts = match_spec.get("endpoints", [])
            if len(eps_pts) == 2 and isinstance(elem["key"], tuple) and len(elem["key"]) == 2:
                if (coords_match(elem["key"][0][0], eps_pts[0][0]) and
                    coords_match(elem["key"][0][1], eps_pts[0][1]) and
                    coords_match(elem["key"][1][0], eps_pts[1][0]) and
                    coords_match(elem["key"][1][1], eps_pts[1][1])):
                    return i

        elif m_type in ("junction", "no_connect"):
            at = match_spec.get("at", [])
            if len(at) == 2 and elem["key"] is not None:
                if coords_match(elem["key"][0], at[0]) and coords_match(elem["key"][1], at[1]):
                    return i

        elif m_type in ("label", "global_label"):
            if elem["key"] == match_spec.get("name"):
                return i

    return -1


def apply_patch(sch_path, patch):
    """Apply a patch manifest to a schematic file.

    Args:
        sch_path: path to .kicad_sch file
        patch: dict with patch manifest (see module docstring)

    Returns:
        (new_content, stats) where stats is a dict of counts
    """
    with open(sch_path, 'r', encoding='utf-8') as f:
        content = f.read()

    parsed = parse_schematic(content)
    stats = {"added_syms": 0, "removed_syms": 0,
             "added_elems": 0, "removed_elems": 0, "replaced_elems": 0}

    # 1. Add lib_symbols
    for name, text in patch.get("add_lib_symbols", {}).items():
        if name not in parsed["lib_symbols"]:
            parsed["lib_symbols"][name] = text
            stats["added_syms"] += 1
            print(f"  + lib_symbol: {name}")
        else:
            print(f"  ~ lib_symbol already exists: {name} (skipped)")

    # 2. Remove lib_symbols
    for name in patch.get("remove_lib_symbols", []):
        if name in parsed["lib_symbols"]:
            # Check if still referenced by any remaining element
            still_used = any(
                elem["lib_id"] == name
                for elem in parsed["elements"]
            )
            if still_used:
                print(f"  ! lib_symbol still in use: {name} (skipped)")
            else:
                del parsed["lib_symbols"][name]
                stats["removed_syms"] += 1
                print(f"  - lib_symbol: {name}")
        else:
            print(f"  ~ lib_symbol not found: {name} (skipped)")

    # 3. Remove elements
    indices_to_remove = set()
    for match_spec in patch.get("remove_elements", []):
        idx = find_element_index(parsed["elements"], match_spec)
        if idx >= 0:
            indices_to_remove.add(idx)
            elem = parsed["elements"][idx]
            print(f"  - {elem['type']}: {elem['key']}")
            stats["removed_elems"] += 1
        else:
            print(f"  ! not found for removal: {match_spec}")

    # Remove in reverse order to preserve indices
    for idx in sorted(indices_to_remove, reverse=True):
        parsed["elements"].pop(idx)

    # 4. Replace elements
    for rep in patch.get("replace_elements", []):
        match_spec = rep["match"]
        new_raw = rep["with"]
        idx = find_element_index(parsed["elements"], match_spec)
        if idx >= 0:
            new_type, new_key, new_lib_id = identify_element(new_raw)
            parsed["elements"][idx] = {
                "type": new_type,
                "key": new_key,
                "lib_id": new_lib_id,
                "raw": new_raw,
            }
            print(f"  ~ replaced {match_spec['type']}: {match_spec.get('ref', match_spec)}")
            stats["replaced_elems"] += 1
        else:
            print(f"  ! not found for replacement: {match_spec}")

    # 5. Add elements
    for raw in patch.get("add_elements", []):
        elem_type, key, lib_id = identify_element(raw)
        parsed["elements"].append({
            "type": elem_type,
            "key": key,
            "lib_id": lib_id,
            "raw": raw,
        })
        print(f"  + {elem_type}: {key}")
        stats["added_elems"] += 1

    # Reassemble
    new_content = reassemble(parsed)
    return new_content, stats


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    reload_kicad = "--reload" in sys.argv

    if len(args) < 2:
        print("Usage: python patch_schematic.py <file.kicad_sch> <patch.json> [--reload]")
        sys.exit(1)

    sch_path = args[0]
    patch_path = args[1]

    if not os.path.exists(sch_path):
        print(f"ERROR: Schematic not found: {sch_path}")
        sys.exit(1)
    if not os.path.exists(patch_path):
        print(f"ERROR: Patch file not found: {patch_path}")
        sys.exit(1)

    with open(patch_path, 'r', encoding='utf-8') as f:
        patch = json.load(f)

    # Backup
    bak_path = sch_path + ".bak"
    shutil.copy2(sch_path, bak_path)
    print(f"Backup: {bak_path}")

    print(f"\nApplying patch from {patch_path}...")
    new_content, stats = apply_patch(sch_path, patch)

    # Write
    with open(sch_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"\nWritten: {sch_path}")
    print(f"  lib_symbols: +{stats['added_syms']} -{stats['removed_syms']}")
    print(f"  elements:    +{stats['added_elems']} -{stats['removed_elems']} ~{stats['replaced_elems']}")

    # Validate
    print("\nValidating...")
    python = sys.executable
    validate = os.path.join(os.path.dirname(os.path.abspath(__file__)), "validate_sch.py")
    if os.path.exists(validate):
        result = subprocess.run([python, validate, sch_path], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print("VALIDATION FAILED — restoring backup")
            shutil.copy2(bak_path, sch_path)
            sys.exit(1)
    else:
        print("  (validate_sch.py not found, skipping)")

    # Auto-reload KiCad if requested
    if reload_kicad:
        try:
            from kicad_patch.kicad_ipc import revert_schematic
            revert_schematic()
        except Exception as e:
            print(f"WARNING: Could not reload KiCad: {e}")


if __name__ == "__main__":
    main()
