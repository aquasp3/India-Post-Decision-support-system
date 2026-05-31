import streamlit as st
#from components import render_sidebar
from services import localization
from services.data_manager import DataManager
from services.data_validator import DataValidator

t = localization.t


def app() -> None:
    # 1. Custom CSS Injection for GOI Enterprise Dashboard Styling
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

            /* Header Styling */
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

            /* Pipeline Section Header */
            .section-container {
                text-align: center;
                margin-bottom: 1.5rem;
                padding: 1rem;
                background: rgba(255, 255, 255, 0.6);
                border-radius: 20px;
                border: 1px solid rgba(15, 23, 42, 0.04);
            }
            .section-icon {
                font-size: 2.5rem;
                margin-bottom: 0.5rem;
            }
            .section-title {
                font-size: 1.45rem;
                color: #0B2D5C;
                font-weight: 800;
                margin-bottom: 0.25rem;
                letter-spacing: -0.02em;
            }
            .section-subtitle {
                font-size: 0.95rem;
                color: #64748B;
                font-weight: 500;
            }

            /* Dashboard Enterprise Cards */
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

            .card-title {
                font-size: 1.14rem;
                font-weight: 800;
                color: #0B2D5C;
                margin-bottom: 1rem;
                border-left: 4px solid #F58220;
                padding-left: 0.75rem;
                letter-spacing: -0.02em;
            }
            
            /* Compact adjustments for Reference Card */
            .compact-card {
                padding: 1.1rem;
            }

            div[data-testid="stDownloadButton"] button {
                border-radius: 999px !important;
                font-weight: 800 !important;
            }

            @media (max-width: 900px) {
                .gov-header { padding: 1.5rem; }
            }
            @media (max-width: 640px) {
                .gov-header, .glass-card { padding: 1.1rem; }
            }
        </style>
    """, unsafe_allow_html=True)

    # Sidebar Render (Retained from original)
    #render_sidebar()

    # 2. Government of India Full-Width Header
    st.markdown('<div class="about-shell">', unsafe_allow_html=True)
    with st.container():
        st.markdown(f"""
            <div class="gov-header">
                <div class="gov-emblem">🏛️</div>
                <div class="gov-subtitle">{t('department_of_posts_goi')}</div>
                <div class="gov-title">{t('decision_support_system_rural_campaign_management')}</div>
            </div>
        """, unsafe_allow_html=True)

    # 3. Centered Pipeline Progress Section
    with st.container():
        st.markdown(f"""
            <div class="section-container">
                <div class="section-icon">📥</div>
                <div class="section-title">{t('regional_data_ingestion_center')}</div>
                <div class="section-subtitle">{t('pipeline_step_upload_validate')}</div>
            </div>
        """, unsafe_allow_html=True)

    # Data Manager Instance
    dm = DataManager()

    # 4. Main Content Area using [4, 1] Column Matrix Split
    col_main, col_ref = st.columns([4, 1])

    # LEFT CARD: Main Upload Workspace
    with col_main:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-title">{t("upload_csv_dataset_matrix")}</div>', unsafe_allow_html=True)
        
        # Dual layout configuration accommodated inside the main card bounds
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            uploaded_demo = st.file_uploader(t("upload_village_demographics"), type=["csv"])
        with sub_col2:
            uploaded_env = st.file_uploader(t("upload_village_environment"), type=["csv"])
        st.markdown('</div>', unsafe_allow_html=True)

    # RIGHT CARD: Reference Forms & Templates
    with col_ref:
        st.markdown('<div class="glass-card compact-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-title">{t("reference_forms")}</div>', unsafe_allow_html=True)
        st.markdown(f"<p style='font-size: 0.85rem; color: #64748B; margin-bottom: 1rem;'>{t('use_standard_formats_for_validation')}</p>", unsafe_allow_html=True)
        
        # Mock template download to meet UI requirements using existing parameters
        template_demo_data = "Village_Code,Village_Name,Total_Population,Literacy_Rate\n"
        st.download_button(
            label=f"📥 {t('download_template_csv')}",
            data=template_demo_data,
            file_name="village_matrix_template.csv",
            mime="text/csv",
            width="stretch",
            key="upload_template_csv"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Backend Core Functional Logic Block ---
    demo_df = None
    env_df = None

    if uploaded_demo is not None:
        demo_df = dm.load_uploaded_demographics(uploaded_demo)
        if demo_df is None or demo_df.empty:
            st.error(f"{t('validation_error')}: {t('invalid_file')}")
        else:
            st.session_state["uploaded_demographics"] = demo_df
            st.session_state["active_demographics"] = demo_df

    if uploaded_env is not None:
        env_df = dm.load_uploaded_environment(uploaded_env)
        if env_df is None or env_df.empty:
            st.warning(f"{t('validation_warning')}: {t('invalid_file')}")
        else:
            st.session_state["uploaded_environment"] = env_df
            st.session_state["active_environment"] = env_df

    # Run Structured Integrity Validation ONLY after data is uploaded
    if demo_df is not None and not demo_df.empty:
        validator = DataValidator(demo_df)
        result = validator.validate()
        status = result.get("status")
        summary = result.get("summary", {})
    else:
        status = None
        summary = {"rows": 0, "columns": 0, "duplicate_count": 0, "missing_values": 0}
        result = {}

    # Validation Results Render Card
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-title">{t("validation")} Framework Summary</div>', unsafe_allow_html=True)
        
        # Control notification banner states strictly based on context conditions
        if demo_df is not None and not demo_df.empty:
            if status == "ok":
                st.success(f"✔️ {t('validation_success')}")
            else:
                st.error(t("validation_failed"))
        else:
            st.info(f"📂 {t('upload_village_demographics_first')}")

        # Analytical Metrics Display Grid
        metric_cols = st.columns(4)
        metric_cols[0].metric(t("rows"), f"{summary.get('rows', 0):,}")
        metric_cols[1].metric(t("columns"), f"{summary.get('columns', 0):,}")
        metric_cols[2].metric(t("duplicate_count"), f"{summary.get('duplicate_count', 0):,}")
        metric_cols[3].metric(t("missing_values"), f"{summary.get('missing_values', 0):,}")

        if result.get("errors") or result.get("warnings"):
            st.markdown("<hr style='margin:16px 0; border:0; border-top:1px dashed #E2E8F0;'/>", unsafe_allow_html=True)
            
            if result.get("errors"):
                st.markdown(f"❌ **{t('validation_errors')}**")
                for e in result.get("errors"):
                    st.markdown(f"- {e}")
                    
            if result.get("warnings"):
                st.markdown(f"⚠️ **{t('validation_warnings')}**")
                for w in result.get("warnings"):
                    st.markdown(f"- {w}")
        st.markdown('</div>', unsafe_allow_html=True)

    # 5 & 6. Collapsible Data Preview Section with Dataframe Presentation Layer
    with st.expander(f"🔍 {t('view_uploaded_data_preview')}", expanded=False):
        if demo_df is not None and not demo_df.empty:
            # Modern, responsive data structure preview window
            st.dataframe(
                demo_df.head(10), 
                use_container_width=True
            )
        else:
            st.info(t("no_file_uploaded_yet"))
    st.markdown('</div>', unsafe_allow_html=True)


app()