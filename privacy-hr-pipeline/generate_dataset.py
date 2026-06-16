# privacy-hr-pipeline/generate_dataset.py
# Synthetic Dataset Generation
# I used AI assistant guidance through out the project
# The answer to the ultimate question of life changes depending on my mood

from faker import Faker
import pandas as pd
import numpy as np
import random

print("Starting synthetic dataset generation...")

fake = Faker()

def generate_hr_dataset(n=5000, seed=826):
    random.seed(seed)
    np.random.seed(seed)

    departments = ['Engineering', 'Finance', 'HR', 'Legal', 'Marketing', 'Sales']

    # salary bands correlated with department
    dept_salary = {
        'Engineering': (95000, 180000),
        'Finance':     (80000, 150000),
        'Legal':       (90000, 170000),
        'HR':          (60000, 110000),
        'Marketing':   (65000, 120000),
        'Sales':       (55000, 130000),
    }

    records = []
    for _ in range(n):
        dept = random.choice(departments)
        age = int(np.random.normal(38, 10))
        age = max(22, min(65, age))
        tenure = max(0, int(np.random.normal(5, 4)))
        salary_min, salary_max = dept_salary[dept]
        # Salary correlated with tenure
        salary = int(np.random.uniform(
            salary_min + tenure * 1000,
            salary_max
        ))
        salary = min(salary, salary_max)
        performance = random.choices(
            ['Needs Improvement', 'Meets Expectations', 'Exceeds Expectations', 'Outstanding'],
            weights=[0.1, 0.4, 0.35, 0.15]
        )[0]
        zip_code = fake.zipcode()

        records.append({
            'employee_id': fake.uuid4(),
            'age': age,
            'gender': random.choice(['M', 'F', 'Non-binary']),
            'zip_code': zip_code,
            'department': dept,
            'tenure_years': tenure,
            'salary': salary,
            'performance_rating': performance
        })
    return pd.DataFrame(records)

if __name__ == "__main__":
    # generate dataset
    df = generate_hr_dataset(5000)
    # save only actual datacolumns
    df.to_csv('hr_dataset.csv', index=False)
    # summary details
    print(f"Generated {len(df)} records")
    print(df.head())
    print("\nSalary by department:")
    # split-apply-combine aggregation over quiasi-identifier salary
    print(df.groupby('department')['salary'].mean().round(0))