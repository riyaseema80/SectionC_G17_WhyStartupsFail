# Data Dictionary

**Project:** Why Startups Fail — VC Investment Pattern Analysis  
**Team:** Section C, Group 17 | Newton School of Technology | DVA Capstone 2  
**Dataset:** Crunchbase VC Investments (raw)  
**Source:** Kaggle — [investments_VC.csv](https://www.kaggle.com/datasets/arindam235/startup-investments-crunchbase)  
**Row Count (raw):** 54,294  
**Row Count (cleaned):** ~40,000–45,000 (after ETL)  
**Time Period:** ~1990 – 2023 (founded year)  

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
| `founded_year` | float | Founding year | Some implausible values (pre-1980); filtered |
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
| `primary_category` | string | First pipe-separated value from `category_list` (index 1) | Simplified sector filter for Tableau |
| `is_closed` | binary (0/1) | `1 if status == 'closed'` | **Target variable** — binary failure indicator |
| `reached_series_a` | binary (0/1) | `1 if round_A > 0 OR round_B > 0 OR round_C > 0` | Survival inflection-point indicator |
| `founding_decade` | integer | `(founded_year // 10) * 10` | Decade-level cohort grouping for time analysis |

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
| `reached_series_a` | Binary predictor | Series A Failure Rate differential |
| `market` | Categorical grouping | Failure Rate by Sector |
| `country_code` | Geographic grouping | Geographic Failure Heatmap |
| `founded_year` | Time dimension | Failure Rate Trend Over Time |
| `avg_funding_per_round` | Efficiency metric | Capital Efficiency by Status |

---

## Data Limitations

1. **Survivorship bias:** Startups with no digital presence may not appear in Crunchbase, understating the true failure rate.
2. **Status lag:** Recent startups (2018–2023) may still be classified as "operating" even if they have since closed — outcomes require time to materialise.
3. **Geographic skew:** The USA is heavily over-represented (~60% of records). Conclusions for other ecosystems have wider uncertainty bands.
4. **Funding amounts:** Some funding values are 0 or very small, which may reflect incomplete Crunchbase reporting rather than actual absence of investment.
5. **Market labels:** Market/sector classification is self-reported by startups and may be inconsistent across similar companies.

---

*Last updated: April 2026 | Section C, Group 17*
