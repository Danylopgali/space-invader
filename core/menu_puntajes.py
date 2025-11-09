import os
import sys
import pygame
from typing import List, Tuple

# Asegurar inicialización básica de Pygame antes de crear ventana
if not pygame.get_init():
    pygame.init()
    try:
        pygame.font.init()
    except Exception:
        pass


class MenuPuntajes:
    # Colores en RGB
    BLANCO = (255, 255, 255)
    NEGRO = (0, 0, 0)
    GRIS = (200, 200, 200)
    ROJO = (255, 0, 0)

    # Dimensiones de la ventana
    ANCHO = 800
    ALTO = 600

    # Configurar ventana y título (siguiendo el esquema solicitado)
    ventana = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Mejores Puntajes")

    def __init__(self) -> None:
        self.fuente_titulo = pygame.font.Font(None, 48)
        self.fuente_item = pygame.font.Font(None, 36)
        self.fuente_subtitulo = pygame.font.Font(None, 28)
        # Ruta de fondo opcional
        self.background_path = os.path.join(os.path.dirname(__file__), '..', 'images', 'background.png')
        self.background_img = None
        if os.path.exists(self.background_path):
            try:
                self.background_img = pygame.image.load(self.background_path).convert()
            except Exception:
                self.background_img = None

    def mostrar_texto(self, texto: str, font: pygame.font.Font, color: tuple, superficie: pygame.Surface, x: float, y: float) -> None:
        """Renderiza y centra texto en (x, y) sobre la superficie dada."""
        texto_objeto = font.render(texto, True, color)
        rectangulo_texto = texto_objeto.get_rect(center=(int(x), int(y)))
        superficie.blit(texto_objeto, rectangulo_texto)

    def dibujar_boton(self, texto: str, font: pygame.font.Font, color_fondo: tuple, superficie: pygame.Surface,
                      x: int, y: int, ancho: int, alto: int) -> pygame.Rect:
        """Dibuja un botón y retorna su rect para detectar clics."""
        boton_rect = pygame.Rect(x, y, ancho, alto)
        pygame.draw.rect(superficie, color_fondo, boton_rect, border_radius=6)
        self.mostrar_texto(texto, font, self.NEGRO, superficie, x + ancho / 2, y + alto / 2)
        return boton_rect

    def mostrar_puntajes(self, lista_puntajes):
        # Fondo
        if self.background_img:
            bg_scaled = pygame.transform.scale(self.background_img, (self.ANCHO, self.ALTO))
            self.ventana.blit(bg_scaled, (0, 0))
        else:
            self.ventana.fill(self.NEGRO)
        # Título y subtítulo
        self.mostrar_texto("Mejores Puntajes", self.fuente_titulo, self.BLANCO, self.ventana, self.ANCHO / 2, 50)
        self.mostrar_texto("Space Invaders", self.fuente_subtitulo, self.GRIS, self.ventana, self.ANCHO / 2, 85)
        # Lista de puntajes o mensaje vacío
        inicio_y = 140
        if not lista_puntajes:
            self.mostrar_texto("No hay registros", self.fuente_item, self.GRIS, self.ventana, self.ANCHO / 2, inicio_y)
        else:
            for i, (nombre, puntaje) in enumerate(lista_puntajes, start=1):
                linea = f"{i}. {nombre} - {puntaje}"
                self.mostrar_texto(linea, self.fuente_item, self.BLANCO, self.ventana, self.ANCHO / 2, inicio_y + (i - 1) * 44)
        # Botón volver
        self.boton_volver = self.dibujar_boton("<", self.fuente_item, self.ROJO, self.ventana, 20, 20, 50, 40)
        pygame.display.update()

    def cargar_puntajes(self, archivo: str) -> List[Tuple[str, int]]:
        """Carga puntajes desde un archivo de texto.
        Formato esperado por línea: nombre,puntaje
        - Ignora líneas vacías o con formato inválido
        - Si no existe, retorna lista vacía
        - Devuelve el top 5 ordenado descendentemente por puntaje
        """
        puntajes: List[Tuple[str, int]] = []
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea:
                        continue
                    # Separador por coma o por punto y coma o tabulación
                    sep = ',' if ',' in linea else (';' if ';' in linea else None)
                    partes = linea.split(sep) if sep else linea.split()
                    if len(partes) < 2:
                        continue
                    nombre = partes[0].strip()
                    try:
                        puntaje = int(partes[1])
                    except ValueError:
                        continue
                    puntajes.append((nombre, puntaje))
        except FileNotFoundError:
            # No existe el archivo: retornar lista vacía (primer arranque)
            return []
        except Exception:
            # Cualquier otro error, ser resiliente y retornar lo que tengamos
            pass
        # Ordenar por puntaje descendente y devolver top 5
        puntajes.sort(key=lambda t: t[1], reverse=True)
        return puntajes[:5]

    def dibujar(self, lista_puntajes: List[Tuple[str, int]]) -> None:
        # Mantener compatibilidad; delegar en mostrar_puntajes
        self.mostrar_puntajes(lista_puntajes)

    def run(self, archivo: str) -> None:
        lista = self.cargar_puntajes(archivo)
        clock = pygame.time.Clock()
        corriendo = True
        while corriendo:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    corriendo = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        corriendo = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if hasattr(self, 'boton_volver') and self.boton_volver.collidepoint(event.pos):
                        corriendo = False
            self.mostrar_puntajes(lista)

    def ejecutar(self, archivo: str) -> None:
        """Muestra la pantalla de puntajes y maneja eventos.
        - Carga y dibuja puntajes.
        - Si se cierra la ventana: cierra Pygame y termina el programa.
        - Si se hace clic izquierdo dentro del botón de retroceso: imprime confirmación y retorna.
        """
        lista = self.cargar_puntajes(archivo)
        clock = pygame.time.Clock()
        while True:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Asegurar que el botón exista en este frame
                    if hasattr(self, 'boton_volver') and self.boton_volver.collidepoint(event.pos):
                        print("acción atrás")
                        return
            self.mostrar_puntajes(lista)

        # No cerramos pygame.quit() aquí por si el menú se llama desde el juego principal
        # El llamador decide cuándo terminar Pygame.
