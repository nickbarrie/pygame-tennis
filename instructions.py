import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT

class Instructions:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font('silkscreen.ttf', 24)

    def draw(self):
        self.screen.fill((0, 0, 0))  # Black background

        instructions_text = self.font.render("Use arrow keys to move", True, (255, 255, 255))
        self.screen.blit(instructions_text, (WINDOW_WIDTH // 2 - instructions_text.get_width() // 2, 200))

        back_text = self.font.render("Press ESC to return", True, (255, 255, 255))
        self.screen.blit(back_text, (WINDOW_WIDTH // 2 - back_text.get_width() // 2, 400))

        pygame.display.flip()
