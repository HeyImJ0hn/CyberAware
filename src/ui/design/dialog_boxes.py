import pygame
import pygame_gui
import colorsys
from pygame_gui.elements import *
from pygame_gui.core import ObjectID
from config.settings import Settings
from ui.design.toast_type import ToastType

class NewGameDialog(UIWindow):
    def __init__(self, ui_manager, game_name="", file_path=""):
        WIDTH, HEIGHT = 440, 210
        super().__init__(pygame.Rect((ui_manager.window_resolution[0]/2-WIDTH/2, ui_manager.window_resolution[1]/2-HEIGHT/2), (WIDTH, HEIGHT)), ui_manager,
                         window_display_title='New Game',
                         object_id='#new_game_dialog',
                         resizable=False)
        
        self.game_name_label = UILabel(relative_rect=pygame.Rect((28, 20), (100, 30)), text="Name", manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@new_game_dialog_label', object_id='#name_label'))
        self.game_name = UITextEntryLine(relative_rect=pygame.Rect((128, 20), (250, 30)), manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@new_game_dialog_input', object_id='#name_input'), initial_text=game_name)
        
        self.file_path_label = UILabel(relative_rect=pygame.Rect((28, 80), (100, 30)), text="Save Path", manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@new_game_dialog_label', object_id='#file_label'))
        self.file_path = UITextEntryLine(relative_rect=pygame.Rect((128, 80), (250, 30)), manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@new_game_dialog_input', object_id='#file_input'), initial_text=file_path)
        self.browse_button = UIButton(relative_rect=pygame.Rect((378, 80), (30, 30)), text="...", manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@new_game_dialog_button', object_id='#browse_button'))
        
        self.create_button = UIButton(relative_rect=pygame.Rect((90, 140), (110, 30)), text="CREATE", manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@new_game_dialog_button', object_id='#create_button'))
        self.cancel_button = UIButton(relative_rect=pygame.Rect((WIDTH-90-90, 140), (110, 30)), text="CANCEL", manager=self.ui_manager, container=self, object_id=ObjectID(class_id='@new_game_dialog_button', object_id='#cancel_button'))

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
        action_long_desc='Are you sure you want to remove the node? This action cannot be undone.',
        action_short_name='Remove',
        blocking=True,
        object_id=ObjectID(class_id='@confirmation_dialog', object_id='#remove_node')
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

class OpenGameDialog:
    def __init__(self, ui_manager, id):
        self.dialog = pygame_gui.windows.UIFileDialog(
        rect=pygame.Rect(160, 50, 440, 500),
        manager=ui_manager,
        window_title='Open Game',
        allow_picking_directories=False,
        allow_existing_files_only=True,
        object_id=id,
        allowed_suffixes={"json"}
        )

class Toast(UIWindow):
    def __init__(self, ui_manager, toast_text, toast_type: ToastType):
        self.shape_corner_radius = 24
        screen_res = Settings.RESOLUTION
        HEIGHT = 60
        WIDTH = len(toast_text) * 15
        padding = 20
        toolbar_height = 40

        font = pygame.font.Font("fonts/Roboto-Regular.ttf", 20)  
        text_width, _ = font.size(toast_text)
        
        min_width = 100 
        max_width = screen_res[0] - 2 * padding 
        
        WIDTH = min(max(text_width + 80, min_width), max_width)
        
        object_id = '#success_toast' if toast_type == ToastType.SUCCESS else '#error_toast' if toast_type == ToastType.ERROR else '#info_toast'
        image = 'static/check-solid.svg' if toast_type == ToastType.SUCCESS else 'static/xmark-solid.svg' if toast_type == ToastType.ERROR else 'static/info-solid.svg'

        super().__init__(pygame.Rect((screen_res[0] - WIDTH - padding, toolbar_height + padding), (WIDTH, HEIGHT)), ui_manager,
                        window_display_title='Toast',
                        object_id=object_id,
                        always_on_top=True,
                        draggable=False)
        
        icon_pos = (16, HEIGHT/2-10) if toast_type == ToastType.INFO else (20, HEIGHT/2-10)
        icon_size = (22.5*1.2, 18.5*1.2) if toast_type == ToastType.INFO else (17.5, 22.5)
        
        self.icon = UIImage(relative_rect=pygame.Rect(icon_pos, icon_size), image_surface=pygame.image.load(image), manager=self.ui_manager, container=self, object_id=ObjectID(class_id=f'@{toast_type.name.lower()}_popup_icon', object_id='#icon'))
        self.message = UILabel(relative_rect=pygame.Rect((28, 0), (WIDTH-28, HEIGHT)), text=toast_text, manager=self.ui_manager, container=self, object_id=ObjectID(class_id=f'@{toast_type.name.lower()}_popup_label', object_id='#message_label'))

class BrowseMediaDialog:
    def __init__(self, ui_manager, id):
        self.dialog = pygame_gui.windows.UIFileDialog(
        rect=pygame.Rect(160, 50, 440, 500),
        manager=ui_manager,
        window_title='Browse Media',
        allow_picking_directories=False,
        allow_existing_files_only=True,
        object_id=id,
        allowed_suffixes={"png", "jpg", "jpeg", "mp4", "mov", "avi", "wmv", "wav"}
        )
        
    def alive(self):
        return self.dialog.alive()
    
    def kill(self):
        return self.dialog.kill()

class ColourPickerDialog:
    def __init__(self, ui_manager, initial_colour=(215, 215, 215)):
        self.dialog = pygame_gui.windows.UIColourPickerDialog(
        rect=pygame.Rect(160, 50, 440, 350),
        manager=ui_manager,
        window_title='Select Colour',
        object_id='#colour_picker_dialog',
        initial_colour=self.rgb_to_hsva(*initial_colour)
        )

    def rgb_to_hsva(self, r, g, b, alpha=1.0):
        r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
        h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
        return pygame.Color(h, s, v, alpha)
    
class LoggerWindow(UIWindow):
    def __init__(self, ui_manager):
        WIDTH, HEIGHT = 800, 600
        super().__init__(pygame.Rect((ui_manager.window_resolution[0]/2-WIDTH/2, ui_manager.window_resolution[1]/2-HEIGHT/2), (WIDTH, HEIGHT)), ui_manager,
                         window_display_title='Logger',
                         object_id='#logger_window',
                         always_on_top=True,
                         resizable=False)
        
        self.log = UITextBox(
            relative_rect=pygame.Rect((10, 10), (WIDTH-20, HEIGHT-80)),
            manager=self.ui_manager,
            html_text="",
            container=self,
            object_id=ObjectID(class_id='@logger_window', object_id='#log')
        )
        
        self.button = UIButton(relative_rect=pygame.Rect((WIDTH-100, HEIGHT-70), (90, 30)), 
                 text="Dismiss", 
                 manager=self.ui_manager, 
                 container=self,
                 object_id=ObjectID(class_id='@logger_window_button', object_id='#logger_dismiss_button'))
        
        self.button.disable()
        
class CompileDialog(UIWindow):
    def __init__(self, ui_manager):
        WIDTH, HEIGHT = 400, 200
        super().__init__(pygame.Rect((ui_manager.window_resolution[0]/2-WIDTH/2, ui_manager.window_resolution[1]/2-HEIGHT/2), (WIDTH, HEIGHT)), ui_manager,
                         window_display_title='Compile Game',
                         object_id='#compile_dialog',
                         always_on_top=True,
                         resizable=False)
        
        self.log = UILabel(
            relative_rect=pygame.Rect((10, 10), (WIDTH-20, HEIGHT-80)),
            manager=self.ui_manager,
            text="Generate Signed App Bundle or Debug APK?",
            container=self,
            object_id=ObjectID(class_id='@compile_dialog', object_id='#info')
        )
        
        self.button_signed = UIButton(relative_rect=pygame.Rect((WIDTH-200, HEIGHT-70), (150, 30)), 
                 text="Signed App Bundle", 
                 manager=self.ui_manager, 
                 container=self,
                 object_id=ObjectID(class_id='@compile_dialog_button', object_id='#compile_signed_button'))
        
        self.button_debug = UIButton(relative_rect=pygame.Rect((WIDTH-350, HEIGHT-70), (150, 30)), 
                 text="Debug APK", 
                 manager=self.ui_manager, 
                 container=self,
                 object_id=ObjectID(class_id='@compile_dialog_button', object_id='#compile_debug_button'))
        
class RequestKeyDialog(UIWindow):
    def __init__(self, ui_manager, game_manager):
        WIDTH, HEIGHT = 500, 250  
        super().__init__(pygame.Rect((ui_manager.window_resolution[0]/2-WIDTH/2, ui_manager.window_resolution[1]/2-HEIGHT/2), (WIDTH, HEIGHT)), ui_manager,
                         window_display_title='Request Key',
                         object_id='#request_key_dialog',
                         always_on_top=True,
                         resizable=False)

        label_width = 150
        entry_width = WIDTH - label_width - 30

        self.key_store_path_label = UILabel(relative_rect=pygame.Rect((10, 20), (label_width, 30)),
                                            text="Key store path", 
                                            manager=self.ui_manager, 
                                            container=self, 
                                            object_id=ObjectID(class_id='@request_key_dialog_label', object_id='#key_store_path_label'))
        
        self.key_store_path = UITextEntryLine(relative_rect=pygame.Rect((label_width + 20, 20), (entry_width, 30)), 
                                              manager=self.ui_manager, 
                                              container=self, 
                                              object_id=ObjectID(class_id='@request_key_dialog_input', object_id='#key_store_path'), 
                                              initial_text=game_manager.keystore.get_path() if game_manager.keystore else "")
        
        self.button_create_new = UIButton(relative_rect=pygame.Rect((WIDTH - 280, 60), (130, 30)), 
                 text="Create new", 
                 manager=self.ui_manager, 
                 container=self,
                 object_id=ObjectID(class_id='@request_key_dialog_button', object_id='#create_new_button'))
        
        self.button_browse = UIButton(relative_rect=pygame.Rect((WIDTH - 140, 60), (130, 30)), 
                 text="Choose existing...", 
                 manager=self.ui_manager, 
                 container=self,
                 object_id=ObjectID(class_id='@request_key_dialog_button', object_id='#browse_key_button'))

        self.key_store_password_label = UILabel(relative_rect=pygame.Rect((10, 100), (label_width, 30)),
                                            text="Key store password", 
                                            manager=self.ui_manager, 
                                            container=self, 
                                            object_id=ObjectID(class_id='@request_key_dialog_label', object_id='#key_store_password_label'))
        
        self.key_store_password = UITextEntryLine(relative_rect=pygame.Rect((label_width + 20, 100), (entry_width, 30)), 
                                              manager=self.ui_manager, 
                                              container=self, 
                                              object_id=ObjectID(class_id='@request_key_dialog_input', object_id='#key_store_password'), 
                                              initial_text=game_manager.keystore.get_store_password() if game_manager.keystore else "")
        self.key_store_password.set_text_hidden(True)
        
        self.app_version_label = UILabel(relative_rect=pygame.Rect((10, 140), (label_width, 30)),
                                            text="App version",
                                            manager=self.ui_manager,
                                            container=self,
                                            object_id=ObjectID(class_id='@request_key_dialog_label', object_id='#app_version_label'))
        self.app_version_input = UITextEntryLine(relative_rect=pygame.Rect((label_width + 20, 140), (entry_width, 30)),
                                                    manager=self.ui_manager,
                                                    container=self,
                                                    object_id=ObjectID(class_id='@request_key_dialog_input', object_id='#app_version_input'),
                                                    initial_text=str(game_manager.app_version))
        self.app_version_input.tool_tip_text = "Numbers only"

        self.button_next = UIButton(relative_rect=pygame.Rect((WIDTH-140, HEIGHT-70), (130, 30)),
                                    text="Compile",
                                    manager=self.ui_manager,
                                    container=self,
                                    object_id=ObjectID(class_id='@request_key_dialog_button', object_id='#compile_button'))
        
        self.button_cancel = UIButton(relative_rect=pygame.Rect((WIDTH-280, HEIGHT-70), (130, 30)),
                                      text="Cancel",
                                      manager=self.ui_manager,
                                      container=self,
                                      object_id=ObjectID(class_id='@request_key_dialog_button', object_id='#cancel_button'))
        
        
class BrowseKeystore:
    def __init__(self, ui_manager, id):
        self.dialog = pygame_gui.windows.UIFileDialog(
        rect=pygame.Rect(160, 50, 440, 500),
        manager=ui_manager,
        window_title='Browse Keystore',
        allow_picking_directories=False,
        allow_existing_files_only=True,
        object_id=id,
        always_on_top=True,
        allowed_suffixes={"jks"}
        )
        
        
    def alive(self):
        return self.dialog.alive()
    
    def kill(self):
        return self.dialog.kill()

##### UNUSED #####
class CreateKeyDialog(UIWindow):
    def __init__(self, ui_manager):
        WIDTH, HEIGHT = 500, 550
        super().__init__(pygame.Rect((ui_manager.window_resolution[0]/2-WIDTH/2, ui_manager.window_resolution[1]/2-HEIGHT/2), (WIDTH, HEIGHT)), ui_manager,
                         window_display_title='New Key Store',
                         object_id='#new_key_store_dialog',
                         always_on_top=True,
                         resizable=False)

        label_width = 150
        entry_width = WIDTH - label_width - 60
        y_offset = 20

        self.key_store_path_label = UILabel(relative_rect=pygame.Rect((10, y_offset), (label_width, 30)),
                                            text="Key store path:", 
                                            manager=self.ui_manager, 
                                            container=self, 
                                            object_id=ObjectID(class_id='@new_key_store_dialog_label', object_id='#key_store_path_label'))
        
        self.key_store_path = UITextEntryLine(relative_rect=pygame.Rect((label_width + 20, y_offset), (entry_width - 22, 30)), 
                                              manager=self.ui_manager, 
                                              container=self, 
                                              object_id=ObjectID(class_id='@new_key_store_dialog_input', object_id='#key_store_path'), 
                                              initial_text="")
        
        self.button_browse = UIButton(relative_rect=pygame.Rect((WIDTH - 69, y_offset), (30, 30)), 
                                      text="...", 
                                      manager=self.ui_manager, 
                                      container=self,
                                      object_id=ObjectID(class_id='@new_key_store_dialog_button', object_id='#browse_button'))
        
        y_offset += 40

        # Password and Confirm
        self.password_label = UILabel(relative_rect=pygame.Rect((10, y_offset), (label_width, 30)),
                                      text="Key Store Password:", 
                                      manager=self.ui_manager, 
                                      container=self, 
                                      object_id=ObjectID(class_id='@new_key_store_dialog_label', object_id='#password_label'))
        
        self.password_entry = UITextEntryLine(relative_rect=pygame.Rect((label_width + 20, y_offset), (entry_width, 30)), 
                                              manager=self.ui_manager, 
                                              container=self, 
                                              object_id=ObjectID(class_id='@new_key_store_dialog_input', object_id='#password_entry'), 
                                              initial_text="")
        
        y_offset += 40

        self.key_alias_label = UILabel(relative_rect=pygame.Rect((10, y_offset), (label_width, 30)),
                                       text="Alias:", 
                                       manager=self.ui_manager, 
                                       container=self, 
                                       object_id=ObjectID(class_id='@new_key_store_dialog_label', object_id='#key_alias_label'))
        
        self.key_alias_entry = UITextEntryLine(relative_rect=pygame.Rect((label_width + 20, y_offset), (entry_width, 30)), 
                                               manager=self.ui_manager, 
                                               container=self, 
                                               object_id=ObjectID(class_id='@new_key_store_dialog_input', object_id='#key_alias_entry'), 
                                               initial_text="mykey")
        
        y_offset += 40

        self.key_password_label = UILabel(relative_rect=pygame.Rect((10, y_offset), (label_width, 30)),
                                          text="Key Password:", 
                                          manager=self.ui_manager, 
                                          container=self, 
                                          object_id=ObjectID(class_id='@new_key_store_dialog_label', object_id='#key_password_label'))
        
        self.key_password_entry = UITextEntryLine(relative_rect=pygame.Rect((label_width + 20, y_offset), (entry_width, 30)), 
                                                  manager=self.ui_manager, 
                                                  container=self, 
                                                  object_id=ObjectID(class_id='@new_key_store_dialog_input', object_id='#key_password_entry'), 
                                                  initial_text="")
        
        y_offset += 40
        
        self.validity = 25        
        
        y_offset += 40

        certificate_fields = [
            "First and Last Name:",
            "Organizational Unit:",
            "Organization:",
            "City or Locality:",
            "State or Province:",
            "Country Code (XX):"
        ]
        self.certificate_entries = []
        for field in certificate_fields:
            label = UILabel(relative_rect=pygame.Rect((10, y_offset), (label_width, 30)),
                            text=field, 
                            manager=self.ui_manager, 
                            container=self, 
                            object_id=ObjectID(class_id='@new_key_store_dialog_label', object_id=f'#{field.split(" ")[0].lower()}_label'))
            
            entry = UITextEntryLine(relative_rect=pygame.Rect((label_width + 20, y_offset), (entry_width, 30)), 
                                    manager=self.ui_manager, 
                                    container=self, 
                                    object_id=ObjectID(class_id='@new_key_store_dialog_input', object_id=f'#{field.split(" ")[0]}_entry'), 
                                    initial_text="")
            self.certificate_entries.append((label, entry))
            y_offset += 40

        self.button_ok = UIButton(relative_rect=pygame.Rect((WIDTH-110, HEIGHT-70), (90, 30)),
                                  text="OK",
                                  manager=self.ui_manager,
                                  container=self,
                                  object_id=ObjectID(class_id='@new_key_store_dialog_button', object_id='#ok_button'))
        
        self.button_cancel = UIButton(relative_rect=pygame.Rect((WIDTH-210, HEIGHT-70), (90, 30)),
                                      text="Cancel",
                                      manager=self.ui_manager,
                                      container=self,
                                      object_id=ObjectID(class_id='@new_key_store_dialog_button', object_id='#cancel_button'))
        
        