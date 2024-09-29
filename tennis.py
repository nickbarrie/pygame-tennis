import pygame
import sys
from random import Random
from ball import Ball
from player import Player , AIPlayer
from power_bar import PowerBar
from net import Net
from settings import *


# Initialize Pygame
pygame.init()
font = pygame.font.Font('silkscreen.ttf', 36)
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption('Top-Down Tennis Game')


def draw_scores(player_score, ai_score):
    # Render the text for both player and AI scores
    player_text = font.render(f"Player: {player_score}", True, WHITE)
    ai_text = font.render(f"AI: {ai_score}", True, WHITE)

    # Display the scores in the top left and right corners
    screen.blit(player_text, (50, 20))
    screen.blit(ai_text, (WINDOW_WIDTH - 150, 20))

def check_point(ball, player, ai_player):

    if ball.y < 0:
        ai_player.score += 1
        ball.reset_ball()

    if ball.y > WINDOW_HEIGHT:
        player.score += 1
        ball.reset_ball()

    # if ball bouces outside the court
    if (ball.x > net.x + net.width or ball.x < net.x) and ball.z <= 1:
        if ball.speed_y > 0:
            ai_player.score += 1
        else:
            player.score += 1
        ball.reset_ball()


# Ball properties
ball_radius = 5
ball_x = WINDOW_WIDTH // 2
ball_y = WINDOW_HEIGHT // 2
ball_z = 1
ball_speed_x = 4
ball_speed_y = 4
ball_speed_z = 0

net_width = WINDOW_WIDTH //2 
net_height = 10  # Half of the window height

# Main game loop
clock = pygame.time.Clock()

player = Player(WINDOW_WIDTH // 2 , 50, 4, 1)

ai_player = AIPlayer(WINDOW_WIDTH // 2, WINDOW_HEIGHT -100 // 2, 4, -1)

ball = Ball(ball_x, ball_y, ball_z, ball_radius)

power_bar = PowerBar(50, 50, 20, 150, 0, 100)

net = Net(net_width, net_height)

serving = True

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.VIDEORESIZE:
                    WINDOW_WIDTH, WINDOW_HEIGHT = event.w, event.h
                    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not ball.served and not serving:
                    serving = True  
                elif ball.served:
                    player.start_swing()
           
            elif event.key == pygame.K_r:
                ball.served = False
                serving = True



    keys = pygame.key.get_pressed()
    player.move(keys)
    player.update_swing()


    ai_player.update_ai(ball)
    ai_player.update_swing()

    if serving:
        power_bar.update()
        if keys[pygame.K_SPACE]:  # Serve when pressing space again
            if power_bar.is_in_ideal_range():
                serve_speed_y = player.swing_speed_y * player.serve_speed_multiplier * player.side
                serve_speed_x = player.swing_speed_x
                servce_speed_z = player.swing_speed_z
            else:
                serve_speed_y = player.swing_speed_y * player.side
                serve_speed_x = player.swing_speed_x * player.serve_speed_multiplier 
                servce_speed_z = player.swing_speed_z

            ball.serve(serve_speed_x, serve_speed_y, servce_speed_z, player.x, player.y)
            serving = False  # Stop the serving process

    # Move the ball
    if ball.served:
        ball.move()
        ball.check_net_collision(net)

    if player.is_ball_in_swing_area(ball) and ball.can_be_hit() and player.swinging:
        ball.speed_y = player.swing_speed_y * player.side 
        ball.speed_x = player.swing_speed_x * Random().choice([-1, 1])
        ball.speed_z = player.swing_speed_z
        ball.register_hit() 

    
    if ai_player.is_ball_in_swing_area(ball) and ball.can_be_hit():
        ai_player.start_swing()
        ball.speed_y = ai_player.swing_speed_y * ai_player.side
        ball.speed_x = ai_player.swing_speed_x * Random().choice([-1, 1])
        ball.speed_z = ai_player.swing_speed_z
        ball.register_hit()
    
    check_point(ball, player, ai_player)

    # Fill the screen with black
    screen.fill(BLACK)

    player.draw(screen)
    ai_player.draw(screen)
    ball.draw(screen)
    net.draw(screen)
    draw_scores(player.score, ai_player.score)

    if not ball.served and serving:
        power_bar.draw(screen)

    # Update the display
    pygame.display.flip()

    # Set the frame rate
    clock.tick(60)
