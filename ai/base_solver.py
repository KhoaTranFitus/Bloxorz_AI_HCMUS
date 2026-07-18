"""Common interface implemented by search solvers."""

from abc import ABC, abstractmethod

from ai.result import SearchResult
from core.board import Board
from core.state import GameState


class BaseSolver(ABC):
    @abstractmethod
    def solve(self, board: Board, initial_state: GameState) -> SearchResult:
        """Search for a path from ``initial_state`` to the board goal."""
