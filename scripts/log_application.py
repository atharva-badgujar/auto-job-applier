#!/usr/bin/env python3
"""
log_application.py — Logs a job application to the resumex.dev job tracker.

Usage:
    python3 log_application.py \
        --company "Acme Corp" \
        --role "Software Engineer" \
        --url "https://linkedin.com/jobs/view/12345" \
        --status "applied" \
        [--cover_letter "path/to/cover.txt"] \
        [--score 87] \
        [--notes "Extra notes here"]

Environment variables:
    RESUMEX_API_KEY   (required)

Valid status values:
    wishlist | applied | interview | offer | rejected
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from datetime import date

API_BASE = "https://resumex.dev/api/v1/agent"
VALID_STATUSES = {"wishlist", "applied", "interview", "offer", "rejected"}


def get_api_key():
    key = os.environ.get("RESUMEX_API_KEY", "").strip()
    if not key:
        print("ERROR: RESUMEX_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)
    return key


def log_application(api_key: str, payload: dict) -> dict:
    url = f"{API_BASE}/jobs"
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
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
        body_text = e.read().decode("utf-8", errors="replace")
        print(f"ERROR: HTTP {e.code} — {e.reason}\n{body_text}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Network error — {e.reason}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Log a job application to resumex.dev")
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--role", required=True, help="Job title / position")
    parser.add_argument("--url", required=True, help="Job posting URL")
    parser.add_argument(
        "--status",
        default="applied",
        choices=list(VALID_STATUSES),
        help="Application status (default: applied)",
    )
    parser.add_argument("--cover_letter", help="Path to cover letter text file (optional)")
    parser.add_argument("--score", type=int, help="Match score 0-100 (optional)")
    parser.add_argument("--notes", default="", help="Extra notes (optional)")
    args = parser.parse_args()

    # Build notes string
    notes_parts = []
    if args.score is not None:
        notes_parts.append(f"Match score: {args.score}/100.")
    if args.notes:
        notes_parts.append(args.notes)
    notes_parts.append("Applied via Auto Job Applier skill.")
    notes = " ".join(notes_parts)

    # Optionally read cover letter
    cover_letter_text = ""
    if args.cover_letter:
        try:
            with open(args.cover_letter, "r") as f:
                cover_letter_text = f.read().strip()
        except FileNotFoundError:
            print(f"WARNING: Cover letter file not found: {args.cover_letter}", file=sys.stderr)

    payload = {
        "company": args.company,
        "position": args.role,
        "url": args.url,
        "status": args.status,
        "appliedDate": date.today().isoformat(),
        "notes": notes,
    }
    if cover_letter_text:
        payload["coverLetter"] = cover_letter_text

    api_key = get_api_key()
    print(f"Logging application: {args.role} at {args.company}...", file=sys.stderr)
    result = log_application(api_key, payload)

    print(json.dumps(result, indent=2))
    print(f"\n✅ Logged: {args.role} @ {args.company} — Status: {args.status}", file=sys.stderr)


if __name__ == "__main__":
    main()
