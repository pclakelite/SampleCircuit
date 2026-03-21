# JLCPCB Cost Audit — SampleCircuit

**Date:** 2026-03-21
**Board Rev:** master @ 0542059

## PCB Fabrication Parameters

| Parameter | Value | Cost Impact |
|---|---|---|
| Layers | 2 | Standard (cheapest) |
| Dimensions | 100 x 90 mm | Medium board, ~$5-7 for 5 pcs |
| Thickness | 1.6 mm | Standard (no surcharge) |
| Min trace width | 6 mil (0.15 mm) | Standard capability |
| Min drill | 0.7 mm | Standard |
| Via type | Through-hole only | Standard (no blind/buried) |
| Surface finish | HASL (default) | Free |
| Solder mask | Green (default) | Free |
| Copper weight | 1 oz (default) | Standard |

**Estimated PCB fab cost: ~$7 for 5 pcs** (no special process surcharges)

## BOM — Basic Parts (no extended fee)

| LCSC | Value | Qty | Unit Price | Subtotal |
|---|---|---|---|---|
| C49678 | 100nF 0805 MLCC | 6 | $0.0051 | $0.03 |
| C17414 | 10k 0805 resistor | 5 | $0.0024 | $0.01 |
| C2297 | Green LED 0805 | 4 | $0.0157 | $0.06 |
| C27834 | 5.1k 0805 resistor | 2 | $0.0024 | $0.005 |
| C28323 | 1uF 0805 MLCC | 2 | $0.0126 | $0.03 |
| C8678 | SS34 Schottky diode | 1 | $0.0295 | $0.03 |
| C15850 | 10uF 0805 MLCC | 1 | $0.0203 | $0.02 |
| C17513 | 1k 0805 resistor | 1 | $0.0025 | $0.003 |

**Basic parts subtotal: ~$0.19/board** (8 unique parts, 22 components)

## BOM — Extended Parts ($3 fee per unique part)

| LCSC | Value | Qty | Unit $ | Subtotal | Notes |
|---|---|---|---|---|---|
| C2685821 | LMZM23601SILR | 3 | $5.95 | $17.85 | TI DC-DC module — biggest cost driver |
| C2913202 | ESP32-S3-WROOM-1-N16R8 | 1 | $5.03 | $5.03 | WiFi/BLE module |
| C2691593 | CSNP1GCR01-BOW (1Gbit Flash) | 1 | $4.38 | $4.38 | NAND flash |
| C3019759 | RV-3028-C7 RTC | 1 | $2.19 | $2.19 | Real-time clock |
| C910588 | NS4168 audio amp | 1 | $0.72 | $0.72 | Class-D amp |
| C542257 | 680uF 35V electrolytic | 1 | $0.61 | $0.61 | Panasonic cap |
| C489223 | PMEG6030EVPX | 1 | $0.29 | $0.29 | Nexperia Schottky |
| C97973 | 10uF 35V 1210 MLCC | 7 | $0.22 | $1.56 | Murata cap |
| C162512 | 47uF 16V 1210 MLCC | 1 | $0.24 | $0.24 | Murata cap |
| C172351 | 47uF 16V 1206 MLCC | 1 | $0.21 | $0.21 | FH cap |
| C2686403 | TS665WS tactile switch | 2 | $0.10 | $0.21 | Boot + Reset |
| C8465 | WJ500V terminal block | 5 | $0.13 | $0.64 | Screw terminals |
| C132016 | TLV803SDBZR supervisor | 1 | $0.12 | $0.12 | Voltage monitor |
| C2765186 | USB-C 16pin connector | 1 | $0.06 | $0.06 | |
| C393941 | MicroSD card slot | 1 | $0.06 | $0.06 | |
| C70376 | CR1220 battery holder | 1 | $0.06 | $0.06 | |
| C89651 | SMBJ26CA TVS diode | 1 | $0.11 | $0.11 | |
| C2992088 | 100uF electrolytic | 1 | $0.02 | $0.02 | |
| C17407 | 100k 0805 resistor | 1 | $0.002 | $0.002 | **DISCONTINUED — swap needed** |
| C17436 | 110k 0805 resistor | 1 | $0.002 | $0.002 | |
| C17665 | 4.22k 0805 resistor | 3 | $0.002 | $0.006 | |
| C17673 | 4.7k 0805 resistor | 2 | $0.002 | $0.004 | |
| C21237 | 2.49k 0805 resistor | 1 | $0.002 | $0.002 | |
| C86211 | 47uF 25V cap | 1 | ~$0.20 | $0.20 | |

**Extended parts subtotal: ~$34.48/board** (24 unique extended parts)

## Cost Summary (per board, qty 5)

| Category | Cost |
|---|---|
| PCB fabrication (5 pcs) | ~$7 total (~$1.40/board) |
| Basic parts | $0.19 |
| Extended parts (components) | $34.48 |
| Extended parts fee (24 unique x $3) | **$72.00** |
| SMT assembly setup | ~$8.00 |
| SMT per-joint cost (~200 joints) | ~$3.50 |
| **Estimated total per board (qty 5)** | **~$118** |
| **Estimated total for 5 boards** | **~$190** |

## Issues

- [ ] **C17407 (100k resistor, R20) is discontinued** — needs swap to C149504 or equivalent
- [ ] 24 extended parts fees dominate cost at low qty
- [ ] 3x LMZM23601SILR @ $5.95 each is the biggest component cost driver

## Cost Savings Opportunities

1. **Replace LMZM23601SILR** with discrete buck converter (e.g., TPS563200 ~$0.40 Basic) — saves ~$16.65 in parts + $3 extended fee per unique swap
2. **Swap non-standard resistor values to Basic equivalents** (4.22k, 2.49k, 4.7k, 110k are all Extended) — could save $12-15 in extended fees
3. **Higher quantity orders** amortize the $72 extended fee (qty 30: ~$2.40/board vs qty 5: ~$14.40/board)
