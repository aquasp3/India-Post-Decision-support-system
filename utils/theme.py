from typing import Final

PRIMARY_COLOR: Final = "#0B5CAD"
SECONDARY_COLOR: Final = "#2E7D32"
ACCENT_COLOR: Final = "#FF9933"
BACKGROUND_COLOR: Final = "#F8FAFC"
CARD_COLOR: Final = "#FFFFFF"
TEXT_COLOR: Final = "#1E293B"
BORDER_COLOR: Final = "#CBD5E1"

CSS = f"""
<style>
:root {{
  --primary: {PRIMARY_COLOR};
  --secondary: {SECONDARY_COLOR};
  --accent: {ACCENT_COLOR};
  --bg: {BACKGROUND_COLOR};
  --card: {CARD_COLOR};
  --text: {TEXT_COLOR};
  --border: {BORDER_COLOR};
}}

body {{ background-color: var(--bg); color: var(--text); }}

/* Sidebar */
.css-1d391kg {{ padding-top: 0.5rem; }}
.sidebar-title {{ font-weight: 700; font-size: 18px; color: var(--primary); }}
.sidebar-sub {{ color: var(--text); font-size: 12px; margin-bottom: 12px; }}

.page-header {{ margin: 8px 0 16px 0; }}

.hero {{ background: linear-gradient(90deg, rgba(11,92,173,0.08), rgba(255,153,51,0.04)); padding: 24px; border-radius: 6px; margin-bottom: 16px; }}
.hero h2 {{ color: var(--primary); margin: 0 0 8px 0; }}
.hero .lead {{ color: var(--text); margin-bottom: 8px; }}
.hero-actions .btn-primary {{ background-color: var(--primary); color: white; padding: 8px 16px; border-radius: 4px; border: none; cursor: pointer; }}

.features-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }}
.card {{ background: var(--card); padding: 16px; border-radius: 6px; border: 1px solid var(--border); box-shadow: 0 1px 2px rgba(0,0,0,0.04); }}

.grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
.upload-placeholder {{ border: 2px dashed var(--border); padding: 40px; text-align: center; color: var(--text); background: #fff; }}
.table-placeholder {{ min-height: 120px; background: #fff; border: 1px solid var(--border); padding: 12px; }}

.search-row {{ display: flex; gap: 8px; margin-bottom: 12px; }}
.search {{ flex: 1; padding: 8px; border: 1px solid var(--border); border-radius: 4px; }}
.filter {{ padding: 8px; border: 1px solid var(--border); border-radius: 4px; }}

.planning-grid {{ display: grid; grid-template-columns: 1fr 320px; gap: 12px; }}
.kpi-cards {{ display: flex; gap: 8px; margin-bottom: 12px; }}

.about {{ padding: 12px; background: var(--card); border-radius: 6px; }}

.spacer {{ height: 12px; }}

</style>
"""


def apply_theme() -> None:
    """Apply theme side-effects if needed (kept minimal for architecture)."""
    # Intentionally minimal: CSS is consumed by components which inject it into pages.
    return None
