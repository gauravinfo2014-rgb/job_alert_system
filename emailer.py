"""
Sends job alert emails with tailored resumes to gaurav.info2014@gmail.com
Uses Gmail SMTP with an App Password stored in GitHub Secrets.
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime

RECIPIENT_EMAIL = "gaurav.info2014@gmail.com"


def ats_color(score):
    if score >= 75: return "#16A34A"
    elif score >= 60: return "#D97706"
    return "#DC2626"


def build_html_body(jobs_with_analysis):
    job_blocks = ""
    for item in jobs_with_analysis:
        job = item["job"]
        analysis = item["analysis"]
        score = analysis.get("ats_score", 0)
        strengths_html = "".join(f"<li>✓ {s}</li>" for s in analysis.get("strengths", []))
        gaps_html = "".join(f"<li>⚠ {g}</li>" for g in analysis.get("gaps", [])) or "<li>No significant gaps</li>"
        tips_html = "".join(f"<li>💡 {t}</li>" for t in analysis.get("tailoring_tips", []))
        color = ats_color(score)
        job_blocks += f"""
        <div style="background:#fff;border:1px solid #E2E8F0;border-radius:12px;padding:24px;margin-bottom:24px;">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;">
            <div>
              <h2 style="margin:0;font-size:18px;color:#1E293B;">{job['title']}</h2>
              <p style="margin:4px 0 0;font-size:14px;color:#64748B;">🏢 {job['company']} &nbsp;|&nbsp; 📍 {job.get('location','See listing')}</p>
            </div>
            <div style="background:{color};color:#fff;border-radius:50%;width:56px;height:56px;display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:700;text-align:center;line-height:1.2;">{score}<br><span style="font-size:9px;">/100</span></div>
          </div>
          <hr style="border:none;border-top:1px solid #F1F5F9;margin:16px 0;">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
            <div><p style="margin:0 0 6px;font-size:12px;font-weight:600;color:#16A34A;text-transform:uppercase;">Strengths</p>
              <ul style="margin:0;padding-left:16px;font-size:13px;color:#374151;line-height:1.8;">{strengths_html}</ul></div>
            <div><p style="margin:0 0 6px;font-size:12px;font-weight:600;color:#D97706;text-transform:uppercase;">Gaps</p>
              <ul style="margin:0;padding-left:16px;font-size:13px;color:#374151;line-height:1.8;">{gaps_html}</ul></div>
          </div>
          <div style="margin-top:16px;background:#F8FAFC;border-radius:8px;padding:12px;">
            <p style="margin:0 0 6px;font-size:12px;font-weight:600;color:#3B82F6;text-transform:uppercase;">AI Tailoring Tips</p>
            <ul style="margin:0;padding-left:16px;font-size:13px;color:#374151;line-height:1.8;">{tips_html}</ul>
          </div>
          <div style="margin-top:16px;text-align:center;">
            <a href="{job.get('url','#')}" style="background:#2563EB;color:#fff;padding:10px 24px;border-radius:8px;text-decoration:none;font-size:14px;font-weight:600;display:inline-block;">View Job & Apply →</a>
          </div>
          <p style="margin:12px 0 0;font-size:11px;color:#94A3B8;text-align:center;">📎 Tailored resume attached</p>
        </div>"""

    return f"""<!DOCTYPE html><html><head><meta charset="UTF-8"></head>
    <body style="margin:0;padding:0;background:#F1F5F9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
      <div style="max-width:680px;margin:0 auto;padding:24px 16px;">
        <div style="background:linear-gradient(135deg,#1D4ED8,#7C3AED);border-radius:12px;padding:28px;margin-bottom:24px;text-align:center;color:#fff;">
          <h1 style="margin:0;font-size:24px;">🎯 New UX/Design Job Alerts</h1>
          <p style="margin:8px 0 0;opacity:0.85;font-size:14px;">{len(jobs_with_analysis)} new role(s) found · {datetime.now().strftime("%b %d, %Y")}</p>
        </div>
        {job_blocks}
        <div style="text-align:center;padding:16px;font-size:11px;color:#94A3B8;">Powered by Claude AI · GitHub Actions · Every 2 hours</div>
      </div></body></html>"""


def send_alert(jobs_with_analysis, resume_paths):
    gmail_user = os.environ.get("GMAIL_USER", RECIPIENT_EMAIL)
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD", "")
    if not gmail_password:
        print("[Email] ERROR: GMAIL_APP_PASSWORD not set")
        return False

    count = len(jobs_with_analysis)
    companies = ", ".join(set(i["job"]["company"] for i in jobs_with_analysis[:3]))
    subject = f"🎯 {count} New UX/Design Job{'s' if count>1 else ''} — {companies}"
    if count > 3: subject += f" +{count-3} more"

    msg = MIMEMultipart("mixed")
    msg["From"] = gmail_user
    msg["To"] = RECIPIENT_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(build_html_body(jobs_with_analysis), "html"))

    for path in resume_paths:
        if os.path.exists(path):
            with open(path, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(path))
            part["Content-Disposition"] = f'attachment; filename="{os.path.basename(path)}"'
            msg.attach(part)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, RECIPIENT_EMAIL, msg.as_string())
        print(f"[Email] ✓ Sent to {RECIPIENT_EMAIL}")
        return True
    except Exception as e:
        print(f"[Email] ERROR: {e}")
        return False
