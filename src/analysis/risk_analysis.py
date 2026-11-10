
import pandas as pd


def generate_risk_analysis():
    employees = pd.read_csv("data/raw/employees.csv")
    surveys = pd.read_csv("data/raw/engagement_surveys.csv")
    workload = pd.read_csv("data/raw/workload_snapshots.csv")

    cutoff = "2026-10-01"

    # Latest completed survey available at cutoff
    surveys = surveys[
        (surveys["survey_date"] <= cutoff)
        & (surveys["response_status"] == "Completed")
    ].copy()

    surveys = surveys.sort_values("survey_date")
    latest_survey = surveys.groupby("employee_id").tail(1)

    # Recent workload available at cutoff
    workload = workload[
        workload["week_start_date"] <= cutoff
    ].copy()

    recent_workload = workload.groupby("employee_id").tail(12)

    workload_summary = recent_workload.groupby(
        "employee_id"
    ).agg(
        average_working_hours=("working_hours", "mean"),
        average_overtime=("overtime_hours", "mean")
    ).reset_index()

    result = employees.merge(
        latest_survey[
            ["employee_id", "engagement_score"]
        ],
        on="employee_id",
        how="left"
    )

    result = result.merge(
        workload_summary,
        on="employee_id",
        how="left"
    )

    result["engagement_score"] = result[
        "engagement_score"
    ].fillna(-1)

    result["average_working_hours"] = result[
        "average_working_hours"
    ].fillna(40)

    result["average_overtime"] = result[
        "average_overtime"
    ].fillna(0)

    scores = []
    reasons = []

    for _, row in result.iterrows():
        score = 0
        employee_reasons = []

        if row["engagement_score"] == -1:
            employee_reasons.append("No recent completed survey")
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

        if row["engagement_score"] >= 4:
            score = max(0, score - 10)

        scores.append(min(score, 100))
        reasons.append(
            "; ".join(employee_reasons)
            if employee_reasons else "No major risk signals detected"
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
        "Medium": "Consider supportive check-in",
        "High": "Prioritize human review and support"
    })

    return result


if __name__ == "__main__":
    analysis = generate_risk_analysis()

    analysis.to_csv(
        "data/processed/employee_risk_analysis.csv",
        index=False
    )

    print("Employee risk analysis completed!")
    print("Total employees:", len(analysis))
    print("\nRisk distribution:")
    print(analysis["risk_category"].value_counts())
    print("\nTop 10 employees for human review:")
    print(
        analysis.nlargest(10, "risk_score")[
            ["employee_id", "risk_score",
             "risk_category", "risk_reason"]
        ].to_string(index=False)
    )
