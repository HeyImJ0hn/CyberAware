import pygame
import pygame_gui
from pygame_gui.elements import *
from pygame_gui.windows import *
from pygame_gui.core import ObjectID

import sys

class View:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.resolution = self.game_manager.resolution
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
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.view_controller.mouse_button_down(event)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.view_controller.mouse_button_up(event)
                elif event.type == pygame.MOUSEMOTION:
                    self.view_controller.mouse_motion(event)
                #elif (event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED and
                #      event.ui_object_id == "#main_text_entry"):
                #    print("Text entered:", event.text)
                elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                    self.view_controller.ui_button_pressed(event)
                elif event.type == pygame.KEYDOWN:
                    self.view_controller.key_down(event)
                elif event.type == pygame.KEYUP:
                    self.view_controller.key_up(event)
                elif event.type == pygame.VIDEORESIZE:
                    self.view_controller.window_resize(event)
                    
            
                self.ui_manager.process_events(event)

            self.render()

    def render(self):
        self.ui_manager.update(self.UI_REFRESH_RATE)
        self.screen.fill((255, 255, 255))

    def update_display(self):
        self.ui_manager.draw_ui(self.screen)
        pygame.display.flip()

class ViewController:
    def __init__(self, view):
        self.view = view

        self.mouse_pos = None
        self.space_pressed = False
        self.dragging_entity = None
        self.hovering_entity = False
        self.dragging_menu = None
        self.open_menu = None
        self.clicked_outside = True

        self.view_offset = (0, 0)

    def mouse_button_down(self, event):
        if isinstance(self.view, BuildView):
            self.mouse_pos = pygame.mouse.get_pos()
            for entity in self.view.game_manager.get_entities():
                if entity.was_button_clicked(self.mouse_pos[0], self.mouse_pos[1]):
                        self.view.game_manager.add_entity(entity)
                        if self.open_menu and self.open_menu == entity.menu:
                            self.open_menu.kill()
                            entity.refresh_menu((self.open_menu.rect.x, self.open_menu.rect.y))
                            self.open_menu = entity.menu
                elif entity.was_body_clicked(self.mouse_pos[0], self.mouse_pos[1]):
                    self.dragging_entity = entity
                    self.offset_x = entity.body.rect.x - self.mouse_pos[0] 
                    self.offset_y = entity.body.rect.y - self.mouse_pos[1]
                elif entity.was_menu_clicked(self.mouse_pos[0], self.mouse_pos[1]):
                    self.offset_x = entity.menu.rect.x - self.mouse_pos[0]
                    self.offset_y = entity.menu.rect.y - self.mouse_pos[1]
                    self.dragging_menu = entity.menu

    def mouse_button_up(self, event):
        if isinstance(self.view, BuildView):
            self.dragging_entity = None
            self.dragging_menu = None
            self.clicked_outside = True

            current_pos = pygame.mouse.get_pos()
            for entity in self.view.game_manager.get_entities():
                if entity.was_menu_clicked(current_pos[0], current_pos[1]) or entity.was_body_clicked(current_pos[0], current_pos[1]) \
                    or entity.was_button_clicked(current_pos[0], current_pos[1]):
                    self.clicked_outside = False

                if self.mouse_pos == current_pos and not self.space_pressed:
                        if entity.was_body_clicked(current_pos[0], current_pos[1]):
                            if not self.open_menu:
                                entity.open_menu()
                                self.open_menu = entity.menu
                            else:
                                self.open_menu.kill()
                                entity.open_menu()
                                self.open_menu = entity.menu

            if self.clicked_outside and self.open_menu:
                for entity in self.view.game_manager.get_entities():
                    if entity.menu == self.open_menu:
                        entity.menu = None
                        self.open_menu.kill()
                        self.open_menu = None

            self.mouse_pos = None

    def mouse_motion(self, event):
        if isinstance(self.view, BuildView):
            if self.mouse_pos is not None:
                if self.space_pressed:
                    mouse_pos = pygame.mouse.get_pos()
                    dx = mouse_pos[0] - self.mouse_pos[0]
                    dy = mouse_pos[1] - self.mouse_pos[1]
                    self.view_offset = (self.view_offset[0] + dx, self.view_offset[1] + dy)
                    self.mouse_pos = mouse_pos
                    for entity in self.view.game_manager.get_entities():
                        entity.move(dx, dy)
                else:
                    if self.dragging_entity:
                        mouse_pos = pygame.mouse.get_pos()
                        dx = mouse_pos[0] + self.offset_x - self.dragging_entity.body.rect.x
                        dy = mouse_pos[1] + self.offset_y - self.dragging_entity.body.rect.y
                        self.dragging_entity.move(dx, dy)
                    elif self.dragging_menu:
                        mouse_pos = pygame.mouse.get_pos()
                        dx = mouse_pos[0] + self.offset_x - self.dragging_menu.rect.x
                        dy = mouse_pos[1] + self.offset_y - self.dragging_menu.rect.y
                        self.dragging_menu.move(dx, dy)

    def ui_button_pressed(self, event):
        if event.ui_object_id == '#new_game_button':
            self.view.controller.new_game()
        elif event.ui_object_id == '#open_game_button':
            self.view.controller.open_game()
        elif event.ui_object_id == '#quit_button':
            pygame.quit()
            sys.exit()

        elif event.ui_object_id == 'auto_resizing_container.#toolbar_new_game':
            self.view.toolbar.controller.new_game()
        elif event.ui_object_id == 'auto_resizing_container.#toolbar_save_game':
            self.view.toolbar.controller.save_game()
        elif event.ui_object_id == 'auto_resizing_container.#toolbar_open_game':
            self.view.toolbar.controller.open_game()
        elif event.ui_object_id == 'auto_resizing_container.#toolbar_compile':
            self.view.toolbar.controller.compile()

    def mouse_hover(self):
        if isinstance(self.view, BuildView):
            if self.hovering_entity and not self.space_pressed:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.hovering_entity = False

            for entity in self.view.game_manager.get_entities():
                entity.hovered = False
                current_pos = pygame.mouse.get_pos()
                if (entity.was_button_clicked(current_pos[0], current_pos[1]) or entity.was_body_clicked(current_pos[0], current_pos[1])):
                    entity.hovered = True
                    self.hovering_entity = True
            
            if not self.hovering_entity and not self.space_pressed:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def key_down(self, event):
        if event.key == pygame.K_SPACE:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
            self.space_pressed = True

    def key_up(self, event):
        if event.key == pygame.K_SPACE:
            self.space_pressed = False
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def window_resize(self, event):
        self.view.resolution = (event.w, event.h)
        self.view.game_manager.update_resolution((event.w, event.h))
        self.view.ui_manager.set_window_resolution(self.view.resolution)

        WIDTH, HEIGHT = self.view.resolution
        if isinstance(self.view, HomeView):
            self.view.ui_manager.clear_and_reset()
            
            self.view.title.rect.x = WIDTH/2 - 400/2
            self.view.subtitle.rect.x = WIDTH/2 - 400/2 + 30
            self.view.new_button.rect.x = WIDTH/2 - 240/2
            self.view.open_button.rect.x = WIDTH/2 - 240/2
            self.view.quit_button.rect.x = WIDTH/2 - 240/2

            self.view.title.rect.y = HEIGHT/2 - 400/2
            self.view.subtitle.rect.y = HEIGHT/2 - 400/2 + 45
            self.view.new_button.rect.y = HEIGHT/2 - 240/2 + 200
            self.view.open_button.rect.y = HEIGHT/2 - 240/2 + 275
            self.view.quit_button.rect.y = HEIGHT/2 - 240/2 + 350

            self.view.draw_ui()

class BuildView(View):
    def __init__(self, game_manager):
        super().__init__(game_manager)

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
        
        for entity in self.game_manager.get_entities():
            entity.draw(self.screen)

        self.toolbar.draw(self.screen)

        self.update_display()

class HomeView(View):
    def __init__(self, game_manager):
        super().__init__(game_manager)

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
                                   text='New Game', object_id=ObjectID(class_id='@main_menu_button', object_id='#new_game_button'), manager=self.ui_manager)
        self.open_button = UIButton(relative_rect=pygame.Rect((WIDTH/2 - button_width/2, HEIGHT/2 - 400/2+275), (button_width, button_height)), 
                                    text='Open Game', object_id=ObjectID(class_id='@main_menu_button', object_id='#open_game_button'), manager=self.ui_manager)
        self.quit_button = UIButton(relative_rect=pygame.Rect((WIDTH/2 - button_width/2, HEIGHT/2 - 400/2+350), (button_width, button_height)), 
                                    text='Quit', object_id=ObjectID(class_id='@main_menu_button', object_id='#quit_button'), manager=self.ui_manager)
        
        
    def render(self):
        super().render()
        
        self.screen.blit(self.bg, (0, 0))
        self.update_display()

class HomeViewControl:
    def __init__(self, view):
        self.view = view

    def new_game(self):
        self.view.game_manager.new_game()

    def open_game(self):
        self.view.game_manager.open_game()

    def quit(self):
        pygame.quit()
        sys.exit()

class Toolbar:
    def __init__(self, view):
        self.view = view

        self.controller = ToolbarControl(self)

        self.toolbar_height = 40
        self.toolbar_width = self.view.resolution[0]

        self.toolbar_container = UIAutoResizingContainer(
            relative_rect=pygame.Rect(0, 0, self.toolbar_width, self.toolbar_height),
            manager=self.view.ui_manager,
            object_id='@toolbar'
        )

        button_width = 100
        button_height = 20
        button_margin = 10

        buttons = [('New Game', '#toolbar_new_game'), ('Save Game', '#toolbar_save_game'), ('Open Game', '#toolbar_open_game'), ('Compile', '#toolbar_compile')]

        for i, (text, object_id) in enumerate(buttons):
            UIButton(
                relative_rect=pygame.Rect(button_margin * (i + 1) + button_width * i, button_margin, button_width, button_height),
                text=text,
                manager=self.view.ui_manager,
                container=self.toolbar_container,
                object_id=ObjectID(class_id='@toolbar_button', object_id=object_id)
            )

        self.input = UITextEntryLine(
            relative_rect=pygame.Rect(button_margin * (len(buttons) + 2) + button_width * len(buttons) - 30, 5, 300, 30),
            manager=self.view.ui_manager,
            container=self.toolbar_container,
            object_id='#toolbar_input'
        )

    def draw(self, screen):
        self.toolbar_width = self.view.resolution[0]

        self.toolbar_container.relative_rect.width = self.toolbar_width

        shadow_surface = pygame.Surface((self.toolbar_width, self.toolbar_height), pygame.SRCALPHA)

        for y in range(self.toolbar_height):
            alpha = 255 - int((255 / self.toolbar_height) * y)
            shadow_color = (0, 0, 0, alpha)
            shadow_rect = pygame.Rect((0, y), (self.toolbar_width, 1))
            pygame.draw.rect(shadow_surface, shadow_color, shadow_rect)

        screen.blit(shadow_surface, (0, 5))

        main_rect = pygame.Rect((0, 0), (self.toolbar_width, self.toolbar_height))
        pygame.draw.rect(screen, (255, 255, 255), main_rect)

class ToolbarControl:
    def __init__(self, toolbar):
        self.toolbar = toolbar

    def new_game(self):
        self.toolbar.view.game_manager.new_game()

    def save_game(self):
        self.toolbar.view.game_manager.save_game()

    def open_game(self):
        self.toolbar.view.game_manager.open_game()

    def compile(self):
        self.toolbar.view.game_manager.compile()