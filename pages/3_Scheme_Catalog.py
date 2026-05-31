import streamlit as st
import pandas as pd
#from components import render_sidebar
from services import localization
from services.data_manager import DataManager

t = localization.t


def _kpi_card(col, label: str, value) -> None:
    col.metric(label, value)


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
                animation: floatTitle 5.5s ease-in-out infinite;
            }

            @keyframes floatTitle {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-3px); }
            }

            .console-header {
                text-align: center;
                margin: 1.25rem 0 0.25rem 0;
                font-size: 1.8rem;
                font-weight: 900;
                color: #0B2D5C;
                letter-spacing: -0.03em;
            }

            .console-subtitle {
                text-align: center;
                margin: 0 0 1.5rem 0;
                font-size: 1rem;
                color: #64748B;
                font-weight: 500;
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

            .catalog-kpi-card {
                position: relative;
                background: rgba(255, 255, 255, 0.88);
                border-top: 4px solid #F58220;
                border-left: 1px solid rgba(15, 23, 42, 0.08);
                border-right: 1px solid rgba(15, 23, 42, 0.08);
                border-bottom: 1px solid rgba(15, 23, 42, 0.08);
                border-radius: 16px;
                padding: 1.1rem 1.2rem;
                box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
                margin-bottom: 1rem;
                backdrop-filter: blur(18px);
            }

            .catalog-filter-shell {
                background: linear-gradient(180deg, rgba(248, 250, 252, 0.9) 0%, rgba(255, 255, 255, 0.9) 100%);
                border: 1px solid rgba(15, 23, 42, 0.08);
                border-radius: 24px;
                padding: 1.35rem;
                margin-bottom: 1.25rem;
                box-shadow: 0 12px 36px rgba(15, 23, 42, 0.07);
                backdrop-filter: blur(18px);
            }

            .catalog-filter-subtitle {
                margin-top: -0.5rem;
                margin-bottom: 1rem;
                color: #64748B;
                font-size: 0.95rem;
            }

            /* --- Upgraded Scheme Detail Dashboard UI --- */
            .detail-panel {
                background-color: rgba(248, 250, 252, 0.8);
                border-radius: 16px;
                padding: 1.5rem;
                border-left: 5px solid #F58220;
                margin-top: 0.5rem;
            }
            
            .detail-main-title {
                font-size: 1.4rem;
                color: #0B2D5C;
                font-weight: 800;
                margin: 0 0 0.25rem 0;
                letter-spacing: -0.02em;
            }
            
            .detail-sub-id {
                font-size: 0.85rem;
                color: #64748B;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 1.25rem;
            }
            
            .meta-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 1rem;
                margin-top: 0.5rem;
            }
            
            .meta-card {
                background: #FFFFFF;
                padding: 1rem;
                border-radius: 12px;
                border: 1px solid rgba(15, 23, 42, 0.08);
                box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03);
            }
            
            .meta-label {
                font-size: 0.75rem;
                color: #64748B;
                text-transform: uppercase;
                font-weight: 800;
                letter-spacing: 0.5px;
                margin-bottom: 0.35rem;
                display: flex;
                align-items: center;
                gap: 0.35rem;
            }
            
            .meta-value {
                font-size: 1.1rem;
                color: #0B2D5C;
                font-weight: 700;
            }
            
            .timeline-badge {
                display: inline-flex;
                align-items: center;
                gap: 0.4rem;
                padding: 0.35rem 0.75rem;
                background-color: #E0F2FE;
                color: #0369A1;
                border-radius: 6px;
                font-size: 0.9rem;
                font-weight: 700;
            }

            @media (max-width: 900px) {
                .gov-header { padding: 1.5rem; }
            }
            @media (max-width: 640px) {
                .gov-header, .glass-card { padding: 1.1rem; }
            }
        </style>
    """, unsafe_allow_html=True)

    title = localization.t("catalog_page_title")
    subtitle = localization.t("catalog_page_subtitle")

    # 2. Government of India Brand Header
    st.markdown('<div class="about-shell">', unsafe_allow_html=True)
    with st.container():
        st.markdown(f"""
            <div class="gov-header">
                <div class="gov-emblem">🏛️</div>
                <div class="gov-subtitle">Department of Posts • Government of India</div>
                <div class="gov-title">Decision Support System (DSS) for Rural Campaign Management</div>
            </div>
            <div class="console-header">📚 {title}</div>
            <div class="console-subtitle">{subtitle}</div>
        """, unsafe_allow_html=True)

    dm = DataManager()
    df = dm.load_scheme_catalog()

    if df is None:
        df = pd.DataFrame()

    # Basic KPIs Calculation Block
    total = int(df.shape[0]) if not df.empty else 0
    tg_count = int(df["target_group"].nunique()) if "target_group" in df.columns and not df.empty else 0
    pr_count = int(df["priority_weight"].nunique()) if "priority_weight" in df.columns and not df.empty else 0

    # 3. Aggregated Metric Indicator Stream
    k0, k1, k2 = st.columns(3)
    with k0:
        st.markdown('<div class="catalog-kpi-card">', unsafe_allow_html=True)
        _kpi_card(st, f"📋 {t('total_schemes')}", total)
        st.markdown('</div>', unsafe_allow_html=True)
    with k1:
        st.markdown('<div class="catalog-kpi-card">', unsafe_allow_html=True)
        _kpi_card(st, f"👥 {t('target_groups_count')}", tg_count)
        st.markdown('</div>', unsafe_allow_html=True)
    with k2:
        st.markdown('<div class="catalog-kpi-card">', unsafe_allow_html=True)
        _kpi_card(st, f"⭐ {t('priority_categories_count')}", pr_count)
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    # 4. Catalog Filtering Control Hub Panel
    st.markdown('<div class="catalog-filter-shell">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-header-title">🔎 {t("catalog_filter_title")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="catalog-filter-subtitle">{t("catalog_filter_subtitle")}</div>', unsafe_allow_html=True)
    
    search_term = st.text_input(t("label_search"), placeholder=t("search_placeholder"))

    f_col1, f_col2 = st.columns(2)
    with f_col1:
        target_options = [t("filter_all")] + [t("filter_farmers"), t("filter_women"), t("filter_children"), t("filter_senior_citizens"), t("filter_others")]
        selected_target = st.selectbox(t("label_filter_target_group"), target_options, index=0)
    with f_col2:
        priority_options = [t("priority_all"), t("priority_high"), t("priority_medium"), t("priority_low")]
        selected_priority = st.selectbox(t("label_filter_priority"), priority_options, index=0)
    st.markdown('</div>', unsafe_allow_html=True)

    # Filtering Logic Execution
    filtered = df.copy()
    if not filtered.empty:
        if search_term:
            mask = pd.Series(False, index=filtered.index)
            for col in ["scheme_name", "target_group", "priority_weight"]:
                if col in filtered.columns:
                    mask = mask | filtered[col].astype(str).str.contains(search_term, case=False, na=False)
            filtered = filtered[mask]

        if selected_target != t("filter_all"):
            target_series = filtered.get("target_group", "").astype(str).str.lower()
            target_filters = {
                t("filter_farmers"): ["farmer", "agriculture"],
                t("filter_women"): ["women", "female"],
                t("filter_children"): ["child", "children"],
                t("filter_senior_citizens"): ["senior", "elder"],
            }
            if selected_target == t("filter_others"):
                known_tokens = ["farmer", "agriculture", "women", "female", "child", "children", "senior", "elder"]
                mask = ~target_series.apply(lambda value: any(token in value for token in known_tokens))
            else:
                tokens = target_filters.get(selected_target, [selected_target.lower()])
                mask = target_series.apply(lambda value: any(token in value for token in tokens))
            filtered = filtered[mask]

        if selected_priority != t("priority_all"):
            priority_series = pd.to_numeric(filtered.get("priority_weight", pd.Series(dtype=float)), errors="coerce")
            high_cutoff = priority_series.quantile(0.67) if not priority_series.dropna().empty else None
            medium_cutoff = priority_series.quantile(0.33) if not priority_series.dropna().empty else None

            if selected_priority == t("priority_high") and high_cutoff is not None:
                filtered = filtered[priority_series >= high_cutoff]
            elif selected_priority == t("priority_medium") and high_cutoff is not None and medium_cutoff is not None:
                filtered = filtered[(priority_series >= medium_cutoff) & (priority_series < high_cutoff)]
            elif selected_priority == t("priority_low") and medium_cutoff is not None:
                filtered = filtered[priority_series < medium_cutoff]

    st.write("")

    if filtered.empty:
        st.info(t("no_schemes_found"))
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Extract valid presentation data framework matrix
    table_cols = []
    if "scheme_name" in filtered.columns:
        table_cols.append("scheme_name")
    if "target_group" in filtered.columns:
        table_cols.append("target_group")
    if "priority_weight" in filtered.columns:
        table_cols.append("priority_weight")
    if "scheme_id" in filtered.columns:
        table_cols.append("scheme_id")
    if "peak_month_name" in filtered.columns:
        table_cols.append("peak_month_name")

    table_df = filtered[table_cols] if table_cols else filtered

    # 5. National Scheme Registry Directory Table
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-header-title">📋 {t("national_scheme_registry_directory")}</div>', unsafe_allow_html=True)
    st.dataframe(table_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")

    # 6. Interactive Scheme Detail Explorer Portal
    scheme_names = filtered["scheme_name"].astype(str).tolist() if "scheme_name" in filtered.columns else [str(i) for i in filtered.index]
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-header-title">📑 {t("scheme_detail")}</div>', unsafe_allow_html=True)
    
    selected = st.selectbox(t("select_scheme_placeholder"), [t("view_details")] + scheme_names, label_visibility="visible")

    if selected and selected != t("view_details"):
        if "scheme_name" in filtered.columns:
            row = filtered[filtered["scheme_name"].astype(str) == selected].iloc[0]
        else:
            row = filtered.iloc[int(selected)]

        st.markdown(f"""
<div class="detail-panel">
<div class="detail-main-title">📂 {row.get('scheme_name', '')}</div>
<div class="detail-sub-id">{t('scheme_id')}: {row.get('scheme_id', 'N/A')}</div>
<div class="meta-grid">
<div class="meta-card">
<div class="meta-label">👥 {t('target_group')}</div>
<div class="meta-value">{row.get('target_group', 'General')}</div>
</div>
<div class="meta-card">
<div class="meta-label">⚖️ {t('priority_weight')}</div>
<div class="meta-value">{row.get('priority_weight', 'N/A')}</div>
</div>
<div class="meta-card">
<div class="meta-label">📅 {t('peak_operational_month')}</div>
<div class="meta-value"><span class="timeline-badge">☀️ {row.get('peak_month_name', 'N/A')}</span></div>
</div>
</div>
<div class="meta-grid" style="margin-top: 1rem;">
<div class="meta-card">
<div class="meta-label">⏳ {t('required_lead_time')}</div>
<div class="meta-value">{row.get('lead_time_months', '0')} {t('months')}</div>
</div>
<div class="meta-card">
<div class="meta-label">🚦 {t('campaign_start_month')}</div>
<div class="meta-value">{row.get('start_month_name', 'N/A')}</div>
</div>
<div class="meta-card">
<div class="meta-label">🔢 {t('start_month_sequence')}</div>
<div class="meta-value">{t('month_number_prefix')}{row.get('start_month_numeric', 'N/A')}</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)
                
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


app()