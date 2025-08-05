from dataclasses import dataclass
from typing import Dict, List
from copy import deepcopy
from custom_types import SongSection, ChordConfig, SectionType

@dataclass
class SectionManager:
    sections: Dict[str, SongSection] = None
    current_section: str = ""
    
    def __post_init__(self):
        if self.sections is None:
            self.sections = {}
    
    def add_section(self, name: str, section_type: SectionType, 
                   length: int = 8, bpm: int = 120):
        """添加新段落"""
        self.sections[name] = {
            'name': name,
            'type': section_type,
            'progression': [],
            'length': length,
            'bpm': bpm
        }
    
    def duplicate_section(self, source_name: str, new_name: str):
        """复制段落"""
        if source_name in self.sections:
            self.sections[new_name] = deepcopy(self.sections[source_name])
            self.sections[new_name]['name'] = new_name
    
    def get_current_progression(self) -> List[ChordConfig]:
        """获取当前段落的和弦进行"""
        return self.sections[self.current_section]['progression']
    
    def set_current_progression(self, progression: List[ChordConfig]):
        """设置当前段落的和弦进行"""
        self.sections[self.current_section]['progression'] = progression