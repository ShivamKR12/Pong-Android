# block.py

import pygame


class Block(pygame.sprite.Sprite):
    def __init__(self, path, x_pos, y_pos, scale=1.0):
        super().__init__()
        original_image = pygame.image.load(path)
        
        if scale != 1.0:
            new_width = int(original_image.get_width() * scale)
            new_height = int(original_image.get_height() * scale)
            self.image = pygame.transform.scale(original_image, (new_width, new_height))
        else:
            self.image = original_image
            
        self.rect = self.image.get_rect(center=(x_pos, y_pos))
