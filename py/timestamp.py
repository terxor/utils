#!/usr/bin/python3

import sys
import argparse
from bench.timestamp import parse_time, convert_time_output_to_data_table
from bench.data import MdFormat, CsvFormat, StreamUtils

def main(args):
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

    parser.add_argument('--csv', action='store_true', help='Output in CSV format')
    parser.add_argument('--quick', action='store_true', help='Only output UTC time in standard format')

    args = parser.parse_args()
    time_output = parse_time(args.time_value, args.timezone)

    table = convert_time_output_to_data_table(time_output)
    if args.quick:
        for row in table.data():
            if row[0] == 'UTC' and row[1] == 'standard':
                print(row[2])
                return
        raise ValueError("No UTC standard time found in the output.")

    if args.csv:
        output_lines = CsvFormat(table).format()
    else:
        output_lines = MdFormat(table).format()

    args = parser.parse_args()
    time_output = parse_time(args.time_value, args.timezone)
    table = convert_time_output_to_data_table(time_output)
    if args.csv:
        output_lines = CsvFormat(table).format()
    else:
        output_lines = MdFormat(table).format()
    StreamUtils.write_to_stream(sys.stdout, output_lines)

if __name__ == '__main__':
    main(sys.argv[1:])
