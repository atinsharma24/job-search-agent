#!/usr/bin/env python3
"""Open a persistent browser profile and wait for manual login."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Open a headed persistent browser session and keep it open until the user closes it."
    )
    parser.add_argument("--portal", required=True, help="Portal label used in terminal messages.")
    parser.add_argument("--login-url", required=True, help="Login URL to open.")
    parser.add_argument("--profile-dir", required=True, help="Persistent Chromium profile directory.")
    parser.add_argument(
        "--channel",
        default=None,
        help="Optional Playwright browser channel. Defaults to PLAYWRIGHT_LOGIN_CHANNEL or chrome.",
    )
    return parser.parse_args()


def chrome_executable() -> Path | None:
    candidates = [
        Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        Path.home() / "Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    return next((path for path in candidates if path.exists()), None)


def open_native_chrome(portal: str, login_url: str, profile_dir: Path, chrome_path: Path) -> int:
    command = [
        str(chrome_path),
        f"--user-data-dir={profile_dir}",
        "--remote-debugging-port=0",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-background-networking",
        "--new-window",
        login_url,
    ]
    print(f"[{portal}] Browser is open in Google Chrome. Log in, then close the browser window.")
    process = subprocess.Popen(command)
    return wait_for_native_chrome_close(process, profile_dir)


def read_devtools_port(profile_dir: Path) -> str | None:
    port_file = profile_dir / "DevToolsActivePort"
    for _ in range(30):
        if port_file.exists():
            lines = port_file.read_text(encoding="utf-8").splitlines()
            if lines:
                return lines[0].strip()
        time.sleep(0.5)
    return None


def chrome_page_count(port: str) -> int | None:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=1) as response:
            targets = json.loads(response.read().decode("utf-8"))
    except Exception:
        return None
    return sum(1 for target in targets if target.get("type") == "page")


def wait_for_native_chrome_close(process: subprocess.Popen, profile_dir: Path) -> int:
    port = read_devtools_port(profile_dir)
    if not port:
        return process.wait()

    saw_page = False
    while process.poll() is None:
        page_count = chrome_page_count(port)
        if page_count is None:
            time.sleep(1)
            continue
        saw_page = saw_page or page_count > 0
        if saw_page and page_count == 0:
            process.terminate()
            try:
                return process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                return process.wait()
        time.sleep(1)

    return process.returncode


def launch_context(playwright, profile_dir: Path, channel: str | None, explicit_channel: bool):
    launch_options = {
        "user_data_dir": str(profile_dir),
        "headless": False,
        "channel": channel,
        "viewport": {"width": 1440, "height": 1200},
        "args": [
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
        ],
        "ignore_default_args": ["--enable-automation"],
    }

    try:
        return playwright.chromium.launch_persistent_context(**launch_options), channel
    except Exception:
        if explicit_channel or not channel:
            raise

    launch_options["channel"] = None
    return playwright.chromium.launch_persistent_context(**launch_options), None


def main() -> int:
    args = parse_args()
    profile_dir = Path(args.profile_dir).expanduser().resolve()
    profile_dir.mkdir(parents=True, exist_ok=True)
    explicit_channel = args.channel is not None or "PLAYWRIGHT_LOGIN_CHANNEL" in os.environ
    browser_channel = args.channel or os.environ.get("PLAYWRIGHT_LOGIN_CHANNEL") or "chrome"
    native_chrome = chrome_executable()

    if native_chrome and not explicit_channel:
        exit_code = open_native_chrome(args.portal, args.login_url, profile_dir, native_chrome)
        if exit_code == 0:
            print(f"[{args.portal}] Session saved in {profile_dir}")
            return 0
        print(f"[{args.portal}] Google Chrome exited with code {exit_code}", file=sys.stderr)
        return exit_code

    try:
        from playwright.sync_api import Error, sync_playwright
    except Exception as exc:
        print(f"[{args.portal}] Playwright import failed: {exc}", file=sys.stderr)
        return 1

    with sync_playwright() as playwright:
        context, active_channel = launch_context(playwright, profile_dir, browser_channel, explicit_channel)
        page = context.pages[0] if context.pages else context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        try:
            page.goto(args.login_url, wait_until="domcontentloaded", timeout=60000)
        except Error as exc:
            print(f"[{args.portal}] Could not open login URL: {exc}", file=sys.stderr)
            context.close()
            return 1

        browser_name = active_channel or "bundled chromium"
        print(f"[{args.portal}] Browser is open in {browser_name}. Log in, then close the browser window.")
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
