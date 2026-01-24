import arcade
from core import *


class PauseMenu:
    """Меню паузы"""

    def __init__(self):
        self.pause_map = arcade.load_tilemap("data/pause.tmx", scaling=TILE_SCALING)
        self.background_list = self.pause_map.sprite_lists.get('Слой тайлов 1', arcade.SpriteList())

        # Смещение для выравнивания по центру
        self.offset_x = 150
        self.offset_y = 0
        # Кнопка Exit (слева)
        self.exit_hitbox = {
            'min_x': 200 + self.offset_x,
            'max_x': 350 + self.offset_x,
            'min_y': 300 + self.offset_y,
            'max_y': 480 + self.offset_y
        }

        # Кнопка Resume (по центру)
        self.resume_hitbox = {
            'min_x': 410 + self.offset_x,
            'max_x': 550 + self.offset_x,
            'min_y': 300 + self.offset_y,
            'max_y': 480 + self.offset_y
        }

        # Кнопка Restart (справа)
        self.restart_hitbox = {
            'min_x': 610 + self.offset_x,
            'max_x': 760 + self.offset_x,
            'min_y': 300 + self.offset_y,
            'max_y': 480 + self.offset_y
        }

    def draw(self):
        """Отрисовка меню паузы"""
        # Смещаем все спрайты для центрирования
        for sprite in self.background_list:
            sprite.center_x += self.offset_x
            sprite.center_y += self.offset_y
        # Фон
        if self.background_list:
            self.background_list.draw()

        for sprite in self.background_list:
            sprite.center_x -= self.offset_x
            sprite.center_y -= self.offset_y

    def check_click(self, x, y):
        """Проверка клика по кнопкам, возвращает действие"""
        if self._point_in_hitbox(x, y, self.resume_hitbox):
            return "resume"

        elif self._point_in_hitbox(x, y, self.exit_hitbox):
            return "exit"

        elif self._point_in_hitbox(x, y, self.restart_hitbox):
            return "restart"

        return None

    def _point_in_hitbox(self, x, y, hitbox):
        """Проверка попадания точки в hitbox"""
        return (hitbox['min_x'] <= x <= hitbox['max_x'] and
                hitbox['min_y'] <= y <= hitbox['max_y'])


class UI:
    def __init__(self):
        pass