"""Tests for soft- and heavy-switch activation."""

from core.block import Block
from core.board import Board
from core.enums import Orientation, TileType
from core.state import GameState
from core.transition import get_activated_switches
from core.level_loader import load_level
from core.enums import Move
from core.transition import apply_move, is_block_supported
from pathlib import Path


def _switch_board(tile: TileType) -> Board:
    return Board(
        width=2,
        height=1,
        tiles=((tile, TileType.FLOOR),),
    )


def test_soft_switch_activates_under_part_of_block() -> None:
    state = GameState(Block(0, 0, Orientation.HORIZONTAL))

    assert get_activated_switches(
        _switch_board(TileType.SOFT_SWITCH), state
    ) == ((0, 0),)


def test_heavy_switch_does_not_activate_under_lying_block() -> None:
    state = GameState(Block(0, 0, Orientation.HORIZONTAL))

    assert get_activated_switches(
        _switch_board(TileType.HEAVY_SWITCH), state
    ) == ()


def test_heavy_switch_activates_under_standing_block() -> None:
    state = GameState(Block(0, 0, Orientation.STANDING))

    assert get_activated_switches(
        _switch_board(TileType.HEAVY_SWITCH), state
    ) == ((0, 0),)


def test_closed_bridge_rejects_block_before_switch_activation() -> None:
    path = Path(__file__).parents[1] / "levels" / "basic" / "level_02.json"
    level = load_level(path)
    state = level.initial_state

    for move in (Move.DOWN, Move.DOWN, Move.RIGHT, Move.RIGHT):
        state = apply_move(level.board, state, move)
        assert state is not None

    assert state.bridge_states == (False,)
    assert apply_move(level.board, state, Move.RIGHT) is None


def test_lying_on_heavy_switch_does_not_open_bridge() -> None:
    path = Path(__file__).parents[1] / "levels" / "basic" / "level_03.json"
    level = load_level(path)
    state = level.initial_state

    for move in (
        Move.DOWN,
        Move.DOWN,
        Move.DOWN,
        Move.RIGHT,
        Move.RIGHT,
    ):
        state = apply_move(level.board, state, move)
        assert state is not None

    assert (6, 3) in state.block.occupied_cells()
    assert state.block.orientation != Orientation.STANDING
    assert state.bridge_states == (False,)


def test_fragile_tile_supports_lying_but_not_standing_block() -> None:
    board = Board(
        width=2,
        height=1,
        tiles=((TileType.FRAGILE, TileType.FRAGILE),),
    )
    state = GameState(Block(0, 0, Orientation.HORIZONTAL))

    assert is_block_supported(board, state, state.block)
    assert not is_block_supported(
        board,
        state,
        Block(0, 0, Orientation.STANDING),
    )
