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
        _BATTLESHIP_IMG = load_and_scale_sprite(img_path, 200, 100) # Load at a high resolution
        if not _BATTLESHIP_IMG:
            _BATTLESHIP_IMG = pygame.Surface((w, h), pygame.SRCALPHA)
            _BATTLESHIP_IMG.fill((100, 100, 100))

    scaled_img = pygame.transform.smoothscale(_BATTLESHIP_IMG, (w, h))
    surf.blit(scaled_img, (0, 0))



# ─────────────────────────────────────────────────────────────
#  Destroyer  (Stage 1 boss)
# ─────────────────────────────────────────────────────────────
class Destroyer(BossBase):
    hp_max      = 1200
    score_value = SCORE_BOSS

    def _build_image(self):
        w, h = 180, 100
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        _draw_ship_body(self.image, w, h, (80, 90, 100), (60, 70, 80))
        # Stack
        pygame.draw.rect(self.image, (50, 50, 55), (w // 2 - 6, 8, 12, 28))

    def _setup_components(self):
        c_left  = BossComponent(self, -60, -20, hp=200, colour=(90, 100, 110), radius=14, comp_type='main_turret')
        c_right = BossComponent(self, 60, -20, hp=200, colour=(90, 100, 110), radius=14, comp_type='main_turret')
        c_aa    = BossComponent(self, 0, 10, hp=150, colour=(200, 50, 50), radius=11, comp_type='aa_gun')
        self.components.extend([c_left, c_right, c_aa])

    def _fire(self):
        from bullet.enemy_bullet import EnemyBullet, spawn_aimed, spawn_spread
        from config import ENEMY_BULLET_SPEED

        for c in self.components:
            if not getattr(c, '_destroyed', False):
                cx, cy = self.rect.centerx + c.offset_x, self.rect.centery + c.offset_y
                if c.comp_type == 'main_turret' and self._player_ref:
                    spawn_aimed(cx, cy, self._player_ref.rect.centerx, self._player_ref.rect.centery,
                                self._bullet_group, speed=ENEMY_BULLET_SPEED + 1)
                elif c.comp_type == 'aa_gun':
                    spawn_spread(cx, cy, self._bullet_group, count=5, speed=ENEMY_BULLET_SPEED - 1, offset=self._t * 5)


# ─────────────────────────────────────────────────────────────
#  Cruiser  (Stage 2 boss)
# ─────────────────────────────────────────────────────────────
class Cruiser(BossBase):
    hp_max      = 1500
    score_value = SCORE_BOSS

    def _build_image(self):
        w, h = 200, 110
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        _draw_ship_body(self.image, w, h, (70, 80, 95), (50, 60, 75))

    def _setup_components(self):
        c_fore  = BossComponent(self, -55, -20, hp=250, colour=(90, 100, 110), radius=14, comp_type='main_turret')
        c_aft   = BossComponent(self, 55, -20, hp=250, colour=(90, 100, 110), radius=14, comp_type='main_turret')
        c_mid   = BossComponent(self, 0, -10, hp=200, colour=(200, 80, 50), radius=12, comp_type='aa_gun')
        self.components.extend([c_fore, c_aft, c_mid])

    def _fire(self):
        from bullet.enemy_bullet import EnemyBullet, spawn_aimed, spawn_spread
        from config import ENEMY_BULLET_SPEED

        for c in self.components:
            if not getattr(c, '_destroyed', False):
                cx, cy = self.rect.centerx + c.offset_x, self.rect.centery + c.offset_y
                if c.comp_type == 'main_turret' and self._player_ref:
                    spawn_aimed(cx, cy, self._player_ref.rect.centerx, self._player_ref.rect.centery,
                                self._bullet_group, speed=ENEMY_BULLET_SPEED + 1.5)
                elif c.comp_type == 'aa_gun':
                    spawn_spread(cx, cy, self._bullet_group, count=6, speed=ENEMY_BULLET_SPEED, offset=self._t * 3)


# ─────────────────────────────────────────────────────────────
#  Carrier  (Stage 3 boss — wider, lower profile)
# ─────────────────────────────────────────────────────────────
class Carrier(BossBase):
    hp_max      = 2000
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
        c_center = BossComponent(self, 0, 10, hp=400, colour=(180, 50, 50), radius=18, comp_type='main_turret')
        # Side small cannons
        c_left = BossComponent(self, -70, -10, hp=200, colour=(110, 120, 130), radius=11, comp_type='aa_gun')
        c_right = BossComponent(self, 70, -10, hp=200, colour=(110, 120, 130), radius=11, comp_type='aa_gun')
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
    hp_max      = 1800
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

    def _setup_components(self):
        c_left = BossComponent(self, -65, 10, hp=250, colour=(200, 50, 30), radius=12, comp_type='main_turret')
        c_right = BossComponent(self, 65, 10, hp=250, colour=(200, 50, 30), radius=12, comp_type='main_turret')
        self.components.extend([c_left, c_right])

    def _fire(self):
        from bullet.enemy_bullet import EnemyBullet, spawn_aimed, spawn_spread
        from config import ENEMY_BULLET_SPEED

        for c in self.components:
            if not getattr(c, '_destroyed', False):
                cx, cy = self.rect.centerx + c.offset_x, self.rect.centery + c.offset_y
                if self._player_ref:
                    # Torpedo pattern: fast targeted dual shots
                    spawn_aimed(cx, cy, self._player_ref.rect.centerx, self._player_ref.rect.centery,
                                self._bullet_group, speed=ENEMY_BULLET_SPEED + 2)


# ─────────────────────────────────────────────────────────────
#  Battleship  (Stages 5, 8)
# ─────────────────────────────────────────────────────────────
class Battleship(BossBase):
    hp_max      = 2500
    score_value = SCORE_BOSS

    def _build_image(self):
        w, h = 240, 120
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        _draw_ship_body(self.image, w, h, (65, 75, 88), (48, 58, 70))
        # Smokestack pair
        pygame.draw.rect(self.image, (45, 45, 50), (w // 2 - 10, 4, 9, 32))
        pygame.draw.rect(self.image, (45, 45, 50), (w // 2 + 2, 4, 9, 28))

    def _setup_components(self):
        c_fore = BossComponent(self, -70, -15, hp=350, colour=(100, 110, 120), radius=15, comp_type='main_turret')
        c_aft  = BossComponent(self, 70, -15, hp=350, colour=(100, 110, 120), radius=15, comp_type='main_turret')
        c_aa1  = BossComponent(self, -20, 15, hp=200, colour=(220, 60, 30), radius=11, comp_type='aa_gun')
        c_aa2  = BossComponent(self, 20, 15, hp=200, colour=(220, 60, 30), radius=11, comp_type='aa_gun')
        self.components.extend([c_fore, c_aft, c_aa1, c_aa2])

    def _fire(self):
        from bullet.enemy_bullet import EnemyBullet, spawn_aimed, spawn_spread
        from config import ENEMY_BULLET_SPEED

        for c in self.components:
            if not getattr(c, '_destroyed', False):
                cx, cy = self.rect.centerx + c.offset_x, self.rect.centery + c.offset_y
                if c.comp_type == 'main_turret':
                    # Triple heavy spread
                    spawn_spread(cx, cy, self._bullet_group, count=3, speed=ENEMY_BULLET_SPEED + 1, offset=0)
                elif c.comp_type == 'aa_gun' and self._player_ref:
                    # Fast AA fire
                    spawn_aimed(cx, cy, self._player_ref.rect.centerx, self._player_ref.rect.centery,
                                self._bullet_group, speed=ENEMY_BULLET_SPEED + 2)


# ─────────────────────────────────────────────────────────────
#  Night Cruiser  (Stage 6)
# ─────────────────────────────────────────────────────────────
class NightCruiser(Cruiser):
    hp_max = 1600

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
    hp_max = 1800

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
    hp_max = 2200

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
    hp_max      = 3500
    score_value = SCORE_BOSS * 2

    def _build_image(self):
        w, h = 260, 140
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        _draw_ship_body(self.image, w, h, (55, 65, 80), (40, 50, 65))
        # Pagoda-style superstructure
        for level, (w2, h2, y2) in enumerate([(60, 30, 5), (44, 20, 30), (28, 15, 46)]):
            pygame.draw.rect(self.image, (48 - level * 5, 55 - level * 5, 68 - level * 5),
                             (w // 2 - w2 // 2, y2, w2, h2))

    def _setup_components(self):
        c_fore = BossComponent(self, -75, -20, hp=500, colour=(80, 90, 105), radius=16, comp_type='main_turret')
        c_mid  = BossComponent(self, 0, 15, hp=500, colour=(80, 90, 105), radius=16, comp_type='main_turret')
        c_aft  = BossComponent(self, 75, -20, hp=500, colour=(80, 90, 105), radius=16, comp_type='main_turret')
        c_p    = BossComponent(self, -40, 30, hp=250, colour=(250, 180, 10), radius=10, comp_type='machine_gun')
        c_s    = BossComponent(self, 40, 30, hp=250, colour=(250, 180, 10), radius=10, comp_type='machine_gun')
        self.components.extend([c_fore, c_mid, c_aft, c_p, c_s])

    def _fire(self):
        from bullet.enemy_bullet import EnemyBullet, spawn_aimed, spawn_spread
        from config import ENEMY_BULLET_SPEED

        for c in self.components:
            if not getattr(c, '_destroyed', False):
                cx, cy = self.rect.centerx + c.offset_x, self.rect.centery + c.offset_y
                if c.comp_type == 'main_turret':
                    spawn_spread(cx, cy, self._bullet_group, count=5, speed=ENEMY_BULLET_SPEED + 1, offset=self._t * 2)
                elif c.comp_type == 'machine_gun' and self._player_ref:
                    spawn_aimed(cx, cy, self._player_ref.rect.centerx, self._player_ref.rect.centery,
                                self._bullet_group, speed=ENEMY_BULLET_SPEED + 3)


# ─────────────────────────────────────────────────────────────
#  Final Boss HQ  (Stage 10)
# ─────────────────────────────────────────────────────────────
class FinalBase(BossBase):
    hp_max      = 5000
    score_value = SCORE_BOSS * 3

    def _build_image(self):
        w, h = 280, 180
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        # Central platform
        pygame.draw.rect(self.image, (80, 20, 20), (20, 40, w - 40, h - 60))
        # Dome
        pygame.draw.ellipse(self.image, (120, 30, 30), (w // 2 - 60, 10, 120, 80))
        pygame.draw.ellipse(self.image, (180, 60, 30, 100), (w // 2 - 40, 20, 80, 60))
        # Antenna
        pygame.draw.line(self.image, ORANGE, (w // 2, 0), (w // 2, 25), 3)

    def _setup_components(self):
        c_port = BossComponent(self, -80, 20, hp=800, colour=(140, 30, 30), radius=18, comp_type='main_turret')
        c_star = BossComponent(self, 80, 20, hp=800, colour=(140, 30, 30), radius=18, comp_type='main_turret')
        c_dome = BossComponent(self, 0, -10, hp=1000, colour=(255, 100, 50), radius=22, comp_type='aa_gun')
        self.components.extend([c_port, c_star, c_dome])

    def _fire(self):
        from bullet.enemy_bullet import spawn_spread, spawn_aimed, EnemyBullet
        from config import ENEMY_BULLET_SPEED

        dome_alive = not getattr(self.components[2], '_destroyed', False)
        if dome_alive:
            spawn_spread(self.rect.centerx, self.rect.centery - 10,
                         self._bullet_group, count=12 + self._phase * 2, speed=ENEMY_BULLET_SPEED,
                         offset=self._t * 4)

        for c in self.components[:2]:
            if not getattr(c, '_destroyed', False):
                cx, cy = self.rect.centerx + c.offset_x, self.rect.centery + c.offset_y
                if self._player_ref:
                    spawn_aimed(cx, cy, self._player_ref.rect.centerx, self._player_ref.rect.centery,
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
