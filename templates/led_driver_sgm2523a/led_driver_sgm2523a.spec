# =============================================================================
# TEMPLATE: SGM2523A Current-Limited LED Driver
# =============================================================================
# Prerequisites: Read templates/TemplateCreation.spec FIRST for universal rules.
# This file covers ONLY circuit-specific details for the LED driver template.
#
# Template Version: 1.0
# Date: March 2026
# Status: Draft
# Reference: AIreference/SCH_simple-blower-V1.0_1-P1_2025-12-20 (1).pdf


# =============================================================================
# 1. OVERVIEW
# =============================================================================
# SGMICRO SGM2523A integrated current-limited power switch. Used to drive
# an external LED string from 12V with programmable current limit.
# SOT-23-6 package. Current limit set by external resistor on ILIM pin:
#   Imax = 0.0105 * R_ILIM (in kohms)
# Reference uses R=100k -> Imax=1.05A and R=51k -> Imax=0.53A.
#
# This template provides a single LED driver instance. Instantiate multiple
# times on the parent sheet for multiple LED channels (e.g., normal LED,
# operation LED).


# =============================================================================
# 2. INTERFACE (what the parent schematic connects to)
# =============================================================================
# Type          | Name    | Shape         | Notes
# --------------|---------|---------------|-------------------------------
# Port symbol   | LED+    | Ports:LED+    | LED anode output (current-limited)
# Power symbol  | +12V    | power:+12V    | Global -- input supply
# Power symbol  | GND     | power:GND     | Global -- auto-connects across sheets
#
# The LED itself and its series resistor (if any) are on the PARENT sheet.
# This template only provides the current-limited switch.
#
# NOTE: Port symbol LED+ may need to be created in Ports.kicad_sym if it
# doesn't already exist.


# =============================================================================
# 3. DESIGN NOTES (circuit-specific decisions from reference schematic)
# =============================================================================
# SGM2523A pin assignments (SOT-23-6):
#   Pin 1 IN        -> +12V input
#   Pin 2 GND       -> GND
#   Pin 3 EN/nFAULT -> Directly tied to IN for always-on (or use GPIO for control)
#   Pin 4 SS        -> Soft-start capacitor (C = 100nF for ~5ms ramp)
#   Pin 5 ILIM      -> Current limit set resistor to GND
#   Pin 6 OUT       -> LED+ output (current-limited)
#
# Current limit formula: Imax = 0.0105 * R (kohms)
#   R7  = 100k -> Imax = 1.05A (reference "NORMAL-LED" channel, U4)
#   R34 = 100k -> Imax = 1.05A (reference "OPERATION-LED" channel, U14)
#   NOTE: Reference annotation near U14 says "Imax=0.0105*51k=0.53A" but
#   the schematic shows R34=100k. This is likely a stale annotation from
#   an earlier revision. Use R=100k (1.05A) unless lower current is needed.
#   For 0.53A limit, change R_ILIM to 51k (LCSC: C17734, 0805W8F5102T5E).
#
# Default in this template: R_ILIM = 100k (1.05A limit).
# Change R_ILIM value to adjust current for specific LED load.
#
# Soft-start: C_SS = 100nF gives ~5ms soft-start ramp.
# EN/nFAULT: Tied to IN for always-on. This pin is bidirectional --
#   it's an enable input and open-drain fault output.
#   To add GPIO shutdown control, connect ESP32 GPIO here instead.
#
# Decoupling: C = 100nF on input (close to IN pin) and 100nF on output.
# The reference shows C1/C2 (input) and C3/C52 (output) = 100nF each.


# =============================================================================
# 4. INTERNAL NETS (stay inside this sheet -- NOT exposed)
# =============================================================================
# Net Name     | Path
# -------------|----------------------------------------------------
# VIN_LOCAL    | +12V -> C_IN (100nF) -> U.IN (pin 1) -> U.EN (pin 3)
# ILIM_NET     | U.ILIM (pin 5) -> R_ILIM (100k) -> GND
# SS_NET       | U.SS (pin 4) -> C_SS (100nF) -> GND
# OUT_NET      | U.OUT (pin 6) -> C_OUT (100nF) -> LED+ port


# =============================================================================
# 5. COMPONENTS -- ALL FROM JLCPCB
# =============================================================================

# [U1] SGM2523A -- Current-Limited Power Switch
#   LCSC:      C5153397
#   Symbol:    JLCImport:SGM2523BXN6G_TR
#   Note:      SGM2523B is functionally identical to SGM2523A (same pinout/formula)
#   Package:   SOT-23-6
#   JLCPCB:    Extended part
#   VIN:       2.5V to 23V
#   Iout:      Up to 2A (set by ILIM)
#   Ron:       ~80 mohm typical

# [R1] 100k -- Current limit resistor (Imax = 1.05A)
#   LCSC:      C17407
#   Symbol:    JLCImport:0805W8F1003T5E
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> ILIM pin, Pin2 -> GND

# [C1] 100nF -- Input decoupling capacitor
#   LCSC:      C49678
#   Symbol:    JLCImport:CC0805KRX7R9BB104
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> VIN rail (+12V), Pin2 -> GND

# [C2] 100nF -- Output decoupling capacitor
#   LCSC:      C49678
#   Symbol:    JLCImport:CC0805KRX7R9BB104
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> OUT net (LED+), Pin2 -> GND

# [C3] 100nF -- Soft-start capacitor
#   LCSC:      C49678
#   Symbol:    JLCImport:CC0805KRX7R9BB104
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> SS pin, Pin2 -> GND


# =============================================================================
# 6. JLCPCB BOM SUMMARY
# =============================================================================
#
# Ref  | Part              | Value     | Pkg      | LCSC     | Type
# -----|-------------------|-----------|----------|----------|----------
# U1   | SGM2523BXN6G/TR   | --        | SOT-23-6 | C5153397 | Extended
# R1   | 0805W8F1003T5E    | 100k 1%   | 0805     | C17407   | Basic
# C1   | CC0805KRX7R9BB104 | 100nF 50V | 0805     | C49678   | Basic
# C2   | CC0805KRX7R9BB104 | 100nF 50V | 0805     | C49678   | Basic
# C3   | CC0805KRX7R9BB104 | 100nF 50V | 0805     | C49678   | Basic
#
# Total: 5 components (4 basic, 1 extended)


# =============================================================================
# 7. VERIFICATION CHECKLIST
# =============================================================================
# [ ] +12V -> C1 (100nF) -> U1.IN (pin 1)
# [ ] U1.EN/nFAULT (pin 3) tied to IN (always-on)
# [ ] U1.GND (pin 2) -> GND
# [ ] U1.ILIM (pin 5) -> R1 (100k) -> GND
# [ ] U1.SS (pin 4) -> C3 (100nF) -> GND
# [ ] U1.OUT (pin 6) -> C2 (100nF) -> LED+ port
# [ ] All positions on 1.27mm grid


# END OF TEMPLATE
