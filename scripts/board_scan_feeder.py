#!/usr/bin/env python3
"""Phase A — Company board scanner: ingestion + dedup.

Polls the verified ATS feeds in ``company_board_registry/`` (Greenhouse, Lever,
Ashby, Workable), normalizes every posting to a common shape, and diffs against
persisted state so the same listing is never processed twice.

First-run behavior (per design): if no prior state exists, ALL currently-open
job ids are seeded as "already seen" and ZERO deltas are emitted (no digest on
the first pass). Deltas are only produced from the second run onward.

This module is import-friendly: ``load_registry()``, ``fetch_company_jobs()``
and ``fetch_many()`` are reused by ``board_filter.py`` for the pre-launch
sample and by the mailer.

Usage:
    python3 scripts/board_scan_feeder.py                 # scan, diff, print summary
    python3 scripts/board_scan_feeder.py --out FILE      # write new jobs (JSON array)
    python3 scripts/board_scan_feeder.py --dry-run       # never touch state
    python3 scripts/board_scan_feeder.py --reseed        # re-seed state from scratch (no digest)
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = VAULT_ROOT / "company_board_registry"
STATE_PATH = VAULT_ROOT / "active_application_context" / "board_scan_state.json"

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

# Polite crawl delays per ATS host. Lever publishes a 1s crawl delay; the
# others get a modest pause. This is a personal job hunt, not a real-time feed.
CRAWL_DELAY = {"greenhouse": 0.4, "lever": 1.0, "ashby": 0.4, "workable": 0.5}


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
def _fetch(url: str, timeout: int = 20, data: dict | None = None) -> tuple[int | None, bytes]:
    headers = {"User-Agent": UA, "Accept": "application/json"}
    body = None
    if data is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode()
    req = urllib.request.Request(url, headers=headers, data=body)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception:
        return None, b""


def _get_json(url: str, data: dict | None = None):
    st, raw = _fetch(url, data=data)
    if st == 200 and raw:
        try:
            return json.loads(raw)
        except Exception:
            return None
    return None


# --------------------------------------------------------------------------- #
# Registry
# --------------------------------------------------------------------------- #
def load_registry() -> list[dict]:
    """Return a flat list of registry entries across all ATS files."""
    entries: list[dict] = []
    for ats in ("greenhouse", "lever", "ashby", "workable"):
        path = REGISTRY_DIR / f"{ats}.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        entries.extend(data.get("companies", []))
    return entries


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")


def _make_job_id(ats: str, slug: str, native_id) -> str:
    return f"{ats}:{slug}:{native_id}"


# --------------------------------------------------------------------------- #
# Per-ATS parsers -> normalized job dict
# --------------------------------------------------------------------------- #
def _norm(ats, company, slug, native_id, title, department, location, remote, url, posted_at, description=""):
    return {
        "job_id": _make_job_id(ats, slug, native_id),
        "ats": ats,
        "company": company,
        "slug": slug,
        "title": (title or "").strip(),
        "department": (department or "").strip(),
        "location": (location or "").strip(),
        "remote": bool(remote),
        "url": url or "",
        "posted_at": posted_at or "",
        "description": description or "",
    }


def _parse_greenhouse(entry) -> list[dict]:
    slug, company = entry["slug"], entry["company"]
    jobs: list[dict] = []
    # departments endpoint carries department -> jobs, which we need for cutting.
    dep_data = _get_json(f"https://boards-api.greenhouse.io/v1/boards/{slug}/departments")
    if dep_data and dep_data.get("departments"):
        for dep in dep_data["departments"]:
            dep_name = dep.get("name", "")
            for j in dep.get("jobs", []) or []:
                loc = (j.get("location") or {}).get("name", "")
                jobs.append(_norm("greenhouse", company, slug, j.get("id"), j.get("title"),
                                  dep_name, loc, "remote" in loc.lower(),
                                  j.get("absolute_url"), j.get("updated_at") or j.get("first_published")))
        return jobs
    # fallback: flat jobs endpoint (no department)
    data = _get_json(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs")
    for j in (data or {}).get("jobs", []):
        loc = (j.get("location") or {}).get("name", "")
        jobs.append(_norm("greenhouse", company, slug, j.get("id"), j.get("title"),
                          "", loc, "remote" in loc.lower(),
                          j.get("absolute_url"), j.get("updated_at")))
    return jobs


def _parse_lever(entry) -> list[dict]:
    slug, company = entry["slug"], entry["company"]
    data = _get_json(f"https://api.lever.co/v0/postings/{slug}?mode=json") or []
    jobs = []
    for j in data:
        cats = j.get("categories") or {}
        loc = cats.get("location", "") or ""
        wp = (j.get("workplaceType") or "").lower()
        jobs.append(_norm("lever", company, slug, j.get("id"), j.get("text"),
                          cats.get("department", ""), loc,
                          wp == "remote" or "remote" in loc.lower(),
                          j.get("hostedUrl"), j.get("createdAt"),
                          j.get("descriptionPlain", "")))
    return jobs


def _parse_ashby(entry) -> list[dict]:
    slug, company = entry["slug"], entry["company"]
    data = _get_json(f"https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true") or {}
    jobs = []
    for j in data.get("jobs", []):
        jobs.append(_norm("ashby", company, slug, j.get("id"), j.get("title"),
                          j.get("department", ""), j.get("location", ""),
                          bool(j.get("isRemote")), j.get("jobUrl"), j.get("publishedAt"),
                          j.get("descriptionPlain", "")))
    return jobs


def _parse_workable(entry) -> list[dict]:
    slug, company = entry["slug"], entry["company"]
    data = _get_json(f"https://apply.workable.com/api/v3/accounts/{slug}/jobs",
                     data={"query": "", "location": [], "department": [], "worktype": [], "remote": []}) or {}
    jobs = []
    for j in data.get("results", []):
        loc = j.get("location") or {}
        loc_str = ", ".join(x for x in [loc.get("city"), loc.get("country")] if x) if isinstance(loc, dict) else str(loc)
        code = j.get("shortcode") or j.get("id")
        url = j.get("url") or f"https://apply.workable.com/{slug}/j/{code}/"
        jobs.append(_norm("workable", company, slug, code, j.get("title"),
                          j.get("department", ""), loc_str, bool(j.get("remote")),
                          url, j.get("published_on") or j.get("created_at")))
    return jobs


_PARSERS = {
    "greenhouse": _parse_greenhouse,
    "lever": _parse_lever,
    "ashby": _parse_ashby,
    "workable": _parse_workable,
}


def fetch_company_jobs(entry: dict) -> list[dict]:
    """Fetch + normalize all open postings for one registry entry."""
    parser = _PARSERS.get(entry["ats"])
    if not parser:
        return []
    try:
        return parser(entry)
    except Exception:
        return []


def fetch_many(entries: list[dict], polite: bool = True, log=lambda *_: None) -> list[dict]:
    """Fetch all entries sequentially, honoring per-ATS crawl delays."""
    all_jobs: list[dict] = []
    for e in entries:
        jobs = fetch_company_jobs(e)
        all_jobs.extend(jobs)
        log(f"  {e['company']:24s} {e['ats']:10s} {len(jobs):>4} roles")
        if polite:
            time.sleep(CRAWL_DELAY.get(e["ats"], 0.5))
    return all_jobs


# --------------------------------------------------------------------------- #
# State / dedup
# --------------------------------------------------------------------------- #
def _load_state() -> dict:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text())
        except Exception:
            pass
    return {"seen_board_job_ids": [], "notified_job_ids": [],
            "first_seeded_on": None, "last_run": None}


def _save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")


def scan(dry_run: bool = False, reseed: bool = False, log=print) -> dict:
    """Run a scan. Returns {new_jobs, total, seeded, ...}."""
    entries = load_registry()
    state = _load_state()
    if reseed:
        state = {"seen_board_job_ids": [], "notified_job_ids": [],
                 "first_seeded_on": None, "last_run": None}

    is_first_run = not state.get("seen_board_job_ids")
    log(f"Scanning {len(entries)} companies across the registry"
        f"{'  (FIRST RUN — seeding, no digest)' if is_first_run else ''}...")

    jobs = fetch_many(entries, polite=True, log=log)
    # de-dup within this scan by job_id (some ATSs list the same role twice)
    by_id = {j["job_id"]: j for j in jobs}
    current_ids = set(by_id)
    seen = set(state.get("seen_board_job_ids", []))

    now = datetime.now(timezone.utc).isoformat()
    if is_first_run:
        state["seen_board_job_ids"] = sorted(current_ids)
        state["first_seeded_on"] = now
        state["last_run"] = now
        if not dry_run:
            _save_state(state)
        log(f"\nSeeded {len(current_ids)} open job ids as already-seen. "
            f"No digest on first pass. Deltas start next run.")
        return {"new_jobs": [], "total": len(current_ids), "seeded": True,
                "dry_run": dry_run}

    new_ids = current_ids - seen
    new_jobs = [by_id[i] for i in new_ids]
    # keep seen bounded to what still exists + the new ones (drops closed roles)
    state["seen_board_job_ids"] = sorted(seen | current_ids)
    state["last_run"] = now
    if not dry_run:
        _save_state(state)

    log(f"\n{len(current_ids)} open roles, {len(new_jobs)} NEW since last run.")
    return {"new_jobs": new_jobs, "total": len(current_ids), "seeded": False,
            "dry_run": dry_run}


def main() -> None:
    ap = argparse.ArgumentParser(description="Company board scanner (Phase A: ingestion + dedup)")
    ap.add_argument("--out", type=Path, help="Write NEW normalized jobs as a JSON array to this path.")
    ap.add_argument("--dry-run", action="store_true", help="Do not modify state.")
    ap.add_argument("--reseed", action="store_true", help="Discard state and re-seed (no digest).")
    args = ap.parse_args()

    result = scan(dry_run=args.dry_run, reseed=args.reseed)
    if args.out:
        args.out.write_text(json.dumps(result["new_jobs"], indent=2) + "\n")
        print(f"Wrote {len(result['new_jobs'])} new jobs -> {args.out}")


if __name__ == "__main__":
    main()
