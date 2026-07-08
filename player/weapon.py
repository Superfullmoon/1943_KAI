# ============================================================
#  player/weapon.py  —  Weapon-type cycling system
# ============================================================
from config import WEAPON_ORDER, WEAPON_VULCAN


class WeaponSystem:
    """Manages the current weapon type and its upgrade level."""

    def __init__(self):
        self.current  = WEAPON_VULCAN
        self._idx     = 0
        self.level    = 1     # 1–3 upgrade levels per weapon

    def cycle_weapon(self):
        """Rotate to the next weapon type (from item pick-up)."""
        self._idx   = (self._idx + 1) % len(WEAPON_ORDER)
        self.current = WEAPON_ORDER[self._idx]
        self.level   = 1

    def upgrade(self):
        """Upgrade current weapon (up to level 3)."""
        self.level = min(3, self.level + 1)

    @property
    def name(self):
        return self.current
