# =============================================================================
# SPEC: Terminal Block Test Point Wiring Pattern
# =============================================================================
# Defines the standard wiring style for 2-pin screw terminal blocks used as
# power test points or signal breakouts in SampleCircuit schematics.
#
# Reference: J3 (5V TEST) in SampleCircuit.kicad_sch
# Date: March 2026


# =============================================================================
# 1. COMPONENT
# =============================================================================
# Part:      WJ500V-5_08-2P-14-00A (Xinya 2-pin 5.08mm screw terminal)
# Symbol:    JLCImport:WJ500V-5_08-2P-14-00A
# Footprint: JLCImport:WJ500V-5_08-2P-14-00A
# LCSC:      C8465
# JLCPCB:    Basic part
#
# Pin layout (angle=0, pins point downward from body):
#   Pin 1: local offset (-1.27, 0), length 5.08 → endpoint at (sym_x - 1.27, sym_y + 5.08)
#   Pin 2: local offset (+1.27, 0), length 5.08 → endpoint at (sym_x + 1.27, sym_y + 5.08)


# =============================================================================
# 2. PIN CONVENTION
# =============================================================================
# Pin 1 (left)  = Power rail or signal positive  (e.g. +5V, +24V, OUTP)
# Pin 2 (right) = GND or signal negative          (e.g. GND, OUTN)


# =============================================================================
# 3. WIRING PATTERN
# =============================================================================
# Layout is vertical: connector body on top, symbols directly below.
#
#       +-------+
#       |  J3   |  <- WJ500V symbol at (sx, sy)
#       +--+-+--+
#          | |
#     P1   | |   P2     <- pin endpoints at (sx-1.27, sy+5.08) and (sx+1.27, sy+5.08)
#          | |
#     +5V  | |   GND    <- power symbols at (sx-1.27, sy+10.16) and (sx+1.27, sy+10.16)
#
# Wire routing:
#   Pin 1 → vertical wire DOWN 5.08mm → power rail symbol (angle=180, flipped)
#   Pin 2 → vertical wire DOWN 5.08mm → GND symbol (angle=0, normal)
#
# Coordinates (relative to symbol center sx, sy):
#   Pin 1 endpoint:   (sx - 1.27,  sy + 5.08)
#   Pin 2 endpoint:   (sx + 1.27,  sy + 5.08)
#   Power symbol:     (sx - 1.27,  sy + 10.16)   angle=180
#   GND symbol:       (sx + 1.27,  sy + 10.16)   angle=0
#   Wire 1:           (sx - 1.27,  sy + 5.08) → (sx - 1.27, sy + 10.16)
#   Wire 2:           (sx + 1.27,  sy + 5.08) → (sx + 1.27, sy + 10.16)


# =============================================================================
# 4. PROPERTY PLACEMENT
# =============================================================================
# Reference (e.g. "J3"):  centered above body, ~9mm above center
#   Position: (sx, sy - 9.1)   angle=0
#
# Value (e.g. "5V TEST"):  centered below reference, ~6.5mm above center
#   Position: (sx, sy - 6.6)   angle=0


# =============================================================================
# 5. SIGNAL VARIANT (SPEAKER)
# =============================================================================
# For non-power terminals (e.g. speaker output), replace power/GND symbols
# with port symbols:
#   Pin 1 → OUTP port (Ports:OUTP)   angle=90 (rotated, pin points down)
#   Pin 2 → OUTN port (Ports:OUTN)   angle=90
#
# Same 5.08mm vertical wire drop applies.


# =============================================================================
# 6. USAGE EXAMPLES
# =============================================================================
# J1: 24V INPUT   Pin 1 = +24V,  Pin 2 = GND
# J2: 12V TEST    Pin 1 = +12V,  Pin 2 = GND
# J3: 5V TEST     Pin 1 = +5V,   Pin 2 = GND
# J4: 3.3V TEST   Pin 1 = +3.3V, Pin 2 = GND
# J5: SPEAKER     Pin 1 = OUTP,  Pin 2 = OUTN


# END OF SPEC
