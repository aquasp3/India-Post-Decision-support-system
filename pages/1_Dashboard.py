import streamlit as st
#from components import render_sidebar
from services import localization

t = localization.t


def app() -> None:
    # 1. Premium Government Dashboard CSS Injection
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

            /* Full-width Government Branding Header */
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

            /* Unified Premium Glassmorphism Card Containers */
            .glass-card {
                position: relative;
                height: 100%;
                background: rgba(255, 255, 255, 0.88);
                border: 1px solid rgba(15, 23, 42, 0.08);
                border-radius: 24px;
                padding: 1.35rem;
                box-shadow: 0 12px 36px rgba(15, 23, 42, 0.07);
                backdrop-filter: blur(18px);
                transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
                margin-bottom: 1.25rem;
            }

            .glass-card:hover {
                transform: translateY(-4px);
                border-color: rgba(11, 45, 92, 0.16);
                box-shadow: 0 20px 44px rgba(15, 23, 42, 0.12);
            }
            
            .card-header-title {
                font-size: 1.14rem;
                font-weight: 800;
                color: #0B2D5C;
                margin-bottom: 1rem;
                border-left: 4px solid #F58220;
                padding-left: 0.75rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                letter-spacing: -0.02em;
            }

            /* Main Welcome Banner Layout text styling */
            .welcome-container {
                text-align: center;
                padding: 1rem 0;
            }
            .welcome-title {
                margin: 0; 
                color: #0B2D5C; 
                font-size: clamp(1.8rem, 3vw, 2.8rem);
                font-weight: 900;
                letter-spacing: -0.04em;
            }
            .welcome-subtitle {
                color: #64748B; 
                font-size: 1.05rem; 
                margin-top: 0.5rem;
                font-weight: 500;
                line-height: 1.6;
            }
            .welcome-description {
                margin: 1.25rem 0; 
                font-weight: 800; 
                font-size: 1.2rem; 
                color: #F58220;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }

            /* Interactive feature block style adjustments */
            .feature-block-text {
                text-align: center; 
                font-weight: 800; 
                color: #0B2D5C;
                font-size: 1.05rem;
            }

            /* Workflow pipeline item configuration */
            .workflow-step-box {
                font-size: 1rem;
                color: #334155;
                font-weight: 700;
                padding: 0.5rem;
                background: rgba(11, 45, 92, 0.04);
                border-radius: 12px;
                border: 1px solid rgba(11, 45, 92, 0.06);
                text-align: center;
            }

            .section-heading-h4 {
                color: #0B2D5C;
                font-weight: 800;
                letter-spacing: -0.02em;
                margin: 1.5rem 0 0.75rem;
            }

            @media (max-width: 900px) {
                .gov-header { padding: 1.5rem; }
            }
            @media (max-width: 640px) {
                .gov-header, .glass-card { padding: 1.1rem; }
            }
        </style>
    """, unsafe_allow_html=True)

    # Sidebar Navigation Render Framework
    #render_sidebar()

    # 2. Government of India Full-Width Branding Header
    st.markdown('<div class="about-shell">', unsafe_allow_html=True)
    with st.container():
        st.markdown(f"""
            <div class="gov-header">
                <div class="gov-emblem">🏛️</div>
                <div class="gov-subtitle">{t('department_of_posts_goi')}</div>
                <div class="gov-title">{t('decision_support_system_rural_campaign_management')}</div>
            </div>
        """, unsafe_allow_html=True)

    # 3. Comprehensive Central Intelligence Welcome Hub
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f"""
        <div class="welcome-container">
            <h1 class="welcome-title">{t('app_name')}</h1>
            <p class="welcome-subtitle">{t('app_subtitle')}</p>
            <h3 class="welcome-description">{t('government_scheme_recommendation')}</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Centered system routing trigger execution block
    _, btn_col, _ = st.columns([1.5, 1, 1.5])
    with btn_col:
        if st.button(t("get_started"), key="dashboard_get_started", type="primary", use_container_width=True):
            try:
                st.switch_page("pages/2_Upload_Village_Data.py")
            except Exception:
                st.warning(t("navigation_failed"))
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    # 4. Enterprise Bento Features Grid Matrix Allocation
    st.markdown(f"<h4 class='section-heading-h4'>🌟 {t('village_intelligence_platform')}</h4>", unsafe_allow_html=True)
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    
    with f_col1:
        st.markdown('<div class="glass-card" style="padding: 1.25rem; margin-bottom:0;">', unsafe_allow_html=True)
        st.markdown(f"<div class='feature-block-text'>📊 {t('village_analysis')}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with f_col2:
        st.markdown('<div class="glass-card" style="padding: 1.25rem; margin-bottom:0;">', unsafe_allow_html=True)
        st.markdown(f"<div class='feature-block-text'>🤝 {t('scheme_matching')}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with f_col3:
        st.markdown('<div class="glass-card" style="padding: 1.25rem; margin-bottom:0;">', unsafe_allow_html=True)
        st.markdown(f"<div class='feature-block-text'>📅 {t('campaign_planning')}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with f_col4:
        st.markdown('<div class="glass-card" style="padding: 1.25rem; margin-bottom:0;">', unsafe_allow_html=True)
        st.markdown(f"<div class='feature-block-text'>🏛️ {t('government_reporting')}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    # 5. Standard Core Operational Workflow Progress Milestones Panel
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-header-title">🔄 {t("workflow_title")}</div>', unsafe_allow_html=True)
    
    w_col1, w_col2, w_col3, w_col4 = st.columns(4)
    with w_col1:
        st.markdown(f"<div class='workflow-step-box'>1️⃣ {t('workflow_upload_data')}</div>", unsafe_allow_html=True)
    with w_col2:
        st.markdown(f"<div class='workflow-step-box'>2️⃣ {t('workflow_select_village')}</div>", unsafe_allow_html=True)
    with w_col3:
        st.markdown(f"<div class='workflow-step-box'>3️⃣ {t('workflow_generate_recommendations')}</div>", unsafe_allow_html=True)
    with w_col4:
        st.markdown(f"<div class='workflow-step-box'>4️⃣ {t('workflow_export_reports')}</div>", unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


app()