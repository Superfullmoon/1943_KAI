# ============================================================
#  sound/bgm.py  —  Background music manager
# ============================================================
import pygame, os


class BGMManager:
    """Loads and plays stage BGM. Gracefully silent if files missing."""

    MUSIC_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets', 'sound')

    BGM_FILES = {
        'title':       'bgm_title.ogg',
        'stage_clear': 'bgm_stage_clear.ogg',
        'gameover':    'bgm_gameover.ogg',
        'victory':     'bgm_victory.ogg',
        **{i: 'bgm_stage{}.ogg'.format(i) for i in range(1, 11)},
    }

    def __init__(self):
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except Exception:
            pass
        self._current = None

    def _play(self, key, loops=-1):
        if self._current == key:
            return
        path = os.path.join(self.MUSIC_DIR, self.BGM_FILES.get(key, ''))
        if not os.path.exists(path):
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.55)
            pygame.mixer.music.play(loops)
            self._current = key
        except Exception:
            pass

    def play_title(self):       self._play('title')
    def play_stage(self, n):    self._play(n, loops=-1)
    def play_stage_clear(self): self._play('stage_clear', loops=0)
    def play_gameover(self):    self._play('gameover', loops=0)
    def play_victory(self):     self._play('victory', loops=0)
    def stop(self):
        try:
            pygame.mixer.music.stop()
            self._current = None
        except Exception:
            pass
