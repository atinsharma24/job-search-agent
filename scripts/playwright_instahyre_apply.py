#!/usr/bin/env python3
"""
Instahyre Apply Script — via CDP (connects to running Chrome on port 9222)
Applies to jobs in the instahyre_queue.md using the logged-in browser session.

Usage:
  python3 scripts/playwright_instahyre_apply.py [--dry-run]
"""

import argparse
import sys
import time
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent))
import vault_config as vc
import vault_answers as va

VAULT_ROOT = Path(__file__).resolve().parents[1]
TRACKER_PATH = VAULT_ROOT / "active_application_context" / "job_applications_tracker.md"
ARTIFACT_DIR = VAULT_ROOT / "output" / "playwright"
CDP_URL = "http://localhost:9222"

# ---------------------------------------------------------------------------
# CTC values (override from user instruction)
# ---------------------------------------------------------------------------
CURRENT_CTC_LPA = vc.current_ctc_lpa()      # canonical: 01_atomic_fact_sheet.json
EXPECTED_CTC_LPA = vc.expected_ctc_numeric()  # stated floor; never the private floor

# ---------------------------------------------------------------------------
# Jobs to apply (from instahyre_queue.md — Ready to Apply section)
# ---------------------------------------------------------------------------
JOBS = [
    {
        "id": "instahyre_salarybox_fullstack",
        "company": "Salarybox",
        "role": "Fullstack Engineer",
        "url": "https://www.instahyre.com/job-421962-fullstack-engineer-at-salarybox-gurgaon/",
        "note": "Salarybox's mission of bringing financial inclusion to India's blue-collar workforce resonates with my work building VyaparGPT, an AI-powered WhatsApp platform for Indian SMBs that ran 40+ real-world pilots. I have hands-on experience with Python backends (FastAPI/Django patterns), React frontends, and PostgreSQL exactly the stack your JD calls out. I enjoy owning features end-to-end from API design through deployment, which suits a small team well. I'm on a 15-day notice period and excited to contribute at this growth stage.",
        "resume": "AI_Integrated_FullStack",
    },
    {
        "id": "instahyre_rocked_backend",
        "company": "RockED",
        "role": "Software Developer Engineer (Backend)",
        "url": "https://www.instahyre.com/job-425638-software-developer-engineer-backend-at-rocked-bangalore/",
        "note": "RockED's approach to disrupting traditional learning with a mobile-first platform is compelling, and the backend stack Node.js, Express, PostgreSQL is exactly what I work with daily. At OpenBiz I architected multi-service Node.js backends integrated with PostgreSQL and external APIs, delivering for 40+ SMB pilot customers. I'm looking to own backend architecture at an early-growth stage company, and I'm available to join immediately.",
        "resume": "AI_Integrated_FullStack",
    },
]


def parse_args():
    p = argparse.ArgumentParser(description="Instahyre Apply via CDP")
    p.add_argument("--dry-run", action="store_true", help="Fill forms but don't submit")
    p.add_argument("--cdp-url", default=CDP_URL, help="CDP endpoint URL")
    return p.parse_args()


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def append_tracker(job: dict, status: str, note: str = ""):
    today = datetime.now().strftime("%Y-%m-%d")
    entry = (
        f"\n| {today} | Instahyre | {job['company']} | {job['role']} | "
        f"{job['url']} | {status} | Current: {CURRENT_CTC_LPA}L, Expected: {EXPECTED_CTC_LPA}L | {note} |"
    )
    with open(TRACKER_PATH, "a", encoding="utf-8") as f:
        f.write(entry)
    log(f"  → Tracker updated: {status}")


def fill_instahyre_form(page, job: dict, dry_run: bool) -> str:
    """
    Navigates to Instahyre job page and clicks 'Express Interest'.
    Returns status string.
    """
    try:
        log(f"  Navigating to: {job['url']}")
        page.goto(job["url"], wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)

        body_text = page.locator("body").inner_text().casefold()

        # Already applied?
        if ("already expressed interest" in body_text or
                "application received" in body_text or
                "already applied" in body_text or
                "application sent" in body_text):
            return "already_applied"

        # Look for Express Interest / Apply button (including hidden ones)
        apply_btn = None
        for selector in [
            "button:has-text('Express Interest')",
            "button:has-text('Apply')",
            "button:has-text('Apply Now')",
            "a:has-text('Express Interest')",
            "a:has-text('Apply')",
            ".express-interest-btn",
            "[data-action='apply']",
        ]:
            candidates = page.locator(selector)
            if candidates.count() > 0:
                apply_btn = candidates.first
                log(f"  ✓ Found apply button: {selector}")
                break

        if apply_btn is None:
            ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(ARTIFACT_DIR / f"instahyre_{job['id']}_no_btn.png"))
            return "error:no_apply_button"

        if dry_run:
            ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(ARTIFACT_DIR / f"instahyre_{job['id']}_dry_run.png"))
            log("  [DRY RUN] Screenshot saved.")
            return "dry_run"

        # Scroll into view + JS click to handle hidden/off-viewport buttons
        try:
            apply_btn.scroll_into_view_if_needed(timeout=5000)
            page.wait_for_timeout(500)
        except Exception:
            pass
        try:
            apply_btn.click(timeout=8000)
        except Exception:
            apply_btn.evaluate("el => el.click()")
        page.wait_for_timeout(3000)

        # Handle any popup/modal that appears after clicking
        # Look for a text input for a cover note
        for sel in ["textarea", "input[placeholder*='note']", "input[placeholder*='message']"]:
            textareas = page.locator(sel)
            if textareas.count() > 0:
                ta = textareas.first
                if ta.is_visible():
                    try:
                        current = ta.input_value()
                        if not current.strip():
                            ta.fill(job["note"])
                            log(f"  ✓ Filled cover note")
                    except Exception:
                        pass
                    break

        # Confirm / Submit the modal if present
        for confirm_sel in [
            "button:has-text('Submit')",
            "button:has-text('Confirm')",
            "button:has-text('Send')",
            "button:has-text('Express Interest')",
            "button[type='submit']",
        ]:
            btn = page.locator(confirm_sel)
            if btn.count() > 0 and btn.first.is_visible():
                btn.first.click()
                page.wait_for_timeout(3000)
                break

        # Verify
        body_after = page.locator("body").inner_text().casefold()
        ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(ARTIFACT_DIR / f"instahyre_{job['id']}_post_apply.png"))

        if ("success" in body_after or "thank" in body_after or
                "interest" in body_after or "applied" in body_after or
                "received" in body_after):
            return "submitted"

        return "submitted_unconfirmed"

    except Exception as exc:
        return f"error:{exc}"


def main():
    args = parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: playwright not installed.", file=sys.stderr)
        sys.exit(1)

    log("=" * 60)
    log(f"INSTAHYRE APPLY PIPELINE — {'DRY RUN' if args.dry_run else 'LIVE'}")
    log(f"Current CTC: {CURRENT_CTC_LPA} LPA | Expected CTC: {EXPECTED_CTC_LPA} LPA")
    log(f"Jobs queued: {len(JOBS)}")
    log("=" * 60)

    results = []

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(args.cdp_url, no_defaults=True)
        context = browser.contexts[0] if browser.contexts else browser.new_context()

        # Reuse single tab instead of opening/closing tabs repeatedly
        apply_page = context.pages[0] if context.pages else context.new_page()

        for job in JOBS:
            log(f"\n▶ [{job['id']}] {job['company']} — {job['role']}")
            try:
                status = fill_instahyre_form(apply_page, job, args.dry_run)
                log(f"  STATUS: {status}")
                results.append({"job": job, "status": status})

                tracker_note = f"Resume: {job['resume']}"
                if args.dry_run:
                    append_tracker(job, "DRY_RUN", tracker_note)
                elif status == "submitted":
                    append_tracker(job, "APPLIED ✅", tracker_note)
                elif status == "submitted_unconfirmed":
                    append_tracker(job, "APPLIED_UNCONFIRMED ⚠️", tracker_note)
                elif status == "already_applied":
                    append_tracker(job, "ALREADY_APPLIED ⏭️", tracker_note)
                else:
                    append_tracker(job, f"FAILED ❌ ({status})", tracker_note)

            except Exception as exc:
                log(f"  EXCEPTION: {exc}")
                results.append({"job": job, "status": f"exception:{exc}"})
                append_tracker(job, f"EXCEPTION ❌ ({exc})", "")
            finally:
                time.sleep(2)

    log("\n" + "=" * 60)
    log("INSTAHYRE PIPELINE SUMMARY")
    log("=" * 60)
    for r in results:
        log(f"  {r['job']['company']:35s} → {r['status']}")

    submitted = sum(1 for r in results if "submitted" in r["status"])
    log(f"\nTotal: {len(results)} | Applied: {submitted} | Failed: {len(results) - submitted}")


if __name__ == "__main__":
    main()
