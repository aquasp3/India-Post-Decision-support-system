import json
from pathlib import Path
from typing import Dict, Any

import streamlit as st

_LOCALE_DIR = Path(__file__).parent.parent / "locale"
_current_lang: str = "en"


@st.cache_data(show_spinner=False)
def _load_translations_from_disk(language_code: str, mtime_ns: int) -> Dict[str, str]:
    path = _LOCALE_DIR / f"{language_code}.json"
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            return {k: str(v) for k, v in data.items()}
    except Exception:
        return {}


def load_translations(language_code: str) -> Dict[str, str]:
    """Load translations for a language code from the locale folder."""
    path = _LOCALE_DIR / f"{language_code}.json"
    mtime_ns = path.stat().st_mtime_ns if path.exists() else -1
    return _load_translations_from_disk(language_code, mtime_ns)


def set_language(language_code: str) -> None:
    """Set active language for the application and persist to session state."""
    global _current_lang
    _current_lang = language_code
    st.session_state["language"] = language_code
    load_translations(language_code)


def get_language() -> str:
    return st.session_state.get("language", _current_lang) or _current_lang


def t(key: str) -> str:
    """Translate a key using the current language with fallbacks."""
    lang = get_language()
    sel = load_translations(lang)
    if key in sel and sel[key]:
        return sel[key]

    # Replaced redundant file processing checks with a localized optimization check loop
    if lang != "en":
        en = load_translations("en")
        if key in en and en[key]:
            return en[key]

    return key