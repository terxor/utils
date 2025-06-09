#!/usr/bin/python3

import argparse
import csv
import sqlite3
import os
import sys

def load_csv_to_sqlite(cursor, table_name, file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)
        headers = [h.strip() for h in headers]

        # Create table
        columns = ', '.join(f'"{h}" TEXT' for h in headers)
        cursor.execute(f'CREATE TABLE "{table_name}" ({columns});')

        # Insert rows
        for row in reader:
            placeholders = ', '.join('?' for _ in row)
            cursor.execute(f'INSERT INTO "{table_name}" VALUES ({placeholders});', row)

def parse_args():
    parser = argparse.ArgumentParser(description="tq - TextQuery over CSVs using SQLite")
    parser.add_argument("bindings_and_query", nargs='+', help="table=csvfile ... SQL")
    return parser.parse_args()

def main():
    args = parse_args()

    bindings = {}
    sql_parts = []

    # Separate bindings from the SQL query
    for arg in args.bindings_and_query:
        if '=' in arg and not arg.strip().lower().startswith("select"):
            name, path = arg.split('=', 1)
            bindings[name.strip()] = path.strip()
        else:
            sql_parts.append(arg)

    if not sql_parts:
        print("Error: SQL query not found.")
        sys.exit(1)

    sql_query = ' '.join(sql_parts)

    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # Load CSVs into the SQLite memory DB
    for table_name, file_path in bindings.items():
        if not os.path.isfile(file_path):
            print(f"Error: File '{file_path}' not found.")
            sys.exit(1)
        load_csv_to_sqlite(cursor, table_name, file_path)

    try:
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        # Output results
        print(','.join(columns))
        for row in rows:
            print(','.join(str(col) if col is not None else '' for col in row))
    except Exception as e:
        print(f"SQL error: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
