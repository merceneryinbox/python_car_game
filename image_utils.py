import os
import pygame


def generate_car_placeholder(width: int, height: int) -> pygame.Surface:
    """
    Генерирует PNG машинки-заглушки (вид сверху).
    Используется, если оригинальное изображение отсутствует.
    """
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))  # прозрачный фон

    # Корпус машины
    pygame.draw.rect(surface, (0, 150, 0), (width // 4, height // 6, width // 2, 2 * height // 3))

    # Крыша
    pygame.draw.rect(surface, (0, 200, 0), (width // 3, height // 3, width // 3, height // 3))

    # Колёса
    wheel_width = width // 6
    wheel_height = height // 8
    # Передние
    pygame.draw.rect(surface, (0, 0, 0), (width // 4 - wheel_width, height // 6, wheel_width, wheel_height))
    pygame.draw.rect(surface, (0, 0, 0), (3 * width // 4, height // 6, wheel_width, wheel_height))
    # Задние
    pygame.draw.rect(surface, (0, 0, 0), (width // 4 - wheel_width, height * 2 // 3, wheel_width, wheel_height))
    pygame.draw.rect(surface, (0, 0, 0), (3 * width // 4, height * 2 // 3, wheel_width, wheel_height))

    return surface


def load_game_image(name: str, width: int, height: int, keep_aspect: bool = True) -> pygame.Surface:
    """
    Универсальная функция загрузки и подгона изображения.
    - Если keep_aspect=True: сохраняем пропорции, добавляя отступы (letterbox).
    - Если keep_aspect=False: растягиваем в точный размер (может исказиться).
    Если файла нет — возвращается заглушка машинки.
    """
    try:
        # Определяем корень проекта (папка python_car_game)
        project_root = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(project_root, "assets", "images", name)

        if not os.path.exists(image_path):
            print(f"❌ Файл не найден: {image_path}. Используем заглушку машинки.")
            return generate_car_placeholder(width, height)

        # Загружаем картинку
        image = pygame.image.load(image_path).convert_alpha()

        orig_w, orig_h = image.get_size()

        if keep_aspect:
            # Вычисляем масштаб с сохранением пропорций
            scale_factor = min(width / orig_w, height / orig_h)
            new_w = int(orig_w * scale_factor)
            new_h = int(orig_h * scale_factor)

            # Масштабируем с сохранением пропорций
            image = pygame.transform.smoothscale(image, (new_w, new_h))

            # Создаём холст целевого размера и центрируем картинку
            final_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            offset_x = (width - new_w) // 2
            offset_y = (height - new_h) // 2
            final_surface.blit(image, (offset_x, offset_y))

            print(f"ℹ Масштабирование {name}: {orig_w}x{orig_h} → {new_w}x{new_h}, "
                  f"помещено в {width}x{height} с отступами")
            return final_surface

        else:
            # Жёсткое масштабирование (может искажать)
            image = pygame.transform.smoothscale(image, (width, height))
            print(f"ℹ Жёсткое масштабирование {name}: {orig_w}x{orig_h} → {width}x{height}")
            return image

    except Exception as e:
        print(f"❌ Ошибка загрузки изображения '{name}': {e}. Используем заглушку машинки.")
        return generate_car_placeholder(width, height)
