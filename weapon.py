import arcade
from core import PLAYER_BULLET_SPEED, PLAYER_BULLET_LIFETIME
from choice import get_gun_choice


class Weapon:
    def __init__(self, weapon_type=None, player_type="biker"):
        if weapon_type is None:
            weapon_type = get_gun_choice()

        self.weapon_type = weapon_type
        self.player_type = player_type

        self.idle_texture = None
        self.idle_texture_flipped = None
        self.shoot_texture = None
        self.shoot_texture_flipped = None

        self.is_active = False
        self.is_shooting = False
        self.facing_direction = 1
        self.shoot_timer = 0

        self.load_textures()

    def load_textures(self):
        """Загрузка текстур оружия"""
        base_path = "assets/sprites/Players/Guns_Players/"

        if self.player_type == "biker":
            if self.weapon_type == "1":
                self.idle_texture = arcade.load_texture(f"{base_path}Biker_gun_1/Biker_gun_1.png")
                self.shoot_texture = arcade.load_texture(f"{base_path}Biker_gun_1/Biker_gun_2.png")
            elif self.weapon_type == "2":
                self.idle_texture = arcade.load_texture(f"{base_path}Biker_gun_2/Biker_gun_1.png")
                self.shoot_texture = arcade.load_texture(f"{base_path}Biker_gun_2/Biker_gun_2.png")
            elif self.weapon_type == "3":
                self.idle_texture = arcade.load_texture(f"{base_path}Biker_gun_3/Biker_gun_1.png")
                self.shoot_texture = arcade.load_texture(f"{base_path}Biker_gun_3/Biker_gun_2.png")

        elif self.player_type == "punk":
            if self.weapon_type == "1":
                self.idle_texture = arcade.load_texture(f"{base_path}Punk_gun_1/Punk_gun_1.png")
                self.shoot_texture = arcade.load_texture(f"{base_path}Punk_gun_1/Punk_gun_2.png")
            elif self.weapon_type == "2":
                self.idle_texture = arcade.load_texture(f"{base_path}Punk_gun_2/Punk_gun_1.png")
                self.shoot_texture = arcade.load_texture(f"{base_path}Punk_gun_2/Punk_gun_2.png")
            elif self.weapon_type == "3":
                self.idle_texture = arcade.load_texture(f"{base_path}Punk_gun_3/Punk_gun_1.png")
                self.shoot_texture = arcade.load_texture(f"{base_path}Punk_gun_3/Punk_gun_2.png")

        elif self.player_type == "cyborg":
            if self.weapon_type == "1":
                self.idle_texture = arcade.load_texture(f"{base_path}Cyborg_gun_1/Cyborg_gun_1.png")
                self.shoot_texture = arcade.load_texture(f"{base_path}Cyborg_gun_1/Cyborg_gun_2.png")
            elif self.weapon_type == "2":
                self.idle_texture = arcade.load_texture(f"{base_path}Cyborg_gun_2/Cyborg_gun_1.png")
                self.shoot_texture = arcade.load_texture(f"{base_path}Cyborg_gun_2/Cyborg_gun_2.png")
            elif self.weapon_type == "3":
                self.idle_texture = arcade.load_texture(f"{base_path}Cyborg_gun_3/Cyborg_gun_1.png")
                self.shoot_texture = arcade.load_texture(f"{base_path}Cyborg_gun_3/Cyborg_gun_2.png")

        if self.idle_texture:
            self.idle_texture_flipped = self.idle_texture.flip_left_right()
        if self.shoot_texture:
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
            if self.shoot_timer >= 0.1:
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