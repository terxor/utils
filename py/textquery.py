#!/usr/bin/python3

import argparse
import os
import sys
from bench.data import DataTableConverter, write_to_stream, read_stream
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
            lines = read_stream(f)
            table = DataTableConverter.from_csv_lines(lines)
            tables[name] = table

    if len(tables) == 0:
        # Use default table name for stdin input
        default_table_name = args.default_table
        lines = read_stream(sys.stdin)
        table = DataTableConverter.from_csv_lines(lines)
        tables[default_table_name] = table

    db = InMemoryDb(tables)
    query = ' '.join(args.query_parts)
    result_table = db.query(query)
    if args.csv:
        write_to_stream(sys.stdout, DataTableConverter.to_csv_lines(result_table))
    else:
        write_to_stream(sys.stdout, DataTableConverter.to_markdown_lines(result_table))

if __name__ == "__main__":
    main()
