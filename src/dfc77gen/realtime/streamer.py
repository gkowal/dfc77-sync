from __future__ import annotations

import threading
import time
from typing import Any
import sounddevice as sd

from dfc77gen.core.config import GeneratorConfig
from dfc77gen.core.state import GeneratorState
from dfc77gen.core.clock import now_dt
from dfc77gen.protocol.encoder import build_time_bits
from dfc77gen.dsp.modulation import is_low_pulse
from dfc77gen.dsp.oscillator import SineOscillator
from dfc77gen.ui.console import print_ui


class RealtimeStreamer:
    """
    Realtime DCF77 audio streamer.

    Uses 100 ms blocks (`blocksize = samplerate // 10`) and advances
    second/deci-second counters once per callback block.
    """

    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.state = GeneratorState()
        self.stop_event = threading.Event()

        self.blocksize = int(self.config.samplerate // 10)

        self.osc = SineOscillator(
            frequency=self.config.frequency,
            samplerate=self.config.samplerate,
            phase=0.0,
        )

    def _refresh_time_bits(self) -> None:
        # Sample wall clock exactly once per refresh.
        refresh_now = now_dt(self.config.utc)
        res = build_time_bits(refresh_now)
        self.state.time_bits = res.time_bits

    def _ui_loop(self, interval_s: float = 0.1) -> None:
        while not self.stop_event.is_set():
            print_ui(self.state, self.config.utc)
            self.stop_event.wait(interval_s)

    def _wait_for_enter(self) -> None:
        input()
        self.stop_event.set()

    def _callback(self, outdata: Any, frames: int, _time_info: Any, _status: Any) -> None:
        if self.stop_event.is_set():
            raise sd.CallbackStop

        is_low = is_low_pulse(self.state.count_sec, self.state.count_deci, self.state.time_bits)
        amp = float(self.config.amplitude) * (self.config.low_factor if is_low else 1.0)

        block = self.osc.render(frames, amp)
        outdata[:, 0] = block

        # advance counters
        self.state.advance_block()

        # Update time bits at deterministic minute refresh point (sec=59, dec=0).
        if self.state.is_minute_refresh_point():
            self._refresh_time_bits()

    def run(self, device_id: int | None = None) -> None:
        self.stop_event.clear()
        self._refresh_time_bits()

        now = now_dt(self.config.utc)
        self.state.seed_from_wallclock(now, self.config.offset)

        print("=" * 96)
        print(f"\n  DCF77 Generator Active ({self.config.frequency} Hz)\n")
        print("  Press Enter to terminate\n")
        print("=" * 96)
        print_ui(self.state, self.config.utc)

        # Same alignment logic as original (kept intentionally for phase-1 refactor)
        alignment_sleep = 0.1 - (now.microsecond % 100000) / 1e6
        time.sleep(alignment_sleep)

        with sd.OutputStream(
            device=device_id,
            blocksize=self.blocksize,
            channels=self.config.channels,
            callback=self._callback,
            samplerate=self.config.samplerate,
            latency=self.config.latency,
            dtype="float32",
        ):
            ui_thread = threading.Thread(target=self._ui_loop, daemon=True)
            ui_thread.start()
            threading.Thread(target=self._wait_for_enter, daemon=True).start()

            try:
                while not self.stop_event.is_set():
                    time.sleep(0.05)
            except KeyboardInterrupt:
                self.stop_event.set()

            ui_thread.join(timeout=1.0)
            print("\r\033[K", end="", flush=True)
