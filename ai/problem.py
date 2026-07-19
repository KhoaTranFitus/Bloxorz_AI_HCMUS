"""Shared transition-cost model for informed and cost-based search."""

from core.board import Board
from core.state import GameState


NORMAL_STEP_COST = 1
SWITCH_ACTIVATION_COST = 2
MINIMUM_STEP_COST = NORMAL_STEP_COST


def get_step_cost(
    board: Board,
    current_state: GameState,
    next_state: GameState,
) -> int:
    """Return the cost of one valid transition.

    A move that changes bridge state costs two. Every other move costs one.
    Orientation and the number of occupied cells do not add extra cost.
    ``board`` remains part of the API so future terrain costs can be added
    without changing solver call sites.
    """

    del board

    if current_state.bridge_states != next_state.bridge_states:
        return SWITCH_ACTIVATION_COST

    return NORMAL_STEP_COST
