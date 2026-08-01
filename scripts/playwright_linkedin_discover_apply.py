#!/usr/bin/env python3
"""
LinkedIn Job Discovery + Easy Apply — via CDP (connects to Chrome on port 9222)

Discovers fresh LinkedIn Easy Apply jobs matching Atin's profile, then applies.
Avoids jobs already in background_agent_state.json applied_job_ids.

Usage:
  python3 scripts/playwright_linkedin_discover_apply.py [--dry-run] [--max-apply N]
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vault_config as vc
import vault_answers as va
from vault_resume import resume_for_job, validate_resume
import vault_state as vs
import vault_browser as vb

VAULT_ROOT = Path(__file__).resolve().parents[1]
FACT_SHEET_PATH = VAULT_ROOT / "core_vault" / "JobApplyFiles" / "01_atomic_fact_sheet.json"
LOGISTICS_PATH = VAULT_ROOT / "core_vault" / "JobApplyFiles" / "06_logistics_mapping.json"
TRACKER_PATH = VAULT_ROOT / "active_application_context" / "job_applications_tracker.md"
STATE_PATH = VAULT_ROOT / "active_application_context" / "background_agent_state.json"
# NOTE: last-resort fallback only. Per-job selection now goes through
# vault_resume.resume_for_job(), which validates extractable text before upload.
RESUME_PATH = VAULT_ROOT / "resumes_and_docs" / "categories" / "pdf" / "Atin_Sharma_Resume_2026.pdf"
ARTIFACT_DIR = VAULT_ROOT / "output" / "playwright"
CDP_URL = "http://localhost:9222"

CURRENT_CTC_LPA = vc.current_ctc_lpa()      # canonical: 01_atomic_fact_sheet.json
EXPECTED_CTC_LPA = vc.expected_ctc_numeric()  # stated floor; never the private floor

# LinkedIn search queries for Easy Apply jobs
LINKEDIN_SEARCH_URLS = [
    # Full-stack / AI / GenAI / Node / TypeScript / React / MERN (Core stack) — posted last 24h
    "https://www.linkedin.com/jobs/search/?f_LF=f_AL&keywords=Full%20Stack%20Engineer%20AI&location=India&f_TPR=r86400&f_WT=2",
    "https://www.linkedin.com/jobs/search/?f_LF=f_AL&keywords=Node.js%20React%20Engineer%20startup&location=India&f_TPR=r86400&f_WT=2",
    "https://www.linkedin.com/jobs/search/?f_LF=f_AL&keywords=Founding%20Engineer%20AI&location=India&f_TPR=r86400",
    "https://www.linkedin.com/jobs/search/?f_LF=f_AL&keywords=AI%20Engineer%20LLM%20RAG&location=India&f_TPR=r86400",
    # Core stack / Broader / Fresher-friendly — last 7 days
    "https://www.linkedin.com/jobs/search/?f_LF=f_AL&keywords=TypeScript%20Node.js%20backend%20engineer&location=India&f_TPR=r604800&f_WT=2",
    "https://www.linkedin.com/jobs/search/?f_LF=f_AL&keywords=MERN%20stack%20engineer%20startup&location=India&f_TPR=r604800",
    "https://www.linkedin.com/jobs/search/?f_LF=f_AL&keywords=Software%20Engineer%20AI%20startup%20fresher&location=India&f_TPR=r604800&f_E=1%2C2",
    "https://www.linkedin.com/jobs/search/?f_LF=f_AL&keywords=product%20engineer%20AI%20SaaS&location=India&f_TPR=r604800",
    "https://www.linkedin.com/jobs/search/?f_LF=f_AL&keywords=LangChain%20LangGraph%20engineer&location=India&f_TPR=r604800",
    # Python-based (Fallback stack)
    "https://www.linkedin.com/jobs/search/?f_LF=f_AL&keywords=GenAI%20Engineer%20Python&location=India&f_TPR=r86400",
    "https://www.linkedin.com/jobs/search/?f_LF=f_AL&keywords=FastAPI%20Python%20engineer%20AI&location=India&f_TPR=r604800",
    "https://www.linkedin.com/jobs/search/?f_LF=f_AL&keywords=backend%20engineer%20Node%20Python%20early%20stage&location=India&f_TPR=r604800",
]


# Minimum stack_match threshold
STACK_MATCH_THRESHOLD = 0.45

# Keywords for core stack (TypeScript/Node/React/MERN/Express/NestJS and general AI/software engineering)
CORE_KEYWORDS = [
    # Core stack
    "node.js", "nodejs", "react", "next.js", "nextjs", "typescript",
    "javascript", "express", "nestjs", "mern",
    # AI/LLM
    "llm", "rag", "langchain", "langgraph", "openai", "gemini", "groq",
    "ai engineer", "genai", "gen ai", "agentic", "agent", "vector", "pgvector",
    "embedding", "prompt", "fine-tun", "chatbot", "conversational",
    # Full stack / General signals
    "full stack", "fullstack", "founding engineer", "early stage",
    "startup", "product engineer", "backend engineer", "software engineer",
    # Cloud/infra light signals
    "docker", "aws", "supabase", "postgresql", "mongodb",
]

# Secondary keywords (Python-based stack, fallback)
SECONDARY_KEYWORDS = [
    "python", "fastapi", "django", "flask",
]

# Keywords that hard-penalise a job
NEGATIVE_KEYWORDS = [
    "java ", " scala", ".net developer", "c# developer", "c++ engineer",
    "ruby on rails", "golang engineer", "go developer",
    "senior manager", "vp of engineering", "director of",
    "10+ years", "15+ years", "12+ years",
    "ios developer", "android developer", "game developer", "unity developer",
    "data scientist only", "mechanical engineer", "hardware engineer",
    # Roles not suitable for Atin
    " intern", "internship", "walk-in", "walkin", "walk in drive",
    "trainee", "apprentice", "fresher drive", "campus hire",
    "junior developer", "junior python", "associate developer",
]

RESUME_PATH_STR = str(RESUME_PATH)


def parse_args():
    p = argparse.ArgumentParser(description="LinkedIn Discover + Easy Apply via CDP")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--max-apply", type=int, default=15, help="Max jobs to apply in one run")
    p.add_argument("--cdp-url", default=CDP_URL)
    return p.parse_args()


def log(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def _legacy_load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {"seen_job_ids": [], "applied_job_ids": [], "blocked_jobs": []}


def save_state(state: dict):
    STATE_PATH.write_text(json.dumps(state, indent=2))


def make_job_id(company: str, role: str) -> str:
    def slug(s):
        return re.sub(r"[^a-z0-9]+", "-", s.casefold()).strip("-")
    return f"{slug(company)}:{slug(role)}"


def score_job(title: str, description: str, company: str = "") -> float:
    title_lower = title.casefold()
    company_lower = (company or "").casefold()
    
    # Check if FAANG-level company
    faang_keywords = ["google", "apple", "meta", "amazon", "microsoft", "netflix", "alphabet", "facebook"]
    is_faang = any(f in company_lower for f in faang_keywords)
    
    # Absolute strict exclusions for internship or trainee roles, unless FAANG
    if not is_faang:
        for word in ["intern", "internship", "trainee", "apprentice"]:
            if word in title_lower:
                return 0.0

    text = (title + " " + description).casefold()
    score = 0.0
    
    def get_pattern(kw: str) -> str:
        # Prepend \b only if first char is alphanumeric, append \b only if last is alphanumeric
        start = r'\b' if kw[0].isalnum() or kw[0] == '_' else ''
        end = r'\b' if kw[-1].isalnum() or kw[-1] == '_' else ''
        return start + re.escape(kw) + end

    # Core hits count full
    for kw in CORE_KEYWORDS:
        pattern = get_pattern(kw)
        if re.search(pattern, title_lower):
            score += 0.20
        elif re.search(pattern, text):
            score += 0.08
            
    # Secondary hits count half
    for kw in SECONDARY_KEYWORDS:
        pattern = get_pattern(kw)
        if re.search(pattern, title_lower):
            score += 0.08
        elif re.search(pattern, text):
            score += 0.03
            
    # If Python-based but has NO Node/TS/React/Express/NestJS/MERN, penalize heavily
    has_core = any(re.search(get_pattern(k), text) for k in ["node", "typescript", "react", "express", "nestjs", "mern", "javascript"])
    has_python = any(re.search(get_pattern(k), text) for k in SECONDARY_KEYWORDS)
    if has_python and not has_core:
        score -= 0.25

    for kw in NEGATIVE_KEYWORDS:
        clean_kw = kw.strip()
        if not clean_kw:
            continue
        pattern = get_pattern(clean_kw)
        if re.search(pattern, text):
            score -= 0.30
            
    return min(max(score, 0.0), 1.0)


def append_tracker(company: str, role: str, url: str, status: str, note: str = ""):
    today = datetime.now().strftime("%Y-%m-%d")
    entry = (
        f"\n- [{today}] **Company:** {company} | **Role:** {role} | "
        f"**Status:** {status} | **URL:** {url} | "
        f"**CTC:** Current {CURRENT_CTC_LPA}L / Expected {EXPECTED_CTC_LPA}L | **Note:** {note}"
    )
    with open(TRACKER_PATH, "a", encoding="utf-8") as f:
        f.write(entry)


def build_answer_bank() -> dict:
    """Canonical answers only.

    This used to rebuild the bank and then overwrite all seven salary keys with
    a hardcoded 16 LPA, which is how every LinkedIn application came to undercut
    the documented floor by 2 LPA.
    """
    return vc.build_answer_bank()


def apply_easy_apply(page, job_url: str, answer_bank: dict, dry_run: bool) -> str:
    """Apply to a LinkedIn Easy Apply job. Returns status string."""
    try:
        sys.path.insert(0, str(VAULT_ROOT / "scripts"))
        from playwright_linkedin_easy_apply import execute_easy_apply
        exit_code = execute_easy_apply(page, RESUME_PATH, answer_bank, dry_run)
        return "submitted" if exit_code == 0 else f"error:{exit_code}"
    except vb.SecurityChallenge:
        raise  # must reach __main__ and abort the run, never be swallowed
    except Exception as exc:
        return f"exception:{exc}"


def discover_and_apply(page, apply_page, context, search_url: str, state: dict, answer_bank: dict,
                       max_apply: int, applied_count: list, dry_run: bool):
    """Navigate to a LinkedIn search URL, find Easy Apply jobs, apply."""
    try:
        log(f"  Searching: {search_url[:80]}...")
        page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)

        # Scroll the LEFT results panel to trigger LinkedIn's lazy-load
        # (window.scrollBy does not work — results are in a nested scrollable pane)
        for _ in range(8):
            scrolled = page.evaluate("""
                () => {
                    const listContainer = document.querySelector('.scaffold-layout__list');
                    if (listContainer) {
                        const divs = listContainer.querySelectorAll('div');
                        for (const d of divs) {
                            if (d.scrollHeight > d.clientHeight) {
                                d.scrollBy(0, 600);
                                return true;
                            }
                        }
                    }
                    window.scrollBy(0, 600);
                    return false;
                }
            """)
            page.wait_for_timeout(700)
        page.wait_for_timeout(1000)

        # Collect job cards
        job_cards = page.locator("li.jobs-search-results__list-item, [data-job-id], li:has(a[href*='/jobs/view/'])")
        count = job_cards.count()
        log(f"  Found {count} job cards")

        for idx in range(min(count, 25)):
            if applied_count[0] >= max_apply:
                log(f"  Max apply limit ({max_apply}) reached.")
                return

            card = job_cards.nth(idx)
            try:
                # Scroll into view then JS-click to avoid viewport issues
                try:
                    card.scroll_into_view_if_needed(timeout=3000)
                    page.wait_for_timeout(300)
                except Exception:
                    pass
                try:
                    card.click(timeout=8000)
                except Exception:
                    card.evaluate("el => el.click()")
                page.wait_for_timeout(2500)

                # Get job title, company, and direct URL from card attributes
                title = ""
                company = ""
                job_direct_url = ""

                # Try to extract job ID from the card for a direct URL
                try:
                    job_data_id = card.evaluate("""el => {
                        // 1. Try to find a link containing /jobs/view/ and extract the numeric ID
                        const anchors = el.querySelectorAll('a[href*="/jobs/view/"]');
                        for (const a of anchors) {
                            const href = a.getAttribute('href') || '';
                            const match = href.match(/\\/jobs\\/view\\/(\\d+)/);
                            if (match && match[1]) {
                                return match[1];
                            }
                        }
                        // 2. Try to get data-job-id or data-occludable-job-id
                        const li = el.closest('[data-job-id], [data-occludable-job-id]') || 
                                   el.querySelector('[data-job-id], [data-occludable-job-id]') || el;
                        const jobId = li.getAttribute('data-job-id') || li.getAttribute('data-occludable-job-id') || '';
                        if (jobId && jobId !== 'search') {
                            return jobId;
                        }
                        return '';
                    }""")
                    if job_data_id:
                        job_direct_url = f"https://www.linkedin.com/jobs/view/{job_data_id}/"
                except Exception:
                    pass

                # Get title from right-panel detail view
                for title_sel in [
                    ".job-details-jobs-unified-top-card__job-title h1",
                    ".jobs-unified-top-card__job-title h1",
                    "h1.t-24", ".t-24.t-bold", "h1",
                ]:
                    el = page.locator(title_sel)
                    if el.count() > 0 and el.first.is_visible():
                        title = el.first.inner_text().strip()
                        break

                for comp_sel in [
                    ".job-details-jobs-unified-top-card__company-name a",
                    ".jobs-unified-top-card__company-name a",
                    ".job-details-jobs-unified-top-card__company-name",
                    ".t-16.t-black.t-bold",
                ]:
                    el = page.locator(comp_sel)
                    if el.count() > 0 and el.first.is_visible():
                        company = el.first.inner_text().strip()
                        break

                # Get job description for scoring
                desc = ""
                for desc_sel in [".jobs-description__content", ".job-description", "#job-details", ".jobs-box__html-content"]:
                    el = page.locator(desc_sel)
                    if el.count() > 0:
                        desc = el.first.inner_text()[:2000]
                        break

                # Fall back to current URL if no direct URL extracted
                navigate_url = job_direct_url or page.url
                job_id = make_job_id(company, title) if (company and title) else f"job:{job_direct_url}"

                if not title and not job_direct_url:
                    continue

                skip, why = state.should_skip(job_id)
                if skip:
                    log(f"  ⏭  SKIP ({why}): {company} — {title}")
                    continue

                # Score the job
                match_score = score_job(title, desc, company)
                if match_score < STACK_MATCH_THRESHOLD:
                    log(f"  ⏭  SKIP (low match {match_score:.2f}): {company} — {title}")
                    vs.record_outcome(job_id, vs.Outcome.SKIPPED_FILTER,
                                      reason=f"score {match_score:.2f}", url=navigate_url)
                    state.record(job_id, vs.Outcome.SKIPPED_FILTER)
                    continue

                log(f"\n  ▶ APPLYING [{match_score:.2f}]: {company or 'Unknown'} — {title or job_direct_url}")
                log(f"    URL: {navigate_url}")

                # Navigate directly to the job URL for Easy Apply using reused apply_page
                try:
                    vb.guarded_goto(apply_page, navigate_url, timeout=30000,
                                    label=f"{company} {title}")
                    apply_page.wait_for_timeout(6000)
                    status = apply_easy_apply(apply_page, navigate_url, answer_bank, dry_run)
                    log(f"  STATUS: {status}")

                    tracker_note = f"Stack match: {match_score:.2f}. LinkedIn Easy Apply."
                    outcome = vs.classify(status)
                    if outcome in (vs.Outcome.APPLIED, vs.Outcome.APPLIED_UNCONFIRMED):
                        append_tracker(company, title, navigate_url, "Applied (confirmed) ✅", tracker_note)
                        applied_count[0] += 1
                    elif outcome is vs.Outcome.DRY_RUN:
                        append_tracker(company, title, navigate_url, "DRY_RUN", tracker_note)
                        applied_count[0] += 1
                    elif outcome is vs.Outcome.ALREADY_APPLIED:
                        append_tracker(company, title, navigate_url, "ALREADY_APPLIED ⏭️", tracker_note)
                    else:
                        append_tracker(company, title, navigate_url, f"FAILED ({status})", tracker_note)

                    # Outcome-driven bookkeeping. This used to mark EVERY outcome
                    # seen, so one transient CAPTCHA blacklisted a job forever.
                    vs.record_outcome(job_id, outcome, reason=status, url=navigate_url)
                    state.record(job_id, outcome, reason=status, url=navigate_url)
                finally:
                    time.sleep(2)

            except vb.SecurityChallenge:
                raise  # abort the run; do not move on to the next card
            except Exception as exc:
                log(f"  Card {idx} error: {exc}")
                continue

    except vb.SecurityChallenge:
        raise
    except Exception as exc:
        log(f"  Search page error: {exc}")


def main():
    args = parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: playwright not installed.", file=sys.stderr)
        sys.exit(1)

    log("=" * 60)
    log(f"LINKEDIN DISCOVER + EASY APPLY — {'DRY RUN' if args.dry_run else 'LIVE'}")
    log(f"Current CTC: {CURRENT_CTC_LPA} LPA | Expected CTC: {EXPECTED_CTC_LPA} LPA")
    log(f"Max applications: {args.max_apply}")
    log("=" * 60)

    state = vs.load_state()
    answer_bank = build_answer_bank()
    applied_count = [0]  # mutable for nested function

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(args.cdp_url, no_defaults=True)
        context = browser.contexts[0] if browser.contexts else browser.new_context()

        search_page = context.pages[0] if context.pages else context.new_page()
        apply_page = context.pages[1] if len(context.pages) > 1 else context.new_page()
        try:
            for search_url in LINKEDIN_SEARCH_URLS:
                if applied_count[0] >= args.max_apply:
                    break
                discover_and_apply(
                    search_page, apply_page, context, search_url, state, answer_bank,
                    args.max_apply, applied_count, args.dry_run
                )
                time.sleep(2)
        finally:
            pass  # Keep reused pages open cleanly without closing the main browser window tabs

    log("\n" + "=" * 60)
    log(f"LINKEDIN PIPELINE COMPLETE: {applied_count[0]} applications submitted")
    log("=" * 60)


if __name__ == "__main__":
    # A security challenge must abort the run with exit 10 (or 12 for a login
    # wall) so run_apply_all.sh stops the whole pipeline. Continuing after a
    # challenge deepens the flag on this IP/profile.
    try:
        main()
    except vb.SecurityChallenge as _exc:
        print(f"🛑 SECURITY CHALLENGE ({_exc.kind}): {_exc}", flush=True)
        raise SystemExit(_exc.exit_code)
