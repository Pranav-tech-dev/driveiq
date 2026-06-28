import streamlit as st
from db import save_application
from email_bot import send_report, build_report_text


def render_report():
    name = (
        f"{st.session_state.applicant_data.get('first_name', 'Candidate')} "
        f"{st.session_state.applicant_data.get('last_name', '')}".strip()
    )
    role   = st.session_state.applicant_data.get("target_role", "Engineering Role")
    scores = st.session_state.get("interview_score")

    if not scores:
        st.markdown("""
        <div class="card" style="text-align:center;padding:3rem;">
            <div style="font-size:3rem;">📊</div>
            <div style="font-size:1.3rem;font-weight:700;color:#fff;margin:1rem 0;">No Report Yet</div>
            <div style="color:#888;">Complete an interview to generate your personalized report card.</div>
        </div>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("🎤 Take Interview", key="go_interview"):
                st.session_state.page = "apply"
                st.rerun()
        return

    # ── Save to database (once) ────────────────────────────────────────────────
    if not st.session_state.get("saved_to_db", False):
        resume_analysis = st.session_state.applicant_data.get("resume_analysis", {})
        db_data = {
            **st.session_state.applicant_data,
            "resume_score":          resume_analysis.get("overall_score", 0),
            "technical_fit":         resume_analysis.get("technical_fit", 0),
            "automotive_relevance":  resume_analysis.get("automotive_relevance", 0),
            "leadership_signals":    resume_analysis.get("leadership_signals", 0),
            "authenticity_score":    resume_analysis.get("authenticity_score", 0),
            "interview_score":       scores.get("overall", 0),
            "verdict":               scores.get("verdict", ""),
        }
        save_application(db_data)
        st.session_state.saved_to_db = True

    overall = scores.get("overall", 7.0)
    verdict = scores.get("verdict", "Hire")
    pct     = int(overall * 10)

    verdict_colors = {
        "Strong Hire": "#00c864",
        "Hire":        "#00c864",
        "Maybe":       "#ffb400",
        "No Hire":     "#E63946",
    }
    verdict_color = verdict_colors.get(verdict, "#E63946")

    # ── Header ─────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="padding:2rem 0 1rem;">
        <div style="font-size:0.85rem;color:#E63946;font-weight:600;text-transform:uppercase;letter-spacing:1px;">Interview Report Card</div>
        <div style="font-size:2rem;font-weight:800;color:#fff;margin:0.4rem 0;">{name}</div>
        <div style="color:#888;font-size:1rem;">Applied for: <strong style="color:#E63946;">{role}</strong></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Overall + Verdict ───────────────────────────────────────────────────────
    oc1, oc2 = st.columns([1, 2])
    with oc1:
        st.markdown(f"""
        <div class="card" style="text-align:center;padding:2rem;">
            <div style="font-size:0.85rem;color:#888;margin-bottom:0.8rem;">Overall Score</div>
            <div style="font-size:4rem;font-weight:800;color:#E63946;line-height:1;">{overall}</div>
            <div style="font-size:0.9rem;color:#888;margin-bottom:1rem;">out of 10</div>
            <div class="progress-bar"><div class="progress-fill" style="width:{pct}%;"></div></div>
            <div style="margin-top:1.5rem;padding:0.5rem 1.2rem;background:{verdict_color};
                 border-radius:20px;display:inline-block;font-weight:700;color:#000;font-size:0.9rem;">
                {verdict}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with oc2:
        st.markdown("""
        <div class="card">
            <div style="font-weight:600;color:#fff;margin-bottom:1.2rem;">📈 Behavioral Metrics</div>
        """, unsafe_allow_html=True)
        metrics = [
            ("Confidence", scores.get("confidence", 70)),
            ("Engagement", scores.get("engagement", 70)),
            ("Composure",  scores.get("composure",  70)),
        ]
        for label, val in metrics:
            st.markdown(f"""
            <div style="margin-bottom:1rem;">
                <div style="display:flex;justify-content:space-between;margin-bottom:0.3rem;">
                    <span style="color:#ccc;font-size:0.9rem;">{label}</span>
                    <span style="color:#E63946;font-weight:600;">{int(val)}%</span>
                </div>
                <div class="progress-bar"><div class="progress-fill" style="width:{int(val)}%;"></div></div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 5-Dimension breakdown ──────────────────────────────────────────────────
    st.markdown('<div style="font-size:1.3rem;font-weight:700;color:#fff;margin-bottom:1rem;">5-Dimension Breakdown</div>', unsafe_allow_html=True)
    dims = [
        ("💬", "Communication",   scores.get("communication",  7)),
        ("🔧", "Technical",       scores.get("technical",      7)),
        ("🧩", "Problem Solving", scores.get("problem_solving",7)),
        ("🤝", "Cultural Fit",    scores.get("cultural_fit",   7)),
        ("👑", "Leadership",      scores.get("leadership",     7)),
    ]
    d_cols = st.columns(5)
    for col, (icon, label, val) in zip(d_cols, dims):
        with col:
            color = "#00c864" if val >= 8 else "#E63946" if val >= 6 else "#ffb400"
            st.markdown(f"""
            <div class="card" style="text-align:center;padding:1.2rem;">
                <div style="font-size:1.8rem;margin-bottom:0.5rem;">{icon}</div>
                <div style="font-size:0.8rem;color:#888;margin-bottom:0.4rem;">{label}</div>
                <div style="font-size:2rem;font-weight:800;color:{color};">{val}</div>
                <div class="progress-bar" style="margin-top:0.5rem;">
                    <div class="progress-fill" style="width:{int(val*10)}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Strengths & Growth ─────────────────────────────────────────────────────
    res_analysis = st.session_state.applicant_data.get("resume_analysis", {})
    s_col, g_col = st.columns(2)
    with s_col:
        strengths = res_analysis.get("strengths", ["Strong communication", "Technical background"])
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div style="font-weight:600;color:#00c864;margin-bottom:1rem;">✅ Key Strengths</div>', unsafe_allow_html=True)
        for s in strengths:
            st.markdown(f'<div style="color:#ccc;padding:0.4rem 0;font-size:0.9rem;border-bottom:1px solid rgba(255,255,255,0.05);">• {s}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with g_col:
        improvements = res_analysis.get("improvements", ["Quantify achievements with metrics"])
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div style="font-weight:600;color:#ffb400;margin-bottom:1rem;">💡 Growth Areas</div>', unsafe_allow_html=True)
        for tip in improvements:
            st.markdown(f'<div style="color:#ccc;padding:0.4rem 0;font-size:0.9rem;border-bottom:1px solid rgba(255,255,255,0.05);">→ {tip}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Email Report Button ────────────────────────────────────────────────────
    email = st.session_state.applicant_data.get("email", "")
    st.markdown('<div class="card" style="text-align:center;padding:2rem;">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:1.1rem;font-weight:700;color:#fff;margin-bottom:0.5rem;">📧 Get Your Report by Email</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:#888;font-size:0.9rem;margin-bottom:1.2rem;">We\'ll send your full report to <strong style="color:#E63946;">{email}</strong></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    ec1, ec2, ec3 = st.columns([1, 2, 1])
    with ec2:
        if st.button("📨 Email Me My Report", key="email_report"):
            report_text = build_report_text(st.session_state.applicant_data, scores)
            with st.spinner("Sending email..."):
                success, msg = send_report(email, name, report_text)
            if success:
                st.success(f"✅ Report sent to {email}!")
            else:
                st.warning(f"⚠️ Email could not be sent: {msg}. You can screenshot this page instead.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Next steps ─────────────────────────────────────────────────────────────
    next_steps = {
        "Strong Hire": ("🎉", "Congratulations! You're a strong match.", "Our team will reach out within 2 business days."),
        "Hire":        ("✅", "Great performance!", "Our talent team will contact you within 3–5 business days."),
        "Maybe":       ("⏳", "Good effort!", "Your profile is under review. We'll match you to other roles."),
        "No Hire":     ("📚", "Keep building!", "We recommend strengthening your automotive skills and reapplying in 6 months."),
    }
    icon, headline, detail = next_steps.get(verdict, next_steps["Maybe"])
    st.markdown(f"""
    <div class="card" style="text-align:center;padding:2.5rem;">
        <div style="font-size:2.5rem;margin-bottom:0.8rem;">{icon}</div>
        <div style="font-size:1.3rem;font-weight:700;color:#fff;margin-bottom:0.4rem;">{headline}</div>
        <div style="color:#888;font-size:0.95rem;max-width:520px;margin:0 auto;">{detail}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔄 Retake Interview", key="retake"):
            st.session_state.interview_started  = False
            st.session_state.interview_complete = False
            st.session_state.messages           = []
            st.session_state.question_scores    = []
            st.session_state.current_q          = 0
            st.session_state.interview_score    = None
            st.session_state.saved_to_db        = False
            st.session_state.page               = "interview"
            st.rerun()
    with c2:
        if st.button("💼 Browse More Jobs", key="browse_jobs"):
            st.session_state.page = "careers"
            st.rerun()
    with c3:
        if st.button("🏠 Back to Home", key="back_home"):
            st.session_state.page = "home"
            st.rerun()
