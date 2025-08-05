from typing import TypedDict, List, Dict, Literal

ChordType = Literal['maj', 'min', '7', 'maj7', 'sus4', 'm7']
RomanNumeral = Literal['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
ChordStyle = Literal['block', 'arpeggio']  # 添加这个类型定义

class ChordConfig(TypedDict):
    roman: RomanNumeral
    type: ChordType
    inversion: int
    duration: float

Progression = List[ChordConfig]
ChordDatabase = Dict[str, Dict[str, List[str]]]