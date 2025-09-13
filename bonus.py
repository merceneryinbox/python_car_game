import random
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, BONUS_WIDTH, BONUS_HEIGHT
from image_utils import load_game_image


class Bonus:
    def __init__(self, bonus_type):
        self.type = bonus_type
        self.width = BONUS_WIDTH
        self.height = BONUS_HEIGHT
        self.x = random.randint(0, SCREEN_WIDTH - self.width)
        self.y = -self.height
        self.speed = 3
        self.image = None
        self.color = self.get_color()
        self.load_image()

    def get_color(self):
        colors = {
            "regular": (255, 255, 0),
            "shield": (0, 0, 255),
            "gun": (255, 0, 0),
            "jeep": (0, 255, 0),
            "machine_gun": (255, 128, 0),
        }
        return colors.get(self.type, (255, 255, 255))

    def load_image(self):
        bonus_images = {
            "regular": "regular_bonus.png",
            "shield": "shield_bonus.png",
            "gun": "gun_bonus.png",
            "jeep": "jeep_bonus.png",
            "machine_gun": "machine_gun_bonus.png",
        }

        filename = bonus_images.get(self.type)
        if filename:
            self.image = load_game_image(filename, self.width, self.height)
        else:
            print(f"⚠ Неизвестный тип бонуса: {self.type}")

    def move(self):
        self.y += self.speed

    def reset(self):
        self.x = random.randint(0, SCREEN_WIDTH - self.width)
        self.y = -self.height

    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT

    def collides_with(self, player):
        return (self.x < player.x + player.width and
                self.x + self.width > player.x and
                self.y < player.y + player.height and
                self.y + self.height > player.y)

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
