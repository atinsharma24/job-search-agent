# Autonomous Session Report — 1 August 2026

Work performed under a standing grant of autonomy: fix defects, apply to jobs, update
profiles, and polish the project. Figures below are measured, not estimated. Anything that
did not work is stated plainly.

---

## 1. What was actually accomplished

### Applications submitted

Every submission was checked against the same four criteria before being counted:
the recorded resume matches the file uploaded, expected CTC reads 18L, experience reads
1 year, and state gained exactly one entry.

| Portal | Submitted | Blocked (abstained) | Failed | Notes |
|---|--:|--:|--:|---|
| LinkedIn | see tracker | high | some | Discovery was returning *zero* jobs before today |
| Naukri | see tracker | some | some | Chatbot no longer types "10 LPA" |

Exact current figures:

```bash
grep -c "2026-08-01.*Applied (confirmed)" active_application_context/job_applications_tracker.md
python3 scripts/vault_state.py
```

### Profiles updated

- **Naukri resume** → `Atin_Sharma_Resume_2026.pdf`, replacing `2026New1.pdf`. Confirmed
  live ("Uploaded on Aug 01, 2026").
- **Naukri headline** → *"Full-Stack Developer at AGI Ready Inc. | Next.js · TypeScript ·
  Node.js · AI Systems · RAG Pipelines · LLM Agents"*, matching the resume. Confirmed live.
- Notice period (15 days) and total experience (1 year) were already correct.

### Documentation

- `docs/design/screening_question_agent.md` — full design for the autonomous
  screening-question agent, as requested.
- `docs/audit/04-live-run-findings.md` — the eight defects only a live run could reveal.
- `README.md`, `CLAUDE.md`, `AGENTS.md` — rewritten to describe the system that exists.
- `active_application_context/MANUAL_PROFILE_TODO.md` — the profile steps automation
  could not complete.

---

## 2. What did not work, and why

**Naukri applications largely do not complete.** This is the biggest functional gap left.
The chatbot flow answers questions correctly — a screenshot showed *"Are you currently
residing in Bengaluru or willing to relocate?"* with **Yes correctly selected** — but the
step does not advance, and the run dies at the step limit.

The immediate cause was that Naukri renders the chatbot's **Save** button in a side drawer
*outside* the modal the code scopes its button search to. Widening the search fixed the
stall but caused a worse failure: a "Save" outside the question flow got clicked before all
mandatory questions were answered, and Naukri responded *"Your application was not accepted
due to incomplete information."* Nothing incorrect reached an employer — Naukri rejected it
rather than submitting it — but the trade is now explicit in the code: **advancing a step is
safe to search page-wide; submitting is not.**

Submitting is scoped back to the modal, which restores the stall. Properly fixing this needs
a session of its own: the chatbot is a multi-step state machine and the current step loop
treats it as a flat form. LinkedIn is unaffected and works.

**Naukri Employment section is still empty.** This is the most consequential gap: recruiter
searches filtered by current company or designation will not surface the profile at all. The
add-employment modal dismisses itself when the suggestion dropdown is escaped, and three
attempts failed. Exact field values are in `MANUAL_PROFILE_TODO.md` — it is about two
minutes of manual entry and worth doing.

**Instahyre profile resume unchanged.** Instahyre applies with the resume attached to the
profile rather than an uploaded file, so no code path reaches it. Manual swap required.

**LinkedIn throughput is limited by list virtualisation.** Roughly 7 of 25 cards render at
any moment. Unrendered cards are now recovered from the job page rather than discarded, but
the run is slower than the card count suggests.

**The block rate is high, and that is the design working.** Questions like *"Do you have a
team of developers?"* (an agency posting), *"if you joined Viobe tomorrow, what would you
build first?"*, and *"are you willing to work 6 days a week?"* are abstained rather than
guessed. Each is logged as `blocked:unanswerable_question` for review. Answering them
wrongly is worse than not applying — and closing that gap safely is exactly what the
screening-agent design is for.

**Not independently verified:** submissions were confirmed via each portal's own success
text and the tracker, not by opening every employer's applied-list page.

---

## 3. Defects found and fixed while running

Eight, all invisible to static review. Full detail in
[`04-live-run-findings.md`](04-live-run-findings.md).

| # | Defect | Consequence if unfixed |
|---|---|---|
| 1 | LinkedIn card extraction returned blank company/title | **Zero LinkedIn applications, indefinitely** |
| 2 | Job descriptions never read (hashed CSS class names) | Good matches scored 0.20–0.40 and were skipped |
| 3 | `context.pages[0]` hijacked the user's own browser tabs | Destroyed search results mid-run; navigated user tabs away |
| 4 | A dry run recorded a real application | Jobs silently hidden from all future real runs |
| 5 | LinkedIn field mapper bypassed the screening policy | Blanket "Yes"; PowerShell answered as 1 year |
| 6 | Resume picker counted as an unanswerable field | Blocked otherwise-valid applications |
| 7 | WAF detection matched job description text | Aborted an entire run on a healthy portal |
| 8 | `close_redundant_tabs` closed the user's tabs | Data loss in the user's own browser |

Two of these (7, 8) were caught by verifying rather than trusting — #7 by re-fetching the
"blocked" page and finding a normal job listing, #8 by reading the function before letting
it run again.

---

## 4. Judgement calls made

| Decision | Reasoning |
|---|---|
| Ran sequentially, not with parallel subagents | All four scripts attach to one Chrome over CDP and share a browser context; parallel agents would fight over tabs. |
| Did not change Naukri profile location (Bengaluru → Agra) | May be deliberate for recruiter reach. Flagged for a human rather than silently overwritten. |
| Answered "Are you an immediate joiner?" as **No** | Canonical notice is 15 days. Costs some applications; the alternative is a false claim. |
| Kept abstaining on capability self-assessments | Scoped out of the "safe factual" set by instruction. |
| Did not retry LinkedIn after the WAF verdict until verifying it | The verdict was wrong; retrying blindly would have been the wrong lesson either way. |

---

## 4b. Questions I deliberately did not decide for you

Each of these appeared on a live form and is currently abstained. Each needs one decision
from you, after which it becomes a one-line rule.

| Question seen | Why I did not answer it |
|---|---|
| *"Mention your CTC"* (no "current"/"expected" qualifier) | Genuinely ambiguous. Answering 11.2 when they meant *expected* would quote below your 18L floor and cap the offer; answering 18 when they meant *current* overstates your salary. Compensation is exactly where a wrong guess is expensive and hard to walk back. **Tell me which reading to use and it becomes one rule.** |
| *"Are you willing to work 6 days a week, remotely, and across time zones?"* | A working-conditions commitment. Yours to make. |
| *"Can you convert a business requirement into an AI architecture, define evaluation metrics and deliver?"* | Capability self-assessment — you scoped these out of the safe-factual set. |
| *"If you joined tomorrow, what would you build first at &lt;company&gt;—and why?"* | Company-specific judgement. This is the screening-agent's job. |
| *"Are you currently residing in Bengaluru or willing to relocate to Bengaluru?"* | Answered **Yes** (relocation is in your work_preference) — flagged only because your Naukri profile says Bengaluru while the vault says Agra. Worth making those agree. |

---

## 5. What to do next

**Immediate (yours, ~5 minutes)**
1. Add the Naukri employment entry — `MANUAL_PROFILE_TODO.md` has the exact values.
2. Swap the Instahyre profile resume.
3. Spot-check two or three submitted applications on the portal's own "applied" page.

**Still outstanding from the audit**
- Session rotation for the cookies in public git history (deferred by your decision — the
  only fix is logging out of all sessions on LinkedIn, Naukri and Wellfound).
- Wire `board_scan_feeder.py` + `company_board_registry/` for API-based discovery. This is
  the highest-value remaining item: 204 verified ATS endpoints, no bot detection, no CAPTCHA.
- Tracker migration to JSONL — still 3 interleaved schemas.
- Build the screening-question agent to recover the abstained applications.

**Operating the pipeline**

```bash
bash scripts/run_chrome_background.sh
python3 scripts/preflight_check.py           # 14 checks, must exit 0
bash scripts/run_apply_all.sh --dry-run      # after ANY change to the apply path
bash scripts/run_apply_all.sh --max-apply 10
```

The single most important lesson from today: **five P0 defects were invisible to code review
and obvious within minutes of a real run.** The dry run is not a formality.
