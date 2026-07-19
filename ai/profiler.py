"""Profiler bọc quanh solver để đo thời gian và bộ nhớ."""

import time
import tracemalloc
from typing import Any, Callable

from core.level import Level
from ai.result import SolveResult


def run_with_profiling(
    algorithm: str,
    search_fn: Callable[[Level], dict[str, Any] | None],
    level: Level,
) -> SolveResult:
    """
    Chạy ``search_fn(level)`` và đo hiệu năng.

    Args:
        algorithm: Tên thuật toán (vd: "BFS").
        search_fn: Hàm tìm kiếm, nhận Level và trả về dict hoặc None.
        level: Level cần giải.

    Returns:
        SolveResult chứa kết quả lời giải và thống kê hiệu năng.
    """

    # ----- Bắt đầu đo -----
    tracemalloc.start()
    start_time = time.perf_counter()

    raw_result = search_fn(level)

    end_time = time.perf_counter()
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # ----- Tính thống kê -----
    search_time = end_time - start_time
    memory_mb = peak_memory / (1024 * 1024)  # bytes → MB

    # ----- Đóng gói kết quả -----
    if raw_result is None:
        return SolveResult(
            algorithm=algorithm,
            success=False,
            search_time=search_time,
            memory_usage=memory_mb,
        )

    return SolveResult(
        algorithm=algorithm,
        success=True,
        moves=raw_result["moves"],
        path=raw_result["path"],
        nodes_expanded=raw_result["nodes_expanded"],
        nodes_generated=raw_result["nodes_generated"],
        total_cost=raw_result.get("total_cost", len(raw_result["moves"])),
        search_time=search_time,
        memory_usage=memory_mb,
    )
