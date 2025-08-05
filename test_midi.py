# test_midi.py
from src.chord_generator import generate_progression_midi

# 简单的和弦进行
progression = [
    {"roman": "I", "type": "maj"},
    {"roman": "V", "type": "7"},
    {"roman": "VI", "type": "min"}
]

# 生成MIDI
midi = generate_progression_midi(progression, key="C", bpm=120)
midi.save("test.mid")
print("MIDI已保存为 test.mid")