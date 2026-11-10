
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
GROUND_TRUTH = ROOT / "data" / "ground_truth.csv"

FEATURE_CUTOFF = pd.Timestamp("2026-10-01")


# Existing project tests

def test_employee_count():
    employees = pd.read_csv(RAW / "employees.csv")
    assert len(employees) == 10000


def test_employee_ids_are_unique():
    employees = pd.read_csv(RAW / "employees.csv")
    assert employees["employee_id"].is_unique


def test_employee_role_relationships():
    employees = pd.read_csv(RAW / "employees.csv")
    roles = pd.read_csv(RAW / "roles.csv")
    assert employees["role_id"].isin(roles["role_id"]).all()


def test_employee_team_relationships():
    employees = pd.read_csv(RAW / "employees.csv")
    teams = pd.read_csv(RAW / "teams.csv")
    assert employees["team_id"].isin(teams["team_id"]).all()


def test_risk_scores_are_valid():
    risk = pd.read_csv(PROCESSED / "employee_risk_analysis.csv")
    assert risk["risk_score"].between(0, 100).all()


def test_risk_categories_are_valid():
    risk = pd.read_csv(PROCESSED / "employee_risk_analysis.csv")
    assert set(risk["risk_category"].dropna().unique()).issubset(
        {"Low", "Medium", "High"}
    )


def test_risk_analysis_has_all_employees():
    risk = pd.read_csv(PROCESSED / "employee_risk_analysis.csv")
    assert len(risk) == 10000
    assert risk["employee_id"].is_unique


def test_attrition_outcomes_are_unique():
    attrition = pd.read_csv(RAW / "attrition_outcomes.csv")
    assert attrition["outcome_id"].is_unique
    assert attrition["employee_id"].is_unique


def test_survey_scores_are_valid():
    surveys = pd.read_csv(RAW / "engagement_surveys.csv")

    score_columns = [
        column for column in surveys.columns
        if "score" in column.lower()
    ]

    for column in score_columns:
        values = surveys[column].dropna()
        assert values.between(1, 5).all()


def test_intervention_employee_ids_are_valid():
    employees = pd.read_csv(RAW / "employees.csv")
    interventions = pd.read_csv(RAW / "interventions.csv")

    assert interventions["employee_id"].isin(
        employees["employee_id"]
    ).all()


# New edge-case and assignment requirement tests

def test_future_information_is_not_used():
    risk = pd.read_csv(PROCESSED / "employee_risk_analysis.csv")

    assert "latest_survey_date" in risk.columns
    assert "latest_workload_date" in risk.columns

    survey_dates = pd.to_datetime(
        risk["latest_survey_date"], errors="coerce"
    )
    workload_dates = pd.to_datetime(
        risk["latest_workload_date"], errors="coerce"
    )

    assert survey_dates.dropna().le(FEATURE_CUTOFF).all()
    assert workload_dates.dropna().le(FEATURE_CUTOFF).all()


def test_missing_surveys_do_not_add_risk_points():
    risk = pd.read_csv(PROCESSED / "employee_risk_analysis.csv")

    missing = risk[risk["survey_missing"] == True].copy()

    assert len(missing) > 0

    for _, row in missing.iterrows():
        expected_score = 0

        if row["average_working_hours"] >= 55:
            expected_score += 30
        elif row["average_working_hours"] >= 48:
            expected_score += 15

        if row["average_overtime"] >= 15:
            expected_score += 20

        assert row["risk_score"] == min(expected_score, 100)
        assert "No recent completed survey" in row["risk_reason"]


def test_attrition_outcomes_match_termination_dates():
    attrition = pd.read_csv(RAW / "attrition_outcomes.csv")

    attrition["termination_date"] = pd.to_datetime(
        attrition["termination_date"], errors="coerce"
    )
    attrition["feature_cutoff_date"] = pd.to_datetime(
        attrition["feature_cutoff_date"]
    )
    attrition["outcome_horizon_end"] = pd.to_datetime(
        attrition["outcome_horizon_end"]
    )

    voluntary = attrition[
        attrition["outcome_label"] == "Voluntary Attrition"
    ]

    no_attrition = attrition[
        attrition["outcome_label"] == "No Attrition"
    ]

    assert voluntary["termination_date"].notna().all()

    assert (
        voluntary["termination_date"]
        > voluntary["feature_cutoff_date"]
    ).all()

    assert (
        voluntary["termination_date"]
        <= voluntary["outcome_horizon_end"]
    ).all()

    assert no_attrition["termination_date"].isna().all()


def test_risk_scores_have_explanations_and_human_review():
    risk = pd.read_csv(PROCESSED / "employee_risk_analysis.csv")

    assert risk["risk_reason"].notna().all()
    assert risk["risk_reason"].str.strip().ne("").all()

    expected_review = risk["risk_category"].isin(
        ["Medium", "High"]
    )

    assert (
        risk["human_review_required"] == expected_review
    ).all()

    assert risk["review_recommendation"].notna().all()


def test_ground_truth_cases_are_separate_from_model_inputs():
    ground_truth = pd.read_csv(GROUND_TRUTH)

    expected_cases = {
        "GT-001",
        "GT-002",
        "GT-003",
        "GT-004"
    }

    assert set(ground_truth["case_id"]) == expected_cases
    assert len(ground_truth) == 4

    assert (
        ground_truth["used_as_model_input"].str.lower() == "no"
    ).all()
