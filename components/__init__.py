from __future__ import annotations

from pathlib import Path
from typing import Optional

import streamlit as st

from config import app_config
from services import localization
from utils import session_manager

ASSETS_DIR = Path(__file__).parent.parent / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"


def render_sidebar() -> None:
    """Render the application sidebar with localized navigation and language selection."""
    session_manager.initialize_session()

    current_code = session_manager.get_language()
    if not current_code:
        current_code = "en"
    localization.set_language(current_code)

    st.markdown(
        """
        <style>
            section[data-testid="stSidebar"] {
                background: #F4F6F9 !important;
            }

            section[data-testid="stSidebar"] > div:first-child {
                padding: 0.8rem 0.95rem 1rem !important;
            }

            div[data-testid="stSidebarNav"],
            nav[data-testid="stSidebarNav"] {
                display: none !important;
                visibility: hidden !important;
                height: 0 !important;
                min-height: 0 !important;
                max-height: 0 !important;
                margin: 0 !important;
                padding: 0 !important;
                overflow: hidden !important;
            }

            div[data-testid="stSidebarNav"] + hr,
            nav[data-testid="stSidebarNav"] + hr,
            section[data-testid="stSidebar"] hr {
                display: none !important;
            }

            section[data-testid="stSidebar"] img {
                display: block !important;
                width: 100% !important;
                max-width: 152px !important;
                height: auto !important;
                margin: 0 auto 0.9rem auto !important;
            }

            .sidebar-brand {
                display: block;
                padding: 0 0 0.85rem 0;
                margin-bottom: 0.5rem;
                border-bottom: 1px solid #DDE3EC;
            }

            .sidebar-brand img {
                margin-bottom: 0.8rem !important;
            }

            .sidebar-title {
                margin: 0 0 0.18rem 0;
                color: #0B2D5C;
                font-size: 1.25rem;
                font-weight: 800;
                line-height: 1.2;
                letter-spacing: -0.02em;
                text-align: center;
            }

            .sidebar-subtitle {
                margin: 0;
                color: #64748B;
                font-size: 0.82rem;
                font-weight: 500;
                line-height: 1.35;
                text-align: center;
            }

            .sidebar-divider {
                border: none;
                border-top: 1px solid #DDE3EC;
                margin: 0.9rem 0 0.75rem;
            }

            /* Custom targets overriding Streamlit structural link elements */
            a[data-testid="stPageLink-NavLink"] {
                display: flex !important;
                align-items: center !important;
                width: 100% !important;
                box-sizing: border-box !important;
                padding: 0.65rem 0.9rem !important;
                border-radius: 12px !important;
                border-left: 4px solid transparent !important;
                color: #475569 !important;
                font-size: 0.92rem !important;
                font-weight: 600 !important;
                text-decoration: none !important;
                transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease !important;
                margin-bottom: 0.25rem !important;
            }

            a[data-testid="stPageLink-NavLink"]:hover {
                background-color: #EBF0F7 !important;
                color: #0B2D5C !important;
            }

            a[data-testid="stPageLink-NavLink"][aria-current="page"] {
                background-color: #E3EEFE !important;
                color: #1558C0 !important;
                font-weight: 700 !important;
                border-left-color: #1558C0 !important;
            }

            .sidebar-spacer {
                min-height: 1rem;
            }

            .sidebar-language {
                margin-top: auto;
                padding-top: 0.85rem;
                border-top: 1px solid #DDE3EC;
            }

            .sidebar-language-label {
                display: flex;
                align-items: center;
                gap: 0.45rem;
                margin: 0 0 0.5rem 0;
                color: #475569;
                font-size: 0.85rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.03em;
            }

            .sidebar-language-label svg {
                width: 15px;
                height: 15px;
                flex-shrink: 0;
                opacity: 0.7;
                color: #0B2D5C;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=138)

        st.markdown(
            f"""
            <div class="sidebar-brand">
                <div class="sidebar-title">{localization.t("app_name")}</div>
                <div class="sidebar-subtitle">{localization.t("app_subtitle")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Unified Native Link Matrix loop iteration replacing placeholder plain text
        nav_pages = [
            ("pages/1_Dashboard.py", f"{localization.t('dashboard')}"),
            ("pages/2_Upload_Village_Data.py", f"{localization.t('upload_village_data')}"),
            ("pages/3_Scheme_Catalog.py", f"{localization.t('scheme_catalog')}"),
            ("pages/4_Planning_Recommendations.py", f"{localization.t('planning_recommendations')}"),
            ("pages/5_About.py", f"{localization.t('about')}"),
        ]

        # Renders the components explicitly through native objects to bind layout CSS classes
        st.page_link("1_Dashboard.py", label=f"📊 {localization.t('dashboard')}")
        st.page_link("pages/2_Upload_Village_Data.py", label=f"📤 {localization.t('upload_village_data')}")
        st.page_link("pages/3_Scheme_Catalog.py", label=f"📚 {localization.t('scheme_catalog')}")
        st.page_link("pages/4_Planning_Recommendations.py", label=f"🗓️ {localization.t('planning_recommendations')}")
        st.page_link("pages/5_About.py", label=f"ℹ️ {localization.t('about')}")

        st.markdown('<div class="sidebar-spacer"></div>', unsafe_allow_html=True)

        globe_icon = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<circle cx="12" cy="12" r="10"/>'
            '<line x1="2" y1="12" x2="22" y2="12"/>'
            '<path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10'
            ' 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>'
            '</svg>'
        )

        st.markdown(
            f"""
            <div class="sidebar-language">
                <div class="sidebar-language-label">
                    {globe_icon}
                    <span>{localization.t("label_select_language")}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        languages = app_config.SUPPORTED_LANGUAGES
        labels = [label for _, label in languages]
        code_to_index = {code: index for index, (code, _) in enumerate(languages)}
        selected_index = code_to_index.get(current_code, 0)

        choice = st.selectbox(
            label="language_selector",
            options=labels,
            index=selected_index,
            key="global_sidebar_language_selector",
            label_visibility="collapsed",
        )

        selected_code = current_code
        try:
            selected_code = languages[labels.index(choice)][0]
        except ValueError:
            pass

        if selected_code != current_code:
            session_manager.set_language(selected_code)
            localization.set_language(selected_code)
            st.session_state["language"] = selected_code
            st.rerun()


def header(title: str, subtitle: Optional[str] = None) -> None:
    """Render a consistent page section header."""
    st.markdown(f"<div class='page-header'><h2 style='color:#0B2D5C; font-weight:800; letter-spacing:-0.02em;'>{title}</h2></div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='page-subtitle' style='color:#64748B; font-weight:500;'>{subtitle}</div>", unsafe_allow_html=True)