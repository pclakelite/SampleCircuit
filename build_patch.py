"""
build_patch.py — Generate a patch manifest (JSON) for adding or removing
template subcircuits from an existing KiCad 9 schematic.

Usage:
    python build_patch.py --target SampleCircuit.kicad_sch --add audio_ns4168 --offset 200,100
    python build_patch.py --target SampleCircuit.kicad_sch --remove audio_ns4168
    python build_patch.py --target SampleCircuit.kicad_sch --add psu_lmzm23601_5v --offset 120,0

Generates patch.json which can then be applied with:
    python patch_schematic.py SampleCircuit.kicad_sch patch.json
"""

import argparse
import importlib.util
import json
import os
import re
import sys
import uuid

from sch_parser import (
    parse_schematic, extract_lib_symbols, find_matching_paren,
    get_max_ref_number, identify_element
)

ROOT = os.path.dirname(os.path.abspath(__file__))
COMBINED_UUID = "f1a2b3c4-d5e6-7f89-0a1b-c2d3e4f5a6b7"


def uid():
    return str(uuid.uuid4())


def load_module(path, name):
    """Dynamically load a Python module from file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def find_template_dir(template_name):
    """Find template directory by name."""
    tpl_dir = os.path.join(ROOT, "templates", template_name)
    if os.path.isdir(tpl_dir):
        return tpl_dir
    return None


def find_build_script(template_dir):
    """Find the build_*.py script in a template directory."""
    for f in os.listdir(template_dir):
        if f.startswith("build_") and f.endswith(".py"):
            return os.path.join(template_dir, f)
    return None


def get_template_schematic(template_dir):
    """Get schematic content from a template (build or pre-built)."""
    build_script = find_build_script(template_dir)
    if build_script:
        mod = load_module(build_script, "build_template")
        sch = mod.build_schematic()
        if sch is not None:
            return sch

    # Fallback: read pre-built .kicad_sch
    for f in os.listdir(template_dir):
        if f.endswith('.kicad_sch'):
            path = os.path.join(template_dir, f)
            with open(path, 'r', encoding='utf-8') as fh:
                return fh.read()

    return None


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


def regenerate_uuids(text, keep=None):
    """Replace all UUIDs with fresh ones."""
    pat = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    return re.sub(pat, lambda m: m.group(0) if m.group(0) == keep else uid(), text)


def extract_body_text(content):
    """Get body text between lib_symbols end and sheet_instances start."""
    ls_start = content.find("(lib_symbols")
    ls_end = find_matching_paren(content, ls_start)
    si_start = content.find("(sheet_instances")
    if si_start == -1:
        si_start = content.rfind("(embedded_fonts")
    return content[ls_end + 1:si_start].strip()


def extract_body_blocks(body_text):
    """Split body text into individual top-level s-expression blocks."""
    blocks = []
    i = 0
    while i < len(body_text):
        if body_text[i] in ' \t\n\r':
            i += 1
            continue
        if body_text[i] == '(':
            end = find_matching_paren(body_text, i)
            blocks.append(body_text[i:end + 1])
            i = end + 1
        else:
            i += 1
    return blocks


def renumber_refs_in_block(block, ref_offsets):
    """Renumber reference designators in a single block.

    ref_offsets: {"U": 10, "R": 20, ...} — amount to add to each prefix.
    """
    for prefix, offset in ref_offsets.items():
        if offset == 0:
            continue
        # Match refs like U1, R3, C10 — but not inside lib_id strings
        # Match in property "Reference" values and (reference "...") in instances
        block = re.sub(
            rf'("Reference" "){re.escape(prefix)}(\d+)(")',
            lambda m, p=prefix, o=offset: f'{m.group(1)}{p}{int(m.group(2)) + o}{m.group(3)}',
            block
        )
        block = re.sub(
            rf'(\(reference "){re.escape(prefix)}(\d+)(")',
            lambda m, p=prefix, o=offset: f'{m.group(1)}{p}{int(m.group(2)) + o}{m.group(3)}',
            block
        )
    return block


def build_add_patch(template_name, dx, dy, target_sch_path):
    """Build a patch manifest to add a template subcircuit.

    Returns patch dict ready to write as JSON.
    """
    tpl_dir = find_template_dir(template_name)
    if not tpl_dir:
        print(f"ERROR: Template directory not found: templates/{template_name}")
        sys.exit(1)

    sch_content = get_template_schematic(tpl_dir)
    if not sch_content:
        print(f"ERROR: Could not get schematic for template: {template_name}")
        sys.exit(1)

    # Parse target schematic to find existing max refs
    with open(target_sch_path, 'r', encoding='utf-8') as f:
        target_content = f.read()
    target_parsed = parse_schematic(target_content)

    # Extract lib_symbols from template
    tpl_lib_syms = extract_lib_symbols(sch_content)[0]

    # Extract body and split into blocks
    body_text = extract_body_text(sch_content)

    # Replace template project references with SampleCircuit
    body_text = body_text.replace('(project "AITestProject"', '(project "SampleCircuit"')
    body_text = body_text.replace('(project "SampleBoard"', '(project "SampleCircuit"')

    # Replace any template root UUID with combined UUID
    # Find the template's root UUID from its schematic header
    root_uuid_m = re.search(r'\(uuid "([^"]+)"\)', sch_content[:500])
    if root_uuid_m:
        tpl_root_uuid = root_uuid_m.group(1)
        body_text = body_text.replace(tpl_root_uuid, COMBINED_UUID)

    # Apply coordinate offsets
    body_text = offset_body(body_text, dx, dy)

    # Split into blocks
    blocks = extract_body_blocks(body_text)

    # Find what ref prefixes the template uses and compute offsets
    ref_prefixes = ["U", "R", "C", "J", "D", "Q", "L"]
    ref_offsets = {}
    for prefix in ref_prefixes:
        target_max = get_max_ref_number(target_parsed["elements"], prefix)
        if target_max > 0:
            ref_offsets[prefix] = target_max
        # Also check the template blocks for this prefix
        tpl_has_prefix = False
        for block in blocks:
            if re.search(rf'"Reference" "{re.escape(prefix)}\d+"', block):
                tpl_has_prefix = True
                break
        if tpl_has_prefix and prefix not in ref_offsets:
            ref_offsets[prefix] = 0

    # Renumber #PWR and #PORT
    pwr_max = get_max_ref_number(target_parsed["elements"], "#PWR")
    port_max = get_max_ref_number(target_parsed["elements"], "#PORT")
    ref_offsets["#PWR"] = pwr_max
    ref_offsets["#PORT"] = port_max

    # Apply renumbering and UUID regeneration to each block
    processed_blocks = []
    for block in blocks:
        block = renumber_refs_in_block(block, ref_offsets)
        block = regenerate_uuids(block, keep=COMBINED_UUID)
        processed_blocks.append(block)

    # Filter lib_symbols — only add ones not already in target
    new_lib_syms = {}
    for name, text in tpl_lib_syms.items():
        if name not in target_parsed["lib_symbols"]:
            new_lib_syms[name] = text

    patch = {
        "description": f"Add template: {template_name} at offset ({dx}, {dy})",
        "add_lib_symbols": new_lib_syms,
        "add_elements": processed_blocks,
    }

    return patch


def build_remove_patch(template_name, target_sch_path):
    """Build a patch manifest to remove a template subcircuit.

    Uses manifest.json from the template directory to know what refs to remove.
    """
    tpl_dir = find_template_dir(template_name)
    if not tpl_dir:
        print(f"ERROR: Template directory not found: templates/{template_name}")
        sys.exit(1)

    manifest_path = os.path.join(tpl_dir, "manifest.json")
    if not os.path.exists(manifest_path):
        print(f"ERROR: No manifest.json in {tpl_dir}")
        print("  Create one with: {\"references\": [\"U1\", \"R1\", ...], \"lib_symbols\": [...]}")
        sys.exit(1)

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    refs = manifest.get("references", [])
    lib_syms = manifest.get("lib_symbols", [])

    remove_elements = [{"type": "symbol", "ref": ref} for ref in refs]

    patch = {
        "description": f"Remove template: {template_name}",
        "remove_elements": remove_elements,
        "remove_lib_symbols": lib_syms,
    }

    return patch


def main():
    parser = argparse.ArgumentParser(description="Generate patch manifest for schematic updates")
    parser.add_argument("--target", required=True, help="Target .kicad_sch file")
    parser.add_argument("--add", help="Template name to add")
    parser.add_argument("--remove", help="Template name to remove")
    parser.add_argument("--offset", default="0,0", help="X,Y offset for --add (e.g. 200,100)")
    parser.add_argument("--output", default="patch.json", help="Output patch file (default: patch.json)")
    args = parser.parse_args()

    if not args.add and not args.remove:
        print("ERROR: Must specify --add or --remove (or both)")
        sys.exit(1)

    patches = []

    if args.remove:
        patch = build_remove_patch(args.remove, args.target)
        patches.append(patch)

    if args.add:
        dx, dy = [float(x) for x in args.offset.split(",")]
        patch = build_add_patch(args.add, dx, dy, args.target)
        patches.append(patch)

    # Merge patches if both add and remove
    if len(patches) == 1:
        final_patch = patches[0]
    else:
        final_patch = {
            "description": f"Remove {args.remove} + Add {args.add}",
            "add_lib_symbols": {},
            "remove_lib_symbols": [],
            "add_elements": [],
            "remove_elements": [],
        }
        for p in patches:
            final_patch["add_lib_symbols"].update(p.get("add_lib_symbols", {}))
            final_patch["remove_lib_symbols"].extend(p.get("remove_lib_symbols", []))
            final_patch["add_elements"].extend(p.get("add_elements", []))
            final_patch["remove_elements"].extend(p.get("remove_elements", []))

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(final_patch, f, indent=2)

    print(f"Patch written: {args.output}")
    print(f"  {final_patch.get('description', '')}")
    if "add_lib_symbols" in final_patch:
        print(f"  lib_symbols to add: {len(final_patch['add_lib_symbols'])}")
    if "remove_lib_symbols" in final_patch:
        print(f"  lib_symbols to remove: {len(final_patch['remove_lib_symbols'])}")
    if "add_elements" in final_patch:
        print(f"  elements to add: {len(final_patch['add_elements'])}")
    if "remove_elements" in final_patch:
        print(f"  elements to remove: {len(final_patch['remove_elements'])}")

    print(f"\nApply with: python patch_schematic.py {args.target} {args.output}")


if __name__ == "__main__":
    main()
