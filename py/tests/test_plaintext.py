import unittest
from typing import List

from importlib.resources import files
from bench.data import DataTableConverter, read_stream

TEST_RESOURCE_PACKAGE = "tests.resources"

def read_test_stream(name: str) -> List[str]:
    filepath = files(TEST_RESOURCE_PACKAGE).joinpath(name)
    with open(filepath, 'r', encoding='utf-8') as f:
        return read_stream(f)

class TestPlainTextConversion(unittest.TestCase):
    def _test_csv_to_md(self, name):
        csv = read_test_stream(f"{name}.csv")
        md = read_test_stream(f"{name}.md")
        table = DataTableConverter.from_csv_lines(csv)
        self.assertEqual(md, DataTableConverter.to_markdown_lines(table))

    def _test_md_to_csv(self, name):
        csv = read_test_stream(f"{name}.csv")
        md = read_test_stream(f"{name}.md")
        table = DataTableConverter.from_markdown_lines(md)
        self.assertEqual(csv, DataTableConverter.to_csv_lines(table))

    def _test_two_way_conv(self, csv_lines, md_lines):
        table = DataTableConverter.from_csv_lines(csv_lines)
        self.assertEqual(md_lines, DataTableConverter.to_markdown_lines(table))
        table = DataTableConverter.from_markdown_lines(md_lines)
        self.assertEqual(csv_lines, DataTableConverter.to_csv_lines(table))

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
            '|     |     |     |',
            '| --- | --- | --- |',
            '|     |     |     |',
        ]
        self._test_two_way_conv(csv_lines, md_lines)

if __name__ == "__main__":
    unittest.main()

