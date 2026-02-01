import arcade
from core import *


def get_game_window_class(level_number=None):
    """Получить класс окна игры в зависимости от номера уровня"""
    if level_number is None:
        from choice import get_level_choice
        level_number = get_level_choice()

    if level_number == 1:
        from level_1 import GameWindow as Level1Class
        return Level1Class
    elif level_number == 2:
        from level_2 import GameWindow2
        return GameWindow2
    elif level_number == 3:
        from level_3 import GameWindow3
        return GameWindow3
    elif level_number == 4:
        from level_4 import GameWindow4
        return GameWindow4
    else:
        from level_1 import GameWindow as Level1Class
        return Level1Class


def create_next_level_window(current_level, width, height, title):
    """Создать окно следующего уровня"""
    next_level = current_level + 1

    if next_level == 2:
        from level_2 import GameWindow2
        return GameWindow2(width, height, title)
    elif next_level == 3:
        from level_3 import GameWindow3
        return GameWindow3(width, height, title)
    elif next_level == 4:
        from level_4 import GameWindow4
        return GameWindow4(width, height, title)
    else:
        return None