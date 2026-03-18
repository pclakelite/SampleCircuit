# =============================================================================
# TEMPLATE: LMZM23601SILR 12V to 3.3V Buck Regulator with Input Protection
# =============================================================================
# Prerequisites: Read templates/TemplateCreation.spec FIRST for universal rules.
# This file covers ONLY circuit-specific details for the 3.3V PSU template.
#
# Template Version: 2.1
# Date: March 2026
# Status: Locked - human-reviewed, wiring verified in KiCad


# =============================================================================
# 1. OVERVIEW
# =============================================================================
# TI LMZM23601 power module, 36V-input, 1A step-down DC-DC converter.
# Converts +12V input to +3.3V output for downstream circuits.
# Includes PMEG6030EVPX Schottky input protection diode.
# Vref = 1.0V, feedback divider sets output:
#   Vout = Vref * (1 + R31/R32) = 1.0 * (1 + 10k/4.22k) = 3.37V


# =============================================================================
# 2. INTERFACE (what the parent schematic connects to)
# =============================================================================
# Type          | Name   | Shape       | Notes
# --------------|--------|-------------|-------------------------------
# Power symbol  | +12V   | power:+12V  | Global input supply
# Power symbol  | +3.3V  | power:+3.3V | Global regulated output
# Power symbol  | GND    | power:GND   | Global ground
#
# No signal ports. This is a pure power supply module.


# =============================================================================
# 3. DESIGN NOTES
# =============================================================================
# - D8 (PMEG6030EVPX): reverse polarity input protection
# - C11 (680uF): bulk electrolytic input capacitor
# - C34 (10uF 35V): ceramic input decoupling close to VIN
# - EN tied to VIN for always-on operation
# - MODE/SYNC tied to GND for forced PWM mode
# - PGOOD unused (no-connect)
# - DNC pins (8, 9, 10) left unconnected
# - EP (pin 11, exposed pad) connected to GND
# - Feedback divider: R31 (10k top) and R32 (4.22k bottom)
# - C35 (47uF 16V): output decoupling


# =============================================================================
# 4. INTERNAL NETS (not exposed)
# =============================================================================
# Net Name    | Path
# ------------|----------------------------------------------------------
# VIN_RAIL    | D8.K -> C11.pin1 -> C34.pin2 -> U5.VIN, U5.EN
# FB_DIV      | U5.FB -> R32.pin1 -> R31.pin2
# VOUT_RAIL   | U5.VOUT -> R31.pin1 -> C35.pin1 -> +3.3V
# GND_OUT     | R32.pin2 + C35.pin2 -> GND


# =============================================================================
# 5. COMPONENTS - ALL FROM JLCPCB
# =============================================================================
#
# [U5] LMZM23601SILR
#   LCSC: C2685821
#   Symbol: JLCImport:LMZM23601SILR
#   Package: USIP-10
#
# [D8] PMEG6030EVPX (input protection diode)
#   LCSC: C489223
#   Symbol: JLCImport:PMEG6030EVPX
#   Package: SOD-128 (SMAF)
#
# [C11] EEEFT1V681UP (680uF 35V electrolytic)
#   LCSC: C542257
#   Symbol: JLCImport:EEEFT1V681UP
#
# [C34] GRM32ER7YA106KA12L (10uF 35V)
#   LCSC: C97973
#   Symbol: JLCImport:GRM32ER7YA106KA12L
#
# [R31] 10k feedback top resistor
#   LCSC: C17414
#   Symbol: JLCImport:0805W8F1002T5E
#
# [R32] 4.22k feedback bottom resistor
#   LCSC: C17665
#   Symbol: JLCImport:0805W8F4221T5E
#
# [C35] GRM32EC81C476KE15L (47uF 16V)
#   LCSC: C162512
#   Symbol: JLCImport:GRM32EC81C476KE15L


# =============================================================================
# 6. JLCPCB BOM SUMMARY
# =============================================================================
# Ref  | Part               | Value      | LCSC     | Type
# -----|--------------------|------------|----------|----------
# U5   | LMZM23601SILR      | --         | C2685821 | Extended
# D8   | PMEG6030EVPX       | 60V 3A     | C489223  | Extended
# C11  | EEEFT1V681UP       | 680uF 35V  | C542257  | Extended
# C34  | GRM32ER7YA106KA12L | 10uF 35V   | C97973   | Extended
# R31  | 0805W8F1002T5E     | 10k 1%     | C17414   | Basic
# R32  | 0805W8F4221T5E     | 4.22k 1%   | C17665   | Basic
# C35  | GRM32EC81C476KE15L | 47uF 16V   | C162512  | Extended
#
# Total: 7 components (2 basic, 5 extended)


# =============================================================================
# 7. SCHEMATIC LAYOUT - POSITIONS (all on 1.27mm grid)
# =============================================================================
# Component    | Position (x, y)     | Angle | Notes
# -------------|---------------------|-------|----------------------------------
# U5 (IC)      | (149.86, 100.33)    | 0     | center
# D8 (diode)   | (99.06, 101.60)     | 180   | anode LEFT, cathode RIGHT
# C11 (680uF)  | (114.30, 106.68)    | 270   | pin1 top, pin2 bottom
# C34 (10uF)   | (125.73, 106.68)    | 0     | native vertical
# R31 (10k)    | (170.18, 118.11)    | 270   | VOUT to FB branch
# R32 (4.22k)  | (185.42, 124.46)    | 270   | FB branch to GND
# C35 (47uF)   | (198.12, 124.46)    | 270   | VOUT to GND
#
# Power symbols:
#   +12V       | (91.44, 93.98)      | 0
#   +3.3V      | (193.04, 100.33)    | 0
#   GND #PWR02 | (133.35, 88.90)     | 180
#   GND #PWR03 | (167.64, 93.98)     | 90
#   GND #PWR04 | (114.30, 116.84)    | 0
#   GND #PWR05 | (125.73, 116.84)    | 0
#   GND #PWR06 | (190.50, 132.08)    | 0
#
# No-connects:
#   U5 pin5 PGOOD at (135.89, 106.68)
#   U5 pin8 DNC   at (163.83, 101.60)
#   U5 pin9 DNC   at (163.83, 99.06)
#   U5 pin10 DNC  at (163.83, 96.52)


# =============================================================================
# 8. PIN ENDPOINTS
# =============================================================================
# U5 at (149.86, 100.33):
#   GND       (135.89, 96.52)
#   MODE/SYNC (135.89, 99.06)
#   VIN       (135.89, 101.60)
#   EN        (135.89, 104.14)
#   PGOOD     (135.89, 106.68)
#   VOUT      (163.83, 106.68)
#   FB        (163.83, 104.14)
#   DNC8      (163.83, 101.60)
#   DNC9      (163.83, 99.06)
#   DNC10     (163.83, 96.52)
#   EP        (163.83, 93.98)
#
# D8 at (99.06, 101.60), angle=180:
#   K (pin1)  (104.14, 101.60)
#   A (pin2)  (93.98, 101.60)
#
# C11 at (114.30, 106.68), angle=270:
#   pin1 (+)  (114.30, 101.60)
#   pin2 (-)  (114.30, 111.76)
#
# C34 at (125.73, 106.68), angle=0:
#   pin2      (125.73, 101.60)
#   pin1      (125.73, 111.76)
#
# R31 at (170.18, 118.11), angle=270:
#   pin1      (170.18, 113.03)
#   pin2      (170.18, 123.19)
#
# R32 at (185.42, 124.46), angle=270:
#   pin1      (185.42, 119.38)
#   pin2      (185.42, 129.54)
#
# C35 at (198.12, 124.46), angle=270:
#   pin1      (198.12, 119.38)
#   pin2      (198.12, 129.54)


# =============================================================================
# 9. WIRING CONNECTIONS (reviewed schematic)
# =============================================================================
# Input rail:
#   +12V (91.44,93.98) -> (91.44,101.60) -> D8.A (93.98,101.60)
#   D8.K (104.14,101.60) -> C11.pin1 (114.30,101.60) -> C34.pin2 (125.73,101.60)
#   -> U5.VIN (135.89,101.60)
#   U5.EN (135.89,104.14) -> U5.VIN rail
#
# GND and MODE:
#   GND #PWR02 (133.35,88.90) -> (133.35,96.52)
#   U5.GND (135.89,96.52) -> (133.35,96.52)
#   U5.MODE (135.89,99.06) -> (133.35,99.06)
#   (133.35,96.52) -> (133.35,99.06)
#
# EP:
#   U5.EP (163.83,93.98) -> GND #PWR03 (167.64,93.98)
#
# Input cap grounds:
#   C11.pin2 (114.30,111.76) -> GND #PWR04 (114.30,116.84)
#   C34.pin1 (125.73,111.76) -> GND #PWR05 (125.73,116.84)
#
# Output rail:
#   U5.VOUT (163.83,106.68) -> node (170.18,106.68) -> node (193.04,106.68)
#   +3.3V symbol (193.04,100.33) -> (193.04,106.68)
#   R31.pin1 (170.18,113.03) -> (170.18,106.68)
#   C35.pin1 (198.12,119.38) -> (198.12,106.68) -> (193.04,106.68)
#
# Feedback:
#   U5.FB (163.83,104.14) -> FB node (176.53,104.14)
#   R32.pin1 (185.42,119.38) -> (185.42,104.14) -> FB node
#   R31.pin2 (170.18,123.19) -> (176.53,123.19) -> FB node
#
# Output ground:
#   R32.pin2 (185.42,129.54) + C35.pin2 (198.12,129.54) -> node (190.50,129.54)
#   node (190.50,129.54) -> GND #PWR06 (190.50,132.08)
#
# Junctions:
#   (114.30,101.60), (125.73,101.60), (135.89,101.60), (133.35,96.52),
#   (170.18,106.68), (193.04,106.68), (176.53,104.14), (190.50,129.54)


# =============================================================================
# 10. VERIFICATION CHECKLIST
# =============================================================================
# [x] +12V -> D8 -> VIN rail -> U5.VIN/U5.EN
# [x] C11 and C34 from VIN rail to GND
# [x] U5.MODE/SYNC tied to GND
# [x] U5.EP tied to GND
# [x] U5.VOUT connected to +3.3V rail
# [x] R31/R32 divider connected to U5.FB
# [x] C35 from output rail to GND
# [x] PGOOD and DNC pins marked no-connect
# [x] Feedback math: Vout = 1.0 * (1 + 10k/4.22k) = 3.37V
# [x] Layout reviewed in KiCad and locked

# END OF TEMPLATE
