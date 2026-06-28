import streamlit as st


JOBS = [
    {
        "icon": "⚡", "title": "EV Battery Systems Engineer",
        "company": "Tesla", "location": "Austin, TX", "type": "Full-time",
        "salary": "$140K–$180K", "level": "Senior",
        "tags": ["Battery Tech", "Python", "MATLAB"],
        "desc": "Design next-gen battery management systems for Tesla's Cybertruck and Model Y platforms.",
    },
    {
        "icon": "🚗", "title": "Autonomous Systems Tech Lead",
        "company": "Waymo", "location": "Mountain View, CA", "type": "Full-time",
        "salary": "$180K–$240K", "level": "Staff",
        "tags": ["LiDAR", "C++", "ROS2"],
        "desc": "Lead a team of 8 engineers building perception and planning modules for Waymo's robotaxi fleet.",
    },
    {
        "icon": "🔧", "title": "ADAS Software Engineer",
        "company": "BMW Group", "location": "Munich, Germany", "type": "Full-time",
        "salary": "€90K–€130K", "level": "Mid-Senior",
        "tags": ["Embedded C", "AUTOSAR", "MISRA"],
        "desc": "Develop and validate ADAS features including lane keep assist and adaptive cruise control.",
    },
    {
        "icon": "📡", "title": "Connected Car Cloud Architect",
        "company": "Ford Motor", "location": "Dearborn, MI", "type": "Hybrid",
        "salary": "$130K–$165K", "level": "Senior",
        "tags": ["AWS", "Kubernetes", "OTA"],
        "desc": "Architect the cloud backbone for Ford's BlueCruise connected vehicle ecosystem.",
    },
    {
        "icon": "🔋", "title": "Powertrain Systems Engineer",
        "company": "Rivian", "location": "Irvine, CA", "type": "Full-time",
        "salary": "$120K–$155K", "level": "Mid",
        "tags": ["Motor Control", "Simulink", "CAN Bus"],
        "desc": "Model and optimize powertrain control strategies for Rivian's R1T and R1S platforms.",
    },
    {
        "icon": "🤖", "title": "AI/ML Engineer – Robotics",
        "company": "Nuro", "location": "Mountain View, CA", "type": "Full-time",
        "salary": "$150K–$200K", "level": "Senior",
        "tags": ["PyTorch", "Computer Vision", "Reinforcement Learning"],
        "desc": "Build and deploy ML models for autonomous delivery vehicle navigation in real-world environments.",
    },
]


def render_careers():
    st.markdown("""
    <div style="padding:2rem 0 1rem;">
        <div style="font-size:0.85rem;color:#E63946;font-weight:600;text-transform:uppercase;letter-spacing:1px;">Open Positions</div>
        <div style="font-size:2.2rem;font-weight:800;color:#fff;margin:0.4rem 0;">Find Your Next Role</div>
        <div style="color:#888;font-size:1rem;">Hand-picked opportunities at the world's most innovative automotive companies</div>
    </div>
    """, unsafe_allow_html=True)

    # Filters
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        search = st.text_input("🔍 Search roles", placeholder="e.g. battery, autonomous...")
    with fc2:
        level_filter = st.selectbox("Experience Level", ["All", "Entry", "Mid", "Senior", "Staff"])
    with fc3:
        type_filter = st.selectbox("Work Type", ["All", "Full-time", "Hybrid", "Remote"])

    st.markdown("<br>", unsafe_allow_html=True)

    filtered = JOBS
    if search:
        filtered = [j for j in filtered if
                    search.lower() in j["title"].lower() or
                    search.lower() in j["desc"].lower() or
                    any(search.lower() in t.lower() for t in j["tags"])]
    if level_filter != "All":
        filtered = [j for j in filtered if level_filter in j["level"]]
    if type_filter != "All":
        filtered = [j for j in filtered if j["type"] == type_filter]

    if not filtered:
        st.info("No roles match your filters. Try broadening your search.")
        return

    for job in filtered:
        tags_html = "".join(f'<span class="job-tag">{t}</span>' for t in job["tags"])
        st.markdown(f"""
        <div class="job-card">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div style="display:flex;gap:1rem;align-items:flex-start;">
                    <span style="font-size:2rem;">{job["icon"]}</span>
                    <div>
                        <div class="job-title">{job["title"]}</div>
                        <div class="job-meta">🏢 {job["company"]} &nbsp;|&nbsp; 📍 {job["location"]} &nbsp;|&nbsp; ⏱ {job["type"]}</div>
                        <div style="color:#ccc;font-size:0.88rem;margin:0.4rem 0 0.6rem;max-width:560px;">{job["desc"]}</div>
                        {tags_html}
                    </div>
                </div>
                <div style="text-align:right;min-width:120px;">
                    <div style="font-size:1rem;font-weight:700;color:#E63946;">{job["salary"]}</div>
                    <div style="font-size:0.8rem;color:#888;margin-top:0.2rem;">{job["level"]}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns([1, 5])
        with c1:
            if st.button(f"Apply →", key=f"apply_{job['title']}"):
                st.session_state.applicant_data["target_role"] = job["title"]
                st.session_state.page = "apply"
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="card" style="text-align:center;padding:2.5rem;">
        <div style="font-size:1.5rem;font-weight:700;color:#fff;margin-bottom:0.5rem;">Don't see your role?</div>
        <div style="color:#888;margin-bottom:1.5rem;">We work with 320+ companies. Submit your profile and we'll match you.</div>
    </div>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("📤 Submit Open Application", key="open_app"):
            st.session_state.page = "apply"
            st.rerun()
