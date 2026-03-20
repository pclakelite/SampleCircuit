KiCad 9 PCB Component Placement - General Specification
=========================================================
Version: 1.5
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

2f. MINIMUM 4 MOUNTING HOLES: Every board must have at least 4 mounting
    holes for proper mechanical support. Default placement is one hole per
    corner, inset 10mm from each edge.

2g. MOUNTING HOLES HAVE HIGHEST PLACEMENT PRIORITY: Mounting holes are
    placed BEFORE components in the placement workflow. If a component
    would conflict with a corner hole's keepout zone, the COMPONENT must
    move — not the hole. The placement algorithm must:
    1. Place all 4 corner holes first (10mm inset from each edge)
    2. Mark each hole's keepout circle as a no-go zone
    3. When placing connectors along an edge, calculate the usable edge
       length by excluding the keepout zones at each end, then distribute
       connectors evenly within the remaining space
    4. If a corner conflicts with a board cutout (e.g., antenna notch),
       shift the hole along the nearest edge until it clears — do not
       omit the hole

2h. Verification: after all placement, confirm:
    - At least 4 mounting holes exist on Edge.Cuts
    - Every hole is within 15mm of a board corner (shifted holes still
      count as "corner" holes if they are on the perimeter)
    - No component bounding box intersects any hole's keepout circle


3. Ratsnest and Routing Optimization
---------------------------------------
3a. NET-AWARE PLACEMENT PRIORITY: Before placing any component, analyze
    the netlist to identify the IC with the most non-power signal
    connections — this is the "hub" IC (typically the MCU). Place the
    hub IC first, then cluster all signal-connected ICs around it in
    order of connection density. ICs sharing high-speed buses (SPI, I2S,
    I2C, UART) with the hub MUST be placed adjacent to it.

3b. SIGNAL OVER POWER: Optimize placement for signal nets first. Power
    nets (+3.3V, +5V, +12V, etc.) are distributed by copper pour planes
    and are far less sensitive to trace distance. GND is handled entirely
    by the ground plane. Do not place a component far from its signal
    partner just to be near a power connector — the power plane will
    reach it.

3c. RATSNEST DISTANCE METRIC: After placement, compute the maximum
    pad-to-pad distance for each non-power, non-GND net. This is a
    proxy for the worst-case unrouted trace length. Flag any signal
    net exceeding 30mm as a WARNING. Signal nets exceeding 50mm
    indicate a layout problem — the connected components should be
    moved closer together.

3d. Ratsnest verification algorithm:
      from collections import defaultdict
      net_pads = defaultdict(list)
      for pad in board.get_pads():
          net = pad.net.name
          if not net or net == 'GND' or net.startswith('+'): continue
          parent = find_parent_footprint(pad)
          net_pads[net].append((parent, pad.position.x/1e6, pad.position.y/1e6))
      for net, plist in net_pads.items():
          max_dist = max(
              sqrt((x2-x1)**2 + (y2-y1)**2)
              for (r1,x1,y1), (r2,x2,y2) in combinations(plist, 2)
              if r1 != r2
          )
          if max_dist > 50: ERROR(f"{net}: {max_dist:.0f}mm")
          elif max_dist > 30: WARN(f"{net}: {max_dist:.0f}mm")

3e. ROTATION FOR ROUTING: Orient ICs so their signal pins face the
    components they connect to. Before finalizing placement, check
    whether rotating an IC by 90° or 180° would bring its bus pins
    closer to the connected ICs, reducing trace crossings and lengths.

3f. PLACEMENT ITERATION: Ratsnest optimization is iterative. After
    initial placement, review the longest signal nets and adjust
    component positions. Re-check overlaps and edge clearance after
    each adjustment. Repeat until all signal nets are below 30mm or
    at their practical minimum given physical constraints.


4. Component Overlap Prevention
---------------------------------
4a. No two component bounding boxes may overlap. This is a hard rule
    with zero exceptions.

4b. Verification: check all N*(N-1)/2 pairs of footprints:
      for i in range(len(fps)):
          for j in range(i+1, len(fps)):
              ASSERT not overlaps(bbox[i], bbox[j])

4c. Bounding box overlap test:
      def overlaps(a, b):
          return a.left < b.right and a.right > b.left \
             and a.top < b.bottom and a.bottom > b.top

4d. Minimum spacing between adjacent component bounding boxes: 0.5mm.
    This ensures silkscreen text, courtyard lines, and solder paste
    do not interfere.

4e. PAD-TO-PAD OVERLAP: No solderable pad from one component may
    overlap a solderable pad from a different component. This is
    verified separately from bounding box overlap because pads are
    smaller than bounding boxes. Use bounding box containment (not
    center distance) to assign pads to their parent footprint, as
    large ICs can have pads far from their center.

4f. After ANY placement change, re-run the full overlap check before
    committing. Fixing one overlap can introduce another.

4g. MINIMUM PAD-TO-PAD CLEARANCE (solder bridge prevention): pads
    belonging to different components must maintain a minimum edge-to-edge
    clearance to prevent solder bridging during assembly.

    Default minimum clearances:
    - 0.20mm pad-to-pad (IPC Class 2 manufacturing)
    - 0.25mm courtyard-to-courtyard (IPC-7351 nominal density)

    These values may be tightened for high-density designs (down to 0.10mm
    for IPC Class 3 / HDI), but must be explicitly documented.

    Verification algorithm: for every pad on the board, compute the
    minimum edge-to-edge distance to every pad owned by a DIFFERENT
    footprint. Report any pair below the threshold:

      MIN_PAD_GAP = 0.20  # mm
      for i in range(len(all_pads)):
          for j in range(i+1, len(all_pads)):
              if parent_fp[i] == parent_fp[j]: continue
              gap = edge_to_edge_distance(pad_bbox[i], pad_bbox[j])
              if gap < MIN_PAD_GAP:
                  ERROR(f"{ref[i]} pad <-> {ref[j]} pad: {gap:.2f}mm")

    Edge-to-edge distance between two axis-aligned rectangles:
      dx = max(0, max(a.left - b.right, b.left - a.right))
      dy = max(0, max(a.top - b.bottom, b.top - a.bottom))
      gap = sqrt(dx*dx + dy*dy)

    Note: NPTH (mounting hole) pads and pads on different board sides
    (F.Cu vs B.Cu only) may be excluded from this check.


5. Functional Grouping
------------------------
5a. Components MUST be grouped by their schematic functional block.
    Each sub-circuit's passives belong physically near the IC they
    support, not scattered across the board.

5b. Decoupling capacitors: place within 3mm of the IC power pin they
    decouple. Closer is always better. The trace from cap to IC power
    pin should be as short as possible.

5c. Feedback resistor dividers: place within 5mm of the IC feedback
    pin. Keep the voltage divider node trace short to avoid noise
    pickup.

5d. Input protection components (TVS diodes, Schottky diodes, fuses):
    place between the input connector and the circuit they protect,
    as close to the connector as possible.

5e. Signal bus grouping: components sharing a bus (SPI, I2C, I2S)
    should be physically close to minimize trace length. Shared-bus
    ICs should be placed in a cluster, not on opposite sides of the
    board.

5f. COMPACT LAYOUT: Components within a functional group should be
    placed as close together as practical — do not spread components
    to fill available board space. Target inter-component spacing of
    1–3mm within a group (enough for silkscreen text and routing, but
    no wasted space). A group's bounding area should be the minimum
    rectangle that fits all its components with routing clearance.

5g. GROUP-TO-GROUP SPACING: Adjacent functional groups should be placed
    close together with 3–5mm between groups.

5g-exception. CONNECTORS are exempt from intra-group compactness rules.
    Connectors must be placed at board edges for user access (per rule
    1d), so they will naturally be spread across the board perimeter.
    Do not flag connector-to-connector distance as a grouping violation.

5h. DEAD SPACE IS ACCEPTABLE: Empty board area on a side or corner is
    fine as long as functional groups are internally compact and placed
    close to their neighboring groups. Do not spread components apart
    just to fill available board space. Tight family grouping takes
    priority over even board utilization.

5i. BALANCE DENSITY VS MANUFACTURABILITY: Compact layout must not
    compromise solderability or inspection. Minimum spacing between
    component bounding boxes remains 0.5mm (per rule 4d). If text
    cannot fit at 0.8mm height in the available space, the layout is
    too tight — increase spacing slightly rather than hiding reference
    designators.


6. RF and Antenna Placement
-----------------------------
6a. MANUFACTURER SPECIFICATION REQUIRED: Any device with an integrated
    antenna or radio (WiFi, Bluetooth, LoRa, cellular, GPS, etc.) MUST
    be placed according to the manufacturer's antenna design guidelines.
    These guidelines define cutout dimensions, keepout zones, ground
    plane exclusions, and clearance distances specific to that device.
    Do not substitute generic rules for manufacturer specifications.

6b. Antenna placement at board edge: modules with PCB antennas should
    have their antenna at a board edge or extending beyond it, unless
    the manufacturer's guidelines specify otherwise.

6c. PCB CUTOUT: If the manufacturer specifies removing board material
    (FR4) under the antenna, create the cutout as part of the Edge.Cuts
    outline (polygon with notch), not as an internal cutout. Match the
    cutout dimensions to the manufacturer's recommended geometry.

6d. KEEPOUT ZONE around antenna: follow the manufacturer's specified
    keepout distances. At minimum, the keepout zone must exclude:
    - Copper traces, pours, and vias
    - Components and their courtyards
    - Ground plane on all copper layers
    The GND copper pour zone outline must be shaped to exclude the
    antenna keepout area.

6e. Antenna orientation: orient the module so the antenna feed point
    is closest to the board edge. Consult the device datasheet for
    which end of the module contains the antenna — it may require
    rotation from the default footprint orientation.

6f. RF noise isolation: keep high-frequency noise sources (switching
    regulators, crystals, high-speed digital) as far from the antenna
    as practical. Follow the manufacturer's recommended minimum
    separation distance; if unspecified, use 20mm as a default.

6g. CUTOUT HEALING on component move: when a component that has an
    associated board cutout (e.g., antenna notch) is repositioned,
    the board outline MUST be updated to match:
    1. Remove the old cutout segments from Edge.Cuts
    2. Restore the original straight board edge where the old cutout was
    3. Create the new cutout at the component's new position
    4. Re-verify edge clearance (rule 1b) after the update
    This applies to any board outline modification tied to a specific
    component — antenna notches, card-slot openings, connector cutouts,
    etc. Never leave an orphaned cutout at a former component position.


7. Copper Pour (Ground Planes)
--------------------------------
7a. GND copper pour should be created on both F.Cu and B.Cu for
    2-layer boards.

7b. The zone outline MUST match the board outline including any
    cutouts (antenna notches, etc.). Do not fill copper into cutout
    areas.

7c. Zone parameters:
    - Net: GND
    - Min thickness: 0.25mm
    - Clearance: 0.2mm (or per design rules)
    - Priority: 0 (lowest, so signal traces take precedence)

7d. After all placement is complete, call board.refill_zones(block=True)
    to fill the copper pour around the final component positions.

7e. Remove existing zones before re-creating them after major placement
    changes to avoid stale fill artifacts.


8. Placement Workflow
-----------------------
8a. BOARD SIZE DETERMINATION: Do NOT pre-define the board size.
    Place all components first in a compact layout, then determine
    the board dimensions:
    1. Calculate the bounding box of all placed components
    2. Add margins: 10mm on each edge for mounting hole inset
    3. Add antenna cutout depth if applicable
    4. Round BOTH width and height UP to the nearest 10mm
    This ensures the board is always the minimum practical size.

8b. The correct order for automated placement is:
    1. Remove existing board outline, copper pour zones, and holes
    2. Analyze netlist: identify hub IC and signal connections (S3)
    3. Calculate board size from component bounding box (per 8a)
    4. Create board outline (with cutouts if needed)
    5. PLACE MOUNTING HOLES FIRST at 4 corners, 10mm inset (per 2f-2g)
    6. Mark hole keepout zones as no-go areas for all subsequent steps
    7. Place the hub IC first (most signal connections)
    8. Place signal-connected ICs adjacent to hub (minimize ratsnest)
    9. Place each IC's decoupling caps and support components
    10. Place connectors at board edges — calculate usable edge length
        by excluding hole keepout zones, then distribute evenly (per 1e)
    11. Place remaining ICs grouped by function, largest first
    12. Place each IC's passives immediately after the IC
    13. Run ratsnest check — adjust positions to minimize signal distances
    14. Run overlap check — fix any violations
    15. Run mounting hole keepout check — fix any violations
    16. Run edge clearance check — fix any violations
    17. Reposition silkscreen text — fix any pad overlaps
    18. Hide value fields that cause clutter
    19. Recreate GND copper pour zones
    19. Refill zones

8c. Each functional group should be committed separately so the user
    can undo individual groups in KiCad (Ctrl+Z).

8d. After all placement, run a final comprehensive verification:
    - Zero bounding box overlaps
    - Zero pad-to-pad overlaps between different components
    - Zero mounting hole keepout violations
    - Zero edge clearance violations
    - Zero silkscreen-on-pad overlaps
    - Zero silkscreen-on-silkscreen overlaps
    - All reference designators visible
    - Connectors aligned at same edge offset with even spacing
    - All signal nets below 30mm (warn) / 50mm (error)
    - All components accounted for (none left unplaced)


9. Orientation for Routing
----------------------------
9a. Orient ICs so their most-connected pins face toward the components
    they connect to. Example: SPI bus pins toward flash/SD card.

9b. Orient passive components (0805, 0603, etc.) so their pads align
    with the traces that will connect them. Vertical (90°) when the
    trace runs vertically, horizontal (0°) when horizontal.

9c. Orient all similar passives consistently within a functional group
    (e.g., all feedback resistors at 90°). This aids visual inspection
    and assembly.

9d. Power flow should be left-to-right or top-to-bottom across the
    board. Place voltage regulators in the order of the power chain
    (e.g., 24V->12V->5V->3.3V left to right).


10. Silkscreen Text Management
--------------------------------
10a. NO SILKSCREEN TEXT ON SOLDERABLE PADS. Reference designators and
    value text must never overlap any pad on the board. This applies
    to pads on the same component AND on adjacent components.

10b. Reference designators (annotations) are MANDATORY. Every component
    must have a visible reference designator (e.g., R1, U1, C1). These
    may be repositioned or resized but NEVER hidden or deleted.

10c. Value/part number text may be hidden if it causes overlap or visual
    clutter. If the value field cannot be placed without overlapping
    pads or other text, hide it (set visible = False). The reference
    designator is the minimum required visible text per component.

10d. Text repositioning algorithm — when a reference designator overlaps
    a pad or another silkscreen text, reposition using this cascading
    strategy:

    STEP 1 — Try all 4 positions at current text size (0.8mm default):
      1. Above the component bounding box
      2. Below the component bounding box
      3. Right of the component bounding box
      4. Left of the component bounding box
    For each candidate, offset the text center by gap + text_height/2
    (above/below) or gap + text_width/2 (left/right), where gap >= 0.3mm.
    Try increasing gap distances (1x, 2x, 3x, 5x) at each position.
    Accept the first position that does not overlap any pad or other
    visible silkscreen text.

    STEP 2 — Try all positions with rotation (0° and 90°):
    If no position works at step 1, rotate the text 90° and retry all
    positions and gap distances. This changes the text's width/height
    ratio and may fit where the original orientation could not.

    STEP 3 — Reduce text size and retry:
    ONLY after exhausting all positions, rotations, and gap distances
    at full size, reduce text size by 0.2mm (0.8 -> 0.6 -> 0.5mm
    minimum) and repeat steps 1-2. Do not go below 0.5mm height.
    Shrinking is a LAST RESORT, not a first option.

    If all attempts fail, flag the component for manual review.

10e. Verification: check every visible text field against all pad rects:
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

10f. NO SILKSCREEN TEXT OVERLAPPING OTHER SILKSCREEN TEXT. Visible
    reference designators must not overlap each other. The repositioning
    algorithm (10d) must check candidate positions against both pads AND
    all other visible silkscreen text bounding boxes.

10g. Text sizing: silkscreen text may be reduced to fit tight areas,
    but must not go below 0.5mm height (minimum readable size for
    standard PCB fabrication). Preferred default is 0.8mm; 1.0mm for
    spacious areas.

10h. Text orientation: keep text readable (0° or 90°). Use the same
    orientation as the component where possible. Within a functional
    group, orient all reference text consistently.


11. IPC API Coordinate System
--------------------------------
11a. All coordinates are in nanometers. 1mm = 1,000,000 nm.
     Helper: Vector2.from_xy(int(x_mm * 1e6), int(y_mm * 1e6))

11b. KiCad board origin is typically at (100mm, 50mm). X increases
     right, Y increases down.

11c. Rotation: 0° = default orientation. Use Angle.from_degrees().
     Positive angles rotate counter-clockwise.

11d. Commit system: always wrap placement in begin_commit/push_commit
     with try/except/drop_commit for rollback on error.


12. Verification Script Template
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
