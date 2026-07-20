# ============================================================
#  enemy/enemy.py  —  Base enemy class + concrete types
# ============================================================
import pygame, random, math
from config import (SCREEN_WIDTH, SCREEN_HEIGHT,
                    RED, DARK_RED, ORANGE, YELLOW, WHITE, GRAY, DARK_GRAY,
                    SCORE_SMALL_ENEMY, SCORE_MEDIUM_ENEMY, SCORE_LARGE_ENEMY,
                    ENEMY_BULLET_SPEED)
from enemy.enemy_ai import get_pattern


# ─────────────────────────────────────────────────────────────
#  Base Enemy
# ─────────────────────────────────────────────────────────────
class BaseEnemy(pygame.sprite.Sprite):
    score_value = SCORE_SMALL_ENEMY
    hp_max      = 30

    def __init__(self, x, y, pattern='straight', pattern_kwargs=None,
                 bullet_group=None, player_ref=None):
        super().__init__()
        if pattern_kwargs is None:
            pattern_kwargs = {}

        # Inject player reference for aimed shots / kamikaze
        if pattern == 'kamikaze' and player_ref:
            pattern_kwargs['player_ref'] = player_ref

        self._move  = get_pattern(pattern, **pattern_kwargs)
        self.hp     = self.hp_max
        self._bullet_group  = bullet_group
        self._player_ref    = player_ref
        self._shoot_cd      = random.randint(40, 100)
        self._shoot_rate    = 80   # frames between shots
        self.drop_chance    = 0.12

        self._build_image()
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

        # Drop callback — set by StageManager
        self.drop_item = None

    def _build_image(self):
        """Override in subclasses."""
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(self.image, RED, (16, 16), 14)

    def update(self):
        self._move(self)
        self._try_shoot()
        # Kill if off screen
        if (self.rect.top > SCREEN_HEIGHT + 60
                or self.rect.right < -60 or self.rect.left > SCREEN_WIDTH + 60):
            self.kill()

    def _try_shoot(self):
        if self._bullet_group is None:
            return
        self._shoot_cd -= 1
        if self._shoot_cd <= 0:
            self._fire()
            self._shoot_cd = self._shoot_rate

    def _fire(self):
        from bullet.enemy_bullet import EnemyBullet
        self._bullet_group.add(
            EnemyBullet(self.rect.centerx, self.rect.bottom))

    def take_damage(self, amount: int) -> bool:
        """Return True if killed."""
        self.hp -= amount
        if self.hp <= 0:
            if self.drop_item and random.random() < self.drop_chance:
                self.drop_item(self.rect.centerx, self.rect.centery)
            self.kill()
            return True
        return False


# ─────────────────────────────────────────────────────────────
#  Small Fighter (Type A — red)
# ─────────────────────────────────────────────────────────────
import os

def _build_enemy_img(w, h, color_main=(60, 120, 60)):
    """Build a Zero-style enemy fighter procedurally with authentic WWII details."""
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = w // 2, h // 2

    # ── Propeller Blur ───────────────────────────────────────
    pygame.draw.ellipse(s, (220, 220, 220, 100), (cx - 16, 0, 32, 4))

    # ── Fuselage ─────────────────────────────────────────────
    pygame.draw.ellipse(s, color_main, (cx - 5, 2, 10, h - 4))
    pygame.draw.ellipse(s, (min(color_main[0]+40, 255),
                            min(color_main[1]+40, 255),
                            min(color_main[2]+20, 255)),
                        (cx - 3, 4, 6, h - 10))

    # ── Wings ───────────────────────────────────────────────
    wing_y = cy - 4
    pygame.draw.polygon(s, color_main,
                        [(0, wing_y + 6), (w, wing_y + 6),
                         (w - 4, wing_y - 2), (4, wing_y - 2)])

    # Yellow leading edges on front of the wings (identification stripes)
    pygame.draw.polygon(s, (255, 180, 0),
                        [(4, wing_y - 1), (w - 4, wing_y - 1),
                         (w - 10, wing_y + 1), (10, wing_y + 1)])

    # ── Engine cowling & Propeller Hub ──────────────────────
    pygame.draw.circle(s, (30, 30, 30), (cx, 4), 6)
    pygame.draw.circle(s, (200, 40, 20), (cx, 3), 3)  # Red hub spinner

    # ── Cockpit ─────────────────────────────────────────────
    pygame.draw.ellipse(s, (50, 110, 190), (cx - 4, cy - 8, 8, 12))
    pygame.draw.ellipse(s, (150, 210, 255, 180), (cx - 3, cy - 7, 6, 8))

    # ── Red rising sun circles (Hinomaru wing markings) ──────
    pygame.draw.circle(s, (180, 20, 20), (8, wing_y + 2), 5)
    pygame.draw.circle(s, (180, 20, 20), (w - 8, wing_y + 2), 5)

    # ── Identification Fuselage Band ────────────────────────
    pygame.draw.rect(s, (240, 240, 240), (cx - 4, cy + 6, 8, 2))

    # ── Horizontal stabilizer (Tail wing) ───────────────────
    pygame.draw.polygon(s, color_main,
                        [(cx - 12, h - 8), (cx + 12, h - 8), (cx + 8, h - 4), (cx - 8, h - 4)])

    # ── Vertical stabilizer (Tail fin) ──────────────────────
    pygame.draw.line(s, (min(color_main[0]+20, 255),
                         min(color_main[1]+20, 255),
                         min(color_main[2]+20, 255)),
                     (cx, h - 10), (cx, h - 2), 2)
    return s


def _get_enemy_img(w, h, color_main=(60, 120, 60)):
    return _build_enemy_img(w, h, color_main)

class SmallFighter(BaseEnemy):
    score_value = SCORE_SMALL_ENEMY
    hp_max      = 45

    def _build_image(self):
        w, h = 34, 34
        self.image = _get_enemy_img(w, h, color_main=(60, 120, 60))


# ─────────────────────────────────────────────────────────────
#  Medium Fighter (Type B — dark blue)
# ─────────────────────────────────────────────────────────────
class MediumFighter(BaseEnemy):
    score_value = SCORE_MEDIUM_ENEMY
    hp_max      = 110

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._shoot_rate = 60
        self.drop_chance = 0.22

    def _build_image(self):
        w, h = 44, 44
        self.image = _get_enemy_img(w, h, color_main=(40, 60, 130))

    def _fire(self):
        from bullet.enemy_bullet import EnemyBullet, spawn_aimed
        if self._player_ref:
            spawn_aimed(self.rect.centerx, self.rect.bottom,
                        self._player_ref.rect.centerx,
                        self._player_ref.rect.centery,
                        self._bullet_group)
        else:
            self._bullet_group.add(EnemyBullet(self.rect.centerx, self.rect.bottom))


# ─────────────────────────────────────────────────────────────
#  Large Heavy Fighter (Type C — red/brown)
# ─────────────────────────────────────────────────────────────
class HeavyFighter(BaseEnemy):
    score_value = SCORE_LARGE_ENEMY
    hp_max      = 250

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._shoot_rate = 45
        self.drop_chance = 0.40

    def _build_image(self):
        w, h = 56, 52
        self.image = _get_enemy_img(w, h, color_main=(130, 50, 30))

    def _fire(self):
        from bullet.enemy_bullet import EnemyBullet, spawn_aimed
        # Triple shot
        for dx in (-12, 0, 12):
            self._bullet_group.add(
                EnemyBullet(self.rect.centerx + dx, self.rect.bottom, vy=ENEMY_BULLET_SPEED))
        if self._player_ref:
            spawn_aimed(self.rect.centerx, self.rect.bottom,
                        self._player_ref.rect.centerx,
                        self._player_ref.rect.centery,
                        self._bullet_group, speed=ENEMY_BULLET_SPEED - 1)


# ─────────────────────────────────────────────────────────────
#  Small Warship — scrolls upward on the sea
# ─────────────────────────────────────────────────────────────
def _build_warship_img(w, h, hull_col, deck_col):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    # Hull
    hull_pts = [(4, h//3), (w-4, h//3), (w-2, h-4), (2, h-4)]
    pygame.draw.polygon(s, hull_col, hull_pts)
    # Deck
    pygame.draw.rect(s, deck_col, (6, 4, w-12, h//3 + 4))
    # Turret(s)
    for tx in range(w//4, w, w//3):
        pygame.draw.circle(s, (60, 60, 70), (tx, h//4), 6)
        pygame.draw.rect(s, (45, 45, 55), (tx-2, 4, 4, h//4))
    # Superstructure
    pygame.draw.rect(s, (80, 85, 95), (w//2-8, 6, 16, h//4))
    # Wake lines
    for i in range(3):
        pygame.draw.line(s, (100, 160, 220, 120),
                         (2+i*4, h-3), (w//2, h+2), 1)
        pygame.draw.line(s, (100, 160, 220, 120),
                         (w-2-i*4, h-3), (w//2, h+2), 1)
    return s


class SmallWarship(BaseEnemy):
    score_value = 200
    hp_max      = 160

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._shoot_rate = 90
        self.drop_chance = 0.25

    def _build_image(self):
        w, h = 60, 40
        self.image = _build_warship_img(w, h, (90, 100, 112), (70, 80, 92))

    def _fire(self):
        from bullet.enemy_bullet import EnemyBullet, spawn_aimed
        if self._player_ref:
            spawn_aimed(self.rect.centerx, self.rect.top,
                        self._player_ref.rect.centerx,
                        self._player_ref.rect.centery,
                        self._bullet_group, speed=ENEMY_BULLET_SPEED - 1)
        else:
            self._bullet_group.add(EnemyBullet(self.rect.centerx, self.rect.top, vy=-ENEMY_BULLET_SPEED))


class MediumWarship(BaseEnemy):
    score_value = 350
    hp_max      = 320

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._shoot_rate = 65
        self.drop_chance = 0.35

    def _build_image(self):
        w, h = 90, 55
        self.image = _build_warship_img(w, h, (75, 85, 100), (55, 65, 80))

    def _fire(self):
        from bullet.enemy_bullet import EnemyBullet, spawn_aimed, spawn_spread
        for dx in (-20, 0, 20):
            self._bullet_group.add(
                EnemyBullet(self.rect.centerx + dx, self.rect.top, vy=-ENEMY_BULLET_SPEED))
        if self._player_ref:
            spawn_aimed(self.rect.centerx, self.rect.top,
                        self._player_ref.rect.centerx,
                        self._player_ref.rect.centery,
                        self._bullet_group, speed=ENEMY_BULLET_SPEED)


class LargeWarship(BaseEnemy):
    score_value = 500
    hp_max      = 600

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._shoot_rate = 50
        self.drop_chance = 0.50

    def _build_image(self):
        w, h = 130, 75
        self.image = _build_warship_img(w, h, (60, 70, 85), (42, 52, 68))

    def _fire(self):
        from bullet.enemy_bullet import EnemyBullet, spawn_aimed, spawn_spread
        spawn_spread(self.rect.centerx, self.rect.top,
                     self._bullet_group, count=5, speed=ENEMY_BULLET_SPEED - 1,
                     offset=0)
        if self._player_ref:
            spawn_aimed(self.rect.centerx, self.rect.top,
                        self._player_ref.rect.centerx,
                        self._player_ref.rect.centery,
                        self._bullet_group, speed=ENEMY_BULLET_SPEED + 1)


# ─────────────────────────────────────────────────────────────
#  Ground Turret — fixed position, rotates to aim
# ─────────────────────────────────────────────────────────────
class GroundTurret(BaseEnemy):
    score_value = SCORE_MEDIUM_ENEMY
    hp_max      = 60

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._shoot_rate = 70

    def _build_image(self):
        w, h = 28, 28
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.circle(s, DARK_GRAY, (14, 14), 13)
        pygame.draw.circle(s, (90, 90, 90), (14, 14), 9)
        pygame.draw.rect(s, (60, 60, 60), (11, 2, 6, 14))  # barrel
        self.image = s

    def _fire(self):
        from bullet.enemy_bullet import spawn_aimed, EnemyBullet
        if self._player_ref:
            spawn_aimed(self.rect.centerx, self.rect.top,
                        self._player_ref.rect.centerx,
                        self._player_ref.rect.centery,
                        self._bullet_group, speed=ENEMY_BULLET_SPEED + 1)
        else:
            self._bullet_group.add(EnemyBullet(self.rect.centerx, self.rect.top, vy=-ENEMY_BULLET_SPEED))


# ─────────────────────────────────────────────────────────────
#  Item drop  (defined here to avoid circular imports)
# ─────────────────────────────────────────────────────────────
class PowerUpItem(pygame.sprite.Sprite):
    """Collectible item dropped by enemies."""

    TYPES = ['ENERGY', 'WEAPON', 'BOMB', 'OPTION']
    COLOURS = {
        'ENERGY': (50, 220, 80),
        'WEAPON': (255, 200, 30),
        'BOMB':   (255, 80, 30),
        'OPTION': (80, 180, 255),
    }

    def __init__(self, x, y, item_type=None):
        super().__init__()
        self.item_type = item_type or random.choice(self.TYPES[:2])  # bias toward useful items
        col = self.COLOURS[self.item_type]

        w = h = 22
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (*col, 200), (w//2, h//2), w//2 - 1)
        pygame.draw.circle(self.image, WHITE, (w//2, h//2), 5)
        # Label letter
        font = pygame.font.SysFont('Arial', 11, bold=True)
        lbl  = font.render(self.item_type[0], True, (0, 0, 0))
        self.image.blit(lbl, (w//2 - lbl.get_width()//2, h//2 - lbl.get_height()//2))

        self.rect  = self.image.get_rect(center=(x, y))
        self._vy   = 2.5
        self._t    = 0

    def update(self):
        self._t     += 1
        self.rect.y += self._vy
        # Slight hover wobble
        self.rect.x += math.sin(self._t * 0.1) * 0.8
        if self.rect.top > SCREEN_HEIGHT + 10:
            self.kill()

    def apply(self, player):
        from config import ENERGY_ITEM_AMOUNT, PLAYER_BOMB_COUNT
        if self.item_type == 'ENERGY':
            player.energy.recover(ENERGY_ITEM_AMOUNT)
        elif self.item_type == 'WEAPON':
            player.weapon.cycle_weapon()
        elif self.item_type == 'BOMB':
            player.bomb_count = min(player.bomb_count + 1, PLAYER_BOMB_COUNT + 2)
        elif self.item_type == 'OPTION':
            player.options.add_option()


# ─────────────────────────────────────────────────────────────
#  Long Battleship — slow-moving long ship with 3 active turrets
# ─────────────────────────────────────────────────────────────
class LongBattleship(BaseEnemy):
    score_value = 800
    hp_max      = 600

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._shoot_rate = 70
        self.drop_chance = 0.50
        self._t = 0

    def _build_image(self):
        w, h = 80, 240
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)

        # Hull shape (pointed prow at top, tapered stern at bottom)
        hull_pts = [
            (w // 2, 4),               # Nose/prow (top)
            (w - 6, 30),
            (w - 4, h - 40),
            (w // 2 + 10, h - 4),     # Stern (bottom)
            (w // 2 - 10, h - 4),
            (4, h - 40),
            (6, 30),
        ]
        pygame.draw.polygon(self.image, (60, 65, 75), hull_pts)

        # Deck area (gray-brown plates)
        deck_pts = [
            (w // 2, 12),
            (w - 10, 32),
            (w - 8, h - 42),
            (w // 2 + 6, h - 8),
            (w // 2 - 6, h - 8),
            (8, h - 42),
            (10, 32),
        ]
        pygame.draw.polygon(self.image, (100, 90, 90), deck_pts)

        # Superstructure / bridge in center
        pygame.draw.rect(self.image, (45, 50, 60), (w // 2 - 14, h // 2 - 25, 28, 50))
        pygame.draw.rect(self.image, (75, 80, 90), (w // 2 - 10, h // 2 - 20, 20, 40))
        # Chimneys / Funnels
        pygame.draw.circle(self.image, (30, 30, 30), (w // 2, h // 2 - 10), 5)
        pygame.draw.circle(self.image, (30, 30, 30), (w // 2, h // 2 + 10), 5)
        # Windows on bridge
        pygame.draw.rect(self.image, (0, 180, 255), (w // 2 - 8, h // 2 - 18, 16, 4))

        # Wake lines at stern
        pygame.draw.line(self.image, (200, 220, 255, 150), (w // 2 - 8, h - 4), (w // 2 - 20, h + 15), 2)
        pygame.draw.line(self.image, (200, 220, 255, 150), (w // 2 + 8, h - 4), (w // 2 + 20, h + 15), 2)

        self.base_image = self.image.copy()

    def update(self):
        # Long battleship scrolls slowly downward
        self.rect.y += 1.0
        self._t += 1
        self._try_shoot()

        # Draw dynamic turrets onto image
        self.image = self.base_image.copy()
        self._draw_turrets()

        if (self.rect.top > SCREEN_HEIGHT + 100
                or self.rect.right < -100 or self.rect.left > SCREEN_WIDTH + 100):
            self.kill()

    def _draw_turrets(self):
        px, py = SCREEN_WIDTH // 2, SCREEN_HEIGHT - 200
        if self._player_ref and self._player_ref.alive():
            px, py = self._player_ref.rect.centerx, self._player_ref.rect.centery

        dx = px - self.rect.centerx
        dy = py - self.rect.centery
        angle = math.atan2(dy, dx)

        # Three turret positions: front, mid, rear
        t_positions = [
            (40, 50, self.hp > 400),
            (40, 95, True),
            (40, 190, self.hp > 200),
        ]

        for tx, ty, active in t_positions:
            base_color = (40, 45, 50) if active else (25, 25, 25)
            pygame.draw.circle(self.image, base_color, (tx, ty), 10)
            pygame.draw.circle(self.image, (90, 90, 95) if active else (40, 40, 40), (tx, ty), 7)

            bx = tx + math.cos(angle) * 16
            by = ty + math.sin(angle) * 16
            barrel_color = (30, 30, 32) if active else (15, 15, 15)
            pygame.draw.line(self.image, barrel_color, (tx, ty), (bx, by), 3)

    def _fire(self):
        from bullet.enemy_bullet import EnemyBullet, spawn_aimed, spawn_spread
        px, py = SCREEN_WIDTH // 2, SCREEN_HEIGHT - 200
        if self._player_ref:
            px, py = self._player_ref.rect.centerx, self._player_ref.rect.centery

        if self.hp > 400:
            spawn_aimed(self.rect.centerx, self.rect.top + 50, px, py, self._bullet_group, speed=ENEMY_BULLET_SPEED)

        spawn_spread(self.rect.centerx, self.rect.top + 95, self._bullet_group, count=3, speed=ENEMY_BULLET_SPEED - 1, offset=self._t * 5)

        if self.hp > 200:
            spawn_aimed(self.rect.centerx, self.rect.top + 190, px, py, self._bullet_group, speed=ENEMY_BULLET_SPEED + 1)


# ─── Factory ─────────────────────────────────────────────────
ENEMY_CLASSES = {
    'SmallFighter':  SmallFighter,
    'MediumFighter': MediumFighter,
    'HeavyFighter':  HeavyFighter,
    'GroundTurret':  GroundTurret,
    'SmallWarship':  SmallWarship,
    'MediumWarship': MediumWarship,
    'LargeWarship':  LargeWarship,
    'LongBattleship': LongBattleship,
}


def make_enemy(type_name: str, x, y, bullet_group=None,
               player_ref=None, pattern='straight', pattern_kwargs=None):
    cls = ENEMY_CLASSES.get(type_name, SmallFighter)
    return cls(x, y, pattern=pattern, pattern_kwargs=pattern_kwargs or {},
               bullet_group=bullet_group, player_ref=player_ref)
