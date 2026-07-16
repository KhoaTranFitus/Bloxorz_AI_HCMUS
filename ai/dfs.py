"""Depth-First Search (DFS) solver."""
from ai.base_solver import BaseSolver
from ai.result import SearchResult
from ai.profiler import Profiler
from core.board import Board
from core.state import GameState
from core.enums import Move
from core.transition import get_valid_moves, is_goal_state

class DFSSolver(BaseSolver):
    """
    Thuật toán tìm kiếm theo chiều sâu (Depth-First Search).
    Sử dụng Stack (list) để duyệt các node.
    """

    def solve(self, board: Board, initial_state: GameState) -> SearchResult:
        profiler = Profiler()
        profiler.start()

        # Mỗi phần tử trong stack là: (current_state, path_so_far)
        stack: list[tuple[GameState, list[Move]]] = [(initial_state, [])]
        visited: set[GameState] = set([initial_state])
        expanded_nodes = 0

        final_path: list[Move] | None = None

        while stack:
            current_state, path = stack.pop()

            if is_goal_state(board, current_state):
                final_path = path
                break

            expanded_nodes += 1

            # Sinh các successor hợp lệ
            # DFS thường thêm con vào stack theo thứ tự lùi để duyệt theo thứ tự đúng 
            # (hoặc không cần thiết miễn là đi sâu).
            for move, next_state in get_valid_moves(board, current_state):
                if next_state not in visited:
                    visited.add(next_state)
                    stack.append((next_state, path + [move]))

        profiler.stop()

        if final_path is None:
            # Không tìm thấy đường đi
            final_path = []

        return SearchResult(
            actions=final_path,
            search_time=profiler.get_search_time,
            peak_memory=profiler.get_peak_memory,
            expanded_nodes=expanded_nodes,
            path_length=len(final_path)
        )
