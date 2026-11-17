import psycopg2
import psycopg2.extras

from config import DATABASE_URL


class _ConnectionWrapper:
    """
    Thin shim so the rest of the app (written against mysql.connector's
    API) keeps working unchanged against psycopg2/Postgres.

    mysql.connector's `connection.cursor(dictionary=True)` returns rows as
    dicts; psycopg2 instead takes a `cursor_factory` argument. This wrapper
    translates the former into the latter so no call site elsewhere in the
    app needs to change.
    """

    def __init__(self, conn):
        self._conn = conn

    def cursor(self, dictionary=False, **kwargs):
        if dictionary:
            return self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return self._conn.cursor()

    def __getattr__(self, name):
        return getattr(self._conn, name)


def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
    return _ConnectionWrapper(conn)
