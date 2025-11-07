import os
import pygame

from core.settings import PROJECT_ROOT, ASSETS_IMG_DIR

# Fallback color if no background image
FALLBACK_BG_COLOR = (10, 10, 25)

class Drawing:
    """Encapsula lógica de dibujado de escena (background, entidades, HUD)."""

    def __init__(self, window: pygame.Surface):
        self.window = window
        self.background = self._load_background()

    def _load_background(self) -> pygame.Surface:
        images_dir = os.path.join(PROJECT_ROOT, 'images')
        root_bg = os.path.join(images_dir, 'background.png')
        legacy_bg = os.path.join(images_dir, 'img', 'background.png')
        assets_bg = os.path.join(ASSETS_IMG_DIR, 'background.png')
        for path in (root_bg, legacy_bg, assets_bg):
            if os.path.exists(path):
                return pygame.image.load(path).convert()
        # Crear fondo placeholder
        surf = pygame.Surface(self.window.get_size())
        surf.fill(FALLBACK_BG_COLOR)
        return surf

    def draw_scene(self, game, player, enemies):
        """Dibuja la escena completa excepto display.update()."""
        # Fondo
        if self.background.get_size() != self.window.get_size():
            bg_scaled = pygame.transform.scale(self.background, self.window.get_size())
            self.window.blit(bg_scaled, (0, 0))
        else:
            self.window.blit(self.background, (0, 0))

        # Enemigos
        for enemy in enemies:
            enemy.draw(self.window)

        # Jugador
        if player:
            player.draw(self.window)

        # HUD del juego
        game.draw_HUD()

    def present(self):
        pygame.display.update()
