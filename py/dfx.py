#!/usr/bin/python3

import sys
import argparse
from bench.data import DataTableConverter, read_stream, write_to_stream

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
    if args.from_format == 'csv':
      table = DataTableConverter.from_csv_lines(read_stream(args.input_file))
    elif args.from_format == 'md':
      table = DataTableConverter.from_markdown_lines(read_stream(args.input_file))
    else:
      raise ValueError(f"Unsupported format: {args.from_format}")
    write_to_stream(args.output, DataTableConverter.to_markdown_lines(table) if args.to_format == 'md' else
        DataTableConverter.to_csv_lines(table))

if __name__ == "__main__":
    main()

