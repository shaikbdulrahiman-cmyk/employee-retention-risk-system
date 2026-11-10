
import pandas as pd
import numpy as np

from config import RANDOM_SEED

FEATURE_CUTOFF_DATE = pd.Timestamp("2026-10-01")
OUTCOME_END_DATE = pd.Timestamp("2027-04-01")


def generate_attrition_data(employees, surveys, workload):
    rng = np.random.default_rng(RANDOM_SEED + 3)

    cutoff = FEATURE_CUTOFF_DATE.strftime("%Y-%m-%d")

    # Filter historical data once
    surveys = surveys[
        (surveys["survey_date"] <= cutoff)
        & (surveys["response_status"] == "Completed")
    ]

    workload = workload[
        workload["week_start_date"] <= cutoff
    ]

    # Prepare recent engagement by employee
    latest_surveys = (
        surveys.sort_values("survey_date")
        .drop_duplicates("employee_id", keep="last")
        .set_index("employee_id")
    )

    # Prepare average of latest 12 workload records
    recent_workload = (
        workload.sort_values("week_start_date")
        .groupby("employee_id")
        .tail(12)
    )

    average_workload = recent_workload.groupby(
        "employee_id"
    )["working_hours"].mean()

    # Vectorized employee features
    employee_ids = employees["employee_id"]

    engagement = employee_ids.map(
        latest_surveys["engagement_score"]
    )

    average_hours = employee_ids.map(
        average_workload
    ).fillna(40)

    probability = np.full(len(employees), 0.08)

    probability += np.where(
        engagement.notna() & (engagement <= 2), 0.04, 0
    )

    probability -= np.where(
        engagement.notna() & (engagement >= 4), 0.02, 0
    )

    probability += np.where(average_hours >= 55, 0.03, 0)
    probability += np.where(
        (average_hours >= 48) & (average_hours < 55), 0.01, 0
    )

    probability = np.clip(probability, 0.05, 0.15)

    outcomes = []

    for employee_id, attrition_probability in zip(
        employee_ids, probability
    ):
        voluntary_attrition = rng.random() < attrition_probability

        if voluntary_attrition:
            days = int(
                rng.integers(
                    1,
                    (OUTCOME_END_DATE - FEATURE_CUTOFF_DATE).days + 1
                )
            )

            termination_date = (
                FEATURE_CUTOFF_DATE + pd.Timedelta(days=days)
            ).strftime("%Y-%m-%d")

            outcome_label = "Voluntary Attrition"
        else:
            termination_date = None
            outcome_label = "No Attrition"

        outcomes.append({
            "outcome_id": f"OUT-{employee_id}-2027",
            "employee_id": employee_id,
            "feature_cutoff_date": cutoff,
            "outcome_horizon_end": OUTCOME_END_DATE.strftime("%Y-%m-%d"),
            "termination_date": termination_date,
            "outcome_label": outcome_label,
            "attrition_probability_used": round(
                float(attrition_probability), 4
            )
        })

    return pd.DataFrame(outcomes)
