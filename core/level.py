"""Level data placeholder."""
from dataclasses import dataclass

from core.board import Board
from core.state import GameState


@dataclass(frozen=True)
class Level:
    name: str
    board: Board
    initial_state: GameState