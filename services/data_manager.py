from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import pandas as pd
import streamlit as st


@st.cache_data(show_spinner=False)
def _read_csv_cached(path_str: str, mtime_ns: int) -> pd.DataFrame:
    path = Path(path_str)
    try:
        if not path.exists() or path.is_dir():
            return pd.DataFrame()
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


@st.cache_data(show_spinner=False)
def _read_uploaded_csv_cached(file_bytes: bytes, filename: str) -> pd.DataFrame:
    try:
        from io import BytesIO

        if not file_bytes:
            return pd.DataFrame()
        return pd.read_csv(BytesIO(file_bytes))
    except Exception:
        return pd.DataFrame()


class DataManager:
    """Manages default and uploaded datasets, storing active datasets in session state."""

    DATA_DIR = Path(__file__).parent.parent / "data"
    DEMO_FILE = DATA_DIR / "village_demographics_cleaned.csv"
    ENV_FILE = DATA_DIR / "village_environmental_data.csv"
    SCHEME_FILE = DATA_DIR / "scheme_catalog_cleaned.csv"

    def __init__(self) -> None:
        # Optimized dictionary update operation to set session defaults without multiple overhead lookups
        defaults = {
            "active_demographics": None,
            "active_environment": None,
            "uploaded_demographics": None,
            "uploaded_environment": None,
            "uploaded_demographics_meta": None,
            "uploaded_environment_meta": None
        }
        for key, val in defaults.items():
            st.session_state.setdefault(key, val)

    def load_default_demographics(self) -> pd.DataFrame:
        return pd.DataFrame()

    def load_default_environment(self) -> pd.DataFrame:
        return pd.DataFrame()

    def load_scheme_catalog(self) -> pd.DataFrame:
        return self._load_csv_safe(self.SCHEME_FILE)

    def load_uploaded_demographics(self, uploaded_file: Any) -> pd.DataFrame:
        df = self._load_uploaded_csv_safe(uploaded_file)
        if df is not None and not df.empty:
            st.session_state["active_demographics"] = df
            st.session_state["uploaded_demographics"] = df
            st.session_state["uploaded_demographics_meta"] = {
                "name": getattr(uploaded_file, "name", "uploaded_demographics"),
            }
        return df

    def load_uploaded_environment(self, uploaded_file: Any) -> pd.DataFrame:
        df = self._load_uploaded_csv_safe(uploaded_file)
        if df is not None and not df.empty:
            st.session_state["active_environment"] = df
            st.session_state["uploaded_environment"] = df
            st.session_state["uploaded_environment_meta"] = {
                "name": getattr(uploaded_file, "name", "uploaded_environment"),
            }
        return df

    def get_active_demographics(self) -> pd.DataFrame:
        df = st.session_state.get("uploaded_demographics")
        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()

    def get_active_environment(self) -> pd.DataFrame:
        df = st.session_state.get("uploaded_environment")
        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()

    def _load_csv_safe(self, path: Path) -> pd.DataFrame:
        try:
            mtime_ns = path.stat().st_mtime_ns if path.exists() else -1
            return _read_csv_cached(str(path), mtime_ns)
        except Exception:
            return pd.DataFrame()

    def _load_uploaded_csv_safe(self, uploaded_file: Any) -> Optional[pd.DataFrame]:
        if uploaded_file is None:
            return None
        try:
            file_bytes = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else uploaded_file.read()
            if not file_bytes:
                return pd.DataFrame()
            return _read_uploaded_csv_cached(bytes(file_bytes), getattr(uploaded_file, "name", "uploaded.csv"))
        except Exception:
            return pd.DataFrame()