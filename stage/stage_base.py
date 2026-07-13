# ============================================================
#  stage/stage_base.py  —  Scrolling background + island/cloud layers
# ============================================================
import pygame, math, random, os
from config import (SCREEN_WIDTH, SCREEN_HEIGHT, SCROLL_SPEED,
                    STAGE_THEMES, WHITE, GRAY)


# ─── Cloud sprite ────────────────────────────────────────────
class Cloud(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, speed, alpha=200):
        super().__init__()
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        # Draw a fluffy cloud from overlapping ellipses
        col = (255, 255, 255, alpha)
        pygame.draw.ellipse(self.image, col, (0,      h//3,   w,     h*2//3))
        pygame.draw.ellipse(self.image, col, (w//6,   0,      w*2//3, h*2//3))
        pygame.draw.ellipse(self.image, col, (w//2,   h//4,  w//3,  h//2))
        pygame.draw.ellipse(self.image, col, (0,      h//4,  w//3,  h//2))
        self.rect   = self.image.get_rect(center=(x, y))
        self._speed = speed

    def update(self):
        self.rect.y += self._speed
        if self.rect.top > SCREEN_HEIGHT + 40:
            self.rect.bottom = -40
            self.rect.x = random.randint(0, SCREEN_WIDTH)


# ─── Island sprite ────────────────────────────────────────────
class Island(pygame.sprite.Sprite):
    def __init__(self, x, y, size, speed):
        super().__init__()
        w = size
        h = int(size * 0.65)
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)

        # Sandy beach base
        beach_col = (210, 185, 120)
        pygame.draw.ellipse(self.image, beach_col, (0, h//3, w, h*2//3))

        # Grass/jungle interior
        jungle_col = (60, 130, 60)
        inner_w = int(w * 0.65)
        inner_h = int(h * 0.55)
        pygame.draw.ellipse(self.image, jungle_col,
                            ((w - inner_w)//2, h//4, inner_w, inner_h))

        # Highlight shimmer
        pygame.draw.ellipse(self.image, (80, 160, 80),
                            ((w - inner_w//2)//2, h//3, inner_w//2, inner_h//2))

        # Optional palm tree silhouette
        if size > 50:
            trunk_x = w // 2
            pygame.draw.line(self.image, (100, 70, 30),
                             (trunk_x, h//4 + 4), (trunk_x, h//4 - 10), 3)
            pygame.draw.ellipse(self.image, (40, 110, 40),
                                (trunk_x - 10, h//4 - 18, 20, 12))

        self.rect   = self.image.get_rect(center=(x, y))
        self._speed = speed

    def update(self):
        self.rect.y += self._speed
        if self.rect.top > SCREEN_HEIGHT + 80:
            self.kill()


# ─── Stage base ──────────────────────────────────────────────
class StageBase:
    """Manages the scrolling ocean background, island, and cloud layers."""

    def __init__(self, stage_num: int):
        theme = STAGE_THEMES.get(stage_num, STAGE_THEMES[1])
        self._sky_top  = theme['sky_top']
        self._sky_bot  = theme['sky_bot']
        self._sea_col  = theme['sea']
        self._stage    = stage_num
        self._scroll_y = 0

        # Pre-render a tall background strip (2× screen height for seamless wrap)
        self._bg = self._make_bg()

        # Cloud layers (fluffy white clouds)
        self._clouds_back  = pygame.sprite.Group()
        self._clouds_front = pygame.sprite.Group()
        for _ in range(6):
            cw = random.randint(70, 130)
            ch = random.randint(35, 65)
            self._clouds_back.add(Cloud(
                random.randint(0, SCREEN_WIDTH),
                random.randint(-SCREEN_HEIGHT, SCREEN_HEIGHT),
                cw, ch, speed=0.6, alpha=140))
        for _ in range(4):
            cw = random.randint(50, 100)
            ch = random.randint(28, 50)
            self._clouds_front.add(Cloud(
                random.randint(0, SCREEN_WIDTH),
                random.randint(-SCREEN_HEIGHT, SCREEN_HEIGHT),
                cw, ch, speed=1.4, alpha=210))

        # Islands (scroll with the background)
        self._islands = pygame.sprite.Group()
        self._island_timer = 0
        self._island_interval = 240  # frames between island spawns

    def _make_bg(self):
        """Pre-render a 2× height surface: sky gradient + tiled sea."""
        H = SCREEN_HEIGHT * 2
        s = pygame.Surface((SCREEN_WIDTH, H))

        sky_h = int(H * 0.40)
        sea_h = H - sky_h

        # ── Sky gradient ──────────────────────────────────────
        for y in range(sky_h):
            t   = y / sky_h
            col = (
                int(self._sky_top[0] * (1 - t) + self._sky_bot[0] * t),
                int(self._sky_top[1] * (1 - t) + self._sky_bot[1] * t),
                int(self._sky_top[2] * (1 - t) + self._sky_bot[2] * t),
            )
            pygame.draw.line(s, col, (0, y), (SCREEN_WIDTH, y))

        # ── Sea (tiled image or solid fallback) ───────────────
        img_path = os.path.join(os.path.dirname(__file__),
                                '..', 'assets', 'image', 'background', 'sea.png')
        sea_img = None
        try:
            sea_img = pygame.image.load(img_path).convert()
        except Exception:
            pass

        if sea_img is not None:
            iw, ih = sea_img.get_size()
            for y in range(sky_h, H, ih):
                for x in range(0, SCREEN_WIDTH, iw):
                    s.blit(sea_img, (x, y))
        else:
            sc = self._sea_col
            pygame.draw.rect(s, sc, (0, sky_h, SCREEN_WIDTH, sea_h))
            # Subtle wave streaks
            for i in range(40):
                wy = sky_h + random.randint(0, sea_h - 4)
                wl = random.randint(30, 100)
                wx = random.randint(0, SCREEN_WIDTH - wl)
                bright = (min(255, sc[0]+55), min(255, sc[1]+55), min(255, sc[2]+45))
                pygame.draw.line(s, bright, (wx, wy), (wx + wl, wy), 1)

        return s

    def _spawn_island(self):
        size = random.choice([40, 55, 75, 95])
        x = random.randint(size, SCREEN_WIDTH - size)
        self._islands.add(Island(x, -size, size, speed=SCROLL_SPEED * 0.8))

    def update(self):
        self._scroll_y = (self._scroll_y + SCROLL_SPEED) % SCREEN_HEIGHT
        self._clouds_back.update()
        self._clouds_front.update()
        self._islands.update()

        # Periodically spawn islands
        self._island_timer += 1
        if self._island_timer >= self._island_interval:
            self._island_timer = 0
            self._island_interval = random.randint(200, 400)
            if random.random() < 0.65:   # 65% chance to actually spawn
                self._spawn_island()

    def draw(self, surface):
        # Two blit positions for seamless scroll
        y0 = self._scroll_y - SCREEN_HEIGHT
        surface.blit(self._bg, (0, y0))
        surface.blit(self._bg, (0, y0 + SCREEN_HEIGHT))

        # Islands (behind clouds, behind sprites)
        self._islands.draw(surface)

        # Back clouds (thin, far away)
        self._clouds_back.draw(surface)

        # Front clouds (thick, close)
        self._clouds_front.draw(surface)
