"""Generate the 90-degree phase-delay figure for the AC-circuits tutorial.

Run from the repository root with:

    uv run --with matplotlib --with SciencePlots python \
        scripts/figures/generate_phase_delay_figure.py
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import numpy as np
import scienceplots  # noqa: F401  # registers the SciencePlots styles
from matplotlib.patches import Arc, FancyArrowPatch


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "articles" / "figures" / "generated"
STEM = "phasor-integral-phase-delay"

INK = "#172b36"
INPUT = "#0b7285"
INTEGRAL = "#c44e2b"
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
    title.text = "Division by j delays a phasor by 90 degrees"
    description = ET.Element(
        f"{{{SVG_NAMESPACE}}}desc", {"id": description_id}
    )
    description.text = (
        "The input phasor X is an arrow at angle theta. A clockwise arc arrow "
        "labelled divide by j and a right-angle marker show the phase delay of "
        "90 degrees. A dot at the same radius marks minus jX, equal to X "
        "divided by j, and demonstrates that division by j does not change "
        "magnitude. The integral phasor X divided by j omega lies on the same "
        "ray at angle theta minus 90 degrees and has magnitude equal to the "
        "magnitude of X divided by omega."
    )
    root.insert(0, description)
    root.insert(0, title)
    tree.write(path, encoding="utf-8", xml_declaration=True)


def main() -> None:
    """Render the phase-delay figure as SVG and a 300 dpi PNG preview."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    theta_deg = 75.0
    integral_angle_deg = theta_deg - 90.0
    theta = np.deg2rad(theta_deg)
    integral_angle = np.deg2rad(integral_angle_deg)
    input_magnitude = 0.78
    integral_magnitude = 0.53

    x_tip = input_magnitude * np.array([np.cos(theta), np.sin(theta)])
    minus_jx_tip = input_magnitude * np.array(
        [np.cos(integral_angle), np.sin(integral_angle)]
    )
    integral_tip = integral_magnitude * np.array(
        [np.cos(integral_angle), np.sin(integral_angle)]
    )

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

        # Complex-plane axes.
        ax.annotate(
            "",
            xy=(1.24, 0.0),
            xytext=(-0.08, 0.0),
            arrowprops={"arrowstyle": "->", "color": INK, "lw": 1.1},
        )
        ax.annotate(
            "",
            xy=(0.0, 1.02),
            xytext=(0.0, -0.53),
            arrowprops={"arrowstyle": "->", "color": INK, "lw": 1.1},
        )
        ax.text(1.22, -0.035, r"$\mathrm{Re}$", ha="right", va="top", fontsize=9)
        ax.text(-0.035, 1.00, r"$\mathrm{Im}$", ha="right", va="top", fontsize=9)

        # Original phasor.
        ax.annotate(
            "",
            xy=x_tip,
            xytext=(0.0, 0.0),
            arrowprops={"arrowstyle": "-|>", "color": INPUT, "lw": 2.4},
        )
        ax.text(
            x_tip[0] + 0.025,
            x_tip[1] + 0.01,
            r"$\underline{X}=|\underline{X}|\angle\theta$",
            color=INPUT,
            ha="left",
            va="bottom",
            fontsize=8.0,
        )

        # A square-corner mark shows that the two phasor directions are 90° apart.
        input_direction = np.array([np.cos(theta), np.sin(theta)])
        integral_direction = np.array(
            [np.cos(integral_angle), np.sin(integral_angle)]
        )
        marker_size = 0.09
        right_angle_points = marker_size * np.vstack(
            [
                input_direction,
                input_direction + integral_direction,
                integral_direction,
            ]
        )
        (right_angle,) = ax.plot(
            right_angle_points[:, 0],
            right_angle_points[:, 1],
            color=MUTED,
            lw=1.25,
            solid_capstyle="butt",
            zorder=6,
        )
        right_angle.set_path_effects(
            [
                path_effects.Stroke(linewidth=3.2, foreground="white"),
                path_effects.Normal(),
            ]
        )
        # A directional inner arc shows the clockwise division by j.
        operation_radius = 0.47
        operation_arc = FancyArrowPatch(
            operation_radius * input_direction,
            operation_radius * integral_direction,
            connectionstyle="arc3,rad=-0.50",
            arrowstyle="-|>",
            mutation_scale=8,
            lw=1.1,
            color=MUTED,
            zorder=5,
        )
        ax.add_patch(operation_arc)
        ax.text(
            0.43,
            0.23,
            r"$\div\,\mathrm{j}$",
            color=MUTED,
            ha="center",
            va="center",
            fontsize=8.0,
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.8},
        )

        # X/j has the same radius as X; division by omega then scales that radius.
        equal_magnitude_arc = Arc(
            (0.0, 0.0),
            width=2 * input_magnitude,
            height=2 * input_magnitude,
            theta1=integral_angle_deg,
            theta2=theta_deg,
            ls=(0, (3, 2)),
            lw=0.9,
            color=GUIDE,
        )
        ax.add_patch(equal_magnitude_arc)
        ax.plot(
            minus_jx_tip[0],
            minus_jx_tip[1],
            marker="o",
            ms=4.5,
            color=MUTED,
            zorder=4,
        )
        ax.text(
            minus_jx_tip[0] + 0.025,
            minus_jx_tip[1] + 0.01,
            r"$-\mathrm{j}\underline{X}=\underline{X}/\mathrm{j}$",
            color=MUTED,
            ha="left",
            va="bottom",
            fontsize=8.0,
        )
        ax.text(
            0.64,
            0.43,
            r"same length $|\underline{X}|$",
            color=MUTED,
            ha="center",
            va="center",
            fontsize=7.0,
            rotation=23,
        )

        # The integral phasor is collinear with X/j but scaled by 1/omega.
        ax.annotate(
            "",
            xy=integral_tip,
            xytext=(0.0, 0.0),
            arrowprops={"arrowstyle": "-|>", "color": INTEGRAL, "lw": 2.4},
            zorder=3,
        )
        ax.text(
            0.48,
            -0.22,
            r"$\underline{X}/(\mathrm{j}\omega)$",
            color=INTEGRAL,
            ha="right",
            va="center",
            fontsize=9.0,
        )
        ax.text(
            0.77,
            -0.36,
            r"angle $\theta-90^\circ$",
            color=INTEGRAL,
            ha="center",
            va="center",
            fontsize=7.0,
        )
        ax.text(
            0.77,
            -0.46,
            r"magnitude $|\underline{X}|/\omega$",
            color=INTEGRAL,
            ha="center",
            va="center",
            fontsize=7.0,
        )

        ax.set_xlim(-0.11, 1.28)
        ax.set_ylim(-0.56, 1.05)
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
