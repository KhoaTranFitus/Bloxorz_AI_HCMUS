"""AI result representation."""
from dataclasses import dataclass
from core.enums import Move


@dataclass
class SearchResult:
    """Kết quả trả về của một thuật toán AI solver."""
    
    actions: list[Move]
    search_time: float
    peak_memory: float
    expanded_nodes: int
    path_length: int
