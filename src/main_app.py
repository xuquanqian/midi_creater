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

class ChordGeneratorApp:
    def __init__(self):
        logger.info("=== 应用程序初始化开始 ===")
        
        # 初始化Pygame
        pygame.init()
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        
        # 创建窗口
        self.screen = pygame.display.set_mode((1000, 700))
        pygame.display.set_caption("MIDI和弦生成器")
        
        # 调试键盘映射
        DebugTools.log_keyboard_mapping()
        
        # 应用状态
        self.current_style = "日式ACG"
        self.current_progression = "经典进行1"
        self.key = "C"
        self.bpm = 120
        self.chord_style = "block"
        
        # UI区域定义
        self.ui_areas = {
            'control_panel': pygame.Rect(20, 20, 300, 660),
            'piano_roll': pygame.Rect(340, 20, 640, 200),
            'chord_preview': pygame.Rect(340, 240, 640, 200),
            'progression_grid': pygame.Rect(340, 460, 640, 200)
        }
        
        # 皮肤管理
        self.skin_manager = SkinManager()
        
        # 初始化组件
        self.piano_visualizer = PianoRoll(self.ui_areas['piano_roll'])
        self.chord_display = ChordPreview(self.ui_areas['chord_preview'])
        self.grid_editor = ChordGridEditor(self.ui_areas['progression_grid'])
        
        # 当前和弦进行
        self.progression: List[ChordConfig] = []
        self.selected_chord_idx = 0
        
        # 加载初始进行
        self.load_current_progression()
        logger.info("=== 应用程序初始化完成 ===")

    def load_current_progression(self):
        """加载当前和弦进行"""
        logger.debug(f"加载和弦进行 - 风格: {self.current_style}, 进行: {self.current_progression}")
        
        progression_data = CHORD_DB[self.current_style][self.current_progression]
        self.progression = []
        
        for roman in progression_data:
            chord_type = "maj" if roman.isupper() else "min"
            self.progression.append({
                "roman": roman.upper(),
                "type": chord_type,
                "inversion": 0
            })
        
        logger.debug(f"加载完成 - 和弦数: {len(self.progression)}")
        self.grid_editor.set_progression(self.progression)
        self.update_chord_display()

    def update_chord_display(self):
        """更新和弦显示"""
        logger.debug("更新和弦显示")
        
        if not self.progression:
            logger.warning("空和弦进行")
            return
            
        logger.debug(f"当前选中和弦索引: {self.selected_chord_idx}")
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
        
        logger.debug(f"显示和弦: {chord_str}, 音符: {notes}")
        self.chord_display.update(chord_str, [60 + note for note in notes])
        self.piano_visualizer.chord_notes = [60 + note for note in notes]

    def handle_events(self) -> bool:
        """处理输入事件"""
        for event in pygame.event.get():
            logger.debug(f"收到事件: {event.type} - {getattr(event, 'pos', '')}")
            
            if event.type == pygame.QUIT:
                logger.info("收到退出事件")
                return False
                
            if event.type == pygame.KEYDOWN:
                key_name = pygame.key.name(event.key)
                logger.debug(f"按键按下: {key_name} (code: {event.key})")
                
                if event.key == pygame.K_e:
                    logger.info("检测到E键按下，触发导出")
                    self.export_midi()
                    pygame.time.delay(200)  # 防止重复触发
                    return True
            
            # 处理网格编辑器事件
            grid_handled = self.grid_editor.handle_event(event)
            logger.debug(f"网格编辑器处理结果: {grid_handled}")
            
            if grid_handled:
                logger.debug("网格编辑器处理了事件，更新数据")
                self.progression = self.grid_editor.progression
                logger.debug(f"新的和弦进行数据: {self.progression}")
                self.update_chord_display()
                return True
        
        return True

    def export_midi(self):
        """导出MIDI文件"""
        try:
            logger.info("开始导出MIDI...")
            output_path = os.path.abspath("chord_progression.mid")
            logger.debug(f"导出路径: {output_path}")
            
            midi = generate_progression_midi(
                progression=self.progression,
                key=self.key,
                bpm=self.bpm,
                style=self.chord_style
            )
            
            midi.save(output_path)
            
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                logger.info(f"导出成功! 文件大小: {file_size}字节")
            else:
                logger.error("导出失败: 文件未生成")
                
        except Exception as e:
            logger.error(f"导出失败: {str(e)}", exc_info=True)

    def draw(self):
        """绘制界面"""
        # 使用皮肤颜色绘制背景
        bg_color = self.skin_manager.get_color('background')
        self.screen.fill(bg_color)
        
        # 绘制控制面板
        panel_color = self.skin_manager.get_color('panel')
        pygame.draw.rect(self.screen, panel_color, self.ui_areas['control_panel'], border_radius=8)
        
        # 绘制组件
        self.piano_visualizer.draw(self.screen)
        self.chord_display.draw(self.screen)
        self.grid_editor.draw(self.screen)
        
        # 绘制帮助提示
        help_text = self.skin_manager.get_font(20).render(
            "按 E 键导出MIDI文件", 
            True, 
            self.skin_manager.get_color('text')
        )
        self.screen.blit(
            help_text, 
            (self.ui_areas['control_panel'].x + 20, self.ui_areas['control_panel'].y + 620)
        )
        
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
        except Exception as e:
            logger.critical(f"应用程序崩溃: {str(e)}", exc_info=True)
        finally:
            pygame.quit()
            logger.info("=== 应用程序退出 ===")

if __name__ == "__main__":
    print("=== MIDI生成器启动 ===")
    try:
        app = ChordGeneratorApp()
        app.run()
        print("=== 应用程序正常退出 ===")
    except Exception as e:
        print(f"!!! 崩溃: {str(e)}")
        raise