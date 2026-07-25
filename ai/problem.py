"""Shared transition-cost model for informed and cost-based search."""

from core.board import Board
from core.enums import TileType
from core.state import GameState


NORMAL_MOVE_COST = 1
SWITCH_MOVE_COST = 2
SPLIT_MOVE_COST = 5
FRAGILE_MOVE_COST = 5
MINIMUM_STEP_COST = NORMAL_MOVE_COST


def get_step_cost(
    board: Board,
    current_state: GameState,
    next_state: GameState,
) -> int:
    """Return the cost of one valid transition.

    A move that splits the block or lands on a fragile tile costs five.
    A move that changes bridge state costs two. Every other move costs one.
    If multiple special costs apply, the first matching cost takes precedence.
    """

    if not current_state.is_split and next_state.is_split:
        return SPLIT_MOVE_COST

    if any(
        board.get_tile(row, col) == TileType.FRAGILE
        for row, col in next_state.occupied_cells()
    ):
        return FRAGILE_MOVE_COST

    if current_state.bridge_states != next_state.bridge_states:
        return SWITCH_MOVE_COST

    return NORMAL_MOVE_COST
