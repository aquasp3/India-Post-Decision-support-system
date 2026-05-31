from typing import Any, Dict, Final, List, Optional, Tuple

import pandas as pd
import streamlit as st

from config import app_config
from services import localization


class PlanningGenerator:
    """Season-aware campaign scheduler that only places schemes inside their lifecycle."""

    MONTH_MAP: Final[Dict[str, int]] = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12,
    }

    OUTPUT_COLUMNS: Final[Tuple[str, ...]] = (
        "month",
        "campaign_name",
        "priority",
        "status",
        "officer_action",
        "why_recommended",
        "month_index",
        "target_audience",
        "Month",
        "Month_Index",
        "Scheme",
        "Target_Audience",
        "Target Group",
        "Priority",
        "Status",
        "Campaign Window",
        "Why_Recommended",
        "Officer_Action",
    )

    PHASE_PRIORITY_BONUS: Final[Dict[str, float]] = {
        "status_peak": 15.0,
        "status_active": 10.0,
        "status_preparation": 5.0,
        "status_followup": 2.0,
    }

    def __init__(self, village_profile: Dict[str, Any], recommendations: pd.DataFrame) -> None:
        self.profile = village_profile or {}
        self.recommendations = recommendations if recommendations is not None else pd.DataFrame()
        self.t = localization.t

    def generate_monthly_plan(self) -> pd.DataFrame:
        """Generate a 12-month plan constrained to each scheme's lifecycle window."""
        if self.recommendations is None or self.recommendations.empty:
            empty_df = self._empty_plan_dataframe()
            st.session_state["monthly_plan"] = empty_df
            return empty_df

        months = [self.t(month_name) for month_name in app_config.OUTREACH_MONTHS]
        top_candidates = self.recommendations.head(3).copy().reset_index(drop=True)

        if top_candidates.empty:
            empty_df = self._empty_plan_dataframe()
            st.session_state["monthly_plan"] = empty_df
            return empty_df

        rows: List[Dict[str, Any]] = []
        previous_scheme: Optional[str] = None

        for idx, month_name in enumerate(months, start=1):
            chosen_idx, phase_key = self._select_strictly_valid_scheme(
                current_month=idx,
                candidates=top_candidates,
                previous_scheme=previous_scheme,
            )

            if chosen_idx is None:
                rows.append(self._build_no_campaign_row(month_name, idx))
                previous_scheme = None
                continue

            row = top_candidates.iloc[chosen_idx]
            scheme_name = str(row.get("scheme_name", "")).strip() or self.t("scheme_no_campaign")
            target_group = str(row.get("target_group", "")).strip().lower()

            previous_scheme = scheme_name
            rows.append(self._build_campaign_row(month_name, idx, row, target_group, scheme_name, phase_key))

        plan_df = pd.DataFrame(rows).reindex(columns=list(self.OUTPUT_COLUMNS), fill_value="")
        st.session_state["monthly_plan"] = plan_df
        return plan_df

    def _select_strictly_valid_scheme(
        self,
        current_month: int,
        candidates: pd.DataFrame,
        previous_scheme: Optional[str],
    ) -> Tuple[Optional[int], str]:
        """Pick the highest-scoring scheme that is valid in the current lifecycle month."""
        scored_candidates: List[Tuple[float, int, str]] = []

        for idx, row in candidates.iterrows():
            start_m = self._get_month_number(row.get("start_month_numeric"), row.get("start_month_name"))
            peak_m = self._get_month_number(row.get("peak_month_numeric"), row.get("peak_month_name"))
            lead_t = max(0, self._safe_int(row.get("lead_time_months", 0), default=0))

            if start_m is None or peak_m is None:
                continue

            phase_key = self._evaluate_lifecycle_phase(current_month, start_m, peak_m, lead_t)
            if phase_key is None:
                continue

            score = self._safe_float(row.get("confidence_score", 0.0), default=0.0)
            score += self._safe_float(row.get("priority_weight", 1.0), default=1.0) * 5.0
            score += self.PHASE_PRIORITY_BONUS.get(phase_key, 0.0)

            scheme_name = str(row.get("scheme_name", "")).strip()
            if previous_scheme and scheme_name == previous_scheme:
                score -= 25.0

            scored_candidates.append((score, idx, phase_key))

        if not scored_candidates:
            return None, ""

        scored_candidates.sort(key=lambda item: item[0], reverse=True)
        return scored_candidates[0][1], scored_candidates[0][2]

    def _evaluate_lifecycle_phase(self, current: int, start: int, peak: int, lead: int) -> Optional[str]:
        """Return the active lifecycle phase for the current month, or None if out of window."""

        def wrap(month_number: int) -> int:
            return (month_number - 1) % 12 + 1

        def inside_range(month_number: int, begin: int, end: int) -> bool:
            if begin <= end:
                return begin <= month_number <= end
            return month_number >= begin or month_number <= end

        lead = max(0, lead)
        preparation_start = wrap(start - lead)
        preparation_end = wrap(start - 1)
        follow_up = wrap(peak + 1)

        if current == peak:
            return "status_peak"
        if inside_range(current, start, peak):
            return "status_active"
        if current == follow_up:
            return "status_followup"
        if lead > 0 and inside_range(current, preparation_start, preparation_end):
            return "status_preparation"

        return None

    def _build_campaign_row(
        self,
        month_name: str,
        month_index: int,
        row: pd.Series,
        target_group: str,
        scheme_name: str,
        phase_key: str,
    ) -> Dict[str, Any]:
        audience = self._map_audience(target_group)
        priority = self._map_priority(self._safe_float(row.get("priority_weight", 1.0), default=1.0), phase_key)
        reason = self._generate_clean_reason(target_group)
        action = self._generate_clean_action(target_group, scheme_name, phase_key)
        status_label = self.t(phase_key) if phase_key else self.t("status_upcoming")

        return {
            "month": month_name,
            "campaign_name": scheme_name,
            "priority": priority,
            "status": status_label,
            "officer_action": action,
            "why_recommended": reason,
            "month_index": month_index,
            "target_audience": audience,
            "Month": month_name,
            "Month_Index": month_index,
            "Scheme": scheme_name,
            "Target_Audience": audience,
            "Target Group": audience,
            "Priority": priority,
            "Status": status_label,
            "Campaign Window": status_label,
            "Why_Recommended": reason,
            "Officer_Action": action,
        }

    def _build_no_campaign_row(self, month_name: str, month_index: int) -> Dict[str, Any]:
        campaign_label = self.t("scheme_no_campaign")
        audience = self.t("audience_general_public")
        priority = f"🟢 {self.t('priority_routine')}"
        status_label = campaign_label
        reason = self.t("reason_general_awareness")
        action = self.t("action_default_awareness")

        return {
            "month": month_name,
            "campaign_name": campaign_label,
            "priority": priority,
            "status": status_label,
            "officer_action": action,
            "why_recommended": reason,
            "month_index": month_index,
            "target_audience": audience,
            "Month": month_name,
            "Month_Index": month_index,
            "Scheme": campaign_label,
            "Target_Audience": audience,
            "Target Group": audience,
            "Priority": priority,
            "Status": status_label,
            "Campaign Window": status_label,
            "Why_Recommended": reason,
            "Officer_Action": action,
        }

    def _empty_plan_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(columns=list(self.OUTPUT_COLUMNS))

    def _get_month_number(self, numeric_value: Any, name_value: Any) -> Optional[int]:
        month_number = self._safe_int(numeric_value, default=0)
        if 1 <= month_number <= 12:
            return month_number

        month_name = str(name_value or "").strip().lower()
        return self.MONTH_MAP.get(month_name)

    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        try:
            if pd.isna(value):
                return default
            return float(value)
        except Exception:
            return default

    def _safe_int(self, value: Any, default: int = 0) -> int:
        try:
            if pd.isna(value):
                return default
            return int(float(value))
        except Exception:
            return default

    def _map_audience(self, group: str) -> str:
        if "women" in group or "female" in group or "mahila" in group:
            return self.t("audience_women_shg")
        if "child" in group or "kid" in group or "girl" in group:
            return self.t("audience_girl_child_parents")
        if "senior" in group or "elder" in group:
            return self.t("audience_senior_citizens")
        if "farmer" in group or "agri" in group or "crop" in group:
            return self.t("audience_farmers_households")
        return self.t("audience_general_public")

    def _map_priority(self, weight: float, status_str: str) -> str:
        if "peak" in status_str:
            return f"⭐ {self.t('priority_peak_campaign')}"
        if weight >= 3.0:
            return f"🔴 {self.t('priority_high')}"
        if weight >= 1.5:
            return f"🟡 {self.t('priority_medium')}"
        return f"🟢 {self.t('priority_routine')}"

    def _generate_clean_reason(self, group: str) -> str:
        if "women" in group or "female" in group or "mahila" in group:
            return self.t("reason_women_concentration")
        if "child" in group or "kid" in group or "girl" in group:
            return self.t("reason_children_population")
        if "senior" in group or "elder" in group:
            return self.t("reason_seniors_population")
        if "farmer" in group or "agri" in group or "crop" in group:
            return self.t("reason_farmer_concentration")
        return self.t("reason_general_fit")

    def _generate_clean_action(self, group: str, scheme: str, phase: str) -> str:
        if "preparation" in phase:
            return self.t("action_prep_phase").format(scheme=scheme)

        if "peak" in phase or "active" in phase:
            if "women" in group or "female" in group or "mahila" in group:
                return self.t("action_active_women").format(scheme=scheme)
            if "child" in group or "kid" in group or "girl" in group:
                return self.t("action_active_children").format(scheme=scheme)
            if "senior" in group or "elder" in group:
                return self.t("action_active_seniors").format(scheme=scheme)
            return self.t("action_active_farmers").format(scheme=scheme)

        return self.t("action_followup_phase")

    def generate_suggested_actions(self) -> List[str]:
        return [
            self.t("checklist_identify_beneficiaries"),
            self.t("checklist_panchayat_coordination"),
            self.t("checklist_awareness_meetings"),
            self.t("checklist_enrollment_camps"),
            self.t("checklist_document_verification"),
            self.t("checklist_submit_report"),
        ]