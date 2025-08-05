import pygame
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class FontManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_fonts()
        return cls._instance
    
    def _init_fonts(self):
        """Initialize fonts with Chinese support"""
        self.fonts: Dict[int, pygame.font.Font] = {}
        font_names = [
            'Microsoft YaHei',
            'SimHei',
            'PingFang SC',
            'STHeiti',
            'WenQuanYi Zen Hei',
            'Noto Sans CJK SC'
        ]
        
        for size in [16, 18, 20, 24, 28]:
            loaded = False
            for name in font_names:
                try:
                    font = pygame.font.SysFont(name, size)
                    # Test Chinese character rendering
                    test_surf = font.render("测试", True, (255,255,255))
                    if test_surf.get_width() > 0:
                        self.fonts[size] = font
                        loaded = True
                        break
                except Exception as e:
                    logger.debug(f"Font {name} not available: {str(e)}")
                    continue
            
            if not loaded:
                self.fonts[size] = pygame.font.SysFont(None, size)
                logger.warning(f"Chinese font not found for size {size}, using default")
    
    def get_font(self, size: int) -> pygame.font.Font:
        """Get font with specified size"""
        return self.fonts.get(size, pygame.font.SysFont(None, size))