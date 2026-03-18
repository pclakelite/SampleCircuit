# =============================================================================
# TEMPLATE: ESP32-S3-WROOM-1-N8R2 MCU Core
# =============================================================================
# Prerequisites: Read templates/TemplateCreation.spec FIRST for universal rules.
# This file covers ONLY circuit-specific details for the ESP32-S3 core template.
#
# Template Version: 1.0
# Date: March 2026
# Status: Draft
# Reference: AIreference/SCH_simple-blower-V1.0_1-P1_2025-12-20 (1).pdf


# =============================================================================
# 1. OVERVIEW
# =============================================================================
# Espressif ESP32-S3-WROOM-1-N8R2 module (8MB flash, 2MB PSRAM).
# Wi-Fi + Bluetooth LE SoC with dual-core Xtensa LX7 processor.
# 41-pin module (39 GPIO + GND + 3V3). Includes integrated antenna (2.4GHz).
#
# This template provides the MCU with:
#   - Power decoupling (100nF + 10uF on 3V3)
#   - EN pin connection (exposed as port for reset supervisor)
#   - All GPIO exposed as hierarchical ports for parent sheet routing
#   - USB D+/D- for native USB
#
# The crystal (X1 13.52127MHz in reference) is NOT included here -- the
# ESP32-S3-WROOM module has an internal crystal. X1 in the reference is
# likely for the SYN480R or other peripheral.


# =============================================================================
# 2. INTERFACE (what the parent schematic connects to)
# =============================================================================
# Type          | Name       | Shape            | Notes
# --------------|------------|------------------|-------------------------------
# Port symbol   | Enable     | Ports:Enable     | EN pin (connect to supervisor or RC reset)
# Port symbol   | TXD0       | Ports:TX         | UART0 TX (default serial)
# Port symbol   | RXD0       | Ports:RX         | UART0 RX (default serial)
# Port symbol   | UD+        | Ports:UD+        | USB D+ (GPIO20)
# Port symbol   | UD-        | Ports:UD-        | USB D- (GPIO19)
# Port symbol   | SCL        | Ports:SCL        | I2C clock (user-assigned GPIO)
# Port symbol   | SDA        | Ports:SDA        | I2C data (user-assigned GPIO)
# Port symbol   | DIN        | Ports:DIN        | I2S data (user-assigned GPIO)
# Port symbol   | BCLK       | Ports:BCLK       | I2S bit clock (user-assigned GPIO)
# Port symbol   | LRCLK      | Ports:LRCLK      | I2S word select (user-assigned GPIO)
# Port symbol   | SD_MISO    | Ports:SD_MISO    | SPI MISO (user-assigned GPIO)
# Port symbol   | SD_MOSI    | Ports:SD_MOSI    | SPI MOSI (user-assigned GPIO)
# Port symbol   | SD_CLK     | Ports:SD_CLK     | SPI clock (user-assigned GPIO)
# Port symbol   | CS_SD      | Ports:CS_SD      | SPI chip select (user-assigned GPIO)
# Port symbol   | KEY_ADC    | Ports:KEY_ADC    | ADC input for button ladder
# Port symbol   | DATA_433   | Ports:DATA_433   | 433MHz receiver data input
# Port symbol   | RS485_DE   | Ports:RS485_DE   | RS-485 direction enable (if using GPIO DE)
# Power symbol  | +3.3V      | power:+3.3V      | Global -- module supply
# Power symbol  | GND        | power:GND        | Global -- auto-connects across sheets
#
# GPIO pin assignments (from reference schematic, adjustable per project):
#   IO0  -> Available (boot mode strapping)
#   IO1  -> IO1 (reference: connected)
#   IO2  -> IO2 (reference: connected)
#   IO3  -> IO3
#   IO4  -> IO4
#   IO5  -> IO5
#   IO6  -> IO6
#   IO7  -> IO7
#   IO8  -> IO8
#   IO9  -> IO9
#   IO10 -> IO10
#   IO11 -> IO11
#   IO12 -> IO12
#   IO13 -> IO13
#   IO14 -> IO14
#   IO15 -> IO15
#   IO16 -> IO16
#   IO17 -> IO17
#   IO18 -> IO18
#   IO19 -> UD- (USB)
#   IO20 -> IO20
#   IO21 -> UD+ (USB)
#   IO35 -> IO35
#   IO36 -> IO36
#   IO37 -> IO37
#   IO38 -> IO38
#   IO39 -> IO39
#   IO40 -> IO40
#   IO41 -> IO41
#   IO42 -> IO42
#   IO45 -> IO45 (strapping pin)
#   IO46 -> IO46 (strapping pin)
#   IO47 -> IO47
#   IO48 -> IO48
#   TXD0 -> TXD0 (UART0 TX, pin 37)
#   RXD0 -> RXD0 (UART0 RX, pin 36)
#
# NOTE: Not all GPIO need dedicated port symbols. Unused GPIO can be left
# as no-connect or grouped. The parent sheet maps ports to specific functions.


# =============================================================================
# 3. DESIGN NOTES (circuit-specific decisions from reference schematic)
# =============================================================================
# ESP32-S3-WROOM-1-N8R2 pin assignments (41-pin module):
#   Pin 1  GND   -> GND
#   Pin 2  3V3   -> +3.3V supply
#   Pin 3  EN    -> Enable port (active-high, must have RC or supervisor)
#   Pin 4-39     -> GPIO (see pin map above)
#   Pin 40 GND   -> GND
#   Pin 41 GND   -> GND (center pad)
#
# Power:
#   - +3.3V supply on pin 2 (3V3)
#   - Decoupling: 100nF close to pin + 10uF bulk
#   - GND on pins 1, 40, 41 (center pad)
#
# EN pin:
#   - Must be held HIGH for normal operation
#   - Connect to supervisor (TLV803S template) or RC delay circuit
#   - Reference does not show external RC -- relies on internal pull-up
#   - Exposed as "Enable" port for parent sheet connection
#
# Boot mode (IO0):
#   - HIGH or floating at reset = normal boot from flash
#   - LOW at reset = download mode (UART/USB programming)
#   - Default: leave floating (internal pull-up) for normal boot
#   - For production, may want pull-up resistor for reliability
#
# Strapping pins (IO45, IO46):
#   - IO45: VDD_SPI voltage select (default: 3.3V, leave floating)
#   - IO46: ROM message printing (default: print, leave floating)
#
# USB native:
#   - IO19 = USB D- , IO20 = USB D+ (directly from module)
#   - No external PHY needed -- built into ESP32-S3


# =============================================================================
# 4. INTERNAL NETS (stay inside this sheet -- NOT exposed)
# =============================================================================
# Net Name     | Path
# -------------|----------------------------------------------------
# VDD_LOCAL    | +3.3V -> C_bulk (10uF) -> C_bypass (100nF) -> U2.3V3 (pin 2)
# GND_NET      | U2.GND (pins 1, 40, 41) -> GND symbols


# =============================================================================
# 5. COMPONENTS -- ALL FROM JLCPCB
# =============================================================================

# [U2] ESP32-S3-WROOM-1-N8R2 -- Wi-Fi + BLE SoC Module
#   LCSC:      C2913206 (or search ESP32-S3-WROOM-1-N8R2)
#   Package:   Module (18x25.5x3.1mm)
#   JLCPCB:    Extended part
#   Flash:     8MB
#   PSRAM:     2MB (octal SPI)
#   Cores:     Dual-core Xtensa LX7 @ 240MHz
#   Wi-Fi:     802.11 b/g/n (2.4GHz)
#   BLE:       Bluetooth 5.0 LE
#   USB:       Native USB 1.1 (OTG)
#   GPIO:      36 programmable

# [C1] 10uF -- VDD bulk decoupling capacitor
#   LCSC:      C15850
#   Symbol:    JLCImport:CL21A106KAYNNNE
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> +3.3V, Pin2 -> GND

# [C2] 100nF -- VDD bypass decoupling capacitor
#   LCSC:      C49678
#   Symbol:    JLCImport:CC0805KRX7R9BB104
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> +3.3V, Pin2 -> GND


# =============================================================================
# 6. JLCPCB BOM SUMMARY
# =============================================================================
#
# Ref  | Part                     | Value    | Pkg     | LCSC     | Type
# -----|--------------------------|----------|---------|----------|----------
# U2   | ESP32-S3-WROOM-1-N8R2   | --       | Module  | C2913206 | Extended
# C1   | CL21A106KAYNNNE          | 10uF 25V | 0805    | C15850   | Basic
# C2   | CC0805KRX7R9BB104        | 100nF    | 0805    | C49678   | Basic
#
# Total: 3 components (2 basic, 1 extended)
# NOTE: This is a minimal core template. GPIO connections are on parent sheet.


# =============================================================================
# 7. VERIFICATION CHECKLIST
# =============================================================================
# [ ] +3.3V -> C1 (10uF) + C2 (100nF) -> U2.3V3 (pin 2)
# [ ] U2.GND (pins 1, 40, 41) -> GND
# [ ] U2.EN (pin 3) -> Enable port
# [ ] U2.TXD0 (pin 37) -> TX port
# [ ] U2.RXD0 (pin 36) -> RX port
# [ ] USB D+/D- (IO19/IO20) -> UD+/UD- ports
# [ ] All other GPIO exposed as ports or marked NC
# [ ] All positions on 1.27mm grid


# =============================================================================
# 8. GPIO ALLOCATION TABLE (from reference, for user mapping)
# =============================================================================
# Pin | GPIO  | Reference Function       | Port Name
# ----|-------|--------------------------|----------
# 27  | IO0   | (boot strapping)         | --
# 39  | IO1   | General GPIO             | --
# 38  | IO2   | General GPIO             | --
# 15  | IO3   | General GPIO             | --
# 4   | IO4   | General GPIO             | --
# 5   | IO5   | General GPIO             | --
# 6   | IO6   | General GPIO             | --
# 7   | IO7   | General GPIO             | --
# 12  | IO8   | General GPIO             | --
# 17  | IO9   | General GPIO             | --
# 18  | IO10  | General GPIO             | --
# 19  | IO11  | General GPIO             | --
# 20  | IO12  | General GPIO             | --
# 21  | IO13  | General GPIO             | --
# 22  | IO14  | General GPIO             | --
# 8   | IO15  | General GPIO             | --
# 9   | IO16  | General GPIO             | --
# 10  | IO17  | General GPIO             | --
# 11  | IO18  | General GPIO             | --
# 13  | IO19  | USB D- / UD-             | UD-
# 14  | IO20  | USB D+ / UD+             | UD+
# 23  | IO21  | General GPIO             | --
# 28  | IO35  | General GPIO             | --
# 29  | IO36  | General GPIO             | --
# 30  | IO37  | General GPIO             | --
# 31  | IO38  | General GPIO             | --
# 32  | IO39  | General GPIO             | --
# 33  | IO40  | General GPIO             | --
# 34  | IO41  | General GPIO             | --
# 35  | IO42  | General GPIO             | --
# 26  | IO45  | (VDD_SPI strapping)      | --
# 16  | IO46  | (ROM print strapping)    | --
# 24  | IO47  | General GPIO             | --
# 25  | IO48  | General GPIO             | --
# 37  | TXD0  | UART0 TX                 | TX
# 36  | RXD0  | UART0 RX                 | RX


# END OF TEMPLATE
