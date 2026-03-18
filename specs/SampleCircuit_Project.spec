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
#
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
# 5. SCHEMATIC PATCH SYSTEM (Non-Destructive Direct Injection)
# =============================================================================
# Problem: build_sample_circuit.py does a COMPLETE OVERWRITE of the .kicad_sch
# every time. It also regenerates all UUIDs. Any manual KiCad layout work
# (moving components, rerouting wires) is destroyed on regeneration.
#
# Solution: 3-script patch system for surgical modifications:
#
# 5A. sch_parser.py — S-expression parser
#   - Parses .kicad_sch into: header, lib_symbols, body elements, footer
#   - Perfect round-trip fidelity (byte-identical output)
#   - Elements identified by: (type, reference/coords, lib_id)
#
# 5B. patch_schematic.py — Surgical patch tool
#   - Applies JSON patch manifests to existing .kicad_sch
#   - Operations: add_lib_symbols, remove_lib_symbols,
#                 add_elements, remove_elements, replace_elements
#   - Auto-backup to .kicad_sch.bak before patching
#   - Auto-validates with validate_sch.py (restores backup on failure)
#   - NEVER touches UUIDs of existing elements
#
# 5C. build_patch.py — Template-aware patch generator
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
# 6. GRID AND COORDINATE RULES
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
#     connections (learned the hard way, see §10)
#
# For KiCad manual editing, set grid to 1.27mm (50 mil) to accommodate
# pin positions that fall on half-grid points.
#
# snap formula: snap(val) = round(round(val / 2.54) * 2.54, 2)
# Only apply to component centers, NOT wire endpoints.


# =============================================================================
# 7. KEY FILES
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
#   specs/KiCad9_SchematicRules.spec  — General schematic rules
#   specs/CircuitCreation.spec        — Circuit creation rules
#   specs/SampleCircuit_Project.spec  — This file


# =============================================================================
# 8. CUSTOM PORT SYMBOLS (Ports.kicad_sym)
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


# =============================================================================
# 9. JLCPCB PARTS ADDED MANUALLY
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
# 10. LESSONS LEARNED (CRITICAL — DO NOT SKIP)
# =============================================================================
#
# 10A. NEVER SNAP COORDINATES BLINDLY
# ------------------------------------
# Running a script that snaps all (at) and (xy) coordinates to 2.54mm grid
# BREAKS all wire-to-pin connections. Wire endpoints must match pin positions,
# and pin positions = component_center + pin_local_offset. Pin offsets like
# 3.81mm are NOT multiples of 2.54mm.
# Result: All wires disconnected from all pins. User lost manual edits.
# Fix: Only snap component centers, then recalculate wire endpoints.
#
# 10B. ALWAYS COMMIT BEFORE MODIFYING THE SCHEMATIC
# --------------------------------------------------
# Before running ANY script that modifies SampleCircuit.kicad_sch, ALWAYS:
#   1. Ask the user to save in KiCad
#   2. git add + git commit the current state
#   3. THEN run the modification
# This ensures manual edits can always be recovered from git history.
#
# 10C. FLASH AND SD CARD NEED SEPARATE CHIP SELECTS
# --------------------------------------------------
# Both flash and SD card share the SPI bus (MISO/MOSI/CLK).
# They MUST have separate CS lines: CS_FLASH (IO8) and CS_SD (IO18).
# Originally both used CS_SD — fixed by creating CS_FLASH port symbol.
#
# 10D. LOCKED TEMPLATES RETURN None FROM build_schematic()
# --------------------------------------------------------
# Several templates check lock status inside build_schematic() and return
# None when locked. The master build script must handle this by falling
# back to reading the pre-built .kicad_sch file from the template directory.
#
# 10E. KICAD AUTO-CONNECT CANNOT BE DISABLED
# -------------------------------------------
# When dragging (G key) components over existing wires, KiCad automatically
# creates connections. There is NO setting to disable this behavior.
# Workaround: Use M (Move) instead of G (Drag) to avoid accidental connections.
# M disconnects everything; G maintains and creates connections.
#
# 10F. PIN OFFSETS VARY BY COMPONENT
# -----------------------------------
# 0805 caps: pins at ±3.81mm (NOT ±2.54mm)
# 0805 resistors: pins at ±5.08mm (JLCImport horizontal orientation)
# Always verify pin positions from the library — never assume.


# =============================================================================
# 11. PYTHON ENVIRONMENT
# =============================================================================
# Python: C:/Users/peter.LAKEMAST/AppData/Local/Python/bin/python.exe
# No virtual environment — system Python with standard library only.
# All build scripts use: importlib, re, uuid, json, os, sys, shutil


# END OF SPEC
