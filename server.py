import socket
import pickle
from _thread import start_new_thread
from settings import WINDOW_WIDTH, WINDOW_HEIGHT
from player import Player
from ball import Ball
from net import Net
from random import Random
import sys
import random
import pygame


class GameServer:
    def __init__(self):
        self.player_1 = Player(None, 100, 50, speed=4, side=1)  # Top player
        self.player_2 = Player(None, 100, 550, speed=4, side=-1)  # Bottom player
        self.net = Net(None, WINDOW_WIDTH // 2, 10)  # Net in the middle
        self.ball = Ball(None, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, 0, radius=10)  # Ball in the center
        self.clients = []  # Keep track of connected clients
        self.point_settled_time = None  # Time when the last point was settled
        self.point_delay_duration = 2000  
        self.game_state = {
            "ball": {"x": self.ball.x, "y": self.ball.y, "z": self.ball.z, "speed_x": self.ball.speed_x, "speed_y": self.ball.speed_y, "served": self.ball.served, "angle": self.ball.angle},
            "players": [
                {"x": self.player_1.x, "y": self.player_1.y, "score": 0, "swinging": False, "serving": False},
                {"x": self.player_2.x, "y": self.player_2.y, "score": 0, "swinging": False, "serving": False}
            ]
        }

    def determine_server(self):
        """ Switch server when the ball is not in play """
        if not self.ball.served :
            print("Determining server...")
            self.player_1.serving = not self.player_1.serving
            self.player_2.serving = not self.player_2.serving


        if not self.player_1.serving and not self.player_2.serving:
            current_server = random.choice([1, 2])
            if current_server == 1:
                self.player_1.serving = True
                self.player_2.serving = False
            else:
                self.player_1.serving = False
                self.player_2.serving = True

        print("Player 1 serving: %s, Player 2 serving: %s" % (self.player_1.serving, self.player_2.serving))
        self.game_state['players'][0]['serving'] = self.player_1.serving
        self.game_state['players'][1]['serving'] = self.player_2.serving



    def check_ball_in_play(self):
        """ Check if the ball is still in play"""
            # Out of bounds horizontally (left or right)
        if self.ball.x < 0 or self.ball.x > WINDOW_WIDTH:
            print("Ball out of bounds horizontally")
            self.ball.in_play = False
            self.ball.served = False
            if self.ball.speed_y < 0:  # Ball was moving towards player 2's side
                self.handle_point_scored(self.player_1)
            else:  # Ball was moving towards player 1's side
                self.handle_point_scored(self.player_2)
            self.point_settled_time = pygame.time.get_ticks()

        # Out of bounds vertically (top or bottom)
        elif self.ball.y < 0 or self.ball.y > WINDOW_HEIGHT:
            
            print("Ball out of bounds vertically")
            self.ball.in_play = False
            self.ball.served = False
            if self.ball.speed_y < 0:  # Ball hit out on player 1's side
                self.handle_point_scored(self.player_2)
            else:  # Ball hit out on player 2's side
                self.handle_point_scored(self.player_1)
            self.point_settled_time = pygame.time.get_ticks()
        
        # Net collision
        elif self.ball.check_net_collision(self.net):  # Ball hit the net and did not cross it
            
            print("Ball hit the net")
            self.ball.in_play = False
            self.ball.served = False
            if self.ball.speed_y > 0:  # ball bounces backwards to player 2's side
                self.handle_point_scored(self.player_1)
            else:  # Ball was moving towards player 1's side
                self.handle_point_scored(self.player_2)
            self.point_settled_time = pygame.time.get_ticks()

        # Check for multiple bounces
        elif self.ball.bounce_count > 1:  # If ball bounces more than once
            print("Ball bounced more than once")
            self.ball.in_play = False
            self.ball.served = False
            if self.ball.speed_y < 0:   # Player 1 hit the ball last, so Player 1 wins the point
                self.handle_point_scored(self.player_1)
            else:  # Player 2 hit the ball last, so Player 1 wins the point
                self.handle_point_scored(self.player_2)
            self.point_settled_time = pygame.time.get_ticks()
        
    

    def handle_point_scored(self, player):
        """ Handle when a point is scored and decide the next server """
        player.score += 1  # Increment player score
        self.determine_server()

    def update_game_state(self):
        """ Update the game state on the server """
        if self.point_settled_time:
            if self.ball.is_at_rest():
                current_time = pygame.time.get_ticks()
                if current_time - self.point_settled_time >= self.point_delay_duration:
                    # Reset the ball after the delay
                    self.ball.reset_ball()
                    self.point_settled_time = None  # Reset the delay timer
                return  # Skip the rest of the update logic during the delay


        if self.player_1.serving:
            self.player_2.serving = False
            self.game_state['players'][1]['serving'] = False    
        
        if self.player_2.serving:
            self.player_1.serving = False
            self.game_state['players'][0]['serving'] = False

        if self.ball.served:
            self.ball.move()

        # Move the ball and check for collisions with the net if the ball is served
        if self.ball.in_play:
            self.check_ball_in_play()

#
        
        # Player 1 Swinging Logic
        if self.player_1.is_ball_in_swing_area(self.ball) and self.ball.can_be_hit() and self.game_state['players'][0]['swinging']:
            print("Player 1 hit the ball")
            self.ball.speed_y = self.player_1.swing_speed_y * self.player_1.side
            self.ball.speed_x = self.player_1.swing_speed_x * Random.choice([-1, 1])
            self.ball.speed_z = self.player_1.swing_speed_z
            self.ball.register_hit()

        # Player 2 (or AI) Swinging Logic
        if self.player_2.is_ball_in_swing_area(self.ball) and self.ball.can_be_hit() and self.game_state['players'][1]['swinging']:
            print("Player 2 hit the ball")
            self.ball.speed_y = self.player_2.swing_speed_y * self.player_2.side
            self.ball.speed_x = self.player_2.swing_speed_x * Random.choice([-1, 1])
            self.ball.speed_z = self.player_2.swing_speed_z
            self.ball.register_hit()

        # Update the ball's position in the game state
        self.game_state['ball'] = {
            'x': self.ball.x,
            'y': self.ball.y,
            'z': self.ball.z,
            'speed_x': self.ball.speed_x,
            'speed_y': self.ball.speed_y,
            'served': self.ball.served,
            'angle': self.ball.angle
        }

        self.game_state['players'][0]['score'] = self.player_1.score
        self.game_state['players'][1]['score'] = self.player_2.score

        # Send the updated game state to all clients
        for client in self.clients:
            client.send(pickle.dumps(self.game_state))

    def handle_player_action(self, player_id, data):
        """ Handle player actions such as moving and swinging """
        player = self.player_1 if player_id == 0 else self.player_2
        # Update player's position based on input
        player.x = data['x']
        player.y = data['y']
      
        if data.get('swinging') and not player.swinging:
            player.start_swing()
        player.update_swing()


        self.game_state['players'][player_id]['x'] = player.x
        self.game_state['players'][player_id]['y'] = player.y
        self.game_state['players'][player_id]['swinging'] = data['swinging']

        if  self.game_state['players'][player_id]['serving']:
            self.ball.x = player.x
            self.ball.y = player.y

        if data.get('swinging'):

            if not self.ball.served and player.serving:
                print("Ball served with speed x: %d, y: %d, z: %d" % (data['speed_x'], data['speed_y'], data['speed_z']))
                self.ball.serve(data['speed_x'], data['speed_y'], data['speed_z'], player.x, player.y)
                self.game_state['players'][player_id]['serving'] = False

   
                

    def threaded_client(self, conn, player_id):
        conn.send(pickle.dumps(player_id))  # Send player ID first
        conn.send(pickle.dumps(self.game_state))  # Send initial game state

       
        while True:
            try:
                data = pickle.loads(conn.recv(2048))
                if not data:
                    break

                # Handle player actions
                self.handle_player_action(player_id, data)

                # Update the game state after processing actions
                self.update_game_state()

            except Exception as e:
                print(f"Error: {e}")
                break

        print(f"Player {player_id} disconnected")
        conn.close()
        self.clients.remove(conn)

def start_server():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('172.20.0.84', 5555))  # Bind to localhost on port 5555
    server.listen(2)  # We only need 2 connections for local multiplayer
    game_server = GameServer()
    game_server.determine_server()

    print("Server started! Waiting for connections...")
    try:
        while True:
            conn, addr = server.accept()
            game_server.clients.append(conn)
            print(f"Connected to {addr}")

            # Assign a player ID based on the number of clients connected
            player_id = len(game_server.clients) - 1

            # Start a new thread for the client
            start_new_thread(game_server.threaded_client, (conn, player_id))
    except KeyboardInterrupt:
            print("\nServer is shutting down...")
            server.close()  # Close the server socket
            sys.exit(0)  # Exit the program gracefully

if __name__ == "__main__":
    start_server()
