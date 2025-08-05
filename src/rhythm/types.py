# src/rhythm/types.py
from typing import Literal

RhythmType = Literal[
    'straight',       # 标准节奏
    'triplet',        # 三连音
    'swing',          # 摇摆节奏
    'shuffle',        # 曳步舞节奏
    'acg_8beat',      # 日式ACG八分音符节奏
    'acg_16beat',     # 日式ACG十六分音符节奏(带切分)
    'pop_ballad',     # 华语流行抒情节奏
    'rock_4beat',     # 摇滚四拍强节奏
    'jazz_waltz',     # 爵士华尔兹三拍节奏
    'citypop',        # 日式CityPop节奏
    'anime_op',       # 动画OP节奏
    'kpop_sync'       # 韩式流行同步节奏
]

RHYTHM_TYPES = [
    'straight',
    'triplet',
    'swing',
    'shuffle',
    'acg_8beat',
    'acg_16beat',
    'pop_ballad',
    'rock_4beat',
    'jazz_waltz',
    'citypop',
    'anime_op',
    'kpop_sync'
]