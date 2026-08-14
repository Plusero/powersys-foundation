"""Generate the editable three-bus single-line diagram and preview exports.

Run from the repository root with:

    uv run python scripts/figures/generate_three_bus_single_line_diagram.py
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "articles" / "figures" / "generated"
STEM = "three-bus-power-flow-single-line"

PAGE_WIDTH = 1280
PAGE_HEIGHT = 720
INK = "#111111"
MUTED = "#43515a"
BUS_STROKE = 3
LINE_STROKE = 1.5
FONT_FAMILY = "Times New Roman"
SVG_NAMESPACE = "http://www.w3.org/2000/svg"


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


def add_text_cell(
    root: ET.Element,
    cell_id: str,
    value: str,
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    font_size: int = 20,
    bold: bool = False,
    align: str = "center",
    color: str = MUTED,
) -> None:
    style = (
        "text;html=1;strokeColor=none;fillColor=none;verticalAlign=middle;"
        f"align={align};whiteSpace=wrap;fontFamily={FONT_FAMILY};"
        f"fontSize={font_size};fontColor={color};"
        f"fontStyle={1 if bold else 0};"
    )
    cell = ET.SubElement(
        root,
        "mxCell",
        {"id": cell_id, "value": value, "style": style, "vertex": "1", "parent": "1"},
    )
    add_geometry(cell, x, y, width, height)


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
    stroke_width: float = LINE_STROKE,
    orthogonal: bool = True,
) -> None:
    style = (
        ("edgeStyle=orthogonalEdgeStyle;orthogonalLoop=1;jettySize=auto;" if orthogonal else "edgeStyle=none;")
        + "rounded=0;"
        f"html=1;endArrow=none;startArrow=none;strokeColor={INK};"
        f"strokeWidth={stroke_width};"
    )
    cell = ET.SubElement(
        root,
        "mxCell",
        {"id": cell_id, "style": style, "edge": "1", "parent": "1"},
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
        {"host": "app.diagrams.net", "modified": "2026-08-14T00:00:00.000Z", "version": "24.7.17"},
    )
    diagram = ET.SubElement(mxfile, "diagram", {"id": STEM, "name": "Page-1"})
    model = ET.SubElement(
        diagram,
        "mxGraphModel",
        {
            "dx": "1280",
            "dy": "720",
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

    conductors = {
        "bus-1": [(150, 190), (410, 190)],
        "bus-2": [(870, 190), (1130, 190)],
        "bus-3": [(540, 500), (740, 500)],
        "line-12": [(380, 190), (380, 265), (900, 265), (900, 190)],
        "line-13": [(210, 190), (210, 235), (570, 470), (570, 500)],
        "line-23": [(1070, 190), (1070, 235), (710, 470), (710, 500)],
        "generator-1-connection": [(280, 118), (280, 190)],
        "generator-2-connection": [(1000, 118), (1000, 190)],
        "load-connection": [(640, 500), (640, 610)],
    }
    for edge_id, points in conductors.items():
        add_edge(
            graph_root,
            edge_id,
            points,
            stroke_width=BUS_STROKE if edge_id.startswith("bus-") else LINE_STROKE,
            orthogonal=edge_id not in {"line-13", "line-23"},
        )

    add_vertex(
        graph_root,
        "generator-1",
        "G1",
        (
            f"ellipse;html=1;aspect=fixed;fillColor=#ffffff;strokeColor={INK};"
            f"strokeWidth={LINE_STROKE};fontFamily={FONT_FAMILY};fontSize=24;fontStyle=1;"
        ),
        252,
        62,
        56,
        56,
    )
    add_vertex(
        graph_root,
        "generator-2",
        "G2",
        (
            f"ellipse;html=1;aspect=fixed;fillColor=#ffffff;strokeColor={INK};"
            f"strokeWidth={LINE_STROKE};fontFamily={FONT_FAMILY};fontSize=24;fontStyle=1;"
        ),
        972,
        62,
        56,
        56,
    )
    add_vertex(
        graph_root,
        "pq-load",
        "",
        f"triangle;direction=south;html=1;fillColor={INK};strokeColor={INK};strokeWidth=1;",
        624,
        610,
        32,
        28,
    )

    add_text_cell(graph_root, "generator-1-spec", "|V<sub>1</sub>| = 1.04 p.u.<br>θ<sub>1</sub> = 0", 64, 66, 154, 52, font_size=18, align="right")
    add_text_cell(graph_root, "generator-2-spec", "P<sub>2</sub> = 0.50 p.u.<br>|V<sub>2</sub>| = 1.01 p.u.", 1050, 66, 166, 52, font_size=18, align="left")

    add_text_cell(graph_root, "bus-1-label", "Bus 1<br>Slack", 64, 148, 78, 52, bold=True, align="right")
    add_text_cell(graph_root, "bus-2-label", "Bus 2<br>PV", 1138, 148, 78, 52, bold=True, align="left")
    add_text_cell(graph_root, "bus-3-label", "Bus 3 — PQ", 748, 486, 170, 28, bold=True, align="left")
    add_text_cell(graph_root, "bus-3-spec", "P<sub>3</sub> = −0.60 p.u.<br>Q<sub>3</sub> = −0.25 p.u.", 748, 516, 230, 52, font_size=18, align="left")
    add_text_cell(graph_root, "load-label", "Load 3", 670, 604, 110, 28, bold=True, align="left")

    add_text_cell(graph_root, "line-12-title", "Line 1", 550, 208, 180, 26, bold=True)
    add_text_cell(graph_root, "line-12-label", "z<sub>12</sub> = 0.02 + j0.06 p.u.", 500, 232, 280, 26, font_size=18)
    add_text_cell(graph_root, "line-13-title", "Line 2", 250, 354, 140, 26, bold=True)
    add_text_cell(graph_root, "line-13-label", "z<sub>13</sub> = 0.08 + j0.24 p.u.", 168, 380, 300, 26, font_size=18)
    add_text_cell(graph_root, "line-23-title", "Line 3", 890, 354, 140, 26, bold=True)
    add_text_cell(graph_root, "line-23-label", "z<sub>23</sub> = 0.06 + j0.18 p.u.", 812, 380, 300, 26, font_size=18)

    ET.indent(mxfile, space="  ")
    tree = ET.ElementTree(mxfile)
    tree.write(path, encoding="utf-8", xml_declaration=True)


def svg_line(parent: ET.Element, points: list[tuple[float, float]], width: float) -> None:
    ET.SubElement(
        parent,
        "polyline",
        {
            "points": " ".join(f"{x},{y}" for x, y in points),
            "fill": "none",
            "stroke": INK,
            "stroke-width": str(width),
            "stroke-linejoin": "miter",
        },
    )


def svg_text(
    parent: ET.Element,
    text: str,
    x: float,
    y: float,
    *,
    size: int = 20,
    weight: str = "normal",
    anchor: str = "middle",
    color: str = MUTED,
) -> None:
    element = ET.SubElement(
        parent,
        "text",
        {
            "x": str(x),
            "y": str(y),
            "font-family": FONT_FAMILY,
            "font-size": str(size),
            "font-weight": weight,
            "text-anchor": anchor,
            "fill": color,
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
            "aria-labelledby": "three-bus-title three-bus-description",
        },
    )
    title = ET.SubElement(svg, f"{{{SVG_NAMESPACE}}}title", {"id": "three-bus-title"})
    title.text = "Three-bus AC power-flow single-line diagram"
    description = ET.SubElement(
        svg, f"{{{SVG_NAMESPACE}}}desc", {"id": "three-bus-description"}
    )
    description.text = (
        "A meshed three-bus network has a slack generator at bus 1, "
        "a generator-controlled PV bus at bus 2, and a PQ load at bus 3. Lines "
        "connect every pair of buses and are labelled with their per-unit impedances."
    )
    ET.SubElement(
        svg,
        f"{{{SVG_NAMESPACE}}}rect",
        {"x": "0", "y": "0", "width": str(PAGE_WIDTH), "height": str(PAGE_HEIGHT), "fill": "white"},
    )

    conductors = [
        ([(150, 190), (410, 190)], BUS_STROKE),
        ([(870, 190), (1130, 190)], BUS_STROKE),
        ([(540, 500), (740, 500)], BUS_STROKE),
        ([(380, 190), (380, 265), (900, 265), (900, 190)], LINE_STROKE),
        ([(210, 190), (210, 235), (570, 470), (570, 500)], LINE_STROKE),
        ([(1070, 190), (1070, 235), (710, 470), (710, 500)], LINE_STROKE),
        ([(280, 118), (280, 190)], LINE_STROKE),
        ([(1000, 118), (1000, 190)], LINE_STROKE),
        ([(640, 500), (640, 610)], LINE_STROKE),
    ]
    for points, width in conductors:
        svg_line(svg, points, width)

    for generator_x, generator_label in ((280, "G1"), (1000, "G2")):
        ET.SubElement(
            svg,
            f"{{{SVG_NAMESPACE}}}circle",
            {"cx": str(generator_x), "cy": "90", "r": "28", "fill": "white", "stroke": INK, "stroke-width": str(LINE_STROKE)},
        )
        svg_text(svg, generator_label, generator_x, 99, size=24, weight="bold", color=INK)
    ET.SubElement(
        svg,
        f"{{{SVG_NAMESPACE}}}polygon",
        {"points": "624,610 656,610 640,638", "fill": INK},
    )

    svg_text(svg, "|V1| = 1.04 p.u.", 218, 82, size=18, anchor="end")
    svg_text(svg, "θ1 = 0", 218, 108, size=18, anchor="end")
    svg_text(svg, "P2 = 0.50 p.u.", 1050, 82, size=18, anchor="start")
    svg_text(svg, "|V2| = 1.01 p.u.", 1050, 108, size=18, anchor="start")

    svg_text(svg, "Bus 1", 138, 170, weight="bold", anchor="end")
    svg_text(svg, "Slack", 138, 194, weight="bold", anchor="end")
    svg_text(svg, "Bus 2", 1142, 170, weight="bold", anchor="start")
    svg_text(svg, "PV", 1142, 194, weight="bold", anchor="start")
    svg_text(svg, "Bus 3 — PQ", 748, 506, weight="bold", anchor="start")
    svg_text(svg, "P3 = −0.60 p.u.", 748, 536, size=18, anchor="start")
    svg_text(svg, "Q3 = −0.25 p.u.", 748, 562, size=18, anchor="start")
    svg_text(svg, "Load 3", 670, 630, weight="bold", anchor="start")

    svg_text(svg, "Line 1", 640, 226, weight="bold")
    svg_text(svg, "z12 = 0.02 + j0.06 p.u.", 640, 252, size=18)
    svg_text(svg, "Line 2", 320, 374, weight="bold")
    svg_text(svg, "z13 = 0.08 + j0.24 p.u.", 318, 400, size=18)
    svg_text(svg, "Line 3", 960, 374, weight="bold")
    svg_text(svg, "z23 = 0.06 + j0.18 p.u.", 962, 400, size=18)

    ET.indent(svg, space="  ")
    ET.ElementTree(svg).write(path, encoding="utf-8", xml_declaration=True)


def validate_drawio(path: Path) -> None:
    tree = ET.parse(path)
    cells = tree.findall(".//mxCell")
    ids = {cell.get("id") for cell in cells}
    required_ids = {
        "bus-1",
        "bus-2",
        "bus-3",
        "line-12",
        "line-13",
        "line-23",
        "generator-1",
        "generator-2",
        "pq-load",
    }
    missing = required_ids - ids
    if missing:
        raise RuntimeError(f"Missing Draw.io cells: {sorted(missing)}")
    for cell in cells:
        if cell.get("edge") != "1" or cell.get("id") in {"line-13", "line-23"}:
            continue
        geometry = cell.find("mxGeometry")
        if geometry is None:
            raise RuntimeError(f"Edge {cell.get('id')} has no geometry")
        source = next(
            point for point in geometry.findall("mxPoint") if point.get("as") == "sourcePoint"
        )
        target = next(
            point for point in geometry.findall("mxPoint") if point.get("as") == "targetPoint"
        )
        ordered_points = [source, *geometry.findall("./Array/mxPoint"), target]
        points = [
            (float(point.get("x", "0")), float(point.get("y", "0")))
            for point in ordered_points
        ]
        if any(x_1 != x_2 and y_1 != y_2 for (x_1, y_1), (x_2, y_2) in zip(points, points[1:])):
            raise RuntimeError(f"Edge {cell.get('id')} is not orthogonal")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    drawio_path = OUTPUT_DIR / f"{STEM}.drawio"
    svg_path = OUTPUT_DIR / f"{STEM}.svg"
    write_drawio(drawio_path)
    write_svg(svg_path)
    validate_drawio(drawio_path)


if __name__ == "__main__":
    main()
