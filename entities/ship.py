import os
import pygame

class Ship:
    """Nave del jugador.

    Proporciona:
      - draw(window)
      - move(dx, dy)
      - clamp_to(width, height)
      - get_width()/get_height()

    Atributos solicitados:
      - x, y
      - health (default 100)
      - ship_img, bullet_img
      - bullet_cooldown_counter
      - bullets, fired_bullets
      - cool_down (frames)
    """

    def __init__(
        self,
        x: int,
        y: int,
        health: int = 100,
        image_path: str = None,
        speed: int = 5,
        bullet_image_path: str = None,
    ) -> None:
        # Posición y estado
        self.x = x
        self.y = y
        self.health = health
        self.speed = speed

        # Imágenes (nave y bala)
        if image_path and os.path.exists(image_path):
            self.ship_img = pygame.image.load(image_path).convert_alpha()
        else:
            # placeholder
            self.ship_img = pygame.Surface((40, 24), pygame.SRCALPHA)
            self.ship_img.fill((0, 200, 255))

        if bullet_image_path and os.path.exists(bullet_image_path):
            self.bullet_img = pygame.image.load(bullet_image_path).convert_alpha()
        else:
            self.bullet_img = None

        # Rect de colisión/dibujo basado en la imagen de la nave
        self.rect = self.ship_img.get_rect(topleft=(self.x, self.y))

        # Disparo
        self.bullet_cooldown_counter = 0
        self.bullets = []
        self.fired_bullets = []
        self.cool_down = 120

    def draw(self, window: pygame.Surface) -> None:
        window.blit(self.ship_img, (self.x, self.y))

    def move(self, dx: int, dy: int) -> None:
        self.x += dx
        self.y += dy
        self.rect.topleft = (self.x, self.y)

    def clamp_to(self, width: int, height: int) -> None:
        self.x = max(0, min(self.x, width - self.rect.width))
        self.y = max(0, min(self.y, height - self.rect.height))
        self.rect.topleft = (self.x, self.y)

    def get_width(self) -> int:
        return self.ship_img.get_width()

    def get_height(self) -> int:
        return self.ship_img.get_height()
