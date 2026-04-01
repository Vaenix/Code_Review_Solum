import math
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(title="CMS Dialysis Mortality API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_PATH = BASE_DIR / "data" / "DFC_FACILITY.csv"


def resolve_data_path() -> Path:
    raw_path = os.getenv("DATA_PATH", str(DEFAULT_DATA_PATH))
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = (BASE_DIR / path).resolve()
    return path


DATA_PATH = resolve_data_path()
REPORT_PERIOD_PATTERN = re.compile(
    r"^\s*(\d{2})([A-Za-z]{3})(\d{4})\s*-\s*(\d{2})([A-Za-z]{3})(\d{4})\s*$"
)


# -----------------------------
# Column alias helpers
# -----------------------------
COLUMN_ALIASES = {
    "facility_name": [
        "Facility Name",
        "facility_name",
        "Provider Name",
        "Name",
    ],
    "state": [
        "State",
        "state",
        "Facility State",
        "Provider State",
    ],
    "zip": [
        "ZIP Code",
        "ZIP",
        "Zip",
        "zip",
        "Facility ZIP",
        "Provider ZIP Code",
        "Provider Zip Code",
        "ZIP Code (Facility)",
    ],
    "date": [
        "SMR Date",
        "Claims Date",
        "EQRS Date",
        "Date",
        "Measure Date",
        "Period",
        "Report Date",
        "Year-Month",
        "month_date",
    ],
    "year": [
        "Year",
        "year",
        "Report Year",
    ],
    "month": [
        "Month",
        "month",
        "Report Month",
    ],
    "mortality": [
        "Mortality Rate (Facility)",
        "Mortality Rate",
        "Facility Mortality Rate",
        "Standardized Mortality Ratio",
        "SMR",
        "mortality_rate",
    ],
    "ccn": [
        "CMS Certification Number (CCN)",
        "CCN",
        "ccn",
    ],
}


def find_column(df: pd.DataFrame, aliases: List[str]) -> Optional[str]:
    cols_lower = {c.lower(): c for c in df.columns}
    for alias in aliases:
        if alias in df.columns:
            return alias
        if alias.lower() in cols_lower:
            return cols_lower[alias.lower()]
    return None


def detect_columns(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    detected: Dict[str, Optional[str]] = {}
    for key, aliases in COLUMN_ALIASES.items():
        detected[key] = find_column(df, aliases)
    return detected


def normalize_zip(value: Any) -> Optional[str]:
    if pd.isna(value):
        return None

    text = str(value).strip()
    if not text:
        return None
    if "." in text:
        text = text.split(".")[0]
    return text


def parse_mortality(value: Any) -> Optional[float]:
    if pd.isna(value):
        return None

    text = str(value).strip()
    if not text or text in {"Not Available", "N/A", "NA", "--", "."}:
        return None

    text = text.replace("%", "").replace(",", "").strip()
    try:
        return float(text)
    except ValueError:
        return None


def parse_single_date(day: str, month: str, year: str) -> Optional[datetime]:
    try:
        return datetime.strptime(f"{day}{month.title()}{year}", "%d%b%Y")
    except ValueError:
        return None


def parse_report_period(value: Any) -> Tuple[Optional[datetime], Optional[datetime], Optional[str]]:
    if pd.isna(value):
        return None, None, None

    text = str(value).strip()
    if not text:
        return None, None, None

    match = REPORT_PERIOD_PATTERN.match(text)
    if not match:
        parsed = pd.to_datetime(text, errors="coerce")
        if pd.isna(parsed):
            return None, None, None
        parsed_dt = parsed.to_pydatetime()
        label = parsed_dt.strftime("%d %b %Y")
        return parsed_dt, parsed_dt, label

    start = parse_single_date(match.group(1), match.group(2), match.group(3))
    end = parse_single_date(match.group(4), match.group(5), match.group(6))
    if start is None or end is None:
        return None, None, None

    label = f"{start.strftime('%d %b %Y')} to {end.strftime('%d %b %Y')}"
    return start, end, label


def build_date_columns(df: pd.DataFrame, cols: Dict[str, Optional[str]]) -> Dict[str, Any]:
    year_col = cols["year"]
    month_col = cols["month"]
    date_col = cols["date"]

    if year_col and month_col:
        year_std = pd.to_numeric(df[year_col], errors="coerce")
        month_std = pd.to_numeric(df[month_col], errors="coerce")
        report_period_std = year_std.fillna("").astype(str).str.strip()
        report_period_std = report_period_std.where(report_period_std != "", None)
        return {
            "year_std": year_std,
            "month_std": month_std,
            "report_period_std": report_period_std,
        }

    if date_col:
        parsed_periods = df[date_col].apply(parse_report_period)
        year_std = parsed_periods.apply(
            lambda item: item[1].year if item[1] is not None else None
        )
        month_std = parsed_periods.apply(
            lambda item: item[1].month if item[1] is not None else None
        )
        report_period_std = parsed_periods.apply(lambda item: item[2])
        return {
            "year_std": pd.to_numeric(year_std, errors="coerce"),
            "month_std": pd.to_numeric(month_std, errors="coerce"),
            "report_period_std": report_period_std,
        }

    return {
        "year_std": pd.Series([None] * len(df), index=df.index, dtype="object"),
        "month_std": pd.Series([None] * len(df), index=df.index, dtype="object"),
        "report_period_std": pd.Series([None] * len(df), index=df.index, dtype="object"),
    }


def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Data file not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    cols = detect_columns(df)

    facility_col = cols["facility_name"]
    if facility_col is None:
        raise ValueError("Could not detect facility name column.")

    mortality_col = cols["mortality"]
    if mortality_col is None:
        raise ValueError("Could not detect mortality column.")

    state_col = cols["state"]
    zip_col = cols["zip"]
    ccn_col = cols["ccn"]
    date_fields = build_date_columns(df, cols)

    derived_columns = {
        "facility_name_std": df[facility_col].fillna("").astype(str).str.strip(),
        "state_std": (
            df[state_col].fillna("").astype(str).str.strip().str.upper()
            if state_col
            else pd.Series([""] * len(df), index=df.index, dtype="object")
        ),
        "zip_std": df[zip_col].apply(normalize_zip) if zip_col else None,
        "mortality_std": df[mortality_col].apply(parse_mortality),
        "ccn_std": (
            df[ccn_col].fillna("").astype(str).str.strip().replace("", None)
            if ccn_col
            else None
        ),
        **date_fields,
    }

    derived_df = pd.DataFrame(derived_columns, index=df.index)
    return pd.concat([df, derived_df], axis=1).copy()


DF = load_data()


# -----------------------------
# Filtering
# -----------------------------
def normalize_optional_text(value: Any) -> Optional[str]:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned or None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value).strip()
    return None


def normalize_optional_int(value: Any) -> Optional[int]:
    if value is None or pd.isna(value) or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned:
            return None
        try:
            return int(float(cleaned))
        except ValueError:
            return None
    return None


def apply_filters(
    df: pd.DataFrame,
    year: Optional[int] = None,
    month: Optional[int] = None,
    state: Optional[str] = None,
    zip_code: Optional[str] = None,
    facility_name: Optional[str] = None,
) -> pd.DataFrame:
    year_value = normalize_optional_int(year)
    month_value = normalize_optional_int(month)
    state_value = normalize_optional_text(state)
    zip_value = normalize_optional_text(zip_code)
    facility_value = normalize_optional_text(facility_name)

    out = df

    if year_value is not None:
        out = out[out["year_std"] == year_value]

    if month_value is not None:
        out = out[out["month_std"] == month_value]

    if state_value:
        out = out[out["state_std"] == state_value.upper()]

    if zip_value:
        out = out[out["zip_std"] == zip_value]

    if facility_value:
        keyword = facility_value.lower()
        out = out[out["facility_name_std"].str.lower().str.contains(keyword, na=False)]

    return out.copy()


def valid_mortality_df(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["mortality_std"].notna()].copy()


def infer_report_period(df: pd.DataFrame) -> Optional[str]:
    labels = sorted(
        [
            value
            for value in df["report_period_std"].dropna().unique().tolist()
            if value
        ]
    )
    if not labels:
        return None
    if len(labels) == 1:
        return labels[0]
    return ", ".join(labels)


def row_to_output(row: pd.Series) -> Dict[str, Any]:
    year_value = row.get("year_std")
    month_value = row.get("month_std")
    mortality_value = row.get("mortality_std")

    return {
        "facilityName": row.get("facility_name_std"),
        "state": row.get("state_std"),
        "zipCode": row.get("zip_std"),
        "year": None if pd.isna(year_value) else int(year_value),
        "month": None if pd.isna(month_value) else int(month_value),
        "mortalityRate": None if pd.isna(mortality_value) else float(mortality_value),
        "ccn": row.get("ccn_std"),
        "reportPeriod": row.get("report_period_std"),
    }


def build_summary_response(
    year: Optional[int] = None,
    month: Optional[int] = None,
    state: Optional[str] = None,
    zip_code: Optional[str] = None,
    facility_name: Optional[str] = None,
) -> Dict[str, Any]:
    filtered = apply_filters(DF, year, month, state, zip_code, facility_name)
    valid = valid_mortality_df(filtered)
    total = int(len(filtered))
    report_period = infer_report_period(filtered)

    if len(valid) == 0:
        return {
            "total": total,
            "avgMortality": None,
            "minMortality": None,
            "maxMortality": None,
            "reportPeriod": report_period,
            "top10Highest": [],
            "top10Lowest": [],
        }

    highest = (
        valid.sort_values("mortality_std", ascending=False)
        .head(10)
        .apply(row_to_output, axis=1)
        .tolist()
    )
    lowest = (
        valid.sort_values("mortality_std", ascending=True)
        .head(10)
        .apply(row_to_output, axis=1)
        .tolist()
    )

    return {
        "total": total,
        "avgMortality": round(float(valid["mortality_std"].mean()), 4),
        "minMortality": round(float(valid["mortality_std"].min()), 4),
        "maxMortality": round(float(valid["mortality_std"].max()), 4),
        "reportPeriod": report_period,
        "top10Highest": highest,
        "top10Lowest": lowest,
    }


def build_table_response(
    year: Optional[int] = None,
    month: Optional[int] = None,
    state: Optional[str] = None,
    zip_code: Optional[str] = None,
    facility_name: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "mortality",
    sort_order: str = "desc",
) -> Dict[str, Any]:
    filtered = apply_filters(DF, year, month, state, zip_code, facility_name)

    sort_map = {
        "mortality": "mortality_std",
        "facilityName": "facility_name_std",
        "state": "state_std",
        "zip": "zip_std",
        "year": "year_std",
        "month": "month_std",
    }
    sort_col = sort_map.get(sort_by, "mortality_std")
    ascending = sort_order.lower() == "asc"
    sortable = filtered.copy()

    if sort_col == "mortality_std":
        sortable = sortable.sort_values(sort_col, ascending=ascending, na_position="last")
    else:
        sortable = sortable.sort_values(sort_col, ascending=ascending, na_position="last")

    total = int(len(sortable))
    start = (page - 1) * page_size
    end = start + page_size
    page_df = sortable.iloc[start:end]

    return {
        "data": page_df.apply(row_to_output, axis=1).tolist(),
        "page": page,
        "pageSize": page_size,
        "total": total,
        "totalPages": math.ceil(total / page_size) if page_size else 0,
    }


def build_analysis_response(
    year: Optional[int] = None,
    month: Optional[int] = None,
    state: Optional[str] = None,
    zip_code: Optional[str] = None,
    facility_name: Optional[str] = None,
) -> Dict[str, Any]:
    filtered = apply_filters(DF, year, month, state, zip_code, facility_name)
    valid = valid_mortality_df(filtered)
    report_period = infer_report_period(filtered)

    if len(valid) == 0:
        return {
            "reportPeriod": report_period,
            "trendMode": "single_period",
            "monthlyTrend": [],
            "byState": [],
            "byZip": [],
            "distribution": [],
            "facilityRanking": [],
            "summary": {
                "totalFacilities": int(len(filtered)),
                "facilitiesWithMortality": 0,
            },
        }

    by_state_df = (
        valid.groupby("state_std", as_index=False)
        .agg(avgMortality=("mortality_std", "mean"), count=("mortality_std", "count"))
        .sort_values("avgMortality", ascending=False)
    )
    by_state = [
        {
            "state": row["state_std"],
            "avgMortality": round(float(row["avgMortality"]), 4),
            "count": int(row["count"]),
        }
        for _, row in by_state_df.iterrows()
        if row["state_std"]
    ]

    by_zip_df = (
        valid[valid["zip_std"].notna()]
        .groupby("zip_std", as_index=False)
        .agg(avgMortality=("mortality_std", "mean"), count=("mortality_std", "count"))
        .sort_values(["count", "avgMortality"], ascending=[False, False])
        .head(20)
    )
    by_zip = [
        {
            "zipCode": row["zip_std"],
            "avgMortality": round(float(row["avgMortality"]), 4),
            "count": int(row["count"]),
        }
        for _, row in by_zip_df.iterrows()
    ]

    distribution = []
    binned = pd.cut(valid["mortality_std"], bins=10)
    dist_df = binned.value_counts(sort=False)
    for interval, count in dist_df.items():
        distribution.append(
            {
                "range": str(interval),
                "count": int(count),
            }
        )

    facility_ranking_df = valid.sort_values("mortality_std", ascending=False).head(50)
    facility_ranking = facility_ranking_df.apply(row_to_output, axis=1).tolist()

    return {
        "reportPeriod": report_period,
        "trendMode": "single_period",
        "monthlyTrend": [],
        "byState": by_state,
        "byZip": by_zip,
        "distribution": distribution,
        "facilityRanking": facility_ranking,
        "summary": {
            "totalFacilities": int(len(filtered)),
            "facilitiesWithMortality": int(len(valid)),
        },
    }


# -----------------------------
# Meta / filters endpoint
# -----------------------------
@app.get("/api/filters")
def get_filters():
    years = sorted([int(x) for x in DF["year_std"].dropna().unique().tolist()])
    months = sorted([int(x) for x in DF["month_std"].dropna().unique().tolist()])
    states = sorted([x for x in DF["state_std"].dropna().unique().tolist() if x])
    return {
        "years": years,
        "months": months,
        "states": states,
        "reportPeriod": infer_report_period(DF),
    }


# -----------------------------
# Summary endpoint
# -----------------------------
@app.get("/api/summary")
def get_summary(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    state: Optional[str] = Query(None),
    zip_code: Optional[str] = Query(None, alias="zip"),
    facility_name: Optional[str] = Query(None),
):
    return build_summary_response(year, month, state, zip_code, facility_name)


# -----------------------------
# Table endpoint
# -----------------------------
@app.get("/")
def root():
    return {
        "message": "CMS Dialysis Mortality API is running",
        "endpoints": [
            "/api/health",
            "/api/filters",
            "/api/summary",
            "/api/table",
            "/api/analysis",
        ],
        "reportPeriod": infer_report_period(DF),
    }


@app.get("/api/table")
def get_table(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    state: Optional[str] = Query(None),
    zip_code: Optional[str] = Query(None, alias="zip"),
    facility_name: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    sort_by: str = Query("mortality"),
    sort_order: str = Query("desc"),
):
    return build_table_response(
        year=year,
        month=month,
        state=state,
        zip_code=zip_code,
        facility_name=facility_name,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


# -----------------------------
# Analysis endpoint
# -----------------------------
@app.get("/api/analysis")
def get_analysis(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    state: Optional[str] = Query(None),
    zip_code: Optional[str] = Query(None, alias="zip"),
    facility_name: Optional[str] = Query(None),
):
    return build_analysis_response(year, month, state, zip_code, facility_name)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "rows": int(len(DF)),
        "reportPeriod": infer_report_period(DF),
        "dataPath": str(DATA_PATH),
    }
