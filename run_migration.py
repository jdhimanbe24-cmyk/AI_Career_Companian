"""
One-off helper: runs add_password_resets_table.sql against your database
using the same connection settings your Flask app already uses (db.py / .env).

Usage:
    python run_migration.py
"""

from db import get_db_connection

with open("add_password_resets_table.sql", "r", encoding="utf-8") as f:
    sql = f.read()

connection = get_db_connection()
cursor = connection.cursor()

# Split on ';' in case more statements are ever added to the file.
for statement in sql.split(";"):
    statement = statement.strip()
    if statement:
        cursor.execute(statement)

connection.commit()
cursor.close()
connection.close()

print("Done. The password_resets table is ready.")
