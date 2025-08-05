from typing import List, Dict, Tuple, Optional
import pygame
import logging
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
        
        # Scroll parameters
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
        self.current_option_type = None
        
        # 新增选项面板滚动参数
        self.option_scroll_offset = 0
        self.option_scroll_dragging = False
        self.option_scroll_thumb_rect = None
        
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
            'scroll_thumb': (150, 150, 170),
            'option_scroll_bar': (80, 80, 100),
            'option_scroll_thumb': (120, 120, 140)
        }
        
        self.font_manager = FontManager()

    def _update_scroll_thumb(self):
        """Update scroll thumb position and size"""
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

    def _update_option_scroll_thumb(self):
        """Update option panel scroll thumb position and size"""
        if not self.option_panel_rect:
            return
            
        total_height = len(self.option_items) * 35 + 20
        visible_height = self.option_panel_rect.height
        if total_height <= visible_height:
            self.option_scroll_thumb_rect = None
            return
            
        thumb_height = max(30, int(visible_height * (visible_height / total_height)))
        scroll_range = total_height - visible_height
        thumb_pos = (self.option_scroll_offset / scroll_range) * (visible_height - thumb_height)
        
        self.option_scroll_thumb_rect = pygame.Rect(
            self.option_panel_rect.right - 8,
            self.option_panel_rect.top + thumb_pos,
            6,
            thumb_height
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
        handled = False
        
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
                # 检查是否点击了选项面板的滚动条
                if self.option_scroll_thumb_rect and self.option_scroll_thumb_rect.collidepoint(mouse_pos):
                    self.option_scroll_dragging = True
                    return True
                    
                # 检查是否点击了选项
                for i, rect in enumerate(self.option_rects):
                    adjusted_rect = pygame.Rect(
                        rect.x,
                        rect.y - self.option_scroll_offset,
                        rect.width,
                        rect.height
                    )
                    if adjusted_rect.collidepoint(mouse_pos):
                        self._apply_option_change(self.option_items[i])
                        self.show_options = False
                        handled = True
                        break
                
            for i, chord in enumerate(self.progression):
                cell_rect = self._get_cell_rect(i)
                if cell_rect.collidepoint(mouse_pos):
                    self.selected_chord_idx = i
                    handled = True
                    self._show_chord_options(i, mouse_pos)
                    break
                    
            self.show_options = False
            
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.scroll_bar_dragging = False
            self.option_scroll_dragging = False
            
        elif event.type == pygame.MOUSEMOTION:
            # Handle scroll bar dragging
            if self.scroll_bar_dragging:
                mouse_x = event.pos[0]
                scroll_bar_left = self.scroll_bar_rect.left
                scroll_bar_right = self.scroll_bar_rect.right
                
                thumb_width = self.scroll_thumb_rect.width
                new_thumb_left = max(scroll_bar_left, min(mouse_x - thumb_width/2, scroll_bar_right - thumb_width))
                
                scroll_range = max(1, len(self.progression) * self.cell_width - self.rect.width)
                thumb_range = self.scroll_bar_rect.width - thumb_width
                if thumb_range > 0:
                    self.scroll_offset = ((new_thumb_left - scroll_bar_left) / thumb_range) * scroll_range
                    self.scroll_offset = max(0, min(self.scroll_offset, scroll_range))
                    self._update_scroll_thumb()
                return True
                
            # Handle option panel scroll bar dragging
            if self.option_scroll_dragging and self.option_panel_rect:
                mouse_y = event.pos[1]
                panel_top = self.option_panel_rect.top
                panel_bottom = self.option_panel_rect.bottom
                
                thumb_height = self.option_scroll_thumb_rect.height
                new_thumb_top = max(panel_top, min(mouse_y - thumb_height/2, panel_bottom - thumb_height))
                
                total_height = len(self.option_items) * 35 + 20
                scroll_range = total_height - self.option_panel_rect.height
                thumb_range = self.option_panel_rect.height - thumb_height
                if thumb_range > 0:
                    self.option_scroll_offset = ((new_thumb_top - panel_top) / thumb_range) * scroll_range
                    self.option_scroll_offset = max(0, min(self.option_scroll_offset, scroll_range))
                    self._update_option_scroll_thumb()
                return True
                
        elif event.type == pygame.MOUSEWHEEL:
            # 获取当前鼠标位置
            mouse_pos = pygame.mouse.get_pos()
            
            # Handle mouse wheel scrolling for main grid
            if not self.show_options or not self.option_panel_rect or not self.option_panel_rect.collidepoint(mouse_pos):
                max_offset = max(0, len(self.progression) * self.cell_width - self.rect.width)
                self.scroll_offset = max(0, min(max_offset, self.scroll_offset - event.y * 30))
                self._update_scroll_thumb()
                return True
            # Handle mouse wheel scrolling for option panel
            elif self.show_options and self.option_panel_rect and self.option_panel_rect.collidepoint(mouse_pos):
                total_height = len(self.option_items) * 35 + 20
                max_offset = max(0, total_height - self.option_panel_rect.height)
                self.option_scroll_offset = max(0, min(max_offset, self.option_scroll_offset - event.y * 20))
                self._update_option_scroll_thumb()
                return True
            
        return handled

    def _get_cell_rect(self, index: int) -> pygame.Rect:
        """Get rectangle for cell at given index"""
        cell_x = self.rect.x + index * self.cell_width + self.cell_padding - self.scroll_offset
        cell_y = self.rect.y + self.cell_padding
        
        # Check if cell is visible
        if cell_x + self.cell_width < self.rect.left or cell_x > self.rect.right:
            return pygame.Rect(0, 0, 0, 0)
            
        return pygame.Rect(
            cell_x,
            cell_y,
            self.cell_width - 2 * self.cell_padding,
            self.rect.height - 2 * self.cell_padding - self.scroll_bar_height
        )

    def _show_chord_options(self, chord_idx: int, pos: Tuple[int, int], option_type: str = None):
        """Show options for chord at given index"""
        if not 0 <= chord_idx < len(self.progression):
            return
            
        self.selected_chord_idx = chord_idx
        chord = self.progression[chord_idx]
        self.current_option_type = option_type
        
        self.option_items = []
        
        # 添加罗马数字选项
        for roman in self.ROMAN_NUMERALS:
            self.option_items.append(('roman', roman))
            
        # 添加和弦类型选项
        for ctype in self.CHORD_TYPES:
            self.option_items.append(('type', ctype))
            
        # 添加转位选项
        for inv in self.INVERSIONS:
            self.option_items.append(('inversion', str(inv)))
        
        # Calculate panel size and position
        panel_width = 180
        item_height = 30
        max_panel_height = self.rect.height - 50
        panel_height = min(max_panel_height, 300)  # 限制面板最大高度
        
        # 调整面板位置，确保不会超出边界
        panel_x = min(pos[0], self.rect.right - panel_width)
        panel_y = min(pos[1], self.rect.bottom - panel_height - self.scroll_bar_height)
        
        # 如果下方空间不足，尝试向上展开
        if panel_y + panel_height > self.rect.bottom - self.scroll_bar_height:
            panel_y = max(self.rect.y, pos[1] - panel_height)
        
        self.option_panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        self.option_scroll_offset = 0
        self._update_option_scroll_thumb()
        
        # Create option rectangles (不考虑滚动偏移，将在绘制时处理)
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
        """Draw the grid editor"""
        # Draw background with clipping
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
            if cell_rect.width == 0:
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
            
            # 在单元格右下角添加小按钮用于切换选项类型
            if i == self.selected_chord_idx:
                btn_size = 20
                btn_rect = pygame.Rect(
                    cell_rect.right - btn_size - 5,
                    cell_rect.bottom - btn_size - 5,
                    btn_size,
                    btn_size
                )
                pygame.draw.rect(surface, self.colors['highlight'], btn_rect, border_radius=4)
                font = self.font_manager.get_font(14)
                text_surf = font.render("...", True, self.colors['text'])
                text_rect = text_surf.get_rect(center=btn_rect.center)
                surface.blit(text_surf, text_rect)
                
                # 检查是否点击了这个小按钮
                mouse_pos = pygame.mouse.get_pos()
                if pygame.mouse.get_pressed()[0] and btn_rect.collidepoint(mouse_pos):
                    self._show_chord_options(i, (btn_rect.x, btn_rect.y), 'roman')
        
        # Reset clipping
        surface.set_clip(old_clip)
        
        # Draw scroll bar if needed
        if len(self.progression) * self.cell_width > self.rect.width:
            pygame.draw.rect(
                surface, 
                self.colors['scroll_bar'], 
                self.scroll_bar_rect, 
                border_radius=self.scroll_bar_height//2
            )
            
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
        """Draw the options panel with scroll functionality"""
        pygame.draw.rect(surface, self.colors['option_panel'], self.option_panel_rect, border_radius=6)
        pygame.draw.rect(surface, self.colors['border'], self.option_panel_rect, 2, border_radius=6)
        
        # 设置选项面板的裁剪区域
        old_clip = surface.get_clip()
        surface.set_clip(self.option_panel_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        font = self.font_manager.get_font(18)
        
        # 绘制选项面板标题
        if self.current_option_type:
            title_text = ""
            if self.current_option_type == 'roman':
                title_text = "选择根音"
            elif self.current_option_type == 'type':
                title_text = "选择和弦类型"
            elif self.current_option_type == 'inversion':
                title_text = "选择转位"
            
            if title_text:
                title_surf = font.render(title_text, True, self.colors['text'])
                surface.blit(title_surf, (self.option_panel_rect.x + 10, self.option_panel_rect.y + 5 - self.option_scroll_offset))
        
        # 绘制选项
        for i, (item, rect) in enumerate(zip(self.option_items, self.option_rects)):
            # 调整rect位置考虑滚动偏移
            adjusted_rect = pygame.Rect(
                rect.x,
                rect.y - self.option_scroll_offset,
                rect.width,
                rect.height
            )
            
            # 只绘制可见的选项
            if adjusted_rect.bottom < self.option_panel_rect.top or adjusted_rect.top > self.option_panel_rect.bottom:
                continue
                
            # Draw option background
            if adjusted_rect.collidepoint(mouse_pos):
                pygame.draw.rect(surface, self.colors['highlight'], adjusted_rect, border_radius=4)
            else:
                pygame.draw.rect(surface, self.colors['option_panel'], adjusted_rect, border_radius=4)
            
            pygame.draw.rect(surface, self.colors['border'], adjusted_rect, 1, border_radius=4)
            
            # Draw option text
            key, value = item
            if key == 'roman':
                text = f"根音: {value}"
            elif key == 'type':
                text = f"类型: {CHORD_TYPE_DISPLAY.get(value, value)}"
            elif key == 'inversion':
                text = f"转位: {value}"
            
            text_surf = font.render(text, True, self.colors['text'])
            text_rect = text_surf.get_rect(midleft=(adjusted_rect.x + 10, adjusted_rect.centery))
            surface.blit(text_surf, text_rect)
        
        # 恢复裁剪区域
        surface.set_clip(old_clip)
        
        # 如果选项内容超过面板高度，绘制滚动条
        total_height = len(self.option_items) * 35 + 20
        if total_height > self.option_panel_rect.height:
            # 绘制滚动条轨道
            scroll_bar_rect = pygame.Rect(
                self.option_panel_rect.right - 8,
                self.option_panel_rect.top,
                8,
                self.option_panel_rect.height
            )
            pygame.draw.rect(surface, self.colors['option_scroll_bar'], scroll_bar_rect, border_radius=4)
            
            # 绘制滚动条滑块
            if self.option_scroll_thumb_rect:
                pygame.draw.rect(surface, self.colors['option_scroll_thumb'], self.option_scroll_thumb_rect, border_radius=4)