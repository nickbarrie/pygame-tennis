import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, WHITE


class Ball:

    

    def __init__(self, x, y, z, radius):
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius
        self.speed_x = 0
        self.speed_y = 0
        self.speed_z = 0
        self.served = False
        self.last_hit_time = 0 
        self.hit_cooldown = 500  
        self.bounce_count = 0

    def check_net_collision(self, net):
        if self.z <= net.height:
            ball_rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
            net_rect = pygame.Rect(net.x, net.y, net.width, net.height)
            if ball_rect.colliderect(net_rect):
                self.speed_x *= -0.2  # Reverse speed with some energy loss
                self.speed_y *= -0.2
                self.speed_z *= -0.2  # Simulate a bounce upward if needed
                self.z = net.height + 1

    def serve(self, speed_x, speed_y, speed_z, player_x, player_y):
        if not self.served:
            self.x = player_x
            self.y = player_y
            self.z = 1
            self.speed_x = speed_x
            self.speed_y = speed_y
            self.speed_z = speed_z
            self.served = True
            self.bounce_count = 0


    def apply_friction(self):
        drag_coefficient = 0.995  # Simulate friction or air resistance
        cutoff_speed = 0.1 
        
        self.speed_x *= drag_coefficient
        self.speed_y *= drag_coefficient

        self.speed_x *= drag_coefficient
        self.speed_y *= drag_coefficient

        if abs(self.speed_x) < cutoff_speed:
            self.speed_x = 0
        if abs(self.speed_y) < cutoff_speed:
            self.speed_y = 0

    
    def apply_gravity(self):
        self.speed_z = self.speed_z -0.03

    def apply_bounce(self):
        if self.z <= 0:  
            self.speed_z *= -0.8
            self.bounce_count += 1 

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.z += self.speed_z

        self.apply_bounce()
        self.apply_friction()
        self.apply_gravity()
            

    def scale_radius(self, min_z, max_z, min_radius, max_radius):
        z = max(min_z, min(max_z, self.z))  
        return min_radius + (max_radius - min_radius) * ((z - min_z) / (max_z - min_z))

    def draw(self,screen):
        min_z = 0
        max_z = 100
        min_radius = 10
        max_radius = 30
        scaled_radius = self.scale_radius(min_z, max_z, min_radius, max_radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), int(scaled_radius))

    def can_be_hit(self):
        current_time = pygame.time.get_ticks()
        return current_time - self.last_hit_time > self.hit_cooldown

    def register_hit(self):
        self.bounce_count = 0
        self.last_hit_time = pygame.time.get_ticks()

    def reset_ball(self):
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT // 2
        self.speed_x = 0
        self.speed_y = 0
        self.speed_z = 0
        self.served = False  # Ready for the next serve