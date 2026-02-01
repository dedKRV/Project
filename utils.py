from core import *
import arcade
import pygame
from database import GameDatabase
from ui import GameOverMenu, CompleteMenu
from music import Music
from particles import ParticleSystem, ParticleEmitter


class Game(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(BACKGROUND_COLOR)

        self.database = GameDatabase()
        self.current_level_number = self.database.get_current_level()

        # Атрибуты уровня (вместо отдельного окна)
        self.player = None
        self.player_spritelist = None
        self.tile_map = None
        self.walls = None
        self.ladders_list = None
        self.entry_list = None
        self.exit_list = None
        self.damage_list = None
        self.damage_2_list = None
        self.transportation_list = None
        self.jump_list = None
        self.cards_list = None
        self.spawn_entities_list = None
        self.animation_layer_sprites = {}
        self.jump_animation_sprites = {}
        self.initial_enemies_data = []
        self.initial_cards_data = []
        self.physics_engine = None
        self.enemies = None
        self.enemy_bullets = None
        self.money_list = None

        from control import Controls
        self.controls = Controls()
        self.on_ladder = False
        self.is_running = False
        self.is_jumping = False
        self.is_climbing = False

        from ui import GameHUD
        self.game_hud = GameHUD()

        self.animation_timer = 0
        self.current_animation_frame = 0
        self.jump_animation_timer = 0
        self.current_jump_animation_frame = 0
        self.animation_layers = ['animation_1', 'animation_2', 'animation_3', 'animation_4']
        self.jump_animation_layers = ['jump_animation_1', 'jump_animation_2', 'jump_animation_3', 'jump_animation_4']
        self.visible_animation_layer = None
        self.visible_jump_animation_layer = 'jump_animation_1'
        self.is_on_jump_layer = False
        self.jump_animation_active = False
        self.jump_animation_duration = 0.4
        self.jump_animation_elapsed = 0

        self.player_health = PLAYER_MAX_HEALTH
        self.damage_cooldown = 0
        self.DAMAGE_COOLDOWN_TIME = 0.5
        self.shoot_timer = 0
        self.cards_collected = 0
        self.total_cards = 0
        self.exit_visible = False
        self.exit_animation_visible = True
        self.exit_animation_list = None

        self.stars_earned = 0
        self.game_completed = False
        self.completion_timer = 0
        self.completion_message = ""
        self.play_time = 0.0
        self.money_collected = 0
        self.right_wall = None

        self.camera = arcade.Camera2D()
        self.camera.zoom = ZOOM_CAM

        self.particle_system = ParticleSystem()
        self.particle_emitter = ParticleEmitter(self.particle_system)

        self.paused = False
        self.pause_menu = None
        self.show_main_menu = True
        self.main_menu = None
        self.game_started = False
        self.custom_cursor = None

        self.show_game_over = False
        self.game_over_menu = None

        self.show_complete_menu = False
        self.complete_menu = None

        self.music = Music()

    def setup(self):
        pygame.init()
        self.custom_cursor = arcade.Sprite('assets/ui_textures/8 Cursors/3.png', 1.0)
        self.custom_cursor.visible = True

        # Загружаем уровень
        self.load_level(self.current_level_number)

        # Инициализируем меню
        from ui import PauseMenu, MainMenu, GameOverMenu, CompleteMenu
        self.pause_menu = PauseMenu()
        self.main_menu = MainMenu(self.database)
        self.game_over_menu = GameOverMenu()
        self.complete_menu = CompleteMenu()  # Новое меню

        # Загружаем настройки из config_gun
        from choice import player, gun
        self.selected_player = player
        self.selected_gun = gun

        if self.database.has_any_save():
            self.show_main_menu = True
            self.game_started = False
        else:
            self.show_main_menu = False
            self.game_started = True

        if self.show_main_menu:
            self.music.play_menu_music()

    def load_level(self, level_number):
        """Загрузить уровень"""
        self.current_level_number = level_number

        # Сбрасываем состояние игры при загрузке нового уровня
        self.game_completed = False
        self.completion_timer = 0
        self.cards_collected = 0
        self.money_collected = 0
        self.player_health = PLAYER_MAX_HEALTH
        self.play_time = 0.0
        self.show_game_over = False
        self.show_complete_menu = False  # Сбрасываем флаг complete menu

        if level_number == 1:
            from level_1 import GameWindow
            from enemy_config import LEVEL_1_CARDS
            self.total_cards = len(LEVEL_1_CARDS)
        elif level_number == 2:
            from level_2 import GameWindow2 as GameWindow
            from enemy_config import LEVEL_2_CARDS
            self.total_cards = len(LEVEL_2_CARDS)
        elif level_number == 3:
            from level_3 import GameWindow3 as GameWindow
            from enemy_config import LEVEL_3_CARDS
            self.total_cards = len(LEVEL_3_CARDS)
        elif level_number == 4:
            from level_4 import GameWindow4 as GameWindow
            from enemy_config import LEVEL_4_CARDS
            self.total_cards = len(LEVEL_4_CARDS)

        # Копируем методы из класса уровня
        self.setup_level = GameWindow.setup.__get__(self, Game)
        self.on_update_level = GameWindow.on_update.__get__(self, Game)
        self.on_draw_level = GameWindow.on_draw.__get__(self, Game)
        self.check_collisions = GameWindow.check_collisions.__get__(self, Game)
        self.check_game_completion = GameWindow.check_game_completion.__get__(self, Game)
        self.apply_damage = GameWindow.apply_damage.__get__(self, Game)
        self.restart_game = GameWindow.restart_game.__get__(self, Game)
        self.get_save_data = GameWindow.get_save_data.__get__(self, Game)
        self.load_from_save = GameWindow.load_from_save.__get__(self, Game)
        self.reset_level_state = GameWindow.reset_level_state.__get__(self, Game)
        self.update_exit_visibility = GameWindow.update_exit_visibility.__get__(self, Game)
        self.load_cards = GameWindow.load_cards.__get__(self, Game)
        self.load_enemies_from_spawn_points = GameWindow.load_enemies_from_spawn_points.__get__(self, Game)
        self.save_initial_enemies_state = GameWindow.save_initial_enemies_state.__get__(self, Game)
        self.get_killed_enemy_indices = GameWindow.get_killed_enemy_indices.__get__(self, Game)
        self.get_level_number = GameWindow.get_level_number.__get__(self, Game)
        self.get_tilemap_path = GameWindow.get_tilemap_path.__get__(self, Game)
        self.get_spawn_position = GameWindow.get_spawn_position.__get__(self, Game)
        self.get_enemy_config = GameWindow.get_enemy_config.__get__(self, Game)
        self.get_cards_config = GameWindow.get_cards_config.__get__(self, Game)

        # Вызываем setup уровня
        self.setup_level()
        # Передаем particle_emitter на уровень
        if hasattr(self, 'particle_emitter'):
            if hasattr(self, 'player'):
                self.player.particle_emitter = self.particle_emitter
            if hasattr(self, 'enemies'):
                for enemy in self.enemies:
                    enemy.particle_emitter = self.particle_emitter

    def switch_to_next_level(self):
        """Переключиться на следующий уровень"""
        next_level = self.current_level_number + 1

        if next_level <= 4:
            # Сбрасываем HUD перед загрузкой нового уровня
            self.game_hud.reset()
            # Удаляем сохранение предыдущего уровня
            self.database.delete_save_for_level(self.current_level_number)
            self.database.save_current_level(next_level)
            # Загружаем следующий уровень
            self.load_level(next_level)
            self.game_completed = False
            self.show_complete_menu = False
            print(f"Переход на уровень {next_level}!")
        else:
            print("Игра пройдена! Поздравляем!")
            self.database.delete_all_saves()
            # Можно показать финальное меню или закрыть игру
            self.show_complete_menu = True
            self.complete_menu.set_stars(self.stars_earned)

    def prepare_next_level(self):
        """Подготовить переход на следующий уровень (создать начальное сохранение)"""
        next_level = self.current_level_number + 1

        if next_level <= 4:
            # Сбрасываем HUD
            self.game_hud.reset()

        if next_level <= 4:
            # Удаляем сохранение текущего уровня
            self.database.delete_save_for_level(self.current_level_number)

            # Сохраняем информацию о том, что следующий уровень доступен
            self.database.save_current_level(next_level)

            # Создаем начальное сохранение для следующего уровня
            from choice import PLAYER_CHOICE, WEAPON_CHOICE

            # Получаем spawn позицию для следующего уровня
            if next_level == 1:
                from enemy_config import LEVEL_1_SPAWN
                spawn_x, spawn_y = LEVEL_1_SPAWN
            elif next_level == 2:
                from enemy_config import LEVEL_2_SPAWN
                spawn_x, spawn_y = LEVEL_2_SPAWN
            elif next_level == 3:
                from enemy_config import LEVEL_3_SPAWN
                spawn_x, spawn_y = LEVEL_3_SPAWN
            elif next_level == 4:
                from enemy_config import LEVEL_4_SPAWN
                spawn_x, spawn_y = LEVEL_4_SPAWN
            else:
                spawn_x, spawn_y = 3, 17

            # Создаем минимальное сохранение для следующего уровня
            initial_save = {
                'level_number': next_level,
                'character_skin': PLAYER_CHOICE,
                'weapon': int(WEAPON_CHOICE),
                'player_x': TILE_SIZE * spawn_x,
                'player_y': TILE_SIZE * spawn_y,
                'player_health': PLAYER_MAX_HEALTH,
                'enemies_killed': 0,
                'cards_collected': 0,
                'money_collected': 0,
                'total_cards': 0,
                'play_time': 0.0,
                'killed_enemy_indices': []
            }

            self.database.save_game(initial_save)

            print(f"Подготовлен переход на уровень {next_level}")
        else:
            self.database.delete_all_saves()
            print("Игра полностью пройдена!")

    def on_update(self, delta_time):
        if self.show_main_menu:
            if self.music.current_music != "menu":
                self.music.play_menu_music()
            if self.main_menu:
                self.main_menu.update(delta_time)
            mouse_x = self._mouse_x
            mouse_y = self._mouse_y
            self.custom_cursor.center_x = mouse_x
            self.custom_cursor.center_y = mouse_y
            return

        if not self.paused and not self.show_game_over and not self.show_complete_menu:
            if self.music.current_music != "battle":
                self.music.play_battle_music()

        self.game_hud.update(delta_time)
        self.game_hud.set_health(self.player_health)

        # Если показываем меню завершения - обновляем только курсор
        if self.show_complete_menu:
            mouse_x = self._mouse_x
            mouse_y = self._mouse_y
            self.custom_cursor.center_x = mouse_x
            self.custom_cursor.center_y = mouse_y
            return

        if self.paused or self.show_game_over:
            mouse_x = self._mouse_x
            mouse_y = self._mouse_y
            self.custom_cursor.center_x = mouse_x
            self.custom_cursor.center_y = mouse_y
            return

        if self.controls.get_pause():
            self.controls.reset_pause()
            self.paused = not self.paused
            return

        # Вызываем update уровня
        self.on_update_level(delta_time)

        # Обновляем частицы
        self.particle_system.update(delta_time)
        if not self.show_main_menu and not self.paused and not self.show_game_over and not self.show_complete_menu:
            if self.player:
                if hasattr(self, 'physics_engine') and self.physics_engine:
                    is_on_ground = self.physics_engine.can_jump()
                    self.particle_emitter.update_run(
                        delta_time,
                        self.is_running and is_on_ground,  # Только если бежит и на земле
                        self.player.center_x,
                        self.player.center_y,
                        self.player.facing_direction
                    )

        # Проверяем завершение уровня
        if self.game_completed:
            # Уменьшаем таймер завершения
            if self.completion_timer > 0:
                self.completion_timer -= delta_time
            else:
                # Показываем меню завершения вместо автоматического перехода
                self.show_complete_menu = True
                self.complete_menu.set_stars(self.stars_earned)
            return

        if self.player:
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
        if not self.game_completed and self.game_started and not self.show_game_over:
            save_data = self.get_save_data()
            self.database.save_game(save_data)
        self.music.stop_all()
        pygame.quit()
        super().on_close()

    def on_draw(self):
        self.clear()

        if self.show_main_menu and self.main_menu:
            self.main_menu.draw()
            self.set_mouse_visible(False)
            arcade.draw_sprite(self.custom_cursor)
            return

        # Если показываем меню завершения уровня
        if self.show_complete_menu and self.complete_menu:
            # Рисуем игру на фоне
            saved_position = self.camera.position
            saved_zoom = self.camera.zoom

            self.camera.position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            self.camera.zoom = 1.0
            self.camera.use()

            self.on_draw_level()

            self.camera.position = saved_position
            self.camera.zoom = saved_zoom

            # Затемнение
            arcade.draw_polygon_filled([
                (0, 0),
                (SCREEN_WIDTH, 0),
                (SCREEN_WIDTH, SCREEN_HEIGHT),
                (0, SCREEN_HEIGHT)
            ], (0, 0, 0, 180))

            # Меню завершения
            self.complete_menu.draw()

            self.set_mouse_visible(False)
            arcade.draw_sprite(self.custom_cursor)
            return

        if self.show_game_over and self.game_over_menu:
            # Рисуем игру на фоне
            saved_position = self.camera.position
            saved_zoom = self.camera.zoom

            self.camera.position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            self.camera.zoom = 1.0
            self.camera.use()

            self.on_draw_level()

            self.camera.position = saved_position
            self.camera.zoom = saved_zoom

            # Затемнение
            arcade.draw_polygon_filled([
                (0, 0),
                (SCREEN_WIDTH, 0),
                (SCREEN_WIDTH, SCREEN_HEIGHT),
                (0, SCREEN_HEIGHT)
            ], (0, 0, 0, 180))

            # Меню Game Over
            self.game_over_menu.draw()

            self.set_mouse_visible(False)
            arcade.draw_sprite(self.custom_cursor)
            return

        if self.paused:
            saved_position = self.camera.position
            saved_zoom = self.camera.zoom

            self.camera.position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            self.camera.zoom = 1.0
            self.camera.use()

            self.on_draw_level()
            self.particle_system.draw()

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

            self.set_mouse_visible(False)
            arcade.draw_sprite(self.custom_cursor)
        else:
            self.camera.use()
            self.on_draw_level()
            self.particle_system.draw()
            # Рисуем HUD поверх игры
            saved_position = self.camera.position
            saved_zoom = self.camera.zoom
            self.camera.position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            self.camera.zoom = 1.0
            self.camera.use()
            # Рисуем полный HUD
            self.game_hud.draw()
            self.camera.position = saved_position
            self.camera.zoom = saved_zoom
            self.camera.use()
            self.set_mouse_visible(False)
            arcade.draw_sprite(self.custom_cursor)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.show_main_menu and self.main_menu:
            action = self.main_menu.check_click(x, y)

            if action == "resume":
                current_level = self.database.get_current_level()

                if self.current_level_number != current_level:
                    self.load_level(current_level)

                save_data = self.database.load_game(current_level)
                if save_data:
                    self.load_from_save(save_data)

                self.show_main_menu = False
                self.game_started = True
                self.music.play_battle_music()

            elif action == "restart":
                self.database.delete_all_saves()
                self.load_level(1)
                self.restart_game()
                self.show_main_menu = False
                self.game_started = True
                self.music.play_battle_music()

            elif action == "exit":
                print("Выход из игры")
                self.close()
            return

        # Обработка кликов в меню завершения уровня
        if self.show_complete_menu and self.complete_menu:
            action = self.complete_menu.check_click(x, y)

            if action == "exit":
                # Выход в главное меню - подготавливаем следующий уровень
                self.prepare_next_level()
                self.show_complete_menu = False
                self.show_main_menu = True
                self.game_started = False
            elif action == "continue":
                # Продолжить - переход на следующий уровень
                self.show_complete_menu = False
                self.switch_to_next_level()
            elif action == "restart":
                # Перезапуск текущего уровня
                self.show_complete_menu = False
                self.restart_game()
            return

        if self.show_game_over and self.game_over_menu:
            action = self.game_over_menu.check_click(x, y)

            if action == "exit":
                # Выход в главное меню - сохраняем текущий прогресс уровня
                save_data = self.get_save_data()
                self.database.save_game(save_data)

                self.show_game_over = False
                self.show_main_menu = True
                self.game_started = False
                self.music.play_menu_music()
            elif action == "restart":
                self.show_game_over = False
                self.music.play_menu_music()
                self.restart_game()
            return

        if self.paused and self.pause_menu:
            action = self.pause_menu.check_click(x, y)

            if action == "resume":
                self.paused = False
                self.music.play_battle_music()
            elif action == "exit":
                save_data = self.get_save_data()
                self.database.save_game(save_data)
                self.paused = False
                self.show_main_menu = True
                self.game_started = False
                self.music.play_menu_music()
            elif action == "restart":
                self.database.delete_save_for_level(self.current_level_number)
                self.restart_game()
                self.paused = False
            return

        self.controls.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        if not self.paused and not self.show_main_menu and not self.show_complete_menu:
            self.controls.on_mouse_release(x, y, button, modifiers)

    def on_key_press(self, key, modifiers):
        if not self.paused and not self.show_main_menu and not self.show_complete_menu:
            if key == arcade.key.KEY_1:
                self.player.toggle_weapon()
            else:
                self.controls.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        if not self.paused and not self.show_main_menu and not self.show_complete_menu:
            self.controls.on_key_release(key, modifiers)


def load_sprite(path, scale=1.0):
    pass