from __future__ import annotations

import argparse
import sounddevice as sd
import sys

from dfc77gen.core.config import GeneratorConfig
from dfc77gen.realtime.streamer import RealtimeStreamer


def _list_output_devices() -> list[tuple[int, dict]]:
    devices = sd.query_devices()
    return [
        (i, dev)
        for i, dev in enumerate(devices)
        if int(dev.get("max_output_channels", 0)) > 0
    ]


def _print_device_matches(matches: list[tuple[int, dict]]) -> None:
    for device_id, dev in matches:
        print(f"  [{device_id}] {dev['name']}")


def _resolve_device_id(device_arg: str | None, parser: argparse.ArgumentParser) -> int | None:
    if device_arg is None:
        return None

    try:
        return int(device_arg)
    except ValueError:
        pass

    query = device_arg.strip().lower()
    if not query:
        parser.error("--device cannot be empty")

    output_devices = _list_output_devices()
    matches = [(i, dev) for i, dev in output_devices if query in str(dev.get("name", "")).lower()]

    if len(matches) == 1:
        return matches[0][0]

    if len(matches) == 0:
        print(f"No output device matches '{device_arg}'.")
        print("Available output devices:")
        _print_device_matches(output_devices)
        parser.exit(2)

    print(f"Multiple output devices match '{device_arg}':")
    _print_device_matches(matches)
    print("Refine --device or pass an explicit numeric device ID.")
    parser.exit(2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Synchronizes DFC77 devices using sound speakers.")
    parser.add_argument("-l", "--list-devices", action="store_true", help="list audio devices")
    parser.add_argument("-d", "--device", type=str, help="device ID or case-insensitive name substring")
    parser.add_argument("-f", "--frequency", type=float, default=77500, help="frequency (Hz)")
    parser.add_argument("-a", "--amplitude", type=float, default=1.0, help="amplitude")
    parser.add_argument("-s", "--samplerate", type=int, default=None, help="sample rate")
    parser.add_argument("-u", "--utc", action="store_true", help="use UTC time")
    parser.add_argument("-o", "--offset", type=int, default=0, help="second offset")

    args = parser.parse_args()

    if args.list_devices:
        print(sd.query_devices())
        return

    device_id = _resolve_device_id(args.device, parser)

    if args.samplerate is not None:
        actual_samplerate = int(args.samplerate)
        try:
            sd.check_output_settings(device_id, samplerate=actual_samplerate)
        except Exception as exc:
            parser.error(
                f"requested --samplerate {actual_samplerate} is not supported by the selected output device: {exc}"
            )
    else:
        actual_samplerate = int(sd.query_devices(device_id, "output")["default_samplerate"])

    try:
        cfg = GeneratorConfig(
            frequency=float(args.frequency),
            samplerate=int(actual_samplerate),
            amplitude=float(args.amplitude),
            utc=bool(args.utc),
            offset=int(args.offset),
        )
        RealtimeStreamer(cfg).run(device_id=device_id)
    except ValueError as exc:
        parser.error(str(exc))
    except KeyboardInterrupt:
        print("\r\033[K", end="", flush=True)
        sys.exit(0)
