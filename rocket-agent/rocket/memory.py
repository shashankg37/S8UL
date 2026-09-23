import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).parent / "rocket_memory.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_memory():
    """Creates Rocket's memory database if it does not exist."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def remember(category: str, content: str) -> str:
    """Stores information in Rocket's persistent memory."""
    initialize_memory()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO memories (category, content)
            VALUES (?, ?)
            """,
            (category, content),
        )

    return f"Remembered: {content}"


def recall(category: str) -> str:
    """Retrieves memories from a category."""
    initialize_memory()

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT content
            FROM memories
            WHERE category = ?
            ORDER BY created_at DESC
            LIMIT 10
            """,
            (category,),
        ).fetchall()

    if not rows:
        return f"No memories found for category '{category}'."

    return "\n".join(row[0] for row in rows)