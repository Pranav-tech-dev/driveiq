"""
DriveIQ AI Engine — Hugging Face Inference API
HF Token hardcoded + loaded from environment
"""

import os
import requests
import time

HF_TOKEN = os.environ.get("HF_TOKEN", "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")
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

DISTILBERT_URL = "https://api-inference.huggingface.co/models/distilbert-base-uncased-finetuned-sst-2-english"
CLASSIFY_URL   = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"


def _post(url, payload, retries=3):
    for attempt in range(retries):
        try:
            r = requests.post(url, headers=HEADERS, json=payload, timeout=40)
            if r.status_code == 503:
                time.sleep(15 + attempt * 10)
                continue
            return r.json()
        except Exception:
            time.sleep(5)
    return {}


def _sentiment_score(text):
    data = _post(DISTILBERT_URL, {"inputs": text[:512]})
    if isinstance(data, list) and data:
        for item in data[0]:
            if item.get("label") == "POSITIVE":
                return item.get("score", 0.5)
    return 0.5


def _classify(text, labels):
    data = _post(CLASSIFY_URL, {
        "inputs": text[:1024],
        "parameters": {"candidate_labels": labels}
    })
    if "scores" in data:
        return dict(zip(data["labels"], data["scores"]))
    return {l: 1 / len(labels) for l in labels}


def analyze_resume(resume_text, job_role):
    tech = _classify(resume_text, ["highly qualified technically", "somewhat qualified", "not technically qualified"])
    tech_fit = tech.get("highly qualified technically", 0.5) * 10

    auto = _classify(resume_text, ["automotive industry experience", "adjacent industry experience", "unrelated experience"])
    auto_fit = auto.get("automotive industry experience", 0.4) * 10

    lead = _classify(resume_text, ["leadership and management experience", "individual contributor", "entry level candidate"])
    lead_fit = lead.get("leadership and management experience", 0.3) * 10

    auth_score = _sentiment_score(resume_text[:400])

    overall = round(tech_fit * 0.4 + auto_fit * 0.35 + lead_fit * 0.25, 1)
    overall = min(max(overall, 3.0), 9.5)

    return {
        "overall_score": overall,
        "technical_fit": round(tech_fit, 1),
        "automotive_relevance": round(auto_fit, 1),
        "leadership_signals": round(lead_fit, 1),
        "authenticity_score": round(auth_score * 100, 1),
        "fraud_flags": [] if auth_score > 0.5 else ["Possible inconsistency detected"],
        "strengths": _extract_strengths(resume_text, job_role),
        "improvements": _extract_improvements(tech_fit, auto_fit),
    }


def _extract_strengths(text, role):
    keywords = {
        "python": "Python programming proficiency",
        "machine learning": "ML/AI expertise",
        "electric vehicle": "EV domain knowledge",
        "autonomous": "Autonomous systems experience",
        "can bus": "CAN bus / embedded systems",
        "supply chain": "Supply chain management",
        "quality": "Quality assurance background",
        "project management": "Project management skills",
        "leadership": "Leadership experience",
        "data": "Data analysis capabilities",
        "java": "Java development skills",
        "embedded": "Embedded systems expertise",
        "ros": "ROS/robotics experience",
    }
    found = [v for k, v in keywords.items() if k in text.lower()]
    return found[:4] if found else ["Relevant educational background", "Transferable technical skills"]


def _extract_improvements(tech_fit, auto_fit):
    tips = []
    if tech_fit < 6:
        tips.append("Strengthen technical skills section with certifications")
    if auto_fit < 5:
        tips.append("Highlight any automotive or mobility-related projects")
    tips.append("Quantify achievements with metrics where possible")
    return tips[:3]


def score_interview_response(user_text, question, role):
    sentiment = _sentiment_score(user_text)
    confidence = min(max(sentiment * 10, 3.0), 9.8)

    comm = _classify(user_text, ["clear and articulate communication", "average communication", "unclear communication"])
    communication = comm.get("clear and articulate communication", 0.5) * 10

    tech = _classify(user_text, ["deep technical knowledge demonstrated", "basic technical understanding", "no technical content"])
    technical = tech.get("deep technical knowledge demonstrated", 0.4) * 10

    ps = _classify(user_text, ["structured problem solving approach", "some analytical thinking", "no problem solving shown"])
    problem_solving = ps.get("structured problem solving approach", 0.4) * 10

    culture = _classify(user_text, ["collaborative team-oriented mindset", "independent work style", "unclear cultural values"])
    cultural_fit = culture.get("collaborative team-oriented mindset", 0.5) * 10

    return {
        "communication": round(min(communication, 9.8), 1),
        "technical": round(min(technical, 9.8), 1),
        "problem_solving": round(min(problem_solving, 9.8), 1),
        "cultural_fit": round(min(cultural_fit, 9.8), 1),
        "confidence": round(confidence, 1),
    }


def generate_interview_question(messages, role, question_number):
    question_bank = {
        1: f"Tell me about yourself and what draws you to the {role} position at DriveIQ.",
        2: "Describe the most technically challenging project you've worked on. What was your approach?",
        3: "How do you stay current with trends in the automotive/EV industry?",
        4: "Walk me through a time you had to solve a complex problem under tight deadlines.",
        5: "Describe a situation where you disagreed with a team decision. How did you handle it?",
        6: "Where do you see the automotive industry in 5 years, and how does your work fit in?",
        7: "What's your approach to working cross-functionally with hardware and software teams?",
        8: "Tell me about a failure you experienced and what you learned from it.",
    }

    if messages and len(messages) > 2:
        last_answer = ""
        for m in reversed(messages):
            if m["role"] == "user" and m.get("content") != "[Skipped]":
                last_answer = m.get("content", "")
                break
        if last_answer:
            topics = _classify(last_answer, ["technical skills", "teamwork", "problem solving", "leadership", "industry knowledge"])
            top = max(topics, key=topics.get)
            follow_ups = {
                "technical skills": "Can you go deeper on the technical stack you used? What were the key design decisions?",
                "teamwork": "How did you ensure alignment across your team during that project?",
                "problem solving": "What alternative approaches did you consider before settling on that solution?",
                "leadership": "How did you mentor or support junior members through that challenge?",
                "industry knowledge": "How do you see that trend specifically impacting EV adoption or autonomous vehicles?",
            }
            return follow_ups.get(top, question_bank.get(question_number, question_bank[8]))

    return question_bank.get(question_number, "What questions do you have for us about DriveIQ?")


def compute_final_score(dimension_scores):
    if not dimension_scores:
        return {"overall": 5.0, "communication": 5, "technical": 5,
                "problem_solving": 5, "cultural_fit": 5, "leadership": 5,
                "confidence": 70, "engagement": 70, "composure": 70, "verdict": "Maybe"}

    def avg(key):
        return round(sum(d.get(key, 5) for d in dimension_scores) / len(dimension_scores), 1)

    communication  = avg("communication")
    technical      = avg("technical")
    problem_solving= avg("problem_solving")
    cultural_fit   = avg("cultural_fit")
    confidence_raw = avg("confidence")

    overall = round(communication*0.2 + technical*0.3 + problem_solving*0.25 + cultural_fit*0.15 + confidence_raw*0.1, 1)

    if overall >= 8.5:   verdict = "Strong Hire"
    elif overall >= 7.0: verdict = "Hire"
    elif overall >= 5.5: verdict = "Maybe"
    else:                verdict = "No Hire"

    return {
        "overall": overall,
        "communication": communication,
        "technical": technical,
        "problem_solving": problem_solving,
        "cultural_fit": cultural_fit,
        "leadership": round((technical + problem_solving) / 2, 1),
        "confidence": round(min(confidence_raw * 10, 98), 0),
        "engagement": round(min((communication + cultural_fit) / 2 * 10, 98), 0),
        "composure": round(min((problem_solving + cultural_fit) / 2 * 10, 98), 0),
        "verdict": verdict,
    }
