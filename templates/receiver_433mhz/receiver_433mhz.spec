# =============================================================================
# TEMPLATE: SYN480R 433MHz ASK/OOK Receiver
# =============================================================================
# Prerequisites: Read templates/TemplateCreation.spec FIRST for universal rules.
# This file covers ONLY circuit-specific details for the 433MHz receiver template.
#
# Template Version: 1.0
# Date: March 2026
# Status: Draft
# Reference: AIreference/SCH_simple-blower-V1.0_1-P1_2025-12-20 (1).pdf


# =============================================================================
# 1. OVERVIEW
# =============================================================================
# Synoxo SYN480R superheterodyne ASK/OOK receiver for 433.92MHz band.
# Used for wireless remote control reception (e.g., key fob, sensor).
# SOP-8 package. 3.3V supply. Digital data output on DO pin.
# Includes LC antenna matching network (L2, L3, C9, C12) and
# 50-ohm antenna connection (RF1).
#
# WARNING: RF matching network component values are specific to the antenna
# and PCB layout. These values are from the reference design and may need
# tuning for a different PCB layout or antenna.


# =============================================================================
# 2. INTERFACE (what the parent schematic connects to)
# =============================================================================
# Type          | Name       | Shape            | Notes
# --------------|------------|------------------|-------------------------------
# Port symbol   | DATA_433   | Ports:DATA_433   | Digital data output to ESP32 GPIO
# Power symbol  | +3.3V      | power:+3.3V      | Global -- receiver supply
# Power symbol  | GND        | power:GND        | Global -- auto-connects across sheets
#
# The antenna (RF1) is included in this template as a PCB trace antenna
# or SMA connector footprint. Not exposed as a port.
#
# NOTE: Port symbol DATA_433 may need to be created in Ports.kicad_sym.


# =============================================================================
# 3. DESIGN NOTES (circuit-specific decisions from reference schematic)
# =============================================================================
# SYN480R pin assignments (SOP-8):
#   Pin 1 GND   -> GND
#   Pin 2 ANT   -> Antenna matching network input
#   Pin 3 VDD   -> +3.3V supply
#   Pin 4 NC    -> No-connect
#   Pin 5 DO    -> Digital data output -> DATA_433 port
#   Pin 6 SHUT  -> Shutdown control (pulled to GND = normal operation)
#   Pin 7 SQ    -> Squelch output (not used, no-connect)
#   Pin 8 RO    -> RSSI output (not used, no-connect)
#
# Antenna matching network (from reference, 433.92MHz):
#   RF1 antenna pad -> C12 (1.8pF) -> L2 (27nH) -> L3 (47nH) -> U1.ANT (pin 2)
#   Between L2/L3 junction and GND: C9 (6.8pF)
#   Between U1.ANT and GND: C13 (100nF, DC blocking / bypass)
#
#   This is a pi-network / L-network impedance match to transform the
#   antenna impedance to the SYN480R input impedance.
#
# IMPORTANT: These LC values are layout-dependent. If the PCB layout changes
# significantly, the matching network may need re-tuning with a VNA.
#
# Decoupling: C13 = 100nF (105 in reference = 1uF, but shown as 105 marking)
#   Actually the reference shows C13 as "105" which is 1uF. This serves as
#   VDD bypass + DC block on the antenna path.


# =============================================================================
# 4. INTERNAL NETS (stay inside this sheet -- NOT exposed)
# =============================================================================
# Net Name     | Path
# -------------|----------------------------------------------------
# ANT_IN       | RF1 -> C12 (1.8pF) -> L2 junction
# MATCH_MID    | L2 (27nH) output -> C9 (6.8pF) to GND -> L3 input
# ANT_IC       | L3 (47nH) output -> C13 (1uF) -> U1.ANT (pin 2)
# DATA_OUT     | U1.DO (pin 5) -> DATA_433 port


# =============================================================================
# 5. COMPONENTS -- ALL FROM JLCPCB
# =============================================================================

# [U1] SYN480R -- 433MHz ASK/OOK Superheterodyne Receiver
#   LCSC:      C15561
#   Symbol:    JLCImport:SYN480R-FS24
#   Package:   SOP-8
#   JLCPCB:    Extended part
#   Freq:      315/433.92MHz (set by SAW filter, internal)
#   VDD:       2.2V to 5.5V
#   Sensitivity: -106dBm typical
#   Pin assignments: see section 3

# [L2] 27nH -- Matching network inductor
#   LCSC:      C76665 (or search 27nH 0402/0603 inductor)
#   Package:   0402 or 0603 (RF, small package acceptable for matching)
#   JLCPCB:    Extended part
#   Note:      RF component -- small package OK for matching network only.
#              This is an exception to the 0805 minimum rule for passives.

# [L3] 47nH -- Matching network inductor
#   LCSC:      C76668 (or search 47nH 0402/0603 inductor)
#   Package:   0402 or 0603 (RF)
#   JLCPCB:    Extended part

# [C9] 6.8pF -- Matching network capacitor
#   LCSC:      C106245 (or search 6.8pF 0402/0603 C0G/NP0)
#   Package:   0402 or 0603 (RF)
#   JLCPCB:    Extended part

# [C12] 1.8pF -- Antenna coupling capacitor
#   LCSC:      C106233 (or search 1.8pF 0402/0603 C0G/NP0)
#   Package:   0402 or 0603 (RF)
#   JLCPCB:    Extended part

# [C13] 1uF -- VDD bypass / DC block
#   LCSC:      C28323
#   Symbol:    JLCImport:CC0805KRX7R7BB105
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> VDD/ANT node, Pin2 -> GND

# [RF1] 433MHz Antenna -- PCB trace or SMA connector
#   LCSC:      C496550 (or search for SMA connector / spring antenna)
#   Package:   SMD or through-hole
#   JLCPCB:    Extended part
#   Note:      Can be a PCB trace antenna (helical or quarter-wave) or
#              an SMA connector for external antenna.


# =============================================================================
# 6. JLCPCB BOM SUMMARY
# =============================================================================
#
# Ref  | Part              | Value    | Pkg    | LCSC     | Type
# -----|-------------------|----------|--------|----------|----------
# U1   | SYN480R-FS24      | 433MHz   | SOP-8  | C15561   | Extended
# L2   | Inductor          | 27nH     | 0402   | C76665   | Extended
# L3   | Inductor          | 47nH     | 0402   | C76668   | Extended
# C9   | Capacitor         | 6.8pF    | 0402   | C106245  | Extended
# C12  | Capacitor         | 1.8pF    | 0402   | C106233  | Extended
# C13  | CC0805KRX7R7BB105 | 1uF      | 0805   | C28323   | Basic
# RF1  | Antenna/SMA       | 433MHz   | SMD    | C496550  | Extended
#
# Total: 7 components (1 basic, 6 extended)
# NOTE: RF matching components use 0402/0603 packages (exception to 0805 rule
# because RF matching requires small parasitic inductance/capacitance).


# =============================================================================
# 7. VERIFICATION CHECKLIST
# =============================================================================
# [ ] +3.3V -> C13 -> U1.VDD (pin 3)
# [ ] U1.GND (pin 1) -> GND
# [ ] U1.SHUT (pin 6) -> GND (normal operation, not shut down)
# [ ] U1.DO (pin 5) -> DATA_433 port
# [ ] NC flags on pins 4 (NC), 7 (SQ), 8 (RO)
# [ ] RF1 -> C12 (1.8pF) -> L2 (27nH) -> L3 (47nH) -> U1.ANT (pin 2)
# [ ] C9 (6.8pF) from L2/L3 junction to GND
# [ ] All positions on 1.27mm grid (except RF matching if smaller grid needed)


# END OF TEMPLATE
