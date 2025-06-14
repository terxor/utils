import unittest
from bench.data import MdFormat

class TestMdParsing(unittest.TestCase):

    def test_null_values_md(self):
        md_lines = [
            '|      |      |      |',
            '| ---- | ---- | ---- |',
            '|      |      |      |',
        ]
        md_format = MdFormat(md_lines)
        table = md_format.table
        self.assertEqual(table.size(), (1, 3))
        self.assertEqual(table.headers, ['col1', 'col2', 'col3'])
        expected_rows = [
            [None, None, None],
        ]
        self.assertEqual(table.data(), expected_rows)

    def test_uncommon_cases_md(self):
        md_lines = [
            '| 1 | 2 |',
            '|---|---|',
            '| "" |  xyz |',
            '| "    " |   |',
            '| "    " | |',
            '| | |',
            '| a long sentence | with a \\| pipe inside quotes |',
            '| | "  fully quoted" |',
            '| true | True |',
            '| TRUE | false |',
            '| 0  | 0.5 |',
        ]
        md_format = MdFormat(md_lines)
        table = md_format.table
        self.assertEqual(table.size(), (len(md_lines) - 2, 2))
        self.assertEqual(table.headers, ['1', '2'])
        expected_rows = [
            ['""', 'xyz'],
            ['"    "', None],
            ['"    "', None],
            [None, None],
            ['a long sentence', 'with a | pipe inside quotes'],
            [None, '"  fully quoted"'],
            [True, True],
            [True, False],
            [0, 0.5],
        ]
        self.assertEqual(table.data(), expected_rows)

    def test_more_weird_quote_cases_md(self):
        # No quoting considerations in MD, we parse it as it is.
        md_lines = [
            '| col1 | col2 | col3 |',
            '|------|------|------|',
            '|   "ab""c""d"   | """""x"""""   | "" x "" y "" |',
            '| quotes at " random " places | " " | """ |',
            '| quotes at "" random "" places |   |   |',
            '| ","","""," | | |',
        ]
        md_format = MdFormat(md_lines)
        table = md_format.table
        self.assertEqual(table.size(), (len(md_lines) - 2, 3))
        self.assertEqual(table.headers, ['col1', 'col2', 'col3'])
        expected_rows = [
            ['"ab""c""d"', '"""""x"""""', '"" x "" y ""'],
            ['quotes at " random " places', '" "', '"""'],
            ['quotes at "" random "" places', None, None],
            ['","",""","', None, None],
        ]
        self.assertEqual(table.data(), expected_rows)


class TestMdFormatting(unittest.TestCase):

    def test_md_formatting(self):
        md_lines = [
            '| col1 | | col3 |',
            '|------|------|------|',
            '|1| 2     | 3|',
            '| 4    | 5 | "6" |',
            '| 7 | "8" | 9 |',
        ]
        md_format = MdFormat(md_lines)
        formatted_lines = md_format.format()
        expected_lines = [
            '| col1 | col2 | col3 |',
            '| ---- | ---- | ---- |',
            '| 1    | 2    | 3    |',
            '| 4    | 5    | "6"  |', # No quoting considerations in MD
            '| 7    | "8"  | 9    |',
        ]
        self.assertEqual(formatted_lines, expected_lines)

    def test_md_formatting_numeric_reformat(self):
        md_lines = [
            '| col1 | col2 | col3 |',
            '|------|------|------|',
            '| +1.0 | -2e3 | 3.14 |',
            '| 0040 | -3.666666667 | 0.0000000000000001 |',
        ]
        md_format = MdFormat(md_lines)
        formatted_lines = md_format.format()
        expected_lines = [
            '| col1 | col2     | col3  |',
            '| ---- | -------- | ----- |',
            '| 1    | -2000    | 3.14  |',
            '| 40   | -3.66667 | 1e-16 |',
        ]
        self.assertEqual(formatted_lines, expected_lines)

if __name__ == "__main__":
    unittest.main()
