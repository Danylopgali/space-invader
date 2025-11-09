import pygame
from game import Game
from core.menu_principal import MenuPrincipal


def main():
    # Inicializar Pygame antes de usar el menú de puntajes
    if not pygame.get_init():
        pygame.init()
        try:
            pygame.font.init()
        except Exception:
            pass

    # Menú principal: retorna nombre si elige "Nuevo Juego"
    menu = MenuPrincipal()
    nombre = menu.run("scores.txt")
    if not nombre:
        pygame.quit()
        return

    # Tras elegir nombre válido, iniciar el juego principal con ese nombre
    game = Game(player_name=nombre)
    game.run()


if __name__ == "__main__":
    main()