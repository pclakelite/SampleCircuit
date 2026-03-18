# =============================================================================
# TEMPLATE: IP6503S 12V to 5V Buck Regulator
# =============================================================================
# Prerequisites: Read templates/TemplateCreation.spec FIRST for universal rules.
# This file covers ONLY circuit-specific details for the IP6503S PSU template.
#
# Template Version: 1.0
# Date: March 2026
# Status: Draft
# Reference: AIreference/SCH_simple-blower-V1.0_1-P1_2025-12-20 (1).pdf


# =============================================================================
# 1. OVERVIEW
# =============================================================================
# IP6503S USB charging/buck controller used as a 12V to 5V step-down converter.
# External inductor design (L4 10uH). Input TVS protection (SMBJ16CA).
# The IP6503S has USB D+/D- pins for USB negotiation but these are unused
# in this pure power supply application (NC pins 3, 4).
#
# Alternative to: psu_lmzm23601_5v (which uses integrated inductor)
# Trade-off: IP6503S is cheaper but needs external inductor; LMZM23601 is
# more compact with integrated inductor.


# =============================================================================
# 2. INTERFACE (what the parent schematic connects to)
# =============================================================================
# Type          | Name    | Shape         | Notes
# --------------|---------|---------------|-------------------------------
# Power symbol  | +12V    | power:+12V    | Global -- input supply
# Power symbol  | +5V     | power:+5V     | Global -- regulated output
# Power symbol  | GND     | power:GND     | Global -- auto-connects across sheets
#
# No signal ports -- this is a pure power supply module.


# =============================================================================
# 3. DESIGN NOTES (circuit-specific decisions from reference schematic)
# =============================================================================
# - VIN (pin 1): 12V input via TVS diode D3 (SMBJ16CA) for surge protection
# - NC (pin 2): No-connect
# - DP (pin 3): USB D+ -- no-connect in PSU-only application
# - DM (pin 4): USB D- -- no-connect in PSU-only application
# - VOUT (pin 5): 5V regulated output
# - GND (pin 6): Power ground
# - SW (pin 7): Switch node -- connects to inductor L4
# - BST (pin 8): Bootstrap -- 100nF cap (C29) from BST to SW
# - GND (pin 9): Additional ground pad
#
# Input protection: D3 SMBJ16CA bidirectional TVS diode (16V clamp)
# Output inductor: L4 = 10uH (shielded power inductor)
# Input cap: C34 = 100uF 50V electrolytic (bulk)
# Output cap: C30 = 470uF 16V electrolytic (bulk output smoothing)
# Output ceramic: C35 = 22uF 25V X5R ceramic (HF decoupling, parallel with C30)
# Bootstrap cap: C29 = 100nF ceramic (BST to SW)


# =============================================================================
# 4. INTERNAL NETS (stay inside this sheet -- NOT exposed)
# =============================================================================
# Net Name     | Path
# -------------|----------------------------------------------------
# VIN_PROT     | +12V -> D3 (TVS, parallel to GND) -> U10.VIN (pin 1)
# SW_NODE      | U10.SW (pin 7) -> L4 (10uH) -> VOUT rail
# BST_NET      | U10.BST (pin 8) -> C29 -> SW_NODE
# VOUT_RAIL    | L4 output -> C30 (470uF) || C35 (22uF) -> +5V


# =============================================================================
# 5. COMPONENTS -- ALL FROM JLCPCB
# =============================================================================

# [U10] IP6503S -- USB Charging/Buck Controller
#   LCSC:      C432571
#   Symbol:    JLCImport:IP6503S-3_1A
#   Package:   ESOP-8
#   JLCPCB:    Extended part
#   Vin Range: 3.5V to 32V
#   Vout:      5V (fixed internal)
#   Iout:      Up to 3.1A (with external inductor)
#   Pin assignments (from reference):
#     Pin 1 VIN   -> VIN rail (12V via TVS)
#     Pin 2 NC    -> No-connect
#     Pin 3 DP    -> No-connect (USB D+, unused)
#     Pin 4 DM    -> No-connect (USB D-, unused)
#     Pin 5 VOUT  -> Output rail (+5V)
#     Pin 6 GND   -> GND
#     Pin 7 SW    -> Switch node to inductor L4
#     Pin 8 BST   -> Bootstrap cap C29
#     Pin 9 GND   -> GND (exposed pad)

# [D3] SMBJ16CA -- Bidirectional TVS Diode (16V clamp)
#   LCSC:      C284001
#   Symbol:    JLCImport:SMBJ16CA_C284001
#   Package:   SMB (DO-214AA)
#   JLCPCB:    Extended part
#   Nets:      Anode1 -> VIN rail, Anode2 -> GND (bidirectional)

# [L4] 10uH Power Inductor -- Buck output inductor
#   LCSC:      C408335
#   Package:   SMD shielded (5x5mm or similar)
#   JLCPCB:    Extended part
#   Nets:      Pin1 -> SW node, Pin2 -> VOUT rail
#   Isat:      >= 3A

# [C34] 100uF 50V -- Input bulk capacitor
#   LCSC:      C2992088
#   Package:   SMD electrolytic
#   JLCPCB:    Extended part
#   Nets:      Pin+ -> VIN rail, Pin- -> GND

# [C30] 470uF 16V -- Output bulk capacitor
#   LCSC:      C164069
#   Symbol:    JLCImport:ECAP_470uF_16V_C164069
#   Package:   SMD electrolytic 8x10mm (Lelon VZH471M1CTR-0810)
#   JLCPCB:    Extended part
#   Nets:      Pin+ -> VOUT rail (+5V), Pin- -> GND
#   Note:      Upgraded from 6.3V to 16V for adequate voltage margin (3.2x derating)

# [C35] 22uF 25V -- Output ceramic capacitor (HF decoupling)
#   LCSC:      C2178233
#   Symbol:    JLCImport:CC1206KKX5R8BB226
#   Package:   1206 (YAGEO X5R)
#   JLCPCB:    Extended part
#   Nets:      Pin1 -> VOUT rail (+5V), Pin2 -> GND
#   Note:      In parallel with C30. Low ESR for fast transient response.

# [C29] 100nF -- Bootstrap capacitor (BST to SW)
#   LCSC:      C49678
#   Symbol:    JLCImport:CC0805KRX7R9BB104
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> BST, Pin2 -> SW node


# =============================================================================
# 6. JLCPCB BOM SUMMARY
# =============================================================================
#
# Ref  | Part           | Value         | Pkg         | LCSC      | Type
# -----|----------------|---------------|-------------|-----------|----------
# U10  | IP6503S-3.1A   | --            | ESOP-8      | C432571   | Extended
# D3   | SMBJ16CA       | 16V TVS       | SMB         | C284001   | Extended
# L4   | Inductor       | 10uH >=3A    | SMD 5x5     | C408335   | Extended
# C34  | Electrolytic   | 100uF 50V     | SMD         | C2992088  | Extended
# C30  | Electrolytic   | 470uF 16V     | SMD 8x10    | C164069   | Extended
# C35  | Ceramic        | 22uF 25V X5R  | 1206        | C2178233  | Extended
# C29  | Ceramic        | 100nF 50V     | 0805        | C49678    | Basic
#
# Total: 7 components (1 basic, 6 extended)
# NOTE: LCSC part numbers are tentative -- verify stock before build script.


# =============================================================================
# 7. VERIFICATION CHECKLIST
# =============================================================================
# [ ] +12V -> TVS D3 -> VIN pin (pin 1)
# [ ] BST (pin 8) -> C29 -> SW (pin 7)
# [ ] SW (pin 7) -> L4 (10uH) -> VOUT rail (+5V)
# [ ] C34 (100uF) between VIN rail and GND
# [ ] C30 (470uF 16V) between VOUT rail and GND
# [ ] C35 (22uF 25V) between VOUT rail and GND (parallel with C30)
# [ ] GND on pins 6 and 9
# [ ] NC flags on pins 2, 3, 4
# [ ] All positions on 1.27mm grid


# END OF TEMPLATE