import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, WHITE

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font('silkscreen.ttf', 32)  # Load font

    def draw(self):
        self.screen.fill((0, 0, 0))  # Fill background with black

        # Draw title
        title_text = self.font.render("Tennis Game", True, (255, 255, 255))
        self.screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 100))

        # Draw "Start Game" button
        start_text = self.font.render("Start Game", True, (255, 255, 255))
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
