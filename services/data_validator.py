from typing import Dict, Any, List, Optional
import pandas as pd
from services import preprocessing


class DataValidator:
    """Validate village datasets with common rules."""

    REQUIRED_COLUMNS = ["village_name", "population"]

    def __init__(self, df: Optional[pd.DataFrame]):
        self.raw_df = df if df is not None else pd.DataFrame()
        self.df: pd.DataFrame = pd.DataFrame()
        self.mapping: Dict[str, str] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []

        try:
            normalized, mapping = preprocessing.normalize_column_names(self.raw_df)
            normalized = preprocessing.clean_text_fields(normalized)
            normalized = preprocessing.clean_numeric_fields(normalized)
            self.df = normalized
            self.mapping = mapping
        except Exception:
            self.df = self.raw_df

    def validate(self) -> Dict[str, Any]:
        if self.df is None or self.df.empty:
            self.errors.append("file_empty")
            return self._result(status="failed")

        # Set lookup for O(1) missing column verification efficiency
        df_cols = self.df.columns
        missing_cols = [c for c in self.REQUIRED_COLUMNS if c not in df_cols]
        if missing_cols:
            self.errors.append(f"missing_columns:{','.join(missing_cols)}")

        # Streamlined conditional selection execution for duplicate count tracks
        if "village_id" in df_cols:
            dup_count = int(self.df["village_id"].duplicated().sum())
        elif "village_name" in df_cols:
            dup_count = int(self.df["village_name"].duplicated().sum())
        else:
            dup_count = 0

        if dup_count > 0:
            self.warnings.append(f"duplicate_villages:{dup_count}")

        if "population" in df_cols:
            neg_count = int((self.df["population"] < 0).sum())
            if neg_count > 0:
                self.errors.append(f"negative_population:{neg_count}")

        if "village_name" in df_cols:
            # Replaced repetitive series transformations with unified missing string checks
            v_name_series = self.df["village_name"]
            missing_names = int(v_name_series.isna().sum() + (v_name_series.astype(str).str.strip() == "").sum())
            if missing_names > 0:
                self.errors.append(f"missing_village_names:{missing_names}")

        return self._result(status=("failed" if self.errors else "ok"))

    def _result(self, status: str) -> Dict[str, Any]:
        df = self.df.copy()

        summary = {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1]),
            "duplicate_count": self._count_duplicates(df),
            "missing_values": int(df.isna().sum().sum()),
        }

        return {
            "status": status,
            "errors": self.errors,
            "warnings": self.warnings,
            "summary": summary,
            "clean_df": df,
            "mapping": self.mapping,
        }

    def _count_duplicates(self, df: pd.DataFrame) -> int:
        cols = df.columns
        if "village_id" in cols:
            return int(df["village_id"].duplicated().sum())
        if "village_name" in cols:
            return int(df["village_name"].duplicated().sum())
        return 0