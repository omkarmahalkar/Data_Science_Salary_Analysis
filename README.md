# 📊 Data Science Salary Pulse

An end-to-end data analytics project exploring global Data Science salaries through SQL, Python, Machine Learning, and Power BI — uncovering what drives compensation across roles, experience levels, and geographies (2020–2022).

---

## 📁 Project Structure
```
Data_Science_Salary_Analysis/
├── ds_salaries.csv                  # Raw dataset
├── ds_salaries_clean.csv            # Cleaned/preprocessed dataset
├── ds_analytics.py                  # Main Python analysis & ML script
├── DS Salary Pulse Queries.sql      # 10 SQL analytical queries
├── Data Science Salary Pulse.pbix   # Power BI interactive dashboard
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Tools |
|---|---|
| Database | MySQL |
| Analysis & EDA | Python, pandas, numpy |
| Visualization | Matplotlib, Seaborn |
| Machine Learning | scikit-learn (Random Forest Regressor) |
| BI Dashboard | Microsoft Power BI |

---

## 📂 Dataset

The dataset contains real-world salary records for Data Science professionals across countries, roles, and experience levels.

| Column | Description |
|---|---|
| `work_year` | Year the salary was recorded (2020–2022) |
| `experience_level` | EN = Entry, MI = Mid, SE = Senior, EX = Executive |
| `employment_type` | FT = Full-time, PT = Part-time, CT = Contract, FL = Freelance |
| `job_title` | Role title (e.g. Data Scientist, ML Engineer) |
| `salary_in_usd` | Salary normalized to USD |
| `remote_ratio` | 0 = On-site, 50 = Hybrid, 100 = Fully Remote |
| `company_size` | S = Small, M = Medium, L = Large |
| `employee_residence` | Country where the employee lives |
| `company_location` | Country where the company is based |

---

## ⚙️ Feature Engineering

The following new columns are derived in `ds_analytics.py` before analysis:

- **Experience** — Readable labels mapped from codes (Entry → Mid → Senior → Executive)
- **Work_Mode** — On-site, Hybrid, or Remote from `remote_ratio`
- **Company_Size** — Small, Medium, Large from `company_size`
- **Job_Cluster** — Job titles grouped into: `ML/AI`, `Engineer`, `Scientist`, `Analyst`, `Management`
- **Cross_Border** — Boolean flag: employee country ≠ company country
- **Salary_Tier** — Quartile-based bands: Low, Mid-Low, Mid-High, Top

---

## 🗄️ SQL Analysis

The `DS Salary Pulse Queries.sql` file includes **10 analytical queries**:

| # | Query | Purpose |
|---|---|---|
| 1 | Dataset Summary | Total records, year range, unique titles & countries |
| 2 | Salary by Experience | Avg/min/max salary and headcount per level |
| 3 | Top 10 Paying Roles | Highest average salaries (min 3 records filter) |
| 4 | Remote Work Premium | Salary comparison across On-site, Hybrid, Remote |
| 5 | Year-Over-Year Growth | YoY salary change in USD & % using window functions |
| 6 | Career ROI (CTE) | Entry → Senior salary growth % by job title |
| 7 | Cross-Border Arbitrage | Remote workers employed by foreign companies |
| 8 | Salary by Company Size | Avg salary across Small, Medium, Large companies |
| 9 | Experience × Company Size | Salary grid data for Power BI heatmap |
| 10 | Top Paying Countries | Countries with highest avg salaries (min 5 jobs) |

---

## 📈 Python Visualizations

The script generates **7 charts** saved as `.png` files:

| File | Chart | Description |
|---|---|---|
| `viz1_salary_by_experience.png` | Box + Violin Plot | Salary spread across experience levels |
| `viz2_remote_premium.png` | Bar Chart | Avg salary by work mode |
| `viz3_career_roi.png` | Lollipop Chart | Salary growth % from Entry to Senior by job cluster |
| `viz4_yoy_trend.png` | Line Chart | Mean & median salary trend 2020–2022 |
| `viz5_top_jobs.png` | Horizontal Bar | Top 10 highest paying job titles |
| `viz6_heatmap.png` | Heatmap | Avg salary by Experience × Company Size |
| `viz7_feature_importance.png` | Horizontal Bar | ML model feature importance scores |

---

## 🤖 Machine Learning Model

A **Random Forest Regressor** is trained to predict `salary_in_usd`.

**Input Features:** `experience_level`, `employment_type`, `remote_ratio`, `company_size`, `work_year`, `job_cluster`

**Pipeline:**
1. Label encoding for categorical columns
2. 80/20 train-test split
3. Random Forest with 200 estimators
4. Evaluated using **MAE** and **R² Score**

Feature importances are exported as `viz7_feature_importance.png`.

---

## 📊 Power BI Dashboard

Open `Data Science Salary Pulse.pbix` in Power BI Desktop. The dashboard is powered by `ds_salaries_for_powerbi.csv`, which is auto-generated at the end of the Python script with cleaned and renamed columns ready for reporting.

---

## 🚀 Getting Started

**1. Install dependencies**
```bash
pip install pandas numpy matplotlib seaborn scikit-learn mysql-connector-python
```

**2. Set up MySQL**

Create a database named `ds_project` and import `ds_salaries.csv` into a table called `ds_salaries`.

**3. Update credentials in `ds_analytics.py`**
```python
conn = mysql.connector.connect(
    host="localhost",
    user="your_username",
    password="your_password",
    database="ds_project"
)
```

**4. Run the script**
```bash
python ds_analytics.py
```

This will generate all 7 visualizations, print ML model metrics, and export the Power BI CSV.

**5. SQL Queries**

Run `DS Salary Pulse Queries.sql` in MySQL Workbench or any MySQL client against the `ds_project` database.

---

## 💡 Key Insights

- **Experience level** is the strongest predictor of salary — Executive roles earn significantly more than Entry-level across all clusters
- **Fully Remote** roles pay a premium on average over Hybrid and On-site positions
- **ML/AI and Management** job clusters offer the highest career ROI from Entry to Senior
- **Salaries grew consistently** year-over-year from 2020 to 2022, reflecting strong global demand for data talent
- **Large companies** generally pay higher, though mid-sized companies are competitive at senior levels
- **Cross-border remote work** creates salary arbitrage opportunities for employees in lower-cost countries working for high-paying employers

---

## 👤 Author

**Omkar Mahalkar**
