import unittest
from bench.data import CsvFormat

class TestCsvParsing(unittest.TestCase):

    def test_from_csv_lines(self):
        csv_lines = [
            "Name,Age,Passed",
            "Charlie,22,true",
            "Dana,28,false"
        ]
        csv_format = CsvFormat(csv_lines)
        table = csv_format.table
        self.assertEqual(table.headers, ["Name", "Age", "Passed"])
        self.assertEqual(table.data(), [["Charlie", 22, True], ["Dana", 28, False]])

    def test_null_values(self):
        csv_lines = [
            ',,',
            ',,',
        ]
        csv_format = CsvFormat(csv_lines)
        table = csv_format.table
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
        csv_format = CsvFormat(csv_lines)
        table = csv_format.table
        self.assertEqual(table.size(), (len(csv_lines) - 1, 2))
        self.assertEqual(table.headers, ['1', '2'])
        expected_rows = [
            ['', 'xyz'],
            ['    ', None],
            ['    ', None],
            [None, None],
            ['a long sentence', 'with a comma, inside quotes'],
            [None, '  fully quoted'],
            [True, True],
            [True, False],
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
        csv_format = CsvFormat(csv_lines)
        table = csv_format.table
        self.assertEqual(table.size(), (len(csv_lines) - 1, 3))
        self.assertEqual(table.headers, ['col1', 'col2', 'col3'])
        expected_rows = [
            ['ab"c"d', '""x""', '" x " y "'],
            ['here is a " string " with quotes at " random " places', ' ', '"'],
            ['here is a " string " with quotes at " random " places', None, None],
            [',","', None, None],
        ]
        self.assertEqual(table.data(), expected_rows)

class TestCsvFormatting(unittest.TestCase):

    def test_csv_formatting(self):
        csv_lines = [
            'col1 ,,  col3',
            '  1 ,    2  ,3',
            ' 4,5,"6"',
            '7,  "8" ,9   ',
        ]
        csv_format = CsvFormat(csv_lines)
        formatted_lines = csv_format.format()
        expected_lines = [
            'col1,col2,col3',
            '1,2,3',
            '4,5,6',
            '7,8,9',
        ]
        self.assertEqual(formatted_lines, expected_lines)

    def test_csv_formatting_numeric_reformat(self):
        csv_lines = [
            ',,',
            '+1.0,-2e3,3.14',
            '0040,-3.666666667,0.0000000000000001',
        ]
        csv_format = CsvFormat(csv_lines)
        formatted_lines = csv_format.format()
        expected_lines = [
            'col1,col2,col3',
            '1,-2000,3.14',
            '40,-3.66667,1e-16',
        ]
        self.assertEqual(formatted_lines, expected_lines)

if __name__ == "__main__":
    unittest.main()

