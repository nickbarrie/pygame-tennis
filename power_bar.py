import pygame
from settings import WHITE, RED, GREEN

class PowerBar:
    def __init__(self, x, y, width, height, min_power, max_power):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_power = min_power
        self.max_power = max_power
        self.current_power = min_power
        self.direction = 1  
        self.ideal_range = (0.4, 0.6)  

    def update(self):
        self.current_power += self.direction * 1  
        if self.current_power >= self.max_power or self.current_power <= self.min_power:
            self.direction *= -1

    def draw(self,screen):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))  
        power_height = (self.current_power / self.max_power) * self.height
        pygame.draw.rect(screen, RED, (self.x, self.y + self.height - power_height, self.width, power_height))

        ideal_start = self.y + self.height * (1 - self.ideal_range[1])
        ideal_end = self.y + self.height * (1 - self.ideal_range[0])
        pygame.draw.rect(screen, GREEN, (self.x, ideal_start, self.width, ideal_end - ideal_start))

    def is_in_ideal_range(self):

        percentage = self.current_power / self.max_power
        return self.ideal_range[0] <= percentage <= self.ideal_range[1]