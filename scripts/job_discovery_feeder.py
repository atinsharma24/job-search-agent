#!/usr/bin/env python3

import argparse
import json
import re
from pathlib import Path
from typing import Iterable
from urllib.parse import quote

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


VAULT_ROOT = Path(__file__).resolve().parents[1]
TRACKER_PATH = VAULT_ROOT / "active_application_context" / "job_applications_tracker.md"
DISCOVERY_DEBUG_PATH = VAULT_ROOT / "logs" / "discovery_debug.png"

MAX_RESULTS = 5
SEARCH_TERMS = [
    "MERN",
    "TypeScript",
    "Next.js",
    "Python",
    "AI Engineer",
]

STACK_PATTERNS = [
    (r"\bmern\b", "MERN"),
    (r"\btypescript\b", "TypeScript"),
    (r"\bnext(?:\.js|js)?\b", "Next.js"),
    (r"\breact(?:\.js)?\b", "React"),
    (r"\bnode(?:\.js)?\b", "Node.js"),
    (r"\bpython\b", "Python"),
    (r"\bdjango\b", "Django"),
    (r"\bfastapi\b", "FastAPI"),
    (r"\bai\b", "AI"),
    (r"\bllm\b", "LLM"),
    (r"\brag\b", "RAG"),
    (r"\bpostgres(?:ql)?\b", "PostgreSQL"),
    (r"\bmongodb\b", "MongoDB"),
    (r"\baws\b", "AWS"),
    (r"\bdocker\b", "Docker"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Headless Playwright feeder for recent, unapplied LinkedIn and Wellfound jobs."
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        help="Optional path to write the discovery JSON array.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=MAX_RESULTS,
        help=f"Maximum jobs to emit. Default: {MAX_RESULTS}",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "")).strip().casefold()


def load_applied_pairs() -> set[tuple[str, str]]:
    if not TRACKER_PATH.exists():
        return set()

    applied: set[tuple[str, str]] = set()
    for line in TRACKER_PATH.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        columns = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(columns) < 5:
            continue
        if columns[0].lower() == "date" or columns[0].startswith("---"):
            continue
        company = normalize(columns[1])
        job_title = normalize(columns[2])
        status = normalize(columns[4])
        if company and job_title and status == "applied":
            applied.add((company, job_title))
    return applied


def extract_required_stack(text: str) -> list[str]:
    normalized_text = text or ""
    stack: list[str] = []
    for pattern, label in STACK_PATTERNS:
        if re.search(pattern, normalized_text, re.I) and label not in stack:
            stack.append(label)
    return stack


def dedupe_key(job_title: str, company: str) -> tuple[str, str]:
    return (normalize(company), normalize(job_title))


def linkedin_search_url() -> str:
    query = quote("AI Engineer OR Full Stack Engineer OR Software Engineer")
    location = quote("India")
    return (
        "https://www.linkedin.com/jobs/search/"
        f"?keywords={query}&location={location}&f_AL=true&sortBy=DD"
    )


def wellfound_search_url() -> str:
    query = quote("AI Engineer TypeScript Next.js Python MERN")
    return f"https://wellfound.com/jobs?query={query}"


def collect_linkedin(page, applied_pairs: set[tuple[str, str]], limit: int) -> list[dict]:
    jobs: list[dict] = []
    seen: set[tuple[str, str]] = set()

    page.goto(linkedin_search_url(), wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3500)

    cards = page.locator(
        "li.jobs-search-results__list-item, div.job-search-card, li:has(a[href*='/jobs/view/'])"
    )
    card_count = min(cards.count(), 20)
    for index in range(card_count):
        if len(jobs) >= limit:
            break
        card = cards.nth(index)
        try:
            if card.is_visible():
                card.click(timeout=3000)
                page.wait_for_timeout(1200)
        except Exception:
            pass

        card_text = card.inner_text(timeout=3000) if card.count() > 0 else ""
        title_locator = card.locator(
            "a.job-card-list__title, a.job-search-card__title, strong, h3, [data-tracking-control-name*='title']"
        )
        company_locator = card.locator(
            "div.artdeco-entity-lockup__subtitle, h4.base-search-card__subtitle, a.hidden-nested-link, .job-card-container__company-name"
        )
        title = ""
        company = ""
        if title_locator.count() > 0:
            title = title_locator.first.inner_text().strip()
        if company_locator.count() > 0:
            company = company_locator.first.inner_text().strip()

        if not title:
            title = card_text.splitlines()[0].strip() if card_text.strip() else ""
        if not company:
            lines = [line.strip() for line in card_text.splitlines() if line.strip()]
            company = lines[1] if len(lines) > 1 else ""

        details_text = ""
        for locator in [
            page.locator("div.jobs-search__job-details--wrapper"),
            page.locator("div.jobs-details"),
            page.locator("main"),
        ]:
            if locator.count() > 0:
                try:
                    details_text = locator.first.inner_text(timeout=3000)
                    if details_text.strip():
                        break
                except Exception:
                    pass

        url = ""
        anchor = card.locator("a[href*='/jobs/view/']")
        if anchor.count() > 0:
            href = anchor.first.get_attribute("href") or ""
            if href.startswith("/"):
                url = f"https://www.linkedin.com{href}"
            else:
                url = href

        key = dedupe_key(title, company)
        if not title or not company or key in applied_pairs or key in seen:
            continue

        required_stack = extract_required_stack(f"{card_text}\n{details_text}") or SEARCH_TERMS
        seen.add(key)
        jobs.append(
            {
                "job_title": title,
                "company": company,
                "required_stack": required_stack,
                "application_url": url,
            }
        )

    return jobs


def collect_wellfound(page, applied_pairs: set[tuple[str, str]], limit: int) -> list[dict]:
    jobs: list[dict] = []
    seen: set[tuple[str, str]] = set()

    page.goto(wellfound_search_url(), wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3500)

    job_links = page.locator("a[href*='/jobs/']")
    link_count = min(job_links.count(), 30)
    for index in range(link_count):
        if len(jobs) >= limit:
            break
        link = job_links.nth(index)
        try:
            href = link.get_attribute("href") or ""
            if not href or "/jobs/" not in href:
                continue
            if href.startswith("/"):
                url = f"https://wellfound.com{href}"
            elif href.startswith("http"):
                url = href
            else:
                url = f"https://wellfound.com/{href.lstrip('/')}"

            text = link.inner_text(timeout=2000).strip()
            container = link.locator("xpath=ancestor::*[self::div or self::li][1]")
            container_text = ""
            if container.count() > 0:
                try:
                    container_text = container.first.inner_text(timeout=2500)
                except Exception:
                    pass

            title = text
            company = ""
            if container.count() > 0:
                title_candidates = container.first.locator("h2, h3, h4, strong")
                if title_candidates.count() > 0:
                    title = title_candidates.first.inner_text().strip() or title

                company_candidates = container.first.locator(
                    "[data-test*='company'], a[href*='/company/'], span"
                )
                for candidate_index in range(min(company_candidates.count(), 6)):
                    candidate_text = company_candidates.nth(candidate_index).inner_text().strip()
                    if candidate_text and candidate_text != title and len(candidate_text) < 80:
                        company = candidate_text
                        break

            if not company:
                lines = [line.strip() for line in container_text.splitlines() if line.strip()]
                for line in lines:
                    if line != title and len(line) < 80:
                        company = line
                        break

            key = dedupe_key(title, company)
            if not title or not company or key in applied_pairs or key in seen:
                continue

            required_stack = extract_required_stack(container_text or text) or SEARCH_TERMS
            seen.add(key)
            jobs.append(
                {
                    "job_title": title,
                    "company": company,
                    "required_stack": required_stack,
                    "application_url": url,
                }
            )
        except Exception:
            continue

    return jobs


def trim_jobs(jobs: Iterable[dict], limit: int) -> list[dict]:
    trimmed: list[dict] = []
    seen_urls: set[str] = set()
    for job in jobs:
        url = job.get("application_url", "")
        if url in seen_urls:
            continue
        seen_urls.add(url)
        trimmed.append(job)
        if len(trimmed) >= limit:
            break
    return trimmed


def main() -> int:
    args = parse_args()
    applied_pairs = load_applied_pairs()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1200})
        try:
            linkedin_page = context.new_page()
            wellfound_page = context.new_page()

            jobs: list[dict] = []
            try:
                jobs.extend(collect_linkedin(linkedin_page, applied_pairs, args.limit))
            except PlaywrightTimeoutError:
                pass
            except Exception:
                pass

            remaining = max(0, args.limit - len(jobs))
            if remaining > 0:
                try:
                    jobs.extend(collect_wellfound(wellfound_page, applied_pairs, remaining))
                except PlaywrightTimeoutError:
                    pass
                except Exception:
                    pass

            jobs = trim_jobs(jobs, args.limit)
            if args.dry_run:
                DISCOVERY_DEBUG_PATH.parent.mkdir(parents=True, exist_ok=True)
                target_page = linkedin_page
                if len(jobs) == 0:
                    target_page = wellfound_page
                target_page.screenshot(path=str(DISCOVERY_DEBUG_PATH), full_page=False)
            output = json.dumps(jobs, indent=2)
            if args.output_file:
                args.output_file.write_text(output + "\n", encoding="utf-8")
            print(output)
            return 0
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    raise SystemExit(main())
