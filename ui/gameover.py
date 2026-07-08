# ============================================================
#  ui/gameover.py  —  Game-over screen
# ============================================================
import pygame, math
from config import SCREEN_WIDTH, SCREEN_HEIGHT, DARK_BLUE, RED, ORANGE, YELLOW, WHITE, SILVER, GOLD


class GameOverScreen:
    def __init__(self, surface):
        self._surf    = surface
        self._font_xl = pygame.font.SysFont('Arial Black', 72, bold=True)
        self._font_lg = pygame.font.SysFont('Arial', 36, bold=True)
        self._font_sm = pygame.font.SysFont('Consolas', 22)
        self._t       = 0

    def draw(self, score, hiscore):
        self._t += 1

        # Background
        self._surf.fill(DARK_BLUE)
        # Red vignette
        vig = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        vig.fill((80, 0, 0, 60))
        self._surf.blit(vig, (0, 0))

        # Animated "GAME OVER" text — pulsing red
        pulse = 0.5 + 0.5 * math.sin(self._t * 0.08)
        r = int(200 + 55 * pulse)
        g = int(30  * (1 - pulse))
        go_txt = self._font_xl.render("GAME OVER", True, (r, g, 0))
        cx = SCREEN_WIDTH  // 2 - go_txt.get_width() // 2
        cy = SCREEN_HEIGHT // 2 - 120
        self._surf.blit(go_txt, (cx, cy))

        # Score
        sc = self._font_lg.render("SCORE   {:08d}".format(score), True, WHITE)
        self._surf.blit(sc, (SCREEN_WIDTH // 2 - sc.get_width() // 2,
                              SCREEN_HEIGHT // 2 - 20))

        # Hi-score
        hi = self._font_lg.render("BEST    {:08d}".format(hiscore), True, GOLD)
        self._surf.blit(hi, (SCREEN_WIDTH // 2 - hi.get_width() // 2,
                              SCREEN_HEIGHT // 2 + 35))

        # Prompt
        if (self._t // 30) % 2 == 0:
            pr = self._font_sm.render("PRESS  ENTER  TO  CONTINUE", True, SILVER)
            self._surf.blit(pr, (SCREEN_WIDTH // 2 - pr.get_width() // 2,
                                  SCREEN_HEIGHT // 2 + 110))
