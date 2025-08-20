import pygame
import sys
import random
import os
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GREEN, RED, GOLD, CYAN,
    BONUS_HEIGHT, ENEMIES_FOR_FIRST_LEVEL, LEVEL_INCREMENT,
    MAX_ENEMY_SPEED, PLAYER_LIVES, MAX_LEVELS, FPS,
    BONUS_SPAWN_CHANCE, SHIELD_SPAWN_CHANCE, GUN_SPAWN_CHANCE
)
from player import Player
from enemy import Enemy
from bonus import Bonus


def create_missing_assets():
    """Создает базовые asset файлы если они отсутствуют"""
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Создаем папки если их нет
    assets_dir = os.path.join(base_dir, 'assets')
    sounds_dir = os.path.join(assets_dir, 'sounds')
    images_dir = os.path.join(assets_dir, 'images')
    backgrounds_dir = os.path.join(assets_dir, 'backgrounds')

    os.makedirs(sounds_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(backgrounds_dir, exist_ok=True)

    # Создаем простые звуки если их нет
    sound_files = ['player_move.wav', 'enemy_move.wav', 'slide.wav']
    for sound_file in sound_files:
        sound_path = os.path.join(sounds_dir, sound_file)
        if not os.path.exists(sound_path):
            with open(sound_path, 'wb') as f:
                f.write(
                    b'RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00')
            print(f"Создан пустой звуковой файл: {sound_file}")

    # Создаем тестовые фоны если их нет
    for i in range(1, MAX_LEVELS + 1):
        bg_path = os.path.join(backgrounds_dir, f'level_{i}.png')
        if not os.path.exists(bg_path):
            # Создаем градиентный фон для уровня
            surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

            # Разные цветовые схемы для разных уровней
            if i == 1:
                # Зеленый градиент - природа
                for y in range(SCREEN_HEIGHT):
                    color = (0, min(255, 100 + y // 2), 0)
                    pygame.draw.line(surf, color, (0, y), (SCREEN_WIDTH, y))
                # Добавляем дорогу
                pygame.draw.rect(surf, (50, 50, 50), (SCREEN_WIDTH // 4, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
                pygame.draw.rect(surf, (255, 255, 0), (SCREEN_WIDTH // 2 - 5, 0, 10, SCREEN_HEIGHT))

            elif i == 2:
                # Синий градиент - вода/небо
                for y in range(SCREEN_HEIGHT):
                    color = (0, 0, min(255, 100 + y // 3))
                    pygame.draw.line(surf, color, (0, y), (SCREEN_WIDTH, y))
                # Песчаная дорога
                pygame.draw.rect(surf, (194, 178, 128), (SCREEN_WIDTH // 4, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))

            elif i == 3:
                # Красный/оранжевый градиент - пустыня/закат
                for y in range(SCREEN_HEIGHT):
                    color = (min(255, 150 + y // 4), max(0, 100 - y // 6), 0)
                    pygame.draw.line(surf, color, (0, y), (SCREEN_WIDTH, y))
                # Асфальтовая дорога
                pygame.draw.rect(surf, (80, 80, 80), (SCREEN_WIDTH // 4, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))

            else:
                # Случайный градиент для остальных уровней
                r = random.randint(50, 200)
                g = random.randint(50, 200)
                b = random.randint(50, 200)
                for y in range(SCREEN_HEIGHT):
                    color = (
                        min(255, r + y // 4),
                        min(255, g + y // 5),
                        min(255, b + y // 6)
                    )
                    pygame.draw.line(surf, color, (0, y), (SCREEN_WIDTH, y))
                # Стандартная дорога
                pygame.draw.rect(surf, (60, 60, 60), (SCREEN_WIDTH // 4, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))

            # Добавляем разметку на дорогу
            for y in range(0, SCREEN_HEIGHT, 40):
                pygame.draw.rect(surf, (255, 255, 0), (SCREEN_WIDTH // 2 - 2, y, 4, 20))

            pygame.image.save(surf, bg_path)
            print(f"Создан фон для уровня {i}: {bg_path}")


class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.music_volume = 0.7
        self.sound_volume = 0.8
        self.setup_audio()

    def setup_audio(self):
        """Настраивает аудио систему для высокого качества"""
        pygame.mixer.init(
            frequency=44100,
            size=-16,
            channels=2,
            buffer=2048
        )
        pygame.mixer.set_num_channels(16)

    def load_sound(self, name, path, volume=1.0):
        """Загружает звук с высоким качеством"""
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(base_dir, path)

            if os.path.exists(full_path):
                sound = pygame.mixer.Sound(full_path)
                sound.set_volume(volume * self.sound_volume)
                self.sounds[name] = sound
                print(f"Звук загружен: {name}, громкость: {volume}")
                return True
            else:
                print(f"Файл не найден: {full_path}")
                return False
        except Exception as e:
            print(f"Ошибка загрузки звука {name}: {e}")
            return False

    def play_sound(self, name, loops=0):
        if name in self.sounds:
            return self.sounds[name].play(loops=loops)
        return None

    def stop_sound(self, name):
        if name in self.sounds:
            self.sounds[name].stop()

    def set_volume(self, volume):
        self.sound_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)

    def stop_all(self):
        pygame.mixer.stop()


class Game:
    def __init__(self):
        # Создаем недостающие asset файлы
        create_missing_assets()

        # Инициализируем pygame
        pygame.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Турбо гонки')

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 25)

        # Game states
        self.game_state = "level_select"
        self.current_level = 1
        self.max_unlocked_level = 1
        self.enemies_defeated = 0
        self.enemies_to_next_level = ENEMIES_FOR_FIRST_LEVEL

        # Load assets
        self.backgrounds = self.load_backgrounds()
        self.sound_manager = SoundManager()
        self.load_high_quality_sounds()
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

    def load_high_quality_sounds(self):
        """Загружает звуки высокого качества"""
        sounds_to_load = [
            ('player_move', 'assets/sounds/player_move.wav', 0.4),
            ('enemy_move', 'assets/sounds/enemy_move.wav', 0.3),
            ('slide', 'assets/sounds/slide.wav', 0.6),
        ]

        for name, path, volume in sounds_to_load:
            self.sound_manager.load_sound(name, path, volume)

    def load_backgrounds(self):
        """Загружает фоны для уровней из папки assets/backgrounds"""
        backgrounds = []
        base_dir = os.path.dirname(os.path.abspath(__file__))
        backgrounds_dir = os.path.join(base_dir, 'assets', 'backgrounds')

        print("Загрузка фонов...")

        for i in range(1, MAX_LEVELS + 1):
            bg_path = os.path.join(backgrounds_dir, f'level_{i}.png')

            if os.path.exists(bg_path):
                try:
                    # Загружаем изображение фона
                    bg_image = pygame.image.load(bg_path).convert()
                    # Масштабируем под размер экрана если нужно
                    if bg_image.get_width() != SCREEN_WIDTH or bg_image.get_height() != SCREEN_HEIGHT:
                        bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
                    backgrounds.append(bg_image)
                    print(f"Фон уровня {i} загружен: {bg_path}")

                except Exception as e:
                    print(f"Ошибка загрузки фона уровня {i}: {e}")
                    # Создаем заглушку
                    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                    color = ((i * 40) % 255, (i * 60) % 255, (i * 80) % 255)
                    surf.fill(color)
                    # Добавляем номер уровня
                    font = pygame.font.SysFont(None, 100)
                    text = font.render(f"LEVEL {i}", True, WHITE)
                    surf.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2,
                                     SCREEN_HEIGHT // 2 - text.get_height() // 2))
                    backgrounds.append(surf)
            else:
                print(f"Фон уровня {i} не найден: {bg_path}")
                # Создаем заглушку
                surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                color = ((i * 30) % 255, (i * 50) % 255, (i * 70) % 255)
                surf.fill(color)
                backgrounds.append(surf)

        # Если не загрузилось ни одного фона, создаем базовые
        if not backgrounds:
            for i in range(MAX_LEVELS):
                surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                color = (i * 30, i * 20, i * 40)
                surf.fill(color)
                backgrounds.append(surf)

        return backgrounds

    def load_music(self):
        """Load high quality music"""
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Создаем плейлист с музыкой
        self.playlist = []
        for i in range(1, 4):
            music_path = os.path.join(base_dir, 'assets', 'sounds', f'background_music{i}.mp3')
            if os.path.exists(music_path):
                self.playlist.append(music_path)
            else:
                print(f"Музыкальный файл не найден: {music_path}")

        # Если нет музыки, создаем пустой плейлист
        if not self.playlist:
            self.playlist = ['']

        self.menu_music = os.path.join(base_dir, 'assets', 'sounds', 'menu_music.mp3')
        if not os.path.exists(self.menu_music):
            print(f"Меню музыка не найдена: {self.menu_music}")
            self.menu_music = self.playlist[0] if self.playlist else ''

        pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
        self.play_menu_music()

    def play_track_for_level(self, level):
        """Play appropriate music track for level"""
        if not self.playlist:
            return

        track_index = (level - 1) % len(self.playlist)
        try:
            pygame.mixer.music.load(self.playlist[track_index])
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Ошибка загрузки музыки уровня: {e}")

    def play_menu_music(self):
        """Play menu music"""
        try:
            if self.menu_music and os.path.exists(self.menu_music):
                pygame.mixer.music.load(self.menu_music)
                pygame.mixer.music.set_volume(0.6)
                pygame.mixer.music.play(-1)
            elif self.playlist:
                # Используем первую музыку из плейлиста как меню музыку
                pygame.mixer.music.load(self.playlist[0])
                pygame.mixer.music.set_volume(0.6)
                pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"Ошибка загрузки меню музыки: {e}")

    def draw_level_menu(self):
        """Draw level selection menu with level previews"""
        # Используем фон первого уровня для меню
        if self.backgrounds:
            self.screen.blit(self.backgrounds[0], (0, 0))
        else:
            self.screen.fill((0, 0, 0))

        # Затемняем фон для лучшей читаемости
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        title_text = self.font.render("Выберите уровень:", True, WHITE)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 30))

        self.level_rects = []
        for level_index in range(MAX_LEVELS):
            row = level_index // 5
            col = level_index % 5

            # Миниатюра фона уровня
            preview_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - 250 + col * 120,
                70 + row * 100,
                100, 60
            )

            # Показываем миниатюру фона
            if level_index < len(self.backgrounds):
                preview = pygame.transform.scale(self.backgrounds[level_index], (100, 60))
                self.screen.blit(preview, preview_rect)

            # Кнопка уровня
            level_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - 250 + col * 120,
                130 + row * 100,
                100, 30
            )
            self.level_rects.append(level_rect)

            # Определяем цвет кнопки
            if level_index + 1 == self.current_level:
                color = GREEN
            elif level_index + 1 <= self.max_unlocked_level:
                color = WHITE
            else:
                color = (100, 100, 100)

            pygame.draw.rect(self.screen, color, level_rect, border_radius=5)

            # Цвет текста в зависимости от фона кнопки
            text_color = (0, 0, 0) if color == WHITE or color == GREEN else WHITE
            level_text = self.font.render(f"Уровень {level_index + 1}", True, text_color)
            self.screen.blit(level_text, (level_rect.x + 10, level_rect.y + 8))

    def start_level(self, level):
        """Initialize level with given number"""
        self.game_state = "playing"
        self.player.lives = PLAYER_LIVES
        self.enemies_defeated = 0
        self.current_level = level
        self.enemies_to_next_level = ENEMIES_FOR_FIRST_LEVEL + (level - 1) * LEVEL_INCREMENT
        self.enemy.speed = min(0.7 + level * 0.3, MAX_ENEMY_SPEED)

        # Обновляем максимальный открытый уровень
        if level > self.max_unlocked_level:
            self.max_unlocked_level = level

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
            elif event.type == pygame.USEREVENT + 1:
                # Музыка закончилась - перезапускаем
                if self.game_state == "playing":
                    self.play_track_for_level(self.current_level)
                else:
                    self.play_menu_music()
            elif event.type == pygame.MOUSEBUTTONDOWN and self.game_state == "level_select":
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(self.level_rects):
                    if rect.collidepoint(mouse_pos) and i + 1 <= self.max_unlocked_level:
                        self.start_level(i + 1)
                        break
            elif event.type == pygame.KEYDOWN:
                if self.game_state == "level_select":
                    # Быстрая навигация по уровням с клавиатуры
                    if pygame.K_1 <= event.key <= pygame.K_0 + MAX_LEVELS:
                        level = event.key - pygame.K_1 + 1
                        if level <= self.max_unlocked_level:
                            self.start_level(level)
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
                self.sound_manager.play_sound('slide')
                self.reset_positions()
                if self.player.lives <= 0:
                    self.game_state = "level_select"
                    pygame.mixer.music.stop()
                    self.play_menu_music()
            else:
                # Враг отскакивает от щита
                self.enemy.reset()

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
            # Рисуем фон уровня
            if 0 <= self.current_level - 1 < len(self.backgrounds):
                self.screen.blit(self.backgrounds[self.current_level - 1], (0, 0))
            else:
                self.screen.fill((0, 0, 0))

            # Рисуем игровые объекты
            self.player.draw(self.screen)
            self.enemy.draw(self.screen)
            self.regular_bonus.draw(self.screen)
            self.shield_bonus.draw(self.screen)
            self.gun_bonus.draw(self.screen)

            # Рисуем статистику
            lives_text = self.font.render(f'Жизни: {self.player.lives}', True, WHITE)
            defeated_text = self.font.render(f'Побеждено: {self.enemies_defeated}/{self.enemies_to_next_level}', True,
                                             WHITE)
            level_text = self.font.render(f'Уровень: {self.current_level}', True, WHITE)

            self.screen.blit(lives_text, (10, 10))
            self.screen.blit(defeated_text, (10, 40))
            self.screen.blit(level_text, (10, 70))

            # Рисуем активные бонусы
            if self.player.shield_active:
                shield_text = self.font.render('ЩИТ АКТИВЕН', True, CYAN)
                self.screen.blit(shield_text, (SCREEN_WIDTH - 150, 10))

            if self.player.gun_active:
                gun_text = self.font.render('ОРУЖИЕ АКТИВНО', True, RED)
                self.screen.blit(gun_text, (SCREEN_WIDTH - 150, 40))

        pygame.display.flip()

    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_events()

            keys = pygame.key.get_pressed()
            if self.game_state == "playing":
                # Управление игроком
                if keys[pygame.K_LEFT]:
                    self.player.move("left")
                    self.sound_manager.play_sound('player_move')
                elif keys[pygame.K_RIGHT]:
                    self.player.move("right")
                    self.sound_manager.play_sound('player_move')
                else:
                    self.sound_manager.stop_sound('player_move')

                # Звук движения врага
                if self.enemy.y > 0:
                    self.sound_manager.play_sound('enemy_move')
                else:
                    self.sound_manager.stop_sound('enemy_move')

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()