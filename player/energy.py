# ============================================================
#  player/energy.py  —  Energy / fuel gauge
# ============================================================
from config import (PLAYER_MAX_ENERGY, PLAYER_START_ENERGY,
                    ENERGY_DRAIN_RATE, ENERGY_ITEM_AMOUNT)


class EnergySystem:
    """Energy drains over time; restored by items or stage bonuses."""

    def __init__(self):
        self.value     = float(PLAYER_START_ENERGY)
        self.max_value = float(PLAYER_MAX_ENERGY)

    # ── Per-frame tick ─────────────────────────────────────────
    def drain(self, extra: float = 0.0):
        self.value = max(0.0, self.value - ENERGY_DRAIN_RATE - extra)

    def recover(self, amount: float = ENERGY_ITEM_AMOUNT):
        self.value = min(self.max_value, self.value + amount)

    def full_restore(self):
        self.value = self.max_value

    # ── Queries ────────────────────────────────────────────────
    @property
    def is_empty(self) -> bool:
        return self.value <= 0

    @property
    def fraction(self) -> float:
        return self.value / self.max_value

    @property
    def display_int(self) -> int:
        return int(self.value)
