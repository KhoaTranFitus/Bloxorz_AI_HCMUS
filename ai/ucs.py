"""Uniform-cost search using the shared terrain cost model."""

from heapq import heappop, heappush
from itertools import count

from ai.base_solver import BaseSolver
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


class UCSSolver(BaseSolver):
    """Expand the frontier state with the lowest accumulated cost."""

    def _calculate_cost(
        self,
        board: Board,
        current_state: GameState,
        next_state: GameState,
    ) -> int:
        return get_step_cost(board, current_state, next_state)

    def solve(self, board: Board, initial_state: GameState) -> SearchResult:
        sequence = count()
        frontier: list[tuple[int, int, GameState]] = []
        best_cost: dict[GameState, int] = {initial_state: 0}
        parents: dict[GameState, tuple[GameState, Move]] = {}
        expanded_nodes = 0

        heappush(frontier, (0, next(sequence), initial_state))

        while frontier:
            cost, _, state = heappop(frontier)
            if cost != best_cost.get(state):
                continue

            if is_goal_state(board, state):
                return SearchResult(
                    _reconstruct_moves(parents, state),
                    cost,
                    expanded_nodes,
                )

            expanded_nodes += 1

            for move, next_state in get_valid_moves(board, state):
                next_cost = cost + self._calculate_cost(
                    board,
                    state,
                    next_state,
                )
                if next_cost >= best_cost.get(next_state, float("inf")):
                    continue

                best_cost[next_state] = next_cost
                parents[next_state] = (state, move)
                heappush(frontier, (next_cost, next(sequence), next_state))

        return SearchResult.no_solution(expanded_nodes)


def solve_ucs(board: Board, initial_state: GameState) -> SearchResult:
    """Functional compatibility wrapper around :class:`UCSSolver`."""

    return UCSSolver().solve(board, initial_state)
