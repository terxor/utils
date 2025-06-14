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
            '| col1 | col2 | col3 |',
            '| ---- | ---- | ---- |',
            '|      |      |      |',
        ]
        # In this case, we expect the headers to be generated
        # since the CSV does not provide any headers.
        table = DataTableConverter.from_csv_lines(csv_lines)
        self.assertEqual(md_lines, DataTableConverter.to_markdown_lines(table))

    def test_null_values(self):
        csv_lines = [
            ',,',
            ',,',
        ]
        table = DataTableConverter.from_csv_lines(csv_lines)
        self.assertEqual(table.size(), (1, 3))
        self.assertEqual(table.headers, ['col1', 'col2', 'col3'])
        expected_rows = [
            [None, None, None],
        ]
        self.assertEqual(table.data(), expected_rows)

    def test_uncommon_cases_csv(self):
        csv_lines = [
            '1,2', # Even though columns are seemingly ints, they are treated as strings
            '"",  xyz', # Initial empty spaces are trimmed.
            '"    ",   ', # Both are strings, second is null effectively
            '"    ",', # In this case, the second column is null
            ',', # Both are null
            'a long sentence   , "with a comma, inside quotes"', # Leading and trailing spaces are trimmed, comma inside quotes is preserved
            ',"  fully quoted"',
            'true,True',
            'TRUE,false',
            '0  , 0.5',
            'ab""efg,""cd""', # Note that [""cd""] is malformed, but we still parse it as ["cd"]
            '"x""abc""","""cd"""', # ["""cd"""] is okay - parsed as ["cd"]
        ]
        table = DataTableConverter.from_csv_lines(csv_lines)
        self.assertEqual(table.size(), (len(csv_lines) - 1, 2))
        self.assertEqual(table.headers, ['1', '2'])
        expected_rows = [
            ['', 'xyz'],
            ['    ', None],
            ['    ', None],
            [None, None],
            ['a long sentence', 'with a comma, inside quotes'],
            [None, '  fully quoted'],
            [True, 'True'],
            ['TRUE', False],
            [0, 0.5],
            ['ab"efg', '"cd"'],
            ['x"abc"', '"cd"'],
        ]
        self.assertEqual(table.data(), expected_rows)

    def test_more_weird_quote_cases(self):
        csv_lines = [
            ',,',
            '   "ab""c""d"   , """""x"""""   , "" x "" y "" ',
            'here is a " string " with quotes at " random " places," ",""""', # stray quotes are just parsed as they are, but ideally should be escaped
            'here is a "" string "" with quotes at "" random "" places,   ,   ', # here, the quotes are escaped properly
            '","",""",,', # Look closely at the first part
        ]
        table = DataTableConverter.from_csv_lines(csv_lines)
        self.assertEqual(table.size(), (len(csv_lines) - 1, 3))
        self.assertEqual(table.headers, ['col1', 'col2', 'col3'])
        expected_rows = [
            ['ab"c"d', '""x""', '" x " y "'],
            ['here is a " string " with quotes at " random " places', ' ', '"'],
            ['here is a " string " with quotes at " random " places', None, None],
            [',","', None, None],
        ]
        self.assertEqual(table.data(), expected_rows)

if __name__ == "__main__":
    unittest.main()

