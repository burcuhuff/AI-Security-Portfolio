{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 24,
   "id": "c57f3577-8e7d-4165-8e16-910597b3d7b4",
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import numpy as np"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 25,
   "id": "30d73c01-e848-4310-acfa-df79553a8fcc",
   "metadata": {},
   "outputs": [],
   "source": [
    "df = pd.read_csv('hr_dataset.csv')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 26,
   "id": "d94185ba-bf4f-480a-993c-11ae6542778e",
   "metadata": {},
   "outputs": [],
   "source": [
    "# quisi-identifiers to generalize and sensitive attribute\n",
    "QI = ['age', 'zip_code', 'gender', 'department']\n",
    "SENSITIVE = ['salary']\n",
    "K = 5 "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 27,
   "id": "b55ac1dc-32fc-4a50-b56c-375659288551",
   "metadata": {},
   "outputs": [],
   "source": [
    "def generalize_age(age, range_size=10):\n",
    "    \"\"\" Generalize age into ranges: 20-29, 30-39 \"\"\"\n",
    "    lower = (age // range_size) * range_size\n",
    "    return f\"{lower}-{lower + range_size -1}\""
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 28,
   "id": "91709dd8-8286-4891-8920-013cdc66a720",
   "metadata": {},
   "outputs": [],
   "source": [
    "def generalize_zip(zip_code, digits=3):\n",
    "    \"\"\" Truncate zip to first n digits: 94065 to 940**\"\"\"\n",
    "    return str(zip_code)[:digits] + '*' * (5 - digits)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 29,
   "id": "48b85f75-985a-4f7d-995a-a84777088c6a",
   "metadata": {},
   "outputs": [],
   "source": [
    "def anonymize(df, k, age_range=10, zip_digits=3):\n",
    "    df = df.copy()\n",
    "    df['age'] = df['age'].apply(lambda x: generalize_age(x, age_range))\n",
    "    df['zip_code'] = df['zip_code'].apply(lambda x: generalize_zip(x, zip_digits))\n",
    "    return df"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 33,
   "id": "fbb270a8-d691-49b9-b11d-51357eadc02a",
   "metadata": {},
   "outputs": [],
   "source": [
    "def check_k_anonymity(df, qi_cols, k):\n",
    "    \"\"\" Check if dataset satisfies k-anonymity\"\"\"\n",
    "    groups = df.groupby(qi_cols).size().reset_index(name='count')\n",
    "    violations = groups[groups['count'] < k]\n",
    "    satisfies = len(violations) == 0\n",
    "    print(f\"K={k} anonymity satisfied: {satisfies}\")\n",
    "    print(f\"Total groups: {len(groups)}\")\n",
    "    print(f\"Violations (groups < k): {len(violations)}\")\n",
    "    print(f\"Smallest group size: {groups['count'].min()}\")\n",
    "    return satisfies, violations"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 31,
   "id": "95220a0b-025f-42fc-a17e-fe256e37117d",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "K=5 anonymity satisfied: False\n",
      "Total groups: 4776\n",
      "Violations (groups < k): 4776\n",
      "Smallest group size: 1\n"
     ]
    }
   ],
   "source": [
    "# start with k=5\n",
    "anon_df = anonymize(df, k=K)\n",
    "satisfies, violations = check_k_anonymity(anon_df, QI, K)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "533219be-0e97-49e4-b187-af9260f177ee",
   "metadata": {},
   "source": [
    "# Observation\n",
    "- K=5 anonymity satisfied: False\n",
    "- Total groups: 4776\n",
    "- Violations (groups < k): 4776\n",
    "- Smallest group size: 1\n",
    "- Given the zip codes are nearly unique (4873/5000), truncating to 3 digits is not enough to satisfy k=5, we will need to try 2 digits or even dropping zip code entirely."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 34,
   "id": "f44c3229-d94f-4443-bb9b-5b8023851392",
   "metadata": {},
   "outputs": [],
   "source": [
    "# zip_digits = 2\n",
    "def anonymize(df, k, age_range=10, zip_digits=2):\n",
    "    df = df.copy()\n",
    "    df['age'] = df['age'].apply(lambda x: generalize_age(x, age_range))\n",
    "    df['zip_code'] = df['zip_code'].apply(lambda x: generalize_zip(x, zip_digits))\n",
    "    return df"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 35,
   "id": "3da10c6b-c0c1-4fed-af63-87a848885d98",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "K=5 anonymity satisfied: False\n",
      "Total groups: 3321\n",
      "Violations (groups < k): 3304\n",
      "Smallest group size: 1\n"
     ]
    }
   ],
   "source": [
    "# try zip_digit = 2\n",
    "anon_df = anonymize(df, k=K)\n",
    "satisfies, violations = check_k_anonymity(anon_df, QI, K)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "fceb6a0e-92ae-4d74-80b2-4506b2619fec",
   "metadata": {},
   "source": [
    "# Observation\n",
    "- zip_digit = 2 is still not enough\n",
    "- Try age_range=5 compared to age_range=10"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 38,
   "id": "dd415e4d-f158-4e6b-815d-6f42dac54029",
   "metadata": {},
   "outputs": [],
   "source": [
    "# age_range=5\n",
    "def anonymize(df, k, age_range=5, zip_digits=2):\n",
    "    df = df.copy()\n",
    "    df['age'] = df['age'].apply(lambda x: generalize_age(x, age_range))\n",
    "    df['zip_code'] = df['zip_code'].apply(lambda x: generalize_zip(x, zip_digits))\n",
    "    return df"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 39,
   "id": "15247fcd-a1de-47fe-9b9a-84f9d7d4f31e",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "K=5 anonymity satisfied: False\n",
      "Total groups: 4024\n",
      "Violations (groups < k): 4023\n",
      "Smallest group size: 1\n"
     ]
    }
   ],
   "source": [
    "# age_range=5\n",
    "anon_df = anonymize(df, k=K)\n",
    "satisfies, violations = check_k_anonymity(anon_df, QI, K)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "8ece50c0-addf-49a5-a77f-d439563006fd",
   "metadata": {},
   "source": [
    "# Observations\n",
    "- With smaller age range, 5 compared to 10, the violations increased, k_anonymity satisfaction decreased.\n",
    "- While changing zip_digit to 2 from 3 lowered the violations and increased the k_anonymity satisfaction.\n",
    "- For minimum information loss, I'd remove zip_code from the quasi-identifiers list and keep the age_range high."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 43,
   "id": "edb646d7-f6b3-4554-b448-0c3a1bcb215e",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "K=5 anonymity satisfied: False\n",
      "Total groups: 90\n",
      "Violations (groups < k): 11\n",
      "Smallest group size: 1\n"
     ]
    }
   ],
   "source": [
    "# Test 1: Dropping zip_code\n",
    "QI_NO_ZIP = ['age', 'gender', 'department']\n",
    "\n",
    "def anonymize_no_zip(df, age_range=10):\n",
    "    df = df.copy()\n",
    "    df['age'] = df['age'].apply(lambda x: generalize_age(x, age_range))\n",
    "    return df\n",
    "\n",
    "anon_no_zip = anonymize_no_zip(df, age_range=10)\n",
    "satisfies, violations = check_k_anonymity(anon_no_zip, QI_NO_ZIP, K)"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "540e482c-4cdb-41e0-80c1-6dad188dd802",
   "metadata": {},
   "source": [
    "# Observation\n",
    "- Dropping the zip_code lowered the unique groups to 90 (from 5000)\n",
    "- We still have 11 viloations at k=5 (we have engineers 60-69 yrs old and this is a privacy risk, even without zip code) "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 44,
   "id": "cd1dc555-7c73-4f1a-9756-0bd7cf35aa48",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "K=10 anonymity satisfied: False\n",
      "Total groups: 90\n",
      "Violations (groups < k): 18\n",
      "Smallest group size: 1\n"
     ]
    }
   ],
   "source": [
    "# Test2: k=10\n",
    "satisfies_k10, violations_k10 = check_k_anonymity(anon_no_zip, QI_NO_ZIP, 10)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 45,
   "id": "4a2af540-05ec-462f-8432-3c5848e02256",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "\n",
      "With zip (3 digits): 5000 unique groups\n",
      "Without zip: 90 unique groups\n"
     ]
    }
   ],
   "source": [
    "# Test 3: Measure information loss for both\n",
    "print(f\"\\nWith zip (3 digits): {df[['age','zip_code','gender','department']].drop_duplicates().shape[0]} unique groups\")\n",
    "print(f\"Without zip: {anon_no_zip[QI_NO_ZIP].drop_duplicates().shape[0]} unique groups\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 46,
   "id": "0c139402-9eee-4fc9-851f-7bdad989b984",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Records suppressed: 26 (0.5% of dataset)\n",
      "K=5 anonymity satisfied: True\n",
      "Total groups: 79\n",
      "Violations (groups < k): 0\n",
      "Smallest group size: 5\n",
      "\n",
      "Original records: 5000\n",
      "After anonymization + suppression: 4974\n",
      "Records retained: 99.5%\n",
      "\n",
      "Original unique QI groups: 703\n",
      "Anonymized unique QI groups: 79\n"
     ]
    }
   ],
   "source": [
    "# subpress the violations by removing records belong to groups smaller than k\n",
    "def suppress_violations(df, qi_cols, k):\n",
    "    \"\"\"Remove records that belong to groups smaller than k\"\"\"\n",
    "    group_sizes = df.groupby(qi_cols)[qi_cols[0]].transform('count')\n",
    "    suppressed = df[group_sizes >= k].copy()\n",
    "    suppressed_count = len(df) - len(suppressed)\n",
    "    print(f\"Records suppressed: {suppressed_count} ({suppressed_count/len(df):.1%} of dataset)\")\n",
    "    return suppressed\n",
    "\n",
    "# Apply suppression to fix remaining violations\n",
    "anon_suppressed = suppress_violations(anon_no_zip, QI_NO_ZIP, K)\n",
    "satisfies_final, _ = check_k_anonymity(anon_suppressed, QI_NO_ZIP, K)\n",
    "\n",
    "# Final information loss measurement\n",
    "print(f\"\\nOriginal records: {len(df)}\")\n",
    "print(f\"After anonymization + suppression: {len(anon_suppressed)}\")\n",
    "print(f\"Records retained: {len(anon_suppressed)/len(df):.1%}\")\n",
    "print(f\"\\nOriginal unique QI groups: {df[['age','gender','department']].drop_duplicates().shape[0]}\")\n",
    "print(f\"Anonymized unique QI groups: {anon_suppressed[QI_NO_ZIP].drop_duplicates().shape[0]}\")\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "dd598f34-15b8-42ce-9870-085dc2776016",
   "metadata": {},
   "source": [
    "# Results\n",
    "- Even after removing zip_code and generalizing age into ranges, 11 groups still violated k=5 — primarily rare combinations of minority gender values with specific department/age combinations.\n",
    "- Suppression removes these records entirely. The tradeoff: 100% privacy guarantee for remaining records, but potential bias introduced if suppressed records are systematically different from retained ones, for example: if Non-binary employees are disproportionately suppressed, the anonymized dataset underrepresents them."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "23b6dfd3-c8e4-4dd1-924d-aaf35d919ee5",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
