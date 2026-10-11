"""Figures for the PIDS-Bench post. Every number is copied from the paper:
cover   -> Table 10 (DeBERTa-v3-FT, five-seed means, tau = 0.5)
fig-sweep -> Section 6.2 (lowest externally-sourced hard-benign FPR with F1 >= 0.95, five seeds)
Style follows the ipi-harness cover: warm paper background, navy text, rust for "blocked".
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
OUT.mkdir(parents=True, exist_ok=True)

BG, NAVY, RUST, LABEL, MUTED, RULE = "#F5F1E8", "#1E2230", "#C0401A", "#7A7266", "#C9C1B3", "#DDD6C8"
family = "Inter" if any("Inter" in f.name for f in font_manager.fontManager.ttflist) else "DejaVu Sans"
plt.rcParams.update({"font.family": family, "text.color": NAVY, "axes.edgecolor": NAVY})


def cover(path):
    fig = plt.figure(figsize=(12, 6.3), dpi=200, facecolor=BG)  # 2400 x 1260 px
    ax = fig.add_axes([0.06, 0.33, 0.88, 0.50], facecolor=BG)

    groups = ["Prompts we wrote\n(curated, 600)", "Prompts we did not write\n(public datasets, 872)"]
    before, after = [48.13, 31.44], [0.10, 31.01]
    x, w = [0, 1.15], 0.36
    for xi, b, a in zip(x, before, after):
        ax.bar(xi - w / 2 - 0.02, b, w, color=MUTED, zorder=2)
        ax.bar(xi + w / 2 + 0.02, a, w, color=RUST, zorder=2)
        ax.text(xi - w / 2 - 0.02, b + 1.2, f"{b:.1f}%", ha="center", va="bottom", fontsize=17, color=LABEL)
        ax.text(xi + w / 2 + 0.02, a + 1.2, f"{a:.1f}%", ha="center", va="bottom", fontsize=17,
                color=RUST, fontweight="bold")
    ax.set_xticks(x, groups, fontsize=15, color=NAVY)
    ax.set_ylim(0, 58)
    ax.set_xlim(-0.55, 1.75)
    ax.set_yticks([])
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(RULE)
    ax.tick_params(axis="x", length=0, pad=10)

    fig.text(0.06, 0.92, "HARMLESS SECURITY-RELATED PROMPTS BLOCKED BY DeBERTa-v3-FT",
             fontsize=13, color=LABEL, fontweight="semibold")
    fig.text(0.06, 0.875, "■", fontsize=14, color=MUTED)
    fig.text(0.08, 0.875, "before", fontsize=13, color=LABEL)
    fig.text(0.155, 0.875, "■", fontsize=14, color=RUST)
    fig.text(0.175, 0.875, "after training on 419 extra harmless examples", fontsize=13, color=LABEL)

    fig.add_artist(plt.Line2D([0.06, 0.94], [0.205, 0.205], color=RULE, lw=1.5))
    fig.text(0.06, 0.105, "Extra training cleared the prompts we wrote.", fontsize=30,
             fontweight="bold", color=NAVY)
    fig.text(0.06, 0.035, "The prompts we didn't write were still blocked.", fontsize=30,
             fontweight="bold", color=RUST)
    fig.text(0.94, 0.92, "five-seed means · threshold 0.5", fontsize=12, color=LABEL, ha="right")
    fig.savefig(path, facecolor=BG)
    plt.close(fig)


def sweep(path):
    fig = plt.figure(figsize=(8, 3.6), dpi=200, facecolor=BG)  # 1600 x 720 px
    ax = fig.add_axes([0.2, 0.2, 0.74, 0.62], facecolor=BG)
    models = ["TF-IDF + LR", "DistilBERT", "DeBERTa-v3-FT"]
    best = [24.1, 27.7, 22.6]
    sd = [0, 9.9, 5.8]
    y = range(len(models))
    ax.barh(y, best, height=0.55, color=RUST, zorder=2)
    for yi, b, s in zip(y, best, sd):
        if s:
            ax.errorbar(b, yi, xerr=s, fmt="none", ecolor=NAVY, elinewidth=1.2, capsize=4, zorder=3)
        label = f"{b:.1f}%" + (f" ± {s:.1f}" if s else "")
        ax.text(b + s + 1.0, yi, label, va="center", fontsize=10.5, color=NAVY)
    ax.axvline(10, color=NAVY, ls=(0, (4, 3)), lw=1.2, zorder=1)
    ax.text(10.6, 2.48, "the 10% we were aiming for", fontsize=10, color=NAVY, va="bottom")
    ax.set_yticks(list(y), models, fontsize=11)
    ax.set_xlim(0, 50)
    ax.set_ylim(-0.5, 2.9)
    ax.set_xticks([0, 10, 20, 30, 40, 50], ["0%", "10%", "20%", "30%", "40%", "50%"], fontsize=10, color=LABEL)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(RULE)
    ax.tick_params(axis="both", length=0)
    fig.text(0.2, 0.9, "LOWEST BLOCK RATE ON PUBLIC-DATASET PROMPTS WITH F1 STILL ≥ 0.95",
             fontsize=10, color=LABEL, fontweight="semibold")
    fig.savefig(path, facecolor=BG)
    plt.close(fig)


cover(OUT / "cover.png")
sweep(OUT / "fig-sweep.png")
print("wrote", OUT / "cover.png", OUT / "fig-sweep.png")
