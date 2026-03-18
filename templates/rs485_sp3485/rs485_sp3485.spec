# =============================================================================
# TEMPLATE: SP3485EN RS-485 Transceiver (Half-Duplex)
# =============================================================================
# Prerequisites: Read templates/TemplateCreation.spec FIRST for universal rules.
# This file covers ONLY circuit-specific details for the RS-485 template.
#
# Template Version: 1.0
# Date: March 2026
# Status: Draft, awaiting human review in KiCad


# =============================================================================
# 1. OVERVIEW
# =============================================================================
# Half-duplex RS-485 transceiver for Modbus or other serial bus communication.
# SP3485EN is a 3.3V, low-power, slew-rate-limited transceiver (SOIC-8).
# ~RE and DE are tied together for half-duplex direction control from one GPIO.
# Includes 120 ohm bus termination resistor (populate on last device only).
# 3 components + power symbols.


# =============================================================================
# 2. INTERFACE (what the parent schematic connects to)
# =============================================================================
# Type          | Name       | Shape            | Notes
# --------------|------------|------------------|-------------------------------
# Port symbol   | RX         | Ports:RX         | UART RX from transceiver RO
# Port symbol   | TX         | Ports:TX         | UART TX to transceiver DI
# Port symbol   | RS485_DE   | Ports:RS485_DE   | Direction enable (HIGH=transmit)
# Port symbol   | RS485_A    | Ports:RS485_A    | Non-inverting bus line (A/+)
# Port symbol   | RS485_B    | Ports:RS485_B    | Inverting bus line (B/-)
# Power symbol  | +3.3V      | power:+3.3V      | Global -- auto-connects across sheets
# Power symbol  | GND        | power:GND        | Global -- auto-connects across sheets
#
# RX, TX, RS485_DE connect to ESP32-S3 GPIOs.
# RS485_A, RS485_B connect to the bus connector (screw terminal on parent sheet).
# ~RE and DE are tied together: HIGH = transmit, LOW = receive.


# =============================================================================
# 3. DESIGN NOTES (circuit-specific decisions)
# =============================================================================
# - SP3485EN is 3.3V compatible (VCC range: 3.0V to 3.6V)
# - Slew-rate limited output reduces EMI (max 250kbps, sufficient for Modbus)
# - ~RE (pin 2) and DE (pin 3) tied together for half-duplex operation:
#     RS485_DE HIGH  = transmit mode (driver enabled, receiver disabled)
#     RS485_DE LOW   = receive mode  (driver disabled, receiver enabled)
# - 120 ohm termination resistor R2 between A and B:
#     Only populate on the LAST device on the bus (both ends for long runs)
#     Leave unpopulated (DNP) for intermediate nodes
# - C1 100nF decoupling cap on VCC, placed close to IC
# - No bias resistors included (bus has built-in fail-safe for open/shorted lines)
# - No ESD protection TVS diodes included (add externally if needed for harsh environments)


# =============================================================================
# 4. INTERNAL NETS (stay inside this sheet -- NOT exposed)
# =============================================================================
# Net Name     | Path
# -------------|----------------------------------------------------
# DE_RE_TIED   | U1.RE# (pin 2) <-> U1.DE (pin 3) <-> RS485_DE port
# VCC_LOCAL    | U1.VCC (pin 8) -> C1.pin1 (junction) -> +3.3V


# =============================================================================
# 5. COMPONENTS -- ALL FROM JLCPCB
# =============================================================================

# [U1] SP3485EN-L/TR -- RS-485 Transceiver
#   LCSC:      C8963
#   Symbol:    JLCImport:SP3485EN-L_TR
#   Package:   SOIC-8 (5.0x4.0mm)
#   JLCPCB:    Basic part
#   VCC Range: 3.0V to 3.6V
#   Data Rate: Up to 10 Mbps (250 kbps with slew limiting)
#   Pin assignments:
#     Pin 1 RO   -> RX port (receiver output to ESP32)
#     Pin 2 RE#  -> Tied to DE (pin 3) for half-duplex
#     Pin 3 DE   -> RS485_DE port (direction control from ESP32 GPIO)
#     Pin 4 DI   -> TX port (driver input from ESP32)
#     Pin 5 GND  -> GND (power symbol)
#     Pin 6 A    -> RS485_A port (non-inverting bus line)
#     Pin 7 B    -> RS485_B port (inverting bus line)
#     Pin 8 VCC  -> +3.3V (power symbol) + C1
#   lib_symbol notes:
#     - Hide pin_numbers: YES
#     - Keep pin_names visible (RO, RE#, DE, DI, A, B, GND, VCC are useful)

# [C1] 100nF Capacitor -- VCC decoupling
#   LCSC:      C49678
#   Symbol:    JLCImport:CC0805KRX7R9BB104
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> VCC net (junction), Pin2 -> GND
#   Note:      Place close to U1 pin 8. Standard bypass cap.
#   lib_symbol notes:
#     - Hide pin_numbers AND pin_names

# [R2] 120 ohm Resistor -- Bus termination
#   LCSC:      C17437
#   Symbol:    JLCImport:0805W8F1200T5E
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> RS485_B net, Pin2 -> RS485_A net
#   Note:      Only populate on the last device on the bus.
#              Leave unpopulated (DNP) for intermediate nodes.
#   lib_symbol notes:
#     - Hide pin_numbers AND pin_names


# =============================================================================
# 6. JLCPCB BOM SUMMARY
# =============================================================================
#
# Ref  | Part             | Value     | Pkg    | LCSC    | Type
# -----|------------------|-----------|--------|---------|----------
# U1   | SP3485EN-L/TR    | --        | SOIC-8 | C8963   | Basic
# C1   | Capacitor        | 100nF 50V | 0805   | C49678  | Basic
# R2   | Resistor         | 120R 1%   | 0805   | C17437  | Basic
#
# Total: 3 components (3 basic, 0 extended)
# JLCPCB extended part fee: $0


# =============================================================================
# 7. SCHEMATIC LAYOUT -- CURRENT POSITIONS (all on 1.27mm grid)
# =============================================================================
# All coordinates in mm on A4 sheet, snapped to 1.27mm grid.
# Grid formula: snap(val) = round(round(val / 1.27) * 1.27, 2)
#
# Component    | Position (x, y)     | Angle | Notes
# -------------|---------------------|-------|----------------------------------
# U1 (IC)      | (149.86, 100.33)    | 0     | Center of sheet, IC body
# C1 (100nF)   | (167.64, 101.6)     | 270   | Vertical (pin1 top=VCC, pin2 bot=GND)
# R2 (120R)    | (185.42, 100.33)    | 270   | Vertical termination between A and B
#
# Port symbols (Ports library, left side):
#   RX         | (128.27, 96.52)     | 0     | Pin at (130.81, 96.52)
#   RS485_DE   | (128.27, 100.33)    | 0     | Pin at (130.81, 100.33)
#   TX         | (128.27, 104.14)    | 0     | Pin at (130.81, 104.14)
#
# Port symbols (Ports library, right side, angle=180):
#   RS485_B    | (177.8, 99.06)      | 180   | Pin at (175.26, 99.06)
#   RS485_A    | (177.8, 101.6)      | 180   | Pin at (175.26, 101.6)
#
# Power symbols:
#   +3.3V      | (167.64, 91.44)     | 0     | Above C1/VCC
#   GND #PWR02 | (167.64, 109.22)    | 0     | Below C1
#   GND #PWR03 | (158.75, 109.22)    | 0     | Below U1.GND
#
# Junctions:
#   (139.7, 100.33)  -- DE/RE# fork point
#   (167.64, 96.52)  -- VCC rail meets cap top
#   (175.26, 99.06)  -- B bus fork to port and R2
#   (175.26, 101.6)  -- A bus fork to port and R2


# =============================================================================
# 8. PIN ENDPOINTS (for wiring -- from lib_symbol pin positions)
# =============================================================================
# Formula: schematic_pos = (sym_x + pin_local_x, sym_y - pin_local_y)
#
# U1 at (149.86, 100.33), angle=0:
#   Pin 1 RO:   (140.97, 96.52)    -- left side, top
#   Pin 2 RE#:  (140.97, 99.06)    -- left side
#   Pin 3 DE:   (140.97, 101.6)    -- left side
#   Pin 4 DI:   (140.97, 104.14)   -- left side, bottom
#   Pin 5 GND:  (158.75, 104.14)   -- right side, bottom
#   Pin 6 A:    (158.75, 101.6)    -- right side
#   Pin 7 B:    (158.75, 99.06)    -- right side
#   Pin 8 VCC:  (158.75, 96.52)    -- right side, top
#
# C1 at (167.64, 101.6), angle=270 (vertical, pin1=top):
#   Pin 1: (167.64, 96.52)  -- top (VCC rail)
#   Pin 2: (167.64, 106.68) -- bottom (GND)
#
# R2 at (185.42, 100.33), angle=270 (vertical, pin1=top):
#   Pin 1: (185.42, 95.25)  -- top (connects to B bus)
#   Pin 2: (185.42, 105.41) -- bottom (connects to A bus)


# =============================================================================
# 9. WIRING CONNECTIONS
# =============================================================================
# Each wire is listed as: from_point -> to_point
#
# Signal wires (left side, straight horizontal):
#   RX port pin (130.81, 96.52) -> U1.RO (140.97, 96.52)         -- horizontal
#   TX port pin (130.81, 104.14) -> U1.DI (140.97, 104.14)       -- horizontal
#
# DE/RE# fork (L-route via x=139.7):
#   RS485_DE port pin (130.81, 100.33) -> junction (139.7, 100.33) -- horizontal
#   junction (139.7, 100.33) -> (139.7, 99.06)                     -- vertical up
#   (139.7, 99.06) -> U1.RE# (140.97, 99.06)                     -- horizontal
#   junction (139.7, 100.33) -> (139.7, 101.6)                     -- vertical down
#   (139.7, 101.6) -> U1.DE (140.97, 101.6)                      -- horizontal
#
# Power wires (right side):
#   +3.3V (167.64, 91.44) -> junction (167.64, 96.52)             -- vertical down
#   U1.VCC (158.75, 96.52) -> junction (167.64, 96.52)            -- horizontal
#   C1.pin2 (167.64, 106.68) -> GND #PWR02 (167.64, 109.22)      -- vertical down
#   U1.GND (158.75, 104.14) -> GND #PWR03 (158.75, 109.22)       -- vertical down
#
# Bus wires (A and B, right side):
#   U1.B (158.75, 99.06) -> junction (175.26, 99.06)              -- horizontal
#   U1.A (158.75, 101.6) -> junction (175.26, 101.6)              -- horizontal
#
# Termination R2 wiring (from bus junctions):
#   junction (175.26, 99.06) -> (185.42, 99.06)                   -- horizontal
#   (185.42, 99.06) -> R2.pin1 (185.42, 95.25)                   -- vertical up
#   junction (175.26, 101.6) -> (185.42, 101.6)                   -- horizontal
#   (185.42, 101.6) -> R2.pin2 (185.42, 105.41)                  -- vertical down


# =============================================================================
# 10. VERIFICATION CHECKLIST
# =============================================================================
# [ ] U1.RO (pin 1) connected to RX port
# [ ] U1.RE# (pin 2) connected to RS485_DE port (tied to DE)
# [ ] U1.DE (pin 3) connected to RS485_DE port (tied to RE#)
# [ ] U1.DI (pin 4) connected to TX port
# [ ] U1.GND (pin 5) connected to GND power symbol
# [ ] U1.A (pin 6) connected to RS485_A port and R2.pin2
# [ ] U1.B (pin 7) connected to RS485_B port and R2.pin1
# [ ] U1.VCC (pin 8) connected to +3.3V power symbol and C1.pin1
# [ ] C1.pin2 connected to GND
# [ ] R2 connects between B and A bus lines (120 ohm termination)
# [ ] All component values match BOM table
# [ ] No unused pins left unconnected (all 8 IC pins wired)
# [ ] ERC passes clean


# =============================================================================
# 11. OPTIONAL ENHANCEMENTS (not in current design)
# =============================================================================
# 1. ESD protection: Add PESD2CAN TVS diode on A/B lines for surge protection
# 2. Bias resistors: Add 390R pull-up on A and 390R pull-down on B for fail-safe
#    idle bus state (prevents floating when no driver active)
# 3. Separate RE# and DE control: Use two GPIOs for independent RX/TX enable
#    (allows simultaneous listen-while-transmit for collision detection)
# 4. Full-duplex: Replace SP3485 with SP3490 (requires separate A/B pairs)
# 5. Higher speed: Remove slew limiting by using MAX3485 instead of SP3485

# END OF TEMPLATE
