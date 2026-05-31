from typing import Dict, Tuple
import pandas as pd
import re


_ALIASES = {
    "village_name": ["village_name", "village name", "village", "villageid_name", "villageName"],
    "population": ["population", "total_population", "population_count", "pop", "totalpop"],
    "farmers_count": ["farmers", "farmer_population", "farmers_count", "num_farmers"],
}


def _sanitize(name: str) -> str:
    name = name or ""
    name = name.strip().lower()
    name = re.sub(r"[^0-9a-z]+", "_", name)
    name = re.sub(r"_+", "_", name)
    return name.strip("_")


def normalize_column_names(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """Normalize DataFrame column names to canonical names when possible."""
    if df is None:
        return df, {}

    orig_cols = list(df.columns)
    mapping: Dict[str, str] = {}

    # Performance optimization: pre-calculate sanitized lookup matrix mapping definitions
    reverse = {
        _sanitize(alias): canon
        for canon, aliases in _ALIASES.items()
        for alias in aliases
    }

    for col in orig_cols:
        s = _sanitize(col)
        mapping[col] = reverse.get(s, s)

    new_names = {}
    seen = {}
    for orig, norm in mapping.items():
        if norm in seen:
            count = seen[norm] + 1
            seen[norm] = count
            new_name = f"{norm}_{count}"
        else:
            seen[norm] = 1
            new_name = norm
        new_names[orig] = new_name

    df_renamed = df.rename(columns=new_names)
    display_map = {orig: new_names[orig] for orig in orig_cols}
    return df_renamed, display_map


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df


def clean_text_fields(df: pd.DataFrame) -> pd.DataFrame:
    if df is None:
        return df
    if "village_name" in df.columns:
        df["village_name"] = df["village_name"].astype(str).str.strip()
    return df


def clean_numeric_fields(df: pd.DataFrame) -> pd.DataFrame:
    if df is None:
        return df
    cols_to_clean = [c for c in ["population", "farmers_count"] if c in df.columns]
    for col in cols_to_clean:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df