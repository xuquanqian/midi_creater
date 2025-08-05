# test_chords.py
from src.chord_generator import chord_to_notes

# 测试C大调的和弦
print("C大调I级和弦:", chord_to_notes('C', 'I', 'maj'))  # 应输出 [0, 4, 7]
print("C大调V级属七:", chord_to_notes('C', 'V', '7'))   # 应输出 [7, 11, 14, 17]