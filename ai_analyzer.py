"""
Uses Claude API to analyze job descriptions against Gaurav's resume.
Returns ATS score, strengths, and gaps for each job.
"""

import os
import json
import re
import anthropic
from resume_data import RESUME_TEXT


def analyze_job(job: dict) -> dict:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    prompt = f"""You are an expert ATS resume analyst for UX/Product Design roles.

RESUME:
{RESUME_TEXT}

JOB TITLE: {job['title']}
COMPANY: {job['company']}
LOCATION: {job['location']}
JOB DESCRIPTION:
{job['description'][:4000]}

Respond ONLY in this JSON format:
{{
  "ats_score": <integer 0-100>,
  "strengths": ["<s1>", "<s2>", "<s3>"],
  "gaps": ["<g1>", "<g2>", "<g3>"],
  "tailoring_tips": ["<tip1>", "<tip2>"],
  "tailored_summary": "<3-sentence tailored summary in first person>"
}}"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = message.content[0].text.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if m:
            return json.loads(m.group())
        return {
            "ats_score": 70,
            "strengths": ["UX experience", "Portfolio", "Design tools"],
            "gaps": ["Could not parse response"],
            "tailoring_tips": ["Review JD manually"],
            "tailored_summary": f"UX Designer applying for {job['title']} at {job['company']}."
        }
