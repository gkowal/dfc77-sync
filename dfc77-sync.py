#!/usr/bin/env python3
"""
Synchronizes DCF77 devices using sound speakers via a class-based architecture
with phase continuity management.
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

        # Phase accumulator to ensure continuity between blocks
        self.phase = 0.0

        # Timing state
        self.count_sec = 0
        self.count_dec = 0 # tenths of a second
        self.time_bits = 0

        # Pre-calculate time array for one block (100ms)
        self.blocksize = int(self.samplerate // 10)
        self.t_block = np.arange(self.blocksize) / self.samplerate

    @staticmethod
    def to_bcd(n):
        """Converts an integer to Binary Coded Decimal."""
        return ((int(n) // 10) % 10 << 4) | (n % 10)

    @staticmethod
    def parity(n, l, u):
        """Calculates even parity for a bit range."""
        r = 0
        for i in range(l, u + 1):
            if n & (1 << i):
                r += 1
        return r & 1

    def update_time_bits(self):
        """Generates the 59-bit DCF77 telegram for the upcoming minute."""
        # Use timezone-aware UTC if requested to avoid DeprecationWarning
        now = datetime.now(UTC) if self.utc else datetime.now()

        # Determine the minute we are currently encoding for
        if now.second < 10:
            target_time = now + timedelta(minutes=1)
        else:
            target_time = now + timedelta(minutes=2)

        bits = 0
        bits |= 1 << 20  # Start of time information (S bit)
        bits |= self.to_bcd(target_time.minute) << 21
        bits |= self.to_bcd(target_time.hour) << 29
        bits |= self.to_bcd(target_time.day) << 36
        bits |= self.to_bcd(target_time.isoweekday()) << 42
        bits |= self.to_bcd(target_time.month) << 45
        bits |= self.to_bcd(target_time.year % 100) << 50

        # Parity bits
        bits |= self.parity(bits, 21, 27) << 28
        bits |= self.parity(bits, 29, 34) << 35
        bits |= self.parity(bits, 36, 57) << 58

        self.time_bits = bits

        # Print bitstream in standard DCF77 segments
        b = ('{:059b}'.format(bits))[::-1]
        print(f"{target_time} -> {b[0]} {b[1:15]} {b[15:20]} {b[20]} "
              f"{b[21:28]}.{b[28]} {b[29:35]}.{b[35]} "
              f"{b[36:42]} {b[42:45]} {b[45:50]} {b[50:58]}.{b[58]} X")

    def callback(self, outdata, frames, time_info, status):
        """Real-time audio callback ensuring phase continuity."""
        if status:
            print(status, file=sys.stderr)

        # Modulation logic: 100ms/200ms amplitude drop
        is_silence = False
        if self.count_sec < 59:
            if self.count_dec == 0:
                is_silence = True
            elif self.count_dec == 1:
                # bit == 1 requires 200ms drop
                if (self.time_bits >> self.count_sec) & 1:
                    is_silence = True

        # Apply amplitude modulation
        current_amp = 0.0 if is_silence else self.amplitude

        # Generate carrier with phase offset
        outdata[:, 0] = current_amp * np.sin(2 * np.pi * self.frequency * self.t_block + self.phase)

        # Update phase accumulator for the next block
        self.phase = (self.phase + 2 * np.pi * self.frequency * frames / self.samplerate) % (2 * np.pi)

        # Advance counters (one block = 0.1s)
        self.count_dec += 1
        if self.count_dec >= 10:
            self.count_dec = 0
            self.count_sec += 1

        if self.count_sec >= 60:
            self.count_sec = 0

        # Refresh telegram bits at the start of the 59th second
        if self.count_sec == 59 and self.count_dec == 0:
            self.update_time_bits()

    def run(self, device_id=None):
        """Initializes and starts the audio stream."""
        self.update_time_bits()

        now = datetime.now(UTC) if self.utc else datetime.now()
        self.count_sec = (now.second + self.offset) % 60
        self.count_dec = int(now.microsecond // 1e5)

        # Align accurately to the next 100ms boundary
        alignment_sleep = 0.1 - (now.microsecond % 100000) / 1e6
        time.sleep(alignment_sleep)

        print('=' * 80)
        print(f"\n  DCF77 Generator Active ({self.frequency} Hz)\n")
        print("  Press Enter to terminate\n")
        print('=' * 80)

        with sd.OutputStream(device=device_id, blocksize=self.blocksize, channels=1,
                             callback=self.callback, samplerate=self.samplerate, latency='low'):
            input()

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

    # Validate output settings
    try:
        sd.check_output_settings(args.device, samplerate=args.samplerate)
        actual_samplerate = args.samplerate
    except Exception:
        actual_samplerate = sd.query_devices(args.device, 'output')['default_samplerate']
        print(f"Warning: Falling back to default sample rate: {actual_samplerate}")

    generator = DCF77Generator(
        frequency=args.frequency,
        samplerate=actual_samplerate,
        amplitude=args.amplitude,
        utc=args.utc,
        offset=args.offset
    )

    try:
        generator.run(device_id=args.device)
    except KeyboardInterrupt:
        sys.exit('\nStopped by user.')

if __name__ == "__main__":
    main()
