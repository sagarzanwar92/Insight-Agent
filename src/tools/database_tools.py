import duckdb
from pathlib import Path


DATABASE_PATH = Path("data/database/insight_agent.duckdb")


def query_database(sql: str):
    """
    Execute a read-only SQL query against the InsightAgent database.

    Parameters
    ----------
    sql : str
        SQL query to execute.

    Returns
    -------
    list[dict]
        Query results as dictionaries.
    """

    connection = duckdb.connect(
        str(DATABASE_PATH),
        read_only=True
    )

    try:
        result = connection.execute(sql).fetchdf()
        return result.to_dict(orient="records")

    finally:
        connection.close()