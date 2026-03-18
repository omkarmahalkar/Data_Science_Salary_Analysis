-- QUERY 1: BASIC DATASET SUMMARY
SELECT
    COUNT(*) AS total_records,
    MIN(work_year) AS earliest_year,
    MAX(work_year) AS latest_year,
    COUNT(DISTINCT job_title) AS unique_job_titles,
    COUNT(DISTINCT company_location) AS total_countries,
    ROUND(AVG(salary_in_usd), 0) AS overall_avg_salary
FROM ds_salaries;


-- QUERY 2: SALARY STATISTICS BY EXPERIENCE LEVEL
SELECT
    CASE experience_level
        WHEN 'EN' THEN '1 - Entry Level'
        WHEN 'MI' THEN '2 - Mid Level'
        WHEN 'SE' THEN '3 - Senior'
        WHEN 'EX' THEN '4 - Executive'
    END AS experience,
    COUNT(*) AS headcount,
    ROUND(AVG(salary_in_usd), 0) AS avg_salary,
    MIN(salary_in_usd) AS min_salary,
    MAX(salary_in_usd) AS max_salary,
    ROUND(MAX(salary_in_usd) - MIN(salary_in_usd), 0) AS salary_range
FROM ds_salaries
GROUP BY experience_level
ORDER BY experience;

-- QUERY 3: TOP 10 HIGHEST PAYING JOB TITLES
SELECT
    job_title,
    COUNT(*) AS job_count,
    ROUND(AVG(salary_in_usd), 0) AS avg_salary,
    MIN(salary_in_usd) AS min_salary,
    MAX(salary_in_usd) AS max_salary
FROM ds_salaries
GROUP BY job_title
HAVING COUNT(*) > 3
ORDER BY avg_salary DESC
LIMIT 10;

-- QUERY 4: REMOTE WORK SALARY PREMIUM ANALYSIS
SELECT
    CASE remote_ratio
        WHEN 0   THEN 'On-site'
        WHEN 50  THEN 'Hybrid'
        WHEN 100 THEN 'Fully Remote'
    END AS work_mode,
    COUNT(*) AS total_roles,
    ROUND(AVG(salary_in_usd), 0) AS avg_salary,
    ROUND(MAX(salary_in_usd), 0) AS max_salary,
    ROUND(MIN(salary_in_usd), 0) AS min_salary
FROM ds_salaries
GROUP BY remote_ratio
ORDER BY avg_salary DESC;

-- QUERY 5: YEAR-OVER-YEAR SALARY GROWTH
SELECT
    work_year,
    COUNT(*) AS total_records,
    ROUND(AVG(salary_in_usd), 0) AS avg_salary,
    ROUND(
        AVG(salary_in_usd) - LAG(AVG(salary_in_usd)) OVER (ORDER BY work_year),
    0) AS yoy_change_usd,
    ROUND(
        (AVG(salary_in_usd) - LAG(AVG(salary_in_usd)) OVER (ORDER BY work_year))
        / LAG(AVG(salary_in_usd)) OVER (ORDER BY work_year) * 100,
    1) AS yoy_growth_pct
FROM ds_salaries
GROUP BY work_year
ORDER BY work_year;

-- QUERY 6: CAREER ROI — BEST GROWTH FROM ENTRY TO SENIOR (CTE)
WITH level_salaries AS (
    SELECT
        job_title,
        experience_level,
        AVG(salary_in_usd) AS avg_salary
    FROM ds_salaries
    GROUP BY job_title, experience_level
),
entry_salaries AS (
    SELECT job_title, avg_salary AS entry_avg
    FROM level_salaries
    WHERE experience_level = 'EN'
),
senior_salaries AS (
    SELECT job_title, avg_salary AS senior_avg
    FROM level_salaries
    WHERE experience_level = 'SE'
)

SELECT
    e.job_title,
    ROUND(e.entry_avg, 0) AS entry_level_salary,
    ROUND(s.senior_avg, 0) AS senior_level_salary,
    ROUND(s.senior_avg - e.entry_avg, 0) AS absolute_growth,
    ROUND((s.senior_avg - e.entry_avg) / e.entry_avg * 100, 1) AS career_roi_pct
FROM entry_salaries e
JOIN senior_salaries s ON e.job_title = s.job_title
WHERE e.entry_avg > 0
ORDER BY career_roi_pct DESC
LIMIT 10;

-- QUERY 7: CROSS-BORDER SALARY ARBITRAGE
SELECT
    employee_residence AS worker_country,
    company_location AS employer_country,
    COUNT(*) AS num_workers,
    ROUND(AVG(salary_in_usd), 0) AS avg_salary,
    MIN(salary_in_usd) AS min_salary,
    MAX(salary_in_usd) AS max_salary
FROM ds_salaries
WHERE employee_residence <> company_location
  AND remote_ratio = 100
GROUP BY employee_residence, company_location
HAVING COUNT(*) >= 2
ORDER BY avg_salary DESC;

-- QUERY 8: SALARY BY COMPANY SIZE
SELECT
    CASE company_size
        WHEN 'S' THEN 'Small'
        WHEN 'M' THEN 'Medium'
        WHEN 'L' THEN 'Large'
    END AS company_size,
    COUNT(*) AS total_employees,
    ROUND(AVG(salary_in_usd), 0) AS avg_salary,
    MAX(salary_in_usd) AS max_salary
FROM ds_salaries
GROUP BY company_size
ORDER BY avg_salary DESC;

-- QUERY 9: SALARY HEATMAP DATA — EXPERIENCE vs COMPANY SIZE
SELECT
    CASE experience_level
        WHEN 'EN' THEN 'Entry'
        WHEN 'MI' THEN 'Mid'
        WHEN 'SE' THEN 'Senior'
        WHEN 'EX' THEN 'Executive'
    END AS experience,
    CASE company_size
        WHEN 'S' THEN 'Small'
        WHEN 'M' THEN 'Medium'
        WHEN 'L' THEN 'Large'
    END AS company_size,
    COUNT(*) AS total,
    ROUND(AVG(salary_in_usd), 0) AS avg_salary
FROM ds_salaries
GROUP BY experience_level, company_size
ORDER BY experience, company_size;

-- QUERY 10: TOP PAYING COUNTRIES
SELECT
    company_location AS country,
    COUNT(*) AS job_count,
    ROUND(AVG(salary_in_usd), 0) AS avg_salary
FROM ds_salaries
GROUP BY company_location
HAVING COUNT(*) >= 5
ORDER BY avg_salary DESC
LIMIT 15;