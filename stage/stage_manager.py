# ============================================================
#  stage/stage_manager.py  —  Stage orchestration
# ============================================================
import pygame, importlib, random
from config import (SCREEN_WIDTH, SCREEN_HEIGHT, SCORE_BONUS_CLEAR, TOTAL_STAGES)
from stage.stage_base import StageBase
from enemy.enemy      import make_enemy, PowerUpItem
from enemy.battleship import BOSS_BY_STAGE


_STAGE_MODULES = {i: 'stage.stage{}'.format(i) for i in range(1, TOTAL_STAGES + 1)}


class StageManager:
    def __init__(self, player, sfx):
        self._player       = player
        self._sfx          = sfx
        self.current_stage_num = 1
        self._score_pending    = 0   # score accumulated this frame

        # Sprite groups (shared with game/collision systems)
        self.enemy_group        = pygame.sprite.Group()
        self.enemy_bullet_group = pygame.sprite.Group()
        self.player_bullet_group= pygame.sprite.Group()
        self.item_group         = pygame.sprite.Group()

        self._boss_sprite = None
        self._boss_components = pygame.sprite.Group()
        self._stage_clear_flag = False
        self.explosion_manager = None
        self._boss_dead_delay = 0
        self._boss_last_center = (0, 0)

        self._frame        = 0
        self._waves        = []
        self._wave_idx     = 0

        self._bg = None
        self._load_stage(self.current_stage_num)

    # ── Load / transition ────────────────────────────────────
    def _load_stage(self, n: int):
        self._bg    = StageBase(n)
        mod         = importlib.import_module(_STAGE_MODULES[n])
        self._waves = list(mod.WAVES)
        self._wave_idx    = 0
        self._frame       = 0
        self._boss_sprite = None
        self._stage_clear_flag = False
        self._boss_dead_delay = 0
        self._boss_last_center = (0, 0)
        self.enemy_group.empty()
        self.enemy_bullet_group.empty()
        self.player_bullet_group.empty()
        self.item_group.empty()

    def next_stage(self):
        self.current_stage_num = min(self.current_stage_num + 1, TOTAL_STAGES)
        self._load_stage(self.current_stage_num)

    # ── Update ───────────────────────────────────────────────
    def update(self) -> int:
        """Tick everything; return score gained this frame."""
        self._score_pending = 0
        self._frame += 1

        self._bg.update()
        self._spawn_waves()

        # Update groups
        self.enemy_group.update()
        self.enemy_bullet_group.update()
        self.player_bullet_group.update()
        self.item_group.update()

        if self._boss_sprite:
            self._boss_components.update()
            # Sync boss component positions
            for c in list(self._boss_components):
                c.sync()
            # Check boss death
            if self._boss_sprite.is_dead:
                self._score_pending += self._boss_sprite.score_value
                for c in list(self._boss_components):
                    c.kill()
                # Save last position and set delay for epic explosion chain sequence!
                self._boss_last_center = self._boss_sprite.rect.center
                self._boss_sprite = None
                self._boss_dead_delay = 120  # 2 seconds delay

        # Run the epic explosion sequence and check clear timing
        if self._boss_dead_delay > 0:
            self._boss_dead_delay -= 1
            if self._boss_dead_delay % 10 == 0:
                if self.explosion_manager:
                    ox = random.randint(-65, 65)
                    oy = random.randint(-45, 45)
                    self.explosion_manager.spawn(
                        self._boss_last_center[0] + ox,
                        self._boss_last_center[1] + oy,
                        'large' if random.random() < 0.7 else 'huge'
                    )
                    self._sfx.play('explosion_large' if random.random() < 0.5 else 'explosion_small')
            if self._boss_dead_delay <= 0:
                self._stage_clear_flag = True

        return self._score_pending

    # ── Wave spawning ────────────────────────────────────────
    def _spawn_waves(self):
        while (self._wave_idx < len(self._waves)
               and self._waves[self._wave_idx][0] <= self._frame):
            self._spawn_entry(self._waves[self._wave_idx])
            self._wave_idx += 1

    def _spawn_entry(self, entry):
        (spawn_t, etype, base_x, pattern, pkwargs, count, x_gap) = entry

        if etype == 'BOSS':
            self._spawn_boss(base_x)
            return

        for i in range(count):
            x = base_x + i * x_gap
            x = max(30, min(SCREEN_WIDTH - 30, x))
            e = make_enemy(etype, x, -50,
                           bullet_group=self.enemy_bullet_group,
                           player_ref=self._player,
                           pattern=pattern,
                           pattern_kwargs=dict(pkwargs))

            # Attach drop-item callback
            e.drop_item = self._drop_item_at
            self.enemy_group.add(e)

    def _spawn_boss(self, x: int):
        BossCls = BOSS_BY_STAGE.get(self.current_stage_num,
                                    BOSS_BY_STAGE[1])
        boss = BossCls(x, -120, self.enemy_bullet_group, self._player)
        self._boss_sprite = boss
        self.enemy_group.add(boss)
        for c in boss.components:
            self._boss_components.add(c)
            self.enemy_group.add(c)

    # ── Item drop ────────────────────────────────────────────
    def _drop_item_at(self, x: int, y: int):
        item_type = random.choices(
            ['ENERGY', 'WEAPON', 'BOMB', 'OPTION'],
            weights=[50, 25, 15, 10]
        )[0]
        self.item_group.add(PowerUpItem(x, y, item_type))

    # ── Checks ───────────────────────────────────────────────
    def is_stage_clear(self) -> bool:
        return self._stage_clear_flag

    def has_boss(self) -> bool:
        return self._boss_sprite is not None

    # ── Draw ─────────────────────────────────────────────────
    def draw_background(self, surface):
        self._bg.draw(surface)

    def draw_boss_hp(self, surface):
        if self._boss_sprite and self._boss_sprite.alive():
            self._boss_sprite.draw_hp_bar(surface)
