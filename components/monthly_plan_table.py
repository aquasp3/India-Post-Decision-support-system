from html import escape
from typing import Any

import streamlit as st

from services import localization
from services.export_service import normalize_action, normalize_campaign_name, normalize_priority, normalize_stage

t = localization.t


def _normalize(value: Any) -> str:
    return str(value or "").strip().lower()


def _cell_value(row, *keys: str) -> str:
    for key in keys:
        value = row.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def _title_case(text: str) -> str:
    cleaned = str(text or "").strip()
    if not cleaned:
        return ""
    return cleaned[0].upper() + cleaned[1:]


def _map_campaign_name(raw_name: str) -> str:
    return normalize_campaign_name(raw_name)


def _priority_badge(priority_raw: str) -> str:
    value = normalize_priority(priority_raw)
    value_key = _normalize(value)
    if value_key == _normalize(t("priority_high")):
        return f'<span class="plan-badge high">🔴 {escape(value)}</span>'
    if value_key == _normalize(t("priority_medium")):
        return f'<span class="plan-badge medium">🟡 {escape(value)}</span>'
    return f'<span class="plan-badge routine">🟢 {escape(value)}</span>'


def _status_badge(status_raw: str, month_raw: str, campaign_name: str) -> str:
    value = _normalize(status_raw)
    month_value = _normalize(month_raw)
    campaign_value = _normalize(campaign_name)
    stage_label = normalize_stage(status_raw)
    stage_value = _normalize(stage_label)

    if not value or value == _normalize(t("scheme_no_campaign")) or "no active campaign" in value:
        return f'<span class="plan-badge neutral">{escape(t("scheme_no_campaign"))}</span>'

    if stage_value == _normalize(t("stage_peak")) or "peak" in value:
        return f'<span class="plan-badge peak">⭐ {escape(stage_label)}</span>'
    if stage_value == _normalize(t("stage_active")) or "active" in value:
        return f'<span class="plan-badge active">🔴 {escape(stage_label)}</span>'
    if stage_value == _normalize(t("stage_prepare")) or "preparation" in value or "prepare" in value:
        return f'<span class="plan-badge preparation">🟡 {escape(stage_label)}</span>'
    if stage_value == _normalize(t("stage_follow_up")) or "follow" in value:
        return f'<span class="plan-badge followup">🟢 {escape(stage_label)}</span>'

    if "women" in campaign_value and month_value in {"august", "september", "october"}:
        return f'<span class="plan-badge peak">⭐ {escape(stage_label or t("stage_peak"))}</span>'

    return f'<span class="plan-badge followup">🟢 {escape(stage_label or t("stage_follow_up"))}</span>'


def _campaign_action(campaign_name: str, status_raw: str) -> str:
    return normalize_action("", campaign_name=campaign_name, stage=status_raw)


def _cell_html(label: str, value_html: str) -> str:
    return f'''
    <div class="plan-cell" data-label="{escape(label)}">
        {value_html}
    </div>
    '''


def _row_html(month: str, campaign: str, priority_html: str, status_html: str, action: str) -> str:
    return f'''
    <div class="plan-row">
        {_cell_html(t("table_month"), f'<span class="month-pill">{escape(month)}</span>')}
        {_cell_html(t("table_campaign"), f'<div class="campaign-name">{escape(campaign)}</div>')}
        {_cell_html(t("table_priority"), priority_html)}
        {_cell_html(t("table_status"), status_html)}
        {_cell_html(t("table_officer_action"), f'<div class="action-text">{escape(action)}</div>')}
    </div>
    '''


def _render_rows(plan_df) -> str:
    html_rows = []
    for _, row in plan_df.iterrows():
        month = _cell_value(row, "month", "Month")
        raw_campaign = _cell_value(row, "Scheme", "campaign_name", "scheme_name")
        raw_priority = _cell_value(row, "priority", "Priority")
        raw_status = _cell_value(row, "status", "Status")
        raw_action = _cell_value(row, "officer_action", "Officer_Action", "Why_Recommended", "why_recommended")

        campaign = _map_campaign_name(raw_campaign)
        priority_html = _priority_badge(raw_priority)
        status_html = _status_badge(raw_status, month, campaign)
        action = _campaign_action(raw_campaign, raw_status) if not raw_action else normalize_action(raw_action, campaign_name=raw_campaign, stage=raw_status)

        html_rows.append(_row_html(month, campaign, priority_html, status_html, action))

    return "".join(html_rows)


def render_monthly_plan_table(plan_df) -> None:
    title = t("annual_campaign_table_title")
    empty_state = t("annual_campaign_table_empty_state")

    st.markdown(
        """
        <style>
            .annual-plan-shell {
                background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(248,250,252,0.98) 100%);
                border: 1px solid rgba(15, 23, 42, 0.08);
                border-radius: 24px;
                box-shadow: 0 16px 40px rgba(15, 23, 42, 0.07);
                padding: 0.95rem;
            }

            .annual-plan-title {
                display: flex;
                align-items: center;
                gap: 0.65rem;
                margin: 0 0 0.7rem;
                color: #0B2D5C;
                font-size: 1.15rem;
                font-weight: 800;
                letter-spacing: -0.03em;
            }

            .annual-plan-title::before {
                content: "";
                width: 10px;
                height: 28px;
                border-radius: 999px;
                background: linear-gradient(180deg, #FF9933 0%, #0B2D5C 100%);
                box-shadow: 0 0 0 5px rgba(255, 153, 51, 0.12);
            }

            .annual-plan-scroll {
                max-height: 62vh;
                overflow-y: auto;
                padding-right: 0.2rem;
            }

            .plan-head,
            .plan-row {
                display: grid;
                grid-template-columns: minmax(110px, 0.8fr) minmax(220px, 1.65fr) minmax(150px, 0.95fr) minmax(150px, 1fr) minmax(260px, 1.7fr);
                gap: 0.65rem;
                align-items: stretch;
            }

            .plan-head {
                position: sticky;
                top: 0;
                z-index: 5;
                margin-bottom: 0.55rem;
                padding: 0.7rem 0.8rem;
                border: 1px solid rgba(15, 23, 42, 0.08);
                border-radius: 18px;
                background: rgba(248, 250, 252, 0.96);
                backdrop-filter: blur(12px);
                color: #64748B;
                font-size: 0.72rem;
                font-weight: 900;
                text-transform: uppercase;
                letter-spacing: 0.14em;
            }

            .plan-row {
                margin-bottom: 0.55rem;
                padding: 0.78rem 0.82rem;
                border: 1px solid rgba(15, 23, 42, 0.08);
                border-radius: 18px;
                background: rgba(255, 255, 255, 0.96);
                box-shadow: 0 8px 18px rgba(15, 23, 42, 0.04);
                transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
            }

            .plan-row:hover {
                transform: translateY(-2px);
                border-color: rgba(11, 45, 92, 0.18);
                box-shadow: 0 14px 28px rgba(15, 23, 42, 0.08);
            }

            .plan-cell {
                min-width: 0;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }

            .plan-cell[data-label]::before {
                content: attr(data-label);
                display: none;
                color: #64748B;
                font-size: 0.7rem;
                font-weight: 900;
                text-transform: uppercase;
                letter-spacing: 0.12em;
                margin-bottom: 0.25rem;
            }

            .month-pill {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: fit-content;
                min-width: 7.6rem;
                padding: 0.48rem 0.85rem;
                border-radius: 999px;
                background: linear-gradient(135deg, #0B2D5C 0%, #123C7A 100%);
                color: #FFFFFF;
                font-size: 0.92rem;
                font-weight: 800;
                box-shadow: 0 8px 18px rgba(11, 45, 92, 0.16);
            }

            .campaign-name {
                color: #0B2D5C;
                font-size: 0.98rem;
                font-weight: 800;
                line-height: 1.35;
            }

            .plan-badge {
                display: inline-flex;
                align-items: center;
                width: fit-content;
                padding: 0.42rem 0.78rem;
                border-radius: 999px;
                font-size: 0.8rem;
                font-weight: 800;
                border: 1px solid transparent;
                box-shadow: 0 6px 14px rgba(15, 23, 42, 0.04);
                line-height: 1.15;
            }

            .plan-badge.high {
                background: #FEE2E2;
                color: #991B1B;
                border-color: #FCA5A5;
            }

            .plan-badge.medium {
                background: #FEF3C7;
                color: #92400E;
                border-color: #FDE68A;
            }

            .plan-badge.routine {
                background: #D1FAE5;
                color: #065F46;
                border-color: #A7F3D0;
            }

            .plan-badge.active {
                background: #FFF5F5;
                color: #C53030;
                border-color: #FEB2B2;
            }

            .plan-badge.preparation {
                background: #FFFDF5;
                color: #975A16;
                border-color: #FDE047;
            }

            .plan-badge.peak {
                background: #EEF2FF;
                color: #3730A3;
                border-color: #C7D2FE;
            }

            .plan-badge.followup {
                background: #F0FDF4;
                color: #166534;
                border-color: #BBF7D0;
            }

            .plan-badge.neutral {
                background: #F1F5F9;
                color: #334155;
                border-color: #CBD5E1;
            }

            .action-text {
                color: #334155;
                font-size: 0.9rem;
                line-height: 1.45;
                font-weight: 600;
            }

            .plan-empty-state {
                padding: 1rem 0.95rem;
                border-radius: 18px;
                background: #F8FAFC;
                border: 1px dashed #CBD5E1;
                color: #475569;
                font-weight: 600;
            }

            @media (max-width: 960px) {
                .plan-head {
                    display: none;
                }

                .plan-row {
                    grid-template-columns: 1fr;
                    gap: 0.45rem;
                }

                .plan-cell[data-label]::before {
                    display: block;
                }

                .plan-cell {
                    padding-bottom: 0.28rem;
                    border-bottom: 1px solid #EEF2F7;
                }

                .plan-cell:last-child {
                    border-bottom: none;
                    padding-bottom: 0;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="annual-plan-shell">', unsafe_allow_html=True)
    st.markdown(f'<div class="annual-plan-title">{escape(title)}</div>', unsafe_allow_html=True)

    if plan_df is None or plan_df.empty:
        st.markdown(f'<div class="plan-empty-state">{escape(empty_state)}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    rows_html = _render_rows(plan_df)

    st.markdown(
        f'''
        <div class="annual-plan-scroll">
            <div class="plan-head">
                <div>{escape(t("table_month"))}</div>
                <div>{escape(t("table_campaign"))}</div>
                <div>{escape(t("table_priority"))}</div>
                <div>{escape(t("table_status"))}</div>
                <div>{escape(t("table_officer_action"))}</div>
            </div>
            {rows_html}
        </div>
        ''',
        unsafe_allow_html=True,
    )

    st.markdown('</div>', unsafe_allow_html=True)
