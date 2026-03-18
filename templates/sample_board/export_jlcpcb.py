"""
Export JLCPCB manufacturing files from SampleBoard.
See specs/ManufacturingExport.spec for full rules.

Outputs (in jlcpcb_output/):
  - SampleBoard_Gerbers.zip   (Gerber + drill files)
  - SampleBoard_BOM.csv       (Bill of Materials)
  - SampleBoard_CPL.csv       (Component Placement List)

Usage:
  python export_jlcpcb.py
"""

import subprocess
import os
import re
import csv
import zipfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PCB_FILE = os.path.join(SCRIPT_DIR, "SampleBoard.kicad_pcb")
KICAD_CLI = r"C:\Program Files\KiCad\9.0\bin\kicad-cli.exe"
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "jlcpcb_output")
GERBER_DIR = os.path.join(OUTPUT_DIR, "gerbers")

# Explicit LCSC mapping — overrides tag extraction when footprint tags
# have incorrect LCSC numbers (e.g. R7/R6 tags inherited from 10k template)
LCSC_MAP = {
    "GRM32ER7YA106KA12L": "C97973",       # 10uF 35V 1210 ceramic
    "0805W8F1001T5E":     "C17513",        # 1k 0805
    "MAX98357AETE_T":     "C910544",       # MAX98357A audio amp
    "LMZM23601SILR":      "C2685821",      # LMZM23601 DC-DC module
    "EEEFT1V681UP":       "C542257",       # 680uF 35V electrolytic
    "0805W8F1002T5E":     "C17414",        # 10k 0805
    "CC0805KRX7R9BB104":  "C49678",        # 100nF 0805
    "1206X476M160NT":     "C172351",       # 47uF 16V 1206
    "0805W8F1003T5E":     "C17407",        # 100k 0805 (tags say C17414 — wrong)
    "GRM32EC81C476KE15L": "C162512",       # 47uF 16V 1210
    "0805W8F1004T5E":     "C17514",        # 1M 0805 (tags say C17414 — wrong)
    "RV-3028-C7_32_768KHZ_1PPM_TA_QC": "C3019759",  # RV-3028-C7 RTC
    "PMEG6030EVPX":       "C489223",       # Schottky diode
    "0805W8F4221T5E":     "C17665",        # 4.22k 0805
    "CL21A106KAYNNNE":    "C15850",        # 10uF 25V 0805
    "0805W8F2491T5E":     "C21237",        # 2.49k 0805
    "CR2032-BS-2-1":      "C70376",        # CR2032 battery holder (TH)
}

# Through-hole footprints (excluded from CPL, flagged in BOM)
TH_FOOTPRINTS = {"CR2032-BS-2-1"}


def parse_pcb_components(pcb_file):
    """Parse footprint blocks from .kicad_pcb to extract component data."""
    with open(pcb_file, "r", encoding="utf-8") as f:
        content = f.read()

    components = []

    # Regex to match each footprint's key fields
    fp_pattern = re.compile(
        r'\(footprint\s+"([^"]+)"\s*\n'
        r'\s*\(layer\s+"([^"]+)"\)\s*\n'
        r'\s*\(uuid\s+"[^"]+"\)\s*\n'
        r'\s*\(at\s+([\d.]+)\s+([\d.]+)(?:\s+([\d.]+))?\)',
        re.MULTILINE
    )
    ref_pattern = re.compile(r'\(property\s+"Reference"\s+"([^"]+)"')
    val_pattern = re.compile(r'\(property\s+"Value"\s+"([^"]+)"')
    tag_pattern = re.compile(r'\(tags\s+"([^"]+)"\)')

    # Split on footprint boundaries
    blocks = content.split('\n\t(footprint "')
    for i, block in enumerate(blocks):
        if i == 0:
            continue  # header before first footprint
        block = '(footprint "' + block

        fp_match = fp_pattern.search(block)
        if not fp_match:
            continue

        footprint = fp_match.group(1)
        layer = fp_match.group(2)
        x = float(fp_match.group(3))
        y = float(fp_match.group(4))
        rotation = float(fp_match.group(5)) if fp_match.group(5) else 0.0

        ref_match = ref_pattern.search(block)
        val_match = val_pattern.search(block)
        tag_match = tag_pattern.search(block)

        reference = ref_match.group(1) if ref_match else "?"
        value = val_match.group(1) if val_match else "?"
        tags = tag_match.group(1) if tag_match else ""

        # LCSC lookup: prefer explicit map, fallback to tag extraction
        lcsc = LCSC_MAP.get(footprint, "")
        if not lcsc:
            lcsc_match = re.search(r'\bC\d{4,7}\b', tags)
            if lcsc_match:
                lcsc = lcsc_match.group(0)

        is_th = footprint in TH_FOOTPRINTS
        side = "Top" if layer == "F.Cu" else "Bottom"

        components.append({
            "reference": reference,
            "value": value,
            "footprint": footprint,
            "lcsc": lcsc,
            "x": x,
            "y": y,
            "rotation": rotation,
            "side": side,
            "is_th": is_th,
        })

    return components


def ref_sort_key(ref):
    """Sort key for reference designators: letter prefix, then numeric."""
    m = re.match(r'([A-Za-z]+)(\d+)', ref)
    if m:
        return (m.group(1), int(m.group(2)))
    return (ref, 0)


def export_gerbers():
    """Export Gerber and drill files using KiCad CLI, then zip them."""
    os.makedirs(GERBER_DIR, exist_ok=True)

    layers = "F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts"

    print("Exporting Gerbers...")
    result = subprocess.run([
        KICAD_CLI, "pcb", "export", "gerbers",
        "--output", GERBER_DIR + "/",
        "--layers", layers,
        "--no-x2",
        PCB_FILE
    ], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")
        return False
    print(f"  Gerbers -> {GERBER_DIR}")

    print("Exporting drill files...")
    result = subprocess.run([
        KICAD_CLI, "pcb", "export", "drill",
        "--output", GERBER_DIR + "/",
        "--format", "excellon",
        "--excellon-units", "mm",
        "--excellon-zeros-format", "decimal",
        "--excellon-separate-th",
        PCB_FILE
    ], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")
        return False
    print(f"  Drill files -> {GERBER_DIR}")

    # Zip all gerber + drill files
    zip_path = os.path.join(OUTPUT_DIR, "SampleBoard_Gerbers.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in sorted(os.listdir(GERBER_DIR)):
            fpath = os.path.join(GERBER_DIR, fname)
            if os.path.isfile(fpath):
                zf.write(fpath, fname)
    print(f"  Zipped -> {zip_path}")
    return True


def export_bom(components):
    """Export BOM CSV in JLCPCB format (Comment, Designator, Footprint, LCSC Part #)."""
    bom_path = os.path.join(OUTPUT_DIR, "SampleBoard_BOM.csv")

    # Group by (value, footprint, lcsc)
    groups = {}
    for c in components:
        key = (c["value"], c["footprint"], c["lcsc"])
        if key not in groups:
            groups[key] = []
        groups[key].append(c["reference"])

    with open(bom_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for (value, footprint, lcsc), refs in sorted(groups.items(), key=lambda x: ref_sort_key(x[1][0])):
            refs_sorted = sorted(refs, key=ref_sort_key)
            writer.writerow([value, ",".join(refs_sorted), footprint, lcsc])

    print(f"BOM -> {bom_path}")
    print(f"  {len(groups)} unique parts, {len(components)} total placements")

    # Warn about missing LCSC
    missing = [r for c in components for r in [c["reference"]] if not c["lcsc"]]
    if missing:
        print(f"  WARNING: Missing LCSC part # for: {', '.join(missing)}")

    return bom_path


def export_cpl(components):
    """Export CPL CSV in JLCPCB format (Designator, Mid X, Mid Y, Rotation, Layer).
    Excludes through-hole components."""
    cpl_path = os.path.join(OUTPUT_DIR, "SampleBoard_CPL.csv")

    smd_components = [c for c in components if not c["is_th"]]

    with open(cpl_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Designator", "Mid X", "Mid Y", "Rotation", "Layer"])
        for c in sorted(smd_components, key=lambda c: ref_sort_key(c["reference"])):
            writer.writerow([
                c["reference"],
                f"{c['x']:.2f}mm",
                f"{c['y']:.2f}mm",
                c["rotation"],
                c["side"]
            ])

    th_count = len(components) - len(smd_components)
    print(f"CPL -> {cpl_path}")
    print(f"  {len(smd_components)} SMD placements")
    if th_count:
        th_refs = [c["reference"] for c in components if c["is_th"]]
        print(f"  {th_count} TH excluded (solder manually): {', '.join(th_refs)}")

    return cpl_path


def print_cost_estimate(components):
    """Print approximate JLCPCB cost for 5 boards."""

    # Group for summary
    groups = {}
    for c in components:
        key = (c["value"], c["footprint"], c["lcsc"])
        if key not in groups:
            groups[key] = {"refs": [], "is_th": c["is_th"]}
        groups[key]["refs"].append(c["reference"])

    smd_count = sum(len(g["refs"]) for g in groups.values() if not g["is_th"])
    th_count = sum(len(g["refs"]) for g in groups.values() if g["is_th"])
    unique_smd = sum(1 for g in groups.values() if not g["is_th"])

    print("\n" + "=" * 65)
    print("COMPONENT SUMMARY")
    print("=" * 65)
    print(f"{'Ref':20s}  {'Value':20s}  {'LCSC':10s}  Type")
    print("-" * 65)
    for (value, footprint, lcsc), info in sorted(groups.items(), key=lambda x: ref_sort_key(x[1]["refs"][0])):
        refs = ",".join(sorted(info["refs"], key=ref_sort_key))
        ptype = "TH" if info["is_th"] else "SMD"
        print(f"  {refs:20s}  {value:20s}  {lcsc:10s}  {ptype}")

    print(f"\nTotal: {len(components)} components ({smd_count} SMD, {th_count} TH)")
    print(f"Unique SMD parts: {unique_smd}")

    # --- Cost estimate ---
    print("\n" + "=" * 65)
    print("JLCPCB COST ESTIMATE — 5 boards, 2-layer, top-side SMT assembly")
    print("=" * 65)
    print("(Approximate — upload files for exact pricing)\n")

    # PCB fab: 101.6 x 101.6mm = slightly over 100x100
    pcb_fab = 7.00

    # Assembly
    smt_setup = 8.00

    # Extended parts: LMZM23601 x2, MAX98357A, RV-3028, PMEG6030, EEEFT1V681UP, GRM32EC81C476KE15L
    # Basic parts: 0805 R/C, CL21A106KAYNNNE, CC0805KRX7R9BB104, 1206X476M160NT, GRM32ER7YA106KA12L
    num_extended = 6
    extended_fee = num_extended * 3.00  # $3 per unique extended part

    # Component unit prices (approximate LCSC pricing)
    unit_prices = {
        "LMZM23601SILR":      3.50,
        "MAX98357AETE_T":     2.00,
        "RV-3028-C7_32_768KHZ_1PPM_TA_QC": 2.80,
        "PMEG6030EVPX":       0.25,
        "EEEFT1V681UP":       1.50,
        "GRM32ER7YA106KA12L": 0.08,
        "GRM32EC81C476KE15L": 0.12,
        "CC0805KRX7R9BB104":  0.01,
        "1206X476M160NT":     0.08,
        "CL21A106KAYNNNE":    0.04,
        "0805W8F1002T5E":     0.005,
        "0805W8F1001T5E":     0.005,
        "0805W8F1003T5E":     0.005,
        "0805W8F1004T5E":     0.005,
        "0805W8F4221T5E":     0.005,
        "0805W8F2491T5E":     0.005,
        "CR2032-BS-2-1":      0.30,
    }

    # Cost per board (component prices)
    per_board_parts = 0.0
    for c in components:
        per_board_parts += unit_prices.get(c["footprint"], 0.10)
    parts_x5 = per_board_parts * 5

    # Placement fee (~$0.0017/pad, rough $0.02/component average)
    placement_x5 = smd_count * 5 * 0.02

    print(f"  PCB fabrication (5 pcs, 101.6x101.6mm, 2-layer):  ${pcb_fab:>7.2f}")
    print(f"  SMT setup fee (one side):                          ${smt_setup:>7.2f}")
    print(f"  Extended part fees ({num_extended} unique x $3):               ${extended_fee:>7.2f}")
    print(f"  Component placement ({smd_count} SMD x 5 boards):            ${placement_x5:>7.2f}")
    print(f"  Component parts ({len(components)} parts x 5 boards):             ${parts_x5:>7.2f}")

    subtotal = pcb_fab + smt_setup + extended_fee + placement_x5 + parts_x5
    shipping_economy = 8.00
    shipping_standard = 20.00

    print(f"                                                     --------")
    print(f"  Subtotal:                                          ${subtotal:>7.2f}")
    print()
    print(f"  + Shipping (economy, ~15-30 days):                 ${shipping_economy:>7.2f}")
    print(f"  TOTAL (economy):                                   ${subtotal + shipping_economy:>7.2f}")
    print(f"  Per board (economy):                               ${(subtotal + shipping_economy) / 5:>7.2f}")
    print()
    print(f"  + Shipping (standard DHL, ~7-12 days):             ${shipping_standard:>7.2f}")
    print(f"  TOTAL (standard):                                  ${subtotal + shipping_standard:>7.2f}")
    print(f"  Per board (standard):                              ${(subtotal + shipping_standard) / 5:>7.2f}")
    print()
    print("  Notes:")
    print("  - B3 (CR2032 battery holder) is TH — solder manually")
    print("  - Board is 101.6x101.6mm (slightly over 100x100 threshold)")
    print("  - Extended part prices vary with JLCPCB stock")
    print("  - First-order coupons may reduce cost significantly")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Parsing {PCB_FILE}...")
    components = parse_pcb_components(PCB_FILE)
    print(f"Found {len(components)} components\n")

    if not components:
        print("ERROR: No components found in PCB file!")
        return

    gerber_ok = export_gerbers()
    print()
    export_bom(components)
    print()
    export_cpl(components)

    print_cost_estimate(components)

    print("\n" + "=" * 65)
    if gerber_ok:
        print("FILES READY FOR JLCPCB UPLOAD:")
        print(f"  1. {os.path.join(OUTPUT_DIR, 'SampleBoard_Gerbers.zip')}")
        print(f"  2. {os.path.join(OUTPUT_DIR, 'SampleBoard_BOM.csv')}")
        print(f"  3. {os.path.join(OUTPUT_DIR, 'SampleBoard_CPL.csv')}")
    else:
        print("Gerber export FAILED — BOM and CPL still generated.")
        print("Try exporting Gerbers manually from KiCad.")
    print("=" * 65)


if __name__ == "__main__":
    main()
