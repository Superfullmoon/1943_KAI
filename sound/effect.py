# ============================================================
#  sound/effect.py  —  Sound-effects manager
# ============================================================
import pygame, os, math, struct


def synthesize_retro_sound(sound_type: str) -> pygame.mixer.Sound:
    """Synthesizes high-quality, authentic retro PSG-style arcade sound effects in memory."""
    sample_rate = 22050
    data = bytearray()

    if sound_type == 'shoot':
        # Retro pitch sweep
        duration = 0.15
        num_samples = int(sample_rate * duration)
        for i in range(num_samples):
            t = i / sample_rate
            freq = 1200 - 1000 * (t / duration)
            val = math.sin(2 * math.pi * freq * t)
            val = 0.5 * val + 0.5 * (1.0 if val >= 0 else -1.0)
            amplitude = 1.0 - (t / duration)
            sample = int(val * amplitude * 16383)
            data.extend(struct.pack('<h', sample))

    elif sound_type == 'shoot_laser' or sound_type == 'laser':
        # Fast slide
        duration = 0.2
        num_samples = int(sample_rate * duration)
        for i in range(num_samples):
            t = i / sample_rate
            freq = 2000 - 1500 * (t / duration)
            val = math.sin(2 * math.pi * freq * t)
            amplitude = 1.0 - (t / duration)
            sample = int(val * amplitude * 14000)
            data.extend(struct.pack('<h', sample))

    elif sound_type in ('explosion_small', 'exp_small'):
        # White noise burst
        import random
        duration = 0.25
        num_samples = int(sample_rate * duration)
        last_val = 0
        for i in range(num_samples):
            t = i / sample_rate
            r = random.uniform(-1.0, 1.0)
            val = 0.7 * r + 0.3 * last_val
            last_val = val
            amplitude = 1.0 - (t / duration)
            sample = int(val * amplitude * 15000)
            data.extend(struct.pack('<h', sample))

    elif sound_type in ('explosion_large', 'exp_large'):
        # Deep explosion
        import random
        duration = 0.5
        num_samples = int(sample_rate * duration)
        last_val = 0
        for i in range(num_samples):
            t = i / sample_rate
            r = random.uniform(-1.0, 1.0)
            freq = 150 - 120 * (t / duration)
            sine = math.sin(2 * math.pi * freq * t)
            val = 0.6 * r + 0.4 * sine + 0.2 * last_val
            last_val = val
            amplitude = 1.0 - (t / duration)
            sample = int(val * amplitude * 22000)
            data.extend(struct.pack('<h', sample))

    elif sound_type == 'bomb':
        # Siren + explosion
        import random
        duration = 0.8
        num_samples = int(sample_rate * duration)
        for i in range(num_samples):
            t = i / sample_rate
            freq = 800 - 600 * (t / duration) + 150 * math.sin(2 * math.pi * 12 * t)
            sine = math.sin(2 * math.pi * freq * t)
            noise = random.uniform(-1.0, 1.0)
            val = 0.5 * sine + 0.5 * noise
            amplitude = (1.0 - (t / duration)) ** 0.5
            sample = int(val * amplitude * 24000)
            data.extend(struct.pack('<h', sample))

    elif sound_type == 'powerup':
        # Cute chord arpeggio
        duration = 0.3
        num_samples = int(sample_rate * duration)
        notes = [523, 659, 784, 1046]
        for i in range(num_samples):
            t = i / sample_rate
            note_idx = min(int(t / (duration / 4)), 3)
            freq = notes[note_idx]
            val = math.sin(2 * math.pi * freq * t)
            val = 1.0 if val >= 0 else -1.0
            amplitude = 1.0 - (t / duration)
            sample = int(val * amplitude * 12000)
            data.extend(struct.pack('<h', sample))

    elif sound_type == 'player_hit':
        # Harsh buzz
        duration = 0.3
        num_samples = int(sample_rate * duration)
        for i in range(num_samples):
            t = i / sample_rate
            freq = 90
            val = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
            if (i % 200) < 50:
                val *= 0.2
            amplitude = 1.0 - (t / duration)
            sample = int(val * amplitude * 16000)
            data.extend(struct.pack('<h', sample))

    elif sound_type == 'boss_hit':
        # Metallic clank
        duration = 0.08
        num_samples = int(sample_rate * duration)
        for i in range(num_samples):
            t = i / sample_rate
            freq = 600
            val = math.sin(2 * math.pi * freq * t) + math.sin(2 * math.pi * 1.4 * freq * t)
            amplitude = 1.0 - (t / duration)
            sample = int(val * amplitude * 14000)
            data.extend(struct.pack('<h', sample))

    elif sound_type == 'stage_clear':
        # Retro melody
        duration = 1.2
        num_samples = int(sample_rate * duration)
        notes = [392, 523, 659, 784, 1046, 1318, 1568]
        for i in range(num_samples):
            t = i / sample_rate
            note_idx = min(int(t / (duration / len(notes))), len(notes) - 1)
            freq = notes[note_idx]
            vibrato = 1.0 + 0.05 * math.sin(2 * math.pi * 8 * t)
            val = math.sin(2 * math.pi * freq * vibrato * t)
            val = 0.6 * val + 0.4 * (1.0 - abs((i % (sample_rate // freq)) / (sample_rate // freq) - 0.5) * 4)
            amplitude = 1.0 - (t / duration) * 0.5
            sample = int(val * amplitude * 15000)
            data.extend(struct.pack('<h', sample))

    else:
        duration = 0.1
        num_samples = int(sample_rate * duration)
        for i in range(num_samples):
            t = i / sample_rate
            val = math.sin(2 * math.pi * 1000 * t)
            sample = int(val * 10000)
            data.extend(struct.pack('<h', sample))

    try:
        return pygame.mixer.Sound(buffer=bytes(data))
    except Exception:
        return None


class SFXManager:
    """Loads WAV/OGG SFX, falling back to fully synthesized classic PSG retro sounds if files are missing."""

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
            # Try loading WAV first, fall back to synthesized PSG retro sounds
            loaded = False
            if os.path.exists(path):
                try:
                    self._sounds[name] = pygame.mixer.Sound(path)
                    loaded = True
                except Exception:
                    pass

            if not loaded:
                self._sounds[name] = synthesize_retro_sound(name)

    def play(self, name: str, volume: float = 0.8):
        sound = self._sounds.get(name)
        if sound:
            sound.set_volume(volume)
            sound.play()
