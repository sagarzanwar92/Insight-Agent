from pathlib import Path

from src.database.connection import get_connection


CURATED_DIR = Path("data/curated")


TABLES = [
    "fact_orders",
    "fact_order_items",
    "fact_payments",
    "dim_products",
    "dim_customers",
    "dim_sellers",
    "dim_date",
]


def create_database():

    connection = get_connection()

    try:

        for table_name in TABLES:

            csv_path = CURATED_DIR / f"{table_name}.csv"

            if not csv_path.exists():
                raise FileNotFoundError(
                    f"Curated table not found: {csv_path}"
                )

            connection.execute(
                f"""
                CREATE OR REPLACE TABLE {table_name} AS
                SELECT *
                FROM read_csv_auto(?)
                """,
                [str(csv_path)],
            )

            row_count = connection.execute(
                f"SELECT COUNT(*) FROM {table_name}"
            ).fetchone()[0]

            print(
                f"Loaded {table_name}: {row_count:,} rows"
            )

    finally:
        connection.close()

    print()
    print("=" * 50)
    print("DUCKDB DATABASE CREATED")
    print("=" * 50)


if __name__ == "__main__":
    create_database()