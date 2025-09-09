import pygame
import random
import os
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, BONUS_WIDTH, BONUS_HEIGHT


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
        """Возвращает цвет для бонуса (резервный вариант)"""
        if self.type == "regular":
            return (255, 255, 0)  # Желтый
        elif self.type == "shield":
            return (0, 0, 255)  # Синий
        elif self.type == "gun":
            return (255, 0, 0)  # Красный
        return (255, 255, 255)  # Белый по умолчанию

    def load_image(self):
        """Загружает изображение для бонуса"""
        try:
            # Получаем абсолютный путь к файлу
            base_dir = os.path.dirname(os.path.abspath(__file__))

            if self.type == "regular":
                image_path = os.path.join(base_dir, 'assets', 'images', 'regular_bonus.png')
            elif self.type == "shield":
                image_path = os.path.join(base_dir, 'assets', 'images', 'shield_bonus.png')
            elif self.type == "gun":
                image_path = os.path.join(base_dir, 'assets', 'images', 'gun_bonus.png')
            else:
                print("Папка assets/images не существует!")
                return

            # Проверяем существование файла
            if not os.path.exists(image_path):
                print(f"Файл не найден: {image_path}")
                return

            # Загружаем изображение
            self.image = pygame.image.load(image_path).convert_alpha()
            print(f"Image loaded successfully: {image_path}")

            # Масштабируем изображение до нужного размера
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
            print(f"Изображение загружено: {image_path}")

        except Exception as e:
            print(f"Ошибка загрузки изображения для бонуса {self.type}: {e}")
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