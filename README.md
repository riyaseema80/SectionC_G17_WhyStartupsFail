# SectionC_G17_WhyStartupsFail

> **Newton School of Technology | Data Visualization & Analytics | Capstone 2**  
> A 2-week industry simulation — converting raw VC investment data into actionable business intelligence using Python, GitHub, and Tableau.

---

## Before You Start

1. Clone the repository: `git clone https://github.com/riyaseema80/SectionC_G17_WhyStartupsFail`
2. Install dependencies: `pip install -r requirements.txt`
3. Place the raw dataset in `data/raw/investments_VC.csv`
4. Run notebooks in order from `01` to `05`, or run `python scripts/etl_pipeline.py` directly
5. Connect the processed CSVs in `data/processed/` to Tableau Public
6. Publish the dashboard and update the URL in `tableau/dashboard_links.md`

### Quick Start

```bash
# Clone and setup
git clone https://github.com/riyaseema80/SectionC_G17_WhyStartupsFail
cd SectionC_G17_WhyStartupsFail
python -m venv .venv
source .venv/bin/activate     # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook
```

If working in Google Colab: upload notebooks from `notebooks/` and keep final `.ipynb` files committed to GitHub.

---

## Project Overview

| Field | Details |
|---|---|
| **Project Title** | Why Startups Fail — VC Investment Pattern Analysis |
| **Sector** | Finance / Venture Capital / Startup Ecosystem |
| **Team ID** | Section C, Group 17 |
| **Section** | Section C |
| **Faculty Mentor** | *(To be filled)* |
| **Institute** | Newton School of Technology |
| **Submission Date** | *(To be filled)* |

### Team Members

| Role | Name | GitHub Username |
|---|---|---|
| Project Lead | *(Name)* | `@riyaseema80` |
| Data Lead | *(Name)* | `github-handle` |
| ETL Lead | *(Name)* | `github-handle` |
| Analysis Lead | *(Name)* | `github-handle` |
| Visualization Lead | *(Name)* | `github-handle` |
| Strategy Lead | *(Name)* | `github-handle` |
| PPT & Quality Lead | *(Name)* | `github-handle` |

---

## Business Problem

The global startup ecosystem is characterised by a well-known but poorly understood phenomenon: the majority of VC-backed startups ultimately fail. Despite billions of dollars in investment flowing into early-stage companies every year, investors, founders, and ecosystem builders lack a data-driven framework to identify which startups are most at risk, and when. This project analyses over 54,000 records of Crunchbase startup investment data to uncover the measurable, quantifiable patterns that separate surviving companies from those that close.

**Core Business Question**

> Which funding, sector, geographic, and timing factors are statistically significant predictors of startup failure — and what actionable thresholds can investors use to improve capital allocation decisions?

**Decision Supported**

> This analysis enables VC investors to build a data-backed screening framework that flags high-risk investment candidates before capital is deployed, and helps portfolio managers identify which existing investments require intervention.

---

## Dataset

| Attribute | Details |
|---|---|
| **Source Name** | Crunchbase Startup Investments (via Kaggle) |
| **Direct Access Link** | [Kaggle — Startup Investments Crunchbase](https://www.kaggle.com/datasets/arindam235/startup-investments-crunchbase) |
| **Row Count (raw)** | 54,294 |
| **Row Count (cleaned)** | ~40,000–45,000 |
| **Column Count** | 39 raw + 8 engineered = 47 total |
| **Time Period Covered** | ~1990 – 2023 (founding year) |
| **Format** | CSV |

**Key Columns Used**

| Column Name | Description | Role in Analysis |
|---|---|---|
| `status` | Startup outcome: operating / closed / acquired / ipo | **Target variable** |
| `funding_total_usd` | Total funding raised (USD) | Primary continuous predictor |
| `funding_rounds` | Number of funding rounds received | Count predictor |
| `market` | Primary sector/industry | Categorical grouping |
| `country_code` | ISO country code | Geographic filter |
| `founded_year` | Year company was founded | Time dimension |
| `round_A` | Series A funding amount | Survival signal feature |
| `is_closed` *(engineered)* | Binary target: 1 = closed, 0 = other | Logistic regression target |
| `reached_series_a` *(engineered)* | Binary: 1 = any Series A+ round | Inflection-point indicator |

For full column definitions, see [`docs/data_dictionary.md`](docs/data_dictionary.md).

---

## KPI Framework

| KPI | Definition | Formula / Computation |
|---|---|---|
| **Overall Failure Rate (%)** | Percentage of all startups that permanently closed | `closed_count / total_count × 100` |
| **Funding Gap ($)** | Median funding difference between operating and closed startups | `median(operating funding) − median(closed funding)` |
| **Series A Survival Differential (%)** | Failure rate gap between pre-Series A and post-Series A startups | `failure_rate(no Series A) − failure_rate(reached Series A)` |
| **Sector Failure Index** | Ranked failure rate per market sector (min. 50 startups) | `closed_in_sector / total_in_sector × 100` |
| **Avg Funding Rounds by Outcome** | Mean number of rounds per status group | `mean(funding_rounds) grouped by status` |
| **Capital Efficiency Ratio** | Average USD raised per funding round | `funding_total_usd / funding_rounds` |

All KPIs computed in `notebooks/04_statistical_analysis.ipynb` and exported via `notebooks/05_final_load_prep.ipynb`.

---

## Tableau Dashboard

| Item | Details |
|---|---|
| **Dashboard URL** | *(Paste Tableau Public link here after publishing)* |
| **Executive View** | KPI summary tiles, failure rate by status, funding gap summary |
| **Operational View** | Sector failure rate bar chart, geographic heatmap, funding scatter plot |
| **Trend View** | Year-over-year startup volume and failure rate dual-axis chart |
| **Main Filters** | Country, Market/Sector, Founding Decade, Status, Funding Round Count |

Dashboard screenshots are stored in [`tableau/screenshots/`](tableau/screenshots/). Links are documented in [`tableau/dashboard_links.md`](tableau/dashboard_links.md).

---

## Key Insights

*Written in decision language — what a stakeholder should think or act on:*

1. **~20–35% of all VC-backed startups permanently close** — failure is not a tail event; it is a mainstream outcome that demands systematic risk frameworks.
2. **Startups with only one funding round fail at the highest rate** — single-round companies represent the riskiest investment profile, requiring higher return hurdles to justify the risk.
3. **Reaching Series A is the single strongest survival signal in this dataset** — failure rates drop dramatically after Series A, confirming that institutional validation at this stage is a quality filter, not just capital.
4. **Closed startups receive a median of several multiples less funding than operating ones** — underfunding is a measurable, statistically significant predictor of failure (Mann-Whitney U, p < 0.001).
5. **Media, gaming, and consumer retail sectors consistently show above-average failure rates** — sector selection accounts for a statistically significant portion of outcome variance.
6. **The dot-com era (1999–2001) produced the highest concentrated failure cluster** — macro conditions amplify underlying business risk; temporal context matters in failure analysis.
7. **USA-based startups benefit from a mature ecosystem** — despite accounting for ~60% of records, the US failure rate is moderate relative to smaller, less-developed ecosystems.
8. **Longer funding duration (first to last round) correlates with survival** — startups that maintain investor engagement over time are significantly more likely to avoid closure.
9. **Funding rounds count is a stronger survival predictor than total funding amount** — sustained multi-round investment signals investor confidence more than a single large cheque.
10. **Logistic regression confirms that funding rounds, total capital, Series A attainment, and US location are all statistically significant independent predictors of survival.**

---

## Recommendations

| # | Insight Addressed | Recommendation | Expected Impact |
|---|---|---|---|
| 1 | Single-round startups have highest failure | VC firms should set minimum round-count thresholds before follow-on investment decisions; flag all single-round portfolio companies for a 90-day review | Reduce portfolio failure rate by 10–15% through early intervention |
| 2 | Underfunding predicts failure | Establish a minimum viable runway benchmark (e.g., $500K for seed-stage SaaS) below which investments require co-investor commitment before deployment | Reduce underfunding-related closures by improving deal structure |
| 3 | Series A is a survival inflection point | Prioritise portfolio support resources (mentorship, connections, follow-on capital) to help pre-Series A companies cross this threshold | Increase Series A conversion rate, substantially reducing closure risk |
| 4 | Sector failure rates are statistically significant | Build a sector-adjusted return hurdle model — require higher expected multiples for investments in high-failure sectors like media and gaming | Improve risk-adjusted return across the portfolio |
| 5 | Macro conditions amplify failure (dot-com parallel) | Implement a macro-sensitivity dashboard: monitor cohort failure rates quarterly and adjust deal velocity during economic downturns | Reduce vintage-year concentration risk and cycle-driven losses |

---

## Repository Structure

```
SectionC_G17_WhyStartupsFail/
│
├── README.md
│
├── data/
│   ├── raw/                         ← Original dataset (never edited)
│   │   └── investments_VC.csv
│   └── processed/                   ← Cleaned ETL outputs
│       ├── startups_cleaned.csv
│       ├── tableau_master.csv
│       ├── kpi_summary.csv
│       ├── country_level_summary.csv
│       ├── sector_level_summary.csv
│       ├── yearly_trend_summary.csv
│       └── etl_run_log.csv
│
├── notebooks/
│   ├── 01_extraction.ipynb
│   ├── 02_cleaning.ipynb
│   ├── 03_eda.ipynb
│   ├── 04_statistical_analysis.ipynb
│   └── 05_final_load_prep.ipynb
│
├── scripts/
│   └── etl_pipeline.py              ← Standalone full pipeline script
│
├── tableau/
│   ├── screenshots/                 ← Dashboard + EDA chart exports
│   └── dashboard_links.md
│
├── reports/
│   ├── project_report.pdf           ← Final report (to be added)
│   └── presentation.pdf            ← Slide deck (to be added)
│
├── docs/
│   └── data_dictionary.md
│
├── DVA-oriented-Resume/
└── DVA-focused-Portfolio/
```

---

## Analytical Pipeline

| Step | Phase | Description |
|---|---|---|
| 1 | **Define** | Sector selected (VC/Finance), problem statement scoped, mentor approval obtained (Gate 1) |
| 2 | **Extract** | Raw dataset sourced (54,294 rows), committed to `data/raw/`; data dictionary drafted |
| 3 | **Clean & Transform** | 10-step Python ETL pipeline in `notebooks/02_cleaning.ipynb` and `scripts/etl_pipeline.py` |
| 4 | **Analyze** | EDA (8 visualisations) + 6 statistical analyses in notebooks 03 and 04 |
| 5 | **Visualize** | Interactive Tableau dashboard built and published on Tableau Public |
| 6 | **Recommend** | 5 data-backed business recommendations delivered with expected impact |
| 7 | **Report** | Final report PDF + presentation deck committed to `reports/` |

---

## Tech Stack

| Tool | Status | Purpose |
|---|---|---|
| Python + Jupyter Notebooks | Mandatory | ETL, cleaning, analysis, KPI computation |
| Google Colab | Supported | Cloud notebook execution |
| Tableau Public | Mandatory | Dashboard design, publishing, sharing |
| GitHub | Mandatory | Version control, collaboration, contribution audit |
| pandas, numpy | Core libraries | Data manipulation and engineering |
| matplotlib, seaborn | Visualisation | EDA charts |
| scipy, statsmodels | Statistics | Hypothesis testing, regression |

---

## Evaluation Rubric

| Area | Marks | Focus |
|---|---|---|
| Problem Framing | 10 | Is the business question clear and well-scoped? |
| Data Quality & ETL | 15 | Is the Python pipeline thorough and documented? |
| Analysis Depth | 25 | Are statistical methods applied correctly with insight? |
| Dashboard & Visualization | 20 | Is the Tableau dashboard interactive and decision-relevant? |
| Business Recommendations | 20 | Are insights actionable and well-reasoned? |
| Storytelling & Clarity | 10 | Is the presentation professional and coherent? |
| **Total** | **100** | |

---

## Submission Checklist

**GitHub Repository**
- [ ] Public repository with naming convention `SectionC_G17_WhyStartupsFail`
- [ ] All notebooks committed in `.ipynb` format
- [ ] `data/raw/` contains original, unedited dataset
- [ ] `data/processed/` contains all 6 cleaned output files
- [ ] `tableau/screenshots/` contains dashboard screenshots
- [ ] `tableau/dashboard_links.md` contains Tableau Public URL
- [ ] `docs/data_dictionary.md` is complete
- [ ] README explains project, dataset, and team
- [ ] All members have visible commits and pull requests

**Tableau Dashboard**
- [ ] Published on Tableau Public (public URL)
- [ ] At least one interactive filter included
- [ ] Dashboard directly addresses the business question

**Project Report (PDF — 10–15 pages)**
- [ ] Cover page, executive summary, sector context
- [ ] ETL methodology, KPI framework
- [ ] EDA with insights, statistical analysis results
- [ ] Dashboard screenshots and explanation
- [ ] 8–12 key insights, 3–5 recommendations
- [ ] Contribution matrix matches GitHub history

**Presentation Deck (PPT/PDF — 10–12 slides)**
- [ ] All slides from title through limitations/next steps

---

## Contribution Matrix

| Team Member | Dataset & Sourcing | ETL & Cleaning | EDA & Analysis | Statistical Analysis | Tableau Dashboard | Report Writing | PPT & Viva |
|---|---|---|---|---|---|---|---|
| Member 1 | Owner | Support | Support | Support | Support | Support | Support |
| Member 2 | Support | Owner | Support | Support | Support | Support | Support |
| Member 3 | Support | Support | Owner | Support | Support | Support | Support |
| Member 4 | Support | Support | Support | Owner | Support | Support | Support |
| Member 5 | Support | Support | Support | Support | Owner | Support | Support |
| Member 6 | Support | Support | Support | Support | Support | Owner | Support |
| Member 7 | Support | Support | Support | Support | Support | Support | Owner |

*Declaration: We confirm the above contribution details are accurate and verifiable through GitHub Insights, PR history, and submitted artifacts.*

---

## Academic Integrity

All analysis, code, and recommendations in this repository are the original work of Section C, Group 17. Free-riding is tracked via GitHub Insights and pull request history. Any mismatch between the contribution matrix and actual commit history may result in individual grade adjustments.

---

*Newton School of Technology — Data Visualization & Analytics | Capstone 2 | Section C, Group 17*
