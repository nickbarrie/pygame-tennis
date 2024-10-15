import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, GREEN, SPRITE_SIZE, SCALE_FACTOR
import sys


class Menu:
    def __init__(self, screen, sprite_sheet):
        self.screen = screen
        self.sprite_sheet = sprite_sheet
        self.font = pygame.font.Font('silkscreen.ttf', 32)
        self.plaqueImage = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE), pygame.SRCALPHA)
        self.plaqueEndImage = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE), pygame.SRCALPHA)
        if self.sprite_sheet is not None:
            self.plaqueImage.blit(self.sprite_sheet, (0, 0), (7 * SPRITE_SIZE, 0, SPRITE_SIZE, SPRITE_SIZE))
            self.plaqueEndImage.blit(self.sprite_sheet, (0, 0), (6 * SPRITE_SIZE, 0, SPRITE_SIZE, SPRITE_SIZE))

        self.menu_state = "MAIN"  # Possible states: MAIN, MULTIPLAYER_MENU, HOST_MENU, JOIN_MENU
        self.selected_port = ""  # Input for port number
        self.selected_ip = ""  # Input for IP address
        self.selected_ip_and_port = ""  # Input for IP address and port number
        self.is_hosting = False

    def render_text(self, text, x, y):
        rendered_text = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(rendered_text, (x, y))

    def draw(self):
        self.screen.fill(GREEN)
        scaled_plaque = pygame.transform.scale(self.plaqueImage, (SPRITE_SIZE * SCALE_FACTOR, SPRITE_SIZE * SCALE_FACTOR))
        scaled_plaque_end = pygame.transform.scale(self.plaqueEndImage, (SPRITE_SIZE * SCALE_FACTOR, SPRITE_SIZE * SCALE_FACTOR))
        scaled_plaque_end_flipped = pygame.transform.flip(scaled_plaque_end, True, False)

        # Title rendering
        title_text = self.font.render("Tennis Game", True, (255, 255, 255))
        self.screen.blit(scaled_plaque_end, (WINDOW_WIDTH // 2 - title_text.get_width() // 2 - scaled_plaque.get_width(), 85))
        for i in range(0, title_text.get_width() // scaled_plaque.get_width() + 1):
            self.screen.blit(scaled_plaque, (WINDOW_WIDTH // 2 - title_text.get_width() // 2 + i * scaled_plaque.get_width(), 85))
        self.screen.blit(scaled_plaque_end_flipped, (WINDOW_WIDTH // 2 + title_text.get_width() // 2, 85))
        self.screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 100))

        menu_text_top = ""
        menu_text_bottom = ""

        if self.menu_state == "MAIN":
            menu_text_top = "Press 1 for Single Player"
            menu_text_bottom = "Press 2 for Multiplayer"
            
        elif self.menu_state == "MULTIPLAYER_MENU":
            menu_text_top = "Press 1 to Host Game"
            menu_text_bottom = "Press 2 to Join Game"
        elif self.menu_state == "JOIN_MENU":
            menu_text_top = "Enter IP:Port number"
            menu_text_bottom = self.selected_ip_and_port
        elif self.menu_state == "HOST_MENU":
            menu_text_top = "Enter Port number"
            menu_text_bottom = self.selected_ip_and_port
        
        render_top_text = self.font.render(menu_text_top, True, (255, 255, 255))
        render_bottom_text = self.font.render(menu_text_bottom, True, (255, 255, 255))

        top_text_x = (WINDOW_WIDTH // 2) - (render_top_text.get_width() // 2)
        top_text_y = WINDOW_HEIGHT // 2

        bottom_text_x = (WINDOW_WIDTH // 2) - (render_bottom_text.get_width() // 2)
        bottom_text_y = (WINDOW_HEIGHT // 2) + 50

        self.screen.blit(render_top_text, (top_text_x, top_text_y))
        self.screen.blit(render_bottom_text, (bottom_text_x, bottom_text_y))
        pygame.display.flip()

    def handle_menu_events(self, game_state):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # Handle Main Menu
                if self.menu_state == "MAIN":
                    if event.key == pygame.K_1:
                        return "SINGLE_PLAYER"  # Start single-player game
                    elif event.key == pygame.K_2:
                        self.menu_state = "MULTIPLAYER_MENU"
                # Handle Multiplayer Menu
                elif self.menu_state == "MULTIPLAYER_MENU":
                    if event.key == pygame.K_1:  # Host Game
                        self.menu_state = "HOST_MENU"
                        self.is_hosting = True
                    elif event.key == pygame.K_2:  # Join Game
                        self.menu_state = "JOIN_MENU"
                        self.is_hosting = False
                # Handle hosting/joining
                elif self.menu_state in ["HOST_MENU", "JOIN_MENU"]:
                    if event.key == pygame.K_RETURN:  # Press Enter to host/join
                        try:
                            if self.is_hosting:
                                self.selected_port = self.selected_ip_and_port
                                return "HOST"
                            else:
                                self.selected_port = self.selected_ip_and_port.split(":")[1]
                                self.selected_ip = self.selected_ip_and_port.split(":")[0]
                                return "JOIN"
                        except IndexError:
                            self.selected_ip_and_port = "Invalid IP:Port"
                    elif event.key == pygame.K_BACKSPACE:
                         self.selected_ip_and_port =  self.selected_ip_and_port[:-1]
                    elif event.unicode.isdigit():
                         self.selected_ip_and_port += event.unicode
                    elif event.key == pygame.K_PERIOD:
                         self.selected_ip_and_port += "."
                    elif event.key == pygame.K_SEMICOLON:
                         self.selected_ip_and_port += ":"  

                    

        return game_state
