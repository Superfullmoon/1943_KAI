# ============================================================
#  stage/stage_base.py  —  Scrolling background + wave base
# ============================================================
import pygame, math, random
from config import (SCREEN_WIDTH, SCREEN_HEIGHT, SCROLL_SPEED,
                    STAGE_THEMES, WHITE, GRAY)


# ─── Cloud sprite ────────────────────────────────────────────
class Cloud(pygame.sprite.Sprite):
    def __init__(self, x, y, radius, speed, alpha=180):
        super().__init__()
        d  = radius * 2
        self.image = pygame.Surface((d, d), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (255, 255, 255, alpha), (0, 0, d, d))
        self.rect  = self.image.get_rect(center=(x, y))
        self._speed = speed

    def update(self):
        self.rect.y += self._speed
        if self.rect.top > SCREEN_HEIGHT + 20:
            self.rect.bottom = -20
            self.rect.x = random.randint(0, SCREEN_WIDTH)


# ─── Stage base ──────────────────────────────────────────────
class StageBase:
    """Manages the scrolling ocean background and cloud layers."""

    def __init__(self, stage_num: int):
        theme = STAGE_THEMES.get(stage_num, STAGE_THEMES[1])
        self._sky_top  = theme['sky_top']
        self._sky_bot  = theme['sky_bot']
        self._sea_col  = theme['sea']
        self._stage    = stage_num
        self._scroll_y = 0

        # Pre-render a tall background strip (2× screen height for seamless wrap)
        self._bg = self._make_bg()

        # Cloud layers
        self._clouds_back  = pygame.sprite.Group()
        self._clouds_front = pygame.sprite.Group()
        for _ in range(5):
            r = random.randint(25, 50)
            self._clouds_back.add(Cloud(
                random.randint(0, SCREEN_WIDTH),
                random.randint(-SCREEN_HEIGHT, SCREEN_HEIGHT),
                r, speed=0.8, alpha=120))
        for _ in range(4):
            r = random.randint(20, 38)
            self._clouds_front.add(Cloud(
                random.randint(0, SCREEN_WIDTH),
                random.randint(-SCREEN_HEIGHT, SCREEN_HEIGHT),
                r, speed=1.6, alpha=180))

        # Wave offsets (animated wave lines on the sea)
        self._wave_offsets = [random.uniform(0, math.pi * 2) for _ in range(8)]

    def _make_bg(self):
        """Pre-render a 2× height surface for seamless vertical scrolling."""
        H = SCREEN_HEIGHT * 2
        s = pygame.Surface((SCREEN_WIDTH, H))

        sky_h = int(H * 0.55)
        sea_h = H - sky_h

        # Sky gradient
        for y in range(sky_h):
            t   = y / sky_h
            col = (
                int(self._sky_top[0] * (1 - t) + self._sky_bot[0] * t),
                int(self._sky_top[1] * (1 - t) + self._sky_bot[1] * t),
                int(self._sky_top[2] * (1 - t) + self._sky_bot[2] * t),
            )
            pygame.draw.line(s, col, (0, y), (SCREEN_WIDTH, y))

        # Sea (solid + highlight)
        pygame.draw.rect(s, self._sea_col, (0, sky_h, SCREEN_WIDTH, sea_h))
        for i in range(30):
            wy = sky_h + random.randint(0, sea_h - 20)
            pygame.draw.line(s, (min(255, self._sea_col[0] + 60),
                                  min(255, self._sea_col[1] + 60),
                                  min(255, self._sea_col[2] + 50)),
                             (random.randint(0, SCREEN_WIDTH),      wy),
                             (random.randint(0, SCREEN_WIDTH), wy + 2), 1)

        # Wave crests (pre-baked — animated lines added at draw-time)
        for i in range(18):
            wy = sky_h + 10 + i * (sea_h // 18)
            for wx in range(0, SCREEN_WIDTH, 50):
                pygame.draw.line(s, (min(255, self._sea_col[0] + 80),
                                      min(255, self._sea_col[1] + 80),
                                      min(255, self._sea_col[2] + 70)),
                                 (wx, wy), (wx + 36, wy), 1)
        return s

    def update(self):
        self._scroll_y = (self._scroll_y + SCROLL_SPEED) % SCREEN_HEIGHT
        for o in range(len(self._wave_offsets)):
            self._wave_offsets[o] += 0.03
        self._clouds_back.update()
        self._clouds_front.update()

    def draw(self, surface):
        # Two blit positions for seamless scroll
        y0 = self._scroll_y - SCREEN_HEIGHT
        surface.blit(self._bg, (0, y0))
        surface.blit(self._bg, (0, y0 + SCREEN_HEIGHT))

        # Back clouds (behind everything)
        self._clouds_back.draw(surface)

        # Animated wave lines on top of sea
        sky_y = int(SCREEN_HEIGHT * 0.55)
        for i, offset in enumerate(self._wave_offsets):
            wy = sky_y + 10 + i * 30 + int(math.sin(offset) * 6)
            wx = int(math.sin(offset * 0.5 + i) * 20)
            col = (min(255, self._sea_col[0] + 70),
                   min(255, self._sea_col[1] + 70),
                   min(255, self._sea_col[2] + 60))
            for sx in range(0, SCREEN_WIDTH, 55):
                pygame.draw.line(surface, col, (sx + wx, wy), (sx + wx + 42, wy), 1)

        # Front clouds (in front of waves, behind sprites)
        self._clouds_front.draw(surface)
