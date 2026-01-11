import arcade
from core import *

class Player(arcade.Sprite):
    def __init__(self):
        super().__init__(
            "assets/sprites/Players/1/1 Biker/Biker_attack1_c/Biker_attack1_1.png",
            scale=1
        )