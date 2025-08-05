from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
from typing import List
from constants import (
    CHORD_DB, SCALE_MAP, CHORD_TYPES, NOTE_NAMES,
    ROMAN_TO_DEGREE, CHORD_TYPE_DISPLAY
)
from custom_types import ChordConfig, ChordStyle
from rhythm.handler import RhythmHandler
import re
import logging

logger = logging.getLogger(__name__)

def get_note_name(note_value: int) -> str:
    """获取音符名称"""
    return NOTE_NAMES[note_value % 12]

def chord_to_name(key: str, roman_numeral: str, chord_type: str) -> str:
    """将罗马数字和弦转换为实际和弦名称"""
    # 检查是否有特殊后缀如(min7b5)
    special_types = {
        '(min)': 'min',
        '(min7)': 'm7',
        '(maj7)': 'maj7',
        '(7)': '7',
        '(sus4)': 'sus4',
        '(min7b5)': 'm7b5',
        '(b9)': '7b9'
    }
    
    actual_type = chord_type
    cleaned_roman = roman_numeral.upper()
    
    # 修复：使用统一的大小写处理
    for suffix, ctype in special_types.items():
        suffix_upper = suffix.upper()
        if suffix_upper in cleaned_roman:
            actual_type = ctype
            cleaned_roman = cleaned_roman.replace(suffix_upper, "")
            break
    
    # 确保罗马数字是有效的（去除空格）
    cleaned_roman = cleaned_roman.strip()
    
    # 检查清理后的罗马数字是否在映射表中
    if cleaned_roman not in ROMAN_TO_DEGREE:
        # 尝试从和弦名称中提取罗马数字部分
        match = re.match(r'([IV]+)', cleaned_roman)
        if match:
            cleaned_roman = match.group(1)
        else:
            logger.error(f"无效的罗马数字: {cleaned_roman} (原始输入: {roman_numeral})")
            return ""  # 返回空字符串避免崩溃
    
    root_idx = ROMAN_TO_DEGREE[cleaned_roman]
    root_note = SCALE_MAP[key][root_idx]
    root_name = get_note_name(root_note)
    
    return f"{root_name}{CHORD_TYPE_DISPLAY.get(actual_type, '')}"

def chord_to_notes(key: str, roman_numeral: str, chord_type: str, inversion: int = 0) -> List[int]:
    """将罗马数字和弦转换为实际音符"""
    special_types = {
        '(min)': 'min',
        '(min7)': 'm7',
        '(maj7)': 'maj7',
        '(7)': '7',
        '(sus4)': 'sus4',
        '(min7b5)': 'm7b5',
        '(b9)': '7b9'
    }
    
    actual_type = chord_type
    cleaned_roman = roman_numeral.upper()
    
    # 修复：使用统一的大小写处理
    for suffix, ctype in special_types.items():
        suffix_upper = suffix.upper()
        if suffix_upper in cleaned_roman:
            actual_type = ctype
            cleaned_roman = cleaned_roman.replace(suffix_upper, "")
            break
    
    # 确保罗马数字是有效的（去除空格）
    cleaned_roman = cleaned_roman.strip()
    
    # 检查清理后的罗马数字是否在映射表中
    if cleaned_roman not in ROMAN_TO_DEGREE:
        # 尝试从和弦名称中提取罗马数字部分
        match = re.match(r'([IV]+)', cleaned_roman)
        if match:
            cleaned_roman = match.group(1)
        else:
            logger.error(f"无效的罗马数字: {cleaned_roman} (原始输入: {roman_numeral})")
            return []  # 返回空列表避免崩溃
    
    root_idx = ROMAN_TO_DEGREE[cleaned_roman]
    root_note = SCALE_MAP[key][root_idx]
    
    # 获取和弦音程
    if actual_type not in CHORD_TYPES:
        logger.warning(f"未知和弦类型: {actual_type}, 使用大三和弦代替")
        actual_type = 'maj'
    
    offsets = CHORD_TYPES[actual_type]
    
    notes = [root_note + offset for offset in offsets]
    return notes[inversion:] + [n + 12 for n in notes[:inversion]]

def _generate_block_chord(track: MidiTrack, notes: List[int], ticks_per_measure: int, 
                         duration: float, rhythm: str = 'straight'):
    """生成柱式和弦（带节奏处理）"""
    RhythmHandler.apply_rhythm(
        track=track,
        notes=[60 + note for note in notes],
        ticks=ticks_per_measure,
        duration=duration,
        rhythm=rhythm,
        velocity=100
    )

def _generate_arpeggio(track: MidiTrack, notes: List[int], ticks_per_measure: int,
                      duration: float, rhythm: str = 'straight'):
    """生成分解和弦（带节奏处理）"""
    RhythmHandler.apply_rhythm(
        track=track,
        notes=[60 + note for note in notes],
        ticks=ticks_per_measure,
        duration=duration/len(notes),  # 分解和弦需要调整时长
        rhythm=rhythm,
        velocity=80
    )

def generate_progression_midi(
    progression: List[ChordConfig],
    key: str = 'C',
    bpm: int = 120,
    style: ChordStyle = 'block',
    rhythm: str = 'straight'
) -> MidiFile:
    """生成MIDI文件（支持节奏参数）"""
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
        duration = chord.get('duration', 1.0)  # 默认1小节
        chord_rhythm = chord.get('rhythm', rhythm)  # 优先使用和弦自身的节奏设置
        
        if style == 'block':
            _generate_block_chord(track, chord_notes, ticks_per_measure, duration, chord_rhythm)
        elif style == 'arpeggio':
            _generate_arpeggio(track, chord_notes, ticks_per_measure, duration, chord_rhythm)
    
    return mid