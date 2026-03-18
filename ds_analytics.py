import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import mysql.connector
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import LabelEncoder

# CONNECT TO MYSQL & LOAD DATA

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="omkarmahalkar45",
    database="ds_project"
)

df = pd.read_sql("SELECT * FROM ds_salaries", conn)
conn.close()

print("Connected successfully!")
print("Shape:", df.shape)
print(df.head())


# FEATURE ENGINEERING

exp_map    = {'EN': 'Entry', 'MI': 'Mid', 'SE': 'Senior', 'EX': 'Executive'}
emp_map    = {'FT': 'Full-time', 'PT': 'Part-time', 'CT': 'Contract', 'FL': 'Freelance'}
size_map   = {'S': 'Small', 'M': 'Medium', 'L': 'Large'}
remote_map = {0: 'On-site', 50: 'Hybrid', 100: 'Remote'}

df['Experience']      = df['experience_level'].map(exp_map)
df['Employment_Type'] = df['employment_type'].map(emp_map)
df['Company_Size']    = df['company_size'].map(size_map)
df['Work_Mode']       = df['remote_ratio'].map(remote_map)

exp_order = ['Entry', 'Mid', 'Senior', 'Executive']
df['Experience'] = pd.Categorical(df['Experience'], categories=exp_order, ordered=True)

def cluster_title(title):
    title = title.lower()
    if any(w in title for w in ['machine learning', 'ml ', 'deep learning', 'ai ']): return 'ML/AI'
    if 'engineer' in title: return 'Engineer'
    if 'scientist' in title: return 'Scientist'
    if 'analyst' in title: return 'Analyst'
    if any(w in title for w in ['manager', 'director', 'head', 'lead']): return 'Management'
    return 'Other'

df['Job_Cluster']  = df['job_title'].apply(cluster_title)
df['Cross_Border'] = df['employee_residence'] != df['company_location']
df['Salary_Tier']  = pd.qcut(df['salary_in_usd'], q=4, labels=['Low', 'Mid-Low', 'Mid-High', 'Top'])

print("\nFeature engineering done!")
print(df[['Experience', 'Work_Mode', 'Job_Cluster', 'Salary_Tier']].head(10))


# VISUALIZATION 1 — Salary by Experience Level

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Salary Distribution by Experience Level', fontsize=16, fontweight='bold')

sns.boxplot(data=df, x='Experience', y='salary_in_usd',
            order=exp_order, palette='Blues', ax=axes[0])
axes[0].set_title('Box Plot — Spread & Outliers')
axes[0].set_xlabel('Experience Level')
axes[0].set_ylabel('Salary (USD)')
axes[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))

sns.violinplot(data=df, x='Experience', y='salary_in_usd',
               order=exp_order, palette='Blues', ax=axes[1])
axes[1].set_title('Violin Plot — Distribution Shape')
axes[1].set_xlabel('Experience Level')
axes[1].set_ylabel('')
axes[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))

plt.tight_layout()
plt.savefig('viz1_salary_by_experience.png', dpi=150, bbox_inches='tight')
plt.close()  # FIX: close after saving so next chart starts fresh
print("Saved: viz1_salary_by_experience.png")


# VISUALIZATION 2 — Remote Work Salary Premium

remote_avg = df.groupby('Work_Mode', observed=True)['salary_in_usd'].mean().sort_values(ascending=False)

plt.figure(figsize=(8, 5))
colors = ['#1F4E79', '#2E75B6', '#BDD7EE']
bars = plt.bar(remote_avg.index, remote_avg.values, color=colors[:len(remote_avg)], edgecolor='white')

for bar, val in zip(bars, remote_avg.values):
    plt.text(bar.get_x() + bar.get_width() / 2,
             bar.get_height() + 1000,
             f'${val:,.0f}', ha='center', fontweight='bold', fontsize=11)

plt.title('Average Salary by Work Mode', fontsize=14, fontweight='bold')
plt.xlabel('Work Mode')
plt.ylabel('Average Salary (USD)')
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
plt.tight_layout()
plt.savefig('viz2_remote_premium.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: viz2_remote_premium.png")


# VISUALIZATION 3 — Career ROI Lollipop Chart

df['Experience_str'] = df['Experience'].astype(str)
entry_senior = df[df['Experience_str'].isin(['Entry', 'Senior'])].copy()

pivot = entry_senior.groupby(['Job_Cluster', 'Experience_str'], observed=True)['salary_in_usd'] \
    .mean().unstack()


pivot = pivot[['Entry', 'Senior']].dropna()
pivot['roi_pct'] = ((pivot['Senior'] - pivot['Entry']) / pivot['Entry'] * 100).round(1)
pivot = pivot.sort_values('roi_pct', ascending=True)

fig, ax = plt.subplots(figsize=(10, 6))
y_pos = range(len(pivot))

ax.hlines(y=y_pos, xmin=0, xmax=pivot['roi_pct'], color='#BDD7EE', linewidth=3)
ax.plot(pivot['roi_pct'], y_pos, 'o', color='#1F4E79', markersize=14, zorder=5)

for i, (idx, row) in enumerate(pivot.iterrows()):
    ax.annotate(f"+{row['roi_pct']:.0f}%",
                xy=(row['roi_pct'], i), xytext=(8, 0),
                textcoords='offset points', va='center',
                fontweight='bold', fontsize=12)

ax.set_yticks(list(y_pos))
ax.set_yticklabels(pivot.index, fontsize=12)
ax.set_xlabel('Salary Growth % (Entry → Senior)', fontsize=12)
ax.set_title('Career ROI by Job Cluster', fontsize=14, fontweight='bold')
ax.set_xlim(0, pivot['roi_pct'].max() * 1.3)
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig('viz3_career_roi.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: viz3_career_roi.png")


# VISUALIZATION 4 — Year-Over-Year Salary Trend

yearly = df.groupby('work_year')['salary_in_usd'].agg(['mean', 'median']).reset_index()

plt.figure(figsize=(9, 5))
plt.plot(yearly['work_year'], yearly['mean'], 'o-', color='#1F4E79',
         linewidth=2.5, markersize=10, label='Mean Salary')
plt.plot(yearly['work_year'], yearly['median'], 's--', color='#2E75B6',
         linewidth=2.5, markersize=10, label='Median Salary')

for _, row in yearly.iterrows():
    plt.annotate(f"${row['mean']:,.0f}",
                 (row['work_year'], row['mean']),
                 textcoords='offset points', xytext=(0, 12),
                 ha='center', fontsize=10, fontweight='bold')

plt.title('DS Salary Growth 2020–2022', fontsize=14, fontweight='bold')
plt.xlabel('Year')
plt.ylabel('Salary (USD)')
plt.legend(fontsize=11)
plt.xticks([2020, 2021, 2022])
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
plt.tight_layout()
plt.savefig('viz4_yoy_trend.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: viz4_yoy_trend.png")



# VISUALIZATION 5 — Top 10 Paying Job Titles


top_titles = (
    df.groupby('job_title')['salary_in_usd']
    .agg(['mean', 'count'])
    .query('count > 3')
    .sort_values('mean', ascending=True)
    .tail(10)
)

plt.figure(figsize=(10, 7))
bars = plt.barh(top_titles.index, top_titles['mean'], color='#1F4E79', edgecolor='white')

for bar, val in zip(bars, top_titles['mean']):
    plt.text(bar.get_width() + 1000,
             bar.get_y() + bar.get_height() / 2,
             f'${val:,.0f}', va='center', fontsize=10, fontweight='bold')

plt.title('Top 10 Highest Paying Data Science Roles', fontsize=14, fontweight='bold')
plt.xlabel('Average Salary (USD)')
plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
plt.tight_layout()
plt.savefig('viz5_top_jobs.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: viz5_top_jobs.png")



# VISUALIZATION 6 — Salary Heatmap (Experience x Company Size)

heatmap_data = df.groupby(['Experience', 'Company_Size'], observed=True)['salary_in_usd'] \
    .mean().unstack()


size_order = [s for s in ['Small', 'Medium', 'Large'] if s in heatmap_data.columns]
heatmap_data = heatmap_data[size_order]

heatmap_data = heatmap_data.reindex([e for e in exp_order if e in heatmap_data.index])

plt.figure(figsize=(8, 5))
sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap='Blues',
            linewidths=0.5, cbar_kws={'label': 'Avg Salary (USD)'})
plt.title('Avg Salary Heatmap — Experience vs Company Size',
          fontsize=13, fontweight='bold')
plt.xlabel('Company Size')
plt.ylabel('Experience Level')
plt.tight_layout()
plt.savefig('viz6_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: viz6_heatmap.png")



# MACHINE LEARNING — SALARY PREDICTION MODEL

print("\n--- Building Salary Prediction Model ---")

df_ml = df[['experience_level', 'employment_type', 'remote_ratio',
            'company_size', 'work_year', 'Job_Cluster', 'salary_in_usd']].dropna().copy()

le = LabelEncoder()
cat_cols = ['experience_level', 'employment_type', 'company_size', 'Job_Cluster']
for col in cat_cols:
    df_ml[col] = le.fit_transform(df_ml[col].astype(str))

features = ['experience_level', 'employment_type', 'remote_ratio',
            'company_size', 'work_year', 'Job_Cluster']

X = df_ml[features]
y = df_ml['salary_in_usd']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2  = r2_score(y_test, y_pred)

print(f"Mean Absolute Error : ${mae:,.0f}")
print(f"R² Score            : {r2:.3f}")



# FEATURE IMPORTANCE CHART


importance_df = pd.DataFrame({
    'Feature': features,
    'Importance': model.feature_importances_
}).sort_values('Importance', ascending=True)

plt.figure(figsize=(9, 5))
bars = plt.barh(importance_df['Feature'], importance_df['Importance'], color='#1F4E79')

for bar, val in zip(bars, importance_df['Importance']):
    plt.text(bar.get_width() + 0.002,
             bar.get_y() + bar.get_height() / 2,
             f'{val:.3f}', va='center', fontsize=10)

plt.title('Feature Importance — What Drives Salary?', fontsize=14, fontweight='bold')
plt.xlabel('Importance Score')
plt.tight_layout()
plt.savefig('viz7_feature_importance.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved: viz7_feature_importance.png")


# EXPORT CLEAN CSV FOR POWER BI

df_export = df[[
    'work_year', 'Experience', 'Employment_Type', 'job_title',
    'Job_Cluster', 'salary_in_usd', 'Work_Mode', 'remote_ratio',
    'employee_residence', 'company_location', 'Company_Size',
    'Cross_Border', 'Salary_Tier'
]].copy()

df_export.columns = [
    'Year', 'Experience', 'Employment_Type', 'Job_Title',
    'Job_Cluster', 'Salary_USD', 'Work_Mode', 'Remote_Ratio',
    'Employee_Country', 'Company_Country', 'Company_Size',
    'Cross_Border', 'Salary_Tier'
]

df_export.to_csv('ds_salaries_for_powerbi.csv', index=False)
print(f"\nExported {len(df_export)} rows → ds_salaries_for_powerbi.csv")
