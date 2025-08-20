import pygame
from constants import *

def load_image(path, size, default_color, default_surface=True):
    """Load an image with fallback to default surface if file not found"""
    try:
        image = pygame.image.load(path)
        return pygame.transform.scale(image, size)
    except FileNotFoundError:
        if default_surface:
            surface = pygame.Surface(size)
            surface.fill(default_color)
            return surface
        raise

def load_sound(path, volume=1.0):
    """Load a sound file with error handling"""
    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        return sound
    except FileNotFoundError:
        print(f"Sound file not found: {path}")
        # Return silent sound
        silent_sound = pygame.mixer.Sound(buffer=bytearray(44))
        silent_sound.set_volume(0)
        return silent_sound

def load_backgrounds():
    """Load background images for all levels"""
    backgrounds = []
    for i in range(1, MAX_LEVELS + 1):
        try:
            bg_image = pygame.image.load(f'assets/images/desert_background_level_{i}.png')
            bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            backgrounds.append(bg_image)
        except FileNotFoundError:
            temp_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            temp_bg.fill(SAND_COLOR)
            backgrounds.append(temp_bg)
    return backgrounds