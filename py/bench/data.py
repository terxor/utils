from typing import List, Optional, Union
from typing import TextIO
import re

Primitive = Union[bool, int, float, str, type(None)]

class DataTable:
    def __init__(self, num_columns: int, headers: List[Optional[str]] = None):
        if num_columns <= 0:
            raise ValueError("Number of columns must be positive.")
        
        self.num_columns = num_columns

        if headers is None:
            self.headers = [f"col{i+1}" for i in range(num_columns)]
        else:
            if len(headers) != num_columns:
                raise ValueError("Length of headers must match number of columns.")
            self.headers = [
                h if h is not None else f"col{i+1}"
                for i, h in enumerate(headers)
            ]

        if len(self.headers) != num_columns:
            raise ValueError("Length of headers must match number of columns.")

        self._data: List[List[Primitive]] = []

    def size(self):
        """Returns (rows, columns)"""
        return (len(self._data), self.num_columns)

    def data(self):
        """Returns the internal data as read-only"""
        return [row.copy() for row in self._data]

    def add_row(self, row: List[Primitive]):
        """Adds a row to the data table after validation"""
        if len(row) != self.num_columns:
            raise ValueError(f"Row length of {row} does not match number of columns (headers: {self.headers}).")
        for item in row:
            if not isinstance(item, (bool, int, float, str, type(None))):
                raise TypeError(f"Unsupported data type: {type(item)}")
        self._data.append(row)

    def to_records(self):
        res = []
        for row in self._data:
            record = {}
            for i in range(self.num_columns):
                record[self.headers[i]] = row[i]
            res.append(record)
        return res

    def __getitem__(self, index):
        """Allows table[i][j] access via table[i][j] -> table[i][j]"""
        return self._data[index]

    def __str__(self):
        """Returns a string representation of the table"""
        output = '\t'.join(self.headers) + '\n'
        for row in self._data:
            output += '\t'.join(str(item) for item in row) + '\n'
        return output.strip()

class StreamUtils:
    @staticmethod
    def read_stream(stream: TextIO) -> List[str]:
        return stream.read().splitlines()

    @staticmethod
    def write_to_stream(stream: TextIO, lines: List[str]):
        lines_with_newlines = [f"{line}\n" for line in lines]
        stream.writelines(lines_with_newlines)

from abc import ABC, abstractmethod
from typing import List, Union
from bench.data import DataTable

class DataFormat(ABC):
    def __init__(self, data: Union[DataTable, List[str]]):
        if isinstance(data, DataTable):
            self.table = data
        elif isinstance(data, list):
            self.table = self._parse_raw(data)
        else:
            raise TypeError("Expected DataTable or list of strings")

    def _parse_raw(self, lines: List[str]) -> DataTable:
        header = self._parse_single_line(self._get_header_line(lines))
        table = DataTable(len(header), header)
        for line in self._get_data_lines(lines):
            table.add_row(
                [Parser.parse_value(field) for field in self._parse_single_line(line)]
            )
        return table

    @abstractmethod
    def _get_header_line(self, lines: List[str]) -> str:
        pass

    @abstractmethod
    def _get_data_lines(self, lines: List[str]) -> List[str]:
        pass

    @abstractmethod
    def _parse_single_line(self, line: str) -> List[Optional[str]]:
        pass

    @abstractmethod
    def format(self) -> List[str]:
        """Format the data into the specific format (e.g. CSV, Markdown)."""
        pass

    @staticmethod
    def _val_to_str(val: Primitive) -> str:
        if val is None:
            return ""
        elif isinstance(val, bool):
            return "true" if val else "false"
        elif isinstance(val, float):
            return f"{val:.6g}"
        return str(val)

class CsvFormat(DataFormat):
    def _get_header_line(self, lines: List[str]) -> str:
        if len(lines) == 0:
            raise ValueError("Empty CSV input.")
        return lines[0]
    
    def _get_data_lines(self, lines: List[str]) -> List[str]:
        return lines[1:]

    def format(self) -> List[str]:
        def to_csv_line(row: List[Primitive]) -> str:
            return ','.join([DataFormat._val_to_str(cell) for cell in row])

        lines = [to_csv_line(self.table.headers)]
        for row in self.table.data():
            lines.append(to_csv_line(row))
        return lines

    def _parse_single_line(self, line: str) -> List[Optional[str]]:
        """Parse one CSV line handling:
        - quoted fields (with commas or escaped quotes)
        - `""` → empty string
        - empty field (bare comma) → None
        """
        def strip_surrounding_quotes(s: str) -> str:
            if len(s) >= 2 and s[0] == s[-1] and s[0] == '"':
                return s[1:-1]
            return s

        def finalize_field(line: str, start: int, end: int) -> Optional[str]:
            s = line[start:end].strip()
            if len(s) == 0:
                return None
            s = strip_surrounding_quotes(s)
            return s.replace('""', '"')  # Replace escaped quotes with single quotes

        fields: List[Optional[str]] = []
        in_quote = False
        start_index = 0
        i = 0
        while i < len(line):
            char = line[i]

            if char == '"':
                if in_quote:
                    if i + 1 < len(line) and line[i + 1] == '"':
                        i += 1
                    else:
                        in_quote = False
                else:
                    in_quote = True
            elif char == ',' and not in_quote:
                fields.append(finalize_field(line, start_index, i))
                start_index = i + 1
            i += 1
        fields.append(finalize_field(line, start_index, i))
        return fields

class MdFormat(DataFormat):
    def _get_header_line(self, lines: List[str]) -> str:
        if len(lines) == 0:
            raise ValueError("Empty MD input.")
        return lines[0]
    
    def _get_data_lines(self, lines: List[str]) -> List[str]:
        if len(lines) < 2:
            raise ValueError("Invalid markdown input.")
        return lines[2:]

    def format(self, colors=None) -> List[str]:
        # Get headers and data rows from the DataTable object
        table = self.table
        headers = table.headers
        data_rows = table.data()
        num_cols = table.num_columns

        # Calculate max width for each column
        # Initialize with header widths
        col_widths = [max(3, len(header)) for header in headers]

        # Precompute stringified rows
        str_rows = [
            [self._val_to_str(cell) for cell in row]
            for row in data_rows
        ]

        # Update widths based on actual data rows
        for row in str_rows:
            for i, cell in enumerate(row):
                # Ensure cell is converted to string for length calculation
                col_widths[i] = max(col_widths[i], len(cell))

        # Helper to pad cells to column width
        def pad(cell: str, width: int, color = None) -> str:
            content = cell
            if color is not None:
                content = TermColor.colorize(cell, color)
            return content + " " * (width - len(cell))

        # Build header row
        header_row = "| " + " | ".join(pad(cell, col_widths[i]) for i, cell in enumerate(headers)) + " |"

        # Build separator row with dashes (left-aligned, matching column width)
        separator_row = "| " + " | ".join("-" * col_widths[i] for i in range(num_cols)) + " |"

        # Build data rows
        lines = [header_row, separator_row]
        for row in str_rows:
            row_str = "| " + " | ".join(pad(cell, col_widths[i], colors[i] if colors is not None and i < len(colors) else None) for i, cell in enumerate(row)) + " |"
            lines.append(row_str)
        return lines
    
    def _parse_single_line(self, line: str) -> List[Optional[str]]:
        """
        Parse one Markdown table row, e.g.:

            "| Alice | 30 | |"`

        → ["Alice", "30", None]
        """
        # 1) Strip leading/trailing pipe and any surrounding spaces
        trimmed = line.strip()
        if trimmed.startswith('|'):
            trimmed = trimmed[1:]
        if trimmed.endswith('|'):
            trimmed = trimmed[:-1]


        # 2) Split using regex that matches unescaped pipes only
        pattern = r'(?<!\\)\|'
        raw_cells = re.split(pattern, trimmed)

        # 3) Replace escaped pipes and strip outer spaces
        def clean(cell: str) -> Optional[str]:
            cell = cell.strip()
            cell = cell.replace(r'\|', '|')
            return None if cell == '' else cell

        return [clean(cell) for cell in raw_cells]

class Parser:
    @staticmethod
    def parse_value(value: Optional[str]) -> Primitive:
        if value is None or not isinstance(value, str):
            return None
        
        if value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        
        if Parser._is_integer(value):
            return int(value)
        
        if Parser._is_made_of_float_chars(value):
            try:
                return float(value)
            except ValueError:
                pass
        
        return value  # Fallback to string if not boolean, integer, or float

    @staticmethod
    def _is_integer(s: str) -> bool:
        s = s.strip()
        if not s:
            return False
        if s[0] in '+-':
            s = s[1:]
        return s.isdigit()

    @staticmethod
    def _is_made_of_float_chars(s: str) -> bool:
        allowed = {'+', '-', '.', 'e', 'E'}
        return all(c.isdigit() or c in allowed for c in s)

class TermColor:
    # Class-level color map using ANSI escape codes
    COLOR_MAP = {
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'bright_black': '\033[90m',
        'bright_red': '\033[91m',
        'bright_green': '\033[92m',
        'bright_yellow': '\033[93m',
        'bright_blue': '\033[94m',
        'bright_magenta': '\033[95m',
        'bright_cyan': '\033[96m',
        'bright_white': '\033[97m',
        'reset': '\033[0m',
    }

    @staticmethod
    def colorize(content: str, color = None) -> str:
        """
        Returns the content string wrapped in the given color.
        If color is not found, returns the content unchanged.
        """
        if color is None:
            return content
        color_code = TermColor.COLOR_MAP.get(color.lower())
        reset_code = TermColor.COLOR_MAP['reset']
        if color_code:
            return f"{color_code}{content}{reset_code}"
        else:
            return content  # Fallback if color not found
