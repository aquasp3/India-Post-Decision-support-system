import streamlit as st
from services import localization

t = localization.t

def render_suggested_actions(actions) -> None:
    """Renders high-impact administrative field checklists with no programmatic metrics."""
    with st.container(border=True):
        st.markdown(f"<h3 style='margin:0 0 16px 0;color:#0B5CAD;font-size:1.3rem;'>📋 Officer Field Action Checklist</h3>", unsafe_allow_html=True)

        if not actions:
            st.info("No tactical pending checklists mapped for the current selection framework criteria.")
            return

        st.markdown(
            "<p style='color:#64748B; font-size:0.9rem; margin-top:-0.5rem; margin-bottom:1.25rem;'>"
            "Mandatory actions for regional officers during campaign windows.</p>", 
            unsafe_allow_html=True
        )

        for i, action in enumerate(actions):
            # Streamlit interactive native session-saved checkbox widgets 
            st.checkbox(action, key=st.session_state.setdefault(f"chk_act_{i}", False))