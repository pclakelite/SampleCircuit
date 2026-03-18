# =============================================================================
# TEMPLATE: LMZM23601SILR 12V to 5V Buck Regulator
# =============================================================================
# Prerequisites: Read templates/TemplateCreation.spec FIRST for universal rules.
# This file covers ONLY circuit-specific details for the 5V PSU template.
#
# Template Version: 1.0
# Date: March 2026
# Status: Locked — human-reviewed, wiring verified in KiCad

# =============================================================================
# 1. OVERVIEW
# =============================================================================
# TI LMZM23601 power module — 36V-input, 1A step-down DC-DC converter.
# Converts +12V input to +5V output for downstream circuits.
# Vref = 1.0V, feedback divider sets output:
#   Vout = Vref * (1 + R3/R4) = 1.0 * (1 + 10k/2.49k) = 5.016V
# Integrated inductor — minimal external components.


# =============================================================================
# 2. INTERFACE (what the parent schematic connects to)
# =============================================================================
# Type          | Name    | Shape         | Notes
# --------------|---------|---------------|-------------------------------
# Power symbol  | +12V    | power:+12V    | Global — input supply
# Power symbol  | +5V     | power:+5V     | Global — regulated output
# Power symbol  | GND     | power:GND     | Global — auto-connects across sheets
#
# No signal ports — this is a pure power supply module.


# =============================================================================
# 3. DESIGN NOTES (circuit-specific decisions)
# =============================================================================
# - EN (pin 4): Tied to VIN rail for always-on operation
# - MODE/SYNC (pin 2): Tied to GND for forced PWM mode
# - PGOOD (pin 5): No-connect (open-drain, unused)
# - DNC pins (8, 9, 10): Do-Not-Connect per datasheet
# - EP (pin 11): Exposed pad, connected to GND
# - Feedback divider: R3 (10k top) / R4 (2.49k bottom) → ~5.0V out
# - Two 10uF 35V input caps (C31, C33) in parallel for decoupling
# - One 47uF 16V output cap (C32) for output filtering
# - NOTE: JLCImport pin numbering for LMZM23601SILR differs from datasheet.
#   Use pin NAMES (VIN, VOUT, FB, etc.) not numbers for wiring reference.


# =============================================================================
# 4. INTERNAL NETS (stay inside this sheet — NOT exposed)
# =============================================================================
# Net Name    | Path
# ------------|----------------------------------------------------
# VIN_RAIL    | +12V → C31.pin2 → C33.pin2 → U6.VIN, U6.EN
# FB_DIV      | U6.FB → R3.pin2 / R4 junction
#             | R3.pin1 → VOUT rail (+5V)
#             | R4.pin2 → GND
# VOUT_RAIL   | U6.VOUT → R3.pin1 area → C32.pin1 → +5V


# =============================================================================
# 5. COMPONENTS — ALL FROM JLCPCB
# =============================================================================

# [U6] LMZM23601SILR — 36V 1A Step-Down Power Module
#   LCSC:      C2685821
#   Symbol:    JLCImport:LMZM23601SILR
#   Package:   USIP-10 (3.8x3.0mm)
#   JLCPCB:    Extended part
#   Vin Range: 4V to 36V
#   Vout:      Adjustable (set by feedback divider)
#   Vref:      1.0V
#   Iout:      1A max
#   JLCImport pin assignments (NOTE: numbering differs from datasheet):
#     Pin 1  GND       → GND (via sideways GND symbol at angle=270)
#     Pin 2  MODE/SYNC → GND (forced PWM, via corner routing)
#     Pin 3  VIN       → VIN rail
#     Pin 4  EN        → VIN rail (always-on)
#     Pin 5  PGOOD     → NC (unused)
#     Pin 6  VOUT      → VOUT rail (+5V)
#     Pin 7  FB        → Feedback divider junction
#     Pin 8  DNC       → NC (do not connect)
#     Pin 9  DNC       → NC (do not connect)
#     Pin 10 DNC       → NC (do not connect)
#     Pin 11 EP        → GND (exposed pad, via sideways GND at angle=90)

# [R3] 10k Resistor — Feedback upper resistor
#   LCSC:      C17414
#   Symbol:    JLCImport:0805W8F1002T5E
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 (left) → VOUT junction, Pin2 (right) → FB junction

# [R4] 2.49k Resistor — Feedback lower resistor
#   LCSC:      C21237
#   Symbol:    JLCImport:0805W8F2491T5E
#   Package:   0805
#   JLCPCB:    Basic part (searched via WebFetch)
#   Nets:      Pin1 (top) → FB junction, Pin2 (bottom) → GND
#   Note:      Placed at angle=270 for vertical orientation

# [C31] 10uF 35V Capacitor — Input decoupling #1
#   LCSC:      C97973
#   Symbol:    JLCImport:GRM32ER7YA106KA12L
#   Package:   1210 (Murata X7R)
#   JLCPCB:    Extended part
#   Nets:      Pin 2 (top) → VIN rail, Pin 1 (bottom) → GND rail
#   Note:      Natively vertical symbol. Pin 2 at top, Pin 1 at bottom.

# [C33] 10uF 35V Capacitor — Input decoupling #2
#   LCSC:      C97973
#   Symbol:    JLCImport:GRM32ER7YA106KA12L
#   Package:   1210 (Murata X7R)
#   JLCPCB:    Extended part
#   Nets:      Pin 2 (top) → VIN rail, Pin 1 (bottom) → GND rail
#   Note:      Same part as C31, staggered placement

# [C32] 47uF 16V Capacitor — Output decoupling
#   LCSC:      C172351
#   Symbol:    JLCImport:1206X476M160NT
#   Package:   1206
#   JLCPCB:    Extended part
#   Nets:      Pin1 (top) → VOUT rail, Pin2 (bottom) → GND rail
#   Note:      Placed at angle=270 for vertical orientation


# =============================================================================
# 6. JLCPCB BOM SUMMARY
# =============================================================================
#
# Ref  | Part             | Value         | Pkg    | LCSC     | Type
# -----|------------------|---------------|--------|----------|----------
# U6   | LMZM23601SILR    | —             | USIP10 | C2685821 | Extended
# C31  | GRM32ER7YA106KA12L| 10uF 35V X7R | 1210   | C97973   | Extended
# C33  | GRM32ER7YA106KA12L| 10uF 35V X7R | 1210   | C97973   | Extended
# R3   | 0805W8F1002T5E   | 10k 1%        | 0805   | C17414   | Basic
# R4   | 0805W8F2491T5E   | 2.49k 1%      | 0805   | C21237   | Basic
# C32  | 1206X476M160NT   | 47uF 16V      | 1206   | C172351  | Extended
#
# Total: 6 components (2 basic, 4 extended)


# =============================================================================
# 7. SCHEMATIC LAYOUT — POSITIONS (all on 1.27mm grid)
# =============================================================================
# Component    | Position (x, y)     | Angle | Notes
# -------------|---------------------|-------|----------------------------------
# U6 (IC)      | (149.86, 100.33)    | 0     | Center of sheet
# C31 (10uF)   | (105.41, 111.76)    | 0     | Vertical (native), pin2 top
# C33 (10uF)   | (116.84, 109.22)    | 0     | Vertical (native), staggered Y
# R3 (10k)     | (173.99, 109.22)    | 0     | Horizontal, VOUT→FB
# R4 (2.49k)   | (186.69, 124.46)    | 270   | Vertical, FB(top)→GND(bot)
# C32 (47uF)   | (167.64, 124.46)    | 270   | Vertical, VOUT(top)→GND(bot)
#
# Power symbols:
#   +12V       | (102.87, 99.06)     | 0     | Above VIN rail
#   +5V        | (170.18, 100.33)    | 0     | Above output rail
#   GND #PWR02 | (116.84, 123.19)    | 0     | Below input caps
#   GND #PWR03 | (128.27, 96.52)     | 270   | Beside U6.GND pin (sideways left)
#   GND #PWR04 | (173.99, 93.98)     | 90    | Beside U6.EP (sideways right)
#   GND #PWR05 | (175.26, 132.08)    | 0     | Below output section
#
# No-connects:
#   PGOOD      | U6 pin 5: (135.89, 106.68)
#   DNC pin 8  | U6 pin 8: (163.83, 101.60)
#   DNC pin 9  | U6 pin 9: (163.83, 99.06)
#   DNC pin 10 | U6 pin 10: (163.83, 96.52)


# =============================================================================
# 8. PIN ENDPOINTS (for wiring)
# =============================================================================
# U6 at (149.86, 100.33), angle=0:
#   Pin 1  GND:       (135.89, 96.52)   — left side
#   Pin 2  MODE/SYNC: (135.89, 99.06)   — left side
#   Pin 3  VIN:       (135.89, 101.60)   — left side
#   Pin 4  EN:        (135.89, 104.14)   — left side
#   Pin 5  PGOOD:     (135.89, 106.68)   — left side
#   Pin 6  VOUT:      (163.83, 106.68)   — right side
#   Pin 7  FB:        (163.83, 104.14)   — right side
#   Pin 8  DNC:       (163.83, 101.60)   — right side
#   Pin 9  DNC:       (163.83, 99.06)    — right side
#   Pin 10 DNC:       (163.83, 96.52)    — right side
#   Pin 11 EP:        (163.83, 93.98)    — right side
#
# C31 at (105.41, 111.76), angle=0 (native vertical):
#   Pin 1: (105.41, 116.84) — bottom (GND)
#   Pin 2: (105.41, 106.68) — top (VIN rail)
#
# C33 at (116.84, 109.22), angle=0 (native vertical):
#   Pin 1: (116.84, 114.30) — bottom (GND)
#   Pin 2: (116.84, 104.14) — top (VIN rail)
#
# R3 at (173.99, 109.22), angle=0 (horizontal):
#   Pin 1: (168.91, 109.22) — left (VOUT junction)
#   Pin 2: (179.07, 109.22) — right (FB junction)
#
# R4 at (186.69, 124.46), angle=270:
#   Pin 1: (186.69, 119.38) — top (FB junction)
#   Pin 2: (186.69, 129.54) — bottom (GND)
#
# C32 at (167.64, 124.46), angle=270:
#   Pin 1: (167.64, 119.38) — top (VOUT)
#   Pin 2: (167.64, 129.54) — bottom (GND)


# =============================================================================
# 9. WIRING CONNECTIONS
# =============================================================================
# Input power chain:
#   +12V (102.87, 99.06) → (102.87, 102.87)                    — vertical down
#   (102.87, 102.87) → (105.41, 102.87)                         — VIN rail start
#   C31.pin2 (105.41, 106.68) → (105.41, 102.87)               — up to VIN rail
#   (105.41, 102.87) → (116.84, 102.87)                         — VIN rail segment
#   C33.pin2 (116.84, 104.14) → (116.84, 102.87)               — up to VIN rail
#   (116.84, 102.87) → (135.89, 102.87)                         — VIN rail to IC
#   (135.89, 102.87) → (135.89, 101.60) U6.VIN                  — down to VIN pin
#   U6.EN (135.89, 104.14) → (135.89, 102.87)                  — up to VIN rail
#   Junctions: (105.41, 102.87), (116.84, 102.87), (135.89, 102.87)
#
# GND + MODE/SYNC (forced PWM via corner routing):
#   GND symbol (128.27, 96.52) angle=270 → (130.81, 96.52)     — horizontal right
#   (130.81, 96.52) → (135.89, 96.52) U6.GND                   — horizontal to GND pin
#   (130.81, 96.52) → (130.81, 99.06)                           — vertical down to MODE level
#   U6.MODE (135.89, 99.06) → (130.81, 99.06)                  — horizontal left
#   Junction at (130.81, 96.52)
#
# EP ground:
#   GND (173.99, 93.98) angle=90 → (163.83, 93.98) U6.EP       — horizontal left
#
# Input cap GND:
#   C33.pin1 (116.84, 114.30) → (116.84, 116.84)               — down
#   C31.pin1 (105.41, 116.84) → (116.84, 116.84)               — horizontal right
#   (116.84, 116.84) → GND (116.84, 123.19)                     — down to GND symbol
#   Junction at (116.84, 116.84)
#
# Output rail:
#   U6.VOUT (163.83, 106.68) → (167.64, 106.68)                — horizontal right
#   +5V connection (170.18, 106.68) → (167.64, 106.68)
#   +5V (170.18, 100.33) → (170.18, 106.68)                    — vertical down
#   (167.64, 109.22) → (167.64, 106.68)                         — C32 area to VOUT
#   R3.pin1 (168.91, 109.22) → (167.64, 109.22)                — to VOUT junction
#   C32.pin1 (167.64, 119.38) → (167.64, 109.22)               — up to VOUT
#   Junctions: (167.64, 106.68), (167.64, 109.22)
#
# Feedback divider:
#   U6.FB (163.83, 104.14) → (180.34, 104.14)                  — horizontal to FB
#   R3.pin2 (179.07, 109.22) → (180.34, 109.22)
#   (180.34, 109.22) → (180.34, 104.14)                         — vertical up to FB
#   R4 (186.69, 104.14) → (180.34, 104.14)                     — horizontal to FB
#   (186.69, 104.14) → (186.69, 119.38) R4.pin1                — down to R4
#   Junction at (180.34, 104.14)
#
# Output GND rail:
#   C32.pin2 (167.64, 129.54) → (175.26, 129.54)
#   (175.26, 129.54) → R4.pin2 (186.69, 129.54)
#   (175.26, 129.54) → GND (175.26, 132.08)
#   Junction at (175.26, 129.54)


# =============================================================================
# 10. VERIFICATION CHECKLIST
# =============================================================================
# [x] +12V → VIN rail at Y=102.87
# [x] C31 (10uF) between VIN rail and GND
# [x] C33 (10uF) between VIN rail and GND
# [x] U6.VIN (pin 3) connected to VIN rail
# [x] U6.EN (pin 4) tied to VIN rail (always-on)
# [x] U6.GND (pin 1) connected to GND (sideways, angle=270)
# [x] U6.MODE/SYNC (pin 2) connected to GND (forced PWM, via corner)
# [x] U6.EP (pin 11) connected to GND (sideways, angle=90)
# [x] U6.VOUT (pin 6) connected to VOUT rail (+5V)
# [x] U6.FB (pin 7) connected to R3/R4 divider junction
# [x] R3 left → VOUT junction, R3 right → FB junction
# [x] R4 top → FB junction, R4 bottom → GND rail
# [x] C32 (47uF) between VOUT and GND
# [x] PGOOD (pin 5) has no-connect flag
# [x] DNC pins (8, 9, 10) have no-connect flags
# [x] Feedback divider: Vout = 1.0 * (1 + 10k/2.49k) = 5.016V
# [x] All positions on 1.27mm grid
# [x] 4 no-connects, 30 wires, 9 junctions

# END OF TEMPLATE
