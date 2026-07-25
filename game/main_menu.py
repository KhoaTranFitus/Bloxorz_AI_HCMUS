"""Main menu shown when the application starts."""

from collections.abc import Callable

from ursina import Button, Entity, Text, camera, color, destroy


class MainMenuScreen(Entity):
    """Display the game title and open level selection on Play."""

    def __init__(self, on_play: Callable[[], None]) -> None:
        super().__init__()

        self.on_play = on_play
        self.ui_root = Entity(parent=camera.ui)

        self.background = Entity(
            parent=self.ui_root,
            model="quad",
            texture="assets/menuSelect.png",
            color=color.white,
            scale=(2, 1),
            z=1,
        )
        self.title = Text(
            parent=self.ui_root,
            text="BLOXORZ",
            origin=(0, 0),
            y=0.18,
            scale=3.5,
            color=color.rgb32(255, 255, 255),
            z=-1,
        )
        self.play_button = Button(
            parent=self.ui_root,
            text="PLAY",
            y=-0.12,
            scale=(0.28, 0.10),
            color=color.rgb32(55, 145, 95),
            highlight_color=color.rgb32(75, 175, 115),
            pressed_color=color.rgb32(38, 83, 62),
            z=-1,
        )
        self.play_button.on_click = self.on_play

    def cleanup(self) -> None:
        destroy(self.ui_root)
        destroy(self)
