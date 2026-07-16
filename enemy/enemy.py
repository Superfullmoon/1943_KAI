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
    """Build a WWII-style enemy fighter procedurally (similar to Zero or twin-engine bombers in 1943)."""
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = w // 2, h // 2

    # ── Wings ───────────────────────────────────────────────
    wing_y = cy - 4
    pygame.draw.polygon(s, color_main,
                        [(0, wing_y + 4), (w, wing_y + 4),
                         (w - 6, wing_y - 4), (6, wing_y - 4)])

    # ── Twin Engines for medium/heavy fighters ──────────────
    if w >= 44:
        # Left wing engine
        pygame.draw.ellipse(s, (40, 40, 40), (w//4 - 5, wing_y - 8, 10, 16))
        pygame.draw.ellipse(s, color_main, (w//4 - 4, wing_y - 6, 8, 12))
        # Right wing engine
        pygame.draw.ellipse(s, (40, 40, 40), (3*w//4 - 5, wing_y - 8, 10, 16))
        pygame.draw.ellipse(s, color_main, (3*w//4 - 4, wing_y - 6, 8, 12))

        # Twin propeller hubs (yellow)
        pygame.draw.circle(s, (240, 200, 10), (w//4, wing_y - 8), 3)
        pygame.draw.circle(s, (240, 200, 10), (3*w//4, wing_y - 8), 3)

    # ── Fuselage ─────────────────────────────────────────────
    pygame.draw.ellipse(s, color_main, (cx - 5, 2, 10, h - 4))
    pygame.draw.ellipse(s, (min(color_main[0]+40, 255),
                            min(color_main[1]+40, 255),
                            min(color_main[2]+20, 255)),
                        (cx - 3, 4, 6, h - 10))

    # ── Engine cowling (front propeller) ───────────────────
    pygame.draw.circle(s, (40, 40, 40), (cx, h - 6), 6)
    pygame.draw.circle(s, (80, 80, 80), (cx, h - 6), 4)
    # Spinning propeller line (yellow)
    pygame.draw.line(s, (240, 200, 10), (cx - 10, h - 6), (cx + 10, h - 6), 1)

    # ── Cockpit ─────────────────────────────────────────────
    pygame.draw.ellipse(s, (50, 100, 180), (cx - 4, cy - 6, 8, 12))
    pygame.draw.ellipse(s, (130, 190, 255, 180), (cx - 3, cy - 5, 6, 8))

    # ── WWII Hinomaru markings on wings (red circles) ───────
    # Left wing red circle with white outline
    pygame.draw.circle(s, (255, 255, 255), (w//6 + 2, wing_y), 6)
    pygame.draw.circle(s, (200, 30, 30), (w//6 + 2, wing_y), 4)
    # Right wing red circle with white outline
    pygame.draw.circle(s, (255, 255, 255), (5*w//6 - 2, wing_y), 6)
    pygame.draw.circle(s, (200, 30, 30), (5*w//6 - 2, wing_y), 4)

    # ── Horizontal stabilizer (at the top/rear of surface) ──
    pygame.draw.polygon(s, (min(color_main[0]+20, 255),
                            min(color_main[1]+20, 255),
                            min(color_main[2]+10, 255)),
                        [(cx - 12, 6), (cx + 12, 6), (cx + 8, 12), (cx - 8, 12)])
    return s


def _get_enemy_img(w, h, color_main=(60, 120, 60)):
    return _build_enemy_img(w, h, color_main)

class SmallFighter(BaseEnemy):
    score_value = SCORE_SMALL_ENEMY
    hp_max      = 30

    def _build_image(self):
        w, h = 34, 34
        self.image = _get_enemy_img(w, h, color_main=(60, 120, 60))


# ─────────────────────────────────────────────────────────────
#  Medium Fighter (Type B — dark blue)
# ─────────────────────────────────────────────────────────────
class MediumFighter(BaseEnemy):
    score_value = SCORE_MEDIUM_ENEMY
    hp_max      = 120

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
    hp_max      = 240

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
    hp_max      = 300

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
    hp_max      = 600

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
    hp_max      = 1000

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
#  Long Warship — elongated warship with multiple turrets
# ─────────────────────────────────────────────────────────────
class LongWarship(BaseEnemy):
    score_value = 1500
    hp_max      = 800

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._shoot_rate = 45
        self.drop_chance = 0.60

    def _build_image(self):
        w, h = 180, 50
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        hull_col = (50, 60, 75)
        deck_col = (35, 45, 55)

        # Hull
        hull_pts = [(10, h//3), (w-10, h//3), (w-5, h-4), (5, h-4)]
        pygame.draw.polygon(self.image, hull_col, hull_pts)
        # Deck
        pygame.draw.rect(self.image, deck_col, (15, 4, w-30, h//3 + 4))

        # 4 Turrets
        for tx in (35, 75, 115, 155):
            pygame.draw.circle(self.image, (40, 40, 50), (tx, h//4), 8)
            pygame.draw.rect(self.image, (30, 30, 40), (tx-2, 2, 4, h//4))

        # Superstructure
        pygame.draw.rect(self.image, (70, 75, 85), (w//2-20, 6, 40, h//4))
        pygame.draw.rect(self.image, (100, 105, 115), (w//2-10, 2, 20, h//4 - 2))

        # Wake lines
        for i in range(5):
            pygame.draw.line(self.image, (120, 180, 240, 140),
                             (4+i*6, h-3), (w//2, h+2), 1)
            pygame.draw.line(self.image, (120, 180, 240, 140),
                             (w-4-i*6, h-3), (w//2, h+2), 1)

    def _fire(self):
        from bullet.enemy_bullet import EnemyBullet, spawn_aimed, spawn_spread
        from config import ENEMY_BULLET_SPEED
        spawn_spread(self.rect.centerx, self.rect.top,
                     self._bullet_group, count=6, speed=ENEMY_BULLET_SPEED - 1,
                     offset=random.randint(0, 45))
        if self._player_ref:
            spawn_aimed(self.rect.centerx - 55, self.rect.top,
                        self._player_ref.rect.centerx,
                        self._player_ref.rect.centery,
                        self._bullet_group, speed=ENEMY_BULLET_SPEED)
            spawn_aimed(self.rect.centerx + 55, self.rect.top,
                        self._player_ref.rect.centerx,
                        self._player_ref.rect.centery,
                        self._bullet_group, speed=ENEMY_BULLET_SPEED)


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


# ─── Factory ─────────────────────────────────────────────────
ENEMY_CLASSES = {
    'SmallFighter':  SmallFighter,
    'MediumFighter': MediumFighter,
    'HeavyFighter':  HeavyFighter,
    'GroundTurret':  GroundTurret,
    'SmallWarship':  SmallWarship,
    'MediumWarship': MediumWarship,
    'LargeWarship':  LargeWarship,
    'LongWarship':   LongWarship,
}


def make_enemy(type_name: str, x, y, bullet_group=None,
               player_ref=None, pattern='straight', pattern_kwargs=None):
    cls = ENEMY_CLASSES.get(type_name, SmallFighter)
    return cls(x, y, pattern=pattern, pattern_kwargs=pattern_kwargs or {},
               bullet_group=bullet_group, player_ref=player_ref)
