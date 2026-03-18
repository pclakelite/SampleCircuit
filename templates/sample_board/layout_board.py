"""
layout_board.py — Use KiCad IPC API (kipy) to lay out the SampleBoard PCB.

Creates a 4" x 4" (101.6mm x 101.6mm) board outline and places all
components in functional groups:
  Top-left:     PSU 12V->5V  (U6 + passives)
  Top-right:    PSU 12V->3.3V (U5 + D8 + passives)
  Bottom-left:  RTC (U8 + B3 + passives)
  Bottom-right: Audio (U4 + passives)

Prerequisites:
  1. KiCad PCB editor must be running with SampleBoard.kicad_pcb open
  2. "Update PCB from Schematic" must have been run first (components imported)
  3. KiCad API must be enabled (Preferences -> Plugins -> Enable KiCad API)

Run with KiCad's Python:
  PYTHONPATH="c:/Projects/CircuitAI/kicad_3rdparty" "/c/Program Files/KiCad/9.0/bin/python.exe" layout_board.py
"""

import sys
sys.path.insert(0, r"c:\Projects\CircuitAI\kicad_3rdparty")

from kipy import KiCad
from kipy.board_types import BoardLayer, BoardRectangle
from kipy.geometry import Vector2, Angle

# ==============================================================
# BOARD DIMENSIONS
# ==============================================================
# 4" x 4" = 101.6mm x 101.6mm
# Board origin at (100mm, 50mm) — standard KiCad offset
BOARD_X = 100.0   # mm, left edge
BOARD_Y = 50.0    # mm, top edge
BOARD_W = 101.6   # mm (4 inches)
BOARD_H = 101.6   # mm (4 inches)

# Center of board
CX = BOARD_X + BOARD_W / 2   # 150.8
CY = BOARD_Y + BOARD_H / 2   # 100.8


def mm_pos(x_mm, y_mm):
    """Convert mm coordinates to KiCad nanometer Vector2."""
    return Vector2.from_xy(int(x_mm * 1e6), int(y_mm * 1e6))


def deg(angle):
    """Create Angle from degrees."""
    return Angle.from_degrees(float(angle))


# ==============================================================
# COMPONENT PLACEMENTS (ref -> (x_mm, y_mm, angle_deg))
# Grouped by functional block on the 4x4" board
# ==============================================================

# PSU 5V — top-left quadrant (center ~125, 75)
PSU_5V = {
    "U6":  (125.0,  72.0,  0),    # LMZM23601 — main IC
    "C31": (112.0,  72.0,  0),    # 10uF input cap #1
    "C33": (112.0,  78.0,  0),    # 10uF input cap #2
    "C32": (138.0,  78.0,  0),    # 47uF output cap
    "R3":  (138.0,  68.0, 90),    # 10k feedback top
    "R4":  (142.0,  78.0, 90),    # 2.49k feedback bottom
}

# PSU 3.3V — top-right quadrant (center ~175, 75)
PSU_3V3 = {
    "U5":  (175.0,  72.0,  0),    # LMZM23601 — main IC
    "D8":  (160.0,  72.0,  0),    # PMEG6030 input protection diode
    "C11": (162.0,  82.0,  0),    # 680uF electrolytic input
    "C34": (168.0,  82.0,  0),    # 10uF ceramic input
    "C35": (188.0,  82.0,  0),    # 47uF output cap
    "R31": (188.0,  68.0, 90),    # 10k feedback top
    "R32": (192.0,  78.0, 90),    # 4.22k feedback bottom
}

# RTC — bottom-left quadrant (center ~125, 125)
RTC = {
    "U8":  (120.0, 120.0,   0),   # RV-3028-C7
    "C10": (132.0, 120.0,   0),   # 100nF VBACKUP decoupling
    "R41": (132.0, 114.0,   0),   # 10k EVI pull-down
    "R46": (138.0, 120.0,  90),   # 1k VBACKUP series
    "B3":  (112.0, 130.0,   0),   # CR1220 battery holder
}

# Audio — bottom-right quadrant (center ~175, 125)
AUDIO = {
    "U4":  (175.0, 120.0,   0),   # MAX98357A
    "R7":  (162.0, 114.0,  90),   # 100k GAIN_SLOT
    "R6":  (162.0, 120.0,  90),   # 1M SD_MODE
    "C15": (162.0, 130.0,   0),   # 10uF bulk decoupling
    "C16": (168.0, 130.0,   0),   # 100nF decoupling
}

# Combine all placements
ALL_PLACEMENTS = {}
ALL_PLACEMENTS.update(PSU_5V)
ALL_PLACEMENTS.update(PSU_3V3)
ALL_PLACEMENTS.update(RTC)
ALL_PLACEMENTS.update(AUDIO)


def main():
    print("Connecting to KiCad IPC API...")
    try:
        kicad = KiCad(timeout_ms=10000)
    except Exception as e:
        print(f"ERROR: Could not connect to KiCad: {e}")
        print("Make sure KiCad PCB editor is running with the API enabled.")
        print("(Preferences -> Plugins -> Enable KiCad API)")
        sys.exit(1)

    version = kicad.get_version()
    print(f"Connected to KiCad {version.full_version}")

    try:
        board = kicad.get_board()
    except Exception as e:
        print(f"ERROR: Could not get board: {e}")
        print("Make sure the PCB editor is open (not just the project manager).")
        sys.exit(1)

    # Start a commit so all changes are one undo step
    commit = board.begin_commit()

    try:
        # ==============================================================
        # 1. CREATE BOARD OUTLINE (4" x 4")
        # ==============================================================
        print(f"\nCreating board outline: {BOARD_W}mm x {BOARD_H}mm ({BOARD_W/25.4:.1f}\" x {BOARD_H/25.4:.1f}\")")

        # Remove any existing outline
        shapes = board.get_shapes()
        edge_cuts = [s for s in shapes if s.layer == BoardLayer.BL_Edge_Cuts]
        if edge_cuts:
            print(f"  Removing {len(edge_cuts)} existing Edge.Cuts shapes")
            board.remove_items(edge_cuts)

        # Create rectangular outline
        outline = BoardRectangle()
        outline.layer = BoardLayer.BL_Edge_Cuts
        outline.top_left = mm_pos(BOARD_X, BOARD_Y)
        outline.bottom_right = mm_pos(BOARD_X + BOARD_W, BOARD_Y + BOARD_H)
        outline.attributes.stroke_width = 100_000  # 0.1mm
        board.create_items(outline)
        print(f"  Board outline created: ({BOARD_X},{BOARD_Y}) to ({BOARD_X+BOARD_W},{BOARD_Y+BOARD_H})")

        # ==============================================================
        # 2. PLACE COMPONENTS
        # ==============================================================
        fps = board.get_footprints()
        by_ref = {fp.reference_field.text.value: fp for fp in fps}

        print(f"\nFound {len(fps)} footprints on board")
        print(f"Placing {len(ALL_PLACEMENTS)} components...\n")

        updated = []
        placed = 0
        missing = []

        for ref, (x_mm, y_mm, angle_deg) in ALL_PLACEMENTS.items():
            if ref in by_ref:
                fp = by_ref[ref]
                fp.position = mm_pos(x_mm, y_mm)
                if angle_deg != 0:
                    fp.orientation = deg(angle_deg)
                updated.append(fp)
                placed += 1
                print(f"  {ref:5s} -> ({x_mm:6.1f}, {y_mm:6.1f}) angle={angle_deg}")
            else:
                missing.append(ref)

        if updated:
            board.update_items(updated)

        print(f"\nPlaced: {placed}/{len(ALL_PLACEMENTS)}")
        if missing:
            print(f"Missing (not found on board): {', '.join(missing)}")
            print("  -> Run 'Update PCB from Schematic' first!")

        # List unplaced footprints (power symbols don't have footprints)
        unplaced = [ref for ref in by_ref if ref not in ALL_PLACEMENTS
                     and not ref.startswith("#")]
        if unplaced:
            print(f"\nNote: {len(unplaced)} footprints not in layout plan: {', '.join(unplaced)}")

        # ==============================================================
        # 3. COMMIT ALL CHANGES
        # ==============================================================
        board.push_commit(commit, "SampleBoard: 4x4 inch layout with component placement")
        print("\nAll changes committed. You can Ctrl+Z to undo.")

    except Exception as e:
        board.drop_commit(commit)
        print(f"\nERROR: {e}")
        print("Changes rolled back.")
        raise

    print("\n=== Layout complete ===")
    print("Next steps:")
    print("  1. Check component placement in KiCad")
    print("  2. Run DRC to check for overlaps")
    print("  3. Route traces (ratsnest should be visible)")
    print("  4. Add ground plane (copper zone on B.Cu)")


if __name__ == "__main__":
    main()
