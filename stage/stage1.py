# ============================================================
#  stage/stage1.py  —  Pacific Ocean (Extended Timeline)
# ============================================================

#  Wave format:
#  (spawn_frame, enemy_type, x, pattern, pattern_kwargs, count, x_gap)
#
#  count  : how many enemies to spawn in a row (same frame, spread by x_gap)
#  x_gap  : pixel gap between enemies in a group

WAVES = [
    # ── Opening (0s - 10s) ───────────────────────────────────
    (90,   'SmallFighter', 160, 'dive_left',  {}, 3, 70),
    (180,  'SmallFighter', 480, 'dive_right', {}, 3, -70),
    (300,  'SmallFighter', 320, 'straight',   {}, 1, 0),
    (420,  'SmallFighter', 100, 'zigzag',     {}, 2, 80),
    (420,  'SmallFighter', 500, 'zigzag',     {}, 2, -80),
    (540,  'SmallWarship', 160, 'straight',   {}, 1, 0),
    (540,  'SmallWarship', 480, 'straight',   {}, 1, 0),

    # ── Mid-opening (10s - 20s) ──────────────────────────────
    (680,  'MediumFighter', 200, 'straight',  {}, 1, 0),
    (680,  'MediumFighter', 440, 'straight',  {}, 1, 0),
    (800,  'MediumWarship', 320, 'straight',  {}, 1, 0),
    (920,  'SmallFighter', 320, 'kamikaze',   {}, 4, 60),
    (1060, 'MediumFighter', 160, 'dive_left',  {}, 2, 80),
    (1060, 'SmallFighter',  480, 'dive_right', {}, 3, -55),

    # ── Long Warship 1 (20s - 30s) ───────────────────────────
    (1240, 'HeavyFighter', 320, 'straight',   {}, 1, 0),
    (1400, 'LongWarship',  320, 'straight',   {}, 1, 0),   # First Long Warship!
    (1560, 'SmallFighter', 100, 'zigzag',     {}, 3, 60),
    (1560, 'SmallFighter', 540, 'zigzag',     {}, 3, -60),

    # ── Mid-Stage Climax (30s - 40s) ─────────────────────────
    (1780, 'LargeWarship', 320, 'straight',   {}, 1, 0),
    (1920, 'MediumFighter', 200, 'zigzag',     {}, 2, 100),
    (2060, 'SmallWarship', 120, 'straight',   {}, 1, 0),
    (2060, 'SmallWarship', 520, 'straight',   {}, 1, 0),
    (2200, 'HeavyFighter', 220, 'dive_left',  {}, 1, 0),
    (2200, 'HeavyFighter', 420, 'dive_right', {}, 1, 0),

    # ── Long Warship 2 & Turrets (40s - 50s) ─────────────────
    (2400, 'GroundTurret', 150, 'stationary', {}, 1, 0),
    (2400, 'GroundTurret', 490, 'stationary', {}, 1, 0),
    (2550, 'SmallFighter', 320, 'kamikaze',   {}, 5, 50),
    (2700, 'LongWarship',  320, 'straight',   {}, 1, 0),   # Second Long Warship!
    (2850, 'MediumWarship', 200, 'straight',  {}, 1, 0),
    (2850, 'MediumWarship', 440, 'straight',  {}, 1, 0),

    # ── Climax Pre-Boss Wave (50s - 60s) ─────────────────────
    (3050, 'HeavyFighter', 320, 'circle_then_exit', {}, 1, 0),
    (3180, 'SmallFighter', 100, 'zigzag',     {}, 3, 80),
    (3180, 'SmallFighter', 540, 'zigzag',     {}, 3, -80),
    (3300, 'MediumFighter', 320, 'straight',  {}, 2, 120),
    (3420, 'SmallFighter', 320, 'kamikaze',   {}, 4, 60),

    # ── BOSS (60s / 3600 frames) ─────────────────────────────
    (3600, 'BOSS', 320, '', {}, 1, 0),
]
