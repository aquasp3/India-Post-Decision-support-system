import streamlit as st
from pathlib import Path
from config import app_config
from services import localization
from utils import session_manager

# 1. Set global page configuration framework layout (MUST be executed first)
st.set_page_config(
    page_title="India Post DSS",
    layout="wide",
)

# 2. Synchronize Session & Localization context states
session_manager.initialize_session()
current_code = session_manager.get_language() or "en"
localization.set_language(current_code)

# 3. Formulate the declarative app routing objects pointing to your actual file names
dashboard_page = st.Page("pages/1_Dashboard.py", title=localization.t('dashboard'), icon="📊", default=True)
upload_page = st.Page("pages/2_Upload_Village_Data.py", title=localization.t('upload_village_data'), icon="📤")
catalog_page = st.Page("pages/3_Scheme_Catalog.py", title=localization.t('scheme_catalog'), icon="📚")

# FIXED: Pointed back to your exact file path name on disk
planning_page = st.Page("pages/4_Planning_Recommendations.py", title=localization.t('planning_recommendations'), icon="🗓️")
about_page = st.Page("pages/5_About.py", title=localization.t('about'), icon="ℹ️")

# 4. Bind pages together and completely suppress native automated layouts
pg = st.navigation(
    [dashboard_page, upload_page, catalog_page, planning_page, about_page], 
    position="hidden"
)

# 5. Render your uniform single Sidebar Layout Frame
ASSETS_DIR = Path(__file__).parent / "assets"
LOGO_PATH = ASSETS_DIR / "logo.png"

with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=138)
        
    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 1rem;">
            <h2 style="color: #0B2E63; margin: 0; font-size: 1.4rem;">{localization.t("app_name")}</h2>
            <p style="color: #64748B; margin: 0.2rem 0 0 0; font-size: 0.85rem;">{localization.t("app_subtitle")}</p>
            <hr style="border: none; border-top: 1px solid #DDE3EC; margin: 1rem 0;"/>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Render navigation elements using declarative Page objects
    st.page_link(dashboard_page, label=localization.t('dashboard'), icon="📊", width="stretch")
    st.page_link(upload_page, label=localization.t('upload_village_data'), icon="📤", width="stretch")
    st.page_link(catalog_page, label=localization.t('scheme_catalog'), icon="📚", width="stretch")
    st.page_link(planning_page, label=localization.t('planning_recommendations'), icon="🗓️", width="stretch")
    st.page_link(about_page, label=localization.t('about'), icon="ℹ️", width="stretch")
    
    # Language Selector Placement Frame Block
    st.markdown(
        f"""
        <div style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #DDE3EC;">
            <p style="margin: 0 0 0.5rem 0; font-size: 0.85rem; font-weight: 600; color: #475569;">
                🌐 {localization.t("label_select_language")}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    languages = app_config.SUPPORTED_LANGUAGES
    labels = [label for _, label in languages]
    code_to_index = {code: index for index, (code, _) in enumerate(languages)}
    selected_index = code_to_index.get(current_code, 0)
    
    choice = st.selectbox(
        label="Language Selector Matrix",
        options=labels,
        index=selected_index,
        key="global_sidebar_language_selector",
        label_visibility="collapsed"
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

# 6. Execute core operational commands for whichever page is active
pg.run()