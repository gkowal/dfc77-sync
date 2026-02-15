# Changelog

All notable changes to the `dfc77-sync` project will be documented in this file.

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