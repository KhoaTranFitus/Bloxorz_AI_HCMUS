"""Solver profiling utility."""
import time
import tracemalloc

class Profiler:
    """
    Công cụ đo lường thời gian (Time) và bộ nhớ đỉnh (Peak Memory) cho thuật toán.
    Sử dụng context manager để wrap code dễ dàng.
    """
    
    def __init__(self):
        self.start_time = 0.0
        self.end_time = 0.0
        self.peak_memory = 0.0

    def start(self):
        """Bắt đầu đo lường."""
        tracemalloc.start()
        self.start_time = time.perf_counter()

    def stop(self):
        """Dừng đo lường và thu thập metrics."""
        self.end_time = time.perf_counter()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Chuyển đổi peak_memory sang Megabytes (MB)
        self.peak_memory = peak / (1024 * 1024)

    @property
    def get_search_time(self) -> float:
        """Thời gian chạy tính bằng giây."""
        return self.end_time - self.start_time

    @property
    def get_peak_memory(self) -> float:
        """Peak memory tính bằng MB."""
        return self.peak_memory
