import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UILabel
from pygame_gui.core import ObjectID
from config.Settings import *
from ui.views.controllers import ViewController, HomeViewControl
from ui.views.toolbar import Toolbar
from ui.views.view_types import ViewType

class View:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.resolution = Settings.RESOLUTION
        self.screen = pygame.display.set_mode(self.resolution, pygame.RESIZABLE | pygame.SRCALPHA)

        self.ui_manager = pygame_gui.UIManager(self.resolution, 'theme.json')
        pygame.display.set_caption("CyberAware - Plataforma")
        
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
                elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    self.view_controller.ui_text_entry_finished(event)
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

        if self.view_controller.active_toast:
            current_time = pygame.time.get_ticks()
            if current_time - self.view_controller.toast_start_time >= self.view_controller.toast_duration:
                self.view_controller.active_toast.kill()
                self.view_controller.active_toast = None

    def update_display(self):
        self.ui_manager.draw_ui(self.screen)
        pygame.display.flip()

class BuildView(View):
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.type = ViewType.BUILD

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

        self.update_display()

class HomeView(View):
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.type = ViewType.HOME

        self.game_manager = game_manager

        self.controller = HomeViewControl(self)

        self.bg = pygame.image.load('static/homeview_bg.png')

        self.draw_ui()

    def draw_ui(self):
        WIDTH, HEIGHT = self.resolution

        label_width = 400
        button_width = 240
        button_height = 50

        self.title = UILabel(relative_rect=pygame.Rect((WIDTH/2 - label_width/2, HEIGHT/2 - 400/2), (label_width, 100)), text='CyberAware', object_id='#title', manager=self.ui_manager)
        self.subtitle = UILabel(relative_rect=pygame.Rect((WIDTH/2 - label_width/2 + 30, HEIGHT/2 - 400/2+45), (label_width, 100)), text='Plataforma', object_id='#subtitle', manager=self.ui_manager)

        self.new_button = UIButton(relative_rect=pygame.Rect((WIDTH/2 - button_width/2, HEIGHT/2 - 400/2+200), (button_width, button_height)), 
                                   text='NEW GAME', object_id=ObjectID(class_id='@main_menu_button', object_id='#new_game_button'), manager=self.ui_manager)
        self.open_button = UIButton(relative_rect=pygame.Rect((WIDTH/2 - button_width/2, HEIGHT/2 - 400/2+275), (button_width, button_height)), 
                                    text='OPEN GAME', object_id=ObjectID(class_id='@main_menu_button', object_id='#open_game_button'), manager=self.ui_manager)
        self.quit_button = UIButton(relative_rect=pygame.Rect((WIDTH/2 - button_width/2, HEIGHT/2 - 400/2+350), (button_width, button_height)), 
                                    text='QUIT', object_id=ObjectID(class_id='@main_menu_button', object_id='#quit_button'), manager=self.ui_manager)
        
        self.buttons = [self.new_button, self.open_button, self.quit_button]
        
    def render(self):
        super().render()
        
        self.screen.blit(self.bg, (0, 0))
        self.update_display()