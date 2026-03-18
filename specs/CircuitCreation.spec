# =============================================================================
# CIRCUIT CREATION SPECIFICATION — CircuitAI Project
# =============================================================================
# This spec defines mandatory design rules for creating new circuits in the
# CircuitAI project. All circuit templates and parent schematics MUST follow
# these rules.
#
# Version: 1.0
# Date: March 2026
# Applies to: All .kicad_sch files and build scripts in this project


# =============================================================================
# 1. BUS REQUIREMENTS — MANDATORY SUPPORT CIRCUITS
# =============================================================================
# When a circuit uses a shared bus, the parent schematic (or a dedicated bus
# sheet) MUST include the required support components. Individual device
# templates must NOT include bus-level components — only ONE set per bus.


# -----------------------------------------------------------------------------
# 1A. I2C BUS (SCL / SDA)
# -----------------------------------------------------------------------------
# Any circuit using I2C MUST have exactly ONE pair of pull-up resistors on the
# bus. These go on the parent sheet or a dedicated I2C bus sheet — NEVER on
# individual device sub-sheets (RTC, flash, sensor, etc.).
#
# Rule: If SCL and SDA port symbols appear anywhere in the design, the parent
#       schematic MUST include R_SCL and R_SDA pull-ups to +3.3V.
#
# Why 4.7k: Standard value for 3.3V I2C at 100/400 kHz. Rise time meets spec
#            with typical bus capacitance (<200pF). For 1MHz Fast Mode Plus,
#            consider 2.2k instead.
#
# WARNING: Multiple pull-ups in parallel (one per device sheet) will lower
#          the effective resistance and violate I2C spec. Example: three 4.7k
#          in parallel = 1.57k, which draws ~2.1mA per line — excessive for
#          most I2C devices and may cause logic level issues.

# CRITICAL: ONE set of pull-ups per I2C bus for the ENTIRE circuit.
# Even if you have 5 I2C devices (RTC, sensor, EEPROM, etc.), you still
# only place ONE R_SCL and ONE R_SDA. The pull-ups serve the bus, not
# individual devices. Adding pull-ups per device is a common mistake.
#
# [Component] I2C SCL Pull-up Resistor
#   Ref:        R_SCL (assigned by parent schematic)
#   Value:      4.7k 1%
#   Symbol:     JLCImport:0805W8F4701T5E
#   Package:    0805
#   LCSC:       C17673
#   JLCPCB:     Basic part
#   Nets:       Pin1 → +3.3V, Pin2 → SCL
#   Placement:  Parent sheet or I2C bus sheet, near MCU or bus connector

# [Component] I2C SDA Pull-up Resistor
#   Ref:        R_SDA (assigned by parent schematic)
#   Value:      4.7k 1%
#   Symbol:     JLCImport:0805W8F4701T5E
#   Package:    0805
#   LCSC:       C17673
#   JLCPCB:     Basic part
#   Nets:       Pin1 → +3.3V, Pin2 → SDA
#   Placement:  Parent sheet or I2C bus sheet, near MCU or bus connector

# I2C Pull-up BOM Summary:
#   Ref     | Value   | Pkg  | LCSC    | Type  | Qty
#   R_SCL   | 4.7k 1% | 0805 | C17673  | Basic | 1
#   R_SDA   | 4.7k 1% | 0805 | C17673  | Basic | 1


# -----------------------------------------------------------------------------
# 1B. SPI BUS (SCK / MOSI / MISO / CS)
# -----------------------------------------------------------------------------
# SPI does not require pull-ups on data lines. However:
# - Each CS (chip select) line needs a 10k pull-up to +3.3V to keep devices
#   deselected during MCU boot/reset.
# - CS pull-ups go on the PARENT sheet, one per SPI device.
#
# [Component] SPI CS Pull-up (per device)
#   Value:      10k 1%
#   Symbol:     JLCImport:0805W8F1002T5E
#   Package:    0805
#   LCSC:       C17414
#   JLCPCB:     Basic part
#   Nets:       Pin1 → +3.3V, Pin2 → CS_x


# =============================================================================
# 2. POWER DECOUPLING RULES
# =============================================================================
# Every IC MUST have a 100nF decoupling capacitor on its VDD/VCC pin, placed
# as close as possible to the IC. This cap goes on the SAME sheet as the IC.
#
# Standard decoupling cap:
#   Symbol:     JLCImport:CC0805KRX7R9BB104
#   Value:      100nF 50V
#   Package:    0805
#   LCSC:       C49678
#   JLCPCB:     Basic part
#
# Exception: If an IC's template spec explicitly states that VDD decoupling
# is handled on the parent sheet (e.g., rtc_rv3028 where VBACKUP has the cap
# but VDD is decoupled on the parent), follow the template spec.


# =============================================================================
# 3. COMPONENT STANDARDS
# =============================================================================
# MINIMUM PACKAGE SIZE: All SMD passives (resistors, capacitors, inductors)
# must be 0805 or larger. DO NOT use 0402 or 0603 packages — they are too
# small for hand rework and visual inspection. Larger packages (1206, 1210,
# etc.) are acceptable when required by voltage/current rating.
#
# All passive components use these JLCPCB basic parts unless the circuit spec
# explicitly requires a different value:
#
# Resistors (0805, 1%, UNI-ROYAL):
#   Value   | Symbol                      | LCSC    | Type
#   100R    | JLCImport:0805W8F1000T5E    | C17408  | Basic
#   1k      | JLCImport:0805W8F1001T5E    | C17513  | Basic
#   4.7k    | JLCImport:0805W8F4701T5E    | C17673  | Basic
#   10k     | JLCImport:0805W8F1002T5E    | C17414  | Basic
#   100k    | JLCImport:0805W8F1003T5E    | C17407  | Basic
#
# Capacitors (0805):
#   Value   | Symbol                      | LCSC    | Type
#   100nF   | JLCImport:CC0805KRX7R9BB104 | C49678  | Basic (YAGEO)
#   1uF     | JLCImport:CC0805KRX7R7BB105 | C28323  | Basic (YAGEO)
#   10uF    | JLCImport:CL21A106KAYNNNE    | C15850  | Basic (Samsung)
#
# Diodes:
#   Value    | Symbol                     | LCSC    | Type
#   1N4148W  | JLCImport:1N4148W          | C2099   | Basic (SOD-123)
#
# MOSFETs:
#   Value   | Symbol                      | LCSC    | Type
#   2N7002  | JLCImport:2N7002            | C8545   | Basic (SOT-23, N-ch)
#
# NOTE: JLCImport symbol names are manufacturer part numbers, NOT generic
# values. Set the "Value" property on the schematic instance to the
# human-readable value (e.g., "10k", "100nF").
#
# All resistors and capacitors: hide pin_numbers AND pin_names in lib_symbol.


# =============================================================================
# 4. TEMPLATE vs PARENT SHEET RESPONSIBILITIES
# =============================================================================
#
# TEMPLATE (device sub-sheet) includes:
#   - The IC and its directly-connected passives (decoupling caps, pull-downs,
#     current limiters, etc.)
#   - Port symbols (SCL, SDA, etc.) for bus connections
#   - Power symbols (+3.3V, GND) for rails
#   - No-connect flags on unused pins
#
# PARENT SHEET includes:
#   - Bus pull-ups (I2C 4.7k, SPI CS 10k)
#   - Bus-level components (level shifters, bus buffers)
#   - MCU connections
#   - Power regulation and bulk decoupling
#   - Connectors and headers
#
# Rule: If a component serves a SINGLE device, it goes in the template.
#       If it serves the BUS (shared by multiple devices), it goes on the parent.


# =============================================================================
# 5. REFERENCE DESIGNATOR RANGES
# =============================================================================
# To avoid conflicts when templates are instantiated on the parent schematic,
# each circuit template uses a reserved reference designator range:
#
# Circuit              | U   | R       | C       | B   | Other
# ---------------------|-----|---------|---------|-----|--------
# ESP32-S3 Core        | U1  | R1-R9   | C1-C4   | —   | Y1
# PSU (LM2596S)        | U2  | R10-R19 | C5-C9   | —   | D1, L1
# Relay Driver         | U3  | R20-R29 | C11-C14 | —   | Q1, K1
# Audio (MAX98357A)    | U4  | R30-R39 | C15-C19 | —   | SP1
# RTC (RV-3028-C7)     | U8  | R40-R49 | C10     | B3  | —
# Flash (W25Q128JVS)   | U9  | R50-R59 | C20-C24 | —   | —
# USB (CH340N)         | U10 | R60-R69 | C25-C29 | —   | —
# I2C Bus (parent)     | —   | R70-R79 | —       | —   | —
# SPI Bus (parent)     | —   | R80-R89 | —       | —   | —


# =============================================================================
# 6. CHECKLIST — NEW CIRCUIT CREATION
# =============================================================================
# Before creating a new circuit template:
#
# [ ] Read templates/TemplateCreation.spec for schematic generation rules
# [ ] Read this file (specs/CircuitCreation.spec) for bus requirements
# [ ] Identify which buses the circuit uses (I2C, SPI, UART, etc.)
# [ ] Verify bus pull-ups are specified for the parent sheet
# [ ] Choose reference designators from the reserved range (section 5)
# [ ] Use standard JLCPCB parts from section 3 where possible
# [ ] Create circuit-specific .spec in templates/<circuit_name>/
# [ ] Create build script that reads from library files (not hardcoded)
# [ ] Run build script and verify in KiCad
# [ ] Run ERC — must pass clean


# =============================================================================
# 7. LESSONS LEARNED — COMMON MISTAKES
# =============================================================================
# These are verified gotchas from building real circuits. Violating them
# produces broken schematics or incorrect designs.
#
# 7A. PIN ENDPOINT FORMULA
# ------------------------
# For a symbol placed at (sx, sy) with angle=0:
#   schematic_pos = (sx + pin_local_x, sy - pin_local_y)
# KiCad schematic Y increases DOWNWARD, but symbol Y increases UPWARD.
# This Y-negation catches everyone. Round to 2 decimal places.
#
# 7B. WIRE ENDPOINTS MUST MATCH PIN ENDPOINTS EXACTLY
# ----------------------------------------------------
# A wire endpoint that is off by even 0.01mm from a pin endpoint will
# NOT connect. Always calculate pin positions using the formula above.
#
# 7C. ALL COORDINATES ON 1.27mm (50 mil) GRID
# --------------------------------------------
# Every component center, wire endpoint, and symbol position MUST be a
# multiple of 1.27mm. Off-grid components cause wiring nightmares.
#   snap(val) = round(round(val / 1.27) * 1.27, 2)
#
# 7D. JLCPCB R/C SYMBOLS ARE HORIZONTAL
# ---------------------------------------
# JLCImport resistors/capacitors have pins at (±5.08, 0) — HORIZONTAL.
# This differs from KiCad built-in Device:R/C which are vertical.
# Use angle=90 or angle=270 to rotate vertically.
# For decoupling caps: angle=270 puts pin 1 (signal) on TOP, pin 2 (GND)
# on BOTTOM — the correct orientation for most decoupling setups.
#
# 7E. HIDE PIN NUMBERS/NAMES ON PASSIVES
# ----------------------------------------
# JLCImport passive symbols often have visible pin numbers ("1", "2").
# These overlap and clutter the schematic. In the lib_symbol definition,
# add BOTH:
#   (pin_numbers (hide yes))
#   (pin_names (offset 1.016) (hide yes))
# Per-pin (hide) is NOT sufficient in KiCad 9. You MUST use symbol-level
# hide directives.
#
# 7F. ONE SET OF BUS PULL-UPS — NOT PER DEVICE
# ---------------------------------------------
# This is worth repeating: I2C pull-ups go on the PARENT sheet, and you
# place exactly ONE set for the entire bus regardless of how many I2C
# devices exist. Three 4.7k in parallel = 1.57k effective — this draws
# excessive current and may violate I2C spec.
#
# 7G. POWER SYMBOLS ARE GLOBAL — NO HIERARCHICAL LABELS FOR POWER
# ----------------------------------------------------------------
# Use power:+3.3V and power:GND symbols, NOT hierarchical labels.
# Power symbols automatically connect across all sheets in the hierarchy.
#
# 7H. COMPONENT SPACING GUIDELINES
# ---------------------------------
#   - IC to passive: minimum 15mm between centers
#   - Passive to passive: minimum 12mm between centers
#   - GND symbol to component pin: 8-10mm vertical gap
#   - +3.3V symbol to IC power pin: 5-8mm vertical gap
#   - Group related components on the same horizontal/vertical line


# 7I. COMPONENT SUBSTITUTION RULES
# ---------------------------------
# ALLOWED without asking: Substituting a different manufacturer's part
# with the SAME value AND SAME (or larger) package size. For example,
# swapping one 680uF 35V SMD electrolytic for another brand's 680uF 35V
# SMD electrolytic is fine — the circuit behavior is identical.
#
# REQUIRES explicit user approval:
#   - Changing component VALUES (e.g., 100k → 10k, 47uF → 22uF)
#   - Using a SMALLER package size (e.g., 0805 → 0603)
#   - Removing components from the design
#   - Changing the circuit topology
#
# If a component is not found in JLCImport or the jlcimport-cli fails:
#   1. Try to find a same-value, same-or-larger-package substitute
#   2. If no substitute exists, report the missing part to the user
#   3. Wait for explicit approval before ANY design changes
#
# Acceptable workarounds:
#   - Manually add the symbol to JLCImport.kicad_sym by copying an existing
#     symbol of the same package type
#   - Try importing again with a different method
#   - Ask the user if they want to proceed without that component


# END OF SPEC
