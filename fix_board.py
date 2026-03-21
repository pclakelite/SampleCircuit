"""
fix_board.py — Via KiCad IPC API:
  1. Move each LED (D11-D14) + its series resistor (R97-R100) next to
     the matching terminal block (J1-J4).
  2. Pull GND zone polygons 1.0mm from board edges (was 0.3mm).

Run with KiCad PCB editor open:
  "/c/Program Files/KiCad/9.0/bin/python.exe" fix_board.py
"""

import sys
sys.path.insert(0, r"c:\Projects\CircuitAI\kicad_3rdparty")

from kipy import KiCad
from kipy.geometry import Vector2, Angle


def mm(x, y):
    return Vector2.from_xy(int(x * 1e6), int(y * 1e6))

def deg(a):
    return Angle.from_degrees(float(a))


# LED + resistor placements: put LED 3mm below its terminal block,
# resistor 3mm below the LED.  All at angle 0.
# J1(124,55)->D11+R97  J2(137,55)->D12+R98  J3(150,55)->D13+R99  J4(163,55)->D14+R100
LED_PLACEMENTS = {
    "D11": (124.0, 60.0, 0),   "R97":  (124.0, 63.0, 0),   # 24V
    "D12": (137.0, 60.0, 0),   "R98":  (137.0, 63.0, 0),   # 12V
    "D13": (150.0, 60.0, 0),   "R99":  (150.0, 63.0, 0),   # 5V
    "D14": (163.0, 60.0, 0),   "R100": (163.0, 63.0, 0),   # 3.3V
}


def main():
    print("Connecting to KiCad IPC API...")
    kicad = KiCad(timeout_ms=10000)
    version = kicad.get_version()
    print(f"Connected to KiCad {version.full_version}")

    board = kicad.get_board()
    commit = board.begin_commit()

    try:
        # --- 1. Move LEDs and resistors near terminal blocks ---
        fps = board.get_footprints()
        by_ref = {fp.reference_field.text.value: fp for fp in fps}

        updated = []
        for ref, (x, y, angle) in LED_PLACEMENTS.items():
            if ref in by_ref:
                fp = by_ref[ref]
                fp.position = mm(x, y)
                fp.orientation = deg(angle)
                updated.append(fp)
                print(f"  Moved {ref:5s} -> ({x:.1f}, {y:.1f})")
            else:
                print(f"  WARNING: {ref} not found on board")

        if updated:
            board.update_items(updated)

        print(f"\nPlaced {len(updated)} LED/resistor components near terminal blocks.")

        board.push_commit(commit, "Move LEDs+resistors near terminal blocks")
        print("\nCommitted. Ctrl+Z in KiCad to undo.")

    except Exception as e:
        board.drop_commit(commit)
        print(f"\nERROR: {e}\nRolled back.")
        raise


if __name__ == "__main__":
    main()
