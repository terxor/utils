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

    parser.add_argument(
        '--parse-types',
        action='store_true',
        help="Whether to parse types (e.g. double, int) during transformation"
    )

    # Additional transforms while conversion
    parser.add_argument(
        '--tf-backtick',
        dest='transform_backtick',
        type=str,
        default=None,
        help="Comma sep list of 1-indexed cols to toggle backtick on"
    )

    # Additional transforms while conversion
    parser.add_argument(
        '--md-colors',
        dest='md_colors',
        type=str,
        default='',
        help="Comma sep list of colors. Will ignore for missing/extra cols."
    )

    args = parser.parse_args()
    input = StreamUtils.read_stream(args.input_file)
    if args.from_format == 'csv':
      table = CsvFormat(input, parse_types=args.parse_types).table
    elif args.from_format == 'md':
      table = MdFormat(input, parse_types=args.parse_types).table
    else:
      raise ValueError(f"Unsupported format: {args.from_format}")

    # TODO: Refactor to modularize data transforms
    if args.transform_backtick:
      cols = [int(x) - 1 for x in args.transform_backtick.split(',')]
      (nrows, _) = table.size()
      for i in range(nrows):
          for c in cols:
            val = table[i][c]
            if val is None:
               continue
            val = str(val)
            if val.startswith("`") and val.endswith("`"):
              res = val[1:-1]
            else:
              res = f'`{val}`'
            table[i][c] = res

    StreamUtils.write_to_stream(args.output, MdFormat(table).format(args.md_colors.split(',')) if args.to_format == 'md' else
        CsvFormat(table).format())

if __name__ == "__main__":
    main()

