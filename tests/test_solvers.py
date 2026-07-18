"""Tests for A* across ordinary and switch/bridge levels."""

from pathlib import Path

from ai.astar import solve_astar
from ai.problem import get_step_cost
from ai.ucs import solve_ucs
from core.block import Block
from core.board import Board
from core.enums import Orientation, TileType
from core.level_loader import load_level
from core.state import GameState
from core.transition import apply_move, is_goal_state


LEVELS = Path(__file__).parents[1] / "levels" / "basic"


def _solve(filename: str):
    level = load_level(LEVELS / filename)
    result = solve_astar(level.board, level.initial_state)
    state = level.initial_state

    for move in result.moves:
        next_state = apply_move(level.board, state, move)
        assert next_state is not None
        state = next_state

    return level, result, state


def test_astar_solves_original_level() -> None:
    level, result, state = _solve("level_01.json")

    assert result.solved
    assert result.cost == len(result.moves)
    assert is_goal_state(level.board, state)


def test_astar_opens_soft_switch_bridge() -> None:
    level, result, state = _solve("level_02.json")

    assert result.solved
    assert state.bridge_states == (True,)
    assert is_goal_state(level.board, state)


def test_astar_opens_heavy_switch_bridge() -> None:
    level, result, state = _solve("level_03.json")

    assert result.solved
    assert state.bridge_states == (True,)
    assert is_goal_state(level.board, state)


def test_touching_switch_without_state_change_costs_one() -> None:
    board = Board(
        width=2,
        height=1,
        tiles=((TileType.FLOOR, TileType.SOFT_SWITCH),),
    )
    lying_state = GameState(Block(0, 0, Orientation.HORIZONTAL))

    assert get_step_cost(board, lying_state, lying_state) == 1


def test_switch_activation_costs_two() -> None:
    board = Board(
        width=1,
        height=1,
        tiles=((TileType.SOFT_SWITCH,),),
    )
    current_state = GameState(
        Block(0, 0, Orientation.STANDING),
        bridge_states=(False,),
    )
    next_state = GameState(
        Block(0, 0, Orientation.STANDING),
        bridge_states=(True,),
    )

    assert get_step_cost(board, current_state, next_state) == 2


def test_fragile_tile_cost_is_five() -> None:
    board = Board(
        width=2,
        height=1,
        tiles=((TileType.FRAGILE, TileType.FRAGILE),),
    )
    lying_state = GameState(Block(0, 0, Orientation.HORIZONTAL))

    assert get_step_cost(board, lying_state, lying_state) == 5


def test_ucs_and_astar_find_same_optimal_cost() -> None:
    for filename in ("level_01.json", "level_02.json", "level_03.json"):
        level = load_level(LEVELS / filename)
        astar_result = solve_astar(level.board, level.initial_state)
        ucs_result = solve_ucs(level.board, level.initial_state)

        assert astar_result.solved
        assert ucs_result.solved
        assert astar_result.cost == ucs_result.cost


def test_switch_level_cost_exceeds_move_count() -> None:
    level = load_level(LEVELS / "level_02.json")
    result = solve_astar(level.board, level.initial_state)

    assert result.cost == len(result.moves) + 1
