"""Admissible heuristics for Bloxorz search."""

from math import ceil

from ai.problem import MINIMUM_STEP_COST
from core.board import Board
from core.state import GameState


def goal_distance(board: Board, state: GameState) -> int:
    """Optimistic remaining cost, ignoring obstacles and switch detours."""

    goal_row, goal_col = board.find_goal()
    distance = min(
        abs(row - goal_row) + abs(col - goal_col)
        for row, col in state.occupied_cells()
    )
    return ceil(distance / 2) * MINIMUM_STEP_COST
