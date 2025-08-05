import json
import os
from typing import Dict, Tuple, Any
import pygame

class SkinManager:
    def __init__(self, skin_name: str = "default"):
        self.skin_name = skin_name
        self.config: Dict[str, Any] = {}
        self.default_config = {
            "colors": {
                "background": (35, 35, 40),
                "panel": (70, 70, 90),
                "button": (100, 100, 120),
                "text": (255, 255, 255),
                "highlight": (150, 200, 250),
                "selected": (100, 150, 200)
            },
            "font": "Microsoft YaHei"  # 确保默认使用中文字体
        }
        self.load_skin(skin_name)
    
    def load_skin(self, skin_name: str):
        self.skin_name = skin_name
        try:
            with open(f"skins/{skin_name}/config.json", encoding='utf-8') as f:
                self.config = json.load(f)
        except:
            self.config = self.default_config
    
    def get_color(self, element: str) -> Tuple[int, int, int]:
        return tuple(self.config["colors"].get(element, (100, 100, 100)))
    
    def get_font(self, size: int = 24) -> pygame.font.Font:
        # 强制优先使用能显示中文的字体
        chinese_fonts = [
            "Microsoft YaHei",
            "SimHei",
            "Arial Unicode MS",
            "Noto Sans CJK SC",
            "sans-serif"
        ]
        
        for font_name in chinese_fonts:
            try:
                font = pygame.font.SysFont(font_name, size)
                # 测试中文字符渲染
                test_surf = font.render("测试", True, (255,255,255))
                if test_surf.get_width() > 0:
                    return font
            except:
                continue
        
        # 最终回退方案
        return pygame.font.SysFont(None, size)