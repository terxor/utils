import unittest
import os, sys
import csv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from csv2md import read_csv_from_file, csv_to_markdown_table
from md2csv import markdown_to_csv_table

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def read_file(filepath: str) -> str:
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read().strip()

def read_csv_file(filepath: str) -> list[list[str]]:
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        return [row for row in reader]

class TestCSVToMarkdownWithFiles(unittest.TestCase):
    def test_sample1(self):
        csv_path = os.path.join(BASE_DIR, "sample1.csv")
        md_path = os.path.join(BASE_DIR, "sample1.md")

        with open(csv_path, 'r', encoding='utf-8') as f:
            csv_data = read_csv_from_file(f)
        expected_output = read_file(md_path)

        self.assertEqual(csv_to_markdown_table(csv_data), expected_output)

    def test_sample2(self):
        csv_path = os.path.join(BASE_DIR, "sample2.csv")
        md_path = os.path.join(BASE_DIR, "sample2.md")

        with open(csv_path, 'r', encoding='utf-8') as f:
            csv_data = read_csv_from_file(f)
        expected_output = read_file(md_path)

        self.assertEqual(csv_to_markdown_table(csv_data), expected_output)

    def test_empty_file(self):
        csv_data = []
        self.assertEqual(csv_to_markdown_table(csv_data), "")

    def test_header_only_file(self):
        csv_data = [["Col1", "Col2"]]
        expected = "| Col1 | Col2 |\n| ---- | ---- |"
        self.assertEqual(csv_to_markdown_table(csv_data), expected)

class TestMarkdownToCSV(unittest.TestCase):
    def test_sample1(self):
        base = os.path.dirname(__file__)
        md_path = os.path.join(base, "sample1.md")
        csv_path = os.path.join(base, "sample1.csv")

        with open(md_path, encoding='utf-8') as f:
            md_lines = f.readlines()
        expected_csv = read_csv_file(csv_path)

        result = markdown_to_csv_table(md_lines)
        self.assertEqual(result, expected_csv)

    def test_sample2(self):
        base = os.path.dirname(__file__)
        md_path = os.path.join(base, "sample2.md")
        csv_path = os.path.join(base, "sample2.csv")

        with open(md_path, encoding='utf-8') as f:
            md_lines = f.readlines()
        expected_csv = read_csv_file(csv_path)

        result = markdown_to_csv_table(md_lines)
        self.assertEqual(result, expected_csv)

    def test_empty_input(self):
        self.assertEqual(markdown_to_csv_table([]), [])

    def test_header_only(self):
        md = [
            "| Col1 | Col2 |",
            "| --- | --- |"
        ]
        expected = [["Col1", "Col2"]]
        self.assertEqual(markdown_to_csv_table(md), expected)


if __name__ == "__main__":
    unittest.main()

