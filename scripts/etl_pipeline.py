"""ETL pipeline for SectionC_G17_WhyStartupsFail — Why Startups Fail.

Newton School of Technology | DVA Capstone 2 | Section C, Group 17

Pipeline overview
-----------------
Step 1  Strip whitespace from column names
Step 2  Convert funding columns from mixed-string to float
Step 3  Parse date columns to datetime64
Step 4  Validate temporal ordering (founded_at <= first_funding_at)
Step 5  Drop rows whose target variable (status) is missing
Step 6  Remove duplicate startup rows and enforce one row per startup
Step 7  Filter founding year to the valid analytical window (1990–2014)
Step 8  Handle extreme funding outliers
Step 9  Engineer derived features (is_closed, reached_series_a, etc.)
Step 10 Validate analytical assumptions
Step 11 Persist cleaned dataset, parquet export, missing report, metadata, and ETL log

Run from the project root::

    python scripts/etl_pipeline.py \\
        --input  data/raw/investments_VC.csv \\
        --output data/processed/startups_cleaned.csv

Or import individual helpers in notebooks::

    from scripts.etl_pipeline import build_clean_dataset, save_processed
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import sys
from pathlib import Path
from typing import NamedTuple

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
RAW_ENCODING: str = "latin-1"

# Columns containing funding amounts that should be converted to float.
FUNDING_AMOUNT_COLS: list[str] = [
    "funding_total_usd",
    "seed",
    "venture",
    "equity_crowdfunding",
    "undisclosed",
    "convertible_note",
    "debt_financing",
    "angel",
    "grant",
    "private_equity",
    "post_ipo_equity",
    "post_ipo_debt",
    "secondary_market",
    "product_crowdfunding",
    "round_A",
    "round_B",
    "round_C",
    "round_D",
    "round_E",
    "round_F",
    "round_G",
    "round_H",
]

DATE_COLS: list[str] = ["founded_at", "first_funding_at", "last_funding_at"]

# Only keep founding years within this closed interval.
YEAR_MIN: int = 1990
YEAR_MAX: int = 2014

# Canonical status values; anything outside this set is treated as unknown.
VALID_STATUS_VALUES: set[str] = {"operating", "closed", "acquired", "ipo"}

# Columns kept in the final cleaned export (order matters for readability).
FINAL_COLUMNS: list[str] = [
    "name",
    "status",
    "is_closed",
    "country_code",
    "state_code",
    "region",
    "city",
    "is_usa",
    "market",
    "primary_category",
    "founded_at",
    "founded_month",
    "founded_quarter",
    "founded_year",
    "founding_decade",
    "first_funding_at",
    "last_funding_at",
    "funding_rounds",
    "funding_total_usd",
    "avg_funding_per_round",
    "funding_tier",
    "has_seed",
    "reached_series_a",
    "days_to_first_funding",
    "funding_duration_days",
    "seed",
    "venture",
    "angel",
    "round_A",
    "round_B",
    "round_C",
    "round_D",
    "round_E",
    "round_F",
    "round_G",
    "round_H",
]

ETL_VERSION: str = "v1.0"


# ---------------------------------------------------------------------------
# ETL log helper
# ---------------------------------------------------------------------------
class StepRecord(NamedTuple):
    """Immutable record of one ETL transformation step."""

    step: int
    description: str
    rows_before: int
    rows_after: int
    rows_dropped: int
    detail: str


_etl_log: list[StepRecord] = []


def _log_step(
    step: int,
    description: str,
    rows_before: int,
    rows_after: int,
    detail: str = "",
) -> None:
    """Append a record to the in-memory ETL log and emit an INFO line."""
    dropped = rows_before - rows_after
    record = StepRecord(step, description, rows_before, rows_after, dropped, detail)
    _etl_log.append(record)
    log.info(
        "Step %02d | %-50s | rows: %6d → %6d  (−%d)",
        step,
        description,
        rows_before,
        rows_after,
        dropped,
    )


def etl_log_to_dataframe() -> pd.DataFrame:
    """Return the accumulated ETL log as a DataFrame."""
    return pd.DataFrame(_etl_log)


# ---------------------------------------------------------------------------
# Step helpers
# ---------------------------------------------------------------------------
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert column names to clean snake_case.

    Strips leading/trailing whitespace, lowercases everything, replaces any
    run of non-alphanumeric characters with a single underscore, and removes
    leading/trailing underscores from the result.

    Parameters
    ----------
    df:
        Input DataFrame whose columns will be renamed.

    Returns
    -------
    pd.DataFrame
        A copy of *df* with standardised column names.
    """
    cleaned = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )
    result = df.copy()
    result.columns = cleaned
    return result


def _parse_funding_value(val: object) -> float:
    """Convert a raw funding string or number to a Python float.

    Handles:
    - Already-numeric values (int, float).
    - Comma-formatted strings such as ``"1,750,000"``.
    - Placeholder strings such as ``"-"``, ``"N/A"``, ``"none"``.
    - ``pd.NA`` and ``np.nan``.

    Returns ``np.nan`` for any value that cannot be interpreted as a number.
    """
    if pd.isna(val):
        return np.nan
    if isinstance(val, (int, float)):
        return float(val) if not np.isnan(float(val)) else np.nan
    cleaned = str(val).strip().replace(",", "").replace(" ", "")
    if cleaned.lower() in {"-", "", "nan", "none", "n/a", "na", "null"}:
        return np.nan
    try:
        return float(cleaned)
    except ValueError:
        return np.nan


def missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return missing-value counts and percentages for every column."""
    return pd.DataFrame(
        {
            "missing_count": df.isna().sum(),
            "missing_pct": (df.isna().mean() * 100).round(2),
        }
    ).sort_values("missing_pct", ascending=False)


def _coerce_numeric_funding(series: pd.Series) -> pd.Series:
    """Vectorised conversion for currency-like funding columns."""
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")

    as_string = series.astype("string").str.strip()
    cleaned = (
        as_string.str.replace(",", "", regex=False)
        .str.replace(" ", "", regex=False)
        .mask(as_string.str.lower().isin(["-", "", "nan", "none", "n/a", "na", "null"]))
    )
    return pd.to_numeric(cleaned, errors="coerce")


def _extract_primary_category(category_list_series: pd.Series) -> pd.Series:
    """Extract the first meaningful tag from a pipe-delimited category string.

    Crunchbase stores categories as ``"|Software|B2B|"``; the leading pipe
    means index 0 is empty, so the first real tag is at index 1.

    Returns a ``pd.Series`` of strings (``pd.NA`` where unavailable).
    """
    return (
        category_list_series.astype("string")
        .str.strip()
        .str.strip("|")
        .str.split("|")
        .apply(
            lambda parts: next(
                (p.strip() for p in (parts if isinstance(parts, list) else []) if p.strip()),
                pd.NA,
            )
        )
    )


def _bucket_funding(series: pd.Series) -> pd.Series:
    """Bin continuous funding amounts into four labelled tiers.

    Boundaries (USD):
        - ``"Micro"``    : < 100 000
        - ``"Seed"``     : 100 000 – 999 999
        - ``"Growth"``   : 1 000 000 – 9 999 999
        - ``"Late Stage"``: ≥ 10 000 000
        - ``"Unknown"``  : NaN / zero

    Returns a ``pd.Series`` of strings.
    """
    bins = [0, 100_000, 1_000_000, 10_000_000, np.inf]
    labels = ["Micro", "Seed", "Growth", "Late Stage"]
    bucketed = pd.cut(series, bins=bins, labels=labels, right=False)
    return bucketed.astype("string").fillna("Unknown")


# ---------------------------------------------------------------------------
# Core pipeline
# ---------------------------------------------------------------------------
def basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Apply safe, format-agnostic cleaning steps.

    Steps applied:
    1. Column names normalised to snake_case via :func:`normalize_columns`.
    2. Exact duplicate rows removed.
    3. All object-dtype columns stripped of leading/trailing whitespace.

    Parameters
    ----------
    df:
        Raw input DataFrame.

    Returns
    -------
    pd.DataFrame
        Cleaned copy.
    """
    result = normalize_columns(df)
    result = result.drop_duplicates().reset_index(drop=True)
    for col in result.select_dtypes(include="object").columns:
        result[col] = result[col].astype("string").str.strip()
    return result


def build_clean_dataset(input_path: Path) -> pd.DataFrame:
    """Execute the full 10-step ETL pipeline on the raw CSV.

    Each step is logged to the in-memory ETL log (retrievable via
    :func:`etl_log_to_dataframe`).  The function is idempotent — calling it
    again on the same file resets and rebuilds the log from scratch.

    Parameters
    ----------
    input_path:
        Path to the raw CSV file (``data/raw/investments_VC.csv``).

    Returns
    -------
    pd.DataFrame
        Cleaned, feature-engineered DataFrame ready for EDA and Tableau.

    Raises
    ------
    FileNotFoundError
        If *input_path* does not exist.
    """
    global _etl_log
    _etl_log = []  # Reset so repeated calls do not accumulate stale records.

    if not input_path.exists():
        raise FileNotFoundError(f"Raw data file not found: {input_path}")

    # ── Load ─────────────────────────────────────────────────────────────────
    log.info("Loading raw data from: %s", input_path)
    df = pd.read_csv(input_path, encoding=RAW_ENCODING, low_memory=False)
    log.info("Raw shape: %d rows × %d columns", *df.shape)
    initial_rows = len(df)

    # ── Step 1: Normalise column names ────────────────────────────────────────
    before = len(df)
    original_cols = df.columns.tolist()
    df = normalize_columns(df)
    renamed = [
        f"'{o}' → '{n}'"
        for o, n in zip(original_cols, df.columns.tolist())
        if o != n
    ]
    _log_step(1, "Normalise column names to snake_case", before, len(df),
              f"{len(renamed)} columns renamed" if renamed else "No renames needed")

    # ── Step 2: Convert funding columns to float ──────────────────────────────
    before = len(df)
    present_funding_cols = [c for c in FUNDING_AMOUNT_COLS if c in df.columns]
    for col in present_funding_cols:
        df[col] = _coerce_numeric_funding(df[col])
    _log_step(
        2,
        "Convert funding columns to float",
        before,
        len(df),
        f"Vectorised numeric conversion for {len(present_funding_cols)} columns",
    )

    # ── Step 3: Parse date columns ────────────────────────────────────────────
    before = len(df)
    present_date_cols = [c for c in DATE_COLS if c in df.columns]
    for col in present_date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    _log_step(3, "Parse date columns to datetime64", before, len(df),
              f"Columns: {present_date_cols}")

    # ── Step 4: Validate temporal ordering ────────────────────────────────────
    before = len(df)
    if "founded_at" in df.columns and "first_funding_at" in df.columns:
        invalid_mask = (
            df["first_funding_at"].notna()
            & df["founded_at"].notna()
            & (df["first_funding_at"] < df["founded_at"])
        )
        df = df[~invalid_mask].reset_index(drop=True)
        _log_step(4, "Remove rows: first_funding_at < founded_at", before, len(df),
                  f"{invalid_mask.sum()} temporally inconsistent records removed")
    else:
        _log_step(4, "Remove rows: first_funding_at < founded_at", before, len(df),
                  "Skipped — date columns absent")

    # ── Step 5: Drop rows missing the target variable ─────────────────────────
    before = len(df)
    if "status" in df.columns:
        df["status"] = df["status"].astype("string").str.strip().str.lower()
        df = df[df["status"].isin(VALID_STATUS_VALUES)].reset_index(drop=True)
        _log_step(5, "Drop rows with missing/invalid status", before, len(df),
                  f"Valid values: {sorted(VALID_STATUS_VALUES)}")
    else:
        _log_step(5, "Drop rows with missing/invalid status", before, len(df),
                  "Skipped — 'status' column absent")

    # ── Step 6: Remove duplicate startup rows ────────────────────────────────
    before = len(df)
    dedupe_keys = [c for c in ["permalink", "name", "country_code", "founded_year"] if c in df.columns]
    if "permalink" in df.columns:
        df = df.drop_duplicates(subset=["permalink"], keep="first").reset_index(drop=True)
    elif all(c in df.columns for c in ["name", "country_code", "founded_year"]):
        df = df.drop_duplicates(subset=["name", "country_code", "founded_year"], keep="first").reset_index(drop=True)

    if "name" in df.columns:
        df = df.drop_duplicates(subset=["name"], keep="first").reset_index(drop=True)

    _log_step(
        6,
        "Remove duplicate startup rows",
        before,
        len(df),
        f"Unit-of-analysis keys enforced: {dedupe_keys or ['name']}",
    )

    # ── Step 7: Filter founding year to valid window ──────────────────────────
    before = len(df)
    if "founded_year" in df.columns:
        df["founded_year"] = pd.to_numeric(df["founded_year"], errors="coerce")
        df = df[df["founded_year"].between(YEAR_MIN, YEAR_MAX)].reset_index(drop=True)
        _log_step(7, f"Filter founded_year to {YEAR_MIN}–{YEAR_MAX}", before, len(df),
                  f"{before - len(df)} records outside window removed")
    else:
        _log_step(7, f"Filter founded_year to {YEAR_MIN}–{YEAR_MAX}", before, len(df),
                  "Skipped — 'founded_year' column absent")

    # ── Step 8: Handle extreme funding outliers ──────────────────────────────
    before = len(df)
    if "funding_total_usd" in df.columns:
        outlier_cap = df["funding_total_usd"].quantile(0.99)
        df = df[df["funding_total_usd"].isna() | (df["funding_total_usd"] <= outlier_cap)].reset_index(drop=True)
        _log_step(
            8,
            "Filter extreme funding outliers at 99th percentile",
            before,
            len(df),
            f"Upper threshold: {outlier_cap:,.0f} USD",
        )
    else:
        _log_step(8, "Filter extreme funding outliers at 99th percentile", before, len(df),
                  "Skipped — 'funding_total_usd' column absent")

    # ── Step 9: Engineer derived features ────────────────────────────────────
    before = len(df)

    # Binary target
    df["is_closed"] = (df["status"] == "closed").astype("int8")

    # Geography flag
    df["is_usa"] = (
        df["country_code"].astype("string").str.upper().fillna("") == "USA"
    ).astype("int8")

    # Simplified category extracted from the pipe-delimited list
    if "category_list" in df.columns:
        df["primary_category"] = _extract_primary_category(df["category_list"])

    # Series A attainment — treat any positive value in A/B/C columns as reached
    series_a_cols = [c for c in ["round_A", "round_B", "round_C"] if c in df.columns]
    if series_a_cols:
        df["reached_series_a"] = (
            df[series_a_cols].fillna(0).gt(0).any(axis=1)
        ).astype("int8")

    # Time-to-first-funding (days)
    if "founded_at" in df.columns and "first_funding_at" in df.columns:
        df["days_to_first_funding"] = (
            df["first_funding_at"] - df["founded_at"]
        ).dt.days

    # Funding duration (days between first and last round)
    if "first_funding_at" in df.columns and "last_funding_at" in df.columns:
        df["funding_duration_days"] = (
            df["last_funding_at"] - df["first_funding_at"]
        ).dt.days

    # Capital efficiency
    if "funding_rounds" in df.columns:
        df["funding_rounds"] = pd.to_numeric(df["funding_rounds"], errors="coerce")

    if "funding_total_usd" in df.columns and "funding_rounds" in df.columns:
        df["avg_funding_per_round"] = np.where(
            df["funding_rounds"] > 0,
            df["funding_total_usd"] / df["funding_rounds"],
            np.nan,
        )

    # Decade cohort
    if "founded_year" in df.columns:
        df["founding_decade"] = (df["founded_year"] // 10 * 10).astype("Int64")

    # Seed presence flag
    if "seed" in df.columns:
        df["has_seed"] = (df["seed"].fillna(0) > 0).astype("int8")

    # Funding tier buckets
    if "funding_total_usd" in df.columns:
        df["funding_tier"] = _bucket_funding(df["funding_total_usd"])

    _log_step(9, "Engineer 10 derived features", before, len(df),
              "is_closed, is_usa, primary_category, reached_series_a, "
              "days_to_first_funding, funding_duration_days, avg_funding_per_round, "
              "founding_decade, has_seed, funding_tier")

    # ── Step 10: Validate analytical assumptions ─────────────────────────────
    before = len(df)
    assert df["funding_total_usd"].dropna().ge(0).all(), "Negative funding found"
    if "funding_rounds" in df.columns:
        assert df["funding_rounds"].dropna().ge(0).all(), "Invalid funding rounds"
    if "name" in df.columns:
        assert df["name"].is_unique, "Duplicate startups found"
    if "founded_year" in df.columns:
        assert df["founded_year"].between(YEAR_MIN, YEAR_MAX).all(), "Founded year outside allowed window"
    if "days_to_first_funding" in df.columns:
        assert df["days_to_first_funding"].dropna().ge(0).all(), "Negative days_to_first_funding found"
    if "funding_duration_days" in df.columns:
        assert df["funding_duration_days"].dropna().ge(0).all(), "Negative funding duration found"
    _log_step(10, "Validate analytical assumptions", before, len(df),
              "Assertions passed for funding, rounds, dates, founded year, and startup uniqueness")

    # ── Step 11: Final column selection and type normalisation ───────────────
    before = len(df)
    present_final_cols = [c for c in FINAL_COLUMNS if c in df.columns]
    extra_cols = [c for c in df.columns if c not in FINAL_COLUMNS]
    df = df[present_final_cols + extra_cols]

    # Ensure text fields use the efficient pandas StringDtype
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype("string")

    _log_step(11, "Select and reorder final columns", before, len(df),
              f"{len(present_final_cols)} ordered columns + {len(extra_cols)} extras")

    df.attrs["etl_version"] = ETL_VERSION
    df.attrs["processed_on"] = datetime.datetime.now().isoformat(timespec="seconds")
    df.attrs["unit_of_analysis"] = "One row represents one startup entity"

    # ── Summary ───────────────────────────────────────────────────────────────
    total_dropped = initial_rows - len(df)
    log.info(
        "Pipeline complete | %d rows retained | %d rows removed (%.1f%%)",
        len(df),
        total_dropped,
        total_dropped / initial_rows * 100,
    )
    return df


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------
def save_processed(df: pd.DataFrame, output_path: Path) -> dict[str, Path]:
    """Write the cleaned DataFrame and companion outputs to disk.

    Parameters
    ----------
    df:
        Cleaned DataFrame to persist.
    output_path:
        Destination path (e.g. ``data/processed/startups_cleaned.csv``).
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    log.info("Saved → %s  (%d rows, %d cols)", output_path, len(df), df.shape[1])

    parquet_path = output_path.with_suffix(".parquet")
    try:
        df.to_parquet(parquet_path, index=False)
        log.info("Saved → %s", parquet_path)
    except Exception as exc:  # noqa: BLE001
        log.warning("Parquet export skipped: %s", exc)
        parquet_path = None

    missing_path = output_path.parent / "missing_report.csv"
    missing_summary(df).to_csv(missing_path)
    log.info("Missing report saved → %s", missing_path)

    meta = {
        "etl_version": df.attrs.get("etl_version", ETL_VERSION),
        "processed_on": df.attrs.get("processed_on", datetime.datetime.now().isoformat(timespec="seconds")),
        "rows": len(df),
        "columns": df.shape[1],
        "unit_of_analysis": df.attrs.get("unit_of_analysis", "One row represents one startup entity"),
        "csv_output": str(output_path),
        "parquet_output": str(parquet_path) if parquet_path else None,
    }
    metadata_path = output_path.parent / "etl_metadata.json"
    metadata_path.write_text(json.dumps(meta, indent=2))
    log.info("Metadata saved → %s", metadata_path)

    return {
        "csv": output_path,
        "parquet": parquet_path,
        "missing_report": missing_path,
        "metadata": metadata_path,
    }


def save_etl_log(log_path: Path) -> None:
    """Persist the ETL run log to a CSV file.

    Parameters
    ----------
    log_path:
        Destination path (e.g. ``data/processed/etl_run_log.csv``).
    """
    log_df = etl_log_to_dataframe()
    if log_df.empty:
        log.warning("ETL log is empty; nothing to save.")
        return
    log_df["run_timestamp"] = datetime.datetime.now().isoformat(timespec="seconds")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_df.to_csv(log_path, index=False)
    log.info("ETL log saved → %s", log_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the DVA Capstone 2 ETL pipeline for 'Why Startups Fail'.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        metavar="PATH",
        help="Path to the raw CSV file, e.g. data/raw/investments_VC.csv",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        metavar="PATH",
        help="Destination path for the cleaned CSV, e.g. data/processed/startups_cleaned.csv",
    )
    parser.add_argument(
        "--log-output",
        type=Path,
        default=None,
        metavar="PATH",
        help="Optional path to save the ETL run log CSV",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point for CLI execution.

    Returns 0 on success, 1 on error, following UNIX convention.
    """
    args = parse_args(argv)
    try:
        cleaned_df = build_clean_dataset(args.input)
        outputs = save_processed(cleaned_df, args.output)

        log_path = args.log_output or args.output.parent / "etl_run_log.csv"
        save_etl_log(log_path)

        print(f"\n✓ Processed dataset → {outputs['csv']}")
        if outputs["parquet"] is not None:
            print(f"  Parquet dataset → {outputs['parquet']}")
        print(f"  Missing report → {outputs['missing_report']}")
        print(f"  Metadata → {outputs['metadata']}")
        print(f"  Rows: {len(cleaned_df):,}  |  Columns: {cleaned_df.shape[1]}")
        print(f"  ETL log → {log_path}\n")
        return 0

    except FileNotFoundError as exc:
        log.error("Input file not found: %s", exc)
        return 1
    except Exception as exc:  # noqa: BLE001
        log.exception("Unexpected error during ETL: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
