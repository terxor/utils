import unittest

from bench.data import DataTable

class TestDataTable(unittest.TestCase):
    def test_initialization_with_headers(self):
        table = DataTable(2, ["Name", "Age"])
        self.assertEqual(table.headers, ["Name", "Age"])
        self.assertEqual(table.size(), (0, 2))

    def test_initialization_with_default_headers(self):
        table = DataTable(3)
        self.assertEqual(table.headers, ['col1', 'col2', 'col3'])

    def test_invalid_column_number(self):
        with self.assertRaises(ValueError):
            DataTable(0)

    def test_mismatched_headers(self):
        with self.assertRaises(ValueError):
            DataTable(3, ["A", "B"])  # Only 2 headers for 3 columns

    def test_add_valid_row(self):
        table = DataTable(2)
        table.add_row(["Alice", 25])
        self.assertEqual(table.size(), (1, 2))
        self.assertEqual(table[0][0], "Alice")
        self.assertEqual(table[0][1], 25)

    def test_add_invalid_row_length(self):
        table = DataTable(2)
        with self.assertRaises(ValueError):
            table.add_row(["Only one item"])

    def test_add_invalid_data_type(self):
        table = DataTable(1)
        with self.assertRaises(TypeError):
            table.add_row([{"name": "Alice"}])  # dict is not allowed

    def test_str_output(self):
        table = DataTable(2, ["Col1", "Col2"])
        table.add_row([1, 2.5])
        table.add_row(["Text", True])
        expected = "Col1\tCol2\n1\t2.5\nText\tTrue"
        self.assertEqual(str(table), expected)

if __name__ == '__main__':
    unittest.main()
