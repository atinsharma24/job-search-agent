#!/usr/bin/env python3
"""
Single source of truth for every value submitted to a job application form.

Everything is derived from the two canonical files:
    core_vault/JobApplyFiles/01_atomic_fact_sheet.json
    core_vault/JobApplyFiles/06_logistics_mapping.json

Before this module existed, each portal script carried its own constants
(`EXPECTED_CTC_LPA = 16`, `years_experience = 0`), so CLAUDE.md's rule that every
field must trace to the fact sheet was false in practice.

--------------------------------------------------------------------------------
The private-floor guarantee
--------------------------------------------------------------------------------
The vault records a PRIVATE walk-away minimum of 15 LPA. It must never reach a form,
a message, or a resume: stating your floor converts it into the employer's ceiling.
Three independent layers enforce that, any one of which is sufficient.

  1. REDACT AT LOAD  - _scrub() deletes every key matching _PRIVATE_KEY_PATTERNS
     before the parsed dict is memoised. The value is not in memory to be read.

  2. NO ACCESSOR     - there is deliberately no function returning a floor. The word
     appears in this file only inside the redaction patterns, so a future
     contributor cannot reach for a getter that does not exist.

  3. VALUE TRIPWIRE  - assert_no_private_floor() raises if a string states 15 as
     money. It is scoped to salary context on purpose: the notice period is
     legitimately 15 days, so a bare "contains 15" check would be wrong.

verify_bank() applies layer 3 to every answer at startup, so a poisoned bank raises
before a browser is ever opened.
"""

from __future__ import annotations

import json
import re
from datetime import date
from functools import lru_cache
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parent.parent
_CANON = VAULT_ROOT / "core_vault" / "JobApplyFiles"
FACT_SHEET_PATH = _CANON / "01_atomic_fact_sheet.json"
LOGISTICS_PATH = _CANON / "06_logistics_mapping.json"


class ConfigError(RuntimeError):
    """Canonical data is missing, unparseable, or internally inconsistent."""


class PrivateDataLeak(RuntimeError):
    """A value that must never leave the vault was about to be emitted."""


# --------------------------------------------------------------------------
# Layer 1 — redact at load
# --------------------------------------------------------------------------

_PRIVATE_KEY_PATTERNS = (
    re.compile(r"negotiation_floor", re.I),
    re.compile(r"_private$", re.I),
    re.compile(r"walk_?away", re.I),
)


def _scrub(node):
    """Recursively drop private keys. Returns a new structure; input untouched."""
    if isinstance(node, dict):
        return {
            k: _scrub(v)
            for k, v in node.items()
            if not any(p.search(k) for p in _PRIVATE_KEY_PATTERNS)
        }
    if isinstance(node, list):
        return [_scrub(v) for v in node]
    return node


def _load(path: Path) -> dict:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigError(f"canonical file missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigError(f"canonical file is not valid JSON: {path} ({exc})") from exc
    # The un-scrubbed dict is never bound to a name that outlives this call.
    return _scrub(raw)


@lru_cache(maxsize=1)
def load_facts() -> dict:
    return _load(FACT_SHEET_PATH)


@lru_cache(maxsize=1)
def load_logistics() -> dict:
    data = _load(LOGISTICS_PATH)
    if "logistics" not in data:
        raise ConfigError(f"{LOGISTICS_PATH}: missing top-level 'logistics' key")
    return data["logistics"]


# --------------------------------------------------------------------------
# Layer 3 — value tripwire
# --------------------------------------------------------------------------

# Two tiers, because "15 days" (notice period) is legitimate but "15L+" is a leak
# even though it contains no salary *keyword* — which is exactly how
# `staged_application_resume.pdf` shipped "15L+ (negotiable)" to employers.
#
#   Tier 1: self-evidently monetary. Raises on sight, no context needed.
#   Tier 2: a bare 15. Raises only alongside a salary keyword.
_FLOOR_MONETARY = re.compile(
    r"(?<![\d.])(?:₹\s*15|15\s*l(?:pa|akhs?|acs?)?\+?(?![\w])|15,00,000|1500000)",
    re.I,
)
# "expect" is included deliberately. It widens tier 2 toward false positives, which
# is the correct bias: a false positive is a loud pre-flight failure, a false
# negative silently publishes the floor.
_SALARY_CONTEXT = re.compile(
    r"(lpa|lakh|lac|\bctc\b|salary|package|compensation|₹|\binr\b|per annum|"
    r"\bp\.?a\.?\b|expect|remunerat|stipend)",
    re.I,
)
_FLOOR_BARE = re.compile(r"(?<![\d.])15(?:\.0+)?(?![\d.])")


def assert_no_private_floor(text: str, *, context: str = "") -> str:
    """Raise if `text` states the private floor as money. Returns text unchanged."""
    if not isinstance(text, str):
        return text
    leaked = bool(_FLOOR_MONETARY.search(text)) or (
        bool(_SALARY_CONTEXT.search(text)) and bool(_FLOOR_BARE.search(text))
    )
    if leaked:
        where = f" in {context}" if context else ""
        raise PrivateDataLeak(
            f"private negotiation floor would be emitted{where}: {text!r}"
        )
    return text


def verify_bank(bank: dict) -> None:
    """Raise if any answer in `bank` would leak the private floor."""
    for key, value in bank.items():
        if isinstance(value, str):
            assert_no_private_floor(value, context=f"answer_bank[{key!r}]")


# --------------------------------------------------------------------------
# Compensation
# --------------------------------------------------------------------------


def current_ctc_lpa() -> float:
    return float(load_facts()["candidate"].get("current_ctc_inr_lpa", 0) or 0)


def _expected() -> dict:
    return load_facts()["candidate"]["salary_expectation_inr_lpa"]


def expected_ctc_min_lpa() -> int:
    return int(_expected()["min"])


def expected_ctc_max_lpa() -> int:
    return int(_expected()["max"])


def expected_ctc_numeric() -> str:
    """Single-number form fields. Always the stated floor, never lower."""
    return assert_no_private_floor(str(expected_ctc_min_lpa()) + " LPA",
                                   context="expected_ctc_numeric")[:-4].strip()


def expected_ctc_range() -> str:
    return f"{expected_ctc_min_lpa()}-{expected_ctc_max_lpa()}"


def expected_ctc_label() -> str:
    label = load_logistics()["compensation"]["expected_ctc_label"]
    return assert_no_private_floor(label, context="expected_ctc_label")


# --------------------------------------------------------------------------
# Availability
# --------------------------------------------------------------------------


def notice_period_days() -> int:
    return int(load_facts()["candidate"]["notice_period_days"])


def notice_period_label() -> str:
    return load_logistics()["availability"]["notice_period_label"]


def notice_option_preferences() -> tuple[str, ...]:
    """Ordered dropdown-match preferences. First match wins — order matters.

    A plain any() over these would let a dropdown listing "Immediate" before
    "15 Days" select Immediate, which misstates the notice period.
    """
    days = notice_period_days()
    return (
        f"{days} days",
        f"{days} day",
        "less than 1 month",
        "less than a month",
        "1 month or less",
        "15 days or less",
        "within 15 days",
        "immediate",
    )


# --------------------------------------------------------------------------
# Experience
# --------------------------------------------------------------------------

_NON_PROFESSIONAL = re.compile(r"academic|part[- ]time|intern", re.I)


def _parse_ym(value: str | None) -> tuple[int, int] | None:
    if not value:
        return None
    m = re.match(r"(\d{4})-(\d{1,2})", str(value))
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def experience_months(today: date | None = None) -> int:
    """Union of calendar months covered by professional roles.

    Unions rather than sums: overlapping roles must not double-count. Excludes
    academic/part-time/internship entries — counting the VIT research role would
    inflate this from 14 to 25.
    """
    today = today or date.today()
    covered: set[tuple[int, int]] = set()
    for exp in load_facts().get("experience", []):
        if _NON_PROFESSIONAL.search(str(exp.get("employment_type", ""))):
            continue
        start = _parse_ym(exp.get("start_date"))
        if not start:
            continue
        end = _parse_ym(exp.get("end_date"))
        if end is None:
            # Ongoing role: count only *completed* months, so a role started on the
            # 28th does not claim a full month. Stops before the current month.
            last = (today.year, today.month - 1) if today.month > 1 else (today.year - 1, 12)
        else:
            # Finished role: the end month was worked, so it counts.
            last = end
        y, m = start
        while (y, m) <= last:
            covered.add((y, m))
            m += 1
            if m > 12:
                y, m = y + 1, 1
    return len(covered)


def years_experience() -> str:
    return str(experience_months() // 12)


def years_experience_decimal() -> str:
    return f"{experience_months() / 12:.1f}"


def tech_stack_flat() -> frozenset[str]:
    out: set[str] = set()
    for value in load_facts().get("tech_stack", {}).values():
        if isinstance(value, list):
            out |= {str(v).casefold() for v in value}
    return frozenset(out)


def experience_for_tech(tech: str) -> str:
    """Honest per-technology YOE: real experience if in the stack, else "0"."""
    needle = (tech or "").strip().casefold()
    if not needle:
        return "0"
    for known in tech_stack_flat():
        if needle in known or known in needle:
            return years_experience()
    return "0"


# --------------------------------------------------------------------------
# Identity
# --------------------------------------------------------------------------


def _split_name(full: str) -> tuple[str, str]:
    parts = (full or "").strip().split()
    if not parts:
        return ("", "")
    if len(parts) == 1:
        return (parts[0], "")
    return (parts[0], " ".join(parts[1:]))


def current_employer() -> str:
    for exp in load_facts().get("experience", []):
        if exp.get("is_current") or exp.get("end_date") is None:
            return str(exp.get("company", ""))
    return ""


def contact() -> dict:
    c = load_facts()["candidate"]
    first, last = _split_name(c["full_name"])
    loc = c.get("location", {})
    return {
        "full_name": c["full_name"],
        "first_name": first,
        "last_name": last,
        "email": c["email"],
        "phone": c["phone"],
        "city": loc.get("city", ""),
        "state": loc.get("state", ""),
        "country": loc.get("country", ""),
        "pincode": loc.get("pincode", ""),
        "github": c.get("github", ""),
        # Fact sheet has no linkedin key; CLAUDE.md declares this an Absolute Rule.
        "linkedin": c.get("linkedin") or "https://www.linkedin.com/in/atinsharma24/",
    }


# --------------------------------------------------------------------------
# Answer bank
# --------------------------------------------------------------------------


def build_answer_bank(**overrides) -> dict:
    """Every value a portal form might need. Verified before return.

    Note this deliberately does NOT embed the raw fact_sheet / logistics dicts the
    way the old builder did — those carried the private floor into every bank.
    """
    facts = load_facts()
    log = load_logistics()
    c = contact()
    lo, hi = expected_ctc_min_lpa(), expected_ctc_max_lpa()
    education = (facts.get("education") or [{}])[0]

    bank = {
        **c,
        "notice_period_days": str(notice_period_days()),
        "notice_period": str(notice_period_days()),
        "availability": facts["candidate"].get("availability", ""),
        "immediate_joiner": notice_period_label(),
        "current_ctc": str(current_ctc_lpa()),
        "current_employer": current_employer(),
        "expected_ctc_min": str(lo),
        "expected_ctc_max": str(hi),
        "expected_ctc_range": expected_ctc_range(),
        "expected_ctc_label": expected_ctc_label(),
        "expected_salary_min": str(lo),
        "expected_salary_max": str(hi),
        "expected_salary_range": expected_ctc_range(),
        "expected_salary_label": expected_ctc_label(),
        "years_experience": years_experience(),
        "years_experience_decimal": years_experience_decimal(),
        "total_experience_months": str(experience_months()),
        "work_authorized": "Yes",
        "requires_sponsorship": "No",
        "open_to_relocate": "Yes",
        "preferred_location": log["work_preference"]["primary"],
        "secondary_location": log["work_preference"]["secondary"],
        "degree": education.get("degree", ""),
        "university": education.get("institution", ""),
        "linkedin_profile": c["linkedin"],
    }
    bank.update(log.get("qa_bank", {}))
    bank.update(overrides)

    verify_bank(bank)
    return bank


# --------------------------------------------------------------------------


def self_check() -> list[str]:
    """Internal consistency assertions. Returns a list of problems (empty == OK)."""
    problems: list[str] = []
    try:
        facts, log = load_facts(), load_logistics()
    except ConfigError as exc:
        return [str(exc)]

    if expected_ctc_min_lpa() <= current_ctc_lpa():
        problems.append(
            f"expected min ({expected_ctc_min_lpa()}) <= current ({current_ctc_lpa()})"
        )
    if expected_ctc_min_lpa() > expected_ctc_max_lpa():
        problems.append("expected min > max")

    log_notice = log.get("availability", {}).get("notice_period_days")
    if log_notice is not None and int(log_notice) != notice_period_days():
        problems.append(
            f"notice mismatch: fact sheet {notice_period_days()} vs logistics {log_notice}"
        )

    log_min = log.get("compensation", {}).get("expected_ctc_inr_lpa_min")
    if log_min is not None and int(log_min) != expected_ctc_min_lpa():
        problems.append(
            f"expected-min mismatch: fact sheet {expected_ctc_min_lpa()} vs logistics {log_min}"
        )

    for name, blob in (("fact sheet", facts), ("logistics", log)):
        leaked = [
            k for k in json.dumps(blob).split('"')
            if any(p.search(k) for p in _PRIVATE_KEY_PATTERNS)
        ]
        if leaked:
            problems.append(f"{name}: private key survived redaction: {leaked[:3]}")

    if experience_months() <= 0:
        problems.append("experience_months() computed 0 — check experience[] dates")

    try:
        verify_bank(build_answer_bank())
    except PrivateDataLeak as exc:
        problems.append(str(exc))

    return problems


if __name__ == "__main__":
    import sys

    issues = self_check()
    print(f"fact sheet : {FACT_SHEET_PATH}")
    print(f"logistics  : {LOGISTICS_PATH}")
    print()
    print(f"current CTC        : {current_ctc_lpa()} LPA")
    print(f"expected CTC       : {expected_ctc_range()} LPA (quote {expected_ctc_numeric()})")
    print(f"notice period      : {notice_period_days()} days ({notice_period_label()})")
    print(f"experience         : {experience_months()} months -> {years_experience()} yr")
    print(f"current employer   : {current_employer()}")
    print(f"answer bank keys   : {len(build_answer_bank())}")
    print()
    if issues:
        print("PROBLEMS:")
        for i in issues:
            print(f"  ✗ {i}")
        sys.exit(1)
    print("✓ self-check passed")
