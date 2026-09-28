from pathlib import Path
import pandas as pd
import json


RAW_DATA_PATH = Path("data/raw/olist")
OUTPUT_PATH = Path("data/processed/profile")

OUTPUT_PATH.mkdir(parents=True, exist_ok=True)


def profile_file(file_path: Path) -> dict:
    """Generate a data quality profile for one CSV file."""

    df = pd.read_csv(file_path)

    profile = {
        "file": file_path.name,
        "rows": len(df),
        "columns": len(df.columns),
        "column_details": {},
    }

    for column in df.columns:
        series = df[column]

        profile["column_details"][column] = {
            "dtype": str(series.dtype),
            "missing_count": int(series.isna().sum()),
            "missing_pct": round(float(series.isna().mean() * 100), 2),
            "unique_count": int(series.nunique(dropna=True)),
            "duplicate_count": int(series.duplicated().sum()),
        }

    return profile


def main():

    csv_files = sorted(RAW_DATA_PATH.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in {RAW_DATA_PATH}"
        )

    all_profiles = {}

    for file_path in csv_files:

        print(f"Profiling: {file_path.name}")

        try:
            profile = profile_file(file_path)
            all_profiles[file_path.name] = profile

            print(
                f"  Rows: {profile['rows']:,} | "
                f"Columns: {profile['columns']}"
            )

        except Exception as error:
            print(f"  ERROR: {error}")

    output_file = OUTPUT_PATH / "data_profile.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(all_profiles, file, indent=2)

    print("\nProfiling complete.")
    print(f"Profile saved to: {output_file}")


if __name__ == "__main__":
    main()