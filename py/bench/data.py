from enum import Enum
from typing import List, Optional, Union
from typing import TextIO

class DataType(Enum):
    BOOL = 1
    INT = 2
    FLOAT = 3
    STR = 4
    NULL = 5

Primitive = Union[bool, int, float, str]

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

    def __getitem__(self, index):
        """Allows table[i][j] access via table[i][j] -> table[i][j]"""
        return self._data[index]

    def __str__(self):
        """Returns a string representation of the table"""
        output = '\t'.join(self.headers) + '\n'
        for row in self._data:
            output += '\t'.join(str(item) for item in row) + '\n'
        return output.strip()


class DataTableConverter:
    @staticmethod
    def to_csv_lines(table: DataTable) -> List[str]:
        lines = [DataTableConverter._to_csv_line(table.headers)]
        for row in table.data():
            lines.append(DataTableConverter._to_csv_line(row))
        return lines

    @staticmethod
    def from_csv_lines(lines: List[str]) -> DataTable:
        if len(lines) == 0:
            raise ValueError("Empty CSV input.")
        headers = DataTableConverter._parse_csv_line(lines[0])
        table = DataTable(len(headers), headers)
        for i in range(1, len(lines)):
            raw = DataTableConverter._parse_csv_line(lines[i])
            table.add_row([DataTableConverter._parse_cell(field) for field in raw])
        return table

    @staticmethod
    def to_markdown_lines(table: DataTable) -> List[str]:
        # Get headers and data rows from the DataTable object
        headers = table.headers
        data_rows = table.data()
        num_cols = table.num_columns

        # Calculate max width for each column
        # Initialize with header widths
        col_widths = [max(3, len(header)) for header in headers]

        # Precompute stringified rows
        str_rows = [
            [DataTableConverter._val_to_str(cell) for cell in row]
            for row in data_rows
        ]

        # Update widths based on actual data rows
        for row in str_rows:
            for i, cell in enumerate(row):
                # Ensure cell is converted to string for length calculation
                col_widths[i] = max(col_widths[i], len(cell))

        # Helper to pad cells to column width
        def pad(cell: str, width: int) -> str:
            return cell + " " * (width - len(cell))

        # Build header row
        header_row = "| " + " | ".join(pad(cell, col_widths[i]) for i, cell in enumerate(headers)) + " |"

        # Build separator row with dashes (left-aligned, matching column width)
        separator_row = "| " + " | ".join("-" * col_widths[i] for i in range(num_cols)) + " |"

        # Build data rows
        lines = [header_row, separator_row]
        for row in str_rows:
            row_str = "| " + " | ".join(pad(cell, col_widths[i]) for i, cell in enumerate(row)) + " |"
            lines.append(row_str)
        return lines

    @staticmethod
    def _val_to_str(val: Primitive) -> str:
        if val is None:
            return ""
        elif isinstance(val, bool):
            return "true" if val else "false"
        return str(val)

    @staticmethod
    def from_markdown_lines(lines: List[str]) -> DataTable:
        if len(lines) < 2:
            raise ValueError("Invalid markdown input.")
        headers = [cell.strip() for cell in lines[0].split('|')[1:-1]]
        table = DataTable(len(headers), headers)
        for line in lines[2:]:
            raw = DataTableConverter._parse_md_line(line)
            table.add_row([DataTableConverter._parse_cell(field) for field in raw])
        return table

    @staticmethod
    def _parse_cell(cell: Optional[str]) -> Primitive:
        if cell is None:
            return None
        if cell in {"true", "false"}:
            return cell == "true"
        try:
            if '.' in cell or 'e' in cell.lower():
                return float(cell)
            return int(cell)
        except ValueError:
            return cell

    @staticmethod
    def _parse_md_line(line: str) -> List[Optional[str]]:
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

        # 2) Split on pipes
        raw_cells = trimmed.split('|')

        # 3) Trim each cell and map empty→None
        result: List[Optional[str]] = []
        for cell in raw_cells:
            c = cell.strip()
            if c == "":
                result.append(None)
            else:
                result.append(c)
        return result
    
    def _to_csv_line(row: List[Primitive]) -> str:
        return ','.join([DataTableConverter._val_to_str(cell) for cell in row])

    @staticmethod
    def _parse_csv_line(line: str) -> List[Optional[str]]:
        """Parse one CSV line handling:
        - quoted fields (with commas or escaped quotes)
        - `""` → empty string
        - empty field (bare comma) → None
        """
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
                fields.append(DataTableConverter._finalize_field(line, start_index, i))
                start_index = i + 1
            i += 1
        fields.append(DataTableConverter._finalize_field(line, start_index, i))
        return fields

    @staticmethod
    def _finalize_field(line: str, start: int, end: int) -> Optional[str]:
        s = line[start:end].strip()
        print('Finalizing field:', s)
        if len(s) == 0:
            return None
        s = DataTableConverter._strip_surrounding_quotes(s)
        return s.replace('""', '"')  # Replace escaped quotes with single quotes

    @staticmethod
    def _strip_surrounding_quotes(s: str) -> str:
        if len(s) >= 2 and s[0] == s[-1] and s[0] == '"':
            return s[1:-1]
        return s

def read_stream(stream: TextIO) -> List[str]:
    return stream.read().splitlines()

def write_to_stream(stream: TextIO, lines: List[str]):
    lines_with_newlines = [f"{line}\n" for line in lines]
    stream.writelines(lines_with_newlines)
