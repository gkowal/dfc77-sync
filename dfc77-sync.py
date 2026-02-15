#!/usr/bin/env python3
"""
Synchronizes DCF77 devices using sound speakers via a class-based architecture
with phase continuity management and real-time visual bit tracking.
"""

import argparse
import numpy as np
import sounddevice as sd
import sys
import time
from datetime import datetime, timedelta, UTC

class DCF77Generator:
    def __init__(self, frequency=77500.0, samplerate=192000, amplitude=1.0, utc=False, offset=0):
        self.frequency = frequency
        self.samplerate = samplerate
        self.amplitude = amplitude
        self.utc = utc
        self.offset = offset

        self.phase = 0.0
        self.count_sec = 0
        self.count_dec = 0
        self.time_bits = 0

        self.blocksize = int(self.samplerate // 10)
        self.t_block = np.arange(self.blocksize) / self.samplerate

    @staticmethod
    def to_bcd(n):
        return ((int(n) // 10) % 10 << 4) | (n % 10)

    @staticmethod
    def parity(n, l, u):
        r = 0
        for i in range(l, u + 1):
            if n & (1 << i):
                r += 1
        return r & 1

    def update_time_bits(self):
        now = datetime.now(UTC) if self.utc else datetime.now()
        target_time = now + (timedelta(minutes=1) if now.second < 10 else timedelta(minutes=2))

        bits = 0
        bits |= 1 << 20
        bits |= self.to_bcd(target_time.minute) << 21
        bits |= self.to_bcd(target_time.hour) << 29
        bits |= self.to_bcd(target_time.day) << 36
        bits |= self.to_bcd(target_time.isoweekday()) << 42
        bits |= self.to_bcd(target_time.month) << 45
        bits |= self.to_bcd(target_time.year % 100) << 50
        bits |= self.parity(bits, 21, 27) << 28
        bits |= self.parity(bits, 29, 34) << 35
        bits |= self.parity(bits, 36, 57) << 58
        self.time_bits = bits

    def update_ui(self):
        b = ('{:059b}'.format(self.time_bits))[::-1]
        slices = [(0,1), (1,15), (15,20), (20,21), (21,28), (28,29),
                  (29,35), (35,36), (36,42), (42,45), (45,50), (50,58), (58,59)]

        INV, RST = '\033[7m', '\033[0m'
        output_segments = []
        bit_idx = 0
        for start, end in slices:
            seg_str = ""
            for i in range(start, end):
                seg_str += f"{INV}{b[i]}{RST}" if bit_idx == self.count_sec else b[i]
                bit_idx += 1
            output_segments.append(seg_str)

        line = (f"{output_segments[0]} {output_segments[1]} {output_segments[2]} "
                f"{output_segments[3]} {output_segments[4]}.{output_segments[5]} "
                f"{output_segments[6]}.{output_segments[7]} {output_segments[8]} "
                f"{output_segments[9]} {output_segments[10]} {output_segments[11]}.{output_segments[12]} X")

        now = datetime.now(UTC) if self.utc else datetime.now()
        print(f"\r{now.strftime('%Y-%m-%d %H:%M:%S')} -> {line}", end='', flush=True)

    def callback(self, outdata, frames, time_info, status):
        if status:
            print(status, file=sys.stderr)

        is_silence = False
        if self.count_sec < 59:
            if self.count_dec == 0 or (self.count_dec == 1 and (self.time_bits >> self.count_sec) & 1):
                is_silence = True

        outdata[:, 0] = (0.0 if is_silence else self.amplitude) * np.sin(2 * np.pi * self.frequency * self.t_block + self.phase)
        self.phase = (self.phase + 2 * np.pi * self.frequency * frames / self.samplerate) % (2 * np.pi)

        if self.count_dec == 0:
            self.update_ui()

        self.count_dec += 1
        if self.count_dec >= 10:
            self.count_dec = 0
            self.count_sec += 1
        if self.count_sec >= 60:
            self.count_sec = 0
        if self.count_sec == 59 and self.count_dec == 0:
            self.update_time_bits()

    def run(self, device_id=None):
        self.update_time_bits()
        now = datetime.now(UTC) if self.utc else datetime.now()
        self.count_sec = (now.second + self.offset) % 60
        self.count_dec = int(now.microsecond // 1e5)

        print('=' * 96)
        print(f"\n  DCF77 Generator Active ({self.frequency} Hz)\n")
        print("  Press Enter to terminate\n")
        print('=' * 96)
        self.update_ui()

        alignment_sleep = 0.1 - (now.microsecond % 100000) / 1e6
        time.sleep(alignment_sleep)

        with sd.OutputStream(device=device_id, blocksize=self.blocksize, channels=1,
                             callback=self.callback, samplerate=self.samplerate, latency='low'):
            input()
            # \r moves to start, \033[K clears the line to prevent leftover text
            print('\r\033[K', end='', flush=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-l', '--list-devices', action='store_true', help='list audio devices')
    parser.add_argument('-d', '--device', type=int, help='device ID')
    parser.add_argument('-f', '--frequency', type=float, default=77500, help='frequency (Hz)')
    parser.add_argument('-a', '--amplitude', type=float, default=1.0, help='amplitude')
    parser.add_argument('-s', '--samplerate', type=float, default=192000, help='sample rate')
    parser.add_argument('-u', '--utc', action='store_true', help='use UTC time')
    parser.add_argument('-o', '--offset', type=int, default=0, help='second offset')

    args = parser.parse_args()

    if args.list_devices:
        print(sd.query_devices())
        return

    try:
        sd.check_output_settings(args.device, samplerate=args.samplerate)
        actual_samplerate = args.samplerate
    except Exception:
        actual_samplerate = sd.query_devices(args.device, 'output')['default_samplerate']

    generator = DCF77Generator(
        frequency=args.frequency, samplerate=actual_samplerate,
        amplitude=args.amplitude, utc=args.utc, offset=args.offset
    )

    try:
        generator.run(device_id=args.device)
    except KeyboardInterrupt:
        print('\r\033[K', end='', flush=True)
        sys.exit(0)

if __name__ == "__main__":
    main()
