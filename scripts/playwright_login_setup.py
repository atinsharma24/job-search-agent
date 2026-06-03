#!/usr/bin/env python3
"""Open a persistent Playwright profile and wait for manual login."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Open a headed persistent Chromium session and keep it open until the user closes it."
    )
    parser.add_argument("--portal", required=True, help="Portal label used in terminal messages.")
    parser.add_argument("--login-url", required=True, help="Login URL to open.")
    parser.add_argument("--profile-dir", required=True, help="Persistent Chromium profile directory.")
    parser.add_argument("--channel", default=None, help="Optional Playwright browser channel.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    profile_dir = Path(args.profile_dir).expanduser().resolve()
    profile_dir.mkdir(parents=True, exist_ok=True)

    try:
        from playwright.sync_api import Error, sync_playwright
    except Exception as exc:
        print(f"[{args.portal}] Playwright import failed: {exc}", file=sys.stderr)
        return 1

    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=False,
            channel=args.channel,
            viewport={"width": 1440, "height": 1200},
        )
        page = context.pages[0] if context.pages else context.new_page()

        try:
            page.goto(args.login_url, wait_until="domcontentloaded", timeout=60000)
        except Error as exc:
            print(f"[{args.portal}] Could not open login URL: {exc}", file=sys.stderr)
            context.close()
            return 1

        print(f"[{args.portal}] Browser is open. Log in, then close the browser window.")
        while True:
            try:
                if not context.pages:
                    break
                time.sleep(1)
            except Error:
                break

        try:
            context.close()
        except Error:
            pass

    print(f"[{args.portal}] Session saved in {profile_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
