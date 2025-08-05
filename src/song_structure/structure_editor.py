import pygame
from typing import Dict, List
from .section_manager import SectionManager
from .clipboard import ChordClipboard
from utils.font_manager import FontManager

class StructureEditor:
    def __init__(self, rect: pygame.Rect, manager: SectionManager):
        self.rect = rect
        self.manager = manager
        self.clipboard = ChordClipboard()
        
        # UI状态
        self.show_section_menu = False
        self.section_buttons: Dict[str, pygame.Rect] = {}
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理段落编辑器事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 检查段落按钮点击
            for name, rect in self.section_buttons.items():
                if rect.collidepoint(event.pos):
                    self.manager.current_section = name
                    return True
            
        elif event.type == pygame.KEYDOWN:
            # 处理复制粘贴快捷键
            if pygame.key.get_mods() & pygame.KMOD_CTRL:
                if event.key == pygame.K_c:
                    self.clipboard.copy(self.manager.get_current_progression())
                    return True
                elif event.key == pygame.K_v:
                    if pasted := self.clipboard.paste():
                        self.manager.set_current_progression(pasted)
                        return True
        
        return False
    
    def draw(self, surface: pygame.Surface):
        """绘制段落编辑器"""
        pygame.draw.rect(surface, (60, 60, 80), self.rect, border_radius=8)
        
        # 使用FontManager获取字体（修改这里）
        font = FontManager().get_font(20)  # 20是字体大小，可以调整
        
        # 绘制段落标签
        label = font.render("段落:", True, (255, 255, 255))
        surface.blit(label, (self.rect.x + 10, self.rect.y + 10))
        
        # 绘制段落按钮
        self.section_buttons = {}
        x_offset = self.rect.x + 80
        for i, name in enumerate(self.manager.sections.keys()):
            btn_rect = pygame.Rect(
                x_offset + i * 100,
                self.rect.y + 10,
                90,
                30
            )
            self.section_buttons[name] = btn_rect
            
            # 绘制按钮
            color = (100, 150, 200) if name == self.manager.current_section else (80, 80, 100)
            pygame.draw.rect(surface, color, btn_rect, border_radius=6)
            
            # 绘制按钮文字
            text = font.render(name[:6], True, (255, 255, 255))
            surface.blit(text, (btn_rect.x + 10, btn_rect.y + 8))