# =============================================================================
# SAMPLE CIRCUIT PROJECT SPECIFICATION
# =============================================================================
# Project: SampleCircuit
# Repo: github.com/pclakelite/SampleCircuit
# Location: c:\Projects\SampleCircuit
# Date: March 2026
#
# This spec documents the project design, tooling, and lessons learned.


# =============================================================================
# 1. PROJECT OVERVIEW
# =============================================================================
# Standalone ESP32-S3 board combining CircuitAI templates.
#
# MCU:        ESP32-S3-WROOM-1 (N16R8)
# Audio:      NS4168 I2S audio amplifier (+5V rail)
# Storage:    CSNP1GCR01-BOW 1Gbit NAND flash (SPI)
# Storage:    Micro SD card (SPI, shared bus with flash)
# Power:      24V input → 12V → 5V (audio) and 12V → 3.3V (ESP32/SD/flash)
# PSU ICs:    LMZM23601SILR buck converters (all 3 rails)
# RTC:        RV-3028-C7 I2C real-time clock (3.3V, battery backup)
# Supervisor: TLV803SDBZR voltage supervisor (holds ESP32 in reset until 3.3V stable)
# Terminals:  WJ500V green screw terminal blocks for all 4 power rails + speaker
# Components: All SMD >= 0805, JLCPCB sourced


# =============================================================================
# 2. POWER CHAIN
# =============================================================================
# 24V INPUT (screw terminal J1)
#   └→ LMZM23601 24V→12V (R1=110K, R2=10K, Vout = 1.0*(1+110/10) = 12V)
#       ├→ LMZM23601 12V→5V  (R3=10K, R4=2.49K, Vout = 1.0*(1+10/2.49) ≈ 5V)
#       │   └→ NS4168 audio amp
#       └→ LMZM23601 12V→3.3V (locked template, Schottky + extra caps)
#           ├→ ESP32-S3
#           ├→ CSNP1G flash
#           └→ Micro SD card
#
# Test point terminal blocks: J2 (12V), J3 (5V), J4 (3.3V)
# Speaker terminal: J5 (OUTP/OUTN from NS4168)


# =============================================================================
# 3. GPIO PIN ASSIGNMENTS
# =============================================================================
# ESP32-S3 GPIO → Signal Port mappings:
#
# GPIO | Signal    | Port Symbol     | Function
# -----|-----------|-----------------|------------------
# IO4  | BCLK      | Ports:BCLK      | I2S bit clock
# IO5  | LRCLK     | Ports:LRCLK     | I2S word select
# IO6  | DIN       | Ports:DIN       | I2S data out
# IO7  | AMP_EN    | Ports:AMP_EN    | NS4168 shutdown control
# IO8  | CS_FLASH  | Ports:CS_FLASH  | NAND flash chip select
# IO15 | SD_MISO   | Ports:SD_MISO   | SPI MISO (shared bus)
# IO16 | SD_MOSI   | Ports:SD_MOSI   | SPI MOSI (shared bus)
# IO17 | SD_CLK    | Ports:SD_CLK    | SPI clock (shared bus)
# IO18 | CS_SD     | Ports:CS_SD     | SD card chip select
# IO19 | UD-       | Ports:UD-       | USB D-
# IO20 | UD+       | Ports:UD+       | USB D+
# EN   | Enable    | Ports:Enable    | Chip enable
# TXD0 | TX        | Ports:TX        | UART TX
# RXD0 | RX        | Ports:RX        | UART RX
# IO1  | SCL       | Ports:SCL       | I2C clock (RTC RV-3028)
# IO2  | SDA       | Ports:SDA       | I2C data (RTC RV-3028)
#
# I2C bus has 10K pull-up resistors to +3.3V (included in rtc_rv3028 template).
# SPI bus is shared between flash (CS_FLASH) and SD card (CS_SD).
# Each has a separate chip select line.


# =============================================================================
# 4. TEMPLATE SYSTEM
# =============================================================================
# Templates are reusable circuit blocks from c:\Projects\CircuitAI\templates\
# Each template has:
#   - build_*.py       — Python script that generates .kicad_sch
#   - status.json      — Lock status (draft/review/locked)
#   - manifest.json    — Lists component refs and lib_symbols (for patch system)
#   - *.spec           — Circuit-specific specification
#   - *.kicad_sch      — Pre-built schematic (used when locked)
#
# Templates used in SampleCircuit:
#   Template              | Status  | Offset (dx, dy)
#   ----------------------|---------|----------------
#   psu_lmzm23601_12v     | draft   | (0, 0)
#   psu_lmzm23601_5v      | locked  | (119.38, 0)
#   psu_lmzm23601_3v3     | locked  | (238.76, 0)
#   esp32s3_core          | review  | (0, 99.06)
#   audio_ns4168          | locked  | (200.66, 99.06)
#   flash_csnp1g          | locked  | (0, 210.82)
#   sdcard_spi            | review  | (139.7, 210.82)
#   terminal_blocks       | inline  | (279.4, 210.82)
#   supervisor_tlv803s    | locked  | (360, 0)         — added via patch
#   rtc_rv3028            | locked  | (280, 210)       — added via patch
#
# LOCKED templates: DO NOT modify. build_schematic() returns None,
# master build reads pre-built .kicad_sch file instead.
#
# Template ROOT UUIDs (from each build script):
#   psu_12v:  c5d6e7f8-a1b2-4c3d-9e0f-1a2b3c4d5e6f
#   psu_5v:   a3e7c1d4-8f2b-4a6e-9c5d-1b3e7f9a2c4d
#   psu_3v3:  7a6fd472-71e4-4f31-b6fe-f7300bc4d95f
#   esp32:    b4d9f2a1-8c3e-5b0f-c6d4-e2f3a5b6c7d8
#   audio:    b4f8a2d1-6e3c-4b97-ae5d-2g3h4i5j6k7l
#   flash:    b4f8c2d3-6e5a-4b90-af7d-2g3e4f5a6b7c
#   sdcard:   d6b4c3e5-1a7f-4d8b-cf92-0e5f6a7b8c9d
#
# Combined schematic UUID: f1a2b3c4-d5e6-7f89-0a1b-c2d3e4f5a6b7


# =============================================================================
# 5. SUPERVISOR & ENABLE PIN DESIGN NOTES
# =============================================================================
#
# 5A. TLV803S VOLTAGE SUPERVISOR → ESP32 EN PIN
# -----------------------------------------------
# The TLV803S monitors the +3.3V rail and holds the ESP32 in reset until
# power is stable. Circuit:
#   - TLV803S RESET# (open-drain, active-low) → Enable net → ESP32 EN pin
#   - R (10k pull-up to +3.3V) on Enable net
#   - C (100nF filter cap) on Enable net
#
# Power-on sequence:
#   1. +3.3V ramping (VDD < 2.93V) → TLV803S holds RESET# LOW → EN LOW → ESP32 in reset
#   2. VDD crosses ~2.93V threshold → TLV803S releases (high-Z) → pull-up drives EN HIGH
#   3. ESP32 boots cleanly on stable rail
#   4. If brownout (VDD dips below threshold) → TLV803S pulls EN LOW → clean reset
#
# The 10k pull-up is REQUIRED because RESET# is open-drain (can only pull low).
# The 100nF cap filters noise to prevent false resets.
#
# 5B. AUDIO AMP (NS4168 / MAX98357A) — NO SUPERVISOR NEEDED
# -----------------------------------------------------------
# The audio amp does NOT need a separate supervisor or enable sequencing.
# Reasons:
#   - No reset/enable pin that requires voltage-level sequencing
#   - The NS4168 has a CTRL pin for software shutdown (connected to AMP_EN GPIO)
#     but this is for mute/power-save, not power-on-reset
#   - The amp cannot produce output until the ESP32 is running and sending
#     valid I2S clocks (BCLK, LRCLK) and data (DIN)
#   - The ESP32 itself gates the audio — it boots first (via TLV803S),
#     then starts the I2S peripheral, then the amp begins operating
#
# Effective boot chain:
#   +3.3V stable → TLV803S releases → ESP32 boots → firmware starts I2S → amp active


# =============================================================================
# 6. SCHEMATIC PATCH SYSTEM (Non-Destructive Direct Injection)
# =============================================================================
# Problem: build_sample_circuit.py does a COMPLETE OVERWRITE of the .kicad_sch
# every time. It also regenerates all UUIDs. Any manual KiCad layout work
# (moving components, rerouting wires) is destroyed on regeneration.
#
# Solution: 3-script patch system for surgical modifications:
#
# 6A. sch_parser.py — S-expression parser
#   - Parses .kicad_sch into: header, lib_symbols, body elements, footer
#   - Perfect round-trip fidelity (byte-identical output)
#   - Elements identified by: (type, reference/coords, lib_id)
#
# 6B. patch_schematic.py — Surgical patch tool
#   - Applies JSON patch manifests to existing .kicad_sch
#   - Operations: add_lib_symbols, remove_lib_symbols,
#                 add_elements, remove_elements, replace_elements
#   - Auto-backup to .kicad_sch.bak before patching
#   - Auto-validates with validate_sch.py (restores backup on failure)
#   - NEVER touches UUIDs of existing elements
#
# 6C. build_patch.py — Template-aware patch generator
#   - Generates patch.json from template subcircuits
#   - Handles coordinate offsets, ref renumbering, UUID generation
#   - Requires manifest.json in template directory for removal
#
# WORKFLOW:
#   1. User saves schematic in KiCad
#   2. Run: python build_patch.py --target X.kicad_sch --add <template> --offset X,Y
#   3. Run: python patch_schematic.py X.kicad_sch patch.json
#   4. User does File → Revert in KiCad
#
# build_sample_circuit.py is for INITIAL generation only.
# All subsequent updates go through the patch system.


# =============================================================================
# 7. GRID AND COORDINATE RULES
# =============================================================================
# Standard grid: 2.54mm (100 mil) — per KiCad9_SchematicRules.spec §6a
#                and CircuitCreation.spec §7C
#
# IMPORTANT: Component pin offsets (e.g. 3.81mm for 0805 passives) are NOT
# multiples of 2.54mm. This means:
#   - Component CENTERS should be on 2.54mm grid
#   - Wire ENDPOINTS must match pin positions exactly, which may be on
#     1.27mm sub-grid depending on pin geometry
#   - NEVER blindly snap all coordinates to 2.54mm — this breaks wire
#     connections (learned the hard way, see §11)
#
# For KiCad manual editing, set grid to 1.27mm (50 mil) to accommodate
# pin positions that fall on half-grid points.
#
# snap formula: snap(val) = round(round(val / 2.54) * 2.54, 2)
# Only apply to component centers, NOT wire endpoints.


# =============================================================================
# 8. KEY FILES
# =============================================================================
# Schematic:
#   SampleCircuit.kicad_sch       — Main schematic (generated + manual edits)
#   SampleCircuit.kicad_pro       — KiCad project file
#   sym-lib-table                 — Symbol library references
#   fp-lib-table                  — Footprint library references
#
# Libraries:
#   JLCImport.kicad_sym           — JLCPCB component symbol library
#   JLCImport.pretty/             — JLCPCB component footprints
#   Ports.kicad_sym               — Custom signal port symbols
#
# Build scripts:
#   build_sample_circuit.py       — Master build (initial generation only)
#   sch_parser.py                 — S-expression parser
#   patch_schematic.py            — Surgical patch tool
#   build_patch.py                — Template-aware patch generator
#   snap_to_grid.py               — DO NOT USE (breaks wire connections)
#   validate_sch.py               — Schematic validator (run after every change)
#
# Specs:
#   specs/KiCad9_SchematicRules.spec      — General schematic rules
#   specs/CircuitCreation.spec            — Circuit creation rules
#   specs/SampleCircuit_Project.spec      — This file
#   specs/TerminalBlock_TestPoint.spec    — Terminal block wiring pattern (J1-J5)


# =============================================================================
# 9. CUSTOM PORT SYMBOLS (Ports.kicad_sym)
# =============================================================================
# Port symbols act as global signal labels connecting ESP32 GPIO to peripherals.
# Each signal needs exactly 2 placements (one on ESP32, one on peripheral).
#
# Available ports:
#   SCL, SDA          — I2C bus
#   DIN, BCLK, LRCLK  — I2S audio bus
#   OUTP, OUTN         — Speaker output
#   CS_SD, CS_FLASH    — SPI chip selects (separate lines!)
#   SD_CLK, SD_MOSI, SD_MISO — SPI data bus
#   Enable             — ESP32 enable
#   TX, RX             — UART
#   UD+, UD-           — USB
#   AMP_EN             — Audio amp shutdown control
#   LED+               — LED driver
#
# 9A. PIN TYPE REQUIREMENT — CRITICAL
# ------------------------------------
# All port symbol pins MUST use `power_in` pin type for KiCad 9 to form
# global net connections. This was discovered through trial and error:
#
#   Pin Type      | Global Net? | ERC Clean? | Verdict
#   --------------|-------------|------------|--------
#   passive       | NO          | Yes        | BROKEN — nets don't connect
#   bidirectional | NO          | Yes        | BROKEN — nets don't connect
#   power_in      | YES         | No*        | CORRECT — use this
#
# * power_in triggers "Input Power pin not driven by any Output Power pins"
#   warnings for every port pair (18 warnings total). These are BENIGN.
#   Suppress in KiCad: Inspect → Schematic Setup → ERC → Pin Conflicts →
#   set "Input Power pin" vs "Input Power pin" to "No error".
#
# The pin definition in each port lib_symbol looks like:
#   (pin power_in line (at 2.54 0 0) (length 0) ...)
# The (at 2.54 0 0) with (length 0) uniquely identifies port pins vs IC pins.
#
# 9B. UPDATING PORT PIN TYPES
# ----------------------------
# Port pin types must be consistent across THREE locations:
#   1. c:\Projects\CircuitAI\Ports.kicad_sym   — master library
#   2. c:\Projects\SampleCircuit\Ports.kicad_sym — project library copy
#   3. SampleCircuit.kicad_sch lib_symbols section — embedded copies
#
# After changing Ports.kicad_sym, update in-schematic copies via:
#   KiCad → Tools → Update Symbols from Library → select all Ports → Update
# Or use a Python script targeting the specific pin pattern (see §9A).
#
# 9C. CURRENT STATE (March 2026)
# --------------------------------
# All 18 port symbols are set to power_in in all three locations.
# ERC shows benign "not driven" warnings — suppress per §9A.


# =============================================================================
# 10. JLCPCB PARTS ADDED MANUALLY
# =============================================================================
# These parts were added to JLCImport.kicad_sym by cloning existing entries:
#
#   Part Number       | Value   | LCSC    | Cloned From
#   ------------------|---------|---------|------------
#   0805W8F1003T5E    | 100K    | C17407  | 10K pattern
#   0805W8F1004T5E    | 1M      | C17514  | 100K pattern
#   0805W8F1104T5E    | 110K    | C17436  | 10K pattern
#
# All have matching footprints in JLCImport.pretty/


# =============================================================================
# 11. LESSONS LEARNED (CRITICAL — DO NOT SKIP)
# =============================================================================
#
# 11A. NEVER SNAP COORDINATES BLINDLY
# ------------------------------------
# Running a script that snaps all (at) and (xy) coordinates to 2.54mm grid
# BREAKS all wire-to-pin connections. Wire endpoints must match pin positions,
# and pin positions = component_center + pin_local_offset. Pin offsets like
# 3.81mm are NOT multiples of 2.54mm.
# Result: All wires disconnected from all pins. User lost manual edits.
# Fix: Only snap component centers, then recalculate wire endpoints.
#
# 11B. ALWAYS COMMIT BEFORE MODIFYING THE SCHEMATIC
# --------------------------------------------------
# Before running ANY script that modifies SampleCircuit.kicad_sch, ALWAYS:
#   1. Ask the user to save in KiCad
#   2. git add + git commit the current state
#   3. THEN run the modification
# This ensures manual edits can always be recovered from git history.
#
# 11C. FLASH AND SD CARD NEED SEPARATE CHIP SELECTS
# --------------------------------------------------
# Both flash and SD card share the SPI bus (MISO/MOSI/CLK).
# They MUST have separate CS lines: CS_FLASH (IO8) and CS_SD (IO18).
# Originally both used CS_SD — fixed by creating CS_FLASH port symbol.
#
# 11D. LOCKED TEMPLATES RETURN None FROM build_schematic()
# --------------------------------------------------------
# Several templates check lock status inside build_schematic() and return
# None when locked. The master build script must handle this by falling
# back to reading the pre-built .kicad_sch file from the template directory.
#
# 11E. KICAD AUTO-CONNECT CANNOT BE DISABLED
# -------------------------------------------
# When dragging (G key) components over existing wires, KiCad automatically
# creates connections. There is NO setting to disable this behavior.
# Workaround: Use M (Move) instead of G (Drag) to avoid accidental connections.
# M disconnects everything; G maintains and creates connections.
#
# 11F. PIN OFFSETS VARY BY COMPONENT
# -----------------------------------
# 0805 caps: pins at ±3.81mm (NOT ±2.54mm)
# 0805 resistors: pins at ±5.08mm (JLCImport horizontal orientation)
# Always verify pin positions from the library — never assume.
#
# 11G. NET HIGHLIGHTING IN KICAD (like DipTrace "highlight net")
# ---------------------------------------------------------------
# Schematic editor:
#   - Press ` (backtick) while clicking a wire or pin to highlight the entire net
#   - Adjust dimming: Edit → Preferences → Schematic Editor → Display
# PCB editor:
#   - Press ` (backtick) while clicking a track or pad to highlight the net
#   - All connected pads/traces light up, everything else dims
#   - Adjust dimming: Edit → Preferences → PCB Editor → Display Options
#   - Inspect → Net Inspector to browse and highlight nets by name
# Tip: M (Move) disconnects; G (Drag) maintains connections (see 10E)
#
# 11H. PORT SYMBOL PIN TYPE MUST BE power_in
# -------------------------------------------
# KiCad 9 only forms global net connections for port symbols when pin type
# is `power_in`. Both `passive` and `bidirectional` types silently fail —
# the net appears connected in the schematic editor but backtick highlighting
# shows the nets are NOT actually tied together.
# This caused supervisor Enable and ESP32 Enable to be disconnected despite
# both using the same Ports:Enable symbol.
# Fix: Change all port symbol pins to power_in (see §9A for full details).
# Trade-off: 18 benign ERC "not driven" warnings (suppressible).
#
# 11I. DUPLICATE COMPONENT REFS WHEN PATCHING TEMPLATES
# ------------------------------------------------------
# When injecting templates via the patch system, component references from
# the new template may collide with existing refs (e.g. both templates
# have C1, C2, U5). KiCad shows "Schematic is not fully annotated" and
# ERC results are incomplete.
# Fix: After patching, renumber duplicates. A Python script was used to
# find duplicates by UUID and renumber: C1→C105, C2→C106, C11→C107,
# U5→U24, U6→U25. Both the property "Reference" and instances (reference)
# must be updated together.
# Alternative: Use KiCad Annotate tool (Tools → Annotate Schematic).
#
# 11J. I2C PULL-UP RESISTORS
# ----------------------------
# The RV-3028 RTC template (rtc_rv3028) includes its own I2C pull-up
# resistors (R89=10K on SCL, R94=10K on SDA, pulled to +3.3V).
# Do NOT add additional pull-ups on the ESP32 side — one set per bus.


# =============================================================================
# 12. PYTHON ENVIRONMENT
# =============================================================================
# Python: C:/Users/peter.LAKEMAST/AppData/Local/Python/bin/python.exe
# No virtual environment — system Python with standard library only.
# All build scripts use: importlib, re, uuid, json, os, sys, shutil


# =============================================================================
# 13. ERC ERRORS AND FIXES (March 2026)
# =============================================================================
# KiCad ERC run on SampleCircuit.kicad_sch: 55 errors, 268 warnings.
# Banner: "Schematic is not fully annotated. ERC results will be incomplete."
#
# 13A. DUPLICATE COMPONENT REFERENCES (C1, C2, U5, U6, etc.)
# ------------------------------------------------------------
# Root cause: renumber_component_refs() is defined in build_sample_circuit.py
# (line 163) but NEVER CALLED in main(). Each template generates its own
# C1, R1, U1 etc. and they collide when combined.
#
# Fix: Use KiCad's built-in Annotate tool (Show Annotation dialog) after
# generating the schematic. This renumbers all refs sequentially.
# Alternatively, call renumber_component_refs() in main() with proper offsets.
# STATUS: PARTIALLY FIXED — C1→C105, C2→C106, C11→C107, U5→U24, U6→U25
#         via Python script (commit 8a54135). Run Annotate for full cleanup.
#
# 13B. DUPLICATE #PORT REFERENCES (#PORT11, #PORT12, #PORT13, #PORT14)
# ---------------------------------------------------------------------
# Root cause: Port offset values in TEMPLATES[] are too small.
# ESP32 template uses ports #PORT01 through ~#PORT16 (offset 0).
# Audio template uses ports #PORT01-#PORT06 (offset +10 -> #PORT11-#PORT16).
# This causes collisions:
#   #PORT11: AMP_EN (ESP32) vs UD- (audio offset)
#   #PORT12: DIN (ESP32) vs UD+ (audio offset)
#   #PORT13: BCLK (ESP32) vs TX (audio offset)
#   #PORT14: LRCLK (ESP32) vs RX (audio offset)
#
# Fix: Increase port_off spacing in TEMPLATES[]. ESP32 has up to 16 ports,
# so audio should use port_off >= 20 (not 10). Cascade all subsequent offsets.
# Current port_off values: psu_12v=-1, psu_5v=-1, psu_3v3=-1, esp32=0,
#                          audio=10, flash=20, sdcard=30, terminal=40
# Proposed port_off:       psu_12v=-1, psu_5v=-1, psu_3v3=-1, esp32=0,
#                          audio=20, flash=30, sdcard=40, terminal=50
# STATUS: NOT YET FIXED
#
# 13C. POWER PINS NOT DRIVEN (#PWR01, #PWR02, #PWR08)
# ----------------------------------------------------
# Error: "Input Power pin not driven by any Output Power pins"
# Root cause: Power symbols (e.g. +3.3V, +5V, +12V) exist on the schematic
# but no PWR_FLAG symbol is placed on those nets, OR the regulator output
# pin type is not set to "Power output" in the lib_symbol.
#
# Fix: Add PWR_FLAG symbols to each power net. In the build script, generate
# a (symbol (lib_id "power:PWR_FLAG") ...) on each voltage rail.
# STATUS: NOT YET FIXED
#
# 13D. INPUT PIN NOT DRIVEN (R1 Pin 2)
# --------------------------------------
# Error: "Input pin not driven by any Output pins"
# One side of R1 is floating - not wired to anything.
# Investigate which template owns R1 and verify wiring.
# STATUS: NOT YET FIXED
#
# 13E. UNCONNECTED ESP32 PINS (EN, TXD0, RXD0, IO3, IO9-IO14, IO46, etc.)
# -------------------------------------------------------------------------
# Error: "Pin not connected" for many ESP32-S3 GPIO pins.
# These are unused GPIO pins that need no-connect (X) flags.
# Add no_connect elements in the ESP32 template for all intentionally
# unused pins. Format:
#   (no_connect (at X Y) (uuid "..."))
# where X,Y is the pin endpoint coordinate.
# STATUS: NOT YET FIXED
#
# 13F. PORT SYMBOL "NOT DRIVEN" WARNINGS (18 total)
# ---------------------------------------------------
# All 18 port symbols trigger "Input Power pin not driven" because
# power_in pins expect an output driver. These are BENIGN — the ports
# form correct global nets. Suppress via ERC settings (see §9A).
# STATUS: BENIGN — suppress in ERC, do not fix
#
# 13G. WARNINGS (268 total)
# --------------------------
# Mostly additional unconnected pin warnings. Lower priority than errors.
# Will decrease as unconnected pins get no-connect flags.


# =============================================================================
# 14. BUILD SCRIPT FIX CHECKLIST
# =============================================================================
# When fixing build_sample_circuit.py, apply these changes:
#
# [ ] 1. Fix #PORT offsets in TEMPLATES[] (S13B) - increase spacing to 20+
# [ ] 2. Add PWR_FLAG symbols to power nets (S13C)
# [ ] 3. Add no-connect flags to unused ESP32 pins in esp32s3_core template (S13E)
# [ ] 4. Investigate R1 Pin 2 floating connection (S13D)
# [ ] 5. After regenerating, run KiCad Annotate to fix component refs (S13A)
# [ ] 6. Re-run ERC to verify fixes
#
# IMPORTANT: Before modifying the schematic, ALWAYS commit current state first
# (see S11B). Use the patch system (S6) for changes after initial generation.


# END OF SPEC
