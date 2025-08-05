import pygame
from typing import List
from utils.font_manager import FontManager

class PianoRoll:
    def __init__(self, rect: pygame.Rect, start_note: int = 36, end_note: int = 84):
        self.rect = rect
        self.start_note = start_note
        self.end_note = end_note
        self.visible_notes = end_note - start_note
        self.key_width = rect.width / self.visible_notes
        self.chord_notes: List[int] = []
        
        # 初始化音符颜色
        self.note_colors = {}
        for note in range(start_note, end_note):
            if note % 12 in [1, 3, 6, 8, 10]:
                self.note_colors[note] = (50, 50, 50)
            else:
                self.note_colors[note] = (220, 220, 220)
        
        # 字体管理
        self.font_manager = FontManager()

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (40, 40, 40), self.rect)
        
        for i, note in enumerate(range(self.start_note, self.end_note)):
            rect = pygame.Rect(
                self.rect.x + i * self.key_width,
                self.rect.y,
                self.key_width,
                self.rect.height
            )
            
            if note in self.chord_notes:
                color = (255, 100, 100)
            else:
                color = self.note_colors[note]
                
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (30, 30, 30), rect, 1)
        
        font = self.font_manager.get_font(16)
        for i, note in enumerate([48, 60, 72, 84]):
            text = font.render(f"C{note//12 - 1}", True, (200, 200, 200))
            pos_x = (note - self.start_note) * self.key_width
            surface.blit(text, (self.rect.x + pos_x + 5, self.rect.y + 10))

class ChordPreview:
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.chord_name = ""
        self.chord_notes: List[int] = []
        self.font_manager = FontManager()
    
    def update(self, chord_name: str, notes: List[int]):
        self.chord_name = chord_name
        self.chord_notes = notes
    
    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (60, 60, 80), self.rect)
        
        # 显示和弦名称
        text = self.font_manager.get_font(28).render(self.chord_name, True, (255, 255, 255))
        surface.blit(text, (self.rect.x + 20, self.rect.y + 20))
        
        # 显示音符名称
        note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        note_labels = []
        for note in self.chord_notes:
            octave = note // 12 - 1
            name = note_names[note % 12]
            note_labels.append(f"{name}{octave}")
        
        notes_text = ", ".join(note_labels)
        text = self.font_manager.get_font(20).render(notes_text, True, (200, 200, 230))
        surface.blit(text, (self.rect.x + 20, self.rect.y + 60))