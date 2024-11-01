import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UILabel, UISelectionList
from pygame_gui.core import ObjectID
from config.settings import *
from ui.views.controllers import ViewController, HomeViewControl
from ui.views.toolbar import Toolbar
from ui.views.view_types import ViewType
import numpy as np
import cv2
import os
import sys

class View:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        #self.resolution = (800, 600) if self.type == ViewType.HOME else Settings.RESOLUTION
        self.resolution = (800, 600)
        self.screen = pygame.display.set_mode(self.resolution, pygame.SRCALPHA if self.type == ViewType.HOME else pygame.RESIZABLE | pygame.SRCALPHA)

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS  # This is where PyInstaller unpacks files at runtime
        else:
            base_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))  # Use the script's directory

        theme_path = os.path.normcase(os.path.join(base_path, 'theme.json'))
        self.ui_manager = pygame_gui.UIManager(self.resolution, theme_path)

        #self.ui_manager = pygame_gui.UIManager(self.resolution, os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'theme.json')))
        pygame.display.set_caption("CyberAware")
        
        self.clock = pygame.time.Clock()

        self.view_controller = ViewController(self)

    def run(self):
        while True:
            self.UI_REFRESH_RATE = self.clock.tick(60)/1000
            self.view_controller.mouse_hover()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.view_controller.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.view_controller.mouse_button_down(event)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.view_controller.mouse_button_up(event)
                elif event.type == pygame.MOUSEMOTION:
                    self.view_controller.mouse_motion(event)
                elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                    self.view_controller.ui_button_pressed(event)
                elif event.type == pygame.KEYDOWN:
                    self.view_controller.key_down(event)
                elif event.type == pygame.KEYUP:
                    self.view_controller.key_up(event)
                elif event.type == pygame.VIDEORESIZE:
                    self.view_controller.window_resize(event)
                elif event.type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
                    self.view_controller.ui_file_dialog_path_picked(event)
                elif event.type == pygame.USEREVENT + 3000: # Entity menu death event
                    self.view_controller.menu_kill(event)
                if event.type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED:
                    self.view_controller.ui_colour_picker_colour_picked(event)
                    
                self.ui_manager.process_events(event)

            self.render()

    def render(self):
        self.ui_manager.update(self.UI_REFRESH_RATE)
        self.screen.fill((255, 255, 255))

        if self.view_controller.active_toast and not self.view_controller.compilling:
            current_time = pygame.time.get_ticks()
            if current_time - self.view_controller.toast_start_time >= self.view_controller.toast_duration:
                self.view_controller.active_toast.kill()
                self.view_controller.active_toast = None

    def update_display(self):
        self.ui_manager.draw_ui(self.screen)
        pygame.display.flip()

class BuildView(View):
    def __init__(self, game_manager):
        self.type = ViewType.BUILD
        super().__init__(game_manager)
        
        pygame.display.set_caption(f"CyberAware - {game_manager.path}")
        
        #self.ui_manager.set_window_resolution(self.resolution)
        
        #window = Window.from_display_module()
        #window.position = (5, 35)
        
        self.loading_angle = 0 
        self.loading_start_time = pygame.time.get_ticks()  
        
        self.toolbar = Toolbar(self)

    def render(self):
        super().render()

        WIDTH, HEIGHT = self.resolution

        num_circles_x = (WIDTH + 15 - 1) // 15
        num_circles_y = (HEIGHT + 15 - 1) // 15
        spacing_x = WIDTH // num_circles_x
        spacing_y = HEIGHT // num_circles_y
        start_x = self.view_controller.view_offset[0] % spacing_x
        start_y = self.view_controller.view_offset[1] % spacing_y
        for x in range(start_x, WIDTH, spacing_x):
            for y in range(start_y, HEIGHT, spacing_y):
                pygame.draw.circle(self.screen, (240, 240, 240), (x, y), 2)
        
        if self.view_controller.draw_to_cursor:
            entity = self.game_manager.get_entity(self.view_controller.current_entity_option_id)
            pygame.draw.aaline(self.screen, (0, 0, 0), entity.centroid, pygame.mouse.get_pos())
        
        self.game_manager.draw_entities(self.screen)

        for entity in self.game_manager.get_entities():
            entity.draw(self.screen)

        self.toolbar.draw(self.screen)
        
        if self.game_manager.finished_compiling:
            self.view_controller.handle_compilation_finish()
            
        if not self.game_manager.finished_compiling and self.view_controller.compilling:
            background_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            background_surface.fill((255, 255, 255, 128))  
            self.screen.blit(background_surface, (0, 0))
            
            center = (WIDTH // 2, HEIGHT // 2)
            arc_length = 70  
            self.loading_angle += 5  
            if self.loading_angle >= 360:
                self.loading_angle = 0 

            start_angle = np.radians(self.loading_angle)
            end_angle = np.radians(self.loading_angle + arc_length)

            self.drawAAArc(self.screen, center, start_angle, end_angle)
            
        if self.view_controller.generating_key:
            if self.game_manager.does_keystore_exist():
                self.view_controller.handle_key_generation_finish()

        self.update_display()
        
    def drawAAArc(self, surf, center, start_angle, end_angle):
        color = (0, 157, 255)
        width = 5
        radius = 50
        padding = width + 2
        surface_size = (radius * 2 + padding * 2 + 4, radius * 2 + padding * 2 + 4)
        
        arc_image = np.zeros((*surface_size, 4), dtype=np.uint8)

        start_angle_deg = np.degrees(start_angle)
        end_angle_deg = np.degrees(end_angle)

        arc_image = cv2.ellipse(
            arc_image, 
            (surface_size[0]//2, surface_size[1]//2),
            (radius, radius),
            0, 
            start_angle_deg, 
            end_angle_deg, 
            (*color, 255), 
            width, 
            lineType=cv2.LINE_AA
        )
        
        arc_surface = pygame.image.frombuffer(arc_image.flatten(), surface_size, 'RGBA')
        arc_rect = arc_surface.get_rect(center=center)
        surf.blit(arc_surface, arc_rect)

class HomeView(View):
    def __init__(self, game_manager):
        self.type = ViewType.HOME
        super().__init__(game_manager)

        self.game_manager = game_manager

        self.controller = HomeViewControl(self)
        
        self.bg_colour = (47, 51, 61)
        self.list_bg_colour = (40, 44, 52)

        self.draw_ui()

    def draw_ui(self):
        WIDTH, HEIGHT = self.resolution
        
        button_margin = 5
        button_height = 30
        button_width = WIDTH*0.25 / 1.1
        
        title_y = 15
        subtitle_y = title_y + 25
        new_button_y = subtitle_y + 100
        open_button_y = new_button_y + button_height + button_margin
        quit_button_y = open_button_y + button_height + button_margin
        
        left_size = WIDTH*0.25
        
        # Left side
        self.title = UILabel(pygame.Rect((0, title_y), (WIDTH*0.25, 50)), text='CyberAware', object_id='#title', manager=self.ui_manager)
        self.subtitle = UILabel(pygame.Rect((15, subtitle_y), (WIDTH*0.25, 50)), text='Platform', object_id='#subtitle', manager=self.ui_manager)
        
        self.new_button = UIButton(pygame.Rect((left_size / 2 - button_width/2, new_button_y), (button_width, button_height)), 
                                   text='New Game', 
                                   object_id=ObjectID(class_id='@main_menu_button', object_id='#new_game_button'), 
                                   manager=self.ui_manager)
        self.open_button = UIButton(pygame.Rect((left_size / 2 - button_width/2, open_button_y), (button_width, button_height)), 
                                    text='Open Game', 
                                    object_id=ObjectID(class_id='@main_menu_button', object_id='#open_game_button'), 
                                    manager=self.ui_manager)
        self.quit_button = UIButton(pygame.Rect((left_size / 2 - button_width/2, quit_button_y), (button_width, button_height)), 
                                    text='Quit', 
                                    object_id=ObjectID(class_id='@main_menu_button', object_id='#quit_button'), 
                                    manager=self.ui_manager)
        
        self.buttons = [self.new_button, self.open_button, self.quit_button]
        
        
        # Right side
        recent_files = self.game_manager.recent_files
        recent_list = []
        for file in recent_files:
            recent_list.append((self.game_manager.game_name_from_path(file), file))
        
        self.recent_label = UILabel(pygame.Rect((WIDTH*0.25, 0), (WIDTH - WIDTH*0.25, 50)), text='Recent Games', object_id='#recent_label', manager=self.ui_manager)

        self.list = UISelectionList(pygame.Rect((WIDTH*0.25, 50), (WIDTH - WIDTH*0.25, HEIGHT)), 
                                    item_list=recent_list,
                                    object_id=ObjectID(class_id='@main_menu_list', object_id='#recent_list'),
                                    manager=self.ui_manager,
                                    )

    def render(self):
        super().render()
        self.screen.fill(self.bg_colour)
        pygame.draw.rect(self.screen, self.list_bg_colour, (self.resolution[0]*0.25, 0, self.resolution[0] - self.resolution[0]*0.25, self.resolution[1]))
        self.update_display()