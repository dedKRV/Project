from core import *
import arcade
from level_1 import GameWindow
import pygame


class Game(GameWindow):
    # класс, который реализует преследование камеры за игроком
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Platformer")
        self.camera = arcade.Camera2D()
        self.camera.zoom = ZOOM_CAM  # В core.py
        self.level_width = 2000
        self.level_height = 1000

        # Добавляем паузу
        self.paused = False
        self.pause_menu = None

    def setup(self):
        pygame.init()  # кастомный курсор на Pygame
        self.custom_cursor = arcade.Sprite('assets/ui_textures/8 Cursors/3.png',
                                           1.0)  # Загружаем текстуру курсора (масштаб 1.0)
        self.custom_cursor.visible = True
        super().setup()

        # Инициализируем меню паузы
        from ui import PauseMenu
        self.pause_menu = PauseMenu()

    def on_update(self, delta_time):
        """Обновление игры"""
        # Проверка паузы
        if self.controls.get_pause():
            self.controls.reset_pause()
            self.paused = not self.paused  # Переключаем паузу
            return

        # Если игра на паузе - не обновляем
        if self.paused:
            # Обновляем только позицию курсора
            mouse_x = self._mouse_x
            mouse_y = self._mouse_y
            self.custom_cursor.center_x = mouse_x
            self.custom_cursor.center_y = mouse_y
            return

        super().on_update(delta_time)
        if hasattr(self, 'game_completed') and self.game_completed:
            return
        mouse_x = self._mouse_x
        mouse_y = self._mouse_y
        mouse_x, mouse_y = self.camera.unproject((mouse_x, mouse_y))[:2]
        self.custom_cursor.center_x = mouse_x
        self.custom_cursor.center_y = mouse_y
        target_x = self.player.center_x
        target_y = self.player.center_y
        lerp_speed = 0.1
        self.camera.position = (
            self.camera.position[0] + (target_x - self.camera.position[0]) * lerp_speed,
            self.camera.position[1] + (target_y - self.camera.position[1]) * lerp_speed
        )

        self.camera.position = (
            max(self.camera.viewport_width / self.camera.zoom / 2,
                min(self.camera.position[0], LEVEL_WIDTH - self.camera.viewport_width / self.camera.zoom / 2)),
            max(self.camera.viewport_height / self.camera.zoom / 2,
                min(self.camera.position[1], LEVEL_HEIGHT - self.camera.viewport_height / self.camera.zoom / 2)))

    def on_close(self):
        """Обработка закрытия окна"""
        super().on_close()
        pygame.quit()

    def on_draw(self):
        if self.paused:
            # При паузе отключаем камеру и рисуем всё без зума
            self.clear()

            # Сохраняем текущие параметры камеры
            saved_position = self.camera.position
            saved_zoom = self.camera.zoom

            # Сбрасываем камеру на центр экрана
            self.camera.position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            self.camera.zoom = 1.0
            self.camera.use()

            # Рисуем игру
            super().on_draw()

            # Восстанавливаем камеру
            self.camera.position = saved_position
            self.camera.zoom = saved_zoom

            # Рисуем затемнение на весь экран
            arcade.draw_polygon_filled([
                (0, 0),
                (SCREEN_WIDTH, 0),
                (SCREEN_WIDTH, SCREEN_HEIGHT),
                (0, SCREEN_HEIGHT)
            ], (0, 0, 0, 180))

            # Рисуем меню паузы
            if self.pause_menu:
                self.pause_menu.draw()

            # Курсор поверх всего
            self.set_mouse_visible(False)
            arcade.draw_sprite(self.custom_cursor)
        else:
            # Обычный режим с камерой
            self.camera.use()
            super().on_draw()
            self.set_mouse_visible(False)
            arcade.draw_sprite(self.custom_cursor)

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка нажатия мыши"""
        # Если пауза активна, обрабатываем клики по меню
        if self.paused and self.pause_menu:
            action = self.pause_menu.check_click(x, y)

            if action == "resume":
                self.paused = False
            elif action == "exit":
                arcade.close_window()
            elif action == "restart":
                self.player_health = PLAYER_MAX_HEALTH
                self.player.center_x = TILE_SIZE * 3
                self.player.center_y = TILE_SIZE * 17
                self.reset_level_state()
                self.paused = False
            return

        # Обычная обработка мыши
        self.controls.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        """Обработка отпускания мыши"""
        if not self.paused:
            self.controls.on_mouse_release(x, y, button, modifiers)


def load_sprite(path, scale=1.0):
    pass