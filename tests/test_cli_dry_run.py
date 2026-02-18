from __future__ import annotations

import sys

from dcf77gen.cli import app


def test_dry_run_does_not_query_sounddevice_without_samplerate(
    monkeypatch, capsys
) -> None:
    def _fail_query(*_args, **_kwargs):
        raise AssertionError("sounddevice query should not happen during dry-run")

    monkeypatch.setattr(app.sd, "query_devices", _fail_query)
    monkeypatch.setattr(app.sd, "check_output_settings", _fail_query)
    monkeypatch.setattr(sys, "argv", ["dcf77-sync", "--dry-run"])

    app.main()
    out = capsys.readouterr().out
    assert "DCF77 dry run" in out
    assert "device: default output (not queried in dry-run)" in out
    assert "samplerate: 192000" in out


def test_dry_run_derives_samplerate_from_frequency_when_needed(
    monkeypatch, capsys
) -> None:
    def _fail_query(*_args, **_kwargs):
        raise AssertionError("sounddevice query should not happen during dry-run")

    monkeypatch.setattr(app.sd, "query_devices", _fail_query)
    monkeypatch.setattr(app.sd, "check_output_settings", _fail_query)
    monkeypatch.setattr(sys, "argv", ["dcf77-sync", "--dry-run", "--frequency", "200000"])

    app.main()
    out = capsys.readouterr().out
    assert "samplerate: 400001" in out
