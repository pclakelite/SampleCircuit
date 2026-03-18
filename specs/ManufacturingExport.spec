# =============================================================================
# MANUFACTURING EXPORT SPECIFICATION — CircuitAI Project
# =============================================================================
# Rules for exporting JLCPCB-ready fabrication and assembly files from a
# KiCad 9.0 PCB project.
#
# Version: 1.0
# Date: March 2026
# Applies to: Any .kicad_pcb board in this project
# Related: specs/PCBLayout.spec §15 (JLCPCB Design Rules)


# =============================================================================
# 1. OVERVIEW — PIPELINE STAGE
# =============================================================================
# This spec covers the final stage of the CircuitAI workflow:
#
#   Design (CircuitCreation.spec)
#     -> Template (TemplateCreation.spec)
#       -> Layout (PCBLayout.spec)
#         -> **Export & Manufacture (this spec)**
#
# Three deliverables are required for JLCPCB PCB + SMT Assembly orders:
#   1. Gerber + Drill archive (.zip)
#   2. Bill of Materials (.csv)
#   3. Component Placement List (.csv)


# =============================================================================
# 2. TOOLS & ENVIRONMENT
# =============================================================================
# 2a. KiCad CLI (preferred for Gerber/drill/position export):
#       "C:/Program Files/KiCad/9.0/bin/kicad-cli.exe"
#     Does NOT require a running KiCad instance.
#
# 2b. Python interpreter (for BOM generation and post-processing):
#       C:/Users/peter.LAKEMAST/AppData/Local/Python/bin/python.exe
#
# 2c. Output directory convention:
#       templates/<board>/jlcpcb_output/
#     Contains: gerbers/ subfolder, BOM CSV, CPL CSV, Gerber ZIP.
#
# 2d. Script naming convention:
#       templates/<board>/export_jlcpcb.py


# =============================================================================
# 3. GERBER FILES
# =============================================================================
# 3a. Use KiCad CLI to export Gerbers:
#       kicad-cli pcb export gerbers \
#         --output <output_dir>/ \
#         --layers F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts \
#         --no-x2 \
#         <board>.kicad_pcb
#
# 3b. Required layers for 2-layer board:
#       F.Cu        — Front copper
#       B.Cu        — Back copper
#       F.Paste     — Front solder paste (stencil)
#       B.Paste     — Back solder paste
#       F.SilkS     — Front silkscreen
#       B.SilkS     — Back silkscreen
#       F.Mask      — Front solder mask
#       B.Mask      — Back solder mask
#       Edge.Cuts   — Board outline
#
# 3c. Options:
#       --no-x2                  Use standard Gerber (JLCPCB compatible)
#       Do NOT use --no-protel-ext (JLCPCB prefers KiCad default extensions)
#
# 3d. For 4+ layer boards, add inner copper layers: In1.Cu, In2.Cu, etc.


# =============================================================================
# 4. DRILL FILES
# =============================================================================
# 4a. Use KiCad CLI to export drill files:
#       kicad-cli pcb export drill \
#         --output <output_dir>/ \
#         --format excellon \
#         --excellon-units mm \
#         --excellon-zeros-format decimal \
#         --excellon-separate-th \
#         <board>.kicad_pcb
#
# 4b. --excellon-separate-th generates separate files for:
#       PTH (plated through-hole)
#       NPTH (non-plated through-hole)
#     JLCPCB expects these separated.
#
# 4c. Units MUST be mm, zeros format MUST be decimal.


# =============================================================================
# 5. GERBER ZIP ARCHIVE
# =============================================================================
# 5a. All Gerber (.gbr/.g*) and drill (.drl) files go into one ZIP.
# 5b. Files should be at the ZIP root — no subdirectories inside the ZIP.
# 5c. Naming: <BoardName>_Gerbers.zip
# 5d. This single ZIP is uploaded to JLCPCB's order page.


# =============================================================================
# 6. BOM (BILL OF MATERIALS)
# =============================================================================
# 6a. JLCPCB BOM format — CSV with these exact column headers:
#       Comment, Designator, Footprint, LCSC Part #
#
# 6b. Column definitions:
#       Comment      — Component value (e.g., "10k", "100nF", "MAX98357A")
#       Designator   — Comma-separated reference designators (e.g., "R1,R2,R3")
#       Footprint    — Footprint/package name from the PCB
#       LCSC Part #  — JLCPCB/LCSC part number (e.g., "C17414")
#
# 6c. Grouping: Components with identical (value, footprint, LCSC) are
#     grouped into one BOM row with combined designators.
#
# 6d. LCSC part numbers are extracted from the PCB footprint tags field.
#     In this project, JLCImport footprints include LCSC numbers in their
#     (tags "...") field, matching pattern: C followed by 4-7 digits.
#
# 6e. Through-hole (TH) components can be included in the BOM but will
#     need manual soldering unless JLCPCB TH assembly is selected
#     (higher cost). Mark them clearly.
#
# 6f. Naming: <BoardName>_BOM.csv


# =============================================================================
# 7. CPL (COMPONENT PLACEMENT LIST)
# =============================================================================
# 7a. JLCPCB CPL format — CSV with these exact column headers:
#       Designator, Mid X, Mid Y, Rotation, Layer
#
# 7b. Column definitions:
#       Designator  — Reference designator (e.g., "R1")
#       Mid X       — X center coordinate with "mm" suffix (e.g., "140.00mm")
#       Mid Y       — Y center coordinate with "mm" suffix (e.g., "118.00mm")
#       Rotation    — Component rotation in degrees (0, 90, 180, 270)
#       Layer       — "Top" or "Bottom"
#
# 7c. Coordinates come from the footprint (at x y angle) in the .kicad_pcb.
#     KiCad's coordinate origin is top-left; JLCPCB uses the same convention.
#
# 7d. IMPORTANT: KiCad CLI can also export position files:
#       kicad-cli pcb export pos \
#         --output <file>.csv \
#         --format csv \
#         --units mm \
#         --smd-only \
#         --exclude-dnp \
#         <board>.kicad_pcb
#     However, the CSV format may need column renaming to match JLCPCB's
#     expected headers. The export script handles this reformatting.
#
# 7e. Only SMD components should be in the CPL. Exclude through-hole parts
#     (battery holders, connectors with TH pins) unless ordering TH assembly.
#
# 7f. Naming: <BoardName>_CPL.csv


# =============================================================================
# 8. LCSC PART NUMBER MAPPING
# =============================================================================
# 8a. Every SMD component MUST have an LCSC part number for JLCPCB assembly.
#     Missing LCSC numbers will cause parts to be skipped during assembly.
#
# 8b. Primary source: the (tags "...") field in .kicad_pcb footprints.
#     JLCImport footprints include the LCSC number in their tags.
#     Pattern: \bC\d{4,7}\b (e.g., C17414, C910544)
#
# 8c. Fallback: maintain an explicit LCSC_MAP dictionary in the export
#     script mapping footprint names to LCSC part numbers. Update this
#     when adding new components.
#
# 8d. JLCPCB part categories:
#       Basic parts  — Common passives (0805 R/C, standard values).
#                      No extra fee. Stocked in large quantities.
#       Extended parts — ICs, specialty passives, connectors.
#                        $3.00 fee per unique extended part (one-time per order).
#
# 8e. To check if a part is Basic or Extended, search on:
#       https://jlcpcb.com/parts
#     Filter by LCSC number. Basic parts show a "Basic" badge.


# =============================================================================
# 9. COST ESTIMATION RULES
# =============================================================================
# 9a. PCB fabrication pricing (2-layer, standard):
#       Board area <= 100x100mm:  ~$2 for 5 pcs
#       Board area > 100x100mm:   ~$2 + $0.04/cm2 over 100cm2
#       101.6x101.6mm (~103.2cm2): ~$5-8 for 5 pcs
#
# 9b. SMT Assembly pricing:
#       Setup fee:           $8.00 (one-time per order, one side)
#       Both-sides assembly: $16.00 setup ($8 per side)
#       Extended part fee:   $3.00 per unique extended part
#       Basic part fee:      $0.00
#       Per-pad fee:         ~$0.0017/pad (varies)
#
# 9c. Component costs: depend on JLCPCB/LCSC stock prices.
#     Rough estimates for common parts (per unit):
#       0805 resistor:          $0.003-0.01
#       0805/1206 MLCC cap:     $0.01-0.15
#       Electrolytic cap (SMD): $0.50-2.00
#       Schottky diode (SMD):   $0.10-0.50
#       DC-DC module (LMZM):    $2.50-4.00
#       Audio IC (MAX98357A):   $1.50-3.00
#       RTC (RV-3028):          $2.00-3.50
#       NAND flash (CSNP1G):    $1.00-2.00
#       Supervisor (TLV803S):   $0.20-0.50
#
# 9d. Shipping estimates:
#       Economy (Global Standard Mail):  $5-10, 15-30 days
#       Standard (DHL/FedEx Economy):    $15-25, 7-12 days
#       Express (DHL/FedEx):             $25-45, 3-7 days
#
# 9e. Minimum order: 5 boards for prototype pricing.
#     Assembly minimum: 2 boards (but 5 is standard).
#
# 9f. Cost estimate accuracy: These are rough guidelines. Always upload
#     the actual files to JLCPCB's order page for exact pricing. Prices
#     change frequently and depend on stock levels.


# =============================================================================
# 10. EXPORT SCRIPT STRUCTURE
# =============================================================================
# 10a. Each board's export script lives at:
#        templates/<board>/export_jlcpcb.py
#
# 10b. The script MUST:
#        1. Parse the .kicad_pcb to extract component data
#        2. Run kicad-cli to generate Gerber and drill files
#        3. ZIP the Gerber/drill files
#        4. Generate BOM CSV in JLCPCB format (§6)
#        5. Generate CPL CSV in JLCPCB format (§7)
#        6. Print a component summary with LCSC part numbers
#        7. Print a cost estimate (§9)
#        8. List the 3 output files ready for upload
#
# 10c. The script should be runnable standalone:
#        python export_jlcpcb.py
#      No arguments needed — it finds paths relative to its own location.
#
# 10d. Output files go to: templates/<board>/jlcpcb_output/
#
# 10e. The script should warn about:
#        - Components missing LCSC part numbers
#        - Through-hole components that need manual soldering
#        - Board dimensions exceeding 100x100mm (higher PCB cost)


# =============================================================================
# 11. UPLOAD PROCEDURE (REFERENCE)
# =============================================================================
# 11a. Go to https://cart.jlcpcb.com/quote
# 11b. Upload <BoardName>_Gerbers.zip — board dimensions auto-detected
# 11c. Set options: layers (2), thickness (1.6mm), color (green default)
# 11d. Toggle "SMT Assembly" ON
# 11e. Select assembly side: Top (or both if components on both sides)
# 11f. Upload BOM CSV and CPL CSV
# 11g. JLCPCB will match parts and show assembly preview
# 11h. Review part matches — confirm orientations in the preview
# 11i. IMPORTANT: Check component rotation in the preview. JLCPCB's
#      rotation convention may differ from KiCad. Adjust rotation offsets
#      in the CPL if components appear rotated incorrectly.
# 11j. Add to cart and complete order.


# =============================================================================
# 12. DFM CHECKS (PRE-EXPORT)
# =============================================================================
# 12a. Run KiCad DRC before exporting — zero errors required.
# 12b. Verify all footprints have correct LCSC part numbers.
# 12c. Check courtyard clearances (no overlapping footprints).
# 12d. Verify board outline is a closed shape on Edge.Cuts.
# 12e. Check minimum annular ring on vias (0.075mm for JLCPCB).
# 12f. Confirm solder paste openings exist for all SMD pads.
# 12g. Check silkscreen doesn't overlap exposed copper pads.
# 12h. Verify copper-to-edge clearance >= 0.3mm (see PCBLayout.spec §15g).
