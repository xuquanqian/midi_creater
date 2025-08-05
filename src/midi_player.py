import pygame
import os
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class MidiPlayer:
    def __init__(self):
        self.midi_file: Optional[str] = None
        self.is_playing = False
        self.output_dir = self._get_output_dir()
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 初始化pygame的midi模块
        pygame.mixer.init()
        pygame.mixer.music.set_endevent(pygame.USEREVENT)
    
    def _get_output_dir(self) -> str:
        """获取输出目录路径"""
        # 获取当前盘符
        current_drive = os.path.splitdrive(os.getcwd())[0]
        # 构建输出路径
        return os.path.join(current_drive, "midi生成器", "output")
    
    def set_midi_file(self, midi_file: str):
        """设置要播放的MIDI文件"""
        self.midi_file = midi_file
        self.is_playing = False
    
    def play(self):
        """播放MIDI文件"""
        if not self.midi_file or not os.path.exists(self.midi_file):
            logger.error("MIDI文件不存在或未设置")
            return False
        
        try:
            pygame.mixer.music.load(self.midi_file)
            pygame.mixer.music.play()
            self.is_playing = True
            logger.info(f"开始播放: {self.midi_file}")
            return True
        except Exception as e:
            logger.error(f"播放失败: {str(e)}")
            return False
    
    def stop(self):
        """停止播放"""
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False
            logger.info("播放已停止")
    
    def save_midi(self, midi_data, filename: str = "chord_progression.mid") -> str:
        """保存MIDI文件到输出目录"""
        output_path = os.path.join(self.output_dir, filename)
        
        # 处理文件名冲突
        counter = 1
        base_name, ext = os.path.splitext(filename)
        while os.path.exists(output_path):
            output_path = os.path.join(self.output_dir, f"{base_name}_{counter}{ext}")
            counter += 1
        
        try:
            midi_data.save(output_path)
            logger.info(f"MIDI文件已保存到: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"保存MIDI文件失败: {str(e)}")
            raise
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理播放相关事件"""
        if event.type == pygame.USEREVENT:  # 播放结束事件
            self.is_playing = False
            return True
        return False