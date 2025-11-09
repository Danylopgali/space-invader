import os
import pygame
from pygame import mixer
from core.settings import PROJECT_ROOT

if not pygame.get_init():
    pygame.init()
try:
    if not pygame.font.get_init():
        pygame.font.init()
except Exception:
    pass

try:
    if not mixer.get_init():
        mixer.init()
except Exception:
    pass

class MenuAcercaDe:
    BLANCO = (255, 255, 255)
    NEGRO = (0, 0, 0)
    GRIS = (180, 180, 180)
    ROJO = (255, 0, 0)

    ANCHO = 800
    ALTO = 600
    ventana = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Acerca de - Space Invaders")

    def __init__(self) -> None:
        self.fuente_titulo = pygame.font.Font(None, 54)
        self.fuente_texto = pygame.font.Font(None, 30)
        self.fuente_pequena = pygame.font.Font(None, 24)
        self.clock = pygame.time.Clock()
        # Fondo opcional reutiliza menu_fondo si existe
        fondo_path = os.path.join(PROJECT_ROOT, 'images', 'menu_fondo.jpg')
        self.background = None
        if os.path.exists(fondo_path):
            try:
                img = pygame.image.load(fondo_path).convert()
                self.background = pygame.transform.scale(img, (self.ANCHO, self.ALTO))
            except Exception:
                self.background = None
        # Logo hybridge opcional
        logo_path = os.path.join(PROJECT_ROOT, 'images', 'hybridge.gif')
        self.logo = None
        if os.path.exists(logo_path):
            try:
                lg = pygame.image.load(logo_path).convert_alpha()
                ratio = 100 / lg.get_width()
                self.logo = pygame.transform.smoothscale(lg, (100, int(lg.get_height() * ratio)))
            except Exception:
                self.logo = None

    def mostrar_texto(self, texto, font, color, superficie, x, y):
        surf = font.render(texto, True, color)
        rect = surf.get_rect(center=(x, y))
        superficie.blit(surf, rect)
        return rect

    def dibujar_boton(self, texto, x, y, ancho, alto, color):
        rect = pygame.Rect(x, y, ancho, alto)
        pygame.draw.rect(self.ventana, color, rect, border_radius=8)
        self.mostrar_texto(texto, self.fuente_texto, self.NEGRO, self.ventana, x + ancho/2, y + alto/2)
        return rect

    def ejecutar(self):
        acerca_lineas = [
            "Space Invaders (versión prototipo)",
            "Proyecto educativo en Python + Pygame", 
            "Objetivo: Practicar POO, manejo de eventos y assets.",
            "Autor: Danylopgali", 
            "Música y recursos: placeholders / usuario", 
            "Hybridge demo logo en esquina." ,
        ]
        boton_volver = pygame.Rect(30, 20, 140, 50)
        running = True
        while running:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if boton_volver.collidepoint(event.pos):
                        running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            # Fondo
            if self.background:
                self.ventana.blit(self.background, (0, 0))
            else:
                self.ventana.fill(self.NEGRO)

            # Titulo
            self.mostrar_texto("Acerca de", self.fuente_titulo, self.BLANCO, self.ventana, self.ANCHO/2, 90)

            # Texto central
            y_base = 170
            for i, linea in enumerate(acerca_lineas):
                self.mostrar_texto(linea, self.fuente_texto, self.GRIS, self.ventana, self.ANCHO/2, y_base + i * 42)

            # Logo
            if self.logo:
                self.ventana.blit(self.logo, (self.ANCHO - self.logo.get_width() - 20, self.ALTO - self.logo.get_height() - 20))

            # Botón volver
            pygame.draw.rect(self.ventana, self.ROJO, boton_volver, border_radius=8)
            self.mostrar_texto("Volver", self.fuente_texto, self.NEGRO, self.ventana, boton_volver.x + boton_volver.width/2, boton_volver.y + boton_volver.height/2)

            pygame.display.flip()

        # No hacemos quit aquí; se regresa al llamador
