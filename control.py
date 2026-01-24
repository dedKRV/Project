import arcade


class Controls:
    def __init__(self):
        """Инициализация управления"""
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.shoot_pressed = False
        self.pause_pressed = False  # Добавили флаг паузы

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиши"""
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = True
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = True
        elif key in (arcade.key.UP, arcade.key.W):
            self.up_pressed = True
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down_pressed = True
        elif key == arcade.key.ESCAPE:  # Добавили ESC
            self.pause_pressed = True

    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиши"""
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = False
        elif key in (arcade.key.UP, arcade.key.W):
            self.up_pressed = False
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down_pressed = False
        elif key == arcade.key.ESCAPE:  # Добавили ESC
            self.pause_pressed = False

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка нажатия кнопки мыши"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.shoot_pressed = True

    def on_mouse_release(self, x, y, button, modifiers):
        """Обработка отпускания кнопки мыши"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.shoot_pressed = False

    def get_movement(self):
        """Получить текущее состояние управления"""
        return {
            "left": self.left_pressed,
            "right": self.right_pressed,
            "up": self.up_pressed,
            "down": self.down_pressed
        }

    def get_shooting(self):
        """Получить состояние стрельбы"""
        return self.shoot_pressed

    def get_pause(self):
        """Получить состояние паузы"""
        return self.pause_pressed

    def reset_pause(self):
        """Сбросить флаг паузы"""
        self.pause_pressed = False