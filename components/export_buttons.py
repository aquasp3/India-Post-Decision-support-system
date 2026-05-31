from __future__ import annotations

import json

import streamlit as st
import streamlit.components.v1 as components

from services import localization
from services.export_service import ExportService

t = localization.t


def _normalize_payload(value):
    if hasattr(value, "to_dict") and hasattr(value, "empty"):
        try:
            return value.to_dict(orient="records")
        except Exception:
            return str(value)
    if isinstance(value, dict):
        return {str(key): _normalize_payload(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_normalize_payload(item) for item in value]
    return value


def _export_signature(profile, recommendations, monthly_plan, suggested_actions, officer_insights) -> str:
    payload = {
        "profile": _normalize_payload(profile),
        "recommendations": _normalize_payload(recommendations),
        "monthly_plan": _normalize_payload(monthly_plan),
        "suggested_actions": _normalize_payload(list(suggested_actions or [])),
        "officer_insights": _normalize_payload(list(officer_insights or [])),
    }
    return json.dumps(payload, sort_keys=True, default=str)


def _action_card_html(icon: str, title: str, description: str) -> str:
    return f"""
    <div style="height:100%; background:rgba(255,255,255,0.92); border:1px solid rgba(15,23,42,0.08); border-radius:18px; padding:0.72rem 0.78rem; box-shadow:0 8px 18px rgba(15,23,42,0.05); backdrop-filter:blur(14px);">
        <div style="display:flex; align-items:flex-start; gap:0.6rem; margin-bottom:0.55rem;">
            <div style="width:2.35rem; height:2.35rem; border-radius:16px; display:inline-flex; align-items:center; justify-content:center; background:linear-gradient(135deg, rgba(11, 45, 92, 0.10), rgba(245, 130, 32, 0.12)); color:#0B2D5C; font-size:1.05rem; flex:0 0 auto;">{icon}</div>
            <div style="min-width:0;">
                <div style="color:#0B2D5C; font-size:0.94rem; font-weight:800; line-height:1.2; margin:0;">{title}</div>
                <div style="margin-top:0.18rem; color:#64748B; font-size:0.8rem; line-height:1.35;">{description}</div>
            </div>
        </div>
    </div>
    """


def render_export_buttons() -> None:
    service = ExportService()
    profile = st.session_state.get("selected_village_profile") or {}
    recommendations = st.session_state.get("recommendations") or []
    monthly_plan = st.session_state.get("monthly_plan")
    suggested_actions = st.session_state.get("suggested_actions") or []
    officer_insights = st.session_state.get("officer_insights") or []

    export_signature = _export_signature(profile, recommendations, monthly_plan, suggested_actions, officer_insights)
    cached_signature = st.session_state.get("_export_payload_signature")
    cached_payload = st.session_state.get("_export_payload_cache", {}) if cached_signature == export_signature else {}

    if not cached_payload:
        try:
            cached_payload = {
                "csv_bytes": service.build_csv_export(profile, recommendations, monthly_plan, suggested_actions),
                "pdf_bytes": service.build_pdf_report(
                    profile,
                    recommendations,
                    monthly_plan,
                    suggested_actions,
                    officer_insights=officer_insights,
                    government_report=False,
                ),
                "government_pdf_bytes": service.build_pdf_report(
                    profile,
                    recommendations,
                    monthly_plan,
                    suggested_actions,
                    officer_insights=officer_insights,
                    government_report=True,
                ),
            }
            st.session_state["_export_payload_signature"] = export_signature
            st.session_state["_export_payload_cache"] = cached_payload
        except Exception:
            st.error(t("export_generation_failed"))
            cached_payload = {"csv_bytes": b"", "pdf_bytes": b"", "government_pdf_bytes": b""}

    csv_bytes = cached_payload.get("csv_bytes", b"")
    pdf_bytes = cached_payload.get("pdf_bytes", b"")
    government_pdf_bytes = cached_payload.get("government_pdf_bytes", b"")

    st.markdown(
        """
        <style>
            .export-card-title {
                color: #0B2D5C;
                font-size: 0.78rem;
                font-weight: 900;
                text-transform: uppercase;
                letter-spacing: 0.16em;
                margin-bottom: 0.3rem;
            }

            .export-card-grid {
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 0.75rem;
            }

            .export-card-cta button,
            .export-card-cta div[data-testid="stDownloadButton"] button {
                min-height: 2.6rem;
                width: 100%;
                border-radius: 999px;
                font-weight: 800;
                padding: 0.55rem 0.85rem;
                border: 1px solid rgba(11, 45, 92, 0.14);
            }

            .export-card-cta button:hover,
            .export-card-cta div[data-testid="stDownloadButton"] button:hover {
                border-color: rgba(11, 45, 92, 0.24);
            }

            @media (max-width: 1100px) {
                .export-card-grid {
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                }
            }

            @media (max-width: 700px) {
                .export-card-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f'<div class="export-card-title">📥 {t("export_center_title")}</div>', unsafe_allow_html=True)

    card_columns = st.columns(4, gap="small")

    with card_columns[0]:
        st.markdown(_action_card_html("💾", "CSV Export", t("export_csv_description")), unsafe_allow_html=True)
        st.markdown('<div class="export-card-cta">', unsafe_allow_html=True)
        st.download_button(
            label=t("download_csv"),
            data=csv_bytes,
            file_name=f"{profile.get('village_name', 'india_post_dss')}_report.csv",
            mime="text/csv",
            use_container_width=True,
            key="export_download_csv",
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with card_columns[1]:
        st.markdown(_action_card_html("📄", "PDF Report", t("export_pdf_description")), unsafe_allow_html=True)
        st.markdown('<div class="export-card-cta">', unsafe_allow_html=True)
        st.download_button(
            label=t("export_pdf"),
            data=pdf_bytes,
            file_name=f"{profile.get('village_name', 'india_post_dss')}_report.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="export_download_pdf",
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with card_columns[2]:
        st.markdown(_action_card_html("🏛️", "Government Report", t("export_government_description")), unsafe_allow_html=True)
        st.markdown('<div class="export-card-cta">', unsafe_allow_html=True)
        st.download_button(
            label=t("government_report"),
            data=government_pdf_bytes,
            file_name=f"{profile.get('village_name', 'india_post_dss')}_government_report.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="export_download_government_pdf",
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with card_columns[3]:
        st.markdown(_action_card_html("🖨️", "Print View", t("export_print_description")), unsafe_allow_html=True)
        st.markdown('<div class="export-card-cta">', unsafe_allow_html=True)
        if st.button(t("print_view"), use_container_width=True, key="export_print_view"):
            st.session_state["show_print_view"] = True
            try:
                st.session_state["print_view_html"] = service.build_print_view_html(
                    profile,
                    recommendations,
                    monthly_plan,
                    suggested_actions,
                    officer_insights=officer_insights,
                )
                st.session_state["print_view_signature"] = export_signature
            except Exception:
                st.error(t("export_generation_failed"))
                st.session_state["print_view_html"] = ""
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get("show_print_view"):
        st.write("")
        st.markdown(_action_card_html("🖨️", t("print_view_registry"), t("print_view_registry")), unsafe_allow_html=True)
        if st.session_state.get("print_view_signature") != export_signature:
            try:
                st.session_state["print_view_html"] = service.build_print_view_html(
                    profile,
                    recommendations,
                    monthly_plan,
                    suggested_actions,
                    officer_insights=officer_insights,
                )
                st.session_state["print_view_signature"] = export_signature
            except Exception:
                st.error(t("export_generation_failed"))
                st.session_state["print_view_html"] = ""

        print_view_html = st.session_state.get("print_view_html", "")
        if print_view_html:
            components.html(print_view_html, height=1200, scrolling=True)
        else:
            st.info(t("no_data_available"))
