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
    enemy_image = pygame.image.load('assets/car_enemy.png')
    enemy_image = pygame.transform.scale(enemy_image, (50, 60))
except FileNotFoundError:
    enemy_image = pygame.Surface((50, 60))
    enemy_image.fill((255, 0, 0))

try:
    bonus_image = pygame.image.load('assets/bonus.png')
    bonus_image = pygame.transform.scale(bonus_image, (30, 30))
except FileNotFoundError:
    bonus_image = pygame.Surface((30, 30))
    bonus_image.fill((255, 215, 0))  # Золотой цвет для обычного бонуса

# Загрузка изображения бонуса щита и бонуса пушки
try:
    shield_image = pygame.image.load('assets/shield.png')
    shield_image = pygame.transform.scale(shield_image, (30, 30))
except FileNotFoundError:
    shield_image = pygame.Surface((30, 30))
    shield_image.fill((0, 255, 255))  # Цвет для бонуса щита

try:
    gun_image = pygame.image.load('assets/gun.png')
    gun_image = pygame.transform.scale(gun_image, (30, 30))
except FileNotFoundError:
    gun_image = pygame.Surface((30, 30))
    gun_image.fill((255, 0, 0))  # Красный цвет для бонуса пушки

# Загрузка звуков
player_move_sound = pygame.mixer.Sound('assets/player_move.wav')
enemy_move_sound = pygame.mixer.Sound('assets/enemy_move.wav')
slide_sound = pygame.mixer.Sound('assets/slide.wav')

# Настройка громкости
player_move_sound.set_volume(0.4)
enemy_move_sound.set_volume(0.0)
slide_sound.set_volume(0.5)

# Параметры игрока
player_width = 50
player_height = 60
player_x = screen_width // 2 - player_width // 2
player_y = screen_height - player_height - 10
player_speed = 2
player_lives = 5
player_score = 0

# Параметры врага
enemy_width = 50
enemy_height = 60
enemy_x = random.randint(0, screen_width - enemy_width)
enemy_y = 0 - enemy_height
enemy_speed = 0.2
max_enemy_speed = 2.3

# Параметры бонусов
bonus_width = 30
bonus_height = 30

# Обычный бонус
bonus_x = random.randint(0, screen_width - bonus_width)
bonus_y = 0 - bonus_height
bonus_speed = 1.0  # Скорость обычного бонуса

# Бонус щита
shield_bonus_x = random.randint(0, screen_width - bonus_width)
shield_bonus_y = -bonus_height  # Скрытый бонус щита
shield_bonus_speed = 1.0
shield_active = False
shield_start_time = 0

# Бонус пушки
gun_bonus_x = random.randint(0, screen_width - bonus_width)
gun_bonus_y = -bonus_height  # Скрытый бонус пушки
gun_bonus_speed = 1.0
gun_active = False
gun_start_time = 0

# Шансы появления бонусов (чем меньше число, тем реже падают бонусы)
bonus_spawn_chance = 0.4
shield_spawn_chance = 0.2
gun_spawn_chance = 0.3

# Счетчики и уровни
enemies_defeated = 0
current_level = 1
enemies_to_next_level = 10
game_state = "level_select"

# Укажите количество уровней
max_levels = 7
level_rects = []  # Список для хранения прямоугольников уровней

# Шрифт для текста
font = pygame.font.SysFont(None, 36)

# Функция для отображения меню уровней
def draw_level_menu():
    global level_rects
    screen.blit(backgrounds[0], (0, 0))  # Фон меню
    title_text = font.render("Выберите уровень:", True, (255, 255, 255))
    screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 50))

    level_rects.clear()  # Очистка списка уровней перед рисованием

    for level_index in range(max_levels):
        row = level_index // 5
        col = level_index % 5
        level_text = font.render(f"Уровень {level_index + 1}", True, (255, 255, 255))
        level_rect = pygame.Rect(
            screen_width // 2 - 250 + col * 120,
            150 + row * 100,
            100, 50
        )
        level_rects.append(level_rect)
        pygame.draw.rect(screen, (0, 200, 0) if level_index + 1 == current_level else (100, 100, 100), level_rect)
        screen.blit(level_text, (level_rect.x + 10, level_rect.y + 10))

# Функция для запуска уровня
def start_level(level):
    global game_state, player_lives, enemies_defeated, current_level, enemies_to_next_level, enemy_speed
    game_state = "playing"  # Переключаем состояние на "playing"
    player_lives = 5
    enemies_defeated = 0
    current_level = level
    enemies_to_next_level = 10 + (level - 1) * 5
    enemy_speed = min(0.5 + level, max_enemy_speed)
    pygame.mixer.music.stop()
    play_track_for_level(level)
    reset_positions()

# Сброс позиции игрока, врага и бонусов
def reset_positions():
    global player_x, player_y, enemy_x, enemy_y, bonus_x, bonus_y, shield_bonus_x, shield_bonus_y, gun_bonus_x, gun_bonus_y
    player_x = screen_width // 2 - player_width // 2
    player_y = screen_height - player_height - 10
    enemy_x = random.randint(0, screen_width - enemy_width)
    enemy_y = 0 - enemy_height
    bonus_x = random.randint(0, screen_width - bonus_width)
    bonus_y = 0 - bonus_height
    shield_bonus_x = random.randint(0, screen_width - bonus_width)
    shield_bonus_y = -bonus_height  # Убираем бонус щита за экран
    gun_bonus_x = random.randint(0, screen_width - bonus_width)
    gun_bonus_y = -bonus_height  # Убираем бонус пушки за экран

# Воспроизведение музыки меню при старте
play_menu_music()

# Основной игровой цикл
running = True
while running:
    # Проверка окончания действия щита
    if shield_active and time.time() - shield_start_time > 10:
        shield_active = False

    # Проверка окончания действия пушки
    if gun_active and time.time() - gun_start_time > 5:
        gun_active = False

    # Отрисовка фона в зависимости от состояния игры
    if game_state == "level_select":
        draw_level_menu()
    elif game_state == "playing":
        screen.blit(backgrounds[current_level - 1], (0, 0))

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and game_state == "level_select":
            mouse_pos = pygame.mouse.get_pos()
            # Проверяем нажатие на каждый прямоугольник уровня
            for i, rect in enumerate(level_rects):
                if rect.collidepoint(mouse_pos):
                    start_level(i + 1)  # Запуск уровня, если нажали на его прямоугольник

    # Если игра в состоянии "playing", обновляем положение игрока и врагов
    if game_state == "playing":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
            player_move_sound.play()  # Воспроизведение звука при перемещении игрока
            if keys[pygame.K_LEFT] and player_x > 0:
                player_x -= player_speed
            if keys[pygame.K_RIGHT] and player_x < screen_width - player_width:
                player_x += player_speed
        else:
            player_move_sound.stop()  # Остановка звука, если игрок не двигается

        # Воспроизведение звука при движении врага вниз
        if enemy_y > 0:
            enemy_move_sound.play()
        else:
            enemy_move_sound.stop()

        enemy_y += enemy_speed

        # Обновление положения бонусов с учетом вероятности появления
        if random.random() < bonus_spawn_chance:
            bonus_y += bonus_speed
        if random.random() < shield_spawn_chance:
            shield_bonus_y += shield_bonus_speed
        if random.random() < gun_spawn_chance:
            gun_bonus_y += gun_bonus_speed

        # Если бонус-пушка активна, уничтожаем врагов на одной линии с игроком
        if gun_active and abs(player_y - enemy_y) < 10:
            enemies_defeated += 1  # Уничтожаем врага и увеличиваем счетчик
            enemy_y = 0 - enemy_height  # Сбрасываем врага наверх

        # Проверка на выход врагов и бонусов за экран и сброс их позиции
        if enemy_y > screen_height:
            enemy_y = 0 - enemy_height
            enemy_x = random.randint(0, screen_width - enemy_width)
            if not gun_active:
                enemies_defeated += 1
            if enemies_defeated >= enemies_to_next_level:
                game_state = "level_select"
                pygame.mixer.music.stop()
                play_menu_music()

        if bonus_y > screen_height:
            bonus_y = 0 - bonus_height
            bonus_x = random.randint(0, screen_width - bonus_width)

        if shield_bonus_y > screen_height:
            shield_bonus_y = -bonus_height
            shield_bonus_x = random.randint(0, screen_width - bonus_width)

        if gun_bonus_y > screen_height:
            gun_bonus_y = -bonus_height
            gun_bonus_x = random.randint(0, screen_width - bonus_width)

        # Проверка столкновений игрока с врагом и бонусами
        if (player_x < enemy_x + enemy_width and player_x + player_width > enemy_x and
                player_y < enemy_y + enemy_height and player_y + player_height > enemy_y):
            if not shield_active:
                player_lives -= 1  # Уменьшаем жизни игрока
                reset_positions()
                if player_lives <= 0:
                    game_state = "level_select"
                    pygame.mixer.music.stop()
                    play_menu_music()

        if (player_x < bonus_x + bonus_width and player_x + player_width > bonus_x and
                player_y < bonus_y + bonus_height and player_y + player_height > bonus_y):
            player_score += 1
            bonus_y = 0 - bonus_height
            bonus_x = random.randint(0, screen_width - bonus_width)

        if (player_x < shield_bonus_x + bonus_width and player_x + player_width > shield_bonus_x and
                player_y < shield_bonus_y + bonus_height and player_y + player_height > shield_bonus_y):
            shield_active = True
            shield_start_time = time.time()
            shield_bonus_y = -bonus_height
            shield_bonus_x = random.randint(0, screen_width - bonus_width)

        if (player_x < gun_bonus_x + bonus_width and player_x + player_width > gun_bonus_x and
                player_y < gun_bonus_y + bonus_height and player_y + player_height > gun_bonus_y):
            gun_active = True
            gun_start_time = time.time()
            gun_bonus_y = -bonus_height
            gun_bonus_x = random.randint(0, screen_width - bonus_width)

        # Отрисовка игрока, врага и бонусов
        screen.blit(player_image, (player_x, player_y))
        screen.blit(enemy_image, (enemy_x, enemy_y))
        screen.blit(bonus_image, (bonus_x, bonus_y))
        screen.blit(shield_image, (shield_bonus_x, shield_bonus_y))
        screen.blit(gun_image, (gun_bonus_x, gun_bonus_y))

        if shield_active:
            pygame.draw.circle(screen, (0, 255, 255), (player_x + player_width // 2, player_y + player_height // 2), 40, 2)

        # Отображение статистики
        lives_text = font.render(f'Жизни: {player_lives}', True, (255, 255, 255))
        defeated_text = font.render(f'Побеждено врагов: {enemies_defeated}', True, (255, 255, 255))
        screen.blit(lives_text, (10, 10))
        screen.blit(defeated_text, (10, 50))

    pygame.display.flip()

pygame.quit()
sys.exit()