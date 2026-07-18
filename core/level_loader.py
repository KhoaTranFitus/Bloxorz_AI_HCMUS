"""Level loading placeholder."""
import json
from pathlib import Path
from typing import Any

from core.block import Block
from core.board import Board
from core.enums import Orientation, TileType
from core.level import Level
from core.state import GameState

# symbol for each tile in the level
TILE_SYMBOLS: dict[str, TileType] = {
    ".": TileType.VOID,
    "#": TileType.FLOOR,
    "G": TileType.GOAL,
}


ORIENTATION_NAMES: dict[str, Orientation] = {
    "standing": Orientation.STANDING,
    "horizontal": Orientation.HORIZONTAL,
    "vertical": Orientation.VERTICAL,
}


def _validate_level_data(data: dict[str, Any]) -> None:
    required_fields = {"name", "board", "start"}

    missing_fields = required_fields - data.keys()

    if missing_fields:
        raise ValueError(
            f"Missing level fields: {sorted(missing_fields)}"
        )

    board_data = data["board"]

    if not isinstance(board_data, list) or not board_data:
        raise ValueError("Level board must be a non-empty list")

    width = len(board_data[0])

    if width == 0:
        raise ValueError("Level rows cannot be empty")

    for index, row in enumerate(board_data):
        if len(row) != width:
            raise ValueError(
                f"Board row {index} has an invalid width"
            )

    goal_count = sum(row.count("G") for row in board_data)

    if goal_count != 1:
        raise ValueError(
            f"Level must contain exactly one goal, found {goal_count}"
        )


def load_level(file_path: str | Path) -> Level:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Level file not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON in level file {path}: {error}"
        ) from error

    _validate_level_data(data)

    board_data: list[str] = data["board"]

    tiles: list[tuple[TileType, ...]] = []

    for row_index, row_text in enumerate(board_data):
        converted_row: list[TileType] = []

        for col_index, symbol in enumerate(row_text):
            if symbol not in TILE_SYMBOLS:
                raise ValueError(
                    f"Unknown tile symbol '{symbol}' "
                    f"at row={row_index}, col={col_index}"
                )

            converted_row.append(TILE_SYMBOLS[symbol])

        tiles.append(tuple(converted_row))

    board = Board(
        width=len(board_data[0]),
        height=len(board_data),
        tiles=tuple(tiles),
    )

    start_data = data["start"]

    start_row = int(start_data["row"])
    start_col = int(start_data["col"])
    orientation_name = start_data.get(
        "orientation",
        "standing",
    ).lower()

    if orientation_name not in ORIENTATION_NAMES:
        raise ValueError(
            f"Unknown start orientation: {orientation_name}"
        )

    start_block = Block(
        row=start_row,
        col=start_col,
        orientation=ORIENTATION_NAMES[orientation_name],
    )

    initial_state = GameState(block=start_block)

    # Kiểm tra block ban đầu có thực sự nằm trên board hay không.
    for row, col in start_block.occupied_cells():
        if not board.is_walkable(row, col):
            raise ValueError(
                f"Initial block is not supported at ({row}, {col})"
            )

    return Level(
        name=str(data["name"]),
        board=board,
        initial_state=initial_state,
    )