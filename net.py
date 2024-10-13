import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, SCALE_FACTOR,SPRITE_SIZE

class Net(pygame.sprite.Sprite):
    def __init__(self,sprite_sheet, width, height):
        self.sprite_width = 16
        self.sprite_height = 16

        self.width = width
        self.height = height
        self.x = (WINDOW_WIDTH - width) // 2  # Center of the window
        self.y = (WINDOW_HEIGHT - height) // 2 - (16 * SCALE_FACTOR)/2 # Middle of the window
    

        if sprite_sheet is not None:
            self.image = pygame.Surface((SPRITE_SIZE, self.height), pygame.SRCALPHA)
            self.image.blit(sprite_sheet, (0, 0), ( 2* SPRITE_SIZE, 0, 16, 16))  # Load sprite from sheet

            self.post = pygame.Surface((SPRITE_SIZE, self.height), pygame.SRCALPHA)
            self.post.blit(sprite_sheet, (0, 0), ( 4* SPRITE_SIZE, 0, 16, 16))
            
            self.rect = self.image.get_rect()  # Create a rect from the image size
            self.rect.topleft = (self.x, self.y)  # Set initial position
    def draw(self, screen):

        scaled_image = pygame.transform.scale(self.image, (SPRITE_SIZE * SCALE_FACTOR, self.rect.height * SCALE_FACTOR))
        scaled_post = pygame.transform.scale(self.post, (SPRITE_SIZE * SCALE_FACTOR, self.rect.height * SCALE_FACTOR))

        scaled_post_flipped = pygame.transform.flip(scaled_post, True, False)
        net_section = self.sprite_width * SCALE_FACTOR
        i = 0
        screen.blit(scaled_post, (self.x- net_section, self.y))
        
        
        
        while i < self.width:
            screen.blit(scaled_image, (self.x + i, self.y))
            i = i + net_section
        screen.blit(scaled_post_flipped, (self.width + self.x, self.y))
        
       
            

        