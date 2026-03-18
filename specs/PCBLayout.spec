KiCad 9 PCB Layout via IPC API - General Specification
========================================================
Version: 1.0
Scope: General-purpose (applies to any KiCad 9 PCB project)

This specification enables programmatic PCB manipulation through KiCad's
IPC API using the `kipy` Python library. Use this spec to connect to a
running KiCad instance and perform automated board operations.


1. Environment Setup
---------------------
1a. Python interpreter: Use KiCad's bundled Python:
      "/c/Program Files/KiCad/9.0/bin/python.exe"

1b. kipy package location (installed with kicad-python v0.5.0):
      c:/Projects/CircuitAI/kicad_3rdparty

1c. PYTHONPATH must include the kipy package:
      PYTHONPATH="c:/Projects/CircuitAI/kicad_3rdparty"

1d. Full command to run a script:
      PYTHONPATH="c:/Projects/CircuitAI/kicad_3rdparty" "/c/Program Files/KiCad/9.0/bin/python.exe" my_script.py

1e. Or for inline Python:
      PYTHONPATH="..." "/c/Program Files/KiCad/9.0/bin/python.exe" -c "..."


2. Prerequisites for IPC Connection
-------------------------------------
2a. KiCad PCB editor MUST be running and have a .kicad_pcb file open.
    The API socket is only available when an editor window is active.

2b. The KiCad API must be enabled:
    Preferences -> Plugins -> "Enable KiCad API" checkbox.

2c. The API listens at: ipc://<TEMP>/kicad/api.sock
    On Windows: ipc://C:\Users\<USER>\AppData\Local\Temp\kicad\api.sock
    kipy auto-detects this path.

2d. No KiCad dialogs should be open (they block the API event loop).

2e. If connecting to the KiCad project manager (not PCB editor), commands
    like GetOpenDocuments and GetBoard will fail with "no handler available".
    Solution: Open the PCB editor window specifically.


3. Connection and Basic Operations
------------------------------------
3a. Connect to KiCad:
      from kipy import KiCad
      kicad = KiCad(timeout_ms=10000)  # 10s timeout recommended

3b. Verify connection:
      kicad.ping()
      version = kicad.get_version()  # returns KiCadVersion object
      print(version.full_version)    # e.g. "9.0.7"

3c. Get the open board:
      board = kicad.get_board()  # returns Board object
      # Raises ApiError if no PCB editor is open

3d. Save the board:
      board.save()


4. Coordinate System
----------------------
4a. ALL coordinates are in NANOMETERS (nm). 1mm = 1,000,000 nm.

4b. Helper for mm to nm:
      def mm(x, y):
          return Vector2.from_xy(int(x * 1e6), int(y * 1e6))

4c. Or use the built-in mm helper:
      from kipy.geometry import Vector2
      pos = Vector2.from_xy_mm(100.0, 50.0)  # 100mm, 50mm

4d. Board origin is typically at (100mm, 50mm) or similar.
    KiCad's coordinate system: X increases right, Y increases down.


5. Working with Footprints
----------------------------
5a. Get all footprints:
      fps = board.get_footprints()  # list of FootprintInstance

5b. Read footprint properties:
      ref = fp.reference_field.text.value  # "U1", "R3", etc.
      val = fp.value_field.text.value      # "LM2596S-3.3", "10K"
      pos = fp.position                     # Vector2 (in nm)
      angle = fp.orientation                # Angle object
      layer = fp.layer                      # BoardLayer enum

5c. Move a footprint:
      fp.position = Vector2.from_xy(int(150e6), int(100e6))  # 150mm, 100mm
      # This automatically updates all child items (pads, text, shapes)

5d. Rotate a footprint:
      from kipy.geometry import Angle
      fp.orientation = Angle.from_degrees(90.0)

5e. Lock/unlock:
      fp.locked = True

5f. Apply changes:
      board.update_items([fp1, fp2, fp3])  # batch update
      # Or: board.update_items(single_fp)  # single update

5g. Build a ref->footprint lookup:
      by_ref = {fp.reference_field.text.value: fp for fp in board.get_footprints()}


6. Board Outline (Edge.Cuts)
------------------------------
6a. Import types:
      from kipy.board_types import BoardLayer, BoardRectangle

6b. Remove existing outline:
      shapes = board.get_shapes()
      edge_cuts = [s for s in shapes if s.layer == BoardLayer.BL_Edge_Cuts]
      if edge_cuts:
          board.remove_items(edge_cuts)

6c. Create rectangular outline:
      outline = BoardRectangle()
      outline.layer = BoardLayer.BL_Edge_Cuts
      outline.top_left = Vector2.from_xy(int(100e6), int(50e6))
      outline.bottom_right = Vector2.from_xy(int(201.6e6), int(151.6e6))
      outline.attributes.stroke_width = 100_000  # 0.1mm line width
      board.create_items(outline)

6d. Common board sizes:
      4" x 4" = 101.6mm x 101.6mm
      100mm x 100mm (JLCPCB prototype pricing sweet spot)
      50mm x 50mm (small board)


7. Commit System (Undo/Redo)
-------------------------------
7a. Without commits, each operation is a separate undo step.

7b. Use commits to group changes into a single undo step:
      commit = board.begin_commit()
      try:
          # ... do multiple operations ...
          board.push_commit(commit, "Description of changes")
      except Exception as e:
          board.drop_commit(commit)
          raise

7c. The commit message appears in KiCad's Edit menu undo history.


8. Nets and Connectivity
--------------------------
8a. Get all nets:
      nets = board.get_nets()
      for net in nets:
          print(net.name)  # "+3V3", "GND", "/SPI_CLK", etc.

8b. Filter by netclass:
      power_nets = board.get_nets(netclass_filter="Power")

8c. Get pads (for connectivity analysis):
      pads = board.get_pads()  # all pads on the board
      for pad in pads:
          print(pad.net.name, pad.position)

8d. Note: get_pads() can be slow on large boards. If KiCad returns
    "busy", retry after a short delay.


9. Layers
-----------
9a. Common layer constants (from kipy.board_types.BoardLayer):
      BL_F_Cu       - Front copper
      BL_B_Cu       - Back copper
      BL_F_SilkS    - Front silkscreen
      BL_B_SilkS    - Back silkscreen
      BL_F_Mask     - Front solder mask
      BL_B_Mask     - Back solder mask
      BL_Edge_Cuts  - Board outline
      BL_F_CrtYd    - Front courtyard
      BL_F_Fab      - Front fabrication

9b. Get/set active layer:
      current = board.get_active_layer()
      board.set_active_layer(BoardLayer.BL_F_Cu)


10. Creating Board Items
--------------------------
10a. Create items:
       created = board.create_items(item)           # single
       created = board.create_items([item1, item2])  # batch

10b. Remove items:
       board.remove_items(item)
       board.remove_items([item1, item2])

10c. Get items by type:
       from kipy.proto.common.types import KiCadObjectType
       tracks = board.get_items(KiCadObjectType.KOT_PCB_TRACE)
       zones = board.get_items(KiCadObjectType.KOT_PCB_ZONE)

10d. Convenience getters:
       board.get_footprints()
       board.get_tracks()
       board.get_vias()
       board.get_pads()
       board.get_shapes()
       board.get_zones()
       board.get_text()


11. Selection
--------------
11a. Get current selection:
       selected = board.get_selection()

11b. Add/remove from selection:
       board.add_to_selection(items)
       board.remove_from_selection(items)
       board.clear_selection()

11c. Initiate interactive move (user drags in GUI):
       board.interactive_move(item.id)
       # Blocks API until user completes the move


12. Board Info and Settings
-----------------------------
12a. Get board stackup:
       stackup = board.get_stackup()
       for layer in stackup.layers:
           print(layer.user_name, layer.thickness)

12b. Get/set copper layers:
       count = board.get_copper_layer_count()

12c. Get bounding box of items:
       bbox = board.get_item_bounding_box(fp)  # returns Box2
       print(bbox.pos, bbox.size)

12d. Refill zones:
       board.refill_zones(block=True)  # waits until complete

12e. Board origin:
       from kipy.board import BoardOriginType
       origin = board.get_origin(BoardOriginType.BOT_GRID_ORIGIN)


13. Complete Example: Auto-Place Components
----------------------------------------------
    from kipy import KiCad
    from kipy.board_types import BoardLayer, BoardRectangle
    from kipy.geometry import Vector2

    kicad = KiCad(timeout_ms=10000)
    board = kicad.get_board()
    commit = board.begin_commit()

    try:
        # Remove old outline
        shapes = board.get_shapes()
        edge = [s for s in shapes if s.layer == BoardLayer.BL_Edge_Cuts]
        if edge:
            board.remove_items(edge)

        # Create 100mm x 100mm board
        outline = BoardRectangle()
        outline.layer = BoardLayer.BL_Edge_Cuts
        outline.top_left = Vector2.from_xy(int(100e6), int(50e6))
        outline.bottom_right = Vector2.from_xy(int(200e6), int(150e6))
        outline.attributes.stroke_width = 100_000
        board.create_items(outline)

        # Place footprints
        fps = board.get_footprints()
        by_ref = {fp.reference_field.text.value: fp for fp in fps}

        placements = {
            "U1": (130, 80),
            "C1": (120, 80),
            "R1": (140, 90),
        }

        updated = []
        for ref, (x_mm, y_mm) in placements.items():
            if ref in by_ref:
                by_ref[ref].position = Vector2.from_xy(
                    int(x_mm * 1e6), int(y_mm * 1e6)
                )
                updated.append(by_ref[ref])

        board.update_items(updated)
        board.push_commit(commit, "Auto-place components")

    except Exception:
        board.drop_commit(commit)
        raise


14. Error Handling
--------------------
14a. kipy.errors.ConnectionError: KiCad not running or API disabled.
     Fix: Open KiCad PCB editor and enable API in Preferences.

14b. kipy.errors.ApiError: "no handler available"
     Fix: The PCB editor window must be open (not just project manager).

14c. kipy.errors.ApiError: "KiCad is busy"
     Fix: Close any open dialogs in KiCad, wait a moment, retry.

14d. kipy.errors.ConnectionError: "Timed out"
     Fix: Increase timeout_ms, close KiCad dialogs, or check if
     KiCad is performing a heavy operation (zone fill, DRC).

14e. Always use try/except with drop_commit() to avoid leaving
     orphaned commits that block future API calls.


15. JLCPCB Design Rules (for fab + assembly)
-----------------------------------------------
15a. Minimum trace width:   0.127mm (5mil)
15b. Minimum trace spacing: 0.127mm (5mil)
15c. Minimum via drill:     0.3mm
15d. Minimum via diameter:  0.45mm (annular ring 0.075mm)
15e. Board thickness:       1.6mm (default)
15f. Minimum hole size:     0.3mm
15g. Copper to edge:        0.3mm minimum

15h. For 2-layer boards, standard stackup:
       F.Cu (35um) / Core 1.6mm / B.Cu (35um)


16. 3D Model Paths
---------------------
16a. JLCImport footprints reference 3D models using:
       (model "${KIPRJMOD}/JLCImport.3dshapes/<part>.wrl" ...)

16b. ${KIPRJMOD} resolves to the directory containing the .kicad_pro file.
     The 3D shapes folder is at the PROJECT ROOT (same level as JLCImport.pretty).

16c. PROBLEM: If the .kicad_pro is in a subfolder (e.g., templates/sample_board/),
     ${KIPRJMOD} resolves to that subfolder, NOT the project root. KiCad will
     fail to find the 3D models and the 3D viewer will show bare PCB only.

16d. FIX FOR SUBFOLDERS: When creating a PCB in a subfolder, the 3D model paths
     in the .kicad_pcb file must use relative path traversal:
       ${KIPRJMOD}/../../JLCImport.3dshapes/<part>.wrl
     The number of "../" depends on how deep the project is relative to the root.

16e. When using pcbnew standalone (FootprintLoad), model paths are copied verbatim
     from the .kicad_mod files. After saving the PCB, fix all model paths:
       sed -i 's|${KIPRJMOD}/JLCImport.3dshapes/|${KIPRJMOD}/../../JLCImport.3dshapes/|g' board.kicad_pcb
     Adjust the ../../ depth to match the project's location relative to the root.

16f. When using KiCad IPC API or "Update PCB from Schematic", the same issue
     applies — verify 3D model paths after import.

16g. VERIFICATION: Open the 3D viewer (Alt+3). If components show as bare pads
     with no 3D bodies, the model paths are wrong.


17. PCB Placement Best Practices
----------------------------------
16a. Place the largest/most-connected IC first (usually MCU).
16b. Place decoupling caps within 3mm of their IC's power pins.
16c. Place connectors at board edges.
16d. Group components by functional block.
16e. Keep high-speed signals short (USB, SPI, I2S).
16f. Separate analog and digital sections.
16g. Place bypass caps on the same side as the IC they serve.
16h. Orient similar components consistently for easier assembly.
16i. Leave space for silkscreen labels.
16j. Consider thermal relief for power components.
