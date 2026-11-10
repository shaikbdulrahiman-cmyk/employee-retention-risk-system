
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Ensure the project root is available for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

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

    statuses = ["Planned", "In Progress", "Completed", "Cancelled"]
    status_probabilities = [0.10, 0.15, 0.65, 0.10]

    records = []

    for i, (_, employee) in enumerate(employees.iterrows(), start=1):

        if rng.random() > 0.25:
            continue

        employee_id = employee["employee_id"]
        action = rng.choice(actions)
        status = rng.choice(statuses, p=status_probabilities)

        intervention_date = pd.Timestamp("2026-10-15") + pd.Timedelta(
            days=int(rng.integers(0, 31))
        )

        follow_up_date = intervention_date + pd.Timedelta(
            days=int(rng.integers(14, 46))
        )

        if status == "Completed":
            outcome = rng.choice(
                [
                    "Positive response",
                    "No measurable change",
                    "Follow-up required"
                ],
                p=[0.55, 0.25, 0.20]
            )

            completion_date = intervention_date + pd.Timedelta(
                days=int(rng.integers(1, 8))
            )

        elif status == "Cancelled":
            outcome = "Not evaluated - cancelled"
            completion_date = None

        else:
            outcome = "Pending evaluation"
            completion_date = None

        records.append({
            "intervention_id": f"INT-2026-{i:06d}",
            "employee_id": employee_id,
            "intervention_date": intervention_date.strftime("%Y-%m-%d"),
            "intervention_type": action,
            "status": status,
            "follow_up_date": follow_up_date.strftime("%Y-%m-%d"),
            "completion_date": (
                completion_date.strftime("%Y-%m-%d")
                if completion_date is not None else None
            ),
            "intervention_outcome": outcome,
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

    print("\nIntervention status distribution:")
    print(interventions["status"].value_counts())

    print("\nIntervention outcome distribution:")
    print(interventions["intervention_outcome"].value_counts())
