import pygame
import sys

from ui.entity_design.EntityDesign import EntityBody, EntityButton, EntityMenu
from ui.views.Views import HomeView, BuildView

class GameManager:
    def __init__(self):
        self.view = HomeView(self)

        self.game_name = None
        self.file_path = None

        self._entity_manager = EntityManager(self.view.ui_manager)

    def run(self):
        self.view.run()

    def new_game(self):
        self.clear_entities()
        self.view.ui_manager.clear_and_reset()
        self.view = BuildView(self)
        
        self.add_entity()

        self.view.run()

    def open_game(self):
        pass

    def save_game(self):
        pass

    def compile(self):
        pass

    def quit(self):
        pygame.quit()
        sys.exit()

    def add_entity(self, parent=None):
        self._entity_manager.add_entity(parent)

    def remove_entity(self, entity):
        self._entity_manager.remove_entity(entity)

    def update_entities(self, entities):
        self._entity_manager.update_entities(entities)

    def get_entities(self):
        return self._entity_manager.entities
    
    def clear_entities(self):
        return self._entity_manager.clear_entities()

class EntityManager:
    def __init__(self, ui_manager, entities=[]):
        self.entities = entities
        self.depth = 0
        self.ui_manager = ui_manager

    def add_entity(self, parent=None):
        entity = None
        if parent:
            depth = parent.depth + 1
            x = parent.x
            y = parent.y + parent.height + 50
            entity = Entity(len(self.entities), x, y, 75, 75, self.ui_manager, depth=depth)
            parent.add_option(entity)
        else:
            entity = Entity(len(self.entities), self.ui_manager.window_resolution[0]//2-75, self.ui_manager.window_resolution[1]//2-75, 75, 75, self.ui_manager)

        self.entities.append(entity)

    def remove_entity(self, entity):
        self.entities.remove(entity) 

    def update_entities(self, entities):
        self.entities = entities

    def clear_entities(self):
        self.entities = []
        self.depth = 0

class Entity:
    def __init__(self, id, x, y, width, height, ui_manager, depth=0, name="", text="", notes="", media=""):
        self.id = id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.depth = depth
        self.name = "Node {}".format(id) if name == "" else name
        self.text = text
        self.notes = notes
        self.media = media
        self.ui_manager = ui_manager

        self.options = []

        self.centroid = (self.x + self.width//2, self.y + self.height//2)

        self.hovered = False

        self.body = EntityBody(x, y, width, height)
        self.button_add = EntityButton(x + width, y, width//5, height//5, "+")
        if (depth != 0):
            self.button_remove = EntityButton(x + width, y + height//5 + 2, width//5, height//5, "-")
        self.buttons = [self.button_add, self.button_remove] if depth != 0 else [self.button_add]

    def draw(self, screen):
        for option in self.options:
            pygame.draw.aaline(screen, (0, 0, 0), self.centroid, option.entity.centroid)

        self.body.draw(screen)

        font = pygame.font.Font(None, 24)
        text_surface = font.render(self.name, True, (0, 0, 0))
        text_rect = pygame.Rect(self.body.x + self.body.width//2 - 25, self.body.y + self.body.height//2 - 55, 24, 75)
        screen.blit(text_surface, text_rect)

        
        if self.hovered:
            for button in self.buttons:
                button.draw(screen)

    def move(self, dx, dy):
        self.set_position(self.x + dx, self.y + dy)

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.body.x = x
        self.body.y = y

        self.body.rect.x = x
        self.body.rect.y = y

        self.button_add.x = x + self.width
        self.button_add.y = y

        self.button_add.rect.x = x + self.width
        self.button_add.rect.y = y

        if self.depth != 0:
            self.button_remove.x = x + self.width
            self.button_remove.y = y + self.height//5 + 2

            self.button_remove.rect.x = x + self.width
            self.button_remove.rect.y = y + self.height//5 + 2

        self.centroid = (self.x + self.width//2, self.y + self.height//2)

    def add_option(self, entity):
        self.options.append(Option("", entity))

    def remove_option(self, entity):
        for option in self.options:
            if option.entity.id == entity.id:
                self.options.remove(option)

    def update_properties(self, name=None, text=None, notes=None):
        self.name = name if name else self.name
        self.text = text if text else self.text
        self.notes = notes if notes else self.notes

    def update_media(self, media):
        self.media = media

    def open_menu(self):
        EntityMenu(self.ui_manager, self)

    def was_body_clicked(self, x, y):
        return self.body.rect.collidepoint(x, y)

    def was_button_clicked(self, x, y):
        return self.buttons[0].rect.collidepoint(x, y)
    
class Option:
    def __init__(self, text, entity):
        self.text = text
        self.entity = entity

class PositionManager:
    def __init__(self):
        self.radius = 50
        self.positions = []

    def get_position(parent, entity):
        # Returns the position of the entity relative to the parent
        pass