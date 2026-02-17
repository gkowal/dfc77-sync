from __future__ import annotations


def is_silence(count_sec: int, count_dec: int, time_bits: int) -> bool:
    """
    Matches:

        is_silence = False
        if count_sec < 59:
            if count_dec == 0 or (count_dec == 1 and (time_bits >> count_sec) & 1):
                is_silence = True
    """
    if count_sec < 59:
        if count_dec == 0:
            return True
        if count_dec == 1 and ((time_bits >> count_sec) & 1):
            return True
    return False