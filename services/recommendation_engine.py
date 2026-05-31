import json
from typing import Any, Dict, List, Sequence, Tuple

import pandas as pd

from services.data_manager import DataManager
from services import localization
from config import app_config


class RecommendationEngine:
    """Rule-based recommendation engine for India Post DSS scheme recommendations."""

    FARMER_KEYWORDS: Tuple[str, ...] = ("farmer", "farm", "agriculture", "agri", "crop")
    WOMEN_KEYWORDS: Tuple[str, ...] = ("women", "woman", "female")
    CHILDREN_KEYWORDS: Tuple[str, ...] = ("child", "children", "kid", "youth")
    SENIOR_KEYWORDS: Tuple[str, ...] = ("senior", "elder", "elderly")
    RISK_KEYWORDS: Tuple[str, ...] = ("insurance", "disaster")

    PRIORITY_WEIGHT_SCALING_FACTOR: float = float(getattr(app_config, "PRIORITY_WEIGHT_SCALING_FACTOR", 10.0))
    SEASONALITY_BONUS_MAX: float = float(getattr(app_config, "RECOMMENDATION_SEASONALITY_BONUS_MAX", 3.0))

    OUTPUT_COLUMNS: Tuple[str, ...] = (
        "scheme_name",
        "target_group",
        "priority_weight",
        "peak_month_name",
        "lead_time_months",
        "start_month_name",
        "confidence_score",
        "reason",
        "score_breakdown",
    )

    def __init__(self) -> None:
        self.dm = DataManager()
        self.t = localization.t

    def generate_recommendations(self, village_profile: Dict[str, Any]) -> pd.DataFrame:
        """Return the diversified top-3 recommendations for a village profile."""
        schemes = self.dm.load_scheme_catalog()
        if schemes is None or schemes.empty:
            return pd.DataFrame(columns=list(self.OUTPUT_COLUMNS))

        results: List[Dict[str, Any]] = []
        for _, row in schemes.iterrows():
            score, breakdown = self.score_scheme(village_profile, row)
            reason = self.generate_reason(village_profile, row)
            results.append({
                "scheme_name": self._string_value(row.get("scheme_name", "")),
                "target_group": self._string_value(row.get("target_group", "")),
                "priority_weight": self._float_value(row.get("priority_weight", 1.0), default=1.0),
                "peak_month_name": self._string_value(row.get("peak_month_name", "")),
                "lead_time_months": self._int_value(row.get("lead_time_months", 0), default=0),
                "start_month_name": self._string_value(row.get("start_month_name", "")),
                "confidence_score": round(score, 2),
                "reason": reason,
                "score_breakdown": json.dumps(breakdown, ensure_ascii=False),
            })

        df = pd.DataFrame(results)
        df = df.sort_values(by="confidence_score", ascending=False).reset_index(drop=True)
        top = self._select_diverse_top_n(df, n=3)
        return top[[col for col in self.OUTPUT_COLUMNS if col in top.columns]].copy()

    def score_scheme(self, village_profile: Dict[str, Any], scheme_row: pd.Series) -> Tuple[float, Dict[str, float]]:
        """Score a scheme and return the confidence score plus a breakdown."""
        base_score = float(app_config.BASE_RECOMMENDATION_SCORE)

        farmers_ratio = float(village_profile.get("farmers_ratio", 0.0))
        women_ratio = float(village_profile.get("women_ratio", 0.0))
        children_ratio = float(village_profile.get("children_ratio", 0.0))
        seniors_ratio = float(village_profile.get("seniors_ratio", 0.0))
        flood_risk = str(village_profile.get("flood_risk", "")).strip().lower()
        drought_risk = str(village_profile.get("drought_risk", "")).strip().lower()

        target = self._normalized_text(scheme_row.get("target_group", ""))
        name = self._normalized_text(scheme_row.get("scheme_name", ""))

        priority_weight = self._float_value(scheme_row.get("priority_weight", 1.0), default=1.0)
        priority_score = priority_weight * self.PRIORITY_WEIGHT_SCALING_FACTOR

        demographic_score = 0.0
        risk_score = 0.0
        seasonality_score = self._seasonality_bonus(scheme_row)

        if self._matches_any(target, self.FARMER_KEYWORDS) or self._matches_any(name, self.FARMER_KEYWORDS):
            if farmers_ratio >= 0.4:
                demographic_score += float(app_config.FARMER_WEIGHT_HIGH)
            elif farmers_ratio >= 0.2:
                demographic_score += float(app_config.FARMER_WEIGHT_MED)

        if self._matches_any(target, self.WOMEN_KEYWORDS) or self._matches_any(name, self.WOMEN_KEYWORDS):
            if women_ratio >= 0.3:
                demographic_score += float(app_config.WOMEN_WEIGHT_HIGH)
            elif women_ratio >= 0.15:
                demographic_score += float(app_config.WOMEN_WEIGHT_MED)

        if self._matches_any(target, self.CHILDREN_KEYWORDS) or self._matches_any(name, self.CHILDREN_KEYWORDS):
            if children_ratio >= 0.2:
                demographic_score += float(app_config.CHILDREN_WEIGHT_HIGH)
            elif children_ratio >= 0.1:
                demographic_score += float(app_config.CHILDREN_WEIGHT_MED)

        if self._matches_any(target, self.SENIOR_KEYWORDS) or self._matches_any(name, self.SENIOR_KEYWORDS):
            if seniors_ratio >= 0.15:
                demographic_score += float(app_config.SENIOR_WEIGHT)

        if "high" in drought_risk:
            if self._matches_any(target, self.RISK_KEYWORDS) or self._matches_any(name, ("crop", "agriculture", "agri")):
                risk_score += float(app_config.DROUGHT_WEIGHT)

        if "high" in flood_risk:
            if self._matches_any(target, self.RISK_KEYWORDS) or "insurance" in name:
                risk_score += float(app_config.FLOOD_WEIGHT)

        if target and target in name:
            demographic_score += float(app_config.TARGET_NAME_MATCH_WEIGHT)

        total_score = base_score + priority_score + demographic_score + risk_score + seasonality_score
        total_score = max(0.0, min(100.0, total_score))

        breakdown = {
            "demographic_score": round(demographic_score, 2),
            "priority_score": round(priority_score, 2),
            "risk_score": round(risk_score, 2),
            "seasonality_score": round(seasonality_score, 2),
        }
        return total_score, breakdown

    def generate_reason(self, village_profile: Dict[str, Any], scheme_row: pd.Series) -> str:
        """Build a dynamic localized reason string utilizing mapped localized tokens."""
        parts: List[str] = []
        t = self.t

        farmers_ratio = float(village_profile.get("farmers_ratio", 0.0))
        women_ratio = float(village_profile.get("women_ratio", 0.0))
        children_ratio = float(village_profile.get("children_ratio", 0.0))
        seniors_ratio = float(village_profile.get("seniors_ratio", 0.0))
        flood_risk = str(village_profile.get("flood_risk", "")).strip().lower()
        drought_risk = str(village_profile.get("drought_risk", "")).strip().lower()

        target = self._normalized_text(scheme_row.get("target_group", ""))
        name = self._normalized_text(scheme_row.get("scheme_name", ""))

        if farmers_ratio >= 0.25 and (self._matches_any(target, self.FARMER_KEYWORDS) or self._matches_any(name, self.FARMER_KEYWORDS)):
            parts.append(t("reason_farmer_concentration"))

        if women_ratio >= 0.25 and (self._matches_any(target, self.WOMEN_KEYWORDS) or self._matches_any(name, self.WOMEN_KEYWORDS)):
            parts.append(t("reason_women_concentration"))

        if children_ratio >= 0.2 and (self._matches_any(target, self.CHILDREN_KEYWORDS) or self._matches_any(name, self.CHILDREN_KEYWORDS)):
            parts.append(t("reason_children_population"))

        if seniors_ratio >= 0.15 and (self._matches_any(target, self.SENIOR_KEYWORDS) or self._matches_any(name, self.SENIOR_KEYWORDS)):
            parts.append(t("reason_seniors_population"))

        if "high" in drought_risk and (self._matches_any(target, self.RISK_KEYWORDS) or self._matches_any(name, ("insurance", "crop", "agriculture", "agri"))):
            parts.append(t("reason_drought_insurance"))

        if "high" in flood_risk and ("insurance" in target or "disaster" in target or "insurance" in name):
            parts.append(t("reason_flood_insurance"))

        if not parts:
            parts.append(t("reason_general_fit"))

        return "; ".join(parts)

    def _select_diverse_top_n(self, df: pd.DataFrame, n: int = 3) -> pd.DataFrame:
        """Select the top N schemes while preferring distinct target groups."""
        if df.empty:
            return df.copy()

        selected_indices: List[int] = []
        seen_groups = set()

        first_index = df.index[0]
        selected_indices.append(first_index)
        first_group = self._normalized_text(df.iloc[0].get("target_group", ""))
        if first_group:
            seen_groups.add(first_group)

        for index, row in df.iloc[1:].iterrows():
            if len(selected_indices) >= n:
                break

            target_group = self._normalized_text(row.get("target_group", ""))
            if target_group and target_group in seen_groups:
                continue

            selected_indices.append(index)
            if target_group:
                seen_groups.add(target_group)

        if len(selected_indices) < n:
            for index in df.index:
                if len(selected_indices) >= n:
                    break
                if index in selected_indices:
                    continue
                selected_indices.append(index)

        return df.loc[selected_indices].head(n).reset_index(drop=True)

    def _seasonality_bonus(self, scheme_row: pd.Series) -> float:
        """Return a small bonus based on the scheme's seasonal rollout metadata."""
        peak_month_name = self._string_value(scheme_row.get("peak_month_name", "")).lower()
        start_month_name = self._string_value(scheme_row.get("start_month_name", "")).lower()
        lead_time_months = self._int_value(scheme_row.get("lead_time_months", 0), default=0)

        bonus = 0.0
        if peak_month_name:
            bonus += 0.5
        if start_month_name:
            bonus += 0.5
        if lead_time_months > 0:
            bonus += max(0.0, 2.0 - (lead_time_months * 0.5))

        return min(self.SEASONALITY_BONUS_MAX, bonus)

    def _matches_any(self, value: str, keywords: Sequence[str]) -> bool:
        """Return True when any keyword appears in the provided text."""
        return any(keyword in value for keyword in keywords)

    def _normalized_text(self, value: Any) -> str:
        """Normalize arbitrary text for keyword matching."""
        return str(value or "").strip().lower()

    def _string_value(self, value: Any) -> str:
        """Coerce a value to a clean string."""
        if value is None:
            return ""
        if pd.isna(value):
            return ""
        return str(value).strip()

    def _float_value(self, value: Any, default: float = 0.0) -> float:
        """Coerce a value to float with a fallback default."""
        try:
            result = float(value)
            return result if pd.notna(result) else default
        except Exception:
            return default

    def _int_value(self, value: Any, default: int = 0) -> int:
        """Coerce a value to int with a fallback default."""
        try:
            if pd.isna(value):
                return default
            return int(float(value))
        except Exception:
            return default