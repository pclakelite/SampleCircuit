KiCad 9 PCB Component Placement - General Specification
=========================================================
Version: 1.3
Scope: General-purpose (applies to any KiCad 9 PCB project)

PURPOSE
-------
This specification provides a reusable set of rules and verification
algorithms for automated PCB component placement via KiCad's IPC API.
It is intended to be referenced by any project that uses programmatic
placement, ensuring consistent quality across different board designs.

All content in this specification MUST remain general-purpose. Do not
add project-specific component references, board dimensions, or layout
decisions. If a rule only applies to a particular circuit or board, it
belongs in that project's layout script — not here.

All placement scripts MUST enforce these rules before committing
changes to the board.


1. Board Outline and Edge Clearance
-------------------------------------
1a. No component courtyard or silkscreen may extend beyond the board
    outline (Edge.Cuts). This includes reference designators, value
    text, and fabrication layer graphics.

1b. Verify edge clearance by checking every footprint's bounding box:
      for fp in board.get_footprints():
          bbox = board.get_item_bounding_box(fp)
          # bbox must be fully inside board outline

1c. Minimum clearance from board edge to nearest component courtyard:
    0.5mm for SMD components, 1.0mm for through-hole components.

1d. Connectors that require user access (card slots, terminal blocks)
    MUST be placed at board edges with their insertion axis perpendicular
    to the edge. Verify the insertion side is not blocked.

1e. CONNECTOR ALIGNMENT: All connectors along the same board edge MUST
    share the same offset distance from that edge. Connectors should be
    evenly distributed along the edge with equal spacing between them,
    respecting mounting hole keepout zones. Calculate usable edge length
    by excluding mounting hole keepout regions at each end, then divide
    remaining space evenly among all connectors on that edge.


2. Mounting Holes
-------------------
2a. Mounting holes are placed as circles on the Edge.Cuts layer.
    Drill diameter = screw clearance hole (e.g., M3=3.4mm, M4=4.5mm,
    M5=5.5mm, M6=6.5mm).

2b. KEEPOUT ZONE: Every mounting hole must have a component-free zone
    around it to clear the fastener head and washer. Minimum keepout
    radius from hole center:

      Screw Size | Hole Drill | Washer OD | Keepout Radius
      M3         | 3.4mm      | 7mm       | 5.0mm
      M4         | 4.5mm      | 9mm       | 6.0mm
      M5         | 5.5mm      | 10mm      | 7.0mm
      M6         | 6.5mm      | 12mm      | 8.0mm

    No component bounding box may intersect the keepout circle.

2c. Keepout verification algorithm:
      for each hole (hx, hy) with keepout radius R:
          for each footprint fp:
              bbox = board.get_item_bounding_box(fp)
              # find closest point on bbox to hole center
              cx = clamp(hx, bbox.left, bbox.right)
              cy = clamp(hy, bbox.top, bbox.bottom)
              distance = sqrt((cx-hx)^2 + (cy-hy)^2)
              ASSERT distance >= R

2d. DEFAULT FASTENER SIZE: M6. Use M6 mounting holes unless the board
    size or application requires a smaller fastener. M6 provides good
    mechanical strength for most enclosure mounting scenarios.

2e. HOLE INSET: Mounting holes should be inset 10mm from each board
    edge where allowable. If 10mm inset would place the hole keepout
    zone outside the board or conflict with a board cutout (e.g.,
    antenna notch), shift the hole along the edge to the nearest
    clear position.

2f. Mounting hole placement strategy:
    - Default: one hole per corner, inset 10mm from each edge
    - If a corner conflicts with a board cutout or large component,
      shift the hole along the edge (not into the board interior)
    - NEVER move mounting holes to accommodate components — move
      components instead. Mechanical mounting points are fixed.


3. Component Overlap Prevention
---------------------------------
3a. No two component bounding boxes may overlap. This is a hard rule
    with zero exceptions.

3b. Verification: check all N*(N-1)/2 pairs of footprints:
      for i in range(len(fps)):
          for j in range(i+1, len(fps)):
              ASSERT not overlaps(bbox[i], bbox[j])

3c. Bounding box overlap test:
      def overlaps(a, b):
          return a.left < b.right and a.right > b.left \
             and a.top < b.bottom and a.bottom > b.top

3d. Minimum spacing between adjacent component bounding boxes: 0.5mm.
    This ensures silkscreen text, courtyard lines, and solder paste
    do not interfere.

3e. PAD-TO-PAD OVERLAP: No solderable pad from one component may
    overlap a solderable pad from a different component. This is
    verified separately from bounding box overlap because pads are
    smaller than bounding boxes. Use bounding box containment (not
    center distance) to assign pads to their parent footprint, as
    large ICs can have pads far from their center.

3f. After ANY placement change, re-run the full overlap check before
    committing. Fixing one overlap can introduce another.


4. Functional Grouping
------------------------
4a. Components MUST be grouped by their schematic functional block.
    Each sub-circuit's passives belong physically near the IC they
    support, not scattered across the board.

4b. Decoupling capacitors: place within 3mm of the IC power pin they
    decouple. Closer is always better. The trace from cap to IC power
    pin should be as short as possible.

4c. Feedback resistor dividers: place within 5mm of the IC feedback
    pin. Keep the voltage divider node trace short to avoid noise
    pickup.

4d. Input protection components (TVS diodes, Schottky diodes, fuses):
    place between the input connector and the circuit they protect,
    as close to the connector as possible.

4e. Signal bus grouping: components sharing a bus (SPI, I2C, I2S)
    should be physically close to minimize trace length. Shared-bus
    ICs should be placed in a cluster, not on opposite sides of the
    board.

4f. COMPACT LAYOUT: Components within a functional group should be
    placed as close together as practical — do not spread components
    to fill available board space. Target inter-component spacing of
    1–3mm within a group (enough for silkscreen text and routing, but
    no wasted space). A group's bounding area should be the minimum
    rectangle that fits all its components with routing clearance.

4g. GROUP-TO-GROUP SPACING: Adjacent functional groups should be placed
    close together with 3–5mm between groups.

4g-exception. CONNECTORS are exempt from intra-group compactness rules.
    Connectors must be placed at board edges for user access (per rule
    1d), so they will naturally be spread across the board perimeter.
    Do not flag connector-to-connector distance as a grouping violation.

4h. DEAD SPACE IS ACCEPTABLE: Empty board area on a side or corner is
    fine as long as functional groups are internally compact and placed
    close to their neighboring groups. Do not spread components apart
    just to fill available board space. Tight family grouping takes
    priority over even board utilization.

4i. BALANCE DENSITY VS MANUFACTURABILITY: Compact layout must not
    compromise solderability or inspection. Minimum spacing between
    component bounding boxes remains 0.5mm (per rule 3d). If text
    cannot fit at 0.8mm height in the available space, the layout is
    too tight — increase spacing slightly rather than hiding reference
    designators.


5. RF and Antenna Placement
-----------------------------
5a. MANUFACTURER SPECIFICATION REQUIRED: Any device with an integrated
    antenna or radio (WiFi, Bluetooth, LoRa, cellular, GPS, etc.) MUST
    be placed according to the manufacturer's antenna design guidelines.
    These guidelines define cutout dimensions, keepout zones, ground
    plane exclusions, and clearance distances specific to that device.
    Do not substitute generic rules for manufacturer specifications.

5b. Antenna placement at board edge: modules with PCB antennas should
    have their antenna at a board edge or extending beyond it, unless
    the manufacturer's guidelines specify otherwise.

5c. PCB CUTOUT: If the manufacturer specifies removing board material
    (FR4) under the antenna, create the cutout as part of the Edge.Cuts
    outline (polygon with notch), not as an internal cutout. Match the
    cutout dimensions to the manufacturer's recommended geometry.

5d. KEEPOUT ZONE around antenna: follow the manufacturer's specified
    keepout distances. At minimum, the keepout zone must exclude:
    - Copper traces, pours, and vias
    - Components and their courtyards
    - Ground plane on all copper layers
    The GND copper pour zone outline must be shaped to exclude the
    antenna keepout area.

5e. Antenna orientation: orient the module so the antenna feed point
    is closest to the board edge. Consult the device datasheet for
    which end of the module contains the antenna — it may require
    rotation from the default footprint orientation.

5f. RF noise isolation: keep high-frequency noise sources (switching
    regulators, crystals, high-speed digital) as far from the antenna
    as practical. Follow the manufacturer's recommended minimum
    separation distance; if unspecified, use 20mm as a default.


6. Copper Pour (Ground Planes)
--------------------------------
6a. GND copper pour should be created on both F.Cu and B.Cu for
    2-layer boards.

6b. The zone outline MUST match the board outline including any
    cutouts (antenna notches, etc.). Do not fill copper into cutout
    areas.

6c. Zone parameters:
    - Net: GND
    - Min thickness: 0.25mm
    - Clearance: 0.2mm (or per design rules)
    - Priority: 0 (lowest, so signal traces take precedence)

6d. After all placement is complete, call board.refill_zones(block=True)
    to fill the copper pour around the final component positions.

6e. Remove existing zones before re-creating them after major placement
    changes to avoid stale fill artifacts.


7. Placement Workflow
-----------------------
7a. BOARD SIZE DETERMINATION: Do NOT pre-define the board size.
    Place all components first in a compact layout, then determine
    the board dimensions:
    1. Calculate the bounding box of all placed components
    2. Add margins: 10mm on each edge for mounting hole inset
    3. Add antenna cutout depth if applicable
    4. Round BOTH width and height UP to the nearest 10mm
    This ensures the board is always the minimum practical size.

7b. The correct order for automated placement is:
    1. Remove existing board outline, copper pour zones, and holes
    2. Place the largest / most-connected IC first (usually MCU)
    3. Place that IC's decoupling caps and support components
    4. Place connectors at board edges (use temporary edge estimate)
    5. Place remaining ICs grouped by function, largest first
    6. Place each IC's passives immediately after the IC
    7. Calculate board size from component bounding box (per 7a)
    8. Create board outline (with cutouts if needed)
    9. Place mounting holes at 10mm inset from edges
    10. Run overlap check — fix any violations
    11. Run mounting hole keepout check — fix any violations
    12. Run edge clearance check — fix any violations
    13. Reposition silkscreen text — fix any pad overlaps
    13. Hide value fields that cause clutter
    14. Recreate GND copper pour zones
    15. Refill zones

7b. Each functional group should be committed separately so the user
    can undo individual groups in KiCad (Ctrl+Z).

7c. After all placement, run a final comprehensive verification:
    - Zero bounding box overlaps
    - Zero pad-to-pad overlaps between different components
    - Zero mounting hole keepout violations
    - Zero edge clearance violations
    - Zero silkscreen-on-pad overlaps
    - Zero silkscreen-on-silkscreen overlaps
    - All reference designators visible
    - Connectors aligned at same edge offset with even spacing
    - All components accounted for (none left unplaced)


8. Orientation for Routing
----------------------------
8a. Orient ICs so their most-connected pins face toward the components
    they connect to. Example: SPI bus pins toward flash/SD card.

8b. Orient passive components (0805, 0603, etc.) so their pads align
    with the traces that will connect them. Vertical (90°) when the
    trace runs vertically, horizontal (0°) when horizontal.

8c. Orient all similar passives consistently within a functional group
    (e.g., all feedback resistors at 90°). This aids visual inspection
    and assembly.

8d. Power flow should be left-to-right or top-to-bottom across the
    board. Place voltage regulators in the order of the power chain
    (e.g., 24V→12V→5V→3.3V left to right).


9. Silkscreen Text Management
--------------------------------
9a. NO SILKSCREEN TEXT ON SOLDERABLE PADS. Reference designators and
    value text must never overlap any pad on the board. This applies
    to pads on the same component AND on adjacent components.

9b. Reference designators (annotations) are MANDATORY. Every component
    must have a visible reference designator (e.g., R1, U1, C1). These
    may be repositioned or resized but NEVER hidden or deleted.

9c. Value/part number text may be hidden if it causes overlap or visual
    clutter. If the value field cannot be placed without overlapping
    pads or other text, hide it (set visible = False). The reference
    designator is the minimum required visible text per component.

9d. Text repositioning algorithm — when a reference designator overlaps
    a pad or another silkscreen text, reposition using this cascading
    strategy:

    STEP 1 — Try all 4 positions at current text size:
      1. Above the component bounding box
      2. Below the component bounding box
      3. Right of the component bounding box
      4. Left of the component bounding box
    For each candidate, offset the text center by gap + text_height/2
    (above/below) or gap + text_width/2 (left/right), where gap >= 0.3mm.
    Accept the first position that does not overlap any pad or other
    visible silkscreen text.

    STEP 2 — Try all 4 positions at each rotation (0° and 90°):
    If no position works at step 1, rotate the text 90° and retry all
    4 positions. This changes the text's width/height ratio and may
    fit where the original orientation could not.

    STEP 3 — Reduce text size and retry:
    If no rotation works, reduce text size by 0.2mm (e.g., 1.0 → 0.8 →
    0.6 → 0.5mm minimum) and repeat steps 1-2 at each size. Do not go
    below 0.5mm height.

    STEP 4 — Increase gap distance and retry:
    If still no fit, multiply the gap by 2x, 3x, 5x and retry all
    combinations of position, rotation, and size.

    If all attempts fail, flag the component for manual review.

9e. Verification: check every visible text field against all pad rects:
      pads = board.get_pads()
      pad_rects = []
      for p in pads:
          px, py = p.position.x/1e6, p.position.y/1e6
          sx = p.padstack.copper_layers[0].size.x/1e6
          sy = p.padstack.copper_layers[0].size.y/1e6
          pad_rects.append((px-sx/2, py-sy/2, px+sx/2, py+sy/2))

      for fp in board.get_footprints():
          ref = fp.reference_field
          if not ref.visible: continue
          tbb = board.get_item_bounding_box(ref.text)
          tx1, ty1 = tbb.pos.x/1e6, tbb.pos.y/1e6
          tx2 = (tbb.pos.x + tbb.size.x)/1e6
          ty2 = (tbb.pos.y + tbb.size.y)/1e6
          for (px1, py1, px2, py2) in pad_rects:
              ASSERT NOT (tx1<px2 and tx2>px1 and ty1<py2 and ty2>py1)

9f. NO SILKSCREEN TEXT OVERLAPPING OTHER SILKSCREEN TEXT. Visible
    reference designators must not overlap each other. The repositioning
    algorithm (9d) must check candidate positions against both pads AND
    all other visible silkscreen text bounding boxes.

9g. Text sizing: silkscreen text may be reduced to fit tight areas,
    but must not go below 0.5mm height (minimum readable size for
    standard PCB fabrication). Preferred default is 1.0mm; 0.8mm is
    acceptable for dense areas.

9h. Text orientation: keep text readable (0° or 90°). Use the same
    orientation as the component where possible. Within a functional
    group, orient all reference text consistently.


10. IPC API Coordinate System
--------------------------------
10a. All coordinates are in nanometers. 1mm = 1,000,000 nm.
     Helper: Vector2.from_xy(int(x_mm * 1e6), int(y_mm * 1e6))

10b. KiCad board origin is typically at (100mm, 50mm). X increases
     right, Y increases down.

10c. Rotation: 0° = default orientation. Use Angle.from_degrees().
     Positive angles rotate counter-clockwise.

10d. Commit system: always wrap placement in begin_commit/push_commit
     with try/except/drop_commit for rollback on error.


11. Verification Script Template
-----------------------------------
    Every placement script MUST include this verification at the end:

    def verify_placement(board, holes, keepout_radius, board_rect):
        """
        board_rect: (x1, y1, x2, y2) in mm — board outline corners
        holes: dict of name -> (x_mm, y_mm) for mounting holes
        keepout_radius: mm clearance from hole center to nearest bbox
        """
        import math
        fps = board.get_footprints()
        errors = []

        # 1. Component overlap check
        boxes = {}
        for fp in fps:
            ref = fp.reference_field.text.value
            if ref.startswith('#'): continue
            bb = board.get_item_bounding_box(fp)
            boxes[ref] = (bb.pos.x/1e6, bb.pos.y/1e6,
                         (bb.pos.x+bb.size.x)/1e6,
                         (bb.pos.y+bb.size.y)/1e6)
        refs = sorted(boxes.keys())
        for i in range(len(refs)):
            for j in range(i+1, len(refs)):
                a, b = boxes[refs[i]], boxes[refs[j]]
                if a[0]<b[2] and a[2]>b[0] and a[1]<b[3] and a[3]>b[1]:
                    errors.append(f"OVERLAP: {refs[i]} <-> {refs[j]}")

        # 2. Mounting hole keepout check
        for name, (hx, hy) in holes.items():
            for ref, (x1,y1,x2,y2) in boxes.items():
                cx = max(x1, min(hx, x2))
                cy = max(y1, min(hy, y2))
                d = math.sqrt((cx-hx)**2 + (cy-hy)**2)
                if d < keepout_radius:
                    errors.append(f"KEEPOUT: {ref} {d:.1f}mm from {name} hole")

        # 3. Edge clearance check
        bx1, by1, bx2, by2 = board_rect
        for ref, (x1, y1, x2, y2) in boxes.items():
            if x1 < bx1:
                errors.append(f"EDGE: {ref} left={x1:.1f}mm beyond board left")
            if y1 < by1:
                errors.append(f"EDGE: {ref} top={y1:.1f}mm beyond board top")
            if x2 > bx2:
                errors.append(f"EDGE: {ref} right={x2:.1f}mm beyond board right")
            if y2 > by2:
                errors.append(f"EDGE: {ref} bottom={y2:.1f}mm beyond board bottom")

        # 4. Silkscreen-on-pad check
        pads = board.get_pads()
        pad_rects = []
        for p in pads:
            px, py = p.position.x/1e6, p.position.y/1e6
            cs = p.padstack.copper_layers
            sx = cs[0].size.x/1e6 if cs else 1.0
            sy = cs[0].size.y/1e6 if cs else 1.0
            pad_rects.append((px-sx/2, py-sy/2, px+sx/2, py+sy/2))

        for fp in fps:
            ref = fp.reference_field
            rn = ref.text.value
            if rn.startswith('#'): continue
            if not ref.visible: continue
            tbb = board.get_item_bounding_box(ref.text)
            tx1, ty1 = tbb.pos.x/1e6, tbb.pos.y/1e6
            tx2 = (tbb.pos.x+tbb.size.x)/1e6
            ty2 = (tbb.pos.y+tbb.size.y)/1e6
            for (px1, py1, px2, py2) in pad_rects:
                if tx1<px2 and tx2>px1 and ty1<py2 and ty2>py1:
                    errors.append(f"SILKSCREEN: {rn} ref text overlaps pad")
                    break

        return errors
