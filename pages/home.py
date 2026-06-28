import streamlit as st


def render_home():
    # Hero
    st.markdown("""
    <div class="hero">
        <div style="display:inline-block;background:rgba(230,57,70,0.1);border:1px solid rgba(230,57,70,0.3);
             color:#E63946;padding:0.3rem 1rem;border-radius:20px;font-size:0.85rem;font-weight:600;margin-bottom:1.5rem;">
            🚗 AI-Powered Automotive Recruitment
        </div>
        <h1>Find Your Dream Career<br><span>in the Automotive Industry</span></h1>
        <p>DriveIQ connects top automotive talent with the world's most innovative companies.
           Our AI-native platform handles everything — from resume screening to intelligent interviews.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🚀 Explore Careers", key="home_careers"):
            st.session_state.page = "careers"
            st.rerun()
    with col2:
        if st.button("📄 Apply Now", key="home_apply"):
            st.session_state.page = "apply"
            st.rerun()
    with col3:
        if st.button("🏢 About DriveIQ", key="home_about"):
            st.session_state.page = "about"
            st.rerun()

    # Stats
    st.markdown("""
    <div class="stats-bar">
        <div class="stat-item"><div class="stat-number">320+</div><div class="stat-label">Partner Companies</div></div>
        <div class="stat-item"><div class="stat-number">42</div><div class="stat-label">Countries</div></div>
        <div class="stat-item"><div class="stat-number">48K+</div><div class="stat-label">Placements</div></div>
        <div class="stat-item"><div class="stat-number">$2.4B</div><div class="stat-label">Valuation</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Features
    st.markdown('<div class="section-title">Why DriveIQ?</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">The only platform built exclusively for the automotive industry</div>', unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)
    features = [
        ("🤖", "ARIA Interview Engine", "Adaptive AI questions that evolve based on your answers, role, and experience level."),
        ("📄", "Smart Resume Screening", "Claude-powered NLP extracts skills, detects inconsistencies, and scores job fit in seconds."),
        ("📊", "Instant Report Card", "Get a detailed 5-dimension breakdown with scores, verdict, and personalized feedback."),
    ]
    for col, (icon, title, desc) in zip([f1, f2, f3], features):
        with col:
            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <div style="font-size:2.5rem;margin-bottom:1rem;">{icon}</div>
                <div style="font-size:1.05rem;font-weight:700;color:#fff;margin-bottom:0.5rem;">{title}</div>
                <div style="font-size:0.9rem;color:#888;line-height:1.6;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Roles preview
    st.markdown('<div class="section-title">Hot Roles Right Now</div>', unsafe_allow_html=True)
    roles = [
        ("⚡", "EV Battery Engineer", "Tesla · Austin, TX", "$140K–$180K"),
        ("🚗", "Autonomous Systems Lead", "Waymo · Mountain View", "$180K–$240K"),
        ("🔧", "ADAS Software Engineer", "BMW · Munich", "€90K–€130K"),
        ("📡", "Connected Car Architect", "Ford · Dearborn", "$130K–$165K"),
    ]
    r1, r2 = st.columns(2)
    for i, (icon, title, company, salary) in enumerate(roles):
        with (r1 if i % 2 == 0 else r2):
            st.markdown(f"""
            <div class="job-card">
                <div style="display:flex;align-items:center;gap:0.8rem;">
                    <span style="font-size:1.8rem;">{icon}</span>
                    <div>
                        <div class="job-title">{title}</div>
                        <div class="job-meta">{company}</div>
                        <span class="job-tag">{salary}</span>
                        <span class="job-tag">Full-time</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🎯 Start Your Interview Now", key="home_interview"):
            st.session_state.page = "apply"
            st.rerun()
