"""Depth-first search solver."""

from ai.base_solver import BaseSolver
from ai.problem import get_step_cost
from ai.result import SolveResult
from core.board import Board
from core.enums import Move
from core.level import Level
from core.state import GameState
from core.transition import get_valid_moves, is_goal_state


class DFSSolver(BaseSolver):
    """Explore states with a LIFO stack."""

    def solve(self, board: Board, initial_state: GameState) -> SolveResult:
        stack: list[tuple[GameState, Move | None]] = [(initial_state, None)]
        visited: set[GameState] = {initial_state}
        parent: dict[GameState, tuple[GameState, Move] | None] = {initial_state: None}
        nodes_expanded = 0
        nodes_generated = 1

        while stack:
            state, _ = stack.pop()

            if is_goal_state(board, state):
                # Reconstruct path
                path = []
                moves = []
                curr = state
                while parent[curr] is not None:
                    prev_state, move = parent[curr]
                    path.append(curr)
                    moves.append(move)
                    curr = prev_state
                path.append(initial_state)
                path.reverse()
                moves.reverse()

                return SolveResult(
                    algorithm="DFS",
                    success=True,
                    moves=moves,
                    path=path,
                    nodes_expanded=nodes_expanded,
                    nodes_generated=nodes_generated,
                    total_cost=sum(
                        get_step_cost(board, path[index], path[index + 1])
                        for index in range(len(path) - 1)
                    ),
                )

            nodes_expanded += 1

            for move, next_state in get_valid_moves(board, state):
                if next_state in visited:
                    continue

                visited.add(next_state)
                parent[next_state] = (state, move)
                nodes_generated += 1
                stack.append((next_state, move))

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
