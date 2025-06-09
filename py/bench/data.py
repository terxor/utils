from typing import List, Union
from typing import TextIO

Primitive = Union[bool, int, float, str]

class DataTable:
    def __init__(self, num_columns: int, headers: List[str] = None):
        if num_columns <= 0:
            raise ValueError("Number of columns must be positive.")
        
        self.num_columns = num_columns
        self.headers = headers if headers is not None else [''] * num_columns

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
            raise ValueError("Row length does not match number of columns.")
        for item in row:
            if not isinstance(item, (bool, int, float, str)):
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
        import csv
        from io import StringIO
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(table.headers)
        writer.writerows(table.data())
        return output.getvalue().strip().splitlines()

    @staticmethod
    def from_csv_lines(lines: List[str]) -> DataTable:
        import csv
        reader = csv.reader(lines)
        rows = list(reader)
        if not rows:
            raise ValueError("Empty CSV input.")
        headers = rows[0]
        table = DataTable(len(headers), headers)
        for row in rows[1:]:
            table.add_row([DataTableConverter._parse_cell(cell) for cell in row])
        return table

    @staticmethod
    def to_markdown_lines(table: DataTable) -> List[str]:
        # Get headers and data rows from the DataTable object
        headers = table.headers
        data_rows = table.data()
        num_cols = table.num_columns

        # Calculate max width for each column
        # Initialize with header widths
        col_widths = [len(header) for header in headers]

        # Update widths based on actual data rows
        for row in data_rows:
            for i, cell in enumerate(row):
                # Ensure cell is converted to string for length calculation
                col_widths[i] = max(col_widths[i], len(str(cell)))

        # Helper to pad cells to column width
        def pad(cell: Primitive, width: int) -> str:
            s_cell = str(cell) # Convert cell to string for consistent length calculation and padding
            return s_cell + " " * (width - len(s_cell))

        # Build header row
        header_row = "| " + " | ".join(pad(cell, col_widths[i]) for i, cell in enumerate(headers)) + " |"

        # Build separator row with dashes (left-aligned, matching column width)
        separator_row = "| " + " | ".join("-" * col_widths[i] for i in range(num_cols)) + " |"

        # Build data rows
        lines = [header_row, separator_row]
        for row in data_rows:
            row_str = "| " + " | ".join(pad(cell, col_widths[i]) for i, cell in enumerate(row)) + " |"
            lines.append(row_str)
        return lines

    @staticmethod
    def from_markdown_lines(lines: List[str]) -> DataTable:
        if len(lines) < 2:
            raise ValueError("Invalid markdown input.")
        headers = [h.strip() for h in lines[0].strip('| \n').split('|')]
        table = DataTable(len(headers), headers)
        for line in lines[2:]:
            if not line.strip(): continue
            row = [DataTableConverter._parse_cell(cell.strip()) for cell in line.strip('| \n').split('|')]
            table.add_row(row)
        return table

    @staticmethod
    def _parse_cell(cell: str) -> Primitive:
        if cell.lower() in {"true", "false"}:
            return cell.lower() == "true"
        try:
            if '.' in cell:
                return float(cell)
            return int(cell)
        except ValueError:
            return cell


def read_stream(stream: TextIO) -> List[str]:
    return stream.read().splitlines()

def write_to_stream(stream: TextIO, lines: List[str]):
    lines_with_newlines = [f"{line}\n" for line in lines]
    stream.writelines(lines_with_newlines)
    stream.write("\n")
