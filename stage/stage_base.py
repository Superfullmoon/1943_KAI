# ============================================================
#  stage/stage_base.py  —  Scrolling background + island/cloud layers
# ============================================================
import pygame, math, random, os
from config import (SCREEN_WIDTH, SCREEN_HEIGHT, SCROLL_SPEED,
                    STAGE_THEMES, WHITE, GRAY)


# ─── Cloud sprite ────────────────────────────────────────────
class Cloud(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, speed, alpha=100):
        super().__init__()
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)

        # 3D shaded cloud using base grey shadow, body, white puff, and offset highlights
        shadow_col  = (140, 150, 175, int(alpha * 0.7))
        body_col    = (190, 200, 215, alpha)
        white_col   = (255, 255, 255, alpha)
        highlight   = (255, 255, 255, min(255, int(alpha * 1.3)))

        # 1. Shadow Base
        pygame.draw.ellipse(self.image, shadow_col, (4, h//3, w-8, h*2//3 - 4))
        pygame.draw.ellipse(self.image, shadow_col, (w//6 + 4, 6, w*2//3 - 8, h*2//3 - 4))
        pygame.draw.ellipse(self.image, shadow_col, (w//2, h//4, w//3 - 2, h//2 - 2))
        pygame.draw.ellipse(self.image, shadow_col, (4, h//4, w//3 - 2, h//2 - 2))

        # 2. Body Layer (slightly shifted up & left)
        pygame.draw.ellipse(self.image, body_col, (2, h//3 - 2, w-6, h*2//3 - 6))
        pygame.draw.ellipse(self.image, body_col, (w//6 + 2, 3, w*2//3 - 6, h*2//3 - 6))
        pygame.draw.ellipse(self.image, body_col, (w//2 - 1, h//4 - 1, w//3 - 3, h//2 - 3))
        pygame.draw.ellipse(self.image, body_col, (2, h//4 - 1, w//3 - 3, h//2 - 3))

        # 3. Fluffy interior Layer
        pygame.draw.ellipse(self.image, white_col, (6, h//3 - 4, w-12, h*2//3 - 8))
        pygame.draw.ellipse(self.image, white_col, (w//6 + 4, 1, w*2//3 - 8, h*2//3 - 8))
        pygame.draw.circle(self.image, white_col, (w//3, h//2), min(w, h)//4)
        pygame.draw.circle(self.image, white_col, (2*w//3, h//2), min(w, h)//4)

        # 4. Highlight Layer (White, shifted up & left for rim lighting)
        pygame.draw.ellipse(self.image, highlight, (1, h//3 - 6, w-12, h*2//3 - 8))
        pygame.draw.ellipse(self.image, highlight, (w//6 - 1, 0, w*2//3 - 8, h*2//3 - 8))
        pygame.draw.circle(self.image, highlight, (w//3 - 2, h//2 - 2), min(w, h)//4 - 1)
        pygame.draw.circle(self.image, highlight, (2*w//3 - 2, h//2 - 2), min(w, h)//4 - 1)

        self.rect   = self.image.get_rect(center=(x, y))
        self._speed = speed

    def update(self):
        self.rect.y += self._speed
        if self.rect.top > SCREEN_HEIGHT + 250:
            self.rect.bottom = -250
            self.rect.x = random.randint(0, SCREEN_WIDTH)


# ─── Island sprite ────────────────────────────────────────────
class Island(pygame.sprite.Sprite):
    def __init__(self, x, y, size, speed):
        super().__init__()
        w = size
        h = int(size * 0.65)
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)

        # 1. Sandy Shoreline Beach Base (pale yellow sand)
        beach_col = (235, 215, 150)
        pygame.draw.ellipse(self.image, beach_col, (0, 0, w, h))

        # 2. Shallow coastal water ring outline (turquoise reef)
        reef_col = (40, 180, 170)
        pygame.draw.ellipse(self.image, reef_col, (4, 4, w-8, h-8), 2)

        # 3. Dense jungle interior (dark green vegetation base)
        jungle_dark = (30, 95, 45)
        inner_w = int(w * 0.75)
        inner_h = int(h * 0.75)
        pygame.draw.ellipse(self.image, jungle_dark,
                            ((w - inner_w)//2, (h - inner_h)//2, inner_w, inner_h))

        # 4. Lush vegetation highlights (lighter green canopy)
        jungle_light = (60, 165, 80)
        canopy_w = int(w * 0.5)
        canopy_h = int(h * 0.5)
        pygame.draw.ellipse(self.image, jungle_light,
                            ((w - canopy_w)//2, (h - canopy_h)//2 - 2, canopy_w, canopy_h))

        # 5. Peak forest highlight (bright yellow-green canopy top)
        peak_col = (110, 205, 90)
        peak_w = int(w * 0.25)
        peak_h = int(h * 0.25)
        pygame.draw.ellipse(self.image, peak_col,
                            ((w - peak_w)//2 - 2, (h - peak_h)//2 - 4, peak_w, peak_h))

        self.rect   = self.image.get_rect(center=(x, y))
        self._speed = speed

    def update(self):
        self.rect.y += self._speed
        if self.rect.top > SCREEN_HEIGHT + 80:
            self.kill()


# ─── Friendly takeoff carrier ────────────────────────────────
class FriendlyCarrier(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        w, h = 140, 450
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        # Draw a beautiful grey aircraft carrier hull
        # Angled bow (top)
        pygame.draw.polygon(self.image, (80, 85, 95), [(w//2, 0), (5, 60), (w-5, 60)])
        # Main deck hull
        pygame.draw.rect(self.image, (80, 85, 95), (5, 60, w-10, h-80))
        # Stern (bottom) slightly tapered
        pygame.draw.polygon(self.image, (80, 85, 95), [(5, h-20), (w-5, h-20), (w//2, h)])

        # Flight deck (darker grey runway)
        pygame.draw.rect(self.image, (45, 50, 55), (15, 30, w-30, h-60))
        # Angled runway stripes
        pygame.draw.line(self.image, (220, 220, 220), (w//2, 30), (w//2, h-30), 2)
        for y in range(50, h-50, 40):
            pygame.draw.line(self.image, (240, 200, 10), (w//2 - 10, y), (w//2 + 10, y), 2)

        # Island superstructure (right side)
        pygame.draw.rect(self.image, (100, 105, 115), (w-25, h//2 - 50, 15, 70))
        pygame.draw.rect(self.image, (60, 65, 75), (w-22, h//2 - 40, 10, 50))
        # Small gun turrets on the sides of the carrier
        for y in (80, 120, h-120, h-80):
            pygame.draw.circle(self.image, (50, 50, 50), (10, y), 6)
            pygame.draw.line(self.image, (30, 30, 30), (10, y), (2, y-3), 2)
            pygame.draw.circle(self.image, (50, 50, 50), (w-10, y), 6)
            pygame.draw.line(self.image, (30, 30, 30), (w-10, y), (w-2, y-3), 2)

        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 220))
        self._speed = SCROLL_SPEED

    def update(self):
        self.rect.y += self._speed


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
        for _ in range(5):
            cw = random.randint(200, 450)
            ch = random.randint(100, 220)
            self._clouds_back.add(Cloud(
                random.randint(0, SCREEN_WIDTH),
                random.randint(-SCREEN_HEIGHT, SCREEN_HEIGHT),
                cw, ch, speed=0.4, alpha=random.randint(60, 90)))
        for _ in range(4):
            cw = random.randint(150, 300)
            ch = random.randint(80, 150)
            self._clouds_front.add(Cloud(
                random.randint(0, SCREEN_WIDTH),
                random.randint(-SCREEN_HEIGHT, SCREEN_HEIGHT),
                cw, ch, speed=1.0, alpha=random.randint(90, 115)))

        # Spawn friendly takeoff carrier at the start of the stage
        self.friendly_carrier = FriendlyCarrier()

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
            # Shift the sea texture's color to match the stage's specific sea color theme
            tinted_sea = sea_img.copy()
            overlay = pygame.Surface(sea_img.get_size(), pygame.SRCALPHA)
            overlay.fill((self._sea_col[0], self._sea_col[1], self._sea_col[2], 120))
            tinted_sea.blit(overlay, (0, 0))

            iw, ih = tinted_sea.get_size()
            for y in range(sky_h, H, ih):
                for x in range(0, SCREEN_WIDTH, iw):
                    s.blit(tinted_sea, (x, y))
        else:
            sc = self._sea_col
            pygame.draw.rect(s, sc, (0, sky_h, SCREEN_WIDTH, sea_h))
            # Bright wave streaks (retro wave pattern for authentic 1987 arcade feel)
            for i in range(60):
                wy = sky_h + random.randint(0, sea_h - 10)
                wl = random.randint(15, 35)  # Shorter, clearer segments
                wx = random.randint(0, SCREEN_WIDTH - wl)
                wave_col = (min(255, sc[0] + 60), min(255, sc[1] + 70), min(255, sc[2] + 80))
                # Draw retro-style stepped dash wave patterns
                pygame.draw.line(s, wave_col, (wx, wy), (wx + wl, wy), 2)
                pygame.draw.line(s, wave_col, (wx + wl//3, wy + 2), (wx + wl*2//3, wy + 2), 1)

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

        if self.friendly_carrier:
            self.friendly_carrier.update()
            if self.friendly_carrier.rect.top > SCREEN_HEIGHT + 100:
                self.friendly_carrier = None

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

        # Draw Friendly Takeoff Carrier (above islands/sea but below sprites and clouds)
        if self.friendly_carrier:
            surface.blit(self.friendly_carrier.image, self.friendly_carrier.rect)

        # Back clouds (thin, far away)
        self._clouds_back.draw(surface)

        # Front clouds (thick, close)
        self._clouds_front.draw(surface)
