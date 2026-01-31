import sys
from pathlib import Path
import streamlit as st
from config import APP_TITLE

# Add project root to PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))


st.set_page_config(
    page_title=APP_TITLE,
    layout="wide",
)
# Force max width
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.title(APP_TITLE)
st.caption("Real NAVs • Risk-adjusted metrics • Explainable recommendations")

st.markdown(
    """
    👈 Use the sidebar to navigate:
    - **Funds Explorer**
    - **Fund Analytics**
    - **Compare Funds**
    - **Recommendations**
    """
)
