import streamlit as st
import io
import time

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


def extract_text_from_file(uploaded_file) -> str:
    """Extract plain text from PDF or DOCX upload."""
    name = uploaded_file.name.lower()
    if name.endswith(".pdf") and PDF_AVAILABLE:
        reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        return " ".join(page.extract_text() or "" for page in reader.pages)
    elif name.endswith(".docx") and DOCX_AVAILABLE:
        doc = Document(io.BytesIO(uploaded_file.read()))
        return " ".join(p.text for p in doc.paragraphs)
    else:
        # Plain text fallback
        try:
            return uploaded_file.read().decode("utf-8", errors="ignore")
        except Exception:
            return ""


def render_apply():
    st.markdown("""
    <div style="padding:2rem 0 1rem;">
        <div style="font-size:0.85rem;color:#E63946;font-weight:600;text-transform:uppercase;letter-spacing:1px;">Application Portal</div>
        <div style="font-size:2.2rem;font-weight:800;color:#fff;margin:0.4rem 0;">Start Your Journey</div>
        <div style="color:#888;font-size:1rem;">Complete your profile and let our AI analyze your fit — it takes under 3 minutes.</div>
    </div>
    """, unsafe_allow_html=True)

    # Step indicator
    step = st.session_state.get("apply_step", 1)
    steps = ["Personal Info", "Resume Upload", "AI Analysis", "Proceed"]
    step_html = '<div style="display:flex;gap:0;margin-bottom:2rem;">'
    for i, s in enumerate(steps, 1):
        active = i == step
        done = i < step
        color = "#E63946" if active else ("#00c864" if done else "#333")
        tc = "#fff" if (active or done) else "#555"
        step_html += f"""
        <div style="flex:1;text-align:center;padding:0.6rem;background:{color};color:{tc};
             font-size:0.8rem;font-weight:600;border-radius:{'8px 0 0 8px' if i==1 else ('0 8px 8px 0' if i==4 else '0')};
             {'opacity:0.9' if not active else ''}">
            {'✓ ' if done else f'{i}. '}{s}
        </div>"""
    step_html += "</div>"
    st.markdown(step_html, unsafe_allow_html=True)

    if step == 1:
        _step1_personal()
    elif step == 2:
        _step2_resume()
    elif step == 3:
        _step3_analysis()
    elif step == 4:
        _step4_proceed()


def _step1_personal():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### 👤 Personal Information")

    c1, c2 = st.columns(2)
    with c1:
        first = st.text_input("First Name *", value=st.session_state.applicant_data.get("first_name", ""))
        email = st.text_input("Email Address *", value=st.session_state.applicant_data.get("email", ""))
        location = st.text_input("City, Country", value=st.session_state.applicant_data.get("location", ""))
    with c2:
        last = st.text_input("Last Name *", value=st.session_state.applicant_data.get("last_name", ""))
        phone = st.text_input("Phone Number", value=st.session_state.applicant_data.get("phone", ""))
        experience = st.selectbox("Years of Experience",
            ["0–1 years", "2–4 years", "5–8 years", "9–12 years", "13+ years"],
            index=["0–1 years", "2–4 years", "5–8 years", "9–12 years", "13+ years"].index(
                st.session_state.applicant_data.get("experience", "0–1 years")
            )
        )

    role = st.selectbox("Target Role *",
        ["EV Battery Systems Engineer", "Autonomous Systems Tech Lead", "ADAS Software Engineer",
         "Connected Car Cloud Architect", "Powertrain Systems Engineer", "AI/ML Engineer – Robotics", "Other"],
        index=0
    )
    linkedin = st.text_input("LinkedIn URL (optional)", value=st.session_state.applicant_data.get("linkedin", ""))

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Continue →", key="step1_next"):
        if not first or not last or not email:
            st.error("Please fill in all required fields (marked with *).")
        else:
            st.session_state.applicant_data.update({
                "first_name": first, "last_name": last,
                "email": email, "phone": phone,
                "location": location, "experience": experience,
                "target_role": role, "linkedin": linkedin,
                # Aliases expected by interview.py / report.py
                "name": f"{first} {last}".strip(),
                "job_title": role,
                "exp": experience,
            })
            st.session_state.apply_step = 2
            st.rerun()


def _step2_resume():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### 📄 Upload Your Resume")
    st.markdown('<p style="color:#888;font-size:0.9rem;">Supported formats: PDF, DOCX, TXT (max 10MB)</p>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Drop your resume here",
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed"
    )

    st.markdown("**Or paste your resume text:**")
    pasted = st.text_area("Paste resume content", height=200,
                          placeholder="Paste your resume text here if you don't have a file...",
                          label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back", key="step2_back"):
            st.session_state.apply_step = 1
            st.rerun()
    with col2:
        if st.button("Analyze Resume →", key="step2_next"):
            resume_text = ""
            if uploaded:
                resume_text = extract_text_from_file(uploaded)
            elif pasted:
                resume_text = pasted

            if not resume_text.strip():
                st.error("Please upload a resume file or paste your resume text.")
            else:
                st.session_state.applicant_data["resume_text"] = resume_text
                st.session_state.apply_step = 3
                st.rerun()


def _step3_analysis():
    resume_text = st.session_state.applicant_data.get("resume_text", "")
    role = st.session_state.applicant_data.get("target_role", "Engineering")
    name = f"{st.session_state.applicant_data.get('first_name', '')} {st.session_state.applicant_data.get('last_name', '')}".strip()

    if not st.session_state.resume_analyzed:
        with st.spinner("🤖 ARIA is analyzing your resume..."):
            progress = st.progress(0)
            stages = [
                "Extracting skills and experience...",
                "Matching to automotive role requirements...",
                "Running authenticity verification...",
                "Computing fit scores...",
            ]
            for i, stage in enumerate(stages):
                st.markdown(f'<div style="color:#888;font-size:0.88rem;">⚙️ {stage}</div>', unsafe_allow_html=True)
                time.sleep(0.6)
                progress.progress((i + 1) * 25)

            from components.ai_engine import analyze_resume
            result = analyze_resume(resume_text, role)
            st.session_state.applicant_data["resume_analysis"] = result
            st.session_state.resume_analyzed = True
            st.rerun()
    else:
        result = st.session_state.applicant_data.get("resume_analysis", {})
        overall = result.get("overall_score", 7.0)
        pct = int(overall * 10)

        st.markdown(f"""
        <div class="card" style="text-align:center;margin-bottom:1.5rem;">
            <div style="font-size:0.9rem;color:#888;margin-bottom:1rem;">Resume Analysis Complete for <strong style="color:#fff;">{name}</strong></div>
            <div style="font-size:3rem;font-weight:800;color:#E63946;">{overall}/10</div>
            <div style="font-size:0.9rem;color:#888;margin-top:0.3rem;">Overall Resume Score</div>
            <div class="progress-bar" style="max-width:300px;margin:1rem auto;">
                <div class="progress-fill" style="width:{pct}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        dims = [
            ("🔧 Technical Fit", result.get("technical_fit", 7)),
            ("🚗 Automotive Relevance", result.get("automotive_relevance", 6)),
            ("👥 Leadership Signals", result.get("leadership_signals", 6)),
        ]
        for col, (label, val) in zip([c1, c2, c3], dims):
            with col:
                st.markdown(f"""
                <div class="card" style="text-align:center;">
                    <div style="font-size:0.85rem;color:#888;margin-bottom:0.4rem;">{label}</div>
                    <div style="font-size:1.8rem;font-weight:800;color:#E63946;">{val}/10</div>
                    <div class="progress-bar"><div class="progress-fill" style="width:{int(val*10)}%;"></div></div>
                </div>
                """, unsafe_allow_html=True)

        # Authenticity
        auth = result.get("authenticity_score", 85)
        flags = result.get("fraud_flags", [])
        auth_color = "#00c864" if auth > 70 else "#ffb400" if auth > 50 else "#E63946"
        st.markdown(f"""
        <div class="card" style="margin-top:1rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <div style="font-size:0.95rem;font-weight:600;color:#fff;">🔐 Document Authenticity</div>
                    <div style="font-size:0.85rem;color:#888;margin-top:0.3rem;">
                        {'✅ Resume appears consistent and credible' if not flags else '⚠️ ' + '; '.join(flags)}
                    </div>
                </div>
                <div style="font-size:2rem;font-weight:800;color:{auth_color};">{auth}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Strengths
        strengths = result.get("strengths", [])
        if strengths:
            st.markdown('<div style="margin-top:1rem;font-weight:600;color:#fff;">✅ Key Strengths Detected</div>', unsafe_allow_html=True)
            for s in strengths:
                st.markdown(f'<div style="color:#aaa;padding:0.3rem 0;font-size:0.9rem;">• {s}</div>', unsafe_allow_html=True)

        improvements = result.get("improvements", [])
        if improvements:
            st.markdown('<div style="margin-top:1rem;font-weight:600;color:#fff;">💡 Improvement Tips</div>', unsafe_allow_html=True)
            for tip in improvements:
                st.markdown(f'<div style="color:#888;padding:0.3rem 0;font-size:0.88rem;">→ {tip}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Re-upload Resume", key="step3_back"):
                st.session_state.apply_step = 2
                st.session_state.resume_analyzed = False
                st.rerun()
        with col2:
            if st.button("🎤 Proceed to Interview →", key="step3_next"):
                st.session_state.apply_step = 4
                st.rerun()


def _step4_proceed():
    name = f"{st.session_state.applicant_data.get('first_name', '')} {st.session_state.applicant_data.get('last_name', '')}".strip()
    role = st.session_state.applicant_data.get("target_role", "the role")

    st.markdown(f"""
    <div class="card" style="text-align:center;padding:3rem;">
        <div style="font-size:3rem;margin-bottom:1rem;">🎯</div>
        <div style="font-size:1.8rem;font-weight:800;color:#fff;margin-bottom:0.5rem;">You're All Set, {name}!</div>
        <div style="color:#888;font-size:1rem;max-width:480px;margin:0 auto 2rem;">
            Your application for <strong style="color:#E63946;">{role}</strong> has been received.
            Next up: a 10-minute AI interview with ARIA. Stay calm, speak clearly, and be yourself.
        </div>
        <div style="background:#1A1A1A;border-radius:12px;padding:1.5rem;max-width:400px;margin:0 auto 2rem;text-align:left;">
            <div style="font-weight:600;color:#fff;margin-bottom:0.8rem;">📋 Interview Tips</div>
            <div style="color:#aaa;font-size:0.88rem;line-height:1.8;">
                ✓ Find a quiet, well-lit space<br>
                ✓ Use specific examples (STAR method)<br>
                ✓ Mention measurable results<br>
                ✓ Show your automotive passion
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🚀 Begin AI Interview", key="begin_interview"):
            st.session_state.page = "interview"
            st.session_state.interview_started = False
            st.session_state.messages = []
            st.session_state.apply_step = 1
            st.rerun()
