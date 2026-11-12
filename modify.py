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


class Ball:
    def __init__(self, x, y, vx=None, vy=-6.0):
        self.x, self.y = float(x), float(y)
        self.radius = 9
        self.vx = random.choice((-4.5, 4.5)) if vx is None else vx
        self.vy = vy
        self.trail = []
        self.stuck = True

    def rect(self):
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius),
                           self.radius * 2, self.radius * 2)

    def launch(self):
        if self.stuck:
            self.stuck = False
            self.vx = random.choice((-4.8, 4.8))
            self.vy = -6.0

    def update(self, paddle, bricks, particles, labels, game):
        if self.stuck:
            self.x = paddle.rect.centerx
            self.y = paddle.rect.top - self.radius - 2
            return True

        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 9:
            self.trail.pop(0)

        old = self.rect()
        self.x += self.vx
        self.y += self.vy

        if self.x <= self.radius + 8:
            self.x = self.radius + 8
            self.vx = abs(self.vx)
            play_tone(260, 35, 0.05)
        elif self.x >= WIDTH - self.radius - 8:
            self.x = WIDTH - self.radius - 8
            self.vx = -abs(self.vx)
            play_tone(260, 35, 0.05)

        if self.y <= PLAY_TOP + self.radius:
            self.y = PLAY_TOP + self.radius
            self.vy = abs(self.vy)

        current = self.rect()
        if current.colliderect(paddle.rect) and self.vy > 0:
            self.y = paddle.rect.top - self.radius
            offset = (self.x - paddle.rect.centerx) / (paddle.rect.width / 2)
            self.vx = max(-7.5, min(7.5, offset * 7.0))
            if abs(self.vx) < 1.2:
                self.vx = 1.2 if self.vx >= 0 else -1.2
            self.vy = -max(5.8, min(8.5, math.hypot(self.vx, self.vy)))
            game.combo = 0
            game.shake = max(game.shake, 2)
            for _ in range(7):
                particles.append(Particle(self.x, self.y, CYAN, 3))
            play_tone(650, 55)

        # One brick collision per frame prevents multiple score hits.
        for brick in bricks[:]:
            if self.rect().colliderect(brick.rect):
                if old.bottom <= brick.rect.top + 5 or old.top >= brick.rect.bottom - 5:
                    self.vy *= -1
                else:
                    self.vx *= -1
                brick.hp -= 1
                game.combo += 1
                game.score += 10 * max(1, game.combo)
                game.shake = max(game.shake, 4)
                labels.append(FloatingLabel(brick.rect.centerx, brick.rect.y,
                                            f"+{10 * max(1, game.combo)}", YELLOW))
                for _ in range(13):
                    particles.append(Particle(brick.rect.centerx,
                                              brick.rect.centery, brick.color, 4))
                play_tone(420 + min(game.combo, 8) * 45, 55)
                if brick.hp <= 0:
                    bricks.remove(brick)
                    game.maybe_drop_powerup(brick.rect.center)
                else:
                    brick.color = YELLOW
                break

        return self.y < HEIGHT + 30

    def draw(self, surface):
        for i, point in enumerate(self.trail):
            radius = max(2, int(self.radius * (i + 1) / len(self.trail) * 0.65))
            pygame.draw.circle(surface, (35 + i * 5, 100 + i * 7, 145 + i * 8),
                               point, radius)
        cx, cy = int(self.x), int(self.y)
        pygame.draw.circle(surface, (35, 105, 120), (cx, cy), 17)
        diamond = [(cx, cy - 11), (cx + 9, cy), (cx, cy + 11), (cx - 9, cy)]
        pygame.draw.polygon(surface, YELLOW, diamond)
        pygame.draw.polygon(surface, WHITE, diamond, 2)
        pygame.draw.circle(surface, WHITE, (cx - 2, cy - 3), 3)


class Brick:
    def __init__(self, rect, color, hp=1):
        self.rect = rect
        self.color = color
        self.hp = hp
        self.max_hp = hp

    def draw(self, surface):
        color = self.color if self.hp == 1 else YELLOW
        r = self.rect
        points = [
            (r.left + 8, r.top), (r.right - 8, r.top),
            (r.right, r.centery), (r.right - 8, r.bottom),
            (r.left + 8, r.bottom), (r.left, r.centery)
        ]
        glow = pygame.Surface((r.width + 24, r.height + 24), pygame.SRCALPHA)
        shifted = [(x - r.left + 12, y - r.top + 12) for x, y in points]
        pygame.draw.polygon(glow, (*color, 42), shifted)
        surface.blit(glow, (r.x - 12, r.y - 12))
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, WHITE, points, 1)
        pygame.draw.line(surface, (255, 255, 255),
                         (r.left + 12, r.top + 4),
                         (r.right - 12, r.top + 4), 1)
        if self.max_hp > 1:
            for i in range(self.hp):
                pygame.draw.circle(surface, BG,
                                   (r.centerx - 5 + i * 10, r.centery), 2)


