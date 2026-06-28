"""
DriveIQ Email Bot — Brevo (Sendinblue) API
─────────────────────────────────────────────────────────────────────────────
SETUP CHECKLIST (do once in your Brevo account):
  1. Go to https://app.brevo.com → Settings → Senders & IP → Senders
  2. Add and VERIFY a sender email (e.g. yourname@gmail.com or your domain).
  3. Set BREVO_SENDER_EMAIL env var to that verified address.
  4. Set BREVO_API_KEY env var to your API key from Brevo → SMTP & API → API Keys.

Without a verified sender the API returns 400/403.
─────────────────────────────────────────────────────────────────────────────
"""

import os
import requests

BREVO_API_KEY    = os.environ.get("BREVO_API_KEY", "")
BREVO_SENDER_EMAIL = os.environ.get("BREVO_SENDER_EMAIL", "")   # must be verified in Brevo
BREVO_SENDER_NAME  = "DriveIQ Recruitment"


def send_report(to_email: str, to_name: str, report_text: str) -> tuple[bool, str]:
    """
    Send interview report via Brevo.
    Returns (success: bool, message: str).
    """
    if not BREVO_API_KEY:
        return False, "BREVO_API_KEY not set in environment variables."

    if not BREVO_SENDER_EMAIL:
        return False, "BREVO_SENDER_EMAIL not set. Add a verified sender in your Brevo account."

    if not to_email:
        return False, "Applicant email address is missing."

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0;padding:0;background:#f4f4f4;font-family:Arial,sans-serif;">
      <div style="max-width:600px;margin:30px auto;background:#0D0D0D;color:#fff;
           border-radius:14px;overflow:hidden;">

        <!-- Header -->
        <div style="background:linear-gradient(90deg,#E63946,#c1121f);
             padding:28px 32px;text-align:center;">
          <h1 style="margin:0;font-size:2rem;letter-spacing:-1px;">
            Drive<span style="color:white;">IQ</span>
          </h1>
          <p style="margin:6px 0 0;font-size:0.85rem;opacity:0.85;">
            AI-Powered Automotive Recruitment
          </p>
        </div>

        <!-- Body -->
        <div style="padding:32px;">
          <h2 style="color:#fff;margin-top:0;">Hi {to_name},</h2>
          <p style="color:#aaa;line-height:1.65;">
            Thank you for completing your DriveIQ AI interview.
            Here is your personalised report card — we hope it gives you
            clear insight into your performance and next steps.
          </p>

          <!-- Report Box -->
          <div style="background:#1A1A1A;border:1px solid #333;border-radius:10px;
               padding:20px 24px;margin:20px 0;">
            <pre style="color:#ccc;font-size:0.85rem;font-family:monospace;
                 white-space:pre-wrap;margin:0;line-height:1.6;">{report_text}</pre>
          </div>

          <p style="color:#888;font-size:0.84rem;line-height:1.6;">
            Our team will review your report and be in touch within 3–5 business days.
            If you have questions, reply to this email or visit
            <a href="https://driveiq.ai" style="color:#E63946;">driveiq.ai</a>.
          </p>
        </div>

        <!-- Footer -->
        <div style="background:#060810;padding:18px 32px;text-align:center;
             border-top:1px solid #1a1a1a;">
          <p style="color:#555;font-size:0.78rem;margin:0;">
            © 2025 DriveIQ Technologies · San Jose · Munich · Tokyo<br>
            <a href="#" style="color:#555;">Unsubscribe</a> ·
            <a href="#" style="color:#555;">Privacy Policy</a>
          </p>
        </div>
      </div>
    </body>
    </html>
    """

    payload = {
        "sender": {"name": BREVO_SENDER_NAME, "email": BREVO_SENDER_EMAIL},
        "to": [{"email": to_email, "name": to_name}],
        "replyTo": {"email": BREVO_SENDER_EMAIL},
        "subject": f"Your DriveIQ Interview Report — {to_name}",
        "htmlContent": html_body,
    }

    try:
        r = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "accept": "application/json",
                "api-key": BREVO_API_KEY,
                "content-type": "application/json",
            },
            json=payload,
            timeout=20
        )

        if r.status_code in (200, 201):
            return True, f"Email sent to {to_email}"
        else:
            # Parse Brevo error
            try:
                err = r.json()
                msg = err.get("message", r.text)
            except Exception:
                msg = r.text
            return False, f"Brevo error {r.status_code}: {msg}"

    except requests.exceptions.Timeout:
        return False, "Email timed out — Brevo API unreachable."
    except Exception as e:
        return False, f"Email exception: {e}"


def build_report_text(applicant_data: dict, scores: dict) -> str:
    """Build the plain-text body for the email report."""
    name  = applicant_data.get("name", "").strip() or \
            f"{applicant_data.get('first_name','')} {applicant_data.get('last_name','')}".strip()
    role  = applicant_data.get("job_title") or applicant_data.get("target_role", "N/A")
    ra    = applicant_data.get("resume_analysis", {})

    strengths    = ra.get("strengths", ra.get("key_positives", []))
    improvements = ra.get("improvements", ra.get("areas_to_improve", []))

    def bar(score, out_of=10):
        filled = round(score / out_of * 20)
        return "█" * filled + "░" * (20 - filled)

    overall = scores.get("overall", 0)
    verdict = scores.get("verdict", "N/A")

    return f"""
╔══════════════════════════════════════════╗
║       DriveIQ Interview Report Card      ║
╚══════════════════════════════════════════╝

Candidate  : {name}
Role       : {role}
Date       : {__import__('datetime').datetime.now().strftime('%d %b %Y, %H:%M')}
Verdict    : {verdict}

┌─────────────────────────────────────────┐
│  OVERALL SCORE: {overall}/10             │
│  {bar(overall, 10)}  │
└─────────────────────────────────────────┘

── 5-DIMENSION BREAKDOWN ─────────────────
Communication    {scores.get('communication',0)}/10  {bar(scores.get('communication',0))}
Technical        {scores.get('technical',0)}/10  {bar(scores.get('technical',0))}
Problem Solving  {scores.get('problem_solving',0)}/10  {bar(scores.get('problem_solving',0))}
Cultural Fit     {scores.get('cultural_fit',0)}/10  {bar(scores.get('cultural_fit',0))}
Leadership       {scores.get('leadership',0)}/10  {bar(scores.get('leadership',0))}

── BEHAVIOURAL METRICS ───────────────────
Confidence  : {scores.get('confidence',0)}%
Engagement  : {scores.get('engagement',0)}%
Composure   : {scores.get('composure',0)}%

── RESUME ANALYSIS ───────────────────────
Overall Score         : {ra.get('overall_score', ra.get('relevance_score',0))} / 10
Authenticity          : {ra.get('authenticity_score',0)}%

── KEY STRENGTHS ─────────────────────────
{chr(10).join('✓ ' + s for s in strengths) if strengths else 'N/A'}

── GROWTH AREAS ──────────────────────────
{chr(10).join('→ ' + t for t in improvements) if improvements else 'N/A'}

══════════════════════════════════════════
DriveIQ AI Assessment · Bias-Free · Confidential
Questions? Reply to this email.
══════════════════════════════════════════
"""
