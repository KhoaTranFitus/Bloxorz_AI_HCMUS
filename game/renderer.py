"""3D renderer for the Bloxorz board and block."""

from ursina import Entity, Vec3, color, destroy, scene

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

    def __init__(
        self,
        board: Board,
        bridge_states: tuple[bool, ...] = (),
    ) -> None:
        self.board = board

        # Keep every board entity under one owner.  Destroying this root makes
        # level transitions atomic and prevents tiles from an old level from
        # remaining in the scene.
        self.root = Entity(parent=scene)

        self.tile_entities: list[Entity] = []
        self.border_entities: list[Entity] = []
        self.bridge_entities: dict[int, list[Entity]] = {}

        self._create_tiles()
        self.sync_bridge_states(bridge_states)

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
            tile_color = color.rgb32(240, 100, 20)
        elif tile_type == TileType.SOFT_SWITCH:
            tile_color = color.rgb32(220, 220, 220)
        elif tile_type == TileType.HEAVY_SWITCH:
            tile_color = color.rgb32(240, 220, 50)
        elif tile_type == TileType.FRAGILE:
            tile_color = color.rgb32(240, 125, 25)

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

        if tile_type == TileType.BRIDGE:
            bridge_id = self.board.get_bridge_id(row, col)
            if bridge_id is not None:
                self.bridge_entities.setdefault(bridge_id, []).extend(
                    (border, tile)
                )

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
        self.bridge_entities.clear()

    def sync_bridge_states(self, bridge_states: tuple[bool, ...]) -> None:
        """Show only bridges whose logical state is currently open."""
        for bridge_id, entities in self.bridge_entities.items():
            is_open = (
                bridge_id < len(bridge_states)
                and bridge_states[bridge_id]
            )
            for entity in entities:
                entity.visible = is_open

class BlockRenderer:
    TILE_TOP_Y = BoardRenderer.TILE_HEIGHT / 2
    CUBE_INNER_SCALE = Vec3(0.76, 0.76, 0.76)
    CUBE_OUTLINE_SCALE = Vec3(0.84, 0.84, 0.84)
    CUBE_BASE_ROTATION = Vec3(0, 0, 0)

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
            color=color.rgb32(25, 25, 28),
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
            parent=scene,
            model="cube",
            texture="white_cube",
            color=color.rgb32(0, 0, 0),
            visible=False,
        )

        self.inactive_entity = Entity(
            model="cube",
            texture="white_cube",
            color=color.rgb32(140, 40, 40), # Màu đỏ sẫm hơn để biểu thị bị động
            parent=scene,
            visible=False,
        )

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
        if block.orientation == Orientation.CUBE:
            return Vec3(
                block.col,
                self.TILE_TOP_Y + 0.38,
                -block.row,
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
        if orientation == Orientation.CUBE:
            return Vec3(0, 0, 0)

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

        if state.is_split:
            active_idx = state.active_cube if state.active_cube is not None else 0
            inactive_idx = 1 - active_idx
            active_row, active_col = state.split_cubes[active_idx]
            inactive_row, inactive_col = state.split_cubes[inactive_idx]

            self.entity.scale = self.CUBE_INNER_SCALE
            self.outline.scale = self.CUBE_OUTLINE_SCALE
            self.entity.position = Vec3(0, 0, 0)
            self.outline.position = Vec3(0, 0, 0)

            self.inactive_entity.visible = True
            self.inactive_outline.visible = True
            self.inactive_entity.scale = self.CUBE_INNER_SCALE
            self.inactive_outline.scale = self.CUBE_OUTLINE_SCALE
            self.inactive_entity.rotation = self.CUBE_BASE_ROTATION
            self.inactive_outline.rotation = self.CUBE_BASE_ROTATION

            inactive_position = Vec3(
                inactive_col,
                self.TILE_TOP_Y + 0.38,
                -inactive_row,
            )
            self.inactive_entity.position = inactive_position
            self.inactive_outline.position = inactive_position
            self.root.position = Vec3(
                active_col,
                self.TILE_TOP_Y + 0.38,
                -active_row,
            )
            self.root.rotation = self.CUBE_BASE_ROTATION
            return

        self.inactive_entity.visible = False
        self.inactive_outline.visible = False
        self.inactive_entity.position = Vec3(0, 0, 0)
        self.inactive_outline.position = Vec3(0, 0, 0)

        # The normal block always has a vertical 1x2 mesh. Its orientation is
        # represented only by root.rotation; changing both scale and rotation
        # would apply the orientation twice.
        self.entity.scale = Vec3(0.76, 2.0, 0.76)
        self.outline.scale = Vec3(0.84, 2.08, 0.84)
        self.entity.position = Vec3(0, 0, 0)
        self.outline.position = Vec3(0, 0, 0)
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

        # A separated cube translates independently and SWITCH has no roll
        # direction. Syncing also swaps the active/inactive visuals correctly.
        if current_state.is_split:
            self.animator.animate_split_to_state(
                current_state=current_state,
                next_state=next_state,
                move=move,
                duration=duration,
            )
            return

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
        destroy(self.inactive_outline)
        destroy(self.inactive_entity)
        destroy(self.root)
