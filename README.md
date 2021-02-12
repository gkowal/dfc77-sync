# dfc77-sync
Time synchronization for DFC77 devices using sound speakers.

This program generates a realtime time DFC77 signal and sends it to the speakers. By placing any DFC77 device it should be synchronized within a few minutes.

Clearly, the funcionality depends on the sound card capabilities, which should have support for the sample rate of 192kHz, the distance between the speaker and the DFC77 device, and the lack of any interference. Place yor speaker and device far from electronic equipments, such as TVs, monitors, computers, etc.

To test the script with audible modulation change the frequency to something reasonable, e.g.:

```
python dfc77-sync.py -f 440
```

You can also play though a different device. Just experiment with options `-l` and `-d`.

Usage:

```
usage: dfc77-sync.py [-h] [-l] [-d DEVICE] [-f FREQUENCY] [-a AMPLITUDE] [-s SAMPLERATE] [-u]

 Synchronizes DFC77 devices using sound speakers.  

optional arguments:
  -h, --help            show this help message and exit
  -l, --list-devices    show list of audio devices and exit
  -d DEVICE, --device DEVICE
                        output device (numeric ID or substring)
  -f FREQUENCY, --frequency FREQUENCY
                        frequency in Hz (default: 77500 Hz)
  -a AMPLITUDE, --amplitude AMPLITUDE
                        amplitude (default: 1)
  -s SAMPLERATE, --samplerate SAMPLERATE
                        sample rate (default: 192000)
  -u, --utc             set time in UTC
```

Requirements:

 - sounddevices: https://pypi.org/project/sounddevice/

The code is inspired and based on:

- "How to manipulate a radio controlled clock via speaker" by Bastian Born: https://bastianborn.de/radio-clock-hack
- txtempus by Henner Zeller: https://github.com/hzeller/txtempus/
- DFC77 technical desciption: https://en.wikipedia.org/wiki/DCF77
