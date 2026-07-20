# ============================================================
#  stage/stage1.py  —  Pacific Ocean (tutorial-friendly)
# ============================================================

#  Wave format:
#  (spawn_frame, enemy_type, x, pattern, pattern_kwargs, count, x_gap)
#
#  count  : how many enemies to spawn in a row (same frame, spread by x_gap)
#  x_gap  : pixel gap between enemies in a group

WAVES = [
    # ── Opening formation (Starts after takeoff sequence) ──────
    (220,  'SmallFighter', 160, 'dive_left',  {}, 3, 70),
    (300,  'SmallFighter', 480, 'dive_right', {}, 3, -70),
    (400,  'SmallFighter', 320, 'straight',   {}, 1, 0),

    # ── Second wave ───────────────────────────────────────────
    (540,  'SmallFighter', 100, 'zigzag',     {}, 2, 80),
    (540,  'SmallFighter', 500, 'zigzag',     {}, 2, -80),

    # ── Small warship formation ──────────────────────────────
    (680,  'SmallWarship', 160, 'straight',   {}, 1, 0),
    (680,  'SmallWarship', 480, 'straight',   {}, 1, 0),

    # ── Medium fighter appears ────────────────────────────────
    (820,  'MediumFighter', 200, 'straight',  {}, 1, 0),
    (820,  'MediumFighter', 440, 'straight',  {}, 1, 0),

    # ── LONG BATTLESHIP (Mid-stage giant warship challenge!) ──
    (960,  'LongBattleship', 320, 'straight', {}, 1, 0),

    # ── Medium warship ────────────────────────────────────────
    (1300, 'MediumWarship', 320, 'straight',  {}, 1, 0),

    # ── Kamikaze pack ─────────────────────────────────────────
    (1440, 'SmallFighter', 320, 'kamikaze',   {}, 4, 60),

    # ── Mixed wave ────────────────────────────────────────────
    (1600, 'MediumFighter', 160, 'dive_left',  {}, 2, 80),
    (1600, 'SmallFighter',  480, 'dive_right', {}, 3, -55),

    # ── Heavy fighter + warships ──────────────────────────────
    (1780, 'HeavyFighter', 320, 'straight',  {}, 1, 0),
    (1780, 'SmallWarship', 120, 'straight',  {}, 1, 0),
    (1780, 'SmallWarship', 520, 'straight',  {}, 1, 0),

    # ── Large warship ─────────────────────────────────────────
    (1960, 'LargeWarship', 320, 'straight',  {}, 1, 0),

    # ── Pre-boss wave ─────────────────────────────────────────
    (2140, 'SmallFighter', 100, 'zigzag',    {}, 2, 80),
    (2140, 'SmallFighter', 540, 'zigzag',    {}, 2, -80),
    (2260, 'MediumFighter', 320, 'straight', {}, 2, 100),

    # ── BOSS (Carrier Boss with side turrets and big cannon) ──
    (2450, 'BOSS', 320, '', {}, 1, 0),
]
