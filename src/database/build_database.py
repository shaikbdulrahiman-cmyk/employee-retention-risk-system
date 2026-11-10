
import sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
DB_PATH = ROOT / "data" / "employee_retention.db"


def build_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    csv_files = list(RAW_DIR.glob("*.csv"))
    csv_files += list(PROCESSED_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError("No CSV files found.")

    with sqlite3.connect(DB_PATH) as connection:
        for file_path in csv_files:
            table_name = file_path.stem
            df = pd.read_csv(file_path)

            df.to_sql(
                table_name,
                connection,
                if_exists="replace",
                index=False
            )

            print(f"Created table: {table_name} ({len(df):,} rows)")

        tables = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table'",
            connection
        )

    print("\nDatabase created successfully!")
    print("Database:", DB_PATH)
    print("Total tables:", len(tables))


if __name__ == "__main__":
    build_database()
