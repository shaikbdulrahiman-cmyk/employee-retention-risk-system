
import pandas as pd
import numpy as np

from config import RANDOM_SEED


def generate_interventions(employees, surveys, workload):
    rng = np.random.default_rng(RANDOM_SEED + 4)

    actions = [
        "Manager Check-in",
        "Career Development Discussion",
        "Workload Adjustment",
        "Training Opportunity",
        "HR Support Conversation"
    ]

    records = []

    for i, (_, employee) in enumerate(employees.iterrows(), start=1):
        if rng.random() > 0.25:
            continue

        action = rng.choice(actions)

        records.append({
            "intervention_id": f"INT-2026-{i:06d}",
            "employee_id": employee["employee_id"],
            "intervention_date": "2026-10-15",
            "intervention_type": action,
            "status": "Completed",
            "notes": "Supportive employee development action"
        })

    return pd.DataFrame(records)


if __name__ == "__main__":
    employees = pd.read_csv("data/raw/employees.csv")
    surveys = pd.read_csv("data/raw/engagement_surveys.csv")
    workload = pd.read_csv("data/raw/workload_snapshots.csv")

    interventions = generate_interventions(
        employees, surveys, workload
    )

    interventions.to_csv(
        "data/raw/interventions.csv",
        index=False
    )

    print("Interventions generated successfully!")
    print("Total interventions:", len(interventions))
    print("Unique employees:", interventions["employee_id"].nunique())
