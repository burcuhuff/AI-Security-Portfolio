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

## 2. Privacy Protection Stack

### 2.1- K-anonymity: 

Generalize/suppress quasi-identifiers until every record matches k others. 

<u>Methodology:</u> Quasi-identifiers selected: age, gender, department.
Zip code excluded, 4,873 of 5,000 records had unique zip 
codes, making it effectively a direct identifier rather than 
a quasi-identifier. Including it made k-anonymity 
unsatisfiable at any reasonable k value.

Age generalized into 10 year ranges (e.g., 30-39, 40-49) 
using the Mondrian style generalization approach. Gender and 
department retained as is, already categorical with limited 
cardinality.

Suppression applied to groups with fewer than k records after 
generalization. Fairness metric computed as suppression rate 
by gender group to detect disproportionate impact.

<u>Chosen threshold:</u>k=5

<u>Rationale:</u> At k=5, 99.5% of records were retained with only 
26 suppressed. Suppression distributed proportionally across 
gender groups (M=0.7%, F=0.5%, NB=0.4%), no measurable 
gender bias introduced.

In a real HR dataset, zip codes would cluster by office 
location and be more generalizable. The exclusion decision 
is dataset specific and must be re-evaluated in production.

<u>Results: </u>K-anonymity  (k=5):   99.5% records retained, 26 suppressed


### 2.2- L-diversity:

<u>Methodology:</u>
Applied to the k-anonymous suppressed dataset (4,974 records, 
79 groups). Sensitive attribute: salary, generalized into 
$20,000 bands (e.g., $80,000-$99,999) for diversity counting.

For each k-anonymous group, counted the number of distinct 
salary bands present. A group satisfies l-diversity if it 
contains at least l distinct sensitive attribute values, 
ensuring an attacker who identifies a group cannot determine 
any individual's salary with certainty (homogeneity attack 
prevention).

Tested l=2 and l=3. At l=3, one group violated: 
(Non-binary, Sales, age 60-69) had exactly 2 distinct 
salary bands.

<u>Chosen threshold:</u> l=2
Rationale: Enforcing l=3 would require suppressing records 
from an already rare demographic combination (Non-binary, 
older workers in Sales), introducing fairness concerns by 
removing the most vulnerable records to satisfy a stricter 
mathematical constraint.

L=2 is sufficient: every group has at least 2 distinct 
salary bands. The homogeneity attack is prevented. Average 
distinct salary bands per group = 3.9, well above the l=2 
threshold.

<u>Results: </u>L-diversity  (l=2):   all 79 groups, 0 violations  

### 2.3 T-closeness:

<u>Methodology:</u>
Applied to the k-anonymous suppressed dataset (4,974 records, 
79 groups). Measured Earth Mover's Distance (EMD) between 
the salary distribution of each group and the global salary 
distribution.

EMD computed using a 10-bin histogram approach (1D Wasserstein 
distance): normalized cumulative distribution functions compared 
bin by bin. A group satisfies t-closeness if its EMD from the 
global distribution is ≤ t.

Global salary skewness = 0.37 (mild positive skew — mean 
$111,545 > median $108,395, right tail from high earners). 
Skew is below the |1.0| threshold for significant concern, 
but t-closeness was implemented to complete the full 
k-anonymity → l-diversity → t-closeness privacy stack.

Tested t=0.1 (70 violations), t=0.2 (23 violations), 
t=0.25 (2 violations), t=0.3 (0 violations).

<u>Chosen threshold:</u> t=0.3
Rationale: All violations at stricter thresholds were 
Engineering department groups whose salary distributions 
legitimately diverge from the global average (Engineering 
avg ~$140K vs global $111K). Enforcing t<0.3 would suppress 
real business signal, not privacy risk.

The worst group (20-29, M, Engineering) has EMD=0.2862 — 
just under the t=0.3 threshold. This illustrates the core 
tension Li et al. (2007) identified: t-closeness can 
conflate privacy protection with information suppression 
when groups have genuine distributional differences.

<u>Results: </u>T-closeness  (t=0.3): all 79 groups, 0 violations

## 3. Differential Privacy:

<u>Methodology:</u>
Implemented the Laplace mechanism for aggregate salary 
queries — the most common differentially private mechanism 
for numerical data. For each department, computed the true 
average salary and added Laplace-distributed noise calibrated 
to the query sensitivity and epsilon budget.

Sensitivity computed as global sensitivity for average query:
Δf = (max_salary - min_salary) / n = $124,149 / 5,000 = $24.83

This measures the maximum change one person's record can 
cause in the query output. Low sensitivity here reflects 
the large dataset size, individual records have limited 
influence on aggregate results.

Two query types implemented and compared:
- Salary average query: sensitivity = $24.83
- Headcount count query: sensitivity = 1.0 (always, 
  regardless of dataset size — adding/removing one person 
  changes the count by exactly 1)

Epsilon tested across six values (0.01, 0.1, 0.5, 1.0, 
5.0, 10.0) to visualize the privacy/accuracy tradeoff curve. 
Composition principle documented: running 6 department 
queries each at ε=1.0 consumes total privacy budget of ε=6.0 
— production systems require a privacy accountant to track 
cumulative epsilon spend.

<u>Chosen epsilon:</u> ε=1.0
Rationale: At ε=1.0, noise scale = $24.83 producing average 
absolute noise of ~$75 per department salary query. Department 
salary rankings remain correct and the data remains 
analytically useful.

ε=0.1 rejected: noise scale of $248 approaches real salary 
differences between some departments, making aggregate 
queries misleading. ε=1.0 aligns with commonly cited 
production deployments (Google RAPPOR, Apple's differential 
privacy implementations) and provides a meaningful formal 
privacy guarantee while preserving utility.


## Privacy Evaluation Results

The privacy engineering pipeline successfully satisfied all targeted privacy guarantees while preserving analytical utility. Table 1 summarizes the privacy techniques and protection goals. Table 2 highlights the corresponding utility tradeoffs and the rationale behind each engineering decision.

**Table 1. Privacy Stack Summary**

| Technique | Setting | Attack Prevented | Result |
|-----------|---------|------------------|:------:|
| K-Anonymity | k = 5 | Identity disclosure | ✅ |
| L-Diversity | l = 2 | Homogeneity attack | ✅ |
| T-Closeness | t = 0.3 | Skewness / inference attack | ✅ |
| Differential Privacy | ε = 1.0 | Aggregate query inference | ✅ |

<br>

**Table 2. Privacy-Utility Tradeoff**

| Technique | Utility Cost | Engineering Decision |
|-----------|--------------|----------------------|
| **K-Anonymity (k = 5)** | 26 records suppressed (0.5%) | Excluded ZIP code because it behaved as a near-unique identifier. |
| **L-Diversity (l = 2)** | No additional suppression | Selected l = 2 to preserve rare demographic groups while maintaining attribute diversity. |
| **T-Closeness (t = 0.3)** | No additional suppression | Selected t = 0.3 to limit distribution distortion while reducing inference risk. |
| **Differential Privacy (ε = 1.0)** | ≈ \$75 average noise per salary query | Selected ε = 1.0 to balance analytical utility with formal privacy guarantees. |

### Key Takeaways

- All four privacy techniques satisfied their target privacy criteria.
- Utility loss remained low, requiring only **26 suppressed records (0.5%)** after removing ZIP code from the quasi-identifiers.
- Differential Privacy introduced only modest statistical noise (approximately **\$75** per salary query) while preserving aggregate trends.
- The complete privacy stack (**k-anonymity → l-diversity → t-closeness → differential privacy**) provided layered protection against identity disclosure, attribute disclosure, inference, and aggregate query attacks with minimal utility loss.
- The primary engineering tradeoff was balancing stronger privacy guarantees with data utility and fairness. Thresholds were selected to avoid disproportionately affecting minority groups or distorting legitimate business patterns while still satisfying each privacy criterion.

## 4. Dashboard

Streamlit or Flask app showing original vs anonymized vs differentially-private results side by side. 

### Dashboard progress
<p>
<img width="300" height="300" alt="Tabs skeleton" src="https://github.com/burcuhuff/AI-Security-Portfolio/blob/main/scripts/Security+701/images/Dashboard-Tab1-Skeleton.png?raw=true">

<img width="300" height="300" alt="Tabs 1 and 2, Sidebar" src="https://github.com/burcuhuff/AI-Security-Portfolio/blob/main/scripts/Security+701/images/Dashboard-Tabs1-2.png?raw=true">
</p>

<p>
<img width="300" height="300" alt="Tab3 (l-diversity)" src="https://github.com/burcuhuff/AI-Security-Portfolio/blob/main/scripts/Security+701/images/Dashboard-Tab3.png?raw=true">
<img width="300" height="300" alt="Tab4 (DP)" src="https://github.com/burcuhuff/AI-Security-Portfolio/blob/main/scripts/Security+701/images/Dashboard-Tab4.png?raw=true"> 
</p>

<TBD - Add T-closeness tab>
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
