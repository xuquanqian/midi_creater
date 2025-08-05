from typing import List, Optional
from custom_types import ChordConfig

class ChordClipboard:
    def __init__(self):
        self._data: Optional[List[ChordConfig]] = None
    
    def copy(self, chords: List[ChordConfig]):
        """复制和弦进行到剪贴板"""
        self._data = [chord.copy() for chord in chords]
    
    def paste(self) -> Optional[List[ChordConfig]]:
        """从剪贴板粘贴和弦进行"""
        if self._data:
            return [chord.copy() for chord in self._data]
        return None
    
    def has_data(self) -> bool:
        """检查剪贴板是否有数据"""
        return self._data is not None
    
    def clear(self):
        """清空剪贴板"""
        self._data = None