from typing import TypedDict, List, Dict, Literal

ChordType = Literal['maj', 'min', '7', 'maj7', 'sus4', 'm7']
RomanNumeral = Literal['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
ChordStyle = Literal['block', 'arpeggio']

class ChordConfig(TypedDict):
    roman: RomanNumeral
    type: ChordType
    inversion: int

Progression = List[ChordConfig]
ChordDatabase = Dict[str, Dict[str, List[str]]]