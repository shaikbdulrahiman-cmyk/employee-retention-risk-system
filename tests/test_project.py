
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"


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
    risk = pd.read_csv(
        PROCESSED / "employee_risk_analysis.csv"
    )
    assert risk["risk_score"].between(0, 100).all()


def test_risk_categories_are_valid():
    risk = pd.read_csv(
        PROCESSED / "employee_risk_analysis.csv"
    )
    assert set(risk["risk_category"].unique()).issubset(
        {"Low", "Medium", "High"}
    )


def test_risk_analysis_has_all_employees():
    risk = pd.read_csv(
        PROCESSED / "employee_risk_analysis.csv"
    )
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
