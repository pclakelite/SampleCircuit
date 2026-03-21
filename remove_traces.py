"""
remove_traces.py — Remove all traces and vias from the board via KiCad IPC API.

Run with KiCad PCB editor open:
  "/c/Program Files/KiCad/9.0/bin/python.exe" remove_traces.py
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

    tracks = board.get_tracks()
    vias = board.get_vias()

    print(f"Found {len(tracks)} traces and {len(vias)} vias")

    if not tracks and not vias:
        print("Nothing to remove.")
        return

    commit = board.begin_commit()
    try:
        if tracks:
            board.remove_items(tracks)
        if vias:
            board.remove_items(vias)
        board.push_commit(commit, "Remove all traces and vias")
        print(f"Removed {len(tracks)} traces and {len(vias)} vias. Ctrl+Z to undo.")
    except Exception as e:
        board.drop_commit(commit)
        print(f"ERROR: {e}\nRolled back.")
        raise


if __name__ == "__main__":
    main()
