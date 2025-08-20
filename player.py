import pygame
from constants import *
from assets_loader import load_image

class Player:
    def __init__(self):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 10
        self.speed = PLAYER_SPEED
        self.lives = PLAYER_LIVES
        self.score = 0
        self.image = None
        self.shield_active = False
        self.shield_start_time = 2
        self.gun_active = False
        self.gun_start_time = 2

    def load_image(self):
        """Load player image with fallback"""
        self.image = load_image('assets/images/car_player.PNG',
                                (self.width, self.height),
                                GREEN)

    def move(self, direction):
        """Move player left or right"""
        if direction == "left" and self.x > 0:
            self.x -= self.speed
        elif direction == "right" and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed

    def activate_shield(self):
        """Activate shield power-up"""
        self.shield_active = True
        self.shield_start_time = pygame.time.get_ticks() / 1000

    def activate_gun(self):
        """Activate gun power-up"""
        self.gun_active = True
        self.gun_start_time = pygame.time.get_ticks() / 1000

    def update_powerups(self):
        """Check and deactivate expired power-ups"""
        current_time = pygame.time.get_ticks() / 1000
        if self.shield_active and current_time - self.shield_start_time > SHIELD_DURATION:
            self.shield_active = False
        if self.gun_active and current_time - self.gun_start_time > GUN_DURATION:
            self.gun_active = False

    def reset(self):
        """Reset player position and state"""
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 10
        self.shield_active = False
        self.gun_active = False

    def draw(self, screen):
        """Draw player on screen"""
        screen.blit(self.image, (self.x, self.y))
        if self.shield_active:
            pygame.draw.circle(screen, CYAN,
                             (self.x + self.width // 2, self.y + self.height // 2),
                             40, 2)