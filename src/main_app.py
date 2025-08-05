# main_app.py
import pygame
import os
import logging
from chord_generator import CHORD_DB, generate_progression_midi, chord_to_notes
from visualizer import PianoRoll, ChordPreview

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('midi_generator.log', mode='w', encoding='utf-8'),
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
        self.debug_keyboard_mapping()
        
        # 应用状态
        self.current_style = "日式ACG"
        self.current_progression = "经典进行1"
        self.key = "C"
        self.bpm = 120
        self.chord_style = "block"
        
        # UI区域
        self.control_panel = pygame.Rect(20, 20, 300, 660)
        self.piano_roll = pygame.Rect(340, 20, 640, 200)
        self.chord_preview = pygame.Rect(340, 240, 640, 200)
        self.progression_grid = pygame.Rect(340, 460, 640, 200)
        
        # 初始化组件
        self.piano_visualizer = PianoRoll(self.piano_roll)
        self.chord_display = ChordPreview(self.chord_preview)
        
        # 当前和弦
        self.selected_chord_idx = 0
        self.current_chord = {
            "roman": "I",
            "type": "maj",
            "inversion": 0
        }
        
        # 加载进行
        self.load_current_progression()
        logger.info("=== 应用程序初始化完成 ===")
    
    def debug_keyboard_mapping(self):
        """打印键盘映射调试信息"""
        print("\n键盘映射测试:")
        print(f"标准E键码(pygame.K_e): {pygame.K_e}")
        print(f"E键名称: {pygame.key.name(pygame.K_e)}")
        
        # 测试其他常用键
        for key in [pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_RETURN]:
            print(f"键码 {key} 对应名称: {pygame.key.name(key)}")

    def load_current_progression(self):
        """加载当前和弦进行（已修复大小写问题）"""
        progression_data = CHORD_DB[self.current_style][self.current_progression]
        self.progression = []
        for roman in progression_data:
            # 自动判断和弦类型（大写=大调，小写=小调）
            chord_type = "maj" if roman.isupper() else "min"
            self.progression.append({
                "roman": roman.upper(),  # 统一转换为大写
                "type": chord_type,
                "inversion": 0
            })
        self.update_chord_display()
    
    def update_chord_display(self):
        """更新和弦显示"""
        if 0 <= self.selected_chord_idx < len(self.progression):
            chord_data = self.progression[self.selected_chord_idx]
            chord_str = f"{chord_data['roman']}{chord_data['type']}"
            notes = chord_to_notes(
                self.key, 
                chord_data['roman'], 
                chord_data['type'], 
                chord_data['inversion']
            )
            self.chord_display.update(chord_str, [60 + note for note in notes])
            self.piano_visualizer.chord_notes = [60 + note for note in notes]
    
    def handle_events(self):
        """处理输入事件（优化版）"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                # 调试输出
                debug_msg = (
                    f"按键事件: 键码={event.key}, "
                    f"名称={pygame.key.name(event.key)}"
                )
                logger.debug(debug_msg)
                
                # 简化检测条件
                if event.key == pygame.K_e:
                    logger.info("E键触发导出")
                    self.export_midi()
                    pygame.time.delay(200)  # 防抖
                    return True
        
        return True
    
    def export_midi(self):
        """导出MIDI文件（带完整错误处理）"""
        try:
            logger.info("开始导出MIDI...")
            output_path = os.path.abspath("chord_progression.mid")
            print(f"\n正在导出到: {output_path}")
            
            midi = generate_progression_midi(
                progression=self.progression,
                key=self.key,
                bpm=self.bpm,
                style=self.chord_style
            )
            
            midi.save(output_path)
            
            # 验证文件
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                logger.info(f"导出成功! 文件大小: {file_size}字节")
                print(f"✓ 导出成功! 文件已创建 ({file_size}字节)")
            else:
                logger.error("导出失败: 文件未生成")
                print("✗ 导出失败: 文件未生成")
                
        except Exception as e:
            logger.error(f"导出失败: {str(e)}", exc_info=True)
            print(f"✗ 导出错误: {str(e)}")

    def draw(self):
        """绘制界面"""
        self.screen.fill((35, 35, 40))
        
        # 绘制控制面板
        pygame.draw.rect(self.screen, (70, 70, 90), self.control_panel, border_radius=8)
        
        # 绘制组件
        self.piano_visualizer.draw(self.screen)
        self.chord_display.draw(self.screen)
        self.draw_progression_grid()
        
        # 绘制帮助提示
        font = pygame.font.SysFont(None, 24)
        help_text = font.render("按 E 键导出MIDI文件", True, (200, 200, 200))
        self.screen.blit(help_text, (self.control_panel.x + 20, self.control_panel.y + 620))
        
        pygame.display.flip()
    
    def draw_progression_grid(self):
        """绘制和弦进行网格"""
        for i, chord in enumerate(self.progression):
            rect = pygame.Rect(
                self.progression_grid.x + i * 80,
                self.progression_grid.y,
                70,
                self.progression_grid.height
            )
            color = (100, 150, 200) if i == self.selected_chord_idx else (70, 70, 90)
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            
            # 显示和弦信息
            font = pygame.font.SysFont(None, 24)
            text = font.render(f"{chord['roman']}{chord['type']}", True, (255, 255, 255))
            self.screen.blit(text, (rect.x + 10, rect.y + 10))
    
    def run(self):
        """主循环"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            running = self.handle_events()
            self.draw()
            clock.tick(30)

if __name__ == "__main__":
    print("=== MIDI生成器启动 ===")
    try:
        app = ChordGeneratorApp()
        app.run()
        print("=== 应用程序正常退出 ===")
    except Exception as e:
        print(f"!!! 崩溃: {str(e)}")
        raise