import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, SCALE_FACTOR, SPRITE_SIZE, GRAY


class Ball(pygame.sprite.Sprite):

    

    def __init__(self,sprite_sheet, x, y, z, radius):
        super().__init__()
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
        self.in_play = False
        self.angle = 0
       
        if sprite_sheet is not None:
            self.image = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE), pygame.SRCALPHA)
            self.image.blit(sprite_sheet, (0, 0), (5 * SPRITE_SIZE, 0, SPRITE_SIZE, SPRITE_SIZE))

            self.rect = self.image.get_rect()  # Create a rect from the image size
            self.rect.center = (x, y)  # Set initial position
        else:
            self.rect = pygame.Rect(x - radius, y - radius, radius , radius )
            self.rect.center = (x, y)

    def check_net_collision(self, net):
        if self.z <= net.height:
            ball_rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
            net_rect = pygame.Rect(net.x, net.y, net.width, net.height)
            if ball_rect.colliderect(net_rect):
                self.speed_x *= -0.2  # Reverse speed with some energy loss
                self.speed_y *= -0.2
                self.speed_z *= -0.2  # Simulate a bounce upward if needed
                return True
        return False

    def serve(self, speed_x, speed_y, speed_z, player_x, player_y):
        if not self.served:
            print("Ball served")
            self.x = player_x
            self.y = player_y
            self.z = 1
            self.speed_x = speed_x
            self.speed_y = speed_y
            self.speed_z = speed_z
            self.served = True
            self.in_play = True
            self.bounce_count = 0

    
    def is_at_rest(self):
        # Check if the ball's speed and height indicate it's at rest
        return self.speed_z == 0 and self.z == 0 and self.speed_x == 0 and self.speed_y == 0

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
        if abs(self.speed_z) < cutoff_speed and self.z <= 0.02:
            self.speed_z = 0
            self.z = 0

    
    def apply_gravity(self):
        if self.z > 0:
            self.speed_z -= 0.03


    def apply_bounce(self):
        if self.z < 0:  
            self.speed_z *= -0.8
            self.bounce_count += 1 

    def apply_spin(self):
        ball_velocity = (self.speed_x ** 2 + self.speed_y ** 2) ** 0.5

        if self.speed_y > 0:
            self.angle -= 1 * ball_velocity   # Spin clockwise when moving down
        else:
            self.angle += 1 * ball_velocity # Spin counter-clockwise when moving up

        self.angle %= 360

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.z += self.speed_z

        self.rect.center = (self.x, self.y)
        
        self.apply_bounce()
        self.apply_friction()
        self.apply_gravity()
        self.apply_spin()

            

    def scale_radius(self, min_z, max_z, min_radius, max_radius):
        z = max(min_z, min(max_z, self.z))  
        return min_radius + (max_radius - min_radius) * ((z - min_z) / (max_z - min_z))

    def draw(self,screen):
        
        min_z = 0
        max_z = 20
        min_radius = 10
        max_radius = 20
        scaled_radius = self.scale_radius(min_z, max_z, min_radius, max_radius)


        scaled_image = pygame.transform.scale(self.image, (int(SCALE_FACTOR * scaled_radius), int(SCALE_FACTOR * scaled_radius)))
        scaled_rotated_image = pygame.transform.rotate(scaled_image, self.angle)
        rotated_rect = scaled_rotated_image.get_rect(center=(self.x, self.y))


            # Draw the shadow
        shadow_width = max(1, int(scaled_radius * (2 - self.z / max_z)))  
        shadow_height = max(1, int(scaled_radius * .7 * (1.2 - self.z / max_z)))

        shadow_color = (0, 0, 0, max(0, min(255, int(150 * (1 - self.z / max_z)))))

        
        # Create a surface for the shadow with alpha transparency
        shadow_surface = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, shadow_color, shadow_surface.get_rect())
        
        # Calculate shadow position (directly below the ball)
        shadow_x = self.x - shadow_width // 2
        shadow_y = self.y + scaled_radius // 2 + self.z * SCALE_FACTOR  # The shadow is slightly below the ball's y-position
        
        # Draw the shadow on the screen
        screen.blit(shadow_surface, (shadow_x, shadow_y))

        screen.blit(scaled_rotated_image, rotated_rect.topleft)

    def can_be_hit(self):
        current_time = pygame.time.get_ticks()
        return current_time - self.last_hit_time > self.hit_cooldown

    def register_hit(self):
        self.bounce_count = 0
        self.last_hit_time = pygame.time.get_ticks()

    def reset_ball(self):
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT // 2
        self.z = 0
        self.speed_x = 0
        self.speed_y = 0
        self.speed_z = 0
        self.served = False  # Ready for the next serve
        self.bounce_count = 0
        self.in_play = False