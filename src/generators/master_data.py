import pandas as pd
import numpy as np
from faker import Faker
from datetime import date
from config import NUM_EMPLOYEES, RANDOM_SEED

fake = Faker()
Faker.seed(RANDOM_SEED)
rng = np.random.default_rng(RANDOM_SEED)


def generate_master_data():
    employees = []
    roles = []
    teams = []

    role_names = [
        "Software Engineer",
        "Data Analyst",
        "HR Executive",
        "Business Analyst",
        "Project Manager",
        "QA Engineer"
    ]

    team_names = [
        "Engineering",
        "Data Science",
        "Human Resources",
        "Operations",
        "Quality Assurance"
    ]

    role_ids = [f"ROLE-{i:03d}" for i in range(1, len(role_names) + 1)]
    team_ids = [f"TEAM-{i:03d}" for i in range(1, len(team_names) + 1)]

    # Generate employee master records
    for i in range(1, NUM_EMPLOYEES + 1):
        hire_date = fake.date_between(
            start_date=date(2018, 10, 1),
            end_date=date(2026, 9, 1)
        )

        employees.append({
            "employee_id": f"EMP-{i:06d}",
            "employee_name": fake.name(),
            "email": f"employee{i}@example.com",
            "hire_date": hire_date.isoformat(),
            "role_id": rng.choice(role_ids),
            "team_id": rng.choice(team_ids),
            "employment_status": "Active"
        })

    # Generate role master records
    for i, role in enumerate(role_names, start=1):
        roles.append({
            "role_id": f"ROLE-{i:03d}",
            "role_name": role
        })

    # Generate team master records
    for i, team in enumerate(team_names, start=1):
        teams.append({
            "team_id": f"TEAM-{i:03d}",
            "team_name": team
        })

    return (
        pd.DataFrame(employees),
        pd.DataFrame(roles),
        pd.DataFrame(teams)
    )


if __name__ == "__main__":
    employees, roles, teams = generate_master_data()

    employees.to_csv("data/raw/employees.csv", index=False)
    roles.to_csv("data/raw/roles.csv", index=False)
    teams.to_csv("data/raw/teams.csv", index=False)

    print("Master data generated successfully!")
    print("Employees:", len(employees))
    print("Roles:", len(roles))
    print("Teams:", len(teams))
    print("Unique employee IDs:", employees["employee_id"].nunique())