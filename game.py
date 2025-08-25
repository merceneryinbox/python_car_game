import pygame
import sys
import random
from assets_loader import load_backgrounds
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GREEN, RED, GOLD, CYAN,
    BONUS_HEIGHT, ENEMIES_FOR_FIRST_LEVEL, LEVEL_INCREMENT,
    MAX_ENEMY_SPEED, PLAYER_LIVES, MAX_LEVELS, FPS,
    BONUS_SPAWN_CHANCE, SHIELD_SPAWN_CHANCE, GUN_SPAWN_CHANCE,
    ROAD_WIDTH
)
from player import Player
from enemy import Enemy
from bonus import Bonus


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

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

    def load_sounds(self):
        """Load all game sounds"""

        def load_sound(path, volume=0.5):
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
        self.enemy_move_sound = load_sound('assets/sounds/enemy_move.wav', 0.3)
        self.slide_sound = load_sound('assets/sounds/slide.wav', 0.5)

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

    # === ИСПРАВЛЕНО: Добавлен отсутствующий метод ===
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

    def update(self):
        """Update game state"""
        if self.game_state != "playing":
            return

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

            # Проверка выезда за пределы дороги
            road_left = (SCREEN_WIDTH - ROAD_WIDTH) // 2
            road_right = road_left + ROAD_WIDTH

            # Если игрок выехал за левую или правую границу дороги
            if self.player.x < road_left or self.player.x + self.player.width > road_right:
                # Замедление
                if not hasattr(self, 'off_road_slowdown'):
                    self.off_road_slowdown = True
                    self.player.speed = max(0.1, self.player.speed - 1)  # Замедляем на 1, но не меньше 0.1

                # Потеря здоровья (раз в секунду, чтобы не терять сразу все жизни)
                current_time = pygame.time.get_ticks()
                if not hasattr(self, 'last_damage_time'):
                    self.last_damage_time = current_time

                if current_time - self.last_damage_time > 1000:  # Раз в секунду
                    self.player.lives -= 3
                    self.last_damage_time = current_time
                    print(f"Выехал за дорогу! Потеряно 3 здоровья. Осталось: {self.player.lives}")

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
            # === КОНЕЦ БЛОКА ===

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

        # Check collisions
        self.check_collisions()

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

    def draw(self):
        """Draw game objects"""
        if self.game_state == "level_select":
            self.draw_level_menu()

        elif self.game_state == "playing":
            # ТОЛЬКО для игрового уровня - дорога с пустыней
            print("Рисуем дорогу и пустыню...")  # Отладочное сообщение

            # Рисуем пустыню по всей площади
            self.screen.blit(self.desert_texture, (0, 0))

            # Рисуем дорогу посередине
            road_x = (SCREEN_WIDTH - ROAD_WIDTH) // 2
            self.screen.blit(self.road_texture, (road_x, 0))

            # Отладочная информация
            debug_text = self.font.render(f"Road X: {road_x}, Road Width: {ROAD_WIDTH}", True, RED)
            self.screen.blit(debug_text, (10, 90))

            self.player.draw(self.screen)
            self.enemy.draw(self.screen)
            self.regular_bonus.draw(self.screen)
            self.shield_bonus.draw(self.screen)
            self.gun_bonus.draw(self.screen)

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