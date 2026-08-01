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


def apply_easy_apply(page, job_url: str, answer_bank: dict, dry_run: bool,
                     resume_path=None) -> str:
    """Apply to a LinkedIn Easy Apply job. Returns status string."""
    try:
        sys.path.insert(0, str(VAULT_ROOT / "scripts"))
        from playwright_linkedin_easy_apply import execute_easy_apply
        # Per-job resume, validated for extractable text. This used to pass the
        # module constant, so the category selection computed above was discarded.
        exit_code = execute_easy_apply(page, validate_resume(resume_path or RESUME_PATH),
                                       answer_bank, dry_run)
        if exit_code == 14:
            return "blocked:unanswerable_question"
        if exit_code == 11:
            return "blocked:external_ats"
        if exit_code != 0:
            return f"error:{exit_code}"
        # execute_easy_apply returns EXIT_SUCCESS for a completed DRY RUN too — it
        # returns before clicking submit. Mapping that to "submitted" wrote false
        # "Applied" rows to the tracker and poisoned the dedup state.
        return "dry_run" if dry_run else "submitted"
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
        # LinkedIn's stable card container. The previous selector list matched only
        # 7-9 of 25 cards, and none of them carried the attributes we need.
        job_cards = page.locator("[data-occludable-job-id]")
        count = job_cards.count()

        # Read every card's metadata in ONE pass, before any clicking. The old code
        # clicked each card and waited 2.5s just to read the right-hand panel, then
        # found the panel selectors stale and got blank strings — so every job
        # collapsed to the same id and skipped as "seen".
        cards_meta = page.evaluate("""() => {
            return Array.from(document.querySelectorAll('[data-occludable-job-id]')).map(li => {
                const a = li.querySelector("a[href*='/jobs/view/']");
                const sub = li.querySelector('.artdeco-entity-lockup__subtitle, [class*="subtitle"]');
                const cap = li.querySelector('.artdeco-entity-lockup__caption, [class*="caption"]');
                const txt = li.innerText || '';
                return {
                    id: li.getAttribute('data-occludable-job-id') || '',
                    title: (a && a.getAttribute('aria-label')) || '',
                    company: sub ? sub.innerText.trim() : '',
                    location: cap ? cap.innerText.trim() : '',
                    easy: txt.includes('Easy Apply'),
                };
            });
        }""")
        usable = sum(1 for c in cards_meta if c.get("id") and c.get("title"))
        log(f"  Found {count} job cards ({usable} with usable metadata)")
        if count and not usable:
            log("  \u26a0 No card metadata extracted — LinkedIn DOM may have changed again.")

        for idx in range(min(count, 25)):
            if applied_count[0] >= max_apply:
                log(f"  Max apply limit ({max_apply}) reached.")
                return

            card = job_cards.nth(idx)
            meta = cards_meta[idx] if idx < len(cards_meta) else {}

            # LinkedIn virtualizes the results list: cards below the fold carry no
            # content until scrolled into view. The upfront pass only populates the
            # rendered ones, so re-read this card individually when it came back empty.
            if not (meta.get("title") and meta.get("company")):
                try:
                    card.scroll_into_view_if_needed(timeout=3000)
                    page.wait_for_timeout(400)
                    meta = card.evaluate("""li => {
                        const a = li.querySelector("a[href*='/jobs/view/']");
                        const sub = li.querySelector('.artdeco-entity-lockup__subtitle, [class*="subtitle"]');
                        const cap = li.querySelector('.artdeco-entity-lockup__caption, [class*="caption"]');
                        const txt = li.innerText || '';
                        return {
                            id: li.getAttribute('data-occludable-job-id') || '',
                            title: (a && a.getAttribute('aria-label')) || '',
                            company: sub ? sub.innerText.trim() : '',
                            location: cap ? cap.innerText.trim() : '',
                            easy: txt.includes('Easy Apply'),
                        };
                    }""") or meta
                except Exception:
                    pass

            try:
                title = (meta.get("title") or "").strip()
                company = (meta.get("company") or "").strip()
                location = (meta.get("location") or "").strip()
                job_data_id = (meta.get("id") or "").strip()
                job_direct_url = f"https://www.linkedin.com/jobs/view/{job_data_id}/" if job_data_id else ""

                if not job_data_id and not title:
                    continue  # unusable card, nothing to dedupe on

                navigate_url = job_direct_url or page.url
                job_id = make_job_id(company, title) if (company and title) else f"job:{job_data_id}"

                skip, why = state.should_skip(job_id)
                if skip:
                    log(f"  \u23ed  SKIP ({why}): {company} — {title}")
                    continue

                # Easy Apply only. Applied ONLY when the card actually rendered —
                # an unresolved card says nothing about the job, and recording it as
                # permanently blocked would blacklist it forever on a rendering glitch.
                metadata_resolved = bool(title and company)
                if metadata_resolved and meta.get("easy") is False:
                    log(f"  \u23ed  SKIP (not Easy Apply): {company} — {title}")
                    vs.record_outcome(job_id, vs.Outcome.BLOCKED_PERMANENT,
                                      reason="not_easy_apply", url=navigate_url)
                    state.record(job_id, vs.Outcome.BLOCKED_PERMANENT)
                    continue
                # A card that never rendered still yields its job id, and we navigate
                # to the job page below anyway for the description — so recover
                # title/company from there instead of discarding the job. This was
                # losing roughly 18 of every 25 results to list virtualisation.
                if not metadata_resolved and not job_data_id:
                    log("  \u23ed  SKIP (no id and no metadata)")
                    continue

                # Cheap title-only pre-filter so we do not pay a page load for
                # obvious non-matches. Skipped when the card never rendered —
                # there is no title to filter on yet.
                pre_score = score_job(title, "", company) if metadata_resolved else 1.0
                if pre_score <= 0.0:
                    log(f"  \u23ed  SKIP (title pre-filter 0.00): {company} — {title}")
                    vs.record_outcome(job_id, vs.Outcome.SKIPPED_FILTER,
                                      reason="title_prefilter", url=navigate_url)
                    state.record(job_id, vs.Outcome.SKIPPED_FILTER)
                    continue

                # Navigate once, then score on the real description. Previously the
                # code clicked every card to read a side panel whose selectors were
                # stale, so desc was always empty and everything scored title-only.
                try:
                    vb.guarded_goto(apply_page, navigate_url, timeout=30000,
                                    label=f"{company} {title}")
                    apply_page.wait_for_timeout(2500)
                except vb.SecurityChallenge:
                    raise
                except Exception as exc:
                    log(f"  \u26a0 Could not open job: {exc}")
                    vs.record_outcome(job_id, vs.Outcome.FAILED_RETRYABLE,
                                      reason="navigation", url=navigate_url)
                    state.record(job_id, vs.Outcome.FAILED_RETRYABLE)
                    continue

                # LinkedIn now ships hashed CSS class names, so class selectors are
                # unreliable. These two anchors are structural and survive redeploys.
                desc = ""
                for desc_sel in ['[id^="JobDetails_AboutTheJob"]', "main"]:
                    try:
                        el = apply_page.locator(desc_sel)
                        if el.count() > 0:
                            desc = el.first.inner_text()[:4000]
                            if desc.strip():
                                break
                    except Exception:
                        pass

                # Recover title/company from the job page for unrendered cards.
                if not metadata_resolved:
                    try:
                        recovered = apply_page.evaluate("""() => {
                            const h = document.querySelector('h1');
                            const main = document.querySelector('main');
                            const first = main ? (main.innerText || '').split('\\n').filter(Boolean) : [];
                            return { title: h ? h.innerText.trim() : (first[1] || ''),
                                     company: first[0] || '' };
                        }""") or {}
                        title = title or (recovered.get("title") or "").strip()
                        company = company or (recovered.get("company") or "").strip()
                        if title and company:
                            new_id = make_job_id(company, title)
                            skip2, why2 = state.should_skip(new_id)
                            if skip2:
                                log(f"  \u23ed  SKIP ({why2}): {company} — {title}")
                                continue
                            job_id = new_id
                            log(f"  \u21bb Recovered from job page: {company} — {title}")
                    except Exception:
                        pass

                match_score = score_job(title, desc, company)
                if match_score < STACK_MATCH_THRESHOLD:
                    log(f"  \u23ed  SKIP (low match {match_score:.2f}): {company} — {title}")
                    vs.record_outcome(job_id, vs.Outcome.SKIPPED_FILTER,
                                      reason=f"score {match_score:.2f}", url=navigate_url)
                    state.record(job_id, vs.Outcome.SKIPPED_FILTER)
                    continue

                log(f"\n  ▶ APPLYING [{match_score:.2f}]: {company or 'Unknown'} — {title or job_direct_url}")
                log(f"    URL: {navigate_url}")

                # Navigate directly to the job URL for Easy Apply using reused apply_page
                try:
                    chosen_resume = resume_for_job(desc, title)
                    status = apply_easy_apply(apply_page, navigate_url, answer_bank, dry_run,
                                              resume_path=chosen_resume)
                    log(f"  STATUS: {status}")

                    tracker_note = f"Stack match: {match_score:.2f}. LinkedIn Easy Apply. Resume: {chosen_resume.name}."
                    outcome = vs.classify(status)
                    if outcome in (vs.Outcome.APPLIED, vs.Outcome.APPLIED_UNCONFIRMED):
                        append_tracker(company, title, navigate_url, "Applied (confirmed) ✅", tracker_note)
                        applied_count[0] += 1
                    elif outcome is vs.Outcome.DRY_RUN:
                        append_tracker(company, title, navigate_url, "DRY_RUN", tracker_note)
                        applied_count[0] += 1
                    elif outcome is vs.Outcome.ALREADY_APPLIED:
                        append_tracker(company, title, navigate_url, "ALREADY_APPLIED ⏭️", tracker_note)
                    elif outcome is vs.Outcome.BLOCKED_PERMANENT:
                        # Not a failure — we declined to answer rather than guess.
                        append_tracker(company, title, navigate_url,
                                       f"BLOCKED ⚠️ ({status})", tracker_note)
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

        # Own our tabs explicitly. The previous code took context.pages[0] and [1],
        # which grabs whatever tabs happen to exist — including the user's own and
        # any left by another tool. That both destroyed the search results mid-run
        # (search_page could be navigated away by the apply flow) and navigated the
        # user's tabs away from under them.
        _pages = {}
        search_page = vb.named_page(context, "search", _pages)
        apply_page = vb.named_page(context, "apply", _pages)
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
            # Close only the tabs we created; never touch the user's.
            for _pg in _pages.values():
                try:
                    _pg.close()
                except Exception:
                    pass

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
