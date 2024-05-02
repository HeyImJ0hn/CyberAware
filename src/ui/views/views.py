import pygame
import pygame_gui
from pygame_gui.elements import *
import sys

class View:
    def __init__(self):
        pygame.init()
        WIDTH, HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("CyberAware - Plataforma")
        self.ui_manager = pygame_gui.UIManager((WIDTH, HEIGHT))
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
        if event.ui_object_id == 'new_game_button':
            self.view.ui_manager.clear_and_reset()
            self.view = BuildView()
            self.view.run()
        elif event.ui_object_id == 'open_game_button':
            pass
        elif event.ui_object_id == 'quit_button':
            pygame.quit()
            sys.exit()

class BuildView(View):
    def __init__(self):
        super().__init__()

    def render(self):
        super().render()
        
        self.update_display()

class HomeView(View):
    def __init__(self):
        super().__init__()

        UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)), text='New Game', object_id='new_game_button', manager=self.ui_manager)
        UIButton(relative_rect=pygame.Rect((350, 350), (100, 50)), text='Open Game', object_id='open_game_button', manager=self.ui_manager)
        UIButton(relative_rect=pygame.Rect((350, 425), (100, 50)), text='Quit', object_id='quit_button', manager=self.ui_manager)
        
    def render(self):
        super().render()
        
        self.update_display()

class Toolbar:
    def __init__(self):
        self.button_width = 100
        self.button_height = 20
        self.button_margin = 10
        self.toolbar_height = 40

        self.toolbar_buttons = [
            {"text": "Button 1", "rect": pygame.Rect(self.button_margin, self.button_margin, self.button_width, self.button_height)},
            {"text": "Button 2", "rect": pygame.Rect(self.button_margin * 2 + self.button_width, self.button_margin, self.button_width, self.button_height)}
        ]

    def draw(self, screen):
        pygame.draw.rect(screen, (200, 200, 200), (0, 0, 800, self.toolbar_height))

        for button in self.toolbar_buttons:
            pygame.draw.rect(screen, (0, 255, 0), button["rect"])
            font = pygame.font.Font(None, 18)
            text_surface = font.render(button["text"], True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=button["rect"].center)
            screen.blit(text_surface, text_rect)

class ToolbarControl:
    def __init__(self, toolbar):
        self.toolbar = toolbar

    def open_file():
        pass

    def save_file():
        pass

    def new_file():
        pass

    def compile():
        pass
    
    def exit():
        sys.exit()

if __name__ == "__main__":
    view = HomeView()
    view.run()