import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, GREEN, SPRITE_SIZE, SCALE_FACTOR
import sys

class Menu:
    def __init__(self, screen, sprite_sheet):
        self.screen = screen
        self.sprite_sheet = sprite_sheet
        self.font = pygame.font.Font('silkscreen.ttf', 32)
        self.menu_state = "MAIN"  # Possible states: MAIN, MULTIPLAYER_MENU, HOST_MENU, JOIN_MENU
        self.selected_ip_and_port = ""  # Input for IP address and port number
        self.is_hosting = False

        # Initialize plaque images and scale once
        if sprite_sheet is not None:
            self.plaqueImage = self._get_scaled_sprite(7)
            self.plaqueEndImage = self._get_scaled_sprite(6)
            self.plaqueEndImageFlipped = pygame.transform.flip(self.plaqueEndImage, True, False)

        # Map for menu states and text options
        self.menu_options = {
            "MAIN": ("Press 1 for Single Player", "Press 2 for Multiplayer"),
            "MULTIPLAYER_MENU": ("Press 1 to Host Game", "Press 2 to Join Game"),
            "JOIN_MENU": ("Enter IP:Port", self.selected_ip_and_port),
            "HOST_MENU": ("Enter Port number", self.selected_ip_and_port),
        }

    def _get_scaled_sprite(self, sprite_index):
        sprite = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE), pygame.SRCALPHA)
        sprite.blit(self.sprite_sheet, (0, 0), (sprite_index * SPRITE_SIZE, 0, SPRITE_SIZE, SPRITE_SIZE))
        return pygame.transform.scale(sprite, (SPRITE_SIZE * SCALE_FACTOR, SPRITE_SIZE * SCALE_FACTOR))

    def render_text(self, text, x, y):
        rendered_text = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(rendered_text, (x, y))

    def draw(self):
        self.screen.fill(GREEN)

        # Title rendering
        title_text = self.font.render("Tennis Game", True, (255, 255, 255))
        title_width = title_text.get_width()
        self.screen.blit(self.plaqueEndImage, (WINDOW_WIDTH // 2 - title_width // 2 - self.plaqueImage.get_width(), 85))
        for i in range(0, title_width // self.plaqueImage.get_width() + 1):
            self.screen.blit(self.plaqueImage, (WINDOW_WIDTH // 2 - title_width // 2 + i * self.plaqueImage.get_width(), 85))
        self.screen.blit(self.plaqueEndImageFlipped, (WINDOW_WIDTH // 2 + title_width // 2, 85))
        self.screen.blit(title_text, (WINDOW_WIDTH // 2 - title_width // 2, 100))

        # Get current menu text
        menu_text_top, menu_text_bottom = self.menu_options[self.menu_state]
        menu_text_bottom = self.selected_ip_and_port if self.menu_state in ["JOIN_MENU", "HOST_MENU"] else menu_text_bottom

        # Render menu text
        self.render_text(menu_text_top, (WINDOW_WIDTH // 2) - self.font.size(menu_text_top)[0] // 2, WINDOW_HEIGHT // 2)
        self.render_text(menu_text_bottom, (WINDOW_WIDTH // 2) - self.font.size(menu_text_bottom)[0] // 2, (WINDOW_HEIGHT // 2) + 50)

        pygame.display.flip()

    def handle_menu_events(self, game_state):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                key = event.key
                if self.menu_state == "MAIN":
                    if key == pygame.K_1:
                        return "SINGLE_PLAYER"  # Start single-player game
                    elif key == pygame.K_2:
                        self.menu_state = "MULTIPLAYER_MENU"
                elif self.menu_state == "MULTIPLAYER_MENU":
                    if key == pygame.K_1:  # Host Game
                        self.menu_state = "HOST_MENU"
                        self.is_hosting = True
                    elif key == pygame.K_2:  # Join Game
                        self.menu_state = "JOIN_MENU"
                        self.is_hosting = False
                elif self.menu_state in ["HOST_MENU", "JOIN_MENU"]:
                    if key == pygame.K_RETURN:  # Press Enter to host/join
                        return self._handle_host_or_join()
                    elif key == pygame.K_BACKSPACE:
                        self.selected_ip_and_port = self.selected_ip_and_port[:-1]
                    elif event.unicode.isdigit() or key in [pygame.K_PERIOD, pygame.K_SEMICOLON]:
                        self.selected_ip_and_port += event.unicode if event.unicode.isdigit() else self._get_special_char(key)
        return game_state

    def _handle_host_or_join(self):
        try:
            if self.is_hosting:
                self.selected_port = self.selected_ip_and_port
                return "HOST"
            else:
                self.selected_ip, self.selected_port = self.selected_ip_and_port.split(":")
                return "JOIN"
        except ValueError:
            self.selected_ip_and_port = "Invalid IP:Port"

    def _get_special_char(self, key):
        return "." if key == pygame.K_PERIOD else ":" if key == pygame.K_SEMICOLON else ""
