# =============================================================================
# TEMPLATE: LMZM23601SILR 24V to 12V Buck Regulator
# =============================================================================
# Prerequisites: Read templates/TemplateCreation.spec FIRST for universal rules.
# This file covers ONLY circuit-specific details for the 12V PSU template.
#
# Template Version: 1.0
# Date: March 2026
# Status: Draft

# =============================================================================
# 1. OVERVIEW
# =============================================================================
# TI LMZM23601 power module — 36V-input, 1A step-down DC-DC converter.
# Converts +24V input to +12V output for downstream circuits.
# Vref = 1.0V, feedback divider sets output:
#   Vout = Vref * (1 + R1/R2) = 1.0 * (1 + 110k/10k) = 12.0V
# Integrated inductor — minimal external components.
# Cloned from psu_lmzm23601_5v template with adjusted feedback resistors.


# =============================================================================
# 2. INTERFACE (what the parent schematic connects to)
# =============================================================================
# Type          | Name    | Shape         | Notes
# --------------|---------|---------------|-------------------------------
# Power symbol  | +24V    | power:+24V    | Global — input supply
# Power symbol  | +12V    | power:+12V    | Global — regulated output
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
# - Feedback divider: R1 (110k top) / R2 (10k bottom) → 12.0V out
# - Two 10uF 35V input caps (C1, C2) in parallel for decoupling
# - One 47uF 16V output cap (C3) for output filtering
# - NOTE: JLCImport pin numbering for LMZM23601SILR differs from datasheet.
#   Use pin NAMES (VIN, VOUT, FB, etc.) not numbers for wiring reference.


# =============================================================================
# 4. INTERNAL NETS (stay inside this sheet — NOT exposed)
# =============================================================================
# Net Name    | Path
# ------------|----------------------------------------------------
# VIN_RAIL    | +24V → C1.pin2 → C2.pin2 → U1.VIN, U1.EN
# FB_DIV      | U1.FB → R1.pin2 / R2 junction
#             | R1.pin1 → VOUT rail (+12V)
#             | R2.pin2 → GND
# VOUT_RAIL   | U1.VOUT → R1.pin1 area → C3.pin1 → +12V


# =============================================================================
# 5. COMPONENTS — ALL FROM JLCPCB
# =============================================================================

# [U1] LMZM23601SILR — 36V 1A Step-Down Power Module
#   LCSC:      C2685821
#   Symbol:    JLCImport:LMZM23601SILR
#   Package:   USIP-10 (3.8x3.0mm)
#   Vin Range: 4V to 36V
#   Vref:      1.0V
#   Iout:      1A max

# [R1] 110k Resistor — Feedback upper resistor
#   LCSC:      C17436
#   Symbol:    JLCImport:0805W8F1104T5E
#   Package:   0805

# [R2] 10k Resistor — Feedback lower resistor
#   LCSC:      C17414
#   Symbol:    JLCImport:0805W8F1002T5E
#   Package:   0805

# [C1] 10uF 35V Capacitor — Input decoupling #1
#   LCSC:      C97973
#   Symbol:    JLCImport:GRM32ER7YA106KA12L
#   Package:   1210

# [C2] 10uF 35V Capacitor — Input decoupling #2
#   LCSC:      C97973
#   Symbol:    JLCImport:GRM32ER7YA106KA12L
#   Package:   1210

# [C3] 47uF 16V Capacitor — Output decoupling
#   LCSC:      C172351
#   Symbol:    JLCImport:1206X476M160NT
#   Package:   1206


# =============================================================================
# 6. JLCPCB BOM SUMMARY
# =============================================================================
#
# Ref  | Part             | Value         | Pkg    | LCSC     | Type
# -----|------------------|---------------|--------|----------|----------
# U1   | LMZM23601SILR    | —             | USIP10 | C2685821 | Extended
# C1   | GRM32ER7YA106KA12L| 10uF 35V X7R | 1210   | C97973   | Extended
# C2   | GRM32ER7YA106KA12L| 10uF 35V X7R | 1210   | C97973   | Extended
# R1   | 0805W8F1104T5E   | 110k 1%       | 0805   | C17436   | Basic
# R2   | 0805W8F1002T5E   | 10k 1%        | 0805   | C17414   | Basic
# C3   | 1206X476M160NT   | 47uF 16V      | 1206   | C172351  | Extended
#
# Total: 6 components (2 basic, 4 extended)


# =============================================================================
# 7. VERIFICATION CHECKLIST
# =============================================================================
# [ ] +24V → VIN rail
# [ ] C1 (10uF) between VIN rail and GND
# [ ] C2 (10uF) between VIN rail and GND
# [ ] U1.VIN connected to VIN rail
# [ ] U1.EN tied to VIN rail (always-on)
# [ ] U1.GND connected to GND
# [ ] U1.MODE/SYNC connected to GND (forced PWM)
# [ ] U1.EP connected to GND
# [ ] U1.VOUT connected to VOUT rail (+12V)
# [ ] U1.FB connected to R1/R2 divider junction
# [ ] R1 left → VOUT junction, R1 right → FB junction
# [ ] R2 top → FB junction, R2 bottom → GND rail
# [ ] C3 (47uF) between VOUT and GND
# [ ] PGOOD has no-connect flag
# [ ] DNC pins (8, 9, 10) have no-connect flags
# [ ] Feedback divider: Vout = 1.0 * (1 + 110k/10k) = 12.0V

# END OF TEMPLATE
