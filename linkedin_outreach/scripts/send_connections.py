"""
send_connections.py

Reads queue/approved.json and sends LinkedIn connection requests
using the persistent playwright session from active_application_context/playwright/linkedin-profile.

Safety rules enforced:
- Hard daily cap: 15 sends per run
- Randomised delay: 45-90s between sends
- Halts on CAPTCHA / security challenge
- Requires Y confirmation per send
- Logs all sends to logs/outreach.log, errors to logs/errors.log
- Moves sent entries to queue/sent.json, marks failed with status=failed
"""

import json
import time
import random
import sys
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

ROOT = Path(__file__).parent.parent
APPROVED_JSON = ROOT / "queue" / "approved.json"
SENT_JSON = ROOT / "queue" / "sent.json"
OUTREACH_LOG = ROOT / "logs" / "outreach.log"
ERRORS_LOG = ROOT / "logs" / "errors.log"
SESSION_DIR = Path("/Users/atinsharma/job_search_vault/active_application_context/playwright/linkedin-profile")

DAILY_CAP = 15
DELAY_MIN = 45
DELAY_MAX = 90


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def log_outreach(line: str):
    with open(OUTREACH_LOG, "a") as f:
        f.write(f"[{now_iso()}] {line}\n")
    print(line)


def log_error(line: str):
    with open(ERRORS_LOG, "a") as f:
        f.write(f"[{now_iso()}] {line}\n")
    print(f"[ERROR] {line}", file=sys.stderr)


def load_json(path: Path):
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def save_json(path: Path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def check_security_challenge(page) -> bool:
    body = page.content().lower()
    indicators = ["security verification", "captcha", "unusual activity",
                  "checkpoint", "verify you're a human", "suspicious"]
    return any(i in body for i in indicators)


def send_connection(page, entry: dict) -> bool:
    """Navigate to profile and send connection request with note. Returns True on success."""
    url = entry["url"]
    name = entry["name"]
    message = entry["message"]

    print(f"\n{'='*60}")
    print(f"Target  : {name} @ {entry['company']}")
    print(f"URL     : {url}")
    print(f"Message : {message}")
    print(f"Chars   : {len(message)}")
    print(f"{'='*60}")

    confirm = input("Send this connection request? [Y/n]: ").strip().lower()
    if confirm not in ("y", ""):
        log_outreach(f"SKIPPED | {name} | {entry['company']} | user skipped")
        entry["status"] = "skipped"
        return False

    try:
        page.goto(url, timeout=30000, wait_until="domcontentloaded")
        time.sleep(3)

        if check_security_challenge(page):
            log_error(f"HUMAN_INTERVENTION_REQUIRED | security challenge on {url}")
            print("\n[HALT] LinkedIn security challenge detected. Stopping. Please resolve manually.")
            sys.exit(1)

        # Find and click Connect button (top-level on profile)
        connect_btn = None
        for selector in [
            "button:has-text('Connect')",
            "//button[normalize-space()='Connect']",
        ]:
            try:
                btn = page.locator(selector).first
                if btn.is_visible(timeout=3000):
                    connect_btn = btn
                    break
            except Exception:
                pass

        if not connect_btn:
            # Try More button → Connect in dropdown
            try:
                more_btn = page.locator("button:has-text('More')").first
                if more_btn.is_visible(timeout=3000):
                    more_btn.click()
                    time.sleep(1)
                    dropdown_connect = page.locator("//span[normalize-space()='Connect']").first
                    if dropdown_connect.is_visible(timeout=3000):
                        connect_btn = dropdown_connect
            except Exception:
                pass

        if not connect_btn:
            log_error(f"BUTTON_NOT_FOUND | {name} | {url} | no Connect button found")
            entry["status"] = "failed"
            entry["error"] = "Connect button not found"
            return False

        connect_btn.click()
        time.sleep(2)

        # Click "Add a note"
        try:
            add_note = page.locator("button:has-text('Add a note')").first
            if add_note.is_visible(timeout=5000):
                add_note.click()
                time.sleep(1)
            else:
                log_error(f"ADD_NOTE_NOT_FOUND | {name} | modal may have closed")
                entry["status"] = "failed"
                entry["error"] = "Add a note button not found"
                return False
        except PlaywrightTimeout:
            log_error(f"ADD_NOTE_NOT_FOUND | {name} | timeout waiting for add note button")
            entry["status"] = "failed"
            entry["error"] = "Add a note button timeout"
            return False

        # Type the message
        try:
            textarea = page.locator("textarea#custom-message").first
            if not textarea.is_visible(timeout=5000):
                textarea = page.locator("textarea[name='message']").first
            if not textarea.is_visible(timeout=3000):
                log_error(f"TEXTAREA_NOT_FOUND | {name}")
                entry["status"] = "failed"
                entry["error"] = "Message textarea not found"
                return False
            textarea.fill(message)
            time.sleep(1)
        except Exception as e:
            log_error(f"TEXTAREA_ERROR | {name} | {e}")
            entry["status"] = "failed"
            entry["error"] = str(e)
            return False

        # Click Send
        try:
            send_btn = page.locator("button:has-text('Send')").first
            if not send_btn.is_visible(timeout=5000):
                log_error(f"SEND_BUTTON_NOT_FOUND | {name}")
                entry["status"] = "failed"
                entry["error"] = "Send button not found"
                return False
            send_btn.click()
            time.sleep(2)
        except Exception as e:
            log_error(f"SEND_ERROR | {name} | {e}")
            entry["status"] = "failed"
            entry["error"] = str(e)
            return False

        entry["status"] = "sent"
        entry["sent_at"] = now_iso()
        log_outreach(f"SENT | {name} | {entry['company']} | {url}")
        print(f"  ✓ Sent to {name}")
        return True

    except Exception as e:
        log_error(f"SEND_ERROR | {name} | {entry['company']} | {e}")
        entry["status"] = "failed"
        entry["error"] = str(e)
        return False


def main():
    approved = load_json(APPROVED_JSON)
    pending_send = [e for e in approved if e.get("status") == "approved"]

    if not pending_send:
        print("No approved entries to send. Run prepare + approve first.")
        sys.exit(0)

    print(f"\nLinkedIn Connection Sender")
    print(f"  Approved queue : {len(pending_send)}")
    print(f"  Daily cap      : {DAILY_CAP}")
    print(f"  Delay          : {DELAY_MIN}–{DELAY_MAX}s between sends")
    print(f"  Session        : {SESSION_DIR}")

    if not SESSION_DIR.exists():
        print(f"\n[ERROR] LinkedIn session not found at {SESSION_DIR}")
        print("Run: python3 scripts/playwright_login_setup.py to create it.")
        sys.exit(1)

    sent = load_json(SENT_JSON)
    sent_count = 0

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            str(SESSION_DIR),
            headless=False,
            args=["--no-sandbox"],
        )
        page = browser.new_page()

        # Verify we're logged in
        page.goto("https://www.linkedin.com/feed/", timeout=30000, wait_until="domcontentloaded")
        time.sleep(3)

        if "login" in page.url or "authwall" in page.url:
            print("\n[ERROR] LinkedIn session expired. Please log in manually first.")
            print(f"Run: python3 scripts/playwright_login_setup.py")
            browser.close()
            sys.exit(1)

        print(f"\n  Logged in. Starting sends...\n")

        for entry in pending_send:
            if sent_count >= DAILY_CAP:
                print(f"\n[HALT] Daily cap of {DAILY_CAP} reached. Re-run tomorrow.")
                log_outreach(f"DAILY_CAP_REACHED | {sent_count} sent this session")
                break

            success = send_connection(page, entry)

            if entry["status"] == "sent":
                sent.append(entry)
                sent_count += 1
            elif entry["status"] == "failed":
                pass  # stays in approved.json for retry

            # Persist state after every send attempt
            save_json(SENT_JSON, sent)
            save_json(APPROVED_JSON, approved)

            if success and sent_count < DAILY_CAP and pending_send.index(entry) < len(pending_send) - 1:
                delay = random.randint(DELAY_MIN, DELAY_MAX)
                print(f"  Waiting {delay}s before next send...")
                time.sleep(delay)

        browser.close()

    print(f"\nDone. Sent {sent_count} connection requests this session.")
    log_outreach(f"SESSION_END | {sent_count} sent")


if __name__ == "__main__":
    main()
