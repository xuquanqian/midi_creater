from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from typing import List, Dict
from .constants import (
    CHORD_DB, SCALE_MAP, CHORD_TYPES, NOTE_NAMES,
    ROMAN_TO_DEGREE, CHORD_TYPE_DISPLAY
)
from .types import ChordConfig, ChordStyle

def get_note_name(note_value: int) -> str:
    """获取音符名称"""
    return NOTE_NAMES[note_value % 12]

def chord_to_name(key: str, roman_numeral: str, chord_type: str) -> str:
    """将罗马数字和弦转换为实际和弦名称"""
    roman_numeral = roman_numeral.upper()
    root_idx = ROMAN_TO_DEGREE[roman_numeral]
    root_note = SCALE_MAP[key][root_idx]
    root_name = get_note_name(root_note)
    return f"{root_name}{CHORD_TYPE_DISPLAY.get(chord_type, '')}"

def chord_to_notes(key: str, roman_numeral: str, chord_type: str, inversion: int = 0) -> List[int]:
    """将罗马数字和弦转换为实际音符"""
    root_idx = ROMAN_TO_DEGREE[roman_numeral.upper()]
    root_note = SCALE_MAP[key][root_idx]
    offsets = CHORD_TYPES[chord_type]
    notes = [root_note + offset for offset in offsets]
    return notes[inversion:] + [n + 12 for n in notes[:inversion]]

def _generate_block_chord(track: MidiTrack, notes: List[int], ticks_per_measure: int, chord_duration: float):
    """生成柱式和弦"""
    for note in notes:
        track.append(Message('note_on', note=60 + note, velocity=100, time=0))
    time_offset = int(ticks_per_measure * chord_duration)
    for note in notes:
        track.append(Message('note_off', note=60 + note, velocity=100, time=time_offset))

def _generate_arpeggio(track: MidiTrack, notes: List[int], ticks_per_measure: int, chord_duration: float):
    """生成分解和弦"""
    arp_time = int(ticks_per_measure * chord_duration / len(notes))
    for i, note in enumerate(notes):
        track.append(Message('note_on', note=60 + note, velocity=80, time=0))
        track.append(Message('note_off', note=60 + note, velocity=80, time=arp_time - 50))

def generate_progression_midi(
    progression: List[ChordConfig],
    key: str = 'C',
    bpm: int = 120,
    chord_duration: float = 1,
    style: ChordStyle = 'block'
) -> MidiFile:
    """生成MIDI文件"""
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    
    ticks_per_beat = mid.ticks_per_beat
    ticks_per_measure = ticks_per_beat * 4  # 4/4拍
    
    # 添加速度和节拍设置
    track.append(Message('program_change', program=0, time=0))
    track.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm)))
    track.append(MetaMessage('time_signature', numerator=4, denominator=4))
    
    # 生成和弦序列
    for chord in progression:
        chord_notes = chord_to_notes(key, chord['roman'], chord['type'], chord.get('inversion', 0))
        
        if style == 'block':
            _generate_block_chord(track, chord_notes, ticks_per_measure, chord_duration)
        elif style == 'arpeggio':
            _generate_arpeggio(track, chord_notes, ticks_per_measure, chord_duration)
    
    return mid