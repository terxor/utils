import sys
import argparse
import csv
from typing import List, TextIO


def markdown_to_csv_table(md_lines: List[str]) -> List[List[str]]:
    """
    Convert markdown table lines to a list of rows (each row is a list of strings).
    Expects well-formed markdown table with header, separator, and data rows.
    """
    # Remove empty lines and strip
    md_lines = [line.strip() for line in md_lines if line.strip()]

    if len(md_lines) < 2:
        return []  # Not a valid markdown table

    # The separator line is usually the second line, e.g. | --- | --- |
    # So we skip the second line
    data_lines = md_lines[:1] + md_lines[2:]

    rows = []
    for line in data_lines:
        # Remove leading and trailing pipe and split on pipes
        if not line.startswith('|') or not line.endswith('|'):
            continue  # Skip lines that don't look like table rows

        row = [cell.strip() for cell in line.strip('|').split('|')]
        rows.append(row)

    return rows


def read_md_from_file(file: TextIO) -> List[str]:
    return file.readlines()


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown table to CSV")
    parser.add_argument('input_file', nargs='?', type=argparse.FileType('r', encoding='utf-8'),
                        default=sys.stdin,
                        help="Input Markdown file (default: stdin)")
    parser.add_argument('-o', '--output', type=argparse.FileType('w', encoding='utf-8'),
                        default=sys.stdout, help="Output CSV file (default: stdout)")
    args = parser.parse_args()

    md_lines = read_md_from_file(args.input_file)
    csv_data = markdown_to_csv_table(md_lines)

    writer = csv.writer(args.output)
    writer.writerows(csv_data)


if __name__ == "__main__":
    main()

