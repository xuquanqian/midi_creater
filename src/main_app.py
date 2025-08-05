import pygame
import os
import logging
from typing import Dict, List
from chord_generator import CHORD_DB, generate_progression_midi, chord_to_notes
from visualizer import PianoRoll, ChordPreview
from grid_editor import ChordGridEditor
from skin_manager import SkinManager
from utils.debug_tools import DebugTools
from custom_types import ChordConfig
from style_selector import StyleSelector

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('midi_generator_debug.log', mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Button:
    def __init__(self, rect: pygame.Rect, text: str, color: tuple, hover_color: tuple, font_size=20):
        self.rect = rect
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.border_radius = 6
        self.font = self._get_chinese_font(font_size)
    
    def _get_chinese_font(self, size):
        """获取支持中文的字体"""
        font_names = [
            'Microsoft YaHei',  # Windows
            'SimHei',           # Windows
            'PingFang SC',      # macOS
            'STHeiti',          # macOS
            'WenQuanYi Zen Hei',# Linux
            'Noto Sans CJK SC'  # Linux
        ]
        
        for name in font_names:
            try:
                font = pygame.font.SysFont(name, size)
                test_surface = font.render("测试", True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    return font
            except:
                continue
        return pygame.font.SysFont(None, size)
    
    def draw(self, surface: pygame.Surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, (30, 30, 30), self.rect, 2, border_radius=self.border_radius)
        
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            return True
        return False

class ChordGeneratorApp:
    def __init__(self):
        logger.info("=== 应用程序初始化开始 ===")
        
        pygame.init()
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.screen = pygame.display.set_mode((1100, 700))  # 宽度增加100px
        pygame.display.set_caption("MIDI和弦生成器")
        
        DebugTools.log_keyboard_mapping()
        
        self.current_style = "日式ACG"
        self.current_progression = "经典进行1"
        self.key = "C"
        self.bpm = 120
        self.chord_style = "block"
        self.default_duration = 1.0
        
        # UI区域定义
        self.ui_areas = {
            'control_panel': pygame.Rect(20, 20, 300, 660),
            'piano_roll': pygame.Rect(340, 20, 540, 180),  # 宽度减小
            'chord_preview': pygame.Rect(340, 220, 540, 120),  # 宽度减小
            'progression_grid': pygame.Rect(340, 360, 540, 320),  # 宽度减小
            'style_selector': pygame.Rect(900, 20, 180, 660)  # 新增右侧区域
        }
        
        self.skin_manager = SkinManager()
        self._init_fonts()
        self._init_ui_elements()
        self._init_components()
        
        self.progression: List[ChordConfig] = []
        self.selected_chord_idx = 0
        self.load_current_progression()
        logger.info("=== 应用程序初始化完成 ===")
    
    def _init_fonts(self):
        """初始化所有字体"""
        self.title_font = self._get_chinese_font(24, bold=True)
        self.ui_font = self._get_chinese_font(20)
        self.small_font = self._get_chinese_font(16)
    
    def _get_chinese_font(self, size, bold=False):
        """获取支持中文的字体"""
        font_names = [
            'Microsoft YaHei', 'SimHei', 
            'PingFang SC', 'STHeiti',
            'WenQuanYi Zen Hei', 'Noto Sans CJK SC'
        ]
        
        for name in font_names:
            try:
                font = pygame.font.SysFont(name, size, bold=bold)
                test_surface = font.render("测试", True, (255, 255, 255))
                if test_surface.get_width() > 0:
                    return font
            except:
                continue
        return pygame.font.SysFont(None, size, bold=bold)
    
    def _init_ui_elements(self):
        """初始化所有UI元素"""
        control_x = self.ui_areas['control_panel'].x + 20
        control_y = self.ui_areas['control_panel'].y + 20
        button_width = 260
        
        # 重新设计间距和对齐
        self.control_elements = {
            'title': (control_x, control_y),
            'bpm_label': (control_x, control_y + 60),
            'bpm_value': (control_x + 180, control_y + 60),
            'bpm_up': (control_x + 220, control_y + 60),
            'bpm_down': (control_x + 140, control_y + 60),
            'duration_label': (control_x, control_y + 100),
            'duration_value': (control_x + 180, control_y + 100),
            'duration_up': (control_x + 220, control_y + 100),
            'duration_down': (control_x + 140, control_y + 100),
            'style_label': (control_x, control_y + 140),
            'style_value': (control_x + 100, control_y + 140),
            'style_toggle': (control_x, control_y + 180),
            'play': (control_x, control_y + 240),
            'stop': (control_x, control_y + 300),
            'export': (control_x, control_y + 520)
        }
        
        self.buttons = {
            'export': Button(
                pygame.Rect(*self.control_elements['export'], button_width, 50),
                "导出 MIDI", 
                (70, 130, 200), 
                (90, 150, 220),
                font_size=24
            ),
            'bpm_up': Button(
                pygame.Rect(*self.control_elements['bpm_up'], 40, 30),
                "+", 
                (80, 120, 200), 
                (100, 150, 250)
            ),
            'bpm_down': Button(
                pygame.Rect(*self.control_elements['bpm_down'], 40, 30),
                "-", 
                (80, 120, 200), 
                (100, 150, 250)
            ),
            'duration_up': Button(
                pygame.Rect(*self.control_elements['duration_up'], 40, 30),
                "+", 
                (80, 120, 200), 
                (100, 150, 250)
            ),
            'duration_down': Button(
                pygame.Rect(*self.control_elements['duration_down'], 40, 30),
                "-", 
                (80, 120, 200), 
                (100, 150, 250)
            ),
            'style_toggle': Button(
                pygame.Rect(*self.control_elements['style_toggle'], button_width, 40),
                "切换为分解和弦" if self.chord_style == "block" else "切换为柱式和弦", 
                (80, 120, 200), 
                (100, 150, 250)
            ),
            'play': Button(
                pygame.Rect(*self.control_elements['play'], button_width, 40),
                "播放", 
                (90, 160, 70), 
                (110, 180, 90)
            ),
            'stop': Button(
                pygame.Rect(*self.control_elements['stop'], button_width, 40),
                "停止", 
                (160, 80, 80), 
                (180, 100, 100)
            )
        }
    
    def _init_components(self):
        """初始化组件"""
        self.piano_visualizer = PianoRoll(self.ui_areas['piano_roll'])
        self.chord_display = ChordPreview(self.ui_areas['chord_preview'])
        self.grid_editor = ChordGridEditor(self.ui_areas['progression_grid'])
        self.style_selector = StyleSelector(self.ui_areas['style_selector'])

    def load_current_progression(self):
        """加载当前和弦进行"""
        progression_data = CHORD_DB[self.current_style][self.current_progression]
        self.progression = []
        
        for roman in progression_data:
            chord_type = "maj" if roman.isupper() else "min"
            self.progression.append({
                "roman": roman.upper(),
                "type": chord_type,
                "inversion": 0,
                "duration": self.default_duration
            })
        
        self.grid_editor.set_progression(self.progression)
        self.update_chord_display()

    def update_chord_display(self):
        """更新和弦显示"""
        if not self.progression:
            return
            
        chord_data = self.progression[self.selected_chord_idx]
        notes = chord_to_notes(
            self.key, 
            chord_data['roman'], 
            chord_data['type'], 
            chord_data.get('inversion', 0)
        )
        
        chord_str = f"{chord_data['roman']}{chord_data['type']}"
        if chord_data.get('inversion', 0) > 0:
            chord_str += f"/{chord_data['inversion']}"
        
        self.chord_display.update(chord_str, [60 + note for note in notes])
        self.piano_visualizer.chord_notes = [60 + note for note in notes]

    def handle_events(self) -> bool:
        """处理输入事件"""
        mouse_pos = pygame.mouse.get_pos()
        
        for button in self.buttons.values():
            button.check_hover(mouse_pos)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            # 处理风格选择器事件
            if self.style_selector.handle_event(event):
                # 当风格或进行改变时，更新当前进行
                self.current_style = self.style_selector.selected_style
                self.current_progression = self.style_selector.selected_progression
                self.load_current_progression()
                return True
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.buttons['export'].handle_event(event):
                    self.export_midi()
                    return True
                elif self.buttons['bpm_up'].handle_event(event):
                    self.bpm = min(240, self.bpm + 5)
                    return True
                elif self.buttons['bpm_down'].handle_event(event):
                    self.bpm = max(40, self.bpm - 5)
                    return True
                elif self.buttons['duration_up'].handle_event(event):
                    self.default_duration = min(4.0, self.default_duration + 0.25)
                    return True
                elif self.buttons['duration_down'].handle_event(event):
                    self.default_duration = max(0.25, self.default_duration - 0.25)
                    return True
                elif self.buttons['style_toggle'].handle_event(event):
                    self.chord_style = 'block' if self.chord_style == 'arpeggio' else 'arpeggio'
                    self.buttons['style_toggle'].text = "切换为分解和弦" if self.chord_style == "block" else "切换为柱式和弦"
                    return True
                elif self.buttons['play'].handle_event(event):
                    return True
                elif self.buttons['stop'].handle_event(event):
                    return True
            
            grid_handled = self.grid_editor.handle_event(event)
            if grid_handled:
                self.progression = self.grid_editor.progression
                self.update_chord_display()
                return True
        
        return True

    def export_midi(self):
        """导出MIDI文件"""
        try:
            midi = generate_progression_midi(
                progression=self.progression,
                key=self.key,
                bpm=self.bpm,
                style=self.chord_style
            )
            midi.save("chord_progression.mid")
        except Exception as e:
            logger.error(f"导出失败: {str(e)}")

    def draw(self):
        """绘制界面"""
        self.screen.fill((40, 40, 50))
        pygame.draw.rect(self.screen, (60, 60, 80), self.ui_areas['control_panel'], border_radius=10)
        
        # 绘制标题
        title_text = self.title_font.render("MIDI和弦生成器", True, (220, 220, 240))
        self.screen.blit(title_text, self.control_elements['title'])
        
        # 绘制组件
        self.piano_visualizer.draw(self.screen)
        self.chord_display.draw(self.screen)
        self.grid_editor.draw(self.screen)
        
        # 绘制风格选择器
        self.style_selector.draw(self.screen)
        
        # 绘制按钮
        for button in self.buttons.values():
            button.draw(self.screen)
        
        # 绘制控制参数 - 确保对齐
        # BPM控制区域
        bpm_text = self.ui_font.render("速度 (BPM):", True, (220, 220, 240))
        self.screen.blit(bpm_text, self.control_elements['bpm_label'])
        
        bpm_value = self.ui_font.render(f"{self.bpm:>3}", True, (255, 255, 255))
        self.screen.blit(bpm_value, self.control_elements['bpm_value'])
        
        # 时值控制区域
        duration_text = self.ui_font.render("时值 (小节):", True, (220, 220, 240))
        self.screen.blit(duration_text, self.control_elements['duration_label'])
        
        duration_value = self.ui_font.render(f"{abs(self.default_duration):.2f}", True, (255, 255, 255))
        self.screen.blit(duration_value, self.control_elements['duration_value'])
        
        # 当前风格显示
        style_text = self.ui_font.render("当前风格:", True, (220, 220, 240))
        self.screen.blit(style_text, self.control_elements['style_label'])
        
        current_style = self.ui_font.render(
            "柱式和弦" if self.chord_style == "block" else "分解和弦", 
            True, 
            (255, 255, 255)
        )
        self.screen.blit(current_style, self.control_elements['style_value'])
        
        pygame.display.flip()
    
    def run(self):
        """主循环"""
        clock = pygame.time.Clock()
        running = True
        
        try:
            while running:
                running = self.handle_events()
                self.draw()
                clock.tick(30)
        finally:
            pygame.quit()

if __name__ == "__main__":
    app = ChordGeneratorApp()
    app.run()