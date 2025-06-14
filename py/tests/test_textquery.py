import unittest
from bench.data import DataTable
from bench.textquery import InMemoryDb, TypeInferer, SQLiteType

class TestInMemoryDb(unittest.TestCase):

    def setUp(self):
        # People table
        self.people = DataTable(3, ["Name", "Age", "IsStudent"])
        self.people.add_row(["Alice", 30, True])
        self.people.add_row(["Bob", 25, False])
        self.people.add_row(["Charlie", 35, True])

        # Courses table
        self.courses = DataTable(2, ["CourseID", "CourseName"])
        self.courses.add_row([101, "Mathematics"])
        self.courses.add_row([102, "Physics"])
        self.courses.add_row([103, "Literature"])

        # Enrollments table (many-to-many relationship)
        self.enrollments = DataTable(2, ["Name", "CourseID"])
        self.enrollments.add_row(["Alice", 101])
        self.enrollments.add_row(["Alice", 102])
        self.enrollments.add_row(["Charlie", 103])

        # Initialize in-memory DB with all tables
        self.db = InMemoryDb({
            "people": self.people,
            "courses": self.courses,
            "enrollments": self.enrollments
        })


    def tearDown(self):
        self.db.close()

    def test_query_all(self):
        result = self.db.query("SELECT * FROM people")
        self.assertEqual(result.size(), (3, 3))
        self.assertEqual(result.headers, ["Name", "Age", "IsStudent"])
        expected_rows = [
            ["Alice", 30, 1],
            ["Bob", 25, 0],
            ["Charlie", 35, 1]
        ]
        self.assertEqual(result.data(), expected_rows)

    def test_query_filter(self):
        result = self.db.query("SELECT Name FROM people WHERE Age > 30")
        self.assertEqual(result.size(), (1, 1))
        self.assertEqual(result.headers, ["Name"])
        self.assertEqual(result.data(), [["Charlie"]])

    def test_query_count(self):
        result = self.db.query("SELECT COUNT(*) FROM people WHERE IsStudent = 1")
        self.assertEqual(result.size(), (1, 1))
        self.assertEqual(result.headers, ["COUNT(*)"])
        self.assertEqual(result.data(), [[2]])

    def test_query_projection(self):
        result = self.db.query("SELECT Name, IsStudent FROM people")
        self.assertEqual(result.size(), (3, 2))
        self.assertEqual(result.headers, ["Name", "IsStudent"])
        expected_rows = [
            ["Alice", 1],
            ["Bob", 0],
            ["Charlie", 1]
        ]
        self.assertEqual(result.data(), expected_rows)

    def test_empty_result(self):
        result = self.db.query("SELECT * FROM people WHERE Age < 10")
        self.assertEqual(result.size(), (0, 3))
        self.assertEqual(result.headers, ["Name", "Age", "IsStudent"])
        self.assertEqual(result.data(), [])

    def test_people_course_join(self):
        result = self.db.query("""
            SELECT people.Name, courses.CourseName
            FROM people
            JOIN enrollments ON people.Name = enrollments.Name
            JOIN courses ON enrollments.CourseID = courses.CourseID
        """)
        
        self.assertEqual(result.headers, ["Name", "CourseName"])
        self.assertEqual(result.size(), (3, 2))
        
        expected_rows = [
            ["Alice", "Mathematics"],
            ["Alice", "Physics"],
            ["Charlie", "Literature"]
        ]
        
        actual_rows = sorted(result.data())  # sort for comparison
        expected_rows = sorted(expected_rows)
        
        self.assertEqual(actual_rows, expected_rows)


class TestTypeInferer(unittest.TestCase):
    def test_all_integer(self):
        table = DataTable(2, ["ID", "Age"])
        table.add_row([1, 30])
        table.add_row([2, 40])
        self.assertEqual(TypeInferer.infer(table), [SQLiteType.INTEGER, SQLiteType.INTEGER])

    def test_mixed_real_integer(self):
        table = DataTable(1, ["Score"])
        table.add_row([95])
        table.add_row([82.5])
        self.assertEqual(TypeInferer.infer(table), [SQLiteType.REAL])

    def test_mixed_with_text(self):
        table = DataTable(1, ["Info"])
        table.add_row(["abc"])
        table.add_row([123])
        self.assertEqual(TypeInferer.infer(table), [SQLiteType.TEXT])

    def test_empty_table(self):
        table = DataTable(2, ["A", "B"])
        self.assertEqual(TypeInferer.infer(table), [SQLiteType.TEXT, SQLiteType.TEXT])

    def test_boolean_handling(self):
        table = DataTable(1, ["Active"])
        table.add_row([True])
        table.add_row([False])
        self.assertEqual(TypeInferer.infer(table), [SQLiteType.INTEGER])
    
    def test_schema_inference(self):
        table = DataTable(3, ["Name", "Age", "IsStudent"])
        table.add_row(["Alice", 30, True])
        table.add_row(["Bob", 25, False])
        self.assertEqual(TypeInferer.infer(table), [SQLiteType.TEXT, SQLiteType.INTEGER, SQLiteType.INTEGER])

if __name__ == '__main__':
    unittest.main()
