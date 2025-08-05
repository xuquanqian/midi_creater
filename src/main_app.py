import pygame
import os
import logging
import tempfile
from typing import Dict, List
from chord_generator import CHORD_DB, generate_progression_midi, chord_to_notes
from visualizer import PianoRoll, ChordPreview
from grid_editor import ChordGridEditor
from skin_manager import SkinManager
from utils.debug_tools import DebugTools
from custom_types import ChordConfig, SongSection, SectionType
from style_selector import StyleSelector
from song_structure.section_manager import SectionManager
from song_structure.clipboard import ChordClipboard
from song_structure.structure_editor import StructureEditor

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

class MidiPlayer:
    def __init__(self):
        self.is_playing = False
        self.current_midi_file = None
        pygame.mixer.init()
    
    def set_midi_file(self, midi_path):
        self.current_midi_file = midi_path
        try:
            pygame.mixer.music.load(midi_path)
        except pygame.error as e:
            logger.error(f"加载MIDI文件失败: {str(e)}")
    
    def play(self):
        if self.current_midi_file:
            try:
                pygame.mixer.music.play()
                self.is_playing = True
            except pygame.error as e:
                logger.error(f"播放MIDI失败: {str(e)}")
                self.is_playing = False
    
    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
    
    def save_midi(self, midi):
        """保存MIDI到临时文件并返回路径"""
        try:
            temp_path = tempfile.mktemp(suffix='.mid')
            midi.save(temp_path)
            return temp_path
        except Exception as e:
            logger.error(f"保存MIDI文件失败: {str(e)}")
            return None
    
    def handle_event(self, event):
        """处理MIDI播放相关事件"""
        if event.type == pygame.USEREVENT and event.code == 'MIDI_END':
            self.is_playing = False
            return True
        return False

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
        
        self.midi_player = MidiPlayer()
        
        pygame.init()
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.screen = pygame.display.set_mode((1100, 700), pygame.RESIZABLE)
        pygame.display.set_caption("MIDI和弦生成器")
        
        DebugTools.log_keyboard_mapping()
        
        self.current_style = "日式ACG"
        self.current_progression = "经典进行1"
        self.key = "C"
        self.bpm = 120
        self.chord_style = "block"
        self.default_duration = 1.0
        self.is_maximized = False
        
        # 新增段落管理相关初始化
        self.section_manager = SectionManager()
        self.clipboard = ChordClipboard()
        self._init_default_sections()
        
        # 初始化UI区域和组件
        self._init_ui_layout()
        
        self.skin_manager = SkinManager()
        self._init_fonts()
        self._init_ui_elements()
        
        self.progression: List[ChordConfig] = []
        self.selected_chord_idx = 0
        self.load_current_progression()
        logger.info("=== 应用程序初始化完成 ===")
    
    def _init_default_sections(self):
        """初始化默认段落"""
        self.section_manager.add_section("主歌1", "verse", length=8, bpm=self.bpm)
        self.section_manager.add_section("副歌1", "chorus", length=8, bpm=self.bpm)
        self.section_manager.current_section = "主歌1"
    
    def _init_ui_layout(self):
        """初始化UI布局"""
        self._init_ui_areas()
        self._init_components()
    
    def _init_ui_areas(self):
        """初始化UI区域"""
        width, height = self.screen.get_size()
        
        # 控制面板保持固定宽度300px，高度自适应
        control_width = 300
        control_height = height - 40
        
        # 右侧风格选择器保持固定宽度180px
        style_width = 180
        
        # 主内容区域宽度自适应
        content_width = width - control_width - style_width - 60  # 60是边距
        
        self.ui_areas = {
            'control_panel': pygame.Rect(20, 20, control_width, control_height),
            'piano_roll': pygame.Rect(control_width + 40, 20, content_width, 180),
            'chord_preview': pygame.Rect(control_width + 40, 220, content_width, 120),
            'progression_grid': pygame.Rect(control_width + 40, 360, content_width, control_height - 360),
            'style_selector': pygame.Rect(width - style_width - 20, 20, style_width, control_height),
            'structure_editor': pygame.Rect(20, height - 50, width - 40, 50)
        }
    
    def _init_components(self):
        """初始化所有UI组件"""
        self.piano_visualizer = PianoRoll(self.ui_areas['piano_roll'])
        self.chord_display = ChordPreview(self.ui_areas['chord_preview'])
        self.grid_editor = ChordGridEditor(self.ui_areas['progression_grid'])
        self.style_selector = StyleSelector(self.ui_areas['style_selector'])
        self.structure_editor = StructureEditor(self.ui_areas['structure_editor'], self.section_manager)
        
        # 确保组件有正确的和弦数据
        if hasattr(self, 'progression'):
            self.grid_editor.set_progression(self.progression)
        if hasattr(self, 'selected_chord_idx'):
            self.update_chord_display()
    
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
        button_width = self.ui_areas['control_panel'].width - 40
        
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
            'export': (control_x, control_y + 520),
            'maximize': (control_x, control_y + 580)
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
            ),
            'maximize': Button(
                pygame.Rect(*self.control_elements['maximize'], button_width, 40),
                "最大化" if not self.is_maximized else "恢复窗口", 
                (120, 80, 160), 
                (140, 100, 180)
            )
        }

    def toggle_maximize(self):
        """切换最大化状态"""
        if not self.is_maximized:
            display_info = pygame.display.Info()
            self.screen = pygame.display.set_mode((display_info.current_w, display_info.current_h), pygame.FULLSCREEN)
            self.is_maximized = True
        else:
            self.screen = pygame.display.set_mode((1100, 700), pygame.RESIZABLE)
            self.is_maximized = False
        
        # 更新UI布局
        self._update_ui_layout()
        self.buttons['maximize'].text = "最大化" if not self.is_maximized else "恢复窗口"
    
    def _update_ui_layout(self):
        """更新UI布局"""
        self._init_ui_areas()
        self._init_components()
        self._init_ui_elements()
    
    def load_current_progression(self):
        """加载当前和弦进行"""
        progression_data = CHORD_DB[self.current_style][self.current_progression]
        self.progression = []
    
        for roman in progression_data:
            # 检查是否有(min)后缀
            is_minor = "(min)" in roman.upper()
            clean_roman = roman.upper().replace("(MIN)", "")
        
            # 获取默认和弦类型（如果是I-IV-V用maj，ii-iii-vi用min）
            default_type = "min" if clean_roman in ["II", "III", "VI"] else "maj"
            chord_type = "min" if is_minor else default_type
        
            self.progression.append({
                "roman": clean_roman,
                "type": chord_type,
                "inversion": 0,
                "duration": self.default_duration
            })
    
        # 更新当前段落的和弦进行
        self.section_manager.set_current_progression(self.progression)
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
            
            if event.type == pygame.VIDEORESIZE and not self.is_maximized:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self._update_ui_layout()
                return True
            
            if self.style_selector.handle_event(event):
                self.current_style = self.style_selector.selected_style
                self.current_progression = self.style_selector.selected_progression
                self.load_current_progression()
                return True
            
            # 新增段落编辑器事件处理
            if self.structure_editor.handle_event(event):
                # 段落切换后更新当前和弦进行
                self.progression = self.section_manager.get_current_progression()
                self.grid_editor.set_progression(self.progression)
                self.update_chord_display()
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
                    # 生成并播放MIDI (使用当前段落的和弦进行)
                    try:
                        midi = generate_progression_midi(
                            progression=self.section_manager.get_current_progression(),
                            key=self.key,
                            bpm=self.bpm,
                            style=self.chord_style
                        )
                        midi_path = self.midi_player.save_midi(midi)
                        if midi_path:
                            self.midi_player.set_midi_file(midi_path)
                            self.midi_player.play()
                    except Exception as e:
                        logger.error(f"播放失败: {str(e)}")
                    return True
                elif self.buttons['stop'].handle_event(event):
                    self.midi_player.stop()
                    return True
                elif self.buttons['maximize'].handle_event(event):
                    self.toggle_maximize()
                    return True
        
            grid_handled = self.grid_editor.handle_event(event)
            if grid_handled:
                # 更新当前段落的和弦进行
                self.progression = self.grid_editor.progression
                self.section_manager.set_current_progression(self.progression)
                # 确保更新选中的和弦索引
                self.selected_chord_idx = self.grid_editor.selected_chord_idx
                self.update_chord_display()
                return True
    
        # 处理MIDI播放事件 - 单独处理USEREVENT事件
        midi_events = [e for e in pygame.event.get(pygame.USEREVENT)]
        for event in midi_events:
            if self.midi_player.handle_event(event):
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
            # 让用户选择保存位置
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.asksaveasfilename(
                defaultextension=".mid",
                filetypes=[("MIDI files", "*.mid"), ("All files", "*.*")],
                title="保存MIDI文件"
            )
            if file_path:
                midi.save(file_path)
                logger.info(f"MIDI文件已保存到: {file_path}")
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
        self.style_selector.draw(self.screen)
        self.structure_editor.draw(self.screen)  # 新增段落编辑器绘制
        
        # 绘制按钮
        for button in self.buttons.values():
            button.draw(self.screen)
            
        # 更新播放按钮颜色
        play_color = (120, 180, 100) if self.midi_player.is_playing else (90, 160, 70)
        self.buttons['play'].color = play_color
        self.buttons['play'].hover_color = (play_color[0]+20, play_color[1]+20, play_color[2]+20)
        
        # 绘制控制参数
        bpm_text = self.ui_font.render("速度 (BPM):", True, (220, 220, 240))
        self.screen.blit(bpm_text, self.control_elements['bpm_label'])
        
        bpm_value = self.ui_font.render(f"{self.bpm:>3}", True, (255, 255, 255))
        self.screen.blit(bpm_value, self.control_elements['bpm_value'])
        
        duration_text = self.ui_font.render("时值 (小节):", True, (220, 220, 240))
        self.screen.blit(duration_text, self.control_elements['duration_label'])
        
        duration_value = self.ui_font.render(f"{abs(self.default_duration):.2f}", True, (255, 255, 255))
        self.screen.blit(duration_value, self.control_elements['duration_value'])
        
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