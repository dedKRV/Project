import arcade
from core import *


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
        self.animation_entry_sprites = None
        self.animation_layer_sprites = {}
        self.physics_engine = None
        self.on_ladder = False
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.animation_timer = 0
        self.current_animation_frame = 0
        self.animation_layers = ['animation_1', 'animation_2', 'animation_3', 'animation_4']
        self.visible_animation_layer = None
        self.player_health = PLAYER_MAX_HEALTH
        self.damage_cooldown = 0
        self.DAMAGE_COOLDOWN_TIME = 0.5

    def setup(self):
        self.player = arcade.Sprite(
            "assets/sprites/Players/1/1 Biker/Biker_attack1_c/Biker_attack1_1.png",
            scale=1)
        self.player.center_x = TILE_SIZE * 3
        self.player.center_y = TILE_SIZE * 17
        self.player_spritelist = arcade.SpriteList()
        self.player_spritelist.append(self.player)

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
            "animation_entry": {"use_spatial_hash": True},
            "animation_1": {"use_spatial_hash": True},
            "animation_2": {"use_spatial_hash": True},
            "animation_3": {"use_spatial_hash": True},
            "animation_4": {"use_spatial_hash": True},
        }

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
        self.animation_entry_sprites = self.tile_map.sprite_lists.get('animation_entry', arcade.SpriteList())

        for layer_name in self.animation_layers:
            self.animation_layer_sprites[layer_name] = self.tile_map.sprite_lists.get(layer_name, arcade.SpriteList())

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

        damage_2_hit_list = arcade.check_for_collision_with_list(self.player, self.damage_2_list)
        if damage_2_hit_list:
            current_frame_index = self.current_animation_frame + 1
            if current_frame_index in [1, 2, 3, 7, 8]:
                self.apply_damage(DAMAGE_2_LAYER_DAMAGE)

        transportation_hit_list = arcade.check_for_collision_with_list(self.player, self.transportation_list)
        if transportation_hit_list:
            self.player.change_x = TRANSPORTATION_SPEED

    def on_draw(self):
        self.clear()
        background_layers = ['background', 'background_2']
        for layer_name in background_layers:
            if layer_name in self.tile_map.sprite_lists:
                self.tile_map.sprite_lists[layer_name].draw()

        self.walls.draw()
        self.ladders_list.draw()
        self.entry_list.draw()
        self.exit_list.draw()

        if self.animation_entry_sprites:
            self.animation_entry_sprites.draw()

        if self.visible_animation_layer in self.animation_layer_sprites:
            self.animation_layer_sprites[self.visible_animation_layer].draw()

        self.player_spritelist.draw()

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

    def on_update(self, delta_time):
        self.animation_timer += delta_time
        if self.animation_timer >= ANIMATION_FRAME_TIME:
            self.animation_timer = 0
            self.current_animation_frame = (self.current_animation_frame + 1) % len(self.animation_layers)
            self.visible_animation_layer = self.animation_layers[self.current_animation_frame]

        if self.damage_cooldown > 0:
            self.damage_cooldown -= delta_time

        self.on_ladder = self.physics_engine.is_on_ladder()

        if self.on_ladder:
            if self.up_pressed and not self.down_pressed:
                self.player.change_y = LADDER_SPEED
            elif self.down_pressed and not self.up_pressed:
                self.player.change_y = -LADDER_SPEED
            else:
                self.player.change_y = 0

            if self.left_pressed and not self.right_pressed:
                self.player.change_x = -PLAYER_SPEED
            elif self.right_pressed and not self.left_pressed:
                self.player.change_x = PLAYER_SPEED
            else:
                self.player.change_x = 0
        else:
            if self.left_pressed and not self.right_pressed:
                self.player.change_x = -PLAYER_SPEED
            elif self.right_pressed and not self.left_pressed:
                self.player.change_x = PLAYER_SPEED
            else:
                self.player.change_x = 0

        self.check_collisions()
        self.physics_engine.update()

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = True
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = True
        elif key in (arcade.key.UP, arcade.key.W):
            self.up_pressed = True
            if not self.on_ladder and self.physics_engine.can_jump():
                self.player.change_y = PLAYER_JUMP_SPEED
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down_pressed = True

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = False
        elif key in (arcade.key.UP, arcade.key.W):
            self.up_pressed = False
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down_pressed = False