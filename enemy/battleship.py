# ============================================================
#  enemy/battleship.py  —  Concrete battleship boss variants
# ============================================================
import pygame, math
from config import (SCREEN_WIDTH, GRAY, DARK_GRAY, WHITE, RED, ORANGE,
                    YELLOW, NAVY, SILVER, DARK_RED, SCORE_BOSS)
from enemy.boss import BossBase, BossComponent


import os

try:
    from config import load_and_scale_sprite
except ImportError:
    def load_and_scale_sprite(path, target_w, target_h, colorkey='auto'):
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.smoothscale(img, (target_w, target_h))
            return img
        except Exception as e:
            print("Failed to load sprite {}: {}".format(path, e))
            return None

_BATTLESHIP_IMG = None

def _draw_ship_body(surf, w, h, hull_col, deck_col, name_col=None):
    """Utility to draw a battleship body using a generated image."""
    global _BATTLESHIP_IMG
    if _BATTLESHIP_IMG is None:
        img_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'image', 'boss', 'battleship.png')
        try:
            _BATTLESHIP_IMG = pygame.image.load(img_path).convert_alpha()
        except Exception as e:
            print("Failed to load battleship image directly: {}".format(e))
            _BATTLESHIP_IMG = None

    if _BATTLESHIP_IMG is not None:
        scaled_img = pygame.transform.smoothscale(_BATTLESHIP_IMG, (w, h))
        surf.blit(scaled_img, (0, 0))
    else:
        # Procedural fallback or solid color
        pygame.draw.rect(surf, (100, 100, 100), (0, 0, w, h))



# ─────────────────────────────────────────────────────────────
#  Destroyer  (Stage 1 boss)
# ─────────────────────────────────────────────────────────────
class Destroyer(BossBase):
    hp_max      = 800
    score_value = SCORE_BOSS

    def _build_image(self):
        w, h = 180, 100
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        _draw_ship_body(self.image, w, h, (80, 90, 100), (60, 70, 80))

        # Turrets (will be BossComponents)
        for tx in (50, 130):
            pygame.draw.circle(self.image, DARK_GRAY, (tx, 30), 14)
            pygame.draw.rect(self.image, (40, 40, 40), (tx - 3, 10, 6, 22))

        # Stack
        pygame.draw.rect(self.image, (50, 50, 55), (w // 2 - 6, 8, 12, 28))

    def _setup_components(self):
        for ox, oy in [(-60, -20), (60, -20)]:
            c = BossComponent(self, ox, oy, hp=200, colour=(90, 100, 110), radius=14)
            self.components.append(c)


# ─────────────────────────────────────────────────────────────
#  Cruiser  (Stage 2 boss)
# ─────────────────────────────────────────────────────────────
class Cruiser(BossBase):
    hp_max      = 1000
    score_value = SCORE_BOSS

    def _build_image(self):
        w, h = 200, 110
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        _draw_ship_body(self.image, w, h, (70, 80, 95), (50, 60, 75))
        # Extra turret positions
        for tx in (45, 100, 155):
            pygame.draw.circle(self.image, DARK_GRAY, (tx, 25), 13)
            pygame.draw.rect(self.image, (40, 40, 40), (tx - 3, 8, 6, 20))


# ─────────────────────────────────────────────────────────────
#  Carrier  (Stage 3 boss — wider, lower profile)
# ─────────────────────────────────────────────────────────────
class Carrier(BossBase):
    hp_max      = 1500
    score_value = SCORE_BOSS

    def _build_image(self):
        w, h = 240, 90
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        _draw_ship_body(self.image, w, h, (60, 70, 80), (45, 55, 65))
        # Flight deck stripes
        for i in range(5):
            pygame.draw.line(self.image, (200, 200, 200, 80),
                             (30, 15 + i * 10), (210, 15 + i * 10), 1)
        # Island superstructure (right side)
        pygame.draw.rect(self.image, (55, 65, 75), (w - 55, 5, 40, 45))

    def _setup_components(self):
        # Center big cannon (larger radius)
        c_center = BossComponent(self, 0, 10, hp=400, colour=(180, 50, 50), radius=20)
        # Side small cannons
        c_left = BossComponent(self, -70, -10, hp=200, colour=(110, 120, 130), radius=12)
        c_right = BossComponent(self, 70, -10, hp=200, colour=(110, 120, 130), radius=12)
        self.components.extend([c_center, c_left, c_right])

    def _fire(self):
        from bullet.enemy_bullet import EnemyBullet, spawn_aimed, spawn_spread
        from config import ENEMY_BULLET_SPEED

        # Check which components are alive
        center_alive = any(c.offset_x == 0 for c in self.components if not getattr(c, '_destroyed', False))
        left_alive = any(c.offset_x < 0 for c in self.components if not getattr(c, '_destroyed', False))
        right_alive = any(c.offset_x > 0 for c in self.components if not getattr(c, '_destroyed', False))

        if center_alive:
            # Center big cannon fires a spread of bullets
            spawn_spread(self.rect.centerx, self.rect.centery + 10,
                         self._bullet_group, count=8 + self._phase * 2, speed=ENEMY_BULLET_SPEED - 1,
                         offset=self._t * 3)
        if left_alive and self._player_ref:
            # Left small cannon fires aimed bullet
            spawn_aimed(self.rect.centerx - 70, self.rect.centery - 10,
                        self._player_ref.rect.centerx, self._player_ref.rect.centery,
                        self._bullet_group, speed=ENEMY_BULLET_SPEED)
        if right_alive and self._player_ref:
            # Right small cannon fires aimed bullet
            spawn_aimed(self.rect.centerx + 70, self.rect.centery - 10,
                        self._player_ref.rect.centerx, self._player_ref.rect.centery,
                        self._bullet_group, speed=ENEMY_BULLET_SPEED)

        # Base ship body shoots in phase 3
        if self._phase >= 3 and self._player_ref:
            spawn_aimed(self.rect.centerx, self.rect.bottom,
                        self._player_ref.rect.centerx, self._player_ref.rect.centery,
                        self._bullet_group, speed=ENEMY_BULLET_SPEED + 2)


# ─────────────────────────────────────────────────────────────
#  Storm Submarine  (Stage 4 boss)
# ─────────────────────────────────────────────────────────────
class Submarine(BossBase):
    hp_max      = 900
    score_value = SCORE_BOSS

    def _build_image(self):
        w, h = 200, 70
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        # Hull (elongated ellipse)
        pygame.draw.ellipse(self.image, (50, 80, 60), (5, 20, w - 10, 40))
        # Conning tower
        pygame.draw.rect(self.image, (60, 100, 70), (w // 2 - 18, 5, 36, 30))
        # Periscopes
        pygame.draw.rect(self.image, (40, 60, 50), (w // 2 - 10, 0, 4, 15))
        pygame.draw.rect(self.image, (40, 60, 50), (w // 2 + 6, 0, 4, 15))
        # Torpedo tubes
        for tx in (15, w - 22):
            pygame.draw.circle(self.image, DARK_GRAY, (tx, 40), 7)


# ─────────────────────────────────────────────────────────────
#  Battleship  (Stages 5, 9)
# ─────────────────────────────────────────────────────────────
class Battleship(BossBase):
    hp_max      = 1500
    score_value = SCORE_BOSS

    def _build_image(self):
        w, h = 240, 120
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        _draw_ship_body(self.image, w, h, (65, 75, 88), (48, 58, 70))
        # Main turrets (large)
        for tx in (50, 120, 190):
            pygame.draw.circle(self.image, (55, 60, 70), (tx, 22), 18)
            # Twin barrels
            pygame.draw.rect(self.image, (35, 40, 50), (tx - 8, 2, 5, 22))
            pygame.draw.rect(self.image, (35, 40, 50), (tx + 3, 2, 5, 22))
        # Smokestack pair
        pygame.draw.rect(self.image, (45, 45, 50), (w // 2 - 10, 4, 9, 32))
        pygame.draw.rect(self.image, (45, 45, 50), (w // 2 + 2, 4, 9, 28))


# ─────────────────────────────────────────────────────────────
#  Night Cruiser  (Stage 6)
# ─────────────────────────────────────────────────────────────
class NightCruiser(Cruiser):
    hp_max = 1100

    def _build_image(self):
        super()._build_image()
        # Tint the image dark
        dark = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        dark.fill((0, 0, 30, 80))
        self.image.blit(dark, (0, 0))


# ─────────────────────────────────────────────────────────────
#  Arctic Icebreaker  (Stage 7)
# ─────────────────────────────────────────────────────────────
class Icebreaker(BossBase):
    hp_max = 1300

    def _build_image(self):
        w, h = 220, 110
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        _draw_ship_body(self.image, w, h, (180, 200, 215), (160, 180, 195))
        # Icebreaker prow
        pts = [(w // 2, 0), (25, h // 3), (w - 25, h // 3)]
        pygame.draw.polygon(self.image, (200, 215, 225), pts)
        # Ice scraper lines
        for i in range(4):
            pygame.draw.line(self.image, (220, 235, 245),
                             (w // 2, 0), (30 + i * 50, h // 3), 2)


# ─────────────────────────────────────────────────────────────
#  Volcanic Dreadnought  (Stage 8)
# ─────────────────────────────────────────────────────────────
class VolcanicDreadnought(Battleship):
    hp_max = 1700

    def _build_image(self):
        super()._build_image()
        # Lava-glow tint
        tint = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        tint.fill((120, 40, 0, 60))
        self.image.blit(tint, (0, 0))
        # Lava vents
        for vx in (60, 120, 180):
            pygame.draw.circle(self.image, (255, 80, 0, 180), (vx, 60), 6)


# ─────────────────────────────────────────────────────────────
#  Super Battleship Yamato  (Stage 9)
# ─────────────────────────────────────────────────────────────
class SuperBattleship(BossBase):
    hp_max      = 2500
    score_value = SCORE_BOSS * 2

    def _build_image(self):
        w, h = 260, 140
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        _draw_ship_body(self.image, w, h, (55, 65, 80), (40, 50, 65))
        # Massive triple-gun turrets
        for tx, size in [(55, 22), (130, 26), (205, 22)]:
            pygame.draw.circle(self.image, (45, 50, 62), (tx, 24), size)
            for bx in (-9, 0, 9):
                pygame.draw.rect(self.image, (30, 35, 45), (tx + bx - 2, 2, 4, 26))
        # Pagoda-style superstructure
        for level, (w2, h2, y2) in enumerate([(60, 30, 5), (44, 20, 30), (28, 15, 46)]):
            pygame.draw.rect(self.image, (48 - level * 5, 55 - level * 5, 68 - level * 5),
                             (w // 2 - w2 // 2, y2, w2, h2))


# ─────────────────────────────────────────────────────────────
#  Final Boss HQ  (Stage 10)
# ─────────────────────────────────────────────────────────────
class FinalBase(BossBase):
    hp_max      = 3500
    score_value = SCORE_BOSS * 3

    def _build_image(self):
        w, h = 280, 180
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        # Central platform
        pygame.draw.rect(self.image, (80, 20, 20), (20, 40, w - 40, h - 60))
        # Dome
        pygame.draw.ellipse(self.image, (120, 30, 30), (w // 2 - 60, 10, 120, 80))
        pygame.draw.ellipse(self.image, (180, 60, 30, 100), (w // 2 - 40, 20, 80, 60))
        # Side cannons
        for cx in (30, w - 30):
            pygame.draw.circle(self.image, (60, 15, 15), (cx, 80), 20)
            pygame.draw.rect(self.image, (40, 10, 10), (cx - 4, 55, 8, 28))
        # Antenna
        pygame.draw.line(self.image, ORANGE, (w // 2, 0), (w // 2, 25), 3)

    def _fire(self):
        from bullet.enemy_bullet import spawn_spread, spawn_aimed, EnemyBullet
        from config import ENEMY_BULLET_SPEED
        # Massive spread in all phases
        spawn_spread(self.rect.centerx, self.rect.centery,
                     self._bullet_group, count=12, speed=ENEMY_BULLET_SPEED,
                     offset=self._t * 3)
        if self._player_ref:
            for _ in range(self._phase):
                spawn_aimed(self.rect.centerx, self.rect.bottom,
                            self._player_ref.rect.centerx,
                            self._player_ref.rect.centery,
                            self._bullet_group, speed=ENEMY_BULLET_SPEED + self._phase)


# ─── Lookup table for StageManager ───────────────────────────
BOSS_BY_STAGE = {
    1:  Destroyer,
    2:  Cruiser,
    3:  Carrier,
    4:  Submarine,
    5:  Battleship,
    6:  NightCruiser,
    7:  Icebreaker,
    8:  VolcanicDreadnought,
    9:  SuperBattleship,
    10: FinalBase,
}
