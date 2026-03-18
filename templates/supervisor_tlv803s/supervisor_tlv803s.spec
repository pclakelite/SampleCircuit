# =============================================================================
# TEMPLATE: TLV803S Voltage Supervisor / Reset Circuit
# =============================================================================
# Prerequisites: Read templates/TemplateCreation.spec FIRST for universal rules.
# This file covers ONLY circuit-specific details for the supervisor template.
#
# Template Version: 1.0
# Date: March 2026
# Status: Reviewed and Locked — 2026-03-06


# =============================================================================
# 1. OVERVIEW
# =============================================================================
# Voltage supervisor that monitors the +3.3V rail and holds the ESP32-S3 in
# reset (Enable low) when power is below threshold (~2.93V typ). Once +3.3V
# is stable, the open-drain RESET# output releases, Enable goes high via
# pull-up, and the ESP32 boots.
# 5 components total. Simple protection circuit.


# =============================================================================
# 2. INTERFACE (what the parent schematic connects to)
# =============================================================================
# Type          | Name    | Shape          | Notes
# --------------|---------|----------------|-------------------------------
# Port symbol   | Enable  | Ports:Enable   | Reset output → ESP32 EN pin (global via power flag)
# Power symbol  | +3.3V   | power:+3.3V    | Global — auto-connects across sheets
# Power symbol  | GND     | power:GND      | Global — auto-connects across sheets
#
# Enable uses a custom port symbol from Ports.kicad_sym (see TemplateCreation.spec §7).


# =============================================================================
# 3. DESIGN NOTES (circuit-specific decisions)
# =============================================================================
# - TLV803S threshold: ~2.93V (typ) for "S" variant — suitable for 3.3V rail
# - RESET# is open-drain active-low: needs external pull-up (R16)
# - R16 (10k) pulls Enable high to +3.3V when RESET# is released
# - C59 (100nF) on Enable line filters noise and adds slight rise-time delay
# - C58 (10uF) bulk decoupling on +3.3V near VDD pin
# - C4 (100nF) bypass decoupling on +3.3V near VDD pin
# - Enable net connects to ESP32 EN pin on the parent sheet
# - From EV4 reference design (schematic page 2, U9/R16/C4/C58/C59)


# =============================================================================
# 4. INTERNAL NETS (stay inside this sheet — NOT exposed)
# =============================================================================
# Net Name    | Path
# ------------|----------------------------------------------------
# (none)      | All nets either go to power symbols or the Enable port


# =============================================================================
# 5. COMPONENTS — ALL FROM JLCPCB
# =============================================================================

# [U9] TLV803SDBZR — Voltage Supervisor
#   LCSC:      C132016
#   Symbol:    JLCImport:TLV803SDBZR
#   Package:   SOT-23-3
#   JLCPCB:    Extended part
#   Threshold: ~2.93V typ (S variant)
#   Output:    Open-drain active-low RESET#
#   Pin assignments:
#     Pin 1 GND     → GND (power symbol)
#     Pin 2 RESET#  → Enable net (R16, C59, Enable port)
#     Pin 3 VDD     → +3.3V (power symbol)
#   lib_symbol notes:
#     - Hide pin_numbers: YES
#     - Keep pin_names visible (GND, RESET#, VDD are useful)

# [R16] 10k Resistor — RESET# pull-up to +3.3V
#   LCSC:      C17414
#   Symbol:    JLCImport:0805W8F1002T5E
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 → +3.3V, Pin2 → Enable net (RESET#)
#   lib_symbol notes:
#     - Hide pin_numbers AND pin_names

# [C58] 10uF Capacitor — +3.3V bulk decoupling
#   LCSC:      C97973
#   Symbol:    JLCImport:GRM32ER7YA106KA12L
#   Package:   1210 (substituted from 1206 35V — same value, larger package OK)
#   JLCPCB:    Basic part
#   Nets:      Pin1 → +3.3V, Pin2 → GND
#   Note:      Murata 10uF X7R. 1210 package is acceptable substitute for 1206.
#   lib_symbol notes:
#     - Hide pin_numbers AND pin_names
#     - VERTICAL pin layout (pins at ±5.08 on Y axis, not X)

# [C4] 100nF Capacitor — +3.3V bypass decoupling
#   LCSC:      C49678
#   Symbol:    JLCImport:CC0805KRX7R9BB104
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 → +3.3V, Pin2 → GND
#   lib_symbol notes:
#     - Hide pin_numbers AND pin_names

# [C59] 100nF Capacitor — Enable output filter
#   LCSC:      C49678
#   Symbol:    JLCImport:CC0805KRX7R9BB104
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 → Enable net, Pin2 → GND
#   lib_symbol notes:
#     - Hide pin_numbers AND pin_names


# =============================================================================
# 6. JLCPCB BOM SUMMARY
# =============================================================================
#
# Ref  | Part             | Value     | Pkg    | LCSC     | Type
# -----|------------------|-----------|--------|----------|----------
# U9   | TLV803SDBZR      | TLV803S   | SOT-23 | C132016  | Extended
# R16  | Resistor         | 10k 1%    | 0805   | C17414   | Basic
# C58  | Capacitor        | 10uF      | 1210   | C97973   | Basic
# C4   | Capacitor        | 100nF     | 0805   | C49678   | Basic
# C59  | Capacitor        | 100nF     | 0805   | C49678   | Basic
#
# Total: 5 components (4 basic, 1 extended)
# JLCPCB extended part fee: ~$3/unique extended × 1 = ~$3 setup


# =============================================================================
# 7. SCHEMATIC LAYOUT — POSITIONS (all on 1.27mm grid, REVIEWED)
# =============================================================================
# All coordinates in mm on A4 sheet, snapped to 1.27mm grid.
# Reviewed and adjusted in KiCad 2026-03-06.
#
# Component    | Position (x, y)     | Angle | Notes
# -------------|---------------------|-------|----------------------------------
# U9 (TLV803S) | (153.67, 100.33)   | 0     | Center of sheet
# R16 (10k)    | (128.27, 90.17)    | 270   | Vertical, pull-up left of U9
# C59 (100nF)  | (140.97, 111.76)   | 270   | Vertical, filter below RESET#
# C58 (10uF)   | (172.72, 99.06)    | 180   | Vertical (native), VDD decoupling
# C4 (100nF)   | (187.96, 99.06)    | 270   | Vertical, VDD bypass
#
# Port symbols:
#   Enable     | (121.92, 101.60)    | 0     | Pin at (124.46, 101.60)
#
# Power symbols:
#   +3.3V #1   | (128.27, 78.74)     | 0     | Above R16
#   +3.3V #2   | (172.72, 88.90)     | 0     | Above VDD rail
#   GND #1     | (135.89, 99.06)     | 270   | Sideways, feeds U9.GND horizontal
#   GND #2     | (140.97, 119.38)    | 0     | Below C59
#   GND #3     | (172.72, 106.68)    | 0     | Below C58
#   GND #4     | (187.96, 106.68)    | 0     | Below C4


# =============================================================================
# 8. PIN ENDPOINTS (for wiring) — REVIEWED
# =============================================================================
# U9 at (153.67, 100.33), angle=0:
#   Pin 1 GND:    (142.24, 99.06)    — left, upper
#   Pin 2 RESET#: (142.24, 101.60)   — left, lower
#   Pin 3 VDD:    (165.10, 100.33)   — right
#
# R16 at (128.27, 90.17), angle=270 (vertical, P1 top):
#   Pin 1: (128.27, 85.09)  — top → +3.3V
#   Pin 2: (128.27, 95.25)  — bottom → Enable junction
#
# C59 at (140.97, 111.76), angle=270 (vertical, P1 top):
#   Pin 1: (140.97, 106.68) — top → Enable junction
#   Pin 2: (140.97, 116.84) — bottom → GND
#
# C58 at (172.72, 99.06), angle=180 (vertical GRM32, P1 top):
#   Pin 1: (172.72, 93.98)  — top → +3.3V rail
#   Pin 2: (172.72, 104.14) — bottom → GND
#
# C4 at (187.96, 99.06), angle=270 (vertical, P1 top):
#   Pin 1: (187.96, 93.98)  — top → +3.3V rail
#   Pin 2: (187.96, 104.14) — bottom → GND


# =============================================================================
# 9. WIRING CONNECTIONS — REVIEWED
# =============================================================================
# +3.3V to R16 pull-up:
#   +3.3V(1) (128.27, 78.74) → R16.P1 (128.27, 85.09)  — vertical down
#
# Enable net (two junctions: 128.27 and 140.97 at y=101.60):
#   Enable port pin (124.46, 101.60) → junction (128.27, 101.60) — horizontal
#   R16.P2 (128.27, 95.25) → junction (128.27, 101.60)           — vertical down
#   Junction (128.27, 101.60) → junction (140.97, 101.60)        — horizontal
#   C59.P1 (140.97, 106.68) → junction (140.97, 101.60)          — vertical up
#   Junction (140.97, 101.60) → U9.RESET# (142.24, 101.60)      — horizontal stub
#
# C59 to GND:
#   GND(2) (140.97, 119.38) → C59.P2 (140.97, 116.84) — vertical up
#
# U9.GND routing (GND symbol sideways, direct horizontal):
#   GND(1) (135.89, 99.06) → U9.GND (142.24, 99.06)   — horizontal right
#
# +3.3V VDD rail:
#   +3.3V(2) (172.72, 88.90) → (172.72, 93.98)         — vertical down
#   VDD stub: (165.10, 93.98) → U9.VDD (165.10, 100.33) — vertical down
#   Rail seg 1: (165.10, 93.98) → (172.72, 93.98)       — horizontal
#   Rail seg 2: (172.72, 93.98) → (187.96, 93.98)       — horizontal
#   Junction at (172.72, 93.98) — C58.P1 + rail + +3.3V wire
#
# Decoupling cap GND:
#   C58.P2 (172.72, 104.14) → GND(3) (172.72, 106.68)  — vertical down
#   C4.P2 (187.96, 104.14) → GND(4) (187.96, 106.68)   — vertical down


# =============================================================================
# 10. VERIFICATION CHECKLIST — REVIEWED
# =============================================================================
# [x] U9.VDD (pin 3) connected to +3.3V via rail
# [x] U9.GND (pin 1) connected to GND (sideways GND symbol, horizontal wire)
# [x] U9.RESET# (pin 2) connected to Enable net (junction at 140.97)
# [x] R16 pulls Enable to +3.3V (pin1→+3.3V, pin2→Enable junction at 128.27)
# [x] C59 filters Enable output (pin1→Enable junction at 140.97, pin2→GND)
# [x] C58 bulk decouples +3.3V (pin1→+3.3V rail, pin2→GND)
# [x] C4 bypass decouples +3.3V (pin1→+3.3V rail, pin2→GND)
# [x] Enable port symbol connects to junction at (128.27, 101.60)
# [x] Junction at (128.27, 101.60) — R16.P2 + Enable port + horizontal wire
# [x] Junction at (140.97, 101.60) — C59.P1 + Enable wire + U9.RESET# stub
# [x] Junction at (172.72, 93.98) — +3.3V rail branch
# [x] All pin numbers hidden
# [x] All component values match BOM table
# [x] ERC passes clean

# END OF TEMPLATE
