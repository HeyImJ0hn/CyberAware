import pygame
import pygame_gui
from pygame_gui.elements import *
from pygame_gui.core import ObjectID
import os

class NewGameDialog(UIWindow):
    def __init__(self, ui_manager, game_name="", file_path=""):
        WIDTH, HEIGHT = 440, 240
        super().__init__(pygame.Rect((ui_manager.window_resolution[0]/2-WIDTH/2, ui_manager.window_resolution[1]/2-HEIGHT/2), (WIDTH, HEIGHT)), ui_manager,
                         window_display_title='New Game',
                         object_id='#new_game_dialog',
                         resizable=False)
        
        self.game_name_label = UILabel(relative_rect=pygame.Rect((28, 40), (100, 30)), text="Name", manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@new_game_dialog_label', object_id='#name_label'))
        self.game_name = UITextEntryLine(relative_rect=pygame.Rect((128, 40), (250, 30)), manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@new_game_dialog_input', object_id='#name_input'), initial_text=game_name)
        
        self.file_path_label = UILabel(relative_rect=pygame.Rect((28, 100), (100, 30)), text="Save Path", manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@new_game_dialog_label', object_id='#file_label'))
        self.file_path = UITextEntryLine(relative_rect=pygame.Rect((128, 100), (250, 30)), manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@new_game_dialog_input', object_id='#file_input'), initial_text=file_path)
        self.browse_button = UIButton(relative_rect=pygame.Rect((378, 100), (30, 30)), text="...", manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@new_game_dialog_button', object_id='#browse_button'))
        
        self.create_button = UIButton(relative_rect=pygame.Rect((100, 180), (100, 30)), text="CREATE", manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@new_game_dialog_button', object_id='#create_button'))
        self.cancel_button = UIButton(relative_rect=pygame.Rect((WIDTH-100-100, 180), (100, 30)), text="CANCEL", manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@new_game_dialog_button', object_id='#cancel_button'))

    def update_name(self, game_name):
        self.game_name.set_text(game_name)

    def update_file_path(self, file_path):
        self.file_path.set_text(file_path)

class ConfirmationDialog:
    def __init__(self, ui_manager):
        pygame_gui.windows.UIConfirmationDialog(
        rect=pygame.Rect(200, 150, 400, 200),
        manager=ui_manager,
        window_title='Remove Node',
        action_long_desc='Are you sure you want to proceed? This action cannot be undone.',
        action_short_name='Proceed',
        blocking=True
        )

class SavePathDialog:
    def __init__(self, ui_manager, id):
        self.dialog = pygame_gui.windows.UIFileDialog(
        rect=pygame.Rect(160, 50, 440, 500),
        manager=ui_manager,
        window_title='Select Save Path',
        allow_picking_directories=True,
        allow_existing_files_only=False,
        object_id=id,
        allowed_suffixes={"."}
        )