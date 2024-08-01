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
        self.dragging_entity_id = None
        self.hovering_entity_id = None
        self.open_menu = None
        self.current_entity_id = None

        self.new_game_dialog = None
        self.active_dialog = None

        self.active_toast = None
        self.toast_duration = 2000
        self.toast_start_time = 0

        self.ctrl_pressed = False
        self.current_entity_option_id = None
        self.draw_to_cursor = False

        self.view_offset = (0, 0)

        self.preview_window = None
        
    def show_toast(self, toast_text, toast_type):
        if self.active_toast:
            self.active_toast.kill()
        self.active_toast = Toast(self.view.ui_manager, toast_text, toast_type)
        self.toast_start_time = pygame.time.get_ticks()

    def mouse_button_down(self, event):
        if not isinstance(self.view, BuildView):
            return
        
        self.mouse_pos = pygame.mouse.get_pos()

        if self.active_dialog:
            return

        for entity in self.view.game_manager.get_entities():
            if entity.hidden:
                continue

            mouse_x, mouse_y = self.mouse_pos[0], self.mouse_pos[1]

            if not self.ctrl_pressed:
                self.handle_no_ctrl(entity, mouse_x, mouse_y)
            else:
                self.handle_ctrl(entity, mouse_x, mouse_y)
    
    def mouse_button_up(self, event):
        if not isinstance(self.view, BuildView):
            return
        
        self.dragging_entity_id = None
        current_pos = pygame.mouse.get_pos()

        if self.active_dialog:
            return

        for entity in self.view.game_manager.get_entities():
            if self.current_entity_option_id and self.draw_to_cursor:
                self.handle_draw_to_cursor(entity, current_pos)
            
            if self.should_handle_click(current_pos, entity):
                self.handle_entity_click(entity)
                
        self.draw_to_cursor = False

        self.mouse_pos = None

    def mouse_motion(self, event):
        if not isinstance(self.view, BuildView) or self.mouse_pos is None:
            return

        mouse_pos = pygame.mouse.get_pos()

        if self.space_pressed:
            self.handle_space_pressed(mouse_pos)
        elif self.ctrl_pressed and self.current_entity_option_id:
            self.handle_ctrl_pressed(mouse_pos)
        elif self.dragging_entity_id:
            self.handle_dragging_entity(mouse_pos)

    def ui_file_dialog_path_picked(self, event):
        handlers = {
            '#save_path_dialog': self.handle_save_path_dialog,
            '#open_path_dialog': self.handle_open_path_dialog,
            '#browse_media_dialog': self.handle_browse_media_dialog
        }
        
        handler = handlers.get(event.ui_object_id)
        if handler:
            handler(event.text)

    def ui_button_pressed(self, event):
        print(event.ui_object_id)
        handlers = {
            '#new_game_button': self.handle_controller_action('new_game'),
            '#open_game_button': self.handle_controller_action('open_game'),
            '#quit_button': self.handle_controller_action('quit'),
            '@toolbar.#toolbar_new_game': self.handle_toolbar_action('new_game'),
            '@toolbar.#toolbar_save_game': self.handle_toolbar_action('save_game'),
            '@toolbar.#toolbar_open_game': self.handle_toolbar_action('open_game'),
            '@toolbar.#toolbar_preview': self.handle_toolbar_action('enable_preview'),
            '@toolbar.#toolbar_compile': self.handle_toolbar_action('compile'),
            '#new_game_dialog.#browse_button': self.browse_new_game_path,
            '#new_game_dialog.#create_button': self.create_new_game,
            '#new_game_dialog.#cancel_button': self.cancel_new_game,
            '#entity_menu.#browse_button': self.browse_media,
            '#browse_media_dialog.#ok_button': self.clear_active_dialog,
            '#browse_media_dialog.#cancel_button': self.clear_active_dialog,
            '#remove_node.#confirm_button': self.confirm_remove_node,
            '#remove_node.#cancel_button': self.cancel_remove_node,
            '#colour_picker_dialog.#cancel_button': self.cancel_colour_picker,
            '#colour_picker_dialog.#close_button': self.cancel_colour_picker
        }

        file_dialog_buttons = {'#file_dialog.#cancel_button', '#file_dialog.#close_button', '#file_dialog.#ok_button',
                            '#open_path_dialog.#cancel_button', '#open_path_dialog.#close_button'}

        entity_menu_buttons = {'#entity_menu.#final_checkbox', '#entity_menu.#option_remove_button'}
        
        if event.ui_object_id in handlers:
            handlers[event.ui_object_id]()
        elif event.ui_object_id in file_dialog_buttons:
            self.handle_file_dialog_buttons(event)
        elif event.ui_object_id in entity_menu_buttons:
            self.handle_entity_menu_buttons(event)
        elif '#preview_window.#option_button_' in event.ui_object_id:
            self.handle_preview_window_option_button(event)
        elif event.ui_object_id == '#preview_window.#final_button':
            self.handle_preview_window_final_button()
            
    def mouse_hover(self):
        if not isinstance(self.view, BuildView) or self.active_dialog:
            return

        current_pos = pygame.mouse.get_pos()
        self.reset_cursor_and_hovering_entity(current_pos)

        for entity in self.view.game_manager.get_entities():
            entity.hovered = False
            if self.is_entity_hovered(entity, current_pos):
                entity.hovered = True
                self.hovering_entity_id = entity.id

        if not self.hovering_entity_id and not self.space_pressed:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def key_down(self, event):
        key_actions = {
            pygame.K_SPACE: self.handle_space_key_down,
            pygame.K_LCTRL: self.handle_ctrl_key_down,
            pygame.K_s: self.handle_save_key_down
        }
        
        if event.key in key_actions:
            key_actions[event.key](event)

    def key_up(self, event):
        key_actions = {
            pygame.K_SPACE: self.handle_space_key_up,
            pygame.K_LCTRL: self.handle_ctrl_key_up
        }
        
        if event.key in key_actions:
            key_actions[event.key](event)

    def window_resize(self, event):
        self.view.resolution = (event.w, event.h)
        Settings.RESOLUTION = (event.w, event.h)
        Settings.FULLSCREEN = False

        self.view.game_manager.update_resolution((event.w, event.h))
        self.view.ui_manager.set_window_resolution(self.view.resolution)

        WIDTH, HEIGHT = self.view.resolution
        if not isinstance(self.view, HomeView):
            return
        
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

        entity.update_properties(
            name=menu.name.get_text(),
            text=menu.text.get_text(),
            notes=menu.notes.get_text(),
            final=menu.final_checkbox.text == "X"
        )
        entity.update_options(menu.options)
        
        entity.menu = None
        #self.open_menu = None
        if self.open_menu and self.open_menu.entity.id == entity.id:
            self.set_open_menu(None)

    def ui_colour_picker_colour_picked(self, event):
        entity = self.view.game_manager.get_entity(self.current_entity_id)
        entity.update_colour((event.colour.r, event.colour.g, event.colour.b))
        self.active_dialog = None
        self.current_entity_id = None

    def quit(self):
        self.view.game_manager.save_settings()
        pygame.quit()
        sys.exit()
        
    ##########################
    #### Helper functions ####
    ##########################
    def handle_no_ctrl(self, entity, mouse_x, mouse_y):
        if entity.was_menu_clicked(mouse_x, mouse_y):
            return

        if entity.was_button_clicked(mouse_x, mouse_y):
            self.handle_button_click(entity)
        elif entity.was_body_clicked(mouse_x, mouse_y) and not (self.open_menu and self.open_menu.is_inside(mouse_x, mouse_y)):
            self.start_dragging(entity, mouse_x, mouse_y)
        elif entity.was_hide_button_clicked(mouse_x, mouse_y):
            entity.toggle_options()
        elif entity.was_remove_button_clicked(mouse_x, mouse_y):
            self.start_removal(entity)
        elif entity.was_colour_button_clicked(mouse_x, mouse_y):
            self.open_colour_picker(entity)

    def handle_ctrl(self, entity, mouse_x, mouse_y):
        if entity.was_body_clicked(mouse_x, mouse_y):
            self.current_entity_option_id = entity.id
            self.draw_to_cursor = True
            
    def start_dragging(self, entity, mouse_x, mouse_y):
        self.dragging_entity_id = entity.id
        self.offset_x = entity.body.rect.x - mouse_x
        self.offset_y = entity.body.rect.y - mouse_y

    def start_removal(self, entity):
        self.active_dialog = ConfirmationDialog(self.view.ui_manager)
        self.current_entity_id = entity

    def open_colour_picker(self, entity):
        self.active_dialog = ColourPickerDialog(self.view.ui_manager, entity.colour)
        self.current_entity_id = entity
        
    def handle_draw_to_cursor(self, entity, current_pos):
        if not entity.was_body_clicked(current_pos[0], current_pos[1]):
            return
        
        entity_option = self.view.game_manager.get_entity(self.current_entity_option_id)
        
        if entity_option.final:
            self.show_toast('Cannot add to final screen', 'error')
        elif entity in self.view.game_manager.get_parents(entity_option):
            self.show_toast('Cannot add parent screen', 'error')
        elif any(option.entity.id == entity.id for option in entity_option.options):
            self.show_toast('Option already exists', 'error')
        else:
            entity_option.add_option(entity)
            self.refresh_menu(entity_option)
        
        self.current_entity_option_id = None
        self.draw_to_cursor = False

    def should_handle_click(self, current_pos, entity):
        return (
            self.mouse_pos == current_pos and 
            not self.space_pressed and 
            not entity.hidden and 
            entity.was_body_clicked(current_pos[0], current_pos[1]) and 
            not (self.open_menu and self.open_menu.is_inside(current_pos[0], current_pos[1]))
        )

    def handle_entity_click(self, entity):
        if not self.open_menu:
            entity.open_menu()
            self.set_open_menu(entity.menu)
        elif self.open_menu.entity.id == entity.id:
            self.open_menu.kill()
        elif self.open_menu.entity.id != entity.id:
            self.open_menu.kill()
            entity.open_menu()
            self.set_open_menu(entity.menu)
        else:
            self.refresh_menu(entity)
            
    def handle_button_click(self, entity):
        if len(entity.options) >= entity.max_options:
            self.show_toast('Max options reached', 'error')
        else:
            self.view.game_manager.add_entity(entity)
            if self.open_menu and self.open_menu.entity.id == entity.id:
                self.refresh_menu(entity)

    def refresh_menu(self, entity_option):
        if self.open_menu:
            self.open_menu.kill()
            entity_option.refresh_menu((self.open_menu.rect.x, self.open_menu.rect.y))
            #self.open_menu = entity_option.menu
            self.set_open_menu(entity_option.menu)
            
    def handle_space_pressed(self, mouse_pos):
        dx, dy = self.get_delta(mouse_pos)
        self.view_offset = (self.view_offset[0] + dx, self.view_offset[1] + dy)
        self.mouse_pos = mouse_pos
        self.move_all_entities(dx, dy)

    def handle_ctrl_pressed(self, mouse_pos):
        mouse_pos = pygame.mouse.get_pos()

    def handle_dragging_entity(self, mouse_pos):
        entity = self.view.game_manager.get_entity(self.dragging_entity_id)
        dx = mouse_pos[0] + self.offset_x - entity.body.rect.x
        dy = mouse_pos[1] + self.offset_y - entity.body.rect.y
        entity.move(dx, dy)

    def get_delta(self, mouse_pos):
        return mouse_pos[0] - self.mouse_pos[0], mouse_pos[1] - self.mouse_pos[1]

    def move_all_entities(self, dx, dy):
        for entity in self.view.game_manager.get_entities():
            entity.move(dx, dy)
            
    def handle_save_path_dialog(self, text):
        self.view.game_manager.file_path = text
        self.new_game_dialog.update_file_path(text)

    def handle_open_path_dialog(self, text):
        self.view.game_manager.open_game(text)

    def handle_browse_media_dialog(self, text):
        self.view.game_manager.submit_media(text, self.open_menu.entity)
        self.open_menu.kill()
        self.open_menu.entity.refresh_menu((self.open_menu.rect.x, self.open_menu.rect.y))
        self.active_dialog = None
        
    def browse_new_game_path(self):
        SavePathDialog(self.view.ui_manager, '#save_path_dialog')

    def create_new_game(self):
        game_name = self.get_ui_element_text('#new_game_dialog.#game_name')
        file_path = self.get_ui_element_text('#new_game_dialog.#file_path')
        self.view.game_manager.game_name = game_name
        self.view.game_manager.path = file_path
        self.view.game_manager.new_game()

    def cancel_new_game(self):
        self.active_dialog = None
        self.kill_ui_element('#new_game_dialog')
        self.view.game_manager.game_name = ""
        self.view.game_manager.file_path = ""
        self.enable_home_or_toolbar_buttons()

    def browse_media(self):
        self.set_active_dialog(BrowseMediaDialog(self.view.ui_manager, '#browse_media_dialog'))

    def confirm_remove_node(self):
        entity = self.view.game_manager.get_entity(self.current_entity_id)
        
        if self.view.game_manager.remove_entity(entity):
            self.show_toast('Removed node', 'success')
            if self.open_menu and self.open_menu.entity.id == self.current_entity_id:
                self.open_menu.kill()
        else:
            self.show_toast('Cannot remove node with connected options', 'error')
        self.current_entity_id = None
        self.active_dialog = None

    def cancel_remove_node(self):
        self.current_entity_id = None
        self.active_dialog = None

    def cancel_colour_picker(self):
        self.active_dialog = None
        self.current_entity_id = None

    def handle_file_dialog_buttons(self, event):
        self.active_dialog = None
        if isinstance(self.view, BuildView):
            self.view.toolbar.controller.enable_toolbar()
        elif isinstance(self.view, HomeView):
            for b in self.view.buttons:
                b.enable()

    def handle_entity_menu_buttons(self, event):
        if event.ui_object_id == '#entity_menu.#final_checkbox':
            self.toggle_final_checkbox()
        elif event.ui_object_id == '#entity_menu.#option_remove_button':
            self.remove_entity_option(event.ui_element)

    def toggle_final_checkbox(self):
        if len(self.open_menu.entity.options) == 0:
            self.open_menu.final_checkbox.set_text("X" if self.open_menu.final_checkbox.text == "" else "")
            self.show_toast('Set Screen to Final', 'success') if self.open_menu.final_checkbox.text == "X" else self.show_toast('Unset Screen to Final', 'success')
        else:
            self.show_toast('Final screen cannot have options', 'error')

    def remove_entity_option(self, ui_element):
        option = self.open_menu.entity.get_option_from_menu(ui_element)
        if len(self.view.game_manager.get_parents(option.entity)) > 1:
            self.open_menu.entity.remove_option(option.entity)
            entity = self.open_menu.entity
            self.refresh_menu(entity)
            self.show_toast('Removed Option', 'success')
        else:
            self.show_toast('Cannot remove option', 'error')

    def handle_preview_window_option_button(self, event):
        entity = self.preview_window.entity
        pos = self.preview_window.rect.topleft
        self.preview_window.kill()
        self.preview_window = self.view.game_manager.open_preview_window(entity.options[int(event.ui_object_id.split('_')[-1])].entity)
        self.preview_window.set_position(pos)

    def handle_preview_window_final_button(self):
        pos = self.preview_window.rect.topleft
        self.preview_window.kill()
        self.preview_window = self.view.game_manager.open_preview_window()
        self.preview_window.set_position(pos)

    def set_active_dialog(self, dialog):
        self.active_dialog = dialog

    def clear_active_dialog(self):
        self.active_dialog = None

    def get_ui_element_text(self, element_id):
        return self.view.ui_manager.get_ui_element(element_id).get_text()

    def kill_ui_element(self, element_id):
        self.view.ui_manager.get_ui_element(element_id).kill()

    def enable_home_or_toolbar_buttons(self):
        if isinstance(self.view, HomeView):
            for b in self.view.buttons:
                b.enable()
        else:
            self.view.toolbar.controller.enable_toolbar()
            
    def reset_cursor_and_hovering_entity(self, current_pos):
        if not self.hovering_entity_id:
            return
        
        entity = self.view.game_manager.get_entity(self.hovering_entity_id)
        if (not self.space_pressed and not entity.hidden and 
                not (self.open_menu and self.open_menu.is_inside(current_pos[0], current_pos[1]))):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            self.hovering_entity_id = None

    def is_entity_hovered(self, entity, current_pos):
        return (entity.was_button_clicked(current_pos[0], current_pos[1]) or 
                entity.was_body_clicked(current_pos[0], current_pos[1]) or 
                entity.was_hide_button_clicked(current_pos[0], current_pos[1]) or 
                entity.was_remove_button_clicked(current_pos[0], current_pos[1]) or 
                entity.was_colour_button_clicked(current_pos[0], current_pos[1])) and not entity.was_menu_clicked(current_pos[0], current_pos[1])
        
    def handle_space_key_down(self, event):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        self.space_pressed = True

    def handle_ctrl_key_down(self, event):
        self.ctrl_pressed = True

    def handle_save_key_down(self, event):
        if self.ctrl_pressed:
            self.view.game_manager.save_game()
            self.show_toast('Saved', 'success')
            
    def handle_space_key_up(self, event):
        self.space_pressed = False
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def handle_ctrl_key_up(self, event):
        self.ctrl_pressed = False
        self.current_entity_option_id = None
        self.draw_to_cursor = False
        
    def handle_toolbar_action(self, action_name):
        if not isinstance(self.view, BuildView):
            return None
        
        toolbar_controller = self.view.toolbar.controller
        action_methods = {
            'new_game': toolbar_controller.new_game,
            'save_game': toolbar_controller.save_game,
            'open_game': toolbar_controller.open_game,
            'enable_preview': toolbar_controller.enable_preview,
            'compile': toolbar_controller.compile
        }
        return action_methods.get(action_name)
    
    def handle_controller_action(self, action_name):
        if not isinstance(self.view, HomeView):
            return None
        
        controller = self.view.controller
        action_methods = {
            'new_game': controller.new_game,
            'open_game': controller.open_game,
            'quit': controller.quit
        }
        return action_methods.get(action_name)
    
    def set_open_menu(self, menu):
        self.open_menu = menu

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