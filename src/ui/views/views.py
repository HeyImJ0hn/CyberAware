import pygame
import pygame_gui
from pygame_gui.elements import *
from pygame_gui.windows import *
from pygame_gui.core import ObjectID

import sys

class View:
    def __init__(self):
        pygame.init()
        WIDTH, HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("CyberAware - Plataforma")
        self.ui_manager = pygame_gui.UIManager((WIDTH, HEIGHT), 'theme.json')
        self.clock = pygame.time.Clock()

        self.view_controller = ViewController(self)
        pass

    def run(self):
        while True:
            self.UI_REFRESH_RATE = self.clock.tick(60)/1000
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
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                        self.view_controller.ui_button_pressed(event)
            
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

    def mouse_button_down(self, event):
        if isinstance(self.view, BuildView):
            self.mouse_pos = pygame.mouse.get_pos()
            for entity in self.view.entity_manager.entities:
                if entity.wasBodyClicked(self.mouse_pos[0], self.mouse_pos[1]):
                    self.view.dragging_entity = entity
                    self.offset_x = entity.body.rect.x - self.mouse_pos[0] 
                    self.offset_y = entity.body.rect.y - self.mouse_pos[1]
                    break

    def mouse_button_up(self, event):
        if isinstance(self.view, BuildView):
            self.view.dragging_entity = None
            current_pos = pygame.mouse.get_pos()
            if self.mouse_pos == current_pos:
                for entity in self.view.entity_manager.entities:
                    if entity.wasButtonClicked(current_pos[0], current_pos[1]):
                        print("Button clicked")
                    if entity.wasBodyClicked(current_pos[0], current_pos[1]):
                        print("Entity clicked")
                        self.view.entity_manager.openMenu(entity)

    def mouse_motion(self, event):
        if isinstance(self.view, BuildView):
            if self.view.dragging_entity:
                mouse_pos = pygame.mouse.get_pos()
                dx = mouse_pos[0] + self.offset_x - self.view.dragging_entity.body.rect.x
                dy = mouse_pos[1] + self.offset_y - self.view.dragging_entity.body.rect.y
                self.view.dragging_entity.update_position(dx, dy)

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

class BuildView(View):
    def __init__(self):
        super().__init__()

        self.toolbar = Toolbar(self)

        self.dragging_entity = None

    def render(self):
        super().render()
        
        self.toolbar.draw(self.screen)

        self.update_display()

class HomeView(View):
    def __init__(self):
        super().__init__()

        self.controller = HomeViewControl(self)

        label_width = 220
        button_width = 220

        UILabel(relative_rect=pygame.Rect((self.screen.get_width()/2 - label_width/2, 100), (label_width, 50)), text='CyberAware', object_id='#title', manager=self.ui_manager)
        UILabel(relative_rect=pygame.Rect((self.screen.get_width()/2 - label_width/2 + 5, 145), (label_width, 50)), text='Plataforma', object_id='#subtitle', manager=self.ui_manager)

        UIButton(relative_rect=pygame.Rect((self.screen.get_width()/2 - button_width/2, 350), (button_width, 50)), text='New Game', 
                 object_id=ObjectID(class_id='@main_menu_button', object_id='#new_game_button'), manager=self.ui_manager)

        UIButton(relative_rect=pygame.Rect((self.screen.get_width()/2 - button_width/2, 425), (button_width, 50)), text='Open Game', 
                 object_id=ObjectID(class_id='@main_menu_button', object_id='#open_game_button'), manager=self.ui_manager)

        UIButton(relative_rect=pygame.Rect((self.screen.get_width()/2 - button_width/2, 500), (button_width, 50)), text='Quit', 
                 object_id=ObjectID(class_id='@main_menu_button', object_id='#quit_button'), manager=self.ui_manager)
        
    def render(self):
        super().render()
        
        self.update_display()

class HomeViewControl:
    def __init__(self, view):
        self.view = view

    def new_game(self):
        self.view.ui_manager.clear_and_reset()
        self.view = BuildView()
        self.view.run()

    def open_game(self):
        pass

    def quit(self):
        pygame.quit()
        sys.exit()

class Toolbar:
    def __init__(self, view):
        self.view = view

        self.controller = ToolbarControl(self)

        self.toolbar_height = 40
        self.toolbar_width = 800

        self.toolbar_container = UIAutoResizingContainer(
            relative_rect=pygame.Rect(0, 0, self.toolbar_width, self.toolbar_height),
            manager=self.view.ui_manager
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

    def draw(self, screen):
        shadow_surface = pygame.Surface((self.toolbar_width, self.toolbar_height), pygame.SRCALPHA)

        for y in range(self.toolbar_height):
            alpha = 255 - int((255 / self.toolbar_height) * y)
            shadow_color = (0, 0, 0, alpha)
            shadow_rect = pygame.Rect((0, y), (self.toolbar_width, 1))
            pygame.draw.rect(shadow_surface, shadow_color, shadow_rect)

        screen.blit(shadow_surface, (0, 3))

        main_rect = pygame.Rect((0, 0), (800, self.toolbar_height))
        pygame.draw.rect(screen, (255, 255, 255), main_rect)

class ToolbarControl:
    def __init__(self, toolbar):
        self.toolbar = toolbar

    def new_game(self):
        self.toolbar.view.ui_manager.clear_and_reset()
        self.toolbar.view = BuildView()
        self.toolbar.view.run()

    def save_game(self):
        pass

    def open_game(self):
        self.file_dialog = UIFileDialog(pygame.Rect(160, 50, 440, 500),
                                                    self.toolbar.view.ui_manager,
                                                    window_title='Open Game',
                                                    allow_picking_directories=False,
                                                    allow_existing_files_only=True,
                                                    allowed_suffixes={""})

    def compile(self):
        pass
    
if __name__ == "__main__":
    view = HomeView()
    view.run()