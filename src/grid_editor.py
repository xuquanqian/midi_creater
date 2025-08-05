import pygame
import logging
from typing import List, Dict, Tuple, Optional
from constants import CHORD_TYPES, CHORD_TYPE_DISPLAY
from custom_types import ChordConfig
from utils.font_manager import FontManager
from chord_generator import chord_to_name  # 新增导入

logger = logging.getLogger(__name__)

class ChordGridEditor:
    ROMAN_NUMERALS = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
    CHORD_TYPES = list(CHORD_TYPES.keys())
    INVERSIONS = [0, 1, 2]
    
    def __init__(self, rect: pygame.Rect, progression: Optional[List[ChordConfig]] = None, key: str = 'C'):
        self.rect = rect
        self.key = key
        self.progression = progression or []
        self.selected_chord_idx = 0
        
        self.cell_width = 100
        self.cell_height = 100
        self.cell_padding = 5
        
        self.active_control = None
        self.show_options = False
        self.option_items: List[Tuple[str, str]] = []
        self.option_rects: List[pygame.Rect] = []
        self.option_panel_rect: Optional[pygame.Rect] = None
        
        self.colors = {
            'background': (60, 60, 80),
            'cell': (80, 80, 100),
            'selected': (100, 150, 200),
            'highlight': (150, 200, 250),
            'text': (255, 255, 255),
            'option_panel': (50, 50, 70)
        }
        
        self.font_manager = FontManager()

    def set_progression(self, progression: List[ChordConfig]):
        self.progression = progression
        if not self.progression:
            self.selected_chord_idx = 0
        else:
            self.selected_chord_idx = max(0, min(self.selected_chord_idx, len(self.progression) - 1))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            return self._handle_mouse_down(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            return self._handle_mouse_up(event)
        return False
    
    def _handle_mouse_down(self, event: pygame.event.Event) -> bool:
        if not self.rect.collidepoint(event.pos):
            self.show_options = False
            return False
        
        for i, chord in enumerate(self.progression):
            cell_rect = self._get_cell_rect(i)
            if cell_rect.collidepoint(event.pos):
                self.selected_chord_idx = i
                self._show_chord_options(i, event.pos)
                return True
        
        self.show_options = False
        return False
    
    def _handle_mouse_up(self, event: pygame.event.Event) -> bool:
        if not self.show_options or not self.option_rects:
            return False
        
        for i, rect in enumerate(self.option_rects):
            if rect.collidepoint(event.pos):
                selected_option = self.option_items[i]
                self._apply_option_change(selected_option)
                self.show_options = False
                return True
        
        self.show_options = False
        return False
    
    def _show_chord_options(self, chord_idx: int, pos: Tuple[int, int]):
        if not 0 <= chord_idx < len(self.progression):
            return
        
        self.selected_chord_idx = chord_idx
        chord = self.progression[chord_idx]
        
        self.option_items = []
        
        for roman in self.ROMAN_NUMERALS:
            self.option_items.append(('roman', roman))
        
        for ctype in self.CHORD_TYPES:
            self.option_items.append(('type', ctype))
        
        for inv in self.INVERSIONS:
            self.option_items.append(('inversion', str(inv)))
        
        panel_width = 150
        panel_height = min(300, len(self.option_items) * 30 + 20)
        panel_x = min(pos[0], self.rect.right - panel_width)
        panel_y = min(pos[1], self.rect.bottom - panel_height)
        
        self.option_panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        self.option_rects = []
        for i, item in enumerate(self.option_items):
            rect = pygame.Rect(
                panel_x + 10,
                panel_y + 10 + i * 30,
                panel_width - 20,
                25
            )
            self.option_rects.append(rect)
        
        self.show_options = True
    
    def _apply_option_change(self, option: Tuple[str, str]):
        if not 0 <= self.selected_chord_idx < len(self.progression):
            return
        
        key, value = option
        chord = self.progression[self.selected_chord_idx]
        
        if key == 'roman':
            chord['roman'] = value
        elif key == 'type':
            chord['type'] = value
        elif key == 'inversion':
            chord['inversion'] = int(value)
    
    def _get_cell_rect(self, index: int) -> pygame.Rect:
        return pygame.Rect(
            self.rect.x + index * self.cell_width + self.cell_padding,
            self.rect.y + self.cell_padding,
            self.cell_width - 2 * self.cell_padding,
            self.rect.height - 2 * self.cell_padding
        )
    
    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.colors['background'], self.rect)
        
        for i, chord in enumerate(self.progression):
            cell_rect = self._get_cell_rect(i)
            
            if i == self.selected_chord_idx:
                color = self.colors['selected']
            else:
                color = self.colors['cell']
            
            pygame.draw.rect(surface, color, cell_rect, border_radius=4)
            
            # 修改的核心部分：使用chord_to_name显示实际和弦名称
            chord_name = chord_to_name(self.key, chord['roman'], chord['type'])
            if chord.get('inversion', 0) > 0:
                chord_name += f"/{chord['inversion']}"
            
            text_surf = self.font_manager.get_font(24).render(chord_name, True, self.colors['text'])
            text_rect = text_surf.get_rect(center=cell_rect.center)
            surface.blit(text_surf, text_rect)
        
        if self.show_options and self.option_items:
            self._draw_option_panel(surface)
    
    def _draw_option_panel(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.colors['option_panel'], self.option_panel_rect, border_radius=4)
        
        font = self.font_manager.get_font(20)
        mouse_pos = pygame.mouse.get_pos()
        
        for i, (item, rect) in enumerate(zip(self.option_items, self.option_rects)):
            if rect.collidepoint(mouse_pos):
                pygame.draw.rect(surface, self.colors['highlight'], rect, border_radius=3)
            
            key, value = item
            if key == 'roman':
                text = f"根音: {value}"
            elif key == 'type':
                text = f"类型: {value}"
            elif key == 'inversion':
                text = f"转位: {value}"
            
            text_surf = font.render(text, True, self.colors['text'])
            text_rect = text_surf.get_rect(midleft=(rect.x + 5, rect.centery))
            surface.blit(text_surf, text_rect)