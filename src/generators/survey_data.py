import pandas as pd
import numpy as np

from config import RANDOM_SEED


def generate_survey_data(employees):
    rng = np.random.default_rng(RANDOM_SEED)

    survey_dates = pd.date_range(
        start="2024-10-01",
        end="2026-10-01",
        freq="3MS"
    )

    survey_records = []
    survey_number = 1

    score_columns = [
        "engagement_score",
        "manager_support_score",
        "work_life_balance_score",
        "career_growth_score",
        "recognition_score"
    ]

    for _, employee in employees.iterrows():

        hire_date = pd.to_datetime(employee["hire_date"])

        for survey_date in survey_dates:

            if survey_date < hire_date:
                continue

            # Simulate missing survey responses
            is_missing = rng.random() < 0.15

            record = {
                "survey_id": f"SURV-{survey_number:06d}",
                "employee_id": employee["employee_id"],
                "survey_date": survey_date.strftime("%Y-%m-%d"),
                "response_status": (
                    "Missing" if is_missing else "Completed"
                )
            }

            if is_missing:
                for column in score_columns:
                    record[column] = np.nan

            else:
                for column in score_columns:
                    record[column] = int(rng.integers(1, 6))

            survey_records.append(record)
            survey_number += 1

    return pd.DataFrame(survey_records)


if __name__ == "__main__":

    employees = pd.read_csv("data/raw/employees.csv")

    surveys = generate_survey_data(employees)

    surveys.to_csv(
        "data/raw/engagement_surveys.csv",
        index=False
    )

    print("Engagement survey data generated successfully!")
    print("Total survey records:", len(surveys))
    print("Unique employees:", surveys["employee_id"].nunique())
    print(
        "Completed surveys:",
        (surveys["response_status"] == "Completed").sum()
    )
    print(
        "Missing surveys:",
        (surveys["response_status"] == "Missing").sum()
    )