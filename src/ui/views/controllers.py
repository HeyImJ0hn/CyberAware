from ui.design.dialog_boxes import *
from ui.views.view_types import ViewType
from ui.design.toast_type import ToastType
from dao.terminal_dao import TerminalDao
import sys

class ViewController:
    def __init__(self, view):
        self.view = view
        self.game_manager = view.game_manager
        self.ui_manager = view.ui_manager

        # Toast
        self.active_toast = None
        self.toast_duration = 2000
        self.toast_start_time = 0
        
        self.mouse_pos = None
        self.space_pressed = False
        self.dragging_entity_id = None
        self.hovering_entity_id = None
        self.open_menu = None
        self.current_entity_id = None

        self.new_game_dialog = None
        self.active_dialog = None
        self.extra_dialog = None

        self.ctrl_pressed = False
        self.current_entity_option_id = None
        self.draw_to_cursor = False

        self.view_offset = (0, 0)

        self.preview_window = None
        
        self.compilling = False
        self.generating_key = False
        
    def show_toast(self, toast_text, toast_type):
        if self.active_toast:
            self.active_toast.kill()
        self.active_toast = Toast(self.ui_manager, toast_text, toast_type)
        self.toast_start_time = pygame.time.get_ticks()

    def mouse_button_down(self, event):
        if not self.view.type == ViewType.BUILD:
            return
        
        self.mouse_pos = pygame.mouse.get_pos()

        if self.active_dialog:
            return

        for entity in self.game_manager.get_entities():
            if entity.hidden:
                continue

            mouse_x, mouse_y = self.mouse_pos[0], self.mouse_pos[1]

            if not self.ctrl_pressed:
                self.handle_no_ctrl(entity, mouse_x, mouse_y)
            else:
                self.handle_ctrl(entity, mouse_x, mouse_y)
    
    def mouse_button_up(self, event):
        if not self.view.type == ViewType.BUILD:
            return
        
        self.dragging_entity_id = None
        current_pos = pygame.mouse.get_pos()

        if self.active_dialog:
            return

        for entity in self.game_manager.get_entities():
            if self.current_entity_option_id and self.draw_to_cursor:
                self.handle_draw_to_cursor(entity, current_pos)
            
            if self.should_handle_click(current_pos, entity):
                self.handle_entity_click(entity)
                
        self.draw_to_cursor = False

        self.mouse_pos = None

    def mouse_motion(self, event):
        if not self.view.type == ViewType.BUILD or self.mouse_pos is None:
            return

        mouse_pos = pygame.mouse.get_pos()

        if self.space_pressed:
            self.handle_space_pressed(mouse_pos)
        elif self.ctrl_pressed and self.current_entity_option_id:
            self.handle_ctrl_pressed(mouse_pos)
        elif self.dragging_entity_id:
            self.handle_dragging_entity(mouse_pos)

    def ui_file_dialog_path_picked(self, event):
        print("ui_file_dialog_path_picked")
        handlers = {
            '#save_path_dialog': self.handle_save_path_dialog,
            '#open_path_dialog': self.handle_open_path_dialog,
            '#browse_media_dialog': self.handle_browse_media_dialog,
            '#browse_keystore_dialog': self.handle_browse_keystore
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
            '#entity_menu.#browse_button': self.browse_media,
            '#browse_media_dialog.#cancel_button': self.clear_active_dialog,
            '#remove_node.#confirm_button': self.confirm_remove_node,
            '#remove_node.#cancel_button': self.cancel_remove_node,
            '#colour_picker_dialog.#cancel_button': self.cancel_colour_picker,
            '#colour_picker_dialog.#close_button': self.cancel_colour_picker,
            '#logger_window.#logger_dismiss_button': self.clear_active_dialog,
            '#compile_dialog.#close_button': self.clear_active_dialog,
            '#compile_dialog.#compile_signed_button': self.compile_signed_dialog,
            '#compile_dialog.#compile_debug_button': self.compile_debug,
            '#request_key_dialog.#browse_key_button': self.browse_keystore,
            '#request_key_dialog.#close_button': self.clear_active_dialog,
            '#request_key_dialog.#cancel_button': self.clear_active_dialog
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
        elif event.ui_object_id == '#new_game_dialog.#cancel_button':
            self.cancel_new_game(event)
        elif event.ui_object_id.startswith('#recent_list.'):
            self.handle_open_game_from_list(event)
        elif event.ui_object_id == '#new_key_store_dialog.#ok_button':
            self.create_key(event)
        elif event.ui_object_id == '#request_key_dialog.#compile_button':
            self.compile_signed(event)
        elif event.ui_object_id == '#request_key_dialog.#create_new_button':
            self.create_key_dialog(event)
    
    def mouse_hover(self):
        if not self.view.type == ViewType.BUILD or self.active_dialog:
            return

        current_pos = pygame.mouse.get_pos()
        self.reset_cursor_and_hovering_entity(current_pos)

        for entity in self.game_manager.get_entities():
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

        self.game_manager.update_resolution((event.w, event.h))
        self.ui_manager.set_window_resolution(self.view.resolution)

        WIDTH, HEIGHT = self.view.resolution
        if not self.view.type == ViewType.HOME:
            return
        
        self.ui_manager.clear_and_reset()
        
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
            self.game_manager.update_game_name(event.text)
            self.show_toast('Game name updated', ToastType.SUCCESS)

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
        
        if self.open_menu and self.open_menu.entity.id == entity.id:
            if entity.menu == menu:
                entity.menu = None
                self.set_open_menu(None)

    def ui_colour_picker_colour_picked(self, event):
        entity = self.game_manager.get_entity(self.current_entity_id)
        entity.update_colour((event.colour.r, event.colour.g, event.colour.b))
        self.active_dialog = None
        self.current_entity_id = None

    def quit(self):
        self.game_manager.save_settings()
        pygame.quit()
        sys.exit()
        
    ##########################
    #### Helper functions ####
    ##########################
    def compile_signed_dialog(self):
        self.clear_active_dialog()
        #self.disable_toolbar()
        self.active_dialog = RequestKeyDialog(self.ui_manager, self.game_manager)
        
    def create_key_dialog(self, event):
        #self.clear_active_dialog()
        #self.extra_dialog = CreateKeyDialog(self.ui_manager)
        self.show_toast('Key Generation Started', ToastType.INFO)
        self.generating_key = True
        TerminalDao.start_key_generation(self.game_manager.game_to_file_name(self.game_manager.game_name).split(".")[0])
            
    def handle_key_generation_finish(self):
        self.generating_key = False
        self.show_toast('Key Generation Completed', ToastType.SUCCESS)
        keystore = self.game_manager.get_keystore_path()
        self.active_dialog.key_store_path.set_text(keystore)
        
    def create_key(self, event):
        key_store_path = event.ui_element.ui_container.parent_element.key_store_path.get_text()
        key_store_password = event.ui_element.ui_container.parent_element.password_entry.get_text()
        key_alias = event.ui_element.ui_container.parent_element.key_alias_entry.get_text()
        key_password = event.ui_element.ui_container.parent_element.key_password_entry.get_text()
        
        first_last_name = event.ui_element.ui_container.parent_element.certificate_entries[0][1].get_text()
        organizational_unit = event.ui_element.ui_container.parent_element.certificate_entries[1][1].get_text()
        organization = event.ui_element.ui_container.parent_element.certificate_entries[2][1].get_text()
        city = event.ui_element.ui_container.parent_element.certificate_entries[3][1].get_text()
        state = event.ui_element.ui_container.parent_element.certificate_entries[4][1].get_text()
        country_code = event.ui_element.ui_container.parent_element.certificate_entries[5][1].get_text()
        
        result = self.game_manager.generate_key(key_alias=key_alias, key_password=key_password, keystore_password=key_store_password, 
                                     keystore_name=key_store_path, name=first_last_name, org_unit=organizational_unit, 
                                     org=organization, city=city, state=state, country=country_code)
        
        if result == 0:
            self.clear_extra_dialog()
            self.clear_active_dialog()
            self.active_dialog = RequestKeyDialog(self.ui_manager, self.game_manager)
            self.show_toast('Key generated', ToastType.SUCCESS)
        else:
            self.show_toast('Key generation failed', ToastType.ERROR)
        
    def compile_debug(self):
        self.compile(False)
        
    def compile_signed(self, event):
        self.compile(True, event)
        
    def compile(self, signed, event=None):
        self.clear_active_dialog()
        #self.disable_toolbar()
        self.compilling = True
        #self.active_dialog = LoggerWindow(self.ui_manager)
        #self.game_manager.logger.subscribe(self.active_dialog.log)
        self.active_toast = Toast(self.ui_manager, 'Compiling...', ToastType.INFO)
        
        if signed:
            key_store_path = event.ui_element.ui_container.parent_element.key_store_path.get_text()
            key_store_password = event.ui_element.ui_container.parent_element.key_store_password.get_text()
            app_version = event.ui_element.ui_container.parent_element.app_version_input.get_text()
            self.game_manager.app_version = app_version
            self.game_manager.set_keystore(key_store_path, key_store_password)
            
        self.game_manager.compile(signed)
    
    def handle_compilation_finish(self):
        self.compilling = False
        #self.active_dialog.log.set_text("".join(self.game_manager.compilation_logs))
        #self.active_dialog.button.enable()
        self.game_manager.finished_compiling = False
        self.game_manager.compilation_logs = []
        self.show_toast('Compilation finished', ToastType.SUCCESS)
        self.view.toolbar.controller.enable_toolbar()
    
        self.game_manager.move_build_folder()
    
    def handle_open_game_from_list(self, event):
        game_path = event.ui_object_id.split('#recent_list.')[1]
        self.game_manager.open_game(game_path)
    
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
        self.active_dialog = ConfirmationDialog(self.ui_manager)
        self.current_entity_id = entity.id

    def open_colour_picker(self, entity):
        self.active_dialog = ColourPickerDialog(self.ui_manager, entity.colour)
        self.current_entity_id = entity.id
        
    def handle_draw_to_cursor(self, entity, current_pos):
        if not entity.was_body_clicked(current_pos[0], current_pos[1]):
            return
        
        entity_option = self.game_manager.get_entity(self.current_entity_option_id)
        
        if entity_option.final:
            self.show_toast('Cannot add to final screen', ToastType.ERROR)
        elif entity in self.game_manager.get_parents(entity_option):
            self.show_toast('Cannot add parent screen', ToastType.ERROR)
        elif any(option.entity.id == entity.id for option in entity_option.options):
            self.show_toast('Option already exists', ToastType.ERROR)
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
            self.show_toast('Max options reached', ToastType.ERROR)
        else:
            self.game_manager.add_entity(entity)
            if self.open_menu and self.open_menu.entity.id == entity.id:
                self.refresh_menu(entity)

    def refresh_menu(self, entity_option):
        if self.open_menu:
            self.open_menu.kill()
            entity_option.refresh_menu((self.open_menu.rect.x, self.open_menu.rect.y))
            self.set_open_menu(entity_option.menu)
            
    def handle_space_pressed(self, mouse_pos):
        dx, dy = self.get_delta(mouse_pos)
        self.view_offset = (self.view_offset[0] + dx, self.view_offset[1] + dy)
        self.mouse_pos = mouse_pos
        self.move_all_entities(dx, dy)

    def handle_ctrl_pressed(self, mouse_pos):
        mouse_pos = pygame.mouse.get_pos()

    def handle_dragging_entity(self, mouse_pos):
        entity = self.game_manager.get_entity(self.dragging_entity_id)
        dx = mouse_pos[0] + self.offset_x - entity.body.rect.x
        dy = mouse_pos[1] + self.offset_y - entity.body.rect.y
        entity.move(dx, dy)

    def get_delta(self, mouse_pos):
        return mouse_pos[0] - self.mouse_pos[0], mouse_pos[1] - self.mouse_pos[1]

    def move_all_entities(self, dx, dy):
        for entity in self.game_manager.get_entities():
            entity.move(dx, dy)
            
    def handle_save_path_dialog(self, text):
        self.game_manager.file_path = text
        self.new_game_dialog.update_file_path(text)

    def handle_open_path_dialog(self, text):
        self.game_manager.open_game(text)

    def handle_browse_media_dialog(self, text):
        self.game_manager.submit_media(text, self.open_menu.entity)
        #self.open_menu.kill()
        #self.open_menu.entity.refresh_menu((self.open_menu.rect.x, self.open_menu.rect.y))
        self.refresh_menu(self.open_menu.entity)
        self.active_dialog = None
        
    def handle_browse_keystore(self, text):
        self.active_dialog.key_store_path.set_text(text)
        self.clear_extra_dialog()
        
    def browse_new_game_path(self):
        SavePathDialog(self.ui_manager, '#save_path_dialog')

    def create_new_game(self, event):
        #game_name = self.get_ui_element_text('#new_game_dialog.#game_name')
        #file_path = self.get_ui_element_text('#new_game_dialog.#file_path')
        game_name = event.ui_element.ui_container.parent_element.game_name
        file_path = event.ui_element.ui_container.parent_element.file_path
        self.game_manager.game_name = game_name
        self.game_manager.path = file_path
        self.game_manager.new_game()

    def cancel_new_game(self, event):
        self.active_dialog = None
        #self.kill_ui_element('#new_game_dialog')
        event.ui_element.ui_container.parent_element.kill()
        self.game_manager.game_name = ""
        self.game_manager.file_path = ""
        self.enable_home_or_toolbar_buttons()

    def browse_media(self):
        self.set_active_dialog(BrowseMediaDialog(self.ui_manager, '#browse_media_dialog'))
        
    def browse_keystore(self):
        self.set_extra_dialog(BrowseKeystore(self.ui_manager, '#browse_keystore_dialog'))

    def confirm_remove_node(self):
        entity = self.game_manager.get_entity(self.current_entity_id)
        
        if self.game_manager.remove_entity(entity):
            self.show_toast('Removed node', ToastType.SUCCESS)
            if self.open_menu and self.open_menu.entity.id == self.current_entity_id:
                self.open_menu.kill()
        else:
            self.show_toast('Cannot remove node with connected options', ToastType.ERROR)
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
        if self.view.type == ViewType.BUILD:
            self.view.toolbar.controller.enable_toolbar()
        elif self.view.type == ViewType.HOME:
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
            self.show_toast('Set Screen to Final', ToastType.SUCCESS) if self.open_menu.final_checkbox.text == "X" else self.show_toast('Unset Screen to Final', ToastType.SUCCESS)
        else:
            self.show_toast('Final screen cannot have options', ToastType.ERROR)

    def remove_entity_option(self, ui_element):
        option = self.open_menu.entity.get_option_from_menu(ui_element)
        if len(self.game_manager.get_parents(option.entity)) > 1:
            self.open_menu.entity.remove_option(option.entity)
            entity = self.open_menu.entity
            self.refresh_menu(entity)
            self.show_toast('Removed Option', ToastType.SUCCESS)
        else:
            self.show_toast('Cannot remove option', ToastType.ERROR)

    def handle_preview_window_option_button(self, event):
        entity = self.preview_window.entity
        pos = self.preview_window.rect.topleft
        self.preview_window.kill()
        self.preview_window = self.game_manager.open_preview_window(entity.options[int(event.ui_object_id.split('_')[-1])].entity)
        self.preview_window.set_position(pos)

    def handle_preview_window_final_button(self):
        pos = self.preview_window.rect.topleft
        self.preview_window.kill()
        self.preview_window = self.game_manager.open_preview_window()
        self.preview_window.set_position(pos)

    def set_active_dialog(self, dialog):
        self.active_dialog = dialog
        
    def set_extra_dialog(self, dialog):
        self.extra_dialog = dialog

    def clear_active_dialog(self):
        if self.active_dialog.alive():
            self.active_dialog.kill()
        self.active_dialog = None
        self.view.toolbar.controller.enable_toolbar()
        
    def clear_extra_dialog(self):
        if self.extra_dialog.alive():
            self.extra_dialog.kill()
        self.extra_dialog = None

    def get_ui_element_text(self, element_id):
        #event.ui_element.ui_container.parent_element.
        return self.ui_manager.get_ui_element(element_id).get_text()

    def kill_ui_element(self, element_id):
        self.ui_manager.get_ui_element(element_id).kill()

    def enable_home_or_toolbar_buttons(self):
        if self.view.type == ViewType.HOME:
            for b in self.view.buttons:
                b.enable()
        else:
            self.view.toolbar.controller.enable_toolbar()
            
    def reset_cursor_and_hovering_entity(self, current_pos):
        if not self.hovering_entity_id:
            return
        
        entity = self.game_manager.get_entity(self.hovering_entity_id)
        
        if (entity == None or not self.space_pressed and not entity.hidden and 
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
            self.show_toast('Saved', ToastType.SUCCESS)
            
    def handle_space_key_up(self, event):
        self.space_pressed = False
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def handle_ctrl_key_up(self, event):
        self.ctrl_pressed = False
        self.current_entity_option_id = None
        self.draw_to_cursor = False
        
    def handle_toolbar_action(self, action_name):
        if not self.view.type == ViewType.BUILD:
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
        if not self.view.type == ViewType.HOME:
            return
        
        controller = self.view.controller
        action_methods = {
            'new_game': controller.new_game,
            'open_game': controller.open_game,
            'quit': controller.quit
        }
        return action_methods.get(action_name)
    
    def set_open_menu(self, menu):
        self.open_menu = menu
        
    def disable_toolbar(self):
        self.view.toolbar.controller.disable_toolbar()
        
    def enable_toolbar(self):
        self.view.toolbar.controller.enable_toolbar()
        
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