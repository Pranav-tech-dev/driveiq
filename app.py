import streamlit as st
from db import init_db

st.set_page_config(
    page_title="DriveIQ – Automotive Careers",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

init_db()

try:
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

defaults = {
    "page": "home",
    "interview_started": False,
    "messages": [],
    "applicant_data": {},
    "interview_score": None,
    "resume_analyzed": False,
    "apply_step": 1,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

from components.navbar import render_navbar
render_navbar()

page = st.session_state.page

if page == "home":
    from pages.home import render_home
    render_home()
elif page == "careers":
    from pages.careers import render_careers
    render_careers()
elif page == "apply":
    from pages.apply import render_apply
    render_apply()
elif page == "interview":
    from pages.interview import render_interview
    render_interview()
elif page == "report":
    from pages.report import render_report
    render_report()
