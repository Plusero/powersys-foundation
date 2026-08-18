"""Generate the four-bus per-unit network diagram and its editable source.

Run from the repository root with:

    uv run python scripts/figures/generate_per_unit_network_diagram.py
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "articles" / "figures" / "generated"
STEM = "per-unit-four-bus-network"

PAGE_WIDTH = 1280
PAGE_HEIGHT = 500
INK = "#111111"
MUTED = "#43515a"
BUS_STROKE = 3
LINE_STROKE = 1.5
PLATE_STROKE = 2.5
FONT_FAMILY = "Times New Roman"
SVG_NAMESPACE = "http://www.w3.org/2000/svg"

AXIS_Y = 260
BUS_TOP_Y = 205
BUS_BOTTOM_Y = 315
GENERATOR_X = 110
GENERATOR_RADIUS = 30
WINDING_RADIUS = 26
BUS_X = {"bus-1": 200, "bus-2": 470, "bus-3": 840, "bus-4": 1080}
T1_WINDING_X = (298, 336)
T2_WINDING_X = (912, 950)
SHUNT_X = (540, 770)
LOAD_X = 1160
LOAD_TRIANGLE_Y = 330
ZONE_BOUNDARY_X = (317, 931)
ZONE_BOUNDARY_TOP_Y = 300
ZONE_BOUNDARY_BOTTOM_Y = 470

TITLE_Y = 64
NAME_Y = 120
SPEC_FIRST_Y = 146
SPEC_SECOND_Y = 170
BUS_LABEL_Y = 196
ZONE_NAME_Y = 420
ZONE_SPEC_Y = 446

TITLE_SIZE = 20
LABEL_SIZE = 20
SPEC_SIZE = 18
CHARACTER_WIDTH_RATIO = 0.52  # rough Times advance width, for Draw.io text boxes


def shunt_conductors(x: int) -> list[tuple[str, list[tuple[float, float]], float]]:
    """Return the lead, capacitor plates, and earth symbol of one charging branch."""
    return [
        (f"shunt-{x}-lead", [(x, AXIS_Y), (x, 326)], LINE_STROKE),
        (f"shunt-{x}-plate-upper", [(x - 18, 326), (x + 18, 326)], PLATE_STROKE),
        (f"shunt-{x}-plate-lower", [(x - 18, 338), (x + 18, 338)], PLATE_STROKE),
        (f"shunt-{x}-earth-lead", [(x, 338), (x, 352)], LINE_STROKE),
        (f"shunt-{x}-earth-wide", [(x - 18, 352), (x + 18, 352)], LINE_STROKE),
        (f"shunt-{x}-earth-mid", [(x - 11, 360), (x + 11, 360)], LINE_STROKE),
        (f"shunt-{x}-earth-narrow", [(x - 4, 368), (x + 4, 368)], LINE_STROKE),
    ]


CONDUCTORS: list[tuple[str, list[tuple[float, float]], float]] = [
    ("generator-lead", [(GENERATOR_X + GENERATOR_RADIUS, AXIS_Y), (BUS_X["bus-1"], AXIS_Y)], LINE_STROKE),
    ("bus-1", [(BUS_X["bus-1"], BUS_TOP_Y), (BUS_X["bus-1"], BUS_BOTTOM_Y)], BUS_STROKE),
    ("bus-1-t1", [(BUS_X["bus-1"], AXIS_Y), (T1_WINDING_X[0] - WINDING_RADIUS, AXIS_Y)], LINE_STROKE),
    ("t1-bus-2", [(T1_WINDING_X[1] + WINDING_RADIUS, AXIS_Y), (BUS_X["bus-2"], AXIS_Y)], LINE_STROKE),
    ("bus-2", [(BUS_X["bus-2"], BUS_TOP_Y), (BUS_X["bus-2"], BUS_BOTTOM_Y)], BUS_STROKE),
    ("line-23", [(BUS_X["bus-2"], AXIS_Y), (BUS_X["bus-3"], AXIS_Y)], LINE_STROKE),
    ("bus-3", [(BUS_X["bus-3"], BUS_TOP_Y), (BUS_X["bus-3"], BUS_BOTTOM_Y)], BUS_STROKE),
    ("bus-3-t2", [(BUS_X["bus-3"], AXIS_Y), (T2_WINDING_X[0] - WINDING_RADIUS, AXIS_Y)], LINE_STROKE),
    ("t2-bus-4", [(T2_WINDING_X[1] + WINDING_RADIUS, AXIS_Y), (BUS_X["bus-4"], AXIS_Y)], LINE_STROKE),
    ("bus-4", [(BUS_X["bus-4"], BUS_TOP_Y), (BUS_X["bus-4"], BUS_BOTTOM_Y)], BUS_STROKE),
    ("load-lead", [(BUS_X["bus-4"], AXIS_Y), (LOAD_X, AXIS_Y), (LOAD_X, LOAD_TRIANGLE_Y)], LINE_STROKE),
    *shunt_conductors(SHUNT_X[0]),
    *shunt_conductors(SHUNT_X[1]),
]

WINDINGS: list[tuple[str, int]] = [
    ("t1-winding-hv", T1_WINDING_X[1]),
    ("t1-winding-lv", T1_WINDING_X[0]),
    ("t2-winding-hv", T2_WINDING_X[0]),
    ("t2-winding-lv", T2_WINDING_X[1]),
]

# (identifier, text, anchor x, baseline y, size, bold, anchor)
LABELS: list[tuple[str, str, float, float, int, bool, str]] = [
    ("title", "System base: 100 MVA", 640, TITLE_Y, TITLE_SIZE, True, "middle"),
    ("generator-name", "Generator G", GENERATOR_X, NAME_Y, LABEL_SIZE, True, "middle"),
    ("generator-rating", "90 MVA, 13.8 kV", GENERATOR_X, SPEC_FIRST_Y, SPEC_SIZE, False, "middle"),
    ("generator-reactance", "x″ = j0.18 p.u.", GENERATOR_X, SPEC_SECOND_Y, SPEC_SIZE, False, "middle"),
    ("t1-name", "T1", 317, NAME_Y, LABEL_SIZE, True, "middle"),
    ("t1-rating", "125 MVA, 13.2/230 kV", 317, SPEC_FIRST_Y, SPEC_SIZE, False, "middle"),
    ("t1-reactance", "x = j0.10 p.u.", 317, SPEC_SECOND_Y, SPEC_SIZE, False, "middle"),
    ("line-name", "230 kV line", 655, NAME_Y, LABEL_SIZE, True, "middle"),
    ("line-impedance", "z = 15 + j80 Ω", 655, SPEC_FIRST_Y, SPEC_SIZE, False, "middle"),
    ("line-charging", "bc = 422 µS total", 655, SPEC_SECOND_Y, SPEC_SIZE, False, "middle"),
    ("t2-name", "T2", 931, NAME_Y, LABEL_SIZE, True, "middle"),
    ("t2-rating", "75 MVA, 230/69 kV", 931, SPEC_FIRST_Y, SPEC_SIZE, False, "middle"),
    ("t2-reactance", "x = j0.08 p.u.", 931, SPEC_SECOND_Y, SPEC_SIZE, False, "middle"),
    ("bus-1-label", "Bus 1", BUS_X["bus-1"], BUS_LABEL_Y, LABEL_SIZE, True, "middle"),
    ("bus-2-label", "Bus 2", BUS_X["bus-2"], BUS_LABEL_Y, LABEL_SIZE, True, "middle"),
    ("bus-3-label", "Bus 3", BUS_X["bus-3"], BUS_LABEL_Y, LABEL_SIZE, True, "middle"),
    ("bus-4-label", "Bus 4", BUS_X["bus-4"], BUS_LABEL_Y, LABEL_SIZE, True, "middle"),
    ("shunt-left-label", "bc/2", SHUNT_X[0] + 26, 338, SPEC_SIZE, False, "start"),
    ("shunt-right-label", "bc/2", SHUNT_X[1] + 26, 338, SPEC_SIZE, False, "start"),
    ("load-name", "Load", LOAD_X - 20, 300, LABEL_SIZE, True, "end"),
    ("load-power", "60 + j25 MVA", LOAD_X - 20, 326, SPEC_SIZE, False, "end"),
    ("load-voltage", "at 66 kV", LOAD_X - 20, 350, SPEC_SIZE, False, "end"),
    ("zone-generator-name", "Generator zone", 230, ZONE_NAME_Y, LABEL_SIZE, True, "middle"),
    ("zone-generator-base", "VB = 13.2 kV", 230, ZONE_SPEC_Y, SPEC_SIZE, False, "middle"),
    ("zone-transmission-name", "Transmission zone", 624, ZONE_NAME_Y, LABEL_SIZE, True, "middle"),
    ("zone-transmission-base", "VB = 230 kV", 624, ZONE_SPEC_Y, SPEC_SIZE, False, "middle"),
    ("zone-distribution-name", "Distribution zone", 1060, ZONE_NAME_Y, LABEL_SIZE, True, "middle"),
    ("zone-distribution-base", "VB = 69 kV", 1060, ZONE_SPEC_Y, SPEC_SIZE, False, "middle"),
]

FIGURE_DESCRIPTION = (
    "Radial single-line diagram. Generator G at bus 1 connects through step-up "
    "transformer T1 to bus 2, a 230 kV line with a charging capacitance at each "
    "end runs to bus 3, and step-down transformer T2 feeds the load at bus 4. "
    "Dashed boundaries through both transformers separate the generator, "
    "transmission, and distribution zones, whose voltage bases are 13.2 kV, "
    "230 kV, and 69 kV on a 100 MVA system base."
)


def text_box_x(text: str, anchor_x: float, size: int, anchor: str) -> tuple[float, float]:
    """Return the top-left x and width of a Draw.io box for anchored text."""
    width = max(len(text) * size * CHARACTER_WIDTH_RATIO, 40.0)
    if anchor == "middle":
        return anchor_x - width / 2.0, width
    if anchor == "end":
        return anchor_x - width, width
    return anchor_x, width


def add_geometry(
    cell: ET.Element, x: float, y: float, width: float, height: float
) -> None:
    ET.SubElement(
        cell,
        "mxGeometry",
        {
            "x": str(x),
            "y": str(y),
            "width": str(width),
            "height": str(height),
            "as": "geometry",
        },
    )


def add_vertex(
    root: ET.Element,
    cell_id: str,
    value: str,
    style: str,
    x: float,
    y: float,
    width: float,
    height: float,
) -> None:
    cell = ET.SubElement(
        root,
        "mxCell",
        {"id": cell_id, "value": value, "style": style, "vertex": "1", "parent": "1"},
    )
    add_geometry(cell, x, y, width, height)


def add_edge(
    root: ET.Element,
    cell_id: str,
    points: list[tuple[float, float]],
    *,
    stroke_width: float,
    stroke_color: str = INK,
    dashed: bool = False,
) -> None:
    style = (
        "edgeStyle=orthogonalEdgeStyle;orthogonalLoop=1;jettySize=auto;rounded=0;"
        f"html=1;endArrow=none;startArrow=none;strokeColor={stroke_color};"
        f"strokeWidth={stroke_width};dashed={1 if dashed else 0};"
    )
    cell = ET.SubElement(
        root, "mxCell", {"id": cell_id, "style": style, "edge": "1", "parent": "1"}
    )
    geometry = ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
    ET.SubElement(
        geometry,
        "mxPoint",
        {"x": str(points[0][0]), "y": str(points[0][1]), "as": "sourcePoint"},
    )
    ET.SubElement(
        geometry,
        "mxPoint",
        {"x": str(points[-1][0]), "y": str(points[-1][1]), "as": "targetPoint"},
    )
    if len(points) > 2:
        array = ET.SubElement(geometry, "Array", {"as": "points"})
        for point_x, point_y in points[1:-1]:
            ET.SubElement(array, "mxPoint", {"x": str(point_x), "y": str(point_y)})


def write_drawio(path: Path) -> None:
    mxfile = ET.Element(
        "mxfile",
        {
            "host": "app.diagrams.net",
            "modified": "2026-08-18T00:00:00.000Z",
            "version": "24.7.17",
        },
    )
    diagram = ET.SubElement(mxfile, "diagram", {"id": STEM, "name": "Page-1"})
    model = ET.SubElement(
        diagram,
        "mxGraphModel",
        {
            "dx": str(PAGE_WIDTH),
            "dy": str(PAGE_HEIGHT),
            "grid": "1",
            "gridSize": "10",
            "guides": "1",
            "tooltips": "1",
            "connect": "1",
            "arrows": "1",
            "fold": "1",
            "page": "1",
            "pageScale": "1",
            "pageWidth": str(PAGE_WIDTH),
            "pageHeight": str(PAGE_HEIGHT),
            "math": "0",
            "shadow": "0",
        },
    )
    graph_root = ET.SubElement(model, "root")
    ET.SubElement(graph_root, "mxCell", {"id": "0"})
    ET.SubElement(graph_root, "mxCell", {"id": "1", "parent": "0"})

    for cell_id, points, stroke_width in CONDUCTORS:
        add_edge(graph_root, cell_id, points, stroke_width=stroke_width)
    for index, boundary_x in enumerate(ZONE_BOUNDARY_X, start=1):
        add_edge(
            graph_root,
            f"zone-boundary-{index}",
            [
                (boundary_x, ZONE_BOUNDARY_TOP_Y),
                (boundary_x, ZONE_BOUNDARY_BOTTOM_Y),
            ],
            stroke_width=LINE_STROKE,
            stroke_color=MUTED,
            dashed=True,
        )

    circle_style = (
        f"ellipse;html=1;aspect=fixed;fillColor=none;strokeColor={INK};"
        f"strokeWidth={LINE_STROKE};fontFamily={FONT_FAMILY};fontSize=24;fontStyle=1;"
    )
    add_vertex(
        graph_root,
        "generator",
        "G",
        circle_style.replace("fillColor=none", "fillColor=#ffffff"),
        GENERATOR_X - GENERATOR_RADIUS,
        AXIS_Y - GENERATOR_RADIUS,
        2 * GENERATOR_RADIUS,
        2 * GENERATOR_RADIUS,
    )
    for cell_id, center_x in WINDINGS:
        add_vertex(
            graph_root,
            cell_id,
            "",
            circle_style,
            center_x - WINDING_RADIUS,
            AXIS_Y - WINDING_RADIUS,
            2 * WINDING_RADIUS,
            2 * WINDING_RADIUS,
        )
    add_vertex(
        graph_root,
        "load",
        "",
        f"triangle;direction=south;html=1;fillColor={INK};strokeColor={INK};strokeWidth=1;",
        LOAD_X - 16,
        LOAD_TRIANGLE_Y,
        32,
        28,
    )

    for cell_id, text, anchor_x, baseline_y, size, bold, anchor in LABELS:
        box_x, width = text_box_x(text, anchor_x, size, anchor)
        style = (
            "text;html=1;strokeColor=none;fillColor=none;verticalAlign=middle;"
            f"align={anchor.replace('middle', 'center').replace('start', 'left').replace('end', 'right')};"
            f"whiteSpace=wrap;fontFamily={FONT_FAMILY};fontSize={size};"
            f"fontColor={INK if bold else MUTED};fontStyle={1 if bold else 0};"
        )
        cell = ET.SubElement(
            graph_root,
            "mxCell",
            {
                "id": cell_id,
                "value": text,
                "style": style,
                "vertex": "1",
                "parent": "1",
            },
        )
        add_geometry(cell, box_x, baseline_y - size, width, size + 8)

    ET.indent(mxfile, space="  ")
    ET.ElementTree(mxfile).write(path, encoding="utf-8", xml_declaration=True)


def svg_line(
    parent: ET.Element,
    points: list[tuple[float, float]],
    width: float,
    *,
    color: str = INK,
    dashed: bool = False,
) -> None:
    attributes = {
        "points": " ".join(f"{x},{y}" for x, y in points),
        "fill": "none",
        "stroke": color,
        "stroke-width": str(width),
        "stroke-linejoin": "miter",
    }
    if dashed:
        attributes["stroke-dasharray"] = "8 6"
    ET.SubElement(parent, "polyline", attributes)


def svg_text(
    parent: ET.Element,
    text: str,
    x: float,
    y: float,
    *,
    size: int,
    bold: bool,
    anchor: str,
) -> None:
    element = ET.SubElement(
        parent,
        "text",
        {
            "x": str(x),
            "y": str(y),
            "font-family": FONT_FAMILY,
            "font-size": str(size),
            "font-weight": "bold" if bold else "normal",
            "text-anchor": anchor,
            "fill": INK if bold else MUTED,
        },
    )
    element.text = text


def write_svg(path: Path) -> None:
    ET.register_namespace("", SVG_NAMESPACE)
    svg = ET.Element(
        f"{{{SVG_NAMESPACE}}}svg",
        {
            "width": str(PAGE_WIDTH),
            "height": str(PAGE_HEIGHT),
            "viewBox": f"0 0 {PAGE_WIDTH} {PAGE_HEIGHT}",
            "role": "img",
            "aria-labelledby": f"{STEM}-title {STEM}-description",
        },
    )
    title = ET.SubElement(svg, f"{{{SVG_NAMESPACE}}}title", {"id": f"{STEM}-title"})
    title.text = "Four-bus network spanning three per-unit voltage zones"
    description = ET.SubElement(
        svg, f"{{{SVG_NAMESPACE}}}desc", {"id": f"{STEM}-description"}
    )
    description.text = FIGURE_DESCRIPTION
    ET.SubElement(
        svg,
        f"{{{SVG_NAMESPACE}}}rect",
        {
            "x": "0",
            "y": "0",
            "width": str(PAGE_WIDTH),
            "height": str(PAGE_HEIGHT),
            "fill": "white",
        },
    )

    for boundary_x in ZONE_BOUNDARY_X:
        svg_line(
            svg,
            [
                (boundary_x, ZONE_BOUNDARY_TOP_Y),
                (boundary_x, ZONE_BOUNDARY_BOTTOM_Y),
            ],
            LINE_STROKE,
            color=MUTED,
            dashed=True,
        )
    for _, points, stroke_width in CONDUCTORS:
        svg_line(svg, points, stroke_width)

    for _, center_x in WINDINGS:
        ET.SubElement(
            svg,
            f"{{{SVG_NAMESPACE}}}circle",
            {
                "cx": str(center_x),
                "cy": str(AXIS_Y),
                "r": str(WINDING_RADIUS),
                "fill": "none",
                "stroke": INK,
                "stroke-width": str(LINE_STROKE),
            },
        )
    ET.SubElement(
        svg,
        f"{{{SVG_NAMESPACE}}}circle",
        {
            "cx": str(GENERATOR_X),
            "cy": str(AXIS_Y),
            "r": str(GENERATOR_RADIUS),
            "fill": "white",
            "stroke": INK,
            "stroke-width": str(LINE_STROKE),
        },
    )
    svg_text(svg, "G", GENERATOR_X, AXIS_Y + 9, size=24, bold=True, anchor="middle")
    ET.SubElement(
        svg,
        f"{{{SVG_NAMESPACE}}}polygon",
        {
            "points": (
                f"{LOAD_X - 16},{LOAD_TRIANGLE_Y} {LOAD_X + 16},{LOAD_TRIANGLE_Y} "
                f"{LOAD_X},{LOAD_TRIANGLE_Y + 28}"
            ),
            "fill": INK,
        },
    )

    for _, text, anchor_x, baseline_y, size, bold, anchor in LABELS:
        svg_text(svg, text, anchor_x, baseline_y, size=size, bold=bold, anchor=anchor)

    ET.indent(svg, space="  ")
    ET.ElementTree(svg).write(path, encoding="utf-8", xml_declaration=True)


def validate_drawio(path: Path) -> None:
    """Check that every element is present and every conductor stays orthogonal."""
    cells = ET.parse(path).findall(".//mxCell")
    identifiers = {cell.get("id") for cell in cells}
    required = {
        "generator",
        "load",
        *BUS_X,
        *(cell_id for cell_id, _ in WINDINGS),
        *(cell_id for cell_id, _, _ in CONDUCTORS),
        *(cell_id for cell_id, *_ in LABELS),
    }
    missing = required - identifiers
    if missing:
        raise RuntimeError(f"Missing Draw.io cells: {sorted(missing)}")

    for cell in cells:
        if cell.get("edge") != "1":
            continue
        geometry = cell.find("mxGeometry")
        if geometry is None:
            raise RuntimeError(f"Edge {cell.get('id')} has no geometry")
        source = next(
            point
            for point in geometry.findall("mxPoint")
            if point.get("as") == "sourcePoint"
        )
        target = next(
            point
            for point in geometry.findall("mxPoint")
            if point.get("as") == "targetPoint"
        )
        ordered = [source, *geometry.findall("./Array/mxPoint"), target]
        points = [
            (float(point.get("x", "0")), float(point.get("y", "0")))
            for point in ordered
        ]
        if any(
            x_1 != x_2 and y_1 != y_2
            for (x_1, y_1), (x_2, y_2) in zip(points, points[1:])
        ):
            raise RuntimeError(f"Edge {cell.get('id')} is not orthogonal")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    drawio_path = OUTPUT_DIR / f"{STEM}.drawio"
    svg_path = OUTPUT_DIR / f"{STEM}.svg"
    write_drawio(drawio_path)
    write_svg(svg_path)
    validate_drawio(drawio_path)
    print(f"Wrote {drawio_path.relative_to(ROOT)} and {svg_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
