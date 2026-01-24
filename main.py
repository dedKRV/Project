import arcade
import pygame
from utils import Game


def main():
    try:
        window = Game()
        window.set_fullscreen(False)
        window.setup()
        arcade.run()
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
