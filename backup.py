import pygame
import sys
import random

# Инициализация Pygame и звука
pygame.init()
pygame.mixer.init()

# Настройка экрана
screen_width = 1280
screen_height = 660
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Моя игра')

# Список треков для фоновой музыки
playlist = [
    'assets/sounds/background_music1.mp3',
    'assets/sounds/background_music2.mp3',
    'assets/sounds/background_music3.mp3'
]
menu_music = 'assets/sounds/menu_music.mp3'  # Музыка для меню

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

# Загрузка изображений
car_image = pygame.image.load('assets/images/car.PNG')
player_image = pygame.transform.scale(car_image, (50, 60))
enemy_image = pygame.transform.scale(car_image, (50, 60))

# Загрузка звуков
player_move_sound = pygame.mixer.Sound('assets/sounds/player_move.wav')
enemy_move_sound = pygame.mixer.Sound('assets/sounds/enemy_move.wav')
slide_sound = pygame.mixer.Sound('assets/sounds/slide.wav')

# Настройка громкости
player_move_sound.set_volume(0.3)
enemy_move_sound.set_volume(0.3)
slide_sound.set_volume(0.5)

# Параметры игрока
player_width = 50
player_height = 60
player_x = screen_width // 2 - player_width // 2
player_y = screen_height - player_height - 10
player_speed = 2
player_lives = 3

# Параметры врага
enemy_width = 50
enemy_height = 60
enemy_x = random.randint(0, screen_width - enemy_width)
enemy_y = 0 - enemy_height
enemy_speed = 0.2

# Счетчики и уровни
enemies_defeated = 0
current_level = 1
enemies_to_next_level = 10
game_state = "level_select"  # Начальное состояние - меню

# Укажите количество уровней
max_levels = 7

# Шрифт для текста
font = pygame.font.SysFont(None, 36)

# Функция для отображения меню уровней
def draw_level_menu():
    screen.fill((0, 0, 0))
    title_text = font.render("Выберите уровень:", True, (255, 255, 255))
    screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 50))

    # Отображаем уровни в два ряда по 5 (или меньше)
    for i in range(max_levels):
        row = i // 5
        col = i % 5
        level_text = font.render(f"Уровень {i + 1}", True, (255, 255, 255))
        level_rect = pygame.Rect(
            screen_width // 2 - 250 + col * 120,
            150 + row * 100,
            100, 50
        )
        pygame.draw.rect(screen, (0, 100, 200), level_rect)
        screen.blit(level_text, (level_rect.x + 10, level_rect.y + 10))

# Функция для запуска уровня
def start_level(level):
    global game_state, player_lives, enemies_defeated, current_level, enemies_to_next_level, enemy_speed
    game_state = "playing"
    player_lives = 5
    enemies_defeated = 0
    current_level = level
    enemies_to_next_level = 10 + (level - 1) * 5
    enemy_speed = 0.5 + level  # Увеличение скорости врагов на каждом уровне
    pygame.mixer.music.stop()  # Остановить музыку меню
    play_track_for_level(level)  # Воспроизведение трека для уровня
    reset_positions()

# Сброс позиции игрока и врага
def reset_positions():
    global player_x, player_y, enemy_x, enemy_y
    player_x = screen_width // 2 - player_width // 2
    player_y = screen_height - player_height - 10
    enemy_x = random.randint(0, screen_width - enemy_width)
    enemy_y = 0 - enemy_height

# Воспроизведение музыки меню при старте
play_menu_music()

# Основной игровой цикл
running = True
while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.USEREVENT + 1:
            if game_state == "playing":
                play_track_for_level(current_level)

        if game_state == "playing":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    slide_sound.play()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    slide_sound.stop()

        elif game_state == "level_select":
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i in range(max_levels):
                    row = i // 5
                    col = i % 5
                    level_rect = pygame.Rect(
                        screen_width // 2 - 250 + col * 120,
                        150 + row * 100,
                        100, 50
                    )
                    if level_rect.collidepoint(mouse_pos):
                        start_level(i + 1)

    if game_state == "playing":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < screen_width - player_width:
            player_x += player_speed

        enemy_y += enemy_speed
        if enemy_y > screen_height:
            enemy_y = 0 - enemy_height
            enemy_x = random.randint(0, screen_width - enemy_width)
            enemies_defeated += 1
            if enemies_defeated >= enemies_to_next_level:
                game_state = "level_select"
                pygame.mixer.music.stop()  # Остановить музыку уровня
                play_menu_music()  # Воспроизведение музыки меню

        if (player_x < enemy_x + enemy_width and
            player_x + player_width > enemy_x and
            player_y < enemy_y + enemy_height and
            player_y + player_height > enemy_y):
            player_lives -= 1
            reset_positions()
            if player_lives <= 0:
                game_state = "level_select"
                pygame.mixer.music.stop()  # Остановить музыку уровня
                play_menu_music()  # Воспроизведение музыки меню

        screen.blit(player_image, (player_x, player_y))
        screen.blit(enemy_image, (enemy_x, enemy_y))

        lives_text = font.render(f'Жизни: {player_lives}', True, (255, 255, 255))
        defeated_text = font.render(f'Побеждено врагов: {enemies_defeated}/{enemies_to_next_level}', True, (255, 255, 255))
        level_text = font.render(f'Уровень: {current_level}', True, (255, 255, 255))
        screen.blit(lives_text, (10, 10))
        screen.blit(defeated_text, (10, 50))
        screen.blit(level_text, (10, 90))

    elif game_state == "level_select":
        draw_level_menu()

    pygame.display.flip()

# Завершение Pygame
pygame.quit()
sys.exit()
