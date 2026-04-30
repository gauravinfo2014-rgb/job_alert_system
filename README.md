# UX/Product Design Job Alert System

Monitors 11 companies every 2 hours. Emails tailored resume + AI analysis to gaurav.info2014@gmail.com when a UX Designer or Product Designer role is posted.

## Companies
Microsoft · Apple · Tesla · Google · Adobe · Razorpay · Amazon · Emirates · Singapore Airlines · Air India · United Airlines

## Setup (3 steps)

### 1. Add GitHub Secrets
Go to repo Settings → Secrets and variables → Actions → New repository secret

| Secret | Value |
|---|---|
| ANTHROPIC_API_KEY | Get from console.anthropic.com (free $5 credit) |
| GMAIL_USER | gaurav.info2014@gmail.com |
| GMAIL_APP_PASSWORD | See step 2 |

### 2. Get Gmail App Password
1. Go to myaccount.google.com → Security
2. Enable 2-Step Verification
3. Search "App passwords" → Mail → Other → type "GitHub Actions"
4. Copy the 16-char password → paste as GMAIL_APP_PASSWORD secret

### 3. Update resume_data.py
Open resume_data.py and fill in your actual experience. The more detail, the better the AI tailoring.

## Test it
Actions tab → "UX Job Alert — 11 Companies" → Run workflow

## What you get in email
- ATS score (0-100) per job
- Strengths and gaps vs the JD
- AI tailoring tips
- Tailored .docx resume attached, ready to send

## Cost
~$0.01-0.03 per job analyzed via Claude API. GitHub Actions runs free.
