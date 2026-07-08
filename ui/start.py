# ============================================================
#  ui/start.py  —  Title / Start screen
# ============================================================
import pygame, math, random
from config import (SCREEN_WIDTH, SCREEN_HEIGHT, DARK_BLUE, SEA_BLUE,
                    WHITE, YELLOW, GOLD, SILVER, CYAN, ORANGE, NAVY)


class Star:
    def __init__(self):
        self.x     = random.randint(0, SCREEN_WIDTH)
        self.y     = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.uniform(0.2, 1.0)
        self.size  = random.choice([1, 1, 1, 2])
        self.alpha = random.randint(100, 255)

    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)


class TitleScreen:
    NUM_STARS = 80

    def __init__(self, surface):
        self._surf    = surface
        self._stars   = [Star() for _ in range(self.NUM_STARS)]
        self._t       = 0
        self._clouds  = [(random.randint(0, SCREEN_WIDTH), random.randint(60, SCREEN_HEIGHT - 200),
                          random.randint(40, 100)) for _ in range(6)]

        self._font_xl  = pygame.font.SysFont('Arial Black', 80, bold=True)
        self._font_sub = pygame.font.SysFont('Arial Black', 28, bold=True)
        self._font_sm  = pygame.font.SysFont('Consolas', 20)
        self._font_xs  = pygame.font.SysFont('Consolas', 15)

    def _draw_sky(self):
        """Gradient sky from dark navy to sea blue."""
        for y in range(SCREEN_HEIGHT):
            t  = y / SCREEN_HEIGHT
            r  = int(DARK_BLUE[0] * (1 - t) + SEA_BLUE[0] * t)
            g  = int(DARK_BLUE[1] * (1 - t) + SEA_BLUE[1] * t)
            b  = int(DARK_BLUE[2] * (1 - t) + SEA_BLUE[2] * t)
            pygame.draw.line(self._surf, (r, g, b), (0, y), (SCREEN_WIDTH, y))

    def _draw_stars(self):
        for s in self._stars:
            pygame.draw.circle(self._surf, (255, 255, 255, s.alpha), (int(s.x), int(s.y)), s.size)

    def _draw_ocean(self):
        """Animated wave at the bottom quarter."""
        h_start = int(SCREEN_HEIGHT * 0.72)
        # Ocean base
        pygame.draw.rect(self._surf, (10, 55, 120),
                         (0, h_start, SCREEN_WIDTH, SCREEN_HEIGHT - h_start))
        # Wave crests
        for i in range(6):
            wave_y = h_start + 8 + i * 6
            offset = math.sin(self._t * 0.04 + i * 0.9) * 18
            for wx in range(-40, SCREEN_WIDTH + 40, 40):
                cx = wx + int(offset)
                pygame.draw.arc(self._surf, (80, 160, 220),
                                (cx, wave_y, 36, 10),
                                0, math.pi, 2)

    def _draw_title(self):
        # Glow layers
        for radius in range(14, 0, -2):
            alpha = 20
            glow  = pygame.Surface((SCREEN_WIDTH, 120), pygame.SRCALPHA)
            pulse = 0.5 + 0.5 * math.sin(self._t * 0.05)
            col   = (int(255 * pulse), int(180 * pulse), 0, alpha)
            pygame.draw.rect(glow, col, (0, 0, SCREEN_WIDTH, 120))
            self._surf.blit(glow, (0, 130))

        title_txt = self._font_xl.render("1943  KAI", True, GOLD)
        shadow    = self._font_xl.render("1943  KAI", True, (60, 30, 0))
        cx = SCREEN_WIDTH  // 2 - title_txt.get_width() // 2
        self._surf.blit(shadow,    (cx + 4, 144))
        self._surf.blit(title_txt, (cx,     140))

        sub = self._font_sub.render("〜太平洋の嵐〜", True, CYAN)
        self._surf.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 228))

    def _draw_controls(self):
        lines = [
            ("ARROWS / WASD", "Move"),
            ("Z",             "Shoot"),
            ("X",             "Bomb"),
            ("ESC",           "Pause"),
        ]
        y0 = SCREEN_HEIGHT - 230
        for i, (key, desc) in enumerate(lines):
            k_txt = self._font_xs.render("[{}]".format(key), True, YELLOW)
            d_txt = self._font_xs.render(desc, True, SILVER)
            self._surf.blit(k_txt, (SCREEN_WIDTH // 2 - 100, y0 + i * 22))
            self._surf.blit(d_txt, (SCREEN_WIDTH // 2 - 10,  y0 + i * 22))

    def draw(self):
        self._t += 1
        for s in self._stars:
            s.update()

        self._draw_sky()
        self._draw_stars()
        self._draw_ocean()
        self._draw_title()
        self._draw_controls()

        # Blinking "PRESS ENTER" prompt
        if (self._t // 35) % 2 == 0:
            pr = self._font_sm.render("PRESS  ENTER  TO  START", True, WHITE)
            self._surf.blit(pr, (SCREEN_WIDTH // 2 - pr.get_width() // 2,
                                  SCREEN_HEIGHT - 120))

        # Version / credit
        ver = self._font_xs.render(f"ver 1.0  —  1943 KAI Python Edition", True, (80, 80, 90))
        self._surf.blit(ver, (SCREEN_WIDTH // 2 - ver.get_width() // 2, SCREEN_HEIGHT - 30))
