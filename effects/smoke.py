# ============================================================
#  effects/smoke.py  —  Smoke trail particles
# ============================================================
import pygame, random, math


class SmokeParticle(pygame.sprite.Sprite):
    def __init__(self, x, y, colour=(100, 100, 100)):
        super().__init__()
        r          = random.randint(4, 10)
        self.image = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (*colour, 180), (r, r), r)
        self.rect  = self.image.get_rect(center=(x, y))
        self.vx    = random.uniform(-0.6, 0.6)
        self.vy    = random.uniform(-0.8, -0.2)
        self._life = random.randint(25, 50)
        self._max  = self._life

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self._life  -= 1
        alpha = int(180 * self._life / self._max)
        self.image.set_alpha(alpha)
        if self._life <= 0:
            self.kill()


class SmokeManager:
    def __init__(self):
        self._group = pygame.sprite.Group()

    def emit(self, x, y, colour=(90, 90, 90)):
        if random.random() < 0.3:
            self._group.add(SmokeParticle(x, y, colour))

    def update(self):
        self._group.update()

    def draw(self, surface):
        self._group.draw(surface)
