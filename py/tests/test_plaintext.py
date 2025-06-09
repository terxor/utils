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

    def test_csv_to_md_samples(self):
        self._test_csv_to_md("sample1")
        # self._test_csv_to_md("sample2")
        # self._test_csv_to_md("sample3")
        # self._test_csv_to_md("sample4")
        # self._test_csv_to_md("sample5")

    def test_md_to_csv_samples(self):
        self._test_csv_to_md("sample1")
        # self._test_csv_to_md("sample2")
        # self._test_csv_to_md("sample3")
        # self._test_csv_to_md("sample4")
        # self._test_csv_to_md("sample5")

if __name__ == "__main__":
    unittest.main()

