import pygame
import sys
import random
from dataclasses import dataclass

# ----------------------------- CONFIGURACIÓN ------------------------------
WIDTH, HEIGHT = 432, 768
FPS = 60

GRAVITY = 1800.0
JUMP_VELOCITY = -550.0
MAX_FALL_SPEED = 1100.0

GROUND_HEIGHT = 100
GROUND_SPEED = 180.0

PIPE_SPEED = 180.0
PIPE_WIDTH = 80
PIPE_GAP = 220
PIPE_SPAWN_TIME = 1.6

WHITE = (245, 245, 245)
BLACK = (5, 5, 5)
BLUE = (66, 135, 245)
GREEN = (60, 200, 120)
GRASS = (40, 170, 90)
DARK = (30, 30, 30)

MENU, PLAYING, GAME_OVER = "MENU", "PLAYING", "GAME_OVER"

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird — Starter (Andrés & David)")
clock = pygame.time.Clock()

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

# --------------------------- CLASE PIPE COMPLETA ---------------------------
class Pipe:
    def __init__(self, x: float, gap_y: float):
        self.x = x
        self.gap_y = gap_y
        self.passed = False

    def update(self, dt: float):
        self.x -= PIPE_SPEED * dt

    def draw(self, surf: pygame.Surface):
        top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.gap_y - PIPE_GAP / 2)
        bottom_rect = pygame.Rect(self.x, self.gap_y + PIPE_GAP / 2, PIPE_WIDTH, HEIGHT - GROUND_HEIGHT - (self.gap_y + PIPE_GAP / 2))
        pygame.draw.rect(surf, GREEN, top_rect)
        pygame.draw.rect(surf, GREEN, bottom_rect)

    def rects(self):
        top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.gap_y - PIPE_GAP / 2)
        bottom_rect = pygame.Rect(self.x, self.gap_y + PIPE_GAP / 2, PIPE_WIDTH, HEIGHT - GROUND_HEIGHT - (self.gap_y + PIPE_GAP / 2))
        return [top_rect, bottom_rect]

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
    gap_y = random.randint(int(HEIGHT * 0.2), int(HEIGHT * 0.6))
    pipe = Pipe(WIDTH, gap_y)
    pipes.append(pipe)

def update_pipes(pipes: list, dt: float):
    for p in pipes:
        p.update(dt)
    pipes[:] = [p for p in pipes if p.x + PIPE_WIDTH > 0]

def check_collisions(bird: Bird, pipes: list, ground: Ground) -> bool:
    # Bird rect
    bird_rect = pygame.Rect(int(bird.x - bird.radius), int(bird.y - bird.radius),
                            bird.radius * 2, bird.radius * 2)
    # Suelo o techo
    if bird.y - bird.radius < 0 or bird.y + bird.radius > ground.y:
        return True
    # Tubos
    for p in pipes:
        for r in p.rects():
            if bird_rect.colliderect(r):
                return True
    return False

def handle_scoring(bird: Bird, pipes: list, current_score: int) -> int:
    for p in pipes:
        if not p.passed and p.x + PIPE_WIDTH < bird.x:
            p.passed = True
            current_score += 1
    return current_score

def maybe_increase_difficulty(elapsed_time: float):
    global PIPE_SPEED, PIPE_GAP
    PIPE_SPEED = 180 + min(100, elapsed_time * 5)
    PIPE_GAP = max(150, 220 - elapsed_time * 3)

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
    try:
        with open("highscore.txt", "r") as f:
            return int(f.read().strip())
    except:
        return 0

def save_highscore(best: int):
    try:
        with open("highscore.txt", "w") as f:
            f.write(str(best))
    except:
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
