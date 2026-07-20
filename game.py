# ============================================================
#  game.py  —  Main Game Orchestrator (1943 KAI)
# ============================================================
import pygame
import sys
import os
import json

from config import *
from player.player import Player
from sound.effect import SFXManager
from sound.bgm import BGMManager
from stage.stage_manager import StageManager
from bullet.collision import check_all
from effects.explosion import ExplosionManager
from effects.bomb import BombEffect
from ui.start import TitleScreen
from ui.gameover import GameOverScreen
from ui.energy_bar import EnergyBar
from ui.score import ScoreDisplay

# 게임 상태 정의
STATE_TITLE = "TITLE"
STATE_PLAYING = "PLAYING"
STATE_PAUSED = "PAUSED"
STATE_STAGE_CLEAR = "STAGE_CLEAR"
STATE_GAMEOVER = "GAMEOVER"
STATE_GAME_CLEAR = "GAME_CLEAR"


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # 사운드 및 이펙트 관리자
        self.sfx = SFXManager()
        self.bgm = BGMManager()
        self.explosion_manager = ExplosionManager()
        self.bomb_effect = BombEffect()

        # 점수 관리 및 최고 기록
        self.score = 0
        self.highscore = 0
        self.highscore_file = os.path.join(os.path.dirname(__file__), 'save', 'highscore.json')
        self.load_highscore()

        # UI 스크린들
        self.title_screen = TitleScreen(self.screen)
        self.gameover_screen = GameOverScreen(self.screen)
        self.score_display = ScoreDisplay(self.score, self.highscore)

        # 게임 상태 초기화
        self.state = STATE_TITLE
        self.player = None
        self.stage_manager = None
        self.energy_bar = None
        self.launch_timer = 0
        self.carrier_y = 0

        # 타이틀 BGM 시작
        self.bgm.play_title()

    def load_highscore(self):
        try:
            os.makedirs(os.path.dirname(self.highscore_file), exist_ok=True)
            if os.path.exists(self.highscore_file):
                with open(self.highscore_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.highscore = data.get('highscore', 0)
        except Exception as e:
            print("Failed to load highscore: {}".format(e))
            self.highscore = 0

    def save_highscore(self):
        try:
            os.makedirs(os.path.dirname(self.highscore_file), exist_ok=True)
            with open(self.highscore_file, 'w', encoding='utf-8') as f:
                json.dump({'highscore': self.highscore}, f, indent=4)
        except Exception as e:
            print("Failed to save highscore: {}".format(e))

    def reset_game(self):
        """게임 시작 시 혹은 재시작 시 게임 상태를 리셋합니다."""
        self.score = 0
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.stage_manager = StageManager(self.player, self.sfx)
        self.energy_bar = EnergyBar(self.player)
        self.score_display.update(self.score, self.highscore)
        self.launch_timer = 180
        self.carrier_y = SCREEN_HEIGHT - 360

    def start_game(self):
        self.reset_game()
        self.bgm.play_stage(self.stage_manager.current_stage_num)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if self.state == STATE_TITLE:
                    if event.key == KEY_START:
                        self.start_game()
                        self.state = STATE_PLAYING

                elif self.state == STATE_PLAYING:
                    if event.key == KEY_PAUSE:
                        self.state = STATE_PAUSED
                    elif event.key == KEY_BOMB:
                        self.use_bomb()

                elif self.state == STATE_PAUSED:
                    if event.key == KEY_PAUSE:
                        self.state = STATE_PLAYING

                elif self.state == STATE_STAGE_CLEAR:
                    if event.key == KEY_START:
                        self.advance_stage()

                elif self.state == STATE_GAMEOVER:
                    if event.key == KEY_START:
                        self.state = STATE_TITLE
                        self.bgm.play_title()

                elif self.state == STATE_GAME_CLEAR:
                    if event.key == KEY_START:
                        self.state = STATE_TITLE
                        self.bgm.play_title()

    def use_bomb(self):
        """메가크래시(폭탄)를 사용합니다."""
        if self.player and self.player.alive() and self.player.bomb_count > 0:
            self.player.bomb_count -= 1
            self.bomb_effect.activate()
            self.sfx.play('bomb')

            # 화면에 있는 적 탄환 제거
            self.stage_manager.enemy_bullet_group.empty()

            # 화면에 있는 적들에게 데미지
            for enemy in list(self.stage_manager.enemy_group):
                # 보스 혹은 보스 컴포넌트 여부에 관계없이 모두 데미지
                enemy.take_damage(BOMB_DAMAGE)

    def advance_stage(self):
        """다음 스테이지로 진입하거나, 최종 클리어 판정합니다."""
        if self.stage_manager.current_stage_num < TOTAL_STAGES:
            self.stage_manager.next_stage()
            # 다음 스테이지 가기 전에 플레이어 라이프 및 에너지를 일부 혹은 전부 복구
            self.player.energy.full_restore()
            self.state = STATE_PLAYING
            self.launch_timer = 180
            self.carrier_y = SCREEN_HEIGHT - 360
            self.bgm.play_stage(self.stage_manager.current_stage_num)
        else:
            # 보너스 점수 가산
            self.score += SCORE_BONUS_CLEAR
            if self.score > self.highscore:
                self.highscore = self.score
                self.save_highscore()
            self.state = STATE_GAME_CLEAR
            self.bgm.play_victory()

    def update(self):
        if self.state == STATE_PLAYING:
            # ── Takeoff Intro Sequence (Carrier Launch) ─────────────────────
            if self.launch_timer > 0:
                self.launch_timer -= 1
                self.carrier_y += 3
                if self.launch_timer > 100:
                    self.player.rect.centerx = SCREEN_WIDTH // 2
                    self.player.rect.centery = self.carrier_y + 220
                else:
                    self.player.rect.centerx = SCREEN_WIDTH // 2
                    self.player.rect.centery = max(SCREEN_HEIGHT - 180, self.player.rect.centery - 4)
                    if self.launch_timer == 100:
                        self.sfx.play('powerup')
                self.stage_manager._bg.update()
                self.player.options.update(self.player.rect.centerx, self.player.rect.centery)
                self.explosion_manager.update()
                self.bomb_effect.update()
                return

            # 1. 키 입력 감지 후 플레이어 업데이트
            keys = pygame.key.get_pressed()
            self.player.update(keys, self.stage_manager.player_bullet_group)

            # 2. 스테이지 매니저 업데이트 (적 스폰, 그룹 업데이트)
            score_gained = self.stage_manager.update()
            self.score += score_gained

            # 3. 충돌 체크
            collision_result = check_all(
                player=self.player,
                player_bullets=self.stage_manager.player_bullet_group,
                enemy_group=self.stage_manager.enemy_group,
                enemy_bullets=self.stage_manager.enemy_bullet_group,
                item_group=self.stage_manager.item_group,
                explosion_mgr=self.explosion_manager,
                sfx=self.sfx
            )

            # 충돌 점수 합산
            self.score += collision_result.score_gained

            # 하이스코어 실시간 업데이트
            if self.score > self.highscore:
                self.highscore = self.score

            self.score_display.update(self.score, self.highscore)

            # 4. 폭발 및 폭탄 이펙트 업데이트
            self.explosion_manager.update()
            self.bomb_effect.update()

            # 5. 플레이어 사망(라이프 소진) 여부 체크
            if self.player.lives <= 0:
                self.state = STATE_GAMEOVER
                self.bgm.play_gameover()
                self.save_highscore()

            # 6. 스테이지 클리어 체크
            elif self.stage_manager.is_stage_clear():
                self.state = STATE_STAGE_CLEAR
                self.bgm.play_stage_clear()

        elif self.state == STATE_STAGE_CLEAR:
            # 스테이지 클리어 중에도 이펙트와 배경은 지속 갱신
            self.explosion_manager.update()
            self.stage_manager._bg.update()

    def draw_takeoff_carrier(self, surface):
        """Draws a beautiful aircraft carrier flight deck for takeoff."""
        w, h = 140, 480
        x = SCREEN_WIDTH // 2 - w // 2
        y = self.carrier_y

        # Flight deck base
        pygame.draw.rect(surface, (50, 52, 60), (x, y, w, h))
        pygame.draw.rect(surface, (110, 100, 90), (x + 10, y + 10, w - 20, h - 20)) # Wood deck

        # Runway markings (yellow dashed line in center)
        for dy in range(15, h - 15, 30):
            pygame.draw.line(surface, YELLOW, (SCREEN_WIDTH // 2, y + dy), (SCREEN_WIDTH // 2, y + dy + 15), 3)

        # Left/Right runway borders (white lines)
        pygame.draw.line(surface, WHITE, (x + 15, y), (x + 15, y + h), 2)
        pygame.draw.line(surface, WHITE, (x + w - 15, y), (x + w - 15, y + h), 2)

        # Bow pointer (pointy carrier front at top of deck)
        pygame.draw.polygon(surface, (40, 42, 50), [(x, y), (SCREEN_WIDTH // 2, y - 40), (x + w, y)])

        # Large yellow "43" painted on the runway to symbolize 1943!
        font = pygame.font.SysFont('Arial Black', 32, bold=True)
        num_txt = font.render("43", True, YELLOW)
        surface.blit(num_txt, (SCREEN_WIDTH // 2 - num_txt.get_width() // 2, y + h - 120))

    def draw(self):
        self.screen.fill(BLACK)

        if self.state == STATE_TITLE:
            self.title_screen.draw()

        elif self.state == STATE_PLAYING or self.state == STATE_PAUSED or self.state == STATE_STAGE_CLEAR:
            # 1. 배경 그리기
            self.stage_manager.draw_background(self.screen)

            # Draw takeoff carrier on the ocean but behind other elements
            if self.launch_timer > 0:
                self.draw_takeoff_carrier(self.screen)

            # 2. 스프라이트 그룹 그리기
            self.stage_manager.enemy_group.draw(self.screen)
            self.stage_manager.player_bullet_group.draw(self.screen)
            self.stage_manager.enemy_bullet_group.draw(self.screen)
            self.stage_manager.item_group.draw(self.screen)

            # 3. 플레이어 그리기
            if self.player.alive():
                self.player.draw(self.screen)

            # 4. 이펙트 그리기
            self.explosion_manager.draw(self.screen)
            self.bomb_effect.draw(self.screen)

            # 5. 보스 HP 바
            self.stage_manager.draw_boss_hp(self.screen)

            # 6. HUD UI 그리기
            self.score_display.draw(self.screen)
            self.energy_bar.draw(self.screen)

            # 7. 플레이어 잔탄/라이프/폭탄 표시
            self.draw_hud_extras()

            # 일시 정지 오버레이
            if self.state == STATE_PAUSED:
                self.draw_paused_overlay()

            # 스테이지 클리어 오버레이
            elif self.state == STATE_STAGE_CLEAR:
                self.draw_stage_clear_overlay()

        elif self.state == STATE_GAMEOVER:
            self.gameover_screen.draw(self.score, self.highscore)

        elif self.state == STATE_GAME_CLEAR:
            self.draw_game_clear_screen()

        pygame.display.flip()

    def draw_hud_extras(self):
        """라이프와 폭탄 개수, 그리고 현재 무기 레벨 정보를 화면 하단에 그립니다."""
        font = pygame.font.SysFont('Consolas', 14, bold=True)

        # 1. 라이프 그리기 (LIVES: 3)
        lives_txt = font.render("LIVES: {}".format(self.player.lives), True, WHITE)
        self.screen.blit(lives_txt, (20, SCREEN_HEIGHT - 34))

        # 2. 폭탄 개수 그리기 (BOMB: X X X)
        bombs = "[BOMB]" + " X" * self.player.bomb_count
        bomb_txt = font.render(bombs, True, YELLOW)
        self.screen.blit(bomb_txt, (20, SCREEN_HEIGHT - 54))

        # 3. 무기 레벨 및 타입 정보 (WEAPON: VULCAN Lv.1)
        wp_info = "WEAPON: {} Lv.{}".format(self.player.weapon.current, self.player.weapon.level)
        wp_txt = font.render(wp_info, True, CYAN)
        self.screen.blit(wp_txt, (SCREEN_WIDTH - 220, SCREEN_HEIGHT - 54))

    def draw_paused_overlay(self):
        # 반투명 어두운 화면
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.SysFont('Arial Black', 48, bold=True)
        txt = font.render("PAUSED", True, WHITE)
        cx = SCREEN_WIDTH // 2 - txt.get_width() // 2
        cy = SCREEN_HEIGHT // 2 - 40
        self.screen.blit(txt, (cx, cy))

        font_sm = pygame.font.SysFont('Consolas', 18)
        sub = font_sm.render("PRESS ESC TO RESUME", True, GRAY)
        cx_sub = SCREEN_WIDTH // 2 - sub.get_width() // 2
        self.screen.blit(sub, (cx_sub, cy + 70))

    def draw_stage_clear_overlay(self):
        # 반투명 어두운 화면
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.SysFont('Arial Black', 48, bold=True)
        txt = font.render("STAGE CLEAR", True, GOLD)
        cx = SCREEN_WIDTH // 2 - txt.get_width() // 2
        cy = SCREEN_HEIGHT // 2 - 80
        self.screen.blit(txt, (cx, cy))

        # 정산 안내
        font_lg = pygame.font.SysFont('Arial', 24, bold=True)
        stage_name = STAGE_THEMES.get(self.stage_manager.current_stage_num, {}).get('name', '')
        info_txt = font_lg.render("Cleared: {}".format(stage_name), True, WHITE)
        cx_info = SCREEN_WIDTH // 2 - info_txt.get_width() // 2
        self.screen.blit(info_txt, (cx_info, cy + 70))

        font_sm = pygame.font.SysFont('Consolas', 18)
        sub = font_sm.render("PRESS ENTER FOR NEXT STAGE", True, YELLOW)
        cx_sub = SCREEN_WIDTH // 2 - sub.get_width() // 2
        self.screen.blit(sub, (cx_sub, cy + 130))

    def draw_game_clear_screen(self):
        self.screen.fill(DARK_BLUE)

        # 반투명 금빛 하이라이트
        glow = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        glow.fill((200, 150, 0, 20))
        self.screen.blit(glow, (0, 0))

        font_xl = pygame.font.SysFont('Arial Black', 54, bold=True)
        title_txt = font_xl.render("VICTORY!", True, GOLD)
        cx = SCREEN_WIDTH // 2 - title_txt.get_width() // 2
        self.screen.blit(title_txt, (cx, SCREEN_HEIGHT // 2 - 150))

        font_lg = pygame.font.SysFont('Arial', 28, bold=True)
        sub1 = font_lg.render("PACIFIC OCEAN LIBERATED", True, WHITE)
        self.screen.blit(sub1, (SCREEN_WIDTH // 2 - sub1.get_width() // 2, SCREEN_HEIGHT // 2 - 50))

        # 최종 스코어 및 베스트 스코어
        font_md = pygame.font.SysFont('Consolas', 22, bold=True)
        score_txt = font_md.render("FINAL SCORE  {:0>8}".format(self.score), True, CYAN)
        hi_txt = font_md.render("BEST SCORE   {:0>8}".format(self.highscore), True, GOLD)
        self.screen.blit(score_txt, (SCREEN_WIDTH // 2 - score_txt.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(hi_txt, (SCREEN_WIDTH // 2 - hi_txt.get_width() // 2, SCREEN_HEIGHT // 2 + 55))

        # 메인메뉴 안내
        if (pygame.time.get_ticks() // 400) % 2 == 0:
            prompt = font_md.render("PRESS ENTER TO MAIN MENU", True, SILVER)
            self.screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, SCREEN_HEIGHT // 2 + 130))


    def run(self):
        """게임 메인 루프."""
        while self.running:
            self.clock.tick(FPS)   # FPS는 설정 파일에 정의된 값 (없으면 60)
            self.handle_events()
            self.update()
            self.draw()

        # 종료 시 마무리
        self.save_highscore()
        pygame.quit()
        sys.exit()