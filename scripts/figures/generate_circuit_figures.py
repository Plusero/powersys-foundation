"""Generate the circuit figures used by the component tutorials.

Run from the repository root with:

    uv run python scripts/figures/generate_circuit_figures.py

Pass one or more figure stems (or SVG filenames) to generate only those figures:

    uv run python scripts/figures/generate_circuit_figures.py practical-capacitor-model

Use ``--check`` to verify that all or selected committed SVG files are up to date.
"""

from __future__ import annotations

import argparse
import filecmp
import tempfile
import xml.etree.ElementTree as ET
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import schemdraw
import schemdraw.elements as elm


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "articles" / "figures" / "generated"

INK = "#172b36"
ACCENT = "#0b7285"
BACKGROUND = "#ffffff"
SVG_NAMESPACE = "http://www.w3.org/2000/svg"
# Trailing-subscript labels: schemdraw plain text -> italic base + subscript.
SVG_SUBSCRIPT_LABELS = {
    "C_p": ("C", "p"),
    "R_w": ("R", "w"),
    "V_f": ("V", "f"),
    "V_t": ("V", "t"),
    "I_f": ("I", "f"),
    "I_t": ("I", "t"),
}
# Whole-string italic math labels.
SVG_ITALIC_LABELS = {
    "y": "y",
}
# Multi-part labels when a subscript is not the final character.
SVG_COMPOUND_LABELS = {
    "jb_c/2": (("j", "base"), ("b", "base"), ("c", "sub"), ("/2", "base")),
}


@dataclass(frozen=True)
class FigureSpec:
    filename: str
    title: str
    description: str
    draw: Callable[[Path], None]


def drawing(*, fontsize: float = 14, margin: float = 0.45) -> schemdraw.Drawing:
    """Create a drawing with the repository's shared visual style."""
    result = schemdraw.Drawing(show=False)
    result.config(
        unit=3.0,
        inches_per_unit=0.55,
        fontsize=fontsize,
        font="DejaVu Sans",
        color=INK,
        lw=2.4,
        bgcolor=BACKGROUND,
        margin=margin,
    )
    return result


def _replace_subscript_label(text_element: ET.Element, text_span: ET.Element) -> None:
    """Rewrite plain text such as V_f as an italic base letter plus a subscript."""
    base, subscript = SVG_SUBSCRIPT_LABELS[text_span.text]
    label_center = float(text_span.get("x", text_element.get("x", "0")))
    first_dy = text_span.get("dy", "13")

    for child in list(text_element):
        if child.tag == f"{{{SVG_NAMESPACE}}}tspan":
            text_element.remove(child)

    text_element.set("font-family", "DejaVu Serif")
    text_element.set("text-anchor", "middle")

    base_span = ET.SubElement(
        text_element,
        f"{{{SVG_NAMESPACE}}}tspan",
        {
            "x": f"{label_center:g}",
            "dy": first_dy,
            "font-style": "italic",
        },
    )
    base_span.text = base
    subscript_span = ET.SubElement(
        text_element,
        f"{{{SVG_NAMESPACE}}}tspan",
        {
            "dx": "2",
            "dy": "4",
            "font-size": "9",
            "font-style": "italic",
        },
    )
    subscript_span.text = subscript


def _replace_italic_label(text_element: ET.Element, text_span: ET.Element) -> None:
    """Rewrite a plain label as a single italic math string."""
    rendered = SVG_ITALIC_LABELS[text_span.text]
    label_center = float(text_span.get("x", text_element.get("x", "0")))
    first_dy = text_span.get("dy", "13")

    for child in list(text_element):
        if child.tag == f"{{{SVG_NAMESPACE}}}tspan":
            text_element.remove(child)

    text_element.set("font-family", "DejaVu Serif")
    text_element.set("text-anchor", "middle")
    span = ET.SubElement(
        text_element,
        f"{{{SVG_NAMESPACE}}}tspan",
        {
            "x": f"{label_center:g}",
            "dy": first_dy,
            "font-style": "italic",
        },
    )
    span.text = rendered


def _replace_compound_label(text_element: ET.Element, text_span: ET.Element) -> None:
    """Rewrite jb_c/2-style labels with a true subscript before trailing text."""
    parts = SVG_COMPOUND_LABELS[text_span.text]
    label_center = float(text_span.get("x", text_element.get("x", "0")))
    first_dy = text_span.get("dy", "13")
    subscript_dy = 4

    for child in list(text_element):
        if child.tag == f"{{{SVG_NAMESPACE}}}tspan":
            text_element.remove(child)

    text_element.set("font-family", "DejaVu Serif")
    text_element.set("text-anchor", "middle")

    previous_was_subscript = False
    for index, (content, role) in enumerate(parts):
        attributes: dict[str, str] = {"font-style": "italic"}
        if index == 0:
            attributes["x"] = f"{label_center:g}"
            attributes["dy"] = first_dy
        else:
            attributes["dx"] = "1"

        if role == "sub":
            attributes["dy"] = str(subscript_dy)
            attributes["font-size"] = "9"
            previous_was_subscript = True
        else:
            if previous_was_subscript:
                attributes["dy"] = str(-subscript_dy)
                attributes["font-size"] = "13"
            previous_was_subscript = False

        span = ET.SubElement(
            text_element,
            f"{{{SVG_NAMESPACE}}}tspan",
            attributes,
        )
        span.text = content


def save_svg(
    diagram: schemdraw.Drawing,
    path: Path,
    *,
    title: str,
    description: str,
) -> None:
    """Save an SVG and add accessible title and description elements."""
    diagram.save(str(path), transparent=False)

    ET.register_namespace("", SVG_NAMESPACE)
    tree = ET.parse(path)
    root = tree.getroot()
    identifier = path.stem
    title_id = f"{identifier}-title"
    description_id = f"{identifier}-description"
    root.set("role", "img")
    root.set("aria-labelledby", f"{title_id} {description_id}")

    for text_element in root.iter(f"{{{SVG_NAMESPACE}}}text"):
        for text_span in list(text_element.findall(f"{{{SVG_NAMESPACE}}}tspan")):
            if text_span.text in SVG_SUBSCRIPT_LABELS:
                _replace_subscript_label(text_element, text_span)
                break
            if text_span.text in SVG_COMPOUND_LABELS:
                _replace_compound_label(text_element, text_span)
                break
            if text_span.text in SVG_ITALIC_LABELS:
                _replace_italic_label(text_element, text_span)
                break

    title_element = ET.Element(f"{{{SVG_NAMESPACE}}}title", {"id": title_id})
    title_element.text = title
    description_element = ET.Element(
        f"{{{SVG_NAMESPACE}}}desc", {"id": description_id}
    )
    description_element.text = description
    root.insert(0, description_element)
    root.insert(0, title_element)
    tree.write(path, encoding="utf-8", xml_declaration=True)


def draw_capacitor(path: Path) -> None:
    diagram = drawing(margin=0.65)
    diagram += elm.Capacitor().right().length(4.0)
    save_svg(
        diagram,
        path,
        title="IEC general symbol for a capacitor",
        description=(
            "Two parallel plates separated by a gap, with one terminal lead "
            "connected to each plate."
        ),
    )


def draw_resistor(path: Path) -> None:
    diagram = drawing(margin=0.65)
    diagram += elm.ResistorIEC().right().length(4.0)
    save_svg(
        diagram,
        path,
        title="IEC general symbol for a resistor",
        description="An unfilled rectangle with one terminal lead connected to each end.",
    )


def draw_inductor(path: Path) -> None:
    diagram = drawing(margin=0.65)
    diagram += elm.Inductor().right().length(4.0)
    save_svg(
        diagram,
        path,
        title="IEC general symbol for a coil or inductor",
        description=(
            "Four connected semicircular arcs with one terminal lead connected "
            "to each end."
        ),
    )


def draw_rc_charging_circuit(path: Path) -> None:
    diagram = drawing(fontsize=13, margin=0.75)

    source = elm.SourceV().up()
    diagram += source
    diagram += elm.Switch().right().label(
        "closes at t = 0", loc="bottom", ofst=0.45
    )
    resistor = elm.ResistorIEC().right().label(
        "R = 10 kΩ", loc="bottom", ofst=0.3
    )
    diagram += resistor
    diagram += elm.Line().right().length(0.8)
    capacitor = elm.Capacitor().down()
    diagram += capacitor
    diagram += elm.Line().left().tox(source.start)

    diagram += (
        elm.CurrentLabel(length=1.4, ofst=0.55)
        .at(resistor)
        .label("i(t)", color=ACCENT)
        .color(ACCENT)
    )
    diagram += elm.Label("V_s = 12 V").at((-1.15, source.center.y))
    diagram += elm.Label("C = 100 µF").at((5.55, capacitor.center.y))
    diagram += elm.Label("+").at((7.25, 2.55))
    diagram += elm.Label("−").at((7.25, 0.45))
    diagram += elm.Label("v_C(t)").at((7.85, capacitor.center.y))
    diagram += elm.Label("v_C(0⁻) = 0").at((capacitor.center.x, -0.55))

    save_svg(
        diagram,
        path,
        title="Series RC charging circuit",
        description=(
            "A switch closes at time zero and connects a 12 volt ideal voltage "
            "source in series with a 10 kiloohm resistor and an initially "
            "uncharged 100 microfarad capacitor. Current flows clockwise, and "
            "the capacitor voltage is positive at its upper plate."
        ),
    )


def draw_rl_switching_circuit(path: Path) -> None:
    diagram = drawing(fontsize=13, margin=0.75)

    source = elm.SourceV().up()
    diagram += source
    diagram += elm.Switch().right().label(
        "closes at t = 0", loc="bottom", ofst=0.45
    )
    resistor = elm.ResistorIEC().right().label("R = 6 Ω", loc="bottom", ofst=0.3)
    diagram += resistor
    diagram += elm.Line().right().length(0.8)
    inductor = elm.Inductor().down()
    diagram += inductor
    diagram += elm.Line().left().tox(source.start)

    diagram += (
        elm.CurrentLabel(length=1.4, ofst=0.55)
        .at(resistor)
        .label("i(t)", color=ACCENT)
        .color(ACCENT)
    )
    diagram += elm.Label("V_s = 24 V").at((-1.15, source.center.y))
    diagram += elm.Label("L = 0.12 H").at((5.55, inductor.center.y))
    diagram += elm.Label("+").at((7.25, 2.55))
    diagram += elm.Label("−").at((7.25, 0.45))
    diagram += elm.Label("v_L(t)").at((7.85, inductor.center.y))
    diagram += elm.Label("i(0⁻) = 0").at((inductor.center.x, -0.55))

    save_svg(
        diagram,
        path,
        title="Series RL switching circuit",
        description=(
            "A switch closes at time zero and connects a 24 volt ideal voltage "
            "source in series with a 6 ohm resistor and an initially unenergized "
            "0.12 henry inductor. Current flows clockwise, and the inductor "
            "voltage is positive at its upper terminal."
        ),
    )


def draw_series_rlc_circuit(path: Path) -> None:
    diagram = drawing(fontsize=13, margin=0.8)

    source = elm.SourceSin().up()
    diagram += source
    resistor = elm.ResistorIEC().right().label(
        "R = 12 Ω", loc="bottom", ofst=0.3
    )
    diagram += resistor
    inductor = elm.Inductor().right().label(
        "L = 80 mH", loc="bottom", ofst=0.3
    )
    diagram += inductor
    capacitor = elm.Capacitor().down()
    diagram += capacitor
    diagram += elm.Line().left().tox(source.start)

    diagram += (
        elm.CurrentLabel(length=1.4, ofst=0.55)
        .at(resistor)
        .label("I", color=ACCENT)
        .color(ACCENT)
    )
    diagram += elm.Label("Vₛ = 230∠0° V RMS").at((-2.65, 1.75))
    diagram += elm.Label("f = 50 Hz").at((-2.65, 1.25))
    diagram += elm.Label("+").at((-0.48, 2.35))
    diagram += elm.Label("−").at((-0.48, 0.65))
    diagram += elm.Label("C = 100 µF").at((7.45, capacitor.center.y))

    save_svg(
        diagram,
        path,
        title="Series RLC circuit for the worked AC example",
        description=(
            "A 230 volt RMS, 50 hertz sinusoidal voltage source supplies a "
            "12 ohm resistor, an 80 millihenry inductor, and a 100 microfarad "
            "capacitor connected in series. The source voltage is positive at "
            "its upper terminal, and the reference current flows clockwise."
        ),
    )


def draw_pf_inductive_load_circuit(path: Path) -> None:
    diagram = drawing(fontsize=13, margin=0.8)

    source = elm.SourceSin().up()
    diagram += source
    line_resistance = elm.ResistorIEC().right().label(
        "Rₗᵢₙₑ = 0.40 Ω", loc="bottom", ofst=0.3
    )
    diagram += line_resistance
    diagram += elm.Dot()

    load_resistance = elm.ResistorIEC().down().length(1.5)
    diagram += load_resistance
    load_reactance = elm.Inductor().down().length(1.5)
    diagram += load_reactance
    diagram += elm.Dot()
    diagram += elm.Line().left().tox(source.start)

    diagram += (
        elm.CurrentLabel(length=1.4, ofst=0.55)
        .at(line_resistance)
        .label("I", color=ACCENT)
        .color(ACCENT)
    )
    diagram += elm.Label("V = 230∠0° V RMS").at((-2.65, 1.75))
    diagram += elm.Label("f = 50 Hz").at((-2.65, 1.25))
    diagram += elm.Label("+").at((-0.48, 2.35))
    diagram += elm.Label("−").at((-0.48, 0.65))
    diagram += elm.Label("R = 12 Ω").at((4.2, 2.25))
    diagram += elm.Label("Xₗ = 9 Ω").at((4.2, 0.75))

    save_svg(
        diagram,
        path,
        title="Worked inductive-load circuit",
        description=(
            "A 230 volt RMS sinusoidal source supplies a 0.40 ohm feeder "
            "resistance and an "
            "inductive load represented by a 12 ohm resistance and 9 ohm "
            "inductive reactance in series. The feeder voltage drop reduces "
            "the load-terminal voltage, and the reference current flows clockwise."
        ),
    )


def draw_pf_shunt_capacitor_correction(path: Path) -> None:
    diagram = drawing(fontsize=13, margin=0.8)

    source = elm.SourceSin().up()
    diagram += source
    line_resistance = elm.ResistorIEC().right().label(
        "Rₗᵢₙₑ = 0.40 Ω", loc="bottom", ofst=0.3
    )
    diagram += line_resistance
    top_node = diagram.here
    diagram += elm.Dot()

    load_resistance = elm.ResistorIEC().down().length(1.5)
    diagram += load_resistance
    load_reactance = elm.Inductor().down().length(1.5)
    diagram += load_reactance
    load_end = diagram.here
    diagram += elm.Dot()

    diagram += elm.Line().at(top_node).right().length(3.0)
    diagram += elm.Dot()
    capacitor = elm.Capacitor().down()
    diagram += capacitor
    capacitor_end = diagram.here
    diagram += elm.Line().at(capacitor_end).left().tox(source.start)

    diagram += (
        elm.CurrentLabel(length=1.4, ofst=0.55)
        .at(line_resistance)
        .label("Iₛ", color=ACCENT)
        .color(ACCENT)
    )
    diagram += elm.Label("V = 230∠0° V RMS").at((-2.65, 1.75))
    diagram += elm.Label("f = 50 Hz").at((-2.65, 1.25))
    diagram += elm.Label("+").at((-0.48, 2.35))
    diagram += elm.Label("−").at((-0.48, 0.65))
    diagram += elm.Label("R = 12 Ω").at((4.2, 2.25))
    diagram += elm.Label("Xₗ = 9 Ω").at((4.2, 0.75))
    diagram += elm.Label("C").at((6.55, 1.5))

    save_svg(
        diagram,
        path,
        title="Shunt capacitor power-factor correction circuit",
        description=(
            "A 230 volt RMS sinusoidal source and 0.40 ohm feeder resistance "
            "supply an inductive load, with a capacitor connected in parallel "
            "across the load to supply negative reactive power."
        ),
    )


def draw_practical_capacitor_model(path: Path) -> None:
    diagram = drawing(fontsize=13, margin=0.8)

    diagram += elm.Dot(open=True).label("terminal", loc="bottom", ofst=0.35)
    diagram += elm.Line().right().length(0.55)
    diagram += elm.Inductor().right().label("ESL", loc="bottom", ofst=0.3)
    diagram += elm.ResistorIEC().right().label("ESR", loc="bottom", ofst=0.3)

    branch_start = diagram.here
    diagram += elm.Dot()
    capacitor = elm.Capacitor().right().label("C", loc="bottom", ofst=0.3)
    diagram += capacitor
    branch_end = diagram.here
    diagram += elm.Dot()
    diagram += elm.Line().right().length(0.55)
    diagram += elm.Dot(open=True).label("terminal", loc="bottom", ofst=0.35)

    diagram += elm.Line().at(branch_start).up().length(1.45)
    diagram += (
        elm.ResistorIEC()
        .right()
        .tox(branch_end[0])
        .label("Rₗₑₐₖ", loc="top", ofst=0.3)
    )
    diagram += elm.Line().down().toy(branch_end[1])

    save_svg(
        diagram,
        path,
        title="First-order practical capacitor model",
        description=(
            "A two-terminal equivalent circuit with equivalent series "
            "inductance and equivalent series resistance in series with a "
            "parallel combination of the ideal capacitance and a leakage "
            "resistance."
        ),
    )


def draw_practical_inductor_model(path: Path) -> None:
    diagram = drawing(fontsize=13, margin=0.8)

    left_terminal = elm.Dot(open=True).label("terminal", loc="bottom", ofst=0.35)
    diagram += left_terminal
    diagram += elm.Line().right().length(0.55)
    branch_start = diagram.here
    diagram += elm.Dot()
    diagram += elm.ResistorIEC().right().label("R_w", loc="bottom", ofst=0.3)
    diagram += elm.Inductor().right().label("L", loc="bottom", ofst=0.3)
    branch_end = diagram.here
    diagram += elm.Dot()
    diagram += elm.Line().right().length(0.55)
    diagram += elm.Dot(open=True).label("terminal", loc="bottom", ofst=0.35)

    diagram += elm.Line().at(branch_start).up().length(1.45)
    diagram += (
        elm.Capacitor()
        .right()
        .tox(branch_end[0])
        .label("C_p", loc="top", ofst=0.3)
    )
    diagram += elm.Line().down().toy(branch_end[1])

    save_svg(
        diagram,
        path,
        title="First-order practical inductor model",
        description=(
            "A two-terminal equivalent circuit with winding resistance and ideal "
            "inductance in series, shunted by a parasitic capacitance."
        ),
    )


def draw_nominal_pi_line_model(path: Path) -> None:
    diagram = drawing(fontsize=13, margin=1.15)

    diagram += elm.Dot(open=True).label("f", loc="left", ofst=0.45)
    left_lead = elm.Line().right().length(1.5)
    diagram += left_lead
    left_node = diagram.here
    diagram += elm.Dot()

    diagram += (
        elm.ResistorIEC()
        .right()
        .length(5.4)
        .label("y", loc="top", ofst=0.4)
    )
    right_node = diagram.here
    diagram += elm.Dot()
    right_lead = elm.Line().right().length(1.5)
    diagram += right_lead
    diagram += elm.Dot(open=True).label("t", loc="right", ofst=0.45)

    # Currents enter the branch from each terminal bus.
    # Draw arrows alone, then place I_f / I_t as separate labels for clearance.
    diagram += (
        elm.CurrentLabel(length=0.85, ofst=0.22, top=True)
        .at(left_lead)
        .color(ACCENT)
    )
    diagram += (
        elm.CurrentLabel(length=0.85, ofst=0.22, top=True)
        .at(right_lead)
        .reverse()
        .color(ACCENT)
    )
    diagram += elm.Label("I_f", color=ACCENT).at(
        (left_node[0] - 0.75, left_node[1] + 0.95)
    )
    diagram += elm.Label("I_t", color=ACCENT).at(
        (right_node[0] + 0.75, right_node[1] + 0.95)
    )

    # Shunt labels sit outside each capacitor, clear of the vertical leads.
    shunt_label_depth = 2.25
    shunt_label_outset = 1.55

    diagram += elm.Line().at(left_node).down().length(0.55)
    diagram += elm.Capacitor().down()
    diagram += elm.Ground()
    diagram += elm.Label("jb_c/2").at(
        (left_node[0] - shunt_label_outset, left_node[1] - shunt_label_depth)
    )

    diagram += elm.Line().at(right_node).down().length(0.55)
    diagram += elm.Capacitor().down()
    diagram += elm.Ground()
    diagram += elm.Label("jb_c/2").at(
        (right_node[0] + shunt_label_outset, right_node[1] - shunt_label_depth)
    )

    # Voltage labels sit above the current labels.
    diagram += elm.Label("V_f").at((left_node[0] - 1.5, left_node[1] + 1.55))
    diagram += elm.Label("V_t").at((right_node[0] + 1.5, right_node[1] + 1.55))

    save_svg(
        diagram,
        path,
        title="Nominal pi model of a transmission line",
        description=(
            "A two-bus equivalent circuit with series admittance y between "
            "buses f and t, shunt charging jb_c/2 from each bus to the "
            "reference, and terminal currents I_f and I_t entering the branch."
        ),
    )


FIGURES = (
    FigureSpec(
        "capacitor-iec-symbol.svg",
        "IEC general symbol for a capacitor",
        "Two parallel plates separated by a gap.",
        draw_capacitor,
    ),
    FigureSpec(
        "resistor-iec-symbol.svg",
        "IEC general symbol for a resistor",
        "An unfilled rectangle with a terminal lead at each end.",
        draw_resistor,
    ),
    FigureSpec(
        "inductor-iec-symbol.svg",
        "IEC general symbol for a coil or inductor",
        "Four connected semicircular arcs with a terminal lead at each end.",
        draw_inductor,
    ),
    FigureSpec(
        "rc-charging-circuit.svg",
        "Series RC charging circuit",
        "A switched 12 volt source, resistor, and initially uncharged capacitor.",
        draw_rc_charging_circuit,
    ),
    FigureSpec(
        "rl-switching-circuit.svg",
        "Series RL switching circuit",
        "A switched 24 volt source, resistor, and initially unenergized inductor.",
        draw_rl_switching_circuit,
    ),
    FigureSpec(
        "series-rlc-ac-circuit.svg",
        "Series RLC circuit for the worked AC example",
        "A sinusoidal source supplying a resistor, inductor, and capacitor in series.",
        draw_series_rlc_circuit,
    ),
    FigureSpec(
        "pf-inductive-load-feeder-circuit.svg",
        "Worked inductive-load circuit",
        "A sinusoidal source and feeder resistance supplying a series R-L load.",
        draw_pf_inductive_load_circuit,
    ),
    FigureSpec(
        "pf-shunt-capacitor-feeder-circuit.svg",
        "Shunt capacitor power-factor correction circuit",
        "A feeder supplying an inductive load and parallel correction capacitor.",
        draw_pf_shunt_capacitor_correction,
    ),
    FigureSpec(
        "practical-capacitor-model.svg",
        "First-order practical capacitor model",
        "Series ESL and ESR followed by capacitance shunted by leakage resistance.",
        draw_practical_capacitor_model,
    ),
    FigureSpec(
        "practical-inductor-model.svg",
        "First-order practical inductor model",
        "Series winding resistance and inductance shunted by parasitic capacitance.",
        draw_practical_inductor_model,
    ),
    FigureSpec(
        "nominal-pi-line-model.svg",
        "Nominal pi model of a transmission line",
        "Series admittance y with shunt charging jb_c/2 at each terminal.",
        draw_nominal_pi_line_model,
    ),
)


def select_figures(names: list[str]) -> tuple[FigureSpec, ...]:
    """Resolve optional figure stems or filenames, preserving request order."""
    if not names:
        return FIGURES

    figures_by_name = {
        name: figure
        for figure in FIGURES
        for name in (figure.filename, Path(figure.filename).stem)
    }
    unknown = [name for name in names if name not in figures_by_name]
    if unknown:
        available = ", ".join(Path(figure.filename).stem for figure in FIGURES)
        unknown_list = ", ".join(unknown)
        raise ValueError(
            f"unknown figure name(s): {unknown_list}. Available figures: {available}"
        )

    selected = []
    selected_filenames = set()
    for name in names:
        figure = figures_by_name[name]
        if figure.filename not in selected_filenames:
            selected.append(figure)
            selected_filenames.add(figure.filename)
    return tuple(selected)


def generate(output_dir: Path, figures: tuple[FigureSpec, ...] = FIGURES) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    schemdraw.use("svg")
    elm.style(elm.STYLE_IEC)
    for figure in figures:
        figure.draw(output_dir / figure.filename)


def check_generated_files(figures: tuple[FigureSpec, ...] = FIGURES) -> int:
    with tempfile.TemporaryDirectory(prefix="powersys-figures-") as temporary:
        temporary_dir = Path(temporary)
        generate(temporary_dir, figures)
        stale = [
            figure.filename
            for figure in figures
            if not (OUTPUT_DIR / figure.filename).is_file()
            or not filecmp.cmp(
                temporary_dir / figure.filename,
                OUTPUT_DIR / figure.filename,
                shallow=False,
            )
        ]

    if stale:
        print("Generated circuit figures are missing or stale:")
        for filename in stale:
            print(f"  {filename}")
        print("Regenerate them with:")
        stems = " ".join(Path(figure.filename).stem for figure in figures)
        print(f"  uv run python scripts/figures/generate_circuit_figures.py {stems}")
        return 1

    if len(figures) == 1:
        print("The selected circuit figure is up to date.")
    else:
        print(f"All {len(figures)} selected circuit figures are up to date.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="check committed SVGs without changing them",
    )
    parser.add_argument(
        "figures",
        nargs="*",
        metavar="FIGURE",
        help="figure stem or SVG filename; omit to process all figures",
    )
    arguments = parser.parse_args()
    try:
        figures = select_figures(arguments.figures)
    except ValueError as error:
        parser.error(str(error))

    if arguments.check:
        return check_generated_files(figures)

    generate(OUTPUT_DIR, figures)
    noun = "figure" if len(figures) == 1 else "figures"
    print(
        f"Generated {len(figures)} circuit {noun} in {OUTPUT_DIR.relative_to(ROOT)}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
