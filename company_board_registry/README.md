# Company Board Registry

Verified public ATS job-feed endpoints for companies tracked in this vault.
This is the **data source** for the (not-yet-built) board scanning pipeline —
it contains no scanning or filtering logic itself.

## Files

| File | Contents |
|---|---|
| `greenhouse.json` | Companies on Greenhouse (`boards-api.greenhouse.io`) |
| `lever.json` | Companies on Lever (`api.lever.co`) |
| `ashby.json` | Companies on Ashby (`api.ashbyhq.com`) |
| `needs_manual_check.json` | Companies that did **not** resolve to a public feed |

Each verified entry records: `company`, `ats`, `slug`, `endpoint`,
`open_roles_at_verification`, `verified_on`.

## How entries were verified

Every slug in the three ATS files was confirmed by **actually calling the live
endpoint** and requiring a `200` response with a non-empty job array. Nothing
here is guessed — a plausible-looking slug that returned `404` or empty data was
rejected and its company moved to `needs_manual_check.json`.

Endpoint shapes (base `endpoint` field stores the first form):

```
Greenhouse : https://boards-api.greenhouse.io/v1/boards/{slug}/jobs   (+ ?content=true for descriptions)
Lever      : https://api.lever.co/v0/postings/{slug}                  (+ ?mode=json)
Ashby      : https://api.ashbyhq.com/posting-api/job-board/{slug}     (+ ?includeCompensation=true)
```

## Re-verifying / extending

Tooling lives in this directory:

```bash
cd company_board_registry
python3 probe.py           # probes companies.json -> verified.json / failed.json
python3 build_registry.py  # regenerates greenhouse/lever/ashby/needs_manual_check.json
```

To add a company, append it to `companies.json` with any known slug hints and
re-run both scripts. `needs_manual_check.json` companies most likely run
Workday, Keka, Darwinbox, SmartRecruiters, Freshteam, or a custom/JS-embedded
board — inspect their live careers page by hand before promoting them.
