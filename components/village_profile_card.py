import streamlit as st
from services import localization

t = localization.t


def render_village_profile_card(profile: dict) -> None:
    """Render a comprehensive structured demographic register card."""
    if not profile:
        return

    st.markdown(f"""
        <div class="dash-card">
            <div class="card-header-title">📌 {profile.get('village_name')} — {t('regional_register_profile')}</div>
            <div style="margin-bottom: 1.5rem;"></div>
        </div>
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    with cols[0]:
        st.markdown(f"**📊 {t('population')}**: {profile.get('population'):,}")
        st.markdown(f"**👨‍🌾 {t('farmers_count')}**: {profile.get('farmers_count'):,}")
        st.markdown(f"**📈 {t('farmers_ratio')}**: {round(profile.get('farmers_ratio', 0) * 100, 2)}%")

    with cols[1]:
        st.markdown(f"**🧒 {t('children_count')}**: {profile.get('children_count'):,}")
        st.markdown(f"**📉 {t('children_ratio')}**: {round(profile.get('children_ratio', 0) * 100, 2)}%")
        st.markdown(f"**👵 {t('seniors_count')}**: {profile.get('seniors_count'):,}")

    with cols[2]:
        st.markdown(f"**⏳ {t('seniors_ratio')}**: {round(profile.get('seniors_ratio', 0) * 100, 2)}%")
        st.markdown(f"**👩 {t('women_count')}**: {profile.get('women_count'):,}")
        st.markdown(f"**🧬 {t('women_ratio')}**: {round(profile.get('women_ratio', 0) * 100, 2)}%")

    st.markdown("<hr style='margin:20px 0; border:0; border-top:1px dashed #E2E8F0;'/>", unsafe_allow_html=True)

    meta_cols = st.columns(2)
    with meta_cols[0]:
        st.markdown(f"⚙️ **{t('working_population')}**: {profile.get('working_population'):,}")
        st.markdown(f"🗺️ **{t('geographic_zone')}**: {profile.get('geographic_zone')}")
        st.markdown(f"🌧️ **{t('rainfall_category')}**: {profile.get('rainfall_category')}")
        st.markdown(f"⚠️ **{t('flood_risk')}**: {profile.get('flood_risk')}")
        st.markdown(f"🔥 **{t('drought_risk')}**: {profile.get('drought_risk')}")
        
    with meta_cols[1]:
        st.markdown(f"🎯 **{t('risk_score')}**: {profile.get('risk_score')}")
        st.markdown(f"💎 **{t('priority_segment')}**: {profile.get('priority_segment')}")
        st.markdown(f"📢 **{t('suggested_campaign_type')}**: {profile.get('suggested_campaign_type')}")
        st.markdown(f"📅 **{t('optimal_outreach_season')}**: {profile.get('optimal_outreach_season')}")