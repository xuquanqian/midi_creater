# chord_generator.py
from mido import MidiFile, MidiTrack, Message
import json

CHORD_DB = {
    "日式ACG": {
        "经典进行1": ["I", "V", "vi", "IV"],
        "伤感进行": ["vi", "IV", "I", "V"]
    },
    "华语流行": {
        "卡农进行": ["I", "V", "vi", "III", "IV", "I", "IV", "V"],
        "4536": ["IV", "V", "III", "VI"]
    }
}

SCALE_MAP = {
    'C': [0, 2, 4, 5, 7, 9, 11],  # C大调音阶
    # 其他调性...
}

CHORD_TYPES = {
    'maj': [0, 4, 7],        # 大三和弦
    'min': [0, 3, 7],        # 小三和弦
    '7': [0, 4, 7, 10],      # 属七和弦
    'maj7': [0, 4, 7, 11],   # 大七和弦
    # 更多和弦类型...
}

def chord_to_notes(key, roman_numeral, chord_type, inversion=0):
    """将罗马数字和弦转换为实际音符"""
    scale_degrees = {'I': 0, 'II': 1, 'III': 2, 'IV': 3, 'V': 4, 'VI': 5, 'VII': 6}
    root_idx = scale_degrees[roman_numeral]
    root_note = SCALE_MAP[key][root_idx]
    
    offsets = CHORD_TYPES[chord_type]
    notes = [root_note + offset for offset in offsets]
    
    # 处理转位
    return notes[inversion:] + [n + 12 for n in notes[:inversion]]

def generate_progression_midi(progression, key='C', bpm=120, chord_duration=1, style='block'):
    """生成MIDI文件"""
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    
    ticks_per_beat = mid.ticks_per_beat
    ticks_per_measure = ticks_per_beat * 4  # 4/4拍
    
    # 添加速度和节拍设置
    track.append(Message('program_change', program=0, time=0))
    track.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm)))
    track.append(MetaMessage('time_signature', numerator=4, denominator=4))
    
    # 生成和弦序列
    for chord in progression:
        chord_notes = chord_to_notes(key, chord['roman'], chord['type'], chord.get('inversion', 0))
        
        if style == 'block':
            # 柱式和弦
            for note in chord_notes:
                track.append(Message('note_on', note=60 + note, velocity=100, time=0))
            time_offset = int(ticks_per_measure * chord_duration)
            for note in chord_notes:
                track.append(Message('note_off', note=60 + note, velocity=100, time=time_offset))
        
        elif style == 'arpeggio':
            # 分解和弦
            arp_time = int(ticks_per_measure * chord_duration / len(chord_notes))
            for i, note in enumerate(chord_notes):
                track.append(Message('note_on', note=60 + note, velocity=80, time=0))
                track.append(Message('note_off', note=60 + note, velocity=80, time=arp_time - 50))
    
    return mid