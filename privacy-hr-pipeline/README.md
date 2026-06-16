# Project: Privacy-Preserving HR Analytics Pipeline

- Self driven project focuses on k-anonymity, l-diversity, differential privacy applied to enterprise HR data

- Synthetic HR/employee dataset (salary, age, department, performance ratings) 

- HR dataset with the correlations (salary tied to department and tenure, age distributed realistically, performance ratings weighted toward the middle)

- Apply k-anonymity + l-diversity for safe internal reporting 

- Add differential privacy for aggregate queries (avg salary by dept, with epsilon-delta noise)



# Build sequence

## Week 1: 
Synthetic dataset generation — Python/Faker library, 5-10k rows, realistic HR attributes with quasi-identifiers (age, zip, department, gender, salary band)

## Week 2: 

k-anonymity implementation — generalize/suppress quasi-identifiers until every record matches k others. Directly from DATASCI-233 Mondrian/Incognito coursework.

l-diversity check — verify sensitive attributes (salary, performance rating) have diversity within each anonymized group, not just k-anonymity

## Weeks 3-4: 

Differential privacy layer — Laplace mechanism for aggregate queries (avg salary, headcount by dept) with configurable epsilon, show the privacy/accuracy tradeoff visually

## Weeks 5-7: 

Dashboard — small Streamlit or Flask app showing original vs anonymized vs differentially-private results side by side. 


# Env Setup

### Python 3.13.7 via pyenv
```
cd ~/secure-agent-execution
mkdir privacy-hr-pipeline
cd privacy-hr-pipeline
python3 -m venv venv
source venv/bin/activate
pip install pandas numpy faker jupyter matplotlib
```
```faker``` generates realistic fake names/data, 

```pandas/numpy``` for the data manipulation, 

```matplotlib``` for visualizing later,

 ```jupyter``` lets us work interactively if we prefer notebooks for exploration before turning things into clean scripts.


## ```.gitignore```: Keep venv/ folder out of the repo
```
echo "venv/" > .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "*.csv" >> .gitignore
```

## ```requirements.txt```: Reproducable setup

```
pip freeze > requirements.txt
git add .gitignore requirements.txt
```

To recreate the environment: ```pip install -r requirements.txt```
### Notes: 

- Press Cmd + Shift + P (Mac) to open the Command Palette.Type Python: Select Interpreter and select it.Look for the entry that says ('venv': venv) or shows the path containing privacy-hr-pipeline/venv/bin/python. Click it.