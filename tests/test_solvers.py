"""Tests for cost, heuristic, UCS, and A* without UI or level files."""

from collections import deque

from ai.astar import solve_astar
from ai.heuristics import goal_distance
from ai.problem import get_step_cost
from ai.ucs import solve_ucs
from core.block import Block
from core.board import Board
from core.enums import Orientation, TileType
from core.state import GameState
from core.transition import get_valid_moves, is_goal_state


def _basic_problem() -> tuple[Board, GameState]:
    void = TileType.VOID
    floor = TileType.FLOOR
    goal = TileType.GOAL
    tiles = (
        (void,) * 10,
        (void, floor, floor, floor) + (void,) * 6,
        (void,) + (floor,) * 8 + (void,),
        (void,) * 3 + (floor,) * 7,
        (void,) * 3 + (floor,) * 3 + (goal,) + (floor,) * 3,
        (void,) * 3 + (floor,) * 7,
        (void,) * 10,
    )
    board = Board(width=10, height=7, tiles=tiles)
    state = GameState(Block(1, 1, Orientation.STANDING))
    return board, state


def _switch_problem(
    switch_type: TileType,
) -> tuple[Board, GameState]:
    switch_symbol = "s" if switch_type == TileType.SOFT_SWITCH else "h"
    rows = (
        "............",
        ".#####......",
        ".#####......",
        ".#####BB###.",
        ".#####BB#G#.",
        ".#####..###.",
        f".##{switch_symbol}##......",
        ".#####......",
        "............",
    )
    symbols = {
        ".": TileType.VOID,
        "#": TileType.FLOOR,
        "G": TileType.GOAL,
        "B": TileType.BRIDGE,
        "s": TileType.SOFT_SWITCH,
        "h": TileType.HEAVY_SWITCH,
    }
    tiles = tuple(
        tuple(symbols[symbol] for symbol in row)
        for row in rows
    )
    bridge_ids = tuple(
        tuple(0 if symbol == "B" else -1 for symbol in row)
        for row in rows
    )
    board = Board(
        width=len(rows[0]),
        height=len(rows),
        tiles=tiles,
        bridge_ids=bridge_ids,
        switch_links=((6, 3, (0,), "open"),),
    )
    state = GameState(
        Block(1, 1, Orientation.STANDING),
        bridge_states=(False,),
    )
    return board, state


def test_cost_is_one_without_bridge_state_change() -> None:
    board, state = _basic_problem()
    lying_state = GameState(Block(1, 2, Orientation.HORIZONTAL))

    assert get_step_cost(board, state, lying_state) == 1


def test_cost_is_two_when_switch_changes_bridge_state() -> None:
    board, state = _switch_problem(TileType.SOFT_SWITCH)
    next_state = GameState(
        state.block,
        bridge_states=(True,),
    )

    assert get_step_cost(board, state, next_state) == 2


def test_orientation_does_not_add_cost() -> None:
    board, standing = _basic_problem()
    lying = GameState(Block(1, 2, Orientation.HORIZONTAL))

    assert get_step_cost(board, standing, lying) == 1
    assert get_step_cost(board, lying, standing) == 1


def test_goal_heuristic_is_zero() -> None:
    board, _ = _basic_problem()
    goal_state = GameState(Block(4, 6, Orientation.STANDING))

    assert goal_distance(board, goal_state) == 0


def test_astar_and_ucs_find_same_basic_optimal_cost() -> None:
    board, state = _basic_problem()
    astar_result = solve_astar(board, state)
    ucs_result = solve_ucs(board, state)

    assert astar_result is not None
    assert ucs_result is not None
    assert astar_result["total_cost"] == ucs_result["total_cost"] == 9
    assert is_goal_state(board, astar_result["path"][-1])


def test_astar_solves_soft_switch_problem_with_activation_cost() -> None:
    board, state = _switch_problem(TileType.SOFT_SWITCH)
    astar_result = solve_astar(board, state)
    ucs_result = solve_ucs(board, state)

    assert astar_result is not None
    assert ucs_result is not None
    assert astar_result["total_cost"] == ucs_result["total_cost"]
    assert astar_result["total_cost"] == len(astar_result["moves"]) + 1
    assert astar_result["path"][-1].bridge_states == (True,)


def test_astar_solves_heavy_switch_problem_with_activation_cost() -> None:
    board, state = _switch_problem(TileType.HEAVY_SWITCH)
    astar_result = solve_astar(board, state)
    ucs_result = solve_ucs(board, state)

    assert astar_result is not None
    assert ucs_result is not None
    assert astar_result["total_cost"] == ucs_result["total_cost"]
    assert astar_result["total_cost"] == len(astar_result["moves"]) + 1
    assert astar_result["path"][-1].bridge_states == (True,)


def test_heuristic_is_consistent_on_switch_state_graph() -> None:
    board, initial_state = _switch_problem(TileType.HEAVY_SWITCH)
    frontier = deque([initial_state])
    visited = {initial_state}

    while frontier:
        state = frontier.popleft()
        for _, next_state in get_valid_moves(board, state):
            step_cost = get_step_cost(board, state, next_state)
            assert goal_distance(board, state) <= (
                step_cost + goal_distance(board, next_state)
            )

            if next_state not in visited:
                visited.add(next_state)
                frontier.append(next_state)
