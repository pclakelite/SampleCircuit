"""
layout_samplecircuit.py — Place all SampleCircuit components via KiCad IPC API.

4" x 4" (101.6mm x 101.6mm) board layout with functional grouping:
  Top edge:      Power connectors (J1-J4), Speaker (J5)
  Upper band:    PSU stages (24→12V, 24→5V, 24→3.3V), Supervisor
  Center-left:   ESP32-S3 module + decoupling + buttons
  Center-right:  Flash, SD Card
  Bottom:        RTC + battery, Audio + output cap

Run with KiCad PCB editor open:
  "/c/Program Files/KiCad/9.0/bin/python.exe" layout_samplecircuit.py
"""

import sys
sys.path.insert(0, r"c:\Projects\CircuitAI\kicad_3rdparty")

from kipy import KiCad
from kipy.board_types import BoardLayer, BoardRectangle
from kipy.geometry import Vector2, Angle

# ==============================================================
# BOARD DIMENSIONS — 4" x 4"
# ==============================================================
BOARD_X = 100.0
BOARD_Y = 50.0
BOARD_W = 101.6   # 4 inches
BOARD_H = 101.6   # 4 inches


def mm(x, y):
    return Vector2.from_xy(int(x * 1e6), int(y * 1e6))

def deg(a):
    return Angle.from_degrees(float(a))


# ==============================================================
# COMPONENT PLACEMENTS: ref -> (x_mm, y_mm, angle_deg)
# ==============================================================

# --- Top edge: Power connectors ---
CONNECTORS = {
    "J1":  (108.0,  55.0,   0),   # 24V INPUT
    "J2":  (132.0,  55.0,   0),   # 12V TEST
    "J3":  (155.0,  55.0,   0),   # 5V TEST
    "J4":  (175.0,  55.0,   0),   # 3.3V TEST
    "J5":  (196.0,  55.0,   0),   # SPEAKER
}

# --- Input protection (near J1) ---
INPUT_PROTECTION = {
    "D9":  (116.0,  58.0,   0),   # SS34 Schottky
    "D10": (116.0,  63.0,   0),   # SMBJ26CA TVS
}

# --- PSU 24V → 12V (left, y≈74) ---
PSU_12V = {
    "U1":  (115.0,  74.0,   0),   # LMZM23601
    "C1":  (106.0,  70.0,   0),   # 10uF 35V input
    "C31": (106.0,  74.0,   0),   # 10uF 35V input
    "C33": (106.0,  78.0,   0),   # 10uF 35V input
    "C3":  (124.0,  74.0,   0),   # 47uF 16V output
    "R1":  (124.0,  70.0,  90),   # 110k feedback top
    "R2":  (127.0,  70.0,  90),   # 10k feedback bottom
}

# --- PSU 24V → 5V (center, y≈74) ---
PSU_5V = {
    "U24": (148.0,  74.0,   0),   # LMZM23601
    "C106":(139.0,  74.0,   0),   # 10uF 35V input
    "C32": (157.0,  74.0,   0),   # 47uF 16V output
    "R3":  (157.0,  70.0,  90),   # 10k feedback top
    "R4":  (160.0,  70.0,  90),   # 2.49k feedback bottom
}

# --- PSU 24V → 3.3V (right, y≈74) ---
PSU_3V3 = {
    "U25": (178.0,  74.0,   0),   # LMZM23601
    "D8":  (169.0,  70.0,   0),   # PMEG6030 input diode
    "C107":(169.0,  78.0,   0),   # 680uF 35V input
    "C93": (169.0,  74.0,   0),   # 10uF input
    "C35": (187.0,  74.0,   0),   # 47uF 16V output
    "R48": (187.0,  70.0,  90),   # 10k feedback top
    "R89": (190.0,  70.0,  90),   # 10k feedback bottom
}

# --- Supervisor (near 3.3V rail) ---
SUPERVISOR = {
    "U15": (196.0,  74.0,   0),   # TLV803S
    "C104":(196.0,  70.0,   0),   # 100nF decoupling
    "C105":(196.0,  78.0,   0),   # 10uF bulk
}

# --- ESP32-S3 Core (center-left, large module) ---
ESP32_CORE = {
    "U2":  (120.0, 108.0,   0),   # ESP32-S3-WROOM-1 (~18x25mm)
    "SW1": (108.0,  90.0,   0),   # RESET button
    "SW2": (108.0,  96.0,   0),   # BOOT button
    # Decoupling caps — column near ESP32
    "C2":  (136.0,  98.0,   0),   # 100nF
    "C4":  (136.0, 101.0,   0),   # 1uF
    "C5":  (136.0, 104.0,   0),   # 100nF
    "C11": (136.0, 107.0,   0),   # 100nF
    "C17": (136.0, 110.0,   0),   # 1uF
    "C39": (136.0, 113.0,   0),   # 100nF
    "C94": (136.0, 116.0,   0),   # 100nF
}

# --- Flash memory (near ESP32 SPI bus) ---
FLASH = {
    "Mem1":(155.0, 100.0,   0),   # CSNP1GCR01-BOW
}

# --- SD Card (near ESP32 SPI bus) ---
SDCARD = {
    "U6":  (170.0, 105.0,   0),   # MicroSD socket
}

# --- RTC (bottom center) ---
RTC = {
    "U23": (155.0, 130.0,   0),   # RV-3028-C7
    "B3":  (148.0, 142.0,   0),   # CR1220 battery holder
    "R94": (162.0, 130.0,   0),   # 1k VBACKUP series
    "C34": (162.0, 134.0,   0),   # 10uF 35V
}

# --- Audio (bottom right) ---
AUDIO = {
    "U5":  (185.0, 115.0,   0),   # NS4168
    "R20": (178.0, 112.0,  90),   # 100k GAIN
    "R31": (178.0, 115.0,  90),   # 10k
    "R32": (178.0, 118.0,  90),   # 4.22k
    "C18": (192.0, 120.0,   0),   # 100uF output
}

# Combine all
ALL = {}
for group in [CONNECTORS, INPUT_PROTECTION, PSU_12V, PSU_5V, PSU_3V3,
              SUPERVISOR, ESP32_CORE, FLASH, SDCARD, RTC, AUDIO]:
    ALL.update(group)


def main():
    print("Connecting to KiCad IPC API...")
    kicad = KiCad(timeout_ms=10000)
    version = kicad.get_version()
    print(f"Connected to KiCad {version.full_version}")

    board = kicad.get_board()
    commit = board.begin_commit()

    try:
        # --- Board outline ---
        print(f"\nBoard outline: {BOARD_W}x{BOARD_H}mm ({BOARD_W/25.4:.0f}\"x{BOARD_H/25.4:.0f}\")")
        shapes = board.get_shapes()
        edge_cuts = [s for s in shapes if s.layer == BoardLayer.BL_Edge_Cuts]
        if edge_cuts:
            print(f"  Removing {len(edge_cuts)} existing Edge.Cuts shapes")
            board.remove_items(edge_cuts)

        outline = BoardRectangle()
        outline.layer = BoardLayer.BL_Edge_Cuts
        outline.top_left = mm(BOARD_X, BOARD_Y)
        outline.bottom_right = mm(BOARD_X + BOARD_W, BOARD_Y + BOARD_H)
        outline.attributes.stroke_width = 100_000  # 0.1mm
        board.create_items(outline)

        # --- Place components ---
        fps = board.get_footprints()
        by_ref = {fp.reference_field.text.value: fp for fp in fps}

        print(f"\n{len(fps)} footprints on board, placing {len(ALL)}...\n")

        updated = []
        placed = 0
        missing = []

        for ref, (x, y, angle) in ALL.items():
            if ref in by_ref:
                fp = by_ref[ref]
                fp.position = mm(x, y)
                if angle != 0:
                    fp.orientation = deg(angle)
                else:
                    fp.orientation = deg(0)
                updated.append(fp)
                placed += 1
                print(f"  {ref:6s} -> ({x:6.1f}, {y:6.1f})  {angle:3d}°")
            else:
                missing.append(ref)

        if updated:
            board.update_items(updated)

        print(f"\nPlaced: {placed}/{len(ALL)}")
        if missing:
            print(f"MISSING (not on board): {', '.join(missing)}")

        unplaced = [r for r in by_ref if r not in ALL and not r.startswith("#")]
        if unplaced:
            print(f"NOT IN PLAN ({len(unplaced)}): {', '.join(sorted(unplaced))}")

        board.push_commit(commit, "SampleCircuit: functional block placement on 4x4 inch board")
        print("\nCommitted. Ctrl+Z to undo.")

    except Exception as e:
        board.drop_commit(commit)
        print(f"\nERROR: {e}\nRolled back.")
        raise

    print("\nDone! Check KiCad — components should be arranged by functional block.")


if __name__ == "__main__":
    main()
