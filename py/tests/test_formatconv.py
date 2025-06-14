import unittest
from typing import List

from importlib.resources import files
from bench.data import DataTable, StreamUtils, MdFormat, CsvFormat

class TestTwoWayConversions(unittest.TestCase):

    def read_test_stream(self, name: str) -> List[str]:
        filepath = files("tests.resources").joinpath(name)
        with open(filepath, 'r', encoding='utf-8') as f:
            return StreamUtils.read_stream(f)

    def _test_csv_to_md(self, name):
        csv = self.read_test_stream(f"{name}.csv")
        md = self.read_test_stream(f"{name}.md")
        self.assertEqual(md, MdFormat(CsvFormat(csv).table).format())

    def _test_md_to_csv(self, name):
        csv = self.read_test_stream(f"{name}.csv")
        md = self.read_test_stream(f"{name}.md")
        self.assertEqual(csv, CsvFormat(MdFormat(md).table).format())

    def _test_two_way_conv(self, csv_lines, md_lines):
        table = CsvFormat(csv_lines).table
        self.assertEqual(md_lines, MdFormat(table).format())
        table = MdFormat(md_lines).table
        self.assertEqual(csv_lines, CsvFormat(table).format())

    def test_csv_to_md_samples(self):
        self._test_csv_to_md("sample1")
        self._test_csv_to_md("sample2")
        self._test_csv_to_md("sample3")

    def test_md_to_csv_samples(self):
        self._test_md_to_csv("sample1")
        self._test_md_to_csv("sample2")
        self._test_md_to_csv("sample3")

    def test_simple_conv(self):
        csv_lines = [
            'Header1,Header2',
            'Data1,Data2'
        ]
        md_lines = [
            '| Header1 | Header2 |',
            '| ------- | ------- |',
            '| Data1   | Data2   |'
        ]
        self._test_two_way_conv(csv_lines, md_lines)

    def test_short_or_empty(self):
        csv_lines = [
            'a,b,c',
            ',x,'
        ]
        md_lines = [
            '| a   | b   | c   |',
            '| --- | --- | --- |',
            '|     | x   |     |',
        ]
        self._test_two_way_conv(csv_lines, md_lines)

    def test_header_only(self):
        csv_lines = [
            'a,b,c',
        ]
        md_lines = [
            '| a   | b   | c   |',
            '| --- | --- | --- |',
        ]
        self._test_two_way_conv(csv_lines, md_lines)

    def test_full_empty(self):
        csv_lines = [
            ',,',
            ',,',
        ]
        md_lines = [
            '| col1 | col2 | col3 |',
            '| ---- | ---- | ---- |',
            '|      |      |      |',
        ]
        # In this case, we expect the headers to be generated
        # since the CSV does not provide any headers.
        self.assertEqual(md_lines, MdFormat(CsvFormat(csv_lines).table).format())

class TestDataTableConverter(unittest.TestCase):
    def setUp(self):
        self.table = DataTable(3, ["Name", "Age", "Passed"])
        self.table.add_row(["Alice", 30, True])
        self.table.add_row(["Bob", 25, False])

    def test_to_csv_lines(self):
        csv_lines = CsvFormat(self.table).format()
        expected = [
            "Name,Age,Passed",
            "Alice,30,true",
            "Bob,25,false"
        ]
        self.assertEqual(csv_lines, expected)

    def test_csv_round_trip(self):
        csv_lines = CsvFormat(self.table).format()
        new_table = CsvFormat(csv_lines).table
        self.assertEqual(new_table.headers, self.table.headers)
        self.assertEqual(new_table.data(), self.table.data())

    def test_to_markdown_lines(self):
        md_lines = MdFormat(self.table).format()
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
        table = MdFormat(md_lines).table
        self.assertEqual(table.headers, ["Name", "Age", "Passed"])
        self.assertEqual(table.data(), [["Charlie", 22, True], ["Dana", 28, False]])

    def test_markdown_round_trip(self):
        md_lines = MdFormat(self.table).format()
        new_table = MdFormat(md_lines).table
        self.assertEqual(new_table.headers, self.table.headers)
        self.assertEqual(new_table.data(), self.table.data())

if __name__ == "__main__":
    unittest.main()
