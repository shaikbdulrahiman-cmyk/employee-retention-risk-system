
import hashlib
import json
from pathlib import Path

import pandas as pd
from faker import Faker

from config import RANDOM_SEED

from src.generators.master_data import generate_master_data
from src.generators.promotion_data import generate_promotion_data
from src.generators.survey_data import generate_survey_data
from src.generators.workload_data import generate_workload_data
from src.generators.tenure_data import generate_tenure_data
from src.generators.compensation_data import generate_compensation_data
from src.generators.attrition_data import generate_attrition_data
from src.generators.intervention_data import generate_interventions


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
METADATA_DIR = PROJECT_ROOT / "data" / "metadata"


def save_csv(dataframe, filename):
    path = RAW_DIR / filename
    dataframe.to_csv(path, index=False)
    return path


def calculate_sha256(path):
    digest = hashlib.sha256()

    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def generate_all():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    Faker.seed(RANDOM_SEED)

    print("Starting complete synthetic data generation...")
    print("Random seed:", RANDOM_SEED)

    # 1. Master data
    employees, roles, teams = generate_master_data()

    # 2. Promotion history and updated employee roles
    promotions, employees = generate_promotion_data(
        employees, roles
    )

    # 3. Historical survey and workload data
    surveys = generate_survey_data(employees)
    workload = generate_workload_data(employees)

    # 4. Tenure and compensation
    tenure = generate_tenure_data(employees)
    compensation = generate_compensation_data(roles)

    # 5. Future attrition outcomes
    outcomes = generate_attrition_data(
        employees, surveys, workload
    )

    # 6. Supportive interventions
    interventions = generate_interventions(
        employees, surveys, workload
    )

    datasets = {
        "employees.csv": employees,
        "roles.csv": roles,
        "teams.csv": teams,
        "promotion_history.csv": promotions,
        "engagement_surveys.csv": surveys,
        "workload_snapshots.csv": workload,
        "tenure_snapshots.csv": tenure,
        "compensation_bands.csv": compensation,
        "attrition_outcomes.csv": outcomes,
        "interventions.csv": interventions,
    }

    manifest = {
        "project": "Employee Retention Risk System",
        "random_seed": RANDOM_SEED,
        "generator": "src/generators/generate_all.py",
        "datasets": {}
    }

    for filename, dataframe in datasets.items():
        output_path = save_csv(dataframe, filename)

        manifest["datasets"][filename] = {
            "rows": len(dataframe),
            "sha256": calculate_sha256(output_path)
        }

        print(f"Generated {filename}: {len(dataframe)} rows")

    manifest_path = METADATA_DIR / "source_manifest.json"

    with open(manifest_path, "w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=4)

    print("\nAll datasets generated successfully!")
    print("Source manifest:", manifest_path)
    print("Fixed seed:", RANDOM_SEED)


if __name__ == "__main__":
    generate_all()
