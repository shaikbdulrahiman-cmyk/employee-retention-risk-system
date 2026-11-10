# Employee Retention Risk Identification and Intervention Management System

## 1. Project Overview

The Employee Retention Risk Identification and Intervention Management System is a Python-based analytical solution designed to identify workforce engagement and workload patterns that may indicate employee retention concerns.

The system analyzes synthetic employee data and prioritizes supportive retention conversations through a risk-scoring approach.

**Important:** This system supports human review only. It must not be used to make automated employment decisions.

## 2. Objectives

- Analyze employee engagement and workload patterns.
- Track employee tenure and promotion history.
- Identify potential retention concerns.
- Generate employee risk scores and categories.
- Recommend supportive interventions.
- Provide interactive workforce analytics.

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

The project generates synthetic data for 10,000 employees.

| Dataset | Records |
|---|---:|
| Employees | 10,000 |
| Roles | 6 |
| Teams | 5 |
| Engagement Surveys | 79,539 |
| Workload Snapshots | 920,824 |
| Tenure Snapshots | 217,826 |
| Promotions | 1,200 |
| Interventions | 2,631 |
| Attrition Outcomes | 10,000 |

## 5. System Features

- Synthetic workforce data generation.
- Employee engagement analysis.
- Workload and overtime analysis.
- Employee retention risk scoring.
- Low, Medium and High risk classification.
- Human-review recommendations.
- Interactive Streamlit dashboard.
- CSV exports and SQLite database.
- Data validation and automated testing.

## 6. Risk Analysis

The system calculates a heuristic risk score using engagement and workload indicators.

Employees are classified into:

- Low Risk
- Medium Risk
- High Risk

Higher-priority cases are presented for supportive human review.

These scores are illustrative prioritization signals, not validated individual attrition predictions.

## 7. Dashboard

The Streamlit dashboard provides:

- Employee statistics.
- Risk distribution charts.
- Engagement overview.
- Employee search.
- Risk review tables.
- CSV download functionality.

## 8. Project Structure

```text
employee_retention_risk_system/
├── data/
│   ├── raw/
│   ├── processed/
│   └── employee_retention.db
├── docs/
├── outputs/
├── src/
│   ├── generators/
│   ├── analysis/
│   ├── validation/
│   ├── database/
│   └── dashboard/
├── tests/
├── config.py
├── requirements.txt
└── README.md
```

## 9. Installation

Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd employee_retention_risk_system
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

## 11. Testing Results

Automated testing completed successfully.

**Result: 10 tests passed.**

Validation checks cover employee records, primary keys, foreign-key relationships, attrition outcomes, risk scores and risk categories.

## 12. Ethical Considerations

- Uses synthetic data rather than real employee personal records.
- Risk scores are intended only to support human review.
- Missing engagement information must not automatically be treated as poor performance.
- No automated hiring, firing, promotion or disciplinary decisions should be made using this system.

## 13. Conclusion

This project demonstrates an end-to-end employee retention analytics workflow using Python, data generation, risk analysis, SQLite, Streamlit and automated testing. It provides workforce insights and helps organize supportive employee retention conversations.