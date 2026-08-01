#!/usr/bin/env python3
"""
Clear jobs that were rejected by a scorer that could not read job descriptions.

    python3 scripts/vault_state_rescan.py            # report only
    python3 scripts/vault_state_rescan.py --yes      # apply

--------------------------------------------------------------------------------
Why this exists
--------------------------------------------------------------------------------
Until 1 Aug 2026 the LinkedIn description selectors matched nothing, so score_job()
ran on the title alone. Jobs were then skipped as "low match" against a 0.45
threshold using a number that was missing most of its input.

The evidence is in the tracker:

    historical scores (title-only): n=584  median 0.44
    today's scores (JD included):   n=25   median 0.70

A median sitting exactly on the threshold is what a broken scorer looks like.
Roughly half the evaluated jobs were rejected for lack of signal rather than lack
of fit — one posting scoring 0.40 title-only scored 0.97 once its description was
read.

LinkedIn compounded it by marking EVERY outcome seen, including transient failures
and CAPTCHAs, so jobs that were never actually attempted are recorded as evaluated.

--------------------------------------------------------------------------------
What this does and does not touch
--------------------------------------------------------------------------------
  CLEARS   seen-only entries — evaluated, never applied to, never blocked
  KEEPS    applied  — we did apply; re-applying would be spam
  KEEPS    blocked  — a real permanent reason (external ATS, unanswerable question)
  KEEPS    attempts — the bounded-retry counter stays intact

Clearing is cheap: it only affects jobs that reappear in a future search. Anything
genuinely unsuitable re-skips on the title pre-filter without a page load.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vault_state as vs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--yes", action="store_true", help="apply the change")
    args = ap.parse_args()

    state = vs.load_state()
    seen_only = state.seen - state.applied - set(state.blocked)

    print(f"  state file : {vs.STATE_PATH}")
    print(f"  applied    : {len(state.applied):>5}   (kept)")
    print(f"  blocked    : {len(state.blocked):>5}   (kept)")
    print(f"  attempts   : {len(state.attempts):>5}   (kept)")
    print(f"  seen       : {len(state.seen):>5}")
    print(f"  seen-only  : {len(seen_only):>5}   <- to clear")
    print()
    print("  These were evaluated by a scorer that could not read job descriptions.")
    print("  Clearing lets them be re-scored properly if they reappear in a search.")

    if not args.yes:
        print("\n  report only — re-run with --yes to apply")
        return 0

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = vs.STATE_PATH.with_suffix(f".json.pre-rescan.{stamp}")
    shutil.copy2(vs.STATE_PATH, backup)

    state.seen = state.applied | set(state.blocked)
    vs.save_state(state)

    after = vs.load_state()
    print(f"\n  ✓ cleared {len(seen_only)} seen-only entries")
    print(f"  ✓ backup  : {backup.name}")
    print(f"  {after.summary()}")
    if after.applied != state.applied:
        print("  ✗ applied set changed — this should be impossible")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
