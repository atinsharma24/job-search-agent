# BEHAVIORAL CONTEXT VAULT — STAR STORIES
### Atin Sharma | Founding Engineer, OpenBiz Software India Pvt Ltd
> Usage: Select the story matching the interviewer's behavioral prompt.  
> All stories are grounded in verifiable experience. Do not embellish metrics.

---

## STORY 1 — DEALING WITH A DIFFICULT TEAMMATE

**Prompt types:** "Tell me about a time you had conflict with a colleague." / "How do you handle disagreement on a team?"

---

### STAR

**Situation:**  
At OpenBiz, as one of three founding engineers, we were a flat team — no formal hierarchy, no designated tech lead. Around Month 3, a pattern emerged where one engineer consistently merged feature branches directly to `main` without PR review, bypassing the informal review process we had verbally agreed on. This caused two separate instances of broken builds reaching staging, one of which delayed a client demo.

**Task:**  
As the engineer who had set up the CI/CD pipeline and owned deployment stability, I needed to address the behavior without creating a rift in a three-person team where interpersonal trust was operationally critical. Escalating to the founder risked damaging team cohesion; ignoring it meant the problem would compound.

**Action:**  
I chose to separate the process problem from the person problem. Instead of raising it as "you're doing this wrong," I called a 30-minute team sync framed around "hardening our deployment pipeline before we scale." I presented two recent broken-build incidents as data — not blame — and proposed formalizing branch protection rules directly in GitHub: required PR approvals before merge to `main`, automated CI checks as a merge gate, and a shared deployment checklist. The rules applied equally to all three of us, including me.

**Result:**  
The engineer agreed without resistance — the framing made it a systems conversation, not a personal one. Branch protection rules were implemented the same week. We had zero direct-to-main incidents in the subsequent four months. The CI/CD pipeline change also contributed to the 30% reduction in deployment cycle time we measured across the team.

---
---

## STORY 2 — ADAPTING TO A MAJOR PIVOT

**Prompt types:** "Tell me about a time you had to change direction quickly." / "How do you handle ambiguity or shifting priorities?"

---

### STAR

**Situation:**  
Three months into building out the VyaparGPT WhatsApp assistant, the founder informed the engineering team that the product strategy was expanding: we were to add an AI-powered Website Builder as a second product targeting the same SMB audience — on a timeline of six weeks, running in parallel with VyaparGPT's ongoing development. No additional engineers were added.

**Task:**  
I needed to rapidly assess what could be reused from the existing architecture, what had to be built net-new, and how to split bandwidth across two active products without either shipping broken. I also had to recalibrate my own expectations — the Website Builder was a meaningfully different product surface (generative UI vs. conversational AI), requiring skills I hadn't been using on VyaparGPT.

**Action:**  
I spent the first two days doing a hard audit: which backend services from VyaparGPT (auth, Supabase layer, Razorpay billing, CI/CD) could be shared with the Website Builder with zero modification, and which required new domain logic. I identified that roughly 60% of infrastructure was reusable. I then restructured my sprint cadence — mornings on Website Builder (high-focus, greenfield work) and afternoons on VyaparGPT maintenance (lower-variance, familiar codebase). I flagged explicitly to the founder which features on each product were in-scope for the six-week window and which were post-launch, getting alignment before writing a line of new code.

**Result:**  
Both products shipped within the six-week window. The Website Builder launched with core generation and hosting functionality. Shared infrastructure meant we didn't double our deployment or monitoring burden. The explicit scope conversation prevented the scope creep that typically derails parallel-track development on small teams.

---
---

## STORY 3 — TAKING OWNERSHIP OF A FAILURE

**Prompt types:** "Tell me about a mistake you made and what you learned." / "Describe a time you failed and how you handled it."

---

### STAR

**Situation:**  
I was integrating Razorpay's subscription billing into the OpenBiz platform — webhook validation, payment state reconciliation, and retry flows. I tested the happy path (successful payment) and the explicit failure path (card declined) thoroughly in the Razorpay test environment, but I did not adequately test the edge case where a webhook arrives out of order: a `payment.captured` event arriving before the `subscription.activated` event it logically depends on.

**Task:**  
When we moved to production with the first paying customers, three users experienced a state where their payment was captured but their account remained in the free tier — the subscription status had not updated. These were real customers who had paid and couldn't access features. I was the sole engineer who had built and shipped this module.

**Action:**  
I did not wait to be told. I identified the bug within two hours of the first support complaint, traced it to the out-of-order webhook processing logic, and pushed a patch the same day: a re-entrant idempotency check that re-queried Razorpay's API to confirm subscription state on every `payment.captured` event, regardless of whether `subscription.activated` had been previously processed. I personally drafted the support responses for the three affected users and ensured their accounts were manually corrected before the fix deployed. I then wrote a post-mortem doc for the founder and the team covering the gap, the fix, and a checklist for webhook integration testing going forward (which included out-of-order event simulation).

**Result:**  
All three affected users were remediated within 24 hours with no churn. The post-mortem checklist became the standard for all subsequent payment and webhook integration work. I've never shipped a payment module since without explicit out-of-order event testing as a pre-launch gate.

---
---

## STORY 4 — MANAGING A 3-PERSON FOUNDING TEAM

**Prompt types:** "Have you ever led a team?" / "Describe your experience with technical leadership." / "How do you coordinate work across engineers?"

---

### STAR

**Situation:**  
OpenBiz had three founding engineers building two AI-powered products simultaneously (VyaparGPT and the Website Builder) for a B2B SMB market. There was no formal engineering manager — decisions about what to build, in what order, and to what quality standard were distributed across the three of us, with the founder setting product direction. In practice, because I had set up the core infrastructure (CI/CD, database schema, deployment pipeline), architectural decisions defaulted to me.

**Task:**  
Without a formal mandate to lead, I needed to create enough coordination structure to prevent duplicated work, conflicting architectural decisions, and deployment conflicts — while not creating bureaucratic overhead that would slow down a three-person startup team.

**Action:**  
I introduced three lightweight processes that added structure without ceremony. First, a shared `ARCHITECTURE.md` in the repo — a living document I maintained that logged every significant technical decision with its rationale, so any engineer could understand why the system was built a certain way without asking. Second, a daily async Slack standup: three bullet points — "shipped," "blocked," "next" — replacing the need for synchronous meetings. Third, explicit ownership tags in Notion tasks: every task had one owner, and owners had full autonomy within their domain. I also made it a policy that any change to shared infrastructure (database schema, environment variables, CI config) required a two-sentence heads-up in the engineering channel before merging, regardless of urgency.

**Result:**  
Zero "I didn't know you changed that" incidents in the last four months of the team's operation. The `ARCHITECTURE.md` was referenced by the founder during investor conversations as evidence of engineering discipline. The async standup format was adopted by the non-engineering team as well. The team shipped two products to 1,000+ users with three engineers and no engineering manager.

---
---

## STORY 5 — PRIORITIZING WITH LIMITED RESOURCES

**Prompt types:** "How do you manage competing priorities?" / "Tell me about a time you had to make a tough trade-off." / "How do you decide what not to build?"

---

### STAR

**Situation:**  
In Month 5 at OpenBiz, the product backlog had grown to approximately 40 open items across VyaparGPT and the Website Builder. These included: a highly requested multilingual response feature for VyaparGPT (demanded by SMB users in non-Hindi states), a VideoSDK integration for in-app conferencing (a founder priority), a performance investigation on API latency (an engineering-identified problem), and three UI polish tasks from the design backlog. We had three engineers and a two-week sprint.

**Task:**  
I needed to help the team — and the founder — make a defensible prioritization call on what entered the sprint and what did not, with explicit reasoning rather than ad-hoc judgment.

**Action:**  
I built a one-page prioritization matrix in Notion scoring each backlog item across three axes: **user impact** (how many active users does this affect, and how severely), **revenue risk** (does this block conversion or cause churn), and **engineering cost** (days to ship, risk of regressions). I scored each item 1–3 on each axis. The latency investigation scored highest on user impact and revenue risk — the N+1 query degradation was affecting all 1,000+ users on every API call. The VideoSDK integration scored high on founder priority but low on user impact (no users had requested it yet). The multilingual feature scored high on user impact but high on engineering cost. I presented the matrix to the founder, explicitly flagging the VideoSDK trade-off: delaying it by one sprint in favor of the latency fix would reduce the risk of user churn from performance complaints. The founder agreed.

**Result:**  
The sprint prioritized: latency investigation and fix (delivered the 40% API latency reduction), one UI polish task (low effort, high-visibility), and initial scaffolding for multilingual support. VideoSDK was deferred one sprint and shipped the following cycle. No user churn was attributed to performance during or after that period. The matrix format was reused for every subsequent sprint planning session.

---

> **Interview Usage Guide:**  
> — "Conflict" prompt → Story 1  
> — "Adaptability / ambiguity" prompt → Story 2  
> — "Failure / mistake" prompt → Story 3  
> — "Leadership / management" prompt → Story 4  
> — "Prioritization / trade-offs" prompt → Story 5  
> — "Tell me about yourself" (behavioral variant) → 90-second version: combine Story 4 opener + Story 5 result
