"""3D renderer for the Bloxorz board and block."""

from ursina import Entity, Vec3, color, destroy

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
                    self._create_floor(row, col)

    def _create_floor(self, row: int, col: int) -> None:
        """
        Tạo một ô sàn gồm:
        - Đế đen lớn ở dưới.
        - Ô xám nhỏ hơn ở trên.
        """

        # Đế đen tạo viền
        border = Entity(
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
            color=FLOOR_COLOR,
            collider=None,
        )

        # Ép Ursina cập nhật màu
        border.color = BORDER_COLOR
        tile.color = FLOOR_COLOR

        self.border_entities.append(border)
        self.tile_entities.append(tile)

    def _create_goal(self, row: int, col: int) -> None:
        """
        Goal là một ô màu đen thấp hơn sàn.
        """

        goal = Entity(
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
        for tile in self.tile_entities:
            destroy(tile)

        for border in self.border_entities:
            destroy(border)

        self.tile_entities.clear()
        self.border_entities.clear()

class BlockRenderer:
    TILE_TOP_Y = BoardRenderer.TILE_HEIGHT / 2

    def __init__(self) -> None:
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
