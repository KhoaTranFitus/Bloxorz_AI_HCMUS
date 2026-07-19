"""Base solver definition."""
from abc import ABC, abstractmethod

from core.board import Board
from core.state import GameState
from ai.result import SolveResult

class BaseSolver(ABC):
    """
    Lớp cơ sở trừu tượng cho tất cả thuật toán AI tìm đường.
    """

    @abstractmethod
    def solve(self, board: Board, initial_state: GameState) -> SolveResult:
        """
        Khởi chạy quá trình tìm kiếm.
        
        Args:
            board: Bản đồ hiện tại của màn chơi.
            initial_state: Trạng thái xuất phát của game.
            
        Returns:
            SolveResult: Kết quả chứa đường đi và các metrics (thời gian, bộ nhớ, số node).
        """
        pass
