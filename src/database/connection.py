from pathlib import Path
import duckdb


DATABASE_DIR = Path("data/database")
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_PATH = DATABASE_DIR / "insight_agent.duckdb"


def get_connection():
    """
    Create and return a live DuckDB connection.

    The caller is responsible for closing the connection.
    """

    return duckdb.connect(str(DATABASE_PATH))