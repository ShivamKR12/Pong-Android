# main.py

"""
IMPROVEMENTS TO BE MADE: 

1. When pressing the back button during an active gameplay, even though the pause menu/screen appears, the game also closes as well, which shouldn't be happening. Need to fix it !
2. When pressing the back button in game difficulty selection menu/screen, instead of going back to the main menu/screen, the game closeing ! Need to fix it !
2. When pressing the back button in settings menu/screen, instead of going back to the main menu/screen, the game closeing ! Need to fix it as well !
"""

import pygame, sys, os, json
from java import jclass

from config import DIFFICULTY_SETTINGS, USER_SETTINGS
from button import Button
from player import Player
from opponent import Opponent
from ball import Ball


class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        self.clock = pygame.time.Clock()

        # Fixed logical resolution - the engine will scale this to the device screen
        self.screen_width = 640
        self.screen_height = 360
        self.screen = pygame.display.set_mode(
            (self.screen_width, self.screen_height), 
            pygame.FULLSCREEN | pygame.SCALED
        )
        
        self.ctx = jclass("org.anvlabs.anvpy.NewActivity").ctx
        self.ctx.setRequestedOrientation(0)
        
        self.PATH = os.path.abspath(".") + "/"
        self.config_path = self.PATH + "config.json"
        
        self.bg_color = pygame.Color('#2F373F')
        self.accent_color = (27, 35, 43)
        self.highlight_color = (210, 78, 61)
        
        self.plob_sound = pygame.mixer.Sound(self.PATH + "assets/pong.ogg")
        self.score_sound = pygame.mixer.Sound(self.PATH + "assets/score.ogg")
        self.click_sound = pygame.mixer.Sound(self.PATH + "assets/click.ogg")

        self.state = "MENU"
        self.play_mode = "PVE" 
        self.winner = None
        
        self.finger_id_left = None
        self.finger_id_right = None
        
        self.load_settings()
        self.update_dynamic_settings()
        self.setup_ui_elements()

    def load_settings(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    saved_settings = json.load(f)
                    for key, value in saved_settings.items():
                        if key in USER_SETTINGS:
                            USER_SETTINGS[key] = value
            except Exception as e:
                print(f"Failed to load settings: {e}")

    def save_settings(self):
        try:
            with open(self.config_path, "w") as f:
                json.dump(USER_SETTINGS, f, indent=4)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def reset_to_defaults(self):
        USER_SETTINGS["win_score"] = 5
        USER_SETTINGS["scale_factor"] = 0.5
        self.save_settings()
        self.setup_ui_elements()

    def update_dynamic_settings(self):
        # Universal safe zone margins (8% of screen width) to avoid notches/edges
        self.margin_left = int(self.screen_width * 0.08)
        self.margin_right = int(self.screen_width * 0.08)
        self.play_width = self.screen_width - self.margin_left - self.margin_right
        self.play_center_x = self.margin_left + (self.play_width / 2)
        
        # Fonts are now fixed since the logical resolution is fixed
        self.font = pygame.font.Font('freesansbold.ttf', 16)
        self.title_font = pygame.font.Font('freesansbold.ttf', 32)
        self.settings_font = pygame.font.Font('freesansbold.ttf', 24)

    def setup_ui_elements(self):
        cw = self.screen_width
        ch = self.screen_height
        cx = cw / 2
        
        btn_width = cw * 0.2
        btn_height = ch * 0.12
        
        # Main Menu (Start Screen)
        self.btn_play = Button("PLAY", cx, ch * 0.40, btn_width + 50, btn_height, self.font, self.accent_color, self.highlight_color)
        self.btn_settings_nav = Button("SETTINGS", cx, ch * 0.55, btn_width + 50, btn_height, self.font, self.accent_color, self.highlight_color)
        self.btn_quit_main = Button("QUIT", cx, ch * 0.70, btn_width + 50, btn_height, self.font, self.accent_color, self.highlight_color)

        # Play Menu (Mode & Difficulty)
        self.btn_mode = Button("MODE: VS AI", cx, ch * 0.30, btn_width + 50, btn_height, self.font, self.accent_color, self.highlight_color)
        self.btn_easy = Button("EASY", cx, ch * 0.45, btn_width, btn_height, self.font, self.accent_color, self.highlight_color)
        self.btn_normal = Button("NORMAL", cx, ch * 0.60, btn_width, btn_height, self.font, self.accent_color, self.highlight_color)
        self.btn_hard = Button("HARD", cx, ch * 0.75, btn_width, btn_height, self.font, self.accent_color, self.highlight_color)
        self.btn_play_back = Button("BACK", cx, ch * 0.90, btn_width, btn_height, self.font, self.accent_color, self.highlight_color)
        
        self.btn_menu = Button("MAIN MENU", cx, ch * 0.75, btn_width + 50, btn_height, self.font, self.accent_color, self.highlight_color)

        # Settings Menu (Streamlined)
        self.settings_config = [
            {
                "key": "win_score", 
                "label": "WIN SCORE", 
                "step": 1, 
                "min": 1, 
                "max": 20, 
                "type": "int"
            },
            {
                "key": "scale_factor", 
                "label": "GAME SCALE", 
                "step": 0.1, 
                "min": 0.2, 
                "max": 1.5, 
                "type": "float"
            }
        ]
        
        self.setting_ui_elements = []
        small_btn_w = cw * 0.15
        small_btn_h = ch * 0.15
        btn_offset_x = cw * 0.35
        
        start_y = ch * 0.40
        y_gap = ch * 0.25

        for i, config in enumerate(self.settings_config):
            y_pos = start_y + (i * y_gap)
            btn_minus = Button("-", cx - btn_offset_x, y_pos, small_btn_w, small_btn_h, self.settings_font, self.accent_color, self.highlight_color)
            btn_plus = Button("+", cx + btn_offset_x, y_pos, small_btn_w, small_btn_h, self.settings_font, self.accent_color, self.highlight_color)
            
            self.setting_ui_elements.append({
                "config": config,
                "btn_minus": btn_minus,
                "btn_plus": btn_plus,
                "y_pos": y_pos
            })

        self.btn_settings_back = Button("BACK", cx - cw * 0.18, ch * 0.90, cw * 0.3, btn_height, self.font, self.accent_color, self.highlight_color)
        self.btn_settings_reset = Button("RESET", cx + cw * 0.18, ch * 0.90, cw * 0.3, btn_height, self.font, self.accent_color, self.highlight_color)

        # Pause Menu
        self.btn_resume = Button("RESUME", cx, ch * 0.45, btn_width + 50, btn_height, self.font, self.accent_color, self.highlight_color)
        self.btn_quit = Button("QUIT TO MENU", cx, ch * 0.65, btn_width + 50, btn_height, self.font, self.accent_color, self.highlight_color)

    def start_game(self, difficulty):
        self.player_score = 0
        self.opponent_score = 0
        self.winner = None
        self.finger_id_left = None
        self.finger_id_right = None
        
        diff_config = DIFFICULTY_SETTINGS[difficulty]
        
        # Grab the custom scale factor and create a dynamically scaled font for scores
        scale_val = USER_SETTINGS["scale_factor"]
        # Base scale was 0.5 mapping to font size 16 (so base font size is 32)
        self.score_font = pygame.font.Font('freesansbold.ttf', max(8, int(32 * scale_val)))

        self.paddle_right = Player(
            self.PATH + 'assets/Paddle.png', 
            self.screen_width - 20, 
            self.screen_height / 2, 
            5, diff_config["instant_drag"], 
            scale=scale_val
        )
        
        if self.play_mode == "PVP":
            self.paddle_left = Player(
                self.PATH + 'assets/Paddle.png', 
                self.margin_left - 35, 
                self.screen_height / 2, 
                5, diff_config["instant_drag"], 
                scale=scale_val
            )
        else:
            self.paddle_left = Opponent(
                self.PATH + 'assets/Paddle.png', 
                self.margin_left - 35, 
                self.screen_height / 2, 
                diff_config["ai_speed"], 
                diff_config["ai_tolerance"], 
                scale=scale_val
            )
        
        self.paddle_group = pygame.sprite.Group()
        self.paddle_group.add(self.paddle_right)
        self.paddle_group.add(self.paddle_left)

        self.ball = Ball(
            self.PATH + 'assets/Ball.png', 
            self.play_center_x, 
            self.screen_height / 2, 
            diff_config, 
            self.paddle_group, 
            self.plob_sound, 
            self.score_sound, 
            self.score_font,  # Pass scaled font here
            self.bg_color, 
            self.accent_color, 
            scale=scale_val
        )
        self.ball_sprite = pygame.sprite.GroupSingle()
        self.ball_sprite.add(self.ball)
        
        self.state = "PLAYING"

    def modify_setting(self, key, step, is_float):
        if is_float:
            USER_SETTINGS[key] = round(USER_SETTINGS[key] + step, 1)
        else:
            USER_SETTINGS[key] += step
            
        self.save_settings()
        self.setup_ui_elements() 

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Contextual Android Back Button Logic
            if event.type == pygame.KEYDOWN and event.key == pygame.K_AC_BACK:
                if self.state == "PLAYING":
                    self.state = "PAUSED"
                elif self.state == "PAUSED":
                    # Pressing back while paused resumes the game
                    self.state = "PLAYING"
                    self.finger_id_left = None
                    self.finger_id_right = None
                elif self.state in ["SETTINGS", "GAME_OVER", "PLAY_MENU"]:
                    # Pressing back in sub-menus returns to the main menu
                    self.state = "MENU"
                elif self.state == "MENU":
                    # Pressing back on the main menu exits the app
                    pygame.quit()
                    sys.exit()

            # Auto-Pause if the system tray is pulled down or app minimizes
            if event.type == pygame.WINDOWFOCUSLOST or event.type == pygame.APP_WILLENTERBACKGROUND:
                if self.state == "PLAYING":
                    self.state = "PAUSED"
                
            if event.type == pygame.FINGERDOWN:
                if self.state == "PLAYING":
                    py = event.y * self.screen_height
                    if event.x > 0.5 and self.finger_id_right is None:
                        self.finger_id_right = event.finger_id
                        self.paddle_right.touch_target_y = py
                    elif event.x <= 0.5 and self.finger_id_left is None and self.play_mode == "PVP":
                        self.finger_id_left = event.finger_id
                        self.paddle_left.touch_target_y = py

            if event.type == pygame.FINGERMOTION:
                if self.state == "PLAYING":
                    py = event.y * self.screen_height
                    if event.finger_id == self.finger_id_right:
                        self.paddle_right.touch_target_y = py
                    elif event.finger_id == self.finger_id_left and self.play_mode == "PVP":
                        self.paddle_left.touch_target_y = py

            if event.type == pygame.FINGERUP:
                px = event.x * self.screen_width
                py = event.y * self.screen_height
                
                if self.state == "MENU":
                    if self.btn_play.check_click(px, py):
                        pygame.mixer.Sound.play(self.click_sound)
                        self.state = "PLAY_MENU"
                    elif self.btn_settings_nav.check_click(px, py):
                        pygame.mixer.Sound.play(self.click_sound)
                        self.state = "SETTINGS"
                    elif self.btn_quit_main.check_click(px, py):
                        pygame.mixer.Sound.play(self.click_sound)
                        pygame.quit()
                        sys.exit()

                elif self.state == "PLAY_MENU":
                    if self.btn_mode.check_click(px, py):
                        pygame.mixer.Sound.play(self.click_sound)
                        self.play_mode = "PVP" if self.play_mode == "PVE" else "PVE"
                        mode_text = "MODE: VS PLAYER" if self.play_mode == "PVP" else "MODE: VS AI"
                        self.btn_mode.update_text(mode_text, self.font, self.highlight_color)
                    elif self.btn_easy.check_click(px, py):
                        pygame.mixer.Sound.play(self.click_sound)
                        self.start_game("EASY")
                    elif self.btn_normal.check_click(px, py):
                        pygame.mixer.Sound.play(self.click_sound)
                        self.start_game("NORMAL")
                    elif self.btn_hard.check_click(px, py):
                        pygame.mixer.Sound.play(self.click_sound)
                        self.start_game("HARD")
                    elif self.btn_play_back.check_click(px, py):
                        pygame.mixer.Sound.play(self.click_sound)
                        self.state = "MENU"
                        
                elif self.state == "SETTINGS":
                    if self.btn_settings_back.check_click(px, py):
                        pygame.mixer.Sound.play(self.click_sound)
                        self.state = "MENU"
                        continue
                        
                    if self.btn_settings_reset.check_click(px, py):
                        pygame.mixer.Sound.play(self.click_sound)
                        self.reset_to_defaults()
                        continue
                        
                    for ui in self.setting_ui_elements:
                        config = ui["config"]
                        key = config["key"]
                        is_float = (config["type"] == "float")
                        
                        if ui["btn_minus"].check_click(px, py) and round(USER_SETTINGS[key], 1) > config["min"]:
                            pygame.mixer.Sound.play(self.click_sound)
                            self.modify_setting(key, -config["step"], is_float)
                            
                        elif ui["btn_plus"].check_click(px, py) and round(USER_SETTINGS[key], 1) < config["max"]:
                            pygame.mixer.Sound.play(self.click_sound)
                            self.modify_setting(key, config["step"], is_float)
                        
                elif self.state == "GAME_OVER":
                    if self.btn_menu.check_click(px, py):
                        pygame.mixer.Sound.play(self.click_sound)
                        self.state = "MENU"

                elif self.state == "PAUSED":
                    if self.btn_resume.check_click(px, py):
                        pygame.mixer.Sound.play(self.click_sound)
                        self.state = "PLAYING"
                        # Reset touches to prevent paddle jumping
                        self.finger_id_right = None
                        self.finger_id_left = None
                    elif self.btn_quit.check_click(px, py):
                        pygame.mixer.Sound.play(self.click_sound)
                        self.state = "MENU"
                        
                elif self.state == "PLAYING":
                    if event.finger_id == self.finger_id_right:
                        self.finger_id_right = None
                        self.paddle_right.touch_target_y = None
                    elif event.finger_id == self.finger_id_left and self.play_mode == "PVP":
                        self.finger_id_left = None
                        self.paddle_left.touch_target_y = None
                        
                    # Top-middle screen tap to pause manually
                    if py < self.screen_height * 0.15 and px > self.screen_width * 0.4 and px < self.screen_width * 0.6:
                        self.state = "PAUSED"

    def check_score(self):
        winning_score = USER_SETTINGS["win_score"]
        
        # Check if the left side of the ball passes the right screen edge
        if self.ball.rect.left >= self.screen_width:
            self.opponent_score += 1
            if self.opponent_score >= winning_score:
                self.winner = "Player 2" if self.play_mode == "PVP" else "Opponent"
                self.state = "GAME_OVER"
            else:
                self.ball.reset_ball(self.play_center_x, self.screen_height)
            
        # Check if the right side of the ball passes the left screen edge
        if self.ball.rect.right <= 0:
            self.player_score += 1
            if self.player_score >= winning_score:
                self.winner = "Player 1" if self.play_mode == "PVP" else "Player"
                self.state = "GAME_OVER"
            else:
                self.ball.reset_ball(self.play_center_x, self.screen_height)

    def draw_score(self):
        player_score_text = self.score_font.render(str(self.player_score), True, self.accent_color)
        opponent_score_text = self.score_font.render(str(self.opponent_score), True, self.accent_color)

        player_score_rect = player_score_text.get_rect(midleft=(self.play_center_x + 40, 40))
        opponent_score_rect = opponent_score_text.get_rect(midright=(self.play_center_x - 40, 40))

        self.screen.blit(player_score_text, player_score_rect)
        self.screen.blit(opponent_score_text, opponent_score_rect)

    def draw_board(self):
        self.screen.fill(self.bg_color)
        middle_strip = pygame.Rect(self.play_center_x - 2, 0, 4, self.screen_height)
        pygame.draw.rect(self.screen, self.accent_color, middle_strip)

    def update(self):
        if self.state == "PLAYING":
            self.paddle_group.update(self.ball_sprite, self.screen_height)
            self.ball.update(self.play_center_x, self.screen_height, self.screen)
            self.check_score()

    def render(self):
        self.screen.fill(self.bg_color)
        true_center_x = self.screen_width / 2
        
        if self.state == "MENU":
            title_text = self.title_font.render("PONG", True, self.highlight_color)
            title_rect = title_text.get_rect(center=(true_center_x, self.screen_height * 0.15))
            self.screen.blit(title_text, title_rect)
            
            self.btn_play.draw(self.screen)
            self.btn_settings_nav.draw(self.screen)
            self.btn_quit_main.draw(self.screen)

        elif self.state == "PLAY_MENU":
            title_text = self.title_font.render("PLAY", True, self.highlight_color)
            title_rect = title_text.get_rect(center=(true_center_x, self.screen_height * 0.15))
            self.screen.blit(title_text, title_rect)
            
            self.btn_mode.draw(self.screen)
            self.btn_easy.draw(self.screen)
            self.btn_normal.draw(self.screen)
            self.btn_hard.draw(self.screen)
            self.btn_play_back.draw(self.screen)
            
        elif self.state == "SETTINGS":
            title_text = self.title_font.render("SETTINGS", True, self.highlight_color)
            title_rect = title_text.get_rect(center=(true_center_x, self.screen_height * 0.15))
            self.screen.blit(title_text, title_rect)
            
            for ui in self.setting_ui_elements:
                ui["btn_minus"].draw(self.screen)
                ui["btn_plus"].draw(self.screen)
                
                key = ui["config"]["key"]
                if ui["config"]["type"] == "int":
                    display_val = int(USER_SETTINGS[key])
                else:
                    display_val = f"{USER_SETTINGS[key]:.1f}"
                label_str = f"{ui['config']['label']}: {display_val}"
                
                label_text = self.settings_font.render(label_str, True, self.highlight_color)
                label_rect = label_text.get_rect(center=(true_center_x, ui["y_pos"]))
                self.screen.blit(label_text, label_rect)
                
            self.btn_settings_back.draw(self.screen)
            self.btn_settings_reset.draw(self.screen)
            
        elif self.state == "PLAYING":
            self.draw_board()
            self.paddle_group.draw(self.screen)
            self.ball_sprite.draw(self.screen)
            self.draw_score()

        elif self.state == "PAUSED":
            # Draw board in background
            self.draw_board()
            self.paddle_group.draw(self.screen)
            self.ball_sprite.draw(self.screen)
            self.draw_score()
            
            # Semi-transparent overlay
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            
            pause_text = self.title_font.render("PAUSED", True, self.highlight_color)
            pause_rect = pause_text.get_rect(center=(true_center_x, self.screen_height * 0.20))
            self.screen.blit(pause_text, pause_rect)
            
            self.btn_resume.draw(self.screen)
            self.btn_quit.draw(self.screen)
            
        elif self.state == "GAME_OVER":
            msg = f"{self.winner.upper()} WINS!" if "Player" in self.winner else "YOU LOSE!"
            outcome_text = self.title_font.render(msg, True, self.highlight_color)
            outcome_rect = outcome_text.get_rect(center=(true_center_x, self.screen_height * 0.40))
            self.screen.blit(outcome_text, outcome_rect)
            
            score_text = self.font.render(f"{self.player_score} - {self.opponent_score}", True, self.accent_color)
            score_rect = score_text.get_rect(center=(true_center_x, self.screen_height * 0.55))
            self.screen.blit(score_text, score_rect)
            
            self.btn_menu.draw(self.screen)

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.render()
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()
