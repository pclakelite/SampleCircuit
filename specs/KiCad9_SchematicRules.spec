KiCad 9.0 Schematic Generation Rules - General Specification
==============================================================
Version: 2.0
Scope: General-purpose (applies to any KiCad 9 schematic project)

This specification ensures programmatically generated KiCad 9 schematics
are correct, neat, and free of common errors.

Device-specific pin references are maintained separately in pin reference
files. See: ../pins/ directory or project-specific .pins files.


1. KiCad 9 S-Expression Format Rules
--------------------------------------
1a. Symbol (at) MUST always have 3 parameters: (at X Y ANGLE)
    Even when angle=0, it must be explicit: (at 100 50 0)
    Omitting the angle causes a parse error.

1b. All coordinates must be numbers (int or float), no Python expressions
    like "66.03999999999999". Round to 2 decimal places max.

1c. Every placed symbol MUST have an (instances ...) block.

1d. Every lib_id referenced in a placed symbol MUST exist in lib_symbols.

1e. Every UUID must be unique across the entire file.

1f. Parentheses must be balanced across the entire file.

1g. Sub-symbols in lib_symbols must NOT have library prefix.
    Correct:   (symbol "2N7002_0_1" ...)
    Incorrect: (symbol "Transistor_FET:2N7002_0_1" ...)

1h. When inserting multi-line text as a single element into a Python list,
    the insertion offset is 1, NOT the number of newlines in the string.


2. Coordinate System and Pin Transform
----------------------------------------
2a. Symbol local coords use Y-up (positive Y = up in symbol editor).
    Schematic coords use Y-down (positive Y = down on screen).

2b. Transform formula (angle=0):
      schematic_x = symbol_x + local_x
      schematic_y = symbol_y - local_y

2c. For rotated symbols, apply rotation to local coords FIRST, then
    add to symbol position. Rotation matrix for angle A (CCW):
      rotated_x =  local_x * cos(A) + local_y * sin(A)
      rotated_y = -local_x * sin(A) + local_y * cos(A)
    Then apply Y-flip: schematic = (sym_x + rotated_x, sym_y - rotated_y)

2d. Common rotation shortcuts (local -> schematic offset):
      angle=0:   offset = (+local_x, -local_y)
      angle=90:  offset = (+local_y, +local_x)   [90 deg CCW]
      angle=180: offset = (-local_x, +local_y)
      angle=270: offset = (-local_y, -local_x)   [90 deg CW]

2e. Pin positions define where wires MUST connect. A wire endpoint that
    misses a pin by even 0.01mm will NOT create an electrical connection.


3. Standard Two-Pin Components (Device:R, Device:C, Device:L, etc.)
---------------------------------------------------------------------
3a. Device:R and Device:C both have pins at local (0, +3.81) and (0, -3.81).
    The pin offset is 3.81mm, NOT 2.54mm. Always verify from the library.

3b. At angle=0 (VERTICAL orientation):
      Pin "1" (top)    -> schematic offset (0, -3.81)
      Pin "2" (bottom) -> schematic offset (0, +3.81)

3c. At angle=90 (HORIZONTAL orientation):
      Pin "1" (left)   -> schematic offset (-3.81, 0)
      Pin "2" (right)  -> schematic offset (+3.81, 0)

3d. IMPORTANT: angle=0 means VERTICAL, angle=90 means HORIZONTAL.
    This is the opposite of what many people assume.

3e. Pullup resistors: Place vertically (angle=0).
      Pin 1 (top) -> power rail, Pin 2 (bottom) -> signal line.

3f. Pulldown resistors: Place vertically (angle=0).
      Pin 1 (top) -> signal line, Pin 2 (bottom) -> GND.

3g. Series resistors: Place horizontally (angle=90).
      Pin 1 (left) -> source, Pin 2 (right) -> destination.


4. Power Symbols (GND, +3V3, +12V, +5V, etc.)
-------------------------------------------------
4a. Power symbols have a single pin at local (0, 0).
    They connect at the symbol's (at x y) position directly.

4b. GND: Place at the bottom of vertical wires, angle=0 (arrow points down).

4c. VCC/+3V3/+12V/+5V: Place at top of vertical wires, angle=0
    (arrow points up).

4d. Place power symbols directly at pin endpoints -- do NOT leave a gap.


5. Property Text Placement (Reference and Value)
----------------------------------------------------
GENERAL RULE: Text must be placed OUTSIDE the component body bounding box,
with at least 1.27mm (half grid) margin from the body edge.

5a. Use extract_bounds.py to get the body bounding box (half_width, half_height)
    for any symbol. Text offsets are calculated from the body edge, NOT the
    component center. Formula:
      text_x = body_half_width + MARGIN    (where MARGIN >= 1.27mm)
      text_y = +-line_spacing / 2          (line_spacing = 2.54mm)

5b. Known body half-sizes (from KiCad 9 standard library):
      Device:R          half = (1.02, 2.54)
      Device:C          half = (1.02, 2.54)   [same as R]
      Q_NMOS_GSD        half = (4.45, 2.79)   [asymmetric, right-heavy]
      1N4001/1N4148W    half = (1.02, 2.54)   [same as R]
      G5LE-1 relay      half = (10.16, 5.08)  [large]
      MAX98357A         half = (10.16, 10.16) [large square IC]
      RV-3028-C7        half = (10.16, 7.62)  [medium IC]
      W25Q32JVZP        half = (10.16, 10.16) [large IC]
      Screw_Terminal_0x half = (1.27, 3.81)

5c. R/C vertical (angle=0): Place ref and value to the RIGHT of the body.
      ref_offset = (+3.81, -1.27), val_offset = (+3.81, +1.27)

5d. R/C horizontal (angle=90): Place ref ABOVE and value BELOW the body.
      ref_offset = (0, -3.81), val_offset = (0, +3.81)

5e. Transistors (SOT-23, etc.): Place text to the upper-right, clear of pins.
      ref_offset = (+5.08, -5.08), val_offset = (+5.08, -2.54)

5f. Diodes (vertical): Place text to the side with most clearance.
      ref_offset = (-5.08, -1.27) or (+5.08, -1.27)
      val_offset = (-5.08, +1.27) or (+5.08, +1.27)

5g. ICs and large symbols: Place text BELOW the body, to the right.
      ref_offset = (+body_hw, +body_hh + 1.27)
      val_offset = (+body_hw, +body_hh + 3.81)
    This avoids overlap with pins and wires on all sides.

5h. Connectors: Place text to the right of the body (pins face left).
      ref_offset = (+5.08, -2.54), val_offset = (+5.08, +2.54)

5i. Relays and multi-unit symbols: Keep text centered inside the body.
      The body is large enough to contain the ref and value.

5j. Keep text at angle=0 (horizontal) for readability unless there is
    a specific reason to rotate it.

5k. Power symbol labels: Reference should be hidden. Value text appears
    at offset (0, -2.54) above the symbol.

5l. Decoupling caps near each other: Place ref ABOVE and value BELOW
    (not to the right) to avoid text from adjacent caps overlapping.
      ref_offset = (0, -5.08), val_offset = (0, +5.08)

5m. Section spacing rule: Circuit blocks must be spaced at least 50mm
    apart (center-to-center). Measure from the RIGHTMOST element of
    one section (including labels, connectors, wires) to the LEFTMOST
    element of the next section. This prevents cross-section overlap.


6. Layout and Spacing Rules
-----------------------------
6a. GRID: All component centers and wire endpoints MUST snap to 2.54mm grid.
    (1/10 inch = standard KiCad grid)

5b. MINIMUM CLEARANCE: Components must have at least 5.08mm (2 grid units)
    between their body outlines. No overlapping symbols.

5c. WIRE ROUTING: All wires must be orthogonal (horizontal or vertical only).
    No diagonal wires. Use L-shaped or stepped routes.

5d. JUNCTIONS: Place a junction wherever 3+ wires meet at a point, or
    wherever a wire T-connects into another wire.

5e. LABELS: Net labels should be placed at the END of a wire stub,
    not floating in space. Wire from pin -> label position.

5f. SECTION HEADERS: Each circuit block should have a bold text note
    above it identifying the section.


7. Circuit Block Layout Pattern
---------------------------------
Each functional circuit block follows a consistent pattern:

6a. SECTION ORIGIN: Define a base (x, y) for each section.
    Sections should be spaced at least 50mm apart horizontally
    or 40mm apart vertically to avoid overlap.

6b. IC AT CENTER: Place the main IC at the section origin.

6c. DECOUPLING CAPS: Place VDD bypass caps near the VDD pin.
    Wire: VDD pin -> cap pin 1 (top). Cap pin 2 (bottom) -> GND.

6d. PULLUP/PULLDOWN RESISTORS: See Section 3e/3f above.

6e. SERIES RESISTORS: See Section 3g above.

6f. INPUT SIGNALS: Enter from the left via net labels.
    Output signals exit to the right.

6g. POWER RAILS: +VCC at top, GND at bottom.


8. Validation Checklist (run before saving)
---------------------------------------------
[ ] Parentheses balanced (depth == 0 at EOF)
[ ] All symbol (at) clauses have 3 numbers (x y angle)
[ ] No duplicate UUIDs
[ ] All lib_ids have matching lib_symbols entries
[ ] All placed symbols have (instances) blocks
[ ] All wire endpoints land exactly on pin positions (within 0.01mm)
[ ] No two symbol bodies overlap (bounding box check)
[ ] All coordinates rounded to 2 decimal places
[ ] All coordinates snap to 2.54mm grid
[ ] Sub-symbols have no library prefix in their names
[ ] No ref/value text overlapping component bodies (see Section 5)


9. Common Mistakes to Avoid
------------------------------
- Using +-2.54 for R/C pin offsets (actual offset is +-3.81)
- Placing R at angle=0 when horizontal is needed (angle=0 = VERTICAL)
- Placing R at angle=90 when vertical is needed (angle=90 = HORIZONTAL)
- Omitting angle in symbol (at x y) -> must be (at x y 0)
- Forgetting multi-unit symbols (e.g. relays have coil + switch units)
- Using Python float artifacts (66.03999999999) instead of round(x, 2)
- Inserting multi-line strings into line lists and miscounting offsets
- Placing power symbols with a gap from the pin (must be at exact pin position)
- Assuming pin offset = 2.54 for any 2-pin component (always extract from library)
- Forgetting (instances) block on placed symbols
- Using library prefix on sub-symbol names in lib_symbols section
- Placing ref/value text at default (0, +-2.54) offset which overlaps component bodies
- Not adjusting text offset for component orientation (horizontal vs vertical R/C)


10. How to Extract Pin Positions for New Components
-----------------------------------------------------
Before using any component for the first time, extract its pin positions
from the KiCad symbol library:

  1. Find the symbol in the .kicad_sym library file
     (typically in C:\Program Files\KiCad\9.0\share\kicad\symbols\)
  2. Locate each (pin ...) block and its (at X Y ANGLE)
  3. Record the local coordinates
  4. Apply the transform from Section 2 to get schematic offsets
  5. Add the results to a .pins file for reuse

Use extract_pins.py (if available in project) for automated extraction.
This prevents connectivity bugs caused by incorrect pin offset assumptions.


11. Script Architecture for Schematic Modification
------------------------------------------------------
When writing Python scripts to modify .kicad_sch files:

10a. Read the file into a list of lines.
10b. Find insertion points by searching for known markers:
     - lib_symbols closing bracket for adding new symbol definitions
     - (sheet_instances) line for adding placed components before it
10c. Build text blocks as multi-line strings, then insert as single elements.
10d. Offset for subsequent insertions after a multi-line insert is 1, not
     the number of newlines.
10e. Always back up the original file before writing modifications.
10f. Run validate_sch.py after every modification.
