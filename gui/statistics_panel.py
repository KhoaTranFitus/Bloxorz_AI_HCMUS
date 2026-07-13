"""Panel hiển thị bảng so sánh hiệu năng các thuật toán."""

from __future__ import annotations

from ursina import Entity, Text, Button, camera, color, Color, destroy

from ai.result import SolveResult


# Tên các thuật toán cần hiển thị (theo thứ tự hàng)
ALGORITHM_NAMES = ["BFS", "DFS", "UCS", "A*"]

# ===== Bloxorz Dark-Red Theme =====
# Background đỏ sẫm đặc trưng Bloxorz
BG_COLOR = Color(0.18, 0.04, 0.04, 0.95)        # #2E0A0A
BG_BORDER_COLOR = Color(0.55, 0.12, 0.12, 1.0)   # #8C1F1F
TITLE_COLOR = Color(1.0, 0.85, 0.3, 1.0)         # Vàng gold
HEADER_COLOR = Color(1.0, 0.95, 0.75, 1.0)       # Kem nhạt
DATA_COLOR = Color(1.0, 1.0, 1.0, 1.0)           # Trắng
NO_DATA_COLOR = Color(0.55, 0.55, 0.55, 1.0)     # Xám
FAIL_COLOR = Color(1.0, 0.4, 0.4, 1.0)           # Đỏ sáng
LINE_COLOR = Color(0.55, 0.15, 0.15, 0.8)        # Đỏ viền


class StatisticsPanel:
    """
    Overlay panel hiển thị bảng thống kê kết quả solver.

    Gồm tiêu đề, header, 4 hàng (BFS/DFS/UCS/A*) và nút Close.
    Theme đỏ sẫm đặc trưng Bloxorz.
    """

    def __init__(self) -> None:
        self._entities: list[Entity | Text | Button] = []
        self.visible = False

    def show(self, results: list[SolveResult]) -> None:
        """Hiển thị panel với dữ liệu từ danh sách SolveResult."""

        # Nếu đang hiện thì xóa cũ trước
        if self.visible:
            self.hide()

        self.visible = True

        # Map kết quả theo tên thuật toán để tra cứu
        result_map: dict[str, SolveResult] = {}
        for r in results:
            result_map[r.algorithm] = r

        # ----- Panel background (lớp ngoài — viền) -----
        border = Entity(
            parent=camera.ui,
            model="quad",
            color=BG_BORDER_COLOR,
            scale=(0.88, 0.58),
            position=(0, 0),
            z=-0.5,
        )
        self._entities.append(border)

        # ----- Panel background (lớp trong) -----
        bg = Entity(
            parent=camera.ui,
            model="quad",
            color=BG_COLOR,
            scale=(0.85, 0.55),
            position=(0, 0),
            z=-1,
        )
        self._entities.append(bg)

        # ----- Tiêu đề -----
        title = Text(
            text="SOLVER STATISTICS",
            parent=camera.ui,
            position=(-0.18, 0.23),
            scale=1.8,
            color=TITLE_COLOR,
            z=-2,
        )
        self._entities.append(title)

        # ----- Đường kẻ ngang dưới tiêu đề -----
        self._add_line(y=0.17)

        # ----- Header -----
        headers = ["Algorithm", "Time (s)", "Memory (MB)", "Expanded", "Solution"]
        col_x = [-0.34, -0.14, 0.04, 0.20, 0.34]
        header_y = 0.13

        for i, header_text in enumerate(headers):
            h = Text(
                text=header_text,
                parent=camera.ui,
                position=(col_x[i], header_y),
                scale=0.95,
                color=HEADER_COLOR,
                z=-2,
            )
            self._entities.append(h)

        # ----- Đường kẻ ngang dưới header -----
        self._add_line(y=header_y - 0.04)

        # ----- Các hàng dữ liệu -----
        row_y_start = header_y - 0.08
        row_spacing = 0.065

        for row_idx, algo_name in enumerate(ALGORITHM_NAMES):
            y = row_y_start - row_idx * row_spacing
            result = result_map.get(algo_name)

            if result is not None and result.success:
                row_data = [
                    algo_name,
                    f"{result.search_time:.4f}",
                    f"{result.memory_usage:.2f}",
                    str(result.nodes_expanded),
                    str(result.solution_length),
                ]
                row_color = DATA_COLOR
            elif result is not None and not result.success:
                row_data = [
                    algo_name,
                    f"{result.search_time:.4f}",
                    f"{result.memory_usage:.2f}",
                    str(result.nodes_expanded),
                    "No solution",
                ]
                row_color = FAIL_COLOR
            else:
                row_data = [algo_name, "—", "—", "—", "—"]
                row_color = NO_DATA_COLOR

            for col_idx, cell_text in enumerate(row_data):
                # Tên thuật toán luôn hiện trắng
                cell_color = DATA_COLOR if col_idx == 0 else row_color

                cell = Text(
                    text=cell_text,
                    parent=camera.ui,
                    position=(col_x[col_idx], y),
                    scale=0.9,
                    color=cell_color,
                    z=-2,
                )
                self._entities.append(cell)

            # Đường kẻ nhạt ngăn cách hàng
            if row_idx < len(ALGORITHM_NAMES) - 1:
                self._add_line(
                    y=y - 0.03,
                    alpha=0.3,
                )

        # ----- Nút Close -----
        close_y = row_y_start - len(ALGORITHM_NAMES) * row_spacing - 0.02

        close_btn = Button(
            text="Close",
            parent=camera.ui,
            position=(0, close_y),
            scale=(0.16, 0.05),
            color=Color(0.6, 0.15, 0.15, 1.0),
            highlight_color=Color(0.75, 0.2, 0.2, 1.0),
            z=-2,
            on_click=self.hide,
        )
        self._entities.append(close_btn)

    def _add_line(self, y: float, alpha: float = 0.8) -> None:
        """Thêm đường kẻ ngang trang trí."""

        line = Entity(
            parent=camera.ui,
            model="quad",
            color=Color(LINE_COLOR.r, LINE_COLOR.g, LINE_COLOR.b, alpha),
            scale=(0.78, 0.002),
            position=(0, y),
            z=-2,
        )
        self._entities.append(line)

    def hide(self) -> None:
        """Ẩn và xóa tất cả entity của panel."""

        for entity in self._entities:
            destroy(entity)

        self._entities.clear()
        self.visible = False
