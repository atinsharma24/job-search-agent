"""
personalize_messages.py

Reads the canonical contacts CSV, scores each message against the personalization
rubric from docs/PERSONALIZATION_GUIDE.md, and for any message scoring < 2 it:

  1. Prints a review block to stdout:
       CONTACT: [name] | [company] | [persona]
       CURRENT: [current message]
       SUGGESTED: [personalized message using PERSONALIZATION_GUIDE mapping]
       SCORE: [new score]
       ---

  2. Writes a new CSV: contacts/personalized_draft.csv
     - Suggested messages filled in, status = "draft_personalized"
     - Original CSV is NOT modified.

Usage:
    python scripts/personalize_messages.py

Requires: python 3.9+, no external deps (stdlib only)
"""

import csv
import os
import sys
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
CONTACTS_CSV = ROOT / "contacts" / "LinkedIn Targets with Messages.csv"
DRAFT_CSV = ROOT / "contacts" / "personalized_draft.csv"
ERRORS_LOG = ROOT / "logs" / "errors.log"

MIN_SCORE = 2
CHAR_WARN = 280
CHAR_HARD = 300

# ---------------------------------------------------------------------------
# Domain-specific keywords (mirrors prepare_queue.ts DOMAIN_KEYWORDS)
# ---------------------------------------------------------------------------

DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "yellow.ai": ["orchestration", "conversational", "enterprise ai", "customer service ai", "ai agent"],
    "haptik": ["whatsapp commerce", "conversational ai", "agent orchestration", "chatbot"],
    "gupshup": ["conversational messaging", "messaging platform", "whatsapp api", "conversational"],
    "observe.ai": ["contact center", "agent guidance", "voice ai", "real-time"],
    "uniphore": ["voice ai", "conversational", "contact center", "speech"],
    "rezo.ai": ["contact center automation", "voice bot", "conversational ai"],
    "skit.ai": ["voice bot", "conversational", "contact center"],
    "sarvam ai": ["indian-language", "foundation model", "llm infrastructure", "multilingual"],
    "krutrim": ["foundation model", "llm", "indian language", "infrastructure"],
    "signzy": ["kyc", "identity verification", "digital kyc", "document verification"],
    "nanonets": ["document processing", "ocr", "intelligent document", "extraction"],
    "razorpay": ["payment", "billing", "fintech", "payment infrastructure", "payments"],
    "hasura": ["graphql", "data api", "real-time data", "api layer"],
    "postman": ["api", "developer workflow", "developer tooling", "api platform"],
    "browserstack": ["browser testing", "automated testing", "test automation", "cross-browser"],
    "lambdatest": ["automated browser", "test automation", "browser testing", "cloud testing"],
    "devrev": ["dev-centric", "customer platform", "product-led", "crm", "developer"],
    "appsmith": ["low-code", "internal tools", "developer tooling"],
    "locus": ["logistics", "supply chain", "routing", "dispatch"],
    "whatfix": ["digital adoption", "product analytics", "in-app guidance"],
}

ATIN_ASSET_KEYWORDS: list[str] = [
    "vyapargpt", "nimbus", "langgraph", "pgvector", "sub-800ms", "800ms",
    "40 smb", "40+ smb", "40%", "n+1", "idempotent", "razorpay webhook",
    "razorpay billing", "gemini vision", "document extraction", "gst", "aadhaar",
    "claude + mcp", "autonomous web agent", "provider fallback",
    "openai → gemini", "openai->gemini", "dual-model", "langchain",
    "100% payment", "100% consistency", "whatsapp-native", "whatsapp native",
    "whatsapp llm", "whatsapp ai", "founding engineer",
]

# ---------------------------------------------------------------------------
# Suggested message templates per company (fallback suggestions for generic messages)
# Uses persona to pick appropriate angle.
# These are template suggestions — a human must review before sending.
# ---------------------------------------------------------------------------

SUGGESTIONS: dict[str, dict[str, str]] = {
    # key: company (lowercase), value: dict keyed by persona_id prefix
    "yellow.ai": {
        "persona_1": "Hey {name} — built VyaparGPT, a WhatsApp-native AI for 40+ SMBs using LangChain and provider fallback. Yellow.ai's orchestration layer is exactly the kind of infra I want to work on. Would value connecting.",
        "persona_2": "Hey {name} — shipped LangGraph stateful agents and pgvector RAG at OpenBiz. Yellow.ai's enterprise conversational AI infra is the right next problem. Would connect.",
        "persona_3": "Hey {name} — own the full AI backend loop: VyaparGPT (WhatsApp LLM, LangGraph, 40 SMBs), pgvector RAG, MERN. Yellow.ai's conversational AI backend — no ramp needed. Would like to connect.",
        "persona_4": "Hey {name} — building LLM backends, curious how Yellow.ai's orchestration layer handles multi-turn context at enterprise scale — LangGraph or custom state machine? Would value exchanging notes.",
        "persona_5": "Hey {name} — Full-stack + AI eng, immediate joiner. VyaparGPT (WhatsApp AI, 40 SMBs), pgvector RAG, MERN, LangGraph. Targeting Yellow.ai's conversational AI roles. 15L+ (negotiable).",
    },
    "haptik": {
        "persona_1": "Hey {name} — built VyaparGPT, a WhatsApp-native LLM for 40+ SMBs with LangGraph state machines and provider fallback. Haptik's WhatsApp commerce and agent orchestration maps exactly to this. Would connect.",
        "persona_3": "Hey {name} — own the full loop: VyaparGPT (WhatsApp AI, LangGraph, 40 SMBs in prod), pgvector RAG, MERN TypeScript. No ramp needed on Haptik's conversational AI backend. Would like to connect.",
        "persona_4": "Hey {name} — building WhatsApp-native LLM systems, curious how Haptik handles multi-turn context at scale. LangGraph or custom orchestration? Would value exchanging notes.",
        "persona_5": "Hey {name} — Full-stack + AI eng, immediate joiner. VyaparGPT (WhatsApp AI, 40 SMBs), LangGraph, pgvector, MERN. Targeting Haptik's engineering roles. 15L+ (negotiable).",
    },
    "gupshup": {
        "persona_1": "Hey {name} — shipped a WhatsApp-native LLM for 40+ SMBs (LangGraph, provider fallback, full webhook lifecycle). Gupshup's conversational messaging platform is the infra layer I've been building on top of. Would connect.",
        "persona_2": "Hey {name} — built LLM orchestration (LangGraph) + pgvector RAG at OpenBiz. Gupshup's messaging API layer and conversational AI platform is a natural fit for this work. Would connect.",
        "persona_3": "Hey {name} — shipped VyaparGPT (WhatsApp AI, 40 SMBs in prod) and pgvector RAG. No ramp on Gupshup's conversational messaging backend. Would like to connect.",
        "persona_5": "Hey {name} — Full-stack + AI eng, immediate joiner. VyaparGPT (WhatsApp LLM, 40 SMBs), LangGraph, MERN, pgvector. Targeting Gupshup engineering roles. 15L+ (negotiable).",
    },
    "observe.ai": {
        "persona_1": "Hey {name} — shipped LangGraph stateful agents and a WhatsApp LLM for 40 SMBs at my last startup. Observe.AI's real-time agent guidance layer is the natural next problem. Would value connecting.",
        "persona_3": "Hey {name} — own the AI backend loop: LangGraph agents, pgvector RAG, MERN TypeScript, 40 SMBs in prod. No ramp on Observe.AI's contact center AI backend. Would like to connect.",
        "persona_5": "Hey {name} — Full-stack + AI eng, immediate joiner. LangGraph agents, pgvector RAG, VyaparGPT (40 SMBs). Targeting Observe.AI's engineering roles. 15L+ (negotiable).",
    },
    "rezo.ai": {
        "persona_1": "Hey {name} — built VyaparGPT (WhatsApp LLM, LangGraph, 40 SMBs) and a LangGraph AI CRM at OpenBiz. Rezo.ai's contact center automation is the exact domain. Would value connecting.",
        "persona_3": "Hey {name} — shipped LangGraph stateful agents and pgvector RAG at OpenBiz (40 SMBs in prod). No ramp on Rezo.ai's conversational AI backend. Would like to connect.",
    },
    "sarvam ai": {
        "persona_1": "Hey {name} — built dual-model fallback (OpenAI → Gemini on 5xx) and a provider-agnostic LLM layer at OpenBiz. Sarvam AI's work on Indian-language foundation models is the infra problem I want to be close to. Would connect.",
        "persona_3": "Hey {name} — shipped Nimbus RAG (sub-800ms pgvector) and dual-model fallback at OpenBiz. Sarvam AI's LLM infrastructure is where this experience maps. Would like to connect.",
        "persona_5": "Hey {name} — Full-stack + AI eng, immediate joiner. Nimbus RAG (sub-800ms pgvector), dual-model fallback, MERN, LangGraph. Targeting Sarvam AI's LLM infra roles. 15L+ (negotiable).",
    },
    "krutrim": {
        "persona_1": "Hey {name} — built dual-model fallback (OpenAI → Gemini) and provider-agnostic LLM layer at OpenBiz. Krutrim's Indian LLM infrastructure is the kind of foundational problem I want to work on. Would connect.",
        "persona_2": "Hey {name} — shipped LLM orchestration with provider-agnostic abstraction (Groq, OpenAI, Anthropic) and pgvector RAG at OpenBiz. Krutrim's LLM infrastructure build-out is where this applies. Would connect.",
        "persona_3": "Hey {name} — shipped Nimbus RAG (pgvector, sub-800ms) and dual-model fallback. No ramp on Krutrim's LLM infrastructure backend. Would like to connect.",
    },
    "signzy": {
        "persona_1": "Hey {name} — built a Gemini Vision doc extraction pipeline in prod at OpenBiz — GST certs, invoices, Aadhaar, unstructured doc fields. Signzy's digital KYC infra is exactly where this applies. Would love to connect.",
        "persona_3": "Hey {name} — shipped Gemini Vision doc extraction (GST, invoices, Aadhaar) and N+1 fix (40% latency drop) at OpenBiz. Ready to contribute to Signzy's KYC engineering stack from day one.",
    },
    "nanonets": {
        "persona_1": "Hey {name} — shipped Gemini Vision document extraction in prod at OpenBiz (GST, invoices, Aadhaar — unstructured to structured). Nanonets is doing this at scale for enterprises. Would value connecting.",
    },
    "razorpay": {
        "persona_1": "Hey {name} — shipped Razorpay idempotent webhook billing at OpenBiz (100% payment-state consistency, zero reconciliation) and resolved N+1 patterns cutting API latency 40%. Would value connecting.",
        "persona_2": "Hey {name} — built Razorpay idempotent webhooks (100% consistency) and resolved N+1 query chains (40% latency drop) at OpenBiz. Razorpay's payments infrastructure is a natural next domain. Would connect.",
        "persona_3": "Hey {name} — shipped idempotent Razorpay webhooks with 100% payment consistency and cut API latency 40% via N+1 resolution. No ramp on Razorpay's payments engineering stack. Looking to connect.",
    },
    "hasura": {
        "persona_1": "Hey {name} — resolved deep N+1 query chains in Supabase (40% latency drop) and built pgvector RAG with sub-800ms retrieval. Hasura's data API layer is where this expertise maps cleanly. Would connect.",
        "persona_3": "Hey {name} — diagnosed and resolved N+1 patterns (40% latency reduction) and shipped pgvector RAG at OpenBiz. No ramp on Hasura's data infrastructure engineering. Would like to connect.",
    },
    "postman": {
        "persona_1": "Hey {name} — built an autonomous web agent on Claude + MCP that translates context schemas into DOM-level interactions. Postman's developer workflow automation is the exact adjacent space. Would value connecting.",
        "persona_3": "Hey {name} — built an autonomous web agent (Claude + MCP) and full MERN stack with strict TypeScript. No ramp on Postman's API tooling backend. Would like to connect.",
        "persona_5": "Hey {name} — Full-stack + AI eng, immediate joiner. Autonomous web agent (Claude + MCP), MERN TypeScript, pgvector RAG. Targeting Postman engineering roles. 15L+ (negotiable).",
    },
    "browserstack": {
        "persona_1": "Hey {name} — built an autonomous web agent using Claude 3.5 + MCP for DOM interactions and WAF/CAPTCHA detection. BrowserStack's automated browser testing infra is where this maps directly. Would connect.",
        "persona_3": "Hey {name} — shipped an autonomous web agent (Claude + MCP) and MERN platform serving 1000+ users. No ramp on BrowserStack's test automation backend. Would like to connect.",
        "persona_5": "Hey {name} — Full-stack + AI eng, immediate joiner. Autonomous web agent (Claude + MCP), MERN TypeScript, GitHub Actions CI/CD. Targeting BrowserStack engineering. 15L+ (negotiable).",
    },
    "lambdatest": {
        "persona_1": "Hey {name} — built an autonomous web agent on Claude 3.5 Sonnet + MCP that navigates DOM interactions and handles WAF/CAPTCHA detection. LambdaTest's automated browser testing infra is where this connects. Would connect.",
        "persona_2": "Hey {name} — shipped an autonomous web agent (Claude + MCP) and full MERN backend at OpenBiz. LambdaTest's cloud testing infrastructure is the natural adjacent space. Would connect.",
        "persona_3": "Hey {name} — built an autonomous web agent (Claude + MCP) handling DOM interactions and CAPTCHA detection. No ramp on LambdaTest's test automation backend. Would like to connect.",
    },
    "devrev": {
        "persona_1": "Hey {name} — shipped LangGraph stateful agents for an AI CRM and an autonomous web agent on Claude + MCP at OpenBiz. DevRev's dev-centric customer platform is the natural application. Would value connecting.",
        "persona_2": "Hey {name} — built LangGraph AI CRM agents and autonomous web agent (Claude + MCP) at OpenBiz. DevRev's developer-first customer platform maps exactly to this intersection. Would connect.",
    },
}

# ---------------------------------------------------------------------------
# Scoring (mirrors prepare_queue.ts logic)
# ---------------------------------------------------------------------------

def score_message(name: str, company: str, message: str) -> tuple[int, list[str]]:
    msg = message.lower()
    co = company.lower()
    flags = []
    score = 0

    if co in msg:
        score += 1
        flags.append(f"+1: company name present")
    else:
        flags.append(f"0: company name missing")

    domain_keys = DOMAIN_KEYWORDS.get(co, [])
    hit = next((k for k in domain_keys if k in msg), None)
    if hit:
        score += 1
        flags.append(f"+1: domain keyword '{hit}' found")
    else:
        flags.append(f"0: no domain keywords found")

    asset_hit = next((k for k in ATIN_ASSET_KEYWORDS if k in msg), None)
    if asset_hit:
        score += 1
        flags.append(f"+1: Atin asset keyword '{asset_hit}' found")
    else:
        flags.append(f"0: no Atin asset keywords found")

    template_phrase = f"i like what {co} is building"
    if template_phrase in msg:
        score -= 1
        flags.append(f"-1: banned template phrase detected")

    return score, flags


def get_suggestion(name: str, company: str, persona: str) -> str:
    co = company.lower()
    persona_key = persona.split("_")[0] + "_" + persona.split("_")[1] if "_" in persona else persona
    # persona_key will be like "persona_1"
    parts = persona.split("_")
    if len(parts) >= 2:
        persona_key = f"{parts[0]}_{parts[1]}"
    else:
        persona_key = persona

    company_templates = SUGGESTIONS.get(co, {})
    template = company_templates.get(persona_key, "")

    if not template:
        # fallback to persona_1 or first available
        template = next(iter(company_templates.values()), "")

    if not template:
        return f"[No suggestion available — add entry to SUGGESTIONS dict in personalize_messages.py for company='{company}', persona='{persona_key}']"

    return template.format(name=name.split()[0])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if not CONTACTS_CSV.exists():
        print(f"ERROR: contacts CSV not found at {CONTACTS_CSV}", file=sys.stderr)
        sys.exit(1)

    with open(CONTACTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        contacts = list(reader)

    draft_rows = []
    flagged = 0
    errors = []

    for row in contacts:
        name = row.get("name", "").strip()
        url = row.get("url", "").strip()
        persona = row.get("persona", "").strip()
        company = row.get("company", "").strip()
        message = row.get("message", "").strip()

        score, flags = score_message(name, company, message)
        char_count = len(message)

        if score < MIN_SCORE:
            flagged += 1
            suggestion = get_suggestion(name, company, persona)
            new_score, _ = score_message(name, company, suggestion)

            print(f"CONTACT: {name} | {company} | {persona}")
            print(f"CURRENT: {message}")
            print(f"SUGGESTED: {suggestion}")
            print(f"SCORE: {new_score} (was {score})")
            print(f"CHARS: {len(suggestion)}")
            print("---")

            draft_rows.append({
                "name": name,
                "url": url,
                "persona": persona,
                "company": company,
                "message": suggestion,
                "status": "draft_personalized",
                "personalization_score": new_score,
                "original_score": score,
                "char_count": len(suggestion),
                "notes": "; ".join(flags),
            })

            if char_count > CHAR_HARD:
                errors.append(f"CHAR_LIMIT_EXCEEDED | {name} | {company} | {char_count} chars")
        else:
            draft_rows.append({
                "name": name,
                "url": url,
                "persona": persona,
                "company": company,
                "message": message,
                "status": "ok",
                "personalization_score": score,
                "original_score": score,
                "char_count": char_count,
                "notes": "; ".join(flags),
            })

    # Write draft CSV
    fieldnames = ["name", "url", "persona", "company", "message", "status",
                  "personalization_score", "original_score", "char_count", "notes"]
    with open(DRAFT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(draft_rows)

    # Append errors to log
    if errors:
        timestamp = datetime.now().isoformat()
        with open(ERRORS_LOG, "a", encoding="utf-8") as f:
            for err in errors:
                f.write(f"[{timestamp}] {err}\n")

    print(f"\nSummary:")
    print(f"  Total contacts: {len(contacts)}")
    print(f"  Flagged (score < {MIN_SCORE}): {flagged}")
    print(f"  Already passing: {len(contacts) - flagged}")
    print(f"  Draft written to: {DRAFT_CSV}")


if __name__ == "__main__":
    main()
