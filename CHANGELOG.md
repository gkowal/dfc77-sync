# Changelog

All notable changes to the `dcf77-sync` project will be documented in this file.

## 2026-02-17 - Unreleased

### Added

* **Dry-Run Mode**: Added `--dry-run` to print resolved runtime settings, computed `target_time`, full `time_bits` output, segmented field view, and parity verification without starting audio output.
* **Low-Pulse Amplitude Control**: Added `low_factor` to `GeneratorConfig` (default `0.15`) and exposed it via `--low-factor` for configurable DCF77 low-amplitude pulses.
* **Device Name Matching**: Extended `--device` to accept either numeric IDs or case-insensitive name substrings, with explicit handling for zero and multiple matches.
* **Protocol Bit Breakdown Helper**: Added a structured encoder helper for human-readable DCF77 time-bit field and parity diagnostics.
* **Pip Console Script**: Added a `project.scripts` entry point so pip installs a `dcf77-sync` executable (instead of requiring `python dcf77-sync.py`).
* **Startup Metadata Banner**: Added a richer realtime startup banner with tool metadata (name/version, author, license, copyright) and resolved audio/runtime parameters.
* **DCF77 Control Bits**: Added generation of control bits `A1/Z1/Z2/A2` (bits 16..19) with CET/CEST signaling based on `Europe/Berlin` time rules.

### Changed

* **DCF77 Minute Semantics**: Updated encoder target-time computation to always use the next minute boundary (`replace(second=0, microsecond=0) + 1 minute`).
* **UTC CLI Semantics**: Clarified `--utc` as a non-standard/test mode; in UTC mode the CET/CEST control indicators are not asserted.
* **Deterministic Refresh Naming**: Renamed state refresh hook to `is_minute_refresh_point()` for clearer end-of-minute intent.
* **Realtime UI Scheduling**: Moved console UI printing out of the PortAudio callback into a periodic loop in `run()` to reduce callback jitter risk.
* **Clean Shutdown Flow**: Introduced coordinated stop-event shutdown with callback-side `sd.CallbackStop`, responsive Enter/Ctrl+C handling, and clean UI thread termination.
* **Samplerate Selection Flow**: Revised CLI samplerate logic so user-requested rates are validated directly and not silently replaced by device defaults; defaults are used only when samplerate is unspecified.
* **Carrier Generation Path**: Refactored oscillator to table-driven synthesis (precomputed 1-second carrier with modulo sample index and wrapped slicing) to reduce per-callback compute.
* **Maintainability Cleanup**: Improved naming/docstrings/type hints across core modules, added a DCF77 bit-index map comment in the encoder, and introduced `is_low_pulse()` with a backward-compatible `is_silence()` alias.
* **Package Metadata Surface**: Promoted module metadata constants in `dcf77gen.__init__` to support consistent runtime/about output.

### Fixed

* **Frame-Size Robustness**: Corrected callback behavior when `frames != blocksize` by using frame-accurate time vectors (and oscillator length guard) to prevent shape mismatch and drift issues.
* **CLI Input Validation**: Tightened runtime parameter checks for amplitude range, offset bounds, and Nyquist constraints.

## 2026-02-15 - v1.0

### Added

* **Class-Based Architecture**: Migrated core signal generation and timing logic into a `DCF77Generator` class to remove global state variables.
* **Phase Continuity**: Implemented a phase accumulator in the audio callback to ensure the 77.5 kHz sine wave remains phase-continuous across buffer boundaries, preventing spectral artifacts.
* **Real-Time UI Highlighting**: Introduced `update_ui()` using ANSI escape codes to provide live visual feedback by highlighting the bit currently being modulated.
* **UI Polish**: Added a cleanup sequence (`\033[K`) on termination to wipe the active line and integrated carriage returns to refresh the transmission line in-place.
* **Python 3.12+ Compatibility**: Replaced deprecated `datetime.utcnow()` with timezone-aware `datetime.now(UTC)`.

### Changed

* **UI Layout**: Reordered the startup sequence to display the program banner before the first bitstream telegram.
* **Telegram Generation**: Added a 'silent' parameter to `update_time_bits()` for initial data calculations without console output.
* **Documentation**: Performed a comprehensive overhaul of the `README.md` to include technical specifications, protocol details, and hardware requirements.


## 2021-02-16

### Changed

* **Documentation**: General updates to `README.md`.


## 2021-02-14

### Changed

* **Signal Generation**: Reduced signal buffer to 0.1s and simplified generation using pregenerated `carrier[:]` and `silence[:]` vectors.
* **Code Cleanup**: Improved readability in `get_minute()`.


## 2021-02-13

### Added

* **Accuracy Control**: Added a command-line argument to manage the offset between the generated signal and actual system time.

### Fixed

* **Robustness**: Improved the accuracy of playback initialization and made minute-transition calculations more robust.


## 2021-02-12

### Added

* **Initial Release**: Script for time synchronization of DCF77 devices using computer speakers.
* **Documentation**: Initial `README.md` with usage instructions and technical references.
