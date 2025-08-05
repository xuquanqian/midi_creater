# visualizer.py
import pygame
import numpy as np
from chord_generator import chord_to_notes

class PianoRoll:
    def __init__(self, rect, start_note=36, end_note=84):
        self.rect = rect
        self.start_note = start_note
        self.end_note = end_note
        self.visible_notes = end_note - start_note
        self.key_width = rect.width / self.visible_notes
        
        # 创建键盘映射
        self.note_colors = {}
        for note in range(start_note, end_note):
            # 白键和黑键的区分
            if note % 12 in [1, 3, 6, 8, 10]:
                self.note_colors[note] = (50, 50, 50)  # 黑键
            else:
                self.note_colors[note] = (220, 220, 220)  # 白键

    def draw(self, surface, chord_notes=[]):
        # 绘制背景
        pygame.draw.rect(surface, (40, 40, 40), self.rect)
        
        # 绘制琴键
        for i, note in enumerate(range(self.start_note, self.end_note)):
            rect = pygame.Rect(
                self.rect.x + i * self.key_width,
                self.rect.y,
                self.key_width,
                self.rect.height
            )
            
            # 判断是否在当前和弦中
            if note in chord_notes:
                color = (255, 100, 100)  # 高亮显示和弦音符
            else:
                color = self.note_colors[note]
                
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (30, 30, 30), rect, 1)
        
        # 添加音符标签
        font = pygame.font.SysFont(None, 16)
        for i, note in enumerate([48, 60, 72, 84]):
            text = font.render(f"C{note//12 - 1}", True, (200, 200, 200))
            pos_x = (note - self.start_note) * self.key_width
            surface.blit(text, (self.rect.x + pos_x + 5, self.rect.y + 10))

class ChordPreview:
    def __init__(self, rect):
        self.rect = rect
        self.chord_name = ""
        self.chord_notes = []
    
    def update(self, chord_name, notes):
        self.chord_name = chord_name
        self.chord_notes = notes
    
    def draw(self, surface):
        # 绘制背景
        pygame.draw.rect(surface, (60, 60, 80), self.rect)
        
        # 显示和弦名称
        font = pygame.font.SysFont(None, 28)
        text = font.render(self.chord_name, True, (255, 255, 255))
        surface.blit(text, (self.rect.x + 20, self.rect.y + 20))
        
        # 显示音符名称
        note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        note_labels = []
        for note in self.chord_notes:
            octave = note // 12 - 1
            name = note_names[note % 12]
            note_labels.append(f"{name}{octave}")
        
        notes_text = ", ".join(note_labels)
        font = pygame.font.SysFont(None, 22)
        text = font.render(notes_text, True, (200, 200, 230))
        surface.blit(text, (self.rect.x + 20, self.rect.y + 60))