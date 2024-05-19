import pygame
import sys
import math

from ui.design.EntityDesign import EntityBody, EntityButton, EntityMenu
from ui.views.Views import HomeView, BuildView
from dao.FileDAO import FileDAO
from conv.JSONConverter import JSONConverter
from config.Settings import Settings

class GameManager:
    def __init__(self):
        pygame.init()

        self.json_converter = JSONConverter()
        self.json_converter.settings_from_json()

        if Settings.FIRST_RUN:
            Settings.FIRST_RUN = False
            self.save_settings()
        
        self.view = HomeView(self)

        self.game_name = ""
        self.path = None

        self._entity_manager = EntityManager(self.view.ui_manager)

    def run(self):
        self.view.run()

    def new_game(self):
        self.file_name = self.game_to_file_name(self.game_name)
        self.path = FileDAO.create_absolute_path(self.path, self.file_name)

        self.view = BuildView(self)
        
        self.clear_entities()

        self.add_entity()

        self._entity_manager.update_ui_manager(self.view.ui_manager)

        self.view.run()

    def load_game(self, path):
        self.game_name, entities = self.json_converter.game_from_json(self, path)
        self.path = path
        self._entity_manager.update_entities(entities)

    def open_game(self, path):
        self.load_game(path)
        self.view = BuildView(self)
        self._entity_manager.update_ui_manager(self.view.ui_manager)
        self.view.run()

    def save_game(self):
        json = self.json_converter.game_to_json(self)
        FileDAO.save(json, self.path)

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
    
    def update_resolution(self, resolution):
        self.resolution = resolution

    def game_to_file_name(self, game_name):
        return game_name.replace(" ", "_").lower() + ".json"
    
    def create_entity(self):
        return self._entity_manager.create_entity()
    
    def create_option(self, text, entity):
        return self._entity_manager.create_option(text, entity)
    
    def save_settings(self):
        self.json_converter.settings_to_json()

    def submit_media(self, media, entity):
        FileDAO.copy_media(media, self.game_to_file_name(self.game_name).split(".")[0])
        entity.update_media(media)

class EntityManager:
    def __init__(self, ui_manager, entities=[]):
        self.entities = entities
        self.ui_manager = ui_manager

    def add_entity(self, parent=None):
        entity = None
        if parent:
            depth = parent.depth + 1
            entity = Entity(len(self.entities), 0, 0, 75, 75, self.ui_manager, depth=depth)
            PositionManager().set_position(parent, entity, self.entities)
            parent.add_option(entity)
        else:
            entity = Entity(len(self.entities), self.ui_manager.window_resolution[0]/2-75/2, self.ui_manager.window_resolution[1]/2-75/2, 75, 75, self.ui_manager)

        self.entities.append(entity)

    def remove_entity(self, entity):
        self.entities.remove(entity) 

    def update_entities(self, entities):
        self.entities = entities

        self.fix_entities()

    def clear_entities(self):
        self.entities = []

    def get_entity_by_id(self, id):
        for entity in self.entities:
            if entity.id == id:
                return entity
        return None
    
    def create_entity(self):
        return Entity(len(self.entities), 0, 0, 75, 75, self.ui_manager, depth=1)
    
    def create_option(self, text, entity):
        return Option(text, entity)
    
    def fix_entities(self):
        for e in self.entities:
            e.create_extra_buttons()
            for o in e.options:
                id = o.entity
                o.entity = self.get_entity_by_id(id)

    def update_ui_manager(self, ui_manager):
        self.ui_manager = ui_manager
        for entity in self.entities:
            entity.ui_manager = ui_manager

class Entity:
    def __init__(self, id, x, y, width, height, ui_manager, depth=0, name="", text="", notes="", media=""):
        self.id = id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.depth = depth
        self.name = f"Node {id}" if name == "" else name
        self.text = text
        self.notes = notes
        self.media = media
        self.ui_manager = ui_manager
        self.menu = None

        self.options = []

        self.centroid = (self.x + self.width/2, self.y + self.height/2)

        self.hidden = False
        self.hovered = False

        self.body = EntityBody(x, y, width, height)
        self.button_add = EntityButton(x + width, y, width/5, height/5, "+")

        self.create_extra_buttons()

    def draw(self, screen):
        if self.hidden:
            return

        for option in self.options:
            if not option.entity.hidden:
                pygame.draw.aaline(screen, (0, 0, 0), self.centroid, option.entity.centroid)

        if self.menu and self.menu.alive():
            self.body.draw_selected(screen)
        else:
            self.body.draw(screen)

        font = pygame.font.Font(None, 24)
        text_surface = font.render(self.name, True, (0, 0, 0))
        text_width, _ = font.size(self.name)
        
        text_x = self.body.x + (self.body.width - text_width) / 2
        text_y = self.body.y + self.body.height/2 - 55
        screen.blit(text_surface, (text_x, text_y))
        
        if self.hovered:
            for button in self.buttons:
                button.draw(screen)

    def create_extra_buttons(self):
        self.buttons = [self.button_add]

        self.button_remove = EntityButton(self.x + self.width, self.y + self.height/5 + 2, self.width/5, self.height/5, "-")
        self.button_hide = EntityButton(self.x - self.width/5 - 2, self.y, self.width/5, self.height/5, "H")
        if self.depth != 0:
            self.buttons.append(self.button_remove)
        self.buttons.append(self.button_hide)

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

        self.button_hide.x = x - 2 - self.width/5
        self.button_hide.y = y

        self.button_hide.rect.x = x - 2 - self.width/5
        self.button_hide.rect.y = y

        if self.depth != 0:
            self.button_remove.x = x + self.width
            self.button_remove.y = y + self.height/5 + 2

            self.button_remove.rect.x = x + self.width
            self.button_remove.rect.y = y + self.height/5 + 2

        self.centroid = (self.x + self.width/2, self.y + self.height/2)

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
        self.menu = EntityMenu(self.ui_manager, self)

    def refresh_menu(self, pos):
        self.menu = EntityMenu(self.ui_manager, self)
        self.menu.set_position(pos)
        
    def was_body_clicked(self, x, y):
        return self.body.rect.collidepoint(x, y)

    def was_button_clicked(self, x, y):
        return self.buttons[0].rect.collidepoint(x, y)
    
    def was_hide_button_clicked(self, x, y):
        return self.buttons[-1].rect.collidepoint(x, y)
    
    def was_remove_button_clicked(self, x, y):
        return self.buttons[1].rect.collidepoint(x, y)
    
    def was_menu_clicked(self, x, y):
        if self.menu:
            return self.menu.rect.collidepoint(x, y)
        return False

    def get_position(self):
        return (self.x, self.y)
    
    def toggle(self):
        self.hidden = not self.hidden

    def toggle_options(self, options=None):
        for option in self.options if not options else options:
            option.entity.toggle()
            if option.entity.options:
                self.toggle_options(option.entity.options)
    
class Option:
    def __init__(self, text, entity):
        self.text = text
        self.entity = entity

class PositionManager:
    def set_position(self, parent, entity, entities):
        radius = 150
        correct_pos = False

        while not correct_pos:
            positions = [(0, radius), (radius, 0), (0, -radius), (-radius, 0), 
                          (radius/1.5, radius/1.5), (radius/1.5, -radius/1.5), 
                          (-radius/1.5, -radius/1.5), (-radius/1.5, radius/1.5)]
            for offset in positions:
                parent_pos = parent.centroid
                pos = (offset[0] + parent_pos[0], offset[1] + parent_pos[1])
                entity.set_position(pos[0] - parent.width/2, pos[1] - parent.height/2)
                correct_pos = True
                for e in entities:
                    if self.dist(e.centroid, entity.centroid) < radius/3 or self.doesCollide(e, entity):
                        correct_pos = False
                        break
                if correct_pos:
                    break
            radius *= 1.8
        
            
    def dist(self, pos_a, pos_b):
        x = pos_a[0] - pos_b[0]
        y = pos_a[1] - pos_b[1]
        return math.sqrt(x**2 + y**2)
    
    def doesCollide(self, e1, e2):
        return e1.body.rect.colliderect(e2.body.rect)