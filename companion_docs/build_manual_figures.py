"""Generate matplotlib figures for the Stage A prototype build manual."""
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Wedge
from matplotlib.lines import Line2D

OUT = "/home/thedoctor/mbm_spacecharge"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.linewidth": 0.8,
    "axes.edgecolor": "#222",
    "savefig.bbox": "tight",
    "savefig.dpi": 200,
})

# ---------------------------------------------------------------------
# Figure 1: top-down bench layout (1.5 m x 1.5 m granite)
# ---------------------------------------------------------------------
def fig_bench_layout():
    fig, ax = plt.subplots(figsize=(7.0, 7.0))
    # Granite slab
    slab = Rectangle((0, 0), 1.5, 1.5, facecolor="#d8d4cc", edgecolor="#444",
                     linewidth=1.5, zorder=1)
    ax.add_patch(slab)

    # Isolator pads (corners)
    for (x, y) in [(0.05, 0.05), (1.35, 0.05), (0.05, 1.35), (1.35, 1.35)]:
        c = Circle((x + 0.05, y + 0.05), 0.06, facecolor="#444",
                   edgecolor="black", linewidth=0.8, zorder=3)
        ax.add_patch(c)
        ax.text(x + 0.05, y + 0.05, "ISO", color="white", ha="center",
                va="center", fontsize=7, fontweight="bold")

    # UHV chamber footprint (center, ~0.4 m diameter incl flanges)
    ch = Circle((0.75, 0.75), 0.22, facecolor="#a8c4e0", edgecolor="#1f4e79",
                linewidth=1.4, zorder=4)
    ax.add_patch(ch)
    ax.text(0.75, 0.78, "UHV\nchamber\n8\" CF", ha="center", va="center",
            fontsize=8.5, fontweight="bold")
    ax.text(0.75, 0.66, "(cryostat above)", ha="center", va="center", fontsize=7,
            style="italic", color="#1f4e79")

    # Source gun side-mount (left)
    sg = Rectangle((0.20, 0.68), 0.20, 0.14, facecolor="#f4cccc",
                   edgecolor="#a64d4d", linewidth=1.2, zorder=4)
    ax.add_patch(sg)
    ax.text(0.30, 0.75, "CFE\ngun", ha="center", va="center", fontsize=8,
            fontweight="bold")
    # gun to chamber connector
    ax.plot([0.40, 0.53], [0.75, 0.75], color="#a64d4d", linewidth=2.0, zorder=3)

    # BSE detector (right of chamber)
    bse = Rectangle((1.10, 0.68), 0.18, 0.14, facecolor="#fff2cc",
                    edgecolor="#bf9000", linewidth=1.2, zorder=4)
    ax.add_patch(bse)
    ax.text(1.19, 0.75, "BSE\ndet.", ha="center", va="center", fontsize=8,
            fontweight="bold")
    ax.plot([0.97, 1.10], [0.75, 0.75], color="#bf9000", linewidth=2.0, zorder=3)

    # Pumping stack (bottom of chamber)
    pump = Rectangle((0.66, 0.30), 0.18, 0.20, facecolor="#d9ead3",
                     edgecolor="#38761d", linewidth=1.2, zorder=4)
    ax.add_patch(pump)
    ax.text(0.75, 0.40, "Turbo\n+ ion\npump", ha="center", va="center",
            fontsize=7.5)
    ax.plot([0.75, 0.75], [0.53, 0.50], color="#38761d", linewidth=2.0, zorder=3)

    # Wafer load lock (back of chamber, top)
    ll = Rectangle((0.66, 1.00), 0.18, 0.14, facecolor="#cfe2f3",
                   edgecolor="#1c4587", linewidth=1.2, zorder=4)
    ax.add_patch(ll)
    ax.text(0.75, 1.07, "Wafer\nload-lock", ha="center", va="center",
            fontsize=7.5)
    ax.plot([0.75, 0.75], [1.00, 0.97], color="#1c4587", linewidth=2.0, zorder=3)

    # Fiber feedthrough (back-right)
    fft = Rectangle((1.05, 1.00), 0.14, 0.12, facecolor="#ead1dc",
                    edgecolor="#741b47", linewidth=1.2, zorder=4)
    ax.add_patch(fft)
    ax.text(1.12, 1.06, "Fiber\nfeedthru", ha="center", va="center",
            fontsize=7)

    # ZMI interferometer head (external, front-right, viewport access)
    zmi = Rectangle((1.05, 0.45), 0.14, 0.12, facecolor="#f9cb9c",
                    edgecolor="#b45f06", linewidth=1.2, zorder=4)
    ax.add_patch(zmi)
    ax.text(1.12, 0.51, "ZMI\nlaser", ha="center", va="center", fontsize=7)
    # viewport line into chamber
    ax.plot([1.05, 0.97], [0.51, 0.62], color="#b45f06", linewidth=1.0,
            linestyle="--", zorder=2)

    # Rack off-bench (drawn outside slab to the right, labelled)
    rack = Rectangle((1.55, 0.50), 0.10, 0.50, facecolor="#cccccc",
                     edgecolor="#222", linewidth=1.0, zorder=4)
    ax.add_patch(rack)
    ax.text(1.60, 0.75, "Control\nrack\n(off-bench)", ha="center", va="center",
            fontsize=7, rotation=90)
    # fiber bundle to feedthrough
    ax.annotate("", xy=(1.10, 1.05), xytext=(1.60, 1.00),
                arrowprops=dict(arrowstyle="-", color="purple", linewidth=1.0,
                                connectionstyle="arc3,rad=-0.2"), zorder=2)

    # North arrow + scale bar
    ax.annotate("N (beam axis +X)", xy=(0.08, 1.45), xytext=(0.08, 1.45),
                fontsize=8, color="#555")
    ax.plot([0.05, 0.25], [0.02, 0.02], color="black", linewidth=2.0)
    ax.text(0.15, -0.025, "200 mm scale", ha="center", fontsize=7)

    # Title and axes
    ax.set_xlim(-0.1, 1.85)
    ax.set_ylim(-0.10, 1.60)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Figure 1. Bench top-down layout\n"
                 "1.5 m × 1.5 m granite slab on 4× pneumatic isolators",
                 fontsize=10, fontweight="bold")
    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.savefig(os.path.join(OUT, "build_fig1_bench.png"), dpi=200)
    plt.savefig(os.path.join(OUT, "build_fig1_bench.pdf"))
    plt.close()
    print("wrote build_fig1_bench.{png,pdf}")


# ---------------------------------------------------------------------
# Figure 2: cross-section of vacuum chamber + cold finger
# ---------------------------------------------------------------------
def fig_chamber_section():
    fig, ax = plt.subplots(figsize=(7.0, 9.5))

    # Pulse-tube cold head (top), water-cooled compressor separate
    pt_body = Rectangle((-0.30, 1.95), 0.60, 0.40, facecolor="#cccccc",
                        edgecolor="#222", linewidth=1.4, zorder=3)
    ax.add_patch(pt_body)
    ax.text(0.0, 2.15, "Cryomech PT-90\npulse-tube cold head",
            ha="center", va="center", fontsize=9, fontweight="bold")
    # vibration-isolating hose tag
    ax.annotate("He hose to\ncompressor\n(vibration-isolated, 3 m)",
                xy=(0.30, 2.15), xytext=(0.85, 2.20),
                fontsize=8, color="#666",
                arrowprops=dict(arrowstyle="->", color="#666", linewidth=0.8))

    # Cold finger drop (custom bellows on CF flange)
    cf_flange = Rectangle((-0.15, 1.80), 0.30, 0.15, facecolor="#999",
                          edgecolor="#222", linewidth=1.2, zorder=3)
    ax.add_patch(cf_flange)
    ax.text(0.0, 1.875, "8\" CF flange + bellows",
            ha="center", va="center", fontsize=8)

    cold_finger = Rectangle((-0.05, 0.90), 0.10, 0.90, facecolor="#bbd6f0",
                            edgecolor="#1f4e79", linewidth=1.2, zorder=4)
    ax.add_patch(cold_finger)
    ax.text(-0.18, 1.50, "Copper\ncold\nfinger\n(77 K)",
            ha="right", va="center", fontsize=8, color="#1f4e79")

    # MLI wrap (drawn as dashed outline around cold finger upper region)
    mli = Rectangle((-0.12, 0.92), 0.24, 0.88, facecolor="none",
                    edgecolor="#888", linewidth=0.8, linestyle=":")
    ax.add_patch(mli)
    ax.text(0.18, 1.55, "30-layer MLI\n(aluminized Mylar)",
            ha="left", va="center", fontsize=8, color="#888")

    # YBCO coil + Meissner shield assembly (bottom of cold finger)
    coil = Rectangle((-0.08, 0.78), 0.16, 0.12, facecolor="#fce5cd",
                     edgecolor="#b45f06", linewidth=1.2, zorder=5)
    ax.add_patch(coil)
    ax.text(0.0, 0.84, "YBCO coil +\nMeissner shield",
            ha="center", va="center", fontsize=7.5, fontweight="bold")

    # Cryo-CMOS DAC chip on interposer
    dac = Rectangle((-0.08, 0.66), 0.16, 0.10, facecolor="#d9d2e9",
                    edgecolor="#5b2c6f", linewidth=1.2, zorder=5)
    ax.add_patch(dac)
    ax.text(0.0, 0.71, "Cryo-CMOS DAC\n+ InP photodiode",
            ha="center", va="center", fontsize=7.5)

    # UHV chamber body (8" CF, drawn as wide rectangle)
    chamber = Rectangle((-0.55, 0.10), 1.10, 1.75, facecolor="none",
                        edgecolor="#1f4e79", linewidth=2.5, zorder=2)
    ax.add_patch(chamber)
    ax.text(-0.50, 1.78, "8\" CF UHV chamber\n(Lesker / Pfeiffer)",
            ha="left", va="top", fontsize=8.5, fontweight="bold",
            color="#1f4e79")

    # Source gun side-mount (left CF port)
    src = Rectangle((-0.95, 0.85), 0.40, 0.20, facecolor="#f4cccc",
                    edgecolor="#a64d4d", linewidth=1.4, zorder=4)
    ax.add_patch(src)
    ax.text(-0.75, 0.95, "CFE gun\n(50 kV)", ha="center", va="center",
            fontsize=8, fontweight="bold")
    # beam path from gun → centerline (45° down then straight down)
    beam_x = [-0.55, -0.10, 0.0, 0.0]
    beam_y = [0.95, 0.95, 0.78, 0.22]
    ax.plot(beam_x, beam_y, color="#a64d4d", linewidth=2.0, linestyle="-",
            zorder=4)
    # condenser lens marker between gun and coil
    lens = Circle((-0.30, 0.95), 0.04, facecolor="#fff", edgecolor="#a64d4d",
                  linewidth=1.5, zorder=5)
    ax.add_patch(lens)
    ax.text(-0.30, 0.85, "condenser\nlens", ha="center", va="center",
            fontsize=7, color="#a64d4d")

    # BSE detector (right CF port)
    bse = Rectangle((0.55, 0.40), 0.30, 0.18, facecolor="#fff2cc",
                    edgecolor="#bf9000", linewidth=1.4, zorder=4)
    ax.add_patch(bse)
    ax.text(0.70, 0.49, "BSE\ndetector", ha="center", va="center",
            fontsize=8, fontweight="bold")

    # Viewport (lower right small port)
    vp = Rectangle((0.55, 0.18), 0.18, 0.10, facecolor="#cfe2f3",
                   edgecolor="#1f4e79", linewidth=1.0, zorder=4)
    ax.add_patch(vp)
    ax.text(0.64, 0.23, "viewport\n+ ZMI", ha="center", va="center",
            fontsize=7)

    # Wafer stage (bottom)
    chuck = Rectangle((-0.18, 0.12), 0.36, 0.08, facecolor="#cccccc",
                      edgecolor="#222", linewidth=1.2, zorder=4)
    ax.add_patch(chuck)
    ax.text(0.0, 0.16, "Al wafer chuck (He backside)", ha="center",
            va="center", fontsize=7.5)
    stage = Rectangle((-0.30, 0.02), 0.60, 0.10, facecolor="#b6d7a8",
                      edgecolor="#38761d", linewidth=1.2, zorder=4)
    ax.add_patch(stage)
    ax.text(0.0, 0.07, "6-DOF piezo stage (PI)", ha="center",
            va="center", fontsize=7.5)

    # Pump-out port (below stage, drawn outside)
    pump_port = Rectangle((-0.10, -0.20), 0.20, 0.15, facecolor="#d9ead3",
                          edgecolor="#38761d", linewidth=1.2, zorder=4)
    ax.add_patch(pump_port)
    ax.text(0.0, -0.13, "turbo +\nion pump", ha="center", va="center",
            fontsize=7.5)

    # Fiber from cold side to chamber (right top)
    fiber = Line2D([0.65, 0.45, 0.05], [1.50, 1.30, 0.71], color="purple",
                   linewidth=1.2, linestyle="-", zorder=5)
    ax.add_line(fiber)
    ax.text(0.65, 1.55, "optical fiber\n(SFP+ → photodiode)",
            ha="center", fontsize=7.5, color="purple")
    # fiber feedthrough port (right upper CF)
    fft = Rectangle((0.55, 1.45), 0.18, 0.10, facecolor="#ead1dc",
                    edgecolor="#741b47", linewidth=1.2, zorder=4)
    ax.add_patch(fft)
    ax.text(0.64, 1.50, "Accu-Glass\nfiber FT", ha="center", va="center",
            fontsize=7)

    # Temperature labels (left axis)
    ax.text(-1.00, 1.20, "77 K", fontsize=10, color="#1f4e79",
            fontweight="bold")
    ax.text(-1.00, 0.16, "295 K", fontsize=10, color="#a64d4d",
            fontweight="bold")
    ax.text(-1.00, 2.20, "295 K\n(compr.)", fontsize=9, color="#666",
            fontweight="bold")

    # working distance arrow
    ax.annotate("", xy=(0.30, 0.65), xytext=(0.30, 0.22),
                arrowprops=dict(arrowstyle="<->", color="black", linewidth=0.8))
    ax.text(0.34, 0.43, "~50 mm\nworking dist.", fontsize=7.5)

    ax.set_xlim(-1.15, 1.20)
    ax.set_ylim(-0.30, 2.45)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Figure 2. Vacuum-chamber cross-section + cold-finger stack\n"
                 "(side view, beam axis vertical)",
                 fontsize=10, fontweight="bold")
    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.savefig(os.path.join(OUT, "build_fig2_chamber.png"), dpi=200)
    plt.savefig(os.path.join(OUT, "build_fig2_chamber.pdf"))
    plt.close()
    print("wrote build_fig2_chamber.{png,pdf}")


# ---------------------------------------------------------------------
# Figure 3: beam path block diagram
# ---------------------------------------------------------------------
def fig_beam_path():
    fig, ax = plt.subplots(figsize=(10.0, 3.6))

    blocks = [
        ("CFE\nsource\n(50 kV)",  "#f4cccc", 0.5),
        ("Condenser\nmagnetic\nlens",  "#fce5cd", 2.0),
        ("YBCO\ndeflection\ncoil (77 K)",  "#bbd6f0", 3.5),
        ("100 mm\ndrift\n(UHV)",  "#ffffff", 5.0),
        ("BSE\ndetector\n(side-mount)",  "#fff2cc", 6.5),
        ("Fiducial /\nresist wafer\n(295 K)",  "#d9ead3", 8.0),
        ("ZMI\nmetrology\n(external)",  "#f9cb9c", 9.5),
    ]
    for (label, color, x) in blocks:
        bb = FancyBboxPatch((x - 0.55, 0.8), 1.10, 1.2,
                            boxstyle="round,pad=0.02", facecolor=color,
                            edgecolor="#222", linewidth=1.2)
        ax.add_patch(bb)
        ax.text(x, 1.4, label, ha="center", va="center", fontsize=9,
                fontweight="bold")

    # arrows between blocks (beam path)
    for x_from, x_to in [(0.5, 2.0), (2.0, 3.5), (3.5, 5.0), (5.0, 8.0)]:
        ax.annotate("", xy=(x_to - 0.55, 1.4), xytext=(x_from + 0.55, 1.4),
                    arrowprops=dict(arrowstyle="->", color="#a64d4d",
                                    linewidth=1.8))
    # BSE side-tap arrow (from wafer up to detector)
    ax.annotate("", xy=(6.5, 2.0), xytext=(8.0, 2.0),
                arrowprops=dict(arrowstyle="->", color="#bf9000",
                                linewidth=1.3))
    ax.text(7.25, 2.15, "backscattered e-", ha="center", fontsize=7.5,
            color="#bf9000", style="italic")
    # ZMI side-read arrow
    ax.annotate("", xy=(8.0, 0.6), xytext=(9.5, 0.8),
                arrowprops=dict(arrowstyle="->", color="#b45f06",
                                linewidth=1.0, linestyle="--"))
    ax.text(8.75, 0.45, "stage position\n(through viewport)", ha="center",
            fontsize=7, color="#b45f06", style="italic")

    # Bottom data-path strip
    ax.text(0.5, 0.15,
            "Photonic data path:  SFP+ TX (rack)  ──fiber──▶  Accu-Glass UHV feedthru  "
            "──▶  InP PD (77 K)  ──▶  Cryo-CMOS DAC  ──▶  HTS coil  (closes inner loop @ 6 μs)",
            fontsize=8, color="#5b2c6f", style="italic")

    ax.set_xlim(-0.3, 10.4)
    ax.set_ylim(0.0, 2.6)
    ax.set_aspect("auto")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Figure 3. Stage A beam-path block diagram",
                 fontsize=10, fontweight="bold")
    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.savefig(os.path.join(OUT, "build_fig3_beampath.png"), dpi=200)
    plt.savefig(os.path.join(OUT, "build_fig3_beampath.pdf"))
    plt.close()
    print("wrote build_fig3_beampath.{png,pdf}")


# ---------------------------------------------------------------------
# Figure 4: assembly sequence Gantt
# ---------------------------------------------------------------------
def fig_gantt():
    fig, ax = plt.subplots(figsize=(10.0, 5.5))

    tasks = [
        ("Week 0  : Procurement, inventory",            0,  1, "#cccccc"),
        ("Week 1  : Bench setup, chamber clean",        1,  1, "#d9ead3"),
        ("Week 2  : Vacuum assembly + leak test",       2,  1, "#d9ead3"),
        ("Wk 3-4  : Bake-out + pump down",              3,  2, "#d9ead3"),
        ("Week 5  : Install source gun + cold finger",  5,  1, "#f4cccc"),
        ("Wk 6-8  : HTS coil + cryo-CMOS DAC + wiring", 6,  3, "#bbd6f0"),
        ("Wk 9-12 : Photonic data path",                9,  4, "#ead1dc"),
        ("Wk 13-15: Wafer stage + BSE detector",       13,  3, "#fff2cc"),
        ("Wk 16-17: Cool-down, HV ramp, alignment",    16,  2, "#f9cb9c"),
        ("Week 18 : First beam → first exposure",      18,  1, "#fce5cd"),
    ]
    y_positions = list(range(len(tasks), 0, -1))
    for y, (label, start, dur, color) in zip(y_positions, tasks):
        ax.broken_barh([(start, dur)], (y - 0.4, 0.8),
                       facecolors=color, edgecolor="#222", linewidth=1.0)
        ax.text(-0.3, y, label, ha="right", va="center", fontsize=9)

    # milestones
    ax.axvline(x=4, color="red", linestyle="--", linewidth=0.8, alpha=0.5)
    ax.text(4, 11.0, "M1: Vacuum OK", color="red", fontsize=8,
            rotation=90, va="bottom")
    ax.axvline(x=9, color="red", linestyle="--", linewidth=0.8, alpha=0.5)
    ax.text(9, 11.0, "M2: Cryo cold", color="red", fontsize=8,
            rotation=90, va="bottom")
    ax.axvline(x=16, color="red", linestyle="--", linewidth=0.8, alpha=0.5)
    ax.text(16, 11.0, "M3: HV up", color="red", fontsize=8,
            rotation=90, va="bottom")
    ax.axvline(x=19, color="green", linestyle="-", linewidth=1.2, alpha=0.7)
    ax.text(19, 11.0, "M4: First exposure", color="green", fontsize=8,
            rotation=90, va="bottom", fontweight="bold")

    ax.set_xlim(-0.5, 22)
    ax.set_ylim(0.2, 11.5)
    ax.set_xlabel("Weeks from authorisation", fontsize=10)
    ax.set_yticks([])
    ax.set_title("Figure 4. Stage A assembly sequence (build phase, ~18 weeks)\n"
                 "Test campaign of 6 validation experiments follows over Months 5–15.",
                 fontsize=10, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)

    plt.savefig(os.path.join(OUT, "build_fig4_gantt.png"), dpi=200)
    plt.savefig(os.path.join(OUT, "build_fig4_gantt.pdf"))
    plt.close()
    print("wrote build_fig4_gantt.{png,pdf}")


# ---------------------------------------------------------------------
# Figure 5: exploded view of cold-finger payload
# ---------------------------------------------------------------------
def fig_exploded():
    fig, ax = plt.subplots(figsize=(7.0, 8.5))

    items = [
        ("CF flange + bellows interface\n(8\" CF, copper gasket)",       7.0, "#cccccc"),
        ("Copper thermal mass\n(OFHC, ~2 kg, drilled for sensors)",      6.0, "#bbd6f0"),
        ("MLI wrap (warm side only)\n30-layer aluminized Mylar",         5.0, "#eeeeee"),
        ("Cryo-CMOS DAC chip\non Al₂O₃ interposer + Au wire-bond",       4.0, "#d9d2e9"),
        ("InP photodiode tile\n(Hamamatsu G12180 cryo-qualified)",       3.0, "#ead1dc"),
        ("YBCO planar Helmholtz coil pair\non sapphire, soldered leads", 2.0, "#fce5cd"),
        ("YBCO Meissner shield\n(adjacent, 10 μm gap)",                  1.2, "#fff2cc"),
        ("Mechanical alignment jig\n(non-mag stainless, picomotor)",     0.4, "#d9ead3"),
    ]

    for (label, y, color) in items:
        bb = FancyBboxPatch((1.0, y - 0.30), 4.5, 0.60,
                            boxstyle="round,pad=0.04",
                            facecolor=color, edgecolor="#222", linewidth=1.2)
        ax.add_patch(bb)
        ax.text(3.25, y, label, ha="center", va="center", fontsize=8.5)

    # vertical assembly arrow
    ax.annotate("", xy=(0.5, 6.8), xytext=(0.5, 0.5),
                arrowprops=dict(arrowstyle="<-", color="#a64d4d", linewidth=2.0))
    ax.text(0.30, 3.65, "Assembly\norder\n(bottom-up)", fontsize=9, color="#a64d4d",
            ha="center", va="center", rotation=90, fontweight="bold")

    # Right-side notes
    notes = [
        (6.0, "← Heat-strap to PT-90 second stage"),
        (4.0, "← Drives the HTS coil"),
        (3.0, "← Receives the optical pattern stream"),
        (2.0, "← Lithographed at SuperPower / univ clean room"),
        (1.2, "← Empirical 80 dB shield test target"),
    ]
    for (y, note) in notes:
        ax.text(5.7, y, note, fontsize=8, color="#444", va="center")

    ax.set_xlim(-0.5, 10.0)
    ax.set_ylim(-0.2, 7.8)
    ax.set_aspect("auto")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Figure 5. Cold-finger payload — exploded view\n"
                 "(stack-up of items mounted to the 77 K cold finger, bottom-up assembly)",
                 fontsize=10, fontweight="bold")
    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.savefig(os.path.join(OUT, "build_fig5_exploded.png"), dpi=200)
    plt.savefig(os.path.join(OUT, "build_fig5_exploded.pdf"))
    plt.close()
    print("wrote build_fig5_exploded.{png,pdf}")


if __name__ == "__main__":
    fig_bench_layout()
    fig_chamber_section()
    fig_beam_path()
    fig_gantt()
    fig_exploded()
    print("All build manual figures generated.")
