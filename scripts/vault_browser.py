#!/usr/bin/env python3
"""
Browser safety: security-challenge detection, guarded navigation, polite pacing.

Pipeline B had none of this. A LinkedIn checkpoint was recorded as a generic
`error:1` and the loop carried on hammering the same portal — which is precisely
how an account gets flagged. Pipeline A *did* have detection
(`playwright_linkedin_easy_apply.py:50`, `linkedin_outreach_batch5.py:159`); this
module consolidates both implementations so the live pipeline finally has it.

Contract on detection: screenshot, raise SecurityChallenge, let the portal script
exit 10, and let run_apply_all.sh abort the WHOLE run. A challenge on one portal
means the IP or profile is flagged — continuing makes it worse, and any further
applications are likely to fail anyway.

    from vault_browser import guarded_goto, detect_security_challenge, polite_sleep
"""

from __future__ import annotations

import random
import re
import time
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = VAULT_ROOT / "output" / "playwright"

# Reuses the codes already documented in INVOKE.md so the contract is unchanged.
EXIT_SUCCESS = 0
EXIT_GENERIC = 1
EXIT_CAPTCHA = 10
EXIT_EXTERNAL = 11
EXIT_LOGIN = 12
EXIT_CONFIG = 13


class SecurityChallenge(RuntimeError):
    """A CAPTCHA, WAF interstitial or login wall. Abort the run — do not retry."""

    def __init__(self, kind: str, url: str = "", detail: str = ""):
        self.kind = kind
        self.url = url
        super().__init__(f"{kind} at {url}: {detail}" if detail else f"{kind} at {url}")

    @property
    def exit_code(self) -> int:
        return EXIT_LOGIN if self.kind == "login" else EXIT_CAPTCHA


# URL fragments that are challenges regardless of page content.
_CHALLENGE_URL = re.compile(r"/checkpoint|/challenge|captcha|/authwall", re.I)

# Auth redirects. Checked before the content markers, because a page mid-redirect
# can render arbitrary transient content — an in-flight OAuth handshake was once
# classified as a WAF block purely on body text.
_LOGIN_URL = re.compile(
    r"/authwall|/uas/login|/login(?:[/?]|$)|/signin(?:[/?]|$)|/nlogin|"
    r"/accounts/login|/auth/login|[?&]next=/",
    re.I,
)

# Body/title markers. Grouped by vendor so failures are attributable.
_MARKERS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("captcha", (
        "captcha", "verify you're a human", "verify you are human",
        "security verification", "quick security check", "security check",
        "suspicious activity", "unusual activity", "prove you're not a robot",
        "i'm not a robot",
    )),
    ("waf", (
        "just a moment", "attention required", "access denied",
        "checking your browser", "cf-chl", "cloudflare", "reference #",
        "request unsuccessful", "incapsula", "akamai",
        "you have been blocked", "rate limit", "too many requests",
    )),
    # Only unambiguous phrases. Weaker ones like "sign in to continue" or
    # "join linkedin" appear on plenty of *authenticated* pages (invite modules,
    # footers), and a false login verdict aborts the whole run with exit 12.
    # Anything softer must be corroborated by a password field — see below.
    ("login", (
        "session expired", "you've been signed out", "you have been signed out",
        "your session has ended", "please log in again",
    )),
)

# Soft login hints: only believed when a password field is also present.
_SOFT_LOGIN = ("sign in to continue", "please sign in", "log in to continue")


def _safe(fn, default=""):
    try:
        return fn() or default
    except Exception:
        return default


def detect_security_challenge(page) -> str | None:
    """Return 'captcha' | 'waf' | 'login' | None. Never raises."""
    url = _safe(lambda: page.url).casefold()
    # Auth redirects first: a session problem, not a bot problem, and the two
    # need different remedies (re-login vs back off).
    if _LOGIN_URL.search(url):
        return "login"
    if _CHALLENGE_URL.search(url):
        return "captcha"

    title = _safe(lambda: page.title()).casefold()
    body = _safe(lambda: page.locator("body").inner_text(timeout=3000)).casefold()
    blob = f"{title}\n{body[:6000]}"

    for kind, markers in _MARKERS:
        for marker in markers:
            if marker in blob:
                # "captcha" appears in ordinary LinkedIn profile pages; require
                # that we are not on a normal content route before believing it.
                if kind == "captcha" and marker == "captcha" and "/in/" in url:
                    continue
                return kind

    # Soft login phrases count only when a password field corroborates them, and a
    # password field alone counts only when the page has no real content. A logged-in
    # LinkedIn feed contains plenty of sign-in prose in modules and footers.
    try:
        has_password = page.locator("input[type='password']").count() > 0
    except Exception:
        has_password = False
    if has_password:
        if any(hint in blob for hint in _SOFT_LOGIN):
            return "login"
        try:
            if page.locator("main, [role='main']").count() == 0:
                return "login"
        except Exception:
            pass
    return None


def assert_no_challenge(page, *, label: str = "") -> None:
    """Raise SecurityChallenge if the current page is a challenge."""
    kind = detect_security_challenge(page)
    if not kind:
        return
    url = _safe(lambda: page.url)
    try:
        ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = re.sub(r"[^a-z0-9]+", "-", (label or kind).casefold())[:40]
        page.screenshot(path=str(ARTIFACT_DIR / f"challenge_{kind}_{stamp}.png"))
    except Exception:
        pass
    raise SecurityChallenge(kind, url, label)


def guarded_goto(page, url: str, *, timeout: int = 30000, retries: int = 2,
                 backoff: tuple[float, ...] = (2.0, 6.0), label: str = "") -> None:
    """Navigate, retrying transient timeouts but never a security challenge."""
    last: Exception | None = None
    for attempt in range(retries + 1):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            page.wait_for_timeout(800)
            assert_no_challenge(page, label=label or url)
            return
        except SecurityChallenge:
            raise  # never retried — retrying a challenge deepens the flag
        except Exception as exc:
            last = exc
            if attempt < retries:
                delay = backoff[min(attempt, len(backoff) - 1)]
                time.sleep(delay + random.uniform(0, 0.6))
    raise last if last else RuntimeError(f"navigation failed: {url}")


_counter = {"n": 0}


def polite_sleep(base: float = 2.0, jitter: float = 0.6, every_n: int | None = 10,
                 long_pause: tuple[float, float] = (8.0, 15.0)) -> None:
    """Jittered pacing. A flat sleep(2) is itself a bot signal."""
    _counter["n"] += 1
    if every_n and _counter["n"] % every_n == 0:
        time.sleep(random.uniform(*long_pause))
    else:
        time.sleep(max(0.0, base + random.uniform(-jitter, jitter)))


def connect_cdp(pw, cdp_url: str = "http://localhost:9222"):
    """Attach to the running Chrome. Returns (browser, context)."""
    browser = pw.chromium.connect_over_cdp(cdp_url)
    context = browser.contexts[0] if browser.contexts else browser.new_context()
    return browser, context


def named_page(context, key: str, registry: dict):
    """Get or create a page tracked by name.

    Replaces `context.pages[0]` / `[1]`, which assume tab order and break when any
    other tab is open — and which `close_redundant_tabs()` mutates mid-run.
    """
    page = registry.get(key)
    if page is not None:
        try:
            if not page.is_closed():
                return page
        except Exception:
            pass
    page = context.new_page()
    registry[key] = page
    return page


if __name__ == "__main__":
    class _FakePage:
        def __init__(self, url, title="", body=""):
            self._u, self._t, self._b = url, title, body
        @property
        def url(self): return self._u
        def title(self): return self._t
        def locator(self, *_a, **_k):
            body, outer = self._b, self
            class L:
                def inner_text(self, **_): return body
                def count(self): return 0
            return L()

    cases = [
        ("https://www.linkedin.com/checkpoint/challenge", "", "", "captcha"),
        ("https://www.linkedin.com/authwall", "", "", "login"),
        ("https://naukri.com/jobs", "Just a moment...", "", "waf"),
        ("https://naukri.com/jobs", "", "verify you're a human", "captcha"),
        ("https://cutshort.io/x", "", "Access Denied  reference #123", "waf"),
        ("https://www.linkedin.com/in/someone", "", "captcha help article", None),
        ("https://www.linkedin.com/jobs/view/1", "Software Engineer", "Apply now", None),
        ("https://x.com/y", "", "Session expired, please sign in", "login"),
    ]
    bad = 0
    for url, title, body, want in cases:
        got = detect_security_challenge(_FakePage(url, title, body))
        ok = got == want
        bad += not ok
        print(f"  {'✓' if ok else '✗'} {url[:44]:<46} {str(got):<8} (want {want})")
    raise SystemExit(1 if bad else 0)
