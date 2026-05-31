import streamlit as st
from typing import Optional


def initialize_session() -> None:
    """Ensure session state keys exist with sane defaults."""
    if "language" not in st.session_state:
        st.session_state["language"] = "en"
    if "active_village" not in st.session_state:
        st.session_state["active_village"] = None
    if "selected_village_profile" not in st.session_state:
        st.session_state["selected_village_profile"] = None
    if "uploaded_demographics" not in st.session_state:
        st.session_state["uploaded_demographics"] = None
    if "uploaded_environment" not in st.session_state:
        st.session_state["uploaded_environment"] = None
    if "recommendations" not in st.session_state:
        st.session_state["recommendations"] = None
    if "monthly_plan" not in st.session_state:
        st.session_state["monthly_plan"] = None


def set_language(lang: str) -> None:
    st.session_state["language"] = lang


def get_language() -> str:
    return st.session_state.get("language", "en")


def set_active_village(village_id: Optional[str]) -> None:
    st.session_state["active_village"] = village_id


def get_active_village() -> Optional[str]:
    return st.session_state.get("active_village")
