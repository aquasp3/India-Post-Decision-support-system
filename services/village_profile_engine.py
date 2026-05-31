from typing import Dict, Any, List, Optional
import re
import pandas as pd
import streamlit as st

from services.data_manager import DataManager
from services import localization
from config import app_config


class VillageProfileEngine:
    """Engine to build unified village profiles from demographics and environmental data."""

    def __init__(self) -> None:
        self.dm = DataManager()
        self._demographics = None
        self._environment = None

    def _load_sources(self) -> None:
        if self._demographics is None:
            self._demographics = st.session_state.get("uploaded_demographics")
        if self._environment is None:
            self._environment = st.session_state.get("uploaded_environment")

        if self._demographics is None:
            self._demographics = pd.DataFrame()
        if self._environment is None:
            self._environment = pd.DataFrame()

    def _column_lookup(self, df: pd.DataFrame) -> Dict[str, str]:
        lookup: Dict[str, str] = {}
        for column in df.columns:
            normalized = re.sub(r"[^a-z0-9]+", "_", str(column).strip().lower()).strip("_")
            lookup.setdefault(normalized, column)
        return lookup

    def _get_column_value(self, row: pd.Series, lookup: Dict[str, str], *candidates: str, default: Any = None) -> Any:
        for candidate in candidates:
            normalized = re.sub(r"[^a-z0-9]+", "_", str(candidate).strip().lower()).strip("_")
            actual = lookup.get(normalized)
            if actual is not None and actual in row.index:
                value = row.get(actual)
                if not pd.isna(value):
                    return value
        return default

    def get_all_villages(self) -> List[str]:
        """Return list of village names available in demographics dataset."""
        self._load_sources()
        df = self._demographics
        if df is None or df.empty:
            return []
        if "village_name" in df.columns:
            return df["village_name"].astype(str).dropna().unique().tolist()
        return df.index.astype(str).tolist()

    def validate_village_exists(self, village_name: str) -> bool:
        """Return True if village exists in demographics."""
        villages = self.get_all_villages()
        target = (village_name or "").strip().lower()
        return any(str(v).strip().lower() == target for v in villages)

    def get_village_profile(self, village_name: str) -> Dict[str, Any]:
        """Build and return a unified profile for the given village name."""
        t = localization.t
        self._load_sources()

        if not village_name:
            raise ValueError(t("invalid_village_name") if t("invalid_village_name") else "Invalid village name")

        df_demo = self._demographics
        df_env = self._environment

        if df_demo is None or df_demo.empty:
            raise ValueError(t("no_demographics_data") if t("no_demographics_data") else "No demographics data available")

        demo_lookup = self._column_lookup(df_demo)
        env_lookup = self._column_lookup(df_env) if df_env is not None and not df_env.empty else {}

        demo_row = None
        village_col = demo_lookup.get("village_name") or demo_lookup.get("village")
        if village_col is not None:
            matches = df_demo[df_demo[village_col].astype(str).str.strip().str.lower() == village_name.strip().lower()]
            if not matches.empty:
                demo_row = matches.iloc[0]
        if demo_row is None:
            raise LookupError(t("village_not_found") if t("village_not_found") else f"Village '{village_name}' not found")

        env_row = None
        env_village_col = env_lookup.get("village_name") or env_lookup.get("village")
        if df_env is not None and not df_env.empty and env_village_col is not None:
            env_matches = df_env[df_env[env_village_col].astype(str).str.strip().str.lower() == village_name.strip().lower()]
            if not env_matches.empty:
                env_row = env_matches.iloc[0]

        def get_int(row: pd.Series, lookup: Dict[str, str], *candidates: str, default: int = 0) -> int:
            try:
                value = self._get_column_value(row, lookup, *candidates, default=None)
                if value is None:
                    return default
                return int(float(value))
            except Exception:
                return default

        def get_float(row: pd.Series, lookup: Dict[str, str], *candidates: str, default: float = 0.0) -> float:
            try:
                value = self._get_column_value(row, lookup, *candidates, default=None)
                if value is None:
                    return default
                return float(value)
            except Exception:
                return default

        population = get_int(demo_row, demo_lookup, "population", "total_population", default=0)
        farmers_count = get_int(demo_row, demo_lookup, "farmers_count", "farmers", "farmer_population", default=0)
        children_count = get_int(demo_row, demo_lookup, "children", "children_count", default=0)
        seniors_count = get_int(demo_row, demo_lookup, "seniors", "seniors_count", default=0)
        women_count = get_int(demo_row, demo_lookup, "women_count", "females_count", "female_count", "female_population", "women", default=0)
        men_count = get_int(demo_row, demo_lookup, "men_count", "males_count", "male_count", "male_population", "men", default=0)

        if population == 0:
            population = get_int(demo_row, demo_lookup, "population", "total_population", "Population", "TOTAL_POPULATION", default=0)

        working_population = get_int(demo_row, demo_lookup, "working_population", default=-1)
        if working_population < 0:
            working_population = max(0, population - children_count - seniors_count)

        def safe_ratio(n: int, denom: int) -> float:
            try:
                if denom <= 0:
                    return 0.0
                return round(float(n) / float(denom), 4)
            except Exception:
                return 0.0

        farmers_ratio = safe_ratio(farmers_count, population)
        children_ratio = safe_ratio(children_count, population)
        seniors_ratio = safe_ratio(seniors_count, population)
        women_ratio = get_float(demo_row, demo_lookup, "women_ratio", default=safe_ratio(women_count, population))
        men_ratio = get_float(demo_row, demo_lookup, "men_ratio", default=safe_ratio(men_count, population))

        if women_count == 0 and women_ratio > 0 and population > 0:
            women_count = int(round(women_ratio * population))
        if men_count == 0 and men_ratio > 0 and population > 0:
            men_count = int(round(men_ratio * population))

        if women_ratio <= 0:
            women_ratio = safe_ratio(women_count, population)
        if men_ratio <= 0:
            men_ratio = safe_ratio(men_count, population)

        if env_row is None:
            flood_risk = app_config.DEFAULT_FLOOD_RISK
            drought_risk = app_config.DEFAULT_DROUGHT_RISK
            geographic_zone = app_config.UNKNOWN_VALUE
        else:
            flood_risk = str(self._get_column_value(env_row, env_lookup, "flood_risk", default=app_config.UNKNOWN_VALUE))
            drought_risk = str(self._get_column_value(env_row, env_lookup, "drought_risk", default=app_config.UNKNOWN_VALUE))
            geographic_zone = str(self._get_column_value(env_row, env_lookup, "geographic_zone", default=app_config.UNKNOWN_VALUE))

        high_indicators = [v for v in [flood_risk, drought_risk] if str(v).strip().lower() == app_config.RISK_HIGH.lower()]
        medium_indicators = [v for v in [flood_risk, drought_risk] if str(v).strip().lower() == app_config.RISK_MEDIUM.lower()]
        
        if high_indicators:
            risk_score = app_config.RISK_HIGH
        elif medium_indicators:
            risk_score = app_config.RISK_MEDIUM
        else:
            risk_score = app_config.DEFAULT_RISK_SCORE

        if farmers_ratio >= 0.4:
            priority_segment = "Agriculture"
            suggested_campaign_type = "Farmer Outreach"
            optimal_outreach_season = str(self._get_column_value(env_row, env_lookup, "optimal_outreach_season", default="Monsoon")) if env_row is not None else "Monsoon"
        elif women_ratio >= 0.3:
            priority_segment = "Women Empowerment"
            suggested_campaign_type = "Women Health & Livelihood"
            optimal_outreach_season = "Post-Monsoon"
        else:
            priority_segment = "General"
            suggested_campaign_type = "Awareness Campaign"
            optimal_outreach_season = "Anytime"

        profile: Dict[str, Any] = {
            "village_name": str(self._get_column_value(demo_row, demo_lookup, "village_name", "village", default=village_name)),
            "population": population,
            "farmers_count": farmers_count,
            "farmers_ratio": farmers_ratio,
            "children_count": children_count,
            "children_ratio": children_ratio,
            "seniors_count": seniors_count,
            "seniors_ratio": seniors_ratio,
            "senior_ratio": seniors_ratio,
            "men_count": men_count,
            "men_ratio": men_ratio,
            "women_count": women_count,
            "women_ratio": women_ratio,
            "working_population": working_population,
            "geographic_zone": geographic_zone,
            "rainfall_category": str(self._get_column_value(env_row, env_lookup, "rainfall_category", default=t("unknown"))) if env_row is not None else t("unknown"),
            "flood_risk": flood_risk,
            "drought_risk": drought_risk,
            "risk_score": risk_score,
            "priority_segment": priority_segment,
            "suggested_campaign_type": suggested_campaign_type,
            "optimal_outreach_season": optimal_outreach_season,
        }

        st.session_state["selected_village_profile"] = profile
        return profile