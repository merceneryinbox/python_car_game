
import pygame
import sys
import random
import time

# Инициализация Pygame и звука
pygame.init()
pygame.mixer.init()

# Настройка экрана
screen_width = 1300
screen_height = 660
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Моя игра')

# Загрузка фонов для каждого уровня
backgrounds = []
for i in range(1, 8):  # Предполагается, что у вас есть 7 фоновых изображений
    try:
        bg_image = pygame.image.load(f'assets/desert_background_level_{i}.png')
        bg_image = pygame.transform.scale(bg_image, (screen_width, screen_height))
        backgrounds.append(bg_image)
    except FileNotFoundError:
        temp_bg = pygame.Surface((screen_width, screen_height))
        temp_bg.fill((194, 178, 128))  # Цвет песка, если фон не найден
        backgrounds.append(temp_bg)

# Список треков для фоновой музыки
playlist = [
    'assets/background_music1.mp3',
    'assets/background_music2.mp3',
    'assets/background_music3.mp3'
]
menu_music = 'assets/menu_music.mp3'

# Функция для воспроизведения трека уровня
def play_track_for_level(level):
    track_index = (level - 1) % len(playlist)
    pygame.mixer.music.load(playlist[track_index])
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

# Функция для воспроизведения музыки меню
def play_menu_music():
    pygame.mixer.music.load(menu_music)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

# Установка события для отслеживания окончания текущего трека
pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)

# Загрузка изображений игрока, врага и бонусов
try:
    player_image = pygame.image.load('assets/car_player.png')
    player_image = pygame.transform.scale(player_image, (50, 60))
except FileNotFoundError:
    player_image = pygame.Surface((50, 60))
    player_image.fill((0, 255, 0))

try:
    gun_image = pygame.image.load('assets/gun.png')
    gun_image = pygame.transform.scale(gun_image, (30, 30))
except FileNotFoundError:
    gun_image = pygame.Surface((30, 30))
    gun_image.fill((255, 0, 0))  # Красный цвет для бонуса пушки

bullet_image = pygame.Surface((10, 4))
bullet_image.fill((255, 255, 0))  # Желтый цвет пули

try:
    gun_sound = pygame.mixer.Sound('assets/gun_fire.wav')
    gun_sound.set_volume(0.5)
except FileNotFoundError:
    gun_sound = None  # Обработка, если звук не найден

# Параметры игрока и бонуса
player_x = screen_width // 2 - 25
player_y = screen_height - 70
gun_bonus_x = random.randint(0, screen_width - 30)
gun_bonus_y = -30
gun_bonus_speed = 1.0
gun_active = False
gun_start_time = 0
bullets = []  # Список для хранения активных пуль

# Основной игровой цикл
running = True
while running:
    # Проверка времени действия бонуса пушки
    if gun_active and time.time() - gun_start_time > 5:
        gun_active = False
    
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Перемещение игрока
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= 5
    if keys[pygame.K_RIGHT] and player_x < screen_width - 50:
        player_x += 5

    # Если бонус пушки активен, стреляем пулей
    if gun_active:
        if len(bullets) < 5:  # Ограничение количества пуль
            bullets.append([player_x + 20, player_y])
            if gun_sound:
                gun_sound.play()

    # Перемещение пуль
    for bullet in bullets[:]:
        bullet[1] -= 7  # Скорость пули
        if bullet[1] < 0:  # Удаление пуль, вышедших за экран
            bullets.remove(bullet)

    # Отрисовка фона и объектов
    screen.fill((0, 0, 0))  # Черный фон
    screen.blit(player_image, (player_x, player_y))
    screen.blit(gun_image, (gun_bonus_x, gun_bonus_y))

    # Отрисовка пуль
    for bullet in bullets:
        screen.blit(bullet_image, bullet)

    pygame.display.flip()

pygame.quit()
sys.exit()
