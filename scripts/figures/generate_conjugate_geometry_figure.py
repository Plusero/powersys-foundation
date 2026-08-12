"""Generate the complex-conjugate geometry figure for the AC tutorial.

Run from the repository root with:

    uv run --with matplotlib --with SciencePlots python \
        scripts/figures/generate_conjugate_geometry_figure.py
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
STEM = "complex-conjugate-geometry"

INK = "#172b36"
ORIGINAL = "#0b7285"
CONJUGATE = "#c44e2b"
MUTED = "#77858c"
GUIDE = "#a8b2b7"
SVG_NAMESPACE = "http://www.w3.org/2000/svg"


def add_svg_accessibility(path: Path) -> None:
    """Add an accessible title and description to the generated SVG."""
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
    title.text = "Geometric interpretation of a complex conjugate"
    description = ET.Element(
        f"{{{SVG_NAMESPACE}}}desc", {"id": description_id}
    )
    description.text = (
        "The complex number z equals a plus j b and is drawn above the real "
        "axis at angle theta. Its conjugate z star equals a minus j b and is "
        "drawn below the real axis at angle minus theta. The arrows have equal "
        "length and the same real component a, while their imaginary "
        "components are plus b and minus b. A vertical double arrow indicates "
        "reflection across the real axis."
    )
    root.insert(0, description)
    root.insert(0, title)
    tree.write(path, encoding="utf-8", xml_declaration=True)


def main() -> None:
    """Render the conjugate geometry as SVG and a 300 dpi PNG preview."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    theta_deg = 35.0
    theta = np.deg2rad(theta_deg)
    magnitude = 0.90
    real_component = magnitude * np.cos(theta)
    imaginary_component = magnitude * np.sin(theta)
    z_tip = np.array([real_component, imaginary_component])
    conjugate_tip = np.array([real_component, -imaginary_component])

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

        # Complex-plane axes; the real axis is also the reflection line.
        ax.annotate(
            "",
            xy=(1.26, 0.0),
            xytext=(-0.08, 0.0),
            arrowprops={"arrowstyle": "->", "color": INK, "lw": 1.1},
        )
        ax.annotate(
            "",
            xy=(0.0, 0.93),
            xytext=(0.0, -0.93),
            arrowprops={"arrowstyle": "->", "color": INK, "lw": 1.1},
        )
        ax.text(1.24, -0.035, r"$\mathrm{Re}$", ha="right", va="top", fontsize=9)
        ax.text(-0.035, 0.91, r"$\mathrm{Im}$", ha="right", va="top", fontsize=9)

        # The original number and its conjugate have equal lengths.
        ax.annotate(
            "",
            xy=z_tip,
            xytext=(0.0, 0.0),
            arrowprops={"arrowstyle": "-|>", "color": ORIGINAL, "lw": 2.4},
        )
        ax.annotate(
            "",
            xy=conjugate_tip,
            xytext=(0.0, 0.0),
            arrowprops={"arrowstyle": "-|>", "color": CONJUGATE, "lw": 2.4},
        )
        ax.text(
            0.08,
            0.69,
            r"$z=a+\mathrm{j}b=|z|\angle\theta$",
            color=ORIGINAL,
            ha="left",
            va="center",
            fontsize=8.0,
        )
        ax.text(
            0.08,
            -0.69,
            r"$z^*=a-\mathrm{j}b=|z|\angle(-\theta)$",
            color=CONJUGATE,
            ha="left",
            va="center",
            fontsize=8.0,
        )

        # Component projections show that only the imaginary sign changes.
        ax.plot(
            [real_component, real_component],
            [-imaginary_component, imaginary_component],
            ls=(0, (3, 2)),
            lw=0.9,
            color=GUIDE,
        )
        ax.text(0.54, -0.07, r"$a$", color=MUTED, ha="center")
        ax.text(
            real_component + 0.035,
            imaginary_component / 2.0,
            r"$+b$",
            color=MUTED,
            ha="left",
            va="center",
            fontsize=8.0,
        )
        ax.text(
            real_component + 0.035,
            -imaginary_component / 2.0,
            r"$-b$",
            color=MUTED,
            ha="left",
            va="center",
            fontsize=8.0,
        )

        # Opposite angle arcs make the sign reversal explicit.
        angle_radius = 0.32
        ax.add_patch(
            Arc(
                (0.0, 0.0),
                2 * angle_radius,
                2 * angle_radius,
                theta1=0.0,
                theta2=theta_deg,
                color=INK,
                lw=1.0,
            )
        )
        ax.add_patch(
            Arc(
                (0.0, 0.0),
                2 * angle_radius,
                2 * angle_radius,
                theta1=-theta_deg,
                theta2=0.0,
                color=INK,
                lw=1.0,
            )
        )
        # Anchor labels next to the real axis, clear of both phasor rays.
        ax.text(
            0.22,
            0.025,
            r"$+\theta$",
            color=INK,
            ha="center",
            va="bottom",
            fontsize=8.0,
        )
        ax.text(
            0.22,
            -0.025,
            r"$-\theta$",
            color=INK,
            ha="center",
            va="top",
            fontsize=8.0,
        )

        # A double arrow identifies the mirror relationship.
        reflection = FancyArrowPatch(
            (0.96, 0.48),
            (0.96, -0.48),
            arrowstyle="<->",
            mutation_scale=8,
            lw=1.0,
            ls=(0, (3, 2)),
            color=MUTED,
        )
        ax.add_patch(reflection)
        ax.text(
            0.96,
            0.61,
            "reflection",
            color=MUTED,
            ha="center",
            va="center",
            fontsize=7.0,
        )

        ax.set_xlim(-0.11, 1.29)
        ax.set_ylim(-0.97, 0.97)
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
