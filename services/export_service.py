from __future__ import annotations

import csv
import os
import re
from datetime import datetime
from io import BytesIO, StringIO
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, Frame, LongTable, PageBreak, PageTemplate
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

from services import localization


def _t(key: str) -> str:
    return localization.t(key)


def _normalize_text(value: Any) -> str:
    return str(value or "").strip().lower()


def _title_case(text: str) -> str:
    cleaned = str(text or "").strip()
    if not cleaned:
        return ""
    return cleaned[0].upper() + cleaned[1:]


def _strip_emoji(text: str) -> str:
    return re.sub(r"[⭐🔴🟡🟢]", "", str(text or "")).strip()


def normalize_campaign_name(raw_name: Any) -> str:
    name_clean = _normalize_text(raw_name)
    if not name_clean:
        return _t("scheme_no_campaign")

    mapping = (
        (("mahila samman savings certificate", "mahila samman", "women savings campaign"), "campaign_women_savings_campaign"),
        (("sukanya samriddhi yojana", "sukanya samriddhi", "ssy", "girl child savings campaign"), "campaign_girl_child_savings_campaign"),
        (("senior citizens savings scheme", "senior citizen savings drive", "scss"), "campaign_senior_citizen_savings_drive"),
        (("rythu bandhu investment support", "rythu bandhu", "farmer outreach campaign", "farmer", "crop"), "campaign_farmer_outreach_campaign"),
        (("pmjjby", "life insurance"), "campaign_life_insurance_campaign"),
        (("pmsby", "accident insurance"), "campaign_accident_insurance_campaign"),
        (("apy", "pension plan"), "campaign_pension_plan_campaign"),
    )

    for tokens, key in mapping:
        if any(token in name_clean for token in tokens):
            return _t(key)

    if "no active campaign" in name_clean or "no campaign" in name_clean:
        return _t("scheme_no_campaign")

    return _title_case(str(raw_name).strip())


def normalize_priority(raw_priority: Any) -> str:
    value = _normalize_text(raw_priority)
    priority_high = _normalize_text(_strip_emoji(_t("priority_high")))
    priority_medium = _normalize_text(_strip_emoji(_t("priority_medium")))
    priority_routine = _normalize_text(_strip_emoji(_t("priority_routine")))
    priority_peak = _normalize_text(_strip_emoji(_t("priority_peak_campaign")))

    numeric_value: Optional[float]
    try:
        numeric_value = float(value)
    except Exception:
        numeric_value = None

    if any(token and token in value for token in ("high", "peak", "urgent", "critical")):
        return _t("priority_high")
    if priority_peak and priority_peak in value:
        return _t("priority_high")
    if any(token and token in value for token in (priority_high, "🔴")):
        return _t("priority_high")
    if numeric_value is not None and numeric_value >= 3.0:
        return _t("priority_high")

    if any(token and token in value for token in ("medium", priority_medium, "🟡")):
        return _t("priority_medium")
    if numeric_value is not None and numeric_value >= 1.5:
        return _t("priority_medium")

    if any(token and token in value for token in ("routine", priority_routine, "🟢")):
        return _t("priority_routine")

    return _t("priority_routine")


def normalize_stage(raw_stage: Any) -> str:
    value = _normalize_text(raw_stage)
    localized_prepare = _normalize_text(_strip_emoji(_t("status_preparation")))
    localized_active = _normalize_text(_strip_emoji(_t("status_active")))
    localized_peak = _normalize_text(_strip_emoji(_t("status_peak")))
    localized_follow = _normalize_text(_strip_emoji(_t("status_followup")))

    if any(token and token in value for token in ("preparation", "prepare", localized_prepare)):
        return _t("stage_prepare")
    if any(token and token in value for token in ("active now", "active", localized_active)):
        return _t("stage_active")
    if any(token and token in value for token in ("peak campaign", "peak", localized_peak)):
        return _t("stage_peak")
    if any(token and token in value for token in ("follow-up required", "follow up", "followup", localized_follow)):
        return _t("stage_follow_up")

    return _title_case(str(raw_stage).strip())


def normalize_action(raw_action: Any, campaign_name: Any = "", stage: Any = "") -> str:
    action_value = _normalize_text(raw_action)
    campaign_value = _normalize_text(campaign_name)
    stage_value = _normalize_text(stage)
    stage_prepare = _normalize_text(_strip_emoji(_t("status_preparation")))
    stage_active = _normalize_text(_strip_emoji(_t("status_active")))
    stage_peak = _normalize_text(_strip_emoji(_t("status_peak")))
    stage_follow = _normalize_text(_strip_emoji(_t("status_followup")))

    if any(token in action_value for token in ("document verification", "verify documents", "verification")):
        return _t("action_document_verification")
    if any(token in action_value for token in ("school", "teacher", "student", "brochure")):
        return _t("action_school_outreach")
    if any(token in action_value for token in ("shg", "awareness meeting", "awareness meetings", "women")):
        return _t("action_shg_awareness_meeting")
    if any(token in action_value for token in ("enrollment camp", "enrollment", "registration camp", "camp")):
        return _t("action_enrollment_camp")
    if any(token in action_value for token in ("panchayat", "coordination")):
        return _t("action_panchayat_coordination")
    if any(token in action_value for token in ("farmer", "agri", "crop")):
        return _t("action_farmer_outreach")

    if any(token in stage_value for token in ("follow", "follow up", stage_follow)):
        return _t("action_document_verification")
    if any(token in stage_value for token in ("prepare", "preparation", stage_prepare)):
        return _t("action_panchayat_coordination")

    if any(token in campaign_value for token in ("women", "mahila")):
        if any(token in stage_value for token in ("active", "peak", stage_active, stage_peak)):
            return _t("action_shg_awareness_meeting")
        return _t("action_panchayat_coordination")
    if any(token in campaign_value for token in ("girl child", "sukanya", "child")):
        if any(token in stage_value for token in ("active", "peak", stage_active, stage_peak)):
            return _t("action_school_outreach")
        return _t("action_enrollment_camp")
    if any(token in campaign_value for token in ("senior", "elder")):
        if any(token in stage_value for token in ("active", "peak", stage_active, stage_peak)):
            return _t("action_enrollment_camp")
        return _t("action_document_verification")
    if any(token in campaign_value for token in ("farmer", "rythu", "crop", "agri")):
        return _t("action_farmer_outreach")

    return _t("action_panchayat_coordination")


class ExportService:
    """Create official-style CSV, PDF, government report, and print-view outputs."""

    def __init__(self) -> None:
        self.t = localization.t
        self.body_font = "Helvetica"
        self.bold_font = "Helvetica-Bold"
        self._register_fonts()

    def build_csv_export(
        self,
        profile: Dict[str, Any],
        recommendations: Any,
        monthly_plan: Any,
        suggested_actions: Iterable[str],
    ) -> bytes:
        """Build a compact CSV export for operational circulation."""
        _ = recommendations
        _ = suggested_actions

        output = StringIO()
        writer = csv.writer(output)

        rows = self._build_csv_rows(profile, monthly_plan)
        writer.writerow([
            self.t("csv_column_village"),
            self.t("csv_column_month"),
            self.t("csv_column_campaign"),
            self.t("csv_column_priority"),
            self.t("csv_column_stage"),
            self.t("csv_column_next_action"),
            self.t("csv_column_focus_group"),
        ])
        for row in rows:
            writer.writerow(row)

        return output.getvalue().encode("utf-8")

    def build_pdf_report(
        self,
        profile: Dict[str, Any],
        recommendations: Any,
        monthly_plan: Any,
        suggested_actions: Iterable[str],
        officer_insights: Optional[Iterable[str]] = None,
        government_report: bool = False,
    ) -> bytes:
        """Build a professional PDF report using a print-friendly government layout."""
        buffer = BytesIO()
        doc = self._build_pdf_document(buffer, government_report=government_report)

        story = self._build_pdf_story(
            profile=profile,
            recommendations=recommendations,
            monthly_plan=monthly_plan,
            suggested_actions=suggested_actions,
            officer_insights=officer_insights,
            government_report=government_report,
        )
        doc.build(story)
        return buffer.getvalue()

    def build_print_view_html(
        self,
        profile: Dict[str, Any],
        recommendations: Any,
        monthly_plan: Any,
        suggested_actions: Iterable[str],
        officer_insights: Optional[Iterable[str]] = None,
    ) -> str:
        """Build a clean print-friendly HTML report with the same structure as the PDF report."""
        overview_rows = self._build_village_overview_rows(profile)
        plan_rows = self._build_plan_rows(monthly_plan)
        recommendation_rows = self._build_recommendation_rows(recommendations, plan_rows)
        checklist_items = self._checklist_items()

        return self._build_print_html(
            title=self.t("report_pdf_title"),
            subtitle=self.t("report_pdf_subtitle"),
            overview_rows=overview_rows,
            plan_rows=plan_rows,
            recommendation_rows=recommendation_rows,
            checklist_items=checklist_items,
            suggested_actions=suggested_actions,
            officer_insights=officer_insights,
            include_metadata=False,
        )

    def _build_pdf_document(self, buffer: BytesIO, government_report: bool) -> BaseDocTemplate:
        page_title = self.t("government_report_title") if government_report else self.t("report_pdf_title")
        page_subtitle = self.t("government_report_subtitle") if government_report else self.t("report_pdf_subtitle")
        doc = BaseDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=14 * mm,
            rightMargin=14 * mm,
            topMargin=32 * mm,
            bottomMargin=18 * mm,
        )
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="report_frame")
        doc.addPageTemplates(
            [
                PageTemplate(
                    id="report_pages",
                    frames=[frame],
                    onPage=lambda canvas, document: self._draw_page_chrome(canvas, document, page_title, page_subtitle),
                )
            ]
        )
        return doc

    def _build_pdf_story(
        self,
        profile: Dict[str, Any],
        recommendations: Any,
        monthly_plan: Any,
        suggested_actions: Iterable[str],
        officer_insights: Optional[Iterable[str]],
        government_report: bool,
    ) -> List[Any]:
        overview_rows = self._build_village_overview_rows(profile)
        plan_rows = self._build_plan_rows(monthly_plan)
        recommendation_rows = self._build_recommendation_rows(recommendations, plan_rows)
        checklist_items = self._checklist_items()
        generated_on = datetime.now().strftime("%d %b %Y")

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            fontName=self.bold_font,
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#111827"),
            alignment=1,
            spaceAfter=4,
        )
        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["BodyText"],
            fontName=self.body_font,
            fontSize=10.5,
            leading=13,
            textColor=colors.HexColor("#374151"),
            alignment=1,
            spaceAfter=8,
        )
        section_style = ParagraphStyle(
            "ReportSection",
            parent=styles["Heading2"],
            fontName=self.bold_font,
            fontSize=11.5,
            leading=14,
            textColor=colors.HexColor("#111827"),
            spaceBefore=8,
            spaceAfter=4,
        )
        body_style = ParagraphStyle(
            "ReportBody",
            parent=styles["BodyText"],
            fontName=self.body_font,
            fontSize=9.5,
            leading=12,
            textColor=colors.HexColor("#1F2937"),
        )

        if government_report:
            title = self.t("government_report_title")
            subtitle = self.t("government_report_subtitle")
            summary_heading = self.t("government_section_village_summary")
            recommendations_heading = self.t("government_section_campaign_recommendations")
            plan_heading = self.t("government_section_campaign_plan")
            checklist_heading = self.t("government_section_officer_action_checklist")
        else:
            title = self.t("report_pdf_title")
            subtitle = self.t("report_pdf_subtitle")
            summary_heading = self.t("report_section_village_overview")
            recommendations_heading = self.t("report_section_recommended_campaigns")
            plan_heading = self.t("report_section_campaign_plan")
            checklist_heading = self.t("report_section_officer_action_checklist")

        story: List[Any] = []
        story.append(Spacer(1, 2))
        story.append(Paragraph(title, title_style))
        story.append(Paragraph(subtitle, subtitle_style))
        story.append(Spacer(1, 4))

        story.append(Paragraph(summary_heading, section_style))
        story.extend(self._paragraph_table_story(overview_rows, [0.42, 0.58], body_style))

        story.append(Paragraph(plan_heading, section_style))
        story.extend(self._long_table_story(plan_rows, self._plan_table_columns(), [22 * mm, 43 * mm, 36 * mm, 24 * mm, 45 * mm], body_style))

        story.append(Paragraph(recommendations_heading, section_style))
        story.extend(self._long_table_story(recommendation_rows, self._recommendation_table_columns(), [42 * mm, 74 * mm, 54 * mm], body_style))

        story.append(Paragraph(checklist_heading, section_style))
        story.append(self._bullet_list_paragraph(checklist_items, body_style))

        if government_report:
            story.append(Spacer(1, 4))
            story.append(Paragraph(f"{self.t('report_label_prepared_by')}: {self.t('report_prepared_by_value')}", body_style))
            story.append(Paragraph(f"{self.t('report_label_generated_on')}: {generated_on}", body_style))

        return story

    def _build_print_html(
        self,
        title: str,
        subtitle: str,
        overview_rows: List[Tuple[str, str]],
        plan_rows: List[Dict[str, str]],
        recommendation_rows: List[Dict[str, str]],
        checklist_items: List[str],
        suggested_actions: Iterable[str],
        officer_insights: Optional[Iterable[str]],
        include_metadata: bool,
    ) -> str:
        del suggested_actions
        del officer_insights

        def render_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
            if not rows:
                return f"<p>{self.t('no_data_available')}</p>"
            table_rows = "".join(
                "<tr>" + "".join(f"<td>{self._escape_html(value)}</td>" for value in row) + "</tr>"
                for row in rows
            )
            header_html = "".join(f"<th>{self._escape_html(header)}</th>" for header in headers)
            return f"""
                <table>
                    <thead><tr>{header_html}</tr></thead>
                    <tbody>{table_rows}</tbody>
                </table>
            """

        overview_table = render_table(
            [self.t("report_label_item"), self.t("report_label_value")],
            overview_rows,
        )
        plan_table = render_table(
            [
                self.t("report_label_month"),
                self.t("report_label_campaign"),
                self.t("report_label_priority"),
                self.t("report_label_stage"),
                self.t("report_label_next_action"),
            ],
            [[row[col] for col in ("Month", "Campaign", "Priority", "Stage", "Next Action")] for row in plan_rows],
        )
        recommendation_table = render_table(
            [
                self.t("report_label_campaign"),
                self.t("report_label_reason"),
                self.t("report_label_recommended_action"),
            ],
            [[row[col] for col in ("Campaign", "Reason", "Recommended Action")] for row in recommendation_rows],
        )
        checklist_html = "".join(f"<li>{self._escape_html(item)}</li>" for item in checklist_items)

        metadata_html = ""
        if include_metadata:
            metadata_html = f"""
                <div class="section">
                    <h2>{self.t('government_section_metadata')}</h2>
                    <div class="meta-row"><span>{self.t('report_label_prepared_by')}</span><span>{self.t('report_prepared_by_value')}</span></div>
                    <div class="meta-row"><span>{self.t('report_label_generated_on')}</span><span>{self._escape_html(datetime.now().strftime('%d %b %Y'))}</span></div>
                </div>
            """

        return f"""
        <html>
        <head>
            <meta charset="utf-8" />
            <title>{self._escape_html(title)}</title>
            <style>
                @page {{ size: A4; margin: 16mm; }}
                body {{ font-family: Arial, sans-serif; color: #111827; margin: 0; padding: 0; background: #ffffff; }}
                .page {{ padding: 0; }}
                h1 {{ font-size: 20px; margin: 0; text-align: center; font-weight: 700; letter-spacing: 0.2px; }}
                h2 {{ font-size: 13px; margin: 0 0 8px 0; font-weight: 700; border-bottom: 1px solid #111827; padding-bottom: 4px; }}
                .subtitle {{ text-align: center; font-size: 11px; color: #374151; margin: 4px 0 12px 0; }}
                .section {{ margin-top: 14px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 6px; }}
                th, td {{ border: 1px solid #D1D5DB; padding: 7px 8px; text-align: left; vertical-align: top; font-size: 10.5px; }}
                th {{ background: #F3F4F6; font-weight: 700; }}
                ul {{ margin: 6px 0 0 18px; padding: 0; }}
                li {{ font-size: 10.5px; line-height: 1.5; margin-bottom: 3px; }}
                .meta-row {{ display: flex; justify-content: space-between; gap: 12px; padding: 4px 0; font-size: 10.5px; border-bottom: 1px solid #E5E7EB; }}
                .meta-row span:first-child {{ font-weight: 700; }}
                .no-data {{ font-size: 10.5px; color: #6B7280; }}
            </style>
        </head>
        <body>
            <div class="page">
                <h1>{self._escape_html(title)}</h1>
                <div class="subtitle">{self._escape_html(subtitle)}</div>

                <div class="section">
                    <h2>{self._escape_html(self.t('report_section_village_overview') if title == self.t('report_pdf_title') else self.t('government_section_village_summary'))}</h2>
                    {overview_table}
                </div>

                <div class="section">
                    <h2>{self._escape_html(self.t('report_section_campaign_plan') if title == self.t('report_pdf_title') else self.t('government_section_campaign_plan'))}</h2>
                    {plan_table}
                </div>

                <div class="section">
                    <h2>{self._escape_html(self.t('report_section_recommended_campaigns') if title == self.t('report_pdf_title') else self.t('government_section_campaign_recommendations'))}</h2>
                    {recommendation_table}
                </div>

                <div class="section">
                    <h2>{self._escape_html(self.t('report_section_officer_action_checklist') if title == self.t('report_pdf_title') else self.t('government_section_officer_action_checklist'))}</h2>
                    <ul>{checklist_html}</ul>
                </div>

                {metadata_html}
            </div>
        </body>
        </html>
        """

    def _build_csv_rows(self, profile: Dict[str, Any], monthly_plan: Any) -> List[List[str]]:
        village_name = self._clean_text(profile.get("village_name", ""))
        rows: List[List[str]] = []
        for record in self._plan_rows_from_any(monthly_plan):
            rows.append(
                [
                    village_name,
                    record["Month"],
                    record["Campaign"],
                    record["Priority"],
                    record["Stage"],
                    record["Next Action"],
                    record["Focus Group"],
                ]
            )
        return rows

    def _build_village_overview_rows(self, profile: Dict[str, Any]) -> List[Tuple[str, str]]:
        return [
            (self.t("report_label_population"), self._clean_text(profile.get("population", ""))),
            (self.t("report_label_men_pct"), self._format_percentage(self._profile_percentage(profile, ["men_ratio", "male_ratio"], ["men_count", "male_count"]))),
            (self.t("report_label_women_pct"), self._format_percentage(self._profile_percentage(profile, ["women_ratio", "female_ratio"], ["women_count", "female_count"]))),
            (self.t("report_label_children_pct"), self._format_percentage(self._profile_percentage(profile, ["children_ratio"], ["children_count"]))),
            (self.t("report_label_senior_citizens_pct"), self._format_percentage(self._profile_percentage(profile, ["seniors_ratio", "senior_ratio"], ["seniors_count", "senior_count"]))),
            (self.t("report_label_focus_group"), self._clean_text(profile.get("priority_segment", ""))),
            (self.t("report_label_suggested_campaign"), self._clean_text(profile.get("suggested_campaign_type", ""))),
        ]

    def _build_plan_rows(self, monthly_plan: Any) -> List[Dict[str, str]]:
        rows: List[Dict[str, str]] = []
        for record in self._plan_rows_from_any(monthly_plan):
            rows.append(record)
        return rows

    def _build_recommendation_rows(self, recommendations: Any, plan_rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
        recommendation_df = self._ensure_dataframe(recommendations)
        plan_lookup = {
            self._normalized_key(row["Campaign"]): row["Next Action"]
            for row in plan_rows
            if row.get("Campaign")
        }

        rows: List[Dict[str, str]] = []
        if recommendation_df.empty:
            return rows

        for _, row in recommendation_df.iterrows():
            campaign_raw = self._first_value(row, ["scheme_name", "campaign_name", "Campaign", "Scheme"])
            campaign = normalize_campaign_name(campaign_raw)
            reason = self._clean_text(self._first_value(row, ["reason", "why_recommended", "Recommendation Reason"]))
            recommended_action_raw = self._first_value(
                row,
                ["recommended_action", "officer_action", "action", "Next Action"],
                default=plan_lookup.get(self._normalized_key(campaign), ""),
            )
            recommended_action = normalize_action(
                recommended_action_raw,
                campaign_name=campaign_raw,
            )
            if not recommended_action:
                recommended_action = normalize_action(
                    plan_lookup.get(self._normalized_key(campaign), self.t("report_recommended_action_default")),
                    campaign_name=campaign_raw,
                )
            rows.append(
                {
                    "Campaign": campaign,
                    "Reason": reason,
                    "Recommended Action": recommended_action,
                }
            )
        return rows

    def _plan_rows_from_any(self, monthly_plan: Any) -> List[Dict[str, str]]:
        plan_df = self._ensure_dataframe(monthly_plan)
        if plan_df.empty:
            return []

        rows: List[Dict[str, str]] = []
        for _, row in plan_df.iterrows():
            campaign_raw = self._first_value(row, ["campaign_name", "Campaign", "Scheme", "scheme_name", "campaign"])
            stage_raw = self._first_value(row, ["stage", "Status", "Campaign Window", "status"])
            next_action_raw = self._first_value(row, ["next_action", "Next Action", "Officer_Action", "officer_action", "action"])
            campaign = normalize_campaign_name(campaign_raw)
            stage = normalize_stage(stage_raw)
            next_action = normalize_action(next_action_raw, campaign_name=campaign_raw, stage=stage_raw)
            focus_group = self._clean_text(self._first_value(row, ["focus_group", "Focus Group", "Target Group", "Target_Audience", "target_audience", "target_group"]))
            month = self._clean_text(self._first_value(row, ["month", "Month"]))
            priority = normalize_priority(self._first_value(row, ["priority", "Priority"]))
            rows.append(
                {
                    "Village": self._clean_text(self._first_value(row, ["village", "Village"], default="")),
                    "Month": month,
                    "Campaign": campaign,
                    "Priority": priority,
                    "Stage": stage,
                    "Next Action": next_action,
                    "Focus Group": focus_group,
                }
            )
        return rows

    def _plan_table_columns(self) -> List[str]:
        return [
            self.t("report_label_month"),
            self.t("report_label_campaign"),
            self.t("report_label_priority"),
            self.t("report_label_stage"),
            self.t("report_label_next_action"),
        ]

    def _recommendation_table_columns(self) -> List[str]:
        return [
            self.t("report_label_campaign"),
            self.t("report_label_reason"),
            self.t("report_label_recommended_action"),
        ]

    def _checklist_items(self) -> List[str]:
        return [
            self.t("report_checklist_identify_beneficiaries"),
            self.t("report_checklist_conduct_awareness_meetings"),
            self.t("report_checklist_organize_enrollment_camp"),
            self.t("report_checklist_verify_documents"),
            self.t("report_checklist_submit_report"),
        ]

    def _paragraph_table_story(self, rows: List[Tuple[str, str]], widths: List[float], body_style: ParagraphStyle) -> List[Any]:
        if not rows:
            return [Paragraph(self.t("no_data_available"), body_style)]

        table = Table([[left, right] for left, right in rows], colWidths=[w * 160 * mm for w in widths])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F3F4F6")),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#111827")),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D1D5DB")),
                    ("FONTNAME", (0, 0), (0, -1), self.bold_font),
                    ("FONTNAME", (1, 0), (1, -1), self.body_font),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEADING", (0, 0), (-1, -1), 12),
                ]
            )
        )
        return [table, Spacer(1, 4)]

    def _long_table_story(self, rows: List[Dict[str, str]], columns: List[str], widths: List[float], body_style: ParagraphStyle) -> List[Any]:
        if not rows:
            return [Paragraph(self.t("no_data_available"), body_style)]

        table_data: List[List[Any]] = [[Paragraph(self._escape_html(column), body_style) for column in columns]]
        for row in rows:
            table_data.append([self._table_cell(row.get(column, ""), body_style) for column in columns])

        table = LongTable(table_data, colWidths=widths, repeatRows=1, splitByRow=1)
        table.setStyle(self._report_table_style())
        return [table, Spacer(1, 4)]

    def _report_table_style(self) -> TableStyle:
        return TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E5E7EB")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D1D5DB")),
                ("FONTNAME", (0, 0), (-1, 0), self.bold_font),
                ("FONTNAME", (0, 1), (-1, -1), self.body_font),
                ("FONTSIZE", (0, 0), (-1, -1), 8.8),
                ("LEADING", (0, 0), (-1, -1), 11),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )

    def _table_cell(self, value: Any, body_style: ParagraphStyle) -> Paragraph:
        return Paragraph(self._escape_html(value), body_style)

    def _bullet_list_paragraph(self, items: List[str], body_style: ParagraphStyle) -> Any:
        if not items:
            return Paragraph(self.t("no_data_available"), body_style)
        bullets = "<br/>".join(f"- {self._escape_html(item)}" for item in items)
        return Paragraph(bullets, body_style)

    def _draw_page_chrome(self, canvas: Any, doc: BaseDocTemplate, title: str, subtitle: str) -> None:
        canvas.saveState()

        page_width, page_height = A4
        left_margin = doc.leftMargin
        right_margin = doc.rightMargin
        header_top = page_height - 12 * mm
        header_bottom = page_height - 24 * mm
        footer_top = 14 * mm

        canvas.setStrokeColor(colors.HexColor("#1F2937"))
        canvas.setLineWidth(0.8)
        canvas.line(left_margin, header_bottom, page_width - right_margin, header_bottom)
        canvas.line(left_margin, footer_top + 4 * mm, page_width - right_margin, footer_top + 4 * mm)

        canvas.setFont(self.bold_font, 13)
        canvas.setFillColor(colors.HexColor("#111827"))
        canvas.drawString(left_margin, header_top, title)

        canvas.setFont(self.body_font, 8.5)
        canvas.setFillColor(colors.HexColor("#4B5563"))
        canvas.drawString(left_margin, header_bottom + 3.5 * mm, subtitle)

        canvas.setFont(self.body_font, 8.5)
        canvas.setFillColor(colors.HexColor("#374151"))
        canvas.drawString(left_margin, footer_top, self.t("report_prepared_by_value"))
        canvas.drawRightString(page_width - right_margin, footer_top, f"Page {canvas.getPageNumber()}")

        canvas.restoreState()

    def _profile_percentage(
        self,
        profile: Dict[str, Any],
        ratio_keys: List[str],
        count_keys: List[str],
    ) -> Optional[float]:
        ratio_value = self._first_value(profile, ratio_keys)
        ratio_number = self._safe_float(ratio_value)
        if ratio_number is not None:
            if ratio_number <= 1:
                return ratio_number * 100.0
            return ratio_number

        count_value = self._first_value(profile, count_keys)
        count_number = self._safe_float(count_value)
        population = self._safe_float(profile.get("population"))
        if count_number is not None and population and population > 0:
            return (count_number / population) * 100.0
        return None

    def _format_percentage(self, value: Optional[float]) -> str:
        if value is None:
            return ""
        return f"{value:.1f}%"

    def _first_value(self, source: Any, keys: Sequence[str], default: str = "") -> str:
        for key in keys:
            value: Any = None
            if isinstance(source, dict):
                value = source.get(key)
            else:
                try:
                    value = source.get(key)
                except Exception:
                    value = None
            if value is not None and str(value).strip():
                return str(value)
        return default

    def _normalized_key(self, value: Any) -> str:
        return self._clean_text(value).lower()

    def _clean_text(self, value: Any) -> str:
        if value is None:
            return ""
        text = str(value).replace("\u200b", " ").strip()
        if not text:
            return ""
        text = re.sub(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", "", text)
        text = re.sub(r"[^\w\s.,/&()\-:%+;#]", "", text, flags=re.UNICODE)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _escape_html(self, value: Any) -> str:
        text = self._clean_text(value)
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )

    def _safe_float(self, value: Any) -> Optional[float]:
        try:
            if value in (None, ""):
                return None
            number = float(value)
            if pd.isna(number):
                return None
            return number
        except Exception:
            return None

    def _register_fonts(self) -> None:
        try:
            windows_fonts = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
            nirmala_font = windows_fonts / "Nirmala.ttc"
            regular_font = windows_fonts / "segoeui.ttf"
            bold_font = windows_fonts / "segoeuib.ttf"
            if nirmala_font.exists():
                pdfmetrics.registerFont(TTFont("NirmalaUI", str(nirmala_font), subfontIndex=0))
                self.body_font = "NirmalaUI"
                self.bold_font = "NirmalaUI"
            elif regular_font.exists():
                pdfmetrics.registerFont(TTFont("SegoeUI", str(regular_font)))
                self.body_font = "SegoeUI"
                self.bold_font = "SegoeUI"
            if bold_font.exists() and self.body_font == "SegoeUI":
                pdfmetrics.registerFont(TTFont("SegoeUI-Bold", str(bold_font)))
                self.bold_font = "SegoeUI-Bold"
        except Exception:
            self.body_font = "Helvetica"
            self.bold_font = "Helvetica-Bold"

    def _ensure_dataframe(self, value: Any) -> pd.DataFrame:
        if value is None:
            return pd.DataFrame()
        if isinstance(value, pd.DataFrame):
            return value.copy()
        if isinstance(value, list):
            return pd.DataFrame(value)
        try:
            return pd.DataFrame(value)
        except Exception:
            return pd.DataFrame()
