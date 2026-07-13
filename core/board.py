"""Board-related logic placeholder."""
from dataclasses import dataclass

from core.enums import TileType


@dataclass(frozen=True)
class Board:
    width: int
    height: int
    tiles: tuple[tuple[TileType, ...], ...]

    def is_inside(self, row: int, col: int) -> bool:
        return (
            0 <= row < self.height
            and 0 <= col < self.width
        )

    def get_tile(self, row: int, col: int) -> TileType:
        if not self.is_inside(row, col):
            return TileType.VOID

        return self.tiles[row][col]

    def is_walkable(
        self,
        row: int,
        col: int,
        bridge_states: tuple[bool, ...] = (),
    ) -> bool:
        """
        Kiểm tra một ô có thể đỡ block hay không.

        Hiện tại FLOOR và GOAL đều có thể đỡ block.
        Logic bridge sẽ được thêm sau.
        """

        tile = self.get_tile(row, col)
        return tile in {
            TileType.FLOOR,
            TileType.GOAL,
            TileType.SPLIT_SWITCH,
            TileType.SOFT_SWITCH,
            TileType.HEAVY_SWITCH,
        }

    def find_goal(self) -> tuple[int, int]:
        for row in range(self.height):
            for col in range(self.width):
                if self.tiles[row][col] == TileType.GOAL:
                    return row, col

        raise ValueError("Board does not contain a goal tile")