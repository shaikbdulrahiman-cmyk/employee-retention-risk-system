
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

    return pd.read_csv(path)


def check_unique(df, column, name):
    if df is None:
        return

    if column not in df.columns:
        errors.append(f"{name}: missing column {column}")
        return

    if df[column].duplicated().any():
        errors.append(f"{name}: duplicate {column} values")
    else:
        print(f"PASS: {name} has unique {column}")


def check_foreign_key(child, column, parent, parent_column, name):
    if child is None or parent is None:
        return

    if column not in child.columns or parent_column not in parent.columns:
        errors.append(f"{name}: required column missing")
        return

    invalid = ~child[column].isin(parent[parent_column])

    if invalid.any():
        errors.append(f"{name}: {invalid.sum()} invalid references")
    else:
        print(f"PASS: {name} relationships valid")


def main():
    print("EMPLOYEE RETENTION SYSTEM - DATA VALIDATION")
    print("=" * 50)

    employees = load_csv(RAW, "employees.csv")
    roles = load_csv(RAW, "roles.csv")
    teams = load_csv(RAW, "teams.csv")
    surveys = load_csv(RAW, "engagement_surveys.csv")
    workload = load_csv(RAW, "workload_snapshots.csv")
    tenure = load_csv(RAW, "tenure_snapshots.csv")
    promotions = load_csv(RAW, "promotion_history.csv")
    interventions = load_csv(RAW, "interventions.csv")
    attrition = load_csv(RAW, "attrition_outcomes.csv")
    risk = load_csv(PROCESSED, "employee_risk_analysis.csv")

    print("\n1. RECORD COUNTS")

    datasets = {
        "Employees": employees,
        "Roles": roles,
        "Teams": teams,
        "Surveys": surveys,
        "Workload": workload,
        "Tenure": tenure,
        "Promotions": promotions,
        "Interventions": interventions,
        "Attrition outcomes": attrition,
        "Risk analysis": risk
    }

    for name, df in datasets.items():
        if df is not None:
            print(f"{name}: {len(df):,} records")

    print("\n2. PRIMARY KEY CHECKS")

    check_unique(employees, "employee_id", "Employees")
    check_unique(roles, "role_id", "Roles")
    check_unique(teams, "team_id", "Teams")
    check_unique(surveys, "survey_id", "Surveys")
    check_unique(workload, "workload_id", "Workload")
    check_unique(tenure, "snapshot_id", "Tenure")
    check_unique(promotions, "promotion_id", "Promotions")
    check_unique(interventions, "intervention_id", "Interventions")
    check_unique(attrition, "outcome_id", "Attrition")
    check_unique(risk, "employee_id", "Risk analysis")

    print("\n3. FOREIGN KEY CHECKS")

    check_foreign_key(
        employees, "role_id", roles, "role_id", "Employee-role"
    )

    check_foreign_key(
        employees, "team_id", teams, "team_id", "Employee-team"
    )

    for name, df in [
        ("Surveys", surveys),
        ("Workload", workload),
        ("Tenure", tenure),
        ("Promotions", promotions),
        ("Interventions", interventions),
        ("Attrition", attrition),
        ("Risk analysis", risk)
    ]:
        check_foreign_key(
            df, "employee_id", employees, "employee_id", name
        )

    print("\n4. BUSINESS RULE CHECKS")

    if employees is not None:
        if len(employees) == 10000:
            print("PASS: Exactly 10,000 employees generated")
        else:
            errors.append("Expected exactly 10,000 employees")

    # Attrition label validation
    if attrition is not None and "outcome_label" in attrition.columns:

        print("\nAttrition outcome values:")
        print(attrition["outcome_label"].value_counts())

        labels = (
            attrition["outcome_label"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        positive_labels = [
            "voluntary attrition",
            "voluntary",
            "attrition",
            "yes",
            "1",
            "true"
        ]

        rate = labels.isin(positive_labels).mean()

        print(f"Attrition rate: {rate:.2%}")

        if 0.05 <= rate <= 0.15:
            print("PASS: Attrition rate within 5%-15% target")
        else:
            errors.append("Attrition rate outside 5%-15% target")

    elif attrition is not None:
        errors.append("Missing outcome_label column")

    # Risk score validation
    if risk is not None:

        if "risk_score" in risk.columns:
            valid_scores = pd.to_numeric(
                risk["risk_score"], errors="coerce"
            ).between(0, 100).all()

            if valid_scores:
                print("PASS: Risk scores between 0 and 100")
            else:
                errors.append("Invalid risk scores found")

        if "risk_category" in risk.columns:
            valid_categories = risk["risk_category"].isin(
                ["Low", "Medium", "High"]
            ).all()

            if valid_categories:
                print("PASS: Risk categories are valid")
            else:
                errors.append("Invalid risk categories found")

        if len(risk) != 10000:
            errors.append("Risk analysis should contain 10,000 employees")

    print("\n5. FINAL VALIDATION SUMMARY")
    print("=" * 50)

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
