from typing import Optional

import pandas as pd
import streamlit as st

from services.village_profile_engine import VillageProfileEngine
from services import localization
from utils import session_manager


t = localization.t


def render_village_selector() -> Optional[str]:
    """Render a searchable village selector and persist selection in session state.

    Returns the selected village name or None.
    """
    demographics = st.session_state.get("uploaded_demographics")
    placeholder = t("upload_demographics_data_first")

    if not isinstance(demographics, pd.DataFrame) or demographics.empty:
        st.selectbox(t("select_village"), [placeholder], index=0, disabled=True)
        if session_manager.get_active_village() is not None:
            session_manager.set_active_village(None)
            st.session_state["selected_village_profile"] = None
        return None

    if "village_name" in demographics.columns:
        villages = demographics["village_name"].astype(str).dropna().unique().tolist()
    elif "village" in demographics.columns:
        villages = demographics["village"].astype(str).dropna().unique().tolist()
    else:
        villages = []

    options = [placeholder] + villages

    current = session_manager.get_active_village()
    try:
        index = options.index(current) if current in options else 0
    except Exception:
        index = 0

    selected = st.selectbox(t("select_village"), options, index=index)

    if selected != placeholder:
        if selected != current:
            session_manager.set_active_village(selected)
            try:
                engine = VillageProfileEngine()
                profile = engine.get_village_profile(selected)
                st.session_state["selected_village_profile"] = profile
            except Exception:
                st.session_state["selected_village_profile"] = None
            st.rerun()
        return selected

    if current is not None:
        session_manager.set_active_village(None)
        st.session_state["selected_village_profile"] = None
        st.rerun()
    return None