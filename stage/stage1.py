# ============================================================
#  stage/stage1.py  —  Pacific Ocean (tutorial-friendly)
# ============================================================

#  Wave format:
#  (spawn_frame, enemy_type, x, pattern, pattern_kwargs, count, x_gap)
#
#  count  : how many enemies to spawn in a row (same frame, spread by x_gap)
#  x_gap  : pixel gap between enemies in a group

WAVES = [
    # ── Opening formation ──────────────────────────────────────
    (90,  'SmallFighter', 160, 'dive_left',  {}, 3, 70),
    (150, 'SmallFighter', 480, 'dive_right', {}, 3, -70),
    (240, 'SmallFighter', 320, 'straight',   {}, 1, 0),

    # ── Second wave ───────────────────────────────────────────
    (360, 'SmallFighter', 100, 'zigzag',     {}, 2, 80),
    (360, 'SmallFighter', 500, 'zigzag',     {}, 2, -80),

    # ── Small warship formation ──────────────────────────────
    (480, 'SmallWarship', 160, 'straight',   {}, 1, 0),
    (480, 'SmallWarship', 480, 'straight',   {}, 1, 0),

    # ── Medium fighter appears ────────────────────────────────
    (600, 'MediumFighter', 200, 'straight',  {}, 1, 0),
    (600, 'MediumFighter', 440, 'straight',  {}, 1, 0),

    # ── Medium warship ────────────────────────────────────────
    (720, 'MediumWarship', 320, 'straight',  {}, 1, 0),

    # ── Kamikaze pack ─────────────────────────────────────────
    (840, 'SmallFighter', 320, 'kamikaze',   {}, 4, 60),

    # ── Mixed wave ────────────────────────────────────────────
    (960, 'MediumFighter', 160, 'dive_left',  {}, 2, 80),
    (960, 'SmallFighter',  480, 'dive_right', {}, 3, -55),

    # ── Heavy fighter + warships ──────────────────────────────
    (1080, 'HeavyFighter', 320, 'straight',  {}, 1, 0),
    (1080, 'SmallWarship', 120, 'straight',  {}, 1, 0),
    (1080, 'SmallWarship', 520, 'straight',  {}, 1, 0),

    # ── Large warship ─────────────────────────────────────────
    (1200, 'LargeWarship', 320, 'straight',  {}, 1, 0),

    # ── Pre-boss wave ─────────────────────────────────────────
    (1320, 'SmallFighter', 100, 'zigzag',    {}, 2, 80),
    (1320, 'SmallFighter', 540, 'zigzag',    {}, 2, -80),
    (1380, 'MediumFighter', 320, 'straight', {}, 2, 100),

    # ── BOSS ──────────────────────────────────────────────────
    (1560, 'BOSS', 320, '', {}, 1, 0),
]
