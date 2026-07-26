"""Regression tests for player input handling."""

from types import SimpleNamespace

from core.block import Block
from core.enums import Move, Orientation
from core.state import GameState
from game.game import GameController


def test_space_is_ignored_after_split_cubes_merge() -> None:
    executed_moves: list[Move] = []
    controller = SimpleNamespace(
        state=GameState(Block(0, 0, Orientation.HORIZONTAL)),
        has_won=False,
        is_busy=False,
        replay_controller=None,
        _execute_move=executed_moves.append,
    )

    GameController.try_move(controller, Move.SWITCH)

    assert executed_moves == []


def test_space_switches_control_while_block_is_split() -> None:
    executed_moves: list[Move] = []
    controller = SimpleNamespace(
        state=GameState(
            block=Block(0, 0, Orientation.CUBE),
            split_cubes=((0, 0), (0, 2)),
            active_cube=0,
        ),
        has_won=False,
        is_busy=False,
        replay_controller=None,
        _execute_move=executed_moves.append,
    )

    GameController.try_move(controller, Move.SWITCH)

    assert executed_moves == [Move.SWITCH]
