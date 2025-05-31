#!/usr/bin/python3

import csv
import sys
import argparse
from typing import List, TextIO

def csv_to_markdown_table(data: list[list[str]]) -> str:
    if not data:
        return ""

    # Calculate max width for each column
    num_cols = len(data[0])
    col_widths = [0] * num_cols

    for row in data:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    # Helper to pad cells to column width
    def pad(cell, width):
        return cell + " " * (width - len(cell))

    # Build header row
    header = data[0]
    header_row = "| " + " | ".join(pad(cell, col_widths[i]) for i, cell in enumerate(header)) + " |"

    # Build separator row with dashes (left-aligned)
    separator_row = "| " + " | ".join("-" * col_widths[i] for i in range(num_cols)) + " |"

    # Build data rows
    data_rows = []
    for row in data[1:]:
        row_str = "| " + " | ".join(pad(cell, col_widths[i]) for i, cell in enumerate(row)) + " |"
        data_rows.append(row_str)

    return "\n".join([header_row, separator_row] + data_rows)

def read_csv_from_file(file: TextIO) -> List[List[str]]:
    reader = csv.reader(file)
    return [row for row in reader]


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown table to CSV")
    parser.add_argument('input_file', nargs='?', type=argparse.FileType('r', encoding='utf-8'),
                        default=sys.stdin,
                        help="Input Markdown file (default: stdin)")
    parser.add_argument('-o', '--output', type=argparse.FileType('w', encoding='utf-8'),
                        default=sys.stdout, help="Output CSV file (default: stdout)")
    args = parser.parse_args()

    csv_data = read_csv_from_file(args.input_file)
    markdown = csv_to_markdown_table(csv_data)
    args.output.write(markdown + "\n")


if __name__ == "__main__":
    main()

