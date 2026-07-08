# ============================================================
#  effects/explosion.py  —  Explosion animation manager
# ============================================================
import pygame, random
from config import YELLOW, ORANGE, RED, WHITE, DARK_GRAY, DARK_BLUE


class ExplosionSprite(pygame.sprite.Sprite):
    """One animated explosion."""

    _FRAMES = {}  # class-level cache  {size: [surf, ...]}

    def __init__(self, x, y, size='small'):
        super().__init__()
        self._frames = self._get_frames(size)
        self._idx    = 0
        self.image   = self._frames[0]
        self.rect    = self.image.get_rect(center=(x, y))

    @classmethod
    def _get_frames(cls, size):
        if size in cls._FRAMES:
            return cls._FRAMES[size]
        r = {'small': 28, 'large': 52, 'huge': 80}[size]
        frames = []
        steps  = 12
        for i in range(steps):
            t    = i / (steps - 1)
            radius = int(r * (0.2 + 0.8 * t))
            surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            # Outer ring fades out
            alpha_out = int(255 * (1 - t))
            col_out   = (*ORANGE, alpha_out)
            pygame.draw.circle(surf, col_out, (r, r), radius)
            # Inner bright core
            if t < 0.6:
                alpha_in  = int(255 * (1 - t / 0.6))
                col_in    = (*YELLOW, alpha_in)
                pygame.draw.circle(surf, col_in, (r, r), max(2, radius // 2))
            # Smoke ring at end
            if t > 0.5:
                alpha_sm = int(180 * (t - 0.5) * 2)
                pygame.draw.circle(surf, (60, 60, 60, alpha_sm), (r, r), radius, 4)
            frames.append(surf)
        cls._FRAMES[size] = frames
        return frames

    def update(self):
        self._idx += 1
        if self._idx >= len(self._frames):
            self.kill()
            return
        cx, cy     = self.rect.center
        self.image = self._frames[self._idx]
        self.rect  = self.image.get_rect(center=(cx, cy))


class ExplosionManager:
    def __init__(self):
        self._group = pygame.sprite.Group()

    def spawn(self, x, y, size='small'):
        self._group.add(ExplosionSprite(x, y, size))
        # Extra sparks
        for _ in range(4 if size == 'small' else 10):
            self._group.add(_Spark(x, y))

    def update(self):
        self._group.update()

    def draw(self, surface):
        self._group.draw(surface)


class _Spark(pygame.sprite.Sprite):
    """Tiny flying spark particle."""

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 4), pygame.SRCALPHA)
        col = random.choice([YELLOW, ORANGE, WHITE])
        pygame.draw.circle(self.image, col, (2, 2), 2)
        self.rect = self.image.get_rect(center=(x, y))
        speed     = random.uniform(1.5, 5.0)
        angle     = random.uniform(0, 360)
        import math
        self.vx   = math.cos(math.radians(angle)) * speed
        self.vy   = math.sin(math.radians(angle)) * speed
        self._life = random.randint(15, 35)
        self._max  = self._life

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.vy      += 0.15   # gravity
        self._life   -= 1
        alpha = int(255 * self._life / self._max)
        self.image.set_alpha(alpha)
        if self._life <= 0:
            self.kill()
