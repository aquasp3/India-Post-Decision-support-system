from typing import Final, Dict, List
from utils import theme

APP_NAME: Final = "India Post DSS"
APP_SUBTITLE: Final = "Village Intelligence Platform"

SUPPORTED_LANGUAGES: Final[List[tuple]] = [
    ("en", "English"),
    ("hi", "Hindi"),
    ("ta", "Tamil"),
    ("te", "Telugu"),
    ("kn", "Kannada"),
]
DEFAULT_LANGUAGE: Final = "en"

THEME_COLORS: Final[Dict[str, str]] = {
    "PRIMARY_COLOR": theme.PRIMARY_COLOR,
    "SECONDARY_COLOR": theme.SECONDARY_COLOR,
    "ACCENT_COLOR": theme.ACCENT_COLOR,
    "BACKGROUND_COLOR": theme.BACKGROUND_COLOR,
    "CARD_COLOR": theme.CARD_COLOR,
    "TEXT_COLOR": theme.TEXT_COLOR,
    "BORDER_COLOR": theme.BORDER_COLOR,
}

PAGE_NAMES: Final[Dict[str, str]] = {
    "dashboard": "1_Dashboard",
    "upload": "2_Upload_Village_Data",
    "catalog": "3_Scheme_Catalog",
    "planning": "4_Planning_Recommendations",
    "about": "5_About",
}

# Risk and fallback constants
DEFAULT_FLOOD_RISK: Final = "Unknown"
DEFAULT_DROUGHT_RISK: Final = "Unknown"
DEFAULT_RISK_SCORE: Final = "Medium"
UNKNOWN_VALUE: Final = "Unknown"
RISK_HIGH: Final = "High"
RISK_MEDIUM: Final = "Medium"
RISK_LOW: Final = "Low"

# Recommendation engine weights (adjustable)
BASE_RECOMMENDATION_SCORE: Final = 50.0

# Priority weights
HIGH_PRIORITY_WEIGHT: Final = 10.0
MEDIUM_PRIORITY_WEIGHT: Final = 5.0
LOW_PRIORITY_WEIGHT: Final = 0.0

# Demographic influence weights (high/medium thresholds handled in engine)
FARMER_WEIGHT_HIGH: Final = 30.0
FARMER_WEIGHT_MED: Final = 15.0

WOMEN_WEIGHT_HIGH: Final = 25.0
WOMEN_WEIGHT_MED: Final = 10.0

CHILDREN_WEIGHT_HIGH: Final = 20.0
CHILDREN_WEIGHT_MED: Final = 8.0

SENIOR_WEIGHT: Final = 18.0

# Environmental risk weights
DROUGHT_WEIGHT: Final = 20.0
FLOOD_WEIGHT: Final = 20.0

# Misc
TARGET_NAME_MATCH_WEIGHT: Final = 5.0

# Planning generator rules
OUTREACH_MONTHS: Final = (
    "month_jan",
    "month_feb",
    "month_mar",
    "month_apr",
    "month_may",
    "month_jun",
    "month_jul",
    "month_aug",
    "month_sep",
    "month_oct",
    "month_nov",
    "month_dec",
)

SEASONAL_CAMPAIGNS: Final = {
    "farmer": ("month_mar", "month_apr", "month_may", "month_jun", "month_jul", "month_aug", "month_sep"),
    "women": ("month_jan", "month_feb", "month_mar", "month_aug", "month_sep", "month_oct", "month_nov"),
    "children": ("month_jun", "month_jul", "month_aug", "month_sep", "month_oct", "month_nov"),
    "senior": ("month_jan", "month_feb", "month_oct", "month_nov", "month_dec"),
    "insurance": ("month_jun", "month_jul", "month_aug", "month_sep", "month_oct"),
}

CAMPAIGN_WINDOWS: Final = {
    "farmer": "season_monsoon",
    "women": "season_year_round",
    "children": "season_school_term",
    "senior": "season_year_round",
    "insurance": "season_risk_response",
    "default": "season_year_round",
}

PRIORITY_CAMPAIGN_FREQUENCY: Final = {
    "high": 8.0,
    "medium": 4.0,
    "low": 0.0,
    "window_match_bonus": 15.0,
    "repeat_scheme_penalty": 25.0,
    "rotation_penalty": 0.1,
}
