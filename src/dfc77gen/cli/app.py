from __future__ import annotations

import argparse
import sounddevice as sd
import sys

from dfc77gen.core.config import GeneratorConfig
from dfc77gen.realtime.streamer import RealtimeStreamer


def main() -> None:
    parser = argparse.ArgumentParser(description="Synchronizes DFC77 devices using sound speakers.")
    parser.add_argument("-l", "--list-devices", action="store_true", help="list audio devices")
    parser.add_argument("-d", "--device", type=int, help="device ID")
    parser.add_argument("-f", "--frequency", type=float, default=77500, help="frequency (Hz)")
    parser.add_argument("-a", "--amplitude", type=float, default=1.0, help="amplitude")
    parser.add_argument("-s", "--samplerate", type=float, default=192000, help="sample rate")
    parser.add_argument("-u", "--utc", action="store_true", help="use UTC time")
    parser.add_argument("-o", "--offset", type=int, default=0, help="second offset")

    args = parser.parse_args()

    if args.list_devices:
        print(sd.query_devices())
        return

    try:
        sd.check_output_settings(args.device, samplerate=args.samplerate)
        actual_samplerate = int(args.samplerate)
    except Exception:
        actual_samplerate = int(sd.query_devices(args.device, "output")["default_samplerate"])

    cfg = GeneratorConfig(
        frequency=float(args.frequency),
        samplerate=int(actual_samplerate),
        amplitude=float(args.amplitude),
        utc=bool(args.utc),
        offset=int(args.offset),
    )

    try:
        RealtimeStreamer(cfg).run(device_id=args.device)
    except KeyboardInterrupt:
        print("\r\033[K", end="", flush=True)
        sys.exit(0)