# Data Dictionary

**Project:** Why Startups Fail — VC Investment Pattern Analysis  
**Team:** Section C, Group 17 | Newton School of Technology | DVA Capstone 2  
**Dataset:** Crunchbase VC Investments (raw)  
**Source:** Kaggle — [investments_VC.csv](https://www.kaggle.com/datasets/arindam235/startup-investments-crunchbase)  
**Unit of Analysis (Grain):** One row represents one startup entity (not individual funding rounds).  
**Row Count (raw):** 54,294  
**Row Count (cleaned):** 33,613 (after ETL)  
**Time Period:** 1990 – 2014 (founded year)  

---

## Original Columns (Raw Dataset)

| Column Name | Data Type (Raw) | Description | Quality Issues |
|---|---|---|---|
| `permalink` | string | Crunchbase unique URL slug for the company | No analysis value — identifier only |
| `name` | string | Company/startup name | Some special characters and encoding issues |
| `homepage_url` | string | Company website URL | High missing rate; not used in analysis |
| `category_list` | string | Pipe-separated list of sector tags (e.g., `\|Software\|B2B\|`) | Requires parsing; first meaningful tag extracted |
| `market` | string | Primary market label (e.g., "Software", "Biotechnology") | Leading/trailing whitespace present |
| `funding_total_usd` | string | Total funding received in USD | Stored as string with commas; dash for missing |
| `status` | string | Current startup status | Values: operating, closed, acquired, ipo; some missing |
| `country_code` | string | ISO 3-letter country code | High missing rate for non-USA records |
| `state_code` | string | US state code | Only relevant for USA startups |
| `region` | string | Geographic region within country | ~40% missing |
| `city` | string | City of headquarters | ~30% missing |
| `funding_rounds` | integer | Number of funding rounds received | Mostly complete |
| `founded_at` | string | Company founding date (YYYY-MM-DD) | ~30% missing; parsed to datetime |
| `founded_month` | string | Founding month (YYYY-MM format) | Redundant with `founded_at` |
| `founded_quarter` | string | Founding quarter (YYYY-QN format) | Redundant with `founded_at` |
| `founded_year` | float | Founding year | Older/sparse records outside the final 1990–2014 window were filtered |
| `first_funding_at` | string | Date of first funding event | Parsed to datetime |
| `last_funding_at` | string | Date of most recent funding event | Parsed to datetime |
| `seed` | float | Amount raised via seed funding (USD) | 0 if no seed round |
| `venture` | float | Amount raised via venture funding (USD) | 0 if none |
| `equity_crowdfunding` | float | Amount from equity crowdfunding (USD) | 0 if none |
| `undisclosed` | float | Undisclosed funding amount (USD) | 0 if none |
| `convertible_note` | float | Convertible note amount (USD) | 0 if none |
| `debt_financing` | float | Debt financing amount (USD) | 0 if none |
| `angel` | float | Angel investment amount (USD) | 0 if none |
| `grant` | float | Government/institutional grant amount (USD) | 0 if none |
| `private_equity` | float | Private equity amount (USD) | 0 if none |
| `post_ipo_equity` | float | Post-IPO equity amount (USD) | 0 if none |
| `post_ipo_debt` | float | Post-IPO debt amount (USD) | 0 if none |
| `secondary_market` | float | Secondary market transactions (USD) | 0 if none |
| `product_crowdfunding` | float | Product crowdfunding amount (USD) | 0 if none |
| `round_A` | float | Series A amount (USD) | 0 if no Series A |
| `round_B` | float | Series B amount (USD) | 0 if none |
| `round_C` | float | Series C amount (USD) | 0 if none |
| `round_D` | float | Series D amount (USD) | 0 if none |
| `round_E` | float | Series E amount (USD) | 0 if none |
| `round_F` | float | Series F amount (USD) | 0 if none |
| `round_G` | float | Series G amount (USD) | 0 if none |
| `round_H` | float | Series H amount (USD) | 0 if none |

---

## Engineered Columns (Added in ETL)

| Column Name | Data Type | Formula / Derivation | Purpose in Analysis |
|---|---|---|---|
| `days_to_first_funding` | integer | `(first_funding_at - founded_at).dt.days` | Measures how quickly startup attracted investors |
| `funding_duration_days` | integer | `(last_funding_at - first_funding_at).dt.days` | Measures investor engagement duration (runway proxy) |
| `avg_funding_per_round` | float | `funding_total_usd / funding_rounds` | Capital efficiency metric |
| `is_usa` | binary (0/1) | `1 if country_code == 'USA'` | Controls for ecosystem effect |
| `primary_category` | string | Extracted as the first non-empty value from the pipe-separated `category_list` (typically index 1 due to the leading pipe delimiter) | Simplified sector filter for Tableau |
| `is_closed` | binary (0/1) | `1 if status == 'closed'` | **Target variable** — binary failure indicator |
| `founding_decade` | integer | `(founded_year // 10) * 10` | Decade-level cohort grouping for time analysis |
| `funding_tier` | string | Bucket `funding_total_usd` into tiers (e.g., Low / Medium / High) | Simplifies segmentation analysis |
| `has_seed` | binary (0/1) | `1 if seed > 0` | Early-stage funding indicator |

---

## Final Dataset (Post-ETL)

**Final cleaned dataset:** `data/processed/startups_cleaned.csv`  
**Total Columns:** 48  
**Total Rows:** 33,613  

### Column Categories

- **Identifiers:** `name`, `permalink`
- **Target:** `is_closed`
- **Numerical:** `funding_total_usd`, `funding_rounds`, `avg_funding_per_round`, `days_to_first_funding`, `funding_duration_days`, funding-stage amount columns (`seed` to `round_H`)
- **Categorical:** `status`, `market`, `country_code`, `state_code`, `region`, `city`, `primary_category`, `funding_tier`, `category_list`
- **Time:** `founded_at`, `founded_month`, `founded_quarter`, `founded_year`, `first_funding_at`, `last_funding_at`, `founding_decade`
- **Binary:** `is_usa`, `has_seed`

This dataset serves as the single source of truth for all downstream EDA, statistical analysis, and modeling.

---

## Target Variable

`is_closed`:
- `1` -> Startup failed (`status = closed`)
- `0` -> Startup survived or achieved a positive exit (`status = operating`, `acquired`, or `ipo`)

**Note:** Acquired and IPO outcomes are treated as successful outcomes, not failures.

---

## Cleaning Summary

| Step | Action |
|---|---|
| Column trimming | Removed leading/trailing whitespace from text fields such as `market` and status labels |
| Funding conversion | Converted funding fields from string to numeric format using vectorised parsing after removing commas and placeholder symbols |
| Dates | Parsed `founded_at`, `first_funding_at`, and `last_funding_at` to datetime |
| Missing status | Dropped records with missing startup status because the target variable could not be derived |
| Duplicate enforcement | Enforced the project grain of one row per startup by removing duplicate startup records |
| Outliers | Removed extreme funding observations above the top 1% threshold and filtered `founded_year` to the final valid range of `1990-2014` |

---

## Units & Scale Clarification

- All funding values are recorded in **USD**
- Log scale is used in visualisations where specified for heavily skewed funding distributions
- Duration-based variables such as `days_to_first_funding` and `funding_duration_days` are measured in **days**

---

## Missing Data Handling Strategy

Missing values in non-critical fields such as `region` and `city` were retained to preserve row coverage. Missing values in critical analytical fields such as `status` resulted in row removal because the target variable could not be derived reliably.

---

## Status Field — Canonical Values

| Value | Meaning | Analytical Treatment |
|---|---|---|
| `operating` | Company is still active and operating | Baseline comparison group |
| `closed` | Company has shut down permanently | **Primary outcome of interest** (is_closed = 1) |
| `acquired` | Company was acquired by another entity | Positive exit outcome |
| `ipo` | Company has gone public (initial public offering) | Strongest positive exit outcome |

---

## Key Analytical Variables (Used in KPI and Dashboard)

| Variable | Role | KPI Linked |
|---|---|---|
| `is_closed` | Target / outcome variable | Overall Failure Rate |
| `funding_total_usd` | Primary continuous predictor | Funding Gap (Closed vs Operating) |
| `funding_rounds` | Count predictor | Avg Rounds by Status |
| `funding_tier` | Segmentation variable | Failure Rate by Funding Band |
| `market` | Categorical grouping | Failure Rate by Sector |
| `country_code` | Geographic grouping | Geographic Failure Heatmap |
| `founded_year` | Time dimension | Failure Rate Trend Over Time |
| `avg_funding_per_round` | Efficiency metric | Capital Efficiency by Status |

---

## Data Limitations

1. **Survivorship bias:** Startups with no digital presence may not appear in Crunchbase, understating the true failure rate.
2. **Status lag:** More recent startups in the final dataset (especially 2010–2014 cohorts) may still be classified as "operating" even if they later closed — outcomes require time to materialise.
3. **Geographic skew:** The USA is heavily over-represented (~60% of records). Conclusions for other ecosystems have wider uncertainty bands.
4. **Funding amounts:** Some funding values are 0 or very small, which may reflect incomplete Crunchbase reporting rather than actual absence of investment.
5. **Market labels:** Market/sector classification is self-reported by startups and may be inconsistent across similar companies.

---

*Last updated: April 2026 | Section C, Group 17*

All transformations are reproducible via the ETL pipeline defined in Notebook 02 — Data Cleaning & ETL.
