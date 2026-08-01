#!/usr/bin/env python3
"""
Pre-flight gate. Run this before any live apply run.

    python3 scripts/preflight_check.py            # exit 0 = safe to run
    python3 scripts/preflight_check.py --json
    python3 scripts/preflight_check.py --skip-network

Exit codes:  0 all pass · 1 at least one FAIL · 2 warnings only

This exists because the pipeline spent months submitting confidently wrong data:
16 LPA against a documented floor of 18, "10 LPA" into Naukri chatbots, 0 years of
experience, and a resume with zero extractable text uploaded 424 times. Nothing
checked, so nothing complained. Every check below corresponds to a defect that
actually shipped.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

VAULT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = VAULT_ROOT / "scripts"
CDP_URL = "http://localhost:9222"

PASS, WARN, FAIL = "PASS", "WARN", "FAIL"
results: list[tuple[str, str, str]] = []


def record(name: str, status: str, detail: str = "") -> None:
    results.append((name, status, detail))


def check(name: str):
    """Decorator: run a check, convert an exception into a FAIL."""
    def wrap(fn):
        try:
            status, detail = fn()
        except Exception as exc:  # a check must never crash the gate
            status, detail = FAIL, f"{type(exc).__name__}: {exc}"
        record(name, status, detail)
        return fn
    return wrap


# --------------------------------------------------------------------------

@check("canon_parse")
def _canon_parse():
    import vault_config as vc

    vc.load_facts(); vc.load_logistics()
    return PASS, f"{vc.FACT_SHEET_PATH.name} + {vc.LOGISTICS_PATH.name}"


@check("canon_sane")
def _canon_sane():
    import vault_config as vc

    problems = vc.self_check()
    if problems:
        return FAIL, "; ".join(problems)
    return PASS, (f"current {vc.current_ctc_lpa()} → expected {vc.expected_ctc_range()} LPA, "
                  f"notice {vc.notice_period_days()}d, {vc.experience_months()}mo exp")


@check("floor_redacted")
def _floor_redacted():
    """The PRIVATE 15 LPA walk-away floor must not survive loading."""
    import vault_config as vc

    blob = json.dumps(vc.load_facts()) + json.dumps(vc.load_logistics())
    leaked = [k for k in re.findall(r'"([^"]+)"\s*:', blob)
              if any(p.search(k) for p in vc._PRIVATE_KEY_PATTERNS)]
    if leaked:
        return FAIL, f"private keys survived redaction: {sorted(set(leaked))[:5]}"
    vc.verify_bank(vc.build_answer_bank())
    return PASS, "no private-floor key or value reachable from the answer bank"


@check("outbound_scan")
def _outbound_scan():
    """Nothing we transmit may state the private floor as money."""
    import vault_config as vc
    from vault_resume import PDF_DIR, extractable_text

    targets: list[tuple[str, str]] = []
    for pdf in sorted(PDF_DIR.glob("*.pdf")):
        try:
            targets.append((pdf.name, extractable_text(pdf)))
        except Exception:
            pass
    for name in ("staged_application_resume.md", "staged_application_resume.pdf"):
        p = VAULT_ROOT / "active_application_context" / name
        if not p.exists():
            continue
        if p.suffix == ".pdf":
            targets.append((name, extractable_text(p)))
        else:
            targets.append((name, p.read_text(encoding="utf-8", errors="replace")))
    for key, value in vc.build_answer_bank().items():
        if isinstance(value, str):
            targets.append((f"answer_bank[{key}]", value))

    leaks = []
    for label, text in targets:
        for line in (text or "").splitlines():
            try:
                vc.assert_no_private_floor(line, context=label)
            except vc.PrivateDataLeak:
                leaks.append(f"{label}: {line.strip()[:70]}")
                break
    if leaks:
        return FAIL, f"{len(leaks)} outbound artifact(s) state the private floor: {leaks[:3]}"
    return PASS, f"{len(targets)} outbound artifacts scanned, clean"


@check("resume_health")
def _resume_health():
    from vault_resume import audit, ROUTING, category_path, extractable_text

    problems = audit()
    if problems:
        return FAIL, "; ".join(problems)
    sizes = [len(re.sub(r"\s+", "", extractable_text(category_path(c)))) for c, _ in ROUTING]
    return PASS, f"{len(sizes)} category resumes, {min(sizes)}–{max(sizes)} extractable chars"


@check("no_bad_resume_refs")
def _no_bad_resume_refs():
    """The image-only PDFs must not be referenced by any apply script."""
    bad = []
    for py in sorted(SCRIPTS.glob("playwright_*.py")):
        text = py.read_text(encoding="utf-8", errors="replace")
        for token in ("NewResDocPdf", "2026New1"):
            if token in text:
                bad.append(f"{py.name}:{token}")
    if bad:
        return FAIL, f"image-only / superseded resume referenced: {bad}"
    return PASS, "no script references an unreadable resume"


@check("answers_sane")
def _answers_sane():
    """Screening policy must refuse to guess and must never blind-affirm."""
    import vault_answers as va
    import vault_config as vc

    bank = vc.build_answer_bank()
    expect = {
        "Do you require visa sponsorship?": va.Decision.NO,
        "Are you willing to sign a 2 year bond?": va.Decision.NO,
        "Are you legally authorized to work in India?": va.Decision.YES,
        "What is your expected CTC?": va.Decision.VALUE,
        "": va.Decision.ABSTAIN,
        "Some question nobody anticipated": va.Decision.ABSTAIN,
    }
    bad = [q for q, want in expect.items()
           if va.answer_for_question(q, bank=bank).decision is not want]
    if bad:
        return FAIL, f"policy regression on: {bad}"
    if va.is_option_allowed("Do you require visa sponsorship?", "Yes", bank=bank):
        return FAIL, "blind-yes gate is open — would affirm a sponsorship question"
    return PASS, "hard-no / hard-yes / abstain rules behave"


@check("state_health")
def _state_health():
    path = VAULT_ROOT / "active_application_context" / "background_agent_state.json"
    if not path.exists():
        return WARN, "no state file yet (first run)"
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return FAIL, f"state file is corrupt: {exc}"
    applied = state.get("applied_job_ids", [])
    seen = state.get("seen_job_ids", [])
    dupes = len(applied) - len(set(applied))
    detail = f"{len(applied)} applied, {len(seen)} seen, {len(state.get('blocked_jobs') or [])} blocked"
    if dupes:
        return WARN, detail + f" — {dupes} duplicate applied id(s)"
    return PASS, detail


@check("imports")
def _imports():
    import importlib

    mods = ["vault_config", "vault_answers", "vault_resume", "playwright_form_helpers"]
    for m in mods:
        importlib.import_module(m)
    return PASS, f"{len(mods)} modules import cleanly"


def _network_checks() -> None:
    @check("cdp_reachable")
    def _cdp():
        try:
            with urllib.request.urlopen(f"{CDP_URL}/json/version", timeout=3) as r:
                v = json.loads(r.read()).get("Browser", "?")
            return PASS, v
        except Exception:
            return FAIL, ("Chrome not reachable on :9222 — start it with "
                          "`bash scripts/run_chrome_background.sh --start`")

    @check("instahyre_profile_resume")
    def _instahyre():
        return WARN, ("Instahyre applies with the resume attached to your PROFILE, not an "
                      "uploaded file — verify it manually at instahyre.com")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--skip-network", action="store_true")
    args = ap.parse_args()

    if not args.skip_network:
        _network_checks()

    if args.json:
        print(json.dumps([{"check": n, "status": s, "detail": d} for n, s, d in results], indent=2))
    else:
        print("\n  PRE-FLIGHT\n  " + "─" * 74)
        for name, status, detail in results:
            icon = {PASS: "✓", WARN: "!", FAIL: "✗"}[status]
            print(f"  {icon} {name:<24} {detail}")
        print("  " + "─" * 74)

    fails = sum(1 for _, s, _ in results if s == FAIL)
    warns = sum(1 for _, s, _ in results if s == WARN)
    if not args.json:
        verdict = ("BLOCKED — do not run the pipeline" if fails
                   else "OK with warnings" if warns else "OK — safe to run")
        print(f"  {len(results) - fails - warns} pass · {warns} warn · {fails} fail   →  {verdict}\n")
    return 1 if fails else (2 if warns else 0)


if __name__ == "__main__":
    raise SystemExit(main())
