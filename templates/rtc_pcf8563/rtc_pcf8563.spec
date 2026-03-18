# =============================================================================
# TEMPLATE: PCF8563 I2C Real-Time Clock with Crystal
# =============================================================================
# Prerequisites: Read templates/TemplateCreation.spec FIRST for universal rules.
# This file covers ONLY circuit-specific details for the PCF8563 RTC template.
#
# Template Version: 1.0
# Date: March 2026
# Status: Draft
# Reference: AIreference/SCH_simple-blower-V1.0_1-P1_2025-12-20 (1).pdf


# =============================================================================
# 1. OVERVIEW
# =============================================================================
# NXP PCF8563 I2C real-time clock/calendar with external 32.768kHz crystal.
# I2C address: 0x51 (fixed). SO-8 package. Battery backup via coin cell (BT1).
#
# Alternative to: rtc_rv3028 (which has internal TCXO, no external crystal)
# Trade-off: PCF8563 is cheaper and widely available but needs external crystal
# and has lower accuracy (~20ppm vs ~1ppm). Higher backup current (~250nA vs 40nA).


# =============================================================================
# 2. INTERFACE (what the parent schematic connects to)
# =============================================================================
# Type          | Name   | Shape          | Notes
# --------------|--------|----------------|-------------------------------
# Port symbol   | SCL    | Ports:SCL      | I2C clock (global power-style label)
# Port symbol   | SDA    | Ports:SDA      | I2C data (global power-style label)
# Power symbol  | +3.3V  | power:+3.3V    | Global -- main supply
# Power symbol  | GND    | power:GND      | Global -- auto-connects across sheets
#
# I2C pull-ups are NOT included -- they belong on the main I2C bus (parent sheet).


# =============================================================================
# 3. DESIGN NOTES (circuit-specific decisions from reference schematic)
# =============================================================================
# Pin assignments (SO-8):
#   Pin 1 OSCI  -> Crystal X3 pin 1
#   Pin 2 OSCO  -> Crystal X3 pin 2
#   Pin 3 INT#  -> No-connect (interrupt not used in reference)
#   Pin 4 VSS   -> GND
#   Pin 5 SDA   -> SDA port (I2C data)
#   Pin 6 SCL   -> SCL port (I2C clock)
#   Pin 7 CLKOUT -> No-connect (clock output not used)
#   Pin 8 VDD   -> +3.3V main supply
#
# Crystal: X3 = 32.768kHz with C49/C50 = 18pF load capacitors.
#   PCF8563 datasheet specifies CL = 12.5pF for the oscillator.
#   With 18pF external caps: CL_effective ~ (18*18)/(18+18) + Cstray = ~12.5pF
#
# Battery backup: BT1 coin cell (CR1220 or CR2032).
#   BAT+ (pin 1) -> +3.3V rail (charges through VDD path)
#   BAT- (pin 2) -> GND
#   Note: The reference ties BAT+ directly to +3.3V. The PCF8563 has an
#   internal battery switchover circuit -- when VDD drops below VBAT, the
#   chip runs from the battery automatically.
#
# Decoupling: C48 = 100nF on VDD (pin 8).
#
# ESD diodes D6, D7 on I2C lines (shown in reference) -- optional, can be
# omitted if the bus is short and internal to the PCB.


# =============================================================================
# 4. INTERNAL NETS (stay inside this sheet -- NOT exposed)
# =============================================================================
# Net Name     | Path
# -------------|----------------------------------------------------
# OSCI_NET     | U16.OSCI (pin 1) -> X3 pin 1 -> C49 -> GND
# OSCO_NET     | U16.OSCO (pin 2) -> X3 pin 2 -> C50 -> GND
# VDD_LOCAL    | +3.3V -> C48 -> U16.VDD (pin 8) -> BT1.BAT+


# =============================================================================
# 5. COMPONENTS -- ALL FROM JLCPCB
# =============================================================================

# [U16] PCF8563 -- I2C Real-Time Clock
#   LCSC:      C5795601
#   Symbol:    JLCImport:PCF8563
#   Package:   SO-8 (SOP-8)
#   JLCPCB:    Extended part
#   I2C Addr:  0x51 (fixed)
#   VDD:       1.0V to 5.5V
#   Ibat:      ~250nA (timekeeping from battery)
#   Pin assignments:
#     Pin 1 OSCI   -> Crystal input
#     Pin 2 OSCO   -> Crystal output
#     Pin 3 INT#   -> No-connect
#     Pin 4 VSS    -> GND
#     Pin 5 SDA    -> SDA port
#     Pin 6 SCL    -> SCL port
#     Pin 7 CLKOUT -> No-connect
#     Pin 8 VDD    -> +3.3V

# [X3] 32.768kHz Crystal
#   LCSC:      C32346 (or equivalent 32.768kHz 2-pin SMD crystal)
#   Package:   2-pin SMD (3.2x1.5mm or similar)
#   JLCPCB:    Basic/Extended part
#   CL:        12.5pF (matches PCF8563 requirement)

# [C49] 18pF -- Crystal load capacitor (OSCI side)
#   LCSC:      C1808 (or search 18pF 0805 C0G/NP0)
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> OSCI net, Pin2 -> GND

# [C50] 18pF -- Crystal load capacitor (OSCO side)
#   LCSC:      C1808
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> OSCO net, Pin2 -> GND

# [C48] 100nF -- VDD decoupling capacitor
#   LCSC:      C49678
#   Symbol:    JLCImport:CC0805KRX7R9BB104
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> VDD (+3.3V), Pin2 -> GND

# [BT1] Coin Cell Holder (CR1220 or CR2032)
#   LCSC:      C70377 (or search for coin cell holder SMD)
#   Package:   Through-hole or SMD holder
#   JLCPCB:    Extended part
#   Nets:      BAT+ -> +3.3V rail, BAT- -> GND


# =============================================================================
# 6. JLCPCB BOM SUMMARY
# =============================================================================
#
# Ref  | Part              | Value         | Pkg      | LCSC     | Type
# -----|-------------------|---------------|----------|----------|----------
# U16  | PCF8563           | RTC           | SOP-8    | C5795601 | Extended
# X3   | Crystal           | 32.768kHz     | 2-pin    | C32346   | Extended
# C49  | Capacitor         | 18pF NP0      | 0805     | C1808    | Basic
# C50  | Capacitor         | 18pF NP0      | 0805     | C1808    | Basic
# C48  | CC0805KRX7R9BB104 | 100nF 50V     | 0805     | C49678   | Basic
# BT1  | Coin cell holder  | CR1220/CR2032 | --       | C70377   | Extended
#
# Total: 6 components (3 basic, 3 extended)


# =============================================================================
# 7. VERIFICATION CHECKLIST
# =============================================================================
# [ ] +3.3V -> C48 -> U16.VDD (pin 8)
# [ ] U16.VSS (pin 4) -> GND
# [ ] X3 between OSCI (pin 1) and OSCO (pin 2)
# [ ] C49 (18pF) from OSCI to GND
# [ ] C50 (18pF) from OSCO to GND
# [ ] U16.SDA (pin 5) -> SDA port
# [ ] U16.SCL (pin 6) -> SCL port
# [ ] NC flags on pins 3 (INT#) and 7 (CLKOUT)
# [ ] BT1.BAT+ -> +3.3V, BT1.BAT- -> GND
# [ ] All positions on 1.27mm grid


# END OF TEMPLATE
