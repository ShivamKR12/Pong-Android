# ball.py

import pygame, random
from block import Block


class Ball(Block):
    def __init__(self, path, x_pos, y_pos, diff_config, paddles, plob_sound, score_sound, font, bg_color, accent_color, scale = 1.0):
        super().__init__(path, x_pos, y_pos, scale)
        
        self.base_speed_x = diff_config["ball_x"]
        self.base_speed_y = diff_config["ball_y"]
        self.speed_inc = diff_config["speed_inc"]
        self.max_speed = diff_config["max_speed"]
        
        self.speed_x = self.base_speed_x * random.choice((-1, 1))
        self.speed_y = self.base_speed_y * random.choice((-1, 1))
        
        self.paddles = paddles
        self.active = False
        self.score_time = 0
        
        self.plob_sound = plob_sound
        self.score_sound = score_sound
        self.font = font
        self.bg_color = bg_color
        self.accent_color = accent_color

    def update(self, play_center_x, current_screen_height, screen):
        if self.active:
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y
            self.collisions(current_screen_height)
        else:
            self.restart_counter(play_center_x, current_screen_height, screen)

    def increase_speed(self):
        if abs(self.speed_x) < self.max_speed:
            self.speed_x += self.speed_inc if self.speed_x > 0 else -self.speed_inc
        if abs(self.speed_y) < self.max_speed:
            self.speed_y += self.speed_inc if self.speed_y > 0 else -self.speed_inc

    def collisions(self, current_screen_height):
        if self.rect.top <= 0 or self.rect.bottom >= current_screen_height:
            pygame.mixer.Sound.play(self.plob_sound)
            self.speed_y *= -1

        if pygame.sprite.spritecollide(self, self.paddles, False):
            pygame.mixer.Sound.play(self.plob_sound)
            collision_paddle = pygame.sprite.spritecollide(self, self.paddles, False)[0].rect

            thresh_x = abs(self.speed_x) + 10
            thresh_y = abs(self.speed_y) + 10

            if abs(self.rect.right - collision_paddle.left) < thresh_x and self.speed_x > 0:
                self.speed_x *= -1
                self.increase_speed()
            elif abs(self.rect.left - collision_paddle.right) < thresh_x and self.speed_x < 0:
                self.speed_x *= -1
                self.increase_speed()
            elif abs(self.rect.top - collision_paddle.bottom) < thresh_y and self.speed_y < 0:
                self.rect.top = collision_paddle.bottom
                self.speed_y *= -1
            elif abs(self.rect.bottom - collision_paddle.top) < thresh_y and self.speed_y > 0:
                self.rect.bottom = collision_paddle.top
                self.speed_y *= -1

    def reset_ball(self, play_center_x, current_screen_height):
        self.active = False
        self.speed_x = self.base_speed_x * random.choice((-1, 1))
        self.speed_y = self.base_speed_y * random.choice((-1, 1))
        self.score_time = pygame.time.get_ticks()
        self.rect.center = (play_center_x, current_screen_height / 2)
        pygame.mixer.Sound.play(self.score_sound)

    def restart_counter(self, play_center_x, current_screen_height, screen):
        current_time = pygame.time.get_ticks()
        countdown_number = 3

        if current_time - self.score_time <= 700:
            countdown_number = 3
        if 700 < current_time - self.score_time <= 1400:
            countdown_number = 2
        if 1400 < current_time - self.score_time <= 2100:
            countdown_number = 1
        if current_time - self.score_time >= 2100:
            self.active = True

        time_counter = self.font.render(str(countdown_number), True, self.accent_color)
        time_counter_rect = time_counter.get_rect(center=(play_center_x, current_screen_height / 2 + 100))
        pygame.draw.rect(screen, self.bg_color, time_counter_rect)
        screen.blit(time_counter, time_counter_rect)
