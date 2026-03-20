"""Build input protection patch JSON from JLCImport.kicad_sym lib_symbols."""
import json
import os

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYM_FILE = os.path.join(PROJ, "JLCImport.kicad_sym")
OUT_FILE = os.path.join(PROJ, "patches", "input_protection.json")
PROJECT_UUID = "f1a2b3c4-d5e6-7f89-0a1b-c2d3e4f5a6b7"


def extract_symbol(content, name):
    marker = f'(symbol "{name}"'
    start = content.find(marker)
    if start == -1:
        return None
    depth = 0
    i = start
    while i < len(content):
        if content[i] == "(":
            depth += 1
        elif content[i] == ")":
            depth -= 1
            if depth == 0:
                return content[start : i + 1]
        i += 1
    return None


def main():
    with open(SYM_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    ss34 = extract_symbol(content, "SS34_C8678")
    smbj26 = extract_symbol(content, "SMBJ26CA_C89651")
    assert ss34, "SS34_C8678 not found in JLCImport.kicad_sym"
    assert smbj26, "SMBJ26CA_C89651 not found in JLCImport.kicad_sym"

    # Rename top-level symbol to include library prefix (required in .kicad_sch format)
    # Sub-symbols (e.g. SS34_C8678_0_1) must keep their bare name
    ss34 = ss34.replace('(symbol "SS34_C8678"', '(symbol "JLCImport:SS34_C8678"', 1)
    smbj26 = smbj26.replace('(symbol "SMBJ26CA_C89651"', '(symbol "JLCImport:SMBJ26CA_C89651"', 1)

    # Hide pin names (K/A visible otherwise)
    ss34 = ss34.replace('(pin_names (offset 1.016))', '(pin_names (offset 1.016) (hide yes))')
    smbj26 = smbj26.replace('(pin_names (offset 1.016))', '(pin_names (offset 1.016) (hide yes))')

    # D9 (SS34) at (34.32, 34.29) rotated 270 — series Schottky
    # Pin 2 (A) at top (34.32, 29.21), Pin 1 (K) at bottom (34.32, 39.37)
    d9 = (
        "(symbol\n"
        '\t\t(lib_id "JLCImport:SS34_C8678")\n'
        "\t\t(at 34.32 34.29 270)\n"
        "\t\t(unit 1)\n"
        "\t\t(exclude_from_sim no)\n"
        "\t\t(in_bom yes)\n"
        "\t\t(on_board yes)\n"
        "\t\t(dnp no)\n"
        '\t\t(uuid "c01f8514-a231-488c-a319-c3ee560c669a")\n'
        '\t\t(property "Reference" "D9"\n'
        "\t\t\t(at 38.13 34.29 0)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n"
        "\t\t)\n"
        '\t\t(property "Value" "SS34"\n'
        "\t\t\t(at 30.51 34.29 0)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n"
        "\t\t)\n"
        '\t\t(property "Footprint" "JLCImport:SS34_C8678"\n'
        "\t\t\t(at 34.32 34.29 0)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(hide yes)\n\t\t\t)\n"
        "\t\t)\n"
        '\t\t(property "Datasheet" ""\n'
        "\t\t\t(at 34.32 34.29 0)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n"
        "\t\t)\n"
        '\t\t(property "Description" ""\n'
        "\t\t\t(at 34.32 34.29 0)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n"
        "\t\t)\n"
        '\t\t(property "LCSC" "C8678"\n'
        "\t\t\t(at 34.32 34.29 0)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(hide yes)\n\t\t\t)\n"
        "\t\t)\n"
        '\t\t(pin "2"\n'
        '\t\t\t(uuid "c3a99707-ccef-442c-9b69-e17655abe1d5")\n'
        "\t\t)\n"
        '\t\t(pin "1"\n'
        '\t\t\t(uuid "867682fc-fb4c-484b-85f8-82054adebea5")\n'
        "\t\t)\n"
        "\t\t(instances\n"
        '\t\t\t(project "SampleCircuit"\n'
        f'\t\t\t\t(path "/{PROJECT_UUID}"\n'
        '\t\t\t\t\t(reference "D9")\n'
        "\t\t\t\t\t(unit 1)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        "\t)"
    )

    # D10 (SMBJ26CA) at (27.94, 49.53) rotated 270 — TVS across VIN/GND
    d10 = (
        "(symbol\n"
        '\t\t(lib_id "JLCImport:SMBJ26CA_C89651")\n'
        "\t\t(at 27.94 49.53 270)\n"
        "\t\t(unit 1)\n"
        "\t\t(exclude_from_sim no)\n"
        "\t\t(in_bom yes)\n"
        "\t\t(on_board yes)\n"
        "\t\t(dnp no)\n"
        '\t\t(uuid "c279b630-8163-4c0c-a491-4461199f92af")\n'
        '\t\t(property "Reference" "D10"\n'
        "\t\t\t(at 31.75 49.53 0)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n"
        "\t\t)\n"
        '\t\t(property "Value" "SMBJ26CA"\n'
        "\t\t\t(at 24.13 49.53 0)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n"
        "\t\t)\n"
        '\t\t(property "Footprint" "JLCImport:SMBJ26CA_C89651"\n'
        "\t\t\t(at 27.94 49.53 0)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(hide yes)\n\t\t\t)\n"
        "\t\t)\n"
        '\t\t(property "Datasheet" ""\n'
        "\t\t\t(at 27.94 49.53 0)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n"
        "\t\t)\n"
        '\t\t(property "Description" ""\n'
        "\t\t\t(at 27.94 49.53 0)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n"
        "\t\t)\n"
        '\t\t(property "LCSC" "C89651"\n'
        "\t\t\t(at 27.94 49.53 0)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(hide yes)\n\t\t\t)\n"
        "\t\t)\n"
        '\t\t(pin "2"\n'
        '\t\t\t(uuid "56927061-240f-4dce-99d3-04ea1b8c8009")\n'
        "\t\t)\n"
        '\t\t(pin "1"\n'
        '\t\t\t(uuid "ab459cb8-2f7e-4373-a3bb-3d19557f42a1")\n'
        "\t\t)\n"
        "\t\t(instances\n"
        '\t\t\t(project "SampleCircuit"\n'
        f'\t\t\t\t(path "/{PROJECT_UUID}"\n'
        '\t\t\t\t\t(reference "D10")\n'
        "\t\t\t\t\t(unit 1)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        "\t)"
    )

    # Move +24V power symbol up to make room for D9
    pwr01_new = (
        "(symbol\n"
        '\t\t(lib_id "power:+24V")\n'
        "\t\t(at 34.32 29.21 0)\n"
        "\t\t(unit 1)\n"
        "\t\t(exclude_from_sim no)\n"
        "\t\t(in_bom yes)\n"
        "\t\t(on_board yes)\n"
        "\t\t(dnp no)\n"
        '\t\t(uuid "849fbdbb-a4ff-41f6-ae0e-f15087ae4882")\n'
        '\t\t(property "Reference" "#PWR01"\n'
        "\t\t\t(at 34.32 33.02 0)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(hide yes)\n\t\t\t)\n"
        "\t\t)\n"
        '\t\t(property "Value" "+24V"\n'
        "\t\t\t(at 34.32 24.89 0)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n"
        "\t\t)\n"
        '\t\t(property "Footprint" ""\n'
        "\t\t\t(at 34.32 29.21 0)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(hide yes)\n\t\t\t)\n"
        "\t\t)\n"
        '\t\t(property "Datasheet" ""\n'
        "\t\t\t(at 34.32 29.21 0)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n"
        "\t\t)\n"
        '\t\t(property "Description" ""\n'
        "\t\t\t(at 34.32 29.21 0)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n"
        "\t\t)\n"
        '\t\t(pin "1"\n'
        '\t\t\t(uuid "9347e818-b563-48bb-9982-b420d9c9f0f7")\n'
        "\t\t)\n"
        "\t\t(instances\n"
        '\t\t\t(project "SampleCircuit"\n'
        f'\t\t\t\t(path "/{PROJECT_UUID}"\n'
        '\t\t\t\t\t(reference "#PWR01")\n'
        "\t\t\t\t\t(unit 1)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        "\t)"
    )

    # GND for D10
    gnd104 = (
        "(symbol\n"
        '\t\t(lib_id "power:GND")\n'
        "\t\t(at 27.94 57.15 0)\n"
        "\t\t(unit 1)\n"
        "\t\t(exclude_from_sim no)\n"
        "\t\t(in_bom yes)\n"
        "\t\t(on_board yes)\n"
        "\t\t(dnp no)\n"
        '\t\t(uuid "3470873f-e68e-42b0-b32b-36910bad1d52")\n'
        '\t\t(property "Reference" "#PWR104"\n'
        "\t\t\t(at 27.94 63.5 0)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(hide yes)\n\t\t\t)\n"
        "\t\t)\n"
        '\t\t(property "Value" "GND"\n'
        "\t\t\t(at 27.94 60.96 0)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n"
        "\t\t)\n"
        '\t\t(property "Footprint" ""\n'
        "\t\t\t(at 27.94 57.15 0)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(hide yes)\n\t\t\t)\n"
        "\t\t)\n"
        '\t\t(property "Datasheet" ""\n'
        "\t\t\t(at 27.94 57.15 0)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n"
        "\t\t)\n"
        '\t\t(property "Description" ""\n'
        "\t\t\t(at 27.94 57.15 0)\n"
        "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n"
        "\t\t)\n"
        '\t\t(pin "1"\n'
        '\t\t\t(uuid "18a91f7d-56e3-4d8f-84a5-5b0e7f1e3fc1")\n'
        "\t\t)\n"
        "\t\t(instances\n"
        '\t\t\t(project "SampleCircuit"\n'
        f'\t\t\t\t(path "/{PROJECT_UUID}"\n'
        '\t\t\t\t\t(reference "#PWR104")\n'
        "\t\t\t\t\t(unit 1)\n"
        "\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        "\t)"
    )

    def wire(x1, y1, x2, y2, uuid):
        return (
            f"(wire\n\t\t(pts\n\t\t\t(xy {x1} {y1}) (xy {x2} {y2})\n\t\t)\n"
            f"\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n"
            f'\t\t(uuid "{uuid}")\n\t)'
        )

    def junction(x, y, uuid):
        return (
            f"(junction\n\t\t(at {x} {y})\n\t\t(diameter 0)\n"
            f'\t\t(color 0 0 0 0)\n\t\t(uuid "{uuid}")\n\t)'
        )

    patch = {
        "description": "Add 24V input protection: D9 (SS34 Schottky) + D10 (SMBJ26CA TVS)",
        "add_lib_symbols": {
            "JLCImport:SS34_C8678": ss34,
            "JLCImport:SMBJ26CA_C89651": smbj26,
        },
        "replace_elements": [
            {"match": {"type": "symbol", "ref": "#PWR01"}, "with": pwr01_new}
        ],
        "remove_elements": [
            {"type": "wire", "endpoints": [[34.32, 39.37], [34.32, 43.18]]}
        ],
        "add_elements": [
            d9,
            # Wire from D9 bottom (K at 39.37) to VIN rail at 43.18
            wire(34.32, 39.37, 34.32, 43.18, "0f9ba501-da0f-44f7-a133-2cd484a7ef0d"),
            d10,
            gnd104,
            # Junction at VIN rail where TVS taps in
            junction(34.32, 43.18, "44c454dd-6126-4a67-a461-7eef99bb62dc"),
            # Wire from TVS top pin down to VIN rail level
            wire(27.94, 43.18, 27.94, 44.45, "0f9ba500-da0f-44f7-a133-2cd484a7ef0c"),
            # Horizontal wire connecting TVS to VIN rail
            wire(27.94, 43.18, 34.32, 43.18, "99228597-3fca-410d-a33c-ad3228791363"),
            # Wire from TVS bottom pin to GND
            wire(27.94, 54.61, 27.94, 57.15, "99fbce43-2589-4817-b06b-ef8ca0356a40"),
        ],
    }

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(patch, f, indent=2, ensure_ascii=False)
    print(f"Patch written: {OUT_FILE}")


if __name__ == "__main__":
    main()
