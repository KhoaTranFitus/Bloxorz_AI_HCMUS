"""Application entry point."""

from ursina import Ursina

from game.app_controller import AppController


app = Ursina()

app_controller = AppController()

app.run()