
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

FEATURE_CUTOFF_DATE = "2026-10-01"


def generate_risk_analysis():
    employees = pd.read_csv(RAW / "employees.csv")
    surveys = pd.read_csv(RAW / "engagement_surveys.csv")
    workload = pd.read_csv(RAW / "workload_snapshots.csv")

    cutoff = pd.Timestamp(FEATURE_CUTOFF_DATE)

    # Keep only completed surveys available at the cutoff.
    surveys["survey_date"] = pd.to_datetime(surveys["survey_date"])

    surveys = surveys[
        (surveys["survey_date"] <= cutoff)
        & (surveys["response_status"] == "Completed")
    ].copy()

    surveys = surveys.sort_values(
        ["employee_id", "survey_date"]
    )

    latest_survey = surveys.groupby(
        "employee_id"
    ).tail(1)

    latest_survey = latest_survey[
        [
            "employee_id",
            "engagement_score",
            "survey_date"
        ]
    ].rename(
        columns={"survey_date": "latest_survey_date"}
    )

    # Keep only workload records available at the cutoff.
    workload["week_start_date"] = pd.to_datetime(
        workload["week_start_date"]
    )

    workload = workload[
        workload["week_start_date"] <= cutoff
    ].copy()

    workload = workload.sort_values(
        ["employee_id", "week_start_date"]
    )

    recent_workload = workload.groupby(
        "employee_id"
    ).tail(12)

    workload_summary = recent_workload.groupby(
        "employee_id"
    ).agg(
        average_working_hours=("working_hours", "mean"),
        average_overtime=("overtime_hours", "mean"),
        latest_workload_date=("week_start_date", "max")
    ).reset_index()

    # Combine employee master data with historical features.
    result = employees.merge(
        latest_survey,
        on="employee_id",
        how="left",
        validate="one_to_one"
    )

    result = result.merge(
        workload_summary,
        on="employee_id",
        how="left",
        validate="one_to_one"
    )

    # Preserve missing survey information.
    result["survey_missing"] = (
        result["engagement_score"].isna()
    )

    # Missing workload is explicitly identified.
    result["workload_data_missing"] = (
        result["average_working_hours"].isna()
    )

    # Neutral fallback values; missing data adds no risk points.
    result["average_working_hours"] = (
        result["average_working_hours"].fillna(40)
    )

    result["average_overtime"] = (
        result["average_overtime"].fillna(0)
    )

    scores = []
    reasons = []

    for _, row in result.iterrows():
        score = 0
        employee_reasons = []

        if row["survey_missing"]:
            employee_reasons.append(
                "No recent completed survey; engagement not scored"
            )
        elif row["engagement_score"] <= 2:
            score += 35
            employee_reasons.append("Low engagement")

        if row["average_working_hours"] >= 55:
            score += 30
            employee_reasons.append("High working hours")
        elif row["average_working_hours"] >= 48:
            score += 15
            employee_reasons.append("Elevated working hours")

        if row["average_overtime"] >= 15:
            score += 20
            employee_reasons.append("High overtime")

        if (
            not row["survey_missing"]
            and row["engagement_score"] >= 4
        ):
            score = max(0, score - 10)
            employee_reasons.append(
                "Positive engagement signal"
            )

        scores.append(min(score, 100))

        reasons.append(
            "; ".join(employee_reasons)
            if employee_reasons
            else "No major risk signals detected"
        )

    result["risk_score"] = scores
    result["risk_reason"] = reasons

    result["risk_category"] = pd.cut(
        result["risk_score"],
        bins=[-1, 19, 49, 100],
        labels=["Low", "Medium", "High"]
    )

    result["review_recommendation"] = result[
        "risk_category"
    ].map({
        "Low": "Routine check-in",
        "Medium": "Consider supportive human review",
        "High": "Prioritize human review and support"
    })

    result["human_review_required"] = (
        result["risk_category"].isin(["Medium", "High"])
    )

    # Record the feature cutoff for auditability.
    result["feature_cutoff_date"] = FEATURE_CUTOFF_DATE

    return result


if __name__ == "__main__":
    analysis = generate_risk_analysis()

    PROCESSED.mkdir(parents=True, exist_ok=True)

    analysis.to_csv(
        PROCESSED / "employee_risk_analysis.csv",
        index=False
    )

    print("Employee risk analysis completed!")
    print("Total employees:", len(analysis))

    print("\nRisk distribution:")
    print(analysis["risk_category"].value_counts())

    print("\nMissing-data summary:")
    print(
        "Employees without a completed survey:",
        int(analysis["survey_missing"].sum())
    )
    print(
        "Employees without workload records:",
        int(analysis["workload_data_missing"].sum())
    )

    print("\nEmployees requiring human review:")
    print(
        int(analysis["human_review_required"].sum())
    )

    print("\nTop 10 employees for human review:")
    print(
        analysis.nlargest(10, "risk_score")[
            [
                "employee_id",
                "risk_score",
                "risk_category",
                "risk_reason",
                "review_recommendation",
                "human_review_required"
            ]
        ].to_string(index=False)
    )
