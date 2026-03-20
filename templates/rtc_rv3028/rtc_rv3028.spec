# =============================================================================
# TEMPLATE: RV-3028-C7 Real-Time Clock with Battery Backup
# =============================================================================
# Prerequisites: Read templates/TemplateCreation.spec FIRST for universal rules.
# This file covers ONLY circuit-specific details for the RTC template.
#
# Template Version: 2.0
# Date: March 2026
# Status: First-pass wired, awaiting human review in KiCad


# =============================================================================
# 1. OVERVIEW
# =============================================================================
# Ultra-low-power I2C RTC with coin cell backup battery.
# Fixed I2C address 0x52. Keeps time when main power is off.
# 5 components + coin cell holder. No I2C pull-ups (they go on the bus).


# =============================================================================
# 2. INTERFACE (what the parent schematic connects to)
# =============================================================================
# Type          | Name  | Shape         | Notes
# --------------|-------|---------------|-------------------------------
# Port symbol   | SCL   | Ports:SCL     | I2C clock bus (global via power flag)
# Port symbol   | SDA   | Ports:SDA     | I2C data bus (global via power flag)
# Power symbol  | +3.3V | power:+3.3V   | Global — auto-connects across sheets
# Power symbol  | GND   | power:GND     | Global — auto-connects across sheets
#
# SCL and SDA use custom port symbols from Ports.kicad_sym (see TemplateCreation.spec §7).
# These are power-style symbols — they auto-connect across sheets like +3.3V/GND.


# =============================================================================
# 3. DESIGN NOTES (circuit-specific decisions)
# =============================================================================
# - EVI pin (pin 8): Unused event input — tied low via R41 (10k pull-down)
# - CLKOUT (pin 1): Unused — no-connect flag
# - ~INT (pin 2): Unused — no-connect flag (EV4 Rev C had INT shorted to SDA)
# - R46 limits charge/discharge current to coin cell (3V/1k = 3mA max)
# - C10 decouples VBACKUP, NOT VDD (VDD decoupled on parent sheet)
# - I2C pull-ups NOT included — they belong on the I2C bus, not per-device
# - RV-3028-C7 has NO exposed pad (thermal pad) — only 8 pins


# =============================================================================
# 4. INTERNAL NETS (stay inside this sheet — NOT exposed)
# =============================================================================
# Net Name    | Path
# ------------|----------------------------------------------------
# VBACKUP     | U8.pin6 → R46.pin1 → C10.pin1 (junction) → R46.pin2 → B3.pin1
# EVI_INT     | U8.pin8 → R41.pin1, R41.pin2 → GND
# (CLKOUT)    | U8.pin1 → no-connect
# (~INT)      | U8.pin2 → no-connect


# =============================================================================
# 5. COMPONENTS — ALL FROM JLCPCB
# =============================================================================

# [U8] RV-3028-C7 — I2C RTC
#   LCSC:      C3019759
#   Symbol:    JLCImport:RV-3028-C7_32_768KHZ_1PPM_TA_QC
#   Package:   SON-8 (1.5x3.2mm)
#   JLCPCB:    Extended part
#   I2C Addr:  0x52 (fixed)
#   VDD Range: 1.1V to 5.5V
#   Backup:    40nA typical at 3.0V VBACKUP
#   Pin assignments:
#     Pin 1 CLKOUT  → NC (no-connect)
#     Pin 2 ~INT    → NC (no-connect)
#     Pin 3 SCL     → SCL global label
#     Pin 4 SDA     → SDA global label
#     Pin 5 VSS     → GND (power symbol)
#     Pin 6 VBACKUP → VBACKUP net → R46, C10
#     Pin 7 VDD     → +3.3V (power symbol)
#     Pin 8 EVI     → R41 → GND
#   lib_symbol notes:
#     - Hide pin_numbers: YES (add (pin_numbers (hide yes)))
#     - Keep pin_names visible (SCL, SDA, VDD, etc. are useful)

# [C10] 100nF Capacitor — VBACKUP decoupling
#   LCSC:      C49678
#   Symbol:    JLCImport:CC0805KRX7R9BB104
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 → VBACKUP net, Pin2 → GND
#   Note:      Place close to U8 pin 6. Decouples VBACKUP, NOT VDD.
#   lib_symbol notes:
#     - Hide pin_numbers AND pin_names (passive — no useful pin names)
#     - Horizontal symbol (pins at ±5.08, y=0) — rotate angle=270 for vertical

# [B3] CR2032 Coin Cell Holder
#   LCSC:      C70376
#   Symbol:    JLCImport:CR2032-BS-2-1
#   Package:   THT holder
#   JLCPCB:    Extended part
#   Battery:   CR2032 (3V, ~40mAh) — >10 years at 40nA
#   Nets:      Pin1 (POS) → R46, Pin2 (NEG) → GND
#   lib_symbol notes:
#     - Hide pin_numbers AND pin_names (just "1"/"2" — clutters display)

# [R46] 1k Resistor — Battery current limiter
#   LCSC:      C17513
#   Symbol:    JLCImport:0805W8F1001T5E
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 → VBACKUP (U8 pin 6), Pin2 → B3.POS
#   lib_symbol notes:
#     - Hide pin_numbers AND pin_names

# [R41] 10k Resistor — EVI pull-down
#   LCSC:      C17414
#   Symbol:    JLCImport:0805W8F1002T5E
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 → U8.EVI (pin 8), Pin2 → GND
#   lib_symbol notes:
#     - Hide pin_numbers AND pin_names


# =============================================================================
# 6. JLCPCB BOM SUMMARY
# =============================================================================
#
# Ref  | Part             | Value     | Pkg   | LCSC     | Type
# -----|------------------|-----------|-------|----------|----------
# U8   | RV-3028-C7       | —         | SON-8 | C3019759 | Extended
# C10  | Capacitor        | 100nF 50V | 0805  | C49678   | Basic
# B3   | Coin cell holder | CR2032    | THT   | C70376   | Extended
# R46  | Resistor         | 1k 1%     | 0805  | C17513   | Basic
# R41  | Resistor         | 10k 1%    | 0805  | C17414   | Basic
#
# Total: 5 components (3 basic, 2 extended)
# JLCPCB extended part fee: ~$3/unique extended × 2 = ~$6 setup


# =============================================================================
# 7. SCHEMATIC LAYOUT — CURRENT POSITIONS (all on 1.27mm grid)
# =============================================================================
# All coordinates in mm on A4 sheet, snapped to 1.27mm grid.
# Grid formula: snap(val) = round(round(val / 1.27) * 1.27, 2)
#
# Component    | Position (x, y)     | Angle | Notes
# -------------|---------------------|-------|----------------------------------
# U8 (RTC)     | (149.86, 100.33)    | 0     | Center of sheet, IC body
# R41 (10k)    | (180.34, 96.52)     | 0     | Horizontal, near EVI pin
# C10 (100nF)  | (175.26, 106.68)    | 90    | Vertical (pin1 top, pin2 bottom)
# R46 (1k)     | (193.04, 101.60)    | 0     | Horizontal, VBACKUP chain
# B3 (CR2032)  | (210.82, 101.60)    | 0     | Far right, battery holder
#
# Port symbols (Ports library — see TemplateCreation.spec §7):
#   SCL        | (128.27, 100.33)    | 0     | Pin at (130.81, 100.33)
#   SDA        | (128.27, 105.41)    | 0     | Pin at (130.81, 105.41)
#
# Power symbols:
#   +3.3V      | (168.91, 91.44)     | 0     | Above U8.VDD, L-route
#   GND #PWR02 | (165.10, 109.22)    | 0     | Below U8.VSS
#   GND #PWR03 | (193.04, 96.52)     | 90    | Beside R41.pin2, rotated sideways
#   GND #PWR04 | (175.26, 114.30)    | 0     | Below C10.pin2
#   GND #PWR05 | (215.90, 106.68)    | 0     | Below B3.pin2
#
# No-connects:
#   CLKOUT     | U8 pin 1 endpoint   |       | Unused clock output
#   ~INT       | U8 pin 2 endpoint   |       | Unused interrupt


# =============================================================================
# 8. PIN ENDPOINTS (for wiring — from KiCad-saved schematic)
# =============================================================================
# These are the ACTUAL wire connection points in schematic coordinates.
# Formula: schematic_pos = (sym_x + pin_local_x, sym_y - pin_local_y)
# NOTE: KiCad negates the lib_symbol local Y when placing in schematic coords.
#
# U8 at (149.86, 100.33), angle=0:
#   Pin 1 CLKOUT:  (134.62, 96.52)   — left side
#   Pin 2 ~INT:    (134.62, 99.06)   — left side
#   Pin 3 SCL:     (134.62, 101.6)   — left side
#   Pin 4 SDA:     (134.62, 104.14)  — left side
#   Pin 5 VSS:     (165.1, 104.14)   — right side
#   Pin 6 VBACKUP: (165.1, 101.6)    — right side
#   Pin 7 VDD:     (165.1, 99.06)    — right side
#   Pin 8 EVI:     (165.1, 96.52)    — right side
#
# R41 at (180.34, 96.52), angle=0 (horizontal):
#   Pin 1: (175.26, 96.52)  — left
#   Pin 2: (185.42, 96.52)  — right
#
# C10 at (175.26, 106.68), angle=90 (vertical, pin1=top):
#   Pin 1: (175.26, 101.6)  — top
#   Pin 2: (175.26, 111.76) — bottom
#
# R46 at (193.04, 101.6), angle=0 (horizontal):
#   Pin 1: (187.96, 101.6)  — left
#   Pin 2: (198.12, 101.6)  — right
#
# B3 at (210.82, 101.6), angle=0 (horizontal):
#   Pin 1: (205.74, 101.6)  — left (POS)
#   Pin 2: (215.9, 101.6)   — right (NEG)


# =============================================================================
# 9. WIRING CONNECTIONS (verified against KiCad-saved schematic)
# =============================================================================
# Each wire is listed as: from_point → to_point
# All coordinates verified against KiCad 9.0 saved file.
#
# Signal wires (L-route via corner at x=133.35):
#   SCL port pin (130.81, 100.33) → (133.35, 100.33)      — horizontal
#   (133.35, 100.33) → (133.35, 101.6)                    — vertical down
#   (133.35, 101.6) → U8.SCL (134.62, 101.6)             — horizontal
#   SDA port pin (130.81, 105.41) → (133.35, 105.41)      — horizontal
#   (133.35, 105.41) → (133.35, 104.14)                   — vertical up
#   (133.35, 104.14) → U8.SDA (134.62, 104.14)           — horizontal
#
# Power wires (L-route for +3.3V):
#   +3.3V (168.91, 91.44) → (168.91, 99.06)              — vertical down
#   (168.91, 99.06) → U8.VDD (165.1, 99.06)              — horizontal left
#   U8.VSS (165.1, 104.14) → GND (165.1, 109.22)         — vertical down
#
# EVI chain (pin 8 → R41 → GND):
#   U8.EVI (165.1, 96.52) → R41.pin1 (175.26, 96.52)     — horizontal right
#   R41.pin2 (185.42, 96.52) → GND3 (193.04, 96.52)      — horizontal right
#
# VBACKUP chain (pin 6 → junction → R46 → B3):
#   U8.VBACKUP (165.1, 101.6) → junction (175.26, 101.6)  — horizontal
#   junction (175.26, 101.6) → R46.pin1 (187.96, 101.6)   — horizontal
#   R46.pin2 (198.12, 101.6) → B3.pin1 (205.74, 101.6)   — horizontal
#
# C10 decoupling (tee off VBACKUP net at junction):
#   Junction at (175.26, 101.6) on VBACKUP wire
#   C10.pin2 (175.26, 111.76) → GND4 (175.26, 114.3)     — vertical down
#
# B3 ground:
#   B3.pin2 (215.9, 101.6) → GND5 (215.9, 106.68)        — vertical down


# =============================================================================
# 10. VERIFICATION CHECKLIST
# =============================================================================
# [ ] U8.SCL (pin 3) connected to SCL global label
# [ ] U8.SDA (pin 4) connected to SDA global label
# [ ] U8.VDD (pin 7) connected to +3.3V power symbol
# [ ] U8.VSS (pin 5) connected to GND power symbol
# [ ] U8.VBACKUP (pin 6) → C10.pin1 AND R46.pin1 (junction on net)
# [ ] C10.pin2 → GND
# [ ] R46.pin2 → B3.pin1 (positive terminal)
# [ ] B3.pin2 → GND
# [ ] U8.EVI (pin 8) → R41.pin1
# [ ] R41.pin2 → GND
# [ ] U8.CLKOUT (pin 1) has no-connect flag
# [ ] U8.~INT (pin 2) has no-connect flag
# [ ] No I2C pull-ups inside this sheet
# [ ] All pin numbers hidden (no "12" clutter on passives/battery)
# [ ] SCL/SDA render as diamond-shaped global labels
# [ ] All component values match BOM table
# [ ] ERC passes clean


# =============================================================================
# 11. OPTIONAL ENHANCEMENTS (not in current design)
# =============================================================================
# 1. ~INT output: Change pin 2 from NC to global label "RTC_INT" for
#    timed interrupts or alarm wakeup. Route to an ESP32 GPIO.
#
# 2. CLKOUT: Add global label "RTC_CLKOUT" on pin 1 for a 32.768kHz
#    or 1Hz reference clock output.
#
# 3. VDD decoupling: Add 100nF cap on VDD if per-device decoupling
#    is preferred over parent-sheet decoupling.
#
# 4. Supercap backup: Replace B3 with 0.1F supercap for rechargeable
#    backup. RV-3028 supports trickle charging via EEPROM register 0x37.

# END OF TEMPLATE
