"""Entry point for the Bloxorz project."""

from pathlib import Path

from ursina import Ursina, window

from game.game import GameController


def main() -> None:
    app = Ursina()

    window.title = "Bloxorz Solver"
    window.borderless = False
    window.fullscreen = False
    window.exit_button.visible = False
    window.fps_counter.enabled = True

    project_root = Path(__file__).resolve().parent
    level_path = (
        project_root
        / "levels"
        / "basic"
        / "level_01.json"
    )

    GameController(level_path)

    app.run()


if __name__ == "__main__":
    main()