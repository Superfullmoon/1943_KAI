# ============================================================
#  sound/effect.py  —  Sound-effects manager
# ============================================================
import pygame, os


class SFXManager:
    """Loads WAV/OGG SFX. Silent if files are missing."""

    SFX_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets', 'sound')

    SFX_FILES = {
        'shoot':           'sfx_shoot.wav',
        'shoot_laser':     'sfx_laser.wav',
        'explosion_small': 'sfx_exp_small.wav',
        'explosion_large': 'sfx_exp_large.wav',
        'bomb':            'sfx_bomb.wav',
        'powerup':         'sfx_powerup.wav',
        'player_hit':      'sfx_player_hit.wav',
        'boss_hit':        'sfx_boss_hit.wav',
        'stage_clear':     'sfx_stage_clear.wav',
    }

    def __init__(self):
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except Exception:
            pass
        self._sounds = {}
        self._load()

    def _load(self):
        for name, filename in self.SFX_FILES.items():
            path = os.path.join(self.SFX_DIR, filename)
            if os.path.exists(path):
                try:
                    self._sounds[name] = pygame.mixer.Sound(path)
                except Exception:
                    self._sounds[name] = None
            else:
                self._sounds[name] = None

    def play(self, name: str, volume: float = 0.8):
        sound = self._sounds.get(name)
        if sound:
            sound.set_volume(volume)
            sound.play()
