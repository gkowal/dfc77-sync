from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class SineOscillator:
    frequency: float
    samplerate: int
    phase: float = 0.0

    def make_block_time(self, blocksize: int) -> np.ndarray:
        # Matches: self.t_block = np.arange(self.blocksize) / self.samplerate
        return np.arange(blocksize) / self.samplerate

    def render(self, t_block: np.ndarray, frames: int, amplitude: float) -> np.ndarray:
        """
        Matches:

            out = amplitude * sin(2π f t_block + phase)
            phase = (phase + 2π f frames / samplerate) % (2π)
        """
        out = amplitude * np.sin(2 * np.pi * self.frequency * t_block + self.phase)
        self.phase = (self.phase + 2 * np.pi * self.frequency * frames / self.samplerate) % (2 * np.pi)
        return out.astype(np.float32, copy=False)