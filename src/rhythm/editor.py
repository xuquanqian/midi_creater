# src/rhythm/editor.py
import pygame
from typing import Dict, List
from .types import RHYTHM_TYPES

class RhythmEditor:
    """独立的节奏编辑器，通过事件与主程序交互"""
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.rhythms: Dict[int, str] = {}  # {chord_index: rhythm_type}
        self.active_index = -1
        self.font = pygame.font.SysFont('Arial', 16)
        
        # 滚动条相关
        self.scroll_offset = 0
        self.scroll_bar_height = 12
        self.scroll_bar_rect = pygame.Rect(
            self.rect.left + 2,
            self.rect.bottom - self.scroll_bar_height - 2,
            self.rect.width - 4,
            self.scroll_bar_height
        )
        self.scroll_thumb_rect = None
        self.scroll_bar_dragging = False
        self._update_scroll_thumb()
        
    def set_rhythm(self, index: int, rhythm: str):
        self.rhythms[index] = rhythm
        
    def get_rhythm(self, index: int) -> str:
        return self.rhythms.get(index, 'straight')
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件，返回是否处理了事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.scroll_thumb_rect and self.scroll_thumb_rect.collidepoint(event.pos):
                    self.scroll_bar_dragging = True
                    return True
                
                if self.scroll_bar_rect.collidepoint(event.pos):
                    # 点击滚动条但不在滑块上
                    if event.pos[0] < self.scroll_thumb_rect.left:
                        self.scroll_offset = max(0, self.scroll_offset - self.rect.width)
                    else:
                        max_offset = max(0, len(self.rhythms) * 20 - self.rect.height)
                        self.scroll_offset = min(max_offset, self.scroll_offset + self.rect.width)
                    self._update_scroll_thumb()
                    return True
                
                self._show_rhythm_menu(event.pos)
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            self.scroll_bar_dragging = False
            
        elif event.type == pygame.MOUSEMOTION:
            if self.scroll_bar_dragging:
                mouse_x = event.pos[0]
                thumb_width = self.scroll_thumb_rect.width
                new_thumb_left = max(self.scroll_bar_rect.left, 
                                   min(mouse_x - thumb_width/2, 
                                       self.scroll_bar_rect.right - thumb_width))
                
                scroll_range = max(1, len(self.rhythms) * 20 - self.rect.height)
                thumb_range = self.scroll_bar_rect.width - thumb_width
                if thumb_range > 0:
                    self.scroll_offset = ((new_thumb_left - self.scroll_bar_rect.left) / thumb_range) * scroll_range
                    self.scroll_offset = max(0, min(self.scroll_offset, scroll_range))
                    self._update_scroll_thumb()
                return True
                
        elif event.type == pygame.MOUSEWHEEL:
            max_offset = max(0, len(self.rhythms) * 20 - self.rect.height)
            self.scroll_offset = max(0, min(max_offset, self.scroll_offset - event.y * 20))
            self._update_scroll_thumb()
            return True
            
        return False
    
    def _update_scroll_thumb(self):
        """更新滚动条滑块位置和大小"""
        content_height = max(len(self.rhythms) * 20, self.rect.height)
        visible_ratio = self.rect.height / content_height
        thumb_height = max(30, int(self.scroll_bar_rect.width * visible_ratio))
        
        scroll_range = content_height - self.rect.height
        if scroll_range <= 0:
            thumb_pos = 0
        else:
            thumb_pos = (self.scroll_offset / scroll_range) * (self.scroll_bar_rect.width - thumb_height)
        
        self.scroll_thumb_rect = pygame.Rect(
            self.scroll_bar_rect.left + thumb_pos,
            self.scroll_bar_rect.top,
            thumb_height,
            self.scroll_bar_rect.height
        )
    
    def _show_rhythm_menu(self, pos: tuple):
        # 在实际项目中实现节奏选择菜单
        pass
    
    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (60, 60, 80), self.rect)
        
        # 设置裁剪区域
        old_clip = surface.get_clip()
        surface.set_clip(self.rect)
        
        # 绘制节奏项
        for i, rhythm in self.rhythms.items():
            y_pos = self.rect.y + 5 + i * 20 - self.scroll_offset
            if y_pos < self.rect.y or y_pos > self.rect.bottom - 20:
                continue
                
            text = self.font.render(f"{i}:{rhythm}", True, (255,255,255))
            surface.blit(text, (self.rect.x+5, y_pos))
        
        # 恢复裁剪区域
        surface.set_clip(old_clip)
        
        # 绘制滚动条
        if len(self.rhythms) * 20 > self.rect.height:
            pygame.draw.rect(surface, (100,100,120), self.scroll_bar_rect, border_radius=6)
            if self.scroll_thumb_rect:
                pygame.draw.rect(surface, (150,150,170), self.scroll_thumb_rect, border_radius=6)