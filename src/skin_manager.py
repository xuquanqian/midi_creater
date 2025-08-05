# skin_manager.py
import json
import os

class SkinManager:
    def __init__(self, skin_name="default"):
        self.skin_name = skin_name
        self.config = {}
        self.load_skin(skin_name)
    
    def load_skin(self, skin_name):
        try:
            with open(f"skins/{skin_name}/config.json") as f:
                self.config = json.load(f)
        except:
            # 默认回退配置
            self.config = {
                "colors": {
                    "background": (35, 35, 40),
                    "panel": (70, 70, 90),
                    "button": (100, 100, 120)
                }
            }
    
    def get_color(self, element):
        return tuple(self.config["colors"].get(element, (100, 100, 100)))