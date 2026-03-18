# =============================================================================
# TEMPLATE CREATION SPECIFICATION
# =============================================================================
# How to build KiCad 9.0 hierarchical sheet circuit templates for this project.
# Follow this spec exactly â€” deviations cause broken schematics.
#
# Project: CircuitAI (KiCad project file: AITestProject.kicad_pro)
# KiCad Version: 9.0 (file format version 20231120)
# Python: C:/Users/peter.LAKEMAST/AppData/Local/Python/bin/python.exe
# Date: March 2026


# =============================================================================
# 1. CONCEPT
# =============================================================================
# Each template is a self-contained circuit module (e.g., RTC, relay driver,
# audio amp, PSU) stored as a KiCad hierarchical sheet. Templates are designed
# to be imported into a parent schematic via KiCad's "Add Hierarchical Sheet"
# feature. The parent sheet connects to the template via hierarchical labels.
#
# AI generates: spec, component placement, first-pass wiring, BOM, verification
# Human reviews/fixes: wiring, spacing, cosmetic cleanup in KiCad


# =============================================================================
# 2. FOLDER STRUCTURE
# =============================================================================
# templates/
#   TemplateCreation.spec          <-- THIS FILE (read first!)
#   rtc_rv3028/                    <-- Example template
#     rtc_rv3028.spec              <-- Circuit specification
#     rtc_rv3028.kicad_sch         <-- KiCad schematic (placed + first-pass wired)
#     build_rtc_template.py        <-- Python script that generates the .kicad_sch
#
# Each template gets its own subfolder. All files for that template live inside
# that subfolder â€” keep everything self-contained.
#
# Required files per template:
#   1. <name>.spec          â€” Circuit specification (components, nets, wiring guide)
#   2. <name>.kicad_sch     â€” Generated KiCad schematic with components placed
#   3. build_<name>.py      â€” Python script that generates the .kicad_sch
#
# The .spec is the source of truth. The .kicad_sch is generated from it.


# =============================================================================
# 3. ALL COMPONENTS MUST COME FROM JLCPCB (JLCImport)
# =============================================================================
# DO NOT use KiCad built-in symbols (Device:R, Device:C, etc.)
# ALL symbols, footprints, and 3D models must come from JLCPCB via jlcimport-cli.
#
# Why: Ensures exact part matching for JLCPCB assembly, includes 3D models,
# and eliminates any ambiguity about which physical part is being used.
#
# Import command:
#   "C:\Users\peter.LAKEMAST\Downloads\jlcimport-cli\jlcimport-cli\jlcimport-cli.exe" \
#     import <LCSC_PART_NUMBER> \
#     -p "c:\Projects\CircuitAI" \
#     --kicad-version 9
#
# This downloads symbol, footprint, and 3D model into the project-level
# JLCImport library:
#   JLCImport.kicad_sym           â€” Symbol library (project root)
#   JLCImport.pretty/             â€” Footprint library (project root)
#   JLCImport.3dshapes/           â€” 3D models STEP + WRL (project root)
#
# 3D MODEL PATH WARNING: Footprint .kicad_mod files reference 3D models as
#   ${KIPRJMOD}/JLCImport.3dshapes/<part>.wrl
# This works for projects at the repo root, but NOT for projects in subfolders
# (e.g., templates/sample_board/). When generating a PCB in a subfolder, you
# MUST fix 3D model paths to use relative traversal (../../). See PCBLayout.spec
# section 16 for details.
#
# IMPORTANT: Run the import command for EVERY component before generating
# the schematic. The import is idempotent â€” it skips existing parts.


# =============================================================================
# 4. COMMON JLCPCB PASSIVE PARTS (reuse these across templates)
# =============================================================================
# These are JLCPCB Basic parts (no extra fee). Use these unless the circuit
# requires a specific different value.
#
# Resistors (0805, 1%, UNI-ROYAL):
#   100R  â€” C17408  â€” JLCImport:0805W8F1000T5E
#   1K    â€” C17513  â€” JLCImport:0805W8F1001T5E
#   4.7K  â€” C17673  â€” JLCImport:0805W8F4701T5E
#   10K   â€” C17414  â€” JLCImport:0805W8F1002T5E
#   100K  â€” C17407  â€” JLCImport:0805W8F1003T5E
#
# Capacitors (0805, YAGEO):
#   100nF â€” C49678  â€” JLCImport:CC0805KRX7R9BB104
#   10uF  â€” C15850  â€” JLCImport:CC0805MKX5R8BB106 (or check current stock)
#   1uF   â€” C28323  â€” JLCImport:CC0805KRX7R7BB105
#
# Diodes:
#   1N4148W â€” C2099  â€” JLCImport:1N4148W (SOD-123, flyback/signal)
#
# MOSFETs:
#   2N7002  â€” C8545  â€” JLCImport:2N7002 (SOT-23, N-ch, relay driver)
#
# NOTE: JLCImport symbol names match the manufacturer part number, NOT the
# generic value. The "Value" property on the schematic instance should be
# set to the human-readable value (e.g., "10k", "100nF").
#
# MINIMUM PACKAGE SIZE: All SMD passives (resistors, capacitors, inductors)
# must be 0805 or larger. DO NOT use 0402 or 0603 packages â€” they are too
# small for hand rework and visual inspection. Larger packages (1206, 1210,
# etc.) are acceptable when required by voltage/current rating.


# =============================================================================
# 5. KICAD SCHEMATIC FORMAT â€” CRITICAL RULES
# =============================================================================
# These rules were learned from bugs. Violating them produces broken schematics.
#
# 5A. FILE STRUCTURE
# ------------------
# (kicad_sch
#   (version 20231120)
#   (generator "build_<name>.py")
#   (generator_version "1.0")
#   (uuid "<SCHEMATIC_ROOT_UUID>")        <-- One UUID for the whole schematic
#   (paper "A4")
#
#   (lib_symbols                           <-- MUST contain cached symbol defs
#     (symbol "JLCImport:<SymbolName>"     <-- One per unique lib_id used
#       ...full symbol definition...
#     )
#   )
#
#   (symbol ...)                           <-- Component instances
#   (hierarchical_label ...)               <-- Interface ports
#
#   (sheet_instances
#     (path "/" (page "1"))
#   )
# )
#
# 5B. lib_symbols SECTION â€” MUST BE POPULATED
# --------------------------------------------
# The lib_symbols section MUST contain a cached copy of every symbol definition
# used by component instances in the schematic. If this section is empty,
# KiCad shows red boxes with "??" instead of proper symbols.
#
# To get the symbol definition:
#   1. Open JLCImport.kicad_sym in the project root
#   2. Find the (symbol "<PartName>" ...) block for each component
#   3. Copy the ENTIRE block into lib_symbols
#   4. Prefix the symbol name with "JLCImport:" in lib_symbols
#      e.g., (symbol "0805W8F1001T5E" ...) becomes
#            (symbol "JLCImport:0805W8F1001T5E" ...)
#   5. Sub-symbol names do NOT get the prefix
#      e.g., (symbol "0805W8F1001T5E_0_1" ...) stays as-is
#
# 5C. INSTANCE PATHS â€” MUST MATCH ROOT UUID
# ------------------------------------------
# Every symbol instance has an (instances ...) block with a path.
# The path MUST be "/<SCHEMATIC_ROOT_UUID>" â€” the same UUID from the
# top-level (uuid ...) field.
#
# WRONG (random UUID per instance â€” references show as "?"):
#   (instances
#     (project "AITestProject"
#       (path "/a1b2c3d4-random-uuid-here"
#         (reference "R1") (unit 1)
#       )
#     )
#   )
#
# CORRECT (uses schematic root UUID â€” references resolve properly):
#   (instances
#     (project "AITestProject"
#       (path "/57cbccc0-4dfd-4b96-9673-3939a22818a6"
#         (reference "R1") (unit 1)
#       )
#     )
#   )
#
# 5D. SYMBOL PLACEMENT
# ---------------------
# (at x y angle) â€” angle is REQUIRED, even if 0
#   angle=0   means default orientation (varies by symbol)
#   angle=90  means rotated 90 degrees counterclockwise
#
# JLCImport R/C symbols are HORIZONTAL by default (pins at Â±5.08, y=0)
# This is different from KiCad Device:R/C which are vertical.
# User will rotate as needed during wiring.
#
# 5E. PROJECT NAME
# ----------------
# Use "AITestProject" as the project name in all instances blocks.
# This matches the .kicad_pro file name.


# =============================================================================
# 6. POWER SYMBOLS (NOT hierarchical labels)
# =============================================================================
# DO NOT use hierarchical labels for power (VDD, GND, +12V, etc.)
# USE KiCad power symbols instead: power:+3.3V, power:GND, power:+12V, etc.
#
# Why: Power symbols are GLOBAL â€” they automatically connect across all sheets
# in the hierarchy. This is cleaner than routing power through hierarchical
# labels. It also matches standard KiCad schematic style.
#
# Power symbols to use (from KiCad built-in "power" library):
#   +3.3V   â€” 3.3V rail (most circuits)
#   +5V     â€” 5V rail
#   +12V    â€” 12V rail
#   GND     â€” Ground
#
# 6A. POWER SYMBOL lib_symbols
# ----------------------------
# Power symbols ALSO need cached definitions in lib_symbols, just like
# JLCImport parts. Extract from:
#   "C:\Program Files\KiCad\9.0\share\kicad\symbols\power.kicad_sym"
#
# In lib_symbols, prefix with "power:":
#   (symbol "power:+3.3V" (power) ...)
#   (symbol "power:GND" (power) ...)
#
# Sub-symbols do NOT get the prefix (same rule as JLCImport):
#   (symbol "+3.3V_0_1" ...)   <-- NO prefix
#   (symbol "GND_1_1" ...)     <-- NO prefix
#
# 6B. POWER SYMBOL INSTANCES
# --------------------------
# Place as regular symbol instances with lib_id "power:+3.3V" or "power:GND".
# Use hidden references: "#PWR01", "#PWR02", etc. (one per instance).
# Each GND/+3.3V placed at a different location needs its own instance.
#
# Connection point is at the symbol's (at x y) position.
# +3.3V: graphic arrow points UP, connection pin at bottom
# GND: graphic triangle points DOWN, connection pin at top
#
# Example +3.3V instance:
#   (symbol
#     (lib_id "power:+3.3V")
#     (at 165.24 90 0)
#     (unit 1)
#     (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
#     (uuid "...")
#     (property "Reference" "#PWR01"
#       (at 165.24 93.81 0)
#       (effects (font (size 1.27 1.27)) hide)
#     )
#     (property "Value" "+3.3V"
#       (at 165.24 86.44 0)
#       (effects (font (size 1.27 1.27)))
#     )
#     (property "Footprint" "" (at 165.24 90 0)
#       (effects (font (size 1.27 1.27)) hide)
#     )
#     (instances (project "AITestProject"
#       (path "/<ROOT_UUID>" (reference "#PWR01") (unit 1))
#     ))
#   )
#
# 6C. MULTIPLE GND SYMBOLS
# -------------------------
# Place a separate GND symbol at each ground connection point.
# Each gets a unique #PWR reference (#PWR02, #PWR03, etc.) and UUID.
# KiCad treats them all as the same global "GND" net.


# =============================================================================
# 7. SIGNAL PORTS (custom port symbols for inter-sheet connections)
# =============================================================================
# Use CUSTOM PORT SYMBOLS from the project's Ports.kicad_sym library for
# signal connections between sheets (SCL, SDA, MOSI, etc.)
#
# DO NOT use global_label or hierarchical_label â€” they render with wires
# passing through the label text, looking messy. Port symbols render as
# clean hexagonal flags with centered text and no overlap.
#
# Port symbols work like power symbols â€” they use the (power) flag so the
# Value property creates a global net that auto-connects across all sheets.
#
# 7A. PORT LIBRARY: Ports.kicad_sym (project root)
# -------------------------------------------------
# Registered in sym-lib-table as "Ports". Each signal gets its own symbol.
# To add a new port (e.g., MOSI), add a new symbol to Ports.kicad_sym
# following the same structure as the existing SCL/SDA symbols.
#
# 7B. PORT SYMBOL STRUCTURE
# -------------------------
# Each port symbol has:
#   - (power) flag â€” creates a global net from the Value property
#   - Hexagonal polyline shape with background fill (in _0_1 sub-symbol)
#   - NO custom (text ...) element â€” the Value property IS the displayed text
#   - Single pin at local (2.54, 0) â€” connection point at the right tip
#   - Hidden Reference (#PORT01, #PORT02, etc.)
#   - VISIBLE Value property positioned at hexagon center (-1.905, 0)
#     KiCad ALWAYS renders Value on (power) symbols (see gotcha #16)
#   - in_bom no, on_board no (not physical components)
#
# 7C. PLACEMENT
# -------------
# The pin is at local (2.54, 0), so the connection point in schematic
# coordinates is at (symbol_x + 2.54, symbol_y).
# Place the symbol so the pin lands on the wire start point:
#   symbol_x = wire_start_x - 2.54
#   symbol_y = wire_start_y
#
# Place ports on the LEFT side of the sheet, spaced vertically.
# Each port instance needs a unique #PORT reference (#PORT01, #PORT02, etc.)
#
# 7D. lib_symbols CACHE
# ---------------------
# Like all symbols, port definitions MUST be cached in the schematic's
# lib_symbols section, prefixed with "Ports:" (e.g., "Ports:SCL").
# Sub-symbols do NOT get the prefix (e.g., "SCL_0_1", "SCL_1_1").
#
# 7E. COMMON SIGNAL PORTS
# -----------------------
#   SCL, SDA       â€” I2C bus
#   MOSI, MISO, SCK, CS â€” SPI bus
#   TX, RX         â€” UART
#   GPIO_xx        â€” General purpose IO
#   RELAY_CTL      â€” Control signals
#   SPK+, SPK-     â€” Speaker output
#
# Internal nets (VBACKUP, EVI_INT, etc.) stay INSIDE the template.
# Do NOT create port symbols for internal nets.


# =============================================================================
# 8. FIRST-PASS WIRING, NO-CONNECTS, AND JUNCTIONS
# =============================================================================
# The generated schematic should include a first-pass wiring attempt.
# This won't be perfect â€” the human will review and fix in KiCad â€” but it
# saves significant time vs placing components with no wires at all.
#
# 8A. WIRE FORMAT
# ---------------
#   (wire (pts (xy x1 y1) (xy x2 y2))
#     (stroke (width 0) (type default))
#     (uuid "<unique-uuid>")
#   )
#
# Wires are point-to-point. For L-shaped routes, use two wire segments.
# Wire endpoints MUST exactly match pin endpoints for connections to work.
#
# 8B. PIN ENDPOINT CALCULATION
# ----------------------------
# For a symbol placed at (sx, sy, angle=0):
#   Pin endpoint = (sx + pin_local_x, sy - pin_local_y)
#   (KiCad schematic Y increases downward, symbol Y increases upward)
#
# JLCImport R/C horizontal (angle=0):
#   Pin 1: (center_x - 5.08, center_y)    â€” left
#   Pin 2: (center_x + 5.08, center_y)    â€” right
#
# JLCImport R/C vertical (angle=90, CCW rotation):
#   Pin 1: (center_x, center_y + 5.08)    â€” bottom
#   Pin 2: (center_x, center_y - 5.08)    â€” top
#
# JLCImport R/C vertical (angle=270, CW rotation):
#   Pin 1: (center_x, center_y - 5.08)    â€” top
#   Pin 2: (center_x, center_y + 5.08)    â€” bottom
#
# Use angle=270 for capacitors so pin 1 is on TOP (connects to signal)
# and pin 2 is on BOTTOM (connects to GND below).
#
# 8C. NO-CONNECT FLAGS
# --------------------
# Place on unused pins (e.g., CLKOUT, INT# on RTC):
#   (no_connect (at x y)
#     (uuid "<unique-uuid>")
#   )
# Coordinates must match the pin endpoint exactly.
#
# 8D. JUNCTIONS
# -------------
# Place where a wire branches (T-junction):
#   (junction (at x y)
#     (diameter 0)
#     (color 0 0 0 0)
#     (uuid "<unique-uuid>")
#   )
#
# 8E. COMPONENT SPACING GUIDELINES
# ---------------------------------
# - IC to passive: minimum 15mm between centers
# - Passive to passive: minimum 12mm between centers
# - Leave 8-10mm between GND symbol and component pin for vertical wires
# - Leave 5-8mm vertical gap between +3.3V symbol and IC power pin
# - Hierarchical labels: place at x â‰ˆ 118, with 2.54mm vertical spacing
# - Group related components (e.g., R46 â†’ B3 on same horizontal line)
#
# 8F. LAYOUT PATTERN
# ------------------
# Standard template layout (left to right):
#   [Labels] â†â€”wiresâ€”â†’ [IC center] â†â€”wiresâ€”â†’ [Passives] â†â€”â†’ [More passives]
#       â†•                   â†•                      â†•
#   (signals)           (+3.3V/GND)             (GND symbols)
#
# Place the main IC at approximately (150, 100) on an A4 sheet.
# Signals enter from the left, power symbols above/below IC.
# Passive chains extend to the right.


# =============================================================================
# 9. SPEC FILE FORMAT
# =============================================================================
# Each template needs a .spec file documenting the circuit. Follow this structure:
#
# Required sections:
#   - OVERVIEW: What the circuit does, 1-3 sentences
#   - DESIGN NOTES: Key decisions, unused pins, gotchas
#   - HIERARCHICAL SHEET PORTS: Table of interface labels
#   - INTERNAL NETS: Nets that stay inside the sheet
#   - COMPONENTS: Full BOM with LCSC numbers, values, packages, pin connections
#   - JLCPCB BOM SUMMARY: Quick reference table
#   - KICAD LAYOUT INSTRUCTIONS: Step-by-step wiring guide for the human
#   - VERIFICATION CHECKLIST: Checkbox list to verify after wiring
#
# See templates/rtc_rv3028/rtc_rv3028.spec for a complete example.


# =============================================================================
# 10. BUILD SCRIPT STRUCTURE
# =============================================================================
# The Python build script generates the .kicad_sch. Key requirements:
#
#   - Output path: writes to same directory as the script (os.path.dirname(__file__))
#   - Must generate unique UUIDs (import uuid; str(uuid.uuid4()))
#   - BUT the root schematic UUID should be FIXED (hardcoded) so instance paths
#     don't change on regeneration. Pick one UUID and keep it.
#   - Must embed full lib_symbols (read from JLCImport.kicad_sym)
#   - All instance paths use the root UUID
#
# Recommended approach: Build scripts MUST read symbol definitions from
# the actual library files at build time:
#   - JLCImport symbols: read from JLCImport.kicad_sym at project root
#   - Port symbols: read from Ports.kicad_sym at project root
#   - Power symbols: hardcoded is OK (they rarely change)
#
# DO NOT hardcode JLCImport or Port symbol definitions in build scripts.
# If the user edits a symbol in KiCad's Symbol Editor, the build script
# must pick up those changes automatically on the next run.


# =============================================================================
# 11. STEP-BY-STEP PROCESS FOR CREATING A NEW TEMPLATE
# =============================================================================
#
# Step 0: Check the reference folder (MANDATORY)
#   ALWAYS read the reference schematics in AIreference/ BEFORE designing
#   a new template. The reference folder contains the original EV4-PDS
#   schematics (PNG images, netlist, Altium source) that this project is
#   recreating in KiCad. Check for:
#     - Existing circuit topology for the subsystem you are building
#     - Component values, part numbers, and design decisions
#     - Pin assignments and net names used in the original design
#     - Notes and annotations from the original designer
#   Files:
#     AIreference/schematic_page_1.png  -- ESP32, RTC, I2C, flash, audio
#     AIreference/schematic_page_2.png  -- Power supply, AC input, buck regs
#     AIreference/schematic_page_3.png  -- Speaker, LED driver, relay, IO
#     AIreference/schematic_page_4.png  -- Front panel, button/LED debounce
#     AIreference/EV4-PDS.asc          -- Altium ASCII schematic source
#     AIreference/EV4-PDS NETLIST.net   -- Netlist for cross-referencing
#   If the reference has a circuit for the subsystem, match its topology
#   unless the user explicitly requests a different design.
#
# Step 1: Create the folder
#   templates/<circuit_name>/
#
# Step 2: Import ALL components from JLCPCB
#   Run jlcimport-cli for every LCSC part number. This populates the shared
#   JLCImport library at project root.
#
# Step 3: Read the imported symbol definitions
#   Open JLCImport.kicad_sym and extract the (symbol ...) blocks for each
#   component you imported. Note the exact symbol names.
#
# Step 4: Write the .spec file
#   Document the complete circuit: components, nets, wiring, verification.
#   This is the source of truth. Follow the format in section 7.
#
# Step 5: Write the build script or .kicad_sch directly
#   Generate the .kicad_sch with:
#   - Populated lib_symbols (JLCImport parts + power symbols from step 3)
#   - All component instances placed with good spacing (see section 8E)
#   - Power symbols (+3.3V, GND) placed near power pins
#   - Hierarchical labels for signals only (SCL, SDA, etc.)
#   - No-connect flags on unused pins
#   - First-pass wiring: wires, junctions (see section 8)
#   - Correct instance paths using root UUID
#
# Step 6: Run the build script (if using one)
#   cd templates/<circuit_name>
#   python build_<name>.py
#
# Step 7: Verify in KiCad
#   Open the .kicad_sch â€” all symbols should render with proper ref designators.
#   No red boxes, no "?" references. Wires should connect to pin endpoints.
#
# Step 8: Hand off to human for review
#   Human opens in KiCad, verifies wiring, adjusts spacing, fixes any
#   missed connections. Much faster than wiring from scratch.


# =============================================================================
# 12. REFERENCE: EXISTING TEMPLATES
# =============================================================================
#
# Completed templates (LOCKED):
#   rtc_rv3028/          - RV-3028-C7 I2C RTC with coin cell backup
#   psu_lmzm23601_5v/   - LMZM23601 12V to 5V buck regulator
#   psu_lmzm23601_3v3/  - LMZM23601 12V to 3.3V buck regulator (with input protection)
#   audio_max98357/      - MAX98357A I2S DAC+amplifier + speaker output
#   flash_csnp1g/        - CSNP1GCR01-BOW 1Gbit NAND flash (SPI mode)
#
# In progress:
#   supervisor_tlv803s/  - TLV803S voltage supervisor (status: review)
#
# Planned templates (from EV4 spec):
#   relay_driver/    - G5LE-1 relay + 2N7002 MOSFET driver + flyback diode
#   esp32s3_core/    - ESP32-S3-WROOM-1 minimum circuit (reset, boot, USB)
#   usb_ch340n/      - CH340N USB-UART bridge


# =============================================================================
# 13. GOTCHAS AND LESSONS LEARNED
# =============================================================================
#
# 1. EMPTY lib_symbols = BROKEN SCHEMATIC
#    KiCad REQUIRES cached symbol definitions. No exceptions.
#
# 2. RANDOM INSTANCE PATHS = "?" REFERENCES
#    Every instance path must be "/<root_uuid>", not a random UUID.
#
# 3. JLCImport R/C ARE HORIZONTAL
#    JLCImport resistors/capacitors have pins at (Â±5.08, 0) â€” horizontal.
#    KiCad Device:R/C have pins at (0, Â±3.81) â€” vertical.
#    Layout accordingly or let the human rotate during wiring.
#
# 4. JLCImport SYMBOL NAMES = MANUFACTURER PART NUMBERS
#    e.g., "0805W8F1001T5E" not "R_1K". Set the "Value" property to the
#    human-readable value ("1k", "100nF") on the instance, not the lib_symbol.
#
# 5. SUB-SYMBOL NAMES DON'T GET LIB PREFIX
#    In lib_symbols: (symbol "JLCImport:0805W8F1001T5E" ...)
#    Sub-symbol:     (symbol "0805W8F1001T5E_0_1" ...)   <-- NO prefix
#
# 6. ALWAYS IMPORT BEFORE GENERATING
#    The jlcimport-cli must run first to populate JLCImport.kicad_sym.
#    The build script reads from this file.
#
# 7. ONE JLCImport LIBRARY FOR ALL TEMPLATES
#    All templates share the same JLCImport.kicad_sym at project root.
#    Parts imported for one template are available to all others.
#
# 8. POWER = POWER SYMBOLS, NOT HIERARCHICAL LABELS
#    Use power:+3.3V and power:GND symbols. They are global across hierarchy.
#    Do NOT use hierarchical labels for VDD/GND â€” that's the old style.
#
# 9. POWER SYMBOLS NEED lib_symbols TOO
#    Just like JLCImport parts, power:+3.3V and power:GND need cached
#    definitions in the lib_symbols section. Extract from KiCad's
#    power.kicad_sym library. Include the (power) flag in the definition.
#
# 10. WIRE ENDPOINTS MUST MATCH PIN ENDPOINTS EXACTLY
#     A wire that doesn't touch a pin endpoint won't connect.
#     Calculate pin positions carefully using section 8B formulas.
#     Round to 2 decimal places max.
#
# 11. USE angle=270 FOR VERTICAL CAPS (pin 1 top, pin 2 bottom)
#     This puts pin 1 (signal) on top and pin 2 (GND) on bottom.
#     angle=90 puts pin 1 on bottom â€” usually wrong for decoupling caps.
#
# 12. EACH GND SYMBOL NEEDS UNIQUE #PWR REFERENCE
#     Multiple GND symbols = multiple instances, each with #PWR01, #PWR02, etc.
#     Same for multiple +3.3V symbols. All connect to the same global net.
#
# 13. NO COMMENTS IN .kicad_sch FILES
#     KiCad's S-expression parser does NOT support comments of any kind.
#     No ;; comments, no # comments, no // comments. The file must contain
#     ONLY valid S-expressions. Comments will cause a parse error.
#
# 14. HIDE PIN NUMBERS AND NAMES ON JLCImport PASSIVE SYMBOLS
#     Many JLCImport symbols have visible pin numbers/names by default.
#     These "1" and "2" labels overlap and clutter the schematic
#     (e.g., "21" behind a battery symbol).
#     Fix: Add BOTH to the lib_symbol definition:
#       (symbol "JLCImport:CR2032-BS-2-1"
#         (pin_numbers (hide yes))              <-- HIDE PIN NUMBERS
#         (pin_names (offset 1.016) (hide yes)) <-- HIDE PIN NAMES
#         ...
#     Per-pin (hide) in (number ...) effects is NOT sufficient in KiCad 9.
#     You MUST use symbol-level (pin_numbers (hide yes)) to actually suppress
#     the display. Add this to ALL JLCImport symbols in lib_symbols:
#     resistors, capacitors, batteries, connectors, etc.
#     For ICs with named pins (like RV-3028-C7), hide pin_numbers but
#     KEEP pin_names visible so SCL/SDA/VDD etc. are readable.
#
# 15. USE PORT SYMBOLS, NOT GLOBAL/HIERARCHICAL LABELS
#     DO NOT use global_label or hierarchical_label for signal connections.
#     global_label causes wire-through-text visual artifacts.
#     hierarchical_label renders as tiny unreadable flags.
#     ALWAYS use custom port symbols from the Ports library (see section 7).
#     Port symbols render as clean hexagonal flags with centered text.
#
# 16. POWER/PORT INSTANCE VALUE MUST BE VISIBLE
#     When placing a (power) or port symbol INSTANCE in the schematic,
#     the instance's Value property MUST NOT have "hide". The instance
#     property overrides the lib_symbol definition. If you set hide on
#     the instance Value, the label text disappears even though the
#     lib_symbol has it visible. This applies to both make_power() and
#     make_port() helper functions in build scripts.
#
# 17. POWER SYMBOL VALUE IS ALWAYS VISIBLE â€” NO CUSTOM TEXT ELEMENT
#     KiCad ALWAYS renders the Value property on (power) symbols, even if
#     you set (hide yes). If you ALSO add a custom (text "SCL" ...) graphic
#     inside the symbol, BOTH will render â€” creating a doubled/ghosted look.
#     FIX: Use the Value property as the displayed text (set position, make
#     visible). Do NOT add a separate (text ...) element in the sub-symbol.
#     This matches how KiCad built-in power symbols (+3.3V, GND) work.
#
# 18. REGEX FOR NESTED S-EXPRESSIONS â€” MATCH FULL NESTING
#     When using regex to modify lib_symbol properties like (pin_names ...),
#     remember that KiCad S-expressions have NESTED PARENS:
#       (pin_names (offset 1.016))    <-- TWO closing parens
#     WRONG regex: r'\(pin_names[^)]*\)'  â€” matches only to the inner ),
#       leaving an extra ) that breaks the parent (symbol ...) block.
#     RIGHT regex: r'\(pin_names\s*\([^)]*\)\)'  â€” matches the full expression
#       including the nested (offset ...) sub-expression.
#     An unmatched ) causes "Expecting 'symbol'" parse errors in KiCad.
#
# 19. ALL COORDINATES MUST BE ON THE 1.27mm (50 mil) GRID
#     Every component center, wire endpoint, label position, and power
#     symbol position MUST be a multiple of 1.27mm. This ensures:
#       - Wires snap cleanly to pins in the KiCad schematic editor
#       - No off-grid frustration during human review/wiring
#       - Consistent spacing across all templates
#
#     WRONG: (at 150 100 0)     â€” 150/1.27=118.11, 100/1.27=78.74 (off grid)
#     RIGHT: (at 149.86 100.33 0) â€” 149.86/1.27=118, 100.33/1.27=79 (on grid)
#
#     Use this formula in build scripts:
#       def snap(val, grid=1.27):
#           return round(round(val / grid) * grid, 2)
#
#     For cleaner numbers, use 2.54mm spacing between components (every
#     2.54mm position is also on the 1.27mm grid). Common grid-aligned
#     reference points:
#       99.06, 101.60, 104.14, 106.68, 109.22, 111.76, 114.30,
#       116.84, 119.38, 121.92, 124.46, 127.00, 129.54, 132.08,
#       134.62, 137.16, 139.70, 142.24, 144.78, 147.32, 149.86,
#       152.40, 154.94, 157.48, 160.02, 162.56, 165.10, 167.64
#
#     The KiCad schematic editor grid should be set to 50 mils (1.27mm)
#     for wiring (Preferences > Schematic Editor > Grids, or Alt+1).

#
# 20. COMPONENT SUBSTITUTION RULES
#     ALLOWED without asking: Substituting a different manufacturer's part
#     with the SAME value AND SAME (or larger) package size. For example,
#     swapping one 680uF 35V SMD electrolytic for another brand's 680uF 35V
#     SMD electrolytic is fine â€” the circuit behavior is identical.
#
#     REQUIRES explicit user approval:
#       - Changing component VALUES (e.g., 100k â†’ 10k, 47uF â†’ 22uF)
#       - Using a SMALLER package size (e.g., 0805 â†’ 0603)
#       - Removing components from the design
#       - Changing the circuit topology
#
#     If a component is not found in JLCImport or jlcimport-cli fails:
#       1. Try to find a same-value, same-or-larger-package substitute
#       2. If no substitute exists, report the missing part to the user
#       3. Wait for explicit approval before ANY design changes
#     Acceptable: manually add the symbol by copying an existing same-package
#     symbol from JLCImport.kicad_sym and changing the part numbers.
#
# 21. JLCImport PIN ENDPOINT FORMULA (CORRECTED â€” verified against RV-3028)
#     The (at px py) in a KiCad lib_symbol pin definition IS the wire
#     connection endpoint. Do NOT subtract pin length â€” it is already
#     accounted for in the (at) coordinates.
#
#     In schematic coordinates (symbol placed at sx, sy, angle=0):
#       endpoint = (sx + px, sy - py)
#
#     The Y-negation is because schematic Y increases downward but
#     lib_symbol Y increases upward.
#
#     WRONG (old bug): endpoint_x = sx + px - length * cos(angle)
#     RIGHT:           endpoint_x = sx + px
#
#     Example: MAX98357A pin DIN at (-16.51, 8.89), symbol at (152.40, 101.60)
#       endpoint = (152.40 + (-16.51), 101.60 - 8.89) = (135.89, 92.71)
#
# 22. BUILD SCRIPT REUSABLE PATTERNS
#     Every build script should use these proven helper functions:
#       extract_symbol(content, sym_name): Extract (symbol ...) block by name
#       read_lib_symbols(): Read JLCImport symbols, add prefix, hide pin numbers
#       read_port_symbols(): Read Ports.kicad_sym, add Ports: prefix
#       make_component(): Place an IC/passive with ref/val properties
#       make_power(): Place power symbol (+3.3V/GND) with explicit positions
#       make_port(): Place port symbol (DIN, SCL, etc.) with Value visible
#       wire(x1,y1,x2,y2): Generate a wire segment with UUID
#     Copy these from the rtc_rv3028 or audio_max98357 build scripts.
#
# 23. FILE FORMAT VERSION
#     KiCad 9.0 schematic format version is 20250114 (not 20231120).
#     Generator version should be "9.0".
#     File must end with (embedded_fonts no) before the closing paren.
#
# 24. ELEMENT ORDERING IN SCHEMATIC
#     The correct order inside (kicad_sch ...) is:
#       1. (version ...) (generator ...) (uuid ...) (paper ...)
#       2. (lib_symbols ...)
#       3. (junction ...) elements
#       4. (no_connect ...) elements
#       5. (wire ...) elements
#       6. (symbol ...) instances
#       7. (sheet_instances ...)
#       8. (embedded_fonts no)

# =============================================================================
# 14. TEMPLATE STATUS & LOCKING
# =============================================================================
# Each template folder MUST contain a `status.json` file that tracks the
# template's lifecycle state. This prevents accidental overwrites of
# reviewed/approved templates.
#
# 14A. STATUS FILE FORMAT (status.json)
# --------------------------------------
# {
#   "template": "<template_name>",
#   "status": "locked",           <-- current state
#   "reviewed": "yes",            <-- "yes" if human-reviewed, else "no"
#   "reviewer_initials": "PL",    <-- reviewer initials, "" if not reviewed
#   "reviewer_name": "Peter",     <-- reviewer name, "" if not reviewed
#   "locked_by": "human",         <-- who set the current status
#   "locked_date": "2026-03-06",  <-- when status was last changed
#   "description": "Brief reason for current status",
#   "changelog": [
#     {"date": "2026-03-05", "from": "draft", "to": "review", "by": "ai"},
#     {"date": "2026-03-06", "from": "review", "to": "locked", "by": "human"}
#   ]
# }
#
# 14B. STATUS VALUES
# ------------------
#   draft       â€” Initial creation, AI is actively generating/editing
#   review      â€” AI finished first pass, awaiting human review in KiCad
#   locked      â€” Human approved. DO NOT regenerate or modify.
#   revision    â€” Unlocked for specific changes (document what & why)
#
# 14C. LOCKING RULES
# ------------------
#   1. Build scripts MUST check status.json before writing .kicad_sch.
#      If status == "locked", print a warning and EXIT without writing.
#   2. AI agents MUST check status.json before modifying ANY file in a
#      template folder. If locked, do NOT modify â€” ask the user first.
#   3. Only a human (or explicit user instruction) can change status
#      from "locked" to "revision".
#   4. When creating a new template, set initial status to "draft".
#   5. After build script runs successfully, set status to "review".
#   6. Review metadata is REQUIRED in status.json for every template:
#      "reviewed", "reviewer_initials", "reviewer_name".
#   7. Default values for new/draft templates:
#      reviewed="no", reviewer_initials="", reviewer_name="".
#   8. When a human approves a template (status -> locked):
#      set reviewed="yes" and fill reviewer_initials/reviewer_name.
#   9. AI agents MUST preserve review metadata when editing status.json
#      unless the user explicitly instructs a change.
#
# 14D. LOCKED TEMPLATES (current)
# --------------------------------
#   rtc_rv3028          - LOCKED. Human-reviewed, RV-3028-C7 I2C RTC.
#   psu_lmzm23601_5v   - LOCKED. Human-reviewed, 12V to 5V buck regulator.
#   psu_lmzm23601_3v3  - LOCKED. Human-reviewed, 12V to 3.3V buck regulator.
#   audio_max98357      - LOCKED. Human-reviewed, MAX98357A I2S audio amp.
#   flash_csnp1g        - LOCKED. Human-reviewed, CSNP1GCR01-BOW 1Gbit NAND flash (SPI).
#

# =============================================================================
# 15. LESSONS LEARNED FROM PSU TEMPLATE (March 2026)
# =============================================================================
#
# 25. GND SYMBOLS CAN BE ROTATED FOR HORIZONTAL CONNECTIONS
#     When a GND pin exits horizontally (e.g., IC pin 1 GND going left),
#     use angle=270 to point the GND symbol LEFT, or angle=90 for RIGHT.
#     Default angle=0 points DOWN. This keeps wiring clean without extra
#     bends. Update ref/val positions accordingly (they shift with rotation).
#
# 26. MODE/SYNC PIN â€” TIE TO GND FOR FORCED PWM
#     The LMZM23601 MODE/SYNC pin should be tied to GND (not NC) for
#     forced PWM mode. Route via a corner junction: GND symbol â†’ corner â†’
#     horizontal to both GND pin and MODE/SYNC pin. This avoids
#     pulse-skipping at light loads.
#
# 27. VIN RAIL DOESN'T NEED TO ALIGN WITH IC PIN Y
#     The VIN rail can run at a different Y than the IC's VIN pin.
#     Use a short vertical stub from the rail down to the pin. This gives
#     more layout flexibility for input caps and power symbols.
#
# 28. SPREAD OUT FEEDBACK DIVIDERS VERTICALLY
#     Place the top feedback resistor horizontally near VOUT, and the
#     bottom resistor vertically below it (at angle=270). Connect via
#     a vertical wire at the FB junction X. This is cleaner than
#     stacking both resistors vertically.
#
# 29. STAGGER INPUT CAPS AT DIFFERENT Y POSITIONS
#     Two parallel input caps look better staggered (different Y) rather
#     than side-by-side at the same Y. Connect their top pins via the VIN
#     rail and bottom pins via a horizontal GND rail.
#
# 30. TEMPLATE NAMING: USE VOLTAGE SUFFIX FOR VARIANTS
#     When the same IC can produce different output voltages, create
#     separate template folders with voltage suffix:
#       psu_lmzm23601_5v/   â€” 12V to 5V version
#       psu_lmzm23601_3v3/  â€” 12V to 3.3V version (with input protection)
#     Each folder has its own spec, build script, schematic, and status.json.
#
# 31. JLCPCB PART NUMBER VERIFICATION IS CRITICAL
#     Always verify LCSC part numbers return the correct component.
#     Multiple searches may be needed â€” LCSC numbers can be wrong in
#     datasheets or community databases. Use WebFetch on JLCPCB search
#     to confirm part number â†’ value/package match before building.

#
# 32. SYNC BUILD SCRIPT TO REVIEWED SCHEMATIC GEOMETRY BEFORE LOCKING
#     After human KiCad edits, update build-script layout constants and wire
#     segment lists to match the reviewed .kicad_sch exactly. Validate with a
#     geometry comparison (symbols, wires, junctions) between script-generated
#     output and the reviewed schematic.
#
# 33. DO NOT GENERATE ZERO-LENGTH WIRES
#     Avoid wire segments where start==end. They add ERC noise and make real
#     connectivity issues harder to spot. Split rails explicitly at branch/tap
#     points instead.
#
# 34. GND ANGLE=180 IS A VALID CLEANUP OPTION
#     A GND symbol at angle=180 can be used above an IC node to create a clean
#     vertical drop connection (for example U5 GND/MODE node in PSU 3.3V).
#
# 35. REVIEWED 3.3V PSU LAYOUT BASELINE
#     Stable reviewed placement pattern:
#       D8 at left input edge; C11/C34 on VIN rail to the right;
#       R31 around x=170,y=118 (vertical); R32 around x=185,y=124 (vertical);
#       C35 around x=198,y=124 (vertical); +3.3V near x=193,y=100.
#     Reuse this baseline for future regenerations of psu_lmzm23601_3v3.
# =============================================================================
# 16. VALIDATION WORKFLOW — MANDATORY AFTER EVERY CHANGE
# =============================================================================
# Every time a .kicad_sch is created/modified OR a build script is changed,
# the AI agent MUST run the validation pipeline and update all related files.
#
# 16A. WHEN TO VALIDATE
# ----------------------
#   - After running a build script (build_<name>.py) to generate a .kicad_sch
#   - After a human saves changes in KiCad (user says "I saved" or similar)
#   - After any manual edit to a .kicad_sch file
#   - Before changing status from "draft" to "review"
#   - Before changing status from "review" to "locked"
#
# 16B. VALIDATION COMMAND
# -----------------------
#   Single template:
#     python templates/validate_template.py templates/<name>/<name>.kicad_sch
#
#   All templates:
#     python templates/validate_template.py
#
# 16C. WHAT THE VALIDATOR CHECKS
# -------------------------------
#   1. Parentheses balance (unmatched parens = corrupt file)
#   2. Symbol (at x y angle) has 3 numbers (missing angle = KiCad crash)
#   3. No duplicate UUIDs (duplicates = ERC errors, broken nets)
#   4. Every placed symbol has an (instances) block (missing = "?" refs)
#   5. Every lib_id referenced by placed symbols exists in lib_symbols
#      (missing = red boxes in KiCad)
#   6. (embedded_fonts no) present (required for KiCad 9.0)
#   7. (sheet_instances) section present
#   8. File format version is 20250114 (KiCad 9.0)
#   9. Summary counts: lines, UUIDs, symbols, wires, no-connects, junctions
#
# 16D. REQUIRED ACTIONS AFTER VALIDATION PASSES
# -----------------------------------------------
#   1. If the build script was changed:
#      a. Run the build script (unless template is locked — see §14)
#      b. Run the validator on the generated .kicad_sch
#      c. Update the .spec file if layout positions changed
#      d. Update status.json changelog if status transitions
#
#   2. If the .kicad_sch was edited in KiCad (human save):
#      a. Run the validator on the saved .kicad_sch
#      b. If positions changed, update the .spec layout section (§7)
#      c. If positions changed, update the build script layout constants
#         (so the build script stays in sync — see lesson #32)
#      d. Update status.json changelog if status transitions
#
#   3. If validation FAILS:
#      a. Report all errors and warnings to the user
#      b. Do NOT advance status (draft→review or review→locked)
#      c. Fix errors before proceeding
#      d. Re-run validation after fixes
#
# 16E. KEEPING FILES IN SYNC — THE THREE-FILE RULE
# --------------------------------------------------
# For every template, these three files MUST stay consistent:
#
#   1. <name>.spec       — Source of truth for circuit design & layout
#   2. build_<name>.py   — Generates .kicad_sch from spec
#   3. <name>.kicad_sch  — The actual schematic (may have human edits)
#
# After ANY change to one file, check if the other two need updating:
#   - .kicad_sch changed in KiCad → update .spec positions & build script
#   - build script changed → regenerate .kicad_sch (if not locked), update .spec
#   - .spec changed → update build script if layout/wiring changed
#
# The .kicad_sch is the source of truth for geometry AFTER human review.
# The .spec is the source of truth for circuit design decisions.
# The build script must match both.
#
# 16F. VALIDATION BEFORE LOCKING
# --------------------------------
# Before a template can move to "locked" status, ALL of these must be true:
#   [x] validate_template.py reports 0 errors, 0 warnings
#   [x] .spec verification checklist is fully checked ([x] all items)
#   [x] .spec layout positions match .kicad_sch actual positions
#   [x] Build script layout constants match .kicad_sch actual positions
#   [x] status.json changelog is up to date
#   [x] Human has opened .kicad_sch in KiCad and confirmed no ERC errors

# =============================================================================
# 17. FINALPASS — POST-REVIEW SYNC & LOCK WORKFLOW
# =============================================================================
# When the user says "FinalPass <template_name>", the AI agent performs the
# complete post-review synchronization and locking sequence in one shot.
#
# TRIGGER: User says "FinalPass" or "FinalPass <name>" (defaults to the
#          template currently being worked on)
#
# PREREQUISITES:
#   - status.json must be "review" (not "draft" or "locked")
#   - Human has reviewed the .kicad_sch in KiCad and is satisfied
#
# THE SEQUENCE (do all of these in order):
#
#   1. READ the reviewed .kicad_sch — extract all symbol positions, wire
#      endpoints, junctions, and power symbol angles/positions
#
#   2. COMPARE to the build script layout constants — identify every
#      difference (position, angle, wire routing, junctions added/removed)
#
#   3. UPDATE build_<name>.py — sync all layout constants, wire definitions,
#      junction definitions, and ref/val text positions to match the reviewed
#      .kicad_sch exactly
#
#   4. CROSS-CHECK — verify the updated build script's wire endpoints match
#      the reviewed schematic's wires (automated comparison)
#
#   5. UPDATE <name>.spec — sync sections 7 (Layout), 8 (Pin Endpoints),
#      9 (Wiring Connections), and 10 (Verification Checklist) to match
#
#   6. LOCK status.json — set status to "locked", fill in reviewer info,
#      add changelog entry with "FinalPass" note
#
#   7. UPDATE CLAUDE.md — add template name to "Currently locked templates"
#
#   8. PRESENT LESSONS LEARNED — summarize what the human changed and why,
#      noting any patterns that should be applied to future templates
#
# LAYOUT PATTERNS LEARNED FROM REVIEWS:
#   - Humans prefer visual spacing over minimal wiring distance
#   - Sideways GND symbols (angle=270) can eliminate L-routes
#   - Break long rail wires at junction points into separate wire segments
#   - Give components more horizontal/vertical spacing than strictly needed
#   - Use intermediate junctions when pull-up/down resistors are offset
#   - Small 1.27mm nudges to symbol positions are normal in review

# END OF SPEC
