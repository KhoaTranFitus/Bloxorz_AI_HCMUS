"""Shared transition-cost model for informed and cost-based search."""

from core.board import Board
from core.state import GameState


NORMAL_MOVE_COST = 1
SWITCH_MOVE_COST = 2
SPLIT_MOVE_COST = 5
MINIMUM_STEP_COST = NORMAL_MOVE_COST


def get_step_cost(
    board: Board,
    current_state: GameState,
    next_state: GameState,
) -> int:
    """Return the cost of one valid transition.

    A move that splits the block costs five. A move that changes bridge
    state costs two. Every other move costs one. If a transition both splits
    the block and changes a bridge, the split cost takes precedence.
    ``board`` remains part of the API so future terrain costs can be added
    without changing solver call sites.
    """

    del board

    if not current_state.is_split and next_state.is_split:
        return SPLIT_MOVE_COST

    if current_state.bridge_states != next_state.bridge_states:
        return SWITCH_MOVE_COST

    return NORMAL_MOVE_COST
