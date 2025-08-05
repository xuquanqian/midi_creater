import pygame
import logging

logger = logging.getLogger(__name__)

class FontManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_fonts()
        return cls._instance
    
    def _init_fonts(self):
        try:
            self.font = pygame.font.SysFont('SimHei', 24)
            self.small_font = pygame.font.SysFont('SimHei', 20)
            self.tiny_font = pygame.font.SysFont('SimHei', 16)
        except:
            self.font = pygame.font.SysFont(None, 24)
            self.small_font = pygame.font.SysFont(None, 20)
            self.tiny_font = pygame.font.SysFont(None, 16)
            logger.warning("无法加载中文字体，将使用默认字体")
    
    def get_font(self, size=24):
        if size == 24:
            return self.font
        elif size == 20:
            return self.small_font
        elif size == 16:
            return self.tiny_font
        return pygame.font.SysFont(None, size)