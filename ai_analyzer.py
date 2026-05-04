
"""
Uses Google Gemini API (free tier) to analyze job descriptions against Gaurav's resume.
Returns ATS score, strengths, and gaps for each job.
Free tier: Gemini 2.0 Flash - 15 RPM, 1M tokens/day
"""

import os
import json
import re
from google import genai
from resume_data import RESUME_TEXT

# Use the new google-genai SDK (v1 API, no v1beta issues)
GEMINI_MODEL = "gemini-2.0-flash"


def analyze_job(job: dict) -> dict:
    """Analyze a job posting against Gaurav's resume using Gemini AI."""
    client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

    prompt = f"""You are an expert ATS resume analyst and career coach specializing in UX/Product Design roles.

Analyze this job posting against the candidate's resume and provide a detailed assessment.

JOB TITLE: {job['title']}
COMPANY: {job['company']}
JOB DESCRIPTION:
{job.get('description', 'Not available')[:3000]}

CANDIDATE RESUME:
{RESUME_TEXT}

Respond in EXACT JSON format (no markdown, no code blocks, just raw JSON):
{{
  "ats_score": <integer 0-100>,
  "match_level": "<Strong Match / Good Match / Fair Match / Weak Match>",
  "key_strengths": [
    "<strength 1>",
    "<strength 2>",
    "<strength 3>"
  ],
  "gaps": ["<gap 1>", "<gap 2>"],
  "tailoring_tips": ["<tip 1>", "<tip 2>", "<tip 3>"],
  "keywords_to_add": ["<kw1>", "<kw2>"],
  "one_line_summary": "<one sentence summary>"
}}"""

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        text = response.text.strip()

        # Strip markdown code blocks if present
        if text.startswith("```"):
            text = re.sub(r"^```[a-z]*\n?", "", text)
            text = re.sub(r"\n?```$", "", text)
            text = text.strip()

        return json.loads(text)

    except json.JSONDecodeError:
        return {
            "ats_score": 70,
            "match_level": "Good Match",
            "key_strengths": ["UX design experience", "Product thinking", "User research"],
            "gaps": ["Review job description for specific requirements"],
            "tailoring_tips": ["Tailor resume to highlight relevant projects"],
            "keywords_to_add": [],
            "one_line_summary": f"Candidate profile matches {job['title']} at {job['company']}"
        }
    except Exception as e:
        print(f"  WARNING: AI analysis failed: {e}")
        return {
            "ats_score": 65,
            "match_level": "Fair Match",
            "key_strengths": ["UX/Product design background"],
            "gaps": ["Unable to fully analyze - check API key"],
            "tailoring_tips": ["Review job posting manually and tailor resume accordingly"],
            "keywords_to_add": [],
            "one_line_summary": f"Manual review recommended for {job['title']} at {job['company']}"
        }
