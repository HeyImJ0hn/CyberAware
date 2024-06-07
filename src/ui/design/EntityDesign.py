import pygame
from pygame_gui.elements import *
from pygame_gui.core import ObjectID
from dao.FileDAO import FileDAO
import cv2
from PIL import Image
import os

class EntityBody:
    def __init__(self, x, y, width, height, colour=(215, 215, 215)):
        self.rect = pygame.Rect(x, y, width, height)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.colour = colour

    def draw(self, screen):
        pygame.draw.rect(screen, self.colour, self.rect, border_radius=12)

    def draw_selected(self, screen):
        pygame.draw.rect(screen, (74, 153, 248), self.rect, border_radius=12)
        pygame.draw.rect(screen, self.colour, pygame.Rect(self.x+4, self.y+4, self.width-8, self.height-8), border_radius=12)

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
        self.ui_manager = ui_manager
        self.entity = entity
        base_height = 315
        option_height = 30
        
        if len(entity.options) == 0:
            self.height = base_height
        elif len(entity.options) == 1:
            self.height = base_height + 80
        else:
            self.height = base_height + 80 + (option_height * (len(entity.options) - 1))
        
        self.width = 355

        self.x = entity.x + entity.width + 25
        self.y = entity.y

        super().__init__(pygame.Rect((self.x, self.y), (self.width, self.height)), 
                         ui_manager, 
                         window_display_title='Properties',
                         object_id='#entity_menu',
                         resizable=False)
        
        self.options = []
        
        self.setup_ui()

    def setup_ui(self):
        UILabel(relative_rect=pygame.Rect((10, 10), (80, 30)), 
                                  text="Name", 
                                  manager=self.ui_manager, 
                                  container=self, 
                                  object_id=ObjectID(class_id='@entity_menu_label', object_id='#name_label'))
        
        self.name = UITextEntryLine(relative_rect=pygame.Rect((80, 10), (260, 30)), 
                                    manager=self.ui_manager, 
                                    container=self, 
                                    initial_text=self.entity.name, 
                                    object_id=ObjectID(class_id='@entity_menu_input', object_id='#name_input'))

        UILabel(relative_rect=pygame.Rect((10, 50), (80, 30)), 
                text="Media", 
                manager=self.ui_manager, 
                container=self, 
                object_id=ObjectID(class_id='@entity_menu_label', object_id='#media_label'))
        
        self.media = UITextEntryLine(relative_rect=pygame.Rect((80, 50), (230, 30)), 
                                     manager=self.ui_manager, 
                                     container=self, 
                                     initial_text=FileDAO.get_base_name(self.entity.media), 
                                     object_id=ObjectID(class_id='@entity_menu_input', object_id='#media_input'))
        
        self.browse_button = UIButton(relative_rect=pygame.Rect((310, 50), (30, 30)),
                                        text='...',
                                        manager=self.ui_manager,
                                        container=self,
                                        object_id=ObjectID(class_id='@entity_menu_button', object_id='#browse_button'))

        UILabel(relative_rect=pygame.Rect((10, 90), (60, 30)), 
                text="Text", 
                manager=self.ui_manager, 
                container=self, 
                object_id=ObjectID(class_id='@entity_menu_label', object_id='#text_label'))
        
        self.text = UITextEntryBox(relative_rect=pygame.Rect((80, 90), (260, 80)), 
                                    manager=self.ui_manager, 
                                    container=self, 
                                    initial_text=self.entity.text, 
                                    object_id=ObjectID(class_id='@entity_menu_input', object_id='#text_input'))

        UILabel(relative_rect=pygame.Rect((10, 180), (80, 30)), 
                text="Notes", 
                manager=self.ui_manager, 
                container=self, 
                object_id=ObjectID(class_id='@entity_menu_label', object_id='#notes_label'))
        
        self.notes = UITextEntryBox(relative_rect=pygame.Rect((80, 180), (260, 60)), 
                                    manager=self.ui_manager, 
                                    container=self, 
                                    initial_text=self.entity.notes, 
                                    object_id=ObjectID(class_id='@entity_menu_input', object_id='#notes_input'))
        
        UILabel(relative_rect=pygame.Rect((10, 250), (80, 30)), 
                text="Final", 
                manager=self.ui_manager, 
                container=self, 
                object_id=ObjectID(class_id='@entity_menu_label', object_id='#final_label'))

        self.final_checkbox = UIButton(relative_rect=pygame.Rect((80, 250), (30, 30)),
                                        manager=self.ui_manager,
                                        container=self,
                                        text="",
                                        object_id=ObjectID(class_id='@entity_menu_checkbox', object_id='#final_checkbox'))
        
        self.final_checkbox.set_text("X" if self.entity.final else "")

        options = self.entity.options
        if len(options) > 0:
            UILabel(relative_rect=pygame.Rect((10, 290), (80, 30)), 
                    text="Options", 
                    manager=self.ui_manager, 
                    container=self, 
                    object_id=ObjectID(class_id='@entity_menu_label', object_id='#options_label'))
            
            for i, option in enumerate(options):
                UILabel(relative_rect=pygame.Rect((10, 320 + 40 * i), (80, 30)), 
                        text=option.entity.name, 
                        manager=self.ui_manager, 
                        container=self, 
                        object_id=ObjectID(class_id='@entity_option_name', object_id='#option_name_label'))
                text = UITextEntryLine(relative_rect=pygame.Rect((90, 320 + 40 * i), (160, 30)), 
                                manager=self.ui_manager, 
                                container=self, 
                                placeholder_text="Texto",
                                initial_text=option.text,
                                object_id=ObjectID(class_id='@entity_option_input', object_id='#option_text_input'))
                
                button = UIButton(relative_rect=pygame.Rect((250, 320 + 40 * i), (30, 30)),
                        text="-",
                        manager=self.ui_manager,
                        container=self,
                        object_id=ObjectID(class_id='@entity_option_button', object_id='#option_remove_button'))
                
                self.options.append((text, button))
        

    def kill(self):
        event_data = {
            'ui_element': self,
            'entity': self.entity
        }
        event = pygame.event.Event(pygame.USEREVENT + 3000, event_data)

        pygame.event.post(event)
        super().kill()

    def move(self, dx, dy):
        self.set_position((self.rect.x + dx, self.rect.y + dy))

    def is_inside(self, x, y):
        return self.rect.collidepoint(x, y)
    
class PreviewWindow(UIWindow):
    def __init__(self, ui_manager, entity, game_name):
        self.ui_manager = ui_manager
        self.entity = entity
        self.width = 360
        self.height = 640
        self.x = 10
        self.y = 10
        self.game_name = game_name

        super().__init__(pygame.Rect((self.x, self.y), (self.width, self.height)), 
                         ui_manager, 
                         window_display_title='Preview',
                         object_id='#preview_window',
                         resizable=False,
                         always_on_top=True)
        
        self.setup_ui()

    def setup_ui(self):
        # Background
        image_surface = self.resize_image_to_height(pygame.image.load("static/homeview_bg.png"), self.height)
        excess_width = image_surface.get_width() - self.width
        if excess_width > 0:
            crop_rect = pygame.Rect(excess_width // 2, 0, self.width, self.height)
            image_surface = image_surface.subsurface(crop_rect)
        self.background = UIImage(relative_rect=pygame.Rect((0, 0), (self.width, self.height)), 
                                image_surface=image_surface,
                                manager=self.ui_manager, 
                                container=self, 
                                object_id=ObjectID(class_id='@preview_window_background', object_id='#background_image'))
        
        # Media
        if FileDAO.is_video_file(self.entity.media):
            path = FileDAO.save_temp_image(self.load_first_frame(self.entity.media))
            image_surface = pygame.image.load(path)
            FileDAO.delete_temp_image()
        elif FileDAO.is_image_file(self.entity.media):
            image_surface = pygame.image.load(self.entity.media)
        else:
            image_surface = None

        if image_surface is not None:
            aspect_ratio = image_surface.get_width() / image_surface.get_height()
            if aspect_ratio > 1:
                image_surface = self.resize_image_to_height(image_surface, self.height)
                excess_width = image_surface.get_width() - self.width
                if excess_width > 0:
                    crop_rect = pygame.Rect(excess_width // 2, 0, self.width, self.height)
                    image_surface = image_surface.subsurface(crop_rect)

            if self.entity.depth == 0:
                rect = pygame.Rect((60, 120), (240, 240))
            else:
                rect = pygame.Rect((0, 0), (self.width, self.height))

            self.media = UIImage(relative_rect=rect, 
                                image_surface=image_surface, 
                                manager=self.ui_manager, 
                                container=self, 
                                object_id=ObjectID(class_id='@preview_window_image', object_id='#media_image'))
        
        if self.entity.depth == 0:
            # Game Name
            self.title = UILabel(relative_rect=pygame.Rect((0, 40), (self.width, 60)), 
                                text=self.game_name, 
                                manager=self.ui_manager, 
                                container=self, 
                                object_id=ObjectID(class_id='@preview_window_title', object_id='#title_label'))
        
        # Text
        self.text = UILabel(relative_rect=pygame.Rect((20, 20), (self.width, self.height - 80)), 
                            text=self.entity.text, 
                            manager=self.ui_manager, 
                            container=self, 
                            object_id=ObjectID(class_id='@preview_window_text', object_id='#text_label'))

        if not self.entity.final:        
            # Options
            options_vertical_position = self.height - (len(self.entity.options) * 30) - 80
            for i, option in enumerate(self.entity.options):
                UIButton(relative_rect=pygame.Rect((200/2-((200/2)/4), options_vertical_position + 40 * i), (200, 30)), 
                        text=option.text, 
                        manager=self.ui_manager, 
                        container=self, 
                        object_id=ObjectID(class_id='@preview_window_button', object_id='#option_button_' + str(i)))
        else:
            UIButton(relative_rect=pygame.Rect((200/2-((200/2)/4), self.height - 80), (200, 30)), 
                        text="Início", 
                        manager=self.ui_manager, 
                        container=self, 
                        object_id=ObjectID(class_id='@preview_window_button', object_id='#final_button'))

    def kill(self):
        super().kill()

    def is_inside(self, x, y):
        return self.rect.collidepoint(x, y)
    
    def load_first_frame(self, video_path):
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        cap.release()

        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            return img
        else:
            raise ValueError("Could not read the video file or the video is empty")
        
    def resize_image_to_height(self, image_surface, target_height):
        scale = target_height / image_surface.get_height()

        new_width = int(image_surface.get_width() * scale)
        new_height = int(image_surface.get_height() * scale)
        return pygame.transform.smoothscale(image_surface, (new_width, new_height))