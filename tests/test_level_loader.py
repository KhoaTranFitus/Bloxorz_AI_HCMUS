"""Loader tests for optional soft/heavy switch and bridge metadata."""

import json

from core.enums import TileType
from core.level_loader import load_level


def test_loader_preserves_split_symbol_and_loads_switch_metadata(
    tmp_path,
) -> None:
    level_data = {
        "name": "metadata test",
        "board": ["#SshBG"],
        "start": {"row": 0, "col": 0, "orientation": "standing"},
        "bridges": [
            {
                "id": 0,
                "cells": [[0, 4]],
                "initially_open": False,
            }
        ],
        "switches": [
            {
                "row": 0,
                "col": 2,
                "bridge_ids": [0],
                "action": "open",
            },
            {
                "row": 0,
                "col": 3,
                "bridge_ids": [0],
                "action": "toggle",
            },
        ],
    }
    level_path = tmp_path / "metadata.json"
    level_path.write_text(json.dumps(level_data), encoding="utf-8")

    level = load_level(level_path)

    assert level.board.get_tile(0, 1) == TileType.SPLIT_SWITCH
    assert level.board.get_tile(0, 2) == TileType.SOFT_SWITCH
    assert level.board.get_tile(0, 3) == TileType.HEAVY_SWITCH
    assert level.board.get_tile(0, 4) == TileType.BRIDGE
    assert level.board.get_bridge_id(0, 4) == 0
    assert level.initial_state.bridge_states == (False,)
