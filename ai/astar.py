"""A* search over complete Bloxorz game states."""

from heapq import heappop, heappush
from itertools import count

from ai.heuristics import goal_distance
from ai.problem import get_step_cost
from ai.result import SearchResult
from core.board import Board
from core.enums import Move
from core.state import GameState
from core.transition import get_valid_moves, is_goal_state


def _reconstruct_moves(
    parents: dict[GameState, tuple[GameState, Move]],
    state: GameState,
) -> tuple[Move, ...]:
    moves: list[Move] = []

    while state in parents:
        state, move = parents[state]
        moves.append(move)

    moves.reverse()
    return tuple(moves)


def solve_astar(board: Board, initial_state: GameState) -> SearchResult:
    """Find a minimum-move solution from ``initial_state``."""

    sequence = count()
    frontier: list[tuple[int, int, int, GameState]] = []
    best_cost: dict[GameState, int] = {initial_state: 0}
    parents: dict[GameState, tuple[GameState, Move]] = {}
    expanded_nodes = 0

    heappush(
        frontier,
        (goal_distance(board, initial_state), 0, next(sequence), initial_state),
    )

    while frontier:
        _, cost, _, state = heappop(frontier)

        if cost != best_cost.get(state):
            continue

        if is_goal_state(board, state):
            moves = _reconstruct_moves(parents, state)
            return SearchResult(moves, cost, expanded_nodes)

        expanded_nodes += 1

        for move, next_state in get_valid_moves(board, state):
            next_cost = cost + get_step_cost(board, state, next_state)

            if next_cost >= best_cost.get(next_state, float("inf")):
                continue

            best_cost[next_state] = next_cost
            parents[next_state] = (state, move)
            priority = next_cost + goal_distance(board, next_state)
            heappush(
                frontier,
                (priority, next_cost, next(sequence), next_state),
            )

    return SearchResult.no_solution(expanded_nodes)
