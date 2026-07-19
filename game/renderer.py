"""3D renderer for the Bloxorz board and block."""

from ursina import Entity, Vec3, color, destroy, Text, scene

from core.board import Board
from core.enums import Move, Orientation, TileType
from core.state import GameState
from game.animation import BlockAnimator


# =========================================================
# CÁC MÀU CÓ THỂ THAY ĐỔI
# =========================================================

FLOOR_COLOR = color.rgb32(125, 135, 145)
BORDER_COLOR = color.rgb32(0, 0, 0)
GOAL_COLOR = color.rgb32(0, 0, 0)
BLOCK_COLOR = color.rgb32(220, 30, 30)

class BoardRenderer:
    TILE_HEIGHT = 0.20
    TILE_WIDTH = 0.94

    # Viền rộng bao nhiêu.
    BORDER_SIZE = 0.07

    def __init__(self, board: Board) -> None:
        self.board = board

        # Keep every board entity under one owner.  Destroying this root makes
        # level transitions atomic and prevents tiles from an old level from
        # remaining in the scene.
        self.root = Entity(parent=scene)

        self.tile_entities: list[Entity] = []
        self.border_entities: list[Entity] = []

        self._create_tiles()

    def _create_tiles(self) -> None:
        """Create tiles in row-major order: left-to-right, top-to-bottom."""
        draw_index = 0
        for row, board_row in enumerate(self.board.tiles):
            for col, tile_type in enumerate(board_row):
                if tile_type == TileType.VOID:
                    continue

                if tile_type == TileType.GOAL:
                    self._create_goal(row, col, draw_index)
                else:
                    self._create_floor(row, col, tile_type, draw_index)

                draw_index += 1

    def _create_floor(
        self,
        row: int,
        col: int,
        tile_type: TileType,
        draw_index: int,
    ) -> None:
        """
        Tạo một ô sàn gồm:
        - Đế đen lớn ở dưới.
        - Ô xám nhỏ hơn ở trên.
        """

        tile_color = FLOOR_COLOR
        if tile_type == TileType.SPLIT_SWITCH:
            tile_color = color.rgb(240, 100, 20)
        elif tile_type == TileType.SOFT_SWITCH:
            tile_color = color.rgb(220, 220, 220)
        elif tile_type == TileType.HEAVY_SWITCH:
            tile_color = color.rgb(240, 220, 50)

        # Đế đen tạo viền
        border = Entity(
            parent=self.root,
            name=f"border_{draw_index:03d}_r{row}_c{col}",
            model="cube",
            texture="white_cube",
            position=Vec3(
                col,
                0,
                -row,
            ),
            scale=Vec3(
                0.96,
                0.20,
                0.96,
            ),
            color=BORDER_COLOR,
            collider=None,
        )

        # Ô sàn màu xám
        tile = Entity(
            parent=self.root,
            name=f"tile_{draw_index:03d}_r{row}_c{col}",
            model="cube",
            texture="white_cube",
            position=Vec3(
                col,
                0.035,
                -row,
            ),
            scale=Vec3(
                0.80,
                0.20,
                0.80,
            ),
            color=tile_color,
            collider=None,
        )

        # Ép Ursina cập nhật màu
        border.color = BORDER_COLOR
        tile.color = tile_color

        self.border_entities.append(border)
        self.tile_entities.append(tile)

        # Thêm kí hiệu chiếc kéo cho ô chia đôi
        # if self.tile_entities == TileType.SPLIT_SWITCH:
        #     symbol = Text(
        #         text="X",
        #         parent=scene,
        #         position=Vec3(col, self.TILE_HEIGHT / 2 + 0.02, -row),
        #         scale=15,
        #         color=color.black, # Màu đen nổi bật trên nền cam
        #         origin=(0, 0),
        #     )
        #     symbol.rotation_x = 90
        #     # Cần lưu trữ để hủy khi đổi level
        #     self.tile_entities.append(symbol)
    def _create_goal(self, row: int, col: int, draw_index: int) -> None:
        """
        Goal là một ô màu đen thấp hơn sàn.
        """

        goal = Entity(
            parent=self.root,
            name=f"goal_{draw_index:03d}_r{row}_c{col}",
            model="cube",
            texture="white_cube",
            position=Vec3(
                col,
                -0.04,
                -row,
            ),
            scale=Vec3(
                0.82,
                0.08,
                0.82,
            ),
            color=GOAL_COLOR,
            collider=None,
        )

        goal.color = GOAL_COLOR

        self.tile_entities.append(goal)

    def destroy(self) -> None:
        destroy(self.root)
        self.tile_entities.clear()
        self.border_entities.clear()

class BlockRenderer:
    TILE_TOP_Y = BoardRenderer.TILE_HEIGHT / 2

    def __init__(self) -> None:
        # Outline entity (black) and inner block (red) for the active block/cube
        """
        Root chịu trách nhiệm về vị trí và góc xoay.

        Outline và block đỏ là con của root nên chúng sẽ
        cùng di chuyển và xoay trong quá trình animation.
        """

        self.root = Entity()

        # Viền ngoài của block.
        self.outline = Entity(
            parent=self.root,
            model="cube",
            texture="white_cube",
            color=color.rgb(25, 25, 28),
            scale=Vec3(0.84, 2.08, 0.84),
            position=Vec3(0, 0, 0),
        )

        # Phần block màu đỏ bên trong.
        self.entity = Entity(
            parent=self.root,
            model="cube",
            texture="white_cube",
            color=BLOCK_COLOR,
            scale=Vec3(0.76, 2.0, 0.76),
            position=Vec3(0, 0, 0),
        )

        self.animator = BlockAnimator(
            root=self.root,
            tile_top_y=self.TILE_TOP_Y,
            get_position=self._get_position,
            sync_with_state=self.sync_with_state,
        )

        # Inactive cube entities (only shown when split)
        self.inactive_outline = Entity(
            parent=self.root,
            model="cube",
            texture="white_cube",
            color=color.black,
            visible=False,
        )

        self.inactive_entity = Entity(
            model="cube",
            texture="white_cube",
            color=color.rgb(140, 40, 40), # Màu đỏ sẫm hơn để biểu thị bị động
            parent=self.root,
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

    def _get_position(self, state: GameState) -> Vec3:
        """
        Tính vị trí tâm của block dựa vào trạng thái.
        """

        block = state.block

        if block.orientation == Orientation.STANDING:
            return Vec3(
                block.col,
                self.TILE_TOP_Y + 1.0,
                -block.row,
            )

        if block.orientation == Orientation.HORIZONTAL:
            return Vec3(
                block.col + 0.5,
                self.TILE_TOP_Y + 0.38,
                -block.row,
            )

        if block.orientation == Orientation.VERTICAL:
            return Vec3(
                block.col,
                self.TILE_TOP_Y + 0.38,
                -(block.row + 0.5),
            )

        raise ValueError(
            f"Unsupported orientation: {block.orientation}"
        )

    def _get_initial_rotation(
        self,
        state: GameState,
    ) -> Vec3:
        """
        Góc xoay ban đầu tương ứng với từng orientation.
        """

        orientation = state.block.orientation

        if orientation == Orientation.STANDING:
            return Vec3(0, 0, 0)

        if orientation == Orientation.HORIZONTAL:
            # Block nằm theo trục X.
            return Vec3(0, 0, -90)

        if orientation == Orientation.VERTICAL:
            # Block nằm theo trục Z.
            return Vec3(90, 0, 0)

        raise ValueError(
            f"Unsupported orientation: {orientation}"
        )

    def sync_with_state(
        self,
        state: GameState,
        reset_rotation: bool = False,
    ) -> None:
        """
        Đặt block ngay lập tức về đúng trạng thái.

        Dùng khi:
        - Bắt đầu game.
        - Restart.
        - Sau khi block rơi.
        """

        self.animator.clear_roll_pivot()
        self.root.position = self._get_position(state)

        if reset_rotation:
            self.root.rotation = self._get_initial_rotation(state)

    def cancel_animation(self) -> None:
        self.animator.cancel()

    def animate_to_state(
        self,
        current_state: GameState,
        next_state: GameState,
        move: Move,
        duration: float = 0.2,
    ) -> None:
        """
        Animation lăn block đến trạng thái hợp lệ tiếp theo.
        """

        self.animator.animate_to_state(
            current_state=current_state,
            next_state=next_state,
            move=move,
            duration=duration,
        )

    def animate_fall(
        self,
        move: Move,
        current_state: GameState,
        roll_duration: float = 0.25,
        fall_duration: float = 0.65,
    ) -> None:
        """
        Block nghiêng về hướng di chuyển rồi rơi xuống.
        """

        self.animator.animate_fall(
            move=move,
            current_state=current_state,
            roll_duration=roll_duration,
            fall_duration=fall_duration,
        )

    def destroy(self) -> None:
        self.animator.destroy()
        destroy(self.root)
