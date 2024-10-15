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
import subprocess

class Game:
    def __init__(self, screen, sprite_sheet, ball_x ,ball_y, ball_z, ball_radius):

      

        self.net_width = WINDOW_WIDTH -120
        self.net_height = 16  # Half of the window height

        # Main game loop
        self.clock = pygame.time.Clock()

        self.top_player = Player(sprite_sheet,WINDOW_WIDTH // 2, 50, 4, 1)

        self.bottom_player = AIPlayer(sprite_sheet,WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100 // 2, 4, -1)

        self.ball = Ball(sprite_sheet, ball_x ,ball_y, ball_z, ball_radius)

        self.power_bar = PowerBar(20, 100, 20, 150, 0, 100)

        self.net = Net(sprite_sheet, self.net_width, self.net_height)


        self.font = pygame.font.Font('silkscreen.ttf',50)
        self.screen = screen

        self.local_player = None  # Initialize local player
        self.remote_player = None  # Initialize remote player

        pygame.display.set_caption('Top-Down Tennis Game')

        # Network setup
        self.port = 5555  # Default port, can be changed later
        self.ip = ""
        self.server = None  # Server for hosting, set later if hosting
        self.client = None  # Client for joining, set later if joining
        self.player_id = 0  # Player's ID (0 or 1 for multiplayer)
        self.server_process = None  # Server process for hosting

        self.grass_sprite = self.get_sprite(sprite_sheet, 3, 0, 16, 16)
        self.score_plaque = self.get_sprite(sprite_sheet, 9, 0, 16, 16)

        self.zero_points = self.get_sprite(sprite_sheet, 3, 1, 16, 16)
        self.fifteen_points = self.get_sprite(sprite_sheet, 0, 1, 16, 16)
        self.thrity_points = self.get_sprite(sprite_sheet, 1, 1, 16, 16)
        self.fourty_points = self.get_sprite(sprite_sheet, 2, 1, 16, 16)

        self.top_player_image = self.get_sprite(sprite_sheet, 0, 0, 16, 16)
        self.bottom_player_image = self.get_sprite(sprite_sheet, 4, 1, 16, 16)

        self.ball_image = self.get_sprite(sprite_sheet, 5, 0, 16, 16)


    def set_state(self, new_state):
        self.game_state = new_state

    def get_sprite(self, sprite_sheet, x, y, width, height):
        """Extracts a sprite from the sprite sheet."""
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(sprite_sheet, (0, 0), (x * SPRITE_SIZE, y * SPRITE_SIZE, width, height))
        sprite = pygame.transform.scale(sprite, (SPRITE_SIZE * SCALE_FACTOR, SPRITE_SIZE * SCALE_FACTOR))
        return sprite

    def draw_grass(self):
        """Fill the screen with the grass sprite."""
        scaled_image = pygame.transform.scale(self.grass_sprite, (16 * SCALE_FACTOR * 3, 16 * SCALE_FACTOR * 3))
        for y in range(0, WINDOW_HEIGHT, 16 * SCALE_FACTOR * 3):  # Step by sprite height
            for x in range(-32, WINDOW_WIDTH, 16 * SCALE_FACTOR * 3):  # Step by sprite width
                self.screen.blit(scaled_image, (x, y))  # Draw grass at (x, y)

    def draw_court(self):
        line_width = 4
        line_color = WHITE
         # Baselines (top and bottom)
        pygame.draw.line(self.screen, line_color, (50, 50), (WINDOW_WIDTH - 50, 50), line_width)  # Top baseline
        pygame.draw.line(self.screen, line_color, (50, WINDOW_HEIGHT - 50), (WINDOW_WIDTH - 50, WINDOW_HEIGHT - 50), line_width)  # Bottom baseline

        # Service lines (near the middle)
        pygame.draw.line(self.screen, line_color, (50, WINDOW_HEIGHT // 2 - 100), (WINDOW_WIDTH - 50, WINDOW_HEIGHT // 2 - 100), line_width)  # Top service line
        pygame.draw.line(self.screen, line_color, (50, WINDOW_HEIGHT // 2 + 100), (WINDOW_WIDTH - 50, WINDOW_HEIGHT // 2 + 100), line_width)  # Bottom service line

        # Center service line
        pygame.draw.line(self.screen, line_color, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100), (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100), line_width)

        # Sidelines (left and right)
        pygame.draw.line(self.screen, line_color, (50, 50), (50, WINDOW_HEIGHT - 50), line_width)  # Left sideline
        pygame.draw.line(self.screen, line_color, (WINDOW_WIDTH - 50, 50), (WINDOW_WIDTH - 50, WINDOW_HEIGHT - 50), line_width)  # Right sideline

        # Center mark on baselines
        pygame.draw.line(self.screen, line_color, (WINDOW_WIDTH // 2, 45), (WINDOW_WIDTH // 2, 55), line_width)  # Top center mark
        pygame.draw.line(self.screen, line_color, (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 55), (WINDOW_WIDTH // 2, WINDOW_HEIGHT - 45), line_width)  # Bottom center mark

    def convert_score_to_tennis_points(self,score):
            if score == 0:
                return self.zero_points
            elif score == 1:
                return self.fifteen_points
            elif score == 2:
                return self.thrity_points
            elif score == 3:
                return self.fourty_points
            elif score >= 4:  # Only applies when player wins the game
                return 50
            
    def draw_scores(self):
        # Render the text for both player and AI scores
        score_plaque_flipped = pygame.transform.flip(self.score_plaque, True, False)

        self.screen.blit(self.score_plaque, (WINDOW_WIDTH - self.score_plaque.get_width(), 20))
        self.screen.blit(score_plaque_flipped, (0, 20))

        top_player_score = self.convert_score_to_tennis_points(self.top_player.score)


        bottom_player_score = self.convert_score_to_tennis_points(self.bottom_player.score)   
 

        # Display the scores in the top left and right corners
        self.screen.blit(top_player_score, (2 * SCALE_FACTOR, 22))
        self.screen.blit(bottom_player_score, ( WINDOW_WIDTH -20 * SCALE_FACTOR, 22))

        # Draw top player's image and sets on the bottom left
        self.screen.blit(self.top_player_image, (2 * SCALE_FACTOR, WINDOW_HEIGHT - 50))
        for i in range(self.top_player.sets):
            self.screen.blit(self.ball_image, (5 * SCALE_FACTOR + (i + 1) * (SPRITE_SIZE * SCALE_FACTOR / 3), WINDOW_HEIGHT - 50))

        # Draw bottom player's image and sets on the bottom right
        self.screen.blit(self.bottom_player_image, (WINDOW_WIDTH - 2 * SCALE_FACTOR - self.bottom_player_image.get_width(), WINDOW_HEIGHT - 50))
        for i in range(self.bottom_player.sets):
            self.screen.blit(self.ball_image, (WINDOW_WIDTH - 5 * SCALE_FACTOR - (i + 1) * (SPRITE_SIZE * SCALE_FACTOR / 3), WINDOW_HEIGHT - 50))


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

    def connect_to_server(self, game_state):
        """ Connect to the multiplayer server """
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip = ""
        if game_state == "HOST":
            print(socket.gethostbyname(socket.gethostname()))
            ip = socket.gethostbyname(socket.gethostname())
            
        if game_state == "JOIN":
            ip = self.ip
        print(f"Connecting to {ip}:{self.port}")
        self.client.connect((ip, int(self.port)))  # Connect to the server
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
        self.local_player.serving = True

    def set_port(self, port):
        self.port = int(port)

    def set_ip(self, ip):
        self.ip = ip

    def host_game(self):
        self.server_process = subprocess.Popen(["python", "server.py", str(self.port)])
         
    def stop_server(self):
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()


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

            opponent_id = 1 if self.player_id == 0 else 0
            self.remote_player.x = game_state['players'][opponent_id]['x']
            self.remote_player.y = game_state['players'][opponent_id]['y']
            self.remote_player.swinging = game_state['players'][opponent_id]['swinging']
            self.remote_player.score = game_state['players'][opponent_id]['score']
            self.remote_player.sets = game_state['players'][opponent_id]['sets']
            self.remote_player.serving = game_state['players'][opponent_id]['serving']
            # Update local player score
            self.local_player.score = game_state['players'][self.player_id]['score']
            self.local_player.sets = game_state['players'][self.player_id]['sets']
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
                    serve_speed_x = self.local_player.swing_speed_x * self.local_player.serve_speed_multiplier
                    serve_speed_z = self.local_player.swing_speed_z * self.local_player.serve_speed_multiplier
                else:
                    serve_speed_y = self.local_player.swing_speed_y * self.local_player.side
                    serve_speed_x = self.local_player.swing_speed_x * self.local_player.serve_speed_multiplier
                    serve_speed_z = self.local_player.swing_speed_z * self.local_player.serve_speed_multiplier

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
        self.draw_grass()
        self.draw_court()

        self.top_player.draw(self.screen, self.ball)
        self.bottom_player.draw(self.screen,self.ball)
       
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
    menu = Menu(game.screen, sprite_sheet)

    if game_state == "MULTIPLAYER":
        game.connect_to_server()  # Add this line
    try:
        while True:
            if game_state == "MENU":
                menu.draw()
                game_state = menu.handle_menu_events(game_state)
            
            elif game_state == "HOST":
                game.set_port(menu.selected_port)
                game.host_game()  # Start hosting the game
                game.connect_to_server(game_state)
                game_state = "MULTIPLAYER"


            elif game_state == "JOIN":
                game.set_port(menu.selected_port)
                game.set_ip(menu.selected_ip)
                game.connect_to_server(game_state)
                game_state = "MULTIPLAYER"

            elif game_state == "MULTIPLAYER":
                game.handle_game_events()
                game.update_game_multiplayer()
                game.draw_game()

            elif game_state == "SINGLE_PLAYER":
                game.load_single_player()
                game_state = "GAME"

            elif game_state == "MULTIPLAYER":
                game.handle_game_events()
                game.update_game_multiplayer()
                game.draw_game()

            elif game_state == "GAME":
                game.handle_game_events()
                game.update_game()
                game.draw_game() 
    finally:
        game.stop_server()
        pygame.quit()



game_state = "MENU"

game_loop(game_state)



