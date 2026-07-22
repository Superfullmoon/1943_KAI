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
        self.image_base = self.image
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

        # Drop callback — set by StageManager
        self.drop_item = None

    def _build_image(self):
        """Override in subclasses."""
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(self.image, RED, (16, 16), 14)

    def update(self):
        old_center = self.rect.center
        self._move(self)
        self._try_shoot()

        # Smooth sprite rotation based on movement direction (planes only)
        is_plane = not any(isinstance(self, cls) for cls in [GroundTurret, SmallWarship, MediumWarship, LargeWarship, LongWarship])
        if is_plane and hasattr(self, 'image_base') and self.image_base:
            dx = self.rect.centerx - old_center[0]
            dy = self.rect.centery - old_center[1]
            if dx != 0 or dy != 0:
                angle = math.degrees(math.atan2(-dy, dx)) - 90
                # Rotate from original base image to avoid quality degradation
                self.image = pygame.transform.rotate(self.image_base, angle)
                cx, cy = self.rect.center
                self.rect = self.image.get_rect(center=(cx, cy))
                self.mask = pygame.mask.from_surface(self.image)

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
    cx = w // 2

    # 1. Outer Hull (Grey) - pointed bow at the top, tapered stern at the bottom
    hull_pts = [
        (cx, 0),                       # Bow tip
        (w - 2, h // 5),               # Upper right
        (w - 2, h - h // 8),           # Lower right
        (cx + w // 4, h),              # Bottom right stern
        (cx - w // 4, h),              # Bottom left stern
        (2, h - h // 8),               # Lower left
        (2, h // 5),                   # Upper left
    ]
    pygame.draw.polygon(s, hull_col, hull_pts)
    pygame.draw.polygon(s, (40, 42, 50), hull_pts, 2)

    # 2. Flight / Gun Deck (wooden brown or darker grey deck inside hull)
    deck_pts = [
        (cx, 4),
        (w - 5, h // 5 + 2),
        (w - 5, h - h // 8 - 2),
        (cx + w // 4 - 3, h - 3),
        (cx - w // 4 + 3, h - 3),
        (5, h - h // 8 - 2),
        (5, h // 5 + 2),
    ]
    pygame.draw.polygon(s, deck_col, deck_pts)

    # 3. Superstructure / Bridge (command deck in the middle)
    bridge_y = h // 2 - h // 10
    bridge_h = h // 5
    bridge_w = int(w * 0.55)
    # Layer 1: lower bridge base
    pygame.draw.rect(s, (100, 105, 115), (cx - bridge_w//2, bridge_y, bridge_w, bridge_h))
    pygame.draw.rect(s, (30, 32, 40), (cx - bridge_w//2, bridge_y, bridge_w, bridge_h), 1)

    # Layer 2: upper command tower with windows
    win_w = int(bridge_w * 0.7)
    win_h = max(4, h // 12)
    pygame.draw.rect(s, (120, 125, 135), (cx - win_w//2, bridge_y + 4, win_w, win_h))
    pygame.draw.rect(s, (30, 100, 160), (cx - win_w//3, bridge_y + 5, win_w//2 + 2, max(2, win_h - 4))) # Blue window stripe

    # Smokestack (on top of bridge)
    pygame.draw.ellipse(s, (50, 52, 58), (cx - 4, bridge_y + bridge_h - 8, 8, 10))
    pygame.draw.circle(s, (20, 20, 22), (cx, bridge_y + bridge_h - 3), 2)

    # 4. Center-line Main Gun Turrets
    turret_positions = []
    if h >= 130:
        turret_positions = [h // 6, h // 3 - 10, h - h // 5]
    elif h >= 90:
        turret_positions = [h // 4 - 5, h - h // 4]
    else:
        turret_positions = [h // 3]

    for ty in turret_positions:
        # Turret base circle
        pygame.draw.circle(s, (50, 52, 60), (cx, ty), max(4, w // 4))
        pygame.draw.circle(s, (30, 32, 40), (cx, ty), max(4, w // 4), 1)
        # Gun barrel pointing upward
        pygame.draw.rect(s, (30, 30, 35), (cx - 1, ty - max(6, w // 3), 2, max(6, w // 3)))

    # 5. Rear Propulsion Wake Lines (White foaming waves at stern)
    for i in range(3):
        wy = h - 2 + i * 3
        pygame.draw.line(s, (230, 240, 255, 150), (cx - w//4 + i*2, wy), (cx + w//4 - i*2, wy), 1)

    return s


class SmallWarship(BaseEnemy):
    score_value = 200
    hp_max      = 300

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._shoot_rate = 90
        self.drop_chance = 0.25

    def _build_image(self):
        w, h = 32, 70
        self.image = _build_warship_img(w, h, (100, 105, 115), (75, 80, 90))

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
        w, h = 44, 100
        self.image = _build_warship_img(w, h, (90, 95, 105), (65, 70, 80))

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
        w, h = 56, 140
        self.image = _build_warship_img(w, h, (80, 85, 95), (55, 60, 70))

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
        w, h = 48, 190
        # Let's draw an extremely detailed long WWII battleship!
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        cx = w // 2

        # 1. Outer Hull (Grey) with pointed bow and stern
        hull_pts = [
            (cx, 0),
            (w - 2, h // 8),
            (w - 2, h - h // 12),
            (cx + w // 4, h),
            (cx - w // 4, h),
            (2, h - h // 12),
            (2, h // 8),
        ]
        pygame.draw.polygon(self.image, (70, 75, 85), hull_pts)
        pygame.draw.polygon(self.image, (30, 32, 40), hull_pts, 2)

        # 2. Deck (wooden tan/brown color)
        deck_pts = [
            (cx, 4),
            (w - 5, h // 8 + 2),
            (w - 5, h - h // 12 - 2),
            (cx + w // 4 - 3, h - 3),
            (cx - w // 4 + 3, h - 3),
            (5, h - h // 12 - 2),
            (5, h // 8 + 2),
        ]
        pygame.draw.polygon(self.image, (135, 115, 95), deck_pts)

        # 3. Massive tiered superstructure / Command bridge (midship)
        bridge_y = h // 2 - 25
        bridge_h = 45
        # Tier 1
        pygame.draw.rect(self.image, (90, 95, 105), (cx - 15, bridge_y, 30, bridge_h))
        pygame.draw.rect(self.image, (30, 32, 40), (cx - 15, bridge_y, 30, bridge_h), 1)
        # Tier 2 (upper command deck)
        pygame.draw.rect(self.image, (110, 115, 125), (cx - 10, bridge_y + 8, 20, 20))
        # Blue command windows
        pygame.draw.rect(self.image, (30, 100, 180), (cx - 7, bridge_y + 12, 14, 4))
        # Smokestacks
        pygame.draw.ellipse(self.image, (45, 45, 50), (cx - 4, bridge_y + 30, 8, 12))
        pygame.draw.circle(self.image, (15, 15, 18), (cx, bridge_y + 36), 3)

        # 4. Center-line Dual Main Gun Turrets (4 in total: 2 at bow, 2 at stern)
        turrets_y = [h // 6, h // 3, h - h // 4, h - h // 8]
        for ty in turrets_y:
            # Turret base circle
            pygame.draw.circle(self.image, (50, 52, 60), (cx, ty), 10)
            pygame.draw.circle(self.image, (25, 25, 30), (cx, ty), 10, 1)
            # Dual barrels pointing upward
            pygame.draw.rect(self.image, (20, 20, 25), (cx - 3, ty - 14, 2, 14))
            pygame.draw.rect(self.image, (20, 20, 25), (cx + 1, ty - 14, 2, 14))

        # 5. Stern wake
        for i in range(4):
            wy = h - 2 + i * 3
            pygame.draw.line(self.image, (230, 240, 255, 160), (cx - 10 + i, wy), (cx + 10 - i, wy), 1)

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

    TYPES = ['ENERGY', 'WEAPON', 'BOMB', 'OPTION', 'VULCAN', 'SHOTGUN', 'LASER', 'WIDE']
    COLOURS = {
        'ENERGY': (50, 220, 80),
        'WEAPON': (255, 200, 30),
        'BOMB':   (255, 80, 30),
        'OPTION': (80, 180, 255),
        'VULCAN': (255, 200, 30),
        'SHOTGUN': (200, 100, 255),
        'LASER': (100, 255, 255),
        'WIDE': (255, 100, 100)
    }

    def __init__(self, x, y, item_type=None):
        super().__init__()
        self.item_type = item_type or random.choice(self.TYPES[:2])  # bias toward useful items
        col = self.COLOURS.get(self.item_type, (255, 255, 255))

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

    def cycle_type(self):
        """Cycles the item type when hit by a player bullet, matching the original 1943."""
        # Find index dynamically or fallback to 0
        try:
            idx = (self.TYPES.index(self.item_type) + 1) % len(self.TYPES)
        except ValueError:
            idx = 0
        self.item_type = self.TYPES[idx]
        col = self.COLOURS.get(self.item_type, (255, 255, 255))

        w = h = 22
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (*col, 220), (w//2, h//2), w//2 - 1)
        pygame.draw.circle(self.image, WHITE, (w//2, h//2), 5)
        # Label letter
        font = pygame.font.SysFont('Arial', 11, bold=True)
        lbl  = font.render(self.item_type[0], True, (0, 0, 0))
        self.image.blit(lbl, (w//2 - lbl.get_width()//2, h//2 - lbl.get_height()//2))

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
        elif self.item_type in ('VULCAN', 'SHOTGUN', 'LASER', 'WIDE'):
            player.weapon.current = self.item_type
            player.weapon.level = 1
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
