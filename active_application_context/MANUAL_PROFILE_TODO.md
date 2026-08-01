# Manual profile steps (automation blocked)

Everything below is already correct in the vault — these are the places the portal
UI resisted automation and needs a human. Values are copy-paste ready.

---

## 1. Naukri — add Employment entry  ⚠ HIGH VALUE

The Employment section is **completely empty**, so recruiter searches filtered by
current company or designation will not surface the profile at all. The
add-employment modal dismisses itself when the suggestion dropdown is escaped,
which is what blocked automation.

`naukri.com/mnjuser/profile` → **Employment** → **Add**

| Field | Value |
|---|---|
| Is this your current employment? | **Yes** |
| Employment type | **Full-time** |
| Total experience | **1 year 2 months** |
| Current company name | **AGI Ready Inc.** |
| Current designation | **Full-Stack Developer** |
| Joining date | **Jun 2026** |
| Current salary | **11,20,000** |
| Skills used | Next.js, TypeScript, Node.js, React, PostgreSQL, RAG, LLM |

**Job profile** (paste as-is):

> Build and ship full-stack product features in Next.js, TypeScript and Node.js
> across multiple concurrent client products. Architect and integrate service APIs
> spanning third-party platforms, AI/LLM providers, webhook receivers and
> asynchronous background workflows. Own production systems end-to-end through
> debugging, deployment and release. Operate an AI-native development workflow
> using Claude Code and Codex.

---

## 2. Naukri — profile location

Currently reads **Bengaluru, INDIA**; the canonical location is **Agra, Uttar
Pradesh**. Deliberately left unchanged — Bengaluru may be intentional, since it
materially widens recruiter reach for on-site and hybrid roles. Change it only if
you want the profile to state where you actually live.

---

## 3. Instahyre — profile resume

Instahyre applies with the resume attached to your **profile**, not an uploaded
file, so no code path can reach it. Replace it manually at
`instahyre.com` → Profile → Resume with:

    resumes_and_docs/categories/pdf/Atin_Sharma_Resume_2026.pdf

---

## 4. LinkedIn — stored resume list

LinkedIn keeps every previously uploaded resume and offers them as a picker. The
list is dominated by old `2026New1.pdf` copies (and one
`staged_application_resume.pdf`, which leaked the private 15L floor). The applier
uploads a fresh validated file per application, so submissions are correct — but
consider deleting the stale entries so a manual application cannot pick one by
mistake.

---

## Already done automatically

- ✅ Naukri resume → `Atin_Sharma_Resume_2026.pdf` (confirmed live, 1 Aug 2026)
- ✅ Naukri headline → "Full-Stack Developer at AGI Ready Inc. | Next.js ·
  TypeScript · Node.js · AI Systems · RAG Pipelines · LLM Agents"
- ✅ Naukri notice period already showed "15 Days or less"
- ✅ Naukri total experience already showed "1 Year"
