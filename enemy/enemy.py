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
class SmallFighter(BaseEnemy):
    score_value = SCORE_SMALL_ENEMY
    hp_max      = 30

    def _build_image(self):
        w, h = 34, 34
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        # Wings
        pygame.draw.polygon(s, (180, 30, 30), [(0, 20), (34, 20), (22, 30), (12, 30)])
        # Body
        pygame.draw.ellipse(s, (210, 40, 40), (11, 4, 12, 26))
        # Cockpit
        pygame.draw.ellipse(s, (80, 80, 110), (14, 8, 6, 9))
        # Engine glow
        pygame.draw.ellipse(s, (255, 180, 50, 180), (14, 28, 6, 4))
        self.image = s


# ─────────────────────────────────────────────────────────────
#  Medium Fighter (Type B — orange)
# ─────────────────────────────────────────────────────────────
class MediumFighter(BaseEnemy):
    score_value = SCORE_MEDIUM_ENEMY
    hp_max      = 80

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._shoot_rate = 60
        self.drop_chance = 0.22

    def _build_image(self):
        w, h = 44, 44
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(s, (200, 100, 20), [(0, 26), (44, 26), (30, 38), (14, 38)])
        pygame.draw.ellipse(s, (230, 120, 30), (14, 4, 16, 36))
        pygame.draw.ellipse(s, (80, 80, 100), (18, 8, 8, 12))
        pygame.draw.ellipse(s, (255, 200, 80, 180), (18, 38, 8, 5))
        self.image = s

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
#  Large Heavy Fighter (Type C — dark green)
# ─────────────────────────────────────────────────────────────
class HeavyFighter(BaseEnemy):
    score_value = SCORE_LARGE_ENEMY
    hp_max      = 180

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._shoot_rate = 45
        self.drop_chance = 0.40

    def _build_image(self):
        w, h = 56, 52
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.polygon(s, (30, 120, 40), [(0, 30), (56, 30), (38, 46), (18, 46)])
        pygame.draw.ellipse(s, (40, 150, 50), (18, 4, 20, 44))
        pygame.draw.ellipse(s, (20, 60, 30), (22, 8, 12, 16))
        pygame.draw.ellipse(s, (100, 255, 120, 160), (22, 44, 12, 6))
        self.image = s

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
}


def make_enemy(type_name: str, x, y, bullet_group=None,
               player_ref=None, pattern='straight', pattern_kwargs=None):
    cls = ENEMY_CLASSES.get(type_name, SmallFighter)
    return cls(x, y, pattern=pattern, pattern_kwargs=pattern_kwargs or {},
               bullet_group=bullet_group, player_ref=player_ref)
