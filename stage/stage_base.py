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

        # 4-layer 3D volumetric cloud representation:
        # Layer 1: Darkest underbelly shadow (ambient occlusion)
        # Layer 2: Main body cloud shadow (grayish-blue)
        # Layer 3: Fluffy cloud body (soft white/gray transition)
        # Layer 4: Bright sun-lit highlight peaks (pure white)

        num_puffs = random.randint(5, 8)
        puffs = []
        for _ in range(num_puffs):
            px = random.randint(w // 4, w * 3 // 4)
            py = random.randint(h // 3, h * 2 // 3)
            pr = random.randint(min(h // 4, 15), min(h // 2, w // 4))
            puffs.append((px, py, pr))

        # Sort puffs from rear/left to front/right to build structured layer depth
        puffs.sort(key=lambda p: (p[1], p[0]))

        # Layer 1 & 2: Shadows (offset down and right)
        for shadow_offset, shadow_col in [(4, (140, 145, 160, int(alpha * 0.45))), (2, (170, 175, 190, int(alpha * 0.7)))]:
            for px, py, pr in puffs:
                pygame.draw.circle(self.image, shadow_col, (px + shadow_offset, py + shadow_offset), pr)

        # Layer 3: Main body
        body_col = (235, 240, 250, alpha)
        for px, py, pr in puffs:
            pygame.draw.circle(self.image, body_col, (px, py), pr)

        # Layer 4: Pure white highlights (offset up and left, slightly smaller)
        highlight_col = (255, 255, 255, min(255, int(alpha * 1.25)))
        for px, py, pr in puffs:
            hx = px - int(pr * 0.15)
            hy = py - int(pr * 0.20)
            hr = int(pr * 0.8)
            if hr > 0:
                pygame.draw.circle(self.image, highlight_col, (hx, hy), hr)

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
        h = int(size * 0.7)
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)

        # Draw an organic, irregular island shape using a cluster of overlapping circles
        num_clusters = random.randint(3, 5)
        clusters = []
        for _ in range(num_clusters):
            cx = random.randint(w // 4, w * 3 // 4)
            cy = random.randint(h // 4, h * 3 // 4)
            cr = random.randint(size // 5, size // 3)
            clusters.append((cx, cy, cr))

        # Shore reef (semi-transparent shallow coral reef)
        for cx, cy, cr in clusters:
            pygame.draw.circle(self.image, (40, 180, 170, 140), (cx, cy), cr + 4)

        # Beach outline (pale yellow sand)
        for cx, cy, cr in clusters:
            pygame.draw.circle(self.image, (235, 215, 150), (cx, cy), cr + 1)

        # Dense jungle interior (dark green base)
        for cx, cy, cr in clusters:
            pygame.draw.circle(self.image, (30, 95, 45), (cx, cy), int(cr * 0.8))

        # Lush vegetation highlights (lighter green canopy)
        for cx, cy, cr in clusters:
            pygame.draw.circle(self.image, (60, 165, 80), (cx - int(cr*0.1), cy - int(cr*0.15)), int(cr * 0.6))

        # Peak forest ridges (bright yellow-green)
        for cx, cy, cr in clusters:
            pygame.draw.circle(self.image, (110, 205, 90), (cx - int(cr*0.2), cy - int(cr*0.25)), int(cr * 0.35))

        # Retro military airfield runway (an iconic 1943 feature for larger islands)
        if size >= 75:
            # Dark gray runway
            pygame.draw.polygon(self.image, (45, 45, 50), [
                (w//4, h//2 - 5),
                (w*3//4, h//2 - 2),
                (w*3//4, h//2 + 2),
                (w//4, h//2 + 5)
            ])
            # Runway stripes (yellow dashes)
            pygame.draw.line(self.image, (255, 215, 0), (w//4 + 10, h//2), (w*3//4 - 10, h//2), 1)

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
            iw, ih = sea_img.get_size()
            for y in range(sky_h, H, ih):
                for x in range(0, SCREEN_WIDTH, iw):
                    s.blit(sea_img, (x, y))
            # Blend the sea texture with the stage-specific color theme overlay (alpha 120)
            overlay = pygame.Surface((SCREEN_WIDTH, sea_h), pygame.SRCALPHA)
            sc = self._sea_col
            overlay.fill((sc[0], sc[1], sc[2], 120))
            s.blit(overlay, (0, sky_h))
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
