from html import escape

import streamlit as st

from services import localization

t = localization.t


def _render_html_cards(cards: list[str], columns: int = 2) -> None:
    for start in range(0, len(cards), columns):
        row = cards[start : start + columns]
        cols = st.columns(len(row), gap="medium")
        for col, card in zip(cols, row):
            with col:
                st.markdown(card, unsafe_allow_html=True)


def _glass_card(title: str, body: str, icon: str, extra_class: str = "") -> str:
    return f"""
    <div class="glass-card {extra_class}">
        <div class="card-icon">{escape(icon)}</div>
        <h3>{escape(title)}</h3>
        {body}
    </div>
    """


def _metric_card(value: str, label: str) -> str:
    return f"""
    <div class="metric-card glass-card">
        <div class="metric-value">{escape(value)}</div>
        <div class="metric-label">{escape(label)}</div>
    </div>
    """


def _feature_card(title: str, items: list[str], icon: str) -> str:
    feature_items = "".join(f"<li>{escape(item)}</li>" for item in items)
    return _glass_card(title, f'<ul class="feature-list">{feature_items}</ul>', icon)


def _timeline_card(step: str, title: str) -> str:
    return f"""
    <div class="timeline-card">
        <div class="timeline-step">{escape(step)}</div>
        <div class="timeline-title">{escape(title)}</div>
    </div>
    """


def _roadmap_card(title: str, items: list[str]) -> str:
    bullet_items = "".join(f"<li>{escape(item)}</li>" for item in items)
    return _glass_card(
        title,
        f'<div class="roadmap-phase">{escape(t("phase_2"))}</div><ul class="feature-list">{bullet_items}</ul>',
        "🗺️",
    )


def app() -> None:
    brief_markdown = "\n".join(
        [
            f"# {t('about_page_system_name')}",
            t("about_page_tagline"),
            "",
            f"## {t('mission')}",
            t("mission_description"),
            "",
            f"## {t('vision')}",
            t("vision_description"),
            "",
            f"## {t('project_impact_metrics')}",
            
            f"- 5 {t('languages_supported')}",
            f"- 12 {t('planning_horizon')}",
            f"- 6+ {t('analytics_engines')}",
            f"- {t('export_formats')}",
        ]
    )

    st.markdown(
        """
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
                    linear-gradient(180deg, #F7F9FC 0%, #FBFCFE 100%);
            }

            .about-shell {
                color: #1E293B;
            }

            .hero-card {
                position: relative;
                overflow: hidden;
                border-radius: 32px;
                padding: 2rem;
                color: #FFFFFF;
                background:
                    linear-gradient(135deg, rgba(11, 45, 92, 0.98) 0%, rgba(16, 58, 111, 0.98) 48%, rgba(245, 130, 32, 0.95) 100%);
                border: 1px solid rgba(255, 255, 255, 0.14);
                box-shadow: 0 32px 80px rgba(15, 23, 42, 0.18);
            }

            .hero-card::before {
                content: "";
                position: absolute;
                inset: 0;
                background-image:
                    radial-gradient(circle at 20% 20%, rgba(255, 255, 255, 0.14) 0, transparent 22%),
                    radial-gradient(circle at 80% 0%, rgba(255, 255, 255, 0.11) 0, transparent 18%),
                    linear-gradient(120deg, rgba(255, 255, 255, 0.06), transparent 40%);
                pointer-events: none;
            }

            .hero-grid {
                position: relative;
                z-index: 1;
                display: grid;
                grid-template-columns: 1.4fr 0.9fr;
                gap: 1.25rem;
                align-items: stretch;
            }

            .hero-badge {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.55rem 0.9rem;
                border-radius: 999px;
                background: rgba(255, 255, 255, 0.12);
                border: 1px solid rgba(255, 255, 255, 0.18);
                color: rgba(255, 255, 255, 0.92);
                font-size: 0.78rem;
                letter-spacing: 0.18em;
                text-transform: uppercase;
                font-weight: 800;
            }

            .hero-title {
                margin: 0.9rem 0 0.65rem;
                font-size: clamp(2.1rem, 4vw, 3.55rem);
                line-height: 1.04;
                font-weight: 900;
                letter-spacing: -0.04em;
            }

            .hero-subtitle {
                margin: 0;
                font-size: 1.05rem;
                line-height: 1.7;
                color: rgba(255, 255, 255, 0.88);
                max-width: 62ch;
            }

            .hero-tagline {
                margin: 1.15rem 0 0;
                padding-left: 1rem;
                border-left: 4px solid rgba(255, 255, 255, 0.74);
                font-size: 1.05rem;
                line-height: 1.6;
                color: rgba(255, 255, 255, 0.96);
                max-width: 58ch;
            }

            .hero-actions {
                display: flex;
                flex-wrap: wrap;
                gap: 0.8rem;
                margin-top: 1.6rem;
            }

            .hero-action {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                min-height: 3rem;
                padding: 0.82rem 1.15rem;
                border-radius: 999px;
                text-decoration: none;
                font-weight: 800;
                letter-spacing: 0.01em;
                transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
            }

            .hero-action:hover {
                transform: translateY(-2px);
            }

            .hero-action.primary {
                background: #FFFFFF;
                color: #0B2D5C;
                box-shadow: 0 16px 28px rgba(15, 23, 42, 0.18);
            }

            .hero-action.secondary {
                color: #FFFFFF;
                background: rgba(255, 255, 255, 0.10);
                border: 1px solid rgba(255, 255, 255, 0.20);
            }

            div[data-testid="stDownloadButton"] button {
                min-height: 3rem;
                border-radius: 999px;
                background: rgba(255, 255, 255, 0.10);
                color: #FFFFFF;
                border: 1px solid rgba(255, 255, 255, 0.20);
                padding: 0.82rem 1.15rem;
                font-weight: 800;
                width: 100%;
            }

            div[data-testid="stDownloadButton"] button:hover {
                background: rgba(255, 255, 255, 0.16);
                border-color: rgba(255, 255, 255, 0.30);
            }

            .hero-panel {
                position: relative;
                z-index: 1;
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 0.9rem;
                align-content: start;
            }

            .hero-chip {
                padding: 1rem;
                border-radius: 20px;
                background: rgba(255, 255, 255, 0.12);
                border: 1px solid rgba(255, 255, 255, 0.16);
                backdrop-filter: blur(16px);
                box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
            }

            .hero-chip strong {
                display: block;
                font-size: 1.45rem;
                line-height: 1.1;
                margin-bottom: 0.25rem;
            }

            .hero-chip span {
                font-size: 0.84rem;
                color: rgba(255, 255, 255, 0.80);
            }

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
            }

            .glass-card:hover {
                transform: translateY(-4px);
                border-color: rgba(11, 45, 92, 0.16);
                box-shadow: 0 20px 44px rgba(15, 23, 42, 0.12);
            }

            .glass-card h3 {
                margin: 0.1rem 0 0.7rem;
                color: #0B2D5C;
                font-size: 1.14rem;
                letter-spacing: -0.02em;
            }

            .card-icon {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 2.55rem;
                height: 2.55rem;
                border-radius: 16px;
                background: linear-gradient(135deg, rgba(11, 45, 92, 0.10), rgba(245, 130, 32, 0.12));
                color: #0B2D5C;
                font-size: 1.15rem;
                margin-bottom: 0.8rem;
            }

            .card-copy,
            .roadmap-phase,
            .timeline-title,
            .section-subtitle,
            .module-copy {
                color: #475569;
                line-height: 1.65;
                margin: 0;
            }

            .section-heading {
                margin: 2rem 0 1rem;
            }

            .section-heading .eyebrow {
                margin: 0 0 0.35rem;
                color: #F58220;
                font-weight: 900;
                text-transform: uppercase;
                letter-spacing: 0.18em;
                font-size: 0.76rem;
            }

            .section-heading h2 {
                margin: 0;
                color: #0B2D5C;
                font-size: clamp(1.45rem, 2.4vw, 2.1rem);
                letter-spacing: -0.03em;
            }

            .section-heading p {
                margin: 0.45rem 0 0;
                color: #64748B;
                max-width: 70ch;
                line-height: 1.7;
            }

            .metric-card {
                border-top: 4px solid #F58220;
                padding: 1.1rem 1.2rem;
                margin-bottom: 1rem;
            }

            .metric-value {
                color: #0B2D5C;
                font-size: 2rem;
                line-height: 1;
                font-weight: 900;
                letter-spacing: -0.04em;
                margin-bottom: 0.45rem;
            }

            .metric-label {
                color: #64748B;
                font-weight: 700;
            }

            .feature-list {
                margin: 0.1rem 0 0;
                padding-left: 1rem;
                color: #334155;
                line-height: 1.8;
            }

            .feature-list li {
                margin-bottom: 0.25rem;
            }

            .timeline-card {
                position: relative;
                background: rgba(255, 255, 255, 0.88);
                border: 1px solid rgba(15, 23, 42, 0.08);
                border-radius: 22px;
                padding: 1.05rem 1.1rem;
                box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
                min-height: 110px;
            }

            .timeline-card::after {
                content: "";
                position: absolute;
                left: 1.1rem;
                bottom: 0.9rem;
                width: 48px;
                height: 3px;
                border-radius: 999px;
                background: linear-gradient(90deg, #0B2D5C, #F58220);
                opacity: 0.8;
            }

            .timeline-step {
                color: #F58220;
                font-size: 0.76rem;
                font-weight: 900;
                text-transform: uppercase;
                letter-spacing: 0.16em;
                margin-bottom: 0.45rem;
            }

            .timeline-title {
                color: #0F172A;
                font-weight: 700;
            }

            .timeline-arrow {
                text-align: center;
                color: #F58220;
                font-size: 1.55rem;
                line-height: 1;
                padding: 0.4rem 0 0.6rem;
                font-weight: 800;
            }

            .architecture-shell {
                border-radius: 28px;
                padding: 1.4rem;
                background: linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(248, 250, 252, 0.98));
                border: 1px solid rgba(15, 23, 42, 0.08);
                box-shadow: 0 16px 40px rgba(15, 23, 42, 0.08);
            }

            .architecture-wrap {
                display: flex;
                flex-direction: column;
                gap: 0.72rem;
                align-items: center;
            }

            .arch-node {
                width: min(100%, 540px);
                padding: 1rem 1.05rem;
                border-radius: 20px;
                text-align: center;
                background: rgba(255, 255, 255, 0.92);
                border: 1px solid rgba(15, 23, 42, 0.08);
                box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
                transition: transform 0.18s ease, border-color 0.18s ease;
            }

            .arch-node:hover {
                transform: translateY(-3px);
                border-color: rgba(11, 45, 92, 0.18);
            }

            .arch-node strong {
                display: block;
                color: #0B2D5C;
                font-size: 1rem;
                margin-bottom: 0.2rem;
            }

            .arch-node span {
                color: #64748B;
                font-size: 0.95rem;
            }

            .arch-arrow {
                color: #F58220;
                font-size: 1.35rem;
                font-weight: 900;
                line-height: 1;
            }

            .badge-row {
                display: flex;
                flex-wrap: wrap;
                gap: 0.65rem;
            }

            .tech-badge {
                display: inline-flex;
                align-items: center;
                gap: 0.45rem;
                padding: 0.62rem 0.92rem;
                border-radius: 999px;
                background: rgba(11, 45, 92, 0.08);
                border: 1px solid rgba(11, 45, 92, 0.10);
                color: #0B2D5C;
                font-weight: 800;
            }

            .module-table-wrap {
                overflow: hidden;
                border-radius: 22px;
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(15, 23, 42, 0.08);
                box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
            }

            .module-table {
                width: 100%;
                border-collapse: collapse;
            }

            .module-table th,
            .module-table td {
                padding: 1rem 1.1rem;
                border-bottom: 1px solid rgba(15, 23, 42, 0.08);
                text-align: left;
                vertical-align: top;
            }

            .module-table th {
                background: rgba(11, 45, 92, 0.06);
                color: #0B2D5C;
                font-size: 0.76rem;
                letter-spacing: 0.14em;
                text-transform: uppercase;
            }

            .module-table tr:last-child td {
                border-bottom: none;
            }

            .roadmap-phase {
                color: #F58220;
                font-size: 0.8rem;
                font-weight: 900;
                letter-spacing: 0.14em;
                text-transform: uppercase;
                margin-bottom: 0.6rem;
            }

            .footer-band {
                margin-top: 1.5rem;
                padding: 1.35rem 1.4rem;
                border-radius: 24px;
                background: linear-gradient(135deg, #0B2D5C, #12386F);
                color: #FFFFFF;
                text-align: center;
                box-shadow: 0 18px 38px rgba(15, 23, 42, 0.14);
            }

            .footer-band h3 {
                margin: 0 0 0.35rem;
                font-size: 1.15rem;
            }

            .footer-band p {
                margin: 0;
                color: rgba(255, 255, 255, 0.82);
                line-height: 1.65;
            }

            @media (max-width: 900px) {
                .hero-grid,
                .profile-grid {
                    grid-template-columns: 1fr;
                }

                .hero-panel {
                    grid-template-columns: 1fr 1fr;
                }
            }

            @media (max-width: 640px) {
                .hero-card,
                .glass-card,
                .architecture-shell {
                    padding: 1.1rem;
                }

                .hero-panel {
                    grid-template-columns: 1fr;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    hero_metrics = [
        ("12", t("planning_horizon")),
        ("6+", t("analytics_engines")),
    ]

    st.markdown('<div class="about-shell">', unsafe_allow_html=True)

    st.markdown(
        f"""
        <section class="hero-card">
            <div class="hero-grid">
                <div>
                    <div class="hero-badge">🏛️ {escape(t("about_page_government_label"))} • {escape(t("about_page_department_label"))}</div>
                    <h1 class="hero-title">{escape(t("about_page_system_name"))}</h1>
                    <p class="hero-subtitle">{escape(t("about_page_subtitle"))} (Capstone Project Showcase)</p>
                    <div class="hero-tagline">“{escape(t("about_page_tagline"))}”</div>
                    <div class="hero-actions">
                        <a class="hero-action primary" href="#architecture">{escape(t("view_architecture"))}</a>
                        <a class="hero-action secondary" href="#capabilities">{escape(t("explore_features"))}</a>
                    </div>
                </div>
                <div class="hero-panel">
                    {''.join(
                        f'<div class="hero-chip"><strong>{escape(value)}</strong><span>{escape(label)}</span></div>'
                        for value, label in hero_metrics
                    )}
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    _, download_col, _ = st.columns([1.1, 1, 1.1], gap="small")
    with download_col:
        st.download_button(
            label=t("download_project_brief"),
            data=brief_markdown.encode("utf-8"),
            file_name="India_Post_DSS_Project_Brief.md",
            mime="text/markdown",
            width="stretch",
            key="about_download_project_brief",
        )

    st.markdown(
        f"""
        <div class="section-heading">
            <div class="eyebrow">{escape(t("mission_and_vision"))}</div>
            <h2>{escape(t("about_page_subtitle"))}</h2>
            <p>{escape(t("about_page_tagline"))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    mission_card = _glass_card(
        t("mission"),
        f'<p class="card-copy">{escape(t("mission_description"))}</p>',
        "🎯",
    )
    vision_card = _glass_card(
        t("vision"),
        f'<p class="card-copy">{escape(t("vision_description"))}</p>',
        "🌍",
    )
    mission_col, vision_col = st.columns(2, gap="medium")
    with mission_col:
        st.markdown(mission_card, unsafe_allow_html=True)
    with vision_col:
        st.markdown(vision_card, unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="section-heading">
            <div class="eyebrow">{escape(t("project_impact_metrics"))}</div>
            <h2>Project Scope Validation</h2>
            <p>{escape(t("about_page_tagline"))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metric_cards = [
        _metric_card("12", t("planning_horizon")),
        _metric_card("6+", t("analytics_engines")),
    ]
    _render_html_cards(metric_cards, columns=2)

    st.markdown('<div id="capabilities"></div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="section-heading">
            <div class="eyebrow">{escape(t("core_capabilities"))}</div>
            <h2>{escape(t("core_capabilities"))}</h2>
            <p>{escape(t("about_page_system_name"))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    capability_cards = [
        _feature_card(t("village_intelligence"), [t("demographic_analysis"), t("population_segmentation"), t("village_profiling")], "📊"),
        _feature_card(t("recommendation_engine"), [t("scheme_matching"), t("relevance_scoring"), t("priority_ranking")], "🤖"),
        _feature_card(t("campaign_planning"), [t("annual_calendar"), t("seasonal_rollouts"), t("outreach_scheduling")], "📅"),
        _feature_card(t("risk_analytics"), [t("flood_risk"), t("drought_vulnerability"), t("insurance_prioritization")], "⚠️"),
        _feature_card(t("multilingual_support"), [t("english_language"), t("hindi_language"), t("telugu_language"), t("tamil_language"), t("kannada_language")], "🌐"),
        _feature_card(t("reporting_system"), [t("csv_export"), t("brief_reports"), t("printable_outputs")], "📄"),
    ]
    _render_html_cards(capability_cards, columns=3)

    st.markdown(
        f"""
        <div class="section-heading">
            <div class="eyebrow">{escape(t("system_workflow"))}</div>
            <h2>{escape(t("system_workflow"))}</h2>
            <p>{escape(t("about_page_tagline"))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    workflow_steps = [
        t("upload_village_dataset"),
        t("validation_engine"),
        t("data_cleaning"),
        t("anomaly_detection"),
        t("village_analysis_step"),
        t("scheme_recommendation_step"),
        t("priority_classification"),
        t("campaign_planning"),
        t("report_generation"),
    ]
    for start in range(0, len(workflow_steps), 3):
        row = workflow_steps[start : start + 3]
        _render_html_cards([
            _timeline_card(f"{index + 1}️⃣", step)
            for index, step in enumerate(row, start=start)
        ], columns=len(row))
        if start + 3 < len(workflow_steps):
            st.markdown('<div class="timeline-arrow">↓</div>', unsafe_allow_html=True)

    st.markdown('<div id="architecture"></div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="section-heading">
            <div class="eyebrow">{escape(t("dss_architecture"))}</div>
            <h2>{escape(t("dss_architecture"))}</h2>
            <p>{escape(t("architecture_flow_label"))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    architecture_steps = [
        (t("village_data"), t("upload_village_dataset")),
        (t("validation_layer"), t("validation_engine")),
        (t("preprocessing_layer"), t("data_cleaning")),
        (t("anomaly_detection"), t("anomaly_detection")),
        (t("analytics_engine_layer"), t("village_analysis_step")),
        (t("scheme_matching"), t("scheme_recommendation_step")),
        (t("priority_engine"), t("priority_classification")),
        (t("planning_generator"), t("campaign_planning")),
        (t("export_service"), t("report_generation")),
    ]
    st.markdown('<div class="architecture-shell">', unsafe_allow_html=True)
    st.markdown('<div class="architecture-wrap">', unsafe_allow_html=True)
    for index, (node_title, node_desc) in enumerate(architecture_steps):
        st.markdown(
            f"""
            <div class="arch-node">
                <strong>{escape(node_title)}</strong>
                <span>{escape(node_desc)}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if index < len(architecture_steps) - 1:
            st.markdown('<div class="arch-arrow">↓</div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="section-heading">
            <div class="technology_stack">{escape(t("technology_stack"))}</div>
            <h2>{escape(t("technology_stack"))}</h2>
            <p>{escape(t("modular_services"))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tech_badges = [
        t("frontend"),
        t("backend"),
        t("analytics"),
        t("data_processing"),
        t("visualization"),
        t("modular_services"),
    ]
    st.markdown(
        "<div class='glass-card'><div class='badge-row'>"
        + "".join(f"<span class='tech-badge'>{escape(badge)}</span>" for badge in tech_badges)
        + "</div></div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="section-heading">
            <div class="eyebrow">{escape(t("project_modules"))}</div>
            <h2>{escape(t("project_modules"))}</h2>
            <p>{escape(t("module"))} • {escape(t("purpose"))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    module_rows = [
        (t("data_validator"), t("validate_uploaded_datasets")),
        (t("preprocessor"), t("clean_and_normalize_data")),
        (t("anomaly_detector"), t("detect_inconsistencies")),
        (t("scheme_matcher"), t("match_villages_to_schemes")),
        (t("priority_engine"), t("assign_priorities")),
        (t("planning_generator"), t("generate_annual_plans")),
        (t("export_service"), t("create_reports")),
        (t("localization_engine"), t("multilingual_support")),
    ]
    table_html = "".join(
        f"<tr><td><strong>{escape(module)}</strong></td><td>{escape(purpose)}</td></tr>"
        for module, purpose in module_rows
    )
    st.markdown(
        f"""
        <div class="module-table-wrap">
            <table class="module-table">
                <thead>
                    <tr>
                        <th>{escape(t("module"))}</th>
                        <th>{escape(t("purpose"))}</th>
                    </tr>
                </thead>
                <tbody>
                    {table_html}
                </tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="section-heading">
            <div class="eyebrow">{escape(t("future_roadmap"))}</div>
            <h2>{escape(t("future_roadmap"))}</h2>
            <p>{escape(t("phase_2"))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    roadmap_cards = [
        _roadmap_card(t("gis_mapping"), [t("village_heatmaps")]),
        _roadmap_card(t("ai_chat_assistant"), [t("predictive_analytics")]),
        _roadmap_card(t("mobile_officer_app"), [t("cloud_deployment")]),
        _roadmap_card(t("village_heatmaps"), [t("predictive_analytics")]),
        _roadmap_card(t("predictive_analytics"), [t("cloud_deployment")]),
        _roadmap_card(t("cloud_deployment"), [t("gis_mapping")]),
    ]
    _render_html_cards(roadmap_cards, columns=3)

    st.markdown(
        f"""
        <div class="footer-band">
            <h3>{escape(t("footer_title"))}</h3>
            <p><strong>Academic Sandbox Prototype</strong></p>
            <p style="font-size: 0.9rem; margin-top: 0.5rem; opacity: 0.85;">
                Developed as an engineering capstone showcase evaluating decision support architectures, data preprocessing frameworks, and localized analytical dashboard pipelines.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


app()