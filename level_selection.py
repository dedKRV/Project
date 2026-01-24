import arcade
from core import *
from config_gun import get_level_choice
from level_1 import GameWindow as Level1Class


def get_game_window_class():
    """Получить класс окна игры в зависимости от выбранного уровня"""
    level = get_level_choice()

    if level == 1:
        return Level1Class
    elif level == 2:
        from level_2 import GameWindow2
        return GameWindow2
    else:
        return Level1Class