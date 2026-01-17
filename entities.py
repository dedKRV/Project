import arcade
from core import *
from player_config import select_player


class Weapon:
    def __init__(self, weapon_type="biker"):
        self.weapon_type = weapon_type
        self.idle_texture = None
        self.idle_texture_flipped = None
        self.shoot_texture = None
        self.shoot_texture_flipped = None
        self.is_active = False
        self.is_shooting = False
        self.facing_direction = 1
        self.shoot_timer = 0

        if weapon_type == "biker":
            self.idle_texture = arcade.load_texture(
                "assets/sprites/Players/Guns_Players/Biker/Biker_gun_1.png")
            self.idle_texture_flipped = self.idle_texture.flip_left_right()
            self.shoot_texture = arcade.load_texture(
                "assets/sprites/Players/Guns_Players/Biker/Biker_gun_2.png")
            self.shoot_texture_flipped = self.shoot_texture.flip_left_right()

        elif weapon_type == "punk":
            self.idle_texture = arcade.load_texture("assets/sprites/Players/Guns_Players/Punk/Punk_gun_1.png")
            self.idle_texture_flipped = self.idle_texture.flip_left_right()
            self.shoot_texture = arcade.load_texture(
                "assets/sprites/Players/Guns_Players/Punk/Punk_gun_2.png")
            self.shoot_texture_flipped = self.shoot_texture.flip_left_right()

        elif weapon_type == "cyborg":
            self.idle_texture = arcade.load_texture(
                "assets/sprites/Players/Guns_Players/Cyborg/Cyborg_gun_1.png")
            self.idle_texture_flipped = self.idle_texture.flip_left_right()
            self.shoot_texture = arcade.load_texture(
                "assets/sprites/Players/Guns_Players/Cyborg/Cyborg_gun_2.png")
            self.shoot_texture_flipped = self.shoot_texture.flip_left_right()

    def activate(self):
        self.is_active = True
        self.is_shooting = False

    def deactivate(self):
        self.is_active = False
        self.is_shooting = False

    def shoot(self):
        if self.is_active:
            self.is_shooting = True
            self.shoot_timer = 0

    def update(self, delta_time, facing_direction):
        self.facing_direction = facing_direction

        if self.is_shooting:
            self.shoot_timer += delta_time
            if self.shoot_timer >= 0.5:
                self.is_shooting = False
                self.shoot_timer = 0

    def get_current_texture(self):
        if not self.is_active:
            return None

        if self.is_shooting:
            if self.facing_direction < 0:
                return self.shoot_texture_flipped
            else:
                return self.shoot_texture
        else:
            if self.facing_direction < 0:
                return self.idle_texture_flipped
            else:
                return self.idle_texture


class PlayerBullet(arcade.Sprite):
    def __init__(self, character_type, scale=0.5):
        if character_type == "biker":
            texture_path = "assets/sprites/Players/2/5 Bullets/6.png"
            damage = 10
        elif character_type == "punk":
            texture_path = "assets/sprites/Players/2/5 Bullets/8.png"
            damage = 15
        elif character_type == "cyborg":
            texture_path = "assets/sprites/Players/2/5 Bullets/10.png"
            damage = 20

        super().__init__(texture_path, scale=scale)
        self.speed = PLAYER_BULLET_SPEED
        self.damage = damage
        self.lifetime = PLAYER_BULLET_LIFETIME
        self.current_lifetime = 0
        self.should_remove = False

    def update(self, delta_time):
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.current_lifetime += delta_time

        if self.current_lifetime >= self.lifetime:
            self.should_remove = True


class Player(arcade.Sprite):
    def __init__(self, character_type=None):
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

        self.player_bullets = []

        self.load_textures()

        self.change_x = 0
        self.change_y = 0
        self.is_jumping_animation = False
        self.jump_animation_frame = 0

    def load_textures(self):
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
        weapon_texture = self.weapon.get_current_texture()
        if weapon_texture:
            self.texture = weapon_texture

    def set_run_texture(self):
        if self.facing_direction < 0:
            self.textures = self.run_textures_flipped
        else:
            self.textures = self.run_textures
        self.current_texture = 0
        self.set_texture(self.current_texture)

    def set_jump_texture(self):
        if self.facing_direction < 0:
            self.textures = self.jump_textures_flipped
        else:
            self.textures = self.jump_textures
        self.current_texture = 0
        self.set_texture(self.current_texture)

    def set_climb_texture(self):
        if self.facing_direction < 0:
            self.textures = self.climb_textures_flipped
        else:
            self.textures = self.climb_textures
        self.current_texture = 0
        self.set_texture(self.current_texture)

    def start_jump_animation(self):
        self.is_jumping_animation = True
        self.jump_animation_timer = 0
        self.jump_animation_frame = 0
        self.set_jump_texture()

    def toggle_weapon(self):
        self.is_armed = not self.is_armed
        if self.is_armed:
            self.weapon.activate()
        else:
            self.weapon.deactivate()

    def shoot(self):
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