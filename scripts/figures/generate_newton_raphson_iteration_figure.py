"""Generate the one-dimensional Newton--Raphson iteration figure.

Run from the repository root with:

    uv run python scripts/figures/generate_newton_raphson_iteration_figure.py
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import scienceplots  # noqa: F401  # registers the SciencePlots styles


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "articles" / "figures" / "generated"
STEM = "newton-raphson-one-dimensional"

INK = "#172b36"
CURVE = "#0b7285"
TANGENT = "#c44e2b"
ZERO = "#59666d"
ROOT = "#2b8a3e"
GUIDE = "#a8b2b7"
GRID = "#e1e6e9"
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
    title.text = "One-dimensional Newton--Raphson iteration"
    description = ET.Element(
        f"{{{SVG_NAMESPACE}}}desc", {"id": description_id}
    )
    description.text = (
        "The nonlinear function F of x equals exponential x minus three and crosses "
        "zero at the root x star. Starting from x superscript zero, three successive "
        "tangent lines intersect the zero line at x superscript one, two, and three. "
        "All four iterates are directly labelled. Vertical dotted arrows connect "
        "each new estimate to the nonlinear curve, showing the iterates approaching "
        "the marked root at approximately 1.099."
    )
    root.insert(0, description)
    root.insert(0, title)
    tree.write(path, encoding="utf-8", xml_declaration=True)


def main() -> None:
    """Render the Newton iteration figure as SVG and a 300 dpi PNG preview."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def function(value: float | np.ndarray) -> float | np.ndarray:
        return np.exp(value) - 3.0

    def derivative(value: float) -> float:
        return float(np.exp(value))

    iterates = [0.0]
    for _ in range(3):
        current = iterates[-1]
        iterates.append(current - float(function(current)) / derivative(current))

    root = float(np.log(3.0))
    state = np.linspace(-0.15, 2.12, 600)
    function_values = function(state)

    with plt.style.context(["science"]), plt.rc_context(
        {
            "text.usetex": False,
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "font.weight": "normal",
            "mathtext.fontset": "dejavusans",
            "axes.labelsize": 12,
            "axes.labelweight": "bold",
            "xtick.labelsize": 10.5,
            "ytick.labelsize": 10.5,
            "legend.fontsize": 9.5,
            "savefig.bbox": None,
            "svg.fonttype": "path",
        }
    ):
        fig, ax = plt.subplots(figsize=(7.16, 3.5))

        ax.plot(
            state,
            function_values,
            color=CURVE,
            lw=2.8,
            label=r"$F(x)=e^x-3$",
            zorder=3,
        )
        ax.axhline(
            0.0,
            color=ZERO,
            lw=1.8,
            ls=(0, (2, 2)),
            label=r"Zero line, $F(x)=0$",
            zorder=1,
        )

        for iteration, (current, next_state) in enumerate(
            zip(iterates[:-1], iterates[1:])
        ):
            current_value = float(function(current))
            tangent_state = np.linspace(
                min(current, next_state), max(current, next_state), 80
            )
            tangent_value = current_value + derivative(current) * (
                tangent_state - current
            )
            ax.plot(
                tangent_state,
                tangent_value,
                color=TANGENT,
                lw=2.0,
                ls=(0, (6, 3)),
                label="Tangent models" if iteration == 0 else None,
                zorder=4,
            )

            next_value = float(function(next_state))
            ax.annotate(
                "",
                xy=(next_state, next_value),
                xytext=(next_state, 0.0),
                arrowprops={
                    "arrowstyle": "->",
                    "color": GUIDE,
                    "lw": 1.2,
                    "linestyle": (0, (3, 3)),
                },
                zorder=2,
            )

        ax.scatter(
            iterates,
            [function(value) for value in iterates],
            s=58,
            marker="o",
            facecolor="white",
            edgecolor=TANGENT,
            linewidth=2.0,
            zorder=5,
        )
        ax.scatter(
            [root],
            [0.0],
            s=130,
            marker="*",
            facecolor=ROOT,
            edgecolor="white",
            linewidth=0.8,
            zorder=7,
        )

        iterate_label_positions = [
            (0.12, -1.62),
            (1.86, 4.78),
            (1.54, 1.42),
            (1.30, 0.48),
        ]
        for iteration, (current, label_position) in enumerate(
            zip(iterates, iterate_label_positions)
        ):
            ax.annotate(
                rf"$x^{{({iteration})}}$",
                xy=(current, float(function(current))),
                xytext=label_position,
                color=TANGENT,
                fontsize=10.5,
                fontweight="bold",
                ha="center",
                va="center",
                arrowprops={"arrowstyle": "-", "color": TANGENT, "lw": 0.9},
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.88},
                zorder=6,
            )

        ax.annotate(
            r"Root: $x^\star=\ln 3\approx1.099$",
            xy=(root, 0.0),
            xytext=(0.58, 0.62),
            color=ROOT,
            fontsize=10.5,
            fontweight="bold",
            ha="center",
            va="bottom",
            arrowprops={"arrowstyle": "->", "color": ROOT, "lw": 1.2},
        )

        ax.set_xlim(-0.15, 2.12)
        ax.set_ylim(-2.35, 5.45)
        ax.set_xlabel(r"State, $x$ (dimensionless)")
        ax.set_ylabel(r"$F(x)$ (dimensionless)")
        ax.set_xticks([0.0, 0.5, 1.0, 1.5, 2.0])
        ax.set_yticks([-2.0, 0.0, 2.0, 4.0])
        ax.grid(color=GRID, lw=0.8, zorder=0)
        handles, labels = ax.get_legend_handles_labels()
        legend = ax.legend(
            [handles[index] for index in [0, 2, 1]],
            [labels[index] for index in [0, 2, 1]],
            loc="upper left",
            ncols=1,
            frameon=True,
            framealpha=0.97,
            borderpad=0.55,
            labelspacing=0.45,
            handlelength=2.5,
            prop={"family": "DejaVu Sans", "size": 9.5, "weight": "normal"},
        )
        legend.get_frame().set_edgecolor(GRID)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.minorticks_off()
        ax.tick_params(colors=INK, top=False, right=False, width=1.0, length=4)
        for tick_label in [*ax.get_xticklabels(), *ax.get_yticklabels()]:
            tick_label.set_fontweight("normal")
        ax.xaxis.label.set_color(INK)
        ax.yaxis.label.set_color(INK)

        fig.tight_layout(pad=1.0)
        svg_path = OUTPUT_DIR / f"{STEM}.svg"
        png_path = OUTPUT_DIR / f"{STEM}.png"
        fig.savefig(svg_path, transparent=False)
        fig.savefig(png_path, dpi=300, transparent=False)
        plt.close(fig)

    add_svg_accessibility(svg_path)


if __name__ == "__main__":
    main()
