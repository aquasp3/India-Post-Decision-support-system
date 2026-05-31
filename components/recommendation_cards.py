import streamlit as st
from services import localization
from services.export_service import normalize_campaign_name

t = localization.t


def _map_campaign_name(raw_name: str) -> str:
    return normalize_campaign_name(raw_name)


def _render_recommendation_card(scheme_name: str, target_group: str, reason: str, priority_badge: str) -> str:
    return f"""
    <div style="height:100%; background:rgba(255,255,255,0.92); border:1px solid rgba(15,23,42,0.08); border-radius:18px; padding:0.68rem 0.78rem; box-shadow:0 8px 18px rgba(15,23,42,0.05); backdrop-filter:blur(14px);">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:0.55rem; flex-wrap:wrap;">
            <div style="min-width:0; flex:1 1 0;">
                <h4 style="margin:0; color:#0B2E63; font-size:0.94rem; font-weight:800; line-height:1.22;">{scheme_name}</h4>
                <div style="margin-top:0.2rem; color:#475569; font-size:0.8rem; line-height:1.35;"><strong>{t('recommendation_audience_label')}:</strong> {target_group}</div>
            </div>
            <div style="font-weight:700; font-size:0.8rem; white-space:nowrap;">
                {priority_badge}
            </div>
        </div>
        <div style="margin-top:0.55rem; padding-top:0.55rem; border-top:1px dashed #E2E8F0; color:#334155; font-size:0.82rem; line-height:1.4;">
            <strong>{t('recommendation_reason_label')}:</strong> {reason}
        </div>
    </div>
    """

def render_recommendation_cards(recommendations_df) -> None:
    """Renders clear, non-technical scheme guidance summaries for postmasters."""
    if recommendations_df is None or recommendations_df.empty:
        st.info(t("recommendation_cards_empty_state"))
        return

    top_recommendations = list(recommendations_df.head(3).iterrows())
    if not top_recommendations:
        st.info(t("recommendation_cards_empty_state"))
        return

    columns = st.columns(len(top_recommendations), gap="small")

    # Safeguard row presentation ceiling directly to the top 3 items
    for column, (_, row) in zip(columns, top_recommendations):
        scheme_name = _map_campaign_name(str(row.get("scheme_name", "")))
        target_group = str(row.get("target_group", ""))
        reason = str(row.get("reason", ""))

        # Pull or dynamically calculate non-technical priority text strings
        raw_weight = float(row.get("priority_weight", 1.0) or 1.0)
        if raw_weight >= 3.0:
            p_badge = f"🔴 {t('priority_high')}"
        elif raw_weight >= 1.5:
            p_badge = f"🟡 {t('priority_medium')}"
        else:
            p_badge = f"🟢 {t('priority_routine')}"

        with column:
            st.markdown(
                _render_recommendation_card(scheme_name, target_group, reason, p_badge),
                unsafe_allow_html=True,
            )