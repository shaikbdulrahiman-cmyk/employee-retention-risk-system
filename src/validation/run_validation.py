
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

errors = []
warnings = []


def load_csv(folder, filename):
    path = folder / filename

    if not path.exists():
        errors.append(f"Missing file: {filename}")
        return None

    try:
        return pd.read_csv(path)
    except Exception as exc:
        errors.append(f"Could not read {filename}: {exc}")
        return None


def check_unique(df, column, name):
    if df is None:
        return

    if column not in df.columns:
        errors.append(f"{name}: missing column {column}")
        return

    if df[column].isna().any():
        errors.append(f"{name}: null values in {column}")
    elif df[column].duplicated().any():
        errors.append(f"{name}: duplicate {column} values")
    else:
        print(f"PASS: {name} unique {column}")


def check_foreign_key(child, column, parent, parent_column, name):
    if child is None or parent is None:
        return

    if column not in child.columns or parent_column not in parent.columns:
        errors.append(f"{name}: required column missing")
        return

    invalid = child[column].isna() | ~child[column].isin(
        parent[parent_column]
    )

    if invalid.any():
        errors.append(f"{name}: {invalid.sum()} invalid references")
    else:
        print(f"PASS: {name} relationships valid")


def check_dates(df, column, name):
    if df is None or column not in df.columns:
        return

    dates = pd.to_datetime(df[column], errors="coerce")

    if dates.isna().any():
        errors.append(f"{name}: invalid or missing dates in {column}")
    else:
        print(f"PASS: {name} dates valid for {column}")


def check_date_order(df, start_col, end_col, name):
    if df is None:
        return

    if start_col not in df.columns or end_col not in df.columns:
        return

    start = pd.to_datetime(df[start_col], errors="coerce")
    end = pd.to_datetime(df[end_col], errors="coerce")

    invalid = end.notna() & start.notna() & (end < start)

    if invalid.any():
        errors.append(f"{name}: {invalid.sum()} invalid date sequences")
    else:
        print(f"PASS: {name} date ordering valid")


def main():
    print("EMPLOYEE RETENTION SYSTEM - DATA VALIDATION")
    print("=" * 55)

    employees = load_csv(RAW, "employees.csv")
    roles = load_csv(RAW, "roles.csv")
    teams = load_csv(RAW, "teams.csv")
    surveys = load_csv(RAW, "engagement_surveys.csv")
    workload = load_csv(RAW, "workload_snapshots.csv")
    tenure = load_csv(RAW, "tenure_snapshots.csv")
    compensation = load_csv(RAW, "compensation_bands.csv")
    promotions = load_csv(RAW, "promotion_history.csv")
    interventions = load_csv(RAW, "interventions.csv")
    attrition = load_csv(RAW, "attrition_outcomes.csv")
    risk = load_csv(PROCESSED, "employee_risk_analysis.csv")

    datasets = {
        "Employees": employees,
        "Roles": roles,
        "Teams": teams,
        "Surveys": surveys,
        "Workload": workload,
        "Tenure": tenure,
        "Compensation": compensation,
        "Promotions": promotions,
        "Interventions": interventions,
        "Attrition": attrition,
        "Risk analysis": risk
    }

    print("\n1. RECORD COUNTS")

    for name, df in datasets.items():
        if df is not None:
            print(f"{name}: {len(df):,} records")

    print("\n2. PRIMARY KEY CHECKS")

    primary_keys = [
        (employees, "employee_id", "Employees"),
        (roles, "role_id", "Roles"),
        (teams, "team_id", "Teams"),
        (surveys, "survey_id", "Surveys"),
        (workload, "workload_id", "Workload"),
        (tenure, "snapshot_id", "Tenure"),
        (compensation, "comp_band_id", "Compensation"),
        (promotions, "promotion_id", "Promotions"),
        (interventions, "intervention_id", "Interventions"),
        (attrition, "outcome_id", "Attrition"),
        (risk, "employee_id", "Risk analysis")
    ]

    for df, column, name in primary_keys:
        check_unique(df, column, name)

    print("\n3. FOREIGN KEY CHECKS")

    relationships = [
        (employees, "role_id", roles, "role_id", "Employee-role"),
        (employees, "team_id", teams, "team_id", "Employee-team"),
        (surveys, "employee_id", employees, "employee_id", "Survey-employee"),
        (workload, "employee_id", employees, "employee_id", "Workload-employee"),
        (tenure, "employee_id", employees, "employee_id", "Tenure-employee"),
        (compensation, "role_id", roles, "role_id", "Compensation-role"),
        (promotions, "employee_id", employees, "employee_id", "Promotion-employee"),
        (promotions, "previous_role_id", roles, "role_id", "Promotion-previous-role"),
        (promotions, "new_role_id", roles, "role_id", "Promotion-new-role"),
        (interventions, "employee_id", employees, "employee_id", "Intervention-employee"),
        (attrition, "employee_id", employees, "employee_id", "Attrition-employee"),
        (risk, "employee_id", employees, "employee_id", "Risk-employee")
    ]

    for child, column, parent, parent_column, name in relationships:
        check_foreign_key(child, column, parent, parent_column, name)

    print("\n4. EMPLOYEE AND BUSINESS RULE CHECKS")

    if employees is not None:
        if len(employees) == 10000:
            print("PASS: Exactly 10,000 employees")
        else:
            errors.append("Expected exactly 10,000 employees")

    print("\n5. DATE VALIDATION")

    check_dates(employees, "hire_date", "Employees")
    check_dates(surveys, "survey_date", "Surveys")
    check_dates(workload, "week_start_date", "Workload")
    check_dates(tenure, "snapshot_date", "Tenure")
    check_dates(promotions, "promotion_date", "Promotions")
    check_dates(interventions, "intervention_date", "Interventions")
    check_dates(attrition, "feature_cutoff_date", "Attrition")
    check_dates(attrition, "outcome_horizon_end", "Attrition")

    if interventions is not None:
        check_dates(interventions, "follow_up_date", "Interventions")

        if "completion_date" in interventions.columns:
            completed_dates = interventions.loc[
                interventions["status"] == "Completed",
                "completion_date"
            ]
            if completed_dates.isna().any():
                errors.append("Completed interventions need completion dates")
            else:
                print("PASS: Completed interventions have completion dates")

    check_date_order(
        compensation,
        "effective_start_date",
        "effective_end_date",
        "Compensation"
    )

    check_date_order(
        interventions,
        "intervention_date",
        "follow_up_date",
        "Interventions"
    )

    print("\n6. SURVEY VALIDATION")

    if surveys is not None:
        score_columns = [
            "engagement_score",
            "manager_support_score",
            "work_life_balance_score",
            "career_growth_score",
            "recognition_score"
        ]

        for column in score_columns:
            if column not in surveys.columns:
                errors.append(f"Survey missing {column}")
                continue

            values = pd.to_numeric(surveys[column], errors="coerce")
            invalid = values.notna() & ~values.between(1, 5)

            if invalid.any():
                errors.append(f"Invalid scores in {column}")
            else:
                print(f"PASS: {column} within 1-5 scale")

        if "response_status" in surveys.columns:
            print("\nSurvey response distribution:")
            print(surveys["response_status"].value_counts(dropna=False))

    print("\n7. TENURE VALIDATION")

    if tenure is not None:
        if "tenure_months" in tenure.columns:
            values = pd.to_numeric(
                tenure["tenure_months"], errors="coerce"
            )

            if values.isna().any() or (values < 0).any():
                errors.append("Invalid tenure_months values")
            else:
                print("PASS: Tenure months are non-negative")

        if {"tenure_months", "tenure_years"}.issubset(tenure.columns):
            months = pd.to_numeric(tenure["tenure_months"], errors="coerce")
            years = pd.to_numeric(tenure["tenure_years"], errors="coerce")

            if not (months.div(12).sub(years).abs() <= 0.01).all():
                errors.append("Tenure months and years do not reconcile")
            else:
                print("PASS: Tenure months and years reconcile")

    print("\n8. INTERVENTION LIFECYCLE VALIDATION")

    if interventions is not None:
        allowed_statuses = [
            "Planned", "In Progress", "Completed", "Cancelled"
        ]

        if "status" in interventions.columns:
            invalid = ~interventions["status"].isin(allowed_statuses)

            if invalid.any():
                errors.append("Invalid intervention lifecycle statuses")
            else:
                print("PASS: Intervention statuses are valid")

        if "intervention_outcome" in interventions.columns:
            completed = interventions["status"] == "Completed"
            cancelled = interventions["status"] == "Cancelled"
            pending = interventions["status"].isin(["Planned", "In Progress"])

            invalid_completed = (
                completed
                & interventions["intervention_outcome"].isin(
                    ["Pending evaluation", "Not evaluated - cancelled"]
                )
            )

            invalid_cancelled = (
                cancelled
                & (interventions["intervention_outcome"] !=
                   "Not evaluated - cancelled")
            )

            invalid_pending = (
                pending
                & (interventions["intervention_outcome"] !=
                   "Pending evaluation")
            )

            if (invalid_completed | invalid_cancelled | invalid_pending).any():
                errors.append("Intervention status and outcome are inconsistent")
            else:
                print("PASS: Intervention status and outcome consistency")

        print("\nIntervention status distribution:")
        print(interventions["status"].value_counts())

    print("\n9. ATTRITION VALIDATION")

    if attrition is not None:
        required = [
            "outcome_label",
            "termination_date",
            "feature_cutoff_date",
            "outcome_horizon_end"
        ]

        if all(column in attrition.columns for column in required):
            labels = attrition["outcome_label"].astype(str).str.strip()

            allowed_labels = ["Voluntary Attrition", "No Attrition"]

            if not labels.isin(allowed_labels).all():
                errors.append("Invalid attrition outcome labels")
            else:
                print("PASS: Attrition labels are valid")

            cutoff = pd.to_datetime(
                attrition["feature_cutoff_date"], errors="coerce"
            )
            horizon = pd.to_datetime(
                attrition["outcome_horizon_end"], errors="coerce"
            )
            termination = pd.to_datetime(
                attrition["termination_date"], errors="coerce"
            )

            positive = labels == "Voluntary Attrition"
            negative = labels == "No Attrition"

            invalid_positive = (
                positive
                & (
                    termination.isna()
                    | (termination <= cutoff)
                    | (termination > horizon)
                )
            )

            invalid_negative = negative & termination.notna()

            if invalid_positive.any():
                errors.append(
                    f"{invalid_positive.sum()} attrition outcomes have "
                    "invalid termination dates"
                )
            else:
                print("PASS: Attrition termination dates within outcome horizon")

            if invalid_negative.any():
                errors.append("No Attrition records contain termination dates")
            else:
                print("PASS: No Attrition records have termination dates")

            rate = positive.mean()
            print(f"Attrition rate: {rate:.2%}")

            if 0.05 <= rate <= 0.15:
                print("PASS: Attrition rate within 5%-15% target")
            else:
                errors.append("Attrition rate outside 5%-15% target")
        else:
            errors.append("Attrition dataset missing required columns")

    print("\n10. RISK ANALYSIS VALIDATION")

    if risk is not None:
        if "risk_score" in risk.columns:
            scores = pd.to_numeric(risk["risk_score"], errors="coerce")

            if scores.isna().any() or not scores.between(0, 100).all():
                errors.append("Invalid risk scores")
            else:
                print("PASS: Risk scores between 0 and 100")

        if "risk_category" in risk.columns:
            allowed_categories = ["Low", "Medium", "High"]

            if not risk["risk_category"].isin(allowed_categories).all():
                errors.append("Invalid risk categories")
            else:
                print("PASS: Risk categories are valid")

        if employees is not None:
            if set(risk["employee_id"]) != set(employees["employee_id"]):
                errors.append("Risk analysis employee coverage does not match")
            else:
                print("PASS: Risk analysis covers all employees")

    print("\n11. FINAL VALIDATION SUMMARY")
    print("=" * 55)

    for warning in warnings:
        print("WARNING:", warning)

    for error in errors:
        print("FAIL:", error)

    if errors:
        print(f"\nVALIDATION FAILED: {len(errors)} error(s)")
    else:
        print("\nALL VALIDATION CHECKS PASSED!")

    print("Total errors:", len(errors))
    print("Total warnings:", len(warnings))


if __name__ == "__main__":
    main()
