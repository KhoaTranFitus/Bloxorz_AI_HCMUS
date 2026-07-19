"""Depth-first search solver."""

from ai.base_solver import BaseSolver
from ai.result import SolveResult
from core.board import Board
from core.enums import Move
from core.level import Level
from core.state import GameState
from core.transition import get_valid_moves, is_goal_state


class DFSSolver(BaseSolver):
    """Explore states with a LIFO stack."""

    def solve(self, board: Board, initial_state: GameState) -> SolveResult:
        stack: list[
            tuple[GameState, list[Move], list[GameState]]
        ] = [(initial_state, [], [initial_state])]
        visited: set[GameState] = {initial_state}
        nodes_expanded = 0
        nodes_generated = 1

        while stack:
            state, moves, path = stack.pop()

            if is_goal_state(board, state):
                return SolveResult(
                    algorithm="DFS",
                    success=True,
                    moves=moves,
                    path=path,
                    nodes_expanded=nodes_expanded,
                    nodes_generated=nodes_generated,
                    total_cost=len(moves),
                )

            nodes_expanded += 1

            for move, next_state in get_valid_moves(board, state):
                if next_state in visited:
                    continue

                visited.add(next_state)
                nodes_generated += 1
                stack.append((
                    next_state,
                    moves + [move],
                    path + [next_state],
                ))

        return SolveResult(algorithm="DFS", success=False)

    def dfs_solve(self, board: Board, initial_state: GameState) -> SolveResult:
        """Compatibility alias for older callers."""

        return self.solve(board, initial_state)


def dfs_search(level: Level) -> dict | None:
    """Level-based adapter compatible with ``run_with_profiling``."""
    result = DFSSolver().solve(level.board, level.initial_state)
    if not result.success:
        return None

    return {
        "moves": result.moves,
        "path": result.path,
        "nodes_expanded": result.nodes_expanded,
        "nodes_generated": result.nodes_generated,
        "total_cost": result.total_cost,
    }
