# Flappy Bird — Starter (50% hecho) 
# Objetivo: Dejar un proyecto que CORRE desde ya (física básica del ave,
# bucle principal, escena, HUD y suelo desplazándose) y el 50% restante
# lo implementan USTEDES con tareas asignadas y detalladas en comentarios.
#
# Requisitos: Python 3.9+ y pygame
#   pip install pygame
# Ejecución:
#   python flappy_starter.py
#
# -------------------------------------------------------------------------
# DISTRIBUCIÓN DE TAREAS
# -------------------------------------------------------------------------
# ANDRÉS — SISTEMA DE TUBOS + COLISIONES (núcleo jugable)
#  1) Implementar la clase Pipe (arriba/abajo) con hueco central aleatorio.
#  2) Spawning: crear tuberías cada PIPE_SPAWN_TIME segundos.
#  3) Movimiento: desplazar tuberías a la izquierda a velocidad PIPE_SPEED.
#  4) Reciclaje/limpieza: eliminar tuberías fuera de pantalla.
#  5) Colisiones: detectar choque del pájaro con tubos o con el suelo/techo.
#  6) Señalar GAME_OVER cuando ocurra colisión.
#
# DAVID — PUNTUACIÓN + DIFICULTAD + AUDIO/EXTRAS (pulido que impresiona)
#  1) Puntuación: sumar 1 punto cuando el pájaro pase un par de tubos.
#  2) Mejor puntuación (high score): guardar en archivo "highscore.txt".
#  3) Curva de dificultad progresiva: aumentar PIPE_SPEED o reducir GAP con el tiempo.
#  4) Sonidos: salto, punto, choque (usar pygame.mixer y archivos .wav libres).
#  5) Menú de inicio y reinicio bonito (texto, instrucciones, animación flotante).
#  6) Partículas o ligera rotación del pájaro al saltar (extra para lucirse).
#
# CONSEJO: trabajen con ramas distintas (git) o por secciones, probando
#          cada cambio de forma incremental. Comenten TODO lo que hagan.
# -------------------------------------------------------------------------

import pygame
import sys
import random
from dataclasses import dataclass

# ----------------------------- CONFIGURACIÓN ------------------------------
WIDTH, HEIGHT = 432, 768
FPS = 60

GRAVITY = 1800.0          # px/s^2
JUMP_VELOCITY = -550.0    # px/s (hacia arriba es negativo)
MAX_FALL_SPEED = 1100.0

GROUND_HEIGHT = 100
GROUND_SPEED = 180.0       # px/s

# --- Tuberías (PARCIAL: deja los valores listos para Andrés/David) ---
PIPE_SPEED = 180.0         # px/s (inicial)  ← DAVID: puede incrementarlo con el tiempo
PIPE_WIDTH = 80
PIPE_GAP = 220             # px            ← DAVID: puede reducirlo progresivamente
PIPE_SPAWN_TIME = 1.6      # s entre spawns

# Colores simples (para no depender de assets)
WHITE = (245, 245, 245)
BLACK = (5, 5, 5)
BLUE = (66, 135, 245)
GREEN = (60, 200, 120)
GRASS = (40, 170, 90)
DARK = (30, 30, 30)

# Estados del juego
MENU, PLAYING, GAME_OVER = "MENU", "PLAYING", "GAME_OVER"

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird — Starter (Andrés & David)")
clock = pygame.time.Clock()

# Fuente
FONT_BIG = pygame.font.SysFont("arial", 64, bold=True)
FONT_MED = pygame.font.SysFont("arial", 32, bold=True)
FONT_SMALL = pygame.font.SysFont("arial", 20)

# ------------------------------- ENTIDADES --------------------------------
@dataclass
class Bird:
    x: float
    y: float
    vy: float = 0.0
    radius: int = 20

    def jump(self):
        self.vy = JUMP_VELOCITY

    def update(self, dt: float):
        self.vy += GRAVITY * dt
        if self.vy > MAX_FALL_SPEED:
            self.vy = MAX_FALL_SPEED
        self.y += self.vy * dt

    def draw(self, surf: pygame.Surface):
        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surf, BLACK, (int(self.x + self.radius * 0.3), int(self.y - self.radius * 0.3)), 4)
        pico = [
            (int(self.x + self.radius), int(self.y)),
            (int(self.x + self.radius + 10), int(self.y - 6)),
            (int(self.x + self.radius + 10), int(self.y + 6)),
        ]
        pygame.draw.polygon(surf, (255, 200, 80), pico)

class Ground:
    def __init__(self):
        self.y = HEIGHT - GROUND_HEIGHT
        self.x1 = 0
        self.x2 = WIDTH

    def update(self, dt: float):
        self.x1 -= GROUND_SPEED * dt
        self.x2 -= GROUND_SPEED * dt
        if self.x1 + WIDTH <= 0:
            self.x1 = self.x2 + WIDTH
        if self.x2 + WIDTH <= 0:
            self.x2 = self.x1 + WIDTH

    def draw(self, surf: pygame.Surface):
        pygame.draw.rect(surf, GRASS, (self.x1, self.y, WIDTH, GROUND_HEIGHT))
        pygame.draw.rect(surf, GRASS, (self.x2, self.y, WIDTH, GROUND_HEIGHT))
        pygame.draw.rect(surf, (30, 120, 70), (self.x1, self.y - 8, WIDTH, 8))
        pygame.draw.rect(surf, (30, 120, 70), (self.x2, self.y - 8, WIDTH, 8))

# -------------------------- PLACEHOLDERS / TODOs ---------------------------
class Pipe:  # ← ANDRÉS: completar
    """
    Representa un par de tuberías (arriba y abajo) con un hueco central.
    TODO (ANDRÉS):
      - __init__(self, x, gap_y): guardar x inicial y posición vertical del hueco.
      - Alturas: la tubería de arriba va de 0 a (gap_y - PIPE_GAP/2);
                 la de abajo va de (gap_y + PIPE_GAP/2) hasta el suelo.
      - update(dt): mover a la izquierda con PIPE_SPEED.
      - draw(surf): dibujar los rectángulos de ambas tuberías.
      - rects(): devolver una lista de pygame.Rect para colisiones (arriba y abajo).
    """
    def __init__(self, x: float, gap_y: float):
        self.x = x
        self.gap_y = gap_y
        self.passed = False  # DAVID la usa para puntaje

    def update(self, dt: float):
        pass

    def draw(self, surf: pygame.Surface):
        pass

    def rects(self):
        return []

# ------------------------------- UTILIDADES --------------------------------
def draw_background(surf: pygame.Surface):
    surf.fill(BLUE)
    for i in range(6):
        base_x = i * 90 - 40
        pygame.draw.polygon(
            surf, (90, 155, 240),
            [(base_x, HEIGHT - GROUND_HEIGHT),
             (base_x + 60, HEIGHT - GROUND_HEIGHT - 140),
             (base_x + 120, HEIGHT - GROUND_HEIGHT)]
        )

def clamp(val, lo, hi):
    return max(lo, min(val, hi))

# ------------------------------- JUEGO -------------------------------------
def reset_game():
    bird = Bird(x=WIDTH * 0.25, y=HEIGHT * 0.4)
    ground = Ground()
    pipes = []
    score = 0
    time_since_spawn = 0.0
    return bird, ground, pipes, score, time_since_spawn

def spawn_pipe(pipes: list):
    """Spawn de tubería con hueco aleatorio. (TODO ANDRÉS)"""
    pass

def update_pipes(pipes: list, dt: float):
    """Actualiza y limpia tuberías. (TODO ANDRÉS)"""
    pass

def check_collisions(bird: Bird, pipes: list, ground: Ground) -> bool:
    """Devuelve True si hay colisión. (TODO ANDRÉS)"""
    return False

def handle_scoring(bird: Bird, pipes: list, current_score: int) -> int:
    """Puntuación (TODO DAVID)."""
    return current_score

def maybe_increase_difficulty(elapsed_time: float):
    """Curva de dificultad. (TODO DAVID)"""
    pass

def draw_hud(state: str, score: int, highscore: int):
    if state == MENU:
        title = FONT_BIG.render("FLAPPY STARTER", True, WHITE)
        sub = FONT_MED.render("Presiona ESPACIO para empezar", True, WHITE)
        tips = FONT_SMALL.render("Andrés: tubos/colisiones  |  David: score/menú/audio", True, WHITE)
        screen.blit(title, (WIDTH/2 - title.get_width()/2, HEIGHT*0.22))
        screen.blit(sub, (WIDTH/2 - sub.get_width()/2, HEIGHT*0.22 + 90))
        screen.blit(tips, (WIDTH/2 - tips.get_width()/2, HEIGHT*0.22 + 140))
    elif state == PLAYING:
        s = FONT_MED.render(f"Score: {score}", True, WHITE)
        screen.blit(s, (16, 16))
    elif state == GAME_OVER:
        over = FONT_BIG.render("GAME OVER", True, WHITE)
        s = FONT_MED.render(f"Score: {score}  |  Best: {highscore}", True, WHITE)
        retry = FONT_SMALL.render("ESPACIO = reiniciar  |  ESC = menú", True, WHITE)
        screen.blit(over, (WIDTH/2 - over.get_width()/2, HEIGHT*0.22))
        screen.blit(s, (WIDTH/2 - s.get_width()/2, HEIGHT*0.22 + 90))
        screen.blit(retry, (WIDTH/2 - retry.get_width()/2, HEIGHT*0.22 + 140))

def load_highscore() -> int:
    return 0

def save_highscore(best: int):
    pass

def main():
    state = MENU
    bird, ground, pipes, score, time_since_spawn = reset_game()
    highscore = load_highscore()
    elapsed = 0.0

    while True:
        dt = clock.tick(FPS) / 1000.0
        elapsed += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if state == MENU:
                    if event.key == pygame.K_SPACE:
                        state = PLAYING
                        bird, ground, pipes, score, time_since_spawn = reset_game()
                elif state == PLAYING:
                    if event.key == pygame.K_SPACE:
                        bird.jump()
                elif state == GAME_OVER:
                    if event.key == pygame.K_SPACE:
                        state = PLAYING
                        bird, ground, pipes, score, time_since_spawn = reset_game()
                    if event.key == pygame.K_ESCAPE:
                        state = MENU

        if state == PLAYING:
            bird.update(dt)
            ground.update(dt)

            time_since_spawn += dt
            if time_since_spawn >= PIPE_SPAWN_TIME:
                time_since_spawn = 0.0
                spawn_pipe(pipes)

            update_pipes(pipes, dt)

            if check_collisions(bird, pipes, ground):
                state = GAME_OVER
                highscore = max(highscore, score)
                save_highscore(highscore)

            score = handle_scoring(bird, pipes, score)
            maybe_increase_difficulty(elapsed)

        draw_background(screen)
        for p in pipes:
            p.draw(screen)
        bird.draw(screen)
        ground.draw(screen)
        draw_hud(state, score, highscore)
        pygame.display.flip()

if __name__ == "__main__":
    main()
