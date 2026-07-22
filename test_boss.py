import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()
pygame.display.set_mode((640, 480))

from enemy.battleship import Destroyer, Cruiser

class DummyPlayer:
    def __init__(self):
        self.rect = pygame.Rect(320, 400, 50, 50)
        self.lives = 3
        self.invincible = False

def test_destroyer_all_components_dead():
    bullet_group = pygame.sprite.Group()
    player = DummyPlayer()

    destroyer = Destroyer(320, 200, bullet_group, player)

    # Initially, components should not be dead
    print("[TEST] Destroyer initialized with components:", len(destroyer.components))
    assert len(destroyer.components) > 0, "Destroyer should have components"
    assert destroyer.all_components_dead is False, "Destroyer's components should not be dead initially"

    # Damage components one by one
    for i, comp in enumerate(destroyer.components):
        print(f"[TEST] Damaging component {i} with HP {comp.hp}...")
        killed = comp.take_damage(comp.hp)
        assert killed is True, f"Component {i} should be killed when taking fatal damage"
        assert comp._destroyed is True, f"Component {i} _destroyed attribute should be True"

        # Check if they are all dead yet
        if i < len(destroyer.components) - 1:
            assert destroyer.all_components_dead is False, f"all_components_dead should be False after killing component {i}"
        else:
            assert destroyer.all_components_dead is True, "all_components_dead should be True after killing all components"

    print("[TEST] test_destroyer_all_components_dead passed successfully!")

def test_cruiser_all_components_dead():
    bullet_group = pygame.sprite.Group()
    player = DummyPlayer()

    cruiser = Cruiser(320, 200, bullet_group, player)

    # Cruiser has no components
    print("[TEST] Cruiser initialized with components:", len(cruiser.components))
    assert len(cruiser.components) == 0, "Cruiser should have 0 components"
    assert cruiser.all_components_dead is True, "Cruiser should have all_components_dead as True by default"
    print("[TEST] test_cruiser_all_components_dead passed successfully!")

if __name__ == "__main__":
    test_destroyer_all_components_dead()
    test_cruiser_all_components_dead()
    print("[TEST] All tests completed and passed successfully!")
