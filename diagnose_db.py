"""
Diagnostic: tries to connect to the database with a short timeout so it
fails fast with a real error message instead of hanging forever.

Usage:
    python diagnose_db.py
"""

import mysql.connector
from config import DB_CONFIG

print("Connecting with:")
print("  host =", repr(DB_CONFIG["host"]))
print("  user =", repr(DB_CONFIG["user"]))
print("  database =", repr(DB_CONFIG["database"]))
print()

try:
    connection = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        connection_timeout=5
    )
    print("SUCCESS: connected.")
    connection.close()

except Exception as e:
    print("FAILED:", type(e).__name__, "-", e)
