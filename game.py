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
    ROAD_WIDTH, BULLET_SPEED, MACHINE_GUN_DURATION, MACHINE_GUN_SPAWN_CHANCE
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
        self.road_offset = 0  # Смещение для анимации дороги
        self.road_speed = 3  # Скорость движения дороги

        # Добавьте после других переменных
        self.turrets = []  # Список для хранения турелей
        self.turret_duration = 5000  # Длительность турелей в миллисекундах
        self.turret_start_time = 0  # Время активации турелей
        self.turret_image = None  # Изображение турели

        # Загрузите изображение турели
        try:
            self.turret_image = pygame.image.load('assets/images/turret.png').convert_alpha()
            self.turret_image = pygame.transform.scale(self.turret_image, (40, 40))
            print("Изображение турели загружено успешно")
        except:
            print("Ошибка загрузки изображения турели. Создаем заглушку")
            self.turret_image = pygame.Surface((40, 40))
            self.turret_image.fill((200, 0, 0))  # Красный цвет
            pygame.draw.circle(self.turret_image, (100, 100, 100), (20, 20), 15)  # Основание
            pygame.draw.rect(self.turret_image, (150, 150, 150), (15, 5, 10, 15))  # Ствол

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
        self.machine_gun_bonus = Bonus("machine_gun")

        # Загружаем изображение джипа-врага
        try:
            self.jeep_enemy_image = pygame.image.load('assets/images/jeep_enemy.png').convert_alpha()
            self.jeep_enemy_image = pygame.transform.scale(self.jeep_enemy_image,
                                                           (self.enemy.width, self.enemy.height))
            print("Изображение джипа-врага загружено успешно")
        except:
            print("Ошибка загрузки изображения джипа-врага. Создаем заглушку")
            self.jeep_enemy_image = pygame.Surface((self.enemy.width, self.enemy.height))
            self.jeep_enemy_image.fill((255, 0, 0))  # Красный цвет для вражеского джипа
            pygame.draw.rect(self.jeep_enemy_image, (100, 0, 0),
                             (5, 5, self.enemy.width - 10, self.enemy.height - 10))

        # Сохраняем оригинальное изображение врага
        self.original_enemy_image = self.enemy.image.copy()

        # Добавьте после загрузки других изображений
        self.gun_rays = []  # Список для хранения информации о лучах
        self.gun_ray_duration = 3000  # Длительность показа лучей в миллисекундах
        self.gun_ray_start_time = 0  # Время активации лучей

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

        # Загрузите изображение для бонуса machine_gun
        try:
            self.machine_gun_bonus_image = pygame.image.load('assets/images/machine_gun_bonus.png').convert_alpha()
            self.machine_gun_bonus_image = pygame.transform.scale(self.machine_gun_bonus_image, (50, 50))
            print("Изображение бонуса machine_gun загружено успешно")
            # Устанавливаем изображение для бонуса
            self.machine_gun_bonus.image = self.machine_gun_bonus_image
        except:
            print("Ошибка загрузки изображения бонуса machine_gun. Создаем заглушку")
            self.machine_gun_bonus_image = pygame.Surface((50, 50))
            self.machine_gun_bonus_image.fill((0, 0, 255))  # Синий цвет для machine_gun
            pygame.draw.rect(self.machine_gun_bonus_image, (0, 0, 200), (5, 5, 40, 40))
            # Рисуем простой пулемет
            pygame.draw.rect(self.machine_gun_bonus_image, (100, 100, 100), (15, 10, 20, 30))  # Основание
            pygame.draw.rect(self.machine_gun_bonus_image, (150, 150, 150), (10, 15, 30, 5))  # Ствол
            self.machine_gun_bonus.image = self.machine_gun_bonus_image

        # После создания других бонусов
        self.machine_gun_bonus = Bonus("machine_gun")

        # После инициализации других бонусов
        self.machine_gun_bonus.y = -BONUS_HEIGHT

        # Добавьте для machine_gun
        self.bullets = []  # Список для хранения пуль
        self.machine_gun_active = False
        self.machine_gun_time = 0
        self.last_bullet_time = 0  # Время последнего выстрела

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

        # Загрузите изображение джипа для игрока
        try:
            self.jeep_image = pygame.image.load('assets/images/jeep_2.png').convert_alpha()
            self.jeep_image = pygame.transform.scale(self.jeep_image, (self.player.width, self.player.height))
            print("Изображение джипа для игрока загружено успешно")
        except:
            print("Ошибка загрузки изображения джипа для игрока. Создаем заглушку")
            self.jeep_image = pygame.Surface((self.player.width, self.player.height))
            self.jeep_image.fill((0, 100, 0))  # Темно-зеленый цвет
            pygame.draw.rect(self.jeep_image, (139, 69, 19), (5, 5, self.player.width - 10, self.player.height - 10))

        # Загрузите изображение для бонуса джипа
        try:
            self.jeep_bonus_image = pygame.image.load('assets/images/jeep_3.png').convert_alpha()
            self.jeep_bonus_image = pygame.transform.scale(self.jeep_bonus_image, (50, 50))
            print("Изображение бонуса джипа загружено успешно")
            # Устанавливаем изображение для бонуса
            self.jeep_bonus.image = self.jeep_bonus_image
        except:
            print("Ошибка загрузки изображения бонуса джипа. Создаем заглушку")
            self.jeep_bonus_image = pygame.Surface((50, 50))
            self.jeep_bonus_image.fill((0, 100, 0))  # Темно-зеленый цвет
            pygame.draw.rect(self.jeep_bonus_image, (139, 69, 19), (5, 5, 40, 40))
            self.jeep_bonus.image = self.jeep_bonus_image

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

    def activate_machine_gun(self):
        """Активировать бонус пулемета"""
        self.machine_gun_active = True
        self.machine_gun_time = pygame.time.get_ticks()
        self.last_bullet_time = pygame.time.get_ticks()

    def deactivate_machine_gun(self):
        """Деактивировать бонус пулемета"""
        self.machine_gun_active = False
        self.bullets = []  # Очищаем все пули

    def create_bullet(self):
        """Создать пулю из центра игрока"""
        bullet = {
            'x': self.player.x + self.player.width // 2 - 5,  # Центр игрока
            'y': self.player.y,
            'width': 10,
            'height': 20,
            'speed': BULLET_SPEED
        }
        self.bullets.append(bullet)

    def create_gun_rays(self):
        """Создать 4 красных луча на дороге, начинающиеся от турелей"""
        self.gun_rays = []  # Очищаем предыдущие лучи
        road_left = (SCREEN_WIDTH - ROAD_WIDTH) // 2
        turret_y = SCREEN_HEIGHT - 100  # Высота турелей

        # Создаем 4 луча, начинающиеся от турелей и идущие ВВЕРХ
        for i in range(4):
            x_pos = road_left + (i + 1) * (ROAD_WIDTH // 5)
            self.gun_rays.append({
                'x': x_pos,  # Сдвигаем на 30px правее для турелей
                'y': 0,  # Начинаются от верха экрана
                'width': 12,  # Толщина луча
                'height': turret_y + 40,  # Высота от верха до турелей + немного ниже
                'color': RED
            })

        self.gun_ray_start_time = pygame.time.get_ticks()
        print("Лучи оружия созданы! Количество лучей:", len(self.gun_rays))

    def create_turrets(self):
        """Создать турели перед игроком, правее лучей"""
        self.turrets = []  # Очищаем предыдущие турели
        road_left = (SCREEN_WIDTH - ROAD_WIDTH) // 2
        turret_y = SCREEN_HEIGHT - 100  # Высота турелей

        # Создаем 4 турели правее лучей
        for i in range(4):  # 4 турели для 4 лучей
            x_pos = road_left + (i + 1) * (ROAD_WIDTH // 5) - 15
            self.turrets.append({
                'x': x_pos,
                'y': turret_y,
                'width': 40,
                'height': 40,
                'image': self.turret_image
            })

        self.turret_start_time = pygame.time.get_ticks()
        print("Турели созданы! Количество:", len(self.turrets))

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
        # Восстанавливаем обычное изображение врага
        self.enemy.image = self.original_enemy_image.copy()
        self.regular_bonus.reset()
        self.shield_bonus.reset()
        self.gun_bonus.reset()
        self.machine_gun_bonus.reset()
        # Сбрасываем размеры к оригинальным
        if hasattr(self.enemy, 'original_width'):
            self.enemy.width = self.enemy.original_width
            self.enemy.height = self.enemy.original_height
        else:
            # Если атрибуты еще не созданы, устанавливаем стандартные размеры
            self.enemy.width = 50  # Стандартная ширина врага
            self.enemy.height = 80  # Стандартная высота врага

        # Hide special bonuses initially
        self.shield_bonus.y = -BONUS_HEIGHT
        self.gun_bonus.y = -BONUS_HEIGHT
        self.machine_gun_bonus.y = -BONUS_HEIGHT

        self.jeep_bonus.reset()
        self.jeep_bonus.y = -BONUS_HEIGHT
        self.deactivate_jeep()

        self.skeleton_signs = []  # Очищаем таблички при ресете
        self.turrets = []  # очищаем турели
        self.bullets = []  # Очищаем пули
        self.gun_rays = []  # Очищаем лучи

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
            self.create_gun_rays()  # ← Добавьте эту строку
            self.create_turrets()  # Турели ← ДОБАВЬТЕ ЭТУ СТРОКУ
            print("Бонус gun подобран, создаем лучи")  # Отладочный вывод

        # Player with jeep bonus
        if self.jeep_bonus.collides_with(self.player):
            self.activate_jeep()
            self.jeep_bonus.reset()
            self.jeep_bonus.y = -BONUS_HEIGHT

        # Player with machine_gun bonus
        if self.machine_gun_bonus.collides_with(self.player):
            self.activate_machine_gun()
            self.machine_gun_bonus.reset()
            self.machine_gun_bonus.y = -BONUS_HEIGHT
            print("Бонус machine_gun подобран!")

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

        # Проверяем время действия лучей оружия
        if self.gun_rays:
            current_time = pygame.time.get_ticks()
            if current_time - self.gun_ray_start_time > self.gun_ray_duration:
                self.gun_rays = []  # Убираем лучи после истечения времени
                print("Лучи оружия скрыты")

        # Проверяем время действия турелей
        if self.turrets:
            current_time = pygame.time.get_ticks()
            if current_time - self.turret_start_time > self.turret_duration:
                self.turrets = []  # Убираем турели после истечения времени
                print("Турели деактивированы")

        # Move enemy
        self.enemy.move()

        # Проверяем время действия machine_gun
        current_time = pygame.time.get_ticks()
        if self.machine_gun_active and current_time - self.machine_gun_time > MACHINE_GUN_DURATION:
            self.deactivate_machine_gun()
            print("Пулемет деактивирован")

        # Стрельба из пулемета (каждую секунду)
        if self.machine_gun_active and current_time - self.last_bullet_time > 1000:  # 1 секунда
            self.create_bullet()
            self.last_bullet_time = current_time

        # Движение пуль и проверка столкновений
        for bullet in self.bullets[:]:
            bullet['y'] -= bullet['speed']  # Двигаем пулю вверх

            # Проверяем столкновение пули с врагом
            if (bullet['x'] < self.enemy.x + self.enemy.width and
                    bullet['x'] + bullet['width'] > self.enemy.x and
                    bullet['y'] < self.enemy.y + self.enemy.height and
                    bullet['y'] + bullet['height'] > self.enemy.y):
                self.enemies_defeated += 1
                self.enemy.reset()
                self.bullets.remove(bullet)
                print("Враг уничтожен пулей!")
                continue

            # Удаляем пули, которые улетели за экран
            if bullet['y'] + bullet['height'] < 0:
                self.bullets.remove(bullet)

        # Проверяем, находится ли враг на дороге или вне ее
        road_left = (SCREEN_WIDTH - ROAD_WIDTH) // 2
        road_right = road_left + ROAD_WIDTH

        # Если враг вне дороги - меняем на джип
        if (self.enemy.x < road_left or self.enemy.x + self.enemy.width > road_right):
            if self.enemy.image != self.jeep_enemy_image:
                self.enemy.image = self.jeep_enemy_image
                # Сохраняем оригинальные размеры перед изменением
                if not hasattr(self.enemy, 'original_width'):
                    self.enemy.original_width = self.enemy.width
                    self.enemy.original_height = self.enemy.height
                # Устанавливаем размеры джипа (такие же как у изображения)
                self.enemy.width = self.jeep_enemy_image.get_width()
                self.enemy.height = self.jeep_enemy_image.get_height()
        else:
            # Если враг на дороге - возвращаем обычное изображение
            if self.enemy.image != self.original_enemy_image:
                self.enemy.image = self.original_enemy_image

        # Move bonuses with random chance
        if random.random() < BONUS_SPAWN_CHANCE:
            self.regular_bonus.move()
        if random.random() < SHIELD_SPAWN_CHANCE:
            self.shield_bonus.move()
        if random.random() < GUN_SPAWN_CHANCE:
            self.gun_bonus.move()
        if random.random() < JEEP_SPAWN_CHANCE:
            self.jeep_bonus.move()
        if random.random() < MACHINE_GUN_SPAWN_CHANCE:
            self.machine_gun_bonus.move()

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

        # Если игрок выехал за левую или правую границу дороги И у него не активен джип И не активен щит
        if ((self.player.x < road_left or self.player.x + self.player.width > road_right) and
            not self.jeep_active and not self.player.shield_active):
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

        # Check if gun active and enemy is visible on screen
        if self.player.gun_active:
            # Проверяем, находится ли враг в видимой области экрана И на дороге
            road_left = (SCREEN_WIDTH - ROAD_WIDTH) // 2
            road_right = road_left + ROAD_WIDTH

            if (self.enemy.y > 0 and self.enemy.y < SCREEN_HEIGHT and
                    self.enemy.x + self.enemy.width > road_left and self.enemy.x < road_right):
                self.enemies_defeated += 1
                self.enemy.reset()
                print("Уничтожен видимый враг на дороге с помощью оружия!")

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
            self.shield_bonus.y = -BONUS_HEIGHT
        if self.gun_bonus.is_off_screen():
            self.gun_bonus.y = -BONUS_HEIGHT
        if self.jeep_bonus.is_off_screen():
            self.jeep_bonus.y = -BONUS_HEIGHT
        if self.machine_gun_bonus.is_off_screen():
            self.machine_gun_bonus.y = -BONUS_HEIGHT

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

            # Рисуем дорогу посередине с анимации
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

            # Рисуем лучи оружия если они активны
            if self.gun_rays:
                for ray in self.gun_rays:
                    pygame.draw.rect(self.screen, ray['color'],
                                     (ray['x'], ray['y'], ray['width'], ray['height']))

            # Рисуем турели если они активны (ОДИН раз!)
            if self.turrets:
                for turret in self.turrets:
                    self.screen.blit(turret['image'], (turret['x'], turret['y']))

            # Рисуем таблички со скелетом - только голову
            for sign in self.skeleton_signs:
                # Рисуем изображение головы скелета
                self.screen.blit(sign['image'], (sign['x'], sign['y']))

            # Рисуем бонусы
            self.regular_bonus.draw(self.screen)
            self.shield_bonus.draw(self.screen)
            self.gun_bonus.draw(self.screen)
            self.jeep_bonus.draw(self.screen)
            self.machine_gun_bonus.draw(self.screen)

            # Рисуем пули
            for bullet in self.bullets:
                pygame.draw.rect(self.screen, (255, 0, 0),  # Красные пули
                                 (bullet['x'], bullet['y'], bullet['width'], bullet['height']))

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