# main_app.py
import pygame
import json
from chord_generator import CHORD_DB, generate_progression_midi
from visualizer import PianoRoll, ChordPreview

class ChordGeneratorApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1000, 700))
        pygame.display.set_caption("MIDI和弦生成器")
        
        # 应用状态
        self.current_style = "日式ACG"
        self.current_progression = "经典进行1"
        self.key = "C"
        self.bpm = 120
        self.chord_style = "block"  # 柱式或分解
        
        # 创建UI区域
        self.control_panel = pygame.Rect(20, 20, 300, 660)
        self.piano_roll = pygame.Rect(340, 20, 640, 200)
        self.chord_preview = pygame.Rect(340, 240, 640, 200)
        self.progression_grid = pygame.Rect(340, 460, 640, 200)
        
        # 初始化组件
        self.piano_visualizer = PianoRoll(self.piano_roll)
        self.chord_display = ChordPreview(self.chord_preview)
        
        # 当前选中的和弦
        self.selected_chord_idx = 0
        self.current_chord = {
            "roman": "I",
            "type": "maj",
            "inversion": 0
        }
        
        # 加载和弦进行
        self.load_current_progression()
    
    def load_current_progression(self):
        # 加载当前选中的和弦进行
        progression_data = CHORD_DB[self.current_style][self.current_progression]
        self.progression = []
        for roman in progression_data:
            self.progression.append({
                "roman": roman,
                "type": "maj" if roman in ["I", "IV", "V"] else "min",
                "inversion": 0
            })
        
        # 更新视图
        self.update_chord_display()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event.pos)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    self.export_midi()
        
        return True
    
    def handle_mouse_click(self, pos):
        # 检查点击位置并更新UI状态
        pass
    
    def update_chord_display(self):
        # 更新和弦显示组件
        if 0 <= self.selected_chord_idx < len(self.progression):
            chord_data = self.progression[self.selected_chord_idx]
            chord_str = f"{chord_data['roman']} {chord_data['type']}"
            notes = chord_to_notes(self.key, chord_data['roman'], chord_data['type'], chord_data['inversion'])
            self.chord_display.update(chord_str, [60 + note for note in notes])
            self.piano_visualizer.chord_notes = [60 + note for note in notes]
    
    def export_midi(self):
        midi = generate_progression_midi(
            progression=self.progression,
            key=self.key,
            bpm=self.bpm,
            style=self.chord_style
        )
        midi.save("chord_progression.mid")
        print("MIDI文件已导出：chord_progression.mid")
    
    def draw(self):
        self.screen.fill((35, 35, 40))
        
        # 绘制控制面板
        pygame.draw.rect(self.screen, (70, 70, 90), self.control_panel, border_radius=8)
        
        # 绘制钢琴卷帘
        self.piano_visualizer.draw(self.screen)
        
        # 绘制和弦预览
        self.chord_display.draw(self.screen)
        
        # 绘制进行网格
        pygame.draw.rect(self.screen, (50, 50, 60), self.progression_grid, border_radius=8)
        
        pygame.display.flip()
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            running = self.handle_events()
            self.draw()
            clock.tick(30)
            
    def draw_progression_grid(self):
        # 绘制和弦网格
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

    def handle_grid_click(self, pos):
        # 检测和弦块点击
        if self.progression_grid.collidepoint(pos):
            index = (pos[0] - self.progression_grid.x) // 80
            if index < len(self.progression):
                self.selected_chord_idx = index
                self.update_chord_display()

if __name__ == "__main__":
    app = ChordGeneratorApp()
    app.run()