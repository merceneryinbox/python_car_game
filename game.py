import random
import sys
import pygame
import os
from assets_loader import load_backgrounds, load_image

from assets_loader import load_backgrounds
from bonus import Bonus
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GREEN, RED, BONUS_HEIGHT, ENEMIES_FOR_FIRST_LEVEL, LEVEL_INCREMENT,
    MAX_ENEMY_SPEED, PLAYER_LIVES, MAX_LEVELS, FPS,
    BONUS_SPAWN_CHANCE, SHIELD_SPAWN_CHANCE, GUN_SPAWN_CHANCE, JEEP_SPAWN_CHANCE, JEEP_DURATION,
    ROAD_WIDTH
)
from enemy import Enemy
from player import Player


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.game = None  # Ссылка на game объект

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Turbo Racing')

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 25)

        # Game states
        self.game_state = "level_select"
        self.current_level = 1
        self.max_unlocked_level = 1
        self.enemies_defeated = 10
        self.enemies_to_next_level = ENEMIES_FOR_FIRST_LEVEL

        # Load assets
        self.backgrounds = load_backgrounds()

        # === ИСПРАВЛЕНО: Убрано дублирование создания текстур ===
        # Загружаем текстуры для дороги и пустыни
        print("Создаем текстуры дороги и пустыни...")

        # Дорога
        self.road_texture = pygame.Surface((ROAD_WIDTH, SCREEN_HEIGHT))
        self.road_texture.fill((50, 50, 50))  # Темно-серый цвет дороги

        # Переменные для анимации дороги
        self.road_offset = 2  # Смещение для анимации дороги
        self.road_speed = 3  # Скорость движения дороги

        # === ВСТАВЬТЕ ЭТОТ БЛОК ЗДЕСЬ ===
        # Добавляем красные линии по краям дороги
        pygame.draw.rect(self.road_texture, RED, (0, 0, 5, SCREEN_HEIGHT))  # Левая красная линия
        pygame.draw.rect(self.road_texture, RED, (ROAD_WIDTH - 5, 0, 5, SCREEN_HEIGHT))  # Правая красная линия
        # Добавляем разметку на дорогу
        for i in range(0, SCREEN_HEIGHT, 60):
            pygame.draw.rect(self.road_texture, (255, 255, 0), (ROAD_WIDTH // 2 - 5, i, 10, 30))  # Желтая разметка

        # Пустыня
        self.desert_texture = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.desert_texture.fill((194, 178, 128))  # Песочный цвет
        # Добавляем детали пустыни
        for _ in range(50):
            x = random.randint(0, SCREEN_WIDTH - 1)
            y = random.randint(0, SCREEN_HEIGHT - 1)
            size = random.randint(3, 8)
            if random.random() > 0.3:
                pygame.draw.circle(self.desert_texture, (139, 69, 19), (x, y), size)  # Коричневые камни
            else:
                pygame.draw.circle(self.desert_texture, (34, 139, 34), (x, y), size)  # Зеленые кактусы

        print(f"Текстуры созданы: дорога {self.road_texture.get_size()}, пустыня {self.desert_texture.get_size()}")

        self.load_sounds()
        self.load_music()

        # Game objects
        self.player = Player()
        self.player.load_image()
        self.enemy = Enemy()
        self.enemy.load_image()
        self.regular_bonus = Bonus("regular")
        self.shield_bonus = Bonus("shield")
        self.gun_bonus = Bonus("gun")

        # Initially hide special bonuses
        self.shield_bonus.y = -BONUS_HEIGHT
        self.gun_bonus.y = -BONUS_HEIGHT

        # Jeep bonus
        self.jeep_bonus = Bonus("jeep")
        self.jeep_bonus.y = -BONUS_HEIGHT  # Скрываем initially

        # Добавьте флаги для джипа
        self.jeep_active = False
        self.jeep_time = 0
        self.original_player_image = None  # Для хранения оригинального изображения
        self.jeep_image = None  # Изображение джипа

        # Таблички со скелетом
        self.skeleton_signs = []
        self.skeleton_head_image = None  # Изменили на голову
        self.skeleton_spawn_chance = 0.005  # Шанс появления таблички за кадр
        self.skeleton_speed = 2  # Скорость движения табличек

        # Загружаем изображение скелета и вырезаем только голову
        try:
            # Пробуем несколько возможных путей
            possible_paths = [
                'assets/images/skelet_1.png',
                'assets/images/skeleton.png',
                'images/skelet_1.png',
                'images/skeleton.png'
            ]

            skeleton_loaded = False
            full_image = None
            for path in possible_paths:
                try:
                    if os.path.exists(path):
                        full_image = pygame.image.load(path).convert_alpha()
                        print(f"Изображение скелета загружено из {path}")
                        skeleton_loaded = True
                        break
                except:
                    continue

            if not skeleton_loaded:
                raise Exception("Не удалось загрузить изображение скелета")

            # Вырезаем только голову скелета (примерные координаты)
            head_width = 40
            head_height = 40
            # Предполагаем, что голова находится в верхней части изображения
            head_rect = pygame.Rect((full_image.get_width() - head_width) // 2,
                                    10,  # Отступ сверху
                                    head_width, head_height)

            self.skeleton_head_image = pygame.Surface((head_width, head_height), pygame.SRCALPHA)
            self.skeleton_head_image.blit(full_image, (0, 0), head_rect)

            # Масштабируем если нужно
            self.skeleton_head_image = pygame.transform.scale(self.skeleton_head_image, (50, 50))
            print(f"Голова скелета подготовлена: {self.skeleton_head_image.get_size()}")

        except Exception as e:
            print(f"Ошибка загрузки изображения скелета: {e}. Создаем заглушку")
            # Создаем заглушку для головы скелета
            self.skeleton_head_image = pygame.Surface((50, 50), pygame.SRCALPHA)
            self.skeleton_head_image.fill((255, 0, 0, 128))  # Полупрозрачный красный
            pygame.draw.circle(self.skeleton_head_image, (255, 255, 255), (25, 25), 20)  # Голова
            pygame.draw.circle(self.skeleton_head_image, (0, 0, 0), (20, 20), 3)  # Глаз
            pygame.draw.circle(self.skeleton_head_image, (0, 0, 0), (30, 20), 3)  # Глаз
            pygame.draw.rect(self.skeleton_head_image, (0, 0, 0), (20, 30, 10, 5))  # Рот

        # Загрузите изображение джипа
        try:
            self.jeep_image = pygame.image.load('assets/images/jeep_2.PNG').convert_alpha()
            self.jeep_image = pygame.transform.scale(self.jeep_image, (self.player.width, self.player.height))
            print("Изображение джипа загружено успешно")
        except:
            print("Ошибка загрузки изображения джипа. Создаем заглушку")
            self.jeep_image = pygame.Surface((self.player.width, self.player.height))
            self.jeep_image.fill((0, 100, 0))  # Темно-зеленый цвет
            pygame.draw.rect(self.jeep_image, (139, 69, 19), (5, 5, self.player.width - 10, self.player.height - 10))

    def activate_jeep(self):
        """Активировать бонус джипа"""
        self.jeep_active = True
        self.jeep_time = pygame.time.get_ticks()
        # Сохраняем оригинальное изображение
        if self.original_player_image is None:
            self.original_player_image = self.player.image.copy()
        # Заменяем изображение на джип
        self.player.image = self.jeep_image

    def deactivate_jeep(self):
        """Деактивировать бонус джипа"""
        self.jeep_active = False
        # Восстанавливаем оригинальное изображение
        if self.original_player_image is not None:
            self.player.image = self.original_player_image

    def load_sounds(self):
        """Load all game sounds"""

        def load_sound(path, volume=0.7):
            """
            Загружает звуковой файл и настраивает громкость

            :param path: Путь к звуковому файлу (форматы: .wav, .ogg)
            :param volume: Уровень громкости от 0.0 до 1.0
            :return: Объект Sound или None при ошибке
            """
            try:
                # Инициализация аудиосистемы pygame (если ещё не сделано)
                if not pygame.mixer.get_init():
                    pygame.mixer.init()

                sound = pygame.mixer.Sound(path)
                sound.set_volume(volume)
                return sound

            except Exception as e:
                print(f"Ошибка загрузки звука {path}: {e}")
                return None

        self.player_move_sound = load_sound('assets/sounds/player_move.wav', 0.3)
        self.enemy_move_sound = load_sound('assets/sounds/enemy_move.wav', 0.1)
        self.slide_sound = load_sound('assets/sounds/slide.wav', 0.4)

    def load_music(self):
        """Load music playlists"""
        self.playlist = [
            'assets/sounds/background_music1.mp3',
            'assets/sounds/background_music2.mp3',
            'assets/sounds/background_music3.mp3'
        ]
        self.menu_music = 'assets/sounds/menu_music.mp3'
        pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
        self.play_menu_music()

    def play_track_for_level(self, level):
        """Play appropriate music track for level"""
        track_index = (level - 1) % len(self.playlist)
        pygame.mixer.music.load(self.playlist[track_index])
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

    def play_menu_music(self):
        """Play menu music"""
        pygame.mixer.music.load(self.menu_music)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

    def draw_level_menu(self):
        """Draw level selection menu"""
        # ТОЛЬКО для меню - обычный фон БЕЗ дороги и пустыни
        self.screen.blit(self.backgrounds[0], (0, 0))  # Обычный фон меню

        title_text = self.font.render("Выберите уровень:", True, WHITE)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

        self.level_rects = []
        for level_index in range(MAX_LEVELS):
            row = level_index // 5
            col = level_index % 5
            level_text = self.font.render(f"Уровень {level_index + 1}", True, WHITE)
            level_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - 250 + col * 120,
                150 + row * 100,
                100, 50
            )
            self.level_rects.append(level_rect)
            color = GREEN if level_index + 1 == self.current_level else (
                WHITE if level_index + 1 <= self.max_unlocked_level else (100, 100, 100))
            pygame.draw.rect(self.screen, color, level_rect)
            self.screen.blit(level_text, (level_rect.x + 10, level_rect.y + 10))

    def start_level(self, level):
        """Initialize level with given number"""
        self.game_state = "playing"
        self.player.lives = PLAYER_LIVES
        self.enemies_defeated = 3
        self.current_level = level
        self.enemies_to_next_level = ENEMIES_FOR_FIRST_LEVEL + (level - 1) * LEVEL_INCREMENT
        self.enemy.speed = min(0.7 + level, MAX_ENEMY_SPEED)
        pygame.mixer.music.stop()
        self.play_track_for_level(level)
        self.reset_positions()

    def reset_positions(self):
        """Reset positions of all game objects"""
        self.player.reset()
        self.enemy.reset()
        self.regular_bonus.reset()
        self.shield_bonus.reset()
        self.gun_bonus.reset()
        # Hide special bonuses initially
        self.shield_bonus.y = -BONUS_HEIGHT
        self.gun_bonus.y = -BONUS_HEIGHT

        self.jeep_bonus.reset()
        self.jeep_bonus.y = -BONUS_HEIGHT
        self.deactivate_jeep()

        self.skeleton_signs = []  # Очищаем таблички при ресете

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN and self.game_state == "level_select":
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(self.level_rects):
                    if rect.collidepoint(mouse_pos):
                        self.start_level(i + 1)
        return True

    def check_collisions(self):
        """Check all game collisions"""
        # Player with enemy
        if self.enemy.collides_with(self.player):
            if not self.player.shield_active:
                self.player.lives -= 1
                self.reset_positions()
                if self.player.lives <= 0:
                    self.game_state = "level_select"
                    pygame.mixer.music.stop()
                    self.play_menu_music()

        # Player with regular bonus
        if self.regular_bonus.collides_with(self.player):
            self.player.score += 1
            self.regular_bonus.reset()

        # Player with shield bonus
        if self.shield_bonus.collides_with(self.player):
            self.player.activate_shield()
            self.shield_bonus.reset()
            self.shield_bonus.y = -BONUS_HEIGHT

        # Player with gun bonus
        if self.gun_bonus.collides_with(self.player):
            self.player.activate_gun()
            self.gun_bonus.reset()
            self.gun_bonus.y = -BONUS_HEIGHT

        # Player with jeep bonus
        if self.jeep_bonus.collides_with(self.player):
            self.activate_jeep()
            self.jeep_bonus.reset()
            self.jeep_bonus.y = -BONUS_HEIGHT

    def check_skeleton_collisions(self):
        """Проверить столкновения с табличками со скелетом"""
        for sign in self.skeleton_signs[:]:
            # Проверяем столкновение с игроком
            if (self.player.x < sign['x'] + sign['width'] and
                    self.player.x + self.player.width > sign['x'] and
                    self.player.y < sign['y'] + sign['height'] and
                    self.player.y + self.player.height > sign['y']):

                # Столкновение произошло!
                if not self.player.shield_active:
                    self.player.lives -= 3.5
                    print(f"Столкнулся с табличкой! Потеряно 3.5 здоровья. Осталось: {self.player.lives}")

                    # Удаляем табличку
                    self.skeleton_signs.remove(sign)

                    # Проверка на смерть
                    if self.player.lives <= 0:
                        self.game_state = "level_select"
                        pygame.mixer.music.stop()
                        self.play_menu_music()
                else:
                    # Если есть щит, просто уничтожаем табличку
                    self.skeleton_signs.remove(sign)

    def spawn_skeleton_sign(self):
        """Создать новую табличку со скелетом"""
        road_left = (SCREEN_WIDTH - ROAD_WIDTH) // 2
        road_right = road_left + ROAD_WIDTH

        # Случайная позиция на дороге
        x = random.randint(road_left + 10, road_right - 70)
        y = -90  # Начинаем выше экрана

        # Сохраняем информацию о табличке с правильными размерами изображения головы
        self.skeleton_signs.append({
            'x': x,
            'y': y,
            'width': self.skeleton_head_image.get_width(),
            'height': self.skeleton_head_image.get_height(),
            'image': self.skeleton_head_image  # Сохраняем ссылку на изображение головы
        })

    def update(self):
        """Update game state"""
        if self.game_state != "playing":
            return

        # Обновляем анимацию дороги (скорость зависит от уровня)
        road_speed_factor = min(1.0 + (self.current_level * 0.2), 3.0)
        self.road_offset += self.road_speed * road_speed_factor
        if self.road_offset >= 60:
            self.road_offset = 0

        # Update power-ups
        self.player.update_powerups()

        # Move enemy
        self.enemy.move()

        # Move bonuses with random chance
        if random.random() < BONUS_SPAWN_CHANCE:
            self.regular_bonus.move()
        if random.random() < SHIELD_SPAWN_CHANCE:
            self.shield_bonus.move()
        if random.random() < GUN_SPAWN_CHANCE:
            self.gun_bonus.move()
        if random.random() < JEEP_SPAWN_CHANCE:
            self.jeep_bonus.move()

        # Добавьте проверку времени действия джипа
        current_time = pygame.time.get_ticks()
        if self.jeep_active and current_time - self.jeep_time > JEEP_DURATION:
            self.deactivate_jeep()

        # Спавн и движение табличек со скелетом
        if random.random() < self.skeleton_spawn_chance:
            self.spawn_skeleton_sign()

        # Двигаем все таблички СИНХРОННО с дорогой
        for sign in self.skeleton_signs[:]:
            # Таблички двигаются с той же скоростью, что и дорога
            sign['y'] += self.road_speed

            # Удаляем таблички, которые уехали за экран
            if sign['y'] > SCREEN_HEIGHT:
                self.skeleton_signs.remove(sign)

        # Проверка столкновений с табличками
        self.check_skeleton_collisions()

        # Проверка выезда за пределы дороги
        road_left = (SCREEN_WIDTH - ROAD_WIDTH) // 2
        road_right = road_left + ROAD_WIDTH

        # Если игрок выехал за левую или правую границу дороги И у него не активен джип
        if (self.player.x < road_left or self.player.x + self.player.width > road_right) and not self.jeep_active:
            # Замедление
            if not hasattr(self, 'off_road_slowdown'):
                self.off_road_slowdown = True
                self.player.speed = max(0.1, self.player.speed - 1)  # Замедляем на 1, но не меньше 0.1

            # Потеря здоровья (раз в секунду, чтобы не терять сразу все жизни)
            current_time = pygame.time.get_ticks()
            if not hasattr(self, 'last_damage_time'):
                self.last_damage_time = current_time

            if current_time - self.last_damage_time > 1000:  # Раз в секунду
                self.player.lives -= 2.5
                self.last_damage_time = current_time
                print(f"Выехал за дорогу! Потеряно 2.5 здоровья. Осталось: {self.player.lives}")

                # Проверка на смерть
                if self.player.lives <= 0:
                    self.game_state = "level_select"
                    pygame.mixer.music.stop()
                    self.play_menu_music()
        else:
            # Если игрок вернулся на дорогу, восстанавливаем нормальную скорость
            if hasattr(self, 'off_road_slowdown'):
                self.player.speed = 2.5  # Нормальная скорость
                del self.off_road_slowdown

        # Check if gun active and enemy is on same line
        if self.player.gun_active and abs(self.player.y - self.enemy.y) < 10:
            self.enemies_defeated += 1
            self.enemy.reset()

        # Check if enemy is off screen
        if self.enemy.is_off_screen():
            self.enemy.reset()
            if not self.player.gun_active:
                self.enemies_defeated += 1
            if self.enemies_defeated >= self.enemies_to_next_level:
                self.game_state = "level_select"
                pygame.mixer.music.stop()
                self.play_menu_music()

        # Check if bonuses are off screen
        if self.regular_bonus.is_off_screen():
            self.regular_bonus.reset()
        if self.shield_bonus.is_off_screen():
            self.shield_bonus.reset()
            self.shield_bonus.y = -BONUS_HEIGHT
        if self.gun_bonus.is_off_screen():
            self.gun_bonus.reset()
            self.gun_bonus.y = -BONUS_HEIGHT
        if self.jeep_bonus.is_off_screen():
            self.jeep_bonus.reset()
            self.jeep_bonus.y = -BONUS_HEIGHT

        # Check collisions
        self.check_collisions()

    def draw(self):
        """Draw game objects"""
        if self.game_state == "level_select":
            self.draw_level_menu()

        elif self.game_state == "playing":
            # ТОЛЬКО для игрового уровня - дорога с пустыней
            # Рисуем пустыню по всей площади
            self.screen.blit(self.desert_texture, (0, 0))

            # Рисуем дорогу посередине с анимацией
            road_x = (SCREEN_WIDTH - ROAD_WIDTH) // 2

            # Создаем временную поверхность для анимированной дороги
            animated_road = pygame.Surface((ROAD_WIDTH, SCREEN_HEIGHT))
            animated_road.fill((50, 50, 50))  # Основной цвет дороги

            # Красные линии по краям
            pygame.draw.rect(animated_road, RED, (0, 0, 5, SCREEN_HEIGHT))
            pygame.draw.rect(animated_road, RED, (ROAD_WIDTH - 5, 0, 5, SCREEN_HEIGHT))

            # Движущаяся разметка (синхронизирована с табличками)
            for i in range(-60, SCREEN_HEIGHT + 60, 60):
                mark_y = i + self.road_offset
                if 0 <= mark_y < SCREEN_HEIGHT:  # Рисуем только видимые segmentы
                    pygame.draw.rect(animated_road, (255, 255, 0),
                                     (ROAD_WIDTH // 2 - 5, mark_y, 10, 30))

            self.screen.blit(animated_road, (road_x, 0))

            # Рисуем таблички со скелетом - только голову
            for sign in self.skeleton_signs:
                # Рисуем изображение головы скелета
                self.screen.blit(sign['image'], (sign['x'], sign['y']))

            # Рисуем бонусы
            self.regular_bonus.draw(self.screen)
            self.shield_bonus.draw(self.screen)
            self.gun_bonus.draw(self.screen)
            self.jeep_bonus.draw(self.screen)

            # Рисуем игрока и врага
            self.player.draw(self.screen)
            self.enemy.draw(self.screen)

            # Draw stats
            lives_text = self.font.render(f'Жизни: {self.player.lives}', True, WHITE)
            defeated_text = self.font.render(f'Побеждено врагов: {self.enemies_defeated}', True, WHITE)
            self.screen.blit(lives_text, (10, 10))
            self.screen.blit(defeated_text, (10, 50))

        pygame.display.flip()

    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_events()

            keys = pygame.key.get_pressed()
            if self.game_state == "playing":
                if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                    self.player_move_sound.play()
                    if keys[pygame.K_LEFT]:
                        self.player.move("left")
                    if keys[pygame.K_RIGHT]:
                        self.player.move("right")
                else:
                    self.player_move_sound.stop()

                if self.enemy.y > 0:
                    self.enemy_move_sound.play()
                else:
                    self.enemy_move_sound.stop()

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()