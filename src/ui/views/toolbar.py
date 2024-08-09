from ui.design.dialog_boxes import UIAutoResizingContainer, UIButton, UITextEntryLine, NewGameDialog, OpenGameDialog, Toast, LoggerWindow
from pygame_gui.core import ObjectID
from ui.design.toast_type import ToastType
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
        
    def create_buttons(self):
        button_width = 100
        button_height = 20
        button_margin = 10

        buttons = [('New Game', '#toolbar_new_game'), ('Save Game', '#toolbar_save_game'), ('Open Game', '#toolbar_open_game'), ('Preview App', '#toolbar_preview'), ('Compile', '#toolbar_compile')]
        toolbar_buttons = []
        
        for i, (text, object_id) in enumerate(buttons):
            toolbar_buttons.append(UIButton(
                relative_rect=pygame.Rect(button_margin * (i + 1) + button_width * i, button_margin, button_width, button_height),
                text=text,
                manager=self.ui_manager,
                container=self.toolbar_container,
                object_id=ObjectID(class_id='@toolbar_button', object_id=object_id)
            ))

        self.input = UITextEntryLine(
            relative_rect=pygame.Rect(button_margin * (len(buttons) + 2) + button_width * len(buttons) - 30, 5, 300, 30),
            manager=self.ui_manager,
            container=self.toolbar_container,
            object_id='#toolbar_input',
            initial_text=self.game_manager.game_name,
        )
        toolbar_buttons.append(self.input)
        return toolbar_buttons
        

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
        self.view_controller.compilling = True
        self.view_controller.active_dialog = LoggerWindow(self.ui_manager)
        self.game_manager.logger.subscribe(self.view_controller.active_dialog.log)
        self.view_controller.active_toast = Toast(self.ui_manager, 'Compiling...', ToastType.INFO)
        self.game_manager.compile()
    
    def disable_toolbar(self):
        for button in self.toolbar.toolbar_buttons:
            button.disable()

    def enable_toolbar(self):
        for button in self.toolbar.toolbar_buttons:
            button.enable()

    def enable_preview(self):
        self.view_controller.preview_window = self.game_manager.open_preview_window()