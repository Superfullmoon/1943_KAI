# ============================================================
#  player/option.py  —  Option drone wingmen
# ============================================================
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, OPTION_OFFSETS, SILVER, CYAN, YELLOW


def _build_option_surf():
    w, h = 30, 38
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    # Fuselage
    pygame.draw.ellipse(s, SILVER, (9, 4, 12, 30))
    # Wings
    pygame.draw.polygon(s, (150, 160, 170), [(0, 20), (30, 20), (21, 28), (9, 28)])
    # Cockpit
    pygame.draw.ellipse(s, (100, 200, 255), (11, 8, 8, 10))
    # Engine glow
    pygame.draw.ellipse(s, (255, 200, 60, 200), (12, 34, 6, 4))
    return s


class Option(pygame.sprite.Sprite):
    """A small wingman drone that mirrors the player's shots."""

    _SURF = None

    def __init__(self, side_index: int):
        super().__init__()
        if Option._SURF is None:
            Option._SURF = _build_option_surf()
        self.image      = Option._SURF
        self.rect       = self.image.get_rect()
        self._offset_x  = OPTION_OFFSETS[side_index][0]
        self._offset_y  = OPTION_OFFSETS[side_index][1]

    def follow(self, player_cx, player_cy):
        self.rect.centerx = player_cx + self._offset_x
        self.rect.centery = player_cy + self._offset_y

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class OptionManager:
    """Manages up to 2 option drones."""

    def __init__(self):
        self._options = []

    def add_option(self):
        idx = len(self._options)
        if idx < 2:
            self._options.append(Option(idx))

    def remove_all(self):
        self._options.clear()

    def update(self, player_cx, player_cy):
        for opt in self._options:
            opt.follow(player_cx, player_cy)

    def positions(self):
        return [(opt.rect.centerx, opt.rect.centery) for opt in self._options]

    def draw(self, surface):
        for opt in self._options:
            opt.draw(surface)

    def __len__(self):
        return len(self._options)
