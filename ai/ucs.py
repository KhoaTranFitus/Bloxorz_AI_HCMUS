"""Uniform-cost graph search for Bloxorz."""

from heapq import heappop, heappush
from itertools import count

from ai.base_solver import BaseSolver
from ai.problem import get_step_cost
from ai.result import SolveResult
from core.board import Board
from core.enums import Move
from core.level import Level
from core.state import GameState
from core.transition import get_valid_moves, is_goal_state


def _reconstruct_path(
    parents: dict[GameState, tuple[GameState, Move]],
    goal_state: GameState,
) -> tuple[list[Move], list[GameState]]:
    moves: list[Move] = []
    path: list[GameState] = [goal_state]
    state = goal_state

    while state in parents:
        state, move = parents[state]
        moves.append(move)
        path.append(state)

    moves.reverse()
    path.reverse()
    return moves, path


def solve_ucs(
    board: Board,
    initial_state: GameState,
) -> dict | None:
    """Return the minimum-cost path and raw search statistics."""

    sequence = count()
    frontier: list[tuple[int, int, GameState]] = [
        (0, next(sequence), initial_state)
    ]
    best_cost: dict[GameState, int] = {initial_state: 0}
    parents: dict[GameState, tuple[GameState, Move]] = {}
    nodes_expanded = 0
    nodes_generated = 1

    while frontier:
        cost, _, state = heappop(frontier)

        if cost != best_cost.get(state):
            continue

        if is_goal_state(board, state):
            moves, path = _reconstruct_path(parents, state)
            return {
                "moves": moves,
                "path": path,
                "total_cost": cost,
                "nodes_expanded": nodes_expanded,
                "nodes_generated": nodes_generated,
            }

        nodes_expanded += 1

        for move, next_state in get_valid_moves(board, state):
            next_cost = cost + get_step_cost(board, state, next_state)

            if next_cost >= best_cost.get(next_state, float("inf")):
                continue

            best_cost[next_state] = next_cost
            parents[next_state] = (state, move)
            nodes_generated += 1
            heappush(
                frontier,
                (next_cost, next(sequence), next_state),
            )

    return None


def ucs_search(level: Level) -> dict | None:
    """Level-based adapter compatible with ``run_with_profiling``."""

    return solve_ucs(level.board, level.initial_state)


class UCSSolver(BaseSolver):
    """Object-oriented adapter retained for existing solver callers."""

    def solve(self, board: Board, initial_state: GameState) -> SolveResult:
        raw_result = solve_ucs(board, initial_state)
        if raw_result is None:
            return SolveResult(algorithm="UCS", success=False)

        return SolveResult(
            algorithm="UCS",
            success=True,
            moves=raw_result["moves"],
            path=raw_result["path"],
            nodes_expanded=raw_result["nodes_expanded"],
            nodes_generated=raw_result["nodes_generated"],
            total_cost=raw_result["total_cost"],
        )
