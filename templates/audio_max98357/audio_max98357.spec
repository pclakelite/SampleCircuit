# =============================================================================
# TEMPLATE: MAX98357A I2S Audio Amplifier
# =============================================================================
# Prerequisites: Read templates/TemplateCreation.spec FIRST for universal rules.
#                Read specs/CircuitCreation.spec for bus requirements.
# This file covers ONLY circuit-specific details for the audio amp template.
#
# Template Version: 3.0
# Date: March 2026
# Status: Human-reviewed and corrected in KiCad


# =============================================================================
# 1. OVERVIEW
# =============================================================================
# MAX98357A I2S DAC + Class D amplifier. Receives digital audio via I2S bus,
# outputs up to 3.2W into a speaker. Single +5V supply, no external MCLK
# needed. TQFN-16 package.


# =============================================================================
# 2. INTERFACE (what the parent schematic connects to)
# =============================================================================
# Type          | Name   | Shape          | Notes
# --------------|--------|----------------|-------------------------------
# Port symbol   | DIN    | Ports:DIN      | I2S serial data (top-left, angle=0)
# Port symbol   | BCLK   | Ports:BCLK     | I2S bit clock (right side, angle=180)
# Port symbol   | LRCLK  | Ports:LRCLK    | I2S word select (right side, angle=180)
# Port symbol   | OUTP   | Ports:OUTP     | Speaker positive (right side, angle=180)
# Port symbol   | OUTN   | Ports:OUTN     | Speaker negative (right side, angle=180)
# Power symbol  | +5V    | power:+5V      | Global — auto-connects across sheets
# Power symbol  | GND    | power:GND      | Global — auto-connects across sheets
#
# I2S and speaker signals use custom port symbols from Ports.kicad_sym.
# Speaker connector goes on PARENT sheet (see CircuitCreation.spec section 4).
#
# PORT PLACEMENT PATTERN:
#   - DIN is on the LEFT (angle=0) because its IC pin is on the left side.
#     It enters from the top and routes vertically down to pin 1.
#   - BCLK, LRCLK are on the RIGHT (angle=180) because their IC pins are
#     on the right side. This eliminates the need for routing across the IC.
#   - OUTP, OUTN are on the RIGHT (angle=180) — same reasoning.
#   - Lesson: Place ports on the SAME SIDE as their IC pins to minimize
#     wire crossings. Use angle=180 for right-side ports.


# =============================================================================
# 3. DESIGN NOTES (circuit-specific decisions — human-reviewed)
# =============================================================================
# - SD_MODE (pin 4): Pulled high via R6 (1.0M to +5V) = L/2+R/2 mixed output.
#   1M to VDD selects mixed mono (both channels summed). To add shutdown
#   control, connect an ESP32 GPIO here instead of the pull-up (on parent sheet).
#
# - GAIN_SLOT (pin 2): Pulled to GND via R7 (100k to GND) = 6dB gain.
#   Gain options per datasheet:
#     GND        = 9dB
#     VDD        = 12dB
#     Float      = 15dB
#     100k→GND   = 6dB  ← selected
#     100k→VDD   = 3dB
#
# - VDD (pins 7, 8): Both connected to +5V via decoupling network
# - GND (pins 3, 11, 15): All tied to GND
# - EP / PAD (pin 17): Exposed pad, connected to GND
# - NC pins (5, 6, 12, 13): No-connect flags
# - C15 (10uF) + C16 (100nF): Bulk + decoupling on VDD per datasheet.
# - OUTP/OUTN: BTL outputs. No coupling capacitors needed.
# - No I2S bus pull-ups — I2S is push-pull.


# =============================================================================
# 4. INTERNAL NETS (stay inside this sheet — NOT exposed)
# =============================================================================
# Net Name       | Path
# ---------------|----------------------------------------------------
# SD_MODE_INT    | R6.P2 → U4.SD_MODE (pin 4)
# GAIN_GND       | R7.P2 → U4.GAIN_SLOT (pin 2), R7.P1 → GND
# VDD_INT        | +5V → C16.P1 → C15.P1 → U4.VDD (pins 7, 8)
# DIN_ROUTE      | DIN port → horizontal → vertical down → U4.DIN (pin 1)
# GND_SHARED     | R7.P1 → junction → U4.GND (pin 3) → GND symbol


# =============================================================================
# 5. COMPONENTS
# =============================================================================
#
# [U4] MAX98357AETE+T — I2S DAC + Class D Amplifier
#   Symbol:    JLCImport:MAX98357AETE_T
#   Position:  (153.67, 101.60) angle=0
#   Package:   TQFN-16 (3x3mm, 0.5mm pitch)
#   LCSC:      C910544
#   JLCPCB:    Extended part
#
# [C15] 10uF — VDD bulk capacitor
#   Symbol:    JLCImport:CL21A106KAYNNNE
#   Position:  (125.73, 113.03) angle=270
#   Package:   0805
#   LCSC:      C15850
#   Nets:      Pin1 → VDD bus, Pin2 → GND
#
# [C16] 100nF — VDD decoupling capacitor
#   Symbol:    JLCImport:CC0805KRX7R9BB104
#   Position:  (119.38, 113.03) angle=270
#   Package:   0805
#   LCSC:      C49678
#   Nets:      Pin1 → VDD bus, Pin2 → GND
#
# [R7] 100k — GAIN_SLOT pull-down to GND (6dB gain)
#   Symbol:    JLCImport:0805W8F1003T5E
#   Position:  (119.38, 87.63) angle=0 (horizontal)
#   Package:   0805
#   LCSC:      C17407
#   Nets:      Pin1 → GND (junction at 114.3, 92.71), Pin2 → GAIN_SLOT
#
# [R6] 1.0M — SD_MODE pull-up to +5V (L/2+R/2 mixed mono)
#   Symbol:    JLCImport:0805W8F1004T5E
#   Position:  (119.38, 100.33) angle=0 (horizontal)
#   Package:   0805
#   LCSC:      C17514
#   Nets:      Pin1 → +5V, Pin2 → SD_MODE


# =============================================================================
# 6. JLCPCB BOM SUMMARY
# =============================================================================
# Ref  | Value        | Pkg  | LCSC     | Type     | Qty
# -----|--------------|------|----------|----------|----
# U4   | MAX98357AETE | TQFN | C910544  | Extended | 1
# C15  | 10uF 25V     | 0805 | C15850   | Basic    | 1
# C16  | 100nF 50V    | 0805 | C49678   | Basic    | 1
# R7   | 100k 1%      | 0805 | C17407   | Basic    | 1
# R6   | 1M 1%        | 0805 | C17514   | Basic    | 1


# =============================================================================
# 7. PIN ENDPOINT REFERENCE (VERIFIED)
# =============================================================================
# CRITICAL: The (at x y) in a KiCad lib_symbol pin IS the wire connection point.
# Do NOT subtract pin length.
#
# U4 at (153.67, 101.60) angle=0:
#   Schematic endpoint = (153.67 + pin_at_x, 101.60 - pin_at_y)
#
# Pin  | Name       | Side   | Pin (at x, y)      | Schematic endpoint
# -----|------------|--------|--------------------|---------------------
# 1    | DIN        | Left   | (-16.51, 8.89)     | (137.16, 92.71)
# 2    | GAIN_SLOT  | Left   | (-16.51, 6.35)     | (137.16, 95.25)
# 3    | GND        | Left   | (-16.51, 3.81)     | (137.16, 97.79)
# 4    | SD_MODE    | Left   | (-16.51, 1.27)     | (137.16, 100.33)
# 5    | NC         | Left   | (-16.51, -1.27)    | (137.16, 102.87)
# 6    | NC         | Left   | (-16.51, -3.81)    | (137.16, 105.41)
# 7    | VDD        | Left   | (-16.51, -6.35)    | (137.16, 107.95)
# 8    | VDD        | Left   | (-16.51, -8.89)    | (137.16, 110.49)
# 9    | OUTP       | Right  | (16.51, -8.89)     | (170.18, 110.49)
# 10   | OUTN       | Right  | (16.51, -6.35)     | (170.18, 107.95)
# 11   | GND        | Right  | (16.51, -3.81)     | (170.18, 105.41)
# 12   | NC         | Right  | (16.51, -1.27)     | (170.18, 100.33)
# 13   | NC         | Right  | (16.51, 1.27)      | (170.18, 102.87)
# 14   | LRCLK      | Right  | (16.51, 3.81)      | (170.18, 97.79)
# 15   | GND        | Right  | (16.51, 6.35)      | (170.18, 95.25)
# 16   | BCLK       | Right  | (16.51, 8.89)      | (170.18, 92.71)
# 17   | EP/PAD     | Bottom | (0, -13.97)        | (153.67, 115.57)


# =============================================================================
# 8. SYMBOL PLACEMENT SUMMARY
# =============================================================================
# Ref      | lib_id                       | Position          | Angle
# ---------|------------------------------|-------------------|------
# U4       | JLCImport:MAX98357AETE_T     | (153.67, 101.60)  | 0
# R7       | JLCImport:0805W8F1003T5E     | (119.38, 87.63)   | 0
# R6       | JLCImport:0805W8F1004T5E     | (119.38, 100.33)  | 0
# C15      | JLCImport:CL21A106KAYNNNE    | (125.73, 113.03)  | 270
# C16      | JLCImport:CC0805KRX7R9BB104  | (119.38, 113.03)  | 270
# #PWR01   | power:+5V                    | (106.68, 100.33)  | 90
# #PWR02   | power:+5V                    | (123.19, 106.68)  | 0
# #PWR03   | power:GND                    | (111.76, 92.71)   | 270
# #PWR04   | power:GND                    | (123.19, 120.65)  | 0
# #PWR05   | power:GND                    | (180.34, 105.41)  | 90
# #PWR06   | power:GND                    | (176.53, 95.25)   | 90
# #PWR07   | power:GND                    | (153.67, 119.38)  | 0
# #PORT01  | Ports:DIN                    | (121.92, 78.74)   | 0
# #PORT02  | Ports:BCLK                   | (187.96, 91.44)   | 180
# #PORT03  | Ports:LRCLK                  | (187.96, 97.79)   | 180
# #PORT04  | Ports:OUTP                   | (189.23, 111.76)  | 180
# #PORT05  | Ports:OUTN                   | (189.23, 107.95)  | 180


# =============================================================================
# 9. WIRING PLAN (as built)
# =============================================================================
# DIN routing (top-left entry, vertical drop):
#   DIN port pin (124.46, 78.74) → horizontal → (137.16, 78.74)
#   → vertical down → U4.DIN (137.16, 92.71)
#
# BCLK routing (right side, short jog):
#   U4.BCLK (170.18, 92.71) → horizontal → (181.61, 92.71)
#   → vertical up → (181.61, 91.44) → horizontal → BCLK port (185.42, 91.44)
#
# LRCLK routing (right side, straight):
#   U4.LRCLK (170.18, 97.79) → horizontal → LRCLK port (185.42, 97.79)
#
# OUTP routing (right side, vertical jog):
#   U4.OUTP (170.18, 110.49) → vertical → (170.18, 111.76)
#   → horizontal → OUTP port (186.69, 111.76)
#
# OUTN routing (right side, straight):
#   U4.OUTN (170.18, 107.95) → horizontal → OUTN port (186.69, 107.95)
#
# R7 GAIN_SLOT (100k to GND):
#   R7.P1 (114.3, 87.63) → vertical down → junction (114.3, 92.71) → GND
#   R7.P2 (124.46, 87.63) → vertical down → (124.46, 95.25)
#   → horizontal → U4.GAIN_SLOT (137.16, 95.25)
#
# R6 SD_MODE (1M to +5V):
#   +5V (106.68, 100.33) → horizontal → R6.P1 (114.3, 100.33)
#   R6.P2 (124.46, 100.33) → horizontal → U4.SD_MODE (137.16, 100.33)
#
# GND pin 3 (shares junction with R7):
#   Junction (114.3, 92.71) → (121.92, 92.71) → vertical down
#   → (121.92, 97.79) → horizontal → U4.GND pin 3 (137.16, 97.79)
#
# VDD power bus:
#   +5V (123.19, 106.68) → vertical → (123.19, 107.95) [cap bus]
#   C16.P1 (119.38, 107.95) → junction (123.19, 107.95)
#   → C15.P1 (125.73, 107.95) → horizontal → U4.VDD pin 7 (137.16, 107.95)
#   U4.VDD pin 7 → vertical → U4.VDD pin 8 (137.16, 110.49)
#
# Cap GND:
#   C16.P2 (119.38, 118.11) → junction (123.19, 118.11) → C15.P2 (125.73, 118.11)
#   Junction → vertical → GND (123.19, 120.65)
#
# Right-side GND:
#   U4.GND pin 11 (170.18, 105.41) → horizontal → GND (180.34, 105.41)
#   U4.GND pin 15 (170.18, 95.25) → horizontal → GND (176.53, 95.25)
#   U4.EP (153.67, 115.57) → vertical → GND (153.67, 119.38)


# =============================================================================
# 10. JUNCTIONS
# =============================================================================
# (114.3, 92.71)   — R7.P1 vertical meets GND pin 3 routing
# (123.19, 107.95)  — +5V vertical meets cap bus horizontal
# (125.73, 107.95)  — cap bus meets C15 top and continues to VDD pins
# (137.16, 107.95)  — VDD bus meets pin 7 vertical to pin 8
# (123.19, 118.11)  — cap GND bus meets vertical to GND symbol


# =============================================================================
# 11. NO-CONNECTS
# =============================================================================
# Pin 5:  (137.16, 102.87)
# Pin 6:  (137.16, 105.41)
# Pin 12: (170.18, 100.33)
# Pin 13: (170.18, 102.87)


# =============================================================================
# 12. VERIFICATION CHECKLIST
# =============================================================================
# [x] All 5 port symbols render clean hexagonal flags
# [x] +5V connects to R6.P1 and VDD bus (C15, C16, pins 7+8)
# [x] GND connects to R7.P1, U4.GND (pins 3, 11, 15), U4.EP (17), C15.P2, C16.P2
# [x] R7 (100k) connects GAIN_SLOT to GND (6dB gain)
# [x] R6 (1M) connects SD_MODE to +5V (L/2+R/2 mixed)
# [x] No-connect flags on pins 5, 6, 12, 13
# [x] All wire endpoints match pin endpoints (corrected formula)
# [x] All coordinates on 1.27mm grid
# [x] #PWR05 alignment fixed to (180.34, 105.41) — on grid
# [ ] Verify #PWR05 project name (was "audio_max98357", should be "AITestProject")


# =============================================================================
# 13. LESSONS LEARNED FROM HUMAN REVIEW
# =============================================================================
# A. Place port symbols on the SAME SIDE as their IC pins to minimize crossings.
#    Use angle=180 for ports on the right side of the schematic.
#
# B. Share GND junctions when routing allows — R7's GND and U4 pin 3 GND
#    share a junction, reducing GND symbol count and wire complexity.
#
# C. When a signal enters from a different side than its IC pin (like DIN
#    entering from the left-top to reach a left-side pin lower down), use
#    a horizontal-then-vertical L-shaped route.
#
# D. OUTP pin 9 is at y=110.49 but the port is at y=111.76 — a short
#    vertical jog is needed. This is acceptable for clean routing.
#
# E. The gain was changed from 100k→+5V (3dB) to 100k→GND (6dB) during
#    review. Always defer to the human-reviewed schematic as the source
#    of truth for design decisions.


# END OF SPEC
