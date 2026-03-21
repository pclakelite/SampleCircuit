"""
remove_stray_u6.py — Remove the stray Micro_SD_Card_C585354 footprint via KiCad IPC API.

Run with KiCad PCB editor open:
  "/c/Program Files/KiCad/9.0/bin/python.exe" remove_stray_u6.py
"""

import sys
sys.path.insert(0, r"c:\Projects\CircuitAI\kicad_3rdparty")

from kipy import KiCad


def main():
    print("Connecting to KiCad IPC API...")
    kicad = KiCad(timeout_ms=10000)
    version = kicad.get_version()
    print(f"Connected to KiCad {version.full_version}")

    board = kicad.get_board()
    fps = board.get_footprints()

    # Find the stray Molex SD card footprint (uuid from PCB file)
    target_uuid = "8ba395a8-b5cf-44a7-bb59-855eb18ce401"
    stray = None
    for fp in fps:
        ref = fp.reference_field.text.value
        uid = str(fp.id.value)
        if uid == target_uuid:
            stray = fp
            print(f"Found stray footprint: {ref} (uuid: {uid})")
            break

    if not stray:
        # Fallback: find by footprint library name
        for fp in fps:
            ref = fp.reference_field.text.value
            if ref == "U6" and "Micro_SD" in str(fp.definition.id):
                stray = fp
                print(f"Found stray footprint by name: {ref}")
                break

    if not stray:
        print("Stray Micro_SD_Card footprint not found. Nothing to do.")
        return

    commit = board.begin_commit()
    try:
        board.remove_items([stray])
        board.push_commit(commit, "Remove stray Micro_SD_Card_C585354 footprint")
        print("Removed. Ctrl+Z in KiCad to undo.")
    except Exception as e:
        board.drop_commit(commit)
        print(f"ERROR: {e}\nRolled back.")
        raise


if __name__ == "__main__":
    main()
