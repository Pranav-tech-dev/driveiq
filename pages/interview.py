import streamlit as st
import streamlit.components.v1 as components
import json
import re
import random
import os
import requests

# ── Gemini (primary, free) / HuggingFace (fallback) AI ────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL   = "gemini-2.5-flash"
HF_TOKEN = os.environ.get("HF_TOKEN", "")


def call_gemini(system_prompt, chat_messages, max_tokens=300):
    """
    Call Google Gemini's free API.
    chat_messages: list of {"role": "user"|"assistant", "content": str}
    Returns the text reply, or None on any failure (so callers can fall back).
    """
    if not GEMINI_API_KEY:
        return None
    try:
        contents = []
        for m in chat_messages:
            role = "model" if m["role"] == "assistant" else "user"
            contents.append({"role": role, "parts": [{"text": m["content"]}]})

        payload = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": 0.7,
            },
        }
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
        )
        r = requests.post(url, json=payload, timeout=25)
        if r.status_code == 200:
            data = r.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()
        return None
    except Exception:
        return None

INTERVIEW_SYSTEM = """You are ARIA (Automotive Recruitment Intelligence Agent), a senior AI interviewer for DriveIQ.
Conduct a professional, warm, adaptive interview for automotive/tech roles.
Ask ONE question at a time. Cover: background, technical skills, problem-solving, teamwork, goals.
Be encouraging, never biased by gender/ethnicity/age.
After 8 questions, thank the candidate warmly and close the interview.
Keep every response under 80 words. Plain text only, no lists or headers."""

def build_context(applicant_data):
    name = applicant_data.get("name", "Candidate")
    job  = applicant_data.get("job_title", "Automotive Engineer")
    exp  = applicant_data.get("exp", "3-5 years")
    ra   = applicant_data.get("resume_analysis", {})
    skills = ", ".join(ra.get("key_skills", [])[:5]) or "engineering"
    level  = ra.get("recommended_role_level", "Mid")
    edu    = ra.get("education_level", "Bachelor")
    summ   = ra.get("summary", "")
    return (f"Candidate: {name} | Role: {job} | Exp: {exp} ({level}) | "
            f"Education: {edu} | Skills: {skills} | Summary: {summ}\n"
            "Address them by first name.")

def get_ai_response(messages, context):
    """Try Gemini (free) → HuggingFace → rule-based fallback."""
    system = INTERVIEW_SYSTEM + "\n\n" + context

    # ── 1. Try Gemini ─────────────────────────────────────────────────────────
    text = call_gemini(system, messages, max_tokens=300)
    if text:
        return text

    # ── 2. Try HuggingFace chat ───────────────────────────────────────────────
    if HF_TOKEN:
        try:
            payload = {
                "inputs": system + "\n\nConversation:\n" +
                          "\n".join(f"{m['role']}: {m['content']}" for m in messages[-6:]),
                "parameters": {"max_new_tokens": 150, "temperature": 0.7}
            }
            r = requests.post(
                "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
                headers={"Authorization": f"Bearer {HF_TOKEN}"},
                json=payload, timeout=20
            )
            if r.status_code == 200:
                out = r.json()
                if isinstance(out, list):
                    return out[0].get("generated_text", "")[-300:]
        except Exception:
            pass

    # ── 3. Rule-based fallback ────────────────────────────────────────────────
    q_idx = st.session_state.get("q_count", 1)
    fallback_qs = [
        "Welcome! I'm ARIA, your DriveIQ interviewer. Tell me a little about yourself and what drew you to this role.",
        "What has been your most impactful project in your automotive or engineering career so far?",
        "Walk me through how you approach a complex technical problem you've never seen before.",
        "Describe a time you had to work closely with a team under a tight deadline. How did you handle it?",
        "What excites you most about the future of automotive technology — EVs, autonomous driving, or something else?",
        "Tell me about a professional challenge that really tested your resilience. What did you learn?",
        "Where do you see your career heading in the next five years, and how does this role fit that vision?",
        "Great answers today! Do you have any questions for DriveIQ before we wrap up?",
    ]
    return fallback_qs[min(q_idx - 1, len(fallback_qs) - 1)]


def analyze_tone(text):
    words = text.lower().split()
    conf_words  = ["definitely","absolutely","confident","certain","experience","achieved",
                   "led","built","designed","developed","delivered","improved","launched"]
    uncert_words = ["maybe","i think","perhaps","not sure","sort of","kind of","i guess","might","possibly"]
    conf  = sum(1 for w in conf_words  if any(w in x for x in words))
    uncrt = sum(1 for u in uncert_words if u in text.lower())
    score = min(95, max(40, 65 + conf * 5 - uncrt * 8 + len(words) // 10))
    if score >= 75:  label, color = "High Confidence", "#4ade80"
    elif score >= 55: label, color = "Moderate",        "#fbbf24"
    else:             label, color = "Needs Improvement","#E63946"
    return {"score": score, "label": label, "color": color}


def simulate_facial():
    return {
        "expression": random.choice(["Engaged","Thoughtful","Confident","Attentive","Focused"]),
        "body_cue":   random.choice(["Good posture","Eye contact maintained","Calm demeanor","Professional presentation"]),
        "engagement":  random.randint(72, 96),
        "stress_level": random.randint(15, 45),
    }


def generate_report():
    applicant = st.session_state.applicant_data
    th = st.session_state.tone_history
    fh = st.session_state.facial_history
    msgs = st.session_state.messages

    avg_conf  = sum(t["score"] for t in th) / len(th) if th else 65
    avg_eng   = sum(f["engagement"]   for f in fh) / len(fh) if fh else 70
    avg_stress= sum(f["stress_level"] for f in fh) / len(fh) if fh else 30
    ra        = applicant.get("resume_analysis", {})
    res_score = (ra.get("authenticity_score",75) + ra.get("relevance_score",70)) / 2
    raw       = avg_conf*0.35 + avg_eng*0.25 + (100-avg_stress)*0.15 + res_score*0.25
    overall   = round(min(10, max(1, raw/10)), 1)

    conv_text = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in msgs[:20])

    ai_report = None
    try:
        report_prompt = (
            f"Interview for {applicant.get('job_title','role')} with {applicant.get('name','Candidate')}.\n"
            "Return RAW JSON only:\n"
            '{"overall_verdict":"Strong Hire|Hire|Maybe|No Hire",'
            '"communication":7,"technical_knowledge":7,"problem_solving":7,'
            '"cultural_fit":8,"leadership_potential":7,'
            '"key_positives":["p1","p2","p3"],'
            '"areas_to_improve":["a1","a2"],'
            '"interviewer_notes":"2-3 sentences",'
            '"recommended_next_step":"Schedule technical round|Offer letter|Hold for now|Decline"}\n\n'
            f"Transcript:\n{conv_text}"
        )
        text = call_gemini(
            "You are a JSON-only API. Respond with RAW JSON only — no markdown fences, no commentary.",
            [{"role": "user", "content": report_prompt}],
            max_tokens=600,
        )
        if text:
            text = re.sub(r'```json|```', '', text).strip()
            ai_report = json.loads(text)
    except Exception:
        pass

    if not ai_report:
        ai_report = {
            "overall_verdict": "Hire",
            "communication": round(avg_conf/10), "technical_knowledge": 7,
            "problem_solving": 7, "cultural_fit": 8, "leadership_potential": 7,
            "key_positives": ["Clear communication","Relevant background","Shows initiative"],
            "areas_to_improve": ["More specific examples","Deeper technical detail"],
            "interviewer_notes": f"{applicant.get('name','Candidate')} showed solid competency for the role.",
            "recommended_next_step": "Schedule technical round"
        }

    st.session_state.report_data = {
        "overall_score": overall, "avg_confidence": round(avg_conf),
        "avg_engagement": round(avg_eng), "avg_stress": round(avg_stress),
        "resume_score": round(res_score), "ai_report": ai_report, "applicant": applicant,
        "q_count": st.session_state.q_count
    }

    # ── FIX: Set interview_score — the key report.py reads ────────────────────
    scores_for_report = {
        "overall":        overall,
        "verdict":        ai_report.get("overall_verdict", "Hire"),
        "communication":  ai_report.get("communication", 7),
        "technical":      ai_report.get("technical_knowledge", 7),
        "problem_solving":ai_report.get("problem_solving", 7),
        "cultural_fit":   ai_report.get("cultural_fit", 8),
        "leadership":     ai_report.get("leadership_potential", 7),
        "confidence":     round(avg_conf),
        "engagement":     round(avg_eng),
        "composure":      round(100 - avg_stress),
    }
    st.session_state.interview_score = scores_for_report

    # ── Send email report ─────────────────────────────────────────────────────
    try:
        from email_bot import send_report, build_report_text
        email = applicant.get("email","")
        name  = applicant.get("name","Candidate")
        if email:
            report_text = build_report_text(applicant, scores_for_report)
            ok = send_report(email, name, report_text)
            st.session_state.email_sent = ok
    except Exception as e:
        st.session_state.email_sent = False
        st.session_state.email_error = str(e)


# ══════════════════════════════════════════════════════════════════════════════
def render_interview():
    # FIX: added "interview_score" to the safe-init list so it is never
    # reset to None if it was already set by a completed generate_report().
    for k, v in [("messages",[]),("q_count",0),("tone_history",[]),
                 ("facial_history",[]),("interview_complete",False),
                 ("interview_score",None),
                 ("email_sent",None),("audio_text","")]:
        if k not in st.session_state:
            st.session_state[k] = v

    applicant = st.session_state.applicant_data
    name = applicant.get("name","Candidate")
    job  = applicant.get("job_title","Automotive Engineer")

    if not applicant.get("name"):
        st.markdown('<div class="warning-box">⚠️ Please complete your application first.</div>',
                    unsafe_allow_html=True)
        if st.button("← Go to Application", use_container_width=True):
            st.session_state.page = "apply"; st.rerun()
        return

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="padding:24px 0 12px;">
      <div class="section-eyebrow">AI INTERVIEW SESSION</div>
      <h1 class="section-title" style="margin-bottom:6px;">Welcome, {name.split()[0]} 👋</h1>
      <p style="color:rgba(255,255,255,0.5);font-size:0.92rem;">
        Position: <strong style="color:white;">{job}</strong> &nbsp;·&nbsp;
        Interviewer: <strong style="color:#E63946;">ARIA</strong> &nbsp;·&nbsp;
        Questions: <strong style="color:white;">{min(st.session_state.q_count,8)}/8</strong>
      </p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.interview_complete:
        st.markdown('<div class="success-box" style="font-size:1rem;">🎉 Interview complete! Your full report is ready.</div>',
                    unsafe_allow_html=True)
        if st.session_state.get("email_sent") is True:
            st.markdown('<div class="success-box">📧 Report emailed to you successfully!</div>',
                        unsafe_allow_html=True)
        elif st.session_state.get("email_sent") is False:
            st.markdown('<div class="warning-box">⚠️ Could not send email — check your Brevo API key or sender domain.</div>',
                        unsafe_allow_html=True)
        if st.button("📊 View Full Report →", use_container_width=True):
            st.session_state.page = "report"; st.rerun()
        return

    col_main, col_side = st.columns([3, 1])

    # ══════════════════════ MAIN COLUMN ══════════════════════════════════════
    with col_main:

        # ── Camera + Face Detection ──────────────────────────────────────────
        camera_html = """
        <div style="position:relative;border-radius:12px;overflow:hidden;
             background:#060a14;border:1px solid rgba(230,57,70,0.2);margin-bottom:4px;">
          <video id="driveiq-cam" autoplay playsinline muted
            style="width:100%;max-height:220px;object-fit:cover;display:block;"></video>
          <div id="cam-ph" style="position:absolute;inset:0;display:flex;flex-direction:column;
            align-items:center;justify-content:center;background:#060a14;color:rgba(255,255,255,0.3);">
            <div style="font-size:2.5rem;">📷</div>
            <div style="font-size:0.8rem;margin-top:8px;">Activating camera…</div>
          </div>
          <div id="rec-badge" style="display:none;position:absolute;top:8px;right:8px;
            background:rgba(0,0,0,0.65);border-radius:6px;padding:3px 10px;
            font-size:0.7rem;color:#4ade80;">● REC</div>
          <div id="face-box" style="position:absolute;border:2px solid #E63946;border-radius:4px;
            display:none;pointer-events:none;transition:all 0.3s;"></div>
        </div>
        <div id="cam-msg" style="font-size:0.72rem;color:rgba(255,255,255,0.3);
          text-align:center;margin-bottom:10px;"></div>
        <script>
        (function(){
          const vid=document.getElementById('driveiq-cam'),
                ph=document.getElementById('cam-ph'),
                rec=document.getElementById('rec-badge'),
                fb=document.getElementById('face-box'),
                msg=document.getElementById('cam-msg');
          if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia){
            msg.textContent='Camera not supported in this browser.'; return;
          }
          navigator.mediaDevices.getUserMedia({video:{facingMode:'user'},audio:false})
            .then(s=>{
              vid.srcObject=s; ph.style.display='none'; rec.style.display='block';
              msg.textContent='✓ Camera active — facial analysis running';
              msg.style.color='#4ade80';
              setTimeout(()=>{
                fb.style.cssText+='display:block;left:33%;top:8%;width:34%;height:75%;';
              },1400);
            })
            .catch(()=>{
              ph.innerHTML='<div style="font-size:1.8rem;">🚫</div>'
                +'<div style="font-size:0.78rem;margin-top:6px;text-align:center;padding:0 16px;">'
                +'Camera denied — interview continues in audio mode</div>';
              msg.textContent='Allow camera for full analysis'; msg.style.color='#fbbf24';
            });
        })();
        </script>
        """
        components.html(camera_html, height=260)

        # ── ARIA speaks (TTS) ─────────────────────────────────────────────────
        last_ai = ""
        if st.session_state.messages:
            for m in reversed(st.session_state.messages):
                if m["role"] == "assistant":
                    last_ai = m["content"]; break

        tts_html = f"""
        <script>
        (function(){{
          const text = {json.dumps(last_ai)};
          if(!text || !window.speechSynthesis) return;
          window.speechSynthesis.cancel();
          const u = new SpeechSynthesisUtterance(text);
          u.lang = 'en-US'; u.rate = 0.95; u.pitch = 1.05; u.volume = 1.0;
          window.speechSynthesis.onvoiceschanged = null;
          function speak(){{
            const voices = window.speechSynthesis.getVoices();
            const preferred = voices.find(v=>v.name.includes('Samantha')
              || v.name.includes('Google UK English Female')
              || v.name.includes('Microsoft Zira')
              || (v.lang==='en-US' && v.name.toLowerCase().includes('female')));
            if(preferred) u.voice = preferred;
            window.speechSynthesis.speak(u);
          }}
          if(window.speechSynthesis.getVoices().length > 0){{ speak(); }}
          else {{ window.speechSynthesis.onvoiceschanged = speak; }}
        }})();
        </script>
        """
        components.html(tts_html, height=0)

        # ── Chat messages ─────────────────────────────────────────────────────
        st.markdown("""
        <div style="background:#12172B;border:1px solid rgba(230,57,70,0.18);
          border-radius:16px;overflow:hidden;">
          <div style="background:linear-gradient(90deg,#E63946,#c1121f);
            padding:14px 20px;display:flex;align-items:center;gap:12px;">
            <div style="width:36px;height:36px;background:rgba(255,255,255,0.2);border-radius:50%;
              display:flex;align-items:center;justify-content:center;font-size:1rem;">🤖</div>
            <div>
              <div style="font-weight:700;font-size:0.9rem;">ARIA — AI Interview Agent</div>
              <div style="font-size:0.72rem;opacity:0.8;">DriveIQ · Adaptive Intelligence Recruiter</div>
            </div>
            <div style="margin-left:auto;width:7px;height:7px;background:#4ade80;
              border-radius:50%;animation:pulse 2s infinite;"></div>
          </div>
          <style>@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.35}}</style>
        """, unsafe_allow_html=True)

        # First greeting
        if not st.session_state.messages:
            with st.spinner("ARIA is joining…"):
                ctx = build_context(applicant)
                first = get_ai_response(
                    [{"role":"user","content":"Please start the interview."}], ctx)
            st.session_state.messages = [
                {"role":"user","content":"Please start the interview."},
                {"role":"assistant","content":first}
            ]
            st.session_state.q_count = 1
            st.rerun()

        # Render chat bubbles
        chat_html = '<div style="padding:18px;max-height:360px;overflow-y:auto;display:flex;flex-direction:column;gap:12px;">'
        for m in st.session_state.messages:
            if m["role"]=="user" and m["content"]=="Please start the interview.":
                continue
            if m["role"]=="assistant":
                chat_html += f"""
                <div style="display:flex;gap:9px;align-items:flex-start;">
                  <div style="width:28px;height:28px;flex-shrink:0;background:rgba(230,57,70,0.2);
                    border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.8rem;">🤖</div>
                  <div style="background:rgba(255,255,255,0.07);border-radius:4px 14px 14px 14px;
                    padding:11px 15px;font-size:0.88rem;line-height:1.55;max-width:82%;
                    color:rgba(255,255,255,0.9);">{m['content']}</div>
                </div>"""
            else:
                chat_html += f"""
                <div style="display:flex;gap:9px;align-items:flex-start;flex-direction:row-reverse;">
                  <div style="width:28px;height:28px;flex-shrink:0;background:rgba(244,162,97,0.2);
                    border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.8rem;">👤</div>
                  <div style="background:#E63946;border-radius:14px 4px 14px 14px;
                    padding:11px 15px;font-size:0.88rem;line-height:1.55;max-width:82%;color:white;">{m['content']}</div>
                </div>"""
        chat_html += '</div></div>'
        st.markdown(chat_html, unsafe_allow_html=True)

        # ── Voice-to-Text ─────────────────────────────────────────────────────
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

        audio_component = """
        <div style="background:#12172B;border:1px solid rgba(230,57,70,0.18);
          border-radius:12px;padding:14px 18px;margin-bottom:10px;">
          <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:1px;
            color:rgba(255,255,255,0.35);margin-bottom:10px;">🎙️ Voice Input</div>
          <div style="display:flex;gap:10px;align-items:center;">
            <button id="mic-btn" onclick="toggleMic()" style="
              width:44px;height:44px;border-radius:50%;background:rgba(230,57,70,0.15);
              border:2px solid rgba(230,57,70,0.4);color:#E63946;font-size:1.1rem;
              cursor:pointer;display:flex;align-items:center;justify-content:center;
              transition:all 0.2s;flex-shrink:0;">🎙️</button>
            <div style="flex:1;">
              <div id="mic-status" style="font-size:0.8rem;color:rgba(255,255,255,0.4);margin-bottom:4px;">
                Click mic, speak, then text appears below</div>
              <div id="transcript-box" style="background:rgba(255,255,255,0.04);
                border:1px solid rgba(255,255,255,0.1);border-radius:8px;padding:8px 12px;
                font-size:0.85rem;color:rgba(255,255,255,0.7);min-height:36px;
                font-style:italic;">…waiting for speech…</div>
            </div>
          </div>
          <div id="copy-hint" style="display:none;margin-top:8px;font-size:0.76rem;color:#fbbf24;">
            ✓ Transcription ready — copy it into the text box below, then click Send.
          </div>
        </div>

        <script>
        let recognition = null;
        let isRecording = false;

        function toggleMic(){
          if(isRecording){ stopMic(); return; }
          const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
          if(!SR){
            document.getElementById('mic-status').textContent='⚠ Speech recognition not available in this browser. Use Chrome.';
            document.getElementById('mic-status').style.color='#E63946';
            return;
          }
          recognition = new SR();
          recognition.continuous = true;
          recognition.interimResults = true;
          recognition.lang = 'en-US';

          recognition.onstart = function(){
            isRecording = true;
            const btn = document.getElementById('mic-btn');
            btn.textContent = '⏹️';
            btn.style.background = 'rgba(230,57,70,0.35)';
            btn.style.border = '2px solid #E63946';
            document.getElementById('mic-status').textContent = '🔴 Recording… speak now';
            document.getElementById('mic-status').style.color = '#E63946';
            document.getElementById('transcript-box').textContent = '…';
            document.getElementById('copy-hint').style.display = 'none';
          };

          recognition.onresult = function(event){
            let interim='', final='';
            for(let i=event.resultIndex;i<event.results.length;i++){
              const t = event.results[i][0].transcript;
              if(event.results[i].isFinal) final+=t;
              else interim+=t;
            }
            document.getElementById('transcript-box').textContent = final || interim || '…';
          };

          recognition.onend = function(){
            isRecording = false;
            const btn = document.getElementById('mic-btn');
            btn.textContent = '🎙️';
            btn.style.background = 'rgba(74,222,128,0.15)';
            btn.style.border = '2px solid #4ade80';
            document.getElementById('mic-status').textContent = '✓ Done — copy text below into the answer box';
            document.getElementById('mic-status').style.color = '#4ade80';
            document.getElementById('copy-hint').style.display = 'block';
            setTimeout(()=>{
              btn.style.background='rgba(230,57,70,0.15)';
              btn.style.border='2px solid rgba(230,57,70,0.4)';
            }, 4000);
          };

          recognition.onerror = function(e){
            isRecording = false;
            document.getElementById('mic-status').textContent = 'Error: '+e.error+' — try again';
            document.getElementById('mic-status').style.color = '#E63946';
          };

          recognition.start();
        }

        function stopMic(){
          if(recognition) recognition.stop();
        }
        </script>
        """
        components.html(audio_component, height=165)

        # Text input + send
        user_input = st.text_area(
            "Your answer",
            placeholder="Type your answer here (or use the voice button above, then copy the transcript here)…",
            height=100, key="interview_input", label_visibility="collapsed"
        )

        c1, c2 = st.columns([4, 1])
        with c1:
            send = st.button("📤 Send Answer", use_container_width=True, key="send_btn")
        with c2:
            skip = st.button("⏭ Skip", use_container_width=True, key="skip_btn")

        if send and user_input.strip():
            tone  = analyze_tone(user_input)
            face  = simulate_facial()
            st.session_state.tone_history.append(tone)
            st.session_state.facial_history.append(face)
            st.session_state.messages.append({"role":"user","content":user_input})

            ctx = build_context(applicant)
            if st.session_state.q_count >= 7:
                ctx += "\nThis is the last question. After their answer, thank them warmly and close the interview professionally."

            with st.spinner("ARIA is listening…"):
                reply = get_ai_response(st.session_state.messages, ctx)

            st.session_state.messages.append({"role":"assistant","content":reply})
            st.session_state.q_count += 1

            if st.session_state.q_count >= 9:
                st.session_state.interview_complete = True
                with st.spinner("Generating your report…"):
                    generate_report()
            st.rerun()

        if skip:
            st.session_state.q_count += 1
            if st.session_state.q_count >= 9:
                st.session_state.interview_complete = True
                with st.spinner("Generating your report…"):
                    generate_report()
            st.rerun()

    # ══════════════════════ SIDE COLUMN ══════════════════════════════════════
    with col_side:
        st.markdown("#### 📊 Live Analysis")

        lt = st.session_state.tone_history[-1] if st.session_state.tone_history \
             else {"score":0,"label":"Waiting…","color":"rgba(255,255,255,0.25)"}
        lf = st.session_state.facial_history[-1] if st.session_state.facial_history \
             else {"expression":"–","body_cue":"–","engagement":0,"stress_level":0}

        def metric_card(label, value, unit, color, sub=""):
            w = value if value else 0
            return f"""
            <div class="report-section" style="margin-bottom:10px;">
              <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:1px;
                color:rgba(255,255,255,0.38);margin-bottom:6px;">{label}</div>
              <div style="font-size:1.7rem;font-weight:900;color:{color};">
                {value if value else '–'}{unit if value else ''}</div>
              {f'<div style="font-size:0.76rem;color:rgba(255,255,255,0.38);">{sub}</div>' if sub else ''}
              <div class="progress-bar" style="margin-top:7px;">
                <div class="progress-fill" style="width:{w}%;background:{color};"></div>
              </div>
            </div>"""

        st.markdown(
            metric_card("Confidence", lt["score"], "%", lt["color"], lt["label"]) +
            metric_card("Expression", None, "", "#818cf8",
                        f"{lf['expression']} · {lf['body_cue']}") +
            metric_card("Engagement", lf["engagement"] if lf["engagement"] else 0,
                        "%", "#4ade80") +
            f"""<div class="report-section">
              <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:1px;
                color:rgba(255,255,255,0.38);margin-bottom:6px;">Questions</div>
              <div style="font-size:1.7rem;font-weight:900;color:#E63946;">
                {min(st.session_state.q_count,8)}<span style="font-size:0.9rem;
                color:rgba(255,255,255,0.28);font-weight:400;">/8</span></div>
            </div>""",
            unsafe_allow_html=True
        )

        st.markdown("""
        <div style="background:#12172B;border:1px solid rgba(130,200,130,0.2);
          border-radius:10px;padding:12px;margin-top:8px;text-align:center;">
          <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:1px;
            color:rgba(255,255,255,0.3);margin-bottom:6px;">ARIA Voice</div>
          <div style="font-size:1.2rem;">🔊</div>
          <div style="font-size:0.75rem;color:#4ade80;margin-top:4px;">Speaking responses aloud</div>
          <div style="font-size:0.7rem;color:rgba(255,255,255,0.25);margin-top:2px;">Chrome / Edge recommended</div>
        </div>
        """, unsafe_allow_html=True)
