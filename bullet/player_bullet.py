# ============================================================
#  bullet/player_bullet.py  —  Player projectile types
# ============================================================
import pygame
import math
from config import (SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_BULLET_SPEED,
                    YELLOW, CYAN, WHITE, ORANGE, GREEN)


class VulcanBullet(pygame.sprite.Sprite):
    """Fast single bullet, the default weapon."""
    DAMAGE = 40

    def __init__(self, x, y, vy=-PLAYER_BULLET_SPEED, vx=0):
        super().__init__()
        self.image = pygame.Surface((5, 18), pygame.SRCALPHA)
        # Glowing yellow bolt
        pygame.draw.rect(self.image, YELLOW, (1, 0, 3, 18))
        pygame.draw.rect(self.image, WHITE,  (2, 2, 1, 12))
        self.rect   = self.image.get_rect(center=(x, y))
        self.vx, self.vy = vx, vy
        self.damage = self.DAMAGE

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if (self.rect.bottom < -10 or self.rect.top > SCREEN_HEIGHT + 10
                or self.rect.right < -10 or self.rect.left > SCREEN_WIDTH + 10):
            self.kill()


class ShotgunPellet(pygame.sprite.Sprite):
    """Short-range spread pellet."""
    DAMAGE = 25

    def __init__(self, x, y, angle_deg):
        super().__init__()
        rad = math.radians(angle_deg)
        speed = PLAYER_BULLET_SPEED * 0.75
        self.vx = math.sin(rad) * speed
        self.vy = -math.cos(rad) * speed
        self.image = pygame.Surface((7, 7), pygame.SRCALPHA)
        pygame.draw.circle(self.image, ORANGE, (3, 3), 3)
        pygame.draw.circle(self.image, YELLOW, (3, 3), 2)
        self.rect   = self.image.get_rect(center=(x, y))
        self.damage = self.DAMAGE
        self._life  = 40   # limited range

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self._life  -= 1
        if (self._life <= 0 or self.rect.bottom < -10
                or self.rect.right < -10 or self.rect.left > SCREEN_WIDTH + 10):
            self.kill()


class LaserBeam(pygame.sprite.Sprite):
    """Tall, narrow laser beam — hits multiple enemies."""
    DAMAGE = 60

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((8, 48), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (0, 255, 255, 160), (3, 0, 2, 48))
        pygame.draw.rect(self.image, (200, 255, 255, 80), (0, 0, 8, 48))
        self.rect   = self.image.get_rect(center=(x, y))
        self.vy     = -PLAYER_BULLET_SPEED - 4
        self.damage = self.DAMAGE

    def update(self):
        self.rect.y += self.vy
        if self.rect.bottom < -10:
            self.kill()


class WideBullet(pygame.sprite.Sprite):
    """Wide horizontal spread shot."""
    DAMAGE = 30

    def __init__(self, x, y, vx=0):
        super().__init__()
        self.image = pygame.Surface((14, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (50, 255, 100), (0, 1, 14, 8))
        pygame.draw.ellipse(self.image, WHITE,           (4, 3, 6,  4))
        self.rect   = self.image.get_rect(center=(x, y))
        self.vx     = vx
        self.vy     = -PLAYER_BULLET_SPEED + 3
        self.damage = self.DAMAGE

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if (self.rect.bottom < -10 or self.rect.top > SCREEN_HEIGHT + 10
                or self.rect.right < -20 or self.rect.left > SCREEN_WIDTH + 20):
            self.kill()


def spawn_weapon_bullets(weapon_type, x, y, group, option_list=None):
    """Factory — spawn the correct bullet(s) for the current weapon.

    option_list: list of option-drone (x, y) positions that also shoot.
    """
    from config import WEAPON_VULCAN, WEAPON_SHOTGUN, WEAPON_LASER, WEAPON_WIDE

    fire_positions = [(x, y)]
    if option_list:
        fire_positions += [(ox, oy) for ox, oy in option_list]

    for fx, fy in fire_positions:
        if weapon_type == WEAPON_VULCAN:
            group.add(VulcanBullet(fx, fy))

        elif weapon_type == WEAPON_SHOTGUN:
            for ang in (-20, -10, 0, 10, 20):
                group.add(ShotgunPellet(fx, fy, ang))

        elif weapon_type == WEAPON_LASER:
            group.add(LaserBeam(fx, fy))

        elif weapon_type == WEAPON_WIDE:
            group.add(WideBullet(fx, fy, vx=-3))
            group.add(WideBullet(fx, fy, vx= 0))
            group.add(WideBullet(fx, fy, vx= 3))
