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
    LEVEL_GROUPS = (
        (
            "EASY", (1, 2, 3),
            color.rgb32(174, 116, 103),
            color.rgb32(66, 38, 43),
        ),
        (
            "MEDIUM", (4, 5, 6),
            color.rgb32(196, 151, 91),
            color.rgb32(72, 45, 42),
        ),
        (
            "HARD", (7, 8, 9),
            color.rgb32(174, 73, 80),
            color.rgb32(68, 30, 38),
        ),
        (
            "SUPER HARD", (10, 11, 12),
            color.rgb32(142, 91, 132),
            color.rgb32(57, 33, 55),
        ),
    )

    def __init__(
        self,
        on_level_selected: Callable[[int], None],
        on_back: Callable[[], None],
    ) -> None:
        super().__init__()

        self.on_level_selected = on_level_selected
        self.on_back = on_back
        self.buttons: list[Button] = []

        self.ui_root = Entity(
            parent=camera.ui,
        )

        self._create_background()
        self._create_title()
        self._create_level_buttons()
        self._create_back_button()

    def _create_background(self) -> None:
        self.background = Entity(
            parent=self.ui_root,
            model="quad",
            texture="assets/menuSelect.png",
            color=color.white,
            scale=(2, 1),
            z=1,
        )

    def _create_title(self) -> None:
        self.title = Text(
            parent=self.ui_root,
            text="SELECT LEVEL",
            origin=(0, 0),
            y=0.43,
            scale=2,
            color=color.rgb32(255, 255, 255),
            z=-1,
        )

    def _create_level_buttons(self) -> None:
        panel_centers = (
            Vec2(-0.34, 0.16),
            Vec2(0.34, 0.16),
            Vec2(-0.34, -0.20),
            Vec2(0.34, -0.20),
        )

        for (label, levels, button_color, panel_color), center in zip(
            self.LEVEL_GROUPS,
            panel_centers,
        ):
            Entity(
                parent=self.ui_root,
                model="quad",
                position=center,
                scale=(0.635, 0.305),
                color=button_color,
                z=0.1,
            )
            Entity(
                parent=self.ui_root,
                model="quad",
                position=center,
                scale=(0.62, 0.29),
                color=panel_color,
                z=0,
            )
            Text(
                parent=self.ui_root,
                text=label,
                origin=(0, 0),
                position=Vec2(center.x, center.y + 0.09),
                scale=1.15,
                color=button_color,
                z=-1,
            )

            for index, level_number in enumerate(levels):
                button = Button(
                    parent=self.ui_root,
                    text=f"Level {level_number}",
                    position=Vec2(
                        center.x + (index - 1) * 0.19,
                        center.y - 0.045,
                    ),
                    scale=(0.16, 0.085),
                    color=button_color,
                    highlight_color=color.rgb32(110, 150, 220),
                    pressed_color=color.rgb32(65, 95, 150),
                    z=-1,
                )
                button.on_click = (
                    lambda selected_level=level_number:
                    self.on_level_selected(selected_level)
                )
                self.buttons.append(button)

    def _create_back_button(self) -> None:
        self.back_button = Button(
            parent=self.ui_root,
            text="BACK",
            position=Vec2(-0.78, 0.43),
            scale=(0.16, 0.07),
            color=color.rgb32(100, 53, 45),
            highlight_color=color.rgb32(185, 80, 55),
            pressed_color=color.rgb32(75, 38, 34),
            z=-1,
        )
        self.back_button.on_click = self.on_back
        self.buttons.append(self.back_button)

    def cleanup(self) -> None:
        destroy(self.ui_root)
        destroy(self)
