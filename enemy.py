import random
import pygame
from assets_loader import load_image
from constants import *

class Enemy:
    def __init__(self):
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.x = random.randint(0, SCREEN_WIDTH - self.width)
        self.y = 0 - self.height
        self.speed = ENEMY_SPEED
        self.image = None

    def load_image(self):
        """Load enemy image with fallback"""
        self.image = load_image('assets/car_enemy.png',
                              (self.width, self.height),
                              RED)

    def move(self):
        """Move enemy down the screen"""
        self.y += self.speed

    def reset(self):
        """Reset enemy position"""
        self.x = random.randint(0, SCREEN_WIDTH - self.width)
        self.y = 0 - self.height

    def is_off_screen(self):
        """Check if enemy is off screen"""
        return self.y > SCREEN_HEIGHT

    def collides_with(self, player):
        """Check collision with player"""
        return (player.x < self.x + self.width and
                player.x + player.width > self.x and
                player.y < self.y + self.height and
                player.y + player.height > self.y)

    def draw(self, screen):
        """Draw enemy on screen"""
        screen.blit(self.image, (self.x, self.y))