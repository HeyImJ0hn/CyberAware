import pygame
import pygame_gui
from pygame_gui.elements import *
from pygame_gui.core import ObjectID

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
        super().__init__(pygame.Rect((entity.x + entity.width + 25, entity.y - entity.height), (224, 224)), ui_manager,
                         window_display_title='Entity Menu',
                         object_id='#entity_menu',
                         resizable=False)
        self.entity = entity

        self.namme_label = UILabel(relative_rect=pygame.Rect((10, 10), (60, 20)), text="Name", manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@entity_menu_label', object_id='#name_label'))
        self.name = UITextEntryLine(relative_rect=pygame.Rect((80, 10), (100, 20)), manager=self.ui_manager, container=self, initial_text=entity.name, object_id=ObjectID(class_id='@entity_menu_input', object_id='#name_input'))

        UILabel(relative_rect=pygame.Rect((10, 40), (60, 20)), text="Media", manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@entity_menu_label', object_id='#media_label'))
        self.media = UITextEntryLine(relative_rect=pygame.Rect((80, 40), (100, 20)), manager=self.ui_manager, container=self, initial_text=entity.media, object_id=ObjectID(class_id='@entity_menu_input', object_id='#media_input'))

        UILabel(relative_rect=pygame.Rect((10, 70), (60, 20)), text="Text", manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@entity_menu_label', object_id='#text_label'))
        self.text = UITextEntryLine(relative_rect=pygame.Rect((80, 70), (100, 20)), manager=self.ui_manager, container=self, initial_text=entity.text, object_id=ObjectID(class_id='@entity_menu_input', object_id='#text_input'))

        UILabel(relative_rect=pygame.Rect((10, 100), (60, 20)), text="Notes", manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@entity_menu_label', object_id='#notes_label'))
        self.notes = UITextEntryBox(relative_rect=pygame.Rect((80, 100), (100, 60)), manager=self.ui_manager, container=self, initial_text=entity.notes, object_id=ObjectID(class_id='@entity_menu_input', object_id='#notes_input'))

        options = entity.options
        if len(options) > 0:
            UILabel(relative_rect=pygame.Rect((10, 170), (60, 20)), text="Options", manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@entity_menu_label', object_id='#options_label'))
            for i, option in enumerate(options):
                UILabel(relative_rect=pygame.Rect((10, 170 + 20*(i+1)), (60, 20)), text=option.entity.name, manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@entity_option_name', object_id='#option_name_label'))
                UITextEntryLine(relative_rect=pygame.Rect((80, 170 + 20*(i+1)), (60, 20)), manager=self.ui_manager, container=self, placeholder_text="Texto", object_id=ObjectID(class_id='@entity_option_input', object_id='#option_text_input'))
        
    def move(self, dx, dy):
        self.set_position((self.rect.x + dx, self.rect.y + dy))