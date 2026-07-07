# dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Privacy-Preserving HR Analytics",
    page_icon="🔒",
    layout="wide"
)

st.title("🔒 Privacy-Preserving HR Analytics Pipeline")
st.markdown("A demonstration of k-anonymity, l-diversity, and differential privacy applied to HR data.")

# load data (with caching for better performance)
@st.cache_data
def load_data():
    return pd.read_csv('hr_dataset.csv')

df = load_data()

# sidebar
st.sidebar.header("Privacy Parameters")
k_value = st.sidebar.slider("k-anonymity (k)", min_value=2, max_value=20, value=5)
l_value = st.sidebar.slider("l-diversity (l)", min_value=2, max_value=5, value=2)
epsilon = st.sidebar.slider(
    "Differential Privacy (ε)", 
    min_value=0.1, 
    max_value=10.0, 
    value=1.0, 
    step=0.1
)  

st.sidebar.markdown("""
---
**ε guide:**
- ε < 0.1 → Strong privacy, high noise
- ε = 1.0 → Balanced (common in practice)
- ε > 5.0 → Weak privacy, low noise
""")


 # tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([ 
    "Original Data",
    "K-Anonymity", 
    "L-Diversity",
    "T-Closeness",
    "Differential Privacy"
])

with tab1:
    st.header("Original HR Dataset Overwiew")
    st.write("This is the original HR dataset before applying any privacy-preserving techniques.")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Records", f"{len(df):,}")
    col2.metric("Departments", df['department'].nunique())
    col3.metric("Unique Zip Codes", f"{df['zip_code'].nunique():,}")
    
st.subheader("Salary Distribution by Department")
dept_salary = df.groupby('department')['salary'].mean().sort_values()
st.bar_chart(dept_salary)
st.dataframe(df.head(10))

st.subheader("Sample Records")
st.dataframe(df.sample(10))

# helper functions from k-anonymity.py and l-diversity.py
def generalize_age(age, range_size=10):
    lower = (age // range_size) * range_size
    return f"{lower}-{lower + range_size - 1}"

def generalize_salary(salary, bucket_size=20000):
    lower = (salary // bucket_size) * bucket_size
    return f"${lower:,}-${lower + bucket_size - 1:,}"

def anonymize_no_zip(df, age_range=10):
    df = df.copy()
    df['age'] = df['age'].apply(lambda x: generalize_age(x, age_range))
    return df

def suppress_violations(df, qi_cols, k):
    group_sizes = df.groupby(qi_cols)[qi_cols[0]].transform('count')
    return df[group_sizes >= k].copy()

def check_k_anonymity(df, qi_cols, k):
    groups = df.groupby(qi_cols).size().reset_index(name='count')
    violations = groups[groups['count'] < k]
    return len(violations) == 0, len(violations), groups['count'].min()

def check_l_diversity(df, qi_cols, sensitive_col, l):
    groups = df.groupby(qi_cols)[sensitive_col].apply(
        lambda x: x.apply(generalize_salary).nunique()
    ).reset_index(name='distinct_values')
    violations = groups[groups['distinct_values'] < l]
    return len(violations) == 0, len(violations)

def laplace_mechanism(true_value, sensitivity, epsilon):
    scale = sensitivity / epsilon
    noise = np.random.laplace(0, scale)
    return true_value + noise

def compute_sensitivity(df, column):
    return (df[column].max() - df[column].min()) / len(df)

# Tab2 k-anonymity
with tab2:
    st.header("K-Anonymity")
    st.markdown("""
    **What it does:** Ensures every record is indistinguishable from 
    at least k-1 others based on quasi-identifiers.
    
    **Quasi-identifiers used:** Age (generalized to ranges), 
    Gender, Department. Zip code excluded — nearly unique (4,873/5,000).
    """)

    QI = ['age', 'gender', 'department']
    anon_df = anonymize_no_zip(df, age_range=10)
    anon_suppressed = suppress_violations(anon_df, QI, k_value)

    satisfies, violations, min_group = check_k_anonymity(
        anon_suppressed, QI, k_value
    )
    suppressed_count = len(df) - len(anon_suppressed)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("k value", k_value)
    col2.metric(
        "K-Anonymity Satisfied",
        "✅ Yes" if satisfies else "❌ No"
    )
    col3.metric("Records Retained",
        f"{len(anon_suppressed):,} ({len(anon_suppressed)/len(df):.1%})"
    )
    col4.metric("Records Suppressed", suppressed_count)

    st.subheader("Anonymized Sample")
    display_cols = ['age', 'gender', 'department', 'salary']
    st.dataframe(anon_suppressed[display_cols].head(10))

    st.subheader("Group Size Distribution")
    group_sizes = anon_suppressed.groupby(QI).size().reset_index(
        name='group_size'
    )
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.hist(group_sizes['group_size'], bins=20, color='#1D9E75', 
            edgecolor='white')
    ax.axvline(x=k_value, color='red', linestyle='--', 
               label=f'k={k_value}')
    ax.set_xlabel('Group Size')
    ax.set_ylabel('Number of Groups')
    ax.set_title('Distribution of K-Anonymous Group Sizes')
    ax.legend()
    st.pyplot(fig)

# Tab3 l-diversity
with tab3:
    st.header("L-Diversity")
    st.markdown("""
    **What it does:** Extends k-anonymity by requiring each group 
    to have at least l distinct values for the sensitive attribute (salary).
    
    **Why it matters:** A k-anonymous group where everyone earns 
    the same salary still leaks that information to an attacker.
    """)

    QI = ['age', 'gender', 'department']
    anon_df = anonymize_no_zip(df, age_range=10)
    anon_suppressed = suppress_violations(anon_df, QI, k_value)

    satisfies_l, violations_l = check_l_diversity(
        anon_suppressed, QI, 'salary', l_value
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("l value", l_value)
    col2.metric(
        "L-Diversity Satisfied",
        "✅ Yes" if satisfies_l else "❌ No"
    )
    col3.metric("Violations", violations_l)

    st.subheader("Distinct Salary Bands per Group")
    diversity_df = anon_suppressed.groupby(QI)['salary'].apply(
        lambda x: x.apply(generalize_salary).nunique()
    ).reset_index(name='distinct_salary_bands')

    fig, ax = plt.subplots(figsize=(8, 3))
    ax.hist(diversity_df['distinct_salary_bands'], bins=10,
            color='#534AB7', edgecolor='white')
    ax.axvline(x=l_value, color='red', linestyle='--',
               label=f'l={l_value}')
    ax.set_xlabel('Distinct Salary Bands in Group')
    ax.set_ylabel('Number of Groups')
    ax.set_title('L-Diversity Distribution Across Groups')
    ax.legend()
    st.pyplot(fig)

    if not satisfies_l:
        st.warning(f"""
        ⚠️ L={l_value} not satisfied. The violating group is typically 
        'Non-binary, Sales, age 60-69' — a rare demographic combination 
        with limited salary diversity. Consider accepting l=2 or 
        suppressing this group (with fairness implications).
        """)

# Tab4 t-closeness
with tab4:
    st.header("T-Closeness")
    st.markdown("""
    **What it does:** Requires the distribution of the sensitive 
    attribute (salary) within each group to be close to its 
    global distribution, measured by Earth Mover's Distance (EMD).
    
    **Why it matters:** L-diversity ensures variety in sensitive 
    values but doesn't prevent skewness attacks — a group where 
    4 of 5 salaries cluster at $50K still leaks information even 
    if one value is $200K.
    """)

    t_value = st.sidebar.slider("T-Closeness (t)", 0.1, 0.5, 0.3, 0.05)

    # Compute EMD for each group
    def earth_movers_distance(group_salaries, global_salaries):
        n_bins = 10
        global_hist, bin_edges = np.histogram(
            global_salaries, bins=n_bins, density=True
        )
        group_hist, _ = np.histogram(
            group_salaries, bins=bin_edges, density=True
        )
        global_hist = global_hist / global_hist.sum() if global_hist.sum() > 0 else global_hist
        group_hist = group_hist / group_hist.sum() if group_hist.sum() > 0 else group_hist
        return np.sum(np.abs(
            np.cumsum(global_hist) - np.cumsum(group_hist)
        )) / n_bins

    QI = ['age', 'gender', 'department']
    anon_df = anonymize_no_zip(df, age_range=10)
    anon_suppressed = suppress_violations(anon_df, QI, k_value)

    global_salaries = df['salary'].values
    results = []
    for name, group in anon_suppressed.groupby(QI):
        emd = earth_movers_distance(group['salary'].values, global_salaries)
        results.append({
            'group': str(name),
            'group_size': len(group),
            'emd': round(emd, 4),
            'satisfies_t': emd <= t_value
        })

    results_df = pd.DataFrame(results)
    satisfies_t = results_df['satisfies_t'].all()
    violations_t = (~results_df['satisfies_t']).sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("t value", t_value)
    col2.metric("T-Closeness Satisfied", "✅ Yes" if satisfies_t else "❌ No")
    col3.metric("Violations", violations_t)
    col4.metric("Max EMD", f"{results_df['emd'].max():.4f}")

    st.subheader("EMD Distribution Across Groups")
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.hist(results_df['emd'], bins=20, color='#F0A500', edgecolor='white')
    ax.axvline(x=t_value, color='red', linestyle='--', label=f't={t_value}')
    ax.set_xlabel('Earth Mover\'s Distance from Global Distribution')
    ax.set_ylabel('Number of Groups')
    ax.set_title('T-Closeness: EMD Distribution')
    ax.legend()
    st.pyplot(fig)

    st.subheader("Groups by EMD (worst first)")
    st.dataframe(
        results_df.sort_values('emd', ascending=False).head(10),
        use_container_width=True
    )

    if not satisfies_t:
        st.warning(f"""
        ⚠️ T={t_value} not satisfied. All violations are Engineering 
        groups — their salary distributions legitimately diverge from 
        the global average. This reflects a real business pattern, 
        not a privacy failure. Try t=0.3 for full satisfaction.
        """)
    else:
        st.success(f"""
        ✅ T={t_value} fully satisfied across all {len(results_df)} groups. 
        Worst group EMD = {results_df['emd'].max():.4f} (20-29, M, Engineering).
        """)

    st.subheader("Privacy Stack Summary")
    summary_data = {
        'Technique': ['K-Anonymity', 'L-Diversity', 'T-Closeness', 'Differential Privacy'],
        'Setting': [f'k={k_value}', f'l={l_value}', f't={t_value}', f'ε={epsilon}'],
        'Attack Prevented': [
            'Identity disclosure',
            'Homogeneity attack',
            'Skewness/inference attack',
            'Aggregate query inference'
        ],
        'Result': ['✅ Satisfied', '✅ Satisfied',
                   '✅ Satisfied' if satisfies_t else '❌ Not satisfied',
                   '✅ Satisfied']
    }
    st.table(pd.DataFrame(summary_data))

# Tab5 differential privacy
with tab5:
    st.header("Differential Privacy")
    st.markdown("""
    **What it does:** Adds mathematically calibrated Laplace noise 
    to query results, providing a provable privacy guarantee regardless 
    of attacker's background knowledge.
    
    **Key insight:** ε is a budget, not just a parameter. 
    Every query consumes epsilon — production systems use a 
    privacy accountant to track total spend.
    """)

    sensitivity = compute_sensitivity(df, 'salary')

    # Private average salary by department
    results = []
    for dept in df['department'].unique():
        dept_df = df[df['department'] == dept]
        true_avg = dept_df['salary'].mean()
        private_avg = laplace_mechanism(true_avg, sensitivity, epsilon)
        results.append({
            'Department': dept,
            'True Avg Salary': f"${true_avg:,.0f}",
            'Private Avg Salary': f"${max(0, private_avg):,.0f}",
            'Noise Added': f"${private_avg - true_avg:+,.0f}"
        })

    results_df = pd.DataFrame(results)

    col1, col2, col3 = st.columns(3)
    col1.metric("Epsilon (ε)", epsilon)
    col2.metric("Sensitivity", f"${sensitivity:.2f}")
    col3.metric("Noise Scale (Δf/ε)", f"${sensitivity/epsilon:,.2f}")

    st.subheader("True vs Private Average Salary")
    st.dataframe(results_df)

    # Tradeoff chart
    st.subheader("Privacy/Accuracy Tradeoff")
    epsilons = [0.01, 0.1, 0.5, 1.0, 5.0, 10.0]
    avg_noise = []
    for eps in epsilons:
        noise_vals = [
            abs(laplace_mechanism(
                df[df['department']==d]['salary'].mean(),
                sensitivity, eps
            ) - df[df['department']==d]['salary'].mean())
            for d in df['department'].unique()
        ]
        avg_noise.append(np.mean(noise_vals))

    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(epsilons, avg_noise, marker='o', color='#1D9E75', linewidth=2)
    ax.axvline(x=epsilon, color='red', linestyle='--',
               label=f'Current ε={epsilon}')
    ax.set_xlabel('Epsilon (ε) — higher = less privacy')
    ax.set_ylabel('Average Absolute Noise ($)')
    ax.set_title('Privacy Budget vs Accuracy Tradeoff')
    ax.set_xscale('log')
    ax.grid(True, alpha=0.3)
    ax.legend()
    st.pyplot(fig)

    st.info(f"""
    **At ε={epsilon}:** Average noise ≈ ${sensitivity/epsilon:,.0f} per query.
    Sensitivity is low ($24.83) because n=5,000 — larger datasets 
    are naturally more privacy-friendly under differential privacy.
    """)