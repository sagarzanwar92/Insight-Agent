from pathlib import Path
import pandas as pd
import json


RAW_DIR = Path("data/raw/olist")
CLEANED_DIR = Path("data/processed/cleaned")
REPORT_DIR = Path("data/processed/cleaning")

CLEANED_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def clean_order_payments(df: pd.DataFrame) -> tuple[pd.DataFrame, list]:
    """
    Clean the order_payments table.

    Current rules:
    1. Standardize payment_type.
    2. Convert 'not_defined' to 'unknown'.
    3. Preserve all records.
    """

    df = df.copy()
    changes = []

    mask = df["payment_type"].eq("not_defined")
    affected = int(mask.sum())

    if affected > 0:
        df.loc[mask, "payment_type"] = "unknown"

        changes.append(
            {
                "column": "payment_type",
                "original_value": "not_defined",
                "new_value": "unknown",
                "records_affected": affected,
            }
        )

    return df, changes


def clean_table(table_name: str) -> tuple[pd.DataFrame, list]:
    """
    Load and clean a specific table.
    """

    input_file = RAW_DIR / f"olist_{table_name}_dataset.csv"

    if not input_file.exists():
        raise FileNotFoundError(f"File not found: {input_file}")

    df = pd.read_csv(input_file)

    if table_name == "order_payments":
        return clean_order_payments(df)

    # Other tables currently pass through unchanged.
    return df.copy(), []


def run_cleaning() -> None:
    """
    Run the cleaning pipeline for all available Olist tables.
    """

    tables = [
        "customers",
        "geolocation",
        "orders",
        "order_items",
        "order_payments",
        "order_reviews",
        "products",
        "sellers",
    ]

    cleaning_report = {
        "status": "SUCCESS",
        "tables": {},
    }

    for table_name in tables:

        print(f"Cleaning: {table_name}")

        df, changes = clean_table(table_name)

        output_file = CLEANED_DIR / f"{table_name}.csv"
        df.to_csv(output_file, index=False)

        cleaning_report["tables"][table_name] = {
            "input_rows": len(df),
            "output_rows": len(df),
            "changes": changes,
        }

        print(f"  Rows: {len(df):,}")
        print(f"  Changes: {len(changes)}")

    report_file = REPORT_DIR / "cleaning_report.json"

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(cleaning_report, f, indent=2)

    print()
    print("=" * 50)
    print("CLEANING COMPLETE")
    print("=" * 50)
    print(f"Report saved to: {report_file}")


if __name__ == "__main__":
    run_cleaning()