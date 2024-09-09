from ui.design.dialogboxes.dialog_boxes import *
from pygame_gui.core import ObjectID
from ui.design.dialogboxes.toast_type import ToastType
import pygame

class Toolbar:
    def __init__(self, view):
        self.view = view
        self.view_controller = view.view_controller
        self.game_manager = view.game_manager
        self.ui_manager = view.ui_manager

        self.controller = ToolbarControl(self)

        self.toolbar_height = 40
        self.toolbar_width = self.view.resolution[0]

        self.toolbar_container = UIAutoResizingContainer(
            relative_rect=pygame.Rect(0, 0, self.toolbar_width, self.toolbar_height),
            manager=self.ui_manager,
            object_id='@toolbar'
        )
        
        self.toolbar_buttons = self.create_buttons()
        self.file_dropdown_menu = None
        self.run_dropdown_menu = None
        self.is_file_dropdown_visible = False
        self.is_run_dropdown_visible = False
        
    def create_buttons(self):
        button_width = 40
        button_height = 20
        button_margin = 10

        toolbar_buttons = []
        
        buttons = [('File', '#toolbar_file'), ('Run', '#toolbar_run')]
        for i, (text, object_id) in enumerate(buttons):
            rect = pygame.Rect(button_margin + (button_margin + button_width) * i, button_margin, button_width, button_height)
            toolbar_buttons.append(UIButton(
                relative_rect=rect,
                text=text,
                manager=self.ui_manager,
                container=self.toolbar_container,
                object_id=ObjectID(class_id='@toolbar_button', object_id=object_id)
            ))

        #self.input = UITextEntryLine(
        #    relative_rect=pygame.Rect(button_margin * (len(buttons) + 1) + button_width * (len(buttons) + 1) - 30, 5, 300, 30),
        #    manager=self.ui_manager,
        #    container=self.toolbar_container,
        #    object_id='#toolbar_input',
        #    initial_text=self.game_manager.game_name,
        #)
        
        #toolbar_buttons.append(self.input)
        return toolbar_buttons
        
    def create_file_dropdown(self, position):
        dropdown_buttons = [('New', '#toolbar_new_game'), ('Open', '#toolbar_open_game'), ('Save', '#toolbar_save_game'), ('', ''), ('Settings', '#toolbar_settings')]
        self.file_buttons = []
        self.file_dropdown_menu = self.create_dropdown(position, dropdown_buttons, self.file_buttons)
        
    def create_run_dropdown(self, position):
        dropdown_buttons = [('Preview App', '#toolbar_preview'), ('Compile', '#toolbar_compile')]
        self.run_buttons = []
        self.run_dropdown_menu = self.create_dropdown(position, dropdown_buttons, self.run_buttons)
            
    def create_dropdown(self, position, buttons, list):
        button_width = 100
        button_height = 20
        button_margin = 6
        padding = 6

        dropdown_height = len(buttons) * (button_height + button_margin) - button_margin + padding*2

        dropdown = UIAutoResizingContainer(
            relative_rect=pygame.Rect(position[0], position[1], button_width + padding*2, dropdown_height),
            manager=self.ui_manager,
            object_id='@toolbar_dropdown'
        )
        
        for i, (text, object_id) in enumerate(buttons):
            if text == '': continue
            y = padding + i * (button_height + button_margin)
            rect = pygame.Rect(padding, y, button_width, button_height)
            list.append(UIButton(
                relative_rect=rect,
                text=text,
                manager=self.ui_manager,
                container=dropdown,
                object_id=ObjectID(class_id='@toolbar_dropdown_button', object_id=object_id)
            ))
        return dropdown
            
    def show_file_dropdown(self):
        if not self.is_file_dropdown_visible:
            self.create_file_dropdown((self.toolbar_buttons[0].relative_rect.left, self.toolbar_buttons[0].relative_rect.bottom))
            self.is_file_dropdown_visible = True

    def hide_file_dropdown(self):
        if self.is_file_dropdown_visible:
            self.file_dropdown_menu.kill()
            self.file_dropdown_menu = None
            self.is_file_dropdown_visible = False
            
    def hover_file_button(self, mouse_pos):
        if self.toolbar_buttons[0].relative_rect.collidepoint(mouse_pos):
            self.show_file_dropdown()
        elif self.is_file_dropdown_visible:
            if not self.file_dropdown_menu.get_rect().collidepoint(mouse_pos):
                self.hide_file_dropdown()
                
    def show_run_dropdown(self):
        if not self.is_run_dropdown_visible:
            self.create_run_dropdown((self.toolbar_buttons[1].relative_rect.left, self.toolbar_buttons[1].relative_rect.bottom))
            self.is_run_dropdown_visible = True

    def hide_run_dropdown(self):
        if self.is_run_dropdown_visible:
            self.run_dropdown_menu.kill()
            self.run_dropdown_menu = None
            self.is_run_dropdown_visible = False
            
    def hover_run_button(self, mouse_pos):
        if self.toolbar_buttons[1].relative_rect.collidepoint(mouse_pos):
            self.show_run_dropdown()
        elif self.is_run_dropdown_visible:
            if not self.run_dropdown_menu.get_rect().collidepoint(mouse_pos):
                self.hide_run_dropdown()

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
        pygame.draw.rect(screen, (47, 51, 61), main_rect)
        
        game_name = self.game_manager.game_name
        font = pygame.font.Font(None, 28)
        text = font.render(game_name, True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.center = (self.toolbar_width // 2, self.toolbar_height // 2)
        screen.blit(text, text_rect)
        
        if self.is_file_dropdown_visible or self.is_run_dropdown_visible:
            dropdown_rect = self.file_dropdown_menu.get_rect() if self.is_file_dropdown_visible else self.run_dropdown_menu.get_rect()
            shadow_offset = 5
            for y in range(shadow_offset):
                alpha = 100 - int((100 / shadow_offset) * y)
                shadow_color = (0, 0, 0, alpha)
                pygame.draw.rect(screen, shadow_color, dropdown_rect, border_radius=6)
                
            background_color = (40, 44, 52) 
            pygame.draw.rect(screen, background_color, dropdown_rect, border_radius=6)
            
            if self.is_file_dropdown_visible:
                line_rect = self.file_buttons[3].rect
                pygame.draw.aaline(screen, (255, 255, 255), (line_rect.left + 6, line_rect.top-16), (line_rect.right - 6, line_rect.top-16))
        
class ToolbarControl:
    def __init__(self, toolbar):
        self.toolbar = toolbar
        self.view_controller = toolbar.view_controller
        self.game_manager = toolbar.game_manager
        self.ui_manager = toolbar.ui_manager

    def new_game(self):
        self.disable_toolbar()
        dialog = NewGameDialog(self.ui_manager)
        self.view_controller.new_game_dialog = dialog
        self.view_controller.active_dialog = dialog

    def save_game(self):
        self.game_manager.save_game()
        self.view_controller.show_toast('Saved', ToastType.SUCCESS)

    def open_game(self):
        self.disable_toolbar()
        OpenGameDialog(self.ui_manager, '#open_path_dialog')

    def compile(self):
        self.view_controller.active_dialog = CompileDialog(self.ui_manager)
        self.disable_toolbar()
        
    def settings(self):
        try:
            pygame.image.load(self.game_manager.icon_path)
        except FileNotFoundError:
            self.view_controller.show_toast('Missing File: App Icon', ToastType.ERROR)
        else:
            self.view_controller.active_dialog = SettingsDialog(self.ui_manager, self.game_manager)
    
    def disable_toolbar(self):
        for button in self.toolbar.toolbar_buttons:
            button.disable()

    def enable_toolbar(self):
        for button in self.toolbar.toolbar_buttons:
            button.enable()

    def enable_preview(self):
        if self.game_manager.is_file_missing():
            self.view_controller.show_toast('Missing Media Files', ToastType.ERROR)
        else:
            self.view_controller.preview_window = self.game_manager.open_preview_window()