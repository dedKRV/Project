import arcade
from core import *
from player_config import select_player
from weapon import Weapon, PlayerBullet


class Player(arcade.Sprite):
    def __init__(self, character_type=None):
        """Создание игрока"""
        if character_type is None:
            character_type = select_player()
        self.character_type = character_type

        self.weapon = Weapon(self.character_type)
        self.weapon.activate()
        self.is_armed = True

        idle_texture = self.weapon.get_current_texture()
        super().__init__(idle_texture, scale=1)

        self.center_x = TILE_SIZE * 3
        self.center_y = TILE_SIZE * 17
        self.textures = []
        self.current_texture = 0
        self.animation_timer = 0
        self.jump_animation_timer = 0
        self.facing_direction = 1

        self.run_textures = []
        self.run_textures_flipped = []
        self.jump_textures = []
        self.jump_textures_flipped = []
        self.climb_textures = []
        self.climb_textures_flipped = []

        self.player_bullets = arcade.SpriteList()  # Теперь это SpriteList

        self.load_textures()

        self.change_x = 0
        self.change_y = 0
        self.is_jumping_animation = False
        self.jump_animation_frame = 0

    def load_textures(self):
        """Загрузка текстур для анимаций"""
        if self.character_type == "biker":
            for i in range(1, 7):
                run_texture = arcade.load_texture(f"assets/sprites/Players/1/1 Biker/Biker_run_c/Biker_run_{i}.png")
                self.run_textures.append(run_texture)
                run_texture_flipped = run_texture.flip_left_right()
                self.run_textures_flipped.append(run_texture_flipped)

                jump_texture = arcade.load_texture(
                    f"assets/sprites/Players/1/1 Biker/Biker_doublejump_c/Biker_doublejump_{i}.png")
                self.jump_textures.append(jump_texture)
                jump_texture_flipped = jump_texture.flip_left_right()
                self.jump_textures_flipped.append(jump_texture_flipped)

                climb_texture = arcade.load_texture(
                    f"assets/sprites/Players/1/1 Biker/Biker_climb_c/Biker_climb_{i}.png")
                self.climb_textures.append(climb_texture)
                climb_texture_flipped = climb_texture.flip_left_right()
                self.climb_textures_flipped.append(climb_texture_flipped)

        elif self.character_type == "punk":
            for i in range(1, 7):
                run_texture = arcade.load_texture(f"assets/sprites/Players/1/2 Punk/Punk_run_c/Punk_run_{i}.png")
                self.run_textures.append(run_texture)
                run_texture_flipped = run_texture.flip_left_right()
                self.run_textures_flipped.append(run_texture_flipped)

                jump_texture = arcade.load_texture(
                    f"assets/sprites/Players/1/2 Punk/Punk_doublejump_c/Punk_doublejump_{i}.png")
                self.jump_textures.append(jump_texture)
                jump_texture_flipped = jump_texture.flip_left_right()
                self.jump_textures_flipped.append(jump_texture_flipped)

                climb_texture = arcade.load_texture(f"assets/sprites/Players/1/2 Punk/Punk_climb_c/Punk_climb_{i}.png")
                self.climb_textures.append(climb_texture)
                climb_texture_flipped = climb_texture.flip_left_right()
                self.climb_textures_flipped.append(climb_texture_flipped)

        elif self.character_type == "cyborg":
            for i in range(1, 7):
                run_texture = arcade.load_texture(f"assets/sprites/Players/1/3 Cyborg/Cyborg_run_c/Cyborg_run_{i}.png")
                self.run_textures.append(run_texture)
                run_texture_flipped = run_texture.flip_left_right()
                self.run_textures_flipped.append(run_texture_flipped)

                jump_texture = arcade.load_texture(
                    f"assets/sprites/Players/1/3 Cyborg/Cyborg_doublejump_c/Cyborg_doublejump_{i}.png")
                self.jump_textures.append(jump_texture)
                jump_texture_flipped = jump_texture.flip_left_right()
                self.jump_textures_flipped.append(jump_texture_flipped)

                climb_texture = arcade.load_texture(
                    f"assets/sprites/Players/1/3 Cyborg/Cyborg_climb_c/Cyborg_climb_{i}.png")
                self.climb_textures.append(climb_texture)
                climb_texture_flipped = climb_texture.flip_left_right()
                self.climb_textures_flipped.append(climb_texture_flipped)

    def set_weapon_texture(self):
        """Установить текстуру оружия"""
        weapon_texture = self.weapon.get_current_texture()
        if weapon_texture:
            self.texture = weapon_texture

    def set_run_texture(self):
        """Установить текстуры для бега"""
        if self.facing_direction < 0:
            self.textures = self.run_textures_flipped
        else:
            self.textures = self.run_textures
        self.current_texture = 0
        self.set_texture(self.current_texture)

    def set_jump_texture(self):
        """Установить текстуры для прыжка"""
        if self.facing_direction < 0:
            self.textures = self.jump_textures_flipped
        else:
            self.textures = self.jump_textures
        self.current_texture = 0
        self.set_texture(self.current_texture)

    def set_climb_texture(self):
        """Установить текстуры для лазания"""
        if self.facing_direction < 0:
            self.textures = self.climb_textures_flipped
        else:
            self.textures = self.climb_textures
        self.current_texture = 0
        self.set_texture(self.current_texture)

    def start_jump_animation(self):
        """Начать анимацию прыжка"""
        self.is_jumping_animation = True
        self.jump_animation_timer = 0
        self.jump_animation_frame = 0
        self.set_jump_texture()

    def toggle_weapon(self):
        """Переключить оружие (вкл/выкл)"""
        self.is_armed = not self.is_armed
        if self.is_armed:
            self.weapon.activate()
        else:
            self.weapon.deactivate()

    def shoot(self):
        """Произвести выстрел из оружия"""
        if self.is_armed and not self.weapon.is_shooting:
            self.weapon.shoot()

            bullet = PlayerBullet(self.character_type)
            bullet.center_x = self.center_x
            bullet.center_y = self.center_y
            bullet.change_x = self.facing_direction * PLAYER_BULLET_SPEED
            bullet.change_y = 0

            self.player_bullets.append(bullet)
            return bullet

    def update_animation(self, delta_time, is_running=False, is_jumping=False, is_climbing=False, is_on_ladder=False,
                         left_pressed=False, right_pressed=False):
        """Обновление анимации игрока"""
        self.animation_timer += delta_time

        if left_pressed:
            self.facing_direction = -1
        elif right_pressed:
            self.facing_direction = 1

        self.weapon.update(delta_time, self.facing_direction)

        if self.is_jumping_animation:
            self.jump_animation_timer += delta_time
            if self.jump_animation_timer >= JUMP_ANIMATION_SPEED:
                self.jump_animation_timer = 0
                self.jump_animation_frame += 1
                if self.jump_animation_frame < len(self.textures):
                    self.set_texture(self.jump_animation_frame)
                else:
                    self.is_jumping_animation = False
                    self.set_weapon_texture()
        elif is_climbing or is_on_ladder:
            if not self.textures is self.climb_textures and not self.textures is self.climb_textures_flipped:
                self.set_climb_texture()
            if self.animation_timer >= ANIMATION_FRAME_TIME:
                self.animation_timer = 0
                self.current_texture = (self.current_texture + 1) % len(self.textures)
                self.set_texture(self.current_texture)
        elif is_running:
            if (not self.textures is self.run_textures and not self.textures is self.run_textures_flipped) or \
                    (self.facing_direction < 0 and self.textures is self.run_textures) or \
                    (self.facing_direction >= 0 and self.textures is self.run_textures_flipped):
                self.set_run_texture()
            if self.animation_timer >= ANIMATION_FRAME_TIME:
                self.animation_timer = 0
                self.current_texture = (self.current_texture + 1) % len(self.textures)
                self.set_texture(self.current_texture)
        else:
            self.set_weapon_texture()