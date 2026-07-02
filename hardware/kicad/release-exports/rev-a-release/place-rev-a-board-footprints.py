from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pcbnew


KICAD_FOOTPRINT_ROOT = Path(r"C:\Program Files\KiCad\10.0\share\kicad\footprints")


@dataclass(frozen=True)
class BoardSpec:
    schematic: str
    board: str
    sheet_name: str
    width_mm: float
    height_mm: float


BOARD_SPECS = [
    BoardSpec("io-board.kicad_sch", "io-board.kicad_pcb", "input-output", 160.0, 75.0),
    BoardSpec("power-backplane.kicad_sch", "power-backplane.kicad_pcb", "power-backplane", 150.0, 95.0),
    BoardSpec("ext-tank-routing.kicad_sch", "ext-tank-routing.kicad_pcb", "ext-tank-routing", 120.0, 80.0),
    BoardSpec(
        "crossfade-feedback-wet.kicad_sch",
        "crossfade-feedback-wet.kicad_pcb",
        "crossfade-feedback-wet",
        100.0,
        70.0,
    ),
    BoardSpec("filter-clipper.kicad_sch", "filter-clipper.kicad_pcb", "filter-clipper", 140.0, 90.0),
    BoardSpec(
        "tank-driver-recovery.kicad_sch",
        "tank-driver-recovery.kicad_pcb",
        "tank-driver-recovery",
        170.0,
        110.0,
    ),
]


@dataclass
class SchematicFootprint:
    ref: str
    value: str
    footprint: str
    x_mm: float
    y_mm: float
    rotation_deg: float


def mm(value: float) -> int:
    return pcbnew.FromMM(value)


def parse_property(block: str, name: str) -> str:
    match = re.search(rf'\(property\s+"{re.escape(name)}"\s+"([^"]*)"', block)
    return match.group(1) if match else ""


def parse_schematic_footprints(path: Path) -> list[SchematicFootprint]:
    lines = path.read_text(encoding="utf-8").splitlines()
    symbols: list[SchematicFootprint] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        if not line.startswith("\t(symbol"):
            index += 1
            continue

        block_lines = [line]
        index += 1
        while index < len(lines):
            block_lines.append(lines[index])
            if lines[index] == "\t)":
                index += 1
                break
            index += 1

        block = "\n".join(block_lines)
        at_match = re.search(r'\(at\s+([\d.]+)\s+([\d.]+)\s+(-?[\d.]+)\)', block)
        if not at_match:
            continue

        ref = parse_property(block, "Reference")
        value = parse_property(block, "Value")
        footprint = parse_property(block, "Footprint")

        if not ref or ref.startswith("#") or not footprint:
            continue

        symbols.append(
            SchematicFootprint(
                ref=ref,
                value=value,
                footprint=footprint,
                x_mm=float(at_match.group(1)),
                y_mm=float(at_match.group(2)),
                rotation_deg=float(at_match.group(3)),
            )
        )

    deduped: dict[str, SchematicFootprint] = {}
    for symbol in symbols:
        deduped.setdefault(symbol.ref, symbol)

    return sorted(deduped.values(), key=lambda item: natural_ref_key(item.ref))


def natural_ref_key(ref: str) -> tuple[str, int, str]:
    match = re.match(r"([A-Z]+)(\d+)(.*)", ref)
    if not match:
        return (ref, 0, "")
    return (match.group(1), int(match.group(2)), match.group(3))


def footprint_path(footprint: str) -> tuple[str, str]:
    if ":" not in footprint:
        raise ValueError(f"Footprint '{footprint}' is missing a library nickname")

    lib, name = footprint.split(":", 1)
    lib_dir = KICAD_FOOTPRINT_ROOT / f"{lib}.pretty"
    mod_file = lib_dir / f"{name}.kicad_mod"
    if not mod_file.exists():
        raise FileNotFoundError(f"Footprint file not found: {mod_file}")

    return str(lib_dir), name


def footprint_bbox_mm(footprint: pcbnew.FOOTPRINT) -> tuple[float, float, float, float]:
    bbox = footprint.GetBoundingBox()
    return (
        pcbnew.ToMM(bbox.GetX()),
        pcbnew.ToMM(bbox.GetY()),
        pcbnew.ToMM(bbox.GetWidth()),
        pcbnew.ToMM(bbox.GetHeight()),
    )


def rank_for_packing(symbol: SchematicFootprint, footprint: pcbnew.FOOTPRINT) -> tuple[int, float, str]:
    _x, _y, width, height = footprint_bbox_mm(footprint)
    ref_prefix = re.match(r"[A-Z]+", symbol.ref)
    prefix = ref_prefix.group(0) if ref_prefix else symbol.ref

    # Keep mechanical and harness connectors near the front of the packing pass,
    # then active devices, then small passives.
    prefix_rank = {
        "J": 0,
        "P": 1,
        "K": 2,
        "PS": 2,
        "U": 3,
        "Q": 3,
        "D": 4,
        "TVS": 4,
        "F": 4,
        "FB": 5,
        "R": 6,
        "C": 6,
    }.get(prefix, 7)

    return (prefix_rank, -max(width, height), symbol.ref)


def packed_footprint_positions(
    loaded: list[tuple[SchematicFootprint, pcbnew.FOOTPRINT]],
    width_mm: float,
    height_mm: float,
) -> dict[str, tuple[float, float]]:
    if not loaded:
        return {}

    left_margin = 7.0
    top_margin = 7.0
    right_margin = 7.0
    row_gap = 3.0
    col_gap = 3.0
    max_x = width_mm - right_margin
    positions: dict[str, tuple[float, float]] = {}

    cursor_x = left_margin
    cursor_y = top_margin
    row_height = 0.0

    for symbol, footprint in sorted(loaded, key=lambda item: rank_for_packing(item[0], item[1])):
        bbox_x, bbox_y, bbox_w, bbox_h = footprint_bbox_mm(footprint)

        if cursor_x > left_margin and cursor_x + bbox_w > max_x:
            cursor_x = left_margin
            cursor_y += row_height + row_gap
            row_height = 0.0

        # Position the footprint so its current bounding-box top-left corner
        # lands at the row-pack cursor.
        anchor_x = cursor_x - bbox_x
        anchor_y = cursor_y - bbox_y
        positions[symbol.ref] = (anchor_x, anchor_y)

        cursor_x += bbox_w + col_gap
        row_height = max(row_height, bbox_h)

    if cursor_y + row_height > height_mm - 4.0:
        print(
            f"warning: packed placement exceeds board height "
            f"({cursor_y + row_height:.1f} mm used of {height_mm:.1f} mm)"
        )

    return positions


def clear_generated_electrical_footprints(board: pcbnew.BOARD) -> None:
    for footprint in list(board.GetFootprints()):
        ref = footprint.GetReference()
        if not ref.startswith("H"):
            board.Delete(footprint)


def remove_mounting_hole_courtyards(board: pcbnew.BOARD) -> None:
    # Loaded-board FOOTPRINT.GraphicalItems() is not consistently iterable in
    # KiCad's Python bindings, so mounting-hole courtyard cleanup is handled
    # by strip_mounting_hole_courtyards_in_file() after board save.
    return None


def normalize_mounting_hole_positions(board: pcbnew.BOARD, width_mm: float, height_mm: float) -> None:
    inset = 3.5
    positions = {
        "H1": (inset, inset),
        "H2": (width_mm - inset, inset),
        "H3": (width_mm - inset, height_mm - inset),
        "H4": (inset, height_mm - inset),
    }

    for ref, (x_mm, y_mm) in positions.items():
        footprint = board.FindFootprintByReference(ref)
        if footprint is not None:
            footprint.SetPosition(pcbnew.VECTOR2I(mm(x_mm), mm(y_mm)))


def strip_mounting_hole_courtyards_in_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r'\n\t\t\(fp_circle\n\t\t\t\(center 0 0\)\n\t\t\t\(end 3\.45 0\)\n\t\t\t\(stroke\n\t\t\t\t\(width 0\.05\)\n\t\t\t\t\(type solid\)\n\t\t\t\)\n\t\t\t\(fill no\)\n\t\t\t\(layer "F\.CrtYd"\)\n(?:\t\t\t\(uuid "[^"]+"\)\n)?\t\t\)',
        "",
        text,
    )
    path.write_text(text, encoding="utf-8")


def place_board(root: Path, spec: BoardSpec) -> tuple[int, int]:
    schematic_path = root / spec.schematic
    board_path = root / spec.board
    symbols = parse_schematic_footprints(schematic_path)
    board = pcbnew.LoadBoard(str(board_path))
    loaded: list[tuple[SchematicFootprint, pcbnew.FOOTPRINT]] = []

    clear_generated_electrical_footprints(board)
    remove_mounting_hole_courtyards(board)
    normalize_mounting_hole_positions(board, spec.width_mm, spec.height_mm)

    for symbol in symbols:
        lib_dir, footprint_name = footprint_path(symbol.footprint)
        footprint = pcbnew.FootprintLoad(lib_dir, footprint_name)
        if footprint is None:
            raise RuntimeError(f"Could not load {symbol.footprint}")
        footprint.SetReference(symbol.ref)
        footprint.SetValue(symbol.value)
        footprint.SetOrientationDegrees(symbol.rotation_deg)
        loaded.append((symbol, footprint))

    positions = packed_footprint_positions(loaded, spec.width_mm, spec.height_mm)

    placed = 0
    for symbol, footprint in loaded:
        x_mm, y_mm = positions[symbol.ref]
        footprint.SetPosition(pcbnew.VECTOR2I(mm(x_mm), mm(y_mm)))
        footprint.SetSheetname(spec.sheet_name)
        footprint.SetSheetfile(spec.schematic)
        board.Add(footprint)
        placed += 1

    pcbnew.SaveBoard(str(board_path), board)
    strip_mounting_hole_courtyards_in_file(board_path)
    return placed, len(symbols)


def main() -> None:
    root = Path(__file__).resolve().parent
    for spec in BOARD_SPECS:
        placed, total = place_board(root, spec)
        print(f"{spec.board}: placed {placed}/{total} schematic footprints")


if __name__ == "__main__":
    main()
