import arcade
from core import *
from entities import Player, PlayerBullet
from enemies import Enemy, Bullet, Card
from enemy_config import LEVEL_1_ENEMIES, ENEMY_Y_OFFSET, LEVEL_1_CARDS
from control import Controls

class GameWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(BACKGROUND_COLOR)

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
        self.physics_engine = None

        self.enemies = None
        self.enemy_bullets = None

        self.controls = Controls()
        self.on_ladder = False
        self.is_running = False
        self.is_jumping = False
        self.is_climbing = False

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

        self.cards_collected = 0
        self.total_cards = len(LEVEL_1_CARDS)
        self.exit_visible = False
        self.exit_animation_visible = True

    def setup(self):
        self.player = Player()
        self.player_spritelist = arcade.SpriteList()
        self.player_spritelist.append(self.player)

        self.enemies = arcade.SpriteList()
        self.enemy_bullets = arcade.SpriteList()
        self.cards_list = arcade.SpriteList()

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
            "data/level_1.tmx",
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

        self.update_exit_visibility()

    def load_cards(self):
        for card_pos in LEVEL_1_CARDS:
            x, y = card_pos
            card = Card(x, y)
            self.cards_list.append(card)

    def load_enemies_from_spawn_points(self):
        if self.spawn_entities_list:
            attack_cooldown, damage = LEVEL_1_ENEMIES
            for spawn in self.spawn_entities_list:
                enemy_x = spawn.center_x
                enemy_y = spawn.center_y
                enemy = Enemy(enemy_x, enemy_y, attack_cooldown, damage, ENEMY_Y_OFFSET)
                self.enemies.append(enemy)

    def update_exit_visibility(self):
        if self.cards_collected >= self.total_cards:
            self.exit_visible = True
            self.exit_animation_visible = False
        else:
            self.exit_visible = False
            self.exit_animation_visible = True

    def apply_damage(self, damage_amount):
        if self.damage_cooldown <= 0:
            self.player_health -= damage_amount
            self.damage_cooldown = self.DAMAGE_COOLDOWN_TIME
            if self.player_health < 0:
                self.player_health = 0
            if self.player_health <= 0:
                self.player_health = PLAYER_MAX_HEALTH
                self.player.center_x = TILE_SIZE * 3
                self.player.center_y = TILE_SIZE * 17

    def check_collisions(self):
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
                    self.enemies.remove(enemy)
                    break

        for bullet in player_bullets_to_remove:
            if bullet in self.player.player_bullets:
                self.player.player_bullets.remove(bullet)

    def on_draw(self):
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

        for bullet in self.player.player_bullets:
            bullet.draw()

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

        player_bullets_to_remove = []
        for bullet in self.player.player_bullets:
            bullet.update(delta_time)
            if bullet.should_remove:
                player_bullets_to_remove.append(bullet)
            elif (bullet.center_x < -SCREEN_MARGIN or
                  bullet.center_x > SCREEN_WIDTH + SCREEN_MARGIN or
                  bullet.center_y < -SCREEN_MARGIN or
                  bullet.center_y > SCREEN_HEIGHT + SCREEN_MARGIN):
                player_bullets_to_remove.append(bullet)

        for bullet in player_bullets_to_remove:
            if bullet in self.player.player_bullets:
                self.player.player_bullets.remove(bullet)

        self.on_ladder = self.physics_engine.is_on_ladder()

        movement = self.controls.get_movement()
        left_pressed = movement["left"]
        right_pressed = movement["right"]
        up_pressed = movement["up"]
        down_pressed = movement["down"]

        self.is_running = (left_pressed or right_pressed) and not self.on_ladder
        self.is_climbing = self.on_ladder and (up_pressed or down_pressed)

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
        if key == arcade.key.KEY_1:
            self.player.toggle_weapon()
        else:
            self.controls.on_key_press(key, modifiers)

    def on_key_release(self, key, modifiers):
        self.controls.on_key_release(key, modifiers)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.player.shoot()