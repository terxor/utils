import unittest

from bench.data import DataTable, DataTableConverter

class TestDataTableConverter(unittest.TestCase):
    def setUp(self):
        self.table = DataTable(3, ["Name", "Age", "Passed"])
        self.table.add_row(["Alice", 30, True])
        self.table.add_row(["Bob", 25, False])

    def test_to_csv_lines(self):
        csv_lines = DataTableConverter.to_csv_lines(self.table)
        expected = [
            "Name,Age,Passed",
            "Alice,30,true",
            "Bob,25,false"
        ]
        self.assertEqual(csv_lines, expected)

    def test_from_csv_lines(self):
        csv_lines = [
            "Name,Age,Passed",
            "Charlie,22,true",
            "Dana,28,false"
        ]
        table = DataTableConverter.from_csv_lines(csv_lines)
        self.assertEqual(table.headers, ["Name", "Age", "Passed"])
        self.assertEqual(table.data(), [["Charlie", 22, True], ["Dana", 28, False]])

    def test_csv_round_trip(self):
        csv_lines = DataTableConverter.to_csv_lines(self.table)
        new_table = DataTableConverter.from_csv_lines(csv_lines)
        self.assertEqual(new_table.headers, self.table.headers)
        self.assertEqual(new_table.data(), self.table.data())

    def test_to_markdown_lines(self):
        md_lines = DataTableConverter.to_markdown_lines(self.table)
        expected = [
            "| Name  | Age | Passed |",
            "| ----- | --- | ------ |",
            "| Alice | 30  | true   |",
            "| Bob   | 25  | false  |"
        ]
        self.assertEqual(md_lines, expected)

    def test_from_markdown_lines(self):
        md_lines = [
            "| Name | Age | Passed |",
            "| --- | --- | --- |",
            "| Charlie | 22 | true |",
            "| Dana | 28 | false |"
        ]
        table = DataTableConverter.from_markdown_lines(md_lines)
        self.assertEqual(table.headers, ["Name", "Age", "Passed"])
        self.assertEqual(table.data(), [["Charlie", 22, True], ["Dana", 28, False]])

    def test_markdown_round_trip(self):
        md_lines = DataTableConverter.to_markdown_lines(self.table)
        new_table = DataTableConverter.from_markdown_lines(md_lines)
        self.assertEqual(new_table.headers, self.table.headers)
        self.assertEqual(new_table.data(), self.table.data())

if __name__ == "__main__":
    unittest.main()
