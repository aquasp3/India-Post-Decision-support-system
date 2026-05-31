import streamlit as st
from html import escape
from datetime import datetime

from config import app_config
from services import localization
from services.planning_generator import PlanningGenerator
from services.recommendation_engine import RecommendationEngine
from services.village_profile_engine import VillageProfileEngine

from components.export_buttons import render_export_buttons
from components.monthly_plan_table import render_monthly_plan_table
from components.recommendation_cards import render_recommendation_cards
from components.village_selector import render_village_selector

t = localization.t

MONTH_FILTER_KEYS = [
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
]

MONTH_INDEX_BY_KEY = {key: index for index, key in enumerate([
    "month_jan",
    "month_feb",
    "month_mar",
    "month_apr",
    "month_may",
    "month_jun",
    "month_jul",
    "month_aug",
    "month_sep",
    "month_oct",
    "month_nov",
    "month_dec",
], start=1)}

MONTH_INDEX_BY_TEXT = {
    "january": 1,
    "jan": 1,
    "month_jan": 1,
    "february": 2,
    "feb": 2,
    "month_feb": 2,
    "march": 3,
    "mar": 3,
    "month_mar": 3,
    "april": 4,
    "apr": 4,
    "month_apr": 4,
    "may": 5,
    "month_may": 5,
    "june": 6,
    "jun": 6,
    "month_jun": 6,
    "july": 7,
    "jul": 7,
    "month_jul": 7,
    "august": 8,
    "aug": 8,
    "month_aug": 8,
    "september": 9,
    "sep": 9,
    "sept": 9,
    "month_sep": 9,
    "october": 10,
    "oct": 10,
    "month_oct": 10,
    "november": 11,
    "nov": 11,
    "month_nov": 11,
    "december": 12,
    "dec": 12,
    "month_dec": 12,
}


def _format_number(value) -> str:
    try:
        return f"{int(float(value)):,}"
    except Exception:
        return "N/A"


def _format_percent(value) -> str:
    try:
        return f"{float(value):.1f}%"
    except Exception:
        return "N/A"


def _snapshot_card(title: str, value: str, accent: str = "#0B2D5C") -> str:
    return f"""
    <div class="snapshot-card">
        <div class="snapshot-accent" style="background:{accent};"></div>
        <div class="snapshot-label">{escape(title)}</div>
        <div class="snapshot-value">{escape(value)}</div>
    </div>
    """


def _month_index_from_key(month_key: str) -> int | None:
    return MONTH_INDEX_BY_KEY.get(month_key)


def _month_index_from_text(month_text: str) -> int | None:
    return MONTH_INDEX_BY_TEXT.get(_normalize_month_key(month_text))


def _normalize_month_key(value: str) -> str:
    return str(value or "").strip().lower().replace(" ", "_")


def _month_filter_options() -> list[str]:
    return [t("all_months")] + [t(key) for key in MONTH_FILTER_KEYS]


def _selected_month_key(selected_label: str) -> str | None:
    label_map = {t("all_months"): None}
    for key in MONTH_FILTER_KEYS:
        label_map[t(key)] = f"month_{key[:3]}" if key != "september" else "month_sep"
    return label_map.get(selected_label)


def _filter_plan_by_month(plan_df, month_key: str | None):
    if not month_key or plan_df is None or plan_df.empty:
        return plan_df

    month_label = t(month_key)
    if "Month" in plan_df.columns:
        filtered = plan_df[plan_df["Month"].astype(str) == str(month_label)]
        if not filtered.empty:
            return filtered
    if "month" in plan_df.columns:
        return plan_df[plan_df["month"].astype(str) == str(month_label)]
    return plan_df


def _lifecycle_phase(current_month: int, start_month: int, peak_month: int, lead_time: int) -> str | None:
    def wrap(month_number: int) -> int:
        return (month_number - 1) % 12 + 1

    def inside_range(month_number: int, begin: int, end: int) -> bool:
        if begin <= end:
            return begin <= month_number <= end
        return month_number >= begin or month_number <= end

    lead_time = max(0, lead_time)
    preparation_start = wrap(start_month - lead_time)
    preparation_end = wrap(start_month - 1)
    follow_up = wrap(peak_month + 1)

    if current_month == peak_month:
        return "peak"
    if inside_range(current_month, start_month, peak_month):
        return "active"
    if current_month == follow_up:
        return "followup"
    if lead_time > 0 and inside_range(current_month, preparation_start, preparation_end):
        return "preparation"
    return None


def _filter_recommendations_by_month(recommendations_df, month_key: str | None):
    if not month_key or recommendations_df is None or recommendations_df.empty:
        return recommendations_df

    month_index = _month_index_from_key(month_key)
    if month_index is None:
        return recommendations_df

    eligible_rows = []
    for _, row in recommendations_df.iterrows():
        start_idx = _month_index_from_text(row.get("start_month_name", ""))
        peak_idx = _month_index_from_text(row.get("peak_month_name", ""))
        lead_time = int(float(row.get("lead_time_months", 0) or 0))
        if start_idx is None or peak_idx is None:
            continue
        if _lifecycle_phase(month_index, start_idx, peak_idx, lead_time) is not None:
            eligible_rows.append(row)

    if not eligible_rows:
        return recommendations_df.iloc[0:0].copy()

    return recommendations_df.iloc[[recommendations_df.index.get_loc(row.name) for row in eligible_rows]].reset_index(drop=True)


def _ratio_from_profile(profile: dict, count_key: str, ratio_key: str) -> float:
    try:
        ratio_value = profile.get(ratio_key)
        if ratio_value not in (None, ""):
            return float(ratio_value) * 100 if float(ratio_value) <= 1 else float(ratio_value)
    except Exception:
        pass

    try:
        total_population = float(profile.get("population", 0) or 0)
        count_value = float(profile.get(count_key, 0) or 0)
        if total_population > 0:
            return (count_value / total_population) * 100
    except Exception:
        pass

    return 0.0


def _render_snapshot_cards(profile: dict) -> None:
    cards = [
        _snapshot_card(f"👥 {t('planning_kpi_population')}", _format_number(profile.get("population", 0)), "#0B2D5C"),
        _snapshot_card(f"👨 {t('planning_kpi_men')}", _format_percent(_ratio_from_profile(profile, "men_count", "men_ratio")), "#123C7A"),
        _snapshot_card(f"👩 {t('planning_kpi_women')}", _format_percent(_ratio_from_profile(profile, "women_count", "women_ratio")), "#F58220"),
        _snapshot_card(f"👶 {t('planning_kpi_children')}", _format_percent(_ratio_from_profile(profile, "children_count", "children_ratio")), "#0F766E"),
        _snapshot_card(f"👴 {t('planning_kpi_seniors')}", _format_percent(_ratio_from_profile(profile, "seniors_count", "seniors_ratio")), "#8A4B08"),
        _snapshot_card(f"🎯 {t('planning_kpi_focus_group')}", str(profile.get("priority_segment", "N/A")), "#7C2D12"),
        _snapshot_card(f"📢 {t('planning_kpi_campaign_type')}", str(profile.get("suggested_campaign_type", "N/A")), "#334155"),
    ]

    st.markdown(
        """
        <style>
            .snapshot-card {
                position: relative;
                background: rgba(255, 255, 255, 0.90);
                border: 1px solid rgba(15, 23, 42, 0.08);
                border-radius: 22px;
                padding: 0.85rem 0.95rem 0.8rem;
                box-shadow: 0 10px 24px rgba(15, 23, 42, 0.07);
                backdrop-filter: blur(16px);
                overflow: hidden;
                min-height: 108px;
                height: 100%;
            }
            .snapshot-accent {
                width: 52px;
                height: 5px;
                border-radius: 999px;
                margin-bottom: 0.65rem;
            }
            .snapshot-label {
                color: #64748B;
                font-size: 0.72rem;
                font-weight: 800;
                letter-spacing: 0.12em;
                text-transform: uppercase;
                margin-bottom: 0.3rem;
            }
            .snapshot-value {
                color: #0F172A;
                font-size: 1.15rem;
                font-weight: 800;
                line-height: 1.18;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(7)
    for col, card_html in zip(cols, cards):
        with col:
            st.markdown(card_html, unsafe_allow_html=True)


def _section_heading(eyebrow: str, title: str, subtitle: str) -> str:
    return f"""
    <div class="section-heading-dss">
        <div class="eyebrow">{escape(eyebrow)}</div>
        <h2>{escape(title)}</h2>
    </div>
    """


def app() -> None:
    st.markdown("""
        <style>
            main .block-container {
                max-width: 1240px;
                padding-top: 1.25rem;
                padding-bottom: 2rem;
            }

            [data-testid="stAppViewContainer"] {
                background:
                    radial-gradient(circle at top left, rgba(245, 130, 32, 0.12), transparent 24%),
                    radial-gradient(circle at top right, rgba(11, 45, 92, 0.10), transparent 22%),
                    linear-gradient(180deg, #F7F9FC 0%, #FBFCFE 100%) !important;
            }

            .about-shell {
                color: #1E293B;
            }

            .gov-header {
                position: relative;
                overflow: hidden;
                border-radius: 24px;
                padding: 2rem;
                color: #FFFFFF;
                background:
                    linear-gradient(135deg, rgba(11, 45, 92, 0.98) 0%, rgba(16, 58, 111, 0.98) 48%, rgba(245, 130, 32, 0.95) 100%);
                border: 1px solid rgba(255, 255, 255, 0.14);
                box-shadow: 0 20px 44px rgba(15, 23, 42, 0.12);
                text-align: center;
                margin-bottom: 1.5rem;
            }

            .gov-header::before {
                content: "";
                position: absolute;
                inset: 0;
                background-image:
                    radial-gradient(circle at 20% 20%, rgba(255, 255, 255, 0.14) 0, transparent 22%),
                    radial-gradient(circle at 80% 0%, rgba(255, 255, 255, 0.11) 0, transparent 18%),
                    linear-gradient(120deg, rgba(255, 255, 255, 0.06), transparent 40%);
                pointer-events: none;
            }

            .gov-emblem {
                font-size: 2.5rem;
                margin-bottom: 0.5rem;
                position: relative;
                z-index: 1;
            }

            .gov-subtitle {
                font-size: 0.78rem;
                letter-spacing: 0.18em;
                text-transform: uppercase;
                font-weight: 800;
                color: rgba(255, 255, 255, 0.92);
                margin-bottom: 0.5rem;
                position: relative;
                z-index: 1;
            }

            .gov-title {
                font-size: clamp(1.45rem, 2.4vw, 2.1rem);
                font-weight: 900;
                letter-spacing: -0.03em;
                margin: 0;
                color: #FFFFFF;
                position: relative;
                z-index: 1;
            }

            .glass-card {
                position: relative;
                height: 100%;
                background: rgba(255, 255, 255, 0.88);
                border: 1px solid rgba(15, 23, 42, 0.08);
                border-radius: 24px;
                padding: 1.35rem;
                margin-bottom: 1.25rem;
                box-shadow: 0 12px 36px rgba(15, 23, 42, 0.07);
                backdrop-filter: blur(18px);
                transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
            }

            .glass-card:hover {
                transform: translateY(-4px);
                border-color: rgba(11, 45, 92, 0.16);
                box-shadow: 0 20px 44px rgba(15, 23, 42, 0.12);
            }

            .section-heading-dss {
                margin: 0 0 0.7rem;
            }

            .section-heading-dss .eyebrow {
                margin: 0 0 0.35rem;
                color: #F58220;
                font-weight: 900;
                text-transform: uppercase;
                letter-spacing: 0.18em;
                font-size: 0.76rem;
            }

            .section-heading-dss h2 {
                margin: 0;
                color: #0B2D5C;
                font-size: clamp(1.45rem, 2.4vw, 2.1rem);
                letter-spacing: -0.03em;
                font-weight: 800;
            }

            .dashboard-row {
                display: grid;
                gap: 0.9rem;
                margin-bottom: 0.9rem;
            }

            @media (max-width: 640px) {
                .glass-card { padding: 1.1rem; }
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="about-shell">', unsafe_allow_html=True)
    with st.container():
        st.markdown(f"""
            <div class="gov-header">
                <div class="gov-emblem">🏛️</div>
                <div class="gov-subtitle">{t('department_of_posts_goi')}</div>
                <div class="gov-title">{t('decision_support_system_rural_campaign_management')}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(_section_heading(t("village_selector_eyebrow"), t("village_selector_title"), t("village_selector_subtitle")), unsafe_allow_html=True)

    month_options = _month_filter_options()
    month_label_to_key = {t("all_months"): None}
    for key in MONTH_FILTER_KEYS:
        month_label_to_key[t(key)] = f"month_{key[:3]}" if key != "september" else "month_sep"
    current_month_key = app_config.OUTREACH_MONTHS[datetime.now().month - 1]
    default_month_label = t(current_month_key)
    default_month_index = month_options.index(default_month_label) if default_month_label in month_options else 0

    col_sel, col_fil = st.columns([2.25, 1], gap="small")
    with col_sel:
        selected_village = render_village_selector()
    with col_fil:
        selected_month_label = st.selectbox(t("month_filter"), month_options, index=default_month_index, key="planning_month_filter")
    st.markdown('</div>', unsafe_allow_html=True)

    uploaded_demographics = st.session_state.get("uploaded_demographics")
    if uploaded_demographics is None or not hasattr(uploaded_demographics, "empty") or uploaded_demographics.empty:
        st.warning(f"⚠️ {t('upload_and_validate_village_demographics_first')}")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    profile = st.session_state.get("selected_village_profile")
    if selected_village and (profile is None or not isinstance(profile, dict) or not profile):
        try:
            profile = VillageProfileEngine().get_village_profile(selected_village)
            st.session_state["selected_village_profile"] = profile
        except Exception:
            profile = None

    if not selected_village or not profile:
        st.info(t("select_village_prompt"))
        st.markdown('</div>', unsafe_allow_html=True)
        return

    engine = RecommendationEngine()
    recommendations_df = engine.generate_recommendations(profile)
    
    planner = PlanningGenerator(profile, recommendations_df)
    monthly_plan_df = planner.generate_monthly_plan()

    selected_month_key = month_label_to_key.get(selected_month_label)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(_section_heading(t("village_snapshot_eyebrow"), t("village_snapshot_title"), t("village_snapshot_subtitle")), unsafe_allow_html=True)
    _render_snapshot_cards(profile)
    st.markdown('</div>', unsafe_allow_html=True)

    display_plan_df = _filter_plan_by_month(monthly_plan_df.copy(), selected_month_key)
    display_recommendations_df = _filter_recommendations_by_month(recommendations_df, selected_month_key)

    st.markdown('<div class="dashboard-row">', unsafe_allow_html=True)
    st.markdown(_section_heading(t("annual_plan_eyebrow"), t("annual_plan_title"), t("annual_plan_subtitle")), unsafe_allow_html=True)
    render_monthly_plan_table(display_plan_df)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="dashboard-row">', unsafe_allow_html=True)
    st.markdown(_section_heading(t("recommendations_eyebrow"), t("recommendations_title"), t("recommendations_subtitle")), unsafe_allow_html=True)
    render_recommendation_cards(display_recommendations_df)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="dashboard-row">', unsafe_allow_html=True)
    st.markdown(_section_heading(t("export_center_eyebrow"), t("export_center_title"), t("export_center_subtitle")), unsafe_allow_html=True)
    render_export_buttons()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    app()