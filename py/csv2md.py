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
    args = parser.parse_args()

    table = DataTableConverter.from_csv_lines(read_stream(args.input_file))
    write_to_stream(args.output, DataTableConverter.to_markdown_lines(table))

if __name__ == "__main__":
    main()

