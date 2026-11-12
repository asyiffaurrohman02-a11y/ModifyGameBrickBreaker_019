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

