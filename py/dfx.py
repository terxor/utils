#!/usr/bin/python3

import sys
import argparse
from bench.data import CsvFormat, MdFormat, StreamUtils

def main():
    parser = argparse.ArgumentParser(description="Convert CSV to markdown")
    parser.add_argument('input_file', nargs='?', type=argparse.FileType('r', encoding='utf-8'),
                        default=sys.stdin,
                        help="Input Markdown file (default: stdin)")
    parser.add_argument('-o', '--output', type=argparse.FileType('w', encoding='utf-8'),
                        default=sys.stdout, help="Output CSV file (default: stdout)")

    allowed_values = ['md', 'csv']
    parser.add_argument(
        '--from',
        dest='from_format',
        choices=allowed_values,
        required=True,
        help="Source format"
    )

    parser.add_argument(
        '--to',
        dest='to_format',
        choices=allowed_values,
        required=True,
        help="Target format"
    )

    args = parser.parse_args()
    input = StreamUtils.read_stream(args.input_file)
    if args.from_format == 'csv':
      table = CsvFormat(input).table
    elif args.from_format == 'md':
      table = MdFormat(input).table
    else:
      raise ValueError(f"Unsupported format: {args.from_format}")
    StreamUtils.write_to_stream(args.output, MdFormat(table).format() if args.to_format == 'md' else
        CsvFormat(table).format())

if __name__ == "__main__":
    main()

