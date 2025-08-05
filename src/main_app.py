# src/main_app.py
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
from rhythm.editor import RhythmEditor
from rhythm.handler import RhythmHandler
from rhythm.types import RHYTHM_TYPES

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

class RhythmSelector:
    def __init__(self, rect: pygame.Rect, default_rhythm: str = 'straight'):
        self.rect = rect
        self.selected_rhythm = default_rhythm
        self.expanded = False
        self.options = RHYTHM_TYPES
        self.option_rects = []
        
        # UI styling
        self.colors = {
            'background': (60, 60, 80),
            'button': (80, 80, 100),
            'hover': (100, 150, 200),
            'text': (255, 255, 255),
            'panel': (50, 50, 70),
            'border': (30, 30, 30),
            'scroll_bar': (80, 80, 100),
            'scroll_thumb': (120, 120, 140)
        }
        
        # 计算面板大小
        self.panel_height = min(300, len(self.options) * 30 + 10)
        self.panel_rect = pygame.Rect(
            self.rect.x,
            self.rect.y + self.rect.height + 5,
            self.rect.width,
            self.panel_height
        )
        
        # 滚动相关
        self.scroll_offset = 0
        self.scroll_thumb_rect = None
        self.scroll_dragging = False
        self._update_scroll_thumb()

    def _update_scroll_thumb(self):
        """更新滚动条滑块位置和大小"""
        total_height = len(self.options) * 30 + 10
        if total_height <= self.panel_height:
            self.scroll_thumb_rect = None
            return
            
        thumb_height = max(30, int(self.panel_height * (self.panel_height / total_height)))
        scroll_range = total_height - self.panel_height
        thumb_pos = (self.scroll_offset / scroll_range) * (self.panel_height - thumb_height)
        
        self.scroll_thumb_rect = pygame.Rect(
            self.panel_rect.right - 8,
            self.panel_rect.top + thumb_pos,
            6,
            thumb_height
        )

    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理输入事件"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            
            # 检查主按钮点击
            if self.rect.collidepoint(mouse_pos):
                self.expanded = not self.expanded
                return True
                
            # 检查选项点击
            if self.expanded and self.panel_rect.collidepoint(mouse_pos):
                if self.scroll_thumb_rect and self.scroll_thumb_rect.collidepoint(mouse_pos):
                    self.scroll_dragging = True
                    return True
                    
                for i, rect in enumerate(self.option_rects):
                    adjusted_rect = pygame.Rect(
                        rect.x,
                        rect.y - self.scroll_offset,
                        rect.width,
                        rect.height
                    )
                    if adjusted_rect.collidepoint(mouse_pos):
                        self.selected_rhythm = self.options[i]
                        self.expanded = False
                        return True
                        
            # 点击其他地方收起选项
            if self.expanded and not self.panel_rect.collidepoint(mouse_pos):
                self.expanded = False
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            self.scroll_dragging = False
            
        elif event.type == pygame.MOUSEMOTION:
            if self.scroll_dragging and self.scroll_thumb_rect:
                mouse_y = event.pos[1]
                panel_top = self.panel_rect.top
                panel_bottom = self.panel_rect.bottom
                
                thumb_height = self.scroll_thumb_rect.height
                new_thumb_top = max(panel_top, min(mouse_y - thumb_height/2, panel_bottom - thumb_height))
                
                total_height = len(self.options) * 30 + 10
                scroll_range = total_height - self.panel_height
                thumb_range = self.panel_height - thumb_height
                if thumb_range > 0:
                    self.scroll_offset = ((new_thumb_top - panel_top) / thumb_range) * scroll_range
                    self.scroll_offset = max(0, min(self.scroll_offset, scroll_range))
                    self._update_scroll_thumb()
                return True
                
        elif event.type == pygame.MOUSEWHEEL and self.expanded:
            total_height = len(self.options) * 30 + 10
            max_offset = max(0, total_height - self.panel_height)
            self.scroll_offset = max(0, min(max_offset, self.scroll_offset - event.y * 20))
            self._update_scroll_thumb()
            return True
                
        return False

    def draw(self, surface: pygame.Surface):
        """Draw the selector"""
        # Draw main button
        mouse_pos = pygame.mouse.get_pos()
        btn_color = self.colors['hover'] if self.rect.collidepoint(mouse_pos) else self.colors['button']
        
        pygame.draw.rect(surface, btn_color, self.rect, border_radius=6)
        pygame.draw.rect(surface, self.colors['border'], self.rect, 2, border_radius=6)
        
        # Draw button text
        font = pygame.font.SysFont('Arial', 18)
        text = font.render(self.selected_rhythm, True, self.colors['text'])
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)
        
        # Draw dropdown arrow
        arrow_size = 8
        arrow_points = [
            (self.rect.right - 15, self.rect.centery - arrow_size//2),
            (self.rect.right - 10, self.rect.centery + arrow_size//2),
            (self.rect.right - 5, self.rect.centery - arrow_size//2)
        ]
        pygame.draw.polygon(surface, self.colors['text'], arrow_points)
        
        # Draw options panel if expanded
        if self.expanded:
            self._draw_options_panel(surface)

    def _draw_options_panel(self, surface: pygame.Surface):
        """Draw the options panel with scroll functionality"""
        pygame.draw.rect(surface, self.colors['panel'], self.panel_rect, border_radius=6)
        pygame.draw.rect(surface, self.colors['border'], self.panel_rect, 2, border_radius=6)
        
        # 设置裁剪区域
        old_clip = surface.get_clip()
        surface.set_clip(self.panel_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        font = pygame.font.SysFont('Arial', 16)
        self.option_rects = []
        
        for i, option in enumerate(self.options):
            option_rect = pygame.Rect(
                self.panel_rect.x + 5,
                self.panel_rect.y + 5 + i * 30 - self.scroll_offset,
                self.panel_rect.width - 10,
                28
            )
            self.option_rects.append(option_rect)
            
            # 只绘制可见的选项
            if option_rect.bottom < self.panel_rect.top or option_rect.top > self.panel_rect.bottom:
                continue
                
            # Draw option background
            color = self.colors['hover'] if option_rect.collidepoint(mouse_pos) else self.colors['panel']
            pygame.draw.rect(surface, color, option_rect, border_radius=4)
            pygame.draw.rect(surface, self.colors['border'], option_rect, 1, border_radius=4)
            
            # Draw option text
            text = font.render(option, True, self.colors['text'])
            text_rect = text.get_rect(midleft=(option_rect.x + 10, option_rect.centery))
            surface.blit(text, text_rect)
        
        # 恢复裁剪区域
        surface.set_clip(old_clip)
        
        # 绘制滚动条
        total_height = len(self.options) * 30 + 10
        if total_height > self.panel_height:
            # 绘制滚动条轨道
            scroll_bar_rect = pygame.Rect(
                self.panel_rect.right - 8,
                self.panel_rect.top,
                8,
                self.panel_height
            )
            pygame.draw.rect(surface, self.colors['scroll_bar'], scroll_bar_rect, border_radius=4)
            
            # 绘制滚动条滑块
            if self.scroll_thumb_rect:
                pygame.draw.rect(surface, self.colors['scroll_thumb'], self.scroll_thumb_rect, border_radius=4)

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
        self.rhythm_type = "straight"
        
        # 新增段落管理相关初始化
        self.section_manager = SectionManager()
        self.clipboard = ChordClipboard()
        self._init_default_sections()
        
        # 初始化UI区域和组件
        self._init_ui_layout()
        self._init_components()
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
            'structure_editor': pygame.Rect(20, height - 50, width - 40, 50),
            'rhythm_editor': pygame.Rect(control_width + 40, 300, content_width, 50)
        }
    
    def _init_components(self):
        """初始化所有UI组件"""
        self.piano_visualizer = PianoRoll(self.ui_areas['piano_roll'])
        self.chord_display = ChordPreview(self.ui_areas['chord_preview'])
        self.grid_editor = ChordGridEditor(self.ui_areas['progression_grid'])
        self.style_selector = StyleSelector(self.ui_areas['style_selector'])
        self.structure_editor = StructureEditor(self.ui_areas['structure_editor'], self.section_manager)
        self.rhythm_editor = RhythmEditor(self.ui_areas['rhythm_editor'])
        
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
            'rhythm_label': (control_x, control_y + 220),
            'rhythm_value': (control_x + 100, control_y + 220),
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
        
        # 替换原来的节奏按钮为新的节奏选择器
        self.rhythm_selector = RhythmSelector(
            pygame.Rect(*self.control_elements['rhythm_value'], 150, 30),
            self.rhythm_type
        )

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
                "duration": self.default_duration,
                "rhythm": self.rhythm_type  # 添加默认节奏型
            })
    
        # 更新当前段落的和弦进行
        self.section_manager.set_current_progression(self.progression)
        if hasattr(self, 'grid_editor'):  # 确保grid_editor已初始化
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
            
            # 处理段落编辑器事件
            if self.structure_editor.handle_event(event):
                # 段落切换后更新当前和弦进行
                self.progression = self.section_manager.get_current_progression()
                self.grid_editor.set_progression(self.progression)
                self.update_chord_display()
                return True
            
            # 处理节奏编辑器事件
            if self.rhythm_editor.handle_event(event):
                return True
            
            # 处理节奏选择器事件
            if self.rhythm_selector.handle_event(event):
                self.rhythm_type = self.rhythm_selector.selected_rhythm
                # 更新当前和弦的节奏型
                for chord in self.progression:
                    chord['rhythm'] = self.rhythm_type
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
                            style=self.chord_style,
                            rhythm=self.rhythm_type
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
                style=self.chord_style,
                rhythm=self.rhythm_type
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
        self.structure_editor.draw(self.screen)
        self.rhythm_editor.draw(self.screen)
        self.rhythm_selector.draw(self.screen)  # 绘制节奏选择器
        
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
        
        # 绘制节奏标签
        rhythm_text = self.ui_font.render("节奏型:", True, (220, 220, 240))
        self.screen.blit(rhythm_text, self.control_elements['rhythm_label'])
        
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