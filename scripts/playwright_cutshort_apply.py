#!/usr/bin/env python3
"""
Cutshort Apply Script — via CDP (connects to running Chrome on port 9222)
Applies to jobs in the cutshort_queue.md using the logged-in browser session.

Usage:
  python3 scripts/playwright_cutshort_apply.py [--dry-run]
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright_form_helpers import maybe_upload_file

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
VAULT_ROOT = Path(__file__).resolve().parents[1]
FACT_SHEET_PATH = VAULT_ROOT / "core_vault" / "JobApplyFiles" / "01_atomic_fact_sheet.json"
LOGISTICS_PATH = VAULT_ROOT / "core_vault" / "JobApplyFiles" / "06_logistics_mapping.json"
TRACKER_PATH = VAULT_ROOT / "active_application_context" / "job_applications_tracker.md"
QUEUE_PATH = VAULT_ROOT / "active_application_context" / "cutshort_queue.md"
RESUME_PATH = VAULT_ROOT / "resumes_and_docs" / "categories" / "pdf" / "2026New1.pdf"
ARTIFACT_DIR = VAULT_ROOT / "output" / "playwright"
CDP_URL = "http://localhost:9222"

# ---------------------------------------------------------------------------
# CTC values (override from user instruction)
# ---------------------------------------------------------------------------
CURRENT_CTC_LPA = 11.2
EXPECTED_CTC_LPA = 16  # 16-22 LPA, negotiable

# ---------------------------------------------------------------------------
# Jobs to apply (from cutshort_queue.md — Ready to Apply section)
# ---------------------------------------------------------------------------
JOBS = [
    {
        "id": "cutshort_nxtwave_sde2",
        "company": "NxtWave Disruptive Technologies",
        "role": "SDE 2 Fullstack Developer",
        "url": "https://cutshort.io/job/SDE-2-Fullstack-Developer-Hyderabad-NxtWave-Disruptive-Technologies-Private-Limited-cPFFuoQ4",
        "note": "NxtWave is redefining how India's next-gen engineers learn and build, and I'm excited by the challenge of scaling learner-facing products. My full-stack work at OpenBiz building real-time data pipelines and Node.js/React services used by SMBs gives me a direct read on the reliability and product thinking NxtWave needs. I've shipped production features independently from design to deployment and I'm available to join immediately.",
        "resume": "AI_Integrated_FullStack",
    },
    {
        "id": "cutshort_hunarstreet_aiml",
        "company": "Hunarstreet Technologies",
        "role": "Senior Developer AI/ML",
        "url": "https://cutshort.io/job/Senior-Developer-AI-ML-Hunarstreet-Technologies-pvt-ltd-mGQ03IWi",
        "note": "I've built production RAG pipelines and multi-agent systems using LangChain and LangGraph most recently VyaparGPT serving 40+ SMB pilots and a stateful LangGraph AI CRM. Hunarstreet's knowledge-graph AI work with Neo4j and FAISS is precisely the applied LLM engineering I want to do full-time. I'm a remote-first engineer with strong async habits and can start immediately.",
        "resume": "GenAI_Prompt_Engineer",
    },
    {
        "id": "cutshort_talentxo_python_react",
        "company": "TalentXO (AI Startup)",
        "role": "Software Developer (Python, React/Vue)",
        "url": "https://cutshort.io/job/Software-Developer-Python-React-Vue-TalentXO-MbqoAOip",
        "note": "Building the backbone of an AI Agentic OS is exactly the kind of greenfield challenge I've been working toward. At OpenBiz I engineered the full data layer for a multi-agent website builder and scaled a WhatsApp AI assistant through 40 pilot deployments. The Python + React stack is my daily driver and I own outcomes end-to-end. Available to join immediately.",
        "resume": "AI_Integrated_FullStack",
    },
    {
        "id": "cutshort_appiness_aiml",
        "company": "Appiness Interactive",
        "role": "AIML Engineer",
        "url": "https://cutshort.io/job/AIML-Engineer-Bengaluru-Bangalore-Appiness-Interactive-ZzRI7o78",
        "note": "The multi-agent and LLM orchestration requirements here are exactly what I've been building: a stateful LangGraph AI CRM, a RAG system with pgvector, and VyaparGPT processing NL business queries. I bring production LangGraph/FastAPI experience not prototype work. In Bangalore and available immediately; happy to do a live system design session.",
        "resume": "GenAI_Prompt_Engineer",
    },
    {
        "id": "cutshort_procedure_workhero",
        "company": "Procedure (WorkHero)",
        "role": "Applied AI Engineer, MERN Stack",
        "url": "https://cutshort.io/job/Applied-AI-Engineer-MERN-Stack-Procedure-osZhIuIE",
        "note": "WorkHero's mission to pair operators with AI workflows resonates strongly it mirrors what we built with VyaparGPT automating SMB business queries via WhatsApp. I've built production AI agent pipelines with TypeScript, Node.js, and LLM orchestration at a founding-engineer level. MERN + AI Agents is my home ground. Available immediately, comfortable with async US time zones.",
        "resume": "AI_Integrated_FullStack",
    },
]


def parse_args():
    p = argparse.ArgumentParser(description="Cutshort Apply via CDP")
    p.add_argument("--dry-run", action="store_true", help="Fill forms but don't submit")
    p.add_argument("--cdp-url", default=CDP_URL, help="CDP endpoint URL")
    return p.parse_args()


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def append_tracker(job: dict, status: str, note: str = ""):
    today = datetime.now().strftime("%Y-%m-%d")
    entry = (
        f"\n| {today} | Cutshort | {job['company']} | {job['role']} | "
        f"{job['url']} | {status} | Current: {CURRENT_CTC_LPA}L, Expected: {EXPECTED_CTC_LPA}L | {note} |"
    )
    with open(TRACKER_PATH, "a", encoding="utf-8") as f:
        f.write(entry)
    log(f"  → Tracker updated: {status}")


def wait_for_network_idle(page, timeout_ms=5000):
    try:
        page.wait_for_load_state("networkidle", timeout=timeout_ms)
    except Exception:
        pass


def fill_cutshort_apply_form(page, job: dict, dry_run: bool) -> str:
    """
    Fills and submits the Cutshort application form.
    Returns: 'submitted' | 'dry_run' | 'already_applied' | 'error:<reason>'
    """
    try:
        log(f"  Navigating to: {job['url']}")
        page.goto(job["url"], wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)

        body_text = page.locator("body").inner_text().casefold()

        # Check if already applied
        if "already applied" in body_text or "application submitted" in body_text:
            return "already_applied"

        # Look for Apply button variations (Cutshort uses label="Apply to this job")
        apply_btn = None
        for selector in [
            "button[label='Apply to this job']",
            "button:has-text('Apply to this job')",
            "button:has-text('Apply Now')",
            "button:has-text('Apply')",
            "a:has-text('Apply')",
            "[data-testid='apply-button']",
            "button.apply-btn",
        ]:
            candidates = page.locator(selector)
            if candidates.count() > 0:
                apply_btn = candidates.first
                break

        if apply_btn is None:
            ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(ARTIFACT_DIR / f"cutshort_{job['id']}_no_apply_btn.png"))
            return "error:no_apply_button"

        # Scroll element into view and use JS click to bypass viewport issues
        try:
            apply_btn.scroll_into_view_if_needed(timeout=5000)
            page.wait_for_timeout(500)
        except Exception:
            pass
        try:
            apply_btn.click(timeout=10000)
        except Exception:
            # JS click fallback for off-viewport elements
            apply_btn.evaluate("el => el.click()")
        page.wait_for_timeout(3000)

        # --- Handle application form/modal ---
        # Try to find modal or form
        form = None
        for sel in ["[role='dialog']", "form", ".application-form", ".apply-modal"]:
            f = page.locator(sel)
            if f.count() > 0 and f.first.is_visible():
                form = f.first
                break

        root = form if form else page

        # Upload resume if required
        uploaded = maybe_upload_file(root, RESUME_PATH)
        if uploaded:
            log("  ✓ Uploaded resume")
            page.wait_for_timeout(4000)

        # Fill cover note / message textarea
        note_filled = False
        for sel in ["textarea", "input[placeholder*='note']", "input[placeholder*='message']", "input[placeholder*='cover']"]:
            textareas = root.locator(sel)
            for i in range(textareas.count()):
                ta = textareas.nth(i)
                try:
                    if not ta.is_visible() or not ta.is_enabled():
                        continue
                    if ta.get_attribute("id") == "wootric-text" or "wootric" in (ta.get_attribute("class") or "").casefold():
                        continue
                except Exception:
                    continue
                current_val = ta.input_value().strip() if hasattr(ta, "input_value") else ""
                if current_val:
                    continue
                ta.fill(job["note"])
                note_filled = True
                log(f"  ✓ Filled cover note ({len(job['note'])} chars)")
                break
            if note_filled:
                break

        # Fill current CTC
        for label_pattern in ["current ctc", "current salary", "current compensation"]:
            inputs = root.locator("input")
            for i in range(inputs.count()):
                inp = inputs.nth(i)
                if not inp.is_visible():
                    continue
                label_text = ""
                try:
                    label_text = inp.evaluate("""el => {
                        const labels = el.labels;
                        if (labels && labels.length) return labels[0].textContent;
                        const ph = el.getAttribute('placeholder') || '';
                        return ph;
                    }""").casefold()
                except Exception:
                    pass
                if label_pattern in label_text:
                    if not inp.input_value().strip():
                        inp.fill(str(CURRENT_CTC_LPA))
                        log(f"  ✓ Filled current CTC: {CURRENT_CTC_LPA}")
                    break

        # Fill expected CTC
        for label_pattern in ["expected ctc", "expected salary", "desired salary"]:
            inputs = root.locator("input")
            for i in range(inputs.count()):
                inp = inputs.nth(i)
                if not inp.is_visible():
                    continue
                label_text = ""
                try:
                    label_text = inp.evaluate("""el => {
                        const labels = el.labels;
                        if (labels && labels.length) return labels[0].textContent;
                        const ph = el.getAttribute('placeholder') || '';
                        return ph;
                    }""").casefold()
                except Exception:
                    pass
                if label_pattern in label_text:
                    if not inp.input_value().strip():
                        inp.fill(str(EXPECTED_CTC_LPA))
                        log(f"  ✓ Filled expected CTC: {EXPECTED_CTC_LPA}")
                    break

        if dry_run:
            ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(ARTIFACT_DIR / f"cutshort_{job['id']}_dry_run.png"))
            log(f"  [DRY RUN] Screenshot saved.")
            return "dry_run"

        # Submit
        for submit_sel in [
            "button[type='submit']",
            "button:has-text('Submit')",
            "button:has-text('Send Application')",
            "button:has-text('Apply')",
            "button:has-text('Send')",
        ]:
            btn = root.locator(submit_sel)
            if btn.count() > 0:
                # Scroll into view and click (JS fallback for off-viewport)
                try:
                    btn.first.scroll_into_view_if_needed(timeout=5000)
                    page.wait_for_timeout(300)
                except Exception:
                    pass
                try:
                    btn.first.click(timeout=8000)
                except Exception:
                    btn.first.evaluate("el => el.click()")
                page.wait_for_timeout(4000)
                body_after = page.locator("body").inner_text().casefold()
                if "success" in body_after or "submitted" in body_after or "applied" in body_after or "thank" in body_after:
                    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=str(ARTIFACT_DIR / f"cutshort_{job['id']}_submitted.png"))
                    return "submitted"
                ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(ARTIFACT_DIR / f"cutshort_{job['id']}_post_submit.png"))
                return "submitted_unconfirmed"

        return "error:no_submit_button"

    except Exception as exc:
        return f"error:{exc}"


def main():
    args = parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: playwright not installed. Run: pip install playwright", file=sys.stderr)
        sys.exit(1)

    log("=" * 60)
    log(f"CUTSHORT APPLY PIPELINE — {'DRY RUN' if args.dry_run else 'LIVE'}")
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
                status = fill_cutshort_apply_form(apply_page, job, args.dry_run)
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
                time.sleep(2)  # Polite delay between applications

    # Summary
    log("\n" + "=" * 60)
    log("CUTSHORT PIPELINE SUMMARY")
    log("=" * 60)
    for r in results:
        log(f"  {r['job']['company']:35s} → {r['status']}")

    submitted = sum(1 for r in results if "submitted" in r["status"])
    log(f"\nTotal: {len(results)} | Applied: {submitted} | Failed: {len(results) - submitted}")


if __name__ == "__main__":
    main()
