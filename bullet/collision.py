# ============================================================
#  bullet/collision.py  —  Centralised collision detection
# ============================================================
import pygame


class CollisionResult:
    def __init__(self):
        self.score_gained  = 0
        self.player_hit    = False
        self.item_picked   = False
        self.enemy_killed  = 0
        self.boss_killed   = False


def check_all(player, player_bullets, enemy_group, enemy_bullets,
              item_group, explosion_mgr, sfx):
    """Run every collision test each frame; return a CollisionResult."""
    result = CollisionResult()

    # ── Player bullets ↔ Enemies ───────────────────────────────
    hits = pygame.sprite.groupcollide(enemy_group, player_bullets,
                                      False, False,
                                      pygame.sprite.collide_mask)
    for enemy, bullets in hits.items():
        for b in bullets:
            if b.__class__.__name__ == 'LaserBeam':
                if not hasattr(b, 'hit_enemies'):
                    b.hit_enemies = set()
                if enemy in b.hit_enemies:
                    continue
                b.hit_enemies.add(enemy)
            else:
                b.kill()

            killed = enemy.take_damage(b.damage)
            if killed:
                result.score_gained += enemy.score_value
                result.enemy_killed += 1
                explosion_mgr.spawn(enemy.rect.centerx, enemy.rect.centery,
                                    'large' if enemy.score_value >= 300 else 'small')
                sfx.play('explosion_small')
                sfx.play('explosion_small')

    # ── Shotgun Pellets ↔ Enemy Bullets (bullet cancellation) ──
    shotgun_pellets = [b for b in player_bullets if b.__class__.__name__ == 'ShotgunPellet']
    if shotgun_pellets and enemy_bullets:
        temp_shotgun_group = pygame.sprite.Group(shotgun_pellets)
        cancelled = pygame.sprite.groupcollide(temp_shotgun_group, enemy_bullets, True, True)
        if cancelled:
            sfx.play('boss_hit', volume=0.2)

    # ── Enemy bullets ↔ Player ─────────────────────────────────
    if player.alive() and not player.invincible:
        hit_bullets = pygame.sprite.spritecollide(player, enemy_bullets,
                                                  True,
                                                  pygame.sprite.collide_mask)
        if hit_bullets:
            total_dmg = sum(b.damage for b in hit_bullets)
            died = player.take_damage(total_dmg)
            result.player_hit = True
            sfx.play('player_hit')
            if died:
                explosion_mgr.spawn(player.rect.centerx, player.rect.centery, 'huge')
                sfx.play('explosion_large')

    # ── Player ↔ Enemies (ram damage) ──────────────────────────
    if player.alive() and not player.invincible:
        rammed = pygame.sprite.spritecollide(player, enemy_group,
                                             False,
                                             pygame.sprite.collide_mask)
        if rammed:
            for e in rammed:
                e.take_damage(999)
            player.take_damage(40)
            result.player_hit = True
            sfx.play('player_hit')

    # ── Player bullets ↔ Items (shoot to cycle item type) ──────
    item_hits = pygame.sprite.groupcollide(item_group, player_bullets,
                                           False, True)   # kill bullet, keep item
    for item in item_hits:
        item.cycle_type()
        sfx.play('boss_hit', volume=0.4)

    # ── Items ↔ Player ─────────────────────────────────────────
    picked = pygame.sprite.spritecollide(player, item_group, True)
    for item in picked:
        item.apply(player)
        result.item_picked = True
        sfx.play('powerup')

    return result
