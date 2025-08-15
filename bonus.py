import random
import pygame
from assets_loader import load_image
from config import *

class Bonus:
    def __init__(self, bonus_type="regular"):
        self.width = BONUS_WIDTH
        self.height = BONUS_HEIGHT
        self.x = random.randint(0, SCREEN_WIDTH - self.width)
        self.y = 0 - self.height
        self.speed = BONUS_SPEED
        self.type = bonus_type
        self.image = None
        self.load_image()

    def load_image(self):
        """Load appropriate image based on bonus type"""
        if self.type == "shield":
            self.image = load_image('assets/shield.png',
                                  (self.width, self.height),
                                  CYAN)
        elif self.type == "gun":
            self.image = load_image('assets/gun.png',
                                  (self.width, self.height),
                                  RED)
        else:  # regular bonus
            self.image = load_image('assets/bonus.png',
                                  (self.width, self.height),
                                  GOLD)

    def move(self):
        """Move bonus down the screen"""
        self.y += self.speed

    def reset(self):
        """Reset bonus position"""
        self.x = random.randint(0, SCREEN_WIDTH - self.width)
        self.y = 0 - self.height

    def is_off_screen(self):
        """Check if bonus is off screen"""
        return self.y > SCREEN_HEIGHT

    def collides_with(self, player):
        """Check collision with player"""
        return (player.x < self.x + self.width and
                player.x + player.width > self.x and
                player.y < self.y + self.height and
                player.y + player.height > self.y)

    def draw(self, screen):
        """Draw bonus on screen"""
        screen.blit(self.image, (self.x, self.y))