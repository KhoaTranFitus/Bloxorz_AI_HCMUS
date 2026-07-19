"""3D renderer for the Bloxorz board and block."""

from ursina import Entity, Vec3, color, destroy, Text, scene

from core.board import Board
from core.enums import Orientation, TileType
from core.state import GameState


# Màu nền xám, khối đỏ, lỗ đen.
FLOOR_COLOR = color.rgb(90, 90, 90)
GOAL_COLOR = color.rgb(0, 0, 0)
BLOCK_COLOR = color.rgb(220, 20, 20)


class BoardRenderer:
    TILE_HEIGHT = 0.25

    # Tile width is slightly smaller than the grid spacing,
    # so each tile becomes a distinct square with visible gaps.
    TILE_WIDTH = 0.92

    def __init__(self, board: Board) -> None:
        self.board = board
        self.tile_entities: list[Entity] = []
        self.border_entities: list[Entity] = []

        self._create_tiles()

    def _create_tiles(self) -> None:
        for row in range(self.board.height):
            for col in range(self.board.width):
                tile_type = self.board.get_tile(row, col)

                if tile_type == TileType.VOID:
                    continue

                if tile_type == TileType.GOAL:
                    self._create_goal(row, col)
                else:
                    self._create_floor(row, col, tile_type)

    def _create_floor(self, row: int, col: int, tile_type: TileType) -> None:
        tile_color = FLOOR_COLOR
        if tile_type == TileType.SPLIT_SWITCH:
            tile_color = color.rgb(240, 100, 20)  # Cam đậm cho Split Switch
        elif tile_type == TileType.SOFT_SWITCH:
            tile_color = color.rgb(220, 220, 220)  # Xám trắng cho Soft Switch
        elif tile_type == TileType.HEAVY_SWITCH:
            tile_color = color.rgb(240, 220, 50)  # Vàng cho Heavy Switch

        tile = Entity(
            model="cube",
            texture=None,
            position=Vec3(
                col,
                0,
                -row,
            ),
            scale=Vec3(
                self.TILE_WIDTH,
                self.TILE_HEIGHT,
                self.TILE_WIDTH,
            ),
            color=tile_color,
            collider=None,
        )

        self.tile_entities.append(tile)
        self._create_tile_border(row, col)

        # Thêm kí hiệu chiếc kéo cho ô chia đôi
        if tile_type == TileType.SPLIT_SWITCH:
            symbol = Text(
                text="X",
                parent=scene,
                position=Vec3(col, self.TILE_HEIGHT / 2 + 0.02, -row),
                scale=15,
                color=color.black, # Màu đen nổi bật trên nền cam
                origin=(0, 0),
            )
            symbol.rotation_x = 90
            # Cần lưu trữ để hủy khi đổi level
            self.tile_entities.append(symbol)

    def _create_goal(self, row: int, col: int) -> None:
        """
        Goal nằm thấp hơn mặt sàn để nhìn giống một cái hố.
        """

        goal = Entity(
            model="cube",
            texture=None,
            position=Vec3(
                col,
                -0.11,
                -row,
            ),
            scale=Vec3(
                self.TILE_WIDTH,
                0.04,
                self.TILE_WIDTH,
            ),
            color=GOAL_COLOR,
            collider=None,
        )

        self.tile_entities.append(goal)
        self._create_tile_border(row, col)

    def destroy(self) -> None:
        for tile in self.tile_entities:
            destroy(tile)

        self.tile_entities.clear()
        for border in self.border_entities:
            destroy(border)

        self.border_entities.clear()


    def _create_tile_border(self, row: int, col: int) -> None:
        thickness = 0.04
        border_height = self.TILE_HEIGHT + 0.01
        half_tile = self.TILE_WIDTH / 2
        offset = half_tile - thickness / 2
        border_y = border_height / 2 - 0.01

        edges = [
            # Left edge
            (col - offset, border_y, -row, thickness, border_height, self.TILE_WIDTH + thickness),
            # Right edge
            (col + offset, border_y, -row, thickness, border_height, self.TILE_WIDTH + thickness),
            # Front edge
            (col, border_y, -row + offset, self.TILE_WIDTH, border_height, thickness),
            # Back edge
            (col, border_y, -row - offset, self.TILE_WIDTH, border_height, thickness),
        ]

        for x, y, z, sx, sy, sz in edges:
            border = Entity(
                model="cube",
                texture=None,
                position=Vec3(x, y, z),
                scale=Vec3(sx, sy, sz),
                color=color.black,
                collider=None,
            )

            self.border_entities.append(border)


class BlockRenderer:
    TILE_TOP_Y = BoardRenderer.TILE_HEIGHT / 2

    def __init__(self) -> None:
        # Outline entity (black) and inner block (red) for the active block/cube
        self.outline = Entity(
            model="cube",
            texture="white_cube",
            color=color.black,
        )

        self.entity = Entity(
            model="cube",
            texture="white_cube",
            color=BLOCK_COLOR,
            parent=None,
        )

        # Inactive cube entities (only shown when split)
        self.inactive_outline = Entity(
            model="cube",
            texture="white_cube",
            color=color.black,
            visible=False,
        )

        self.inactive_entity = Entity(
            model="cube",
            texture="white_cube",
            color=color.rgb(140, 40, 40), # Màu đỏ sẫm hơn để biểu thị bị động
            parent=None,
            visible=False,
        )

    # def sync_with_state(self, state: GameState) -> None:
    #     if state.is_split:
    #         # Hiện khối bị động
    #         self.inactive_outline.visible = True
    #         self.inactive_entity.visible = True

    #         cubes = state.split_cubes
    #         active_idx = state.active_cube
    #         inactive_idx = 1 - active_idx

    #         active_pos = cubes[active_idx]
    #         inactive_pos = cubes[inactive_idx]

    #         # 1. Vẽ khối chủ động
    #         inner = Vec3(0.76, 0.76, 0.76)
    #         outline = inner + Vec3(0.06, 0.06, 0.06)

    #         self.outline.scale = outline
    #         self.entity.scale = inner

    #         pos_active = Vec3(active_pos[1], self.TILE_TOP_Y + 0.38, -active_pos[0])
    #         self.outline.position = pos_active
    #         self.entity.position = pos_active

    #         # 2. Vẽ khối bị động
    #         self.inactive_outline.scale = outline
    #         self.inactive_entity.scale = inner

    #         pos_inactive = Vec3(inactive_pos[1], self.TILE_TOP_Y + 0.38, -inactive_pos[0])
    #         self.inactive_outline.position = pos_inactive
    #         self.inactive_entity.position = pos_inactive

    #     else:
    #         # Ẩn khối bị động
    #         # self.inactive_outline.visible = False
    #         # self.inactive_entity.visible = False

    #         # block = state.block

    #         if block.orientation == Orientation.STANDING:
    #             inner = Vec3(0.76, 2.0, 0.76)
    #             outline = inner + Vec3(0.06, 0.06, 0.06)

    #             self.outline.scale = outline
    #             self.entity.scale = inner

    #             pos = Vec3(block.col, self.TILE_TOP_Y + 1.0, -block.row)
    #             self.outline.position = pos
    #             self.entity.position = pos

    #         elif block.orientation == Orientation.HORIZONTAL:
    #             inner = Vec3(2.0, 0.76, 0.76)
    #             outline = inner + Vec3(0.06, 0.06, 0.06)

    #             self.outline.scale = outline
    #             self.entity.scale = inner

    #             pos = Vec3(block.col + 0.5, self.TILE_TOP_Y + 0.38, -block.row)
    #             self.outline.position = pos
    #             self.entity.position = pos

    #         elif block.orientation == Orientation.VERTICAL:
    #             inner = Vec3(0.76, 0.76, 2.0)
    #             outline = inner + Vec3(0.06, 0.06, 0.06)

    #             self.outline.scale = outline
    #             self.entity.scale = inner

    #             pos = Vec3(block.col, self.TILE_TOP_Y + 0.38, -(block.row + 0.5))
    #             self.outline.position = pos
    #             self.entity.position = pos

    #         elif block.orientation == Orientation.CUBE:
    #             inner = Vec3(0.76, 0.76, 0.76)
    #             outline = inner + Vec3(0.06, 0.06, 0.06)

    #             self.outline.scale = outline
    #             self.entity.scale = inner

    #             pos = Vec3(block.col, self.TILE_TOP_Y + 0.38, -block.row)
    #             self.outline.position = pos
    #             self.entity.position = pos

    #         else:
    #             raise ValueError(
    #                 f"Unsupported orientation: {block.orientation}"
    #             )

    #     self.entity.rotation = Vec3(0, 0, 0)

    def destroy(self) -> None:
        destroy(self.entity)
        destroy(self.outline)
        destroy(self.inactive_entity)
        destroy(self.inactive_outline)
