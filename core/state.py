"""Game state placeholder."""
from dataclasses import dataclass

from core.block import Block


@dataclass(frozen=True)
class GameState:
    """
    Toàn bộ trạng thái có thể thay đổi của trò chơi.

    Hiện tại chỉ xử lý block thông thường.

    bridge_states và split_cubes được chuẩn bị trước để sau này
    thêm bridge, switch và split block mà không phải thay đổi
    toàn bộ kiến trúc solver.
    """

    block: Block

    # Mỗi phần tử biểu diễn trạng thái đóng/mở của một bridge.
    # Phiên bản hiện tại chưa sử dụng.
    bridge_states: tuple[bool, ...] = ()

    # Khi block bị tách, đây sẽ là vị trí hai cube.
    # Tuple rỗng nghĩa là block chưa bị tách.
    split_cubes: tuple[tuple[int, int], ...] = ()

    # Cube hiện đang được điều khiển khi block bị tách.
    active_cube: int | None = None

    @property
    def is_split(self) -> bool:
        return len(self.split_cubes) == 2