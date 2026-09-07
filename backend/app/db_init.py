from pathlib import Path

from app.db import get_connection

SCHEMA_PATH = Path(__file__).parent.parent / "db" / "schema.sql"

def initialize_database():
    print("Initializing database...")

    schema = SCHEMA_PATH.read_text()

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(schema)

        conn.commit()

    print("Database initialized successfully.")