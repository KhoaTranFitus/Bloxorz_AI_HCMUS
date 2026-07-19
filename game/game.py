"""Main game controller."""

from pathlib import Path
from typing import Any, Callable

from ursina import (
    Button,
    Color,
    DirectionalLight,
    Entity,
    Text,
    Vec3,
    camera,
    color,
    destroy,
    invoke,
)

from ai.bfs import bfs_search
from ai.profiler import run_with_profiling
from ai.result import SolveResult
BACKGROUND_COLOR = color.rgb32(45, 55, 70)


from core.enums import Move
from core.level import Level
from core.level_loader import load_level
from core.state import GameState
from core.transition import apply_move, is_goal_state
from game.renderer import BlockRenderer, BoardRenderer
from game.replay_controller import ReplayController
from gui.statistics_panel import StatisticsPanel

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

    # Registry: tên thuật toán → hàm search tương ứng.
    # Khi DFS/UCS/A* được viết xong, chỉ cần thêm vào đây.
    SOLVER_REGISTRY: dict[str, Callable[..., dict[str, Any] | None] | None] = {
        "BFS": bfs_search,
        "DFS": None,    # Chưa implement
        "UCS": None,    # Chưa implement
        "A*":  None,    # Chưa implement
    }

    def __init__(self, level_path: str | Path) -> None:
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

        print("[DEBUG] NEW GameController loaded — solver buttons active")

        # Lưu trữ kết quả chạy solver (dùng cho Statistics panel)
        self.solver_results: list[SolveResult] = []

        # Replay controller (khởi tạo khi chạy solver)
        self.replay_controller: ReplayController | None = None

        # Statistics panel
        self.statistics_panel = StatisticsPanel()

        self.next_level_button: Button | None = None

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
        # Background image gắn trực tiếp đằng sau camera (local Z = 50)
        # unlit=True giúp ảnh không bị ảnh hưởng bởi ánh sáng 3D
        self.bg_plane = Entity(
            parent=camera,
            model="quad",
            texture="assets/background.png",
            position=(0, 0, 50),
            scale=(100, 56.25),
            unlit=True,
        )

        # Chữ "CodenChill" ở gần mép dưới của màn hình trò chơi
        self.brand_text = Text(
            text="CodenChill",
            position=(0, -0.42),
            origin=(0, 0),
            scale=2.2,
            color=Color(1.0, 1.0, 1.0, 0.75),
        )
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
        Tạo giao diện chữ, nút Restart, nút solver và nút Statistics.
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

        # ----- Nút Restart -----
        self.restart_button = Button(
            text="Restart",
            position=(0.72, 0.43),
            scale=(0.18, 0.07),
            color=Color(0.12, 0.45, 0.72, 1.0),       # Xanh dương nổi bật
            highlight_color=Color(0.18, 0.56, 0.86, 1.0),
            texture=None,
            on_click=self.restart,
        )
        self.restart_button.text_entity.color = Color(1.0, 1.0, 1.0, 1.0)

        # ----- Nút solver (BFS, DFS, UCS, A*) -----
        solver_names = ["BFS", "DFS", "UCS", "A*"]
        button_start_y = 0.33
        button_spacing = 0.085

        self.solver_buttons: list[Button] = []

        for i, name in enumerate(solver_names):
            btn = Button(
                text=name,
                position=(0.72, button_start_y - i * button_spacing),
                scale=(0.18, 0.065),
                color=Color(0.18, 0.20, 0.24, 1.0),       # Màu xám than chì sang trọng
                highlight_color=Color(0.26, 0.29, 0.35, 1.0),
                texture=None,
                on_click=self._make_solver_callback(name),
            )
            btn.text_entity.color = Color(1.0, 0.82, 0.35, 1.0) # Chữ vàng gold tương phản cao
            self.solver_buttons.append(btn)

        # ----- Nút Statistics -----
        self.statistics_button = Button(
            text="Statistics",
            position=(0.72, button_start_y - len(solver_names) * button_spacing - 0.02),
            scale=(0.18, 0.065),
            color=Color(0.28, 0.30, 0.34, 1.0),       # Màu xám đá sáng hơn
            highlight_color=Color(0.38, 0.40, 0.45, 1.0),
            texture=None,
            on_click=self._toggle_statistics,
        )
        self.statistics_button.text_entity.color = Color(1.0, 1.0, 1.0, 1.0)

    def _make_solver_callback(self, algorithm_name: str) -> Callable[[], None]:
        """Tạo closure cho on_click của mỗi nút solver."""

        def callback() -> None:
            self._run_solver(algorithm_name)

        return callback

    def _run_solver(self, algorithm_name: str) -> None:
        """
        Chạy thuật toán solver, lưu kết quả, và bắt đầu replay.
        """

        if self.is_busy:
            self._show_temporary_message("Đang chạy, vui lòng đợi!")
            return

        # Đóng statistics panel nếu đang mở
        if self.statistics_panel.visible:
            self.statistics_panel.hide()

        # Kiểm tra solver đã implement chưa
        search_fn = self.SOLVER_REGISTRY.get(algorithm_name)

        if search_fn is None:
            self._show_temporary_message(
                f"{algorithm_name}: Chưa implement!"
            )
            return

        # Hiển thị trạng thái đang chạy
        self.status_text.text = f"{algorithm_name}: Đang chạy..."
        self.status_text.color = color.yellow

        # Reset game về trạng thái ban đầu trước khi chạy
        self.restart()

        # Chạy solver với profiling
        result = run_with_profiling(algorithm_name, search_fn, self.level)

        # Lưu kết quả (thay thế nếu đã chạy thuật toán này trước đó)
        self.solver_results = [
            r for r in self.solver_results
            if r.algorithm != algorithm_name
        ]
        self.solver_results.append(result)

        if not result.success:
            self._show_temporary_message(
                f"{algorithm_name}: Không tìm được lời giải!"
            )
            return

        # Hiển thị kết quả tìm kiếm
        self.status_text.text = (
            f"{algorithm_name}: {result.solution_length} bước | "
            f"{result.search_time:.4f}s | "
            f"{result.memory_usage:.2f}MB"
        )
        self.status_text.color = color.lime

        # Bắt đầu replay
        self.replay_controller = ReplayController(
            game=self,
            moves=result.moves,
            step_delay=0.4,
        )
        self.replay_controller.start()

    def _toggle_statistics(self) -> None:
        """Bật/tắt panel thống kê."""

        if self.statistics_panel.visible:
            self.statistics_panel.hide()
        else:
            self.statistics_panel.show(self.solver_results)

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

        if key == "space":
            self.try_move(Move.SWITCH)
            return

        if key in self.MOVE_KEYS:
            self.try_move(self.MOVE_KEYS[key])
            return

    def try_move(self, move: Move) -> None:
        """
        Thử di chuyển block theo hướng được chọn (player input).

        Bị block khi đang replay hoặc đã thắng.
        """

        if self.has_won or self.is_busy:
            return

        self._execute_move(move)

    def _execute_move(self, move: Move) -> None:
        """
        Thực hiện di chuyển block (internal).

        Không kiểm tra is_busy — dùng cho cả player lẫn replay.
        """

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

            # Tự động tìm màn tiếp theo
            next_level = self._get_next_level_path()
            if next_level:
                self.next_level_button = Button(
                    text="Next Level",
                    position=(0, 0),
                    scale=(0.22, 0.08),
                    color=Color(0.12, 0.6, 0.3, 1.0), # Xanh lá chiến thắng
                    highlight_color=Color(0.18, 0.75, 0.38, 1.0),
                    texture=None,
                    on_click=lambda: self.load_new_level(next_level)
                )
                self.next_level_button.text_entity.color = Color(1.0, 1.0, 1.0, 1.0)
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

        # Xóa nút Next Level nếu có
        if self.next_level_button:
            destroy(self.next_level_button)
            self.next_level_button = None

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

        if self.state.is_split:
            status = (
                f"Moves: {self.move_count}\n"
                f"Status: SPLIT (Active Cube: {self.state.active_cube})\n"
                f"Press [SPACE] to switch control"
            )
        else:
            orientation_name = self.state.block.orientation.name
            status = (
                f"Moves: {self.move_count}\n"
                f"Orientation: {orientation_name}"
            )

        self.status_text.text = status
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

    def _get_next_level_path(self) -> Path | None:
        """Tìm đường dẫn tới level tiếp theo trong thư mục basic."""
        try:
            folder = self.level_path.parent
            levels = sorted([f for f in folder.glob("*.json")])
            current_idx = levels.index(self.level_path)
            if current_idx + 1 < len(levels):
                return levels[current_idx + 1]
        except Exception as e:
            print(f"[DEBUG] Error finding next level: {e}")
        return None

    def load_new_level(self, next_level_path: Path) -> None:
        """Dọn dẹp level cũ và tải level mới lên màn hình."""
        # 1. Hủy render của board và block cũ
        if self.board_renderer:
            for entity in self.board_renderer.tile_entities:
                destroy(entity)
            for entity in self.board_renderer.border_entities:
                destroy(entity)

        if self.block_renderer:
            self.block_renderer.destroy()

        # Hủy nút Next Level
        if self.next_level_button:
            destroy(self.next_level_button)
            self.next_level_button = None

        # 2. Tải level mới
        self.level_path = next_level_path
        self.level = load_level(self.level_path)

        # 3. Reset các biến trạng thái
        self.state = self.level.initial_state
        self.move_count = 0
        self.has_won = False
        self.is_busy = False
        self.solver_results = []
        if self.replay_controller:
            self.replay_controller = None

        # 4. Khởi tạo lại renderers
        self.board_renderer = BoardRenderer(self.level.board)
        self.block_renderer = BlockRenderer()
        self.block_renderer.sync_with_state(self.state)

        # 5. Cập nhật camera để căn giữa map mới
        self._setup_camera()

        # 6. Cập nhật lại UI text hiển thị
        self.title_text.text = self.level.name
        self._update_status_text()
