# ============================================================
#  config.py  —  1943 KAI  Global Constants
# ============================================================

# ── Screen ───────────────────────────────────────────────────
SCREEN_WIDTH  = 640
SCREEN_HEIGHT = 960
FPS           = 60
TITLE         = "Pacific_Storm_1943 '태평양의 폭풍우 속으로'  ~太平洋の嵐~"
GAME_VERSION  = "1.0.0"

# ── Colours (RGB tuples) ─────────────────────────────────────
BLACK       = (  0,   0,   0)
WHITE       = (255, 255, 255)
RED         = (220,  50,  50)
DARK_RED    = (140,  20,  20)
ORANGE      = (255, 140,   0)
YELLOW      = (255, 220,   0)
GREEN       = ( 50, 200,  50)
DARK_GREEN  = ( 20, 100,  20)
BLUE        = ( 50, 100, 220)
DARK_BLUE   = (  8,  18,  55)
SEA_BLUE    = ( 15,  70, 140)
SKY_BLUE    = ( 80, 140, 210)
NAVY        = ( 20,  40, 100)
CYAN        = (  0, 220, 255)
GRAY        = (128, 128, 128)
DARK_GRAY   = ( 50,  50,  50)
SILVER      = (192, 192, 192)
GOLD        = (255, 200,  30)
PURPLE      = (160,   0, 200)
TURQUOISE   = (  0, 180, 160)
PINK        = (255, 100, 150)

# ── Player ───────────────────────────────────────────────────
PLAYER_SPEED             = 5
PLAYER_MAX_ENERGY        = 100
PLAYER_START_ENERGY      = 100
PLAYER_LIVES             = 3
PLAYER_INVINCIBLE_FRAMES = 120   # 2 sec at 60 fps
PLAYER_SHOOT_COOLDOWN    = 8     # frames
PLAYER_BOMB_COUNT        = 3

# ── Weapons ──────────────────────────────────────────────────
WEAPON_VULCAN  = "VULCAN"
WEAPON_SHOTGUN = "SHOTGUN"
WEAPON_LASER   = "LASER"
WEAPON_WIDE    = "WIDE"
WEAPON_ORDER   = [WEAPON_VULCAN, WEAPON_SHOTGUN, WEAPON_LASER, WEAPON_WIDE]

# ── Bullets ──────────────────────────────────────────────────
PLAYER_BULLET_SPEED = 15
ENEMY_BULLET_SPEED  =  5
ENEMY_BULLET_FAST   =  9

# ── Energy ───────────────────────────────────────────────────
ENERGY_DRAIN_RATE  = 0.010   # per frame (drains slowly)
ENERGY_ITEM_AMOUNT = 25

# ── Scroll ───────────────────────────────────────────────────
SCROLL_SPEED = 2

# ── Scoring ──────────────────────────────────────────────────
SCORE_SMALL_ENEMY  =   100
SCORE_MEDIUM_ENEMY =   300
SCORE_LARGE_ENEMY  =   600
SCORE_BOSS_PART    =  2000
SCORE_BOSS         = 10000
SCORE_BONUS_CLEAR  =  5000

# ── Bomb ─────────────────────────────────────────────────────
BOMB_DAMAGE = 9999

# ── Option drones ────────────────────────────────────────────
OPTION_OFFSETS = [(-58, 36), (58, 36)]   # relative to player centre

# ── Stages ───────────────────────────────────────────────────
TOTAL_STAGES = 10

# ── Stage colour themes ──────────────────────────────────────
STAGE_THEMES = {
    1:  {'sky_top': ( 10,  30,  80), 'sky_bot': ( 15,  70, 140),
         'sea':     ( 10,  55, 120), 'name': "Stage 1 — Pacific Ocean"},
    2:  {'sky_top': ( 15,  55, 100), 'sky_bot': ( 10,  95, 155),
         'sea':     (  5,  85, 145), 'name': "Stage 2 — Coral Sea"},
    3:  {'sky_top': ( 30,  80, 160), 'sky_bot': ( 55, 135, 205),
         'sea':     ( 20, 105, 175), 'name': "Stage 3 — Tropical Atoll"},
    4:  {'sky_top': ( 20,  20,  30), 'sky_bot': ( 40,  50,  55),
         'sea':     ( 12,  38,  58), 'name': "Stage 4 — Storm Front"},
    5:  {'sky_top': (120,  60,  10), 'sky_bot': (175,  95,  28),
         'sea':     ( 75,  48,  18), 'name': "Stage 5 — Sunset Battle"},
    6:  {'sky_top': (  5,   5,  15), 'sky_bot': ( 10,  18,  48),
         'sea':     (  5,  14,  38), 'name': "Stage 6 — Midnight Raid"},
    7:  {'sky_top': (155, 185, 215), 'sky_bot': (195, 215, 235),
         'sea':     (115, 175, 205), 'name': "Stage 7 — Arctic Waters"},
    8:  {'sky_top': ( 80,  18,   5), 'sky_bot': (128,  48,  10),
         'sea':     ( 58,  18,   5), 'name': "Stage 8 — Volcanic Strait"},
    9:  {'sky_top': ( 10,  10,  28), 'sky_bot': ( 18,  28,  68),
         'sea':     (  8,  18,  48), 'name': "Stage 9 — Final Approach"},
   10:  {'sky_top': ( 20,   5,   5), 'sky_bot': ( 48,  14,   8),
         'sea':     ( 28,   8,   5), 'name': "Stage 10 — Enemy Stronghold"},
}

import pygame
KEY_SHOOT = pygame.K_z
KEY_BOMB  = pygame.K_x
KEY_START = pygame.K_RETURN
KEY_PAUSE = pygame.K_ESCAPE

