# ============================================================
#  player/player.py  —  Player aircraft sprite
# ============================================================
import pygame
from config import (SCREEN_WIDTH, SCREEN_HEIGHT,
                    PLAYER_SPEED, PLAYER_LIVES, PLAYER_BOMB_COUNT,
                    PLAYER_INVINCIBLE_FRAMES, PLAYER_SHOOT_COOLDOWN,
                    KEY_SHOOT, KEY_BOMB,
                    SILVER, CYAN, YELLOW, ORANGE, DARK_GRAY, WHITE)
from player.weapon  import WeaponSystem
from player.energy  import EnergySystem
from player.option  import OptionManager
from bullet.player_bullet import spawn_weapon_bullets


# ── Player aircraft surface (hand-crafted P-38 style) ────────
def _build_player_surf():
    w, h = 52, 68
    s = pygame.Surface((w, h), pygame.SRCALPHA)

    # ── Twin-boom fuselage (P-38 style) ────────────────────────
    # Left boom
    pygame.draw.ellipse(s, (160, 175, 190), (4,  20, 10, 40))
    pygame.draw.ellipse(s, (200, 215, 228), (5,  22,  8, 36))
    # Right boom
    pygame.draw.ellipse(s, (160, 175, 190), (38, 20, 10, 40))
    pygame.draw.ellipse(s, (200, 215, 228), (39, 22,  8, 36))

    # ── Center nacelle ──────────────────────────────────────────
    pygame.draw.ellipse(s, (140, 158, 175), (18,  8, 16, 52))
    pygame.draw.ellipse(s, (200, 218, 235), (20, 10, 12, 46))

    # ── Wing ────────────────────────────────────────────────────
    wing_pts = [(4, 36), (48, 36), (44, 44), (8, 44)]
    pygame.draw.polygon(s, (150, 165, 182), wing_pts)
    pygame.draw.polygon(s, (180, 198, 215), [(6, 37), (46, 37), (43, 42), (9, 42)])

    # ── Horizontal stabilizer (rear) ────────────────────────────
    stab_pts = [(10, 56), (42, 56), (40, 62), (12, 62)]
    pygame.draw.polygon(s, (130, 148, 165), stab_pts)

    # ── Engine intake circles ────────────────────────────────────
    pygame.draw.circle(s, (80, 90, 100), (9, 22), 5)
    pygame.draw.circle(s, (50, 60, 70),  (9, 22), 3)
    pygame.draw.circle(s, (80, 90, 100), (43, 22), 5)
    pygame.draw.circle(s, (50, 60, 70),  (43, 22), 3)

    # ── Cockpit ──────────────────────────────────────────────────
    pygame.draw.ellipse(s, (60, 120, 200), (21, 18, 10, 14))
    pygame.draw.ellipse(s, (140, 200, 255, 180), (22, 19, 8, 11))

    # ── Star emblem on wing ──────────────────────────────────────
    pygame.draw.circle(s, (200, 30, 30), (26, 40), 5)
    pygame.draw.circle(s, (255, 255, 255), (26, 40), 3)

    return s


# ── Hit mask ─────────────────────────────────────────────────
def _build_hit_surf():
    """Smaller inner rect for precise hit detection."""
    s = pygame.Surface((20, 20), pygame.SRCALPHA)
    pygame.draw.ellipse(s, WHITE, (0, 0, 20, 20))
    return s


class Player(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()

        self._normal_surf    = _build_player_surf()
        self._hit_surf       = _build_hit_surf()   # used for mask collision
        self.image           = self._normal_surf
        self.rect            = self.image.get_rect(center=(x, y))
        self.mask            = pygame.mask.from_surface(self.image)

        # Sub-systems
        self.weapon   = WeaponSystem()
        self.energy   = EnergySystem()
        self.options  = OptionManager()

        # State
        self.lives           = PLAYER_LIVES
        self.bomb_count      = PLAYER_BOMB_COUNT
        self.invincible      = False
        self._inv_timer      = 0
        self._shoot_cd       = 0
        self._blink          = False

    # ── Update ───────────────────────────────────────────────
    def update(self, keys, bullet_group):
        self._move(keys)
        self._handle_shoot(keys, bullet_group)
        self._tick_invincibility()
        self.energy.drain()
        self.options.update(self.rect.centerx, self.rect.centery)

        if self._shoot_cd > 0:
            self._shoot_cd -= 1

    # ── Movement ─────────────────────────────────────────────
    def _move(self, keys):
        dx = dy = 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += 1
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy += 1
        self.rect.x = max(0, min(SCREEN_WIDTH  - self.rect.width,
                                 self.rect.x + dx * PLAYER_SPEED))
        self.rect.y = max(0, min(SCREEN_HEIGHT - self.rect.height,
                                 self.rect.y + dy * PLAYER_SPEED))

    # ── Shooting ─────────────────────────────────────────────
    def _handle_shoot(self, keys, bullet_group):
        if keys[KEY_SHOOT] and self._shoot_cd <= 0:
            spawn_weapon_bullets(self.weapon.current,
                                 self.rect.centerx,
                                 self.rect.top + 6,
                                 bullet_group,
                                 self.options.positions())
            self._shoot_cd = PLAYER_SHOOT_COOLDOWN

    # ── Invincibility blink ──────────────────────────────────
    def _tick_invincibility(self):
        if self.invincible:
            self._inv_timer -= 1
            self._blink = (self._inv_timer // 5) % 2 == 0
            if self._inv_timer <= 0:
                self.invincible  = False
                self._blink      = False
                self.image       = self._normal_surf

    # ── Take damage ──────────────────────────────────────────
    def take_damage(self, amount: int) -> bool:
        """Returns True if the player lost a life."""
        self.energy.recover(-amount)   # negative recover = drain
        if self.energy.is_empty:
            return self._lose_life()
        return False

    def _lose_life(self) -> bool:
        self.lives -= 1
        if self.lives > 0:
            self.energy.full_restore()
            self.invincible = True
            self._inv_timer = PLAYER_INVINCIBLE_FRAMES
            self.options.remove_all()
            return False
        return True   # game over

    # ── Draw ─────────────────────────────────────────────────
    def draw(self, surface):
        if self._blink:
            return
        surface.blit(self.image, self.rect)
        self.options.draw(surface)

    # ── Properties ───────────────────────────────────────────
    @property
    def energy_value(self) -> float:
        return self.energy.value

    @property
    def center(self):
        return self.rect.center
