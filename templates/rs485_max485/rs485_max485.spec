# =============================================================================
# TEMPLATE: MAX485ESA+T RS-485 Transceiver (Half-Duplex, Auto-Direction)
# =============================================================================
# Prerequisites: Read templates/TemplateCreation.spec FIRST for universal rules.
# This file covers ONLY circuit-specific details for the MAX485 RS-485 template.
#
# Template Version: 1.0
# Date: March 2026
# Status: Draft
# Reference: AIreference/SCH_simple-blower-V1.0_1-P1_2025-12-20 (1).pdf


# =============================================================================
# 1. OVERVIEW
# =============================================================================
# Maxim MAX485ESA+T RS-485/RS-422 transceiver in SOIC-8. 5V supply with
# 3.3V-compatible logic inputs. Half-duplex operation with NPN transistor
# (Q1 SS8050) for automatic TX direction control from UART TX line.
# Includes 4.7k bus bias resistors on A/B lines.
#
# Alternative to: rs485_sp3485 (which uses SP3485EN at 3.3V with GPIO DE control)
# Trade-off: MAX485 runs at 5V (better noise margin on long buses) with
# auto-direction via TX line. SP3485 is 3.3V native with explicit GPIO control.


# =============================================================================
# 2. INTERFACE (what the parent schematic connects to)
# =============================================================================
# Type          | Name       | Shape            | Notes
# --------------|------------|------------------|-------------------------------
# Port symbol   | RX         | Ports:RX         | UART RX from transceiver RO (to ESP32)
# Port symbol   | TX         | Ports:TX         | UART TX from ESP32 (drives DI and auto-DE)
# Port symbol   | RS485_A    | Ports:RS485_A    | Non-inverting bus line (A/+)
# Port symbol   | RS485_B    | Ports:RS485_B    | Inverting bus line (B/-)
# Power symbol  | +5V        | power:+5V        | Global -- transceiver supply
# Power symbol  | GND        | power:GND        | Global -- auto-connects across sheets
#
# NOTE: No RS485_DE port -- direction is automatic via Q1 transistor.
# When TX is idle (HIGH), Q1 is ON, pulling DE LOW = receive mode.
# When TX goes LOW (start bit), Q1 turns OFF, DE goes HIGH = transmit mode.
# R11 (1k) pulls DE HIGH when Q1 is off. R13/R14 (4.7k) bias the bus.


# =============================================================================
# 3. DESIGN NOTES (circuit-specific decisions from reference schematic)
# =============================================================================
# MAX485 pin assignments (SOIC-8):
#   Pin 1 RO   -> RX port (receiver output to ESP32 RXD0)
#   Pin 2 RE#  -> Active-low receiver enable (tied to DE for half-duplex)
#   Pin 3 DE   -> Driver enable (auto-controlled via Q1 NPN)
#   Pin 4 DI   -> TX port (driver input from ESP32 TXD0)
#   Pin 5 GND  -> GND
#   Pin 6 A    -> RS485_A bus line (non-inverting)
#   Pin 7 B    -> RS485_B bus line (inverting)
#   Pin 8 VCC  -> +5V supply
#
# Auto-direction control circuit:
#   - Q1 (SS8050 NPN): Base driven by TX line via R13 (4.7k)
#   - Q1 Collector -> DE/RE# junction
#   - Q1 Emitter -> GND
#   - R11 (1k) pull-up from +5V to DE/RE# junction
#   - When TX idle (HIGH): Q1 ON -> DE pulled LOW -> receive mode
#   - When TX active (LOW/start bit): Q1 OFF -> R11 pulls DE HIGH -> transmit
#
# Bus biasing (from reference):
#   - R14 (4.7k): Bias on B line (pull-down to GND for fail-safe idle state)
#   - R15, R16: Marked N/C in reference (not populated). Available pads for
#     optional termination or A-line bias if needed for specific bus topology.
#
# No termination resistor in reference (R15, R16 = N/C).
# Add 120 ohm termination externally if needed for long bus runs.
#
# Decoupling: C14 = 100nF on VCC (pin 8).


# =============================================================================
# 4. INTERNAL NETS (stay inside this sheet -- NOT exposed)
# =============================================================================
# Net Name     | Path
# -------------|----------------------------------------------------
# DE_RE_NET    | U7.RE# (pin 2) <-> U7.DE (pin 3) <-> Q1.C <-> R11
# TX_BASE      | TX port -> R13 (4.7k) -> Q1.Base
# VCC_LOCAL    | +5V -> C14 -> U7.VCC (pin 8) -> R11 (1k pull-up)


# =============================================================================
# 5. COMPONENTS -- ALL FROM JLCPCB
# =============================================================================

# [U7] MAX485ESA+T -- RS-485/RS-422 Transceiver
#   LCSC:      C19738
#   Symbol:    JLCImport:MAX485ESA_T
#   Package:   SOIC-8
#   JLCPCB:    Extended part
#   VCC:       4.75V to 5.25V
#   Data Rate: Up to 2.5 Mbps
#   Pin assignments: see section 3

# [Q1] SS8050 -- NPN Transistor (auto-direction control)
#   LCSC:      C2150
#   Symbol:    JLCImport:SS8050_C2150
#   Package:   SOT-23
#   JLCPCB:    Basic part
#   hFE:       >= 100
#   Nets:      Base -> R13, Collector -> DE/RE# junction, Emitter -> GND

# [R11] 1k -- DE/RE# pull-up to +5V
#   LCSC:      C17513
#   Symbol:    JLCImport:0805W8F1001T5E
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> +5V, Pin2 -> DE/RE# junction

# [R13] 4.7k -- TX to Q1 base resistor
#   LCSC:      C17673
#   Symbol:    JLCImport:0805W8F4701T5E
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> TX port net, Pin2 -> Q1.Base

# [R14] 4.7k -- Bus B line pull-down to GND
#   LCSC:      C17673
#   Symbol:    JLCImport:0805W8F4701T5E
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> RS485_B net, Pin2 -> GND

# [C14] 100nF -- VCC decoupling capacitor
#   LCSC:      C49678
#   Symbol:    JLCImport:CC0805KRX7R9BB104
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> VCC (+5V), Pin2 -> GND


# =============================================================================
# 6. JLCPCB BOM SUMMARY
# =============================================================================
#
# Ref  | Part              | Value    | Pkg      | LCSC     | Type
# -----|-------------------|----------|----------|----------|----------
# U7   | MAX485ESA+T       | --       | SOIC-8   | C19738   | Extended
# Q1   | SS8050            | NPN      | SOT-23   | C2150    | Basic
# R11  | 0805W8F1001T5E    | 1k 1%    | 0805     | C17513   | Basic
# R13  | 0805W8F4701T5E    | 4.7k 1%  | 0805     | C17673   | Basic
# R14  | 0805W8F4701T5E    | 4.7k 1%  | 0805     | C17673   | Basic
# C14  | CC0805KRX7R9BB104 | 100nF    | 0805     | C49678   | Basic
#
# Total: 6 components (5 basic, 1 extended)


# =============================================================================
# 7. VERIFICATION CHECKLIST
# =============================================================================
# [ ] U7.RO (pin 1) -> RX port
# [ ] U7.DI (pin 4) -> TX port
# [ ] U7.RE# (pin 2) tied to U7.DE (pin 3) -- half-duplex
# [ ] Q1.Collector -> DE/RE# junction
# [ ] Q1.Base -> R13 (4.7k) -> TX net
# [ ] Q1.Emitter -> GND
# [ ] R11 (1k) from +5V to DE/RE# junction (pull-up)
# [ ] R14 (4.7k) from B line to GND (bias pull-down)
# [ ] U7.VCC (pin 8) -> +5V via C14 (100nF)
# [ ] U7.GND (pin 5) -> GND
# [ ] All positions on 1.27mm grid


# END OF TEMPLATE
