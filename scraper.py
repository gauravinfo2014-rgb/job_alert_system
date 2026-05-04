
"""
Job scraper for 11 target companies.
Catches all UX/Product design roles regardless of level or naming convention.
"""

import requests, json, os, time
from datetime import datetime
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

# Broad keyword matching — catches any level/seniority variant
TARGET_KEYWORDS = [
    "ux designer", "ux design",
    "product designer", "product design",
    "ux/ui designer", "ui/ux designer",
    "experience designer", "user experience designer",
    "interaction designer",
    "visual designer",
    "digital designer",
    "design lead",
    "lead designer",
    "principal designer",
    "staff designer",
]

# Search terms sent to each company API — broad enough to surface all levels
# (Senior, II, III, Lead, Principal, Staff, etc.)
SEARCH_QUERIES = ["UX Designer", "Product Designer", "UX Design", "Product Design"]

SEEN_JOBS_FILE = "seen_jobs.json"


def load_seen_jobs():
    if os.path.exists(SEEN_JOBS_FILE):
        with open(SEEN_JOBS_FILE) as f:
            return set(json.load(f))
    return set()


def save_seen_jobs(seen):
    with open(SEEN_JOBS_FILE, "w") as f:
        json.dump(list(seen), f)


def is_relevant(title: str) -> bool:
    t = title.lower()
    return any(kw in t for kw in TARGET_KEYWORDS)


# ── GREENHOUSE (Tesla, Adobe, Razorpay, Emirates) ─────────────────────────────

def scrape_greenhouse(slug, name):
    jobs = []
    try:
        r = requests.get(
            f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true",
            headers=HEADERS, timeout=15
        )
        r.raise_for_status()
        for job in r.json().get("jobs", []):
            title = job.get("title", "")
            if is_relevant(title):
                loc = (job.get("offices") or [{}])[0].get("name", "") or job.get("location", {}).get("name", "")
                jobs.append({
                    "id": f"{slug}_{job['id']}",
                    "company": name,
                    "title": title,
                    "location": loc,
                    "url": job.get("absolute_url", ""),
                    "description": BeautifulSoup(job.get("content", ""), "html.parser").get_text(separator="\n")[:3000],
                    "posted_at": job.get("updated_at", ""),
                })
    except Exception as e:
        print(f"[Greenhouse/{name}] {e}")
    return jobs


# ── MICROSOFT ─────────────────────────────────────────────────────────────────

def scrape_microsoft():
    jobs = []
    seen_ids = set()
    try:
        for kw in SEARCH_QUERIES:
            r = requests.get(
                "https://gcsservices.careers.microsoft.com/search/api/v1/search",
                params={"q": kw, "l": "en_us", "pg": 1, "pgSz": 20, "o": "Relevance", "flt": True},
                headers=HEADERS, timeout=15
            )
            r.raise_for_status()
            for job in r.json().get("operationResult", {}).get("result", {}).get("jobs", []):
                title = job.get("title", "")
                jid = job.get("jobId", "")
                if is_relevant(title) and jid not in seen_ids:
                    seen_ids.add(jid)
                    jobs.append({
                        "id": f"microsoft_{jid}",
                        "company": "Microsoft",
                        "title": title,
                        "location": job.get("location", ""),
                        "url": f"https://jobs.careers.microsoft.com/global/en/job/{jid}",
                        "description": job.get("description", "")[:3000],
                        "posted_at": job.get("postingDate", ""),
                    })
            time.sleep(1)
    except Exception as e:
        print(f"[Microsoft] {e}")
    return jobs


# ── APPLE ─────────────────────────────────────────────────────────────────────

def scrape_apple():
    jobs = []
    seen_ids = set()
    try:
        for kw in SEARCH_QUERIES:
            r = requests.get(
                "https://jobs.apple.com/api/role/search",
                params={"page": 1, "locale": "en-us", "query": kw},
                headers=HEADERS, timeout=15
            )
            r.raise_for_status()
            for job in r.json().get("searchResults", []):
                title = job.get("postingTitle", "")
                jid = job.get("positionId", "")
                if is_relevant(title) and jid not in seen_ids:
                    seen_ids.add(jid)
                    jobs.append({
                        "id": f"apple_{jid}",
                        "company": "Apple",
                        "title": title,
                        "location": job.get("location", ""),
                        "url": f"https://jobs.apple.com/en-us/details/{jid}",
                        "description": job.get("jobSummary", "")[:3000],
                        "posted_at": job.get("postDate", ""),
                    })
            time.sleep(1)
    except Exception as e:
        print(f"[Apple] {e}")
    return jobs


# ── GOOGLE ────────────────────────────────────────────────────────────────────

def scrape_google():
    jobs = []
    seen_ids = set()
    try:
        for kw in SEARCH_QUERIES:
            r = requests.get(
                "https://careers.google.com/api/v3/search/",
                params={"q": kw, "hl": "en_US", "employment_type": "FULL_TIME", "page_size": 20, "page": 1},
                headers=HEADERS, timeout=15
            )
            r.raise_for_status()
            for job in r.json().get("jobs", []):
                title = job.get("title", "")
                jid = job.get("job_id", "").replace("/", "").replace("jobs/", "")
                if is_relevant(title) and jid not in seen_ids:
                    seen_ids.add(jid)
                    loc = (job.get("locations") or [{}])[0].get("display", "")
                    jobs.append({
                        "id": f"google_{jid}",
                        "company": "Google",
                        "title": title,
                        "location": loc,
                        "url": f"https://careers.google.com/jobs/results/{jid}",
                        "description": job.get("description", "")[:3000],
                        "posted_at": job.get("publish_date", ""),
                    })
            time.sleep(1)
    except Exception as e:
        print(f"[Google] {e}")
    return jobs


# ── AMAZON ────────────────────────────────────────────────────────────────────

def scrape_amazon():
    jobs = []
    seen_ids = set()
    try:
        for kw in SEARCH_QUERIES:
            r = requests.get(
                "https://www.amazon.jobs/en/search.json",
                params={"query": kw, "result_limit": 20, "offset": 0},
                headers=HEADERS, timeout=15
            )
            r.raise_for_status()
            for job in r.json().get("jobs", []):
                title = job.get("title", "")
                jid = job.get("id_icims", "")
                if is_relevant(title) and jid not in seen_ids:
                    seen_ids.add(jid)
                    jobs.append({
                        "id": f"amazon_{jid}",
                        "company": "Amazon",
                        "title": title,
                        "location": job.get("location", ""),
                        "url": f"https://www.amazon.jobs{job.get('job_path', '')}",
                        "description": job.get("description", "")[:3000],
                        "posted_at": job.get("posted_date", ""),
                    })
            time.sleep(1)
    except Exception as e:
        print(f"[Amazon] {e}")
    return jobs


# ── SINGAPORE AIRLINES ────────────────────────────────────────────────────────

def scrape_singapore_airlines():
    jobs = []
    try:
        for kw in ["UX+Designer", "Product+Designer", "UX+Design", "Product+Design"]:
            r = requests.get(
                f"https://careers.singaporeair.com/search/?q={kw}",
                headers=HEADERS, timeout=15
            )
            soup = BeautifulSoup(r.text, "html.parser")
            for item in soup.select(".job-result-item,.job-tile,article.job"):
                tel = item.select_one("h2,h3,.job-title,a")
                if tel:
                    title = tel.get_text(strip=True)
                    if is_relevant(title):
                        link = item.find("a")
                        href = link["href"] if link else ""
                        if href and not href.startswith("http"):
                            href = "https://careers.singaporeair.com" + href
                        uid = f"sia_{hash(title+href)}"
                        if uid not in [j["id"] for j in jobs]:
                            jobs.append({
                                "id": uid,
                                "company": "Singapore Airlines",
                                "title": title,
                                "location": "Singapore",
                                "url": href,
                                "description": f"Role: {title} at Singapore Airlines.",
                                "posted_at": datetime.now().isoformat(),
                            })
            time.sleep(1)
    except Exception as e:
        print(f"[Singapore Airlines] {e}")
    return jobs


# ── AIR INDIA ─────────────────────────────────────────────────────────────────

def scrape_air_india():
    jobs = []
    try:
        for kw in ["UX+Designer", "Product+Designer", "UX+Design", "Product+Design"]:
            r = requests.get(
                f"https://careers.airindia.com/search/?q={kw}",
                headers=HEADERS, timeout=15
            )
            soup = BeautifulSoup(r.text, "html.parser")
            for item in soup.select(".job-listing-item,.job-tile,.job-result"):
                tel = item.select_one("h2,h3,.job-title,a.job-link")
                if tel:
                    title = tel.get_text(strip=True)
                    if is_relevant(title):
                        link = item.find("a")
                        href = link["href"] if link else ""
                        if href and not href.startswith("http"):
                            href = "https://careers.airindia.com" + href
                        uid = f"airindia_{hash(title+href)}"
                        if uid not in [j["id"] for j in jobs]:
                            jobs.append({
                                "id": uid,
                                "company": "Air India",
                                "title": title,
                                "location": "India",
                                "url": href,
                                "description": f"Role: {title} at Air India.",
                                "posted_at": datetime.now().isoformat(),
                            })
            time.sleep(1)
    except Exception as e:
        print(f"[Air India] {e}")
    return jobs


# ── UNITED AIRLINES ───────────────────────────────────────────────────────────

def scrape_united_airlines():
    jobs = []
    seen_ids = set()
    try:
        for kw in SEARCH_QUERIES:
            r = requests.get(
                "https://careers.united.com/api/jobs",
                params={"keyword": kw, "page": 1, "pagesize": 20},
                headers=HEADERS, timeout=15
            )
            r.raise_for_status()
            for job in r.json().get("jobs", r.json().get("results", [])):
                title = job.get("title", job.get("Title", ""))
                jid = str(job.get("id", job.get("Id", "")))
                if is_relevant(title) and jid not in seen_ids:
                    seen_ids.add(jid)
                    jobs.append({
                        "id": f"united_{jid}",
                        "company": "United Airlines",
                        "title": title,
                        "location": job.get("location", ""),
                        "url": f"https://careers.united.com/job/{jid}",
                        "description": job.get("description", "")[:3000],
                        "posted_at": job.get("posted_date", ""),
                    })
            time.sleep(1)
    except Exception as e:
        print(f"[United Airlines] {e}")
    return jobs


# ── ORCHESTRATOR ──────────────────────────────────────────────────────────────

def scrape_all():
    print(f"[{datetime.now().isoformat()}] Starting scrape...")
    seen = load_seen_jobs()
    all_new = []

    scrapers = [
        ("Microsoft",         scrape_microsoft),
        ("Apple",             scrape_apple),
        ("Tesla",             lambda: scrape_greenhouse("tesla", "Tesla")),
        ("Google",            scrape_google),
        ("Adobe",             lambda: scrape_greenhouse("adobe", "Adobe")),
        ("Razorpay",          lambda: scrape_greenhouse("razorpay", "Razorpay")),
        ("Amazon",            scrape_amazon),
        ("Emirates",          lambda: scrape_greenhouse("emiratesgroup", "Emirates")),
        ("Singapore Airlines",scrape_singapore_airlines),
        ("Air India",         scrape_air_india),
        ("United Airlines",   scrape_united_airlines),
    ]

    for name, fn in scrapers:
        print(f"  Scraping {name}...")
        try:
            for job in fn():
                if job["id"] not in seen:
                    all_new.append(job)
                    seen.add(job["id"])
        except Exception as e:
            print(f"  ERROR [{name}]: {e}")
        time.sleep(2)

    save_seen_jobs(seen)
    print(f"Total new: {len(all_new)}")
    return all_new
