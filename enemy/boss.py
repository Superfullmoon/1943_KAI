# ============================================================
#  enemy/boss.py  —  Boss base class with multi-part HP
# ============================================================
import pygame, math
from config import (SCREEN_WIDTH, DARK_GRAY, GRAY, WHITE, RED, ORANGE, YELLOW,
                    SCORE_BOSS_PART, SCORE_BOSS, ENEMY_BULLET_SPEED)


class BossComponent(pygame.sprite.Sprite):
    """A destroyable sub-component of the boss (turret, antenna, etc.)."""

    def __init__(self, parent, offset_x, offset_y, hp, colour, radius=14):
        super().__init__()
        self.parent   = parent
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.hp       = hp
        self.hp_max   = hp
        self._colour  = colour
        self._radius  = radius
        self.score_value = SCORE_BOSS_PART

        self.image = self._build(colour, radius)
        self.rect  = self.image.get_rect()
        self.mask  = pygame.mask.from_surface(self.image)
        self._destroyed = False

    @staticmethod
    def _build(colour, radius):
        r  = radius
        s  = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, colour,         (r, r), r)
        pygame.draw.circle(s, (255, 255, 255), (r, r), r, 2)
        pygame.draw.circle(s, (50, 50, 50),   (r, r), r // 2)
        return s

    def sync(self):
        """Move to parent body position + offset."""
        self.rect.centerx = self.parent.rect.centerx + self.offset_x
        self.rect.centery = self.parent.rect.centery + self.offset_y

    def take_damage(self, amount):
        if self._destroyed:
            return False
        self.hp -= amount
        if self.hp <= 0:
            self._destroyed = True
            self.kill()
            return True
        return False

    def drop_item(self):
        pass


class BossBase(pygame.sprite.Sprite):
    """Abstract boss: subclasses provide `image` and component list."""

    score_value = SCORE_BOSS
    hp_max      = 1200

    def __init__(self, x, y, bullet_group, player_ref):
        super().__init__()
        self.hp          = self.hp_max
        self._bullet_group = bullet_group
        self._player_ref   = player_ref
        self._t            = 0
        self._shoot_cd     = 120
        self._phase        = 1        # increases as hp decreases
        self.components = []
        self.score_value = SCORE_BOSS
        self.drop_item   = None

        self._build_image()
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

    def _build_image(self):
        """Subclasses override."""
        w, h = 160, 80
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, GRAY, (0, 0, w, h))

    def update(self):
        self._t += 1
        self._ai_move()
        for comp in self.components:
            comp.sync()
        self._update_phase()
        self._tick_shoot()

    def _ai_move(self):
        self.rect.x += math.sin(self._t * 0.015) * 1.2
        if self.rect.centery < 260:
            self.rect.y += 1.5

    def _update_phase(self):
        frac = self.hp / self.hp_max
        self._phase = 1 if frac > 0.5 else (2 if frac > 0.25 else 3)

    def _tick_shoot(self):
        self._shoot_cd -= 1
        rate = {1: 90, 2: 65, 3: 45}[self._phase]
        if self._shoot_cd <= 0:
            self._fire()
            self._shoot_cd = rate

    def _fire(self):
        from bullet.enemy_bullet import EnemyBullet, spawn_aimed, spawn_spread
        # Phase 1: aimed shot
        if self._player_ref:
            spawn_aimed(self.rect.centerx, self.rect.bottom,
                        self._player_ref.rect.centerx,
                        self._player_ref.rect.centery,
                        self._bullet_group, speed=ENEMY_BULLET_SPEED + 1)
        # Phase 2+: add spread
        if self._phase >= 2:
            spawn_spread(self.rect.centerx, self.rect.centery,
                         self._bullet_group, count=6, speed=ENEMY_BULLET_SPEED - 1,
                         offset=self._t * 2)
        # Phase 3: extra fast aimed
        if self._phase >= 3 and self._player_ref:
            spawn_aimed(self.rect.centerx + 40, self.rect.bottom,
                        self._player_ref.rect.centerx,
                        self._player_ref.rect.centery,
                        self._bullet_group, speed=ENEMY_BULLET_SPEED + 3)
            spawn_aimed(self.rect.centerx - 40, self.rect.bottom,
                        self._player_ref.rect.centerx,
                        self._player_ref.rect.centery,
                        self._bullet_group, speed=ENEMY_BULLET_SPEED + 3)

    def take_damage(self, amount) -> bool:
        self.hp -= amount
        if self.hp <= 0:
            self.kill()
            return True
        return False

    @property
    def is_dead(self):
        return not self.alive()

    def draw_hp_bar(self, surface):
        """Render a red HP bar at the top of the screen."""
        bar_w = SCREEN_WIDTH - 40
        bar_h = 14
        bx, by = 20, 10
        pygame.draw.rect(surface, (60, 20, 20), (bx, by, bar_w, bar_h))
        fill = int(bar_w * max(0, self.hp / self.hp_max))
        pygame.draw.rect(surface, RED,    (bx, by, fill, bar_h))
        pygame.draw.rect(surface, ORANGE, (bx, by, fill, 5))
        pygame.draw.rect(surface, WHITE,  (bx, by, bar_w, bar_h), 1)
        font = pygame.font.SysFont('Arial', 12, bold=True)
        lbl  = font.render("BOSS", True, YELLOW)
        surface.blit(lbl, (bx + bar_w + 5, by))
