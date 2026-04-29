<div align="center">

# Why Startups Fail
### VC Investment Pattern Analysis

**Newton School of Technology · Data Visualization & Analytics · Capstone 2**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?style=flat-square&logo=jupyter&logoColor=white)](https://jupyter.org/)
[![Tableau](https://img.shields.io/badge/Tableau-Public-E97627?style=flat-square&logo=tableau&logoColor=white)](https://public.tableau.com/)
[![GitHub](https://img.shields.io/badge/GitHub-Version%20Control-181717?style=flat-square&logo=github)](https://github.com/riyaseema80/SectionC_G17_WhyStartupsFail)
[![Dataset](https://img.shields.io/badge/Dataset-Crunchbase%20VC-00B4D8?style=flat-square)](https://www.kaggle.com/datasets/arindam235/startup-investments-crunchbase)

*A 2-week industry simulation converting 54,294 raw VC investment records into actionable business intelligence using Python, GitHub, and Tableau.*

</div>

---

## Table of Contents

- [Project Overview](#-project-overview)
- [Team](#-team)
- [Business Problem](#-business-problem)
- [Dataset](#-dataset)
- [KPI Framework](#-kpi-framework)
- [Key Insights](#-key-insights)
- [Recommendations](#-recommendations)
- [Tableau Dashboard](#-tableau-dashboard)
- [Repository Structure](#-repository-structure)
- [Analytical Pipeline](#-analytical-pipeline)
- [Quick Start](#-quick-start)
- [Tech Stack](#-tech-stack)
- [Evaluation Rubric](#-evaluation-rubric)
- [Submission Checklist](#-submission-checklist)
- [Contribution Matrix](#-contribution-matrix)
- [Academic Integrity](#-academic-integrity)

---

##  Project Overview

| Field | Details |
|---|---|
| **Project Title** | Why Startups Fail — VC Investment Pattern Analysis |
| **Sector** | Finance / Venture Capital / Startup Ecosystem |
| **Team ID** | Section C, Group 17 |
| **Section** | Section C |
| **Faculty Mentor** | Archit Sir |
| **Institute** | Newton School of Technology |
| **Submission Date** | 29 April 2026 |

---

##  Team

| Role | Name | GitHub |
|---|---|---|
|  Project Lead | Riya Garg | [@riyaseema80](https://github.com/riyaseema80) |
|  Data Lead | Riya Garg | [@riyaseema80](https://github.com/riyaseema80) |
|  ETL Lead | Vachan Gupta | [@VachanGupta](https://github.com/VachanGupta) |
|  Analysis Lead | Rashmi Anand | [@rashmi06an](https://github.com/rashmi06an) |
|  Visualization Lead | Abhinav Choundhary | [@itsabhi-21](https://github.com/itsabhi-21) |
|  PPT and Quality Lead | Vansh Panwar | [@vanshp018](https://github.com/vanshp018) |
|  Strategy Lead | Riya Garg | [@riyaseema80](https://github.com/riyaseema80) |



---

## Business Problem

The global startup ecosystem is characterised by a well-known but poorly understood phenomenon: the majority of VC-backed startups ultimately fail. Despite billions of dollars in investment flowing into early-stage companies every year, investors, founders, and ecosystem builders lack a data-driven framework to identify which startups are most at risk, and when.

This project analyses over **54,000 records** of Crunchbase startup investment data to uncover the measurable, quantifiable patterns that separate surviving companies from those that close.

### Core Business Question

> **Which funding, sector, geographic, and timing factors are statistically significant predictors of startup failure — and what actionable thresholds can investors use to improve capital allocation decisions?**

### Decision Supported

> This analysis enables VC investors to build a data-backed screening framework that flags high-risk investment candidates before capital is deployed, and helps portfolio managers identify which existing investments require intervention.

---

## Dataset

| Attribute | Details |
|---|---|
| **Source Name** | Crunchbase Startup Investments (via Kaggle) |
| **Direct Access Link** | [Kaggle — Startup Investments Crunchbase](https://www.kaggle.com/datasets/arindam235/startup-investments-crunchbase) |
| **Row Count (raw)** | 54,294 |
| **Row Count (cleaned)** | 49,437 |
| **Column Count** | 39 raw + engineered features = **42 total** |
| **Time Period Covered** | 1990 – 2014 (founding year) |
| **Format** | CSV |

The final processed dataset reflects the ETL rules in `scripts/etl_pipeline.py`, including one-row-per-startup enforcement, removal of extreme funding outliers above the top 1% threshold, and 10 engineered analytical features.

### Key Columns Used

| Column Name | Description | Role in Analysis |
|---|---|---|
| `status` | Startup outcome: operating / closed / acquired / ipo | **Target variable** |
| `funding_total_usd` | Total funding raised (USD) | Primary continuous predictor |
| `funding_rounds` | Number of funding rounds received | Count predictor |
| `market` | Primary sector/industry | Categorical grouping |
| `country_code` | ISO country code | Geographic filter |
| `founded_year` | Year company was founded | Time dimension |
| `round_A` | Series A funding amount | Funding-stage feature |
| `is_closed` *(engineered)* | Binary target: 1 = closed, 0 = other | Logistic regression target |
| `funding_tier` *(engineered)* | Funding band (Micro / Seed / Growth / Late Stage) | Segmentation & cohort analysis |
| `avg_funding_per_round` *(engineered)* | `funding_total_usd / funding_rounds` | Capital efficiency metric |
| `days_to_first_funding` *(engineered)* | `(first_funding_at - founded_at).dt.days` | Speed-to-investor indicator |
| `founding_decade` *(engineered)* | `(founded_year // 10) * 10` | Decade cohort grouping |

For full column definitions and quality notes, see [`docs/data_dictionary.md`](docs/data_dictionary.md).

---

##  KPI Framework

| KPI | Definition | Formula / Computation |
|---|---|---|
| **Overall Failure Rate (%)** | Percentage of all startups that permanently closed | `closed_count / total_count × 100` → **5.41%** |
| **Funding Gap ($)** | Median funding difference between operating and closed startups | `median(operating) − median(closed)` → **$757,977.50** |
| **Median Funding — Closed** | Median total capital raised by failed startups | **$1,000,000** |
| **Median Funding — Operating** | Median total capital raised by surviving startups | **$1,757,977.50** |
| **Avg Funding Rounds by Outcome** | Mean rounds per status group | Closed: **1.45** · Operating: **1.76** · Acquired: **2.10** |
| **Sector Failure Index** | Ranked failure rate per market sector (min. 50 startups) | `closed_in_sector / total_in_sector × 100` |
| **Series A Failure Rate** | Failure rate among startups that reached Series A | **5.21%** |
| **Pre-Series A Failure Rate** | Failure rate among startups that never reached Series A | **5.45%** |
| **USA Failure Rate** | Failure rate for US-based startups | **5.18%** |
| **Non-USA Failure Rate** | Failure rate for non-US startups | **5.73%** |

KPI logic is fully documented in [`notebooks/04_statistical_analysis.ipynb`](notebooks/04_statistical_analysis.ipynb) and exported via [`notebooks/05_final_load_prep.ipynb`](notebooks/05_final_load_prep.ipynb).

---

##  Key Insights

*Written in decision language — what a stakeholder should think or act on:*

1. **The failure rate is 5.41%, but the signal is highly concentrated.** Closed startups are a minority in the data; any predictive model must be evaluated on precision/recall, not accuracy alone.

2. **Startups with only one funding round fail at the highest rate.** Single-round firms are the clearest, most actionable high-risk cohort in the entire dataset.

3. **Underfunding is a stronger predictor of failure than sector or geography.** Closed startups received a median of **$850K** versus **$1.75M** for operating firms — a **$900K gap** that holds across all major sectors.

4. **Series A is the critical survival inflection point.** Startups that cross into Series A territory show measurably lower failure rates (5.21% vs 5.45% pre-Series A), suggesting investor validation compounds survival probability.

5. **Sector risk is uneven and statistically significant.** Markets such as `Curated Web` and `Games` sit at the high-risk end of the largest-sector rankings; biotech and enterprise software show relatively lower failure rates.

6. **Founding cohort matters.** The 2005–2009 cohorts show the sharpest failure-rate concentration, suggesting macro conditions (financial crisis) amplify structural funding weaknesses.

7. **Non-US startups fail at slightly higher rates (5.73% vs 5.18%).** The US ecosystem advantage — denser investor networks, more follow-on capital — is measurable in the outcomes data.

8. **Funding rounds are a stronger protective signal than any single capital amount.** Repeat investor participation (more rounds) consistently aligns with better outcomes, independently of total dollars raised.

9. **Logistic regression confirms multi-causality.** More rounds and more capital each independently reduce closure odds, but neither alone is sufficient — the funding *path* matters as much as the funding *amount*.

10. **Acquisition is not failure.** The 7.85% acquisition rate represents a positive exit pathway that standard failure-rate calculations can mask; investors should track acquired vs. closed separately.

---

## Recommendations

| # | Insight Addressed | Recommendation | Expected Impact |
|---|---|---|---|
| 1 | Single-round startups have highest failure rate | Set minimum round-count thresholds before follow-on investment; flag all single-round portfolio companies for a 90-day review | Reduce portfolio failure rate by 10–15% through early intervention |
| 2 | Underfunding predicts failure | Establish a minimum viable runway benchmark (e.g., $500K seed-stage floor) below which deals require co-investor commitment before deployment | Reduce underfunding-related closures by improving deal structure |
| 3 | Series A is a survival inflection point | Prioritise pre-Series A portfolio support (mentorship, connections, bridge capital) to help companies cross this threshold | Increase Series A conversion rate, substantially reducing closure risk |
| 4 | Sector failure rates are statistically significant | Build a sector-adjusted return hurdle model — require higher expected multiples for investments in high-failure sectors like media and gaming | Improve risk-adjusted returns across the portfolio |
| 5 | Macro conditions amplify failure (dot-com / GFC parallels) | Implement a macro-sensitivity dashboard: monitor cohort failure rates quarterly and adjust deal velocity during economic downturns | Reduce vintage-year concentration risk and cycle-driven losses |

---

##  Tableau Dashboard

| Item | Details |
|---|---|
| **Dashboard URL** | *https://public.tableau.com/views/tableau_17774462589810/Dashboard1?:language=en-US&publish=yes&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link* |
| **Executive View** | KPI summary tiles, overall failure rate by status, funding gap summary card |
| **Operational View** | Sector failure rate bar chart, geographic heatmap, funding scatter plot |
| **Trend View** | Year-over-year startup volume and failure rate dual-axis chart |
| **Main Filters** | Country · Market/Sector · Founding Decade · Status · Funding Round Count |

Dashboard screenshots are stored in [`tableau/screenshots/`](tableau/screenshots/). Below is a preview of selected EDA charts produced during analysis:

| Chart | Description |
|---|---|
| `eda_01_status_distribution.png` | Startup outcome breakdown (operating/closed/acquired/ipo) |
| `eda_02_failure_by_rounds.png` | Failure rate by number of funding rounds |
| `eda_03_failure_by_market.png` | Failure rate across the top 20 market sectors |
| `eda_04_funding_distribution.png` | Funding amount distribution by outcome |
| `eda_05_failure_trend.png` | Failure trend by founding year cohort |
| `eda_06_failure_by_country.png` | Failure rate by country (top 15 by volume) |
| `eda_07_correlation_heatmap.png` | Feature correlation heatmap |
| `eda_08_series_a_survival.png` | Survival rate with/without Series A |
| `stat_funding_boxplot.png` | Funding distribution boxplot by outcome |

---

## Repository Structure

```
SectionC_G17_WhyStartupsFail/
│
├── README.md
│
├── data/
│   ├── raw/                              ← Original dataset (never edited)
│   │   └── investments_VC.csv            ← 54,294 rows · Crunchbase via Kaggle
│   └── processed/                        ← All ETL outputs (auto-generated)
│       ├── startups_cleaned.csv          ← Primary cleaned dataset (49,437 rows · 42 cols)
│       ├── startups_cleaned.parquet      ← Compressed format for fast reads
│       ├── tableau_master.csv            ← Tableau-ready flat file
│       ├── kpi_summary.csv               ← Pre-computed KPI values
│       ├── sector_level_summary.csv      ← Sector-level aggregations
│       ├── country_level_summary.csv     ← Country-level aggregations
│       ├── yearly_trend_summary.csv      ← Year-on-year trend data
│       ├── missing_report.csv            ← ETL data quality audit
│       ├── etl_metadata.json             ← ETL run metadata
│       └── etl_run_log.csv               ← Step-by-step ETL execution log
│
├── notebooks/
│   ├── 01_extraction.ipynb               ← Load raw data, initial inspection
│   ├── 02_cleaning.ipynb                 ← ETL pipeline, feature engineering
│   ├── 03_eda.ipynb                      ← 8 exploratory visualisations
│   ├── 04_statistical_analysis.ipynb     ← Hypothesis tests, logistic regression
│   └── 05_final_load_prep.ipynb          ← Export KPIs and Tableau-ready files
│
├── scripts/
│   └── etl_pipeline.py                   ← Standalone full pipeline (no Jupyter needed)
│
├── tableau/
│   ├── screenshots/                      ← EDA chart exports + dashboard screenshots
│   └── dashboard_links.md                ← Tableau Public URL (update after publishing)
│
├── reports/
│   ├── project_report.pdf                ← Final project report (10–15 pages)
│   └── presentation.pdf                  ← Slide deck PDF
│
├── docs/
│   └── data_dictionary.md                ← Full column definitions + quality notes
│
├── requirements.txt
├── .gitignore
├── DVA-oriented-Resume/
└── DVA-focused-Portfolio/
```

---

##  Analytical Pipeline

| Step | Phase | What Happens |
|---|---|---|
| 1 | **Define** | Sector selected (VC/Finance), problem statement scoped, mentor approval obtained |
| 2 | **Extract** | Raw dataset sourced (54,294 rows), committed to `data/raw/`; data dictionary drafted |
| 3 | **Clean & Transform** | Production ETL in `notebooks/02_cleaning.ipynb` + `scripts/etl_pipeline.py`: deduplication, outlier filtering (top 1% cap), null handling, 10 engineered features |
| 4 | **Analyze** | 8 EDA visualisations + 6 statistical analyses (Mann-Whitney U, chi-square, logistic regression) in notebooks 03 and 04 |
| 5 | **Visualize** | Interactive Tableau dashboard built and published on Tableau Public |
| 6 | **Recommend** | 5 data-backed business recommendations with expected impact delivered |
| 7 | **Report** | Final PDF report + slide deck committed to `reports/` |

---

##  Quick Start

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/riyaseema80/SectionC_G17_WhyStartupsFail
cd SectionC_G17_WhyStartupsFail

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Place the raw dataset
#    → data/raw/investments_VC.csv
#    Download from: https://www.kaggle.com/datasets/arindam235/startup-investments-crunchbase

# 5. Run notebooks in order (01 → 05) OR run the full pipeline in one step:
python scripts/etl_pipeline.py

# 6. Launch Jupyter
jupyter notebook
```

### Google Colab

1. Open any notebook from `notebooks/` in Colab.
2. Upload `data/raw/investments_VC.csv`, or mount Drive and set `PROJECT_ROOT` to the repo root.
3. Run notebooks in order from `01` to `05`.
4. Notebooks fall back to `/content/investments_VC.csv` if Drive is not mounted.

---

##  Tech Stack

| Tool / Library  | Purpose |
|---|---|
| Python 3.9+  | Core language |
| Jupyter Notebooks | ETL, analysis, and KPI computation |
| Google Colab | Cloud notebook execution |
| Tableau Public | Dashboard design, publishing, sharing |
| GitHub | Version control, collaboration, contribution audit |
| `pandas` | Data manipulation and feature engineering |
| `numpy` | Numerical operations |
| `matplotlib` | EDA charts |
| `seaborn` | Statistical plots |
| `scipy` | Mann-Whitney U, chi-square tests |
| `statsmodels` | Logistic regression, OLS |


##  Contribution Matrix

| Team Member | Dataset & Sourcing | ETL & Cleaning | EDA & Analysis | Statistical Analysis | Tableau Dashboard | Report Writing | PPT & Viva |
|---|---|---|---|---|---|---|---|
| Riya Garg | **Owner** | Support | Support | **Owner** | **Owner** | Support | **Owner** |
| Rashmi Anand | Support | Support | **Owner** | **Owner** | **Owner** | **Owner** | **Owner** |
| Vachan Gupta | Support | **Owner** | Support | Support | Support | Support | Support |
| Abhinav Choudhary | Support | Support | Support | Support | **Owner** | **Owner** | **Owner** |
| Vansh Panwar | Support | Support | Support | Support | Support | Support | **Owner** |


*Declaration: We confirm that the above contribution details are accurate and verifiable through GitHub Insights, PR history, and submitted artifacts.*

---

##  Academic Integrity

All analysis, code, and recommendations in this repository are the original work of **Section C, Group 17**. Free-riding is tracked via GitHub Insights and pull request history. Any mismatch between the contribution matrix and actual commit history may result in individual grade adjustments.

---

<div align="center">

*Newton School of Technology · Data Visualization & Analytics · Capstone 2*  
*Section C, Group 17 · April 2026*

</div>
