# Employee Retention Risk Identification and Intervention Management System

## 1. Project Overview

The Employee Retention Risk Identification and Intervention Management System is a Python-based analytical solution designed to identify workforce engagement, tenure and workload patterns that may indicate employee retention concerns.

The system analyzes synthetic employee data and prioritizes supportive retention conversations through an explainable, rule-based risk-scoring approach.

**Important:** This system supports human review only. It must not be used to make automated employment decisions.

## 2. Objectives

- Analyze employee engagement and workload patterns.
- Track employee tenure and promotion history.
- Identify potential retention concerns.
- Generate employee risk scores and categories.
- Recommend supportive interventions.
- Provide interactive workforce analytics.
- Maintain traceability through historical records and validation.

## 3. Technologies Used

- Python 3.13
- Pandas
- NumPy
- Streamlit
- SQLite
- Matplotlib
- Faker
- Pytest

## 4. Dataset Information

The project generates synthetic workforce data for 10,000 employees.

| Dataset | Records |
|---|---:|
| Employees | 10,000 |
| Roles | 6 |
| Teams | 5 |
| Engagement Surveys | 79,539 |
| Workload Snapshots | 920,824 |
| Tenure Snapshots | 221,186 |
| Compensation Bands | 24 |
| Promotion History | 1,200 |
| Interventions | 2,617 |
| Attrition Outcomes | 10,000 |
| Employee Risk Analysis | 10,000 |

**Data generation configuration:**

- Random seed: `20261022`
- Employee population: 10,000
- Historical period: 24 months
- Prediction cutoff: October 1, 2026
- Attrition outcome horizon: April 1, 2027
- Synthetic attrition rate: 8.74%

All generated workforce records are synthetic and do not represent real employees.

## 5. System Features

- Synthetic workforce data generation.
- Employee engagement analysis.
- Workload and overtime analysis.
- Employee retention risk scoring.
- Low, Medium and High risk classification.
- Explainable risk reasons.
- Human-review recommendations.
- Supportive intervention tracking.
- Interactive Streamlit dashboard.
- CSV exports and SQLite database.
- Data validation and automated testing.
- Separate ground-truth records for documented edge cases.

## 6. Risk Analysis

The system calculates a heuristic risk score using engagement and workload indicators.

The scoring rules include:

- Low engagement: additional risk points.
- Elevated working hours: additional risk points.
- High overtime: additional risk points.
- Strong engagement: a risk reduction.

Employees are classified into Low, Medium and High risk categories.

Each risk result includes explanatory reasons and a review recommendation.

These scores are illustrative prioritization signals, not independently validated individual attrition predictions.

## 7. Dashboard

The Streamlit dashboard provides:

- Employee statistics.
- Risk distribution charts.
- Engagement overview.
- Employee search.
- Risk review tables.
- Prioritized human-review recommendations.
- CSV download functionality.

## 8. Project Structure

```text
employee_retention_risk_system/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── ground_truth.csv
│   └── employee_retention.db
├── docs/
│   └── data_dictionary.md
├── src/
│   ├── generators/
│   ├── analysis/
│   ├── validation/
│   ├── database/
│   └── dashboard/
├── tests/
│   └── test_project.py
├── config.py
├── requirements.txt
└── README.md
```

## 9. Installation

Clone the repository:

```bash
git clone https://github.com/shaikbdulrahiman-cmyk/employee-retention-risk-system.git
cd employee-retention-risk-system
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 10. Run the Project

Run the dashboard:

```bash
streamlit run src/dashboard/app.py
```

Run data validation:

```bash
python src/validation/run_validation.py
```

Run automated tests:

```bash
python -m pytest -v
```

Build the SQLite database:

```bash
python src/database/build_database.py
```

## 11. Testing and Validation Results

Automated testing completed successfully.

**Pytest result: 15 tests passed.**

Data validation completed successfully with:

- Primary-key checks passed.
- Foreign-key checks passed.
- Date validation passed.
- Survey and tenure validation passed.
- Intervention lifecycle validation passed.
- Attrition outcome validation passed.
- Risk analysis validation passed.
- Total validation errors: 0.
- Total validation warnings: 0.

The generated attrition rate was 8.74%, within the configured target range of 5-15%.

## 12. Documentation and Ground Truth

- `docs/data_dictionary.md` documents the dataset entities, fields, relationships and validation rules.
- `data/ground_truth.csv` contains four documented edge cases, expected outcomes and model-input exclusion flags.

Ground-truth records are kept separate from the model input datasets.

## 13. Ethical Considerations

- Uses synthetic data rather than real employee personal records.
- Risk scores are intended only to support human review.
- Missing engagement information must not automatically be treated as poor performance.
- Risk indicators must be explainable and reviewable.
- No automated hiring, firing, promotion or disciplinary decisions should be made using this system.

## 14. Conclusion

This project demonstrates an end-to-end employee retention analytics workflow using Python, synthetic data generation, risk analysis, SQLite, Streamlit and automated testing.

It provides explainable workforce insights, documents data-quality edge cases and helps organize supportive employee retention conversations while preserving human oversight.
