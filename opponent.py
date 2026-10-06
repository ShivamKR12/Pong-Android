# opponent.py

from block import Block


class Opponent(Block):
    def __init__(self, path, x_pos, y_pos, speed, tolerance, scale = 1.0):
        super().__init__(path, x_pos, y_pos, scale)
        self.speed = speed
        self.tolerance = tolerance

    def update(self, ball_group, current_screen_height):
        ball = ball_group.sprite
        
        # 1. Smarter tracking: Only chase if the ball is moving left (towards the AI)
        if ball.speed_x < 0:
            target_y = ball.rect.centery
        else:
            # 2. Return to the center of the screen when defending
            target_y = current_screen_height / 2

        # 3. Apply the difficulty tolerance to determine if it needs to move
        if abs(self.rect.centery - target_y) > self.tolerance:
            if self.rect.centery < target_y:
                self.rect.y += self.speed
            else:
                self.rect.y -= self.speed
                
        self.constrain(current_screen_height)

    def constrain(self, current_screen_height):
        if self.rect.top <= 0: self.rect.top = 0
        if self.rect.bottom >= current_screen_height: self.rect.bottom = current_screen_height
