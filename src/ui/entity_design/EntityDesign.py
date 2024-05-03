import pygame
import pygame_gui
from pygame_gui.elements import *

class EntityBody:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, screen):
        pygame.draw.rect(screen, (215, 215, 215), self.rect, border_radius=12)

class EntityButton:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, screen):
        colour = (0, 255, 0) if self.text == "+" else (255, 0, 0)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, border_radius=24)
        font = pygame.font.Font(None, 24)
        text_surface = font.render(self.text, True, colour)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class EntityMenu(UIWindow):
    def __init__(self, ui_manager, entity):
        super().__init__(pygame.Rect((50, 50), (224, 224)), ui_manager,
                         window_display_title='Entity Menu',
                         object_id='#entity_menu',
                         resizable=False)
        
        self.entity = entity
        UILabel(relative_rect=pygame.Rect((10, 10), (100, 20)), text=f"X: {self.entity.x}", manager=self.ui_manager, container=self)
        UILabel(relative_rect=pygame.Rect((10, 30), (100, 20)), text=f"Y: {self.entity.y}", manager=self.ui_manager, container=self)