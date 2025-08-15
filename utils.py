# utils.py
import pygame
import random
from settings import screen_width, screen_height, enemy_width, enemy_height

# Функция для воспроизведения трека уровня
def play_track_for_level(level, playlist):
    track_index = (level - 1) % len(playlist)
    pygame.mixer.music.load(playlist[track_index])
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

# Функция для воспроизведения музыки меню
def play_menu_music(menu_music):
    pygame.mixer.music.load(menu_music)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

# Функция для сброса позиции игрока, врагов и бонусов
def reset_positions():
    player_x = screen_width // 2 - player_width // 2
    player_y = screen_height - player_height - 10
    enemy_x = random.randint(0, screen_width - enemy_width)
    enemy_y = 0 - enemy_height
    return player_x, player_y, enemy_x, enemy_y