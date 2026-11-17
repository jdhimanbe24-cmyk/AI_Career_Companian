"""
One-off script: creates a dedicated, low-privilege MySQL user for the
deployed app to use (instead of root), scoped to only the app's database.

Run this once with: venv\\Scripts\\python.exe create_app_db_user.py
It uses the root credentials already in your .env file - it does not
ask you to type a password.
"""

import getpass
import mysql.connector
from config import DB_CONFIG

NEW_USER = "job_prep_app"

print(f"Connecting to MySQL at {DB_CONFIG['host']}:{DB_CONFIG['port']} as '{DB_CONFIG['user']}'...")

new_password = getpass.getpass(
    f"Enter a strong NEW password to create for the '{NEW_USER}' MySQL user: "
)
if not new_password:
    print("No password entered, aborting.")
    raise SystemExit(1)

conn = mysql.connector.connect(
    host=DB_CONFIG["host"],
    port=DB_CONFIG["port"],
    user=DB_CONFIG["user"],
    password=DB_CONFIG["password"],
    connection_timeout=10,
)
cursor = conn.cursor()

cursor.execute(
    f"CREATE USER IF NOT EXISTS '{NEW_USER}'@'%%' IDENTIFIED BY %s",
    (new_password,),
)
cursor.execute(
    f"ALTER USER '{NEW_USER}'@'%%' IDENTIFIED BY %s",
    (new_password,),
)
cursor.execute(
    f"GRANT SELECT, INSERT, UPDATE, DELETE ON {DB_CONFIG['database']}.* TO '{NEW_USER}'@'%%'"
)
cursor.execute("FLUSH PRIVILEGES")

conn.commit()
cursor.close()
conn.close()

print(f"\nDone. Created/updated MySQL user '{NEW_USER}' with access to only '{DB_CONFIG['database']}'.")
print("Use this as DB_USER in Render, with the password you just typed as DB_PASSWORD.")
