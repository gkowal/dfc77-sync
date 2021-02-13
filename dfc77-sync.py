#!/usr/bin/env python3
#
""" Synchronizes DFC77 devices using sound speakers.  """

from datetime import datetime, timedelta
import argparse
import numpy as np
import sounddevice as sd
import sys
import time

def to_bcd(n):
    return ((int(n) // 10) % 10 << 4) | (n % 10)

def parity(n, l, u):
    r = 0
    for i in range(l, u+1):
        b = 1 << i
        if n & b == b:
            r += 1
    return r & 1

def get_minute(utc=False):
    if utc:
        now = datetime.utcnow()
    else:
        now = datetime.now()
    if now.second < 10:
        now = now + timedelta(minutes=1)
    else:
        now = now + timedelta(minutes=2)
    time_bits = 0
    time_bits |= 1 << 20
    time_bits |= to_bcd(now.minute)        << 21
    time_bits |= to_bcd(now.hour)          << 29
    time_bits |= to_bcd(now.day)           << 36
    time_bits |= to_bcd(now.isoweekday())  << 42
    time_bits |= to_bcd(now.month)         << 45
    time_bits |= to_bcd(now.year % 100)    << 50

    time_bits |= parity(time_bits, 21, 27) << 28
    time_bits |= parity(time_bits, 29, 34) << 35
    time_bits |= parity(time_bits, 36, 57) << 58
    bits = ('{:059b}'.format(time_bits))[::-1]
    print("{} -> {} {} {} {} {}.{} {}.{} {} {} {} {}.{} X".format(now, bits[0], bits[1:15], bits[15:20], bits[20], bits[21:28], bits[28], bits[29:35], bits[35], bits[36:42], bits[42:45], bits[45:50], bits[50:58], bits[58]))
    return time_bits

def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='output device (numeric ID or substring)')
parser.add_argument(
    '-f', '--frequency', type=float, default=77500,
    help='frequency in Hz (default: %(default)s Hz)')
parser.add_argument(
    '-a', '--amplitude', type=float, default=1,
    help='amplitude (default: %(default)s)')
parser.add_argument(
    '-s', '--samplerate', type=float, default=192000,
    help='sample rate (default: %(default)s)')
parser.add_argument(
    '-u', '--utc', action='store_true',
    help='set time in UTC')
args = parser.parse_args(remaining)

print('=' * 80)
print('')
print('  DFC77-sync - a tool to synchronize DFC77 devices using sound speakers')
print('')
print('    For command line options use: dfc77-sync.py -h')
print('')
print('    Press Return to quit')
print('')
print('=' * 80)

try:
    sd.check_output_settings(args.device, samplerate=args.samplerate)
    samplerate = args.samplerate
except Exception:
    samplerate = sd.query_devices(args.device, 'output')['default_samplerate']

blocksize = int(samplerate)

time_bits = get_minute(args.utc)
if args.utc:
    now = datetime.utcnow()
else:
    now = datetime.now()
start_sec = (now.second + 2) % 60
start_idx = 0

time.sleep((1e6 - now.microsecond) / 1e6)

try:

    def callback(outdata, frames, time, status):
        if status:
            print(status, file=sys.stderr)

        global start_idx, start_sec, time_bits

        t = (start_idx + np.arange(frames)) / samplerate
        t = t.reshape(-1, 1)

        outdata[:] = args.amplitude * np.sin(2 * np.pi * args.frequency * t)

        if start_sec < 59:
            b = 1 << start_sec
            if time_bits & b == b:
                i = np.where((t - np.floor(t)) < 0.2)
                if i[0].size > 0:
                    outdata[i] *= 0
            else:
                i = np.where((t - np.floor(t)) < 0.1)
                if i[0].size > 0:
                    outdata[i] *= 0
        else:
            time_bits = get_minute(args.utc)

        start_idx += frames
        start_sec += 1

        if start_sec >= 60:
            start_sec = 0

    with sd.OutputStream(device=args.device, blocksize=blocksize, channels=1, callback=callback,
                         latency='low', samplerate=samplerate):
        input()

except KeyboardInterrupt:
    parser.exit('')

except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
