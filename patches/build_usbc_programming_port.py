"""Build patch to add USB-C programming port for ESP32-S3.

Components:
  USB1 — TYPE-C_16PIN_2MD_073 connector (C2765186)
  R95  — 5.1k CC1 pulldown (C27834)
  R96  — 5.1k CC2 pulldown (C27834)

Connections:
  DP1/DP2 → UD+ (ESP32 IO20)
  DN1/DN2 → UD- (ESP32 IO19)
  CC1 → R95 → GND
  CC2 → R96 → GND
  VBUS → +5V
  GND/SHELL → GND
  SBU1/SBU2 → no connect
"""
import json
import os
import re

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYM_FILE = os.path.join(PROJ, "JLCImport.kicad_sym")
OUT_FILE = os.path.join(PROJ, "patches", "usbc_programming_port.json")
PROJECT_UUID = "f1a2b3c4-d5e6-7f89-0a1b-c2d3e4f5a6b7"

# Connector placement — center of USB-C symbol
CX, CY = 175.0, 95.0

# Pin offsets from connector center (pins exit left at x - 11.43)
PIN_X = CX - 11.43  # ≈ 163.57
PIN_OFFSETS_Y = {
    1: -13.97,   # GND
    2: -11.43,   # VBUS
    3: -8.89,    # SBU2
    4: -6.35,    # CC1
    5: -3.81,    # DN2
    6: -1.27,    # DP1
    7: 1.27,     # DN1
    8: 3.81,     # DP2
    9: 6.35,     # SBU1
    10: 8.89,    # CC2
    11: 11.43,   # VBUS
    12: 13.97,   # GND
}
# Shell pins exit right side
SHELL_X = CX + 10.16
SHELL_13_Y = CY + 13.97
SHELL_14_Y = CY - 13.97


def pin_y(pin_num):
    return CY + PIN_OFFSETS_Y[pin_num]


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


def prepare_lib_symbol(text, bare_name):
    """Transform .kicad_sym lib_symbol for .kicad_sch embedding."""
    # Prefix top-level symbol name with JLCImport:
    text = text.replace(
        f'(symbol "{bare_name}"',
        f'(symbol "JLCImport:{bare_name}"',
        1,
    )
    # Hide pin names
    text = text.replace(
        "(pin_names (offset 1.016))",
        "(pin_names (offset 1.016) (hide yes))",
    )
    return text


def symbol(lib_id, x, y, rot, uuid, ref, value, footprint, lcsc, pins, extra_props=""):
    """Build a component symbol s-expression."""
    pin_lines = ""
    for pnum, puuid in pins:
        pin_lines += f'\t\t(pin "{pnum}"\n\t\t\t(uuid "{puuid}")\n\t\t)\n'

    return (
        f"(symbol\n"
        f'\t\t(lib_id "{lib_id}")\n'
        f"\t\t(at {x} {y} {rot})\n"
        f"\t\t(unit 1)\n"
        f"\t\t(exclude_from_sim no)\n"
        f"\t\t(in_bom yes)\n"
        f"\t\t(on_board yes)\n"
        f"\t\t(dnp no)\n"
        f'\t\t(uuid "{uuid}")\n'
        f'\t\t(property "Reference" "{ref}"\n'
        f"\t\t\t(at {x + 3} {y} 0)\n"
        f"\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n"
        f"\t\t)\n"
        f'\t\t(property "Value" "{value}"\n'
        f"\t\t\t(at {x - 3} {y} 0)\n"
        f"\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n"
        f"\t\t)\n"
        f'\t\t(property "Footprint" "{footprint}"\n'
        f"\t\t\t(at {x} {y} 0)\n"
        f"\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(hide yes)\n\t\t\t)\n"
        f"\t\t)\n"
        f'\t\t(property "Datasheet" ""\n'
        f"\t\t\t(at {x} {y} 0)\n"
        f"\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n"
        f"\t\t)\n"
        f'\t\t(property "Description" ""\n'
        f"\t\t\t(at {x} {y} 0)\n"
        f"\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n"
        f"\t\t)\n"
        f'\t\t(property "LCSC" "{lcsc}"\n'
        f"\t\t\t(at {x} {y} 0)\n"
        f"\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(hide yes)\n\t\t\t)\n"
        f"\t\t)\n"
        f"{extra_props}"
        f"{pin_lines}"
        f"\t\t(instances\n"
        f'\t\t\t(project "SampleCircuit"\n'
        f'\t\t\t\t(path "/{PROJECT_UUID}"\n'
        f'\t\t\t\t\t(reference "{ref}")\n'
        f"\t\t\t\t\t(unit 1)\n"
        f"\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        f"\t)"
    )


_uuid_counter = 0

def next_uuid(prefix="cc"):
    """Generate a unique UUID for each call."""
    global _uuid_counter
    _uuid_counter += 1
    return f"{prefix}{_uuid_counter:06d}-0000-4000-8000-{_uuid_counter:012d}"


def pwr_symbol(lib_id, x, y, uuid, ref, value, rot=0):
    """Build a power symbol (GND, +5V, +3.3V)."""
    pin_uuid = next_uuid("dd")
    hide_offset_y = y + 3.81 if "GND" in value else y - 3.81
    return (
        f"(symbol\n"
        f'\t\t(lib_id "{lib_id}")\n'
        f"\t\t(at {x} {y} {rot})\n"
        f"\t\t(unit 1)\n"
        f"\t\t(exclude_from_sim no)\n"
        f"\t\t(in_bom yes)\n"
        f"\t\t(on_board yes)\n"
        f"\t\t(dnp no)\n"
        f'\t\t(uuid "{uuid}")\n'
        f'\t\t(property "Reference" "{ref}"\n'
        f"\t\t\t(at {x} {hide_offset_y} 0)\n"
        f"\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(hide yes)\n\t\t\t)\n"
        f"\t\t)\n"
        f'\t\t(property "Value" "{value}"\n'
        f"\t\t\t(at {x} {y + (3.81 if 'GND' in value else -3.81)} 0)\n"
        f"\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n"
        f"\t\t)\n"
        f'\t\t(property "Footprint" ""\n'
        f"\t\t\t(at {x} {y} 0)\n"
        f"\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(hide yes)\n\t\t\t)\n"
        f"\t\t)\n"
        f'\t\t(property "Datasheet" ""\n'
        f"\t\t\t(at {x} {y} 0)\n"
        f"\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n"
        f"\t\t)\n"
        f'\t\t(property "Description" ""\n'
        f"\t\t\t(at {x} {y} 0)\n"
        f"\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n"
        f"\t\t)\n"
        f'\t\t(pin "1"\n'
        f'\t\t\t(uuid "{pin_uuid}")\n'
        f"\t\t)\n"
        f"\t\t(instances\n"
        f'\t\t\t(project "SampleCircuit"\n'
        f'\t\t\t\t(path "/{PROJECT_UUID}"\n'
        f'\t\t\t\t\t(reference "{ref}")\n'
        f"\t\t\t\t\t(unit 1)\n"
        f"\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        f"\t)"
    )


def port_symbol(lib_id, x, y, uuid, ref, value, rot=0):
    """Build a port symbol (UD+, UD-)."""
    pin_uuid = next_uuid("ee")
    return (
        f"(symbol\n"
        f'\t\t(lib_id "{lib_id}")\n'
        f"\t\t(at {x} {y} {rot})\n"
        f"\t\t(unit 1)\n"
        f"\t\t(exclude_from_sim no)\n"
        f"\t\t(in_bom yes)\n"
        f"\t\t(on_board yes)\n"
        f"\t\t(dnp no)\n"
        f'\t\t(uuid "{uuid}")\n'
        f'\t\t(property "Reference" "{ref}"\n'
        f"\t\t\t(at {x} {y} 0)\n"
        f"\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(hide yes)\n\t\t\t)\n"
        f"\t\t)\n"
        f'\t\t(property "Value" "{value}"\n'
        f"\t\t\t(at {x - 4} {y} 0)\n"
        f"\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n"
        f"\t\t)\n"
        f'\t\t(property "Footprint" ""\n'
        f"\t\t\t(at {x} {y} 0)\n"
        f"\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(hide yes)\n\t\t\t)\n"
        f"\t\t)\n"
        f'\t\t(property "Datasheet" ""\n'
        f"\t\t\t(at {x} {y} 0)\n"
        f"\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n"
        f"\t\t)\n"
        f'\t\t(property "Description" ""\n'
        f"\t\t\t(at {x} {y} 0)\n"
        f"\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n"
        f"\t\t)\n"
        f'\t\t(pin "1"\n'
        f'\t\t\t(uuid "{pin_uuid}")\n'
        f"\t\t)\n"
        f"\t\t(instances\n"
        f'\t\t\t(project "SampleCircuit"\n'
        f'\t\t\t\t(path "/{PROJECT_UUID}"\n'
        f'\t\t\t\t\t(reference "{ref}")\n'
        f"\t\t\t\t\t(unit 1)\n"
        f"\t\t\t\t)\n\t\t\t)\n\t\t)\n"
        f"\t)"
    )


def wire(x1, y1, x2, y2, uuid):
    return (
        f"(wire\n\t\t(pts\n\t\t\t(xy {x1} {y1}) (xy {x2} {y2})\n\t\t)\n"
        f"\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n"
        f'\t\t(uuid "{uuid}")\n\t)'
    )


def no_connect(x, y, uuid):
    return (
        f"(no_connect\n\t\t(at {x} {y})\n"
        f'\t\t(uuid "{uuid}")\n\t)'
    )


def junction(x, y, uuid):
    return (
        f"(junction\n\t\t(at {x} {y})\n\t\t(diameter 0)\n"
        f'\t\t(color 0 0 0 0)\n\t\t(uuid "{uuid}")\n\t)'
    )


def main():
    with open(SYM_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    usbc_sym = extract_symbol(content, "TYPE-C_16PIN_2MD_073")
    r5k1_sym = extract_symbol(content, "0805W8F5101T5E")
    assert usbc_sym, "TYPE-C_16PIN_2MD_073 not found"
    assert r5k1_sym, "0805W8F5101T5E not found"

    usbc_sym = prepare_lib_symbol(usbc_sym, "TYPE-C_16PIN_2MD_073")
    r5k1_sym = prepare_lib_symbol(r5k1_sym, "0805W8F5101T5E")

    elements = []

    # --- USB-C connector (USB1) ---
    usb_pins = [
        ("1", "bb110001-1111-4111-8111-111111110001"),
        ("2", "bb110001-1111-4111-8111-111111110002"),
        ("3", "bb110001-1111-4111-8111-111111110003"),
        ("4", "bb110001-1111-4111-8111-111111110004"),
        ("5", "bb110001-1111-4111-8111-111111110005"),
        ("6", "bb110001-1111-4111-8111-111111110006"),
        ("7", "bb110001-1111-4111-8111-111111110007"),
        ("8", "bb110001-1111-4111-8111-111111110008"),
        ("9", "bb110001-1111-4111-8111-111111110009"),
        ("10", "bb110001-1111-4111-8111-111111110010"),
        ("11", "bb110001-1111-4111-8111-111111110011"),
        ("12", "bb110001-1111-4111-8111-111111110012"),
        ("13", "bb110001-1111-4111-8111-111111110013"),
        ("14", "bb110001-1111-4111-8111-111111110014"),
    ]
    elements.append(
        symbol(
            "JLCImport:TYPE-C_16PIN_2MD_073", CX, CY, 0,
            "bb110001-0000-4000-8000-000000000001",
            "USB1", "TYPE-C", "JLCImport:TYPE-C_16PIN_2MD_073", "C2765186",
            usb_pins,
        )
    )

    WX = PIN_X  # pin exit x ≈ 163.57

    # === DATA LINES (individual port labels — no crossing wires) ===
    # Pins are interleaved (5=DN2, 6=DP1, 7=DN1, 8=DP2) so joining
    # with wires causes shorts. Use separate port labels instead;
    # KiCad connects same-name ports automatically.

    port_stub_x = 155.0  # short stub wire endpoint

    # DP1 (pin 6) → UD+
    elements.append(wire(WX, pin_y(6), port_stub_x, pin_y(6), "bb220001-0001-4001-8001-000000000001"))
    elements.append(
        port_symbol("Ports:UD+", port_stub_x, pin_y(6),
                     "bb440001-0001-4001-8001-000000000001", "#PORT119", "UD+", 180)
    )

    # DN2 (pin 5) → UD-
    elements.append(wire(WX, pin_y(5), port_stub_x, pin_y(5), "bb220001-0002-4001-8001-000000000001"))
    elements.append(
        port_symbol("Ports:UD-", port_stub_x, pin_y(5),
                     "bb440001-0002-4001-8001-000000000001", "#PORT120", "UD-", 180)
    )

    # DN1 (pin 7) → UD-
    elements.append(wire(WX, pin_y(7), port_stub_x, pin_y(7), "bb220001-0002-4001-8001-000000000002"))
    elements.append(
        port_symbol("Ports:UD-", port_stub_x, pin_y(7),
                     "bb440001-0002-4001-8001-000000000002", "#PORT121", "UD-", 180)
    )

    # DP2 (pin 8) → UD+
    elements.append(wire(WX, pin_y(8), port_stub_x, pin_y(8), "bb220001-0001-4001-8001-000000000002"))
    elements.append(
        port_symbol("Ports:UD+", port_stub_x, pin_y(8),
                     "bb440001-0001-4001-8001-000000000002", "#PORT122", "UD+", 180)
    )

    # === CC RESISTORS (vertical, dropping down from CC pins) ===

    # CC1 (pin 4, y=88.65) → wire down → R95 vertical → GND
    cc1_y = pin_y(4)
    r95_x = WX - 5.08  # resistor center left of pin, at 158.49
    r95_y = cc1_y - 8.0  # above pin
    elements.append(wire(WX, cc1_y, r95_x, cc1_y, "bb220001-0003-4001-8001-000000000001"))
    elements.append(wire(r95_x, cc1_y, r95_x, r95_y + 5.08, "bb220001-0003-4001-8001-000000000003"))
    elements.append(
        symbol(
            "JLCImport:0805W8F5101T5E", r95_x, r95_y, 90,
            "bb110001-0003-4000-8000-000000000001",
            "R95", "5.1k", "JLCImport:0805W8F5101T5E", "C27834",
            [("1", "bb110001-0003-4000-8000-000000000011"),
             ("2", "bb110001-0003-4000-8000-000000000012")],
        )
    )
    elements.append(
        pwr_symbol("power:GND", r95_x, r95_y - 5.08,
                    "bb550001-0003-4001-8001-000000000001", "#PWR107", "GND", rot=180)
    )

    # CC2 (pin 10, y=103.89) → wire down → R96 vertical → GND
    cc2_y = pin_y(10)
    r96_x = WX - 5.08
    r96_y = cc2_y + 8.0  # below pin
    elements.append(wire(WX, cc2_y, r96_x, cc2_y, "bb220001-0004-4001-8001-000000000001"))
    elements.append(wire(r96_x, cc2_y, r96_x, r96_y - 5.08, "bb220001-0004-4001-8001-000000000003"))
    elements.append(
        symbol(
            "JLCImport:0805W8F5101T5E", r96_x, r96_y, 90,
            "bb110001-0004-4000-8000-000000000001",
            "R96", "5.1k", "JLCImport:0805W8F5101T5E", "C27834",
            [("1", "bb110001-0004-4000-8000-000000000011"),
             ("2", "bb110001-0004-4000-8000-000000000012")],
        )
    )
    elements.append(wire(r96_x, r96_y + 5.08, r96_x, r96_y + 7.62, "bb220001-0004-4001-8001-000000000004"))
    elements.append(
        pwr_symbol("power:GND", r96_x, r96_y + 7.62,
                    "bb550001-0004-4001-8001-000000000001", "#PWR108", "GND")
    )

    # === POWER: VBUS pins 2 & 11 → +5V ===
    # Pin 2 (VBUS, y=83.57) — wire left, +5V above
    vbus_x = 148.0
    elements.append(wire(WX, pin_y(2), vbus_x, pin_y(2), "bb220001-0005-4001-8001-000000000001"))
    elements.append(wire(vbus_x, pin_y(2), vbus_x, pin_y(2) - 5.08, "bb220001-0005-4001-8001-000000000002"))
    elements.append(
        pwr_symbol("power:+5V", vbus_x, pin_y(2) - 5.08,
                    "bb550001-0005-4001-8001-000000000001", "#PWR109", "+5V")
    )
    # Pin 11 (VBUS, y=106.43) — wire to same net via vertical
    elements.append(wire(WX, pin_y(11), vbus_x, pin_y(11), "bb220001-0006-4001-8001-000000000001"))
    elements.append(wire(vbus_x, pin_y(2), vbus_x, pin_y(11), "bb220001-0006-4001-8001-000000000002"))
    elements.append(junction(vbus_x, pin_y(2), "bb330001-0005-4001-8001-000000000001"))

    # === GND: pins 1 & 12 ===
    # Pin 1 (GND, y=81.03) — wire left, GND above
    gnd_x = 143.0
    elements.append(wire(WX, pin_y(1), gnd_x, pin_y(1), "bb220001-0007-4001-8001-000000000001"))
    elements.append(wire(gnd_x, pin_y(1), gnd_x, pin_y(1) - 5.08, "bb220001-0007-4001-8001-000000000002"))
    elements.append(
        pwr_symbol("power:GND", gnd_x, pin_y(1) - 5.08,
                    "bb550001-0007-4001-8001-000000000001", "#PWR110", "GND", rot=180)
    )
    # Pin 12 (GND, y=108.97) — wire left, GND below
    elements.append(wire(WX, pin_y(12), gnd_x, pin_y(12), "bb220001-0008-4001-8001-000000000001"))
    elements.append(wire(gnd_x, pin_y(12), gnd_x, pin_y(12) + 5.08, "bb220001-0008-4001-8001-000000000002"))
    elements.append(
        pwr_symbol("power:GND", gnd_x, pin_y(12) + 5.08,
                    "bb550001-0008-4001-8001-000000000001", "#PWR111", "GND")
    )

    # === SHELL pins 13 & 14 → GND ===
    elements.append(wire(SHELL_X, SHELL_13_Y, SHELL_X, SHELL_13_Y + 5.08, "bb220001-0009-4001-8001-000000000001"))
    elements.append(
        pwr_symbol("power:GND", SHELL_X, SHELL_13_Y + 5.08,
                    "bb550001-0009-4001-8001-000000000001", "#PWR112", "GND")
    )
    elements.append(wire(SHELL_X, SHELL_14_Y, SHELL_X, SHELL_14_Y - 5.08, "bb220001-0010-4001-8001-000000000001"))
    elements.append(
        pwr_symbol("power:GND", SHELL_X, SHELL_14_Y - 5.08,
                    "bb550001-0010-4001-8001-000000000001", "#PWR113", "GND", rot=180)
    )

    # === No connects: SBU1 (pin 9), SBU2 (pin 3) ===
    elements.append(no_connect(WX, pin_y(3), "bb660001-0001-4001-8001-000000000001"))
    elements.append(no_connect(WX, pin_y(9), "bb660001-0002-4001-8001-000000000001"))

    patch = {
        "description": "Add USB-C programming port for ESP32-S3 (USB1, R95, R96)",
        "add_lib_symbols": {
            "JLCImport:TYPE-C_16PIN_2MD_073": usbc_sym,
            "JLCImport:0805W8F5101T5E": r5k1_sym,
        },
        "add_elements": elements,
    }

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(patch, f, indent=2, ensure_ascii=False)
    print(f"Patch written: {OUT_FILE}")
    print(f"  Elements: {len(elements)}")


if __name__ == "__main__":
    main()
