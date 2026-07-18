"""Level selection screen."""

from collections.abc import Callable

from ursina import (
    Button,
    Entity,
    Text,
    Vec2,
    camera,
    color,
    destroy,
)


class LevelSelectScreen(Entity):
    def __init__(
        self,
        on_level_selected: Callable[[int], None],
    ) -> None:
        super().__init__()

        self.on_level_selected = on_level_selected
        self.buttons: list[Button] = []

        self.ui_root = Entity(
            parent=camera.ui,
        )

        self._create_background()
        self._create_title()
        self._create_level_buttons()

    def _create_background(self) -> None:
        self.background = Entity(
            parent=self.ui_root,
            model="quad",
            color=color.rgb32(35, 40, 50),
            scale=(2, 1),
            z=1,
        )

    def _create_title(self) -> None:
        self.title = Text(
            parent=self.ui_root,
            text="SELECT LEVEL",
            origin=(0, 0),
            y=0.35,
            scale=2,
            color=color.white,
            z=-1,
        )

    def _create_level_buttons(self) -> None:
        start_x = -0.48
        start_y = 0.12

        horizontal_gap = 0.24
        vertical_gap = 0.24

        for level_number in range(1, 11):
            row = (level_number - 1) // 5
            column = (level_number - 1) % 5

            button = Button(
                parent=self.ui_root,
                text=f"Level {level_number}",
                position=Vec2(
                    start_x + column * horizontal_gap,
                    start_y - row * vertical_gap,
                ),
                scale=(0.2, 0.12),
                color=color.rgb32(85, 120, 180),
                highlight_color=color.rgb32(110, 150, 220),
                pressed_color=color.rgb32(65, 95, 150),
                z=-1,
            )

            button.on_click = (
                lambda selected_level=level_number:
                self.on_level_selected(selected_level)
            )

            self.buttons.append(button)

    def cleanup(self) -> None:
        destroy(self.ui_root)
        destroy(self)