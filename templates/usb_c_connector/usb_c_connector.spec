# =============================================================================
# TEMPLATE: USB-C Connector with Data Lines
# =============================================================================
# Prerequisites: Read templates/TemplateCreation.spec FIRST for universal rules.
# This file covers ONLY circuit-specific details for the USB-C template.
#
# Template Version: 1.1
# Date: March 2026
# Status: Draft (v1.1 -- corrected: SGM2523A removed, it belongs in LED driver)
# Reference: AIreference/SCH_simple-blower-V1.0_1-P1_2025-12-20 (1).pdf


# =============================================================================
# 1. OVERVIEW
# =============================================================================
# USB-C (or Type-C) connector for USB 2.0 data connection to ESP32-S3.
# Provides D+/D- data lines and VBUS (+5V) power input from host.
# Simple design: connector + pull-down resistors on data lines + decoupling.
#
# NOTE: The reference schematic SGM2523A units (U4, U14) are LED drivers,
# NOT USB VBUS protectors. The USB section in the reference is a direct
# VBUS->+5V connection with no current limiting on VBUS itself.


# =============================================================================
# 2. INTERFACE (what the parent schematic connects to)
# =============================================================================
# Type          | Name    | Shape         | Notes
# --------------|---------|---------------|-------------------------------
# Port symbol   | UD+     | Ports:UD+     | USB D+ data line (to ESP32 IO20)
# Port symbol   | UD-     | Ports:UD-     | USB D- data line (to ESP32 IO19)
# Power symbol  | +5V     | power:+5V     | Global -- VBUS from USB host
# Power symbol  | GND     | power:GND     | Global -- auto-connects across sheets
#
# NOTE: Port symbols UD+ and UD- may need to be created in Ports.kicad_sym.
# This is USB device mode -- VBUS is an INPUT from the host.


# =============================================================================
# 3. DESIGN NOTES (circuit-specific decisions from reference schematic)
# =============================================================================
# USB-C connector (USB1 in reference, 18-pin):
#   VBUS pins -> +5V rail (direct, with C39=100nF decoupling)
#   D+ pins   -> UD+ port (with R31 = 4.7k pull-down to GND)
#   D- pins   -> UD- port (with R30 = 4.7k pull-down to GND)
#   GND pins  -> GND
#   Shield    -> GND
#
# USB data line resistors:
#   R30 = 4.7k pull-down on UD+ (ensures clean state when USB disconnected)
#   R31 = 4.7k pull-down on UD- (ensures clean state when USB disconnected)
#   ESP32-S3 has internal USB PHY; no external series resistors needed.
#
# Decoupling: C39 = 100nF on VBUS close to connector.
#
# The 5V from VBUS feeds the board's +5V rail directly. For overcurrent
# protection, add a fuse or current limiter on the parent sheet if needed.


# =============================================================================
# 4. INTERNAL NETS (stay inside this sheet -- NOT exposed)
# =============================================================================
# Net Name     | Path
# -------------|----------------------------------------------------
# VBUS_NET     | USB connector VBUS -> C39 (100nF) -> +5V power symbol
# DP_NET       | USB connector D+ -> R31 (4.7k to GND) -> UD+ port
# DM_NET       | USB connector D- -> R30 (4.7k to GND) -> UD- port


# =============================================================================
# 5. COMPONENTS -- ALL FROM JLCPCB
# =============================================================================

# [J1] USB-C Connector (USB 2.0, 16-pin)
#   LCSC:      C2765186
#   Symbol:    JLCImport:TYPE-C_16PIN_2MD_073
#   Note:      Already in JLCImport library (TYPE-C_16PIN_2MD_073)
#   Package:   SMD USB-C receptacle
#   JLCPCB:    Extended part
#   Note:      16-pin variant for USB 2.0 (no SS TX/RX pairs needed).
#              Must have VBUS, D+, D-, GND, and shield pins.

# [R30] 4.7k -- USB D+ pull-down
#   LCSC:      C17673
#   Symbol:    JLCImport:0805W8F4701T5E
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> UD+ net, Pin2 -> GND

# [R31] 4.7k -- USB D- pull-down
#   LCSC:      C17673
#   Symbol:    JLCImport:0805W8F4701T5E
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> UD- net, Pin2 -> GND

# [C39] 100nF -- VBUS decoupling capacitor
#   LCSC:      C49678
#   Symbol:    JLCImport:CC0805KRX7R9BB104
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> VBUS (+5V), Pin2 -> GND


# =============================================================================
# 6. JLCPCB BOM SUMMARY
# =============================================================================
#
# Ref  | Part              | Value     | Pkg      | LCSC     | Type
# -----|-------------------|-----------|----------|----------|----------
# J1   | USB-C connector   | USB 2.0   | SMD      | C2765186 | Extended
# R30  | 0805W8F4701T5E    | 4.7k 1%   | 0805     | C17673   | Basic
# R31  | 0805W8F4701T5E    | 4.7k 1%   | 0805     | C17673   | Basic
# C39  | CC0805KRX7R9BB104 | 100nF 50V | 0805     | C49678   | Basic
#
# Total: 4 components (3 basic, 1 extended)


# =============================================================================
# 7. VERIFICATION CHECKLIST
# =============================================================================
# [ ] USB connector VBUS -> C39 (100nF) -> +5V power symbol
# [ ] USB D+ -> R30 (4.7k to GND) -> UD+ port
# [ ] USB D- -> R31 (4.7k to GND) -> UD- port
# [ ] USB GND and shield -> GND
# [ ] All positions on 1.27mm grid


# END OF TEMPLATE
