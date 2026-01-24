from core import *
import arcade
from level_selection import get_game_window_class
import pygame
from database import GameDatabase


class Game(get_game_window_class()):
    # класс, который реализует преследование камеры за игроком
    def __init__(self):
        # наследуемся от правильного класса, а не создаем экземпляр
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.camera = arcade.Camera2D()
        self.camera.zoom = ZOOM_CAM
        self.level_width = 2000
        self.level_height = 1000

        # Добавляем паузу
        self.paused = False
        self.pause_menu = None
        self.database = GameDatabase()

        # Получаем номер текущего уровня
        from config_gun import get_level_choice
        self.current_level = get_level_choice()

    def setup(self):
        pygame.init()  # кастомный курсор на Pygame
        self.custom_cursor = arcade.Sprite('assets/ui_textures/8 Cursors/3.png',
                                           1.0)  # Загружаем текстуру курсора (масштаб 1.0)
        self.custom_cursor.visible = True
        super().setup()

        # Загружаем сохранение только для текущего уровня
        if self.database.has_save_for_level(self.current_level):
            save_data = self.database.load_game(self.current_level)
            self.load_from_save(save_data)

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
        if not self.game_completed:
            save_data = self.get_save_data()
            self.database.save_game(save_data)
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

            super().on_draw()

            self.camera.position = saved_position
            self.camera.zoom = saved_zoom

            arcade.draw_polygon_filled([
                (0, 0),
                (SCREEN_WIDTH, 0),
                (SCREEN_WIDTH, SCREEN_HEIGHT),
                (0, SCREEN_HEIGHT)
            ], (0, 0, 0, 180))

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
                self.restart_game()
            return

        self.controls.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        """Обработка отпускания мыши"""
        if not self.paused:
            self.controls.on_mouse_release(x, y, button, modifiers)



def load_sprite(path, scale=1.0):
    pass