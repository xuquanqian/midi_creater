import pygame
import mido
import time
import os
from pygame import mixer

def play_midi_file(file_path):
    """播放MIDI文件的简单播放器"""
    
    # 初始化pygame mixer
    mixer.init(44100, -16, 2, 1024)
    
    try:
        # 加载MIDI文件
        mixer.music.load(file_path)
        print(f"正在播放: {os.path.basename(file_path)}")
        
        # 开始播放
        mixer.music.play()
        
        # 获取MIDI文件信息
        mid = mido.MidiFile(file_path)
        duration = mid.length  # 获取时长(秒)
        print(f"时长: {duration:.2f}秒")
        
        # 等待播放完成
        while mixer.music.get_busy():
            time.sleep(0.1)
            
    except Exception as e:
        print(f"播放错误: {e}")
    finally:
        mixer.quit()

if __name__ == "__main__":
    # 获取当前目录下的MIDI文件
    midi_files = [f for f in os.listdir() if f.lower().endswith('.mid')]
    
    if not midi_files:
        print("当前目录下没有找到MIDI文件(.mid)")
    else:
        print("找到以下MIDI文件:")
        for i, f in enumerate(midi_files, 1):
            print(f"{i}. {f}")
        
        try:
            choice = int(input("请选择要播放的文件编号: ")) - 1
            if 0 <= choice < len(midi_files):
                play_midi_file(midi_files[choice])
            else:
                print("无效的选择")
        except ValueError:
            print("请输入有效的数字")

    input("按Enter键退出...")