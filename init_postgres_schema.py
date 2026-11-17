"""
Run automatically on every Render build (see render.yaml's buildCommand).

Applies schema_postgres.sql to the configured Postgres database. Safe to
run on every deploy: every statement in schema_postgres.sql is written to
be idempotent (CREATE TABLE IF NOT EXISTS, CREATE OR REPLACE FUNCTION,
DROP TRIGGER IF EXISTS before CREATE TRIGGER), so re-running it against an
already-initialized database is a no-op.
"""

import os
import psycopg2

from config import DATABASE_URL

SCHEMA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema_postgres.sql")

if not DATABASE_URL:
    print("No DATABASE_URL set - skipping schema init (expected for local MySQL dev).")
    raise SystemExit(0)

with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
    schema_sql = f.read()

conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
cursor = conn.cursor()
cursor.execute(schema_sql)
conn.commit()
cursor.close()
conn.close()

print("Postgres schema applied successfully.")
