# =============================================================================
# TEMPLATE: SC16IS752 I2C-to-Dual-UART Bridge with GPIO
# =============================================================================
# Prerequisites: Read templates/TemplateCreation.spec FIRST for universal rules.
# This file covers ONLY circuit-specific details for the UART bridge template.
#
# Template Version: 1.0
# Date: March 2026
# Status: Draft


# =============================================================================
# 1. OVERVIEW
# =============================================================================
# I2C-to-dual-UART bridge with 8 GPIO pins. Replaces PI7C9X760CZDEX from
# EV4 reference design with a JLCPCB-available NXP part. Supports up to
# 5 Mbps UART. Uses 16MHz crystal for exact 1 Mbps baud rate (servo comms).
# Channel A: primary UART (TX/RX exposed). Channel B: secondary UART
# (TXB/RXB exposed). All 8 GPIOs exposed as ports.
# I2C address configurable via A0/A1 (default: both GND = 0x4D).


# =============================================================================
# 2. INTERFACE (what the parent schematic connects to)
# =============================================================================
# Type          | Name    | Shape         | Notes
# --------------|---------|---------------|--------------------------------------
# Port symbol   | SCL     | Ports:SCL     | I2C clock bus (global via power flag)
# Port symbol   | SDA     | Ports:SDA     | I2C data bus (global via power flag)
# Port symbol   | TX      | Ports:TX      | Channel A transmit output
# Port symbol   | RX      | Ports:RX      | Channel A receive input
# Power symbol  | +3.3V   | power:+3.3V   | Global - auto-connects across sheets
# Power symbol  | GND     | power:GND     | Global - auto-connects across sheets
#
# SCL and SDA use custom port symbols from Ports.kicad_sym.
# TX and RX use custom port symbols from Ports.kicad_sym.


# =============================================================================
# 3. DESIGN NOTES (circuit-specific decisions)
# =============================================================================
# - 14.7456MHz crystal chosen for exact standard baud rate division:
#     115200: divisor = 14.7456MHz / (16 * 115200) = 8.000 (exact, zero error)
#     230400: divisor = 4.000 (exact)
#     460800: divisor = 2.000 (exact)
#     921600: divisor = 1.000 (exact)
#   Based on nebkat/i2c_uart_board_reference_design.
#   NOTE: 1 Mbps NOT supported (divisor = 0.9216, ~8% error — too high).
#
# - Crystal load capacitors: 15pF each. 7U14745AE12UCG has CL=12pF.
#   With Cstray ~3pF: CL_actual = 15/2 + 3 = 10.5pF (close to 12pF, within pull range).
#
# - 1M feedback resistor (R3) across crystal (XTAL1 to XTAL2):
#   Provides DC bias for the internal oscillator amplifier.
#   Ensures reliable crystal startup. Matches reference design R5.
#
# - I2C mode: pin 9 (I2C/SPI) tied to +3.3V via wire to VDD
#
# - I2C address: A0=GND, A1=GND (default 0x4D 7-bit).
#   A0/A1 can be tied to VDD, VSS, SCL, or SDA (16 combinations).
#   Common VDD/GND-only addresses (8-bit write -> 7-bit):
#     A0=VDD  A1=VDD  -> 0x90 -> 0x48
#     A0=GND  A1=VDD  -> 0x98 -> 0x4C
#     A0=VDD  A1=GND  -> 0x92 -> 0x49
#     A0=GND  A1=GND  -> 0x9A -> 0x4D
#   See datasheet Table 32/33 for full 16-address table.
#
# - #RESET: 10k pull-up to +3.3V (active low, keeps chip out of reset)
#
# - IRQ#: 1k pull-up to +3.3V (active low open-drain output).
#   NOT exposed as a port in this version. Connected internally with pull-up.
#   User can add IRQ port later if interrupt-driven operation is needed.
#
# - Channel B (TXB/RXB): pins have no-connect flags.
#   User can wire these later if dual-UART is needed.
#
# - GPIO0-7: All have no-connect flags.
#   User can wire these later for LED/switch/control IO.
#
# - Pin 12 (N.C./SO): No-connect (SPI-only pin, unused in I2C mode)
#
# - #RTSA, #CTSA (pins 1, 2): No-connect (flow control not used)
#
# - #CTSB, #RTSB (pins 16, 17): No-connect (Channel B flow control not used)


# =============================================================================
# 4. INTERNAL NETS (stay inside this sheet - NOT exposed)
# =============================================================================
# Net Name    | Path
# ------------|----------------------------------------------------
# XTAL1_NET   | U.XTAL1 (pin 6) -> X.OSC1 (pin 1) -> R3.pin1 -> C1.pin1
# XTAL2_NET   | U.XTAL2 (pin 7) -> X.OSC2 (pin 3) -> R3.pin2 -> C2.pin1
# IRQ_NET     | U.IRQ# (pin 15) -> R_irq.pin1, R_irq.pin2 -> +3.3V
# RESET_NET   | U.#RESET (pin 5) -> R_reset.pin1, R_reset.pin2 -> +3.3V


# =============================================================================
# 5. COMPONENTS - ALL FROM JLCPCB
# =============================================================================

# [U1] SC16IS752IPW,112 - I2C/SPI to Dual UART Bridge
#   LCSC:      C57156
#   Symbol:    JLCImport:SC16IS752IPW_112
#   Package:   TSSOP-28 (9.7x4.4mm)
#   JLCPCB:    Extended part
#   I2C Addr:  0x4D (A0=GND, A1=GND, 7-bit; 0x9A 8-bit write)
#   VDD Range: 2.3V to 3.6V
#   UART:      2 channels, up to 5 Mbps
#   GPIO:      8 programmable I/O
#   FIFO:      64 bytes TX + 64 bytes RX per channel
#   Pin assignments:
#     Pin 1  #RTSA      -> NC (no-connect)
#     Pin 2  #CTSA      -> NC (no-connect)
#     Pin 3  TXA        -> TX port (Channel A transmit)
#     Pin 4  RXA        -> RX port (Channel A receive)
#     Pin 5  #RESET     -> R_reset (10k pull-up to +3.3V)
#     Pin 6  XTAL1      -> X1.OSC1 + C1.pin1 (crystal + load cap)
#     Pin 7  XTAL2      -> X1.OSC2 + C2.pin1 (crystal + load cap)
#     Pin 8  VDD        -> +3.3V (power symbol)
#     Pin 9  I2C[SPI]   -> +3.3V (I2C mode select)
#     Pin 10 A0[#CS]    -> GND (address bit 0)
#     Pin 11 A1[SI]     -> GND (address bit 1)
#     Pin 12 N.C.[SO]   -> NC (SPI-only, unused)
#     Pin 13 SCL[SCLK]  -> SCL port
#     Pin 14 SDA[VSS]   -> SDA port
#     Pin 15 IRQ#       -> R_irq (1k pull-up to +3.3V)
#     Pin 16 CTSB#      -> NC (no-connect)
#     Pin 17 RTSB#      -> NC (no-connect)
#     Pin 18 GPIO0      -> NC (no-connect)
#     Pin 19 GPIO1      -> NC (no-connect)
#     Pin 20 GPIO2      -> NC (no-connect)
#     Pin 21 GPIO3      -> NC (no-connect)
#     Pin 22 VSS        -> GND (power symbol)
#     Pin 23 TXB        -> NC (no-connect)
#     Pin 24 RXB        -> NC (no-connect)
#     Pin 25 GPIO4      -> NC (no-connect)
#     Pin 26 GPIO5      -> NC (no-connect)
#     Pin 27 GPIO6      -> NC (no-connect)
#     Pin 28 GPIO7      -> NC (no-connect)
#   lib_symbol notes:
#     - Hide pin_numbers: YES
#     - Keep pin_names visible (TXA, RXA, SCL, etc. are useful)

# [X1] 7U14745AE12UCG - 14.7456MHz Crystal
#   LCSC:      C557185
#   Symbol:    JLCImport:7U14745AE12UCG
#   Package:   SMD3225-4P (3.2x2.5mm)
#   JLCPCB:    Basic part
#   Manufacturer: SJK
#   Frequency: 14.7456 MHz
#   CL:        12 pF
#   Tolerance: +/-10 ppm
#   Temp:      -40 to +85C
#   Pin assignments:
#     Pin 1 OSC1 -> U1.XTAL1 (pin 6)
#     Pin 2 GND  -> GND
#     Pin 3 OSC2 -> U1.XTAL2 (pin 7)
#     Pin 4 GND  -> GND
#   lib_symbol notes:
#     - Hide pin_numbers AND pin_names
#
# [R3] 1M Resistor - Crystal feedback
#   LCSC:      C17514
#   Symbol:    JLCImport:0805W8F1004T5E
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> XTAL1_NET (R3.P1 = C1.P1), Pin2 -> XTAL2_NET (R3.P2 = C2.P1)
#   Note:      Provides DC bias for oscillator amplifier. Ref design R5.

# [C1] 15pF Capacitor - XTAL1 load cap
#   LCSC:      C1794
#   Symbol:    JLCImport:CL21C150JBANNNC
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> XTAL1_NET, Pin2 -> GND
#   Note:      Place close to X1 pin 1

# [C2] 15pF Capacitor - XTAL2 load cap
#   LCSC:      C1794
#   Symbol:    JLCImport:CL21C150JBANNNC
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> XTAL2_NET, Pin2 -> GND

# [C3] 100nF Capacitor - VDD decoupling
#   LCSC:      C49678
#   Symbol:    JLCImport:CC0805KRX7R9BB104
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> +3.3V, Pin2 -> GND
#   Note:      Place close to U1 pin 8 (VDD)

# [R1] 10k Resistor - #RESET pull-up
#   LCSC:      C17414
#   Symbol:    JLCImport:0805W8F1002T5E
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> U1.#RESET (pin 5), Pin2 -> +3.3V

# [R2] 1k Resistor - IRQ# pull-up
#   LCSC:      C17513
#   Symbol:    JLCImport:0805W8F1001T5E
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> U1.IRQ# (pin 15), Pin2 -> +3.3V


# =============================================================================
# 6. JLCPCB BOM SUMMARY
# =============================================================================
#
# Ref  | Part              | Value       | Pkg      | LCSC     | Type
# -----|-------------------|-------------|----------|----------|----------
# U1   | SC16IS752IPW,128  | --          | TSSOP-28 | C57156   | Extended
# X1   | 7U14745AE12UCG    | 14.7456MHz  | SMD3225  | C557185  | Basic
# C1   | Capacitor         | 15pF 50V    | 0805     | C1794    | Basic
# C2   | Capacitor         | 15pF 50V    | 0805     | C1794    | Basic
# C3   | Capacitor         | 100nF 50V   | 0805     | C49678   | Basic
# R1   | Resistor          | 10k 1%      | 0805     | C17414   | Basic
# R2   | Resistor          | 1k 1%       | 0805     | C17513   | Basic
# R3   | Resistor          | 1M 1%       | 0805     | C17514   | Basic
#
# Total: 8 components (1 extended, 7 basic)
# JLCPCB extended part fee: ~$3 x 1 = ~$3 setup


# =============================================================================
# 7. SCHEMATIC LAYOUT - INITIAL POSITIONS (all on 1.27mm grid)
# =============================================================================
# All coordinates in mm on A4 sheet, snapped to 1.27mm grid.
# Grid formula: snap(val) = round(round(val / 1.27) * 1.27, 2)
#
# Component    | Position (x, y)     | Angle | Notes
# -------------|---------------------|-------|----------------------------------
# U1 (UART)    | (149.86, 100.33)    | 0     | Center of sheet, IC body
# X1 (16MHz)   | (119.38, 96.52)     | 0     | Left of U1, near XTAL pins
# C1 (15pF)    | (114.30, 91.44)     | 270   | Vertical, pin1 top (XTAL1 net)
# C2 (15pF)    | (124.46, 91.44)     | 270   | Vertical, pin1 top (XTAL2 net)
# C3 (100nF)   | (139.70, 109.22)    | 270   | Vertical, near VDD pin
# R1 (10k)     | (119.38, 106.68)    | 0     | Horizontal, #RESET pull-up
# R2 (1k)      | (180.34, 116.84)    | 270   | Vertical, IRQ# pull-up
#
# Port symbols (Ports library):
#   SCL        | (119.38, 114.30)    | 0     | Pin at (121.92, 114.30)
#   SDA        | (119.38, 116.84)    | 0     | Pin at (121.92, 116.84)
#   TX         | (119.38, 88.90)     | 0     | Pin at (121.92, 88.90)
#   RX         | (119.38, 91.44)     | 0     | Pin at (121.92, 91.44)
#
# Power symbols:
#   +3.3V #1   | (149.86, 88.90)     | 0     | Above U1.VDD
#   +3.3V #2   | (119.38, 104.14)    | 0     | Above R1 (RESET pull-up)
#   +3.3V #3   | (180.34, 109.22)    | 0     | Above R2 (IRQ pull-up)
#   GND #1     | (149.86, 119.38)    | 0     | Below U1.VSS
#   GND #2     | (114.30, 99.06)     | 0     | Below C1
#   GND #3     | (124.46, 99.06)     | 0     | Below C2
#   GND #4     | (139.70, 116.84)    | 0     | Below C3
#   GND #5     | (129.54, 106.68)    | 90    | A0 pin GND (right of wire)
#   GND #6     | (129.54, 109.22)    | 90    | A1 pin GND (right of wire)
#
# No-connects: pins 1, 2, 12, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 28


# =============================================================================
# 8. PIN ENDPOINTS (for wiring - calculated from symbol positions)
# =============================================================================
# Formula: schematic_pos = (sym_x + pin_local_x, sym_y - pin_local_y)
#
# U1 at (149.86, 100.33), angle=0:
#   Pin 1  #RTSA:       (129.54, 83.82)    -- left side
#   Pin 2  #CTSA:       (129.54, 86.36)    -- left side
#   Pin 3  TXA:         (129.54, 88.90)    -- left side
#   Pin 4  RXA:         (129.54, 91.44)    -- left side
#   Pin 5  #RESET:      (129.54, 93.98)    -- left side
#   Pin 6  XTAL1:       (129.54, 96.52)    -- left side
#   Pin 7  XTAL2:       (129.54, 99.06)    -- left side
#   Pin 8  VDD:         (129.54, 101.60)   -- left side
#   Pin 9  I2C/SPI:     (129.54, 104.14)   -- left side
#   Pin 10 A0/#CS:      (129.54, 106.68)   -- left side
#   Pin 11 A1/SI:       (129.54, 109.22)   -- left side
#   Pin 12 N.C./SO:     (129.54, 111.76)   -- left side
#   Pin 13 SCL/SCLK:    (129.54, 114.30)   -- left side
#   Pin 14 SDA/VSS:     (129.54, 116.84)   -- left side
#   Pin 15 IRQ#:        (170.18, 116.84)   -- right side
#   Pin 16 CTSB#:       (170.18, 114.30)   -- right side
#   Pin 17 RTSB#:       (170.18, 111.76)   -- right side
#   Pin 18 GPIO0:       (170.18, 109.22)   -- right side
#   Pin 19 GPIO1:       (170.18, 106.68)   -- right side
#   Pin 20 GPIO2:       (170.18, 104.14)   -- right side
#   Pin 21 GPIO3:       (170.18, 101.60)   -- right side
#   Pin 22 VSS:         (170.18, 99.06)    -- right side
#   Pin 23 TXB:         (170.18, 96.52)    -- right side
#   Pin 24 RXB:         (170.18, 93.98)    -- right side
#   Pin 25 GPIO4:       (170.18, 91.44)    -- right side
#   Pin 26 GPIO5:       (170.18, 88.90)    -- right side
#   Pin 27 GPIO6:       (170.18, 86.36)    -- right side
#   Pin 28 GPIO7:       (170.18, 83.82)    -- right side
#
# X1 at (119.38, 96.52), angle=0:
#   Pin 1 OSC1:  (111.76, 99.06)   -- left
#   Pin 2 GND:   (126.99, 99.06)   -- right (NOTE: rounded from 127.000015)
#   Pin 3 OSC2:  (126.99, 93.98)   -- right
#   Pin 4 GND:   (111.76, 93.98)   -- left
#
# C1 at (114.30, 91.44), angle=270 (vertical, pin1 top):
#   Pin 1: (114.30, 86.36)   -- top
#   Pin 2: (114.30, 96.52)   -- bottom
#
# C2 at (124.46, 91.44), angle=270 (vertical, pin1 top):
#   Pin 1: (124.46, 86.36)   -- top
#   Pin 2: (124.46, 96.52)   -- bottom
#
# R1 at (119.38, 106.68), angle=0 (horizontal):
#   Pin 1: (114.30, 106.68)  -- left
#   Pin 2: (124.46, 106.68)  -- right
#
# R2 at (180.34, 116.84), angle=270 (vertical, pin1 top):
#   Pin 1: (180.34, 111.76)  -- top
#   Pin 2: (180.34, 121.92)  -- bottom
#
# C3 at (139.70, 109.22), angle=270 (vertical, pin1 top):
#   Pin 1: (139.70, 104.14)  -- top
#   Pin 2: (139.70, 114.30)  -- bottom


# =============================================================================
# 9. WIRING CONNECTIONS
# =============================================================================
# Each wire is listed as: from_point -> to_point
#
# --- Signal wires (ports to IC) ---
# TX port pin (121.92, 88.90)  -> U1.TXA (129.54, 88.90)        -- horizontal
# RX port pin (121.92, 91.44)  -> U1.RXA (129.54, 91.44)        -- horizontal
# SCL port pin (121.92, 114.30) -> U1.SCL (129.54, 114.30)      -- horizontal
# SDA port pin (121.92, 116.84) -> U1.SDA (129.54, 116.84)      -- horizontal
#
# --- Crystal wiring ---
# U1.XTAL1 (129.54, 96.52) -> (114.30, 96.52)                   -- horizontal left
#   junction at (114.30, 96.52) -- C1.pin2 connects here
# X1.OSC1 (111.76, 99.06) -> (114.30, 99.06)                    -- short horizontal
#   (114.30, 99.06) -> (114.30, 96.52)                           -- vertical up to junction
#
# U1.XTAL2 (129.54, 99.06) -> (124.46, 99.06)                   -- horizontal left
#   junction at (124.46, 99.06) -- connects to X1 and C2
# X1.OSC2 (126.99, 93.98) -> (124.46, 93.98)                    -- short horizontal
#   (124.46, 93.98) -> (124.46, 99.06)                           -- vertical down to junction
# C2.pin2 (124.46, 96.52) -> (124.46, 99.06)                    -- vertical down to junction
#
# X1.GND pin 4 (111.76, 93.98) -> GND via short wire
# X1.GND pin 2 (126.99, 99.06) -> already on XTAL2 net? No, GND pad.
#   Actually crystal GND pads (pins 2, 4) should go to GND.
#   (111.76, 93.98) -> (111.76, 96.52)   -- vertical to GND below
#   (126.99, 99.06) -> (126.99, 101.60)  -- vertical to GND below
#
# --- Power wiring ---
# U1.VDD (129.54, 101.60) -> (139.70, 101.60)                   -- horizontal right
#   junction at (139.70, 101.60)
#   (139.70, 101.60) -> (139.70, 104.14) -> C3.pin1             -- vertical
#   (139.70, 101.60) -> (149.86, 101.60)                        -- to +3.3V above
#   Actually: +3.3V at (149.86, 88.90) -> (149.86, 101.60) vertical down
#   Then (149.86, 101.60) -> (129.54, 101.60) horizontal to VDD pin
#
# U1.VSS (170.18, 99.06) -> GND (170.18, 119.38)               -- vertical down
#
# I2C mode: U1.I2C/SPI (129.54, 104.14) -> wire to +3.3V rail
#   (129.54, 104.14) -> (139.70, 104.14)                        -- junction with C3 top
#
# A0 pin: U1.A0 (129.54, 106.68) -> GND symbol at right
# A1 pin: U1.A1 (129.54, 109.22) -> GND symbol at right
#
# --- Reset pull-up ---
# U1.#RESET (129.54, 93.98) -> (114.30, 93.98)                  -- horizontal left
#   (114.30, 93.98) -> R1.pin1 (114.30, 106.68)                 -- vertical down
#   R1.pin2 (124.46, 106.68) -> +3.3V above
#   Actually, let me re-route: R1 horizontal near reset pin
#
# --- IRQ pull-up ---
# U1.IRQ# (170.18, 116.84) -> R2.pin1 (180.34, 111.76) via L-route
#   (170.18, 116.84) -> (180.34, 116.84)                        -- horizontal right
#   (180.34, 116.84) -> R2.pin2 (180.34, 121.92)                -- wait, pin2 is bottom
#   Actually R2 at angle=270: pin1 top (180.34, 111.76), pin2 bottom (180.34, 121.92)
#   So: (170.18, 116.84) -> (180.34, 116.84) -> junction
#   (180.34, 116.84) -> (180.34, 111.76) vertical up to R2.pin1? No...
#   Let me reconsider R2 placement.
#
# NOTE: Exact wiring will be refined during build script creation and
# human review in KiCad. The above is the first-pass wiring intent.


# =============================================================================
# 10. VERIFICATION CHECKLIST
# =============================================================================
# [ ] U1.TXA (pin 3) connected to TX port
# [ ] U1.RXA (pin 4) connected to RX port
# [ ] U1.SCL (pin 13) connected to SCL port
# [ ] U1.SDA (pin 14) connected to SDA port
# [ ] U1.VDD (pin 8) connected to +3.3V power symbol
# [ ] U1.VSS (pin 22) connected to GND power symbol
# [ ] U1.I2C/SPI (pin 9) connected to +3.3V (I2C mode)
# [ ] U1.A0 (pin 10) connected to GND
# [ ] U1.A1 (pin 11) connected to GND
# [ ] U1.#RESET (pin 5) -> R1 (10k) -> +3.3V
# [ ] U1.IRQ# (pin 15) -> R2 (1k) -> +3.3V
# [ ] U1.XTAL1 (pin 6) -> X1.OSC1 (pin 1) + C1.pin1
# [ ] U1.XTAL2 (pin 7) -> X1.OSC2 (pin 3) + C2.pin1
# [ ] C1.pin2 -> GND
# [ ] C2.pin2 -> GND
# [ ] C3.pin1 -> +3.3V (or VDD net), C3.pin2 -> GND
# [ ] X1 GND pins (2, 4) -> GND
# [ ] No-connect flags on pins: 1, 2, 12, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 28
# [ ] All pin numbers hidden on passives and crystal
# [ ] SCL/SDA/TX/RX render as diamond-shaped port labels
# [ ] All component values match BOM table
# [ ] Crystal is 14.7456MHz (for exact standard baud rates)
# [ ] R3 (1M) bridges XTAL1 and XTAL2 nets (feedback resistor)


# =============================================================================
# 11. OPTIONAL ENHANCEMENTS (not in current design)
# =============================================================================
# 1. IRQ port: Expose U1.IRQ# as a port for interrupt-driven comms.
#    Route to an ESP32 GPIO for FIFO threshold / error interrupts.
#
# 2. Channel B: Add TXB/RXB ports for second UART channel.
#    Useful for dual-servo bus or debug serial.
#
# 3. GPIO ports: Expose GPIO0-7 as ports for LED/switch control.
#    Replaces the PI7C9X760's GPIO functionality from EV4 design.
#
# 4. RS-485: Add RS-485 transceiver on Channel A for half-duplex
#    servo comms (like the EV4 design with U20 transceiver).
#
# 5. Address jumpers: Add 0R resistors or solder jumpers on A0/A1
#    for field-configurable I2C address.

# END OF TEMPLATE
