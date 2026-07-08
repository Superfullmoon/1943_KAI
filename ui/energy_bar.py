# ============================================================
#  ui/energy_bar.py  —  Energy / fuel gauge HUD
# ============================================================
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, GREEN, YELLOW, RED, WHITE, DARK_GRAY


class EnergyBar:
    BAR_W  = 200
    BAR_H  = 18
    BAR_X  = SCREEN_WIDTH - 220
    BAR_Y  = SCREEN_HEIGHT - 34

    def __init__(self, player):
        self._player = player
        self._font   = pygame.font.SysFont('Consolas', 13, bold=True)

    def draw(self, surface):
        frac = self._player.energy.fraction
        val  = self._player.energy.display_int

        # Background
        pygame.draw.rect(surface, (20, 20, 20), (self.BAR_X - 2, self.BAR_Y - 2,
                                                  self.BAR_W + 4, self.BAR_H + 4))
        pygame.draw.rect(surface, DARK_GRAY, (self.BAR_X, self.BAR_Y,
                                               self.BAR_W, self.BAR_H))

        # Colour: green → yellow → red
        if frac > 0.5:
            col = GREEN
        elif frac > 0.25:
            col = YELLOW
        else:
            col = RED

        # Filled portion
        fill_w = int(self.BAR_W * frac)
        pygame.draw.rect(surface, col, (self.BAR_X, self.BAR_Y, fill_w, self.BAR_H))

        # Highlight stripe
        pygame.draw.rect(surface, (*col[:3],), (self.BAR_X, self.BAR_Y, fill_w, 5))

        # Border
        pygame.draw.rect(surface, WHITE, (self.BAR_X, self.BAR_Y,
                                           self.BAR_W, self.BAR_H), 1)

        # Label
        lbl = self._font.render("ENERGY  {:3d}".format(val), True, WHITE)
        surface.blit(lbl, (self.BAR_X - lbl.get_width() - 4, self.BAR_Y + 2))
