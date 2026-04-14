#!/usr/bin/env python3
"""
draft_cover_letter.py — Generates a tailored cover letter using the Anthropic API
                         based on the user's resume data and a job description.

Usage:
    python3 draft_cover_letter.py \
        --resume path/to/resume.json \
        --job_title "Software Engineer" \
        --company "Acme Corp" \
        --job_description "We are looking for..." \
        [--output "cover_letter.txt"]

Output:
    Prints the cover letter to stdout (and saves to --output if provided).
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error

ANTHROPIC_API = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-20250514"


def load_resume(path: str) -> dict:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Resume file not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in resume file: {e}", file=sys.stderr)
        sys.exit(1)


def format_resume_for_prompt(resume: dict) -> str:
    basics = resume.get("basics", {})
    skills = resume.get("skills", [])
    experience = resume.get("experience", [])
    education = resume.get("education", [])
    projects = resume.get("projects", [])

    exp_str = "\n".join(
        f"  - {e.get('title','?')} at {e.get('company','?')} "
        f"({e.get('startDate','?')} – {e.get('endDate','present')}): "
        f"{e.get('description','')}"
        for e in experience[:4]
    )
    edu_str = "\n".join(
        f"  - {e.get('degree','?')} from {e.get('institution','?')} ({e.get('year','?')})"
        for e in education[:2]
    )
    proj_str = "\n".join(
        f"  - {p.get('name','?')}: {p.get('description','')[:100]}"
        for p in projects[:3]
    )

    return f"""
Name: {basics.get('name', 'Candidate')}
Location: {basics.get('location', '')}
Summary: {basics.get('summary', '')}

Skills: {', '.join(skills[:12])}

Experience:
{exp_str or '  (none listed)'}

Education:
{edu_str or '  (none listed)'}

Notable Projects:
{proj_str or '  (none listed)'}
""".strip()


def generate_cover_letter(resume: dict, job_title: str, company: str, job_desc: str) -> str:
    """Calls Anthropic API to generate a cover letter."""
    resume_text = format_resume_for_prompt(resume)
    name = resume.get("basics", {}).get("name", "the candidate")

    prompt = f"""You are a professional career coach writing a cover letter.

CANDIDATE RESUME:
{resume_text}

JOB DETAILS:
Role: {job_title}
Company: {company}
Job Description:
{job_desc[:2000]}

Write a concise, compelling cover letter for {name} applying to this role.
Requirements:
- Under 200 words
- Professional but warm tone — not robotic
- Hook: one sentence about why this specific company/role appeals to them
- Match: 2-3 specific skills/experiences that directly map to the job requirements (use concrete examples from their resume)
- Value add: one concrete achievement or result from their past work
- Close: a brief, confident call to action

Output ONLY the cover letter text — no subject line, no "Dear Hiring Manager", no metadata."""

    payload = {
        "model": MODEL,
        "max_tokens": 500,
        "messages": [{"role": "user", "content": prompt}],
    }

    req = urllib.request.Request(
        ANTHROPIC_API,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
            # No API key needed — handled by OpenClaw environment
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["content"][0]["text"].strip()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"ERROR: Anthropic API {e.code} — {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Network error — {e.reason}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Generate a tailored cover letter")
    parser.add_argument("--resume", required=True, help="Path to resume JSON file")
    parser.add_argument("--job_title", required=True, help="Job title")
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--job_description", required=True, help="Job description text")
    parser.add_argument("--output", help="Save cover letter to this file path (optional)")
    args = parser.parse_args()

    resume = load_resume(args.resume)

    print(f"Generating cover letter for {args.job_title} at {args.company}...", file=sys.stderr)
    letter = generate_cover_letter(
        resume=resume,
        job_title=args.job_title,
        company=args.company,
        job_desc=args.job_description,
    )

    print(letter)

    if args.output:
        with open(args.output, "w") as f:
            f.write(letter)
        print(f"\n✅ Saved to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
  
