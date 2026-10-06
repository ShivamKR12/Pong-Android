# button.py

import pygame


class Button:
    def __init__(self, text, x, y, width, height, font, bg_color, text_color, elevation=6, hover_color=None, bottom_color=None):
        # --- Core Positional & Elevation Attributes ---
        self.original_y_pos = y - height // 2
        self.elevation = elevation
        self.dynamic_elevation = elevation
        self.pressed = False

        # --- Top and Bottom Rectangles ---
        self.top_rect = pygame.Rect(x - width // 2, self.original_y_pos, width, height)
        self.bottom_rect = pygame.Rect(x - width // 2, self.original_y_pos, width, elevation)

        # --- Colors ---
        self.original_top_color = pygame.Color(bg_color) if not isinstance(bg_color, pygame.Color) else bg_color
        self.top_color = self.original_top_color
        
        # Automatically generate hover/press and bottom 3D colors if not explicitly provided
        self.hover_color = hover_color if hover_color else self._lighten_color(self.original_top_color, 25)
        self.bottom_color = bottom_color if bottom_color else self._darken_color(self.original_top_color, 35)

        # --- Text Surface & Rect ---
        self.update_text(text, font, text_color)

    def _darken_color(self, color, amount=35):
        """Helper to create a darker shade for the bottom elevation rectangle."""
        c = pygame.Color(color)
        return pygame.Color(
            max(0, c.r - amount),
            max(0, c.g - amount),
            max(0, c.b - amount)
        )

    def _lighten_color(self, color, amount=25):
        """Helper to create a brighter shade for the touch/press highlight."""
        c = pygame.Color(color)
        return pygame.Color(
            min(255, c.r + amount),
            min(255, c.g + amount),
            min(255, c.b + amount)
        )

    def update_text(self, text, font, text_color):
        self.text_surface = font.render(text, True, text_color)
        self.text_rect = self.text_surface.get_rect(center=self.top_rect.center)

    def reset_state(self):
        """Explicitly resets visual highlight and elevation to normal."""
        self.top_color = self.original_top_color
        self.dynamic_elevation = self.elevation
        self.pressed = False

    def _update_elevation_and_hover(self):
        """Handles dynamic elevation and touch/press state."""
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        if self.top_rect.collidepoint(mouse_pos):
            if mouse_pressed:
                # Active touch/press: sink button down and highlight
                self.top_color = self.hover_color
                self.dynamic_elevation = 0
                self.pressed = True
            else:
                # Finger lifted / not pressing:
                # Reset immediately so Android touch doesn't get stuck highlighted
                self.reset_state()
        else:
            self.reset_state()

    def draw(self, screen):
        # 1. Update hover/press color and elevation every frame
        self._update_elevation_and_hover()

        # 2. Apply elevation vertical shift to top rectangle & text
        self.top_rect.y = self.original_y_pos - self.dynamic_elevation
        self.text_rect.center = self.top_rect.center

        # 3. Align bottom rectangle directly under the top rectangle
        self.bottom_rect.midtop = self.top_rect.midtop
        self.bottom_rect.height = self.top_rect.height + self.dynamic_elevation

        # 4. Draw bottom rectangle first (3D side), then top rectangle, then text
        pygame.draw.rect(screen, self.bottom_color, self.bottom_rect, border_radius=12)
        pygame.draw.rect(screen, self.top_color, self.top_rect, border_radius=12)
        screen.blit(self.text_surface, self.text_rect)

    def check_click(self, px=None, py=None):
        """
        Supports both explicit touch coordinates from FINGERUP events (px, py)
        and standard Pygame mouse release detection.
        """
        # Explicit touch coordinates from FINGERUP event in main.py
        if px is not None and py is not None:
            if self.top_rect.collidepoint(px, py):
                self.reset_state()
                return True
            return False

        # Standard Pygame desktop mouse-release check
        mouse_pos = pygame.mouse.get_pos()
        if self.top_rect.collidepoint(mouse_pos):
            if self.pressed and not pygame.mouse.get_pressed()[0]:
                self.reset_state()
                return True
        return False
