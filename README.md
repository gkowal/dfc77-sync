# dfc77-sync

**dfc77-sync** is a Python-based software-defined signal generator designed to synchronize DCF77-compatible radio-controlled clocks using standard computer audio hardware. By utilizing high-sample-rate Digital-to-Analog Converters (DACs), the script emulates the 77.5 kHz longwave signal typically broadcast from Mainflingen, Germany.

## Program Overview

The program generates a modulated carrier wave through the system's speakers. When a DCF77 device is placed in close proximity to the speaker’s voice coil, the inductive coupling allows the device's internal ferrite antenna to pick up the emulated signal.

This tool is particularly useful for synchronizing clocks in environments with poor longwave reception or for testing DCF77 receivers in regions outside the broadcast range.

## The DCF77 Standard

The DCF77 signal is a transition-keyed amplitude-modulated signal with the following characteristics:

* **Carrier Frequency:** 77.5 kHz.
* **Modulation:** Pulse-width modulation (PWM) via amplitude reduction.
* **Data Rate:** 1 bit per second.
* **Bit Encoding:**
  * **Logic 0:** Amplitude reduction for 100 ms at the start of the second.
  * **Logic 1:** Amplitude reduction for 200 ms at the start of the second.
* **Framing:** A complete time code is transmitted over 59 seconds, with the 60th second omitted to serve as a minute marker.

## Requirements

### Software

* **Python 3.x**
* **NumPy:** Used for efficient signal synthesis and buffer management.
* **sounddevice:** Provides the interface to the system's audio backend (PortAudio).

### Hardware

* **High-Sample-Rate DAC:** To generate a 77.5 kHz signal, the audio hardware must support a sample rate of at least **192 kHz** to satisfy the Nyquist-Shannon sampling theorem.
* **Unshielded Speakers:** Passive or active speakers without magnetic shielding are preferred to maximize inductive coupling with the target device.

## Command Line Options

The script provides several parameters to fine-tune the signal generation based on your hardware environment:

| Option | Description |
| --- | --- |
| `-h, --help` | Displays the help message and exits. |
| `-l, --list-devices` | Enumerates available audio output devices and their IDs. |
| `-d, --device` | Specifies the output device by numeric ID or substring. |
| `-f, --frequency` | Sets the carrier frequency in Hz (Default: 77500 Hz). |
| `-a, --amplitude` | Adjusts the signal gain (Default: 1.0). |
| `-o, --offset` | Introduces a manual second offset to compensate for system latency. |
| `-s, --samplerate` | Forces a specific sample rate in Hz (Default: 192000 Hz). |
| `-u, --utc` | Encodes the DCF77 telegram using UTC instead of the local system time. |

## Usage Examples

### Standard Synchronization

Generate the default 77.5 kHz signal using the default output device:

```bash
python dfc77-sync.py
```

### Testing with Audible Frequencies

To verify the modulation logic is working, you can shift the carrier into the audible range (e.g., 440 Hz):

```bash
python dfc77-sync.py -f 440
```

### Specifying a High-Resolution DAC

If you have an external DAC identified as device index 2 that supports 192 kHz:

```bash
python dfc77-sync.py -d 2 -s 192000
```

## Technical References

* **DCF77 Technical Description:** [Physikalisch-Technische Bundesanstalt (PTB)](https://www.ptb.de/cms/en/ptb/fachabteilungen/abt4/fb-44/ag-442/dissemination-of-legal-time/dcf77.html)
* **Signal Theory:** [Wikipedia: DCF77](https://en.wikipedia.org/wiki/DCF77)
* **Inspired By:**
  * Bastian Born: ["How to manipulate a radio controlled clock via speaker"](https://bastianborn.de/radio-clock-hack)
  * Henner Zeller: [txtempus](https://github.com/hzeller/txtempus/)
