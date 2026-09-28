from pathlib import Path
import json

import pandas as pd
import yaml


RAW_DATA_PATH = Path("data/raw/olist")
CONFIG_PATH = Path("config/data_quality.yaml")
OUTPUT_PATH = Path("data/processed/validation")

OUTPUT_PATH.mkdir(parents=True, exist_ok=True)


TABLE_FILES = {
    "customers": "olist_customers_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
}


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)["validation"]


def load_tables(data_path=RAW_DATA_PATH, cleaned=False):
    tables = {}

    for table_name, filename in TABLE_FILES.items():

        if cleaned:
            filename = f"{table_name}.csv"

        path = data_path / filename

        if not path.exists():
            raise FileNotFoundError(f"Missing file: {path}")

        tables[table_name] = pd.read_csv(path)

    return tables


def add_result(results, table, check, status, severity, details):
    results.append(
        {
            "table": table,
            "check": check,
            "status": status,
            "severity": severity,
            "details": details,
        }
    )


def validate_primary_key(df, table, rule, results):
    column = rule["column"]

    if column not in df.columns:
        add_result(
            results,
            table,
            f"Primary key exists: {column}",
            "FAIL",
            "CRITICAL",
            "Column is missing.",
        )
        return

    null_count = int(df[column].isna().sum())
    duplicate_count = int(df[column].duplicated().sum())

    if rule.get("nullable", True) and rule.get("unique", False):
        status = "PASS" if duplicate_count == 0 else "FAIL"
        severity = "CRITICAL" if duplicate_count else "LOW"

    else:
        status = "PASS" if null_count == 0 and duplicate_count == 0 else "FAIL"
        severity = "CRITICAL"

    add_result(
        results,
        table,
        f"Primary key: {column}",
        status,
        severity,
        f"Nulls={null_count}, duplicates={duplicate_count}",
    )


def validate_required_columns(df, table, rules, results):
    for column, rule in rules.items():

        if column not in df.columns:
            add_result(
                results,
                table,
                f"Required column: {column}",
                "FAIL",
                "CRITICAL",
                "Column is missing.",
            )
            continue

        null_count = int(df[column].isna().sum())

        status = "PASS" if (
            not rule.get("nullable", True) and null_count == 0
        ) else "PASS"

        severity = "HIGH" if null_count > 0 else "LOW"

        add_result(
            results,
            table,
            f"Required column: {column}",
            status,
            severity,
            f"Nulls={null_count}",
        )


def validate_numeric_ranges(df, table, rules, results):
    for column, rule in rules.items():

        if column not in df.columns:
            add_result(
                results,
                table,
                f"Numeric range: {column}",
                "FAIL",
                "CRITICAL",
                "Column is missing.",
            )
            continue

        series = pd.to_numeric(df[column], errors="coerce")

        invalid = pd.Series(False, index=df.index)

        if "min" in rule:
            invalid |= series < rule["min"]

        if "max" in rule:
            invalid |= series > rule["max"]

        invalid_count = int(invalid.sum())

        status = "PASS" if invalid_count == 0 else "FAIL"

        add_result(
            results,
            table,
            f"Numeric range: {column}",
            status,
            "CRITICAL" if invalid_count else "LOW",
            f"Invalid values={invalid_count}",
        )


def validate_allowed_values(df, table, rules, results):
    for column, rule in rules.items():

        if column not in df.columns:
            add_result(
                results,
                table,
                f"Allowed values: {column}",
                "FAIL",
                "CRITICAL",
                "Column is missing.",
            )
            continue

        allowed = set(rule["values"])

        invalid_mask = (
            df[column].notna()
            & ~df[column].isin(allowed)
        )

        invalid_count = int(invalid_mask.sum())

        add_result(
            results,
            table,
            f"Allowed values: {column}",
            "PASS" if invalid_count == 0 else "FAIL",
            "HIGH" if invalid_count else "LOW",
            f"Invalid values={invalid_count}",
        )


def validate_foreign_keys(tables, table_name, df, rules, results):
    for column, rule in rules.items():

        reference_table = rule["reference_table"]
        reference_column = rule["reference_column"]

        if column not in df.columns:
            add_result(
                results,
                table_name,
                f"Foreign key: {column}",
                "FAIL",
                "CRITICAL",
                "Column is missing.",
            )
            continue

        reference_df = tables[reference_table]

        missing_keys = (
            df[column].dropna()
            .loc[
                ~df[column].dropna().isin(
                    reference_df[reference_column]
                )
            ]
        )

        invalid_count = int(missing_keys.nunique())

        add_result(
            results,
            table_name,
            f"Foreign key: {column}",
            "PASS" if invalid_count == 0 else "FAIL",
            "CRITICAL" if invalid_count else "LOW",
            (
                f"Missing reference keys={invalid_count}; "
                f"references {reference_table}.{reference_column}"
            ),
        )


def validate_dates(df, table, columns, results):
    for column in columns:

        if column not in df.columns:
            add_result(
                results,
                table,
                f"Date parsing: {column}",
                "FAIL",
                "CRITICAL",
                "Column is missing.",
            )
            continue

        parsed = pd.to_datetime(
            df[column],
            errors="coerce"
        )

        invalid_count = int(
            parsed.isna().sum() - df[column].isna().sum()
        )

        add_result(
            results,
            table,
            f"Date parsing: {column}",
            "PASS" if invalid_count == 0 else "FAIL",
            "HIGH" if invalid_count else "LOW",
            f"Invalid dates={invalid_count}",
        )


def validate_tables(tables, config):
    results = []

    for table_name, rules in config.items():

        if table_name not in tables:
            continue

        df = tables[table_name]

        print(f"\nValidating: {table_name}")

        if "primary_key" in rules:
            validate_primary_key(
                df,
                table_name,
                rules["primary_key"],
                results,
            )

        if "required_columns" in rules:
            validate_required_columns(
                df,
                table_name,
                rules["required_columns"],
                results,
            )

        if "numeric_ranges" in rules:
            validate_numeric_ranges(
                df,
                table_name,
                rules["numeric_ranges"],
                results,
            )

        if "allowed_values" in rules:
            validate_allowed_values(
                df,
                table_name,
                rules["allowed_values"],
                results,
            )

        if "foreign_keys" in rules:
            validate_foreign_keys(
                tables,
                table_name,
                df,
                rules["foreign_keys"],
                results,
            )

        if "date_columns" in rules:
            validate_dates(
                df,
                table_name,
                rules["date_columns"],
                results,
            )

    return results


def summarize(results):

    total = len(results)
    passed = sum(r["status"] == "PASS" for r in results)
    failed = sum(r["status"] == "FAIL" for r in results)

    critical_failures = sum(
        r["status"] == "FAIL"
        and r["severity"] == "CRITICAL"
        for r in results
    )

    if critical_failures > 0:
        overall_status = "FAIL"
    elif failed > 0:
        overall_status = "WARNING"
    else:
        overall_status = "PASS"

    return {
        "overall_status": overall_status,
        "total_checks": total,
        "passed": passed,
        "failed": failed,
        "critical_failures": critical_failures,
    }


def main():

    print("Loading configuration...")
    config = load_config()

    print("Loading raw data...")
    tables = load_tables(RAW_DATA_PATH)

    print("Running validation...")
    results = validate_tables(tables, config)

    summary = summarize(results)

    report = {
        "summary": summary,
        "results": results,
    }

    output_file = OUTPUT_PATH / "raw_validation_report.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print("\n" + "=" * 50)
    print("RAW DATA VALIDATION SUMMARY")
    print("=" * 50)

    print(f"Overall status: {summary['overall_status']}")
    print(f"Total checks:   {summary['total_checks']}")
    print(f"Passed:         {summary['passed']}")
    print(f"Failed:         {summary['failed']}")
    print(f"Critical:       {summary['critical_failures']}")

    print(f"\nReport saved to: {output_file}")

    print("\nLoading cleaned data...")
    cleaned_tables = load_tables(
        Path("data/processed/cleaned"),
        cleaned=True
    )

    print("Running validation on cleaned data...")
    cleaned_results = validate_tables(cleaned_tables, config)

    cleaned_summary = summarize(cleaned_results)

    cleaned_report = {
        "summary": cleaned_summary,
        "results": cleaned_results,
    }

    cleaned_output_file = OUTPUT_PATH / "cleaned_validation_report.json"

    with open(cleaned_output_file, "w", encoding="utf-8") as file:
        json.dump(cleaned_report, file, indent=2)

    print("\n" + "=" * 50)
    print("CLEANED DATA VALIDATION SUMMARY")
    print("=" * 50)

    print(f"Overall status: {cleaned_summary['overall_status']}")
    print(f"Total checks:   {cleaned_summary['total_checks']}")
    print(f"Passed:         {cleaned_summary['passed']}")
    print(f"Failed:         {cleaned_summary['failed']}")
    print(f"Critical:       {cleaned_summary['critical_failures']}")

    print(f"\nReport saved to: {cleaned_output_file}")

if __name__ == "__main__":
    main()