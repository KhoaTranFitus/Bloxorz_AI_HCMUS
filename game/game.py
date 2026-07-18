"""Main game controller."""

from pathlib import Path

from ursina import (
    Button,
    Entity,
    Text,
    Vec3,
    camera,
    color,
    invoke,
)

BACKGROUND_COLOR = color.rgb32(45, 55, 70)


from core.enums import Move
from core.level import Level
from core.level_loader import load_level
from core.state import GameState
from core.transition import apply_move, is_goal_state
from game.renderer import BlockRenderer, BoardRenderer
from collections.abc import Callable

class GameController(Entity):
    MOVE_ANIMATION_TIME = 0.28
    FALL_ANIMATION_TIME = 1.05
    FALL_ROLL_TIME = 0.30
    FALL_DROP_TIME = 0.70
    FALL_RESET_DELAY = FALL_ROLL_TIME + FALL_DROP_TIME + 0.10
    MOVE_KEYS: dict[str, Move] = {
        "up arrow": Move.UP,
        "w": Move.UP,

        "down arrow": Move.DOWN,
        "s": Move.DOWN,

        "left arrow": Move.LEFT,
        "a": Move.LEFT,

        "right arrow": Move.RIGHT,
        "d": Move.RIGHT,
    }

    def __init__(
        self,
        level_path: str | Path,
        on_back: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()

        self.level_path = Path(level_path)
        self.on_back = on_back

        self.level: Level = load_level(self.level_path)

        self.state: GameState = self.level.initial_state
        self.move_count = 0
        self.has_won = False
        self.is_busy = False

        self.board_renderer = BoardRenderer(self.level.board)

        self.block_renderer = BlockRenderer()
        self.block_renderer.sync_with_state(self.state,reset_rotation=True,)

        self._create_environment()
        self._create_ui()
        self._setup_camera()
        self._update_status_text()
        self._create_back_button()
        
    def _create_back_button(self) -> None:
        self.back_button = Button(
            parent=camera.ui,
            text="Back",
            position=(-0.72, 0.43),
            scale=(0.14, 0.07),
            color=color.rgb32(80, 90, 110),
        )

        self.back_button.on_click = self._go_back

    def _go_back(self) -> None:
        if self.on_back is not None:
            self.on_back()

    def _create_environment(self) -> None:
        """
        Thiết lập màu nền và ánh sáng cho game.
        """

        # Màu nền thật sự phía sau toàn bộ bàn chơi.
        camera.clear_color = BACKGROUND_COLOR

        # # Ánh sáng môi trường giúp các mặt không bị tối đen.
        # self.ambient_light = AmbientLight(
        #     color=AMBIENT_LIGHT_COLOR
        # )

        # # Ánh sáng chính tạo chiều sâu cho block và các viên gạch.
        # self.directional_light = DirectionalLight(
        #     shadows=False
        # )

        # self.directional_light.color = (
        #     DIRECTIONAL_LIGHT_COLOR
        # )

        # self.directional_light.look_at(
        #     Vec3(1, -2, 1)
        # )
    def _create_ui(self) -> None:
        """
        Tạo giao diện chữ và nút Restart.
        """

        self.title_text = Text(
            text=self.level.name,
            position=(-0.87, 0.46),
            scale=1.3,
            color=color.rgb(235, 240, 245),
        )

        self.status_text = Text(
            text="",
            position=(-0.87, 0.40),
            scale=1.0,
            color=color.white,
        )

        self.control_text = Text(
            text=(
                "Move: WASD / Arrow keys\n"
                "Restart: R\n"
            ),
            position=(-0.87, 0.31),
            scale=0.85,
            color=color.rgb(195, 205, 215),
        )

        self.restart_button = Button(
            text="Restart",
            position=(0.72, 0.43),
            scale=(0.18, 0.07),
            color=color.rgb(45, 130, 190),
            highlight_color=color.rgb(65, 155, 215),
            pressed_color=color.rgb(30, 100, 155),
            text_color=color.white,
            on_click=self.restart,
        )
    def _setup_camera(self) -> None:
        """
        Camera có góc nhìn cố định cho tất cả màn chơi.

        Camera không xoay, không zoom bằng phím và không di chuyển
        trong quá trình chơi. Chỉ điều chỉnh phạm vi nhìn để toàn bộ
        bàn chơi luôn nằm trong màn hình.
        """

        board_width = self.level.board.width
        board_height = self.level.board.height

        # Tâm của bàn chơi.
        center_x = (board_width - 1) / 2
        center_z = -(board_height - 1) / 2

        board_center = Vec3(
            center_x,
            0,
            center_z,
        )

        # Camera trực giao giúp các viên gạch không bị méo do phối cảnh.
        camera.orthographic = True

        # Một góc nhìn cố định cho tất cả level.
        camera.position = board_center + Vec3(
            10,
            14,
            -14,
        )

        camera.look_at(board_center)

        # Chỉ thay đổi vùng nhìn để level lớn vẫn nằm trọn màn hình.
        board_size = max(
            board_width,
            board_height,
        )

        camera.fov = board_size + 4

    def input(self, key: str) -> None:
        """
        Nhận thao tác bàn phím từ Ursina.
        """

        if key == "r":
            self.restart()
            return

        if key in self.MOVE_KEYS:
            self.try_move(self.MOVE_KEYS[key])
            return

    def try_move(self, move: Move) -> None:
        """
        Thử di chuyển block theo hướng được chọn.
        """

        if self.has_won or self.is_busy:
            return

        # Khóa input trong lúc animation.
        self.is_busy = True
        

        next_state = apply_move(
            self.level.board,
            self.state,
            move,
        )

        # Nước đi không hợp lệ: block rơi xuống.
        if next_state is None:
            self._show_temporary_message("You fell!")

            self.block_renderer.animate_fall(move,
                current_state=self.state,
                roll_duration=self.FALL_ROLL_TIME,
                fall_duration=self.FALL_DROP_TIME,)

            invoke(
                self._reset_after_fall,
                delay=self.FALL_RESET_DELAY,
            )

            return

        # Nước đi hợp lệ: chạy animation trước.
        self.block_renderer.animate_to_state(
            current_state=self.state,
            next_state=next_state,
            move=move,
            duration=self.MOVE_ANIMATION_TIME,
        )

        # Sau khi animation kết thúc mới cập nhật state.
        invoke(
            self._finish_valid_move,
            next_state,
            delay=self.MOVE_ANIMATION_TIME,
        )
    def _finish_valid_move(
        self,
        next_state: GameState,
    ) -> None:
        """
        Hoàn tất một nước đi sau animation.
        """

        self.state = next_state
        self.move_count += 1
        self.is_busy = False

        self._update_status_text()

        if is_goal_state(self.level.board, self.state):
            self.has_won = True

            self.status_text.text = (
                "YOU WIN!\n"
                f"Moves: {self.move_count}"
            )

            self.status_text.color = color.lime

    def _reset_after_fall(self) -> None:
        """
        Đưa block về trạng thái đầu sau khi rơi.
        """

        self.state = self.level.initial_state
        self.move_count = 0
        self.has_won = False
        self.is_busy = False

        self.block_renderer.sync_with_state(
            self.state,
            reset_rotation=True,
        )

        self._update_status_text()

    def restart(self) -> None:
        """
        Đưa game về trạng thái ban đầu.
        """

        self.state = self.level.initial_state
        self.move_count = 0
        self.has_won = False
        self.is_busy = False

        self.block_renderer.sync_with_state(self.state,reset_rotation=True,)
        self._update_status_text()

    def _update_status_text(self) -> None:
        """
        Cập nhật số bước và trạng thái của block.
        """

        orientation_name = self.state.block.orientation.name

        self.status_text.text = (
            f"Moves: {self.move_count}\n"
            f"Orientation: {orientation_name}"
        )

        self.status_text.color = color.white

    def _show_temporary_message(self, message: str) -> None:
        """
        Hiện thông báo lỗi tạm thời.
        """

        self.status_text.text = message
        self.status_text.color = color.red

        invoke(
            self._restore_status,
            delay=0.7,
        )

    def _restore_status(self) -> None:
        """
        Khôi phục nội dung trạng thái sau thông báo tạm thời.
        """

        if self.has_won:
            return

        self._update_status_text()
