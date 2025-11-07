import os
import pygame

from core.settings import PROJECT_ROOT, ASSETS_IMG_DIR, WIDTH, HEIGHT
from entities.ship import Ship
from entities.bullet import Bullet


def first_existing(paths):
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None


class Player(Ship):
    def __init__(self, x: int, y: int, x_speed: float, y_speed: float, health: int = 100) -> None:
        # Cargar imágenes del jugador y bala
        images_dir = os.path.join(PROJECT_ROOT, 'images')
        player_img_path = first_existing([
            os.path.join(images_dir, 'img', 'player_image.png'),
            os.path.join(images_dir, 'player_image.png'),
            os.path.join(ASSETS_IMG_DIR, 'ship.png'),
        ])
        bullet_img_path = first_existing([
            os.path.join(images_dir, 'img', 'bullet_image.png'),
            os.path.join(images_dir, 'bullet_image.png'),
            os.path.join(ASSETS_IMG_DIR, 'bullet.png'),
        ])
        super().__init__(x, y, health=health, image_path=player_img_path, speed=int(max(x_speed, y_speed)), bullet_image_path=bullet_img_path)
        
        # Velocidades específicas
        self.x_speed = x_speed
        self.y_speed = y_speed

        # Parámetros de disparo
        self.bullet_speed = -10
        self.max_health = health
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.creation_cooldown_counter = 0
        self.max_amount_bullets = 3
        self.bullets = []
        self.fired_bullets = []
        self.bullet_cooldown_counter = 0

    def move(self, width: int = WIDTH, height: int = HEIGHT) -> None:
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and (self.y > 0):
            self.y -= self.y_speed
        elif (keys[pygame.K_DOWN] or keys[pygame.K_s]) and (self.y < height - self.ship_img.get_height() - 60):
            self.y += self.y_speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and (self.x < width - self.ship_img.get_width()):
            self.x += self.x_speed
        elif (keys[pygame.K_LEFT] or keys[pygame.K_a]) and (self.x > 0):
            self.x -= self.x_speed
        self.rect.topleft = (int(self.x), int(self.y))

    def increase_speed(self) -> None:
        if self.x_speed < 10:
            self.x_speed += 1.25
            self.y_speed += 1.25
        elif self.x_speed >= 10:
            self.x_speed = 10
            self.y_speed = 8
        if self.cool_down > 25:
            self.cool_down = int(self.cool_down * 0.9)

    def create_bullets(self) -> None:
        if (len(self.bullets) < self.max_amount_bullets) and (self.creation_cooldown_counter == 0):
            img = self.bullet_img or pygame.Surface((8, 16), pygame.SRCALPHA)
            if self.bullet_img is None:
                img.fill((255, 255, 0))
            bullet = Bullet(self.x, self.y, img, speed=self.bullet_speed)
            self.bullets.append(bullet)
            self.creation_cooldown_counter = 1

    def cooldown(self) -> None:
        if self.bullet_cooldown_counter >= 20:
            self.bullet_cooldown_counter = 0
        elif self.bullet_cooldown_counter > 0:
            self.bullet_cooldown_counter += 1

        if self.creation_cooldown_counter >= self.cool_down:
            self.creation_cooldown_counter = 0
        elif self.creation_cooldown_counter > 0:
            self.creation_cooldown_counter += 1

    def fire(self, window: pygame.Surface | None = None) -> None:
        """Gestiona el disparo (sin dibujar)."""
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_SPACE]) and (len(self.bullets) > 0) and (self.bullet_cooldown_counter == 0):
            # Centrar bala en la nave
            last = self.bullets[-1]
            last.x = self.x + (self.ship_img.get_width() - (last.image.get_width())) / 2
            last.y = self.y + 10
            last.rect.topleft = (int(last.x), int(last.y))
            self.fired_bullets.append(self.bullets.pop())
            self.bullet_cooldown_counter = 1
            self.creation_cooldown_counter = 1

    def update_bullets(self) -> None:
        """Actualiza posición de las balas disparadas y limpia las fuera de pantalla."""
        for b in self.fired_bullets:
            b.move(self.bullet_speed)
        self.fired_bullets = [b for b in self.fired_bullets if b.y > -40]

    def hit(self, enemy) -> bool:
        if not self.fired_bullets:
            return False
        # Checa colisión con la última bala disparada
        b = self.fired_bullets[-1]
        self.creation_cooldown_counter = int(self.cool_down * 0.8)
        return b.collision(enemy)
