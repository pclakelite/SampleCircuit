# =============================================================================
# TEMPLATE: 6-Button ADC Resistor Ladder
# =============================================================================
# Prerequisites: Read templates/TemplateCreation.spec FIRST for universal rules.
# This file covers ONLY circuit-specific details for the button ladder template.
#
# Template Version: 1.0
# Date: March 2026
# Status: Draft
# Reference: AIreference/SCH_simple-blower-V1.0_1-P1_2025-12-20 (1).pdf


# =============================================================================
# 1. OVERVIEW
# =============================================================================
# 6 tactile push-buttons read via a single ADC pin using a resistor voltage
# divider ladder. Each button press produces a unique voltage on the ADC pin,
# allowing firmware to identify which button was pressed.
#
# This is a common technique to save GPIO pins -- 6 buttons use only 1 ADC pin
# instead of 6 digital GPIO pins.
#
# The resistor values from the reference create distinct voltage levels at the
# KEY-ADC output for each button press (with 3.3V supply).


# =============================================================================
# 2. INTERFACE (what the parent schematic connects to)
# =============================================================================
# Type          | Name      | Shape           | Notes
# --------------|-----------|-----------------|-------------------------------
# Port symbol   | KEY_ADC   | Ports:KEY_ADC   | ADC input to ESP32 (single analog pin)
# Power symbol  | +3.3V     | power:+3.3V     | Global -- pull-up supply
# Power symbol  | GND       | power:GND       | Global -- auto-connects across sheets
#
# NOTE: Port symbol KEY_ADC may need to be created in Ports.kicad_sym.


# =============================================================================
# 3. DESIGN NOTES (circuit-specific decisions from reference schematic)
# =============================================================================
# Circuit topology:
#   +3.3V -> R12 (100k) -> R22 (51k) -> R3 (30k) -> R2 (20k) -> R25 (10k) -> R26 (4.7k) -> GND
#   Each button (SW1-SW6) taps a different node on the resistor chain to GND.
#   C4 (100nF) on ADC output for debounce/noise filtering.
#   R1 (10k) between ADC output and the ladder tap point.
#
# Resistor ladder (top to bottom, from +3.3V):
#   R12 = 100k  (top, closest to +3.3V)
#   R22 = 51k
#   R3  = 30k
#   R2  = 20k
#   R25 = 10k
#   R26 = 4.7k  (bottom, closest to GND)
#
# Button connections (each button shorts its node to GND when pressed):
#   SW5: Between R12/R22 junction and GND
#   SW1: Between R22/R3 junction and GND
#   SW2: Between R3/R2 junction and GND
#   SW3: Between R2/R25 junction and GND
#   SW4: Between R25/R26 junction and GND
#   SW6: Between R26/GND junction and GND (shorts R26)
#
# ADC tap point: Top of ladder (R12/+3.3V junction area) through R1 (10k)
# to KEY_ADC output. C4 (100nF) from KEY_ADC to GND for filtering.
#
# Approximate ADC voltages when each button is pressed (3.3V supply):
#   No press: ~3.3V (pulled up through R12)
#   SW5: ~2.45V
#   SW1: ~1.73V
#   SW2: ~1.14V
#   SW3: ~0.68V
#   SW4: ~0.30V
#   SW6: ~0.00V
#
# Firmware must use ADC thresholds with hysteresis to identify button presses.
# Recommended: sample at 10-50ms intervals, require 2+ consecutive matches.


# =============================================================================
# 4. INTERNAL NETS (stay inside this sheet -- NOT exposed)
# =============================================================================
# Net Name     | Path
# -------------|----------------------------------------------------
# LADDER_0     | +3.3V -> R12 top
# LADDER_1     | R12 bottom / R22 top / SW5 tap
# LADDER_2     | R22 bottom / R3 top / SW1 tap
# LADDER_3     | R3 bottom / R2 top / SW2 tap
# LADDER_4     | R2 bottom / R25 top / SW3 tap
# LADDER_5     | R25 bottom / R26 top / SW4 tap
# LADDER_6     | R26 bottom / SW6 tap -> GND
# ADC_TAP      | R1 -> C4 -> KEY_ADC port


# =============================================================================
# 5. COMPONENTS -- ALL FROM JLCPCB
# =============================================================================

# [R12] 100k -- Ladder resistor (top)
#   LCSC:      C17407
#   Symbol:    JLCImport:0805W8F1003T5E
#   Package:   0805
#   JLCPCB:    Basic part

# [R22] 51k -- Ladder resistor
#   LCSC:      C17737
#   Symbol:    JLCImport:0805W8F5102T5E
#   Package:   0805
#   JLCPCB:    Basic part

# [R3] 30k -- Ladder resistor
#   LCSC:      C17621
#   Symbol:    JLCImport:0805W8F3002T5E
#   Package:   0805
#   JLCPCB:    Basic part

# [R2] 20k -- Ladder resistor
#   LCSC:      C4328
#   Symbol:    JLCImport:0805W8F2002T5E
#   Package:   0805
#   JLCPCB:    Basic part

# [R25] 10k -- Ladder resistor
#   LCSC:      C17414
#   Symbol:    JLCImport:0805W8F1002T5E
#   Package:   0805
#   JLCPCB:    Basic part

# [R26] 4.7k -- Ladder resistor (bottom)
#   LCSC:      C17673
#   Symbol:    JLCImport:0805W8F4701T5E
#   Package:   0805
#   JLCPCB:    Basic part

# [R1] 10k -- ADC series resistor (isolation/current limiting)
#   LCSC:      C17414
#   Symbol:    JLCImport:0805W8F1002T5E
#   Package:   0805
#   JLCPCB:    Basic part

# [C4] 100nF -- ADC filter capacitor (debounce)
#   LCSC:      C49678
#   Symbol:    JLCImport:CC0805KRX7R9BB104
#   Package:   0805
#   JLCPCB:    Basic part

# [SW1-SW6] Tactile Push Buttons (6x)
#   LCSC:      C318884 (or search for 4-pin SMD tactile switch)
#   Package:   SMD 4-pin (typically 6x6mm or 3x6mm)
#   JLCPCB:    Basic/Extended part
#   Nets:      Pin 1+2 (common) -> ladder tap, Pin 3+4 (common) -> GND
#   Note:      4-pin switches have pins 1-2 shorted and 3-4 shorted internally.


# =============================================================================
# 6. JLCPCB BOM SUMMARY
# =============================================================================
#
# Ref    | Part              | Value    | Pkg    | LCSC    | Type
# -------|-------------------|----------|--------|---------|----------
# R12    | 0805W8F1003T5E    | 100k 1%  | 0805   | C17407  | Basic
# R22    | 0805W8F5102T5E    | 51k 1%   | 0805   | C17737  | Basic
# R3     | 0805W8F3002T5E    | 30k 1%   | 0805   | C17621  | Basic
# R2     | 0805W8F2002T5E    | 20k 1%   | 0805   | C4328   | Basic
# R25    | 0805W8F1002T5E    | 10k 1%   | 0805   | C17414  | Basic
# R26    | 0805W8F4701T5E    | 4.7k 1%  | 0805   | C17673  | Basic
# R1     | 0805W8F1002T5E    | 10k 1%   | 0805   | C17414  | Basic
# C4     | CC0805KRX7R9BB104 | 100nF    | 0805   | C49678  | Basic
# SW1-6  | Tactile switch    | --       | SMD    | C318884 | Extended
#
# Total: 14 components (8 basic, 6 extended for switches)


# =============================================================================
# 7. VERIFICATION CHECKLIST
# =============================================================================
# [ ] +3.3V -> R12 -> R22 -> R3 -> R2 -> R25 -> R26 -> GND (ladder chain)
# [ ] SW5 shorts R12/R22 junction to GND
# [ ] SW1 shorts R22/R3 junction to GND
# [ ] SW2 shorts R3/R2 junction to GND
# [ ] SW3 shorts R2/R25 junction to GND
# [ ] SW4 shorts R25/R26 junction to GND
# [ ] SW6 shorts R26/GND junction to GND
# [ ] R1 (10k) from ladder top to ADC tap
# [ ] C4 (100nF) from ADC tap to GND
# [ ] KEY_ADC port connected to ADC tap
# [ ] All positions on 1.27mm grid


# END OF TEMPLATE
