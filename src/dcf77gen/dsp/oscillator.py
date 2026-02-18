from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np


@dataclass
class SineOscillator:
    frequency: float
    samplerate: int
    phase: float = 0.0
    _table: np.ndarray = field(init=False, repr=False)
    _sample_index: int = field(init=False, default=0, repr=False)

    def __post_init__(self) -> None:
        t = np.arange(self.samplerate, dtype=np.float64) / float(self.samplerate)
        self._table = np.sin(2 * np.pi * self.frequency * t).astype(np.float32, copy=False)
        phase_turns = (self.phase % (2 * np.pi)) / (2 * np.pi)
        self._sample_index = int(phase_turns * self.samplerate) % self.samplerate

    def render(self, frames: int, amplitude: float) -> np.ndarray:
        """
        Table-driven oscillator:
          - precompute one second of carrier at `samplerate`
          - read `frames` samples with wrap-around
          - advance sample index modulo table length
        """
        if frames <= 0:
            return np.zeros(0, dtype=np.float32)

        table_len = len(self._table)
        start = self._sample_index
        end = start + frames

        if end <= table_len:
            wave = self._table[start:end]
        else:
            wrap = end - table_len
            wave = np.concatenate((self._table[start:], self._table[:wrap]))

        self._sample_index = end % table_len
        return (wave * np.float32(amplitude)).astype(np.float32, copy=False)
