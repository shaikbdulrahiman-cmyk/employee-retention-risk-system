import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta

from config import RANDOM_SEED


def generate_tenure_data(employees):
    records = []

    end_date = date(2026, 10, 1)
    start_date = end_date - relativedelta(months=24)

    for _, employee in employees.iterrows():
        hire_date = pd.to_datetime(employee["hire_date"]).date()

        for month in range(25):
            snapshot_date = start_date + relativedelta(months=month)

            if snapshot_date < hire_date:
                continue

            tenure_months = (
                (snapshot_date.year - hire_date.year) * 12
                + snapshot_date.month - hire_date.month
            )

            records.append({
                "snapshot_id": (
                    f"SNAP-{employee['employee_id']}-"
                    f"{snapshot_date.strftime('%Y%m')}"
                ),
                "employee_id": employee["employee_id"],
                "snapshot_date": snapshot_date.isoformat(),
                "tenure_months": tenure_months,
                "tenure_years": round(tenure_months / 12, 2)
            })

    return pd.DataFrame(records)


if __name__ == "__main__":
    employees = pd.read_csv("data/raw/employees.csv")

    tenure = generate_tenure_data(employees)

    tenure.to_csv("data/raw/tenure_snapshots.csv", index=False)

    print("Tenure history generated successfully!")
    print("Total records:", len(tenure))
    print("Unique employees:", tenure["employee_id"].nunique())