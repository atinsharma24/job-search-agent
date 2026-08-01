#!/usr/bin/env python3
"""
Durable dedup state for the apply pipeline.

Replaces a plain-list JSON file written with `Path.write_text()` after every job:
no lock, no atomic write, no backup, and a bare `json.loads` on read. A Ctrl-C
mid-write truncated it and the next run died with JSONDecodeError, taking the
whole dedup history with it.

--------------------------------------------------------------------------------
The dedup bug this exists to fix
--------------------------------------------------------------------------------
Both portals were wrong, in opposite directions:

  Naukri   never marked failures seen, so it retried every failure on all 62
           search URLs in a run and on every future run. One URL was logged
           54 times; 503 of 855 tracker rows are duplicates.

  LinkedIn marked EVERY outcome seen, so a single transient CAPTCHA permanently
           blacklisted a job that was never actually attempted.

Neither "always mark seen" nor "never mark seen on failure" is correct. A bounded
attempt counter is, and it fixes both with one mechanism: a retryable failure is
retried up to MAX_ATTEMPTS and then auto-promoted to blocked. A CAPTCHA is
explicitly NOT counted, because it says nothing about the job.

    from vault_state import load_state, record_outcome, Outcome, classify
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import shutil
import sys
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = VAULT_ROOT / "active_application_context" / "background_agent_state.json"
BAK_PATH = STATE_PATH.with_suffix(".json.bak")
LOCK_PATH = STATE_PATH.with_suffix(".json.lock")
TRACKER_PATH = VAULT_ROOT / "active_application_context" / "job_applications_tracker.md"

SCHEMA_VERSION = 2
MAX_ATTEMPTS = 2


class StateUnavailable(RuntimeError):
    """State could not be read. Do NOT proceed — an empty state re-applies to everything."""


class Outcome(str, Enum):
    APPLIED = "applied"
    APPLIED_UNCONFIRMED = "applied_unconfirmed"
    ALREADY_APPLIED = "already_applied"
    SKIPPED_FILTER = "skipped_filter"
    BLOCKED_PERMANENT = "blocked_permanent"
    FAILED_RETRYABLE = "failed_retryable"
    CAPTCHA = "captcha"
    DRY_RUN = "dry_run"


# outcome -> (mark applied, mark seen, mark blocked, count an attempt)
_EFFECTS: dict[Outcome, tuple[bool, bool, bool, bool]] = {
    Outcome.APPLIED:             (True,  True,  False, False),
    Outcome.APPLIED_UNCONFIRMED: (True,  True,  False, False),
    Outcome.ALREADY_APPLIED:     (True,  True,  False, False),
    Outcome.SKIPPED_FILTER:      (False, True,  False, False),
    Outcome.BLOCKED_PERMANENT:   (False, True,  True,  False),
    Outcome.FAILED_RETRYABLE:    (False, False, False, True),
    Outcome.CAPTCHA:             (False, False, False, False),
    Outcome.DRY_RUN:             (False, False, False, False),
}

# Maps the status strings the portal scripts already emit onto outcomes.
_CLASSIFY: tuple[tuple[str, Outcome], ...] = (
    (r"^submitted$|^applied", Outcome.APPLIED),
    (r"unconfirmed", Outcome.APPLIED_UNCONFIRMED),
    (r"already[_ ]applied", Outcome.ALREADY_APPLIED),
    (r"^dry_run$", Outcome.DRY_RUN),
    (r"captcha|challenge|security", Outcome.CAPTCHA),
    (r"^blocked|unanswerable|external|no_apply_button|no apply", Outcome.BLOCKED_PERMANENT),
    (r"^skip|below|filter|score", Outcome.SKIPPED_FILTER),
    (r"step_limit|timeout|^error|exception|failed", Outcome.FAILED_RETRYABLE),
)


def classify(status: str) -> Outcome:
    s = (status or "").strip().casefold()
    for pattern, outcome in _CLASSIFY:
        if re.search(pattern, s):
            return outcome
    return Outcome.FAILED_RETRYABLE


@dataclass
class VaultState:
    applied: set[str] = field(default_factory=set)
    seen: set[str] = field(default_factory=set)
    blocked: dict[str, dict] = field(default_factory=dict)
    attempts: dict[str, dict] = field(default_factory=dict)

    def should_skip(self, job_id: str) -> tuple[bool, str]:
        if job_id in self.applied:
            return True, "already applied"
        if job_id in self.blocked:
            return True, f"blocked ({self.blocked[job_id].get('reason', 'unknown')})"
        tries = self.attempts.get(job_id, {}).get("count", 0)
        if tries >= MAX_ATTEMPTS:
            return True, f"exhausted {tries} attempts"
        if job_id in self.seen:
            return True, "seen"
        return False, ""

    def record(self, job_id: str, outcome: Outcome, *, reason: str = "", url: str = "") -> None:
        if not job_id:
            return
        mark_applied, mark_seen, mark_blocked, count_attempt = _EFFECTS[outcome]
        now = datetime.now().isoformat(timespec="seconds")

        if mark_applied:
            self.applied.add(job_id)
            self.attempts.pop(job_id, None)
        if mark_seen:
            self.seen.add(job_id)
        if mark_blocked:
            self.blocked[job_id] = {"reason": reason or outcome.value, "at": now, "url": url}
        if count_attempt:
            rec = self.attempts.setdefault(job_id, {"count": 0})
            rec["count"] += 1
            rec["last"] = now
            rec["last_status"] = reason or outcome.value
            rec["url"] = url
            # Bounded retry: stop rather than looping on a job that keeps failing.
            if rec["count"] >= MAX_ATTEMPTS:
                self.seen.add(job_id)
                self.blocked[job_id] = {
                    "reason": f"max_attempts_exhausted ({rec.get('last_status','')})",
                    "at": now, "url": url,
                }

    def to_json(self) -> dict:
        return {
            "version": SCHEMA_VERSION,
            "applied_job_ids": sorted(self.applied),
            "seen_job_ids": sorted(self.seen),
            "blocked_jobs": self.blocked,
            "attempts": self.attempts,
        }

    def summary(self) -> str:
        return (f"{len(self.applied)} applied · {len(self.seen)} seen · "
                f"{len(self.blocked)} blocked · {len(self.attempts)} retrying")


def _from_json(data: dict) -> VaultState:
    blocked = data.get("blocked_jobs") or {}
    if isinstance(blocked, list):  # v1 stored a bare list
        blocked = {str(j): {"reason": "migrated_v1", "at": "", "url": ""} for j in blocked}
    return VaultState(
        applied=set(data.get("applied_job_ids") or []),
        seen=set(data.get("seen_job_ids") or []),
        blocked=blocked,
        attempts=data.get("attempts") or {},
    )


@contextmanager
def exclusive(path: Path = STATE_PATH):
    """Cross-process lock, so two portals can run concurrently without clobbering."""
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(LOCK_PATH, os.O_CREAT | os.O_RDWR)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


def load_state(path: Path = STATE_PATH, *, strict: bool = True) -> VaultState:
    """Read state. Falls back to .bak; raises rather than silently returning empty.

    Failing open here would be catastrophic: an empty state means re-applying to
    every job already done.
    """
    if not path.exists():
        return VaultState()
    try:
        return _from_json(json.loads(path.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, OSError) as exc:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        corrupt = path.with_suffix(f".json.corrupt.{stamp}")
        try:
            shutil.copy2(path, corrupt)  # preserve evidence, never overwrite
        except OSError:
            pass
        sys.stderr.write(f"[vault_state] state unreadable ({exc}); saved to {corrupt.name}\n")
        if BAK_PATH.exists():
            try:
                state = _from_json(json.loads(BAK_PATH.read_text(encoding="utf-8")))
                sys.stderr.write(f"[vault_state] recovered from backup: {state.summary()}\n")
                return state
            except Exception:
                pass
        if strict:
            raise StateUnavailable(
                f"{path} is corrupt and no usable backup exists. Refusing to run with "
                "empty state — that would re-apply to every completed job."
            ) from exc
        return VaultState()


def _atomic_write(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        try:
            shutil.copy2(path, BAK_PATH)
        except OSError:
            pass
    tmp = path.with_suffix(f".json.tmp.{os.getpid()}")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    with open(tmp, "rb") as fh:
        os.fsync(fh.fileno())
    os.replace(tmp, path)  # atomic within a filesystem


def save_state(state: VaultState, path: Path = STATE_PATH) -> None:
    with exclusive(path):
        _atomic_write(state.to_json(), path)


def record_outcome(job_id: str, outcome: Outcome, *, reason: str = "", url: str = "",
                   path: Path = STATE_PATH) -> None:
    """Read-modify-write under lock. Correct even with concurrent portal runs."""
    with exclusive(path):
        state = load_state(path, strict=False)
        state.record(job_id, outcome, reason=reason, url=url)
        _atomic_write(state.to_json(), path)


# --------------------------------------------------------------------------
# Migration
# --------------------------------------------------------------------------

_TRACKER_URL = re.compile(r"https?://[^\s|)\]]+")


def _tracker_applied_urls() -> set[str]:
    if not TRACKER_PATH.exists():
        return set()
    urls: set[str] = set()
    for line in TRACKER_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        low = line.casefold()
        if "applied" in low and "already" not in low and "failed" not in low:
            urls |= set(_TRACKER_URL.findall(line))
    return urls


def migrate(commit: bool = False) -> int:
    before = json.loads(STATE_PATH.read_text(encoding="utf-8")) if STATE_PATH.exists() else {}
    state = load_state(strict=False)

    raw_applied = before.get("applied_job_ids") or []
    dupes = len(raw_applied) - len(set(raw_applied))
    tracker_urls = _tracker_applied_urls()

    print(f"  schema version : {before.get('version', 1)} -> {SCHEMA_VERSION}")
    print(f"  applied        : {len(raw_applied)} rows, {len(state.applied)} unique "
          f"({dupes} duplicate{'s' if dupes != 1 else ''} collapsed)")
    print(f"  seen           : {len(state.seen)}")
    print(f"  blocked        : {len(state.blocked)}")
    print(f"  attempts       : {len(state.attempts)} (new in v2)")
    print(f"  tracker URLs marked applied: {len(tracker_urls)}")
    if not commit:
        print("\n  dry run — re-run with --yes to write")
        return 0
    save_state(state)
    print(f"\n  ✓ written: {STATE_PATH}")
    print(f"  ✓ backup : {BAK_PATH.name}")
    print(f"  {state.summary()}")
    return 0


def _selftest() -> int:
    import tempfile

    tmp = Path(tempfile.mkdtemp()) / "state.json"
    fails = 0

    def check(label, cond):
        nonlocal fails
        fails += not cond
        print(f"  {'✓' if cond else '✗'} {label}")

    s = VaultState()
    # Naukri's bug: a failure must be retried, but not forever.
    s.record("j1", Outcome.FAILED_RETRYABLE, reason="error:step_limit")
    check("1st failure -> retryable, not seen", s.should_skip("j1") == (False, ""))
    s.record("j1", Outcome.FAILED_RETRYABLE, reason="error:step_limit")
    skip, why = s.should_skip("j1")
    check(f"2nd failure -> auto-blocked ({why})", skip and "j1" in s.blocked)

    # LinkedIn's bug: a CAPTCHA must NOT blacklist a job.
    s.record("j2", Outcome.CAPTCHA)
    check("captcha leaves job retryable", s.should_skip("j2") == (False, ""))

    s.record("j3", Outcome.APPLIED)
    check("applied -> skipped", s.should_skip("j3")[0] and "j3" in s.applied)
    s.record("j4", Outcome.SKIPPED_FILTER)
    check("filtered -> seen, not applied", s.should_skip("j4")[0] and "j4" not in s.applied)

    save_state(s, tmp)
    check("round-trips", load_state(tmp).to_json() == s.to_json())

    tmp.write_text("{ this is not json")
    try:
        load_state(tmp, strict=True); ok = False
    except StateUnavailable:
        ok = True
    check("corrupt state raises rather than failing open", ok)

    check("classify(error:step_limit)", classify("error:step_limit") is Outcome.FAILED_RETRYABLE)
    check("classify(submitted)", classify("submitted") is Outcome.APPLIED)
    check("classify(blocked:unanswerable_question)",
          classify("blocked:unanswerable_question") is Outcome.BLOCKED_PERMANENT)
    check("classify(already_applied)", classify("already_applied") is Outcome.ALREADY_APPLIED)
    return 1 if fails else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Vault dedup state")
    ap.add_argument("--migrate", action="store_true")
    ap.add_argument("--yes", action="store_true", help="commit the migration")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        raise SystemExit(_selftest())
    if a.migrate:
        raise SystemExit(migrate(commit=a.yes))
    st = load_state(strict=False)
    print(f"  {STATE_PATH}")
    print(f"  {st.summary()}")
    raise SystemExit(0)
