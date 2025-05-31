#!/usr/bin/python3

import sys
import pytz
from datetime import datetime, timezone
from typing import Dict, Tuple, List
import argparse

DEFAULT_TZ = 'UTC'

def parse_args():
    parser = argparse.ArgumentParser(
        description="Time utility to convert and display time in multiple formats and timezones."
    )

    parser.add_argument(
        "time_value",
        nargs="?",
        default=None,
        help="Time input (e.g., epoch, '2025-05-26 23:34', '2025-05-26T23:34:40.123')"
    )

    parser.add_argument(
        "timezone",
        nargs="?",
        default=None,
        help="Optional source timezone label (default: UTC). Example: IST, PST"
    )

    return parser.parse_args()

class TimeOutput:

    def __init__(self, dt: datetime, tz_map: Dict[str, str]):
        """
        dt: tz-aware datetime (ideally UTC)
        tz_list: list of timezone labels to output, e.g. ['UTC', 'IST', 'PST']
        tz_map: dict mapping labels to pytz timezone names, e.g. {'IST': 'Asia/Kolkata'}
        """
        if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
            raise ValueError("datetime object must be timezone-aware")

        # Normalize to UTC
        dt_utc = dt.astimezone(pytz.UTC)

        timestamp = dt_utc.timestamp()
        self.epoch_seconds = int(timestamp)
        self.epoch_millis = int(timestamp * 1_000)
        self.epoch_micros = int(timestamp * 1_000_000)

        self.tz_times: Dict[str, Tuple[str, str, str]] = {}

        fmt_lambdas = [
                lambda d: ('standard', d.strftime("%Y-%m-%d %H:%M:%S")),
                lambda d: ('micros', d.strftime("%Y-%m-%d %H:%M:%S.%f")),
                lambda d: ('iso', d.strftime("%Y-%m-%dT%H:%M:%S%z")),
        ]
        self.num_fmt = len(fmt_lambdas)
        self.fmt_names = [f(dt_utc)[0] for f in fmt_lambdas]

        for key, pytz_name in tz_map.items():
            tz = pytz.timezone(pytz_name)
            dt_tz = dt_utc.astimezone(tz)

            self.tz_times[key] = [f(dt_tz)[1] for f in fmt_lambdas]

    def __repr__(self):
        return (
            f"TimeOutput(epoch_seconds={self.epoch_seconds}, "
            f"epoch_millis={self.epoch_millis}, epoch_micros={self.epoch_micros}, "
            f"tz_times={self.tz_times})"
        )

    def __eq__(self, other):
        if not isinstance(other, TimeOutput):
            return False
        return (
            self.epoch_seconds == other.epoch_seconds and
            self.epoch_millis == other.epoch_millis and
            self.epoch_micros == other.epoch_micros and
            self.tz_times == other.tz_times
        )



# Mapping of friendly labels to pytz timezone names
LABEL_TO_PYTZ = {
    DEFAULT_TZ: DEFAULT_TZ,
    'IST': 'Asia/Kolkata',
    'PST': 'America/Los_Angeles'
}

# Acceptable input datetime string formats
DATETIME_INPUT_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S%z",
]

def print_time_output(time_output):
    # 3 columns: category, subcategory, value
    rows = []
    rows.append(['Category', 'Type', 'Value'])

    rows.append(['Epoch', 'seconds', str(time_output.epoch_seconds)])
    rows.append(['', 'ms', str(time_output.epoch_millis)])
    rows.append(['', 'micros', str(time_output.epoch_micros)])

    for label in time_output.tz_times.keys():
        first = True
        rows.append(['' for i in range(3)])
        for i in range(time_output.num_fmt):
            rows.append([
                (label if first else ''),
                time_output.fmt_names[i],
                time_output.tz_times[label][i]
                ])
            first = False
    for r in rows:
        print(*r, sep=',')
    # print(format_table(rows))

def detect_epoch_precision(value: int) -> datetime:
    MIN_VALID_EPOCH = 10000000

    if value < MIN_VALID_EPOCH:
        raise ValueError("Epoch timestamp too small to be valid. Did you mean a year?")

    if value < 1e12:
        return datetime.fromtimestamp(value, tz=timezone.utc)  # seconds
    elif value < 1e15:
        return datetime.fromtimestamp(value / 1e3, tz=timezone.utc)  # milliseconds
    elif value < 1e18:
        return datetime.fromtimestamp(value / 1e6, tz=timezone.utc)  # microseconds
    else:
        return datetime.fromtimestamp(value / 1e9, tz=timezone.utc)  # nanoseconds

def parse_time_input(value: str) -> datetime:

    # Try detailed datetime formats
    for fmt in DATETIME_INPUT_FORMATS:
        try:
            dt = datetime.strptime(value, fmt)
            return dt
            # if dt.tzinfo is None:
            #     dt = dt.replace(tzinfo=timezone.utc)
            # return dt.astimezone(timezone.utc)
        except ValueError:
            continue

    # Fallback for partial dates
    fallback_formats = [
        ("%Y-%m-%d", "%Y-%m-%d 00:00:00"),
        ("%Y-%m", "%Y-%m-01 00:00:00"),
        ("%Y", "%Y-01-01 00:00:00"),
    ]
    for test_fmt, full_fmt_str in fallback_formats:
        try:
            datetime.strptime(value, test_fmt)  # Confirm format
            padded = datetime.strptime(datetime.strptime(value, test_fmt).strftime(full_fmt_str), "%Y-%m-%d %H:%M:%S")
            # padded = padded.replace(tzinfo=timezone.utc)
            return padded
        except ValueError:
            continue

    raise ValueError("Could not parse datetime input.")


def format_table(rows):
    non_empty_rows = [row for row in rows if row]
    col_widths = [max(len(str(cell)) for cell in col) for col in zip(*non_empty_rows)]

    def format_row(row):
        if len(row) > 0:
            return ' = '.join(f'{cell:<{w}}' for cell, w in zip(row, col_widths))
        return ''

    result = []

    for row in rows:
        result.append(format_row(row))

    return '\n'.join(result)

def parse_time (time_input=None, tz=None):
    if not time_input:
        timezone = pytz.timezone(DEFAULT_TZ)
        return TimeOutput(datetime.now(timezone), LABEL_TO_PYTZ)
    # print(f'Time=|{time_input}|')
    try:
        # tz is ignored here
        # Try parsing as epoch integer
        epoch = float(time_input)
        dt = detect_epoch_precision(epoch)
        return TimeOutput(dt, LABEL_TO_PYTZ)
    except ValueError:
        pass

    if tz is None:
        tz = DEFAULT_TZ
    dt = parse_time_input(time_input)
    if tz not in LABEL_TO_PYTZ:
        raise ValueError(f"Unknown timezone label: {source_tz_label}")
    timezone = pytz.timezone(LABEL_TO_PYTZ[tz])
    dt = timezone.localize(dt)
    return TimeOutput(dt, LABEL_TO_PYTZ)

def main(args):
    try:
        args = parse_args()
        output = parse_time(args.time_value, args.timezone)
        print_time_output(output)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main(sys.argv[1:])
