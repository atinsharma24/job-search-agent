# Live-Run Findings — 1 August 2026

Defects found by **actually running the pipeline**, after the static audit
([`01-findings.md`](01-findings.md)) was complete and its P0 fixes had landed.

The static audit found what the code *said*. These are what it *did*. Every one of them
was invisible to review and obvious within minutes of a real run — which is the argument
for the pre-flight gate and for never skipping the dry run again.

---

## L1 · LinkedIn was applying to nothing — **P0**

The first live attempt produced **zero** applications across 12 search URLs. Every job
logged `SKIP (seen)` with a blank company and title.

Card selectors matched 7–9 of 25 results and none carried usable attributes, so
`make_job_id("", "")` collapsed every job to a single id. Once that id was recorded as
seen, every subsequent job on every subsequent run skipped as a duplicate.

Probing the live DOM gave the real structure:

| What | Where |
|---|---|
| Card container | `[data-occludable-job-id]` — 25 present vs 7 for the old selector |
| Job ID | the `data-occludable-job-id` attribute |
| Title | the `/jobs/view/` anchor's `aria-label` |
| Company | `.artdeco-entity-lockup__subtitle` |
| Easy Apply | `"Easy Apply"` in the card's text |

**Now 25/25 cards resolve to unique ids.**

## L2 · Job descriptions were never read — **P0**

Every description selector returned zero elements, so scoring ran on the title alone.
That is why genuine matches scored 0.20–0.40 against a 0.45 threshold and were skipped as
irrelevant.

Cause: **LinkedIn now ships hashed CSS class names** (`_1e5f23a7`, `d4848df5`), so any
class-based selector is one deploy away from breaking. Replaced with structural anchors —
`[id^="JobDetails_AboutTheJob"]`, falling back to `main`.

A real match now scores **0.97–1.00**.

## L3 · Scripts hijacked whatever browser tabs existed — **P0**

```python
search_page = context.pages[0] if context.pages else context.new_page()
apply_page  = context.pages[1] if len(context.pages) > 1 else context.new_page()
```

This is the positional-tab defect flagged in
[`02-browser-automation.md`](02-browser-automation.md), caught here doing real damage: it
navigated the user's own tabs away, and let the apply flow destroy the search results
mid-run — which is why cards stopped resolving after the first few applications.

All four portal scripts now own their tabs via `vault_browser.named_page()` and close only
what they created.

## L4 · A dry run recorded a real application — **P0**

`execute_easy_apply()` returns `EXIT_SUCCESS` for a completed dry run — it returns *before*
clicking submit. `apply_easy_apply()` mapped exit 0 to `"submitted"` unconditionally.

One dry run therefore wrote a false `Applied (confirmed) ✅` row for Talentgigs and marked
the job applied in state, which would have hidden it from every future real run.

Verified nothing was actually submitted (the dry-run artifact was from that minute; the
last real-submit artifact was 12 July), then reverted both the tracker row and the state
entry. Guarded by the `dry_run_isolation` pre-flight check.

## L5 · The LinkedIn field mapper bypassed the screening policy — **P0**

A screenshot of a live HARP form showed the compensation and experience fixes working —
Expected CTC **18**, JavaScript **1**, Node.js **1** — alongside one wrong answer:

> *"How many years of experience do you have using PowerShell for Microsoft 365 administration and automation?"* → **1**

PowerShell is not in the stack. `vault_answers` correctly returns 0; it was never consulted,
because `answer_mapper` ran `LINKEDIN_MAPPING` first and its blanket `\bexperience\b` rule
mapped any label containing "experience" to total years. Everything that fell through then
hit:

```python
is_yes_no = (... or "?" in label_lower or "experience" in label_lower ...)
if is_yes_no:
    if sponsorship/visa/felony: return "No"
    return "Yes"          # ← blanket Yes for every question on the form
```

The same blind-affirmation defect already fixed on Naukri, in a second location.

`LINKEDIN_MAPPING` also carried qa_bank entries matching bare topic words, so
`\bleadership\b` answered *"Rate your leadership 1-10"* with a 500-word essay.

## L6 · The resume picker blocked valid applications — P1

Easy Apply's resume chooser is a radio list of previously uploaded files. `answer_mapper`
counted it as an unanswerable field, so the new early-bail treated it as a blocking
required question and aborted otherwise-fine applications. File pickers are now recognised
as widgets and ignored.

Worth noting what that list contained: **many stale `2026New1.pdf` copies and one
`staged_application_resume.pdf`** — the artifact that leaked the private 15L floor.

## L7 · List virtualisation was discarding 18 of every 25 results — P1

Only ~7 cards carry metadata at any moment. Unrendered cards were skipped outright.

They still expose their job id, and the loop already navigates to the job page for the
description — so title and company are now recovered there, deduped, and scored normally,
at no extra page load.

---

## Screening policy, observed on real forms

The policy held up. Correctly **answered**:

- *"How many years with Node.js / JavaScript?"* → 1
- *"Years using PowerShell for M365?"* → 0
- *"Mention your Expected CTC"* → 18
- *"Have you worked with LangChain, LlamaIndex, CrewAI?"* → Yes (LangChain is in the stack)
- *"Are you an immediate joiner?"* → No (canonical notice is 15 days)
- *"Are you currently working in a remote setting?"* → Yes

Correctly **abstained**, each surfaced as `blocked:unanswerable_question` rather than guessed:

| Question | Why abstaining is right |
|---|---|
| *"Do you have team of Developers (Backend, Frontend, AI, DevOps, Testers)?"* | An agency/outsourcing posting. "Yes" would be a lie. |
| *"After reading about Viobe, if you joined tomorrow, what would you build first—and why?"* | Company-specific judgement no rule table can hold. |
| *"Are you willing to work 6 days a week, remotely, and across time zones?"* | A working-conditions commitment that is the candidate's to make. |

That last category is exactly what the
[screening-question agent design](../design/screening_question_agent.md) exists to handle —
and exactly why its `commitment` risk class is routed to a human, never auto-answered.

---

## What this changes about the process

1. **Never skip the dry run.** Five P0 defects were invisible to static review and obvious
   within minutes of running. The pipeline had been "working" for months while applying to
   nothing on LinkedIn.
2. **Portal DOMs are hostile to class selectors.** LinkedIn's move to hashed class names
   means anything class-based is temporary. Prefer `id^=`, `data-*`, ARIA, and structure.
3. **Screenshot real forms.** The PowerShell defect was found by looking at a rendered form,
   not by reading code. The values were all individually plausible.
4. **Every fix needs a pre-flight check.** Each defect above now has a regression guard, so
   the next refactor cannot silently reintroduce it.
