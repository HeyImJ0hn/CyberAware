import pygame
import pygame_gui
from model.Model import GameManager

if __name__ == "__main__":
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE | pygame.SRCALPHA)
    ui_manager = pygame_gui.UIManager((WIDTH, HEIGHT), 'theme.json')

    view = GameManager(screen, ui_manager, (WIDTH, HEIGHT))
    view.run()