import pygame
import random
import math
import sys

# ============================================================
# NEON BREAKER DELUXE
# Controls: A/D or arrows = move, SPACE = launch/pause,
#           P = pause, R = restart after game over, ESC = quit
# ============================================================

pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    pass

WIDTH, HEIGHT = 1000, 700
FPS = 60
PLAY_TOP = 82
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ROYAL SUNSET - BLOCK BREAKER")
clock = pygame.time.Clock()
# Palette - ROYAL SUNSET
BG = (11, 14, 32)
WHITE = (255, 248, 235)
CYAN = (75, 235, 210)       # turquoise
BLUE = (95, 145, 255)       # royal blue
PURPLE = (174, 130, 255)    # lavender
PINK = (255, 112, 145)      # coral pink
GREEN = (145, 225, 165)     # mint
YELLOW = (255, 205, 105)     # warm gold
ORANGE = (255, 145, 100)    # sunset orange
MUTED = (145, 155, 185)

FONT = pygame.font.SysFont("arial", 20, bold=True)
SMALL = pygame.font.SysFont("arial", 14, bold=True)
MEDIUM = pygame.font.SysFont("arial", 30, bold=True)
LARGE = pygame.font.SysFont("arial", 66, bold=True)
TITLE = pygame.font.SysFont("arial", 58, bold=True)

# Optional synthesized sound effects. Game remains playable without audio.
def play_tone(frequency=500, duration=70, volume=0.12):
    if not pygame.mixer.get_init():
        return
    try:
        import array
        sample_rate = 22050
        count = int(sample_rate * duration / 1000)
        wave = array.array("h")
        for i in range(count):
            envelope = 1.0 - i / max(1, count)
            value = int(32767 * volume * envelope *
                        math.sin(2 * math.pi * frequency * i / sample_rate))
            wave.append(value)
        sound = pygame.mixer.Sound(buffer=wave.tobytes())
        sound.play()
    except (pygame.error, ValueError):
        pass


def text(surface, value, font, color, center, shadow=True):
    image = font.render(str(value), True, color)
    rect = image.get_rect(center=center)
    if shadow:
        shade = font.render(str(value), True, (15, 35, 65))
        surface.blit(shade, rect.move(2, 3))
    surface.blit(image, rect)


def rounded_glow(surface, rect, color, radius=9, glow=18):
    # A few translucent outlines create a neon-like glow.
    for width, alpha in ((glow, 18), (glow // 2, 28), (3, 65)):
        layer = pygame.Surface((rect.width + glow * 2, rect.height + glow * 2),
                               pygame.SRCALPHA)
        expanded = pygame.Rect(glow, glow, rect.width, rect.height)
        pygame.draw.rect(layer, (*color, alpha), expanded,
                         width=max(1, width), border_radius=radius + glow // 2)
        surface.blit(layer, (rect.x - glow, rect.y - glow))
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    inner = rect.inflate(-4, -4)
    if inner.width > 0 and inner.height > 0:
        pygame.draw.rect(surface, WHITE, inner, width=1, border_radius=max(2, radius - 2))


class Particle:
    def __init__(self, x, y, color, force=4):
        angle = random.random() * math.tau
        speed = random.uniform(1, force)
        self.x, self.y = float(x), float(y)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = self.max_life = random.randint(22, 42)
        self.radius = random.randint(2, 4)
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.985
        self.vy *= 0.985
        self.vy += 0.025
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            r = max(1, int(self.radius * self.life / self.max_life))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), r)


class FloatingLabel:
    def __init__(self, x, y, message, color):
        self.x, self.y = x, y
        self.message, self.color = message, color
        self.life = 48

    def update(self):
        self.y -= 0.7
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            image = SMALL.render(self.message, True, self.color)
            image.set_alpha(min(255, self.life * 6))
            surface.blit(image, image.get_rect(center=(int(self.x), int(self.y))))


class Paddle:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT - 75, 150, 18)
        self.speed = 9
        self.wide_timer = 0
        self.sticky_timer = 0

    def update(self, keys):
        direction = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(
            keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.rect.x += direction * self.speed
        self.rect.clamp_ip(pygame.Rect(12, PLAY_TOP, WIDTH - 24, HEIGHT - PLAY_TOP))
        if self.wide_timer > 0:
            self.wide_timer -= 1
        if self.sticky_timer > 0:
            self.sticky_timer -= 1

    def draw(self, surface):
        color = PURPLE if self.sticky_timer else CYAN
        r = self.rect
        # Wing-shaped paddle with a raised central cockpit.
        points = [
            (r.left, r.bottom - 2), (r.left + 13, r.top + 5),
            (r.centerx - 22, r.top + 2), (r.centerx, r.top - 5),
            (r.centerx + 22, r.top + 2), (r.right - 13, r.top + 5),
            (r.right, r.bottom - 2), (r.right - 18, r.bottom + 2),
            (r.left + 18, r.bottom + 2)
        ]
        glow_rect = r.inflate(28, 22)
        glow_layer = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
        local = [(x - glow_rect.x, y - glow_rect.y) for x, y in points]
        pygame.draw.polygon(glow_layer, (*color, 38), local)
        surface.blit(glow_layer, glow_rect.topleft)
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, WHITE, points, 2)
        pygame.draw.line(surface, WHITE,
                         (r.centerx - 17, r.top + 5),
                         (r.centerx + 17, r.top + 5), 2)
        pygame.draw.circle(surface, YELLOW, (r.centerx, r.top + 8), 3)


