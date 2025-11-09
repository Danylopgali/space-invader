import os
import pygame
from pygame import mixer
from core.settings import PROJECT_ROOT
from core.menu_puntajes import MenuPuntajes

# Inicialización segura de Pygame (display, fonts, audio)
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
    # En entornos sin audio (p.ej., WSL), ignorar
    pass


class MenuPrincipal:
    # Colores
    BLANCO = (255, 255, 255)
    NEGRO = (0, 0, 0)
    ROJO = (255, 0, 0)

    # Ventana
    ANCHO = 800
    ALTO = 600
    ventana = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Space Invaders")

    # Música de fondo (opcional, ignorando errores)
    try:
        # Intentar en assets/sounds y luego en sounds/ relativo
        CANDIDATOS = [
            os.path.join(PROJECT_ROOT, 'assets', 'sounds', 'background_song.mp3'),
            os.path.join(PROJECT_ROOT, 'sounds', 'background_song.mp3'),
            'sounds/background_song.mp3',
        ]
        _music_path = next((p for p in CANDIDATOS if os.path.exists(p)), None)
        if _music_path:
            mixer.music.load(_music_path)
            try:
                mixer.music.play(-1)
            except Exception:
                pass
    except Exception:
        # No se pudo cargar el sonido; continuar sin música
        pass

    # Ruta de imágenes (usar images/img si existe, si no images)
    _img_dir_candidates = [
        os.path.join(PROJECT_ROOT, 'images', 'img'),
        os.path.join(PROJECT_ROOT, 'images'),
        'img',
    ]
    DIR_IMAGENES = next((p for p in _img_dir_candidates if os.path.exists(p)), _img_dir_candidates[0])

    def __init__(self) -> None:
        # Preparar fuentes por si luego se usan en textos
        try:
            self.fuente_titulo = pygame.font.Font(None, 56)
            self.fuente_item = pygame.font.Font(None, 36)
            self.fuente_input = pygame.font.Font(None, 32)
        except Exception:
            self.fuente_titulo = None
            self.fuente_item = None
            self.fuente_input = None

        # Cargar imágenes: fondo del menú y logo hybridge
        # Fondo: preferir ruta absoluta dada; fallback a images/menu_fondo.jpg en el proyecto
        bg_abs = r"C:\\Users\\danie\\Desktop\\escuela\\space_ivaders\\images\\menu_fondo.jpg"
        bg_rel = os.path.join(PROJECT_ROOT, 'images', 'menu_fondo.jpg')
        self.menu_bg_img = None
        for p in (bg_abs, bg_rel):
            if os.path.exists(p):
                try:
                    self.menu_bg_img = pygame.image.load(p).convert()
                    break
                except Exception:
                    self.menu_bg_img = None
        # Pre-escalar una sola vez
        self.menu_bg_scaled = None
        if self.menu_bg_img is not None:
            try:
                self.menu_bg_scaled = pygame.transform.scale(self.menu_bg_img, (self.ANCHO, self.ALTO))
            except Exception:
                self.menu_bg_scaled = None

        # Logo hybridge en esquina
        logo_candidates = [
            os.path.join(PROJECT_ROOT, 'images', 'hybridge.gif'),
            os.path.join('images', 'hybridge.gif'),
        ]
        self.logo_img = None
        for p in logo_candidates:
            if os.path.exists(p):
                try:
                    self.logo_img = pygame.image.load(p).convert_alpha()
                    break
                except Exception:
                    self.logo_img = None
        self.logo_scaled = None
        if self.logo_img is not None:
            try:
                max_w = 90
                ratio = max_w / self.logo_img.get_width() if self.logo_img.get_width() else 1.0
                new_w = max_w
                new_h = int(self.logo_img.get_height() * ratio) if ratio > 0 else self.logo_img.get_height()
                self.logo_scaled = pygame.transform.smoothscale(self.logo_img, (new_w, new_h))
            except Exception:
                self.logo_scaled = None

    def mostrar_texto(self, texto, font, color, superficie, x, y):
        """Renderiza texto centrado en (x, y) y devuelve su rectángulo."""
        texto_objeto = font.render(texto, True, color)
        rectangulo_texto = texto_objeto.get_rect()
        rectangulo_texto.center = (x, y)
        superficie.blit(texto_objeto, rectangulo_texto)
        return rectangulo_texto

    def dibujar(self) -> None:
        """Dibuja el fondo del menú y el logo en una esquina."""
        # Fondo (ya escalado)
        if self.menu_bg_scaled is not None:
            self.ventana.blit(self.menu_bg_scaled, (0, 0))
        else:
            self.ventana.fill(self.NEGRO)

        # Logo en esquina inferior derecha ya escalado
        if self.logo_scaled is not None:
            padding = 10
            pos_x = self.ANCHO - self.logo_scaled.get_width() - padding
            pos_y = self.ALTO - self.logo_scaled.get_height() - padding
            self.ventana.blit(self.logo_scaled, (pos_x, pos_y))

    # Nota: no hacemos flip aquí; el present se hace al final del frame en run()

    def dibujar_boton(self, texto: str, x: int, y: int, ancho: int, alto: int, color_fondo: tuple | None = None) -> pygame.Rect:
        if color_fondo is None:
            color_fondo = (50, 200, 50)
        rect = pygame.Rect(x, y, ancho, alto)
        pygame.draw.rect(self.ventana, color_fondo, rect, border_radius=8)
        if self.fuente_item:
            self.mostrar_texto(texto, self.fuente_item, self.NEGRO, self.ventana, x + ancho / 2, y + alto / 2)
        return rect

    def _leer_nombres_existentes(self, archivo: str) -> set[str]:
        nombres: set[str] = set()
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea:
                        continue
                    sep = ',' if ',' in linea else (';' if ';' in linea else None)
                    partes = linea.split(sep) if sep else linea.split()
                    if len(partes) < 1:
                        continue
                    nombre = partes[0].strip().lower()
                    if nombre:
                        nombres.add(nombre)
        except FileNotFoundError:
            return set()
        except Exception:
            return nombres
        return nombres

    def solicitar_nombre(self, archivo_scores: str = "scores.txt") -> str | None:
        """Pantalla de entrada de nombre; valida no duplicado en archivo.
        Retorna el nombre válido o None si se cancela con ESC o cierre de ventana."""
        clock = pygame.time.Clock()
        nombre = ""
        mensaje_error = ""
        input_rect = pygame.Rect(self.ANCHO // 2 - 200, self.ALTO // 2 - 24, 400, 48)
        while True:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    elif event.key == pygame.K_BACKSPACE:
                        nombre = nombre[:-1]
                    elif event.key == pygame.K_RETURN:
                        n = nombre.strip()
                        if not n:
                            mensaje_error = "Ingresa un nombre"
                        else:
                            existentes = self._leer_nombres_existentes(archivo_scores)
                            if n.lower() in existentes:
                                mensaje_error = "Ese nombre ya existe"
                            else:
                                return n
                    else:
                        # Agregar caracteres de texto
                        ch = event.unicode
                        if ch and 32 <= ord(ch) < 127 and len(nombre) < 20:
                            nombre += ch

            # Dibujar fondo
            self.dibujar()
            # Caja y etiquetas
            self.mostrar_texto("Ingresa tu nombre de jugador", self.fuente_titulo, self.BLANCO, self.ventana, self.ANCHO/2, self.ALTO/2 - 80)
            pygame.draw.rect(self.ventana, self.BLANCO, input_rect, width=2, border_radius=6)
            # Texto dentro de input
            texto_input = (nombre + ("_" if (pygame.time.get_ticks() // 500) % 2 == 0 else "")) if self.fuente_input else nombre
            if self.fuente_input:
                self.mostrar_texto(texto_input, self.fuente_input, self.BLANCO, self.ventana, self.ANCHO/2, self.ALTO/2)
            # Error
            if mensaje_error and self.fuente_item:
                self.mostrar_texto(mensaje_error, self.fuente_item, self.ROJO, self.ventana, self.ANCHO/2, self.ALTO/2 + 70)
            pygame.display.flip()

    def run(self, archivo_scores: str = "scores.txt") -> str | None:
        """Muestra menú principal; devuelve nombre del jugador si elige Nuevo Juego, o None si cierra."""
        clock = pygame.time.Clock()
        while True:
            clock.tick(60)
            # Preparar botones antes de manejar eventos (evita acceso antes de creación)
            self.dibujar()
            if self.fuente_titulo:
                self.mostrar_texto("Space Invaders", self.fuente_titulo, self.BLANCO, self.ventana, self.ANCHO/2, 110)
            btn_w, btn_h = 280, 60
            nuevo_rect = self.dibujar_boton("Nuevo Juego", self.ANCHO//2 - btn_w//2, 220, btn_w, btn_h, (90, 200, 90))
            tabla_rect = self.dibujar_boton("Tabla de Puntajes", self.ANCHO//2 - btn_w//2, 300, btn_w, btn_h, (90, 150, 220))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = event.pos
                    if nuevo_rect.collidepoint(pos):
                        nombre = self.solicitar_nombre(archivo_scores)
                        if nombre:
                            return nombre
                    elif tabla_rect.collidepoint(pos):
                        # Mostrar tabla de puntajes; al cerrar vuelve al menú
                        MenuPuntajes().ejecutar(archivo_scores)
