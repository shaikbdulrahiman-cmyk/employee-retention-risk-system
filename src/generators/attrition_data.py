
import pandas as pd
import numpy as np

from config import RANDOM_SEED


FEATURE_CUTOFF_DATE = pd.Timestamp("2026-10-01")
OUTCOME_END_DATE = pd.Timestamp("2027-04-01")


def generate_attrition_data(employees, surveys, workload):

    rng = np.random.default_rng(RANDOM_SEED + 3)

    outcomes = []

    for _, employee in employees.iterrows():

        employee_id = employee["employee_id"]

        # Use only information available on or before cutoff
        employee_surveys = surveys[
            (surveys["employee_id"] == employee_id)
            & (surveys["survey_date"] <= FEATURE_CUTOFF_DATE.strftime("%Y-%m-%d"))
            & (surveys["response_status"] == "Completed")
        ]

        employee_workload = workload[
            (workload["employee_id"] == employee_id)
            & (workload["week_start_date"] <= FEATURE_CUTOFF_DATE.strftime("%Y-%m-%d"))
        ]

        # Calculate recent engagement
        if not employee_surveys.empty:
            latest_survey = employee_surveys.sort_values(
                "survey_date"
            ).iloc[-1]

            engagement = latest_survey["engagement_score"]
        else:
            engagement = np.nan

        # Calculate recent workload
        recent_workload = employee_workload.tail(12)

        if not recent_workload.empty:
            average_hours = recent_workload["working_hours"].mean()
        else:
            average_hours = 40

        # Documented risk-based simulation
        attrition_probability = 0.08

        if pd.notna(engagement):
            if engagement <= 2:
                attrition_probability += 0.04
            elif engagement >= 4:
                attrition_probability -= 0.02

        if average_hours >= 55:
            attrition_probability += 0.03
        elif average_hours >= 48:
            attrition_probability += 0.01

        attrition_probability = float(
            np.clip(attrition_probability, 0.05, 0.15)
        )

        # Simulate future voluntary attrition event
        voluntary_attrition = (
            rng.random() < attrition_probability
        )

        if voluntary_attrition:
            days = int(
                rng.integers(
                    1,
                    (OUTCOME_END_DATE - FEATURE_CUTOFF_DATE).days + 1
                )
            )

            termination_date = (
                FEATURE_CUTOFF_DATE
                + pd.Timedelta(days=days)
            ).strftime("%Y-%m-%d")

            outcome_label = "Voluntary Attrition"
        else:
            termination_date = None
            outcome_label = "No Attrition"

        outcomes.append({
            "outcome_id": f"OUT-{employee_id}-2027",
            "employee_id": employee_id,
            "feature_cutoff_date": FEATURE_CUTOFF_DATE.strftime("%Y-%m-%d"),
            "outcome_horizon_end": OUTCOME_END_DATE.strftime("%Y-%m-%d"),
            "termination_date": termination_date,
            "outcome_label": outcome_label,
            "attrition_probability_used": round(
                attrition_probability, 4
            )
        })

    return pd.DataFrame(outcomes)


if __name__ == "__main__":

    employees = pd.read_csv("data/raw/employees.csv")
    surveys = pd.read_csv("data/raw/engagement_surveys.csv")
    workload = pd.read_csv("data/raw/workload_snapshots.csv")

    outcomes = generate_attrition_data(
        employees,
        surveys,
        workload
    )

    outcomes.to_csv(
        "data/raw/attrition_outcomes.csv",
        index=False
    )

    print("Attrition outcomes generated successfully!")
    print("Total employees:", len(outcomes))
    print("Unique employees:", outcomes["employee_id"].nunique())

    print("\nOutcome distribution:")
    print(outcomes["outcome_label"].value_counts())

    print(
        "\nAttrition rate:",
        round(
            (outcomes["outcome_label"] == "Voluntary Attrition").mean() * 100,
            2
        ),
        "%"
    )
