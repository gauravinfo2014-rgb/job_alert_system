
"""
Uses Google Gemini API (free tier) to analyze job descriptions against Gaurav's resume.
Returns ATS score, strengths, and gaps for each job.
Free tier: Gemini Flash — 15 RPM, 1M tokens/day
"""

import os
import json
import re
import google.generativeai as genai
from resume_data import RESUME_TEXT

# Model fallback list — tries each in order until one works
GEMINI_MODELS = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.0-pro",
    "gemini-pro",
]


def get_model():
    """Return the first available Gemini model."""
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    available = {m.name for m in genai.list_models()}
    for name in GEMINI_MODELS:
        full = f"models/{name}"
        if full in available or name in available:
            return genai.GenerativeModel(name)
    # Last resort — just try the first one and let the API error surface
    return genai.GenerativeModel(GEMINI_MODELS[0])


def analyze_job(job: dict) -> dict:
    """
    Send the JD + resume to Gemini and get back:
      - ats_score: int (0-100)
      - strengths: list[str]
      - gaps: list[str]
      - tailoring_tips: list[str]
      - tailored_summary: str
    """
    model = get_model()

    prompt = f"""You are an expert ATS resume analyst and career coach specializing in UX/Product Design roles.

RESUME:
{RESUME_TEXT}

JOB TITLE: {job['title']}
COMPANY: {job['company']}
LOCATION: {job['location']}
JOB DESCRIPTION:
{job['description'][:4000]}

Analyze how well this resume matches the job description and respond in this EXACT JSON format (no markdown, no extra text):
{{
  "ats_score": <integer 0-100>,
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "gaps": ["<gap 1>", "<gap 2>", "<gap 3>"],
  "tailoring_tips": ["<tip 1>", "<tip 2>"],
  "tailored_summary": "<3-sentence summary tailored for this role. First person. Highlight most relevant experience.>"
}}

ATS score rubric:
- 90-100: Near-perfect match
- 75-89: Strong match
- 60-74: Moderate match
- Below 60: Significant gaps"""

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # Strip markdown code fences if present
    raw = re.sub(r'^```(?:json)?\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw).strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            result = json.loads(match.group())
        else:
            result = {
                "ats_score": 70,
                "strengths": ["Resume analysis unavailable"],
                "gaps": ["Could not parse AI response"],
                "tailoring_tips": ["Review job description manually"],
                "tailored_summary": f"Experienced UX/Product Designer applying for {job['title']} at {job['company']}.",
            }

    return result


if __name__ == "__main__":
    test_job = {
        "title": "UX Designer",
        "company": "Google",
        "location": "Mountain View, CA",
        "description": "We are looking for a UX Designer. Figma proficiency required.",
    }
    result = analyze_job(test_job)
    print(f"ATS Score: {result['ats_score']}/100")
    print(f"Strengths: {result['strengths']}")
