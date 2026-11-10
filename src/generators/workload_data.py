
import pandas as pd
import numpy as np

from config import RANDOM_SEED


def generate_workload_data(employees):
    rng = np.random.default_rng(RANDOM_SEED + 1)

    weeks = pd.date_range(
        start="2024-10-01",
        end="2026-10-01",
        freq="W-MON"
    )

    records = []
    record_number = 1

    for _, employee in employees.iterrows():
        hire_date = pd.to_datetime(employee["hire_date"])

        base_hours = rng.normal(40, 3)

        for week_date in weeks:
            if week_date < hire_date:
                continue

            working_hours = round(
                float(np.clip(rng.normal(base_hours, 5), 20, 65)), 1
            )

            overtime_hours = round(
                max(0, working_hours - 40), 1
            )

            active_projects = int(rng.integers(1, 5))

            # Some employees experience temporary high workloads
            if rng.random() < 0.10:
                working_hours = round(
                    float(rng.uniform(52, 65)), 1
                )
                overtime_hours = round(
                    working_hours - 40, 1
                )

            if working_hours >= 55:
                workload_level = "High"
            elif working_hours >= 45:
                workload_level = "Moderate"
            else:
                workload_level = "Normal"

            records.append({
                "workload_id": f"WORK-{record_number:08d}",
                "employee_id": employee["employee_id"],
                "week_start_date": week_date.strftime("%Y-%m-%d"),
                "working_hours": working_hours,
                "overtime_hours": overtime_hours,
                "active_projects": active_projects,
                "workload_level": workload_level
            })

            record_number += 1

    return pd.DataFrame(records)


if __name__ == "__main__":
    employees = pd.read_csv("data/raw/employees.csv")

    workload = generate_workload_data(employees)

    workload.to_csv(
        "data/raw/workload_snapshots.csv",
        index=False
    )

    print("Workload history generated successfully!")
    print("Total records:", len(workload))
    print("Unique employees:", workload["employee_id"].nunique())
    print("\nWorkload distribution:")
    print(workload["workload_level"].value_counts())
