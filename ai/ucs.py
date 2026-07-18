"""Uniform Cost Search (UCS) solver."""
import heapq
from ai.base_solver import BaseSolver
from ai.result import SearchResult
from ai.profiler import Profiler
from core.board import Board
from core.state import GameState
from core.enums import Move, TileType
from core.transition import get_valid_moves, is_goal_state

class UCSSolver(BaseSolver):
    """
    Thuật toán Uniform Cost Search.
    Sử dụng Priority Queue (heapq) để duyệt các node theo chi phí đường đi (cost).
    """

    def _calculate_cost(self, board: Board, current_state: GameState, next_state: GameState) -> int:
        """
        Logic tính hàm Cost (Cost Function):
        - Đi trên gạch cứng bình thường (Floor): Cost = 1
        - Bước đi làm thay đổi trạng thái cầu/công tắc: Cost = 2
        - Bước đi đè lên gạch dễ vỡ (Fragile): Cost = 5
        """
        # Nếu trạng thái cầu thay đổi (công tắc đã được kích hoạt)
        if current_state.bridge_states != next_state.bridge_states:
            return 2

        # Kiểm tra xem có ô nào nằm đè lên gạch dễ vỡ (Fragile) không
        for r, c in next_state.block.occupied_cells():
            if board.get_tile(r, c) == TileType.FRAGILE:
                return 5

        # Mặc định Floor / Goal
        return 1

    def solve(self, board: Board, initial_state: GameState) -> SearchResult:
        profiler = Profiler()
        profiler.start()

        # Frontier dùng heapq. Cấu trúc phần tử: (cost, id, current_state, path_so_far)
        # Bổ sung counter `id` để tránh heapq so sánh GameState khi cost bằng nhau.
        counter = 0
        frontier = [(0, counter, initial_state, [])]
        
        # Dictonary `cost_so_far` dùng để theo dõi chi phí thấp nhất để đến được 1 state
        cost_so_far: dict[GameState, int] = {initial_state: 0}
        
        expanded_nodes = 0
        final_path: list[Move] | None = None

        while frontier:
            current_cost, _, current_state, path = heapq.heappop(frontier)

            if is_goal_state(board, current_state):
                final_path = path
                break

            expanded_nodes += 1

            for move, next_state in get_valid_moves(board, current_state):
                step_cost = self._calculate_cost(board, current_state, next_state)
                new_cost = current_cost + step_cost

                # Nếu state này chưa được duyệt hoặc tìm được đường đi có cost rẻ hơn
                if next_state not in cost_so_far or new_cost < cost_so_far[next_state]:
                    cost_so_far[next_state] = new_cost
                    counter += 1
                    heapq.heappush(frontier, (new_cost, counter, next_state, path + [move]))

        profiler.stop()

        if final_path is None:
            final_path = []

        return SearchResult(
            actions=final_path,
            search_time=profiler.get_search_time,
            peak_memory=profiler.get_peak_memory,
            expanded_nodes=expanded_nodes,
            path_length=len(final_path)
        )
