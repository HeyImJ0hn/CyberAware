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

class ViewController:
    def __init__(self, view):
        self.view = view

        self.mouse_pos = None
        self.space_pressed = False
        self.dragging_entity = None
        self.hovering_entity = None
        self.open_menu = None
        self.current_entity = None

        self.new_game_dialog = None
        self.active_dialog = None

        self.active_toast = None
        self.toast_duration = 2000
        self.toast_start_time = 0

        self.ctrl_pressed = False
        self.current_entity_option = None
        self.draw_to_cursor = False

        self.view_offset = (0, 0)

        self.preview_window = None

    def show_toast(self, toast_text, toast_type):
        if self.active_toast:
            self.active_toast.kill()
        self.active_toast = Toast(self.view.ui_manager, toast_text, toast_type)
        self.toast_start_time = pygame.time.get_ticks()

    def mouse_button_down(self, event):
        if isinstance(self.view, BuildView):
            self.mouse_pos = pygame.mouse.get_pos()

            if not self.active_dialog:
                for entity in self.view.game_manager.get_entities():
                    if entity.hidden:
                        continue
                    if not self.ctrl_pressed:
                        if entity.was_menu_clicked(self.mouse_pos[0], self.mouse_pos[1]):
                            pass
                        elif entity.was_button_clicked(self.mouse_pos[0], self.mouse_pos[1]):
                                if len(entity.options) >= entity.max_options:
                                    self.show_toast('Max options reached', 'error')
                                else:
                                    self.view.game_manager.add_entity(entity)
                                    if self.open_menu and self.open_menu.entity.id == entity.id:
                                        self.open_menu.kill()
                                        entity.refresh_menu((self.open_menu.rect.x, self.open_menu.rect.y))
                                        self.open_menu = entity.menu
                        elif entity.was_body_clicked(self.mouse_pos[0], self.mouse_pos[1]) and not (self.open_menu and self.open_menu.is_inside(self.mouse_pos[0], self.mouse_pos[1])): 
                            self.dragging_entity = entity
                            self.offset_x = entity.body.rect.x - self.mouse_pos[0] 
                            self.offset_y = entity.body.rect.y - self.mouse_pos[1]
                        elif entity.was_hide_button_clicked(self.mouse_pos[0], self.mouse_pos[1]):
                            entity.toggle_options()
                        elif entity.was_remove_button_clicked(self.mouse_pos[0], self.mouse_pos[1]):
                            self.active_dialog = ConfirmationDialog(self.view.ui_manager)
                            self.current_entity = entity
                        elif entity.was_colour_button_clicked(self.mouse_pos[0], self.mouse_pos[1]):
                            self.active_dialog = ColourPickerDialog(self.view.ui_manager, entity.colour)
                            self.current_entity = entity
                    else:
                        if entity.was_body_clicked(self.mouse_pos[0], self.mouse_pos[1]):
                            self.current_entity_option = entity
                            self.draw_to_cursor = True

    def mouse_button_up(self, event):
        if isinstance(self.view, BuildView):
            self.dragging_entity = None

            current_pos = pygame.mouse.get_pos()
            if not self.active_dialog:
                for entity in self.view.game_manager.get_entities():
                    if self.current_entity_option and self.draw_to_cursor:
                        if entity.was_body_clicked(current_pos[0], current_pos[1]):
                            if self.current_entity_option.final:
                                self.show_toast('Cannot add to final screen', 'error')
                            elif entity in self.view.game_manager.get_parents(self.current_entity_option):
                                self.show_toast('Cannot add parent screen', 'error')
                            else:
                                self.current_entity_option.add_option(entity)
                
                                if self.open_menu:
                                    self.open_menu.kill()
                                    self.current_entity_option.refresh_menu((self.open_menu.rect.x, self.open_menu.rect.y))
                                    self.open_menu = self.current_entity_option.menu
            
                            self.current_entity_option = None
                            self.draw_to_cursor = False

                    if self.mouse_pos == current_pos and not self.space_pressed and not entity.hidden:
                            if entity.was_body_clicked(current_pos[0], current_pos[1]) and not (self.open_menu and self.open_menu.is_inside(current_pos[0], current_pos[1])):
                                if not self.open_menu:
                                    entity.open_menu()
                                    self.open_menu = entity.menu
                                else:
                                    self.open_menu.kill()
                                    entity.open_menu()
                                    self.open_menu = entity.menu

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
                elif self.ctrl_pressed and self.current_entity_option:
                    mouse_pos = pygame.mouse.get_pos()
                else:
                    if self.dragging_entity:
                        mouse_pos = pygame.mouse.get_pos()
                        dx = mouse_pos[0] + self.offset_x - self.dragging_entity.body.rect.x
                        dy = mouse_pos[1] + self.offset_y - self.dragging_entity.body.rect.y
                        self.dragging_entity.move(dx, dy)

    def ui_file_dialog_path_picked(self, event):
        if event.ui_object_id == '#save_path_dialog':
            self.view.game_manager.file_path = event.text
            self.new_game_dialog.update_file_path(event.text)
        elif event.ui_object_id == '#open_path_dialog':
            self.view.game_manager.open_game(event.text)
        elif event.ui_object_id == '#browse_media_dialog':
            self.view.game_manager.submit_media(event.text, self.open_menu.entity)
            self.open_menu.kill()
            self.open_menu.entity.refresh_menu((self.open_menu.rect.x, self.open_menu.rect.y))
            self.active_dialog = None

    def ui_button_pressed(self, event):
        print(event.ui_object_id)
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
        elif event.ui_object_id == '@toolbar.#toolbar_preview':
            self.view.toolbar.controller.enable_preview()
        elif event.ui_object_id == '@toolbar.#toolbar_compile':
            self.view.toolbar.controller.compile()

        elif event.ui_object_id == '#new_game_dialog.#browse_button':
            SavePathDialog(self.view.ui_manager, '#save_path_dialog')

        elif event.ui_object_id == '#new_game_dialog.#create_button':
            self.view.game_manager.game_name = event.ui_element.ui_container.parent_element.game_name.get_text()
            self.view.game_manager.path = event.ui_element.ui_container.parent_element.file_path.get_text()
            self.view.game_manager.new_game()
        elif event.ui_object_id == '#new_game_dialog.#cancel_button':
            self.active_dialog = None
            event.ui_element.ui_container.parent_element.kill()
            self.view.game_manager.game_name = ""
            self.view.game_manager.file_path = ""
            if isinstance(self.view, HomeView):
                for b in self.view.buttons:
                    b.enable()
            else:
                self.view.toolbar.controller.enable_toolbar()

        elif event.ui_object_id == '#file_dialog.#cancel_button' or event.ui_object_id == '#file_dialog.#close_button' \
            or event.ui_object_id == '#file_dialog.#ok_button':
            if isinstance(self.view, BuildView):
                self.view.toolbar.controller.enable_toolbar()

        elif event.ui_object_id == '#entity_menu.#browse_button':
            self.active_dialog = BrowseMediaDialog(self.view.ui_manager, '#browse_media_dialog')
        elif event.ui_object_id == '#browse_media_dialog.#ok_button':
            self.active_dialog = None
        elif event.ui_object_id == '#browse_media_dialog.#cancel_button':
            self.active_dialog = None
        elif event.ui_object_id == '#remove_node.#confirm_button':
            if self.view.game_manager.remove_entity(self.current_entity):
                self.show_toast('Removed node', 'success')
                if self.open_menu and self.open_menu.entity.id == self.current_entity.id:
                    self.open_menu.kill()
                    self.open_menu = None
            else:
                self.show_toast('Cannot remove node with connected options', 'error')
            self.current_entity = None
            self.active_dialog = None
        elif event.ui_object_id == '#remove_node.#cancel_button':
            self.current_entity = None
            self.active_dialog = None

        elif event.ui_object_id == '#colour_picker_dialog.#cancel_button':
            self.active_dialog = None
            self.current_entity = None

        elif event.ui_object_id == '#open_path_dialog.#cancel_button' or event.ui_object_id == '#open_path_dialog.#close_button':
            self.active_dialog = None
            if isinstance(self.view, BuildView):
                self.view.toolbar.controller.enable_toolbar()
            elif isinstance(self.view, HomeView):
                for b in self.view.buttons:
                    b.enable()

        elif event.ui_object_id == '#entity_menu.#final_checkbox':
            if len(self.open_menu.entity.options) == 0:
                self.open_menu.final_checkbox.set_text("X" if self.open_menu.final_checkbox.text == "" else "")
                self.show_toast('Set Screen to Final', 'success') if self.open_menu.final_checkbox.text == "X" else self.show_toast('Unset Screen to Final', 'success')
            else:
                self.show_toast('Final screen cannot have options', 'error')
        elif event.ui_object_id == '#entity_menu.#option_remove_button':
            option = self.open_menu.entity.get_option_from_menu(event.ui_element)
            if len(self.view.game_manager.get_parents(option.entity)) > 1:
                self.open_menu.entity.remove_option(option.entity)
                entity = self.open_menu.entity
                self.open_menu.kill()
                entity.refresh_menu((self.open_menu.rect.x, self.open_menu.rect.y))
                self.open_menu = entity.menu
                self.show_toast('Removed Option', 'success')
            else:
                self.show_toast('Cannot remove option', 'error')

        # Preview Window                
        elif '#preview_window.#option_button_' in event.ui_object_id:
            option = int(event.ui_object_id.split('_')[-1])
            entity = self.preview_window.entity
            pos = self.preview_window.rect.topleft
            self.preview_window.kill()
            self.preview_window = self.view.game_manager.open_preview_window(entity.options[option].entity)
            self.preview_window.set_position(pos)
        elif event.ui_object_id == '#preview_window.#final_button':
            pos = self.preview_window.rect.topleft
            self.preview_window.kill()
            self.preview_window = self.view.game_manager.open_preview_window()
            self.preview_window.set_position(pos)


    def mouse_hover(self):
        if isinstance(self.view, BuildView) and not self.active_dialog:
            if self.hovering_entity and not self.space_pressed and not self.hovering_entity.hidden and \
                not (self.open_menu and self.open_menu.is_inside(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.hovering_entity = None

            for entity in self.view.game_manager.get_entities():
                entity.hovered = False
                current_pos = pygame.mouse.get_pos()
                if entity.was_button_clicked(current_pos[0], current_pos[1]) or entity.was_body_clicked(current_pos[0], current_pos[1]) \
                    or entity.was_hide_button_clicked(current_pos[0], current_pos[1]) or entity.was_remove_button_clicked(current_pos[0], current_pos[1]) \
                        or entity.was_colour_button_clicked(current_pos[0], current_pos[1]):
                    if not entity.was_menu_clicked(current_pos[0], current_pos[1]):
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
            self.show_toast('Saved', 'success')

    def key_up(self, event):
        if event.key == pygame.K_SPACE:
            self.space_pressed = False
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        elif event.key == pygame.K_LCTRL:
            self.ctrl_pressed = False
            self.current_entity_option = None
            self.draw_to_cursor = False

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
        if event.ui_object_id == '@toolbar.#toolbar_input':
            self.view.game_manager.update_game_name(event.text)
            self.show_toast('Game name updated', 'success')

    def menu_kill(self, event):
        entity = event.entity
        menu = event.ui_element
        entity.update_properties(menu.name.get_text(), menu.text.get_text(), menu.notes.get_text(), menu.final_checkbox.text=="X")
        entity.update_options(menu.options)
        entity.menu = None
        self.open_menu = None

    def ui_colour_picker_colour_picked(self, event):
        self.current_entity.update_colour((event.colour.r, event.colour.g, event.colour.b))
        self.active_dialog = None
        self.current_entity = None

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
        
        if self.view_controller.draw_to_cursor:
            pygame.draw.aaline(self.screen, (0, 0, 0), self.view_controller.current_entity_option.centroid, pygame.mouse.get_pos())
        
        self.game_manager.draw_entities(self.screen)

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
        for b in self.view.buttons:
            b.disable()

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

        buttons = [('New Game', '#toolbar_new_game'), ('Save Game', '#toolbar_save_game'), ('Open Game', '#toolbar_open_game'), ('Preview App', '#toolbar_preview'), ('Compile', '#toolbar_compile')]
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
        dialog = NewGameDialog(self.toolbar.view.ui_manager)
        self.toolbar.view.view_controller.new_game_dialog = dialog
        self.toolbar.view.view_controller.active_dialog = dialog

    def save_game(self):
        self.toolbar.view.game_manager.save_game()
        self.toolbar.view.view_controller.show_toast('Saved', 'success')

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

    def enable_preview(self):
        self.toolbar.view.view_controller.preview_window = self.toolbar.view.game_manager.open_preview_window()