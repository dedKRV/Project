import arcade
from core import *
from entities import Player
from enemies import Enemy, Bullet, Card
from enemy_config import LEVEL_2_ENEMIES, LEVEL_2_SPAWN, ENEMY_Y_OFFSET, LEVEL_2_CARDS
from control import Controls


class GameWindow2(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(BACKGROUND_COLOR)

        # Основные игровые объекты
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

        self.controls = Controls()
        self.on_ladder = False
        self.is_running = False
        self.is_jumping = False
        self.is_climbing = False

        # Таймеры анимаций
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

        # Здоровье и урон
        self.player_health = PLAYER_MAX_HEALTH
        self.damage_cooldown = 0
        self.DAMAGE_COOLDOWN_TIME = 0.5

        self.shoot_timer = 0

        self.cards_collected = 0
        self.total_cards = len(LEVEL_2_CARDS)
        self.exit_visible = False
        self.exit_animation_visible = True

        self.stars_earned = 0
        self.game_completed = False
        self.completion_timer = 0
        self.completion_message = ""

        self.play_time = 0.0

    def setup(self):
        """Инициализация уровня """
        self.player = Player()
        self.player.center_x = TILE_SIZE * LEVEL_2_SPAWN[0]
        self.player.center_y = TILE_SIZE * LEVEL_2_SPAWN[1]
        self.player_spritelist = arcade.SpriteList()
        self.player_spritelist.append(self.player)

        self.right_wall = arcade.SpriteSolidColor(10, LEVEL_HEIGHT, arcade.color.BLACK)
        self.right_wall.center_x = LEVEL_WIDTH + 5
        self.right_wall.center_y = LEVEL_HEIGHT / 2

        self.enemies = arcade.SpriteList()
        self.enemy_bullets = arcade.SpriteList()
        self.cards_list = arcade.SpriteList()
        self.initial_cards_data = LEVEL_2_CARDS.copy()

        self.load_cards()

        layer_options = {
            "ground": {"use_spatial_hash": True},
            "floor1": {"use_spatial_hash": True},
            "floor2": {"use_spatial_hash": True},
            "ladders": {"use_spatial_hash": True},
            "entry": {"use_spatial_hash": True},
            "exit": {"use_spatial_hash": True},
            "collision": {"use_spatial_hash": True},
            "damage": {"use_spatial_hash": True},
            "damage_2": {"use_spatial_hash": True},
            "transportation": {"use_spatial_hash": True},
            "jump": {"use_spatial_hash": True},
            "spawn_entities": {"use_spatial_hash": True},
        }

        for layer_name in self.animation_layers:
            layer_options[layer_name] = {"use_spatial_hash": False}

        for layer_name in self.jump_animation_layers:
            layer_options[layer_name] = {"use_spatial_hash": False}

        layer_options['exit_animation'] = {"use_spatial_hash": False}

        self.tile_map = arcade.load_tilemap(
            "data/level_2.tmx",
            scaling=TILE_SCALING,
            layer_options=layer_options)

        ground_list = self.tile_map.sprite_lists.get('ground', arcade.SpriteList())
        floor1_list = self.tile_map.sprite_lists.get('floor1', arcade.SpriteList())
        floor2_list = self.tile_map.sprite_lists.get('floor2', arcade.SpriteList())
        self.ladders_list = self.tile_map.sprite_lists.get('ladders', arcade.SpriteList())
        self.entry_list = self.tile_map.sprite_lists.get('entry', arcade.SpriteList())
        self.exit_list = self.tile_map.sprite_lists.get('exit', arcade.SpriteList())
        collision_list = self.tile_map.sprite_lists.get('collision', arcade.SpriteList())
        self.damage_list = self.tile_map.sprite_lists.get('damage', arcade.SpriteList())
        self.damage_2_list = self.tile_map.sprite_lists.get('damage_2', arcade.SpriteList())
        self.transportation_list = self.tile_map.sprite_lists.get('transportation', arcade.SpriteList())
        self.jump_list = self.tile_map.sprite_lists.get('jump', arcade.SpriteList())
        self.spawn_entities_list = self.tile_map.sprite_lists.get('spawn_entities', arcade.SpriteList())
        self.exit_animation_list = self.tile_map.sprite_lists.get('exit_animation', arcade.SpriteList())

        for layer_name in self.animation_layers:
            self.animation_layer_sprites[layer_name] = self.tile_map.sprite_lists.get(layer_name, arcade.SpriteList())

        for layer_name in self.jump_animation_layers:
            self.jump_animation_sprites[layer_name] = self.tile_map.sprite_lists.get(layer_name, arcade.SpriteList())

        self.walls = arcade.SpriteList()
        self.walls.extend(ground_list)
        self.walls.extend(floor1_list)
        self.walls.extend(floor2_list)
        self.walls.extend(collision_list)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            player_sprite=self.player,
            gravity_constant=GRAVITY,
            walls=self.walls,
            ladders=self.ladders_list
        )

        self.visible_animation_layer = self.animation_layers[0]

        if self.spawn_entities_list:
            self.load_enemies_from_spawn_points()
            self.save_initial_enemies_state()

        self.update_exit_visibility()
        self.play_time = 0.0

    def load_cards(self):
        """Загрузка карт"""
        for card_pos in LEVEL_2_CARDS:
            x, y = card_pos
            card = Card(x, y)
            self.cards_list.append(card)

    def load_enemies_from_spawn_points(self):
        """Создание врагов в точках спавна"""
        if self.spawn_entities_list:
            attack_cooldown, damage = LEVEL_2_ENEMIES
            for spawn in self.spawn_entities_list:
                enemy_x = spawn.center_x
                enemy_y = spawn.center_y
                enemy = Enemy(enemy_x, enemy_y, attack_cooldown, damage, ENEMY_Y_OFFSET)
                self.enemies.append(enemy)

    def update_exit_visibility(self):
        """Показать/скрыть выход в зависимости от собранных карт"""
        if self.cards_collected >= self.total_cards:
            self.exit_visible = True
            self.exit_animation_visible = False
        else:
            self.exit_visible = False
            self.exit_animation_visible = True

    def save_initial_enemies_state(self):
        """Сохраняем исходные данные врагов"""
        self.initial_enemies_data = []
        for spawn in self.spawn_entities_list:
            self.initial_enemies_data.append({
                'x': spawn.center_x,
                'y': spawn.center_y
            })

    def reset_level_state(self):
        """Сброс уровня при смерти игрока"""
        self.cards_list.clear()
        for card_pos in self.initial_cards_data:
            x, y = card_pos
            card = Card(x, y)
            self.cards_list.append(card)

        self.cards_collected = 0

        self.enemies.clear()
        self.enemy_bullets.clear()

        attack_cooldown, damage = LEVEL_2_ENEMIES
        for enemy_data in self.initial_enemies_data:
            enemy = Enemy(
                enemy_data['x'],
                enemy_data['y'],
                attack_cooldown,
                damage,
                ENEMY_Y_OFFSET
            )
            self.enemies.append(enemy)

        self.player.player_bullets.clear()
        self.update_exit_visibility()
        self.jump_animation_active = False

    def apply_damage(self, damage_amount):
        """Нанесение урона игроку"""
        if self.damage_cooldown <= 0:
            self.player_health -= damage_amount
            self.damage_cooldown = self.DAMAGE_COOLDOWN_TIME

            if self.player_health < 0:
                self.player_health = 0

            if self.player_health <= 0:
                self.reset_level_state()

                self.player_health = PLAYER_MAX_HEALTH
                from enemy_config import LEVEL_2_SPAWN
                self.player.center_x = TILE_SIZE * LEVEL_2_SPAWN[0]
                self.player.center_y = TILE_SIZE * LEVEL_2_SPAWN[1]

                self.damage_cooldown = 0
                self.shoot_timer = 0

    def check_game_completion(self):
        """Проверка завершения игры и подсчет звезд для уровня 2"""
        exit_hit_list = arcade.check_for_collision_with_list(self.player, self.exit_list)

        if not exit_hit_list:
            return False

        all_cards_collected = self.cards_collected >= self.total_cards

        if not all_cards_collected:
            return False

        all_enemies_dead = True
        for enemy in self.enemies:
            if enemy.state != 'dead':
                all_enemies_dead = False
                break

        time_bonus = self.play_time <= PERFECT_TIME

        if all_cards_collected and all_enemies_dead and time_bonus:
            self.stars_earned = 3
            print("★ ★ ★ - ИДЕАЛЬНО! Уровень 2 пройден!")
            print(f"Собрано карт: {self.cards_collected}/{self.total_cards}")
            print(f"Убито врагов: Все!")
            print(f"Время: {int(self.play_time)}с (бонус за скорость!)")
        elif all_cards_collected and all_enemies_dead:
            self.stars_earned = 2
            print("★ ★ - Отлично! Уровень 2 пройден!")
            print(f"Собрано карт: {self.cards_collected}/{self.total_cards}")
            print(f"Убито врагов: Все!")
            print(f"Время: {int(self.play_time)}с")
        elif all_cards_collected:
            self.stars_earned = 1
            print("УРОВЕНЬ 2 ПРОЙДЕН!")
            print("★ - Хорошо!")
            print(f"Собрано карт: {self.cards_collected}/{self.total_cards}")

            killed_enemies = 0
            for enemy in self.enemies:
                if enemy.state == 'dead':
                    killed_enemies += 1
            print(f"Убито врагов: {killed_enemies}/{len(self.enemies)}")
            print(f"Время: {int(self.play_time)}с")
            print("=" * 50)

        self.game_completed = True
        self.completion_timer = 1.0

        return True

    def check_collisions(self):
        """Проверка всех коллизий"""
        damage_hit_list = arcade.check_for_collision_with_list(self.player, self.damage_list)
        if damage_hit_list:
            self.apply_damage(DAMAGE_LAYER_DAMAGE)

        transportation_hit_list = arcade.check_for_collision_with_list(self.player, self.transportation_list)
        if transportation_hit_list:
            self.player.change_x = TRANSPORTATION_SPEED

        jump_hit_list = arcade.check_for_collision_with_list(self.player, self.jump_list)
        if jump_hit_list and not self.jump_animation_active:
            self.is_on_jump_layer = True
            self.jump_animation_active = True
            self.jump_animation_elapsed = 0
            self.player.change_y = JUMP_POWER

        cards_hit_list = arcade.check_for_collision_with_list(self.player, self.cards_list)
        for card in cards_hit_list:
            if card in self.cards_list:
                self.cards_list.remove(card)
                self.cards_collected += 1
                self.update_exit_visibility()

        bullets_to_remove = []
        for bullet in self.enemy_bullets:
            wall_hit_list = arcade.check_for_collision_with_list(bullet, self.walls)
            if wall_hit_list:
                bullets_to_remove.append(bullet)
                continue

            if arcade.check_for_collision(bullet, self.player):
                self.apply_damage(bullet.damage)
                bullets_to_remove.append(bullet)

        for bullet in bullets_to_remove:
            if bullet in self.enemy_bullets:
                self.enemy_bullets.remove(bullet)
                for enemy in self.enemies:
                    if bullet in enemy.bullets:
                        enemy.bullets.remove(bullet)

        player_bullets_to_remove = []
        for bullet in self.player.player_bullets:
            wall_hit_list = arcade.check_for_collision_with_list(bullet, self.walls)
            if wall_hit_list:
                player_bullets_to_remove.append(bullet)
                continue

            for enemy in self.enemies:
                if arcade.check_for_collision(bullet, enemy):
                    player_bullets_to_remove.append(bullet)
                    if enemy.take_damage(bullet.damage):
                        self.enemies.remove(enemy)
                    break

        for bullet in player_bullets_to_remove:
            if bullet in self.player.player_bullets:
                self.player.player_bullets.remove(bullet)

    def on_draw(self):
        """Отрисовка всех объектов"""
        self.clear()

        background_layers = ['background', 'background_2']
        for layer_name in background_layers:
            if layer_name in self.tile_map.sprite_lists:
                self.tile_map.sprite_lists[layer_name].draw()

        self.walls.draw()
        self.ladders_list.draw()
        self.entry_list.draw()

        if self.exit_visible:
            self.exit_list.draw()

        if self.exit_animation_visible and self.exit_animation_list:
            self.exit_animation_list.draw()

        self.damage_list.draw()
        self.damage_2_list.draw()
        self.transportation_list.draw()
        self.jump_list.draw()

        if self.spawn_entities_list:
            self.spawn_entities_list.draw()

        self.enemies.draw()
        self.enemy_bullets.draw()
        self.cards_list.draw()

        if self.visible_animation_layer in self.animation_layer_sprites:
            self.animation_layer_sprites[self.visible_animation_layer].draw()

        if self.visible_jump_animation_layer and self.visible_jump_animation_layer in self.jump_animation_sprites:
            self.jump_animation_sprites[self.visible_jump_animation_layer].draw()

        self.player_spritelist.draw()
        self.player.player_bullets.draw()

        minutes = int(self.play_time // 60)
        seconds = int(self.play_time % 60)
        time_text = f"Время: {minutes:02d}:{seconds:02d}"
        arcade.draw_text(
            time_text,
            10,
            SCREEN_HEIGHT - 90,
            UI_TEXT_COLOR,
            UI_FONT_SIZE,
            font_name=UI_FONT_NAME,
            bold=True
        )

        health_text = f"Здоровье: {self.player_health}/{PLAYER_MAX_HEALTH}"
        arcade.draw_text(
            health_text,
            10,
            SCREEN_HEIGHT - 30,
            UI_TEXT_COLOR,
            UI_FONT_SIZE,
            font_name=UI_FONT_NAME,
            bold=True
        )

        cards_text = f"Карты: {self.cards_collected}/{self.total_cards}"
        arcade.draw_text(
            cards_text,
            10,
            SCREEN_HEIGHT - 60,
            UI_TEXT_COLOR,
            UI_FONT_SIZE,
            font_name=UI_FONT_NAME,
            bold=True
        )

    def on_update(self, delta_time):
        """Основной игровой цикл"""
        if not self.game_completed:
            self.play_time += delta_time

        if self.game_completed:
            self.completion_timer -= delta_time
            if self.completion_timer <= 0:
                arcade.close_window()
            return

        self.player.center_x = max(0, min(self.player.center_x, LEVEL_WIDTH))
        self.player.center_y = max(0, min(self.player.center_y, LEVEL_HEIGHT))

        self.animation_timer += delta_time
        if self.animation_timer >= ANIMATION_FRAME_TIME:
            self.animation_timer = 0
            self.current_animation_frame = (self.current_animation_frame + 1) % len(self.animation_layers)
            self.visible_animation_layer = self.animation_layers[self.current_animation_frame]

        if self.jump_animation_active:
            self.jump_animation_elapsed += delta_time

            if self.jump_animation_elapsed < 0.1:
                self.visible_jump_animation_layer = 'jump_animation_1'
            elif self.jump_animation_elapsed < 0.2:
                self.visible_jump_animation_layer = 'jump_animation_2'
            elif self.jump_animation_elapsed < 0.3:
                self.visible_jump_animation_layer = 'jump_animation_3'
            else:
                self.visible_jump_animation_layer = 'jump_animation_4'

            if self.jump_animation_elapsed >= self.jump_animation_duration:
                self.jump_animation_active = False

        if self.damage_cooldown > 0:
            self.damage_cooldown -= delta_time

        for card in self.cards_list:
            card.update(delta_time)

        for enemy in self.enemies:
            enemy.update(self.player, delta_time, self.walls)

            bullets_to_remove = []
            for bullet in enemy.bullets:
                bullet.update(delta_time)

                if bullet.should_remove:
                    bullets_to_remove.append(bullet)
                elif (bullet.center_x < -SCREEN_MARGIN or
                      bullet.center_x > SCREEN_WIDTH + SCREEN_MARGIN or
                      bullet.center_y < -SCREEN_MARGIN or
                      bullet.center_y > SCREEN_HEIGHT + SCREEN_MARGIN):
                    bullets_to_remove.append(bullet)
                else:
                    wall_hit_list = arcade.check_for_collision_with_list(bullet, self.walls)
                    if wall_hit_list:
                        bullets_to_remove.append(bullet)
                    elif bullet not in self.enemy_bullets:
                        self.enemy_bullets.append(bullet)

            for bullet in bullets_to_remove:
                if bullet in enemy.bullets:
                    enemy.bullets.remove(bullet)
                if bullet in self.enemy_bullets:
                    self.enemy_bullets.remove(bullet)

        bullets_to_remove = []
        for bullet in self.enemy_bullets:
            if bullet.should_remove:
                bullets_to_remove.append(bullet)
            elif (bullet.center_x < -SCREEN_MARGIN or
                  bullet.center_x > SCREEN_WIDTH + SCREEN_MARGIN or
                  bullet.center_y < -SCREEN_MARGIN or
                  bullet.center_y > SCREEN_HEIGHT + SCREEN_MARGIN):
                bullets_to_remove.append(bullet)

        for bullet in bullets_to_remove:
            if bullet in self.enemy_bullets:
                self.enemy_bullets.remove(bullet)
            for enemy in self.enemies:
                if bullet in enemy.bullets:
                    enemy.bullets.remove(bullet)

        self.player.player_bullets.update()

        bullets_to_remove = []
        for bullet in self.player.player_bullets:
            if bullet.should_remove or \
                    bullet.center_x < -SCREEN_MARGIN or \
                    bullet.center_x > SCREEN_WIDTH + SCREEN_MARGIN or \
                    bullet.center_y < -SCREEN_MARGIN or \
                    bullet.center_y > SCREEN_HEIGHT + SCREEN_MARGIN:
                bullets_to_remove.append(bullet)

        for bullet in bullets_to_remove:
            bullet.remove_from_sprite_lists()

        self.on_ladder = self.physics_engine.is_on_ladder()

        movement = self.controls.get_movement()
        left_pressed = movement["left"]
        right_pressed = movement["right"]
        up_pressed = movement["up"]
        down_pressed = movement["down"]
        shoot_pressed = self.controls.get_shooting()

        if shoot_pressed and self.shoot_timer <= 0:
            self.player.shoot()
            self.shoot_timer = SHOOT_COOLDOWN

        if self.shoot_timer > 0:
            self.shoot_timer -= delta_time

        self.is_running = (left_pressed or right_pressed) and not self.on_ladder
        self.is_climbing = self.on_ladder and (up_pressed or down_pressed)

        if self.check_game_completion():
            return

        self.player.update_animation(
            delta_time,
            is_running=self.is_running,
            is_jumping=False,
            is_climbing=self.is_climbing,
            is_on_ladder=self.on_ladder,
            left_pressed=left_pressed,
            right_pressed=right_pressed
        )

        if self.on_ladder:
            if up_pressed and not down_pressed:
                self.player.change_y = LADDER_SPEED
            elif down_pressed and not up_pressed:
                self.player.change_y = -LADDER_SPEED
            else:
                self.player.change_y = 0

            if left_pressed and not right_pressed:
                self.player.change_x = -PLAYER_SPEED
            elif right_pressed and not left_pressed:
                self.player.change_x = PLAYER_SPEED
            else:
                self.player.change_x = 0
        else:
            if left_pressed and not right_pressed:
                self.player.change_x = -PLAYER_SPEED
            elif right_pressed and not left_pressed:
                self.player.change_x = PLAYER_SPEED
            else:
                self.player.change_x = 0

            if up_pressed and not self.on_ladder and self.physics_engine.can_jump():
                self.player.change_y = PLAYER_JUMP_SPEED
                self.player.start_jump_animation()

        self.check_collisions()
        self.physics_engine.update()

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш"""
        if key == arcade.key.KEY_1:
            self.player.toggle_weapon()
        else:
            self.controls.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиш"""
        self.controls.on_key_release(key, modifiers)

    def get_killed_enemy_indices(self):
        """Получить индексы убитых врагов"""
        killed_indices = []
        for i, enemy in enumerate(self.enemies):
            if enemy.state == 'dead':
                killed_indices.append(i)
        return killed_indices

    def get_save_data(self):
        """Получить данные для сохранения"""
        from config_gun import PLAYER_CHOICE, WEAPON_CHOICE

        return {
            'level_number': 2,
            'character_skin': PLAYER_CHOICE,
            'weapon': int(WEAPON_CHOICE),
            'player_x': self.player.center_x,
            'player_y': self.player.center_y,
            'player_health': self.player_health,
            'enemies_killed': len(self.get_killed_enemy_indices()),
            'cards_collected': self.cards_collected,
            'total_cards': self.total_cards,
            'play_time': self.play_time,
            'killed_enemy_indices': self.get_killed_enemy_indices()
        }

    def load_from_save(self, save_data):
        """Загрузить игру из сохранения"""
        if not save_data:
            return

        self.player.center_x = save_data['player_x']
        self.player.center_y = save_data['player_y']
        self.player_health = save_data['player_health']

        self.cards_collected = save_data['cards_collected']
        cards_to_remove = []
        for i, card_pos in enumerate(self.initial_cards_data):
            if i < save_data['cards_collected']:
                for card in self.cards_list:
                    x_tile = (card.center_x - TILE_SIZE * TILE_SCALING / 2) / (TILE_SIZE * TILE_SCALING)
                    y_tile = (card.center_y - TILE_SIZE * TILE_SCALING / 2) / (TILE_SIZE * TILE_SCALING)
                    if abs(x_tile - card_pos[0]) < 0.1 and abs(y_tile - card_pos[1]) < 0.1:
                        cards_to_remove.append(card)
                        break

        for card in cards_to_remove:
            if card in self.cards_list:
                self.cards_list.remove(card)

        for enemy_index in save_data['killed_enemy_indices']:
            if enemy_index < len(self.enemies):
                self.enemies[enemy_index].state = 'dead'
                self.enemies[enemy_index].health = 0

        self.play_time = save_data['play_time']
        self.update_exit_visibility()