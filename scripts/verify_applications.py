#!/usr/bin/env python3
"""
Verify tracker rows against the portal's OWN record of what you applied to.

    python3 scripts/verify_applications.py                 # today
    python3 scripts/verify_applications.py --date 2026-08-01
    python3 scripts/verify_applications.py --limit 40

Why this exists: everything else in the pipeline trusts the portal's success text
at submit time. That is a reasonable signal, but it is our reading of their page.
This checks the other direction — does LinkedIn's "My Jobs → Applied" list actually
contain the jobs we recorded? A row we wrote that the portal does not know about
means the application did not land, and the tracker is lying to us.

Read-only. Opens its own tab and closes it; never touches yours.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vault_browser as vb

VAULT_ROOT = Path(__file__).resolve().parents[1]
TRACKER = VAULT_ROOT / "active_application_context" / "job_applications_tracker.md"
APPLIED_URL = "https://www.linkedin.com/my-items/saved-jobs/?cardType=APPLIED"

_JOB_ID = re.compile(r"/jobs/view/(\d+)")


def tracker_rows(day: str) -> list[tuple[str, str, str]]:
    """(job_id, company, role) for LinkedIn rows recorded as applied on `day`."""
    if not TRACKER.exists():
        return []
    out = []
    for line in TRACKER.read_text(encoding="utf-8", errors="replace").splitlines():
        if day not in line or "linkedin.com/jobs/view" not in line:
            continue
        if "Applied" not in line or "ALREADY" in line:
            continue
        m = _JOB_ID.search(line)
        if not m:
            continue
        company = re.search(r"\*\*Company:\*\*\s*([^|]+)", line)
        role = re.search(r"\*\*Role:\*\*\s*([^|]+)", line)
        out.append((m.group(1),
                    (company.group(1).strip() if company else "?"),
                    (role.group(1).strip() if role else "?")))
    return out


def portal_applied_ids(limit: int) -> set[str]:
    from playwright.sync_api import sync_playwright

    found: set[str] = set()
    with sync_playwright() as pw:
        browser, ctx = vb.connect_cdp(pw)
        pages: dict = {}
        page = vb.named_page(ctx, "verify", pages)
        try:
            page.goto(APPLIED_URL, wait_until="domcontentloaded", timeout=40000)
            page.wait_for_timeout(4000)
            kind = vb.detect_security_challenge(page)
            if kind:
                print(f"  ! cannot verify — {kind} on the applied-jobs page")
                return found
            for _ in range(max(1, limit // 10)):
                hrefs = page.evaluate(
                    """() => Array.from(document.querySelectorAll("a[href*='/jobs/view/']"))
                              .map(a => a.getAttribute('href'))"""
                )
                for h in hrefs or []:
                    m = _JOB_ID.search(h or "")
                    if m:
                        found.add(m.group(1))
                page.evaluate("() => window.scrollBy(0, 1400)")
                page.wait_for_timeout(1200)
        finally:
            try:
                page.close()
            except Exception:
                pass
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--limit", type=int, default=40)
    args = ap.parse_args()

    rows = tracker_rows(args.date)
    if not rows:
        print(f"  no LinkedIn applied rows recorded on {args.date}")
        return 0

    print(f"  tracker says {len(rows)} LinkedIn application(s) on {args.date}")
    portal = portal_applied_ids(args.limit)
    if not portal:
        print("  ! portal list empty or unreadable — cannot confirm either way")
        return 2
    print(f"  portal 'Applied' list shows {len(portal)} job(s)\n")

    confirmed = [r for r in rows if r[0] in portal]
    missing = [r for r in rows if r[0] not in portal]
    for jid, company, role in confirmed:
        print(f"  ✓ {company[:30]:<32} {role[:44]}")
    for jid, company, role in missing:
        print(f"  ✗ NOT ON PORTAL  {company[:26]:<28} {role[:40]}  (id {jid})")

    print(f"\n  {len(confirmed)}/{len(rows)} confirmed by the portal itself")
    if missing:
        print("  Rows the portal does not know about mean the tracker overstates reality.")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
