import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, WHITE

class Net:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = (WINDOW_WIDTH - width) // 2  # Center of the window
        self.y = (WINDOW_HEIGHT - height) // 2  # Middle of the window
    
    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))