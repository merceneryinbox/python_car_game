# game_logic.py
import pygame
import random
from assets import player_move_sound, enemy_move_sound, backgrounds
from settings import player_speed, screen_width, screen_height, bonus_spawn_chance, shield_spawn_chance, gun_spawn_chance

# Функция для обработки движения игрока
def handle_player_movement(keys, player_x):
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < screen_width - player_width:
        player_x += player_speed
    return player_x

# Функция для обновления врагов и бонусов
def update_positions(enemy_y, bonus_y, shield_bonus_y, gun_bonus_y):
    enemy_y += enemy_speed
    if random.random() < bonus_spawn_chance:
        bonus_y += bonus_speed
    if random.random() < shield_spawn_chance:
        shield_bonus_y += shield_bonus_speed
    if random.random() < gun_spawn_chance:
        gun_bonus_y += gun_bonus_speed
    return enemy_y, bonus_y, shield_bonus_y, gun_bonus_y
