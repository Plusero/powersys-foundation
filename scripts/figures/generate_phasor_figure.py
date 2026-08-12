"""Generate the geometric phasor figure used by the AC-circuits tutorial.

Run from the repository root with:

    uv run --with matplotlib --with SciencePlots python \
        scripts/figures/generate_phasor_figure.py
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import scienceplots  # noqa: F401  # registers the SciencePlots styles
from matplotlib.patches import Arc, FancyArrowPatch


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "articles" / "figures" / "generated"
STEM = "phasor-geometry"

INK = "#172b36"
ACCENT = "#0b7285"
MUTED = "#77858c"
GUIDE = "#a8b2b7"
SVG_NAMESPACE = "http://www.w3.org/2000/svg"


def add_svg_accessibility(path: Path) -> None:
    """Add an accessible title and description to a generated SVG."""
    ET.register_namespace("", SVG_NAMESPACE)
    ET.register_namespace("cc", "http://creativecommons.org/ns#")
    ET.register_namespace("dc", "http://purl.org/dc/elements/1.1/")
    ET.register_namespace("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
    tree = ET.parse(path)
    root = tree.getroot()
    title_id = f"{STEM}-title"
    description_id = f"{STEM}-description"
    root.set("role", "img")
    root.set("aria-labelledby", f"{title_id} {description_id}")

    title = ET.Element(f"{{{SVG_NAMESPACE}}}title", {"id": title_id})
    title.text = "Geometric interpretation of a voltage phasor"
    description = ET.Element(
        f"{{{SVG_NAMESPACE}}}desc", {"id": description_id}
    )
    description.text = (
        "A fixed voltage phasor is drawn as an arrow in the complex plane. "
        "Its length is the RMS magnitude V and its angle from the positive "
        "real axis is theta sub v. Its dashed horizontal projection is V "
        "cosine theta sub v, and its dashed vertical projection is V sine "
        "theta sub v. A light curved arrow is labelled omega."
    )
    root.insert(0, description)
    root.insert(0, title)
    tree.write(path, encoding="utf-8", xml_declaration=True)


def main() -> None:
    """Render the phasor figure as SVG and a 300 dpi PNG preview."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    theta = np.deg2rad(35.0)
    magnitude = 1.0
    x_tip = magnitude * np.cos(theta)
    y_tip = magnitude * np.sin(theta)

    with plt.style.context(["science"]), plt.rc_context(
        {
            "text.usetex": False,
            "font.family": "DejaVu Sans",
            "mathtext.fontset": "dejavusans",
            "savefig.bbox": None,
            "svg.fonttype": "none",
        }
    ):
        fig, ax = plt.subplots(figsize=(3.5, 2.6))

        ax.annotate(
            "",
            xy=(1.28, 0.0),
            xytext=(-0.08, 0.0),
            arrowprops={"arrowstyle": "->", "color": INK, "lw": 1.1},
        )
        ax.annotate(
            "",
            xy=(0.0, 1.17),
            xytext=(0.0, -0.08),
            arrowprops={"arrowstyle": "->", "color": INK, "lw": 1.1},
        )
        ax.text(1.27, -0.035, r"$\mathrm{Re}$", ha="right", va="top", fontsize=9)
        ax.text(-0.035, 1.15, r"$\mathrm{Im}$", ha="right", va="top", fontsize=9)

        ax.plot([x_tip, x_tip], [0.0, y_tip], ls="--", lw=0.9, color=GUIDE)
        ax.plot([0.0, x_tip], [y_tip, y_tip], ls="--", lw=0.9, color=GUIDE)
        ax.text(
            x_tip / 2.0,
            -0.12,
            r"$\mathrm{Re}\{\underline{V}\}=V\cos\theta_v$",
            color=MUTED,
            ha="center",
            va="top",
            fontsize=7.0,
        )
        ax.text(
            x_tip + 0.14,
            y_tip / 2.0,
            r"$\mathrm{Im}\{\underline{V}\}=V\sin\theta_v$",
            color=MUTED,
            ha="center",
            va="center",
            rotation=90,
            fontsize=7.0,
        )

        ax.annotate(
            "",
            xy=(x_tip, y_tip),
            xytext=(0.0, 0.0),
            arrowprops={"arrowstyle": "-|>", "color": ACCENT, "lw": 2.4},
        )
        ax.text(
            0.43,
            0.35,
            r"$|\underline{V}|=V$",
            color=ACCENT,
            ha="center",
            va="bottom",
            rotation=35,
            fontsize=8.5,
        )
        ax.text(
            x_tip + 0.025,
            y_tip + 0.025,
            r"$\underline{V}$",
            color=ACCENT,
            ha="left",
            va="bottom",
            fontsize=9,
        )

        angle_arc = Arc(
            (0.0, 0.0),
            width=0.58,
            height=0.58,
            theta1=0.0,
            theta2=np.rad2deg(theta),
            color=INK,
            lw=1.1,
        )
        ax.add_patch(angle_arc)
        ax.text(0.17, 0.045, r"$\theta_v$", color=INK, ha="center")

        rotation_arc = FancyArrowPatch(
            (1.08, 0.44),
            (0.31, 1.08),
            connectionstyle="arc3,rad=0.42",
            arrowstyle="-|>",
            mutation_scale=8,
            lw=1.0,
            ls=(0, (3, 2)),
            color=MUTED,
        )
        ax.add_patch(rotation_arc)
        ax.text(
            0.72,
            1.07,
            r"$\omega$",
            color=MUTED,
            ha="center",
            va="bottom",
            fontsize=9.0,
        )

        ax.set_xlim(-0.12, 1.34)
        ax.set_ylim(-0.25, 1.23)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

        fig.tight_layout()
        svg_path = OUTPUT_DIR / f"{STEM}.svg"
        png_path = OUTPUT_DIR / f"{STEM}.png"
        fig.savefig(svg_path, transparent=False)
        fig.savefig(png_path, dpi=300, transparent=False)
        plt.close(fig)

    add_svg_accessibility(svg_path)


if __name__ == "__main__":
    main()
