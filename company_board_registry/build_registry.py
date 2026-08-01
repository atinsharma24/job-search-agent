#!/usr/bin/env python3
"""Turn probe results into the structured registry files (one per ATS)."""
import json, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROBE = HERE
REG = HERE

TODAY = datetime.date.today().isoformat()

verified = json.loads((PROBE / "verified.json").read_text())
failed = json.loads((PROBE / "failed.json").read_text())

BASE = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
    "lever": "https://api.lever.co/v0/postings/{slug}",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{slug}",
    "workable": "https://apply.workable.com/api/v3/accounts/{slug}/jobs",
}
# query params (GET) or method note that also return full descriptions / comp when polling
CONTENT_HINT = {
    "greenhouse": "?content=true",
    "lever": "?mode=json",
    "ashby": "?includeCompensation=true",
    "workable": "POST with JSON body {\"query\":\"\",\"department\":[],...}; paginate via token",
}

buckets = {"greenhouse": [], "lever": [], "ashby": [], "workable": []}
for v in verified:
    ats = v["ats"]
    buckets[ats].append({
        "company": v["name"],
        "ats": ats,
        "slug": v["slug"],
        "endpoint": BASE[ats].format(slug=v["slug"]),
        "open_roles_at_verification": v["open_roles"],
        "verified_on": TODAY,
    })

for ats, rows in buckets.items():
    rows.sort(key=lambda r: r["company"].lower())
    payload = {
        "ats": ats,
        "base_endpoint": BASE[ats],
        "content_query_hint": CONTENT_HINT[ats],
        "verified_on": TODAY,
        "count": len(rows),
        "companies": rows,
    }
    (REG / f"{ats}.json").write_text(json.dumps(payload, indent=2) + "\n")

# needs manual check
manual = {
    "verified_on": TODAY,
    "reason": ("No public Greenhouse/Lever/Ashby JSON feed resolved after probing "
               "obvious slug variants across all three platforms. These companies "
               "likely run Workday, Keka, Darwinbox, SmartRecruiters, Freshteam, or a "
               "custom/JS-embedded careers board. Re-check the live careers page by hand "
               "before adding."),
    "named_targets_checked": {
        "Signzy": "custom /careers page, no GH/Lever/Ashby embed",
        "Yellow.ai": "JS-rendered careers portal, no public feed found",
        "Leegality": "careers page not resolvable via public feed",
        "Digio": "careers page not resolvable via public feed",
    },
    "count": len(failed),
    "companies": sorted(failed, key=str.lower),
}
(REG / "needs_manual_check.json").write_text(json.dumps(manual, indent=2) + "\n")

print("Wrote registry files:")
for ats in buckets:
    print(f"  {ats}.json -> {len(buckets[ats])} companies")
print(f"  needs_manual_check.json -> {len(failed)} companies")
