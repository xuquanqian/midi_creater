# src/rhythm/handler.py
from mido import MidiTrack, Message
from .types import RhythmType

class RhythmHandler:
    @staticmethod
    def apply_rhythm(track: MidiTrack, notes: list[int], ticks: int, 
                   duration: float, rhythm: RhythmType, velocity: int = 100):
        """独立节奏处理器，不影响原有和弦生成逻辑"""
        if rhythm == 'straight':
            RhythmHandler._straight(track, notes, ticks, duration, velocity)
        elif rhythm == 'triplet':
            RhythmHandler._triplet(track, notes, ticks, duration, velocity)
        elif rhythm == 'swing':
            RhythmHandler._swing(track, notes, ticks, duration, velocity)
        elif rhythm == 'shuffle':
            RhythmHandler._shuffle(track, notes, ticks, duration, velocity)
        elif rhythm == 'acg_8beat':
            RhythmHandler._acg_8beat(track, notes, ticks, duration, velocity)
        elif rhythm == 'acg_16beat':
            RhythmHandler._acg_16beat(track, notes, ticks, duration, velocity)
        elif rhythm == 'pop_ballad':
            RhythmHandler._pop_ballad(track, notes, ticks, duration, velocity)
        elif rhythm == 'rock_4beat':
            RhythmHandler._rock_4beat(track, notes, ticks, duration, velocity)
        elif rhythm == 'jazz_waltz':
            RhythmHandler._jazz_waltz(track, notes, ticks, duration, velocity)
        elif rhythm == 'citypop':
            RhythmHandler._citypop(track, notes, ticks, duration, velocity)
        elif rhythm == 'anime_op':
            RhythmHandler._anime_op(track, notes, ticks, duration, velocity)
        elif rhythm == 'kpop_sync':
            RhythmHandler._kpop_sync(track, notes, ticks, duration, velocity)

    @staticmethod
    def _straight(track: MidiTrack, notes: list[int], ticks: int, 
                 duration: float, velocity: int):
        time = int(ticks * duration)
        for note in notes:
            track.append(Message('note_on', note=note, velocity=velocity, time=0))
        track.append(Message('note_off', note=notes[0], velocity=velocity, time=time))
        for note in notes[1:]:
            track.append(Message('note_off', note=note, velocity=velocity, time=0))

    @staticmethod
    def _triplet(track: MidiTrack, notes: list[int], ticks: int, 
                duration: float, velocity: int):
        time = int(ticks * duration / 3)
        for _ in range(3):
            for note in notes:
                track.append(Message('note_on', note=note, velocity=velocity, time=0))
            track.append(Message('note_off', note=notes[0], velocity=velocity, time=time))
            for note in notes[1:]:
                track.append(Message('note_off', note=note, velocity=velocity, time=0))

    @staticmethod
    def _swing(track: MidiTrack, notes: list[int], ticks: int, 
              duration: float, velocity: int):
        first = int(ticks * duration * 0.6)
        second = int(ticks * duration * 0.4)
        
        # 第一拍
        for note in notes:
            track.append(Message('note_on', note=note, velocity=velocity, time=0))
        track.append(Message('note_off', note=notes[0], velocity=velocity, time=first))
        for note in notes[1:]:
            track.append(Message('note_off', note=note, velocity=velocity, time=0))
        
        # 第二拍
        for note in notes:
            track.append(Message('note_on', note=note, velocity=int(velocity*0.9), time=0))
        track.append(Message('note_off', note=notes[0], velocity=int(velocity*0.9), time=second))
        for note in notes[1:]:
            track.append(Message('note_off', note=note, velocity=int(velocity*0.9), time=0))

    @staticmethod
    def _shuffle(track: MidiTrack, notes: list[int], ticks: int, 
               duration: float, velocity: int):
        first = int(ticks * duration * 0.75)
        second = int(ticks * duration * 0.25)
        
        # 第一拍
        for note in notes:
            track.append(Message('note_on', note=note, velocity=velocity, time=0))
        track.append(Message('note_off', note=notes[0], velocity=velocity, time=first))
        for note in notes[1:]:
            track.append(Message('note_off', note=note, velocity=velocity, time=0))
        
        # 第二拍
        for note in notes:
            track.append(Message('note_on', note=note, velocity=int(velocity*0.8), time=0))
        track.append(Message('note_off', note=notes[0], velocity=int(velocity*0.8), time=second))
        for note in notes[1:]:
            track.append(Message('note_off', note=note, velocity=int(velocity*0.8), time=0))

    # 以下是新增的节奏型
    @staticmethod
    def _acg_8beat(track: MidiTrack, notes: list[int], ticks: int, 
                  duration: float, velocity: int):
        """日式ACG八分音符节奏"""
        time = int(ticks * duration / 2)
        for _ in range(2):
            for note in notes:
                track.append(Message('note_on', note=note, velocity=int(velocity*0.95), time=0))
            track.append(Message('note_off', note=notes[0], velocity=int(velocity*0.95), time=time))
            for note in notes[1:]:
                track.append(Message('note_off', note=note, velocity=int(velocity*0.95), time=0))

    @staticmethod
    def _acg_16beat(track: MidiTrack, notes: list[int], ticks: int, 
                   duration: float, velocity: int):
        """日式ACG十六分音符节奏，带切分"""
        time1 = int(ticks * duration * 0.3)
        time2 = int(ticks * duration * 0.2)
        time3 = int(ticks * duration * 0.5)
        
        # 第一拍
        for note in notes:
            track.append(Message('note_on', note=note, velocity=int(velocity*0.9), time=0))
        track.append(Message('note_off', note=notes[0], velocity=int(velocity*0.9), time=time1))
        for note in notes[1:]:
            track.append(Message('note_off', note=note, velocity=int(velocity*0.9), time=0))
        
        # 第二拍
        for note in notes:
            track.append(Message('note_on', note=note, velocity=int(velocity*0.8), time=0))
        track.append(Message('note_off', note=notes[0], velocity=int(velocity*0.8), time=time2))
        for note in notes[1:]:
            track.append(Message('note_off', note=note, velocity=int(velocity*0.8), time=0))
        
        # 第三拍
        for note in notes:
            track.append(Message('note_on', note=note, velocity=velocity, time=0))
        track.append(Message('note_off', note=notes[0], velocity=velocity, time=time3))
        for note in notes[1:]:
            track.append(Message('note_off', note=note, velocity=velocity, time=0))

    @staticmethod
    def _pop_ballad(track: MidiTrack, notes: list[int], ticks: int, 
                    duration: float, velocity: int):
        """华语流行抒情节奏"""
        time1 = int(ticks * duration * 0.7)
        time2 = int(ticks * duration * 0.3)
        
        # 强拍
        for note in notes:
            track.append(Message('note_on', note=note, velocity=velocity, time=0))
        track.append(Message('note_off', note=notes[0], velocity=velocity, time=time1))
        for note in notes[1:]:
            track.append(Message('note_off', note=note, velocity=velocity, time=0))
        
        # 弱拍
        for note in notes:
            track.append(Message('note_on', note=note, velocity=int(velocity*0.7), time=0))
        track.append(Message('note_off', note=notes[0], velocity=int(velocity*0.7), time=time2))
        for note in notes[1:]:
            track.append(Message('note_off', note=note, velocity=int(velocity*0.7), time=0))

    @staticmethod
    def _rock_4beat(track: MidiTrack, notes: list[int], ticks: int, 
                   duration: float, velocity: int):
        """摇滚四拍强节奏"""
        time = int(ticks * duration / 4)
        for i in range(4):
            vel = velocity if i == 0 else int(velocity * 0.85)
            for note in notes:
                track.append(Message('note_on', note=note, velocity=vel, time=0))
            track.append(Message('note_off', note=notes[0], velocity=vel, time=time))
            for note in notes[1:]:
                track.append(Message('note_off', note=note, velocity=vel, time=0))

    @staticmethod
    def _jazz_waltz(track: MidiTrack, notes: list[int], ticks: int, 
                   duration: float, velocity: int):
        """爵士华尔兹三拍节奏"""
        time = int(ticks * duration / 3)
        velocities = [velocity, int(velocity*0.8), int(velocity*0.7)]
        for i in range(3):
            for note in notes:
                track.append(Message('note_on', note=note, velocity=velocities[i], time=0))
            track.append(Message('note_off', note=notes[0], velocity=velocities[i], time=time))
            for note in notes[1:]:
                track.append(Message('note_off', note=note, velocity=velocities[i], time=0))

    @staticmethod
    def _citypop(track: MidiTrack, notes: list[int], ticks: int, 
                duration: float, velocity: int):
        """日式CityPop节奏，带切分和弱拍重音"""
        time1 = int(ticks * duration * 0.4)
        time2 = int(ticks * duration * 0.2)
        time3 = int(ticks * duration * 0.4)
        
        # 第一拍
        for note in notes:
            track.append(Message('note_on', note=note, velocity=int(velocity*0.9), time=0))
        track.append(Message('note_off', note=notes[0], velocity=int(velocity*0.9), time=time1))
        for note in notes[1:]:
            track.append(Message('note_off', note=note, velocity=int(velocity*0.9), time=0))
        
        # 第二拍
        for note in notes:
            track.append(Message('note_on', note=note, velocity=int(velocity*0.7), time=0))
        track.append(Message('note_off', note=notes[0], velocity=int(velocity*0.7), time=time2))
        for note in notes[1:]:
            track.append(Message('note_off', note=note, velocity=int(velocity*0.7), time=0))
        
        # 第三拍
        for note in notes:
            track.append(Message('note_on', note=note, velocity=int(velocity*0.95), time=0))
        track.append(Message('note_off', note=notes[0], velocity=int(velocity*0.95), time=time3))
        for note in notes[1:]:
            track.append(Message('note_off', note=note, velocity=int(velocity*0.95), time=0))

    @staticmethod
    def _anime_op(track: MidiTrack, notes: list[int], ticks: int, 
                 duration: float, velocity: int):
        """动画OP常用节奏，强调第一和第三拍"""
        time1 = int(ticks * duration * 0.4)
        time2 = int(ticks * duration * 0.2)
        time3 = int(ticks * duration * 0.3)
        time4 = int(ticks * duration * 0.1)
        
        # 第一拍（强）
        for note in notes:
            track.append(Message('note_on', note=note, velocity=velocity, time=0))
        track.append(Message('note_off', note=notes[0], velocity=velocity, time=time1))
        for note in notes[1:]:
            track.append(Message('note_off', note=note, velocity=velocity, time=0))
        
        # 第二拍（弱）
        for note in notes:
            track.append(Message('note_on', note=note, velocity=int(velocity*0.6), time=0))
        track.append(Message('note_off', note=notes[0], velocity=int(velocity*0.6), time=time2))
        for note in notes[1:]:
            track.append(Message('note_off', note=note, velocity=int(velocity*0.6), time=0))
        
        # 第三拍（次强）
        for note in notes:
            track.append(Message('note_on', note=note, velocity=int(velocity*0.9), time=0))
        track.append(Message('note_off', note=notes[0], velocity=int(velocity*0.9), time=time3))
        for note in notes[1:]:
            track.append(Message('note_off', note=note, velocity=int(velocity*0.9), time=0))
        
        # 第四拍（弱）
        for note in notes:
            track.append(Message('note_on', note=note, velocity=int(velocity*0.5), time=0))
        track.append(Message('note_off', note=notes[0], velocity=int(velocity*0.5), time=time4))
        for note in notes[1:]:
            track.append(Message('note_off', note=note, velocity=int(velocity*0.5), time=0))

    @staticmethod
    def _kpop_sync(track: MidiTrack, notes: list[int], ticks: int, 
                  duration: float, velocity: int):
        """韩式流行同步节奏，强调反拍"""
        time1 = int(ticks * duration * 0.25)
        time2 = int(ticks * duration * 0.25)
        time3 = int(ticks * duration * 0.5)
        
        # 前两拍（弱）
        for note in notes:
            track.append(Message('note_on', note=note, velocity=int(velocity*0.7), time=0))
        track.append(Message('note_off', note=notes[0], velocity=int(velocity*0.7), time=time1))
        for note in notes[1:]:
            track.append(Message('note_off', note=note, velocity=int(velocity*0.7), time=0))
        
        # 第三拍（强）
        for note in notes:
            track.append(Message('note_on', note=note, velocity=velocity, time=0))
        track.append(Message('note_off', note=notes[0], velocity=velocity, time=time2))
        for note in notes[1:]:
            track.append(Message('note_off', note=note, velocity=velocity, time=0))
        
        # 第四拍（次强）
        for note in notes:
            track.append(Message('note_on', note=note, velocity=int(velocity*0.9), time=0))
        track.append(Message('note_off', note=notes[0], velocity=int(velocity*0.9), time=time3))
        for note in notes[1:]:
            track.append(Message('note_off', note=note, velocity=int(velocity*0.9), time=0))