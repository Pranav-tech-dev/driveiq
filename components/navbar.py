import streamlit as st


def render_navbar():
    cols = st.columns([1, 4, 1])
    with cols[0]:
        st.markdown('<div class="navbar-logo">Drive<span>IQ</span></div>', unsafe_allow_html=True)
    with cols[1]:
        # About page removed
        pages = [
            ("🏠 Home", "home"),
            ("💼 Careers", "careers"),
            ("📄 Apply", "apply"),
            ("🎤 Interview", "interview"),
            ("📊 Report", "report"),
        ]
        nav_cols = st.columns(len(pages))
        for i, (label, page_key) in enumerate(pages):
            with nav_cols[i]:
                if st.button(label, key=f"nav_{page_key}"):
                    st.session_state.page = page_key
                    st.rerun()
    st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:0'>", unsafe_allow_html=True)
