import pygame
import sys
from random import Random
from ball import Ball
from player import Player , AIPlayer
from power_bar import PowerBar
from net import Net
from settings import *
from menu import Menu
from instructions import Instructions


class Game:
    def __init__(self, screen):
        self.game_state = "MENU"  # Start the game in the menu state

        self.ball_radius = 5
        self.ball_x = WINDOW_WIDTH // 2
        self.ball_y = WINDOW_HEIGHT // 2
        self.ball_z = 1
        self.ball_speed_x = 4
        self.ball_speed_y = 4
        self.ball_speed_z = 0

        self.net_width = WINDOW_WIDTH //2 
        self.net_height = 10  # Half of the window height

        # Main game loop
        self.clock = pygame.time.Clock()

        self.player = Player(WINDOW_WIDTH // 2 , 50, 4, 1)

        self.ai_player = AIPlayer(WINDOW_WIDTH // 2, WINDOW_HEIGHT -100 // 2, 4, -1)

        self.ball = Ball(self.ball_x, self.ball_y, self.ball_z, self.ball_radius)

        self.power_bar = PowerBar(50, 50, 20, 150, 0, 100)

        self.net = Net(self.net_width, self.net_height)

        self.serving = True

        self.font = pygame.font.Font('silkscreen.ttf', 36)
        self.screen = screen

        pygame.display.set_caption('Top-Down Tennis Game')

    def set_state(self, new_state):
        self.game_state = new_state

    
    def draw_scores(self):
        # Render the text for both player and AI scores
        player_text = self.font.render(f"Player: {self.player.score}", True, WHITE)
        ai_text = self.font.render(f"AI: {self.ai_player.score}", True, WHITE)

        # Display the scores in the top left and right corners
        self.screen.blit(player_text, (50, 20))
        self.screen.blit(ai_text, (WINDOW_WIDTH - 150, 20))

    def check_point(self):
        if self.ball.y < 0:
            self.ai_player.score += 1
            self.ball.reset_ball()

        if self.ball.y > WINDOW_HEIGHT:
            self.player.score += 1
            self.ball.reset_ball()

        # if ball bouces outside the court
        if (self.ball.x > self.net.x + self.net.width or self.ball.x < self.net.x) and self.ball.z <= 1:
            if self.ball.speed_y > 0:
                self.ai_player.score += 1
            else:
                self.player.score += 1
            self.ball.reset_ball()

    def handle_menu_events(self):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Add logic to switch game state when user clicks "Start Game" button
                    self.set_state("GAME")
        
    def handle_game_events(self):

        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                        WINDOW_WIDTH, WINDOW_HEIGHT = event.w, event.h
                        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.ball.served and not self.serving:
                        self.serving = True  
                    elif self.ball.served:
                        self.player.start_swing()
            
                elif event.key == pygame.K_r:
                    self.ball.served = False
                    self.serving = True
                if event.key == pygame.K_ESCAPE:
                    self.set_state("MENU")
        if self.serving:
                self.power_bar.update()
                if keys[pygame.K_SPACE]:  # Serve when pressing space again
                    if self.power_bar.is_in_ideal_range():
                        serve_speed_y = self.player.swing_speed_y * self.player.serve_speed_multiplier * self.player.side
                        serve_speed_x = self.player.swing_speed_x
                        serve_speed_z = self.player.swing_speed_z
                    else:
                        serve_speed_y = self.player.swing_speed_y * self.player.side
                        serve_speed_x = self.player.swing_speed_x * self.player.serve_speed_multiplier 
                        serve_speed_z = self.player.swing_speed_z

                    self.ball.serve(serve_speed_x, serve_speed_y, serve_speed_z, self.player.x, self.player.y)
                    self.serving = False  # Stop the serving process


        
        self.player.move(keys)
        self.player.update_swing()

    def update_game(self):
        self.ai_player.update_ai(self.ball)
        self.ai_player.update_swing()

    

        # Move the ball
        if self.ball.served:
            self.ball.move()
            self.ball.check_net_collision(self.net)

        if self.player.is_ball_in_swing_area(self.ball) and self.ball.can_be_hit() and self.player.swinging:
            self.ball.speed_y = self.player.swing_speed_y * self.player.side 
            self.ball.speed_x = self.player.swing_speed_x * Random().choice([-1, 1])
            self.ball.speed_z = self.player.swing_speed_z
            self.ball.register_hit() 

        
        if self.ai_player.is_ball_in_swing_area(self.ball) and self.ball.can_be_hit():
            self.ai_player.start_swing()
            self.ball.speed_y = self.ai_player.swing_speed_y * self.ai_player.side
            self.ball.speed_x = self.ai_player.swing_speed_x * Random().choice([-1, 1])
            self.ball.speed_z = self.ai_player.swing_speed_z
            self.ball.register_hit()
        
        self.check_point()

    def draw_game(self):
    
        # Fill the screen with black
        self.screen.fill(BLACK)

        self.player.draw(self.screen)
        self.ai_player.draw(self.screen)
        self.ball.draw(self.screen)
        self.net.draw(self.screen)
        self.draw_scores()

        if not self.ball.served and self.serving:
            self.power_bar.draw(self.screen)

        # Update the display
        pygame.display.flip()

        # Set the frame rate
        self.clock.tick(60)

# Initialize Pygame



def game_loop():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    game = Game(screen)
    menu = Menu(game.screen)

    while True:
        if game.game_state == "MENU":
            menu.draw()
            game.handle_menu_events()  # Handle clicks in the menu
        if game.game_state == "MENU":
            menu.draw()
            game.handle_menu_events()  # Handle clicks in the menu
        elif game.game_state == "GAME":
            # Your game logic here
            game.handle_game_events()
            game.update_game()
            game.draw_game()





# Ball properties


game_loop()
