from typing import TypedDict, List, Dict, Literal

ChordType = Literal['maj', 'min', '7', 'maj7', 'sus4', 'm7']
RomanNumeral = Literal['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
ChordStyle = Literal['block', 'arpeggio']

# 新增 SectionType 类型
SectionType = Literal['intro', 'verse', 'chorus', 'bridge', 'outro']

class ChordConfig(TypedDict):
    roman: RomanNumeral
    type: ChordType
    inversion: int
    duration: float
    rhythm: str  # 新增字段

# 新增 SongSection 类型
class SongSection(TypedDict):
    name: str
    type: SectionType
    progression: List[ChordConfig]
    length: int  # 小节数
    bpm: int

Progression = List[ChordConfig]
ChordDatabase = Dict[str, Dict[str, List[str]]]