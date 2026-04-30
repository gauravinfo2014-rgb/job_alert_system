"""
Main orchestrator — run by GitHub Actions every 2 hours.
1. Scrape all 11 companies for new UX/Product Designer jobs
2. For each new job: Claude AI analysis + tailored Word resume
3. Send email with all results and attached resumes
"""

import os
import sys
import tempfile
from scraper import scrape_all
from ai_analyzer import analyze_job
from resume_generator import generate_resume
from emailer import send_alert


def main():
    print("=" * 60)
    print("  JOB ALERT SYSTEM — Gaurav's UX/Product Design Tracker")
    print("=" * 60)

    new_jobs = scrape_all()

    if not new_jobs:
        print("\n✓ No new jobs found this run. Nothing to send.")
        return

    print(f"\n✓ Found {len(new_jobs)} new job(s). Analyzing with Claude AI...\n")

    jobs_with_analysis = []
    resume_paths = []

    with tempfile.TemporaryDirectory() as tmp_dir:
        for i, job in enumerate(new_jobs, 1):
            print(f"[{i}/{len(new_jobs)}] {job['company']} — {job['title']}")
            try:
                analysis = analyze_job(job)
                print(f"  ATS Score: {analysis.get('ats_score', '?')}/100")
            except Exception as e:
                print(f"  WARNING: AI analysis failed: {e}")
                analysis = {
                    "ats_score": 65,
                    "strengths": ["UX design experience", "Portfolio available"],
                    "gaps": ["Unable to analyze — review manually"],
                    "tailoring_tips": ["Tailor summary to this role", "Highlight relevant projects"],
                    "tailored_summary": f"Experienced UX/Product Designer applying for {job['title']} at {job['company']}.",
                }
            try:
                resume_path = generate_resume(job, analysis, output_dir=tmp_dir)
                resume_paths.append(resume_path)
            except Exception as e:
                print(f"  WARNING: Resume generation failed: {e}")

            jobs_with_analysis.append({"job": job, "analysis": analysis})

        print(f"\nSending email to gaurav.info2014@gmail.com...")
        success = send_alert(jobs_with_analysis, resume_paths)
        if success:
            print("\n✓ All done!")
        else:
            print("\n✗ Email failed — check GMAIL_APP_PASSWORD secret.")
            sys.exit(1)


if __name__ == "__main__":
    missing = [v for v in ["ANTHROPIC_API_KEY", "GMAIL_APP_PASSWORD"] if not os.environ.get(v)]
    if missing:
        print(f"ERROR: Missing env vars: {', '.join(missing)}")
        sys.exit(1)
    main()
