from base_level import BaseLevel
from enemy_config import LEVEL_4_ENEMIES, LEVEL_4_SPAWN, LEVEL_4_CARDS


class GameWindow4(BaseLevel):
    """Уровень 4"""

    def get_level_number(self):
        """Номер уровня"""
        return 4

    def get_tilemap_path(self):
        """Путь к тайлмапу уровня 4"""
        return "data/level_4.tmx"

    def get_spawn_position(self):
        """Позиция спавна игрока"""
        return LEVEL_4_SPAWN

    def get_enemy_config(self):
        """Конфигурация врагов"""
        return LEVEL_4_ENEMIES

    def get_cards_config(self):
        """Конфигурация карт"""
        return LEVEL_4_CARDS
