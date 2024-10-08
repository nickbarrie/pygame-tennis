import socket
import pickle
import pygame
import sys
from random import Random
from ball import Ball
from player import Player , AIPlayer
from power_bar import PowerBar
from net import Net
from settings import *
from menu import Menu

class Game:
    def __init__(self, screen, sprite_sheet, ball_x ,ball_y, ball_z, ball_radius):

      

        self.net_width = WINDOW_WIDTH // 2
        self.net_height = 16  # Half of the window height

        # Main game loop
        self.clock = pygame.time.Clock()

        self.top_player = Player(sprite_sheet,WINDOW_WIDTH // 2, 50, 4, 1)

        self.bottom_player = AIPlayer(sprite_sheet,WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100 // 2, 4, -1)

        self.ball = Ball(sprite_sheet, ball_x ,ball_y, ball_z, ball_radius)

        self.power_bar = PowerBar(50, 50, 20, 150, 0, 100)

        self.net = Net(sprite_sheet, self.net_width, self.net_height)


        self.font = pygame.font.Font('silkscreen.ttf', 36)
        self.screen = screen

        self.local_player = None  # Initialize local player
        self.remote_player = None  # Initialize remote player

        pygame.display.set_caption('Top-Down Tennis Game')

        # Network setup
        self.client = None
        self.player_id = 0  # Player's ID (0 or 1 for multiplayer)

        self.grass_sprite = self.get_sprite(sprite_sheet, 48, 0, 16, 16)

    def set_state(self, new_state):
        self.game_state = new_state

    def get_sprite(self, sprite_sheet, x, y, width, height):
        """Extracts a sprite from the sprite sheet."""
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(sprite_sheet, (0, 0), (x, y, width, height))
        return sprite

    def draw_grass(self):
        """Fill the screen with the grass sprite."""
        scaled_image = pygame.transform.scale(self.grass_sprite, (16 * SCALE_FACTOR * 3, 16 * SCALE_FACTOR * 3))
        for y in range(0, WINDOW_HEIGHT, 16 * SCALE_FACTOR * 3):  # Step by sprite height
            for x in range(-32, WINDOW_WIDTH, 16 * SCALE_FACTOR * 3):  # Step by sprite width
                self.screen.blit(scaled_image, (x, y))  # Draw grass at (x, y)
    
    def draw_scores(self):
        # Render the text for both player and AI scores
        player_text = self.font.render(f"Player: {self.top_player.score}", True, WHITE)
        ai_text = self.font.render(f"AI: {self.bottom_player.score}", True, WHITE)

        # Display the scores in the top left and right corners
        self.screen.blit(player_text, (50, 20))
        self.screen.blit(ai_text, (WINDOW_WIDTH - 150, 20))

    def check_point(self):
        if self.ball.y < 0:
            self.bottom_player.score += 1
            self.ball.reset_ball()

        if self.ball.y > WINDOW_HEIGHT:
            self.top_player.score += 1
            self.ball.reset_ball()

        # if ball bouces outside the court
        if (self.ball.x > self.net.x + self.net.width or self.ball.x < self.net.x) and self.ball.z <= 1:
            if self.ball.speed_y > 0:
                self.bottom_player.score += 1
            else:
                self.top_player.score += 1
            self.ball.reset_ball()

    def connect_to_server(self):
        """ Connect to the multiplayer server """
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(('172.20.0.84', 5555))  # Connect to the server
        self.player_id = pickle.loads(self.client.recv(2048))  # Receive player ID from the server
        print(f"Connected to the server as player {self.player_id}")

        if self.player_id == 0:
            self.local_player = self.top_player  # Player 1
            self.remote_player = self.bottom_player  # Player 2 (opponent)

        else:
            self.local_player = self.bottom_player  # Player 1
            self.remote_player = self.top_player  # Player 2 (opponent)

    def load_single_player(self):
        """ Load single player game state """
        self.local_player = self.top_player

    def send_player_data(self):
        """ Send player data to the server """
        player_data = {
            'x': self.local_player.x,
            'y': self.local_player.y,
            'swinging': self.local_player.swinging,  # Include whether the player is swinging
            'speed_x': self.ball.speed_x,            # Include the speed of the ball when swinging
            'speed_y': self.ball.speed_y,
            'speed_z': self.ball.speed_z,
        }
        # Send player data to the server
        self.client.sendall(pickle.dumps(player_data))
    


    def receive_game_state(self):
        """ Receive the updated game state from the server """
        data = b""
        while True:
            part = self.client.recv(2048)
            data += part
            if len(part) < 2048:
                break  # Break if the last packet is smaller than the buffer size
        try:
            return pickle.loads(data)
        except Exception as e:
            print(f"Error receiving game state: {e}")
            return None

    def update_game_multiplayer(self):
        """ Update the game state in multiplayer mode """
        # Send player data to the server
        self.send_player_data()
        
        # Receive updated game state from the server
        game_state = self.receive_game_state()

        if game_state:
            # Update the remote player's position and swing state from the game state
            print("opponent x and y",game_state['players'][1]['x'],game_state['players'][1]['y'])
            opponent_id = 1 if self.player_id == 0 else 0
            self.remote_player.x = game_state['players'][opponent_id]['x']
            self.remote_player.y = game_state['players'][opponent_id]['y']
            self.remote_player.swinging = game_state['players'][opponent_id]['swinging']
            self.remote_player.score = game_state['players'][opponent_id]['score']
            self.remote_player.serving = game_state['players'][opponent_id]['serving']
            print("remote player x and y",self.remote_player.x,self.remote_player.y)
            # Update local player score
            self.local_player.score = game_state['players'][self.player_id]['score']
            self.local_player.serving = game_state['players'][self.player_id]['serving']
            
            # Update ball position
            self.ball.x = game_state['ball']['x']
            self.ball.y = game_state['ball']['y']
            self.ball.z = game_state['ball']['z']
            self.ball.served = game_state['ball']['served']
            self.ball.angle = game_state['ball']['angle']

            

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
                   if self.ball.served:
                        self.local_player.start_swing()
                if event.key == pygame.K_ESCAPE:
                    self.set_state("MENU")

        if self.local_player.serving:
            self.power_bar.update()
            if keys[pygame.K_SPACE]:  # Serve when pressing space again
                self.local_player.start_swing()
                if self.power_bar.is_in_ideal_range():
                    serve_speed_y = self.local_player.swing_speed_y * self.local_player.serve_speed_multiplier * self.local_player.side
                    serve_speed_x = self.local_player.swing_speed_x
                    serve_speed_z = self.local_player.swing_speed_z
                else:
                    serve_speed_y = self.local_player.swing_speed_y * self.local_player.side
                    serve_speed_x = self.local_player.swing_speed_x * self.local_player.serve_speed_multiplier
                    serve_speed_z = self.local_player.swing_speed_z

                self.ball.serve(serve_speed_x, serve_speed_y, serve_speed_z, self.local_player.x, self.local_player.y)
                self.local_player.serving = False  # Stop the serving process

        self.local_player.move(keys)
        self.local_player.update_swing()


    def update_game(self):
        self.bottom_player.update_ai(self.ball)
        self.bottom_player.update_swing()

        if self.local_player.serving:
            self.ball.served = False

        # Move the ball
        if self.ball.served:
            self.ball.move()
            self.ball.check_net_collision(self.net)

        if self.top_player.is_ball_in_swing_area(self.ball) and self.ball.can_be_hit() and self.top_player.swinging:
            self.ball.speed_y = self.top_player.swing_speed_y * self.top_player.side
            self.ball.speed_x = self.top_player.swing_speed_x * Random().choice([-1, 1])
            self.ball.speed_z = self.top_player.swing_speed_z
            self.ball.register_hit()

        if self.bottom_player.is_ball_in_swing_area(self.ball) and self.ball.can_be_hit():
            self.bottom_player.start_swing()
            self.ball.speed_y = self.bottom_player.swing_speed_y * self.bottom_player.side
            self.ball.speed_x = self.bottom_player.swing_speed_x * Random().choice([-1, 1])
            self.ball.speed_z = self.bottom_player.swing_speed_z
            self.ball.register_hit()

        self.check_point()

    def draw_game(self):
        # Fill the screen with black
        self.draw_grass()

        self.top_player.draw(self.screen)
        self.bottom_player.draw(self.screen)
       
        self.net.draw(self.screen)
        self.draw_scores()
        self.ball.draw(self.screen)
        if not self.ball.served and self.local_player.serving:
            self.power_bar.draw(self.screen)

        # Update the display
        pygame.display.flip()

        # Set the frame rate
        self.clock.tick(60)



def game_loop(game_state):
    pygame.init()


    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    sprite_sheet = pygame.image.load('sprites.png').convert_alpha()
    ball_radius = 5
    ball_x = WINDOW_WIDTH // 2
    ball_y = WINDOW_HEIGHT // 2
    ball_z = 1
    ball_speed_x = 4
    ball_speed_y = 4
    ball_speed_z = 0



    game = Game(screen,sprite_sheet, ball_x ,ball_y, ball_z, ball_radius)
    menu = Menu(game.screen)

    if game_state == "MULTIPLAYER":
        game.connect_to_server()  # Add this line

    while True:
        if game_state == "MENU":
            menu.draw()
            game_state = menu.handle_menu_events(game_state)
        elif game_state == "MULTIPLAYER":
            if not game.local_player:
                game.connect_to_server()  # Ensure we connect if not already connected
            game.handle_game_events()
            game.update_game_multiplayer()
            game.draw_game()
        elif game_state == "GAME":
            if not game.local_player:
                game.load_single_player()
            game.handle_game_events()
            game.update_game()
            game.draw_game()



game_state = "MENU"

game_loop(game_state)
