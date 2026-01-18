import arcade
import math
from core import *


class Enemy(arcade.Sprite):
    def __init__(self, x, y, attack_cooldown=ENEMY_SHOOT_COOLDOWN, damage=10, y_offset=10, health=ENEMY_MAX_HEALTH,
                 texture="assets/sprites/Enemies/2/Attack_c/Attack_1.png", scale=1):
        """Создание врага"""
        super().__init__(texture, scale=scale)
        self.center_x = x
        self.center_y = y + y_offset
        self.attack_range = 400
        self.attack_cooldown = attack_cooldown
        self.current_cooldown = 0
        self.bullets = []
        self.damage = damage
        self.health = health  # НОВОЕ: здоровье врага

    def update(self, player, delta_time, walls):
        """Обновление логики врага"""
        if self.current_cooldown > 0:
            self.current_cooldown -= delta_time

        distance = arcade.get_distance_between_sprites(self, player)

        if distance < self.attack_range and self.current_cooldown <= 0:
            self.shoot(player)
            self.current_cooldown = self.attack_cooldown

    def take_damage(self, damage):
        """Получение урона врагом"""
        self.health -= damage
        if self.health <= 0:
            return True  # враг мертв
        return False  # враг жив

    def shoot(self, player):
        """Стрельба в игрока"""
        bullet = Bullet(self.damage)
        bullet.center_x = self.center_x
        bullet.center_y = self.center_y

        dx = player.center_x - self.center_x
        dy = player.center_y - self.center_y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance > 0:
            bullet.change_x = (dx / distance) * BULLET_SPEED
            bullet.change_y = (dy / distance) * BULLET_SPEED

        self.bullets.append(bullet)
        return bullet


class Bullet(arcade.Sprite):
    def __init__(self, damage, texture="assets/sprites/Enemies/2/Projectile_c/Projectile_1.png", scale=0.5):
        """Создание пули врага"""
        super().__init__(texture, scale=scale)
        self.speed = BULLET_SPEED
        self.damage = damage
        self.lifetime = BULLET_LIFETIME
        self.current_lifetime = 0
        self.should_remove = False

    def update(self, delta_time):
        """Обновление пули"""
        super().update()
        self.current_lifetime += delta_time

        if self.current_lifetime >= self.lifetime:
            self.should_remove = True


class Card(arcade.Sprite):
    def __init__(self, x, y):
        """Создание коллекционной карты"""
        super().__init__("assets/sprites/Items/Card_c/Card_1.png", scale=1)
        self.center_x = x * TILE_SIZE * TILE_SCALING + TILE_SIZE * TILE_SCALING / 2
        self.center_y = y * TILE_SIZE * TILE_SCALING + TILE_SIZE * TILE_SCALING / 2
        self.animation_timer = 0
        self.current_frame = 0
        self.frames = [
            "assets/sprites/Items/Card_c/Card_1.png",
            "assets/sprites/Items/Card_c/Card_2.png",
            "assets/sprites/Items/Card_c/Card_3.png",
            "assets/sprites/Items/Card_c/Card_4.png",
            "assets/sprites/Items/Card_c/Card_5.png",
            "assets/sprites/Items/Card_c/Card_6.png",
            "assets/sprites/Items/Card_c/Card_7.png",
            "assets/sprites/Items/Card_c/Card_8.png",
        ]

    def update(self, delta_time):
        """Обновление анимации карты"""
        self.animation_timer += delta_time
        if self.animation_timer >= COLLECTIBLE_ANIMATION_SPEED:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.texture = arcade.load_texture(self.frames[self.current_frame])