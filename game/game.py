"""Main game controller."""

from pathlib import Path

from ursina import (
    AmbientLight,
    Button,
    DirectionalLight,
    Entity,
    Text,
    Vec3,
    camera,
    color,
    invoke,
)

from ai.astar import solve_astar
from core.enums import Move, TileType
from core.level import Level
from core.level_loader import load_level
from core.state import GameState
from core.transition import apply_move, get_activated_switches, is_goal_state
from game.renderer import BlockRenderer, BoardRenderer


class GameController(Entity):
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

    def __init__(self, level_path: str | Path) -> None:
        super().__init__()

        self.level_path = Path(level_path)
        self.level_paths = sorted(self.level_path.parent.glob("*.json"))
        self.level_index = self.level_paths.index(self.level_path)
        self.level: Level = load_level(self.level_path)

        self.state: GameState = self.level.initial_state
        self.move_count = 0
        self.has_won = False
        self.is_busy = False
        self.autoplay_moves: list[Move] = []
        self.autoplay_generation = 0

        self.board_renderer = BoardRenderer(self.level.board)
        self.board_renderer.sync_with_state(self.state)

        self.block_renderer = BlockRenderer()
        self.block_renderer.sync_with_state(self.state)

        self._create_environment()
        self._create_ui()
        self._setup_camera()
        self._update_status_text()

    def _create_environment(self) -> None:
        # Nền xám xanh tối.
        camera.color = color.rgb(30, 35, 45)

        # Ánh sáng nền vừa phải.
        self.ambient_light = AmbientLight(
            color=color.rgba(90, 90, 90, 255)
        )

        # Ánh sáng chiếu từ trên xuống.
        self.directional_light = DirectionalLight(
            shadows=False
        )

        self.directional_light.color = color.rgba(
            170,
            170,
            170,
            255,
        )

        self.directional_light.look_at(
            Vec3(1, -2, 1)
        )

    def _create_ui(self) -> None:
        """
        Tạo giao diện chữ và nút Restart.
        """

        self.title_text = Text(
            text=self.level.name,
            position=(-0.87, 0.46),
            scale=1.3,
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
                "Camera: Fixed view"
            ),
            position=(-0.87, 0.31),
            scale=0.85,
        )

        self.restart_button = Button(
            text="Restart",
            position=(0.72, 0.43),
            scale=(0.18, 0.07),
            color=color.azure,
            on_click=self.restart,
        )

        self.astar_button = Button(
            text="A* Auto Play",
            position=(0.50, 0.43),
            scale=(0.22, 0.07),
            color=color.orange,
            on_click=self.start_astar_autoplay,
        )

    def _setup_camera(self) -> None:
        board_width = self.level.board.width
        board_height = self.level.board.height

        center_x = (board_width - 1) / 2
        center_z = -(board_height - 1) / 2

        board_center = Vec3(
            center_x,
            0,
            center_z,
        )

        camera.orthographic = False
        camera.fov = 55

        camera.position = Vec3(
            center_x,
            16,
            center_z - 16,
        )
        camera.look_at(board_center)

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

        next_state = apply_move(
            self.level.board,
            self.state,
            move,
        )

        if next_state is None:
            self._show_temporary_message("Illegal move!")
            return

        self._accept_state(next_state)

    def _accept_state(self, next_state: GameState) -> None:
        previous_switches = set(
            get_activated_switches(self.level.board, self.state)
        )
        self.state = next_state
        self.move_count += 1

        self.block_renderer.sync_with_state(self.state)
        self.board_renderer.sync_with_state(self.state)
        self._update_status_text()

        activated = set(get_activated_switches(self.level.board, self.state))
        newly_activated = activated - previous_switches
        if newly_activated:
            row, col = next(iter(newly_activated))
            switch_type = self.level.board.get_tile(row, col)
            label = (
                "SOFT SWITCH"
                if switch_type == TileType.SOFT_SWITCH
                else "HEAVY SWITCH"
            )
            self._show_temporary_message(f"{label} ACTIVATED!")

        if is_goal_state(self.level.board, self.state):
            self.has_won = True

            self.status_text.text = (
                f"YOU WIN!\n"
                f"Moves: {self.move_count}"
            )

            self.status_text.color = color.lime

            if self.level_index + 1 < len(self.level_paths):
                self.is_busy = True
                invoke(self._load_next_level, delay=1.5)

    def start_astar_autoplay(self) -> None:
        """Solve from the current state and replay the A* path."""

        if self.has_won or self.is_busy:
            return

        self.status_text.text = "A* searching..."
        self.status_text.color = color.yellow
        result = solve_astar(self.level.board, self.state)

        if not result.solved:
            self._show_temporary_message("A*: No solution")
            return

        self.autoplay_moves = list(result.moves)
        self.autoplay_generation += 1
        generation = self.autoplay_generation
        self.is_busy = True
        self.status_text.text = (
            f"A*: {len(result.moves)} moves, cost {result.cost}\n"
            f"Expanded: {result.expanded_nodes}"
        )
        self.status_text.color = color.azure
        invoke(self._play_next_move, generation, delay=0.35)

    def _play_next_move(self, generation: int) -> None:
        if generation != self.autoplay_generation:
            return

        if not self.autoplay_moves:
            self.is_busy = False
            if not self.has_won:
                self._update_status_text()
            return

        move = self.autoplay_moves.pop(0)
        next_state = apply_move(self.level.board, self.state, move)
        if next_state is None:
            self.is_busy = False
            self._show_temporary_message("A* replay failed")
            return

        self._accept_state(next_state)
        if not self.has_won:
            invoke(self._play_next_move, generation, delay=0.35)

    def _load_next_level(self) -> None:
        """Replace the current board with the next JSON level."""

        self.level_index += 1
        self.level_path = self.level_paths[self.level_index]
        self.level = load_level(self.level_path)
        self.state = self.level.initial_state
        self.move_count = 0
        self.has_won = False
        self.is_busy = False
        self.autoplay_moves.clear()
        self.autoplay_generation += 1

        self.board_renderer.destroy()
        self.board_renderer = BoardRenderer(self.level.board)
        self.board_renderer.sync_with_state(self.state)
        self.block_renderer.sync_with_state(self.state)
        self.title_text.text = self.level.name
        self._setup_camera()
        self._update_status_text()

    def restart(self) -> None:
        """
        Đưa game về trạng thái ban đầu.
        """

        self.state = self.level.initial_state
        self.move_count = 0
        self.has_won = False
        self.is_busy = False
        self.autoplay_moves.clear()
        self.autoplay_generation += 1

        self.block_renderer.sync_with_state(self.state)
        self.board_renderer.sync_with_state(self.state)
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
