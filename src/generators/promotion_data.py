
import pandas as pd
import numpy as np

from config import RANDOM_SEED


def generate_promotion_data(employees, roles):
    rng = np.random.default_rng(RANDOM_SEED + 2)

    start_date = pd.Timestamp("2024-10-01")
    end_date = pd.Timestamp("2026-09-30")

    role_ids = roles["role_id"].tolist()

    records = []
    updated_employees = employees.copy()
    promotion_number = 1

    # Approximately 12% of employees receive a promotion
    promotion_count = int(len(employees) * 0.12)

    selected_indices = rng.choice(
        employees.index.to_numpy(),
        size=promotion_count,
        replace=False
    )

    for index in selected_indices:
        employee = updated_employees.loc[index]

        hire_date = pd.to_datetime(employee["hire_date"])

        earliest_date = max(start_date, hire_date)

        if earliest_date > end_date:
            continue

        days_available = (end_date - earliest_date).days

        promotion_date = earliest_date + pd.Timedelta(
            days=int(rng.integers(0, days_available + 1))
        )

        previous_role = employee["role_id"]

        available_roles = [
            role_id for role_id in role_ids
            if role_id != previous_role
        ]

        new_role = rng.choice(available_roles)

        promotion_type = rng.choice([
            "Level Promotion",
            "Internal Role Change"
        ])

        records.append({
            "promotion_id": f"PROM-{promotion_number:06d}",
            "employee_id": employee["employee_id"],
            "previous_role_id": previous_role,
            "new_role_id": new_role,
            "promotion_date": promotion_date.strftime("%Y-%m-%d"),
            "promotion_type": promotion_type
        })

        # Keep the employee's current role consistent
        updated_employees.loc[index, "role_id"] = new_role

        promotion_number += 1

    promotion_history = pd.DataFrame(records)

    return promotion_history, updated_employees


if __name__ == "__main__":

    employees = pd.read_csv("data/raw/employees.csv")
    roles = pd.read_csv("data/raw/roles.csv")

    promotions, updated_employees = generate_promotion_data(
        employees, roles
    )

    promotions.to_csv(
        "data/raw/promotion_history.csv",
        index=False
    )

    updated_employees.to_csv(
        "data/raw/employees.csv",
        index=False
    )

    print("Promotion history generated successfully!")
    print("Total promotions:", len(promotions))
    print(
        "Unique employees promoted:",
        promotions["employee_id"].nunique()
    )
    print(
        "Updated employee records:",
        len(updated_employees)
    )
