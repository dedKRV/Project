from core import *
import arcade
from level_1 import GameWindow

class Game(GameWindow):
    # класс, который реализует преследование камеры за игроком
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Platformer")
        self.camera = arcade.Camera2D()
        self.camera.zoom = ZOOM_CAM # В core.py
        self.level_width = 2000
        self.level_height = 1000

    def setup(self):
        super().setup()

    def on_update(self, delta_time):
        super().on_update(delta_time)
        target_x = self.player.center_x
        target_y = self.player.center_y
        lerp_speed = 0.1
        self.camera.position = (
            self.camera.position[0] + (target_x - self.camera.position[0]) * lerp_speed,
            self.camera.position[1] + (target_y - self.camera.position[1]) * lerp_speed
        )

        self.camera.position = (
            max(self.camera.viewport_width / self.camera.zoom / 2,
                min(self.camera.position[0], self.level_width - self.camera.viewport_width / self.camera.zoom / 2)),
            max(self.camera.viewport_height / self.camera.zoom / 2,
                min(self.camera.position[1], self.level_height - self.camera.viewport_height / self.camera.zoom / 2))
        )

    def on_draw(self):
        self.camera.use()
        super().on_draw()

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка нажатия мыши"""
        self.controls.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        """Обработка отпускания мыши"""
        self.controls.on_mouse_release(x, y, button, modifiers)

def load_sprite(path, scale=1.0):
    pass