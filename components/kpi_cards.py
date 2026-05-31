import streamlit as st
from services import localization

t = localization.t


def render_kpi_cards(profile: dict) -> None:
    """Render four stylized KPI cards matching GOI enterprise specs."""
    if not profile:
        return

    pop = profile.get("population", 0)
    farmers_ratio = profile.get("farmers_ratio", 0.0)
    risk = profile.get("risk_score", t("unknown"))
    priority = profile.get("priority_segment", "-")

    # Inject minor localized utility style to ensure metrics inherit card spacing
    st.markdown("""
        <style>
            .kpi-container {
                background-color: #FFFFFF;
                padding: 1.25rem;
                border-radius: 12px;
                border: 1px solid #E2E8F0;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
                margin-bottom: 1rem;
            }
        </style>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown('<div class="kpi-container">', unsafe_allow_html=True)
        st.metric(t("kpi_population"), f"{pop:,}")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="kpi-container">', unsafe_allow_html=True)
        st.metric(t("kpi_farmers_ratio"), f"{round(farmers_ratio * 100, 2)}%")
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        # Determine strict status color flags mapping directly to dashboard theme rules
        value = str(risk).strip().lower()
        if "high" in value:
            badge_color = "#DC2626"
        elif "medium" in value:
            badge_color = "#D97706"
        else:
            badge_color = "#16A34A"

        st.markdown('<div class="kpi-container">', unsafe_allow_html=True)
        st.markdown(f"<label style='font-size:0.875rem; font-weight:500; color:#64748B;'>{t('kpi_risk_level')}</label>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style='background:{badge_color}; padding:6px 12px; border-radius:6px;
            color:white; text-align:center; font-weight:600; margin-top:8px; font-size:1.1rem; letter-spacing:0.5px;'>
                {risk}
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="kpi-container">', unsafe_allow_html=True)
        st.metric(t("kpi_priority_segment"), priority)
        st.markdown('</div>', unsafe_allow_html=True)