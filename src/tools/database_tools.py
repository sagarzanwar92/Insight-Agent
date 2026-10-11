import re
from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "database" / "insight_agent.duckdb"


def query_database(sql: str) -> list[dict]:
    """
    Execute one read only SELECT query against the InsightAgent database.
    Return query results as a list of dictionaries.
    """

    if not sql or not sql.strip():
        raise ValueError("SQL query cannot be empty.")

    # Remove optional Markdown code fences from LLM output.
    sql = sql.strip()
    sql = re.sub(r"^```(?:sql)?\s*", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s*```$", "", sql).strip()

    # Allow one SELECT or WITH query only.
    if not re.match(r"^(SELECT|WITH)\b", sql, flags=re.IGNORECASE):
        raise ValueError("Only SELECT queries are allowed.")

    # Reject multiple statements.
    if ";" in sql.rstrip(";"):
        raise ValueError("Only one SQL statement is allowed.")

    connection = duckdb.connect(
        str(DATABASE_PATH),
        read_only=True
    )

    try:
        result = connection.execute(sql).fetchdf()
        return result.to_dict(orient="records")
    finally:
        connection.close()