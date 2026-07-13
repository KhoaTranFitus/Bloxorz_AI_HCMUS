"""Dataclass lưu trữ kết quả chạy của một thuật toán tìm kiếm."""

from dataclasses import dataclass, field

from core.enums import Move
from core.state import GameState


@dataclass
class SolveResult:
    """
    Kết quả trả về sau khi chạy một thuật toán solver.

    Được tạo bởi ``run_with_profiling`` trong ``ai/profiler.py``.
    """

    algorithm: str
    """Tên thuật toán: "BFS", "DFS", "UCS", "A*"."""

    success: bool
    """True nếu tìm được lời giải."""

    moves: list[Move] = field(default_factory=list)
    """Chuỗi bước đi từ trạng thái đầu đến goal."""

    path: list[GameState] = field(default_factory=list)
    """Chuỗi state tương ứng (bao gồm initial_state)."""

    nodes_expanded: int = 0
    """Số node đã mở rộng (lấy ra khỏi frontier)."""

    nodes_generated: int = 0
    """Số node đã sinh ra (thêm vào frontier)."""

    search_time: float = 0.0
    """Thời gian tìm kiếm (giây)."""

    memory_usage: float = 0.0
    """Bộ nhớ đỉnh sử dụng (MB)."""

    @property
    def solution_length(self) -> int:
        """Số bước đi trong lời giải."""
        return len(self.moves)
