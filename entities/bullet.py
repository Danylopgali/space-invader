import pygame

class Bullet:
    def __init__(self, x: float, y: float, image: pygame.Surface, speed: int = -10) -> None:
        self.x = x
        self.y = y
        self.image = image
        self.speed = speed
        self.rect = self.image.get_rect(topleft=(int(self.x), int(self.y)))

    def move(self, dy: int | float = None) -> None:
        if dy is None:
            dy = self.speed
        self.y += dy
        self.rect.topleft = (int(self.x), int(self.y))

    def draw(self, window: pygame.Surface) -> None:
        window.blit(self.image, (int(self.x), int(self.y)))

    def collision(self, target) -> bool:
        # Usa mask overlap si disponible; si no, rects
        if hasattr(target, 'mask') and hasattr(target, 'rect'):
            # Crear mask de bala en caliente
            bullet_mask = pygame.mask.from_surface(self.image)
            offset = (int(target.rect.x - self.rect.x), int(target.rect.y - self.rect.y))
            overlap = bullet_mask.overlap(target.mask, offset)
            return overlap is not None
        # Fallback a rects
        return self.rect.colliderect(getattr(target, 'rect', pygame.Rect(target.x, target.y, 1, 1)))
