import pygame
import sys
import math

from src.ui.design.entity_design import EntityBody, EntityButton, PreviewWindow, EntityMenu
from ui.views.views import HomeView, BuildView
from src.dao.file_dao import FileDAO
from src.conv.json_converter import JSONConverter
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
        return self._entity_manager.remove_entity(entity)

    def update_entities(self, entities):
        self._entity_manager.update_entities(entities)

    def get_entities(self):
        return self._entity_manager.entities
    
    def get_entity(self, id):
        return self._entity_manager.get_entity_by_id(id)
    
    def clear_entities(self):
        return self._entity_manager.clear_entities()
    
    def draw_entities(self, screen):
        self._entity_manager.draw_entities(screen)
    
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
        entity.update_media(FileDAO.copy_media(media, self.game_to_file_name(self.game_name).split(".")[0]))

    def get_parents(self, entity):
        return self._entity_manager.get_parents(entity)
    
    def update_game_name(self, game_name):
        old_name = self.game_name
        self.game_name = game_name
        self.file_name = self.game_to_file_name(self.game_name)
        self.path = FileDAO.create_absolute_path(FileDAO.get_dir_name(self.path), self.file_name)

        FileDAO.update_game_name(FileDAO.get_file_name_without_extension(self.game_to_file_name(old_name)), FileDAO.get_file_name_without_extension(self.file_name))

    def open_preview_window(self, entity=None):
        return PreviewWindow(self.view.ui_manager, entity if entity else self._entity_manager.entities[0], self.game_name)

class EntityManager:
    def __init__(self, ui_manager, entities=[]):
        self.entities = entities
        self.ui_manager = ui_manager

    def add_entity(self, parent=None):
        entity = None
        if parent:
            depth = parent.depth + 1
            entity = Entity(self.entities[-1].id+1, 0, 0, 75, 75, self.ui_manager, depth=depth, colour=parent.colour)
            PositionManager().set_position(parent, entity, self.entities)
            parent.add_option(entity)
        else:
            entity = Entity(0, self.ui_manager.window_resolution[0]/2-75/2, self.ui_manager.window_resolution[1]/2-75/2, 75, 75, self.ui_manager)

        self.entities.append(entity)

    def remove_entity(self, entity):
        if len(entity.options) > 0:
            return False
        
        self.entities.remove(entity)
        self.remove_entity_from_options(entity)
        return True

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
    
    def remove_entity_from_options(self, entity):
        for e in self.entities:
            e.remove_option(entity)

    def draw_entities(self, screen):
        for entity in self.entities:
            for option in entity.options:
                if not option.entity.hidden:
                    pygame.draw.aaline(screen, (0, 0, 0), entity.centroid, option.entity.centroid)

        for entity in self.entities:
            entity.draw(screen)
    
    def create_entity(self):
        return Entity(len(self.entities), 0, 0, 75, 75, self.ui_manager, depth=1)
    
    def create_option(self, text, entity):
        return Option(text, entity)
    
    def fix_entities(self):
        for e in self.entities:
            e.create_buttons()
            for o in e.options:
                id = o.entity
                o.entity = self.get_entity_by_id(id)

    def update_ui_manager(self, ui_manager):
        self.ui_manager = ui_manager
        for entity in self.entities:
            entity.ui_manager = ui_manager

    def get_parents(self, entity):
        parents = []
        for e in self.entities:
            for o in e.options:
                if o.entity.id == entity.id:
                    parents.append(e)
        return parents

class Entity:
    def __init__(self, id, x, y, width, height, ui_manager, depth=0, name="", text="", notes="", media="", colour=(215, 215, 215)):
        self.id = id
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.depth = depth
        self.name = f"Screen {id}" if name == "" else name
        self.text = text
        self.notes = notes
        self.media = media
        self.ui_manager = ui_manager
        self.menu = None
        self.colour = colour

        self.final = False

        self.max_options = 6
        self.options = []

        self.centroid = (self.x + self.width/2, self.y + self.height/2)

        self.options_font = pygame.font.Font("fonts/Roboto-Regular.ttf", 20)
        self.name_font = pygame.font.Font("fonts/Roboto-Bold.ttf", 20)

        self.hidden = False
        self.hovered = False

        self.body = EntityBody(x, y, width, height, colour)
        self.create_buttons()

    def draw(self, screen):
        if self.hidden:
            return

        for option in self.options:
            if not option.entity.hidden:
                #pygame.draw.aaline(screen, (0, 0, 0), self.centroid, option.entity.centroid)

                # Texto da opção
                midpoint_x = (self.centroid[0] + option.entity.centroid[0]) / 2
                midpoint_y = (self.centroid[1] + option.entity.centroid[1]) / 2
                
                text = option.text if len(option.text) < 10 else option.text[:10] + "..." 
                text_surface = self.options_font.render(text, True, (0, 0, 0)) 
                text_width, text_height = self.options_font.size(text)
                
                text_x = midpoint_x - text_width / 2
                text_y = midpoint_y - text_height / 2
                
                screen.blit(text_surface, (text_x, text_y))

                # Seta
                dir_x = option.entity.centroid[0] - self.centroid[0]
                dir_y = option.entity.centroid[1] - self.centroid[1]
                length = math.sqrt(dir_x ** 2 + dir_y ** 2)
                unit_dir_x = dir_x / length
                unit_dir_y = dir_y / length

                arrow_base_x = option.entity.centroid[0] - unit_dir_x * (option.entity.width / 2 + 30)
                arrow_base_y = option.entity.centroid[1] - unit_dir_y * (option.entity.height / 2 + 30)

                arrow_size = 12
                angle = math.atan2(dir_y, dir_x)
                left_wing_x = arrow_base_x - math.cos(angle + math.pi / 6) * arrow_size
                left_wing_y = arrow_base_y - math.sin(angle + math.pi / 6) * arrow_size
                right_wing_x = arrow_base_x - math.cos(angle - math.pi / 6) * arrow_size
                right_wing_y = arrow_base_y - math.sin(angle - math.pi / 6) * arrow_size

                pygame.draw.polygon(screen, (0, 0, 0), [(arrow_base_x, arrow_base_y), (left_wing_x, left_wing_y), (right_wing_x, right_wing_y)])

        if self.menu and self.menu.alive():
            self.body.draw_selected(screen)
        else:
            self.body.draw(screen)

        # Nome da Entidade
        text_surface = self.name_font.render(self.name, True, (0, 0, 0))
        text_width, _ = self.name_font.size(self.name)
        
        text_x = self.body.x + (self.body.width - text_width) / 2
        text_y = self.body.y + self.body.height/2 - 60
        screen.blit(text_surface, (text_x, text_y))

        if self.final:
            # Texto se for "Final"
            text = "Final"
            text_surface = self.name_font.render(text, True, (0, 0, 0)) 
            text_width, _ = self.name_font.size(text)
            
            text_x = self.body.x + (self.body.width - text_width) / 2
            text_y = self.body.y + self.body.height/2 + 35
            
            screen.blit(text_surface, (text_x, text_y))
        
        if self.hovered:
            for button in self.buttons:
                button.draw(screen)

    def create_buttons(self):
        self.buttons = []

        self.button_add = EntityButton(self.x + self.width, self.y, self.width/5, self.height/5, "+")
        self.button_remove = EntityButton(self.x + self.width, self.y + self.height/5 + 2, self.width/5, self.height/5, "-")

        self.button_hide = EntityButton(self.x - self.width/5 - 2, self.y, self.width/5, self.height/5, "H")
        self.button_colour = EntityButton(self.x - self.width/5 - 2, self.y + self.height/5 + 2, self.width/5, self.height/5, "C")

        self.buttons.append(self.button_add)
        self.buttons.append(self.button_hide)
        self.buttons.append(self.button_colour)
        if self.depth != 0:
            self.buttons.append(self.button_remove)

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

        self.button_colour.x = x - 2 - self.width/5
        self.button_colour.y = y + self.height/5 + 2

        self.button_colour.rect.x = x - 2 - self.width/5
        self.button_colour.rect.y = y + self.height/5 + 2

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

    def update_properties(self, name=None, text=None, notes=None, final=False):
        self.name = name if name else self.name
        self.text = text if text else self.text
        self.notes = notes if notes else self.notes
        self.final = final

    def update_options(self, ui_options):
        ui_options = [o[0] for o in ui_options]
        for i, option in enumerate(self.options):
            try:
                option.text = ui_options[i].get_text()
            except IndexError:
                pass

    def remove_option_menu(self, option):
        toRemove = None
        for option in self.options:
            if option.entity.id == option.id:
                toRemove = option

        if toRemove: 
            self.options.pop(toRemove)

    def get_option_from_menu(self, button):
        for option in self.menu.options:
            if option[1] == button:
                return self.options[self.menu.options.index(option)]

    def update_media(self, media):
        self.media = media

    def update_colour(self, colour):
        self.colour = colour
        self.body.colour = colour

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
        return self.buttons[1].rect.collidepoint(x, y)
    
    def was_remove_button_clicked(self, x, y):
        return self.buttons[-1].rect.collidepoint(x, y) if self.depth != 0 else False
    
    def was_colour_button_clicked(self, x, y):
        return self.buttons[2].rect.collidepoint(x, y)
    
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
        radius = 200
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