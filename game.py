import os
import sys
import math
import wave
import struct
import pygame

from core.settings import WIDTH, HEIGHT, FPS, ASSETS_IMG_DIR, PROJECT_ROOT
from core.drawing import Drawing
from entities.ship import Ship
from entities.player import Player
from entities.enemy import Enemy
from entities.bullet import Bullet

class Game:
    def __init__(self, width: int = WIDTH, height: int = HEIGHT, fps: int = FPS,
                 lives: int = 3, nivel: int = 1, player_name: str | None = None) -> None:
        pygame.init()
        pygame.font.init()
        # Inicializar audio (ignorando errores si falla en WSL sin soporte)
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception as e:
            print(f"[Audio] Mixer no disponible: {e}")

        self.Screen_width = width
        self.screen_height = height
        self.Window = pygame.display.set_mode((self.Screen_width, self.screen_height))
        pygame.display.set_caption("Space Invaders - Game")

        self.FPS = fps
        self.clock = pygame.time.Clock()

        self.lives = lives
        self.Nivel = nivel
        self.bullets = 0
        self.Contador = 0
        self.score = 0
        self.count = 0  # contador para GAME OVER
        # Progreso de nivel y spawner (enemigos infinitos hasta cumplir objetivo)
        self.target_kills = 12  # Kills necesarios para terminar el nivel
        self.kills = 0
        self.max_enemies_on_screen = 6
        self.spawn_cooldown = 30
        self.spawn_counter = 0
        self.enemy_speed = 1.0
        self.player_name = player_name
        # Cargar top scores existentes (si el archivo está disponible)
        self.top_scores = self.leer_registro()

        self.Font = pygame.font.Font(None, 28)
        # aliases
        self.font = self.Font
        self.level = self.Nivel
        self.window = self.Window
        self.WIDTH = self.Screen_width
        self.HEIGTH = self.screen_height

        # bullet image for HUD: prefer images/ bullet_image.png then assets/images/bullet.png
        images_dir = os.path.join(PROJECT_ROOT, "images")
        bullet_candidates = [
            os.path.join(images_dir, "bullet_image.png"),
            os.path.join(ASSETS_IMG_DIR, "bullet.png"),
        ]
        self.bullet_img = None
        for bp in bullet_candidates:
            if os.path.exists(bp):
                self.bullet_img = pygame.image.load(bp).convert_alpha()
                break
        if self.bullet_img is None:
            self.bullet_img = pygame.Surface((16, 8), pygame.SRCALPHA)
            self.bullet_img.fill((255, 255, 0))

        # Instanciar jugador ahora que self.* está definido
        ship_candidates = [
            os.path.join(images_dir, "ship.png"),
            os.path.join(ASSETS_IMG_DIR, "ship.png"),
        ]
        bullet_candidates_player = [
            os.path.join(images_dir, "bullet_image.png"),
            os.path.join(ASSETS_IMG_DIR, "bullet.png"),
        ]
        ship_image = next((p for p in ship_candidates if os.path.exists(p)), None)
        bullet_image = next((p for p in bullet_candidates_player if os.path.exists(p)), None)
        start_x = (self.Screen_width // 2) - 20
        start_y = self.screen_height - 80
        # Instanciar jugador (Player) con velocidades en X/Y y salud inicial
        self.player = Player(start_x, start_y, x_speed=6, y_speed=6, health=100)
        # Llenar arsenal de balas al inicio del juego
        self.player.fired_bullets = []
        self.player.bullets = []
        for _ in range(self.player.max_amount_bullets):
            img = self.player.bullet_img or pygame.Surface((8, 16), pygame.SRCALPHA)
            if self.player.bullet_img is None:
                img.fill((255, 255, 0))
            b = Bullet(self.player.x, self.player.y, img, speed=self.player.bullet_speed)
            self.player.bullets.append(b)
        self.player.creation_cooldown_counter = 0
        self.player.bullet_cooldown_counter = 0
        # Instanciar enemigos iniciales
        self.enemies = Enemy(speed=int(max(1, self.enemy_speed))).create(6)
        # Reproducir sonido inicial
        self.play_start_sound()
        # Iniciar música de fondo (si existe)
        self.play_music()
        # Cargar background usando Drawing helper (reutiliza lógica existente)
        self._drawing = Drawing(self.Window)
        self.background = self._drawing.background
        # Preparar umbral de récord del jugador para sonido de "ganar"
        self._played_highscore_sound = False
        self.player_prev_best = self._leer_puntaje_jugador(self.player_name)
        # Flag para guardar puntaje solo una vez al finalizar
        self._score_saved = False

    def run(self) -> None:
        running = True
        while running:
            self.clock.tick(self.FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Movimiento y disparo del jugador usando su propia lógica interna
            self.player.move(width=self.Screen_width, height=self.screen_height)
            self.player.create_bullets()
            self.player.cooldown()
            self.player.fire(self.Window)
            # Actualizar movimiento de balas del jugador
            self.player.update_bullets()

            self.Contador += 1
            # Mover enemigos (descenso simple)
            for e in self.enemies:
                e.update()

            # Si algún enemigo toca el fondo, perder vida y reiniciar
            if self._enemy_reached_bottom():
                self.lives -= 1
                if self.lives <= 0:
                    pass
                else:
                    self._restart_level()

            # Colisión jugador-enemigo -> perder vida y reiniciar nivel
            if self._player_hit_by_enemy():
                self.lives -= 1
                if self.lives <= 0:
                    # Game over se maneja abajo pero rompemos flujo de reinicio
                    pass
                else:
                    self._restart_level()

            # Colisiones: balas del jugador contra enemigos
            self._handle_collisions()

            # Spawner de enemigos continuo
            self._spawn_enemies()

            self.update_HUD()

            # Progresión de nivel (subir de nivel cuando cumples objetivo y limpias la pantalla)
            self._progress_level()

            # Verificar salida / game over
            if self.over() or self.escape():
                running = False

        pygame.quit()
        sys.exit()

    def escape(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
        return False

    def over(self) -> bool:
        if self.lives <= 0:
            # Guardar puntaje del jugador una sola vez cuando termina la partida
            if not self._score_saved and self.player_name:
                try:
                    self.guardar_puntaje(self.player_name, self.score)
                    # refrescar top en memoria
                    self.top_scores = self.leer_registro()
                except Exception as e:
                    print(f"[Scores] No se pudo guardar el puntaje: {e}")
                finally:
                    self._score_saved = True
            if not hasattr(self, "count") or self.count == 0:
                self.count = 0
            while self.count < self.FPS * 3:
                self.clock.tick(self.FPS)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return True
                self.Window.fill((0, 0, 0))
                surf = self.Font.render("GAME OVER", True, (255, 255, 255))
                x = (self.Screen_width - surf.get_width()) // 2
                y = (self.screen_height - surf.get_height()) // 2
                self.Window.blit(surf, (x, y))
                pygame.display.update()
                self.count += 1
            return True
        return False

    def reload_bullet(self, bullet: int) -> None:
        self.bullets = int(bullet)

    # -------- Puntajes util ---------
    def leer_registro(self, archivo: str = "scores.txt") -> list[tuple[str, int]]:
        """Lee registros de puntajes y devuelve el top 5 ordenado por puntuación descendente.
        Formato esperado por línea: nombre,puntaje
        Ignora líneas vacías o formatos inválidos.
        """
        registros: list[tuple[str, int]] = []
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea:
                        continue
                    partes = linea.split(',')
                    if len(partes) < 2:
                        continue
                    nombre = partes[0].strip()
                    try:
                        puntaje = int(partes[1])
                    except ValueError:
                        continue
                    registros.append((nombre, puntaje))
        except FileNotFoundError:
            # Archivo inexistente en primer arranque
            return []
        except Exception as e:
            print(f"[Scores] Error leyendo '{archivo}': {e}")
        registros.sort(key=lambda t: t[1], reverse=True)
        return registros[:5]

    def _leer_puntaje_jugador(self, nombre: str, archivo: str = "scores.txt") -> int:
        """Obtiene el puntaje previo guardado para un nombre (0 si no existe)."""
        if not nombre:
            return 0
        try:
            path = archivo if os.path.isabs(archivo) else os.path.join(PROJECT_ROOT, archivo)
            with open(path, 'r', encoding='utf-8') as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea:
                        continue
                    partes = linea.split(',')
                    if len(partes) < 2:
                        continue
                    if partes[0].strip().lower() == nombre.lower():
                        try:
                            return int(partes[1])
                        except ValueError:
                            return 0
        except FileNotFoundError:
            return 0
        except Exception:
            return 0
        return 0

    def play_win_sound(self) -> None:
        if not pygame.mixer.get_init():
            return
        try:
            # Cachear el sonido para no recargarlo
            if not hasattr(self, '_win_sound') or self._win_sound is None:
                candidates = [
                    os.path.join(PROJECT_ROOT, 'assets', 'sounds', 'ganar.mp3'),
                    r"C:\\Users\\danie\\Desktop\\escuela\\space_ivaders\\assets\\sounds\\ganar.mp3",
                ]
                chosen = next((p for p in candidates if os.path.exists(p)), None)
                if not chosen:
                    return
                self._win_sound = pygame.mixer.Sound(chosen)
            self._win_sound.play()
        except Exception:
            pass

    def guardar_puntaje(self, nombre: str, puntaje: int, archivo: str = "scores.txt") -> None:
        """Guarda/actualiza el puntaje del jugador en el archivo.
        - Si el jugador existe, se guarda el mayor entre el previo y el nuevo.
        - Si no existe, se agrega la nueva entrada.
        """
        if not nombre:
            return
        path = archivo if os.path.isabs(archivo) else os.path.join(PROJECT_ROOT, archivo)
        registros: dict[str, int] = {}
        # Leer existentes
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea:
                        continue
                    partes = linea.split(',')
                    if len(partes) < 2:
                        continue
                    n = partes[0].strip()
                    try:
                        p = int(partes[1])
                    except ValueError:
                        continue
                    registros[n] = max(registros.get(n, 0), p)
        except FileNotFoundError:
            # Crear carpeta si fuese necesario
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
            except Exception:
                pass
        # Actualizar o agregar
        prev = registros.get(nombre, 0)
        registros[nombre] = max(prev, puntaje)
        # Escribir de vuelta ordenado desc
        ordenados = sorted(registros.items(), key=lambda t: t[1], reverse=True)
        with open(path, 'w', encoding='utf-8') as f:
            for n, p in ordenados:
                f.write(f"{n},{p}\n")

    def leer_registro(self, archivo: str = "scores.txt") -> list[tuple[str, int]]:
        """Lee registros de puntajes y devuelve el top 5 ordenado por puntuación descendente.
        Formato esperado por línea: nombre,puntaje
        Ignora líneas vacías o formatos inválidos.
        """
        registros: list[tuple[str, int]] = []
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea:
                        continue
                    partes = linea.split(',')
                    if len(partes) < 2:
                        continue
                    nombre = partes[0].strip()
                    try:
                        puntaje = int(partes[1])
                    except ValueError:
                        continue
                    registros.append((nombre, puntaje))
        except FileNotFoundError:
            # Archivo inexistente en primer arranque; retornamos lista vacía
            return []
        except Exception as e:
            print(f"[Scores] Error leyendo '{archivo}': {e}")
        registros.sort(key=lambda t: t[1], reverse=True)
        return registros[:5]

    # -------- Audio util ---------
    def _ensure_start_wav(self, path: str) -> None:
        """Genera un WAV corto (senoidal) si no existe el archivo."""
        if os.path.exists(path):
            return
        try:
            sample_rate = 22050
            duration = 0.35  # segundos
            freq = 440.0
            amplitude = 120  # 8-bit rango 0-255
            n_samples = int(sample_rate * duration)
            with wave.open(path, 'w') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(1)  # 8-bit
                wf.setframerate(sample_rate)
                for i in range(n_samples):
                    t = i / sample_rate
                    val = int(128 + amplitude * math.sin(2 * math.pi * freq * t))
                    wf.writeframes(struct.pack('<B', val))
        except Exception as e:
            print(f"No se pudo generar WAV: {e}")

    def play_start_sound(self) -> None:
        if not pygame.mixer.get_init():
            return
        sounds_dir = os.path.join(PROJECT_ROOT, 'assets', 'sounds')
        os.makedirs(sounds_dir, exist_ok=True)
        start_path = os.path.join(sounds_dir, 'start.wav')
        self._ensure_start_wav(start_path)
        try:
            snd = pygame.mixer.Sound(start_path)
            snd.play()
        except Exception as e:
            print(f"No se pudo reproducir sonido de inicio: {e}")

    def play_music(self) -> None:
        """Carga y reproduce en loop la música de fondo si el mixer está disponible."""
        if not pygame.mixer.get_init():
            return
        # Ruta proporcionada por el usuario
        music_path = os.path.join(PROJECT_ROOT, 'music.mp3')
        # Si el usuario tiene una ruta absoluta distinta, también la intentamos
        alt_absolute = r"C:\\Users\\danie\\Desktop\\escuela\\space_ivaders\\music.mp3"
        chosen = music_path if os.path.exists(music_path) else (alt_absolute if os.path.exists(alt_absolute) else None)
        if not chosen:
            return
        try:
            pygame.mixer.music.load(chosen)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)  # loop infinito
        except Exception as e:
            print(f"No se pudo reproducir música: {e}")

    def draw_HUD(self) -> None:
        offset = 0
        lives_label = self.font.render(f"Lives: {self.lives}", True, (255, 255, 255))
        level_label = self.font.render(f"Level: {self.level}", True, (255, 255, 255))
        score_label = self.font.render(f"Score: {self.score}", True, (255, 255, 0))
        kills_label = self.font.render(f"Kills: {self.kills}/{self.target_kills}", True, (0, 200, 255))
        self.window.blit(lives_label, (10, 10))
        self.window.blit(level_label, (self.WIDTH - level_label.get_width() - 10, 10))
        self.window.blit(score_label, (10, 34))
        self.window.blit(kills_label, (10, 58))
        # Mostrar balas disponibles del jugador (en la "recámara")
        ready_bullets = len(getattr(self.player, "bullets", []))
        for _ in range(ready_bullets):
            offset += self.bullet_img.get_width()
            self.window.blit(self.bullet_img, (self.WIDTH - offset, self.HEIGTH - 50))

    def update_HUD(self) -> None:
        # Dibujar fondo primero
        if self.background:
            if self.background.get_size() != self.Window.get_size():
                bg_scaled = pygame.transform.scale(self.background, self.Window.get_size())
                self.Window.blit(bg_scaled, (0, 0))
            else:
                self.Window.blit(self.background, (0, 0))
        else:
            self.Window.fill((0, 0, 0))
        # Dibujar enemigos
        for e in self.enemies:
            e.draw(self.Window)
        # Dibujar balas disparadas del jugador
        for b in getattr(self.player, 'fired_bullets', []):
            b.draw(self.Window)
        # Dibujar jugador
        self.player.draw(self.Window)
        self.draw_HUD()
        pygame.display.update()

    # -------- Lógica de colisiones simple ---------
    def _handle_collisions(self):
        if not self.player.fired_bullets or not self.enemies:
            return
        # Revisar cada bala contra cada enemigo (simple, pequeño número)
        remaining_enemies = []
        level_target_reached = False
        for enemy in self.enemies:
            if level_target_reached:
                break  # ya alcanzamos objetivo, ignorar enemigos restantes
            hit = False
            for bullet in list(self.player.fired_bullets):
                if bullet.collision(enemy):
                    # Eliminar bala y marcar impacto
                    if bullet in self.player.fired_bullets:
                        self.player.fired_bullets.remove(bullet)
                    hit = True
                    self.score += 100
                    # Si supera su récord previo, reproducir sonido (una sola vez)
                    if (not self._played_highscore_sound) and self.player_name and (self.score > self.player_prev_best):
                        self.play_win_sound()
                        self._played_highscore_sound = True
                    if self.kills < self.target_kills:
                        self.kills += 1
                    # Si alcanzamos exactamente el objetivo, no obligar a eliminar el resto manualmente
                    if self.kills >= self.target_kills:
                        level_target_reached = True
                    break
            if not hit:
                remaining_enemies.append(enemy)
        # Si se alcanzó el objetivo, limpiar completamente la lista para avanzar de nivel sin kills extra
        self.enemies = [] if level_target_reached else remaining_enemies

    def _progress_level(self) -> None:
        """Si cumpliste objetivo (independiente de enemigos restantes), sube de nivel y crea nueva oleada."""
        if self.kills < self.target_kills:
            return
        # Sonido al ganar el nivel
        self.play_win_sound()
        # Mensaje breve de nivel completado
        frames = 0
        msg = self.Font.render("LEVEL COMPLETE", True, (0, 255, 0))
        while frames < self.FPS:  # ~1s
            self.clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
            self.Window.fill((0, 0, 0))
            self.Window.blit(msg, ((self.Screen_width - msg.get_width()) // 2,
                                    (self.screen_height - msg.get_height()) // 2))
            pygame.display.update()
            frames += 1
        # Subir nivel y ajustar parámetros
        self.level += 1
        self.Nivel = self.level
        self.enemy_speed *= 1.15
        # Aumentar objetivo próximo nivel
        self.target_kills = int(max(self.target_kills + 4, self.target_kills * 1.25))
        self.kills = 0
        # Aumentar arsenal de balas en +1 por nivel
        if hasattr(self.player, "max_amount_bullets"):
            self.player.max_amount_bullets += 1
        # Refill de balas del jugador al máximo según el nuevo nivel
        self.player.fired_bullets = []
        self.player.bullets = []
        for _ in range(self.player.max_amount_bullets):
            img = self.player.bullet_img or pygame.Surface((8, 16), pygame.SRCALPHA)
            if self.player.bullet_img is None:
                img.fill((255, 255, 0))
            b = Bullet(self.player.x, self.player.y, img, speed=self.player.bullet_speed)
            self.player.bullets.append(b)

        # Nueva oleada inicial
        start_count = min(6 + self.level, 12)
        self.enemies = Enemy(speed=int(max(1, round(self.enemy_speed)))).create(start_count)
    def _spawn_enemies(self) -> None:
        # Deja de spawnear solo si ya alcanzó los kills objetivos
        if self.kills >= self.target_kills:
            return
        if len(self.enemies) >= self.max_enemies_on_screen:
            return
        if self.spawn_counter > 0:
            self.spawn_counter -= 1
            return
        new_enemy = Enemy(speed=int(max(1, round(self.enemy_speed)))).create(1)[0]
        self.enemies.append(new_enemy)
        self.spawn_counter = self.spawn_cooldown

    def _enemy_reached_bottom(self) -> bool:
        """Retorna True si algún enemigo tocó el borde inferior; elimina el enemigo."""
        hit = False
        remaining = []
        for e in self.enemies:
            if e.rect.bottom >= self.screen_height:
                hit = True
                continue
            remaining.append(e)
        if hit:
            self.enemies = remaining
        return hit

    def _player_hit_by_enemy(self) -> bool:
        """Detecta si algún enemigo colisiona con el jugador."""
        player_mask = getattr(self.player, 'mask', None)
        if not player_mask:
            # Fallback rect
            for e in self.enemies:
                if e.rect.colliderect(self.player.rect):
                    return True
            return False
        for e in self.enemies:
            offset = (int(e.rect.x - self.player.rect.x), int(e.rect.y - self.player.rect.y))
            if player_mask.overlap(e.mask, offset):
                return True
        return False

    def _restart_level(self) -> None:
        """Reinicia el estado del nivel manteniendo score y vidas restantes."""
        self.kills = 0
        self.enemies = Enemy(speed=int(max(1, round(self.enemy_speed)))).create(6)
        self.spawn_counter = 0
        # Reposicionar jugador al centro inferior
        self.player.x = (self.Screen_width // 2) - (self.player.ship_img.get_width() // 2)
        self.player.y = self.screen_height - 80
        self.player.rect.topleft = (int(self.player.x), int(self.player.y))
        # Limpiar balas
        self.player.bullets.clear()
        self.player.fired_bullets.clear()
        # Resetear cooldowns de creación/disparo
        self.player.creation_cooldown_counter = 0
        self.player.bullet_cooldown_counter = 0
