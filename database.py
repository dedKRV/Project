import sqlite3
from datetime import datetime


class GameDatabase:
    """Управление базой данных игры"""

    def __init__(self, db_file="game_save.db"):
        self.db_file = db_file
        self.conn = None
        self.create_tables()

    def connect(self):
        """Подключение к базе данных"""
        self.conn = sqlite3.connect(self.db_file)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """Закрытие соединения"""
        if self.conn:
            self.conn.close()

    def create_tables(self):
        """Создание таблиц если их нет"""
        conn = self.connect()
        cursor = conn.cursor()

        # Таблица сохранений - теперь с уровнем как частью ключа
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_save (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level_number INTEGER NOT NULL,
                character_skin TEXT NOT NULL,
                weapon INTEGER NOT NULL,
                player_x REAL NOT NULL,
                player_y REAL NOT NULL,
                player_health INTEGER NOT NULL,
                enemies_killed INTEGER DEFAULT 0,
                cards_collected INTEGER DEFAULT 0,
                total_cards INTEGER DEFAULT 0,
                play_time REAL DEFAULT 0.0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(level_number)  -- Уникальный уровень
            )
        ''')

        # Таблица убитых врагов - теперь с привязкой к уровню
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS killed_enemies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level_number INTEGER NOT NULL,
                enemy_index INTEGER NOT NULL,
                FOREIGN KEY (level_number) REFERENCES game_save(level_number)
            )
        ''')

        conn.commit()
        self.close()

    def save_game(self, game_data):
        """Сохранить игру для конкретного уровня"""
        conn = self.connect()
        cursor = conn.cursor()

        # Удаляем старое сохранение для этого уровня
        cursor.execute('DELETE FROM game_save WHERE level_number = ?',
                      (game_data['level_number'],))
        cursor.execute('DELETE FROM killed_enemies WHERE level_number = ?',
                      (game_data['level_number'],))

        # Создаём новое сохранение для уровня
        cursor.execute('''
            INSERT INTO game_save 
            (level_number, character_skin, weapon, player_x, player_y, 
             player_health, enemies_killed, cards_collected, total_cards, play_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            game_data['level_number'],
            game_data['character_skin'],
            game_data['weapon'],
            game_data['player_x'],
            game_data['player_y'],
            game_data['player_health'],
            game_data['enemies_killed'],
            game_data['cards_collected'],
            game_data['total_cards'],
            game_data['play_time']
        ))

        # Сохраняем индексы убитых врагов для этого уровня
        if 'killed_enemy_indices' in game_data:
            for enemy_index in game_data['killed_enemy_indices']:
                cursor.execute('''
                    INSERT INTO killed_enemies (level_number, enemy_index)
                    VALUES (?, ?)
                ''', (game_data['level_number'], enemy_index))

        conn.commit()
        self.close()
        print(f"Игра сохранена для уровня {game_data['level_number']}!")
        return 1

    def load_game(self, level_number):
        """Загрузить сохранение для конкретного уровня"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM game_save WHERE level_number = ?', (level_number,))
        save = cursor.fetchone()

        if not save:
            self.close()
            return None

        # Получаем индексы убитых врагов для этого уровня
        cursor.execute('SELECT enemy_index FROM killed_enemies WHERE level_number = ?',
                      (level_number,))
        killed_enemies = [row['enemy_index'] for row in cursor.fetchall()]

        self.close()

        return {
            'level_number': save['level_number'],
            'character_skin': save['character_skin'],
            'weapon': save['weapon'],
            'player_x': save['player_x'],
            'player_y': save['player_y'],
            'player_health': save['player_health'],
            'enemies_killed': save['enemies_killed'],
            'cards_collected': save['cards_collected'],
            'total_cards': save['total_cards'],
            'play_time': save['play_time'],
            'killed_enemy_indices': killed_enemies
        }

    def has_save_for_level(self, level_number):
        """Проверить есть ли сохранение для конкретного уровня"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) as count FROM game_save WHERE level_number = ?',
                      (level_number,))
        result = cursor.fetchone()

        self.close()
        return result['count'] > 0

    def delete_save_for_level(self, level_number):
        """Удалить сохранение для конкретного уровня"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM game_save WHERE level_number = ?', (level_number,))
        cursor.execute('DELETE FROM killed_enemies WHERE level_number = ?', (level_number,))
        conn.commit()
        self.close()