from typing import Dict, Any, List
import streamlit as st
from services import localization


t = localization.t


def generate_insights(profile: Dict[str, Any], recommendations) -> List[str]:
    """Create 3-5 short officer-friendly insights from profile and recommendations."""
    insights: List[str] = []

    farmers_ratio = float(profile.get("farmers_ratio", 0.0) or 0.0)
    women_ratio = float(profile.get("women_ratio", 0.0) or 0.0)
    children_ratio = float(profile.get("children_ratio", 0.0) or 0.0)
    seniors_ratio = float(profile.get("seniors_ratio", 0.0) or 0.0)
    flood_risk = str(profile.get("flood_risk", "")).strip().lower()
    drought_risk = str(profile.get("drought_risk", "")).strip().lower()

    if farmers_ratio >= 0.4:
        insights.append(t("insight_high_farmer_concentration"))
        insights.append(t("insight_agricultural_priority"))

    if women_ratio >= 0.3:
        insights.append(t("insight_large_women_population"))

    if children_ratio >= 0.2:
        insights.append(t("insight_child_welfare_focus"))

    if seniors_ratio >= 0.15:
        insights.append(t("insight_senior_citizen_focus"))

    if "high" in drought_risk or "high" in flood_risk:
        insights.append(t("insight_insurance_awareness"))

    if recommendations is not None and not recommendations.empty:
        top_scheme = str(recommendations.iloc[0].get("scheme_name", ""))
        if top_scheme:
            insights.append(t("insight_top_scheme_ready").format(scheme=top_scheme))

    return insights[:5]


def render_officer_insights(village_profile: Dict[str, Any], recommendations_df) -> None:
    insights = generate_insights(village_profile, recommendations_df)
    st.session_state["officer_insights"] = insights

    with st.container(border=True):
        st.markdown(f"<h3 style='margin:0 0 16px 0;color:#0B5CAD;font-size:1.3rem;'>{t('officer_insights')}</h3>", unsafe_allow_html=True)

        if not insights:
            st.info(t("insight_no_observations"))
        else:
            for insight in insights:
                st.markdown(f"💡 {insight}")