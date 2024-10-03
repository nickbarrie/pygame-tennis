import pygame
from settings import WHITE, RED, WINDOW_HEIGHT, WINDOW_WIDTH
import random as Random

class Player:
    def __init__(self, x, y, speed, side):
        self.x = x
        self.y = y
        self.speed = speed
        self.width = 20
        self.height = 20
        self.swinging = False
        self.swing_duration = 500  # Swing lasts 500ms
        self.swing_start_time = 0
        self.swing_speed_x = 2
        self.swing_speed_y = 4
        self.swing_speed_z = 1
        self.serve_speed_multiplier = 2
        self.side = side # 1 for top -1 for bottom
        self.score = 0
        self.serving = False

    def move(self, keys):
        if keys[pygame.K_w]:  # Move up
            self.y -= self.speed
        if keys[pygame.K_s]:  # Move down
            self.y += self.speed
        if keys[pygame.K_a]:  # Move left
            self.x -= self.speed
        if keys[pygame.K_d]:  # Move right
            self.x += self.speed

    def start_swing(self):
        self.swinging = True
        self.swing_start_time = pygame.time.get_ticks()  # Record the time swing started

    def update_swing(self):
        if self.swinging and pygame.time.get_ticks() - self.swing_start_time > self.swing_duration:
            self.swinging = False

    def draw(self,screen):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))
        if self.swinging:
            self.draw_swing(screen)

    def draw_swing(self,screen):
        swing_area = pygame.Rect(self.x + self.width, self.y, 20, 10)
        pygame.draw.rect(screen, RED, swing_area)  
    
    def is_ball_in_swing_area(self, ball):
        swing_area = pygame.Rect(self.x + self.width, self.y, 400, 200)
        ball_rect = pygame.Rect(ball.x - ball.radius, ball.y - ball.radius, ball.radius * 2, ball.radius * 2)
        return swing_area.colliderect(ball_rect) > 0
    
class AIPlayer(Player):
    def __init__(self, x, y, speed, side):
        super().__init__(x, y, speed, side)

    def update_ai(self, ball):

        center_y =  3* WINDOW_HEIGHT // 4 
        center_x = WINDOW_WIDTH // 2
        ai_margin = 50 


        if self.swinging == False:
            if ball.y > WINDOW_HEIGHT // 2:

                if ball.x < self.x  +ai_margin: 
                    self.x -= self.speed
                elif ball.x > self.x:  
                    self.x += self.speed
            
                if ball.y < self.y:
                    self.y -= self.speed
                elif ball.y > self.y: 
                    self.y += self.speed

                if abs(ball.x - self.x) < 30: 
                    if Random.random() < 0.3:  
                        self.speed = 1 
                    else:
                        self.speed = 4  

                self.y = max(0, min(self.y, WINDOW_HEIGHT - self.height))
            else:
                if self.y < center_y:
                    self.y += self.speed 
                elif self.y > center_y:
                    self.y -= self.speed 
                if self.x < center_x:
                    self.x += self.speed  
                elif self.x > center_x:
                    self.x -= self.speed  

