import arcade


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
            self.bullet_texture = "assets/sprites/Players/2/5 Bullets/6"

        elif weapon_type == "punk":
            self.idle_texture = arcade.load_texture("assets/sprites/Players/Guns_Players/Punk/Punk_gun_1.png")
            self.idle_texture_flipped = self.idle_texture.flip_left_right()
            self.shoot_texture = arcade.load_texture(
                "assets/sprites/Players/Guns_Players/Punk/Punk_gun_2.png")
            self.shoot_texture_flipped = self.shoot_texture.flip_left_right()
            self.bullet_texture = "assets/sprites/Players/2/5 Bullets/8"

        elif weapon_type == "cyborg":
            self.idle_texture = arcade.load_texture(
                "assets/sprites/Players/Guns_Players/Cyborg/Cyborg_gun_1.png")
            self.idle_texture_flipped = self.idle_texture.flip_left_right()
            self.shoot_texture = arcade.load_texture(
                "assets/sprites/Players/Guns_Players/Cyborg/Cyborg_gun_2.png")
            self.shoot_texture_flipped = self.shoot_texture.flip_left_right()
            self.bullet_texture = "assets/sprites/Players/2/5 Bullets/10"

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