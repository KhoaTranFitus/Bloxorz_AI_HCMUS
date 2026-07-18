"""Tests for bridge and switch level loading."""

from pathlib import Path

from core.enums import TileType
from core.level_loader import load_level


LEVELS = Path(__file__).parents[1] / "levels" / "basic"


def test_soft_switch_level_loads_bridge_metadata() -> None:
    level = load_level(LEVELS / "level_02.json")

    assert level.board.get_tile(6, 3) == TileType.SOFT_SWITCH
    assert level.board.get_tile(3, 6) == TileType.BRIDGE
    assert level.board.get_bridge_id(3, 6) == 0
    assert level.initial_state.bridge_states == (False,)


def test_heavy_switch_level_loads() -> None:
    level = load_level(LEVELS / "level_03.json")

    assert level.board.get_tile(6, 3) == TileType.HEAVY_SWITCH
