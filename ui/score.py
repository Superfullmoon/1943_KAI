# ============================================================
#  ui/score.py  —  Score HUD
# ============================================================
import pygame
from config import WHITE, YELLOW, GOLD, SILVER, DARK_BLUE


class ScoreDisplay:
    def __init__(self, score=0, hiscore=0):
        self.score   = score
        self.hiscore = hiscore
        self._font_big  = pygame.font.SysFont('Consolas', 22, bold=True)
        self._font_sm   = pygame.font.SysFont('Consolas', 14)

    def update(self, score, hiscore):
        self.score   = score
        self.hiscore = hiscore

    def draw(self, surface):
        # Hi-score (top centre)
        hi_lbl = self._font_sm.render("HI-SCORE", True, SILVER)
        hi_val = self._font_big.render("{:08d}".format(self.hiscore), True, GOLD)
        surface.blit(hi_lbl, (surface.get_width() // 2 - hi_lbl.get_width() // 2, 28))
        surface.blit(hi_val, (surface.get_width() // 2 - hi_val.get_width() // 2, 42))

        # Score (top left)
        sc_lbl = self._font_sm.render("SCORE", True, SILVER)
        sc_val = self._font_big.render("{:08d}".format(self.score), True, WHITE)
        surface.blit(sc_lbl, (10, 28))
        surface.blit(sc_val, (10, 42))
