# ============================================================
#  enemy/enemy_ai.py  —  Movement-pattern functions
# ============================================================
import math, random
from config import SCREEN_WIDTH, SCREEN_HEIGHT, SCROLL_SPEED


class AIPattern:
    """Each method returns a callable that moves the enemy each frame."""

    @staticmethod
    def straight(speed=2.5):
        """Fly straight down."""
        def tick(enemy):
            enemy.rect.y += speed + SCROLL_SPEED * 0.4
        return tick

    @staticmethod
    def dive_left(speed=3.0):
        """Arc from upper-right toward lower-left."""
        def tick(enemy):
            enemy._t = getattr(enemy, '_t', 0) + 1
            enemy.rect.x -= 0.8
            enemy.rect.y += speed
        return tick

    @staticmethod
    def dive_right(speed=3.0):
        def tick(enemy):
            enemy._t = getattr(enemy, '_t', 0) + 1
            enemy.rect.x += 0.8
            enemy.rect.y += speed
        return tick

    @staticmethod
    def zigzag(speed=2.5, period=60):
        """Zigzag left-right while descending."""
        def tick(enemy):
            enemy._t  = getattr(enemy, '_t', 0) + 1
            enemy.rect.x += math.sin(enemy._t * math.pi / period) * 3
            enemy.rect.y += speed
        return tick

    @staticmethod
    def kamikaze(player_ref, speed=5.0):
        """Aim straight at the player."""
        _init = [False]
        _vx   = [0.0]
        _vy   = [0.0]

        def tick(enemy):
            if not _init[0]:
                dx = player_ref.rect.centerx - enemy.rect.centerx
                dy = player_ref.rect.centery - enemy.rect.centery
                dist = math.hypot(dx, dy) or 1
                _vx[0]   = dx / dist * speed
                _vy[0]   = dy / dist * speed
                _init[0] = True
            enemy.rect.x += _vx[0]
            enemy.rect.y += _vy[0]
        return tick

    @staticmethod
    def formation_v(index=0, speed=2.0):
        """V-formation: each unit holds its slot position."""
        def tick(enemy):
            enemy.rect.y += speed
        return tick

    @staticmethod
    def circle_then_exit(speed=2.0, radius=120):
        """Fly a half-circle then exit downward."""
        def tick(enemy):
            enemy._t = getattr(enemy, '_t', 0) + 1
            if enemy._t < 90:
                angle    = math.pi * enemy._t / 90
                enemy.rect.x += math.sin(angle) * 3
                enemy.rect.y += math.cos(angle) * speed * 0.5 + speed * 0.5
            else:
                enemy.rect.y += speed * 1.5
        return tick

    @staticmethod
    def stationary():
        """Ground turret: stays in place (scrolls with background)."""
        def tick(enemy):
            enemy.rect.y += SCROLL_SPEED
        return tick

    @staticmethod
    def boss_move(speed=1.2):
        """Boss side-to-side slow motion."""
        def tick(enemy):
            enemy._t  = getattr(enemy, '_t', 0) + 1
            enemy.rect.x += math.sin(enemy._t * 0.015) * speed
            # Slowly creep down to a set Y then hold
            if enemy.rect.centery < 260:
                enemy.rect.y += 1.5
        return tick


def get_pattern(name: str, **kwargs):
    """Look up an AI pattern by string name."""
    mapping = {
        'straight':         AIPattern.straight,
        'dive_left':        AIPattern.dive_left,
        'dive_right':       AIPattern.dive_right,
        'zigzag':           AIPattern.zigzag,
        'kamikaze':         AIPattern.kamikaze,
        'formation_v':      AIPattern.formation_v,
        'circle_then_exit': AIPattern.circle_then_exit,
        'stationary':       AIPattern.stationary,
        'boss_move':        AIPattern.boss_move,
    }
    factory = mapping.get(name, AIPattern.straight)
    return factory(**kwargs)
