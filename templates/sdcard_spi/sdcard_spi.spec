# =============================================================================
# TEMPLATE: SPI-Mode Micro SD Card Interface
# =============================================================================
# Prerequisites: Read templates/TemplateCreation.spec FIRST for universal rules.
# This file covers ONLY circuit-specific details for the SD card template.
#
# Template Version: 1.0
# Date: March 2026
# Status: Draft
# Reference: AIreference/SCH_simple-blower-V1.0_1-P1_2025-12-20 (1).pdf


# =============================================================================
# 1. OVERVIEW
# =============================================================================
# Micro SD card socket in SPI mode for data logging or file storage.
# Uses 4 SPI signals (MISO, MOSI, CLK, CS). +3.3V power supply.
# Optional ESD protection diodes (D1, D2) on data lines.
#
# The SD card socket (U6 in reference) is an 8-pin micro SD connector.
# In SPI mode, only 4 of the 8 data pins are used; unused pins are NC.


# =============================================================================
# 2. INTERFACE (what the parent schematic connects to)
# =============================================================================
# Type          | Name      | Shape           | Notes
# --------------|-----------|-----------------|-------------------------------
# Port symbol   | SD_MISO   | Ports:SD_MISO   | SPI data out (from SD card)
# Port symbol   | SD_MOSI   | Ports:SD_MOSI   | SPI data in (to SD card)
# Port symbol   | SD_CLK    | Ports:SD_CLK    | SPI clock
# Port symbol   | CS_SD     | Ports:CS_SD     | Chip select (active low)
# Power symbol  | +3.3V     | power:+3.3V     | Global -- SD card power
# Power symbol  | GND       | power:GND       | Global -- auto-connects across sheets
#
# NOTE: Some port symbols may need to be created in Ports.kicad_sym.


# =============================================================================
# 3. DESIGN NOTES (circuit-specific decisions from reference schematic)
# =============================================================================
# Micro SD card pinout (SPI mode):
#   Pin 1 SDD2/NC  -> No-connect (DAT2, unused in SPI mode)
#   Pin 2 CD/SDD3  -> CS_SD (chip select in SPI mode, directly from reference)
#   Pin 3 SCLK     -> SD_CLK
#   Pin 4 VSS      -> GND
#   Pin 5 CMD      -> SD_MOSI (data in, CMD pin becomes MOSI in SPI mode)
#   Pin 6 SDD0     -> SD_MISO (data out, DAT0 pin becomes MISO in SPI mode)
#   Pin 7 SDD1/NC  -> No-connect (DAT1, unused in SPI mode)
#   Pin 8 VCC      -> +3.3V
#
# ESD protection: D1, D2 (reference shows on CS_SD and SD_MISO lines).
#   ESD diodes are optional for internal PCB-only connections.
#   Recommended if SD card is user-accessible (hot-plug ESD risk).
#
# Decoupling: C11 = 100nF on VCC (pin 8) close to socket.
#
# SD card voltage: 3.3V only. Do NOT connect to 5V.
# Max SPI clock: Typically 25MHz in SPI mode (50MHz for high-speed).


# =============================================================================
# 4. INTERNAL NETS (stay inside this sheet -- NOT exposed)
# =============================================================================
# Net Name     | Path
# -------------|----------------------------------------------------
# VCC_SD       | +3.3V -> C11 (100nF) -> U6.VCC (pin 8)
# CS_NET       | CS_SD port -> D2 (optional ESD) -> U6.CD/SDD3 (pin 2)
# MISO_NET     | U6.SDD0 (pin 6) -> D1 (optional ESD) -> SD_MISO port


# =============================================================================
# 5. COMPONENTS -- ALL FROM JLCPCB
# =============================================================================

# [U6] Micro SD Card Socket
#   LCSC:      C585354 (or search for micro SD card socket SMD push-push)
#   Package:   SMD micro SD socket (9-pin + shield tabs)
#   JLCPCB:    Extended part
#   Pin assignments: see section 3

# [C11] 100nF -- VCC decoupling capacitor
#   LCSC:      C49678
#   Symbol:    JLCImport:CC0805KRX7R9BB104
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 -> VCC (+3.3V), Pin2 -> GND

# [D1] ESD Protection Diode (optional, on MISO line)
#   LCSC:      C7420 (or search for PESD5V0S1BA / USBLC6-2SC6)
#   Package:   SOD-323 or SOT-23
#   JLCPCB:    Extended part
#   Nets:      Line -> SD_MISO, VCC -> +3.3V, GND -> GND
#   Note:      Optional -- omit if SD card is not user-accessible.

# [D2] ESD Protection Diode (optional, on CS line)
#   LCSC:      C7420
#   Package:   SOD-323 or SOT-23
#   JLCPCB:    Extended part
#   Nets:      Line -> CS_SD, VCC -> +3.3V, GND -> GND
#   Note:      Optional -- omit if SD card is not user-accessible.


# =============================================================================
# 6. JLCPCB BOM SUMMARY
# =============================================================================
#
# Ref  | Part              | Value     | Pkg      | LCSC     | Type
# -----|-------------------|-----------|----------|----------|----------
# U6   | Micro SD Socket   | --        | SMD      | C585354  | Extended
# C11  | CC0805KRX7R9BB104 | 100nF 50V | 0805     | C49678   | Basic
# D1   | ESD diode         | --        | SOD-323  | C7420    | Extended (optional)
# D2   | ESD diode         | --        | SOD-323  | C7420    | Extended (optional)
#
# Total: 2-4 components (1 basic, 1-3 extended)


# =============================================================================
# 7. VERIFICATION CHECKLIST
# =============================================================================
# [ ] +3.3V -> C11 (100nF) -> U6.VCC (pin 8)
# [ ] U6.VSS (pin 4) -> GND
# [ ] U6.CD/SDD3 (pin 2) -> CS_SD port
# [ ] U6.SCLK (pin 3) -> SD_CLK port
# [ ] U6.CMD (pin 5) -> SD_MOSI port
# [ ] U6.SDD0 (pin 6) -> SD_MISO port
# [ ] NC flags on pin 1 (SDD2) and pin 7 (SDD1)
# [ ] All positions on 1.27mm grid


# END OF TEMPLATE
