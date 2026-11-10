
import pandas as pd


def generate_compensation_data(roles):

    salary_ranges = {
        1: [(400000, 700000), (700000, 1100000),
            (1100000, 1600000), (1600000, 2200000)],
        2: [(350000, 600000), (600000, 900000),
            (900000, 1400000), (1400000, 1900000)],
        3: [(300000, 500000), (500000, 800000),
            (800000, 1200000), (1200000, 1600000)],
        4: [(400000, 650000), (650000, 1000000),
            (1000000, 1500000), (1500000, 2000000)],
        5: [(600000, 900000), (900000, 1400000),
            (1400000, 2000000), (2000000, 2800000)],
        6: [(350000, 550000), (550000, 850000),
            (850000, 1300000), (1300000, 1800000)]
    }

    levels = ["Junior", "Mid", "Senior", "Lead"]

    records = []

    for role_index, (_, role) in enumerate(
        roles.iterrows(), start=1
    ):
        ranges = salary_ranges[role_index]

        for level_index, (minimum, maximum) in enumerate(
            ranges
        ):
            records.append({
                "comp_band_id": (
                    f"CB-{role['role_id']}-"
                    f"{level_index + 1:02d}"
                ),
                "role_id": role["role_id"],
                "job_level": levels[level_index],
                "minimum_annual_salary": minimum,
                "maximum_annual_salary": maximum,
                "currency": "INR",
                "effective_start_date": "2024-10-01",
                "effective_end_date": None
            })

    return pd.DataFrame(records)


if __name__ == "__main__":

    roles = pd.read_csv("data/raw/roles.csv")

    compensation = generate_compensation_data(roles)

    compensation.to_csv(
        "data/raw/compensation_bands.csv",
        index=False
    )

    print("Compensation data generated successfully!")
    print("Total compensation bands:", len(compensation))
    print("Unique roles:", compensation["role_id"].nunique())
    print("Currency: INR")
