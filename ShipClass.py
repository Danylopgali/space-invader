import os
import pygame


class Ship:
    """Nave del jugador.

    - Si se proporciona una ruta de imagen válida, se carga y usa su tamaño.
    - Si no hay imagen, se dibuja un rectángulo como placeholder.
    """

    def __init__(self, x: int, y: int, image_path: str | None = None, speed: int = 5) -> None:
        self.x = x
        self.y = y
        self.speed = speed

        self.image: pygame.Surface | None
        if image_path and os.path.exists(image_path):
            self.image = pygame.image.load(image_path).convert_alpha()
        else:
            # placeholder rectangular (40x24)
            surf = pygame.Surface((40, 24), pygame.SRCALPHA)
            surf.fill((0, 200, 255))
            self.image = surf

        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    # --- API ---
    def draw(self, window: pygame.Surface) -> None:
        window.blit(self.image, (self.rect.x, self.rect.y))

    def get_width(self) -> int:
        return self.rect.width

    def get_height(self) -> int:
        return self.rect.height

    def move(self, dx: int, dy: int) -> None:
        self.rect.x += dx
        self.rect.y += dy

    def clamp_to(self, width: int, height: int) -> None:
        """Mantiene a la nave dentro de los límites del área dada."""
        self.rect.x = max(0, min(self.rect.x, width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, height - self.rect.height))
