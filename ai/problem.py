"""Shared search-problem costs for Bloxorz solvers."""

from core.board import Board
from core.enums import TileType
from core.state import GameState


NORMAL_STEP_COST = 1
SWITCH_ACTIVATION_COST = 2
FRAGILE_STEP_COST = 5
MINIMUM_STEP_COST = NORMAL_STEP_COST


def get_step_cost(
    board: Board,
    current_state: GameState,
    next_state: GameState,
) -> int:
    """Return the cost of a transition from current state to next state.

    Activating a switch is detected through a bridge-state change. Fragile
    terrain costs five. Every other valid roll costs one, independently of
    whether the block is standing or lying.
    """

    if current_state.bridge_states != next_state.bridge_states:
        return SWITCH_ACTIVATION_COST

    if any(
        board.get_tile(row, col) == TileType.FRAGILE
        for row, col in next_state.block.occupied_cells()
    ):
        return FRAGILE_STEP_COST

    return NORMAL_STEP_COST
