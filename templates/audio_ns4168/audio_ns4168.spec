# =============================================================================
# TEMPLATE: NS4168 I2S Audio Amplifier
# =============================================================================
# Prerequisites: Read templates/TemplateCreation.spec FIRST for universal rules.
#                Read specs/CircuitCreation.spec for bus requirements.
# This file covers ONLY circuit-specific details for the NS4168 audio amp template.
#
# Template Version: 1.0
# Date: March 2026
# Status: Draft (AI-generated, pending human review)


# =============================================================================
# 1. OVERVIEW
# =============================================================================
# NS4168 I2S digital input mono Class D audio amplifier. Receives digital audio
# via I2S bus, outputs up to 2.5W into a 4-ohm speaker. Single +5V supply,
# no external MCLK needed. ESOP-8 package with exposed pad.
# Manufacturer: Shenzhen Nsiway Technology. LCSC: C910588.


# =============================================================================
# 2. INTERFACE (what the parent schematic connects to)
# =============================================================================
# Type          | Name   | Shape          | Notes
# --------------|--------|----------------|-------------------------------
# Port symbol   | AMP_EN | Ports:AMP_EN   | Amp enable/shutdown GPIO (left side, angle=0)
# Port symbol   | DIN    | Ports:DIN      | I2S serial data (left side, angle=0)
# Port symbol   | BCLK   | Ports:BCLK     | I2S bit clock (left side, angle=0)
# Port symbol   | LRCLK  | Ports:LRCLK    | I2S word select (left side, angle=0)
# Port symbol   | OUTP   | Ports:OUTP     | Speaker positive (right side, angle=180)
# Port symbol   | OUTN   | Ports:OUTN     | Speaker negative (right side, angle=180)
# Power symbol  | +5V    | power:+5V      | Global -- auto-connects across sheets
# Power symbol  | GND    | power:GND      | Global -- auto-connects across sheets
#
# I2S and speaker signals use custom port symbols from Ports.kicad_sym.
# Speaker connector goes on PARENT sheet (see CircuitCreation.spec section 4).
#
# PORT PLACEMENT PATTERN:
#   - AMP_EN, DIN, BCLK, LRCLK are on the LEFT (angle=0) because their IC pins
#     are on the left side. This eliminates wire crossings.
#   - OUTP, OUTN are on the RIGHT (angle=180) -- same side as VOP/VON pins.


# =============================================================================
# 3. DESIGN NOTES (circuit-specific decisions -- from datasheet)
# =============================================================================
# - CTRL (pin 1): GPIO-controlled via AMP_EN port + R20 (100K pull-down to GND).
#   CTRL pin voltage thresholds (per datasheet):
#     1.5V to VDD    = Right channel
#     0.9V to 1.15V  = Left channel
#     0V to 0.4V     = Shutdown (low power)
#   R20 (100K) pulls CTRL to GND = shutdown at boot (prevents startup pop).
#   ESP32 GPIO drives AMP_EN HIGH after I2S init = right channel active.
#   GPIO floating or LOW = amp shutdown (~1uA), no speaker output.
#
# - VDD (pin 6): Connected to +5V via decoupling network.
#   Datasheet recommends 100uF electrolytic + 1uF ceramic bypass caps.
#
# - GND (pin 7): Power ground.
# - EP / PAD (pin 9): Exposed pad, connected to GND.
#
# - VOP/VON (pins 8/5): BTL differential speaker outputs.
#   No coupling capacitors needed (Class D filterless output).
#   No output filter needed per datasheet (filterless architecture).
#
# - No I2S bus pull-ups -- I2S is push-pull.
#
# - Anti-distortion (NCN) feature is built-in, no external components needed.


# =============================================================================
# 4. INTERNAL NETS (stay inside this sheet -- NOT exposed)
# =============================================================================
# Net Name       | Path
# ---------------|----------------------------------------------------
# CTRL_INT       | AMP_EN port -> R20.P2 (junction) -> U5.CTRL (pin 1)
#                | R20.P1 -> GND (pull-down, keeps CTRL low at boot)
# VDD_INT        | +5V -> C18.P1 -> C17.P1 -> U5.VDD (pin 6)


# =============================================================================
# 5. COMPONENTS
# =============================================================================
#
# [U5] NS4168 -- I2S DAC + Class D Amplifier
#   Symbol:    JLCImport:NS4168_C910588
#   Position:  (152.40, 101.60) angle=0
#   Package:   ESOP-8-EP (3.9x4.9mm, 1.27mm pitch)
#   LCSC:      C910588
#   JLCPCB:    Extended part
#
# [R20] 100K -- CTRL pull-down to GND (shutdown at boot, GPIO enables)
#   Symbol:    JLCImport:0805W8F1003T5E
#   Position:  (132.08, 104.14) angle=90 (vertical)
#   Package:   0805
#   LCSC:      C17407
#   Nets:      Pin1 -> GND (bottom), Pin2 -> CTRL wire (top, junction)
#
# [C17] 1uF -- VDD ceramic decoupling capacitor
#   Symbol:    JLCImport:CL21B105KBFNNNE
#   Position:  (172.72, 107.95) angle=270
#   Package:   0805
#   LCSC:      C28323
#   Nets:      Pin1 -> VDD bus, Pin2 -> GND
#
# [C18] 100uF -- VDD electrolytic bulk capacitor
#   Symbol:    JLCImport:ECAP_100uF_50V_C2992088
#   Position:  (180.34, 107.95) angle=0 (already vertical)
#   Package:   SMD electrolytic
#   LCSC:      C2992088
#   Nets:      Pin1 -> VDD bus, Pin2 -> GND


# =============================================================================
# 6. JLCPCB BOM SUMMARY
# =============================================================================
# Ref  | Value        | Pkg   | LCSC     | Type     | Qty
# -----|--------------|-------|----------|----------|----
# U5   | NS4168       | ESOP8 | C910588  | Extended | 1
# R20  | 100k 1%      | 0805  | C17407   | Basic    | 1
# C17  | 1uF 50V      | 0805  | C28323   | Basic    | 1
# C18  | 100uF 50V    | SMD   | C2992088 | Basic    | 1


# =============================================================================
# 7. PIN ENDPOINT REFERENCE (VERIFIED)
# =============================================================================
# CRITICAL: The (at x y) in a KiCad lib_symbol pin IS the wire connection point.
# Do NOT subtract pin length.
#
# U5 at (152.40, 101.60) angle=0:
#   Schematic endpoint = (152.40 + pin_at_x, 101.60 - pin_at_y)
#
# Pin  | Name   | Side   | Pin (at x, y)      | Schematic endpoint
# -----|--------|--------|--------------------|---------------------
# 1    | CTRL   | Left   | (-11.43, 2.54)     | (140.97, 99.06)
# 2    | LRCLK  | Left   | (-11.43, 0)        | (140.97, 101.60)
# 3    | BCLK   | Left   | (-11.43, -2.54)    | (140.97, 104.14)
# 4    | SDATA  | Left   | (-11.43, -5.08)    | (140.97, 106.68)
# 5    | VON    | Right  | (11.43, -5.08)     | (163.83, 106.68)
# 6    | VDD    | Right  | (11.43, -2.54)     | (163.83, 104.14)
# 7    | GND    | Right  | (11.43, 0)         | (163.83, 101.60)
# 8    | VOP    | Right  | (11.43, 2.54)      | (163.83, 99.06)
# 9    | EP     | Right  | (11.43, 5.08)      | (163.83, 96.52)


# =============================================================================
# 8. SYMBOL PLACEMENT SUMMARY
# =============================================================================
# Ref      | lib_id                          | Position          | Angle
# ---------|---------------------------------|-------------------|------
# U5       | JLCImport:NS4168_C910588        | (152.40, 101.60)  | 0
# R20      | JLCImport:0805W8F1003T5E        | (132.08, 104.14)  | 90
# C17      | JLCImport:CL21B105KBFNNNE       | (172.72, 107.95)  | 270
# C18      | JLCImport:ECAP_100uF_50V_C2992088 | (180.34, 107.95) | 0
# #PWR01   | power:+5V                       | (176.53, 101.60)  | 0
# #PWR02   | power:GND                       | (170.18, 101.60)  | 90
# #PWR03   | power:GND                       | (170.18, 96.52)   | 90
# #PWR04   | power:GND                       | (132.08, 111.76)  | 0
# #PWR05   | power:GND                       | (172.72, 114.30)  | 0
# #PWR06   | power:GND                       | (180.34, 114.30)  | 0
# #PORT01  | Ports:AMP_EN                    | (121.92, 99.06)   | 0
# #PORT02  | Ports:DIN                       | (121.92, 106.68)  | 0
# #PORT03  | Ports:BCLK                      | (121.92, 104.14)  | 0
# #PORT04  | Ports:LRCLK                     | (121.92, 101.60)  | 0
# #PORT05  | Ports:OUTP                      | (187.96, 99.06)   | 180
# #PORT06  | Ports:OUTN                      | (187.96, 106.68)  | 180


# =============================================================================
# 9. WIRING PLAN (as designed)
# =============================================================================
# LRCLK routing (left side, straight):
#   LRCLK port pin (124.46, 101.60) -> horizontal -> U5.LRCLK (140.97, 101.60)
#
# BCLK routing (left side, straight):
#   BCLK port pin (124.46, 104.14) -> horizontal -> U5.BCLK (140.97, 104.14)
#
# DIN routing (left side, straight):
#   DIN port pin (124.46, 106.68) -> horizontal -> U5.SDATA (140.97, 106.68)
#
# AMP_EN -> CTRL (with R20 100K pull-down):
#   AMP_EN port pin (124.46, 99.06) -> horizontal -> U5.CTRL (140.97, 99.06)
#   R20.P2 (132.08, 99.06) junction on CTRL wire [top of R20]
#   R20.P1 (132.08, 109.22) -> vertical -> GND (132.08, 111.76)
#
# VOP -> OUTP (right side, straight):
#   U5.VOP (163.83, 99.06) -> horizontal -> OUTP port (185.42, 99.06)
#
# VON -> OUTN (right side, straight):
#   U5.VON (163.83, 106.68) -> horizontal -> OUTN port (185.42, 106.68)
#
# GND pin 7:
#   U5.GND (163.83, 101.60) -> horizontal -> GND (170.18, 101.60)
#
# EP GND:
#   U5.EP (163.83, 96.52) -> horizontal -> GND (170.18, 96.52)
#
# VDD power bus:
#   +5V (176.53, 101.60) -> vertical down -> (176.53, 104.14) [VDD bus]
#   VDD bus: U5.VDD (163.83, 104.14) -> C17.P1 (172.72, 104.14)
#            -> C18.P1 (180.34, 104.14)
#
# Cap GND (separate):
#   C17.P2 (172.72, 111.76) -> vertical -> GND (172.72, 114.30)
#   C18.P2 (180.34, 111.76) -> vertical -> GND (180.34, 114.30)


# =============================================================================
# 10. JUNCTIONS
# =============================================================================
# (172.72, 104.14)  -- C17 top meets VDD bus horizontal
# (176.53, 104.14)  -- +5V vertical meets VDD bus horizontal
# (132.08, 99.06)   -- R20 top meets AMP_EN->CTRL wire


# =============================================================================
# 11. NO-CONNECTS
# =============================================================================
# None -- all 9 pins are used.


# =============================================================================
# 12. VERIFICATION CHECKLIST
# =============================================================================
# [ ] All 6 port symbols render clean hexagonal flags (AMP_EN, DIN, BCLK, LRCLK, OUTP, OUTN)
# [ ] +5V connects to VDD bus (C17, C18, pin 6)
# [ ] GND connects to U5.GND (pin 7), U5.EP (pin 9), R20.P1, C17.P2, C18.P2
# [ ] R20 (100K) pulls CTRL to GND (shutdown at boot); AMP_EN port drives CTRL via GPIO
# [ ] All wire endpoints match pin endpoints (verified formula)
# [ ] All coordinates on 1.27mm grid
# [ ] Bypass caps per datasheet: 100uF electrolytic + 1uF ceramic


# END OF SPEC
