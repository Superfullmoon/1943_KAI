# ============================================================
#  effects/bomb.py  —  Screen-clearing bomb flash
# ============================================================
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, YELLOW, ORANGE


class BombEffect:
    """Full-screen flash + shockwave ring when a bomb is used."""

    def __init__(self):
        self._active   = False
        self._timer    = 0
        self._duration = 30   # frames

    def activate(self):
        self._active = True
        self._timer  = self._duration

    def update(self):
        if self._active:
            self._timer -= 1
            if self._timer <= 0:
                self._active = False

    def draw(self, surface):
        if not self._active:
            return
        t     = self._timer / self._duration  # 1 → 0
        alpha = int(220 * t)
        # White flash
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 200, alpha))
        surface.blit(overlay, (0, 0))
        # Expanding ring
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        radius = int((1 - t) * SCREEN_WIDTH)
        if radius > 0:
            pygame.draw.circle(surface, (*ORANGE, min(255, alpha)),
                               (cx, cy), radius, 6)
            pygame.draw.circle(surface, (*YELLOW, min(255, alpha // 2)),
                               (cx, cy), max(1, radius - 12), 3)
