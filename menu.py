import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, GREEN, SPRITE_SIZE, SCALE_FACTOR

class Menu:
    def __init__(self, screen, sprite_sheet):
        self.screen = screen
        self.sprite_sheet = sprite_sheet
        self.font = pygame.font.Font('silkscreen.ttf', 32)  # Load font
        self.plaqueImage = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE), pygame.SRCALPHA)
        self.plaqueEndImage = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE), pygame.SRCALPHA)
        if self.sprite_sheet is not None:
                self.plaqueImage.blit(self.sprite_sheet, (0, 0), (7 * SPRITE_SIZE, 0, SPRITE_SIZE, SPRITE_SIZE))
                self.plaqueEndImage.blit(self.sprite_sheet, (0, 0), (6 * SPRITE_SIZE, 0, SPRITE_SIZE, SPRITE_SIZE))

    def draw(self):
        # Fill background with green
        self.screen.fill(GREEN)
        
        

        scaled_plaque = pygame.transform.scale(self.plaqueImage, ( SPRITE_SIZE * SCALE_FACTOR, SPRITE_SIZE * SCALE_FACTOR))
        scaled_plaque_end = pygame.transform.scale(self.plaqueEndImage, ( SPRITE_SIZE * SCALE_FACTOR, SPRITE_SIZE * SCALE_FACTOR))

        scaled_plaque_end_flipped = pygame.transform.flip(scaled_plaque_end, True, False)


        

        # Draw title
        title_text = self.font.render("Tennis Game", True, (255, 255, 255))
        self.screen.blit(scaled_plaque_end, (WINDOW_WIDTH // 2 - title_text.get_width() // 2 - scaled_plaque.get_width(), 85))
        i = 0
        for i in range(0, title_text.get_width() // scaled_plaque.get_width() + 1):
            print(i)
            self.screen.blit(scaled_plaque, (WINDOW_WIDTH // 2 - title_text.get_width() // 2 + i * scaled_plaque.get_width() , 85))

        self.screen.blit(scaled_plaque_end_flipped, (WINDOW_WIDTH // 2 + title_text.get_width() // 2, 85))
        self.screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 100))

        # Draw "Start Game" button
        start_text = self.font.render("Singleplayer", True, (255, 255, 255))
        self.screen.blit(start_text, (WINDOW_WIDTH // 2 - start_text.get_width() // 2, 300))

        # Draw "Instructions" button
        instructions_text = self.font.render("Multiplayer", True, (255, 255, 255))
        self.screen.blit(instructions_text, (WINDOW_WIDTH // 2 - instructions_text.get_width() // 2, 400))

        pygame.display.flip()  # Update the screen

    def handle_menu_events(self, game_state):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # Check if "Start Game" button was clicked
                if 300 < mouse_pos[1] < 350:  
                   print("SINGLE Game button clicked")
                   return "GAME"  # Change to game state
                # Check if "Instructions" button was clicked
                elif 400 < mouse_pos[1] < 450:
                    print("Multiplayer Game button clicked")
                    return "MULTIPLAYER"  # Change to instructions state
        return game_state
