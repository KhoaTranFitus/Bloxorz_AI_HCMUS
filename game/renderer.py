"""3D renderer for the Bloxorz board and block."""

from ursina import Entity, Vec3, color, destroy

from core.board import Board
from core.enums import Orientation, TileType
from core.state import GameState


# Màu nền xám, khối đỏ, lỗ đen.
FLOOR_COLOR = color.rgb(90, 90, 90)
GOAL_COLOR = color.rgb(0, 0, 0)
BLOCK_COLOR = color.rgb(220, 20, 20)
SOFT_SWITCH_COLOR = color.rgb(255, 190, 0)
HEAVY_SWITCH_COLOR = color.rgb(255, 0, 80)
BRIDGE_COLOR = color.rgb(70, 150, 190)
FRAGILE_COLOR = color.rgb(205, 175, 120)


class BoardRenderer:
    TILE_HEIGHT = 0.25

    # Tile width is slightly smaller than the grid spacing,
    # so each tile becomes a distinct square with visible gaps.
    TILE_WIDTH = 0.92

    def __init__(self, board: Board) -> None:
        self.board = board
        self.tile_entities: list[Entity] = []
        self.border_entities: list[Entity] = []
        self.bridge_entities: dict[int, list[Entity]] = {}

        self._create_tiles()

    def _create_tiles(self) -> None:
        for row in range(self.board.height):
            for col in range(self.board.width):
                tile_type = self.board.get_tile(row, col)

                if tile_type == TileType.VOID:
                    continue

                if tile_type == TileType.GOAL:
                    self._create_goal(row, col)
                elif tile_type == TileType.SOFT_SWITCH:
                    self._create_floor(row, col, SOFT_SWITCH_COLOR)
                elif tile_type == TileType.HEAVY_SWITCH:
                    self._create_floor(row, col, HEAVY_SWITCH_COLOR)
                elif tile_type == TileType.BRIDGE:
                    bridge_id = self.board.get_bridge_id(row, col)
                    border_start = len(self.border_entities)
                    tile = self._create_floor(row, col, BRIDGE_COLOR)
                    if bridge_id is not None:
                        bridge_parts = [
                            tile,
                            *self.border_entities[border_start:],
                        ]
                        self.bridge_entities.setdefault(bridge_id, []).extend(
                            bridge_parts
                        )
                elif tile_type == TileType.FRAGILE:
                    self._create_floor(row, col, FRAGILE_COLOR)
                else:
                    self._create_floor(row, col)

    def _create_floor(
        self,
        row: int,
        col: int,
        tile_color=FLOOR_COLOR,
        create_border: bool = True,
    ) -> Entity:
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
        if create_border:
            self._create_tile_border(row, col)
        return tile

    def sync_with_state(self, state: GameState) -> None:
        for bridge_id, entities in self.bridge_entities.items():
            is_open = (
                bridge_id < len(state.bridge_states)
                and state.bridge_states[bridge_id]
            )
            for entity in entities:
                entity.enabled = is_open

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
        # Outline entity (black) and inner block (red) to make block edges clear.
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

    def sync_with_state(self, state: GameState) -> None:
        block = state.block

        if block.orientation == Orientation.STANDING:
            inner = Vec3(0.76, 2.0, 0.76)
            outline = inner + Vec3(0.06, 0.06, 0.06)

            self.outline.scale = outline
            self.entity.scale = inner

            pos = Vec3(block.col, self.TILE_TOP_Y + 1.0, -block.row)
            self.outline.position = pos
            self.entity.position = pos

        elif block.orientation == Orientation.HORIZONTAL:
            inner = Vec3(2.0, 0.76, 0.76)
            outline = inner + Vec3(0.06, 0.06, 0.06)

            self.outline.scale = outline
            self.entity.scale = inner

            pos = Vec3(block.col + 0.5, self.TILE_TOP_Y + 0.38, -block.row)
            self.outline.position = pos
            self.entity.position = pos

        elif block.orientation == Orientation.VERTICAL:
            inner = Vec3(0.76, 0.76, 2.0)
            outline = inner + Vec3(0.06, 0.06, 0.06)

            self.outline.scale = outline
            self.entity.scale = inner

            pos = Vec3(block.col, self.TILE_TOP_Y + 0.38, -(block.row + 0.5))
            self.outline.position = pos
            self.entity.position = pos

        else:
            raise ValueError(
                f"Unsupported orientation: {block.orientation}"
            )

        self.entity.rotation = Vec3(0, 0, 0)

    def destroy(self) -> None:
        destroy(self.entity)
        destroy(self.outline)
