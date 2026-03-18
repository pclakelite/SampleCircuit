# =============================================================================
# TEMPLATE: RT9013-33GB 5V to 3.3V LDO Regulator
# =============================================================================
# Prerequisites: Read templates/TemplateCreation.spec FIRST for universal rules.
# This file covers ONLY circuit-specific details for the RT9013 LDO template.
#
# Template Version: 1.0
# Date: March 2026
# Status: Draft
# Reference: AIreference/SCH_simple-blower-V1.0_1-P1_2025-12-20 (1).pdf


# =============================================================================
# 1. OVERVIEW
# =============================================================================
# Richtek RT9013-33GB 500mA LDO regulator. Converts +5V to +3.3V with low
# dropout (typically 250mV at full load). Fixed 3.3V output version.
# SOT-23-5 package. Includes Zener clamp (D5 1SMA4729A) on output for
# overvoltage protection.
#
# Alternative to: psu_lmzm23601_3v3 (which is a buck converter from 12V)
# Trade-off: LDO is simpler and cheaper but less efficient (66% from 5V).
# Requires 5V rail to already exist. Buck is direct 12V->3.3V, more efficient.


# =============================================================================
# 2. INTERFACE (what the parent schematic connects to)
# =============================================================================
# Type          | Name    | Shape         | Notes
# --------------|---------|---------------|-------------------------------
# Power symbol  | +5V     | power:+5V     | Global -- input supply (from 5V buck)
# Power symbol  | +3.3V   | power:+3.3V   | Global -- regulated output
# Power symbol  | GND     | power:GND     | Global -- auto-connects across sheets
#
# No signal ports -- this is a pure power supply module.


# =============================================================================
# 3. DESIGN NOTES (circuit-specific decisions from reference schematic)
# =============================================================================
# - VIN (pin 1): +5V input
# - GND (pin 2): Power ground
# - EN (pin 3): Enable -- tied to VIN for always-on operation
# - NC (pin 4): No-connect (no internal connection)
# - VOUT (pin 5): 3.3V regulated output
#
# - D5 (1SMA4729A): 3.6V Zener diode on output for overvoltage clamp.
#   Prevents output from exceeding 3.6V if regulator fails shorted.
#   Cathode to VOUT, anode to GND.
#
# - Input decoupling: C42 = 10uF, C43 = 100nF (close to VIN pin)
# - Output decoupling: C41 = 10uF, C40 = 100nF (close to VOUT pin)
# - Datasheet recommends >= 1uF on both input and output for stability.


# =============================================================================
# 4. INTERNAL NETS (stay inside this sheet -- NOT exposed)
# =============================================================================
# Net Name     | Path
# -------------|----------------------------------------------------
# VIN_LOCAL    | +5V -> C42/C43 -> U15.VIN (pin 1), U15.EN (pin 3)
# VOUT_LOCAL   | U15.VOUT (pin 5) -> D5 (cathode) -> C41/C40 -> +3.3V


# =============================================================================
# 5. COMPONENTS -- ALL FROM JLCPCB
# =============================================================================

# [U15] RT9013-33GB -- 500mA LDO Regulator (fixed 3.3V)
#   LCSC:      C47773
#   Symbol:    JLCImport:RT9013-33GB
#   Package:   SOT-23-5 (TSOT-25)
#   JLCPCB:    Extended part
#   Vin Range: 2.2V to 5.5V
#   Vout:      3.3V fixed
#   Iout:      500mA max
#   Dropout:   250mV typical at 500mA
#   Pin assignments:
#     Pin 1 VIN  -> +5V input rail
#     Pin 2 GND  -> GND
#     Pin 3 EN   -> Tied to VIN (always-on)
#     Pin 4 NC   -> No-connect
#     Pin 5 VOUT -> 3.3V output rail

# [D5] 1SMA4729A -- 3.6V Zener Diode (output overvoltage clamp)
#   LCSC:      C145089
#   Package:   SMA (DO-214AC)
#   JLCPCB:    Extended part
#   Nets:      Cathode -> VOUT rail (+3.3V), Anode -> GND

# [C42] 10uF -- Input bulk capacitor
#   LCSC:      C15850
#   Symbol:    JLCImport:CL21A106KAYNNNE
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> VIN rail (+5V), Pin2 -> GND

# [C43] 100nF -- Input decoupling capacitor
#   LCSC:      C49678
#   Symbol:    JLCImport:CC0805KRX7R9BB104
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> VIN rail (+5V), Pin2 -> GND

# [C41] 10uF -- Output bulk capacitor
#   LCSC:      C15850
#   Symbol:    JLCImport:CL21A106KAYNNNE
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> VOUT rail (+3.3V), Pin2 -> GND

# [C40] 100nF -- Output decoupling capacitor
#   LCSC:      C49678
#   Symbol:    JLCImport:CC0805KRX7R9BB104
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> VOUT rail (+3.3V), Pin2 -> GND


# =============================================================================
# 6. JLCPCB BOM SUMMARY
# =============================================================================
#
# Ref  | Part              | Value       | Pkg      | LCSC     | Type
# -----|-------------------|-------------|----------|----------|----------
# U15  | RT9013-33GB       | 3.3V LDO    | SOT-23-5 | C47773   | Extended
# D5   | 1SMA4729A         | 3.6V Zener  | SMA      | C145089  | Extended
# C42  | CL21A106KAYNNNE   | 10uF 25V    | 0805     | C15850   | Basic
# C43  | CC0805KRX7R9BB104 | 100nF 50V   | 0805     | C49678   | Basic
# C41  | CL21A106KAYNNNE   | 10uF 25V    | 0805     | C15850   | Basic
# C40  | CC0805KRX7R9BB104 | 100nF 50V   | 0805     | C49678   | Basic
#
# Total: 6 components (4 basic, 2 extended)


# =============================================================================
# 7. VERIFICATION CHECKLIST
# =============================================================================
# [ ] +5V -> C42/C43 -> U15.VIN (pin 1)
# [ ] U15.EN (pin 3) tied to VIN (always-on)
# [ ] U15.GND (pin 2) connected to GND
# [ ] NC flag on pin 4
# [ ] U15.VOUT (pin 5) -> D5 cathode -> C41/C40 -> +3.3V
# [ ] D5 anode to GND
# [ ] All positions on 1.27mm grid


# END OF TEMPLATE
