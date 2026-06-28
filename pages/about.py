import streamlit as st


def render_about():
    st.markdown("""
    <div style="padding:3rem 0 1rem;">
        <div style="font-size:0.85rem;color:#E63946;font-weight:600;text-transform:uppercase;letter-spacing:1px;margin-bottom:0.5rem;">Our Story</div>
        <div style="font-size:2.5rem;font-weight:800;color:#fff;line-height:1.2;margin-bottom:1rem;">
            Reimagining Automotive<br>Talent Acquisition
        </div>
        <div style="font-size:1.05rem;color:#aaa;max-width:640px;line-height:1.8;">
            Founded in 2019 in San Jose, DriveIQ was built to solve a fundamental gap:
            the automotive industry's most innovative roles required specialized assessment
            that generic hiring platforms simply couldn't provide.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Mission cards
    m1, m2, m3 = st.columns(3)
    missions = [
        ("🎯", "Our Mission", "Democratize access to high-impact automotive careers through AI-powered, bias-free assessment."),
        ("👁️", "Our Vision", "A world where the best automotive talent finds the best opportunities — regardless of geography or background."),
        ("⚖️", "Our Values", "Transparency, fairness, and candidate-first thinking in every product decision we make."),
    ]
    for col, (icon, title, desc) in zip([m1, m2, m3], missions):
        with col:
            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <div style="font-size:2rem;margin-bottom:0.8rem;">{icon}</div>
                <div style="font-size:1rem;font-weight:700;color:#E63946;margin-bottom:0.5rem;">{title}</div>
                <div style="font-size:0.9rem;color:#aaa;line-height:1.6;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Timeline
    st.markdown('<div class="section-title">Our Journey</div>', unsafe_allow_html=True)
    timeline = [
        ("2019", "🚀", "Founded in San Jose with a vision to transform automotive hiring"),
        ("2020", "🤖", "Launched ARIA — the world's first automotive-specific AI interview engine"),
        ("2021", "🌍", "Expanded to 15 countries; reached 5,000 successful placements"),
        ("2022", "📈", "Series B — $180M raised; partnerships with 100+ OEMs and Tier-1 suppliers"),
        ("2023", "🏆", "Named Top HR Tech Company by Forbes; 30,000+ placements milestone"),
        ("2024", "💎", "Series D — $2.4B valuation; 42 countries, 320+ company partners"),
    ]
    for year, icon, event in timeline:
        st.markdown(f"""
        <div style="display:flex;align-items:flex-start;gap:1.5rem;margin-bottom:1.2rem;padding:1rem;
             background:#1A1A1A;border-radius:12px;border-left:3px solid #E63946;">
            <div style="min-width:60px;font-size:0.85rem;font-weight:700;color:#E63946;margin-top:0.2rem;">{year}</div>
            <div style="font-size:1.4rem;">{icon}</div>
            <div style="color:#ccc;font-size:0.95rem;line-height:1.5;">{event}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Team — UPDATED NAMES
    st.markdown('<div class="section-title">Team Behind DriveIQ</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">The people driving our mission forward</div>', unsafe_allow_html=True)

    team = [
        ("SB", "Sushant Umakant Birajdar", "Co-Founder & CEO"),
        ("JR", "Jandhavi Ramakant", "Co-Founder & CTO"),
        ("SD", "Samarth Dulange", "Chief People Officer"),
        ("SC", "Saniya Chavan", "Chief Product Officer"),
        ("SK", "Sakshi Karande", "Human Resources"),
    ]

    # Show 3 then 2
    row1 = st.columns(3)
    row2 = st.columns(2)
    cols = list(row1) + list(row2)

    for col, (initials, name, role) in zip(cols, team):
        with col:
            st.markdown(f"""
            <div class="team-card">
                <div class="team-avatar">{initials}</div>
                <div class="team-name">{name}</div>
                <div class="team-role">{role}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Ethics
    st.markdown('<div class="section-title">Ethical AI Framework</div>', unsafe_allow_html=True)
    e1, e2, e3 = st.columns(3)
    ethics = [
        ("🚫", "Zero Demographic Bias", "No gender, ethnicity, age, or accent data influences scoring. Certified by Stanford HAI."),
        ("🔍", "Transparent Scoring", "Every score is explainable and reviewable. Candidates see exactly how they were assessed."),
        ("🔒", "Candidate Privacy", "Video feeds are processed in-browser. No video footage is stored on our servers."),
    ]
    for col, (icon, title, desc) in zip([e1, e2, e3], ethics):
        with col:
            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <div style="font-size:2rem;margin-bottom:0.8rem;">{icon}</div>
                <div style="font-size:1rem;font-weight:700;color:#fff;margin-bottom:0.5rem;">{title}</div>
                <div style="font-size:0.88rem;color:#888;line-height:1.6;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
