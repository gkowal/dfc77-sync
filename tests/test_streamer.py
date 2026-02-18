from __future__ import annotations

from datetime import datetime

from dcf77gen.core.config import GeneratorConfig
from dcf77gen.realtime import streamer


def test_run_reseeds_timing_after_alignment_sleep(monkeypatch) -> None:
    cfg = GeneratorConfig(frequency=440.0, samplerate=48000, amplitude=0.5)
    realtime = streamer.RealtimeStreamer(cfg)

    refresh_before = datetime(2026, 2, 18, 10, 0, 0, 1000)
    seed_before_sleep = datetime(2026, 2, 18, 10, 0, 0, 24000)
    seed_after_sleep = datetime(2026, 2, 18, 10, 0, 0, 100000)
    refresh_after = datetime(2026, 2, 18, 10, 0, 0, 101000)
    now_values = iter([refresh_before, seed_before_sleep, seed_after_sleep, refresh_after])

    monkeypatch.setattr(streamer, "now_dt", lambda _use_utc: next(now_values))
    monkeypatch.setattr(streamer.time, "sleep", lambda _s: None)
    monkeypatch.setattr(streamer, "print_ui", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(streamer.sys.stdin, "isatty", lambda: False)

    seed_calls: list[tuple[datetime, int]] = []
    original_seed = realtime.state.seed_from_wallclock

    def _seed_spy(now: datetime, offset_s: int) -> None:
        seed_calls.append((now, offset_s))
        original_seed(now, offset_s)

    monkeypatch.setattr(realtime.state, "seed_from_wallclock", _seed_spy)

    class _FakeOutputStream:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        def __enter__(self):
            realtime.stop_event.set()
            return self

        def __exit__(self, _exc_type, _exc, _tb) -> bool:
            return False

    monkeypatch.setattr(streamer.sd, "OutputStream", _FakeOutputStream)

    realtime.run(device_id=None)

    assert len(seed_calls) == 2
    assert seed_calls[0][0] == seed_before_sleep
    assert seed_calls[1][0] == seed_after_sleep
    assert seed_calls[1][0] != seed_calls[0][0]


def test_wait_for_enter_handles_eof_and_sets_stop_event(monkeypatch) -> None:
    cfg = GeneratorConfig(frequency=440.0, samplerate=48000, amplitude=0.5)
    realtime = streamer.RealtimeStreamer(cfg)

    def _raise_eof() -> str:
        raise EOFError

    monkeypatch.setattr("builtins.input", _raise_eof)
    realtime._wait_for_enter()
    assert realtime.stop_event.is_set()
