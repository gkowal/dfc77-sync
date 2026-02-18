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

* **Python 3.10+**
* **NumPy:** Used for efficient signal synthesis and buffer management.
* **sounddevice:** Provides the interface to the system's audio backend (PortAudio).

## Installation

From the repository root:

```bash
python -m pip install --user .
```

This installs the package and creates a `dfc77-sync` executable in your user scripts directory (typically `~/.local/bin` on Linux).

For development (editable install):

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

If `dfc77-sync` is not found after user install, add `~/.local/bin` to your `PATH`.

### Hardware

* **High-Sample-Rate DAC:** To generate a 77.5 kHz signal, the audio hardware must support a sample rate of at least **192 kHz** to satisfy the Nyquist-Shannon sampling theorem.
* **Unshielded Speakers:** Passive or active speakers without magnetic shielding are preferred to maximize inductive coupling with the target device.

## Command Line Options

The script provides several parameters to fine-tune the signal generation based on your hardware environment:

| Option | Description |
| --- | --- |
| `-h, --help` | Displays the help message and exits. |
| `-l, --list-devices` | Enumerates available audio output devices and their IDs. |
| `-d, --device` | Output device selector. Accepts numeric ID or case-insensitive name substring. |
| `-f, --frequency` | Sets the carrier frequency in Hz (Default: 77500 Hz). |
| `-a, --amplitude` | Carrier amplitude. Valid range: `(0, 1.0]` (Default: `1.0`). |
| `--low-factor` | Relative amplitude during DCF77 low pulse. Valid range: `[0, 1]` (Default: `0.15`). |
| `-o, --offset` | Introduces a manual second offset to compensate for system latency. |
| `-s, --samplerate` | Forces a specific sample rate in Hz. If omitted, device default is used. |
| `-u, --utc` | Encodes the DCF77 telegram using UTC instead of the local system time. |
| `--dry-run` | Prints encoding diagnostics and exits without starting audio output. |

Validation notes:

* `offset` must be in `0..59`.
* `frequency` must be below Nyquist (`samplerate / 2`).
* If `--samplerate` is explicitly provided and unsupported by the selected device, the program exits with an error (no silent fallback).

## Usage Examples

### Standard Synchronization

Generate the default 77.5 kHz signal using the default output device:

```bash
dfc77-sync
```

### Testing with Audible Frequencies

To verify the modulation logic is working, you can shift the carrier into the audible range (e.g., 440 Hz):

```bash
dfc77-sync -f 440
```

### Selecting Device by Name (Recommended)

Device IDs can change across reboots/sessions. Name matching is often more stable:

```bash
dfc77-sync -d "ALC1220" -s 192000
```

If the substring matches multiple outputs, the CLI prints candidates and exits without guessing.

### Dry Run (No Audio Initialization)

Inspect computed DCF77 bits/parity and `target_time` without opening an output stream:

```bash
dfc77-sync --dry-run -u
```

### Specifying a High-Resolution DAC by ID

If you have an external DAC identified as device index 2 that supports 192 kHz:

```bash
dfc77-sync -d 2 -s 192000
```

## Runtime and Internal Notes

Recent implementation updates:

* Encoder now follows DCF77 semantics and always encodes the **next minute boundary**.
* Time-bit refresh occurs at an explicit deterministic minute refresh point (`sec=59`, `deci=0`).
* Console UI updates run outside the PortAudio callback (periodic thread), reducing underrun/jitter risk.
* Shutdown is coordinated via a shared stop event and `sd.CallbackStop` for clean stream termination.
* Oscillator is table-driven (precomputed 1-second carrier) with wrapped slicing for lower callback CPU load.
* Callback logic handles variable `frames` robustly.
* `--dry-run` provides structured bit-field and parity diagnostics for protocol verification.
* Startup banner now includes tool/version metadata, author/license/copyright, resolved output device, samplerate, carrier frequency, amplitude, and low-pulse factor.

## Technical References

* **DCF77 Technical Description:** [Physikalisch-Technische Bundesanstalt (PTB)](https://www.ptb.de/cms/en/ptb/fachabteilungen/abt4/fb-44/ag-442/dissemination-of-legal-time/dcf77.html)
* **Signal Theory:** [Wikipedia: DCF77](https://en.wikipedia.org/wiki/DCF77)
* **Inspired By:**
  * Bastian Born: ["How to manipulate a radio controlled clock via speaker"](https://bastianborn.de/radio-clock-hack)
  * Henner Zeller: [txtempus](https://github.com/hzeller/txtempus/)
