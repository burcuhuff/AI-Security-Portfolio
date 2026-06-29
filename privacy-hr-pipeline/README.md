# Project: Privacy-Preserving HR Analytics Pipeline ***** WIP *****

- Self driven project focuses on k-anonymity, l-diversity, differential privacy applied to enterprise HR data

- Synthetic HR/employee dataset (salary, age, department, performance ratings) 

- HR dataset with the correlations (salary tied to department and tenure, age distributed realistically, performance ratings weighted toward the middle)

- Apply k-anonymity + l-diversity for safe internal reporting 

- Add differential privacy for aggregate queries (avg salary by dept, with epsilon-delta noise)

# Data Set
## Why Correlated Salary Bands?
- Realism Factor: In a real company, human resources data is never truly random. An engineer with 10 years of experience naturally makes more than a newly hired coordinator. Tying salary to department and adding a $1,000 * tenure bump mimics real corporate compensation structures. 

- The Privacy Risk Testing: By creating realistic, predictable salary bands, we create statistical patterns. In data privacy, this allows us to test whether our data masking techniques can successfully hide individual identities while still preserving the overall company wide salary trends for analysts.

## Why Seed the Random Generator?
- The Reproducibility Requirement: If we don't use a seed, every single run of our script creates a chaotic new batch of employees. If a bug crashes your pipeline on row 4,112, we could never replicate that exact crash again.

- The Scientific Control: Locking the seed at personally picked 826 provides a "control group" for our data privacy experiments. We can run our masking algorithms on the exact same input dataset over and over again, allowing us to measure precisely how much privacy we are adding without the data changing under your feet.

## Why Cap Age at 22–65?
- Eliminating "Data Noise": Python's statistical functions (np.random.normal) use infinite mathematical bell curves. Without guardrails, the math would occasionally generate a 4-year-old software engineer or a 115-year-old HR manager. 

- Corporate Compliance Guardrails: The max(22, min(65, age)) code enforces realistic workforce boundaries. It assumes a typical post college entry age (22) and standard corporate retirement thresholds (65), ensuring your downstream privacy pipeline isn't wasted processing impossible edge cases.

# Build sequence

## 1. Synthetic dataset generation: 
Python/Faker library, 5-10k rows, realistic HR attributes with quasi-identifiers (age, zip, department, gender, salary band)

## 2. k-anonymity implementation: 

Generalize/suppress quasi-identifiers until every record matches k others. Directly from DATASCI-233 Mondrian/Incognito coursework.

l-diversity check — verify sensitive attributes (salary, performance rating) have diversity within each anonymized group, not just k-anonymity

## 3. Differential privacy layer:

Laplace mechanism for aggregate queries (avg salary, headcount by dept) with configurable epsilon, show the privacy/accuracy tradeoff visually

## 4. Dashboard

Streamlit or Flask app showing original vs anonymized vs differentially-private results side by side. 


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

- Press Cmd + Shift + P to open the Command Palette.Type Python: Select Interpreter and select it.Look for the entry that says ('venv': venv) or shows the path containing privacy-hr-pipeline/venv/bin/python. Click it.

- Repo name changed, venv connection not available at the repo level
  ```
  cd ai-security-portfolio/privacy-hr-pipeline
  deactivate
  rm -rf venv
  python3 -m venv venv
  source venv/bin/activate
  pip install pandas numpy faker jupyter matplotlib
  jupyter notebook

  ```
  otherwise
  ```
  python3 -m venv venv
  source venv/bin/activate
  jupyter notebook

  ```
- For the dashboard install streamlit
    
  ```
  source venv/bin/activate
  pip install streamlit
  ```
