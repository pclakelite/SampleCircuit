"""
Generate and apply a patch to add 24V input protection to SampleCircuit.kicad_sch.

Adds:
  D1 (SS34) — series Schottky for reverse polarity protection
  D2 (SMBJ26CA) — TVS diode across VIN/GND for transient suppression

The +24V power symbol (#PWR01) is moved up to make room for D1 in series.
"""

import json
import os
import sys
import uuid

# Add project root to path for sch_parser
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from sch_parser import parse_schematic, extract_lib_symbols, find_matching_paren


def uid():
    return str(uuid.uuid4())


COMBINED_UUID = "f1a2b3c4-d5e6-7f89-0a1b-c2d3e4f5a6b7"


def extract_symbol_from_lib(content, sym_name):
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
    return content[start:i + 1]


def build_patch():
    """Build the patch manifest for input protection."""

    # ---------------------------------------------------------------
    # 1. Extract lib_symbols from JLCImport.kicad_sym
    # ---------------------------------------------------------------
    jlc_path = os.path.join(ROOT, "JLCImport.kicad_sym")
    with open(jlc_path, 'r', encoding='utf-8') as f:
        jlc_content = f.read()

    # Extract SS34 and SMBJ26CA symbols
    ss34_text = extract_symbol_from_lib(jlc_content, "SS34_C8678")
    smbj26ca_text = extract_symbol_from_lib(jlc_content, "SMBJ26CA_C89651")

    if not ss34_text:
        print("ERROR: SS34_C8678 not found in JLCImport.kicad_sym")
        sys.exit(1)
    if not smbj26ca_text:
        print("ERROR: SMBJ26CA_C89651 not found in JLCImport.kicad_sym")
        sys.exit(1)

    # Add JLCImport: prefix
    ss34_text = ss34_text.replace(
        '(symbol "SS34_C8678"',
        '(symbol "JLCImport:SS34_C8678"', 1)
    smbj26ca_text = smbj26ca_text.replace(
        '(symbol "SMBJ26CA_C89651"',
        '(symbol "JLCImport:SMBJ26CA_C89651"', 1)

    # Force hide pin numbers and names for passives
    import re
    for text_var in ['ss34_text', 'smbj26ca_text']:
        text = locals()[text_var]
        if '(pin_numbers' not in text:
            text = text.replace(
                '(pin_names',
                '(pin_numbers (hide yes))\n    (pin_names', 1)
        else:
            text = re.sub(r'\(pin_numbers[^)]*\)', '(pin_numbers (hide yes))', text, count=1)
        text = re.sub(
            r'\(pin_names\s*\([^)]*\)\)',
            '(pin_names (offset 1.016) (hide yes))',
            text, count=1)
        locals()[text_var]  # just to reference
        if text_var == 'ss34_text':
            ss34_text = text
        else:
            smbj26ca_text = text

    add_lib_symbols = {
        "JLCImport:SS34_C8678": ss34_text,
        "JLCImport:SMBJ26CA_C89651": smbj26ca_text,
    }

    # ---------------------------------------------------------------
    # 2. Existing positions in SampleCircuit.kicad_sch
    # ---------------------------------------------------------------
    # +24V (#PWR01) currently at (34.32, 39.37)
    # Wire 1: (34.32, 39.37) → (34.32, 43.18) — +24V down to VIN rail
    # VIN rail at Y = 43.18
    # C1 at (36.86, 52.07) — GND side pin at ~(36.86, 57.15)

    # New positions:
    # Move +24V up by 10.16mm: (34.32, 39.37) → (34.32, 29.21)
    # D1 (SS34) at center (34.32, 34.29), angle=270
    #   Anode at (34.32, 29.21) — connects to +24V
    #   Cathode at (34.32, 39.37) — existing Wire 1 connects to VIN rail
    # D2 (SMBJ26CA) at center (27.94, 49.53), angle=270
    #   Pin A at (27.94, 44.45) — VIN side
    #   Pin K at (27.94, 54.61) — GND side
    # New GND symbol at (27.94, 57.15) for D2

    # ---------------------------------------------------------------
    # 3. Find next available ref numbers from target schematic
    # ---------------------------------------------------------------
    sch_path = os.path.join(ROOT, "SampleCircuit.kicad_sch")
    with open(sch_path, 'r', encoding='utf-8') as f:
        sch_content = f.read()

    parsed = parse_schematic(sch_content)

    # Find max D and #PWR refs
    from sch_parser import get_max_ref_number
    max_d = get_max_ref_number(parsed["elements"], "D")
    max_pwr = get_max_ref_number(parsed["elements"], "#PWR")

    d1_ref = f"D{max_d + 1}"
    d2_ref = f"D{max_d + 2}"
    pwr_gnd_ref = f"#PWR{max_pwr + 1:02d}"

    print(f"  D1 reference: {d1_ref}")
    print(f"  D2 reference: {d2_ref}")
    print(f"  New GND ref: {pwr_gnd_ref}")

    # ---------------------------------------------------------------
    # 4. Build component s-expressions
    # ---------------------------------------------------------------

    # D1 — SS34 Schottky (series reverse polarity, vertical angle=270)
    d1_block = f"""(symbol
    (lib_id "JLCImport:SS34_C8678")
    (at 34.32 34.29 270)
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{uid()}")
    (property "Reference" "{d1_ref}"
      (at 38.13 34.29 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "SS34"
      (at 30.51 34.29 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "JLCImport:SS34_C8678"
      (at 34.32 34.29 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (property "Datasheet" ""
      (at 34.32 34.29 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Description" ""
      (at 34.32 34.29 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "LCSC" "C8678"
      (at 34.32 34.29 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (pin "2"
      (uuid "{uid()}")
    )
    (pin "1"
      (uuid "{uid()}")
    )
    (instances
      (project "SampleCircuit"
        (path "/{COMBINED_UUID}"
          (reference "{d1_ref}")
          (unit 1)
        )
      )
    )
  )"""

    # D2 — SMBJ26CA TVS (transient suppression, vertical angle=270)
    d2_block = f"""(symbol
    (lib_id "JLCImport:SMBJ26CA_C89651")
    (at 27.94 49.53 270)
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{uid()}")
    (property "Reference" "{d2_ref}"
      (at 31.75 49.53 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Value" "SMBJ26CA"
      (at 24.13 49.53 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" "JLCImport:SMBJ26CA_C89651"
      (at 27.94 49.53 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (property "Datasheet" ""
      (at 27.94 49.53 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Description" ""
      (at 27.94 49.53 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "LCSC" "C89651"
      (at 27.94 49.53 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (pin "2"
      (uuid "{uid()}")
    )
    (pin "1"
      (uuid "{uid()}")
    )
    (instances
      (project "SampleCircuit"
        (path "/{COMBINED_UUID}"
          (reference "{d2_ref}")
          (unit 1)
        )
      )
    )
  )"""

    # New +24V power symbol at moved position (34.32, 29.21)
    new_pwr01 = f"""(symbol
    (lib_id "power:+24V")
    (at 34.32 29.21 0)
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{uid()}")
    (property "Reference" "#PWR01"
      (at 34.32 33.02 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (property "Value" "+24V"
      (at 34.32 24.89 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" ""
      (at 34.32 29.21 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (property "Datasheet" ""
      (at 34.32 29.21 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Description" ""
      (at 34.32 29.21 0)
      (effects (font (size 1.27 1.27)))
    )
    (pin "1"
      (uuid "{uid()}")
    )
    (instances
      (project "SampleCircuit"
        (path "/{COMBINED_UUID}"
          (reference "#PWR01")
          (unit 1)
        )
      )
    )
  )"""

    # New GND power symbol for D2 at (27.94, 57.15)
    gnd_d2 = f"""(symbol
    (lib_id "power:GND")
    (at 27.94 57.15 0)
    (unit 1)
    (exclude_from_sim no)
    (in_bom yes)
    (on_board yes)
    (dnp no)
    (uuid "{uid()}")
    (property "Reference" "{pwr_gnd_ref}"
      (at 27.94 63.5 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (property "Value" "GND"
      (at 27.94 60.96 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Footprint" ""
      (at 27.94 57.15 0)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
    (property "Datasheet" ""
      (at 27.94 57.15 0)
      (effects (font (size 1.27 1.27)))
    )
    (property "Description" ""
      (at 27.94 57.15 0)
      (effects (font (size 1.27 1.27)))
    )
    (pin "1"
      (uuid "{uid()}")
    )
    (instances
      (project "SampleCircuit"
        (path "/{COMBINED_UUID}"
          (reference "{pwr_gnd_ref}")
          (unit 1)
        )
      )
    )
  )"""

    # ---------------------------------------------------------------
    # 5. Wire s-expressions
    # ---------------------------------------------------------------
    def wire(x1, y1, x2, y2):
        return f"""(wire (pts (xy {x1} {y1}) (xy {x2} {y2}))
    (stroke (width 0) (type default))
    (uuid "{uid()}")
  )"""

    wires = []

    # D2 anode to VIN rail: vertical up from D2 pin to VIN rail height
    wires.append(wire(27.94, 43.18, 27.94, 44.45))
    # D2 horizontal connection to VIN rail
    wires.append(wire(27.94, 43.18, 34.32, 43.18))
    # D2 cathode to GND symbol
    wires.append(wire(27.94, 54.61, 27.94, 57.15))

    # Junction at (34.32, 43.18) where D2 wire meets existing VIN rail
    junction = f"""(junction (at 34.32 43.18)
    (diameter 0)
    (color 0 0 0 0)
    (uuid "{uid()}")
  )"""

    # ---------------------------------------------------------------
    # 6. Assemble patch
    # ---------------------------------------------------------------
    add_elements = [d1_block, d2_block, new_pwr01, gnd_d2, junction] + wires

    # Remove old +24V symbol and old Wire 1 (+24V to VIN rail)
    # Wire 1 goes from (34.32, 39.37) to (34.32, 43.18)
    # After adding D1, D1 cathode is at (34.32, 39.37) so this wire
    # still connects cathode to VIN rail — we KEEP it.
    # We only need to remove the old +24V symbol at old position.
    remove_elements = [
        {"type": "symbol", "ref": "#PWR01"},  # old +24V at (34.32, 39.37)
    ]

    patch = {
        "description": "Add 24V input protection: D1 (SS34 Schottky) + D2 (SMBJ26CA TVS)",
        "add_lib_symbols": add_lib_symbols,
        "add_elements": add_elements,
        "remove_elements": remove_elements,
    }

    return patch


if __name__ == "__main__":
    print("Building input protection patch...")
    patch = build_patch()

    patch_path = os.path.join(ROOT, "patches", "input_protection_patch.json")
    with open(patch_path, 'w', encoding='utf-8') as f:
        json.dump(patch, f, indent=2)

    print(f"\nPatch written: {patch_path}")
    print(f"  lib_symbols to add: {len(patch['add_lib_symbols'])}")
    print(f"  elements to add: {len(patch['add_elements'])}")
    print(f"  elements to remove: {len(patch['remove_elements'])}")
    print(f"\nApply with: python patch_schematic.py SampleCircuit.kicad_sch patches/input_protection_patch.json")
