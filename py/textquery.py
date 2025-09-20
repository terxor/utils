#!/usr/bin/python3

import argparse
import os
import sys
from bench.data import CsvFormat, MdFormat, StreamUtils
from bench.textquery import InMemoryDb

def parse_args():
    parser = argparse.ArgumentParser(description="tq - TextQuery over CSVs using SQLite")

    # Optional multiple --table arguments
    parser.add_argument('--table', action='append', default=[],
                        help='Specify table name(s) with --table=a:path/to/file.csv. Can be used multiple times.')

    # Optional --csv flag
    parser.add_argument('--csv', action='store_true',
                        help='Output in CSV format')

    # Optional default table name
    parser.add_argument('--default_table', type=str, default='T',
                        help='Default table name (for stdin input)')

    # Capture remaining args as-is (preserves order and content)
    parser.add_argument('query_parts', nargs=argparse.REMAINDER,
                        help='Query string and any additional arguments')

    return parser.parse_args()

def main():
    args = parse_args()

    tables = {}
    for t in args.table:
        name, path = t.split(':', 1)
        if not os.path.isfile(path):
            print(f"Error: File '{path}' not found.")
            sys.exit(1)
        
        with open(path, "r", encoding="utf-8", newline='') as f:
            lines = StreamUtils.read_stream(f)
            table = CsvFormat(lines, parse_types=True).table
            tables[name] = table

    if len(tables) == 0:
        # Use default table name for stdin input
        default_table_name = args.default_table
        lines = StreamUtils.read_stream(sys.stdin)
        table = CsvFormat(lines, parse_types=True).table
        tables[default_table_name] = table

    db = InMemoryDb(tables)
    query = ' '.join(args.query_parts)
    result_table = db.query(query)
    output = CsvFormat(result_table).format() if args.csv else MdFormat(result_table).format()
    StreamUtils.write_to_stream(sys.stdout, output)

if __name__ == "__main__":
    main()
