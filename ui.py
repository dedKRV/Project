import arcade
import random
from core import *
import choice
from particles import ParticleSystem


class MainMenu:
    """Главное меню игры"""

    def __init__(self, database):
        self.database = database
        self.menu_map = arcade.load_tilemap("data/menu.tmx", scaling=TILE_SCALING)

        # Список всех доступных слоев
        self.background_layer_names = ['background_1', 'background_2', 'background_3']
        self.background_image_names = ['background_image_1', 'background_image_2']
        self.part_layer_names = ['part_1', 'part_2', 'part_3', 'part_4']

        # Текущие отображаемые слои
        self.current_background_index = random.randint(0, len(self.background_layer_names) - 1)
        self.current_image_index = 0
        self.current_part_index = 0
        self.image_switch_timer = 0
        self.image_switch_duration = 1.0
        self.part_switch_timer = 0
        self.part_switch_duration = 0.05
        self.part_pause_timer = 0
        self.part_pause_duration = 1.0

        self.tile_size = TILE_SIZE * TILE_SCALING

        # Анимация игроков
        self.player_anim_timer = 0
        self.player_anim_duration = 0.05
        self.current_player_anim_frame = 0
        self.player_anim_frames = [f'players_anim_{i}' for i in range(1, 13)]

        # Анимация оружия
        self.gun_anim_timer = 0
        self.gun_anim_duration = 0.1
        self.current_gun_frame = 0
        self.gun_anim_frames = [1, 2]

        # Флаги для отображения дополнительных слоев
        self.show_weapon_selection = False
        self.show_player_selection = False
        self.show_frames_2 = False

        # Таймеры для анимации нажатия кнопок
        self.restart_press_timer = 0
        self.resume_press_timer = 0
        self.gun_button_press_timer = 0
        self.player_button_press_timer = 0
        self.button_press_duration = 0.1

        # Координаты кнопок выбора персонажа (в тайлах)
        self.player_button_positions = {
            1: {'x': 9 * self.tile_size,
                'y': 13 * self.tile_size,
                'width': 1 * self.tile_size,
                'height': 1 * self.tile_size},
            2: {'x': 9 * self.tile_size,
                'y': 10 * self.tile_size,
                'width': 1 * self.tile_size,
                'height': 1 * self.tile_size},
            3: {'x': 9 * self.tile_size,
                'y': 7 * self.tile_size,
                'width': 1 * self.tile_size,
                'height': 1 * self.tile_size}
        }

        # Координаты кнопок выбора оружия (в тайлах)
        self.gun_button_positions = {
            1: {'x': 9 * self.tile_size,
                'y': 13 * self.tile_size,
                'width': 1 * self.tile_size,
                'height': 1 * self.tile_size},
            2: {'x': 9 * self.tile_size,
                'y': 10 * self.tile_size,
                'width': 1 * self.tile_size,
                'height': 1 * self.tile_size},
            3: {'x': 9 * self.tile_size,
                'y': 7 * self.tile_size,
                'width': 1 * self.tile_size,
                'height': 1 * self.tile_size}
        }

        self.particle_system = ParticleSystem()
        self.shot_particle_timer = 0
        self.shot_particle_interval = 0.5  # Интервал между выстрелами
        self.gun_particle_positions = {
            1: {'x': 5 * self.tile_size, 'y': 13.7 * self.tile_size},
            2: {'x': 5 * self.tile_size, 'y': 10.7 * self.tile_size},
            3: {'x': 5 * self.tile_size, 'y': 7.7 * self.tile_size}
        }

        self.exit_button_x = 32 * self.tile_size + 3 * self.tile_size / 2
        self.exit_button_y = 2 * self.tile_size + 1.5 * self.tile_size / 2
        self.exit_button_width = 6 * self.tile_size
        self.exit_button_height = 3 * self.tile_size
        self.exit_press_timer = 0

        # Загружаем все спрайт-листы
        self.background_layers = {}
        self.background_image_layers = {}
        self.frames_layers = {}
        self.frames_2_layers = {}
        self.part_layers = {}
        self.button_layers = {}
        self.button_active_layers = {}
        self.gun_button_layers = {}
        self.gun_button_active_layers = {}
        self.player_button_layers = {}
        self.player_button_active_layers = {}
        self.players_anim_layers = {}
        self.gun_players_layers = {}

        self._load_all_layers()

        self.ui_background_list = self.menu_map.sprite_lists.get('Слой тайлов 1', arcade.SpriteList())

        self.font_name = "assets/ui_textures/10 Font/CyberpunkCraftpixPixel.otf"

        self.tile_size = TILE_SIZE * TILE_SCALING

        self.gun_button_x = 3 * self.tile_size + self.tile_size / 2
        self.gun_button_y = 3 * self.tile_size + self.tile_size / 2
        self.gun_button_width = 3 * self.tile_size
        self.gun_button_height = 3 * self.tile_size

        self.player_button_x = 8 * self.tile_size + self.tile_size / 2
        self.player_button_y = 3 * self.tile_size + self.tile_size / 2
        self.player_button_width = 3 * self.tile_size
        self.player_button_height = 3 * self.tile_size

        self.button_width = 250
        self.button_height = 90
        self.title_y = 520
        self.resume_button_y = 385
        self.restart_button_y = 290

        self.current_player_choice = choice.player
        self.current_gun_choice = choice.gun

    def _load_all_layers(self):
        """Загрузка всех слоев из тайлмапа"""
        # Фоновые слои
        for layer_name in self.background_layer_names:
            self.background_layers[layer_name] = self.menu_map.sprite_lists.get(layer_name, arcade.SpriteList())

        for layer_name in self.background_image_names:
            self.background_image_layers[layer_name] = self.menu_map.sprite_lists.get(layer_name, arcade.SpriteList())

        # frames слои - задние
        self.frames_layers['frames_2'] = self.menu_map.sprite_lists.get('frames_2', arcade.SpriteList())
        self.frames_layers['frames'] = self.menu_map.sprite_lists.get('frames', arcade.SpriteList())

        # Дополнительные frames_2 слои
        self.frames_2_layers['frames_2_1'] = self.menu_map.sprite_lists.get('frames_2_1', arcade.SpriteList())
        self.frames_2_layers['frames_2_2'] = self.menu_map.sprite_lists.get('frames_2_2', arcade.SpriteList())

        # Частицы (искры) - ПЕРЕД frames
        for layer_name in self.part_layer_names:
            self.part_layers[layer_name] = self.menu_map.sprite_lists.get(layer_name, arcade.SpriteList())

        # Основные кнопки
        self.button_layers['restart'] = self.menu_map.sprite_lists.get('restart', arcade.SpriteList())
        self.button_layers['resume'] = self.menu_map.sprite_lists.get('resume', arcade.SpriteList())
        self.button_layers['gun_button'] = self.menu_map.sprite_lists.get('gun_button', arcade.SpriteList())
        self.button_layers['player_button'] = self.menu_map.sprite_lists.get('player_button', arcade.SpriteList())
        self.button_layers['exit'] = self.menu_map.sprite_lists.get('exit', arcade.SpriteList())

        # Активные состояния кнопок
        self.button_active_layers['restart'] = self.menu_map.sprite_lists.get('restart_active', arcade.SpriteList())
        self.button_active_layers['resume'] = self.menu_map.sprite_lists.get('resume_active', arcade.SpriteList())
        self.button_active_layers['gun_button'] = self.menu_map.sprite_lists.get('gun_button_active',
                                                                                 arcade.SpriteList())
        self.button_active_layers['player_button'] = self.menu_map.sprite_lists.get('player_button_active',
                                                                                    arcade.SpriteList())
        self.button_active_layers['exit'] = self.menu_map.sprite_lists.get('exit_active', arcade.SpriteList())

        # Кнопки оружия
        for i in range(1, 4):
            self.gun_button_layers[f'gun_button_{i}'] = self.menu_map.sprite_lists.get(f'gun_button_{i}',
                                                                                       arcade.SpriteList())
            self.gun_button_active_layers[f'gun_button_active_{i}'] = self.menu_map.sprite_lists.get(
                f'gun_button_active_{i}', arcade.SpriteList())

        # Кнопки персонажей
        for i in range(1, 4):
            self.player_button_layers[f'player_button_{i}'] = self.menu_map.sprite_lists.get(f'player_button_{i}',
                                                                                             arcade.SpriteList())
            self.player_button_active_layers[f'player_button_active_{i}'] = self.menu_map.sprite_lists.get(
                f'player_button_active_{i}', arcade.SpriteList())

        # Анимации персонажей
        for i in range(1, 13):
            self.players_anim_layers[f'players_anim_{i}'] = self.menu_map.sprite_lists.get(f'players_anim_{i}',
                                                                                           arcade.SpriteList())

        # Оружие персонажей
        self.gun_players_layers['gun_biker_1'] = self.menu_map.sprite_lists.get('gun_biker_1', arcade.SpriteList())
        self.gun_players_layers['gun_biker_2'] = self.menu_map.sprite_lists.get('gun_biker_2', arcade.SpriteList())
        self.gun_players_layers['gun_punk_1'] = self.menu_map.sprite_lists.get('gun_punk_1', arcade.SpriteList())
        self.gun_players_layers['gun_punk_2'] = self.menu_map.sprite_lists.get('gun_punk_2', arcade.SpriteList())
        self.gun_players_layers['gun_cyborg_1'] = self.menu_map.sprite_lists.get('gun_cyborg_1', arcade.SpriteList())
        self.gun_players_layers['gun_cyborg_2'] = self.menu_map.sprite_lists.get('gun_cyborg_2', arcade.SpriteList())

    def update(self, delta_time):
        """Обновление таймеров анимации"""
        # Анимация переключения background_image слоев
        self.image_switch_timer += delta_time
        if self.image_switch_timer >= self.image_switch_duration:
            self.image_switch_timer = 0
            self.current_image_index = (self.current_image_index + 1) % len(self.background_image_names)

        # Анимация частиц (искр)
        if self.part_pause_timer > 0:
            self.part_pause_timer -= delta_time
            if self.part_pause_timer <= 0:
                self.current_part_index = 0
                self.part_switch_timer = 0
        else:
            self.part_switch_timer += delta_time
            if self.part_switch_timer >= self.part_switch_duration:
                self.part_switch_timer = 0
                self.current_part_index += 1
                if self.current_part_index >= len(self.part_layer_names):
                    self.current_part_index = 0
                    self.part_pause_timer = self.part_pause_duration

        # Анимация игроков (только при открытом меню выбора персонажа)
        if self.show_player_selection:
            self.player_anim_timer += delta_time
            if self.player_anim_timer >= self.player_anim_duration:
                self.player_anim_timer = 0
                self.current_player_anim_frame = (self.current_player_anim_frame + 1) % len(self.player_anim_frames)

        # Анимация оружия (только при открытом меню выбора оружия)
        if self.show_weapon_selection:
            self.gun_anim_timer += delta_time

            if self.gun_anim_timer >= self.gun_anim_duration:
                self.gun_anim_timer = 0
                self.current_gun_frame = (self.current_gun_frame + 1) % len(self.gun_anim_frames)

                if self.current_gun_frame == 1:
                    for weapon_type in [1, 2, 3]:
                        if weapon_type in self.gun_particle_positions:
                            pos = self.gun_particle_positions[weapon_type]
                            self.particle_system.create_particles(
                                pos['x'],
                                pos['y'],
                                f'shot_spark_{weapon_type}',
                                0,
                                30
                            )
            # Обновляем частицы
        self.particle_system.update(delta_time)

        # Обновление таймеров нажатия кнопок
        if self.restart_press_timer > 0:
            self.restart_press_timer -= delta_time

        if self.resume_press_timer > 0:
            self.resume_press_timer -= delta_time

        if self.gun_button_press_timer > 0:
            self.gun_button_press_timer -= delta_time

        if self.player_button_press_timer > 0:
            self.player_button_press_timer -= delta_time

        if self.exit_press_timer > 0:
            self.exit_press_timer -= delta_time

    def draw(self):
        """Отрисовка главного меню"""
        current_bg_name = self.background_layer_names[self.current_background_index]
        if current_bg_name in self.background_layers:
            self.background_layers[current_bg_name].draw()

        current_image_name = self.background_image_names[self.current_image_index]
        if current_image_name in self.background_image_layers:
            self.background_image_layers[current_image_name].draw()

        if 'frames_2' in self.frames_layers:
            self.frames_layers['frames_2'].draw()
        if 'frames' in self.frames_layers:
            self.frames_layers['frames'].draw()

        # Анимация искр
        current_part_name = self.part_layer_names[self.current_part_index]
        if current_part_name in self.part_layers and self.part_pause_timer <= 0:
            self.part_layers[current_part_name].draw()

        if self.ui_background_list:
            self.ui_background_list.draw()

        self._draw_main_buttons()

        if self.show_frames_2:
            self.frames_2_layers['frames_2_1'].draw()
            self.frames_2_layers['frames_2_2'].draw()

        if self.show_weapon_selection:
            self._draw_weapon_selection()

        if self.show_player_selection:
            self._draw_player_selection()

        self._draw_text_elements()

        self.particle_system.draw()

    def _draw_main_buttons(self):
        """Отрисовка основных кнопок"""
        # Кнопка RESTART
        if self.restart_press_timer > 0 and 'restart' in self.button_active_layers:
            self.button_active_layers['restart'].draw()
        elif 'restart' in self.button_layers:
            self.button_layers['restart'].draw()

        # Кнопка RESUME
        if self.resume_press_timer > 0 and 'resume' in self.button_active_layers:
            self.button_active_layers['resume'].draw()
        elif 'resume' in self.button_layers:
            self.button_layers['resume'].draw()

        # Кнопка выбора оружия
        if self.gun_button_press_timer > 0 and 'gun_button' in self.button_active_layers:
            self.button_active_layers['gun_button'].draw()
        elif 'gun_button' in self.button_layers:
            self.button_layers['gun_button'].draw()

        # Кнопка выбора персонажа
        if self.player_button_press_timer > 0 and 'player_button' in self.button_active_layers:
            self.button_active_layers['player_button'].draw()
        elif 'player_button' in self.button_layers:
            self.button_layers['player_button'].draw()

        # Кнопка EXIT
        if self.exit_press_timer > 0 and 'exit' in self.button_active_layers:
            self.button_active_layers['exit'].draw()
        elif 'exit' in self.button_layers:
            self.button_layers['exit'].draw()

    def _draw_weapon_selection(self):
        """Отрисовка панели выбора оружия"""
        for i in range(1, 4):
            button_name = f'gun_button_{i}'
            active_button_name = f'gun_button_active_{i}'

            if i == self.current_gun_choice and active_button_name in self.gun_button_active_layers:
                # Рисуем активную кнопку
                self.gun_button_active_layers[active_button_name].draw()
            elif button_name in self.gun_button_layers:
                # Рисуем неактивную кнопку
                self.gun_button_layers[button_name].draw()

        self._draw_gun_animation()

    def _draw_gun_animation(self):
        """Отрисовка анимации оружия"""
        current_gun_frame = self.gun_anim_frames[self.current_gun_frame]

        if self.current_player_choice == 1:  # Biker
            gun_key = f'gun_biker_{current_gun_frame}'
        elif self.current_player_choice == 2:  # Punk
            gun_key = f'gun_punk_{current_gun_frame}'
        else:  # Cyborg
            gun_key = f'gun_cyborg_{current_gun_frame}'

        if gun_key in self.gun_players_layers:
            self.gun_players_layers[gun_key].draw()

    def _draw_player_selection(self):
        """Отрисовка панели выбора персонажа"""
        current_anim_frame = self.player_anim_frames[self.current_player_anim_frame]
        if current_anim_frame in self.players_anim_layers:
            self.players_anim_layers[current_anim_frame].draw()

        for i in range(1, 4):
            button_name = f'player_button_{i}'
            active_button_name = f'player_button_active_{i}'
            if i == self.current_player_choice and active_button_name in self.player_button_active_layers:
                self.player_button_active_layers[active_button_name].draw()
            elif button_name in self.player_button_layers:
                self.player_button_layers[button_name].draw()

    def _draw_text_elements(self):
        """Отрисовка текстовых элементов"""
        # Заголовок
        arcade.draw_text(
            "LADDERS RUNNER",
            SCREEN_WIDTH / 2,
            self.title_y,
            arcade.color.WHITE,
            font_size=32,
            anchor_x="center",
            anchor_y="center",
            font_name=self.font_name,
            bold=True
        )

        # Проверяем наличие любых сохранений
        has_save = self.database.has_any_save()

        # Надпись RESUME (только если есть сохранение)
        if has_save:
            arcade.draw_text(
                "RESUME",
                SCREEN_WIDTH / 2,
                self.resume_button_y,
                arcade.color.WHITE,
                font_size=24,
                anchor_x="center",
                anchor_y="center",
                font_name=self.font_name
            )

        # Надпись RESTART (всегда показываем)
        arcade.draw_text(
            "RESTART",
            SCREEN_WIDTH / 2,
            self.restart_button_y,
            arcade.color.WHITE,
            font_size=24,
            anchor_x="center",
            anchor_y="center",
            font_name=self.font_name
        )

        arcade.draw_text(
            "EXIT",
            self.exit_button_x + 1.35 * TILE_SIZE,
            self.exit_button_y + 0.8 * TILE_SIZE,
            arcade.color.WHITE,
            font_size=24,
            anchor_x="center",
            anchor_y="center",
            font_name=self.font_name
        )

    def check_click(self, x, y):
        """Проверка клика по всем кнопкам"""
        has_save = self.database.has_any_save()

        if self._point_in_button(x, y, SCREEN_WIDTH / 2, self.restart_button_y,
                                 self.button_width, self.button_height):
            self.restart_press_timer = self.button_press_duration
            return "restart"

        if has_save and self._point_in_button(x, y, SCREEN_WIDTH / 2, self.resume_button_y,
                                              self.button_width, self.button_height):
            self.resume_press_timer = self.button_press_duration
            return "resume"

        if self._point_in_button(x, y, self.exit_button_x, self.exit_button_y,
                                 self.exit_button_width, self.exit_button_height):
            self.exit_press_timer = self.button_press_duration
            return "exit"

        if self._point_in_button(x, y, self.gun_button_x, self.gun_button_y,
                                 self.gun_button_width, self.gun_button_height):
            self.gun_button_press_timer = self.button_press_duration

            self.show_weapon_selection = not self.show_weapon_selection
            if self.show_weapon_selection:
                self.show_frames_2 = True
                self.show_player_selection = False
            else:
                if not self.show_player_selection:
                    self.show_frames_2 = False

            return "gun_button"

        if self._point_in_button(x, y, self.player_button_x, self.player_button_y,
                                 self.player_button_width, self.player_button_height):
            self.player_button_press_timer = self.button_press_duration
            self.show_player_selection = not self.show_player_selection
            if self.show_player_selection:
                self.show_frames_2 = True
                self.show_weapon_selection = False
            else:
                if not self.show_weapon_selection:
                    self.show_frames_2 = False

            return "player_button"

        # Проверка кнопок выбора оружия
        if self.show_weapon_selection:
            for i in range(1, 4):
                pos = self.gun_button_positions[i]
                if self._point_in_button(x, y, pos['x'], pos['y'], pos['width'], pos['height']):
                    self.current_gun_choice = i
                    choice.gun = i
                    print(f"Выбрано оружие {i}")
                    return f"gun_select_{i}"

        # Проверка кнопок выбора персонажа
        if self.show_player_selection:
            for i in range(1, 4):
                pos = self.player_button_positions[i]
                if self._point_in_button(x, y, pos['x'], pos['y'], pos['width'], pos['height']):
                    self.current_player_choice = i
                    choice.player = i
                    print(f"Выбран персонаж {i}")
                    return f"player_select_{i}"

        return None

    def _point_in_button(self, x, y, button_x, button_y, button_width, button_height):
        """Проверка попадания точки в кнопку"""
        return (button_x - button_width / 2 <= x <= button_x + button_width / 2 and
                button_y - button_height / 2 <= y <= button_y + button_height / 2)

    def reset_background(self):
        """Сбросить выбор фона (выбрать случайный)"""
        self.current_background_index = random.randint(0, len(self.background_layer_names) - 1)


class PauseMenu:
    """Меню паузы"""

    def __init__(self):
        self.pause_map = arcade.load_tilemap("data/pause.tmx", scaling=TILE_SCALING)
        self.background_list = self.pause_map.sprite_lists.get('Слой тайлов 1', arcade.SpriteList())

        # Смещение для выравнивания по центру
        self.offset_x = 150
        self.offset_y = 0
        # Кнопка Exit
        self.exit_hitbox = {
            'min_x': 200 + self.offset_x,
            'max_x': 350 + self.offset_x,
            'min_y': 300 + self.offset_y,
            'max_y': 480 + self.offset_y
        }

        # Кнопка Resume
        self.resume_hitbox = {
            'min_x': 410 + self.offset_x,
            'max_x': 550 + self.offset_x,
            'min_y': 300 + self.offset_y,
            'max_y': 480 + self.offset_y
        }

        # Кнопка Restart
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


class GameOverMenu:
    """Меню Game Over"""

    def __init__(self):
        self.gameover_map = arcade.load_tilemap("data/gameover.tmx", scaling=TILE_SCALING)
        self.background_list = self.gameover_map.sprite_lists.get('Слой тайлов 1', arcade.SpriteList())

        # Смещение для выравнивания по центру
        self.offset_x = 45
        self.offset_y = 10

        # Кнопка Exit/Menu (слева - стрелка)
        self.exit_hitbox = {
            'min_x': 457 + self.offset_x,
            'max_x': 580 + self.offset_x,
            'min_y': 195 + self.offset_y,
            'max_y': 315 + self.offset_y
        }

        # Кнопка Restart (справа - круговая стрелка)
        self.restart_hitbox = {
            'min_x': 682 + self.offset_x,
            'max_x': 816 + self.offset_x,
            'min_y': 195 + self.offset_y,
            'max_y': 315 + self.offset_y
        }

    def draw(self):
        """Отрисовка меню Game Over"""
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
        if self._point_in_hitbox(x, y, self.exit_hitbox):
            return "exit"

        elif self._point_in_hitbox(x, y, self.restart_hitbox):
            return "restart"

        return None

    def _point_in_hitbox(self, x, y, hitbox):
        """Проверка попадания точки в hitbox"""
        return (hitbox['min_x'] <= x <= hitbox['max_x'] and
                hitbox['min_y'] <= y <= hitbox['max_y'])


class CompleteMenu:
    """Меню завершения уровня"""

    def __init__(self):
        self.complete_map = arcade.load_tilemap("data/complete.tmx", scaling=TILE_SCALING)

        # Загружаем слои для разного количества звезд
        self.complete_layers = {}
        for stars in [1, 2, 3]:
            layer_name = f'complete_{stars}'
            self.complete_layers[stars] = self.complete_map.sprite_lists.get(layer_name, arcade.SpriteList())

        self.background_layer = self.complete_map.sprite_lists.get('background', arcade.SpriteList())

        # Смещение для центрирования (аналогично другим меню)
        self.offset_x = 0
        self.offset_y = 0

        # Текущее количество звезд для отображения
        self.stars = 1

        # Кнопка слева - выход в главное меню
        self.exit_hitbox = {
            'min_x': 457 + self.offset_x,
            'max_x': 580 + self.offset_x,
            'min_y': 220 + self.offset_y,
            'max_y': 340 + self.offset_y
        }

        # Кнопка по центру - продолжить на следующий уровень
        self.continue_hitbox = {
            'min_x': 583 + self.offset_x,
            'max_x': 678 + self.offset_x,
            'min_y': 210 + self.offset_y,
            'max_y': 330 + self.offset_y
        }

        # Кнопка справа - перезапуск уровня
        self.restart_hitbox = {
            'min_x': 682 + self.offset_x,
            'max_x': 816 + self.offset_x,
            'min_y': 220 + self.offset_y,
            'max_y': 340 + self.offset_y
        }

    def set_stars(self, stars):
        """Установить количество звезд для отображения"""
        self.stars = max(1, min(3, stars))  # Ограничиваем 1-3

    def draw(self):
        """Отрисовка меню завершения"""
        # Смещаем спрайты для центрирования
        all_sprites = []

        if self.background_layer:
            all_sprites.extend(self.background_layer)

        if self.stars in self.complete_layers:
            all_sprites.extend(self.complete_layers[self.stars])

        for sprite in all_sprites:
            sprite.center_x += self.offset_x
            sprite.center_y += self.offset_y

        # Рисуем фон и соответствующий слой
        if self.background_layer:
            self.background_layer.draw()

        if self.stars in self.complete_layers:
            self.complete_layers[self.stars].draw()

        # Возвращаем спрайты обратно
        for sprite in all_sprites:
            sprite.center_x -= self.offset_x
            sprite.center_y -= self.offset_y

    def check_click(self, x, y):
        """Проверка клика по кнопкам"""
        if self._point_in_hitbox(x, y, self.exit_hitbox):
            return "exit"

        elif self._point_in_hitbox(x, y, self.continue_hitbox):
            return "continue"

        elif self._point_in_hitbox(x, y, self.restart_hitbox):
            return "restart"

        return None

    def _point_in_hitbox(self, x, y, hitbox):
        """Проверка попадания точки в hitbox"""
        return (hitbox['min_x'] <= x <= hitbox['max_x'] and
                hitbox['min_y'] <= y <= hitbox['max_y'])


class GameHUD:

    def __init__(self, tilemap_path="data/interface.tmx"):
        self.tilemap = arcade.load_tilemap(tilemap_path, scaling=TILE_SCALING)

        self.heart_good_layers = {}
        self.heart_not_good_layers = {}
        self.heart_not_good_anim_layers = {}
        self.heart_anim_one_layers = {}
        self.heart_anim_two_layers = {}

        self.skull_anim_one_layers = {}
        self.skull_anim_two_layers = {}
        self.skull_anim_three_layers = {}

        self.dollars_layers = {}
        self.dollars_anim_layers = {}

        self.cards_layers = {}
        self.cards_anim_layers = {}

        self.blood_layer = None

        self._load_all_hud_layers()

        self.current_health = PLAYER_MAX_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
        self.hearts_state = [10] * 10
        self.active_hearts = 10
        self.heart_animations = []

        self.killed_enemies = 0
        self.max_enemies = 10
        self.skull_animations = []

        self.money_collected = 0
        self.max_money = 10
        self.money_animations = []

        self.cards_collected = 0
        self.max_cards = 10
        self.card_animations = []

        self.blood_timer = 0
        self.show_blood = False

    def _load_all_hud_layers(self):
        for i in range(1, 11):
            layer_name = f'heart_good_{i}'
            self.heart_good_layers[i] = self.tilemap.sprite_lists.get(layer_name, arcade.SpriteList())

            layer_name = f'heart_not_good_{i}'
            self.heart_not_good_layers[i] = self.tilemap.sprite_lists.get(layer_name, arcade.SpriteList())

            layer_name = f'heart_not_good_anim_{i}'
            self.heart_not_good_anim_layers[i] = self.tilemap.sprite_lists.get(layer_name, arcade.SpriteList())

            layer_name = f'heart_anim_one_{i}'
            self.heart_anim_one_layers[i] = self.tilemap.sprite_lists.get(layer_name, arcade.SpriteList())

            layer_name = f'heart_anim_two_{i}'
            self.heart_anim_two_layers[i] = self.tilemap.sprite_lists.get(layer_name, arcade.SpriteList())

        for i in range(1, 11):
            layer_name = f'skull_anim_one_{i}'
            self.skull_anim_one_layers[i] = self.tilemap.sprite_lists.get(layer_name, arcade.SpriteList())

            layer_name = f'skull_anim_two_{i}'
            self.skull_anim_two_layers[i] = self.tilemap.sprite_lists.get(layer_name, arcade.SpriteList())

            layer_name = f'skull_anim_three_{i}'
            self.skull_anim_three_layers[i] = self.tilemap.sprite_lists.get(layer_name, arcade.SpriteList())

        for i in range(1, 11):
            layer_name = f'dollars_{i}'
            self.dollars_layers[i] = self.tilemap.sprite_lists.get(layer_name, arcade.SpriteList())

            layer_name = f'dollars_anim_{i}'
            self.dollars_anim_layers[i] = self.tilemap.sprite_lists.get(layer_name, arcade.SpriteList())

        for i in range(1, 11):
            layer_name = f'card_{i}'
            self.cards_layers[i] = self.tilemap.sprite_lists.get(layer_name, arcade.SpriteList())

            layer_name = f'card_anim_{i}'
            self.cards_anim_layers[i] = self.tilemap.sprite_lists.get(layer_name, arcade.SpriteList())

        self.blood_layer = self.tilemap.sprite_lists.get('blood', arcade.SpriteList())

    def set_health(self, health):
        old_health = self.current_health
        self.current_health = max(0, min(health, self.max_health))

        health_diff = old_health - self.current_health

        if health_diff > 0:
            self._process_health_loss(health_diff)

    def _process_health_loss(self, damage):
        damage_remaining = damage

        for i in range(self.active_hearts - 1, -1, -1):
            if damage_remaining <= 0:
                break

            heart_index = i + 1

            if self.hearts_state[i] == 10:
                if damage_remaining >= 10:
                    self.hearts_state[i] = 0
                    self.heart_animations.append({
                        'index': heart_index,
                        'stage': 1,
                        'timer': 0
                    })
                    damage_remaining -= 10
                    self.active_hearts -= 1
                elif damage_remaining >= 5:
                    self.hearts_state[i] = 5
                    self.heart_animations.append({
                        'index': heart_index,
                        'type': 'not_good',
                        'timer': HEART_NOT_GOOD_ANIM_DURATION
                    })
                    damage_remaining -= 5
            elif self.hearts_state[i] == 5:
                self.hearts_state[i] = 0
                self.heart_animations.append({
                    'index': heart_index,
                    'stage': 1,
                    'timer': 0
                })
                damage_remaining -= 5
                self.active_hearts -= 1

    def add_kill(self):
        if self.killed_enemies < self.max_enemies:
            skull_index = self.killed_enemies + 1
            self.killed_enemies += 1

            self.skull_animations.append({
                'index': skull_index,
                'stage': 3,
                'timer': 0
            })

    def add_money(self):
        if self.money_collected < self.max_money:
            money_index = self.money_collected + 1
            self.money_collected += 1

            self.money_animations.append({
                'index': money_index,
                'stage': 1,
                'timer': 0
            })

    def add_card(self):
        if self.cards_collected < self.max_cards:
            card_index = self.cards_collected + 1
            self.cards_collected += 1

            self.card_animations.append({
                'index': card_index,
                'stage': 1,
                'timer': 0
            })

    def show_blood_animation(self):
        self.show_blood = True
        self.blood_timer = BLOOD_ANIM_DURATION

    def update(self, delta_time):
        updated_heart_animations = []
        for anim in self.heart_animations:
            if 'type' in anim and anim['type'] == 'not_good':
                anim['timer'] -= delta_time
                if anim['timer'] > 0:
                    updated_heart_animations.append(anim)
            else:
                anim['timer'] += delta_time
                if anim['stage'] == 1 and anim['timer'] < HEART_ANIM_ONE_DURATION:
                    updated_heart_animations.append(anim)
                elif anim['stage'] == 1 and anim['timer'] >= HEART_ANIM_ONE_DURATION:
                    anim['stage'] = 2
                    anim['timer'] = 0
                    updated_heart_animations.append(anim)
                elif anim['stage'] == 2 and anim['timer'] < HEART_ANIM_TWO_DURATION:
                    updated_heart_animations.append(anim)
        self.heart_animations = updated_heart_animations

        updated_skull_animations = []
        for anim in self.skull_animations:
            anim['timer'] += delta_time

            if anim['stage'] == 3 and anim['timer'] < SKULL_ANIM_THREE_DURATION:
                updated_skull_animations.append(anim)
            elif anim['stage'] == 3 and anim['timer'] >= SKULL_ANIM_THREE_DURATION:
                anim['stage'] = 2
                anim['timer'] = 0
                updated_skull_animations.append(anim)
            elif anim['stage'] == 2 and anim['timer'] < SKULL_ANIM_TWO_DURATION:
                updated_skull_animations.append(anim)
            elif anim['stage'] == 2 and anim['timer'] >= SKULL_ANIM_TWO_DURATION:
                anim['stage'] = 1
        self.skull_animations = updated_skull_animations

        updated_money_animations = []
        for anim in self.money_animations:
            anim['timer'] += delta_time

            if anim['stage'] == 1 and anim['timer'] < DOLLAR_ANIM_DURATION:
                updated_money_animations.append(anim)
            elif anim['stage'] == 1 and anim['timer'] >= DOLLAR_ANIM_DURATION:
                anim['stage'] = 2
        self.money_animations = updated_money_animations

        updated_card_animations = []
        for anim in self.card_animations:
            anim['timer'] += delta_time

            if anim['stage'] == 1 and anim['timer'] < CARD_ANIM_DURATION:
                updated_card_animations.append(anim)
            elif anim['stage'] == 1 and anim['timer'] >= CARD_ANIM_DURATION:
                anim['stage'] = 2
        self.card_animations = updated_card_animations

        if self.show_blood:
            self.blood_timer -= delta_time
            if self.blood_timer <= 0:
                self.show_blood = False

    def draw(self):
        self._draw_health()
        self._draw_skulls()
        self._draw_money()
        self._draw_cards()

        if self.show_blood and self.blood_layer:
            self.blood_layer.draw()

    def _draw_health(self):
        for i in range(10):
            heart_index = i + 1
            heart_state = self.hearts_state[i] if i < len(self.hearts_state) else 0

            active_anim = None
            for anim in self.heart_animations:
                if anim['index'] == heart_index:
                    active_anim = anim
                    break

            current_layer = None

            if active_anim:
                if 'type' in active_anim and active_anim['type'] == 'not_good':
                    if heart_index in self.heart_not_good_anim_layers:
                        current_layer = self.heart_not_good_anim_layers[heart_index]
                elif active_anim['stage'] == 1:
                    if heart_index in self.heart_anim_one_layers:
                        current_layer = self.heart_anim_one_layers[heart_index]
                elif active_anim['stage'] == 2:
                    if heart_index in self.heart_anim_two_layers:
                        current_layer = self.heart_anim_two_layers[heart_index]
            elif heart_state == 10:
                if heart_index in self.heart_good_layers:
                    current_layer = self.heart_good_layers[heart_index]
            elif heart_state == 5:
                if heart_index in self.heart_not_good_layers:
                    current_layer = self.heart_not_good_layers[heart_index]

            if current_layer:
                current_layer.draw()

    def _draw_skulls(self):
        for i in range(self.killed_enemies):
            skull_index = i + 1

            active_anim = None
            for anim in self.skull_animations:
                if anim['index'] == skull_index:
                    active_anim = anim
                    break

            current_layer = None

            if active_anim:
                if active_anim['stage'] == 3:
                    if skull_index in self.skull_anim_three_layers:
                        current_layer = self.skull_anim_three_layers[skull_index]
                elif active_anim['stage'] == 2:
                    if skull_index in self.skull_anim_two_layers:
                        current_layer = self.skull_anim_two_layers[skull_index]
                elif active_anim['stage'] == 1:
                    if skull_index in self.skull_anim_one_layers:
                        current_layer = self.skull_anim_one_layers[skull_index]
            else:
                if skull_index in self.skull_anim_one_layers:
                    current_layer = self.skull_anim_one_layers[skull_index]

            if current_layer:
                current_layer.draw()

    def _draw_money(self):
        for i in range(self.money_collected):
            money_index = i + 1

            active_anim = None
            for anim in self.money_animations:
                if anim['index'] == money_index:
                    active_anim = anim
                    break

            current_layer = None

            if active_anim:
                if active_anim['stage'] == 1:
                    if money_index in self.dollars_anim_layers:
                        current_layer = self.dollars_anim_layers[money_index]
                elif active_anim['stage'] == 2:
                    if money_index in self.dollars_layers:
                        current_layer = self.dollars_layers[money_index]
            else:
                if money_index in self.dollars_layers:
                    current_layer = self.dollars_layers[money_index]

            if current_layer:
                current_layer.draw()

    def _draw_cards(self):
        for i in range(self.cards_collected):
            card_index = i + 1

            active_anim = None
            for anim in self.card_animations:
                if anim['index'] == card_index:
                    active_anim = anim
                    break

            current_layer = None

            if active_anim:
                if active_anim['stage'] == 1:
                    if card_index in self.cards_anim_layers:
                        current_layer = self.cards_anim_layers[card_index]
                elif active_anim['stage'] == 2:
                    if card_index in self.cards_layers:
                        current_layer = self.cards_layers[card_index]
            else:
                if card_index in self.cards_layers:
                    current_layer = self.cards_layers[card_index]

            if current_layer:
                current_layer.draw()

    def reset(self):
        self.current_health = PLAYER_MAX_HEALTH
        self.hearts_state = [10] * 10
        self.active_hearts = 10
        self.heart_animations = []

        self.killed_enemies = 0
        self.skull_animations = []

        self.money_collected = 0
        self.money_animations = []

        self.cards_collected = 0
        self.card_animations = []

        self.blood_timer = 0
        self.show_blood = False