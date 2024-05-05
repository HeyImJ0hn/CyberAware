import pygame
import pygame_gui
from pygame_gui.elements import *
from pygame_gui.core import ObjectID

class NewGameDialog(UIWindow):
    def __init__(self, ui_manager):
        super().__init__(pygame.Rect((ui_manager.window_resolution[0]//2-240//2, ui_manager.window_resolution[1]//2-100//2), (240, 120)), ui_manager,
                         window_display_title='New Game',
                         object_id='#new_game_dialog',
                         resizable=False)
        
        self.game_name_label = UILabel(relative_rect=pygame.Rect((20, 15), (80, 20)), text="Name", manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@new_game_dialog_label', object_id='#name_label'))
        self.game_name = UITextEntryLine(relative_rect=pygame.Rect((100, 15), (100, 20)), manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@new_game_dialog_input', object_id='#name_input'))
        
        self.file_path_label = UILabel(relative_rect=pygame.Rect((20, 45), (80, 20)), text="Save Path", manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@new_game_dialog_label', object_id='#file_label'))
        self.file_path = UITextEntryLine(relative_rect=pygame.Rect((100, 45), (100, 20)), manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@new_game_dialog_input', object_id='#file_input'))
        self.browse_button = UIButton(relative_rect=pygame.Rect((200, 45), (20, 20)), text="...", manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@new_game_dialog_button', object_id='#browse_button'))
        
        self.create_button = UIButton(relative_rect=pygame.Rect((30, 85), (80, 20)), text="Create", manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@new_game_dialog_button', object_id='#create_button'))
        self.cancel_button = UIButton(relative_rect=pygame.Rect((130, 85), (80, 20)), text="Cancel", manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@new_game_dialog_button', object_id='#cancel_button'))