import pygame
import random
from constants import SCREEN_WIDTH, BONUS_WIDTH, BONUS_HEIGHT


class Bonus:
    def __init__(self, bonus_type):
        self.type = bonus_type
        self.width = BONUS_WIDTH
        self.height = BONUS_HEIGHT
        self.x = random.randint(0, SCREEN_WIDTH - self.width)
        self.y = -self.height
        self.speed = 2
        self.image = None
        self.load_image()

    def load_image(self):
        """Загружает изображение для бонуса"""
        try:
            if self.type == "regular":
                self.image = pygame.image.load('assets/images/regular_bonus.png')
            elif self.type == "shield":
                self.image = pygame.image.load('assets/images/shield_bonus.png')
            elif self.type == "gun":
                self.image = pygame.image.load('assets/images/gun_bonus.png')

            # Масштабируем изображение до нужного размера
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except:
            # Если изображение не загрузилось, создаем цветной прямоугольник
            if self.type == "regular":
                self.color = (255, 255, 0)  # Желтый
            elif self.type == "shield":
                self.color = (0, 0, 255)  # Синий
            elif self.type == "gun":
                self.color = (255, 0, 0)  # Красный
            self.image = None

    def move(self):
        """Двигает бонус вниз"""
        self.y += self.speed

    def reset(self):
        """Сбрасывает позицию бонуса"""
        self.x = random.randint(0, SCREEN_WIDTH - self.width)
        self.y = -self.height

    def is_off_screen(self):
        """Проверяет, ушел ли бонус за экран"""
        return self.y > SCREEN_HEIGHT

    def collides_with(self, player):
        """Проверяет столкновение с игроком"""
        return (self.x < player.x + player.width and
                self.x + self.width > player.x and
                self.y < player.y + player.height and
                self.y + self.height > player.y)

    def draw(self, screen):
        """Рисует бонус на экране"""
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            # Резервный вариант - цветной прямоугольник
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))