# ============================================================
#  stage/stage1.py  —  Pacific Ocean (tutorial-friendly)
# ============================================================

#  Wave format:
#  (spawn_frame, enemy_type, x, pattern, pattern_kwargs, count, x_gap)
#
#  count  : how many enemies to spawn in a row (same frame, spread by x_gap)
#  x_gap  : pixel gap between enemies in a group

WAVES = [
    # ── Opening formation ─────────────────────────────────────
    (90,  'SmallFighter', 160, 'dive_left',  {}, 3, 70),
    (150, 'SmallFighter', 480, 'dive_right', {}, 3, -70),
    (240, 'SmallFighter', 320, 'straight',   {}, 1, 0),

    # ── Second wave ───────────────────────────────────────────
    (360, 'SmallFighter', 100, 'zigzag',     {}, 2, 80),
    (360, 'SmallFighter', 500, 'zigzag',     {}, 2, -80),

    # ── Medium fighter appears ────────────────────────────────
    (480, 'MediumFighter', 200, 'straight',  {}, 1, 0),
    (480, 'MediumFighter', 440, 'straight',  {}, 1, 0),

    # ── Ground turrets (scroll with background) ───────────────
    (600, 'GroundTurret', 130, 'stationary', {}, 1, 0),
    (600, 'GroundTurret', 510, 'stationary', {}, 1, 0),

    # ── Kamikaze pack ─────────────────────────────────────────
    (720, 'SmallFighter', 320, 'kamikaze',   {}, 4, 60),

    # ── Mixed wave ────────────────────────────────────────────
    (900, 'MediumFighter', 160, 'dive_left',  {}, 2, 80),
    (900, 'SmallFighter',  480, 'dive_right', {}, 3, -55),

    # ── Heavy fighter ────────────────────────────────────────
    (1080, 'HeavyFighter', 320, 'straight',  {}, 1, 0),

    # ── Pre-boss wave ─────────────────────────────────────────
    (1260, 'SmallFighter', 100, 'zigzag',    {}, 2, 80),
    (1260, 'SmallFighter', 540, 'zigzag',    {}, 2, -80),
    (1320, 'MediumFighter', 320, 'straight', {}, 2, 100),

    # ── BOSS ─────────────────────────────────────────────────
    (1500, 'BOSS', 320, '', {}, 1, 0),
]
