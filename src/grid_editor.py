import pygame
import logging
from typing import List, Dict, Tuple, Optional
from constants import CHORD_TYPES, CHORD_TYPE_DISPLAY
from custom_types import ChordConfig
from utils.font_manager import FontManager
from chord_generator import chord_to_name

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
        
        # Grid layout parameters
        self.cell_width = 140
        self.cell_height = 120
        self.cell_padding = 10
        self.cell_spacing = 5
        
        # Scroll parameters (modified for horizontal scroll at bottom)
        self.scroll_offset = 0
        self.scroll_bar_height = 12
        self.scroll_bar_dragging = False
        self.scroll_bar_rect = pygame.Rect(
            self.rect.left + 2,
            self.rect.bottom - self.scroll_bar_height - 2,
            self.rect.width - 4,
            self.scroll_bar_height
        )
        self.scroll_thumb_rect = None
        self._update_scroll_thumb()
        
        # UI state
        self.active_control = None
        self.show_options = False
        self.option_items: List[Tuple[str, str]] = []
        self.option_rects: List[pygame.Rect] = []
        self.option_panel_rect: Optional[pygame.Rect] = None
        
        # Colors
        self.colors = {
            'background': (60, 60, 80),
            'cell': (80, 80, 100),
            'selected': (100, 150, 200),
            'highlight': (150, 200, 250),
            'text': (255, 255, 255),
            'option_panel': (50, 50, 70),
            'border': (30, 30, 30),
            'scroll_bar': (100, 100, 120),
            'scroll_thumb': (150, 150, 170)
        }
        
        self.font_manager = FontManager()

    def _update_scroll_thumb(self):
        """Update scroll thumb position and size (modified for horizontal scroll)"""
        content_width = max(len(self.progression) * self.cell_width, self.rect.width)
        visible_ratio = self.rect.width / content_width
        thumb_width = max(30, int(self.scroll_bar_rect.width * visible_ratio))
        
        scroll_range = content_width - self.rect.width
        if scroll_range <= 0:
            thumb_pos = 0
        else:
            thumb_pos = (self.scroll_offset / scroll_range) * (self.scroll_bar_rect.width - thumb_width)
        
        self.scroll_thumb_rect = pygame.Rect(
            self.scroll_bar_rect.left + thumb_pos,
            self.scroll_bar_rect.top,
            thumb_width,
            self.scroll_bar_rect.height
        )

    def set_progression(self, progression: List[ChordConfig]):
        """Set the chord progression"""
        self.progression = progression
        if not self.progression:
            self.selected_chord_idx = 0
        else:
            self.selected_chord_idx = max(0, min(self.selected_chord_idx, len(self.progression) - 1))
        self._update_scroll_thumb()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            if not self.rect.collidepoint(mouse_pos):
                self.show_options = False
                return False
                
            # Check scroll bar drag
            if self.scroll_thumb_rect and self.scroll_thumb_rect.collidepoint(mouse_pos):
                self.scroll_bar_dragging = True
                return True
                
            if self.scroll_bar_rect.collidepoint(mouse_pos):
                # Click on scroll bar but not thumb
                if mouse_pos[0] < self.scroll_thumb_rect.left:
                    self.scroll_offset = max(0, self.scroll_offset - self.rect.width)
                else:
                    max_offset = max(0, len(self.progression) * self.cell_width - self.rect.width)
                    self.scroll_offset = min(max_offset, self.scroll_offset + self.rect.width)
                self._update_scroll_thumb()
                return True
                
            if self.show_options and self.option_panel_rect and self.option_panel_rect.collidepoint(mouse_pos):
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(mouse_pos):
                        self._apply_option_change(self.option_items[i])
                        self.show_options = False
                        return True
                
            for i, chord in enumerate(self.progression):
                cell_rect = self._get_cell_rect(i)
                if cell_rect.collidepoint(mouse_pos):
                    self.selected_chord_idx = i
                    self._show_chord_options(i, mouse_pos)
                    return True
                    
            self.show_options = False
            
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.scroll_bar_dragging = False
            
        elif event.type == pygame.MOUSEMOTION and self.scroll_bar_dragging:
            # Handle scroll bar dragging (modified for horizontal scroll)
            mouse_x = event.pos[0]
            scroll_bar_left = self.scroll_bar_rect.left
            scroll_bar_right = self.scroll_bar_rect.right
            
            # Calculate new thumb position
            thumb_width = self.scroll_thumb_rect.width
            new_thumb_left = max(scroll_bar_left, min(mouse_x - thumb_width/2, scroll_bar_right - thumb_width))
            
            # Calculate new scroll offset
            scroll_range = max(1, len(self.progression) * self.cell_width - self.rect.width)
            thumb_range = self.scroll_bar_rect.width - thumb_width
            if thumb_range > 0:
                self.scroll_offset = ((new_thumb_left - scroll_bar_left) / thumb_range) * scroll_range
                self.scroll_offset = max(0, min(self.scroll_offset, scroll_range))
                self._update_scroll_thumb()
            return True
            
        elif event.type == pygame.MOUSEWHEEL:
            # Handle mouse wheel scrolling
            max_offset = max(0, len(self.progression) * self.cell_width - self.rect.width)
            self.scroll_offset = max(0, min(max_offset, self.scroll_offset - event.y * 30))
            self._update_scroll_thumb()
            return True
            
        return False

    def _get_cell_rect(self, index: int) -> pygame.Rect:
        """Get rectangle for cell at given index (modified for bottom scroll bar)"""
        cell_x = self.rect.x + index * self.cell_width + self.cell_padding - self.scroll_offset
        cell_y = self.rect.y + self.cell_padding
        
        # Check if cell is visible
        if cell_x + self.cell_width < self.rect.left or cell_x > self.rect.right:
            return pygame.Rect(0, 0, 0, 0)
            
        return pygame.Rect(
            cell_x,
            cell_y,
            self.cell_width - 2 * self.cell_padding,
            self.rect.height - 2 * self.cell_padding - self.scroll_bar_height  # Account for scroll bar height
        )

    def _show_chord_options(self, chord_idx: int, pos: Tuple[int, int]):
        """Show options for chord at given index"""
        if not 0 <= chord_idx < len(self.progression):
            return
            
        self.selected_chord_idx = chord_idx
        chord = self.progression[chord_idx]
        
        self.option_items = []
        
        # Add roman numeral options
        for roman in self.ROMAN_NUMERALS:
            self.option_items.append(('roman', roman))
            
        # Add chord type options
        for ctype in self.CHORD_TYPES:
            self.option_items.append(('type', ctype))
            
        # Add inversion options
        for inv in self.INVERSIONS:
            self.option_items.append(('inversion', str(inv)))
        
        # Calculate panel size and position
        panel_width = 180
        item_height = 30
        panel_height = min(300, len(self.option_items) * item_height + 20)
        panel_x = min(pos[0], self.rect.right - panel_width)
        panel_y = min(pos[1], self.rect.bottom - panel_height - self.scroll_bar_height)  # Account for scroll bar
        
        self.option_panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        # Create option rectangles
        self.option_rects = []
        for i, item in enumerate(self.option_items):
            rect = pygame.Rect(
                panel_x + 10,
                panel_y + 10 + i * item_height,
                panel_width - 20,
                item_height - 5
            )
            self.option_rects.append(rect)
        
        self.show_options = True

    def _apply_option_change(self, option: Tuple[str, str]):
        """Apply the selected option change"""
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

    def draw(self, surface: pygame.Surface):
        """Draw the grid editor (modified for bottom scroll bar)"""
        # Draw background with clipping (account for scroll bar)
        clip_rect = pygame.Rect(
            self.rect.x, self.rect.y,
            self.rect.width, self.rect.height - self.scroll_bar_height
        )
        old_clip = surface.get_clip()
        surface.set_clip(clip_rect)
        
        pygame.draw.rect(surface, self.colors['background'], self.rect, border_radius=8)
        
        # Draw chord cells
        for i, chord in enumerate(self.progression):
            cell_rect = self._get_cell_rect(i)
            if cell_rect.width == 0:  # Skip if outside visible area
                continue
                
            # Draw cell background
            color = self.colors['selected'] if i == self.selected_chord_idx else self.colors['cell']
            pygame.draw.rect(surface, color, cell_rect, border_radius=6)
            pygame.draw.rect(surface, self.colors['border'], cell_rect, 2, border_radius=6)
            
            # Generate chord name
            chord_name = chord_to_name(self.key, chord['roman'], chord['type'])
            if chord.get('inversion', 0) > 0:
                chord_name += f"/{chord['inversion']}"
            
            duration = chord.get('duration', 1.0)
            duration_text = f"{duration}拍"
            
            # Draw chord name (centered)
            font = self.font_manager.get_font(20)
            text_surf = font.render(chord_name, True, self.colors['text'])
            text_rect = text_surf.get_rect(center=(cell_rect.centerx, cell_rect.centery - 20))
            surface.blit(text_surf, text_rect)
            
            # Draw duration (centered)
            font = self.font_manager.get_font(16)
            dur_surf = font.render(duration_text, True, self.colors['text'])
            dur_rect = dur_surf.get_rect(center=(cell_rect.centerx, cell_rect.centery + 25))
            surface.blit(dur_surf, dur_rect)
        
        # Reset clipping
        surface.set_clip(old_clip)
        
        # Draw scroll bar if needed
        if len(self.progression) * self.cell_width > self.rect.width:
            # Draw scroll bar track
            pygame.draw.rect(
                surface, 
                self.colors['scroll_bar'], 
                self.scroll_bar_rect, 
                border_radius=self.scroll_bar_height//2
            )
            
            # Draw scroll thumb
            if self.scroll_thumb_rect:
                pygame.draw.rect(
                    surface,
                    self.colors['scroll_thumb'],
                    self.scroll_thumb_rect,
                    border_radius=self.scroll_bar_height//2
                )
        
        # Draw options panel if visible
        if self.show_options and self.option_items:
            self._draw_option_panel(surface)

    def _draw_option_panel(self, surface: pygame.Surface):
        """Draw the options panel"""
        pygame.draw.rect(surface, self.colors['option_panel'], self.option_panel_rect, border_radius=6)
        pygame.draw.rect(surface, self.colors['border'], self.option_panel_rect, 2, border_radius=6)
        
        mouse_pos = pygame.mouse.get_pos()
        font = self.font_manager.get_font(18)
        
        for i, (item, rect) in enumerate(zip(self.option_items, self.option_rects)):
            # Draw option background
            if rect.collidepoint(mouse_pos):
                pygame.draw.rect(surface, self.colors['highlight'], rect, border_radius=4)
            else:
                pygame.draw.rect(surface, self.colors['option_panel'], rect, border_radius=4)
            
            pygame.draw.rect(surface, self.colors['border'], rect, 1, border_radius=4)
            
            # Draw option text
            key, value = item
            if key == 'roman':
                text = f"根音: {value}"
            elif key == 'type':
                text = f"类型: {CHORD_TYPE_DISPLAY.get(value, value)}"
            elif key == 'inversion':
                text = f"转位: {value}"
            
            text_surf = font.render(text, True, self.colors['text'])
            text_rect = text_surf.get_rect(midleft=(rect.x + 10, rect.centery))
            surface.blit(text_surf, text_rect)