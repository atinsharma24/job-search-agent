# Browser Automation — What To Use

**Question asked:** is
`/Applications/Google\ Chrome.app/.../Google\ Chrome --remote-debugging-port=9222 --user-data-dir="$HOME/ChromeDebugProfile"`
a good approach, or should this use Claude-in-Chrome, or something else?

**Answer: keep CDP. It is the right choice. Harden two things.** But the browser layer is not
what is limiting results — see [§5](#5-the-thing-that-actually-matters).

---

## 1. The current setup, assessed

`scripts/run_chrome_background.sh:91-98` launches:

```bash
nohup "$CHROME_BIN" \
    --remote-debugging-port=9222 \
    --user-data-dir="$HOME/ChromeDebugProfile" \
    --headless=new \
    --disable-gpu --no-first-run --no-default-browser-check &
```

and the four portal scripts attach with `pw.chromium.connect_over_cdp(url, no_defaults=True)`.

**This is a good design, for four concrete reasons:**

| Property | Why it matters here |
|---|---|
| Real Chrome binary | Not Playwright's bundled Chromium. Materially better TLS/JA3 and navigator fingerprint — LinkedIn and Naukri both fingerprint aggressively. |
| `--headless=new` | No window is created, so macOS never activates the app. This is what actually solved the focus-stealing problem, and it does so correctly. |
| Persistent `--user-data-dir` | Log in once. Sessions survive across runs and reboots. |
| Deterministic + free | Selector-driven, ~2 s/step, zero marginal token cost. For 15 applications × 4 portals, nothing else is close. |

**Keep it.** The two fixes below are hardening, not redesign.

### Fix 1 — treat port 9222 as a credential

The CDP port is unauthenticated. Any local process that can reach `127.0.0.1:9222` gets full
control of the browser and read access to every logged-in session — LinkedIn, Naukri,
Cutshort, Instahyre, and anything else in that profile. It is functionally a password with no
password.

```bash
--remote-debugging-address=127.0.0.1   # be explicit; never bind 0.0.0.0
```

And stop the daemon when not applying:

```bash
bash scripts/run_chrome_background.sh --stop
```

`run_apply_all.sh` should stop the browser on exit if it started it.

### Fix 2 — stop addressing tabs by position

```python
# playwright_linkedin_discover_apply.py:407-408, naukri:1082-1083
search_page = context.pages[0] if context.pages else context.new_page()
apply_page  = context.pages[1] if len(context.pages) > 1 else context.new_page()
```

Positional indexing assumes tab order and no foreign tabs. `close_redundant_tabs()` mutates
that list mid-run. If anything else is open in the profile, `search_page` becomes *that* tab
and the script navigates it away.

Worse, `playwright_naukri_discover_apply.py:1103`:

```python
close_redundant_tabs(context, keep_domains=())     # empty tuple
```

With an empty `keep_domains`, the `is_naukri` guard is always `False` — **this closes every
non-blank tab in the browser.** Track pages by explicit handle instead.

---

## 2. Alternative considered — `launch_persistent_context(channel="chrome")`

Playwright owns the browser directly; no debugging port, no daemon script.

```python
ctx = pw.chromium.launch_persistent_context(
    user_data_dir=PROFILE, channel="chrome", headless=True,
)
```

**Genuinely better on three axes:** no open CDP port (Fix 1 becomes moot), no orphaned Chrome
processes or `pgrep`/`pkill` lifecycle management, and no tab-index ambiguity because you own
every page you create. It deletes `run_chrome_background.sh` entirely. Pipeline A already uses
this pattern, and `playwright_login_setup.py` is the cleanest browser code in the repo.

**Cost:** you lose the ability to attach a second tool to a live browser and watch it work,
which is genuinely useful while debugging a portal.

**Recommendation: stay on CDP for now.** It works, the team knows it, and migrating during a
correctness push adds risk for a modest structural gain. Revisit once P0 is closed.

---

## 3. Claude in Chrome

**No for the bulk loop. Yes as a narrow, supervised fallback.**

Against it as the primary path:

- **Cannot run unattended.** It drives the user's visible Chrome and needs an interactive
  session — the exact opposite of the background execution `--headless=new` was adopted for.
- **Cost scales per step.** Each interaction is an LLM call. 60 applications × ~15 steps is
  ~900 model round-trips per run.
- **Non-determinism on an irreversible action.** Submitting a job application cannot be undone.
  A selector-driven script fails predictably and loudly; a reasoning agent occasionally
  succeeds at the wrong thing. Given the vault's history of blind "Yes" answers, adding
  *more* judgement to the submit path is the wrong direction until the deterministic path is
  trustworthy.

For it, in one specific slot: novel ATS layouts (Workday, Greenhouse custom forms, one-off
portals) where selectors don't generalise and writing a bespoke filler isn't worth it. As a
**tier-2 escalation with a human watching**, it is the right tool.

> Note: the existing "claude fallback" in `browseros_apply_macro.sh` is broken independently
> of any of this. It tells Claude to read three files that don't exist, then instructs it to
> stop if data is missing — so it always stops. See [findings D1](01-findings.md#d1--pipeline-a-is-documented-but-broken-at-four-points--p1).

---

## 4. The higher-leverage change: don't use a browser for discovery

Discovery and submission are different problems and deserve different tools.

**Discovery does not need a browser at all.** `company_board_registry/` already contains **204
verified** Greenhouse / Lever / Ashby JSON feed endpoints, built with real methodology —
live-200 checks plus non-empty-array validation, no guessed slugs. And
`scripts/board_scan_feeder.py` already consumes them: per-host `CRAWL_DELAY`, a real
`--dry-run`, first-run seeding, its own state file. It is the best-engineered script in the
repository and it is **completely unwired.**

| | Browser scraping | Public ATS JSON |
|---|---|---|
| Bot detection | Constant | None |
| CAPTCHA | Yes | None |
| Session expiry | Yes | N/A |
| Cost per poll | ~30 s + a browser | ~200 ms |
| Breaks when | Any DOM change | Documented API change |

**Recommendation: APIs for discovery, browser only for submission.** This also removes most of
the CAPTCHA surface, since the browser stops crawling search-results pages and only opens a
page when there is a specific job to apply to.

---

## 5. The thing that actually matters

No browser technology choice moves these numbers:

```
65 confirmed applications · 554 failures
424 applications naming a resume with 0 extractable characters
503 of 855 tracker rows are duplicates
Naukri typed "10 LPA" into salary fields
Every form declared 0 years of experience
```

Roughly half the submissions were unreadable to any ATS that parses PDFs, and effectively all
of them understated experience and compensation. The browser did its job — it faithfully
delivered wrong data to hundreds of employers.

**Order of work:** correctness → observability → discovery via APIs → throughput. Browser
technology is not on the list, because the current one is already adequate.

---

## Summary

| Option | Verdict |
|---|---|
| **CDP + `--headless=new` + persistent profile** | ✅ **Keep.** Apply Fix 1 (bind + stop daemon) and Fix 2 (tab handles). |
| `launch_persistent_context(channel="chrome")` | Structurally cleaner; revisit after P0. Not worth the migration risk now. |
| **Claude in Chrome** | ❌ For volume. ✅ As a supervised tier-2 for novel ATS forms. |
| Bundled Chromium (no `channel`) | ❌ Worse fingerprint for no benefit. |
| **Public ATS JSON for discovery** | ✅ **Adopt.** Already built, already verified, unwired. |
