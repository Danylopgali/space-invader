import os
import random
import pygame

from core.settings import ASSETS_IMG_DIR, WIDTH, PROJECT_ROOT
from entities.ship import Ship


def _load_or_placeholder(path: str | None, size=None, color=(200, 50, 50)) -> pygame.Surface:
    """Carga imagen; evita convert_alpha antes de que el display esté inicializado.

    Si la imagen existe pero aún no hay display (import temprano), se devuelve la superficie cruda.
    Después, al dibujar, pygame usará esa superficie sin problemas; para optimizar se podría convertir
    tras crear la ventana.
    """
    if path and os.path.exists(path):
        img = pygame.image.load(path)  # no convert_alpha aún si no hay display
        if pygame.display.get_init():
            img = img.convert_alpha()
        if size is not None:
            img = pygame.transform.smoothscale(img, size)
        return img
    w, h = size if size else (40, 24)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill(color)
    return surf


# Directorio de imágenes: ahora priorizamos directamente images/ (según tu carpeta actual)
IMAGES_DIR = os.path.join(PROJECT_ROOT, 'images')
IMG_DIR = os.path.join(IMAGES_DIR, 'img')  # aún soportado como fallback

def first_existing(paths):
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None

# Cargar superficies (prioridad absoluta a images/ raíz con nombres explícitos)
ENEMY_BLUE_IMAGE = _load_or_placeholder(first_existing([
    os.path.join(IMAGES_DIR, 'enemy_blue_image.png'),
    os.path.join(IMG_DIR, 'enemy_blue_image.png'),
    os.path.join(ASSETS_IMG_DIR, 'enemy_blue.png'),
]), size=None, color=(80, 80, 255))
ENEMY_GREEN_IMAGE = _load_or_placeholder(first_existing([
    os.path.join(IMAGES_DIR, 'enemy_green_image.png'),
    os.path.join(IMG_DIR, 'enemy_green_image.png'),
    os.path.join(ASSETS_IMG_DIR, 'enemy_green.png'),
]), size=None, color=(60, 200, 60))
ENEMY_PURPLE_IMAGE = _load_or_placeholder(first_existing([
    os.path.join(IMAGES_DIR, 'enemy_purple_image.png'),
    os.path.join(IMG_DIR, 'enemy_purple_image.png'),
    os.path.join(ASSETS_IMG_DIR, 'enemy_purple.png'),
]), size=None, color=(160, 80, 200))
SHOT_BLUE_IMAGE = _load_or_placeholder(first_existing([
    os.path.join(IMAGES_DIR, 'shot_blue.png'),
    os.path.join(IMG_DIR, 'shot_blue.png'),
    os.path.join(ASSETS_IMG_DIR, 'shot_blue.png'),
]), size=None, color=(80, 160, 255))
SHOT_GREEN_IMAGE = _load_or_placeholder(first_existing([
    os.path.join(IMAGES_DIR, 'shot_green.png'),
    os.path.join(IMG_DIR, 'shot_green.png'),
    os.path.join(ASSETS_IMG_DIR, 'shot_green.png'),
]), size=None, color=(80, 255, 120))
SHOT_PURPLE_IMAGE = _load_or_placeholder(first_existing([
    os.path.join(IMAGES_DIR, 'shot_purple.png'),
    os.path.join(IMG_DIR, 'shot_purple.png'),
    os.path.join(ASSETS_IMG_DIR, 'shot_purple.png'),
]), size=None, color=(200, 120, 255))


class Enemy(Ship):
    """Representa un enemigo que hereda de Ship.

    - Constructor define posición, color, salud y velocidad.
    - Usa un mapeo COLOR para asignar imágenes de nave/disparo por color.
    - Incluye utilidades para movimiento y creación de múltiples enemigos.
    """

    COLOR = {
        'blue': (ENEMY_BLUE_IMAGE, SHOT_BLUE_IMAGE),
        'green': (ENEMY_GREEN_IMAGE, SHOT_GREEN_IMAGE),
        'purple': (ENEMY_PURPLE_IMAGE, SHOT_PURPLE_IMAGE),
    }

    def __init__(self, speed: int, x: int = 50, y: int = 50, color: str = 'blue', health: int = 100) -> None:
        # Inicializar posición/estado base (Ship maneja x, y, health, speed y rect)
        super().__init__(x, y, health=health, image_path=None, speed=speed, bullet_image_path=None)
        color = (color or 'blue').lower()
        ship_img, bullet_img = self.COLOR.get(color, self.COLOR['blue'])
        self.ship_img = ship_img
        self.bullet_img = bullet_img
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.speed = speed
        self.rect = self.ship_img.get_rect(topleft=(self.x, self.y))

    def update(self) -> None:
        """Movimiento hacia abajo simple (Space Invaders clásico para este nivel)."""
        self.move()

    def increase_speed(self, delta: int = 1) -> None:
        self.speed = max(0, self.speed + delta)

    def move(self) -> None:  # type: ignore[override]
        """Movimiento vertical hacia abajo, como en tu ejemplo."""
        super().move(0, self.speed)

    @classmethod
    def create_enemies(cls, count: int, y: int = 50, speed: int = 2, colors=None, width: int = None, padding: int = 16):
        """(Modo fila) Conservado por compatibilidad: crea una fila horizontal en y fija."""
        if width is None:
            width = WIDTH
        if not colors:
            colors = ['blue', 'green', 'purple']

        enemies = []
        ship_w = ENEMY_BLUE_IMAGE.get_width()
        total_w = count * ship_w + (count - 1) * padding
        start_x = max(10, (width - total_w) // 2)
        for i in range(count):
            x = start_x + i * (ship_w + padding)
            color = random.choice(colors)
            enemies.append(cls(speed=speed, x=x, y=y, color=color))
        return enemies

    @classmethod
    def create(cls, count: int, y: int = 50, speed: int = 2, colors=None, width: int = None, padding: int = 16):
        """Alias simple (fila)."""
        return cls.create_enemies(count=count, y=y, speed=speed, colors=colors, width=width, padding=padding)

    # -------- API estilo ejemplo del usuario ---------
    def create(self, amount: int):  # instance method
        """Crea 'amount' enemigos con x aleatoria y y fuera de pantalla (-1000,-100)."""
        enemies = []
        for _ in range(amount):
            enemy = Enemy(
                x=random.randrange(20, WIDTH - ENEMY_BLUE_IMAGE.get_width() - 20),
                y=random.randrange(-1000, -100),
                color=random.choice(['blue', 'green', 'purple']),
                speed=self.speed,
            )
            enemies.append(enemy)
        return enemies

    def increase_speed(self):  # override multiplicativo como el ejemplo
        self.speed *= 1.02
