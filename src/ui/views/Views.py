import pygame
import pygame_gui
from pygame_gui.elements import *
from pygame_gui.windows import *
from pygame_gui.core import ObjectID
from ui.design.DialogBoxes import *
from config.Settings import *

import sys

class View:
    def __init__(self, game_manager):
        self.game_manager = game_manager
        self.resolution = Settings.RESOLUTION
        self.screen = pygame.display.set_mode(self.resolution, pygame.RESIZABLE | pygame.SRCALPHA)

        #if Settings.FULLSCREEN:
        #    Window.from_display_module().maximize()
        
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
                elif event.type == pygame.USEREVENT + 3000:
                    self.view_controller.menu_kill(event)
                    
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

class ViewController:
    def __init__(self, view):
        self.view = view

        self.mouse_pos = None
        self.space_pressed = False
        self.dragging_entity = None
        self.hovering_entity = None
        self.dragging_menu = None
        self.open_menu = None
        self.clicked_outside = True

        self.new_game_dialog = None
        self.media_dialog = None

        self.active_toast = None
        self.toast_duration = 2000
        self.toast_start_time = 0

        self.ctrl_pressed = False

        self.view_offset = (0, 0)

    def mouse_button_down(self, event):
        if isinstance(self.view, BuildView):
            self.mouse_pos = pygame.mouse.get_pos()
            for entity in self.view.game_manager.get_entities():
                if entity.hidden:
                    continue
                if entity.was_button_clicked(self.mouse_pos[0], self.mouse_pos[1]):
                        self.view.game_manager.add_entity(entity)
                        if self.open_menu and self.open_menu.entity.id == entity.id:
                            self.open_menu.kill()
                            entity.refresh_menu((self.open_menu.rect.x, self.open_menu.rect.y))
                            self.open_menu = entity.menu
                elif entity.was_body_clicked(self.mouse_pos[0], self.mouse_pos[1]):
                    if not self.dragging_menu:
                        self.dragging_entity = entity
                        self.offset_x = entity.body.rect.x - self.mouse_pos[0] 
                        self.offset_y = entity.body.rect.y - self.mouse_pos[1]
                elif entity.was_menu_clicked(self.mouse_pos[0], self.mouse_pos[1]):
                    self.offset_x = entity.menu.rect.x - self.mouse_pos[0]
                    self.offset_y = entity.menu.rect.y - self.mouse_pos[1]
                    self.dragging_menu = entity.menu
                elif entity.was_hide_button_clicked(self.mouse_pos[0], self.mouse_pos[1]):
                    entity.toggle_options()
                elif entity.was_remove_button_clicked(self.mouse_pos[0], self.mouse_pos[1]):
                    ConfirmationDialog(self.view.ui_manager)

    def mouse_button_up(self, event):
        if isinstance(self.view, BuildView):
            self.dragging_entity = None
            self.dragging_menu = None
            self.clicked_outside = True

            current_pos = pygame.mouse.get_pos()
            for entity in self.view.game_manager.get_entities():
                if entity.was_menu_clicked(current_pos[0], current_pos[1]) or entity.was_body_clicked(current_pos[0], current_pos[1]) \
                    or entity.was_button_clicked(current_pos[0], current_pos[1]) or entity.was_hide_button_clicked(current_pos[0], current_pos[1]) \
                    or entity.was_remove_button_clicked(current_pos[0], current_pos[1]):
                    self.clicked_outside = False

                if self.mouse_pos == current_pos and not self.space_pressed and not entity.hidden:
                        if entity.was_body_clicked(current_pos[0], current_pos[1]):
                            if not self.open_menu:
                                entity.open_menu()
                                self.open_menu = entity.menu
                            else:
                                self.open_menu.kill()
                                entity.open_menu()
                                self.open_menu = entity.menu

            if not self.media_dialog:
                if self.clicked_outside and self.open_menu:
                    for entity in self.view.game_manager.get_entities():
                        if entity.id == self.open_menu.entity.id:
                            self.open_menu.kill()
                            self.open_menu = None
                            entity.menu = None
                            break

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

    def ui_file_dialog_path_picked(self, event):
        if event.ui_object_id == '#save_path_dialog':
            self.view.game_manager.file_path = event.text
            self.new_game_dialog.update_file_path(event.text)
        elif event.ui_object_id == '#open_path_dialog':
            self.view.game_manager.open_game(event.text)
        elif event.ui_object_id == '#browse_media_dialog':
            self.view.game_manager.submit_media(event.text, self.open_menu.entity)
            self.media_dialog = None

    def ui_button_pressed(self, event):
        if event.ui_object_id == '#new_game_button':
            self.view.controller.new_game()
        elif event.ui_object_id == '#open_game_button':
            self.view.controller.open_game()
        elif event.ui_object_id == '#quit_button':
            self.view.controller.quit()

        elif event.ui_object_id == '@toolbar.#toolbar_new_game':
            self.view.toolbar.controller.new_game()
        elif event.ui_object_id == '@toolbar.#toolbar_save_game':
            self.view.toolbar.controller.save_game()
        elif event.ui_object_id == '@toolbar.#toolbar_open_game':
            self.view.toolbar.controller.open_game()
        elif event.ui_object_id == '@toolbar.#toolbar_compile':
            self.view.toolbar.controller.compile()

        elif event.ui_object_id == '#new_game_dialog.#browse_button':
            SavePathDialog(self.view.ui_manager, '#save_path_dialog')

        elif event.ui_object_id == '#new_game_dialog.#create_button':
            self.view.game_manager.game_name = event.ui_element.ui_container.parent_element.game_name.get_text()
            self.view.game_manager.path = event.ui_element.ui_container.parent_element.file_path.get_text()
            self.view.game_manager.new_game()
        elif event.ui_object_id == '#new_game_dialog.#cancel_button':
            event.ui_element.ui_container.parent_element.kill()
            self.view.game_manager.game_name = ""
            self.view.game_manager.file_path = ""
            for b in self.view.buttons:
                b.enable()

        elif event.ui_object_id == '#file_dialog.#cancel_button' or event.ui_object_id == '#file_dialog.#close_button' \
            or event.ui_object_id == '#file_dialog.#ok_button':
            if isinstance(self.view, BuildView):
                self.view.toolbar.controller.enable_toolbar()

        elif event.ui_object_id == '#entity_menu.#browse_button':
            self.media_dialog = BrowseMediaDialog(self.view.ui_manager, '#browse_media_dialog')
        elif event.ui_object_id == '#browse_media_dialog.#ok_button':
            self.media_dialog = None
        elif event.ui_object_id == '#browse_media_dialog.#cancel_button':
            self.media_dialog = None

        print(event.ui_object_id)
            
    def mouse_hover(self):
        if isinstance(self.view, BuildView):
            if self.hovering_entity and not self.space_pressed and not self.hovering_entity.hidden:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.hovering_entity = None

            for entity in self.view.game_manager.get_entities():
                entity.hovered = False
                current_pos = pygame.mouse.get_pos()
                if entity.was_button_clicked(current_pos[0], current_pos[1]) or entity.was_body_clicked(current_pos[0], current_pos[1]) \
                    or entity.was_hide_button_clicked(current_pos[0], current_pos[1]) or entity.was_remove_button_clicked(current_pos[0], current_pos[1]):
                    entity.hovered = True
                    self.hovering_entity = entity
            
            if not self.hovering_entity and not self.space_pressed:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def key_down(self, event):
        if event.key == pygame.K_SPACE:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
            self.space_pressed = True
        elif event.key == pygame.K_LCTRL:
            self.ctrl_pressed = True
        elif event.key == pygame.K_s and self.ctrl_pressed:
            self.view.game_manager.save_game()
            if self.active_toast:
                self.active_toast.kill()
            self.active_toast = SavedToast(self.view.ui_manager)
            self.toast_start_time = pygame.time.get_ticks()

    def key_up(self, event):
        if event.key == pygame.K_SPACE:
            self.space_pressed = False
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        elif event.key == pygame.K_LCTRL:
            self.ctrl_pressed = False

    def window_resize(self, event):
        self.view.resolution = (event.w, event.h)
        Settings.RESOLUTION = (event.w, event.h)
        Settings.FULLSCREEN = False

        #monitor_res = pygame.display.list_modes()[0]
        #if event.w == monitor_res[0] and event.h >= monitor_res[1] - 80:
        #    Settings.FULLSCREEN = True
        #else:
        #    Settings.RESOLUTION = (event.w, event.h)
        
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

    def ui_text_entry_finished(self, event):
        print(event.ui_object_id, event.text)

    def menu_kill(self, event):
        entity = event.entity
        menu = event.ui_element
        entity.update_properties(menu.name.get_text(), menu.text.get_text(), menu.notes.get_text())

    def quit(self):
        self.view.game_manager.save_settings()
        pygame.quit()
        sys.exit()

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

class HomeViewControl:
    def __init__(self, view):
        self.view = view

    def new_game(self):
        self.view.view_controller.new_game_dialog = NewGameDialog(self.view.ui_manager)
        for b in self.view.buttons:
            b.disable()

    def open_game(self):
        OpenGameDialog(self.view.ui_manager, '#open_path_dialog')

    def quit(self):
        self.view.view_controller.quit()

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
        self.toolbar_buttons = []

        for i, (text, object_id) in enumerate(buttons):
            self.toolbar_buttons.append(UIButton(
                relative_rect=pygame.Rect(button_margin * (i + 1) + button_width * i, button_margin, button_width, button_height),
                text=text,
                manager=self.view.ui_manager,
                container=self.toolbar_container,
                object_id=ObjectID(class_id='@toolbar_button', object_id=object_id)
            ))

        self.input = UITextEntryLine(
            relative_rect=pygame.Rect(button_margin * (len(buttons) + 2) + button_width * len(buttons) - 30, 5, 300, 30),
            manager=self.view.ui_manager,
            container=self.toolbar_container,
            object_id='#toolbar_input',
            initial_text=self.view.game_manager.game_name,
        )
        self.toolbar_buttons.append(self.input)

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
        self.disable_toolbar()
        self.toolbar.view.game_manager.new_game()

    def save_game(self):
        self.toolbar.view.game_manager.save_game()
        self.toolbar.view.view_controller.toast_start_time = pygame.time.get_ticks()
        self.toolbar.view.view_controller.active_toast = SavedToast(self.toolbar.view.ui_manager)

    def open_game(self):
        self.disable_toolbar()
        OpenGameDialog(self.toolbar.view.ui_manager, '#open_path_dialog')

    def compile(self):
        self.toolbar.view.game_manager.compile()
    
    def disable_toolbar(self):
        for button in self.toolbar.toolbar_buttons:
            button.disable()

    def enable_toolbar(self):
        for button in self.toolbar.toolbar_buttons:
            button.enable()