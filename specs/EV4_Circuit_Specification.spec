# EV4 Lake Lifter Main Control Board — Complete Circuit Specification
# Source: DipTrace 5.1.0.3 schematic export (EV4-PDS)
# Reverse-engineered from: EV4-PDS.asc, EV4-PDS NETLIST.net, DC_EV4-PDS NETLIST.eli
# Date: March 2026
# Purpose: Full circuit spec for rebuilding in KiCad with JLCPCB components

# ==============================================================================
# SECTION 1: BOARD OVERVIEW
# ==============================================================================

Board Name:     Lake Lifter EV4 Main Control Board (PDS = Post Drive System)
Function:       Motorized boat lift controller with up/down/rotation via 24VAC contactors
MCU:            ESP32-WROOM-32E-N8R2 (WiFi + Bluetooth, 8MB Flash, 2MB PSRAM)
Power Input:    120/240VAC mains → 30W AC-DC module → 12VDC → 3.3V/5V DC-DC
Schematic:      4 pages (Main, Power Supply, IO, Panel IO)
Total Components: ~201 (per netlist comp entries)
Total Nets:     132

# Subsystems:
# A. Power Supply (AC-DC + dual DC-DC)
# B. ESP32 MCU + Reset/Boot
# C. I2C Bus (RTC + 3x IO Expanders)
# D. SD Card + NAND Flash (SDIO 4-bit)
# E. I2S Audio Amplifier (MAX98357A)
# F. RS-485 Transceiver (Modbus)
# G. 2.4GHz RF Receiver
# H. LED Driver (constant current)
# I. Relay Drivers (2x motor contactors)
# J. Panel IO (6 buttons + 6 LEDs)
# K. Limit Switches + Hall Sensor
# L. Buzzer
# M. Heartbeat LED + Status LEDs


# ==============================================================================
# SECTION 2: POWER SUPPLY
# ==============================================================================
# Page: Power Supply

## 2A. AC Input Protection
# AC mains → J21 (3-pos 5mm screw terminal: LINE, NEUTRAL, EARTH)
# Surge protection: MOV1 (MOV-14D471KTR) across LINE-NEUTRAL
# Inrush limiting: NTC1 (MF72-050D9) in series with LINE
# Earth ground: J21 pin 3 → chassis screw (Screw1)

[Component] MOV1
  Part:       MOV-14D471KTR
  Type:       Metal Oxide Varistor
  Rating:     470V clamping
  Package:    14mm radial
  Function:   AC surge protection (Line to Neutral)
  Nets:       Pin1→LINE_IN, Pin2→NEUTRAL_IN

[Component] NTC1
  Part:       MF72-050D9
  Type:       NTC Inrush Current Limiter
  Rating:     5 ohm cold, 9mm
  Package:    Through-hole radial
  Function:   Inrush current limiting on AC input
  Nets:       Pin1→LINE_IN (from J21), Pin2→LINE_IN_SUPPLY (to U3)

[Component] J21
  Part:       395210003
  Type:       3-position screw terminal (5.0mm pitch)
  Function:   AC mains input connector
  Nets:       Pin1→LINE_IN, Pin2→NEUTRAL_IN, Pin3→GND_EARTH

## 2B. AC-DC Module (12V)

[Component] U3
  Part:       IRM-30-12
  Manufacturer: Mean Well
  Type:       Enclosed AC-DC module
  Rating:     30W, 120/240VAC input, 12VDC 2.5A output
  Package:    IRM-30-12 (PCB mount module)
  Function:   Main AC to 12V DC conversion
  Nets:       AC/L→LINE_IN_SUPPLY, AC/N→NEUTRAL_IN, V+→+12V, V-→GND

## 2C. DC-DC Converter: 12V → 3.3V

[Component] U5
  Part:       LMZM23601SILR
  Manufacturer: Texas Instruments
  LCSC:       (needs JLCPCB equivalent)
  Type:       Integrated DC-DC step-down power module
  Rating:     1A output, 4-36V input
  Package:    SIL0010A (8-pin module)
  Function:   12V to 3.3V main logic rail
  Feedback:   R31 (10k) / R32 (4.22k) → Vout = 1.0V × (1 + 10k/4.22k) = 3.37V
  Note:       Netlist exported 4.7k but PDF schematic (Rev A_2) shows 4.22k — PDF is authoritative
  Note:       Fed through D8 (Schottky) from +12V for reverse protection
  Input Caps: C11 (680uF 35V electrolytic), C34 (10uF 35V ceramic 1210)
  Output Caps: C35 (47uF 16V 1210)
  Nets:       VIN→(D8 output), EN→(D8 output), VOUT→+3.3VDC, GND→GND

[Component] D8
  Part:       PMEG6030EVPX
  Manufacturer: Nexperia
  Type:       Schottky barrier diode
  Rating:     60V, 3A
  Package:    SOD-128 (CFP5)
  Function:   Reverse polarity protection on 12V input to U5
  Nets:       A→+12V, K→U5.VIN

[Component] R31
  Value:      10.0k 1%
  Package:    0805
  Function:   U5 feedback divider (top)
  Nets:       Pin1→+3.3VDC, Pin2→U5.FB

[Component] R32
  Value:      4.7k 1%
  Package:    0805
  Function:   U5 feedback divider (bottom)
  Nets:       Pin1→U5.FB, Pin2→GND

## 2D. DC-DC Converter: 12V → 5V

[Component] U6
  Part:       LMZM23601SILR
  Manufacturer: Texas Instruments
  Type:       Integrated DC-DC step-down power module
  Rating:     1A output, 4-36V input
  Package:    SIL0010A (8-pin module)
  Function:   12V to 5V for audio amp, field sensors, panel IO
  Feedback:   R3 (10k) / R4 (2.49k) → Vout = 1.0V × (1 + 10k/2.49k) = 5.02V
  Input Caps: C31 (10uF 35V 1210), C33 (10uF 35V 1210)
  Output Caps: C32 (47uF 16V 1210)
  Nets:       VIN→+12V, EN→+12V, VOUT→+5VDC, GND→GND

[Component] R3
  Value:      10.0k 1%
  Package:    0805
  Function:   U6 feedback divider (top)
  Nets:       Pin1→+5VDC, Pin2→U6.FB

[Component] R4
  Value:      2.49k 1%
  Package:    0805
  Function:   U6 feedback divider (bottom)
  Nets:       Pin1→U6.FB, Pin2→GND

## 2E. 12V Monitoring (ADC)

[Component] R9
  Value:      100.0k 1%
  Package:    0805
  Function:   12V voltage divider (top)
  Nets:       Pin1→+12V, Pin2→BATT_V1

[Component] R10
  Value:      12.0k 1%
  Package:    0805
  Function:   12V voltage divider (bottom, to GND via R25)
  Nets:       Pin1→BATT_V1, Pin2→GND

[Component] R25
  Value:      10.0k 1%
  Package:    0805
  Function:   12V ADC filter/divider (midpoint to ESP32)
  Nets:       Pin1→BATT_V1, Pin2→+12V_Mon

[Component] C30
  Value:      0.1uF 50V
  Package:    0805
  Function:   ADC filter capacitor
  Nets:       Pin1→+12V_Mon, Pin2→GND

# ADC Voltage divider: Vmon = 12V × (12k/(100k+12k)) = 1.286V at 12V input
# ESP32 ADC range: 0-3.3V → measures 0-30.8V range
# Connected to: ESP32 IO36 (input-only, SVP)

## 2F. Power Rails Summary

# +12V Rail (from U3 IRM-30-12): ~16 connections
#   → K2, K4 relay coils
#   → U7 LED driver VIN
#   → U6 DC-DC input (→ 5V)
#   → D8 → U5 DC-DC input (→ 3.3V)
#   → J5, J18 RS-485 bus power
#   → R9 voltage divider (ADC monitoring)

# +3.3VDC Rail (from U5): ~55 connections
#   → U1 ESP32
#   → U2, U4, U15 I2C-UART bridges
#   → U8 RTC
#   → U9 voltage supervisor
#   → U11 RF receiver
#   → U20 RS-485 transceiver
#   → Mem1 NAND flash
#   → J1 SD card, J9 panel header, J10 I2C header
#   → X1-X3 oscillators, Y1 crystal load
#   → I2C pull-ups, LED series R, buzzer

# +5VDC Rail (from U6): ~10 connections
#   → U10 MAX98357A audio amp
#   → J13, J17 sensor headers (limit switches, hall)
#   → R6 ~SD_MODE pull-up

# Bulk Decoupling (per rail):
#   +12V: C31 (10uF), C33 (10uF), C23 (10uF), C25 (0.1uF)
#   +3.3V: C1(1uF), C3,C4,C6,C7,C12,C15,C28,C29,C36-C39,C55 (0.1uF each), C58(10uF)
#   Note: C10 is on VBACKUP net (not +3.3V), C59 is on Enable net (not +3.3V)
#   +5V: C2(0.1uF), C5(10uF), C32(47uF)

[Component] C6
  Value:      10,000pF (10nF) 50V
  Package:    0805
  Function:   +3.3V rail decoupling (Main page)
  Nets:       Pin1→+3.3VDC, Pin2→GND

[Component] C7
  Value:      1000pF (1nF) 50V
  Package:    0805
  Function:   +3.3V rail decoupling (Main page)
  Nets:       Pin1→+3.3VDC, Pin2→GND

[Component] C12
  Value:      1.0uF 50V
  Package:    0805
  Function:   +3.3V rail bulk decoupling
  Nets:       Pin1→+3.3VDC, Pin2→GND


# ==============================================================================
# SECTION 3: ESP32 MCU + RESET/BOOT
# ==============================================================================
# Page: Main

[Component] U1
  Part:       ESP32-WROOM-32E-N8R2
  Manufacturer: Espressif Systems
  Type:       WiFi + Bluetooth module
  Flash:      8MB
  PSRAM:      2MB
  Package:    ESP-WROOM-32 (18x25.5mm module)
  Power:      +3.3VDC
  Function:   Main MCU — controls all subsystems

## 3A. ESP32 GPIO Assignment Table

# Pin | GPIO  | Net Name        | Function              | Direction
# ----|-------|-----------------|----------------------|----------
#  3  | EN    | Enable          | Reset (TLV803S)      | Input
#  4  | IO36  | +12V_Mon        | ADC 12V monitoring   | ADC Input (input-only)
#  5  | IO39  | 2.4G_DATA       | RF data from YXW6552E| Digital Input (input-only)
#  6  | IO34  | SD_MISO         | SDIO DAT0            | SDIO (input-only)
#  8  | IO32  | Rotation        | Rotation relay Q3    | Digital Output
#  9  | IO33  | Motor_EN        | Motor relay Q4       | Digital Output
# 10  | IO25  | PWM_LED         | LED dimming          | PWM Output
# 11  | IO26  | ~CS_SD          | SDIO CS/DAT3         | SDIO
# 12  | IO27  | LRCLK           | I2S L/R clock        | I2S Output
# 13  | IO14  | SD_CLK          | SDIO clock           | SDIO
# 14  | IO12  | BCLK            | I2S bit clock        | I2S Output
# 16  | IO13  | SD_MOSI         | SDIO CMD             | SDIO
# 24  | IO2   | HB_LED          | Heartbeat LED Q6     | Digital Output
# 25  | IO0   | IO0             | Boot mode / JTAG     | Special (strapping)
# 26  | IO4   | Hall_IO         | Hall sensor input    | Digital Input
# 30  | IO18  | DIN             | I2S data out         | I2S Output
# 31  | IO19  | Upper_Limit_IO  | Upper limit switch   | Digital Input
# 33  | IO21  | Lower_Limit_IO  | Lower limit switch   | Digital Input
# 34  | RXD0  | RX0             | UART0 RX debug       | UART Input
# 35  | TXD0  | TX0             | UART0 TX debug       | UART Output
# 36  | IO22  | SDA             | I2C data             | I2C
# 37  | IO23  | SCL             | I2C clock            | I2C

# Unused GPIOs: IO5, IO15, IO16, IO17, IO35
# Strapping pins: IO0(Pull-Up), IO2(Pull-Down), IO12(Pull-Down), IO15(Pull-Up), IO5(Pull-Up)

## 3B. Reset Circuit

[Component] U9
  Part:       TLV803S
  Manufacturer: Texas Instruments
  Type:       Voltage supervisor / reset IC
  Threshold:  Various (select correct suffix)
  Package:    SOT-23
  Function:   Power-on-reset for ESP32 EN pin
  Nets:       VDD→+3.3VDC, ~RESET→Enable, GND→GND

[Component] R16
  Value:      10.0k 1%
  Package:    0805
  Function:   EN pull-up resistor
  Nets:       Pin1→+3.3VDC, Pin2→Enable

[Component] C59
  Value:      0.1uF 50V
  Package:    0805
  Function:   EN pin filter capacitor
  Nets:       Pin1→Enable, Pin2→GND

## 3C. JTAG / Debug Header

[Component] J2
  Part:       M52-5010845 (PPTC081LFBN-RC)
  Type:       8-pin 1.27mm pitch header (JTAG)
  Function:   Debug/programming header
  Pinout:
    Pin 1: GND
    Pin 2: Enable (EN)
    Pin 3: IO0 (boot select)
    Pin 4: TX0
    Pin 5: RX0
    Pin 6: GND
    Pin 7: GND
    Pin 8: +3.3VDC


# ==============================================================================
# SECTION 4: I2C BUS
# ==============================================================================
# Page: Main

# I2C Bus: SCL (IO23), SDA (IO22)
# Pull-ups: R17 (4.7k to 3.3V), R18 (4.7k to 3.3V)
# Bus speed: Standard/Fast (100/400 kHz)

[Component] R17
  Value:      4.7k 1%
  Package:    0805
  Function:   I2C SCL pull-up
  Nets:       Pin1→+3.3VDC, Pin2→SCL

[Component] R18
  Value:      4.7k 1%
  Package:    0805
  Function:   I2C SDA pull-up
  Nets:       Pin1→+3.3VDC, Pin2→SDA

# I2C External Header
[Component] J10
  Part:       PPTC041LFBN-RC
  Type:       4-pin 2.54mm header
  Function:   External I2C access
  Pinout:     Pin1→+3.3VDC, Pin2→SCL, Pin3→SDA, Pin4→GND

## 4A. I2C Device Address Map
# Address | Device         | RefDes
# --------|----------------|-------
# 0x4A    | PI7C9X760CZDEX | U15 (A0=GND, A1=GND)
# 0x4C    | PI7C9X760CZDEX | U2  (A0=VDD, A1=GND)
# 0x4D    | PI7C9X760CZDEX | U4  (A0=VDD, A1=VDD)
# 0x52    | RV-3028-C7     | U8  (fixed address)

## 4B. RV-3028-C7 Real-Time Clock

[Component] U8
  Part:       RV-3028-C7
  Manufacturer: Micro Crystal AG
  LCSC:       C3019759
  Type:       Ultra-low-power I2C RTC
  Package:    SON-8 (1.5x3.2mm)
  I2C Addr:   0x52 (fixed)
  Function:   Timekeeping with battery backup
  Nets:
    SCL (pin 3) → SCL
    SDA (pin 4) → SDA
    VDD (pin 7) → +3.3VDC
    VBACKUP (pin 6) → B3 coin cell (via R46 1k)
    VSS (pin 5) → GND
    EVI (pin 8) → R41 (10k pull-down to GND)
    CLKOUT (pin 1) → NC
    ~INT (pin 2) → NC (note: "Disconnect INT from SDA / was milled on rev C")

[Component] C10
  Value:      0.1uF 50V
  Package:    0805
  Function:   U8 VBACKUP decoupling
  Nets:       Pin1→Net_7 (U8.VBACKUP), Pin2→GND

[Component] B3
  Part:       BR-1225/HCN
  Manufacturer: Panasonic
  Type:       Coin cell battery holder (BR-1225)
  Function:   RTC backup battery
  Nets:       POS→R46→U8.VBACKUP, NEG→GND

[Component] R46
  Value:      1.0k 1%
  Package:    0805
  Function:   Battery current limiting to RTC VBACKUP
  Nets:       Pin1→U8.VBACKUP, Pin2→B3.POS

[Component] R41
  Value:      10.0k 1%
  Package:    0805
  Function:   EVI pull-down (unused event input)
  Nets:       Pin1→U8.EVI, Pin2→GND

## 4C. PI7C9X760CZDEX I2C-to-UART/GPIO Bridge (x3)

[Component] U2
  Part:       PI7C9X760CZDEX
  Manufacturer: Diodes Incorporated
  Type:       I2C to UART + GPIO bridge
  Package:    QFN-25 (4x4mm)
  I2C Addr:   0x4C (A0=VDD, A1=GND)
  Clock:      X2 (24MHz oscillator)
  Function:   Panel IO bridge #1 — Down/Stop/Up buttons & LEDs
  GPIO Map:
    GPIO0 → Down_SW_IO (button input)
    GPIO1 → Down_LED_IO (LED output via Q8)
    GPIO2 → Stop_SW_IO (button input)
    GPIO3 → Stop_LED_IO (LED output via Q9)
    GPIO4/~DSR → Up_SW_IO (button input)
    GPIO5/~DTR → Up_LED_IO (LED output via Q10)
    GPIO6/~CD → U2_IO6 (spare, on J7 header)
    GPIO7/~RI → U2_IO7 (spare, on J7 header)
    ~IRQ → R59 (1k pull-up to 3.3V)
  Nets:       SCL→SCL, SDA→SDA, VDD→+3.3VDC, GND→GND

[Component] U15
  Part:       PI7C9X760CZDEX
  Manufacturer: Diodes Incorporated
  Type:       I2C to UART + GPIO bridge
  Package:    QFN-25 (4x4mm)
  I2C Addr:   0x4A (A0=GND, A1=GND)
  Clock:      X1 (24MHz oscillator)
  Function:   Panel IO bridge #2 — AutoRun/Light/Menu buttons & LEDs + RS-485 UART + Buzzer
  UART:       TX→TX1 (to U20.D), RX→RX1 (from U20.R), ~RTS→DIR (RS-485 direction)
  GPIO Map:
    GPIO0 → Auto_Run_SW_IO (button input)
    GPIO1 → Auto_Run_LED_IO (LED output via Q1)
    GPIO2 → Light_SW_IO (button input)
    GPIO3 → Light_LED_IO (LED output via Q2)
    GPIO4/~DSR → Menu_SW_IO (button input)
    GPIO5/~DTR → Menu_LED_IO (LED output via Q5)
    GPIO6/~CD → U15_IO6 → Buzzer drive (via J4.P1, R69, Q7)
    GPIO7/~RI → U15_IO7 (spare, on J4.P2)
    ~IRQ → R5 (1k pull-up to 3.3V)
  Nets:       SCL→SCL, SDA→SDA, VDD→+3.3VDC, GND→GND

[Component] U4
  Part:       PI7C9X760CZDEX
  Manufacturer: Diodes Incorporated
  Type:       I2C to UART + GPIO bridge
  Package:    QFN-25 (4x4mm)
  I2C Addr:   0x4D (A0=VDD, A1=VDD)
  Clock:      X3 (24MHz oscillator)
  Function:   DIP switch address config + spare GPIOs
  GPIO Map:
    GPIO0 → SW1 pos 1 (Mode_1's, R63 10k pull-down)
    GPIO1 → SW1 pos 2 (Mode_2's, R64 10k pull-down)
    GPIO2 → SW1 pos 4 (Mode_4's, R65 10k pull-down)
    GPIO3 → SW1 pos 8 (Mode_8's, R66 10k pull-down)
    GPIO4/~DSR → U4_IO4 (spare, on J11.P1)
    GPIO5/~DTR → U4_IO5 (spare, on J11.P2)
    GPIO6/~CD → U4_IO6 (spare, on J11.P3)
    GPIO7/~RI → U4_IO7 (spare, on J11.P4)
    ~IRQ → R62 (1k pull-up to 3.3V)
  Nets:       SCL→SCL, SDA→SDA, VDD→+3.3VDC, GND→GND

# Each PI7C9X760CZDEX requires:
#   - 24MHz oscillator (ECS-2520MV-240-BL-TR)
#   - 0.1uF decoupling cap on VDD
#   - 1k pull-up on ~IRQ
#   - Address pins tied to VDD or GND as needed

[Component] X1
  Part:       ECS-2520MV-240-BL-TR
  Type:       24MHz MEMS oscillator
  Package:    2520 (2.5x2.0mm)
  Function:   Clock for U15
  Nets:       OUT→U15.XTAL1, VDD→+3.3VDC, GND→GND

[Component] X2
  Part:       ECS-2520MV-240-BL-TR
  Type:       24MHz MEMS oscillator
  Package:    2520 (2.5x2.0mm)
  Function:   Clock for U2
  Nets:       OUT→U2.XTAL1, VDD→+3.3VDC, GND→GND

[Component] X3
  Part:       ECS-2520MV-240-BL-TR
  Type:       24MHz MEMS oscillator
  Package:    2520 (2.5x2.0mm)
  Function:   Clock for U4
  Nets:       OUT→U4.XTAL1, VDD→+3.3VDC, GND→GND

[Component] SW1
  Part:       SH-7010TA
  Type:       DIP switch (4-position)
  Package:    SH-700 series
  Function:   Functional mode selection (read by U4 GPIO0-3)
  Nets:       Pos1→Mode_1's, Pos2→Mode_2's, Pos4→Mode_4's, Pos8→Mode_8's


# ==============================================================================
# SECTION 5: SD CARD + NAND FLASH (SDIO 4-BIT)
# ==============================================================================
# Page: Main

# SDIO Bus (shared between SD card and NAND flash):
#   SD_CLK (IO14), SD_MOSI/CMD (IO13), SD_MISO/DAT0 (IO34), ~CS_SD/DAT3 (IO26)

[Component] J1
  Part:       DM3AT-SF-PEJM5
  Manufacturer: Hirose
  Type:       Micro-SD card connector
  Package:    DM3AT (push-push, SMD)
  Function:   Removable SD card storage
  Nets:
    CLK → SD_CLK (IO14)
    CMD → SD_MOSI (IO13)
    DAT0 → SD_MISO (IO34)
    DAT3/CD → ~CS_SD (IO26)
    VDD → +3.3VDC
    VSS → GND

[Component] Mem1
  Part:       CSNP1GCR01-BOW
  Manufacturer: Creat Storage World
  Type:       1Gbit (128MB) NAND Flash
  Package:    BGA/custom (csnp1gcr01-bow)
  Function:   Onboard persistent storage (shares SDIO bus with SD card)
  Nets:
    CLK → SD_CLK
    CMD → SD_MOSI
    DO/DAT0 → SD_MISO
    CS/DAT3 → ~CS_SD
    DAT1 → (test point only)
    DAT2 → (test point only)
    VDD → +3.3VDC
    GND → GND


# ==============================================================================
# SECTION 6: I2S AUDIO AMPLIFIER (MAX98357A)
# ==============================================================================
# Page: IO

[Component] U10
  Part:       MAX98357AETE+T
  Manufacturer: Analog Devices / Maxim
  LCSC:       C910544
  Type:       I2S mono DAC + Class D amplifier
  Rating:     3.2W into 4 ohm at 5V
  Package:    TQFN-16 (3x3mm)
  Power:      +5VDC (pins 7, 8)
  Function:   Audio playback from ESP32 I2S
  Configuration:
    Gain:     R7 (100k) to GND → 15dB
    Channel:  R6 (1.0M) to +5V → L/2 + R/2 (mono mix)
    SD_MODE:  R6 also serves as ~SD_MODE pull-up → always enabled
  Nets:
    BCLK (pin 16) → BCLK (ESP32 IO12)
    LRCLK (pin 14) → LRCLK (ESP32 IO27)
    DIN (pin 1) → DIN (ESP32 IO18)
    VDD (pins 7,8) → +5VDC
    GND (pins 3,11,15) → GND
    PAD (pin 17) → GND
    GAIN_SLOT (pin 2) → R7 → GND
    ~SD_MODE (pin 4) → R6 → +5VDC
    OUTP (pin 9) → Speaker_(+) → J19.P2
    OUTN (pin 10) → Speaker_(-) → J19.P1

[Component] R6
  Value:      1.0M 1%
  Package:    0805
  Function:   MAX98357A channel select (L/2+R/2 mono) + SD_MODE pull-up
  Nets:       Pin1→+5VDC, Pin2→~SD_MODE

[Component] R7
  Value:      100.0k 1%
  Package:    0805
  Function:   MAX98357A gain select (15dB)
  Nets:       Pin1→GND, Pin2→GAIN_SLOT

[Component] C5
  Value:      10uF 25V
  Package:    0805
  Function:   U10 VDD bulk decoupling
  Nets:       Pin1→+5VDC, Pin2→GND

[Component] C2
  Value:      0.1uF 50V
  Package:    0805
  Function:   U10 VDD bypass
  Nets:       Pin1→+5VDC, Pin2→GND

[Component] R12
  Value:      10.0k 1%
  Package:    0805
  Function:   BCLK pull-down resistor (keeps line low when idle)
  Nets:       Pin1→BCLK, Pin2→GND

[Component] J19
  Part:       395111002
  Type:       2-position screw terminal (3.81mm pitch)
  Function:   Speaker output connector
  Nets:       Pin1→Speaker_(-), Pin2→Speaker_(+)

# Speaker spec: 38.8uH @ 4kHz, 4.6 ohm, 3 Watt


# ==============================================================================
# SECTION 7: RS-485 TRANSCEIVER (MODBUS)
# ==============================================================================
# Page: Main

[Component] U20
  Part:       SN65HVD72D
  Manufacturer: Texas Instruments
  Type:       RS-485/RS-422 transceiver (half-duplex)
  Package:    SOIC-8
  Power:      +3.3VDC
  Function:   Modbus RS-485 communication (via U15 UART, NOT direct ESP32)
  Nets:
    D (driver input) → TX1 (from U15.TX)
    R (receiver output) → RX1 (to U15.RX)
    DE (driver enable) → DIR (from U15.~RTS)
    ~RE (receiver enable) → DIR (tied to DE for half-duplex)
    A → R56 (10 ohm) → A bus
    B → R57 (10 ohm) → B bus
    VCC → +3.3VDC
    GND → GND

# RS-485 Bus Protection:
[Component] D10
  Part:       SM712
  Type:       Bidirectional TVS diode (asymmetric)
  Package:    SOT-23
  Function:   ESD protection on RS-485 A/B lines
  Nets:       I/O1→B, I/O2→A, GND→GND

[Component] R56
  Value:      10.0 1%
  Package:    0805
  Function:   RS-485 A line series resistor
  Nets:       Pin1→U20.A, Pin2→A bus

[Component] R57
  Value:      10.0 1%
  Package:    0805
  Function:   RS-485 B line series resistor
  Nets:       Pin1→U20.B, Pin2→B bus

[Component] R58
  Value:      120.0 1%
  Package:    0805
  Function:   RS-485 bus termination resistor
  Nets:       Pin1→A bus, Pin2→B bus

# RS-485 Connectors (daisy-chain capable):
[Component] J5
  Part:       B4B-XH-A(LF)(SN)
  Manufacturer: JST
  Type:       4-pin JST-XH connector
  Function:   RS-485 bus connector #1
  Pinout:     Pin1→A, Pin2→B, Pin3→+12V, Pin4→GND

[Component] J18
  Part:       395111004
  Type:       4-position screw terminal (3.81mm pitch)
  Function:   RS-485 bus connector #2 (Modbus/Encoder)
  Pinout:     Pin1→A, Pin2→B, Pin3→+12V, Pin4→GND


# ==============================================================================
# SECTION 8: 2.4GHz RF RECEIVER
# ==============================================================================
# Page: Main

[Component] U11
  Part:       YXW6552E-RX
  Type:       2.4GHz wireless receiver module
  Package:    Custom (YXW6552E-RX)
  Power:      +3.3VDC
  Function:   Wireless remote control receiver (OOK/ASK or FSK)
  Crystal:    Y1 (16MHz, ECS-160-S-23A-EN-TR) with C8/C9 (36pF load caps)
  Nets:
    ANT → J3 (SMA antenna connector)
    B4 (DATA) → 2.4G_DATA → ESP32 IO39 (input-only)
    B3 (LED) → R14 (510) → D1 (LED indicator)
    X1 → Y1 crystal pin 1 (with C9 36pF to GND)
    X2 → Y1 crystal pin 2 (with C8 36pF + R11 510 to GND)
    VDD → +3.3VDC
    GND → GND

[Component] J3
  Part:       BWSMA-KE-Z001
  Type:       SMA edge-mount antenna connector
  Function:   2.4GHz antenna connection

[Component] Y1
  Part:       ECS-160-S-23A-EN-TR
  Type:       16MHz crystal (4-pin SMD)
  Package:    HC49/US (1.6x5.0mm)
  Function:   RF receiver clock source
  Load Caps:  C8=36pF, C9=36pF


# ==============================================================================
# SECTION 9: LED DRIVER (CONSTANT CURRENT)
# ==============================================================================
# Page: IO

[Component] U7
  Part:       TPS92200D2DDCR
  Manufacturer: Texas Instruments
  Type:       Constant-current LED driver (buck topology)
  Package:    SOT-23-6
  Input:      +12V
  Function:   External LED lighting control with PWM dimming
  Nets:
    VIN → +12V
    SW → L6 pin 1 (switch node)
    BOOT → C22 (bootstrap cap)
    DIM → R24 → PWM_LED (from ESP32 IO25)
    FB → R22 → LED- (current sense feedback)
    GND → GND

[Component] L6
  Part:       7440650047
  Manufacturer: Wurth Elektronik
  Value:      4.7uH, 4.6A
  Package:    Custom (7440650047)
  Function:   Buck inductor for LED driver

[Component] C22
  Value:      0.1uF 50V
  Package:    0805
  Function:   Bootstrap capacitor for U7
  Nets:       Pin1→LED_BOOT (U7.BOOT), Pin2→SW_LED (U7.SW)

[Component] R24
  Value:      1.0k 1%
  Package:    0805
  Function:   PWM dimming signal conditioning
  Nets:       Pin1→PWM_LED (ESP32 IO25), Pin2→DIM_LED (U7.DIM)

[Component] R20
  Value:      0.1 ohm 1% 0.5W
  Package:    1206
  Function:   Current sense resistor #1
  Nets:       Pin1→LED-, Pin2→R21

[Component] R21
  Value:      0.1 ohm 1% 0.5W
  Package:    1206
  Function:   Current sense resistor #2 (parallel with R20)
  Nets:       Pin1→R20.Pin2, Pin2→GND

[Component] R22
  Value:      1.0k 1%
  Package:    0805
  Function:   Current feedback to U7.FB
  Nets:       Pin1→LED-, Pin2→U7.FB

# R20 || R21 = 0.05 ohm total sense resistance
# LED current = V_FB / R_sense

[Component] D6
  Part:       SMBJ33A
  LCSC:       C353366
  Type:       TVS diode (33V unidirectional)
  Package:    SMB (DO-214AA)
  Function:   Output clamping / overvoltage protection on LED+
  Nets:       A→GND, K→LED+

[Component] D7
  Part:       PMEG6030EVPX
  Type:       Schottky diode
  Rating:     60V, 3A
  Function:   Output rectification / reverse blocking
  Nets:       A→LED+, K→LED+_Out

[Component] C13
  Value:      10.0uF 35V
  Package:    1206
  Function:   LED output filter cap
  Nets:       Pin1→LED+, Pin2→GND

[Component] C16
  Value:      0.1uF 50V
  Package:    0805
  Function:   LED output bypass
  Nets:       Pin1→LED+, Pin2→GND

[Component] J20
  Part:       395111002
  Type:       2-position screw terminal (3.81mm pitch)
  Function:   LED output connector
  Nets:       Pin1→LED+_Out, Pin2→LED-


# ==============================================================================
# SECTION 10: RELAY DRIVERS (MOTOR CONTACTORS)
# ==============================================================================
# Page: IO

# Two identical relay circuits control 24VAC motor contactors:
#   K2 = Motor Enable (Up/Down)
#   K4 = Rotation Direction
# Each relay driven by SQ2318AES N-MOSFET through coil resistor

## 10A. Motor Enable Relay (K2)

[Component] K2
  Part:       AGQ200A12Z (TE 1-1462039-8 / 2-1462037-3)
  Manufacturer: TE Connectivity
  Type:       Signal relay (DPDT, SMT)
  Coil:       12V
  Contact:    2A max
  Package:    RELAY8_SMTGUL_TE (8-pin SMD)
  Function:   Motor contactor enable (switches 24VAC)
  Nets:
    Pin 1 → +12V (coil power)
    Pin 8 → R13 → Q4.D (coil drive)
    Pin 2,7 → NC contacts (tied together, unused)
    Pin 3,6 → NO contacts → Contactor_Motor_EN → J16.P1
    Pin 4,5 → 24_VAC_Line (common — incoming 24VAC)

[Component] Q4
  Part:       SQ2318AES
  Manufacturer: Vishay
  Type:       N-Channel MOSFET
  Package:    SOT-23 (GSD pinout)
  Rating:     20V, 3.4A
  Function:   K2 relay coil low-side driver
  Nets:       G→Motor_EN (via R2 10k), D→R13→K2.8, S→GND

[Component] R2
  Value:      10.0k 1%
  Package:    0805
  Function:   Q4 gate pull-down (prevents float during boot)
  Nets:       Pin1→Motor_EN, Pin2→GND

[Component] R13
  Value:      360 ohm
  Package:    1206
  Function:   K2 coil current limiting (12V/360 = 33mA coil current)
  Nets:       Pin1→Q4.D, Pin2→K2.Pin8

[Component] D3
  Part:       1N4448W-TP
  Type:       Signal diode (flyback protection)
  Package:    SOD-123
  Function:   Flyback diode across K2 coil
  Nets:       A→K2.Pin8 (coil−), K→+12V (coil+)

[Component] D12
  Part:       DIO_0805_N (green LED)
  Package:    0805
  Function:   Motor enable status LED
  Nets:       A→Motor_EN (via series R), K→GND

## 10B. Rotation Relay (K4) — identical topology

[Component] K4
  Part:       AGQ200A12Z (TE 1-1462039-8 / 2-1462037-3)
  Type:       Signal relay (DPDT, SMT)
  Function:   Rotation direction contactor (switches 24VAC)
  Nets:
    Pin 1 → +12V
    Pin 8 → R15 → Q3.D
    Pin 2,7 → NC contacts (tied together, unused)
    Pin 3,6 → NO contacts → Contactor_Rotation → J15.P1
    Pin 4,5 → 24_VAC_Line

[Component] Q3
  Part:       SQ2318AES
  Type:       N-Channel MOSFET, SOT-23
  Function:   K4 relay coil low-side driver
  Nets:       G→Rotation (via R1 10k), D→R15→K4.8, S→GND

[Component] R1
  Value:      10.0k 1%
  Package:    0805
  Function:   Q3 gate pull-down
  Nets:       Pin1→Rotation, Pin2→GND

[Component] R15
  Value:      360 ohm
  Package:    1206
  Function:   K4 coil current limiting
  Nets:       Pin1→Q3.D, Pin2→K4.Pin8

[Component] D2
  Part:       1N4448W-TP
  Package:    SOD-123
  Function:   Flyback diode across K4 coil
  Nets:       A→K4.Pin8, K→+12V

[Component] D13
  Part:       DIO_0805_N (green LED)
  Package:    0805
  Function:   Rotation status LED

## 10C. 24VAC Contactor Circuit

[Component] PTC1
  Part:       SMDC300F/24-2
  Type:       Resettable PTC fuse
  Rating:     3A hold, 24V
  Package:    2920
  Function:   24VAC input protection
  Nets:       Pin1→24_VAC_Line_IN (from J6.P1), Pin2→24_VAC_Line

[Component] J6
  Part:       395111002
  Type:       2-position screw terminal (3.81mm pitch)
  Function:   24VAC input connector
  Nets:       Pin1→24_VAC_Line_IN, Pin2→24VAC_N

[Component] J15
  Part:       395111002
  Type:       2-position screw terminal (3.81mm pitch)
  Function:   Rotation contactor output
  Nets:       Pin1→Contactor_Rotation, Pin2→24VAC_N

[Component] J16
  Part:       395111002
  Type:       2-position screw terminal (3.81mm pitch)
  Function:   Motor contactor output
  Nets:       Pin1→Contactor_Motor_EN, Pin2→24VAC_N

# Note: 24VAC contactor coil inrush up to 5A on start (unverified)
# Note: K2/K4 are DPDT relays with both NO contacts wired in parallel for current handling


# ==============================================================================
# SECTION 11: PANEL IO (6 BUTTONS + 6 LEDs)
# ==============================================================================
# Page: Panel IO

# All panel IO goes through 13-pin header J9 to membrane panel switch
# LEDs driven by SQ2318AES N-MOSFETs (low-side switching)
# Buttons read through GPIO expanders U2 and U15

[Component] J9
  Part:       PPTC131LFBN-RC
  Type:       13-pin 2.54mm header
  Function:   Front panel membrane switch interface
  Pinout:
    Pin 1:  +3.3VDC (power to panel LEDs)
    Pin 2:  Menu_LED
    Pin 3:  Menu_SW
    Pin 4:  Light_LED
    Pin 5:  Light_SW
    Pin 6:  Auto_Run_LED
    Pin 7:  Auto_Run_SW
    Pin 8:  Up_LED
    Pin 9:  Up_SW
    Pin 10: Stop_LED
    Pin 11: Stop_SW
    Pin 12: Down_LED
    Pin 13: Down_SW

## Panel Button Input Circuit (repeating pattern, 6 instances):
# J9 pin (button) → 1k pull-down R to GND (R35,R37,R39 for Down/Stop/Up; R36,R38,R40 for AutoRun/Light/Menu)
#   Junction → IO_Expander_GPIO (SW_IO net)
#   Junction → 0.1uF cap to GND (debounce filter)
# Button pressed → pulls GPIO low through 1k to GND; released → floats high via expander internal pull-up

## Panel LED Output Circuit (repeating pattern, 6 instances):
# IO_Expander_GPIO → 1k gate series R → SQ2318AES Gate
#   10k gate pull-down R: Gate → GND (prevents float during boot)
#   SQ2318AES Drain → 1k drain-to-J9 series R → J9 pin (to LED anode, cathode at 3.3V through panel)
#   SQ2318AES Source → GND

# Button/LED MOSFET Assignment:
# Q1:  Auto_Run_LED (via U15.GPIO1)
# Q2:  Light_LED (via U15.GPIO3)
# Q5:  Menu_LED (via U15.GPIO5)
# Q8:  Down_LED (via U2.GPIO1)
# Q9:  Stop_LED (via U2.GPIO3)
# Q10: Up_LED (via U2.GPIO5)

# Panel Resistor Values:
# Button pull-down (1k to GND):  R35,R36,R37,R38,R39,R40
# LED gate series (1k):          R42,R44,R48,R50,R52,R54
# LED gate pull-down (10k):      (shared with gate series pattern, 10k to GND)
# LED drain series (1k to J9):   R43,R45,R49,R51,R53,R55
# Button debounce filter:        0.1uF caps (C18-C21, C26-C27)


# ==============================================================================
# SECTION 12: LIMIT SWITCHES + HALL SENSOR
# ==============================================================================
# Page: IO

## 12A. Upper Limit Switch

[Component] R19
  Value:      1.0k 1%
  Package:    0805
  Function:   Upper limit series resistor
  Nets:       Pin1→Upper_Limit (J13.P2), Pin2→Upper_Limit_IO

[Component] R61
  Value:      10.0k 1%
  Package:    0805
  Function:   Upper limit pull-up
  Nets:       Pin1→Upper_Limit_IO, Pin2→+3.3VDC

[Component] D5
  Part:       ESD7351HT1G
  Type:       ESD protection diode
  Package:    SOD-323
  Function:   Upper limit ESD protection
  Nets:       K→Upper_Limit_IO, A→GND

[Component] C14
  Value:      1000pF 50V
  Package:    0805
  Function:   Upper limit filter cap
  Nets:       Pin1→Upper_Limit_IO, Pin2→GND

# Upper_Limit_IO → ESP32 IO19

## 12B. Lower Limit Switch

[Component] R23
  Value:      1.0k 1%
  Package:    0805
  Function:   Lower limit series resistor
  Nets:       Pin1→Lower_Limit (J13.P3), Pin2→Lower_Limit_IO

[Component] R60
  Value:      10.0k 1%
  Package:    0805
  Function:   Lower limit pull-up
  Nets:       Pin1→Lower_Limit_IO, Pin2→+3.3VDC

[Component] D9
  Part:       ESD7351HT1G
  Type:       ESD protection diode
  Package:    SOD-323
  Function:   Lower limit ESD protection
  Nets:       K→Lower_Limit_IO, A→GND

[Component] C17
  Value:      1000pF 50V
  Package:    0805
  Function:   Lower limit filter cap
  Nets:       Pin1→Lower_Limit_IO, Pin2→GND

# Lower_Limit_IO → ESP32 IO21

[Component] J13
  Part:       395111003
  Type:       3-position screw terminal (3.81mm pitch)
  Function:   Limit switch connector
  Nets:       Pin1→+5VDC, Pin2→Upper_Limit, Pin3→Lower_Limit

## 12C. Hall/Proximity Sensor

[Component] R8
  Value:      100.0k 1%
  Package:    0805
  Function:   Hall sensor pull-up
  Nets:       Pin1→+3.3VDC, Pin2→Hall

[Component] R27
  Value:      1.0k 1%
  Package:    0805
  Function:   Hall sensor series resistor
  Nets:       Pin1→Hall, Pin2→Hall_IO

[Component] D4
  Part:       ESD7351HT1G
  Type:       ESD protection diode
  Package:    SOD-323
  Function:   Hall sensor ESD protection
  Nets:       K→Hall_IO, A→GND

[Component] C24
  Value:      1000pF 50V
  Package:    0805
  Function:   Hall sensor filter cap
  Nets:       Pin1→Hall_IO, Pin2→GND

# Hall_IO → ESP32 IO4

[Component] J17
  Part:       395111003
  Type:       3-position screw terminal (3.81mm pitch)
  Function:   Hall/proximity sensor connector
  Nets:       Pin1→+5VDC, Pin2→Hall, Pin3→GND


# ==============================================================================
# SECTION 13: BUZZER
# ==============================================================================
# Page: IO

[Component] BZ1
  Part:       CI12E-07T230-C-6
  Type:       Piezo buzzer (driven, with oscillator)
  Package:    12mm round
  Function:   Audio alert / beeper
  Power:      +3.3VDC
  Nets:       V+→+3.3VDC, GND→Q7.D (low-side switched)

[Component] Q7
  Part:       SQ2318AES
  Type:       N-Channel MOSFET, SOT-23
  Function:   Buzzer low-side driver
  Nets:       G→R47→U15_IO6, D→BZ1.GND, S→GND

[Component] R47
  Value:      10.0k 1%
  Package:    0805
  Function:   Q7 gate pull-down
  Nets:       Pin1→Q7.G, Pin2→GND

[Component] R69
  Value:      1.0k 1%
  Package:    0805
  Function:   Q7 gate series resistor
  Nets:       Pin1→U15_IO6 (via J4.P1), Pin2→Q7.G


# ==============================================================================
# SECTION 14: HEARTBEAT LED + STATUS INDICATORS
# ==============================================================================
# Page: Main/IO

[Component] Q6
  Part:       SQ2318AES
  Type:       N-Channel MOSFET, SOT-23
  Function:   Heartbeat LED driver (on ESP32 IO2)
  Nets:       G→HB_LED (R67 10k gate pull-down), D→LED circuit, S→GND

[Component] R67
  Value:      10.0k 1%
  Package:    0805
  Function:   Q6 gate pull-down
  Nets:       Pin1→HB_LED (IO2), Pin2→GND

[Component] R68
  Value:      1k 1%
  Package:    0805
  Function:   Q6 gate series resistor

[Component] D1
  Part:       LTST-C171GKT (or WP483IDT)
  Type:       Green LED
  Package:    0805
  Function:   Power/heartbeat indicator
  Nets:       Via series resistor to +3.3V, switched by Q6

[Component] D11
  Part:       DIO_0805_N
  Type:       Green LED
  Package:    0805
  Function:   Status indicator (on Main page)

[Component] D12
  Part:       Green_LED_0805
  Type:       Green LED
  Package:    0805
  Function:   Motor Enable status LED (IO page)
  Nets:       A→Motor_EN (ESP32 IO33), K→R70→GND

[Component] D13
  Part:       Green_LED_0805
  Type:       Green LED
  Package:    0805
  Function:   Rotation status LED (IO page)
  Nets:       A→Rotation (ESP32 IO32), K→R71→GND

[Component] R70
  Value:      1k 1%
  Package:    0805
  Function:   D12 (Motor_EN LED) cathode current limiting resistor
  Nets:       Pin1→D12.K (Net_132), Pin2→GND

[Component] R71
  Value:      1k 1%
  Package:    0805
  Function:   D13 (Rotation LED) cathode current limiting resistor
  Nets:       Pin1→D13.K (Net_131), Pin2→GND


# ==============================================================================
# SECTION 15: MISCELLANEOUS COMPONENTS
# ==============================================================================

## 15A. Spare GPIO Headers

[Component] J4
  Part:       PPTC021LFBN-RC
  Type:       2-pin 2.54mm header
  Function:   U15 spare GPIO access (buzzer + spare)
  Nets:       Pin1→U15_IO6, Pin2→U15_IO7

[Component] J7
  Part:       PPTC021LFBN-RC
  Type:       2-pin 2.54mm header
  Function:   U2 spare GPIO access
  Nets:       Pin1→U2_IO6, Pin2→U2_IO7

[Component] J11
  Part:       PPTC041LFBN-RC
  Type:       4-pin 2.54mm header
  Function:   U4 spare GPIO access
  Nets:       Pin1→U4_IO4, Pin2→U4_IO5, Pin3→U4_IO6, Pin4→U4_IO7

## 15B. Fiducials and Mounting

[Component] Fid1
  Part:       Fiducial 2.0mm RD
  Type:       Round fiducial marker

[Component] Fid2
  Part:       Fiducial 2.0mm SQ
  Type:       Square fiducial marker

[Component] Screw1-Screw6
  Part:       97349A411 (McMaster-Carr)
  Type:       #2 18-8 stainless 1/4" screws
  Function:   PCB mounting holes (M3)
  Package:    M3_MTGP650H350V6H50

## 15C. Test Points
# CLK, CMD, CS, D0, DAT1, DAT2 — SDIO bus test points
# EN, IO0 — Boot/reset test points
# RX, TX — UART0 debug test points
# A1, B1 — RS-485 bus test points (2.75mm pads)


# ==============================================================================
# SECTION 16: KNOWN LCSC PART NUMBERS (from ELI file)
# ==============================================================================

# The following LCSC part numbers were extracted from the DipTrace ELI library:
# C233436  — (component TBD, needs cross-reference)
# C353366  — SMBJ33A TVS diode (D6)
# C908219  — (component TBD)
# C496549  — (component TBD)
# C144395  — (component TBD)
# C563800  — (component TBD)
# C2691593 — (component TBD)

# Note: Most components in the original design did NOT have LCSC numbers.
# All components need JLCPCB-equivalent sourcing.


# ==============================================================================
# SECTION 17: JLCPCB COMPONENT REPLACEMENT TABLE
# ==============================================================================
# Status: TO BE FILLED — match each component to JLCPCB in-stock part

# RefDes | Original Part          | JLCPCB Equivalent | LCSC #  | Status
# -------|------------------------|--------------------|---------|---------
# U1     | ESP32-WROOM-32E-N8R2   |                   |         | FIND
# U2,4,15| PI7C9X760CZDEX         |                   |         | FIND
# U3     | IRM-30-12              |                   |         | FIND
# U5,U6  | LMZM23601SILR          |                   |         | FIND
# U7     | TPS92200D2DDCR         |                   |         | FIND
# U8     | RV-3028-C7             | RV-3028-C7        | C3019759| MATCHED
# U9     | TLV803S                |                   |         | FIND
# U10    | MAX98357AETE+T         | MAX98357AETE+T    | C910544 | MATCHED
# U11    | YXW6552E-RX            |                   |         | FIND
# U20    | SN65HVD72D             |                   |         | FIND
# Mem1   | CSNP1GCR01-BOW         |                   |         | FIND
# K2,K4  | AGQ200A12Z             |                   |         | FIND
# Q1-Q10 | SQ2318AES              |                   |         | FIND
# D2,D3  | 1N4448W-TP             |                   |         | FIND
# D4,5,9 | ESD7351HT1G            |                   |         | FIND
# D6     | SMBJ33A                |                   | C353366 | MATCHED
# D7,D8  | PMEG6030EVPX           |                   |         | FIND
# D10    | SM712                  |                   |         | FIND
# X1-X3  | ECS-2520MV-240-BL-TR   |                   |         | FIND
# Y1     | ECS-160-S-23A-EN-TR    |                   |         | FIND
# L6     | 7440650047 (4.7uH)     |                   |         | FIND
# BZ1    | CI12E-07T230-C-6       |                   |         | FIND
# B3     | BR-1225/HCN            |                   |         | FIND
# MOV1   | MOV-14D471KTR          |                   |         | FIND
# NTC1   | MF72-050D9             |                   |         | FIND
# PTC1   | SMDC300F/24-2          |                   |         | FIND
# SW1    | SH-7010TA              |                   |         | FIND
# J1     | DM3AT-SF-PEJM5         |                   |         | FIND
# J2     | M52-5010845            |                   |         | FIND
# J3     | BWSMA-KE-Z001          |                   |         | FIND
# J5     | B4B-XH-A(LF)(SN)      |                   |         | FIND
# Connectors (395111002/3/4)      |                   |         | FIND
# J21    | 395210003              |                   |         | FIND
# J9     | PPTC131LFBN-RC         |                   |         | FIND
# All R  | 0805 1% (various)      | Generic 0805      |         | STANDARD
# All C  | 0805/1206/1210         | Generic            |         | STANDARD


# ==============================================================================
# SECTION 18: DESIGN NOTES (FROM SCHEMATIC ANNOTATIONS)
# ==============================================================================

# Page 0 (Main):
# - "PSRam Reserved" — IO16/IO17 reserved for PSRAM (don't use)
# - "Strapping Pin: GPIO0:Pull-Up, GPIO2:Pull-Down, GPIO12:Pull-Down, GPIO15:Pull-Up, GPIO5:Pull-Up"
# - "Disconnect INT from SDA / was milled on rev C Production" — RTC INT bug fix
# - "make holes 0.7 from 0.65 for female header"

# Page 1 (Power Supply):
# - "Observed: +5.05Vdc" / "Observed: +3.?Vdc" — measured values
# - "Consider using a Type 1 SPD / Such as the 1220 series Bourns / maybe a gas discharge tube"
# - "Monitor Loss of Power to save positions"
# - "Add connector for 24vac — VHR Series 3.96mm spacing"
# - "Break solenoid drives up into two 2-pin connectors"

# Page 2 (IO):
# - "Current Speaker Characteristic: 38.8uH @4kHz 4.6 Ohm 3 Watt"
# - "D6 SMBJ12A to clamp LED output for protection" (note: actual part is SMBJ33A)
# - "24vac Contactor Coil inrush up to 5A on start (Unverified)"
# - "Consider a connector for each contactor instead of combined"
# - "Line Length ? 25'? / maybe 12v better"
# - "Should Limit Current — 12v Modbus power"
# - "Should Limit Current — 5vdc rotary power"
# - "Should Limit Current — 5v Hall/Prox power"
# - "Gauge size after measuring current on coil of contactor"

# Page 3 (Panel IO):
# - "Add header for easy access to SDA SCL 3.3/5 GND and open IO Expander Pins"


# ==============================================================================
# SECTION 19: SUBSYSTEM EXTRACTION GUIDE
# ==============================================================================
# Use this section to identify which components belong to each subsystem
# when rebuilding individual sections in KiCad.

# SUBSYSTEM A: Power Supply (AC-DC + DC-DC)
# Components: U3, U5, U6, D7, D8, MOV1, NTC1, J21, R3, R4, R9, R10, R25, R31, R32
# Caps: C6, C7, C11, C12, C30, C31, C32, C33, C34, C35
# Page: Power Supply

# SUBSYSTEM B: ESP32 MCU + Reset
# Components: U1, U9, J2, R16, C59
# Page: Main

# SUBSYSTEM C: I2C Bus + RTC
# Components: U8, B3, R17, R18, R41, R46, C10, J10
# Page: Main

# SUBSYSTEM D: I2C-UART Bridges (3x)
# Components: U2, U4, U15, X1, X2, X3, SW1, R5, R59, R62, R63-R66
# Caps: C3, C4, C15, C28, C29, C36-C39, C55
# Headers: J4, J7, J11
# Page: Main

# SUBSYSTEM E: SD Card + NAND Flash
# Components: J1, Mem1
# Page: Main

# SUBSYSTEM F: I2S Audio
# Components: U10, R6, R7, R12, C2, C5, J19
# Page: IO

# SUBSYSTEM G: RS-485 (Modbus)
# Components: U20, D10, R56, R57, R58, J5, J18
# Page: Main + IO

# SUBSYSTEM H: 2.4GHz RF Receiver
# Components: U11, Y1, J3, C8, C9, R11, R14, D1
# Page: Main

# SUBSYSTEM I: LED Driver
# Components: U7, L6, D6, D7, C13, C16, C22, R20, R21, R22, R24, J20
# Page: IO

# SUBSYSTEM J: Relay Drivers (2x motor contactors)
# Components: K2, K4, Q3, Q4, D2, D3, R1, R2, R13, R15, PTC1, J6, J15, J16
# Status LEDs: D12 (Motor_EN) + R70, D13 (Rotation) + R71
# Page: IO

# SUBSYSTEM K: Panel IO
# Components: J9, Q1, Q2, Q5, Q8, Q9, Q10
# Resistors: R26, R28-R30, R33-R55 (button/LED series, gate, pull-down)
# Caps: C18-C21, C26-C27
# Page: Panel IO

# SUBSYSTEM L: Limit Switches + Hall Sensor
# Components: D4, D5, D9, R8, R19, R23, R27, R60, R61, C14, C17, C24, J13, J17
# Page: IO

# SUBSYSTEM M: Buzzer
# Components: BZ1, Q7, R47, R69
# Page: IO

# SUBSYSTEM N: Heartbeat LED + Status LEDs
# Components: Q6, R67, R68, D1, D11, D12, D13, R70, R71
# Page: Main


# ==============================================================================
# SECTION 20: COMPONENT COUNT SUMMARY
# ==============================================================================

# Category              | Count | Packages
# ----------------------|-------|------------------
# ICs                   | 12    | Various (QFN, SOIC, SOT-23, module)
# Capacitors            | 44    | 0805 (×38), 1206 (×3), 1210 (×5), Electrolytic (×1)
# Resistors             | 71    | 0805 (×67), 1206 (×4)
# MOSFETs               | 10    | SOT-23 (all SQ2318AES)
# Diodes/LEDs/TVS       | 15    | SOD-123, SOD-323, SOT-23, SMB, 0805 (incl. D12, D13)
# Relays                | 2     | SMD 8-pin (AGQ200A12Z)
# Connectors            | 18    | Screw terminal, JST-XH, SMA, pin headers, SD card
# Inductors             | 1     | Custom (Wurth 7440650047)
# Crystals/Oscillators  | 4     | HC49 (×1), 2520 (×3)
# Protection            | 3     | MOV, NTC, PTC
# Misc                  | 10    | Buzzer, DIP switch, NAND flash, battery, fiducials, screws
# Test Points           | 12    | 1.5mm (×10), 2.75mm (×2)
# ----------------------|-------|
# TOTAL                 | ~201  | (per netlist comp entries)

# END OF SPECIFICATION
