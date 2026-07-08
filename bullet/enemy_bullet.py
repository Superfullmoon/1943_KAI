# ============================================================
#  bullet/enemy_bullet.py  —  Enemy projectile types
# ============================================================
import pygame, math
from config import SCREEN_WIDTH, SCREEN_HEIGHT, ENEMY_BULLET_SPEED, ENEMY_BULLET_FAST, RED, ORANGE, YELLOW, WHITE


class EnemyBullet(pygame.sprite.Sprite):
    """Standard single downward bullet."""
    DAMAGE = 15

    def __init__(self, x, y, vx=0, vy=ENEMY_BULLET_SPEED, colour=RED):
        super().__init__()
        self.image = pygame.Surface((6, 14), pygame.SRCALPHA)
        pygame.draw.rect(self.image, colour, (1, 0, 4, 14))
        pygame.draw.rect(self.image, ORANGE, (2, 2, 2,  8))
        self.rect   = self.image.get_rect(center=(x, y))
        self.vx, self.vy = vx, vy
        self.damage = self.DAMAGE

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if (self.rect.top > SCREEN_HEIGHT + 10 or self.rect.bottom < -10
                or self.rect.left > SCREEN_WIDTH + 10 or self.rect.right < -10):
            self.kill()


class AimedBullet(pygame.sprite.Sprite):
    """Aimed bullet that travels toward the player's last position."""
    DAMAGE = 18

    def __init__(self, x, y, target_x, target_y, speed=ENEMY_BULLET_SPEED):
        super().__init__()
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy) or 1
        self.vx = dx / dist * speed
        self.vy = dy / dist * speed

        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(self.image, ORANGE, (4, 4), 4)
        pygame.draw.circle(self.image, YELLOW, (4, 4), 2)
        self.rect   = self.image.get_rect(center=(x, y))
        self.damage = self.DAMAGE

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if (self.rect.top > SCREEN_HEIGHT + 10 or self.rect.bottom < -10
                or self.rect.left > SCREEN_WIDTH + 10 or self.rect.right < -10):
            self.kill()


class SpreadBullet(pygame.sprite.Sprite):
    """One bullet from a radial spread burst."""
    DAMAGE = 12

    def __init__(self, x, y, angle_deg, speed=ENEMY_BULLET_SPEED - 1):
        super().__init__()
        rad = math.radians(angle_deg)
        self.vx = math.cos(rad) * speed
        self.vy = math.sin(rad) * speed
        self.image = pygame.Surface((7, 7), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 80, 0), (3, 3), 3)
        self.rect   = self.image.get_rect(center=(x, y))
        self.damage = self.DAMAGE

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if (self.rect.top > SCREEN_HEIGHT + 10 or self.rect.bottom < -10
                or self.rect.left > SCREEN_WIDTH + 10 or self.rect.right < -10):
            self.kill()


def spawn_spread(x, y, group, count=8, speed=ENEMY_BULLET_SPEED - 1, offset=0):
    """Spawn a radial spread of bullets."""
    for i in range(count):
        angle = offset + (360 / count) * i
        group.add(SpreadBullet(x, y, angle, speed))


def spawn_aimed(x, y, px, py, group, speed=ENEMY_BULLET_SPEED):
    group.add(AimedBullet(x, y, px, py, speed))
