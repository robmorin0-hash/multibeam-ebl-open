"""
Phase 3 publication-quality system diagrams for the Morin v4 multi-beam EBL preprint.

Figure 9: v4 system block diagram (top-to-bottom flowchart with cryogenic zones,
          control loops, and data path).
Figure 10: Photonic data path topology (hierarchical 3-tier).

Pure matplotlib; no external drawing tools.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

# -----------------------------------------------------------------------------
# Global style
# -----------------------------------------------------------------------------
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "font.size": 9,
    "axes.linewidth": 0.8,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

# Color palette
COLOR_CRYO = "#cfe2f3"          # 77 K zone fill
COLOR_CRYO_EDGE = "#1f4e79"     # 77 K zone outline
COLOR_WARM = "#fce5cd"          # 295 K zone fill
COLOR_WARM_EDGE = "#b45f06"     # 295 K zone outline
COLOR_INTERFACE = "#e6d5f2"     # cold-warm gap
COLOR_INTERFACE_EDGE = "#674ea7"
COLOR_DATA = "#0b8043"          # data path green
COLOR_CTRL = "#cc0000"          # control loops
COLOR_BOX_FILL = "#ffffff"
COLOR_BOX_EDGE = "#333333"


def rounded_box(ax, x, y, w, h, text, fc=COLOR_BOX_FILL, ec=COLOR_BOX_EDGE,
                lw=0.9, fontsize=9, fontweight="normal", text_color="black"):
    """Draw a rounded rectangle with centred multi-line text."""
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.15",
        linewidth=lw, edgecolor=ec, facecolor=fc, zorder=2,
    )
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, text,
            ha="center", va="center",
            fontsize=fontsize, fontweight=fontweight, color=text_color,
            zorder=3)
    return (x, y, w, h)


def arrow(ax, x1, y1, x2, y2, color=COLOR_DATA, lw=1.4, style="-|>",
          label=None, label_offset=(0.15, 0), label_fontsize=8,
          linestyle="-", mutation_scale=14):
    a = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle=style, color=color, lw=lw,
        mutation_scale=mutation_scale, linestyle=linestyle, zorder=4,
    )
    ax.add_patch(a)
    if label:
        mx = (x1 + x2) / 2 + label_offset[0]
        my = (y1 + y2) / 2 + label_offset[1]
        ax.text(mx, my, label, fontsize=label_fontsize, color=color,
                ha="left", va="center", zorder=5)


# =============================================================================
# Figure 9: v4 system block diagram
# =============================================================================

def make_figure9(out_pdf, out_png):
    fig, ax = plt.subplots(figsize=(8.5, 11))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 15)
    ax.set_aspect("equal")
    ax.axis("off")

    # ------------------------------------------------------------------------
    # Layout constants
    # ------------------------------------------------------------------------
    # Center column x-axis around x=5
    cx = 5.0
    bw = 5.2   # default box width for column stages
    bh = 0.55  # default box height

    # Top: pattern streamer (small narrow box, upper right area)
    stream_x = cx - 1.6
    stream_y = 12.7
    rounded_box(
        ax, stream_x, stream_y, 3.2, 0.8,
        "Pattern streamer\n(datacenter-class)",
        fc="#ffffff", ec=COLOR_DATA, lw=1.4, fontweight="bold",
    )

    # Photonic transport (wider)
    photo_w = 6.4
    photo_x = cx - photo_w / 2
    photo_y = 11.6
    rounded_box(
        ax, photo_x, photo_y, photo_w, 0.7,
        "Photonic transport  (32 fibers x 96$\\lambda$ x 200 Gbps PAM4)",
        fc="#e6f4ea", ec=COLOR_DATA, lw=1.4, fontweight="bold",
    )

    # Arrow streamer -> photonic, with 50 Tbps label (placed to the right
    # so it doesn't collide with the upper-left legend block)
    arrow(ax, cx, stream_y, cx, photo_y + 0.7,
          color=COLOR_DATA, lw=1.6,
          label="50 Tbps (compressed)",
          label_offset=(0.20, 0), label_fontsize=8)

    # Feedthrough label between photonic and cryo zone
    ax.text(cx + 0.15, 11.15, "via UHV fiber feedthroughs",
            fontsize=7.5, color=COLOR_DATA, ha="left", va="center", style="italic")

    # ------------------------------------------------------------------------
    # 77 K cryogenic zone (large bounding box)
    # ------------------------------------------------------------------------
    cryo_x = cx - 3.4
    cryo_y = 4.4
    cryo_w = 6.8
    cryo_h = 6.4
    cryo_zone = FancyBboxPatch(
        (cryo_x, cryo_y), cryo_w, cryo_h,
        boxstyle="round,pad=0.05,rounding_size=0.2",
        linewidth=2.0, edgecolor=COLOR_CRYO_EDGE, facecolor=COLOR_CRYO,
        zorder=1,
    )
    ax.add_patch(cryo_zone)
    ax.text(cryo_x + 0.25, cryo_y + cryo_h - 0.25, "77 K cryogenic zone",
            fontsize=10.5, fontweight="bold", color=COLOR_CRYO_EDGE,
            ha="left", va="center")

    # Arrow from photonic into cryo zone top
    arrow(ax, cx, photo_y, cx, cryo_y + cryo_h,
          color=COLOR_DATA, lw=1.6)

    # Inner stack (centered on cx)
    inner_w = 4.4
    inner_x = cx - inner_w / 2

    stages = [
        # (y, height, text, fill, edge) -- y is bottom-left corner
        (9.70, 0.55, "In-column receiver tiles\n(cryo InP photodiodes)",
         "#ffffff", COLOR_BOX_EDGE),
        (8.85, 0.55, "Cryo-CMOS DAC array\n($10^{6}$ x 16-bit, GF 22FDX)",
         "#ffffff", COLOR_BOX_EDGE),
        (8.00, 0.55, "MEMS CNT field-emitter array\n($10^{6}$ tips)",
         "#ffffff", COLOR_BOX_EDGE),
        (7.15, 0.45, "Condenser optics (50 kV)",
         "#ffffff", COLOR_BOX_EDGE),
        (6.25, 0.55, "Per-beam YBCO Lorentz\ndeflection coils + Meissner shields",
         "#ffffff", COLOR_BOX_EDGE),
        (5.30, 0.65, "Per-beam blanker array\n(CMOS-MEMS, water-cooled\nstop aperture)",
         "#ffffff", COLOR_BOX_EDGE),
    ]

    # Draw stage boxes and short interconnect arrows
    placed = []
    for (y, h, txt, fc, ec) in stages:
        rounded_box(ax, inner_x, y, inner_w, h, txt, fc=fc, ec=ec, fontsize=8.5)
        placed.append((y, h))

    # Interconnect arrows between stages
    for i in range(len(placed) - 1):
        y_top = placed[i][0]            # bottom of upper box = y
        y_bot_box_top = placed[i+1][0] + placed[i+1][1]  # top of next box
        arrow(ax, cx, y_top, cx, y_bot_box_top,
              color=COLOR_DATA, lw=1.3, mutation_scale=10)

    # Label "e- beams" on arrow between field-emitter (idx 2) and condenser (idx 3)
    y_top_em = placed[2][0]
    y_top_cond = placed[3][0] + placed[3][1]
    ax.text(cx + 0.12, (y_top_em + y_top_cond) / 2, "e$^-$ beams",
            fontsize=7.5, color=COLOR_DATA, ha="left", va="center", style="italic")

    # ------------------------------------------------------------------------
    # Control loop arrows (dashed, red, entering from the right)
    # ------------------------------------------------------------------------
    ctrl_x_start = cryo_x + cryo_w + 0.05   # outside cryo zone
    ctrl_x_target = inner_x + inner_w       # right edge of inner stage boxes

    # 1. Per-tip closed-loop current control -> MEMS CNT field-emitter (stage idx 2)
    y_mems = placed[2][0] + placed[2][1] / 2
    arrow(ax, ctrl_x_start + 1.6, y_mems, ctrl_x_target, y_mems,
          color=COLOR_CTRL, lw=1.1, linestyle="--", mutation_scale=10)
    ax.text(ctrl_x_start + 1.65, y_mems, "Per-tip closed-loop\ncurrent control",
            fontsize=7.5, color=COLOR_CTRL, ha="left", va="center")

    # 2. Inner loop @ 100 kHz -> YBCO deflection (stage idx 4)
    y_ybco = placed[4][0] + placed[4][1] / 2
    arrow(ax, ctrl_x_start + 1.6, y_ybco, ctrl_x_target, y_ybco,
          color=COLOR_CTRL, lw=1.1, linestyle="--", mutation_scale=10)
    ax.text(ctrl_x_start + 1.65, y_ybco, "Inner loop\n@ 100 kHz",
            fontsize=7.5, color=COLOR_CTRL, ha="left", va="center")

    # 3. Middle loop @ 1 kHz -> blanker array (stage idx 5)
    y_blk = placed[5][0] + placed[5][1] / 2
    arrow(ax, ctrl_x_start + 1.6, y_blk, ctrl_x_target, y_blk,
          color=COLOR_CTRL, lw=1.1, linestyle="--", mutation_scale=10)
    ax.text(ctrl_x_start + 1.65, y_blk, "Middle loop\n@ 1 kHz",
            fontsize=7.5, color=COLOR_CTRL, ha="left", va="center")

    # ------------------------------------------------------------------------
    # Cold-warm interface
    # ------------------------------------------------------------------------
    iface_x = cx - 3.0
    iface_y = 3.35
    iface_w = 6.0
    iface_h = 0.75
    rounded_box(
        ax, iface_x, iface_y, iface_w, iface_h,
        "Cold-warm UHV gap (50 mm) | Cryoperm magnetic shield\n"
        "Differential pumping (Pfeiffer HiPace 2300)",
        fc=COLOR_INTERFACE, ec=COLOR_INTERFACE_EDGE, lw=1.4,
        fontsize=8.5, fontweight="bold",
    )

    # Arrow from bottom of cryo zone to interface
    arrow(ax, cx, cryo_y, cx, iface_y + iface_h,
          color=COLOR_DATA, lw=1.4, mutation_scale=12)

    # Arrow from interface to wafer zone (label e- landing)
    arrow(ax, cx, iface_y, cx, 2.85,
          color=COLOR_DATA, lw=1.4, mutation_scale=12)
    ax.text(cx + 0.12, (iface_y + 2.85) / 2, "e$^-$ landing",
            fontsize=7.5, color=COLOR_DATA, ha="left", va="center", style="italic")

    # ------------------------------------------------------------------------
    # 295 K wafer zone
    # ------------------------------------------------------------------------
    warm_x = cx - 3.6
    warm_y = 0.4
    warm_w = 7.2
    warm_h = 2.45
    warm_zone = FancyBboxPatch(
        (warm_x, warm_y), warm_w, warm_h,
        boxstyle="round,pad=0.05,rounding_size=0.2",
        linewidth=2.0, edgecolor=COLOR_WARM_EDGE, facecolor=COLOR_WARM,
        zorder=1,
    )
    ax.add_patch(warm_zone)
    ax.text(warm_x + 0.2, warm_y + warm_h - 0.22, "295 K wafer zone",
            fontsize=10.5, fontweight="bold", color=COLOR_WARM_EDGE,
            ha="left", va="center")

    # Wafer + chuck box
    wafer_x = warm_x + 0.4
    wafer_y = warm_y + 1.20
    wafer_w = 5.2
    wafer_h = 0.75
    rounded_box(
        ax, wafer_x, wafer_y, wafer_w, wafer_h,
        "Wafer (300 mm Si, Inpria resist) on AlN chuck\n"
        "+ 5 Torr He backside + Galden microloop + 36-zone TEC",
        fc="#ffffff", ec=COLOR_BOX_EDGE, lw=0.9, fontsize=8,
    )

    # Stage box
    stage_x = warm_x + 0.4
    stage_y = warm_y + 0.30
    stage_w = 5.2
    stage_h = 0.75
    rounded_box(
        ax, stage_x, stage_y, stage_w, stage_h,
        "6-DOF stage on granite + active pneumatic isolators\n"
        "Zygo ZMI interferometer (0.1 nm/$\\sqrt{\\mathrm{Hz}}$ resolution)",
        fc="#ffffff", ec=COLOR_BOX_EDGE, lw=0.9, fontsize=8,
    )

    # Control arrows into wafer + stage from the right
    ctrl_warm_x_start = warm_x + warm_w + 0.05
    # BSE registration probes -> wafer
    y_w = wafer_y + wafer_h / 2
    arrow(ax, ctrl_warm_x_start + 1.6, y_w, wafer_x + wafer_w, y_w,
          color=COLOR_CTRL, lw=1.1, linestyle="--", mutation_scale=10)
    ax.text(ctrl_warm_x_start + 1.65, y_w,
            "BSE registration probes\n($10^{3}$ of $10^{6}$ beams)",
            fontsize=7.5, color=COLOR_CTRL, ha="left", va="center")

    # Outer loop -> stage
    y_s = stage_y + stage_h / 2
    arrow(ax, ctrl_warm_x_start + 1.6, y_s, stage_x + stage_w, y_s,
          color=COLOR_CTRL, lw=1.1, linestyle="--", mutation_scale=10)
    ax.text(ctrl_warm_x_start + 1.65, y_s,
            "Outer loop\n@ 1-10 Hz\n(mechanical stage)",
            fontsize=7.5, color=COLOR_CTRL, ha="left", va="center")

    # ------------------------------------------------------------------------
    # Legend (placed in upper-left header area, separate from any diagram boxes)
    # ------------------------------------------------------------------------
    legend_handles = [
        mpatches.Patch(facecolor=COLOR_CRYO, edgecolor=COLOR_CRYO_EDGE,
                       label="77 K cryogenic zone"),
        mpatches.Patch(facecolor=COLOR_WARM, edgecolor=COLOR_WARM_EDGE,
                       label="295 K wafer zone"),
        mpatches.Patch(facecolor=COLOR_INTERFACE, edgecolor=COLOR_INTERFACE_EDGE,
                       label="Cold-warm interface"),
        plt.Line2D([0], [0], color=COLOR_DATA, lw=1.6, label="Data / beam path"),
        plt.Line2D([0], [0], color=COLOR_CTRL, lw=1.1, ls="--",
                   label="Control loops"),
    ]
    leg = ax.legend(
        handles=legend_handles, loc="upper left",
        bbox_to_anchor=(0.005, 0.965),
        fontsize=7.5, frameon=True, framealpha=0.95,
        handlelength=1.5, handleheight=1.0, borderpad=0.5,
    )
    leg.get_frame().set_edgecolor("#999999")

    # Title (placed at top, fully above the streamer + legend)
    ax.text(cx, 14.55,
            "v4 multi-beam EBL system block diagram",
            ha="center", va="center",
            fontsize=13, fontweight="bold")

    fig.savefig(out_pdf, bbox_inches="tight", pad_inches=0.15)
    fig.savefig(out_png, bbox_inches="tight", pad_inches=0.15, dpi=220)
    plt.close(fig)


# =============================================================================
# Figure 10: Photonic data path topology
# =============================================================================

def make_figure10(out_pdf, out_png):
    fig, ax = plt.subplots(figsize=(8.5, 11))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 14)
    ax.set_aspect("equal")
    ax.axis("off")

    cx = 5.0

    # Title
    ax.text(cx, 13.6,
            "Photonic data path topology",
            ha="center", va="center",
            fontsize=12, fontweight="bold")
    ax.text(cx, 13.15,
            "Datacenter source -> in-column DACs (3-tier hierarchy)",
            ha="center", va="center", fontsize=9.5, style="italic", color="#555555")

    # --- Tier 0: Datacenter pattern streamer (wide top box)
    t0_w = 7.6
    t0_x = cx - t0_w / 2
    t0_y = 11.6
    rounded_box(
        ax, t0_x, t0_y, t0_w, 0.95,
        "Datacenter pattern streamer (1 PB pre-staged)\n"
        "Hierarchical compression (10x)",
        fc="#e6f4ea", ec=COLOR_DATA, lw=1.5, fontsize=10, fontweight="bold",
    )

    # Bandwidth label below t0
    ax.text(cx, 11.30, "50 Tbps after compression",
            ha="center", va="center", fontsize=8.5,
            color=COLOR_DATA, style="italic")

    # --- Two parallel children: L0 sync + L1+L2
    # L0 sync (left)
    l0_w = 3.0
    l0_x = cx - 3.6
    l0_y = 9.85
    rounded_box(
        ax, l0_x, l0_y, l0_w, 0.95,
        "L0 sync\n1 Gbps frame clock\n(global timing distribution)",
        fc="#ffffff", ec=COLOR_BOX_EDGE, lw=1.0, fontsize=8.5,
    )

    # L1 + L2 (right)
    l1_w = 3.6
    l1_x = cx + 0.6
    l1_y = 9.85
    rounded_box(
        ax, l1_x, l1_y, l1_w, 0.95,
        "L1 + L2  Deflector + Blanker data\n320 Gbps + 50 Tbps\n(deterministic + pattern stream)",
        fc="#ffffff", ec=COLOR_BOX_EDGE, lw=1.0, fontsize=8.5,
    )

    # Branch arrows from t0 to two children
    arrow(ax, cx - 1.0, t0_y, l0_x + l0_w / 2, l0_y + 0.95,
          color=COLOR_DATA, lw=1.4)
    arrow(ax, cx + 1.0, t0_y, l1_x + l1_w / 2, l1_y + 0.95,
          color=COLOR_DATA, lw=1.4)

    # --- Merge into trunk box (Tier 1: 32 trunks)
    t1_w = 6.8
    t1_x = cx - t1_w / 2
    t1_y = 7.85
    rounded_box(
        ax, t1_x, t1_y, t1_w, 1.10,
        "32 single-mode trunks\n"
        "96 wavelengths x 200 Gbps PAM4\n"
        "= 19.2 Tbps per trunk    |    608 Tbps raw (12% loaded)",
        fc="#fff2cc", ec="#bf9000", lw=1.4, fontsize=9, fontweight="bold",
    )

    # Merge arrows
    arrow(ax, l0_x + l0_w / 2, l0_y, cx - 0.8, t1_y + 1.10,
          color=COLOR_DATA, lw=1.4)
    arrow(ax, l1_x + l1_w / 2, l1_y, cx + 0.8, t1_y + 1.10,
          color=COLOR_DATA, lw=1.4)

    # --- Feedthrough annotation
    ax.text(cx, 7.55,
            "UHV fiber feedthroughs (Accu-Glass, Thorlabs)",
            ha="center", va="center", fontsize=8.5,
            color=COLOR_DATA, style="italic")

    # --- Tier 2a: In-column receiver tiles @ 77 K
    t2_w = 6.8
    t2_x = cx - t2_w / 2
    t2_y = 6.0
    rounded_box(
        ax, t2_x, t2_y, t2_w, 1.10,
        "In-column receiver tiles @ 77 K\n"
        "Cryo InP photodiode arrays\n"
        "(32 tiles x ~1.5 W each = 48 W optical-to-electrical)",
        fc=COLOR_CRYO, ec=COLOR_CRYO_EDGE, lw=1.4, fontsize=9,
    )

    arrow(ax, cx, t1_y, cx, t2_y + 1.10, color=COLOR_DATA, lw=1.5)
    ax.text(cx + 0.15, (t1_y + t2_y + 1.10) / 2, "608 Tbps raw",
            fontsize=7.5, color=COLOR_DATA, ha="left", va="center", style="italic")

    # --- Tier 2b: Per-tile cryo-CMOS decode/buffer
    t3_w = 6.8
    t3_x = cx - t3_w / 2
    t3_y = 4.10
    rounded_box(
        ax, t3_x, t3_y, t3_w, 1.10,
        "Per-tile cryo-CMOS decode / buffer\n"
        "GF 22FDX FD-SOI, 1024 channels/tile\n"
        "1000 tiles total (32 photonic tiles -> 1000 electrical tiles)",
        fc=COLOR_CRYO, ec=COLOR_CRYO_EDGE, lw=1.4, fontsize=9,
    )

    arrow(ax, cx, t2_y, cx, t3_y + 1.10, color=COLOR_DATA, lw=1.5)
    ax.text(cx + 0.15, (t2_y + t3_y + 1.10) / 2, "Electrical fan-out",
            fontsize=7.5, color=COLOR_DATA, ha="left", va="center", style="italic")

    # --- Tier 3: 10^6 cryo-CMOS DACs
    t4_w = 6.8
    t4_x = cx - t4_w / 2
    t4_y = 2.20
    rounded_box(
        ax, t4_x, t4_y, t4_w, 1.10,
        "$10^{6}$ x 16-bit cryo-CMOS DACs\n"
        "Imec + Fraunhofer IPMS (dual-source)\n"
        "100 $\\mu$W each, 100 W total -> per-beam current shaping",
        fc=COLOR_CRYO, ec=COLOR_CRYO_EDGE, lw=1.4, fontsize=9, fontweight="bold",
    )

    arrow(ax, cx, t3_y, cx, t4_y + 1.10, color=COLOR_DATA, lw=1.5)
    ax.text(cx + 0.15, (t3_y + t4_y + 1.10) / 2, "Per-channel routing",
            fontsize=7.5, color=COLOR_DATA, ha="left", va="center", style="italic")

    # --- Sink annotation under final tier
    ax.text(cx, 1.85,
            "-> MEMS CNT field-emitter array ($10^{6}$ tips, 50 kV)",
            ha="center", va="center", fontsize=8.5, color=COLOR_DATA,
            style="italic")

    # --- Right-hand tier annotations
    tier_label_x = 9.65
    for (y, txt) in [
        (12.1, "Tier 0\n(warm,\ndatacenter)"),
        (8.4, "Tier 1\n(photonic\ntrunk)"),
        (6.55, "Tier 2a\n(77 K\nO/E)"),
        (4.65, "Tier 2b\n(77 K\ndecode)"),
        (2.75, "Tier 3\n(77 K\nDAC array)"),
    ]:
        ax.text(tier_label_x, y, txt,
                ha="right", va="center", fontsize=7.5,
                color="#555555", fontweight="bold")

    # --- Left-hand cumulative bandwidth annotations
    bw_label_x = 0.35
    for (y, txt, col) in [
        (12.1, "500 Tbps\nuncompressed", "#888888"),
        (10.3, "50 Tbps\npost-compression", COLOR_DATA),
        (8.4, "608 Tbps\nraw photonic\n(headroom 8x)", "#bf9000"),
        (6.55, "Optical -> electrical", COLOR_CRYO_EDGE),
        (4.65, "1024 ch/tile\n1024 Mbps avg", COLOR_CRYO_EDGE),
        (2.75, "16 bit @\n~100 MS/s/beam", COLOR_CRYO_EDGE),
    ]:
        ax.text(bw_label_x, y, txt,
                ha="left", va="center", fontsize=7.5,
                color=col, style="italic")

    # --- Legend
    legend_handles = [
        mpatches.Patch(facecolor="#e6f4ea", edgecolor=COLOR_DATA,
                       label="Warm datacenter source"),
        mpatches.Patch(facecolor="#fff2cc", edgecolor="#bf9000",
                       label="Photonic trunk (room temp -> cryo)"),
        mpatches.Patch(facecolor=COLOR_CRYO, edgecolor=COLOR_CRYO_EDGE,
                       label="77 K cryogenic zone"),
        plt.Line2D([0], [0], color=COLOR_DATA, lw=1.5,
                   label="Data flow"),
    ]
    leg = ax.legend(
        handles=legend_handles, loc="lower left",
        bbox_to_anchor=(0.005, 0.005),
        fontsize=7.5, frameon=True, framealpha=0.95,
        handlelength=1.5, handleheight=1.0, borderpad=0.5,
    )
    leg.get_frame().set_edgecolor("#999999")

    fig.savefig(out_pdf, bbox_inches="tight", pad_inches=0.15)
    fig.savefig(out_png, bbox_inches="tight", pad_inches=0.15, dpi=220)
    plt.close(fig)


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    base = "/home/thedoctor/mbm_spacecharge"
    make_figure9(f"{base}/figure_phase3_block_diagram.pdf",
                 f"{base}/figure_phase3_block_diagram.png")
    print("Figure 9 (block diagram) written.")

    make_figure10(f"{base}/figure_phase3_datapath.pdf",
                  f"{base}/figure_phase3_datapath.png")
    print("Figure 10 (data path topology) written.")
