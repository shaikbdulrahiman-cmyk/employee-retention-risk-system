# Employee Retention Risk System — Data Dictionary

## 1. Project overview

This project uses synthetic workforce data to identify employee retention risk signals and prioritize supportive human review.

- Employee records: 10,000
- Historical data period: 24 months
- Feature cutoff date: 2026-10-01
- Attrition prediction horizon end: 2027-04-01
- Random seed: 20261022
- Data provenance: Synthetic, programmatically generated data
- Sensitive employee information: No real employee records are intended to be used.

All dates use the ISO format `YYYY-MM-DD`.
All generated employee and entity identifiers are strings.

## 2. Entity relationships

| Parent entity | Child entity | Relationship |
|---|---|---|
| Role | Employee | One role can be assigned to many employees |
| Team | Employee | One team can contain many employees |
| Employee | EngagementSurvey | One employee can have many surveys |
| Employee | TenureSnapshot | One employee can have many snapshots |
| Employee | WorkloadSnapshot | One employee can have many workload records |
| Role | CompensationBand | One role can have multiple compensation bands |
| Employee | PromotionHistory | One employee can have multiple promotion records |
| Role | PromotionHistory | Previous and new roles reference Role |
| Employee | AttritionOutcome | One outcome record per employee |
| Employee | Intervention | One employee can have multiple interventions |

## 3. Entity definitions

### 3.1 Employee

Source: `data/raw/employees.csv`

Purpose: Master employee records.

| Field | Data type | Requirement | Description / validation |
|---|---|---|---|
| employee_id | String | Required, PK | Unique employee identifier, format EMP-000001 |
| employee_name | String | Required | Synthetic employee name |
| email | String | Required | Synthetic employee email |
| hire_date | Date | Required | Employee hiring date |
| role_id | String | Required, FK | References roles.role_id |
| team_id | String | Required, FK | References teams.team_id |
| employment_status | String | Required | Employment lifecycle status |

Validation:
- employee_id must be unique.
- role_id must reference an existing role.
- team_id must reference an existing team.
- hire_date must be a valid date.

### 3.2 Role

Source: `data/raw/roles.csv`

Purpose: Master list of job roles.

| Field | Data type | Requirement | Description / validation |
|---|---|---|---|
| role_id | String | Required, PK | Unique role identifier |
| role_name | String | Required | Role name |

Validation:
- role_id must be unique.
- Employee and compensation references must resolve to an existing role.

### 3.3 Team

Source: `data/raw/teams.csv`

Purpose: Master list of organizational teams.

| Field | Data type | Requirement | Description / validation |
|---|---|---|---|
| team_id | String | Required, PK | Unique team identifier |
| team_name | String | Required | Team name |

Validation:
- team_id must be unique.
- Employee team references must resolve to an existing team.

### 3.4 EngagementSurvey

Source: `data/raw/engagement_surveys.csv`

Purpose: Stores employee engagement survey responses over time.

| Field | Data type | Requirement | Description / validation |
|---|---|---|---|
| survey_id | String | Required, PK | Unique survey identifier |
| employee_id | String | Required, FK | References employees.employee_id |
| survey_date | Date | Required | Survey date |
| response_status | String | Required | Response lifecycle status |
| engagement_score | Float | Conditional | Engagement score, scale 1–5 |
| manager_support_score | Float | Optional | Manager support score, scale 1–5 |
| work_life_balance_score | Float | Optional | Work-life balance score, scale 1–5 |
| career_growth_score | Float | Optional | Career growth score, scale 1–5 |
| recognition_score | Float | Optional | Recognition score, scale 1–5 |

Validation:
- survey_id must be unique.
- employee_id must reference an existing employee.
- Scores must be between 1 and 5 when present.
- Missing responses must not be treated as negative scores.
- Only completed surveys available at the feature cutoff may contribute to risk features.

### 3.5 TenureSnapshot

Source: `data/raw/tenure_snapshots.csv`

Purpose: Maintains historical employee tenure records.

| Field | Data type | Requirement | Description / validation |
|---|---|---|---|
| snapshot_id | String | Required, PK | Unique snapshot identifier |
| employee_id | String | Required, FK | References employees.employee_id |
| snapshot_date | Date | Required | Date of snapshot |
| tenure_months | Integer | Required | Employee tenure in months |
| tenure_years | Float | Required | Employee tenure in years |

Validation:
- snapshot_id must be unique.
- employee_id must reference an existing employee.
- Tenure cannot be negative.
- tenure_years must reconcile with tenure_months.

### 3.6 WorkloadSnapshot

Source: `data/raw/workload_snapshots.csv`

Purpose: Stores weekly employee workload information.

| Field | Data type | Requirement | Description / validation |
|---|---|---|---|
| workload_id | String | Required, PK | Unique workload record identifier |
| employee_id | String | Required, FK | References employees.employee_id |
| week_start_date | Date | Required | Start date of workload week |
| working_hours | Float | Required | Total weekly working hours |
| overtime_hours | Float | Required | Weekly overtime hours |
| active_projects | Integer | Required | Number of active projects |
| workload_level | String | Required | Workload classification |

Validation:
- workload_id must be unique.
- employee_id must reference an existing employee.
- Working hours, overtime and project counts must be nonnegative.
- Risk analysis uses records available on or before the feature cutoff.

### 3.7 CompensationBand

Source: `data/raw/compensation_bands.csv`

Purpose: Stores salary ranges associated with job levels and roles.

| Field | Data type | Requirement | Description / validation |
|---|---|---|---|
| comp_band_id | String | Required, PK | Unique compensation band identifier |
| role_id | String | Required, FK | References roles.role_id |
| job_level | String | Required | Job level classification |
| minimum_annual_salary | Integer | Required | Minimum annual salary |
| maximum_annual_salary | Integer | Required | Maximum annual salary |
| currency | String | Required | Salary currency code |
| effective_start_date | Date | Required | Start of band validity |
| effective_end_date | Date | Optional | End of band validity |

Validation:
- comp_band_id must be unique.
- role_id must reference an existing role.
- Minimum salary must not exceed maximum salary.
- Effective end date must not precede effective start date.
- Salary values must be nonnegative.

### 3.8 PromotionHistory

Source: `data/raw/promotion_history.csv`

Purpose: Records employee role progression and promotion events.

| Field | Data type | Requirement | Description / validation |
|---|---|---|---|
| promotion_id | String | Required, PK | Unique promotion identifier |
| employee_id | String | Required, FK | References employees.employee_id |
| previous_role_id | String | Required, FK | Previous role reference |
| new_role_id | String | Required, FK | New role reference |
| promotion_date | Date | Required | Date of promotion |
| promotion_type | String | Required | Promotion classification |

Validation:
- promotion_id must be unique.
- employee_id must reference an existing employee.
- Both role references must exist in roles.
- Promotion dates must be valid and consistent with employee history.

### 3.9 AttritionOutcome

Source: `data/raw/attrition_outcomes.csv`

Purpose: Stores future-horizon attrition outcomes for evaluation.

| Field | Data type | Requirement | Description / validation |
|---|---|---|---|
| outcome_id | String | Required, PK | Unique outcome identifier |
| employee_id | String | Required, FK | References employees.employee_id |
| feature_cutoff_date | Date | Required | Last date allowed for feature information |
| outcome_horizon_end | Date | Required | End of outcome evaluation period |
| termination_date | Date | Conditional | Termination date for voluntary attrition |
| outcome_label | String | Required | Voluntary Attrition or No Attrition |
| attrition_probability_used | Float | Required | Probability used during synthetic outcome generation |

Validation:
- outcome_id must be unique.
- One outcome record is expected per employee.
- Voluntary Attrition requires a valid termination date after the feature cutoff and on or before the outcome horizon.
- No Attrition requires a missing termination date.
- Attrition probability must be between 0 and 1.
- Outcome labels are kept separate from risk-analysis input features.

### 3.10 Intervention

Source: `data/raw/interventions.csv`

Purpose: Records supportive employee interventions and their follow-up outcomes.

| Field | Data type | Requirement | Description / validation |
|---|---|---|---|
| intervention_id | String | Required, PK | Unique intervention identifier |
| employee_id | String | Required, FK | References employees.employee_id |
| intervention_date | Date | Required | Intervention start date |
| intervention_type | String | Required | Supportive intervention type |
| status | String | Required | Planned, In Progress, Completed or Cancelled |
| follow_up_date | Date | Optional | Planned follow-up date |
| completion_date | Date | Conditional | Actual completion date |
| intervention_outcome | String | Conditional | Recorded intervention outcome |
| notes | String | Optional | Supporting notes |

Known intervention types:
- Manager Check-in
- Career Development Discussion
- Workload Adjustment
- Training Opportunity
- HR Support Conversation

Validation:
- intervention_id must be unique.
- employee_id must reference an existing employee.
- Follow-up date must not precede intervention date.
- Completed interventions require a completion date.
- Pending and cancelled interventions must have consistent outcome states.

## 4. Processed dataset

### EmployeeRiskAnalysis

Source: `data/processed/employee_risk_analysis.csv`

Purpose: Contains the employee-level risk analysis generated from employee master data, completed surveys and historical workload records.

| Field | Data type | Description |
|---|---|---|
| employee_id | String | Employee identifier |
| employee_name | String | Employee name |
| email | String | Employee email |
| hire_date | Date | Employee hiring date |
| role_id | String | Role reference |
| team_id | String | Team reference |
| employment_status | String | Employment status |
| engagement_score | Float | Latest eligible completed survey score |
| latest_survey_date | Date | Latest eligible survey date |
| average_working_hours | Float | Average of recent workload records |
| average_overtime | Float | Average overtime in recent workload records |
| latest_workload_date | Date | Latest eligible workload date |
| survey_missing | Boolean | Indicates unavailable completed survey |
| workload_data_missing | Boolean | Indicates unavailable workload records |
| risk_score | Integer | Explainable rule-based score, 0–100 |
| risk_reason | String | Explanation of identified risk signals |
| risk_category | String | Low, Medium or High |
| review_recommendation | String | Suggested supportive review action |
| human_review_required | Boolean | Indicates whether human review is required |
| feature_cutoff_date | Date | Feature availability cutoff |

Risk scoring rules:
- Engagement score 2 or below: +35 points.
- Average working hours 55 or above: +30 points.
- Average working hours from 48 to below 55: +15 points.
- Average overtime 15 or above: +20 points.
- Engagement score 4 or above: -10 points.
- Final score is bounded between 0 and 100.
- Missing engagement does not add risk points.
- Missing workload is explicitly flagged and uses a neutral scoring fallback.

Risk categories:
- Low: 0–19
- Medium: 20–49
- High: 50–100

Human review:
- Low: Routine check-in.
- Medium: Consider supportive human review.
- High: Prioritize human review and support.

These scores are prioritization signals, not validated predictions or automatic employment decisions. Human review is required for consequential decisions.

## 5. Identifier conventions

| Entity | Identifier convention |
|---|---|
| Employee | EMP-000001 |
| Survey | SURV-2026-000001 |
| Intervention | INT-2026-000001 |
| Tenure snapshot | SNAP-<employee-id>-2026Q1 |
| Attrition outcome | OUT-<employee-id>-2027 |

Other entity identifiers use unique generated string identifiers.

## 6. Data quality and integrity rules

The project validation process checks:

1. Primary key uniqueness.
2. Foreign key integrity.
3. Required employee population size.
4. Valid survey score ranges.
5. Nonnegative tenure and tenure reconciliation.
6. Valid intervention lifecycle states and dates.
7. Attrition outcome and termination date consistency.
8. Attrition rate within the intended synthetic range.
9. Risk score bounds and valid risk categories.
10. Complete risk-analysis coverage for the employee population.
11. Temporal cutoff compliance for risk features.
12. Explanation and human-review flags.

## 7. Ground truth and edge cases

Source: `data/ground_truth.csv`

The separate ground-truth file documents four deliberate test scenarios:

- GT-001: Future information leakage.
- GT-002: Missing survey treated as negative.
- GT-003: Inconsistent attrition outcome and termination date.
- GT-004: Unexplained risk score without human review.

These scenarios are test documentation and are not model input data. They must not be merged into the employee risk-analysis dataset.

## 8. Reproducibility and limitations

- Random seed: 20261022.
- Data is synthetically generated.
- Generator scripts and validation scripts are maintained in the source repository.
- Risk analysis uses a fixed feature cutoff.
- Synthetic attrition outcomes are generated using documented risk-related rules.
- Because the synthetic outcomes are based on related signals, evaluation results must not be interpreted as proof of real-world predictive performance.
- The system is designed to support employee well-being and human decision-making, not automate hiring, firing or other employment decisions.
