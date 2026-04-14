---
name: auto-job-applier
description: >
  Automatically find and apply to jobs that match the user's resume using the resumex.dev API.
  Use this skill whenever the user asks to: search for jobs, find job matches, auto-apply to jobs,
  apply for jobs automatically, find jobs based on my resume, or any variant of job hunting,
  job searching, or job application automation. Fetches the user's full resume data from resumex.dev,
  extracts skills/experience/preferences, searches for matching jobs on the web, drafts personalized
  cover letters, and logs applications to the user's resumex.dev job tracker. Always use this skill
  when the user mentions "apply to jobs", "job search", "find jobs for me", "auto apply", or
  "job hunting" — even if they haven't explicitly mentioned resumex.
requires:
  bins: [python3, curl]
  env:
    required:
      - RESUMEX_API_KEY   # Get from resumex.dev → Settings → API Keys
    optional:
      - JOB_SEARCH_LOCATION   # Default city/country for job search (e.g. "Pune, India")
      - JOB_TYPE              # full-time | part-time | contract | internship (default: full-time)
      - REMOTE_ONLY           # true | false (default: false)
---

# Auto Job Applier Skill

This skill connects to the user's **resumex.dev** account, reads their resume data, matches them
to relevant jobs via web search, drafts tailored cover letters, and optionally logs applications
to their resumex.dev job tracker — all in one automated flow.

---

## Workflow Overview

```
1. Fetch resume data from resumex.dev
2. Build a job-match profile (skills, roles, seniority, preferences)
3. Search the web for matching jobs
4. Score & rank each job against the resume
5. Draft personalized cover letters for top matches
6. Log applications to resumex.dev job tracker
7. Present a clean summary to the user
```

---

## Step 1 — Fetch Resume from resumex.dev

Use the agent endpoint. All calls require `Authorization: Bearer $RESUMEX_API_KEY`.

```bash
# Fetch full resume data
curl -s -X GET "https://resumex.dev/api/v1/agent/resume" \
  -H "Authorization: Bearer $RESUMEX_API_KEY" \
  -H "Content-Type: application/json"
```

Or via Python (see `scripts/fetch_resume.py`):

```python
python3 scripts/fetch_resume.py
```

**Expected response shape:**
```json
{
  "resume": {
    "basics": {
      "name": "...", "email": "...", "phone": "...",
      "location": "...", "summary": "..."
    },
    "skills": ["Python", "React", "..."],
    "experience": [
      {
        "title": "...", "company": "...",
        "startDate": "...", "endDate": "...",
        "description": "..."
      }
    ],
    "education": [ { "degree": "...", "institution": "...", "year": "..." } ],
    "projects": [ { "name": "...", "description": "...", "tech": ["..."] } ],
    "certifications": [ { "name": "...", "issuer": "..." } ]
  }
}
```

If the API returns a `401`, the `RESUMEX_API_KEY` is missing or invalid. Prompt the user to:
1. Go to **resumex.dev → Settings → API Keys**
2. Generate a new key
3. Set `RESUMEX_API_KEY` in their OpenClaw environment

---

## Step 2 — Build Job-Match Profile

From the resume JSON, extract and infer:

| Field | How to Derive |
|---|---|
| Target roles | Latest job title + adjacent titles (e.g. "Software Engineer" → also "Backend Developer", "Full Stack Developer") |
| Key skills | Top 5–8 from `skills` array + tech stack from `experience[].description` |
| Seniority | Years of experience calculated from earliest `startDate` to today |
| Location | `basics.location` (override with `JOB_SEARCH_LOCATION` env var if set) |
| Job type | `JOB_TYPE` env var (default: full-time) |
| Remote | `REMOTE_ONLY` env var (default: false) |
| Industry | Infer from company names / job descriptions in experience |

**Example derived profile:**
```
Roles: Software Engineer, Backend Developer, Full Stack Developer
Skills: Python, Django, React, PostgreSQL, Docker, AWS
Seniority: Mid-level (3 years)
Location: Pune, India
Type: Full-time
Remote: No preference
```

---

## Step 3 — Search for Matching Jobs

Use **web search** to find real, current job postings. Run 3–5 targeted searches using different
query permutations to maximize coverage.

**Query templates:**
```
"{role}" "{top_skill}" jobs "{location}" site:linkedin.com OR site:naukri.com OR site:indeed.com
"{role}" "{top_skill}" "{second_skill}" hiring 2025
"{role}" remote jobs "{top_skill}" "{seniority}"
```

**Per job posting, extract:**
- Job title
- Company name
- Location (or Remote)
- Job URL (apply link)
- Required skills (from description)
- Nice-to-have skills
- Experience required
- Salary range (if visible)
- Application method (Easy Apply / form / email)

Aim to collect **10–20 raw job postings** before scoring.

---

## Step 4 — Score & Rank Jobs

Score each job 0–100 against the resume profile:

| Factor | Max Points |
|---|---|
| Skill overlap (required skills matched) | 40 |
| Role title match | 20 |
| Seniority match | 15 |
| Location / remote match | 15 |
| Industry familiarity | 10 |

**Formula:**
```
score = (skills_matched / skills_required) * 40
      + role_title_match * 20    # 20 if exact, 10 if adjacent, 0 if unrelated
      + seniority_match * 15     # 15 if exact, 8 if ±1 level, 0 if 2+ off
      + location_match * 15      # 15 if match, 8 if remote, 0 if mismatch
      + industry_match * 10      # 10 if same industry, 5 if adjacent
```

Present the **top 5 matches** to the user, ordered by score.

---

## Step 5 — Draft Cover Letters

For each of the top 5 jobs, generate a tailored cover letter using the resume data and job
description. Use `scripts/draft_cover_letter.py` or inline generation.

**Cover letter structure:**
1. **Hook** (1 sentence): why this specific company/role excites the candidate
2. **Match** (2–3 sentences): 2–3 specific skills/experiences that directly map to job requirements
3. **Value add** (1–2 sentences): a concrete result from their past work
4. **Close** (1 sentence): call to action

Keep it under 200 words. Professional but human tone.

---

## Step 6 — Log Applications to resumex.dev

After user confirms which jobs to apply to, log each application to the resumex.dev job tracker:

```bash
python3 scripts/log_application.py \
  --company "Acme Corp" \
  --role "Software Engineer" \
  --url "https://linkedin.com/jobs/view/..." \
  --status "applied" \
  --cover_letter "path/to/cover_letter.txt"
```

Or via curl:

```bash
curl -s -X POST "https://resumex.dev/api/v1/agent/jobs" \
  -H "Authorization: Bearer $RESUMEX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Acme Corp",
    "position": "Software Engineer",
    "url": "https://linkedin.com/jobs/view/...",
    "status": "applied",
    "appliedDate": "2025-04-14",
    "notes": "Applied via Auto Job Applier skill. Match score: 87/100."
  }'
```

Valid `status` values: `wishlist` | `applied` | `interview` | `offer` | `rejected`

---

## Step 7 — Present Summary to User

Show a clean summary table:

```
🎯 Job Match Results for [Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

#  Company          Role                    Score  Location        Link
1  Acme Corp        Software Engineer       92/100 Pune (On-site)  [Apply →]
2  TechStartup      Backend Developer       87/100 Remote          [Apply →]
3  MegaCorp India   Full Stack Engineer     81/100 Mumbai          [Apply →]
4  DevShop          Python Developer        76/100 Pune (Hybrid)   [Apply →]
5  CloudCo          API Engineer            73/100 Remote          [Apply →]

✅ Applications logged to your resumex.dev tracker.
📄 Cover letters saved for each role.
```

Then ask: "Would you like me to apply to all of these, or select specific ones?"

---

## Error Handling

| Error | Response |
|---|---|
| `401 Unauthorized` | Ask user to check `RESUMEX_API_KEY` in OpenClaw environment |
| `404 Not Found` | Resume may not be set up on resumex.dev — prompt user to create one |
| `429 Rate Limited` | Wait 10s, retry once; if still limited, inform user |
| No jobs found | Broaden search: remove location filter, try adjacent roles |
| Web search blocked | Try alternate job boards (Naukri, Internshala, AngelList, etc.) |

---

## Important Notes

- **Auto-apply limits**: This skill drafts applications and logs them — it does NOT submit forms
  on job portals automatically (that would violate most ToS). Present the apply link + cover letter
  so the user can submit with one click.
- **Privacy**: Resume data is fetched live each run. No data is stored locally by this skill.
- **Freshness**: Job postings are searched live. Re-run the skill weekly for fresh listings.
- **Rate limits**: resumex.dev API has rate limits. Don't call the resume endpoint more than
  once per session — cache the result in memory for that session.

---

## Files in This Skill

| File | Purpose |
|---|---|
| `SKILL.md` | This file — instructions for Claude |
| `scripts/fetch_resume.py` | Fetches and parses resume from resumex.dev |
| `scripts/log_application.py` | Logs a job application to resumex.dev tracker |
| `scripts/draft_cover_letter.py` | Generates a cover letter given resume + job description |
| `references/job_boards.md` | List of job boards and their search URL patterns |
