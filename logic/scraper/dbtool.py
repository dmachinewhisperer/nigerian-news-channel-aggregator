import sqlite3
import sys

def query_database(dbname, tbname, num_rows=None, show_total=False, show_schema=False, clean=False):
    """
    Query the specified database and table.

    Args:
        dbname (str): Name of the SQLite database file.
        tbname (str): Name of the table in the database.
        num_rows (int, optional): Number of rows to print. Defaults to None.
        show_total (bool, optional): If True, show the total number of rows in the table.
        show_schema (bool, optional): If True, show the schema of the table.
        clean (bool, optional): If True, remove all rows from the table.

    Returns:
        int: Total number of rows in the table if show_total is True, else None.
    """
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()

    if show_schema:
        cursor.execute(f"PRAGMA table_info({tbname})")
        schema_info = cursor.fetchall()
        for col in schema_info:
            print(f"Column: {col[1]}, Type: {col[2]}, Not Null: {bool(col[3])}, Default: {col[4]}, Primary Key: {bool(col[5])}")
        conn.close()
        return

    if show_total:
        cursor.execute(f"SELECT COUNT(*) FROM {tbname}")
        total_rows = cursor.fetchone()[0]
        conn.close()
        return total_rows

    if clean:
        cursor.execute(f"DELETE FROM {tbname}")
        conn.commit()
        print(f"All rows in table '{tbname}' have been removed.")
        conn.close()
        return

    if num_rows is not None:
        cursor.execute(f"SELECT * FROM {tbname} LIMIT {num_rows}")
    else:
        cursor.execute(f"SELECT * FROM {tbname}")

    rows = cursor.fetchall()
    for row in rows:
        print(row)

    conn.close()

def main():
    """
    Main function to handle command line arguments and perform the database query.

    Usage:
        python script.py dbname tbname 10        # Prints the specified number of rows from the table
        python script.py dbname tbname count     # Shows the total number of rows in the table
        python script.py dbname tbname schema    # Shows the schema of the table
        python script.py dbname tbname clean     # Removes all rows from the table
    """
    if len(sys.argv) != 4:
        print("Usage:")
        print("  python script.py dbname tbname 10        # Prints the specified number of rows from the table")
        print("  python script.py dbname tbname count     # Shows the total number of rows in the table")
        print("  python script.py dbname tbname schema    # Shows the schema of the table")
        print("  python script.py dbname tbname clean     # Removes all rows from the table")
        return

    dbname = sys.argv[1]
    tbname = sys.argv[2]
    operation = sys.argv[3]

    if operation.isdigit():
        num_rows = int(operation)
        query_database(dbname, tbname, num_rows=num_rows)
    elif operation.lower() == 'count':
        total_rows = query_database(dbname, tbname, show_total=True)
        print(f"Total number of rows in the table '{tbname}': {total_rows}")
    elif operation.lower() == 'schema':
        query_database(dbname, tbname, show_schema=True)
    elif operation.lower() == 'clean':
        query_database(dbname, tbname, clean=True)
    else:
        print(f"Unknown operation: {operation}")
        print("Please provide a valid number of rows, use 'count' to get the total number of rows, 'schema' to see the table's schema, or 'clean' to remove all rows from the table.")

if __name__ == "__main__":
    main()
