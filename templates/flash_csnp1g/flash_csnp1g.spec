# =============================================================================
# TEMPLATE: CSNP1GCR01-BOW 1Gbit NAND Flash (SPI Mode)
# =============================================================================
# Prerequisites: Read templates/TemplateCreation.spec FIRST for universal rules.
# This file covers ONLY circuit-specific details for the flash template.
#
# Template Version: 1.0
# Date: March 2026
# Status: Locked — human-reviewed, wiring verified in KiCad


# =============================================================================
# 1. OVERVIEW
# =============================================================================
# 1Gbit NAND flash memory (CSNP1GCR01-BOW) operated in SPI mode.
# Provides 128MB of non-volatile storage for audio files, data logging, etc.
# SPI interface: CS, CLK, MOSI (CMD), MISO (DO). DAT1/DAT2 unused in SPI mode.
# Replaces the originally-planned W25Q128JVS (same SPI interface, more storage).


# =============================================================================
# 2. INTERFACE (what the parent schematic connects to)
# =============================================================================
# Type          | Name      | Shape           | Notes
# --------------|-----------|-----------------|-------------------------------
# Port symbol   | CS_SD     | Ports:CS_SD     | SPI chip select (active low)
# Port symbol   | SD_CLK    | Ports:SD_CLK    | SPI clock
# Port symbol   | SD_MOSI   | Ports:SD_MOSI   | SPI data in (CMD pin)
# Port symbol   | SD_MISO   | Ports:SD_MISO   | SPI data out (SDD0 pin)
# Power symbol  | +3.3V     | power:+3.3V     | Global — auto-connects across sheets
# Power symbol  | GND       | power:GND       | Global — auto-connects across sheets
#
# Signal names match the reference design (EV4-PDS) for ESP32 GPIO mapping.


# =============================================================================
# 3. DESIGN NOTES (circuit-specific decisions)
# =============================================================================
# - SDD2 (pin 1): Unused in SPI mode — no-connect flag
# - SDD1 (pin 7): Unused in SPI mode — no-connect flag
# - CD/SDD3 (pin 2): Functions as CS (chip select) in SPI mode
# - CMD (pin 5): Functions as MOSI (data in) in SPI mode
# - SDD0 (pin 6): Functions as MISO (data out) in SPI mode
# - Two decoupling caps on VCC: 1uF bulk + 100nF bypass (per reference design)
# - Operating voltage: 2.7V to 3.6V (3.3V rail)
# - Max SPI clock: 50MHz
# - Package: LGA-8 (6x8mm)


# =============================================================================
# 4. INTERNAL NETS (stay inside this sheet — NOT exposed)
# =============================================================================
# Net Name    | Path
# ------------|----------------------------------------------------
# (SDD2)      | Mem1.pin1 → no-connect
# (SDD1)      | Mem1.pin7 → no-connect


# =============================================================================
# 5. COMPONENTS — ALL FROM JLCPCB
# =============================================================================

# [Mem1] CSNP1GCR01-BOW — 1Gbit NAND Flash
#   LCSC:      C2691593
#   Symbol:    JLCImport:CSNP1GCR01-BOW
#   Package:   LGA-8 (6x8mm)
#   JLCPCB:    Extended part
#   VCC Range: 2.7V to 3.6V
#   SPI Clock: Up to 50MHz
#   Pin assignments:
#     Pin 1 SDD2     → NC (no-connect, unused in SPI mode)
#     Pin 2 CD/SDD3  → CS_SD port (chip select)
#     Pin 3 SCLK     → SD_CLK port (SPI clock)
#     Pin 4 VSS      → GND (power symbol)
#     Pin 5 CMD      → SD_MOSI port (SPI data in)
#     Pin 6 SDD0     → SD_MISO port (SPI data out)
#     Pin 7 SDD1     → NC (no-connect, unused in SPI mode)
#     Pin 8 VCC      → +3.3V (power symbol)
#   lib_symbol notes:
#     - Hide pin_numbers: YES
#     - Keep pin_names visible (SDD2, CD/SDD3, SCLK, etc. are useful)

# [C1] 1uF Capacitor — VCC bulk decoupling
#   LCSC:      C28323
#   Symbol:    JLCImport:CL21B105KBFNNNE
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 → +3.3V bus, Pin2 → GND
#   Note:      Bulk decoupling, place close to Mem1 VCC pin
#   lib_symbol notes:
#     - Hide pin_numbers AND pin_names

# [C3] 100nF Capacitor — VCC bypass decoupling
#   LCSC:      C49678
#   Symbol:    JLCImport:CC0805KRX7R9BB104
#   Package:   0805
#   JLCPCB:    Basic part
#   Nets:      Pin1 → +3.3V bus, Pin2 → GND
#   Note:      Bypass decoupling, place close to Mem1 VCC pin
#   lib_symbol notes:
#     - Hide pin_numbers AND pin_names


# =============================================================================
# 6. JLCPCB BOM SUMMARY
# =============================================================================
#
# Ref  | Part              | Value     | Pkg     | LCSC     | Type
# -----|-------------------|-----------|---------|----------|----------
# Mem1 | CSNP1GCR01-BOW    | 1Gbit     | LGA-8   | C2691593 | Extended
# C1   | Capacitor         | 1uF 50V   | 0805    | C28323   | Basic
# C3   | Capacitor         | 100nF 50V | 0805    | C49678   | Basic
#
# Total: 3 components (2 basic, 1 extended)
# JLCPCB extended part fee: ~$3/unique extended x 1 = ~$3 setup


# =============================================================================
# 7. SCHEMATIC LAYOUT — POSITIONS (all on 1.27mm grid)
# =============================================================================
# All coordinates in mm on A4 sheet, snapped to 1.27mm grid.
# Grid formula: snap(val) = round(round(val / 1.27) * 1.27, 2)
#
# Component    | Position (x, y)     | Angle | Notes
# -------------|---------------------|-------|----------------------------------
# Mem1 (Flash) | (149.86, 100.33)    | 0     | Center of sheet, IC body
# C1 (1uF)    | (175.26, 91.44)     | 270   | Vertical, pin1=top (VCC), pin2=bottom (GND)
# C3 (100nF)  | (182.88, 91.44)     | 270   | Vertical, pin1=top (VCC), pin2=bottom (GND)
#
# Port symbols (Ports library):
#   CS_SD      | (120.65, 99.06)     | 0     | Pin at (123.19, 99.06)
#   SD_CLK     | (120.65, 101.60)    | 0     | Pin at (123.19, 101.60)
#   SD_MOSI    | (180.34, 104.14)    | 180   | Pin at (177.80, 104.14)
#   SD_MISO    | (180.34, 101.60)    | 180   | Pin at (177.80, 101.60)
#
# Power symbols:
#   +3.3V      | (175.26, 82.55)     | 0     | Above VCC bus
#   GND #PWR02 | (135.89, 111.76)    | 0     | Below Mem1.VSS
#   GND #PWR03 | (175.26, 99.06)     | 0     | Below cap GND bus
#
# No-connects:
#   SDD2       | Mem1 pin 1 endpoint |       | Unused in SPI mode
#   SDD1       | Mem1 pin 7 endpoint |       | Unused in SPI mode


# =============================================================================
# 8. PIN ENDPOINTS (for wiring)
# =============================================================================
# Formula: schematic_pos = (sym_x + pin_local_x, sym_y - pin_local_y)
#
# Mem1 at (149.86, 100.33), angle=0:
#   Pin 1 SDD2:    (135.89, 96.52)   — left side
#   Pin 2 CD/SDD3: (135.89, 99.06)   — left side
#   Pin 3 SCLK:    (135.89, 101.60)  — left side
#   Pin 4 VSS:     (135.89, 104.14)  — left side
#   Pin 5 CMD:     (163.83, 104.14)  — right side
#   Pin 6 SDD0:    (163.83, 101.60)  — right side
#   Pin 7 SDD1:    (163.83, 99.06)   — right side
#   Pin 8 VCC:     (163.83, 96.52)   — right side
#
# C1 at (175.26, 91.44), angle=270 (vertical, pin1=top):
#   Pin 1: (175.26, 86.36)  — top (VCC bus)
#   Pin 2: (175.26, 96.52)  — bottom (GND bus)
#
# C3 at (182.88, 91.44), angle=270 (vertical, pin1=top):
#   Pin 1: (182.88, 86.36)  — top (VCC bus)
#   Pin 2: (182.88, 96.52)  — bottom (GND bus)


# =============================================================================
# 9. WIRING CONNECTIONS
# =============================================================================
# Each wire is listed as: from_point → to_point
#
# SPI signal wires:
#   CS_SD port pin (123.19, 99.06) → Mem1.CD/SDD3 (135.89, 99.06)    — horizontal
#   SD_CLK port pin (123.19, 101.60) → Mem1.SCLK (135.89, 101.60)    — horizontal
#   Mem1.CMD (163.83, 104.14) → SD_MOSI port pin (177.80, 104.14)    — horizontal
#   Mem1.SDD0 (163.83, 101.60) → SD_MISO port pin (177.80, 101.60)   — horizontal
#
# Power wires (VCC bus at y=86.36):
#   +3.3V (175.26, 82.55) → (175.26, 86.36)                          — vertical down
#   (175.26, 86.36) → (182.88, 86.36)                                — horizontal (cap bus)
#   (163.83, 86.36) → (175.26, 86.36)                                — horizontal (IC to bus)
#   Mem1.VCC (163.83, 96.52) → (163.83, 86.36)                       — vertical up
#
# Cap GND bus (y=96.52):
#   (175.26, 96.52) → (182.88, 96.52)                                — horizontal
#   (175.26, 96.52) → (175.26, 99.06)                                — vertical to GND symbol
#
# VSS ground:
#   Mem1.VSS (135.89, 104.14) → GND (135.89, 111.76)                 — vertical down
#
# Junctions:
#   (175.26, 86.36) — VCC bus T (IC wire + cap bus + +3.3V)
#   (175.26, 96.52) — Cap GND bus T (C1.pin2 + GND wire)


# =============================================================================
# 10. VERIFICATION CHECKLIST
# =============================================================================
# [x] Mem1.CD/SDD3 (pin 2) connected to CS_SD port
# [x] Mem1.SCLK (pin 3) connected to SD_CLK port
# [x] Mem1.CMD (pin 5) connected to SD_MOSI port
# [x] Mem1.SDD0 (pin 6) connected to SD_MISO port
# [x] Mem1.VCC (pin 8) connected to +3.3V via VCC bus
# [x] Mem1.VSS (pin 4) connected to GND
# [x] C1.pin1 and C3.pin1 connected to +3.3V bus
# [x] C1.pin2 and C3.pin2 connected to GND
# [x] Mem1.SDD2 (pin 1) has no-connect flag
# [x] Mem1.SDD1 (pin 7) has no-connect flag
# [x] All pin numbers hidden
# [x] All component values match BOM table
# [x] Schematic opens in KiCad 9.0 without errors

# END OF TEMPLATE
