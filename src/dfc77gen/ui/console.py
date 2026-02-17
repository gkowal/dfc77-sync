from __future__ import annotations

from datetime import datetime, UTC

from dfc77gen.core.state import GeneratorState


def render_status_line(state: GeneratorState) -> str:
    b = ("{:059b}".format(state.time_bits))[::-1]
    slices = [
        (0, 1), (1, 15), (15, 20), (20, 21), (21, 28), (28, 29),
        (29, 35), (35, 36), (36, 42), (42, 45), (45, 50), (50, 58), (58, 59),
    ]

    INV, RST = "\033[7m", "\033[0m"
    output_segments = []
    bit_idx = 0
    for start, end in slices:
        seg_str = ""
        for i in range(start, end):
            seg_str += f"{INV}{b[i]}{RST}" if bit_idx == state.count_sec else b[i]
            bit_idx += 1
        output_segments.append(seg_str)

    line = (
        f"{output_segments[0]} {output_segments[1]} {output_segments[2]} "
        f"{output_segments[3]} {output_segments[4]}.{output_segments[5]} "
        f"{output_segments[6]}.{output_segments[7]} {output_segments[8]} "
        f"{output_segments[9]} {output_segments[10]} {output_segments[11]}.{output_segments[12]} X"
    )
    return line


def print_ui(state: GeneratorState, use_utc: bool) -> None:
    now = datetime.now(UTC) if use_utc else datetime.now()
    line = render_status_line(state)
    print(f"\r{now.strftime('%Y-%m-%d %H:%M:%S')} -> {line}", end="", flush=True)