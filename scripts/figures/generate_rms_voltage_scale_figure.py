"""Generate the to-scale RMS and peak voltage figure.

Run from the repository root with:

    uv run python scripts/figures/generate_rms_voltage_scale_figure.py
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import scienceplots  # noqa: F401  # registers the SciencePlots styles


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "articles" / "figures" / "generated"
STEM = "rms-voltage-scale"

INK = "#172b36"
WAVEFORM = "#0b7285"
RMS_GUIDE = "#c44e2b"
GRID = "#d7dee2"
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
    title.text = "RMS and peak scales of a 230 volt RMS sinusoid"
    description = ET.Element(
        f"{{{SVG_NAMESPACE}}}desc", {"id": description_id}
    )
    description.text = (
        "One period of a sinusoidal voltage is plotted against a voltage axis. "
        "Dashed horizontal lines mark plus and minus 230 volts RMS. The waveform "
        "reaches plus and minus 230 times the square root of two, approximately "
        "plus and minus 325.3 volts."
    )
    root.insert(0, description)
    root.insert(0, title)
    tree.write(path, encoding="utf-8", xml_declaration=True)


def main() -> None:
    """Render the voltage scale figure as SVG and a 300 dpi PNG preview."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    rms_voltage = 230.0
    peak_voltage = rms_voltage * np.sqrt(2.0)
    phase = np.linspace(0.0, 2.0 * np.pi, 1001)
    voltage = peak_voltage * np.sin(phase)

    with plt.style.context(["science"]), plt.rc_context(
        {
            "text.usetex": False,
            "font.family": "DejaVu Sans",
            "font.size": 11,
            "mathtext.fontset": "dejavusans",
            "axes.labelsize": 12,
            "axes.labelweight": "bold",
            "xtick.labelsize": 11,
            "ytick.labelsize": 11,
            "legend.fontsize": 10,
            "savefig.bbox": None,
            "svg.fonttype": "none",
        }
    ):
        fig, ax = plt.subplots(figsize=(7.16, 4.0))

        ax.plot(
            phase,
            voltage,
            color=WAVEFORM,
            lw=2.8,
            label="Sinusoidal voltage",
            zorder=3,
        )
        ax.axhline(
            rms_voltage,
            color=RMS_GUIDE,
            lw=1.8,
            ls=(0, (5, 3)),
            label="RMS reference levels",
            zorder=2,
        )
        ax.axhline(
            -rms_voltage,
            color=RMS_GUIDE,
            lw=1.8,
            ls=(0, (5, 3)),
            zorder=2,
        )

        ax.annotate(
            "Vₚₖ = 230√2 ≈ 325.3 V",
            xy=(np.pi / 2.0, peak_voltage),
            xytext=(np.pi / 2.0, 390.0),
            ha="center",
            va="bottom",
            color=INK,
            fontsize=11,
            fontweight="bold",
            arrowprops={"arrowstyle": "-", "color": INK, "lw": 1.1},
        )
        ax.annotate(
            "−Vₚₖ = −230√2 ≈ −325.3 V",
            xy=(3.0 * np.pi / 2.0, -peak_voltage),
            xytext=(3.0 * np.pi / 2.0, -390.0),
            ha="center",
            va="top",
            color=INK,
            fontsize=11,
            fontweight="bold",
            arrowprops={"arrowstyle": "-", "color": INK, "lw": 1.1},
        )

        ax.set_xlim(0.0, 2.0 * np.pi)
        ax.set_ylim(-475.0, 475.0)
        ax.set_xlabel(r"Phase angle, $\omega t$ (rad)")
        ax.set_ylabel(r"Instantaneous voltage, $v(t)$ (V)")
        ax.set_xticks(
            [0.0, np.pi / 2.0, np.pi, 3.0 * np.pi / 2.0, 2.0 * np.pi],
            [r"$0$", r"$\pi/2$", r"$\pi$", r"$3\pi/2$", r"$2\pi$"],
        )
        ax.set_yticks(
            [-peak_voltage, -rms_voltage, 0.0, rms_voltage, peak_voltage],
            [r"$-325.3$", r"$-230$", r"$0$", r"$230$", r"$325.3$"],
        )
        ax.grid(axis="y", color=GRID, lw=0.9, zorder=0)
        legend = ax.legend(
            loc="upper right",
            frameon=True,
            framealpha=0.96,
            borderpad=0.7,
            labelspacing=0.6,
            handlelength=3.0,
            prop={"family": "DejaVu Sans", "size": 10, "weight": "bold"},
        )
        legend.get_frame().set_edgecolor(GRID)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.minorticks_off()
        ax.tick_params(colors=INK, top=False, right=False, width=1.1, length=4)
        for tick_label in [*ax.get_xticklabels(), *ax.get_yticklabels()]:
            tick_label.set_fontweight("bold")
        ax.xaxis.label.set_color(INK)
        ax.yaxis.label.set_color(INK)

        fig.tight_layout(pad=1.1)
        svg_path = OUTPUT_DIR / f"{STEM}.svg"
        png_path = OUTPUT_DIR / f"{STEM}.png"
        fig.savefig(svg_path, transparent=False)
        fig.savefig(png_path, dpi=300, transparent=False)
        plt.close(fig)

    add_svg_accessibility(svg_path)


if __name__ == "__main__":
    main()
