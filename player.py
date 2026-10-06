# player.py

import pygame
from block import Block


class Player(Block):
    def __init__(self, path, x_pos, y_pos, speed, instant_drag, scale = 1.0):
        super().__init__(path, x_pos, y_pos, scale)
        self.speed = speed
        self.instant_drag = instant_drag
        self.movement = 0
        self.touch_target_y = None 

    def screen_constrain(self, current_screen_height):
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= current_screen_height:
            self.rect.bottom = current_screen_height

    def update(self, ball_group, current_screen_height):
        if self.touch_target_y is not None:
            if self.instant_drag:
                self.rect.centery = self.touch_target_y
            else:
                if abs(self.rect.centery - self.touch_target_y) > self.speed:
                    if self.rect.centery < self.touch_target_y:
                        self.rect.y += self.speed
                    else:
                        self.rect.y -= self.speed
        else:
            self.rect.y += self.movement
            
        self.screen_constrain(current_screen_height)
