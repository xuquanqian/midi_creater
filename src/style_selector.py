import pygame
import logging
from typing import List, Dict, Tuple, Optional
from constants import CHORD_DB
from utils.font_manager import FontManager

logger = logging.getLogger(__name__)

class StyleSelector:
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.font_manager = FontManager()
        self.expanded = False
        self.selected_style = "日式ACG"
        self.selected_progression = "经典进行1"
        self.showing_progressions = False  # 新增状态标记
        
        # UI styling
        self.colors = {
            'background': (60, 60, 80),
            'button': (80, 80, 100),
            'hover': (100, 150, 200),
            'text': (255, 255, 255),
            'panel': (50, 50, 70),
            'border': (30, 30, 30)
        }
        
        # Initialize UI elements
        self.style_button_rect = pygame.Rect(
            self.rect.x + 10,
            self.rect.y + 10,
            self.rect.width - 20,
            40
        )
        
        self.progression_button_rect = pygame.Rect(
            self.rect.x + 10,
            self.rect.y + 60,
            self.rect.width - 20,
            40
        )
        
        self.panel_rect = pygame.Rect(
            self.rect.x + 10,
            self.rect.y + 110,
            self.rect.width - 20,
            min(400, len(CHORD_DB) * 35 + 20)
        )
        
        self.style_items: List[Tuple[str, pygame.Rect]] = []
        self.progression_items: List[Tuple[str, pygame.Rect]] = []

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            if not self.rect.collidepoint(mouse_pos):
                self.expanded = False
                self.showing_progressions = False
                return False
                
            if self.style_button_rect.collidepoint(mouse_pos):
                self.expanded = not self.expanded
                self.showing_progressions = False
                return True
                
            if self.progression_button_rect.collidepoint(mouse_pos):
                self.expanded = True
                self.showing_progressions = True
                return True
                
            if self.expanded and self.panel_rect.collidepoint(mouse_pos):
                if not self.showing_progressions:
                    for item, rect in self.style_items:
                        if rect.collidepoint(mouse_pos):
                            self.selected_style = item
                            if CHORD_DB.get(item):
                                self.selected_progression = next(iter(CHORD_DB[item].keys()))
                            self.expanded = False
                            return True
                else:
                    for item, rect in self.progression_items:
                        if rect.collidepoint(mouse_pos):
                            self.selected_progression = item
                            self.expanded = False
                            return True
                        
        return False

    def draw(self, surface: pygame.Surface):
        """Draw the component"""
        # Draw background
        pygame.draw.rect(surface, self.colors['background'], self.rect, border_radius=8)
        
        # Draw style button
        self._draw_button(
            surface,
            self.style_button_rect,
            f"风格: {self.selected_style[:10]}{'...' if len(self.selected_style) > 10 else ''}"
        )
        
        # Draw progression button
        self._draw_button(
            surface,
            self.progression_button_rect,
            f"进行: {self.selected_progression[:10]}{'...' if len(self.selected_progression) > 10 else ''}"
        )
        
        # Draw panel if expanded
        if self.expanded:
            self._draw_panel(surface)

    def _draw_button(self, surface: pygame.Surface, rect: pygame.Rect, text: str):
        """Draw a button"""
        mouse_pos = pygame.mouse.get_pos()
        color = self.colors['hover'] if rect.collidepoint(mouse_pos) else self.colors['button']
        
        # Draw button background
        pygame.draw.rect(surface, color, rect, border_radius=6)
        pygame.draw.rect(surface, self.colors['border'], rect, 2, border_radius=6)
        
        # Draw button text
        font = self.font_manager.get_font(18)
        text_surf = font.render(text, True, self.colors['text'])
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)

    def _draw_panel(self, surface: pygame.Surface):
        """Draw the options panel"""
        pygame.draw.rect(surface, self.colors['panel'], self.panel_rect, border_radius=6)
        pygame.draw.rect(surface, self.colors['border'], self.panel_rect, 2, border_radius=6)
        
        mouse_pos = pygame.mouse.get_pos()
        font = self.font_manager.get_font(18)
        
        if not self.showing_progressions:
            # Draw style options
            self.style_items = []
            y_offset = self.panel_rect.y + 10
            
            for i, style in enumerate(CHORD_DB.keys()):
                rect = pygame.Rect(
                    self.panel_rect.x + 10,
                    y_offset + i * 35,
                    self.panel_rect.width - 20,
                    32
                )
                self.style_items.append((style, rect))
                
                # Draw option background
                color = self.colors['hover'] if rect.collidepoint(mouse_pos) else self.colors['panel']
                pygame.draw.rect(surface, color, rect, border_radius=4)
                pygame.draw.rect(surface, self.colors['border'], rect, 1, border_radius=4)
                
                # Draw option text
                display_text = style[:14] + ('...' if len(style) > 14 else '')
                text_surf = font.render(display_text, True, self.colors['text'])
                text_rect = text_surf.get_rect(midleft=(rect.x + 10, rect.centery))
                surface.blit(text_surf, text_rect)
        
        elif self.selected_style in CHORD_DB:
            # Draw progression options
            self.progression_items = []
            y_offset = self.panel_rect.y + 10
            
            for i, progression in enumerate(CHORD_DB[self.selected_style].keys()):
                rect = pygame.Rect(
                    self.panel_rect.x + 10,
                    y_offset + i * 35,
                    self.panel_rect.width - 20,
                    32
                )
                self.progression_items.append((progression, rect))
                
                # Draw option background
                color = self.colors['hover'] if rect.collidepoint(mouse_pos) else self.colors['panel']
                pygame.draw.rect(surface, color, rect, border_radius=4)
                pygame.draw.rect(surface, self.colors['border'], rect, 1, border_radius=4)
                
                # Draw option text
                display_text = progression[:14] + ('...' if len(progression) > 14 else '')
                text_surf = font.render(display_text, True, self.colors['text'])
                text_rect = text_surf.get_rect(midleft=(rect.x + 10, rect.centery))
                surface.blit(text_surf, text_rect)