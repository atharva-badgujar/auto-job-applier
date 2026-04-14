#!/usr/bin/env python3
"""
fetch_resume.py — Fetches and pretty-prints resume data from resumex.dev API.

Usage:
    python3 fetch_resume.py

Environment variables:
    RESUMEX_API_KEY   (required) API key from resumex.dev → Settings → API Keys

Output:
    Prints JSON resume data to stdout. Exits with code 1 on failure.
"""

import os
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime

API_BASE = "https://resumex.dev/api/v1/agent"


def get_api_key():
    key = os.environ.get("RESUMEX_API_KEY", "").strip()
    if not key:
        print(
            "ERROR: RESUMEX_API_KEY environment variable is not set.\n"
            "Steps to fix:\n"
            "  1. Go to https://resumex.dev → Settings → API Keys\n"
            "  2. Generate a new API key\n"
            "  3. Set RESUMEX_API_KEY in your OpenClaw environment variables",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def fetch_resume(api_key: str) -> dict:
    url = f"{API_BASE}/resume"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print(
                "ERROR: 401 Unauthorized. Your RESUMEX_API_KEY is invalid or expired.\n"
                "Please generate a new key at resumex.dev → Settings → API Keys",
                file=sys.stderr,
            )
        elif e.code == 404:
            print(
                "ERROR: 404 Not Found. Make sure your resume is set up at resumex.dev.",
                file=sys.stderr,
            )
        elif e.code == 429:
            print(
                "ERROR: 429 Rate Limited. Please wait a moment and try again.",
                file=sys.stderr,
            )
        else:
            print(f"ERROR: HTTP {e.code} — {e.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Network error — {e.reason}", file=sys.stderr)
        sys.exit(1)


def summarize_profile(resume: dict) -> str:
    """Return a plain-text job-match profile summary from resume data."""
    basics = resume.get("basics", {})
    skills = resume.get("skills", [])
    experience = resume.get("experience", [])
    
    name = basics.get("name", "Unknown")
    location = basics.get("location", "Not specified")

    # Calculate years of experience
    years = 0
    if experience:
        try:
            earliest = min(
                e["startDate"] for e in experience if e.get("startDate")
            )
            start_year = int(earliest[:4])
            years = datetime.now().year - start_year
        except (ValueError, KeyError):
            pass

    seniority = "Entry-level"
    if years >= 7:
        seniority = "Senior"
    elif years >= 3:
        seniority = "Mid-level"
    elif years >= 1:
        seniority = "Junior"

    # Get most recent title
    latest_title = ""
    if experience:
        latest_title = experience[0].get("title", "")

    summary = f"""
=== Job Match Profile for {name} ===
Location    : {location}
Latest Role : {latest_title}
Experience  : {years} years ({seniority})
Top Skills  : {", ".join(skills[:8]) if skills else "None listed"}
"""
    return summary.strip()


if __name__ == "__main__":
    api_key = get_api_key()
    print("Fetching resume from resumex.dev...", file=sys.stderr)
    data = fetch_resume(api_key)
    
    resume = data.get("resume", data)  # handle both wrapped and unwrapped responses
    
    # Print full JSON for Claude to parse
    print(json.dumps(resume, indent=2))
    
    # Also print human-readable summary to stderr
    print("\n" + summarize_profile(resume), file=sys.stderr)
