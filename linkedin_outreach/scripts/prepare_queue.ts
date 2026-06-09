/**
 * prepare_queue.ts
 *
 * Reads contacts CSV, scores each message for personalization,
 * and writes pending.json for human review before send.
 *
 * Personalization score rubric (see docs/PERSONALIZATION_GUIDE.md):
 *   +1  message contains the contact's company name
 *   +1  message references something specific about what the company builds
 *       (detected via domain keyword heuristics per company — see DOMAIN_KEYWORDS below)
 *   +1  message references a specific Atin project or metric
 *       (detected via ATIN_ASSET_KEYWORDS below)
 *   -1  message contains the phrase "I like what [Company] is building" (template tell)
 *
 * Passing threshold: score >= 2 (set in agent_config.json as min_personalization_score)
 * Character limit: 300 hard (LinkedIn), 280 soft (flagged as warning)
 *
 * Entries scoring below threshold are written to pending.json with
 * status = "needs_personalization" and a warning is logged to errors.log.
 * Only entries with status = "pending" or "approved" advance through the pipeline.
 */

import fs from "fs";
import path from "path";
import { parse } from "csv-parse/sync";

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const ROOT = path.resolve(__dirname, "..");
const CONTACTS_CSV = path.join(ROOT, "contacts", "priority_personalized.csv");
const PENDING_JSON = path.join(ROOT, "queue", "pending.json");
const ERRORS_LOG = path.join(ROOT, "logs", "errors.log");

const MIN_PERSONALIZATION_SCORE = 2;
const CHAR_WARN_LIMIT = 280;
const CHAR_HARD_LIMIT = 300;

// ---------------------------------------------------------------------------
// Keyword heuristics for "references something specific about what the company builds"
// Add entries here as new companies are targeted.
// ---------------------------------------------------------------------------

const DOMAIN_KEYWORDS: Record<string, string[]> = {
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
};

// ---------------------------------------------------------------------------
// Keywords that indicate a specific Atin project or metric is referenced
// ---------------------------------------------------------------------------

const ATIN_ASSET_KEYWORDS: string[] = [
  "vyapargpt",
  "nimbus",
  "langgraph",
  "pgvector",
  "sub-800ms",
  "800ms",
  "40 smb",
  "40+ smb",
  "40%",
  "n+1",
  "idempotent",
  "razorpay webhook",
  "razorpay billing",
  "gemini vision",
  "document extraction",
  "gst",
  "aadhaar",
  "claude + mcp",
  "autonomous web agent",
  "provider fallback",
  "openai → gemini",
  "openai->gemini",
  "dual-model",
  "langchain",
  "100% payment",
  "100% consistency",
  "whatsapp-native",
  "whatsapp native",
  "whatsapp llm",
  "whatsapp ai",
  "founding engineer",
];

// ---------------------------------------------------------------------------
// Scoring
// ---------------------------------------------------------------------------

interface Contact {
  name: string;
  url: string;
  persona: string;
  company: string;
  message: string;
}

interface QueueEntry extends Contact {
  status: "pending" | "needs_personalization" | "approved" | "sent" | "skipped";
  personalization_score: number;
  char_count: number;
  score_flags: string[];
}

function scoreMessage(contact: Contact): { score: number; flags: string[] } {
  const msg = contact.message.toLowerCase();
  const company = contact.company.toLowerCase();
  const flags: string[] = [];
  let score = 0;

  // +1: company name present
  if (msg.includes(company)) {
    score += 1;
    flags.push(`+1: company name "${contact.company}" found`);
  } else {
    flags.push(`0: company name "${contact.company}" NOT found`);
  }

  // +1: references something specific about what the company builds
  const domainKeys = DOMAIN_KEYWORDS[company] ?? [];
  const domainHit = domainKeys.find((kw) => msg.includes(kw));
  if (domainHit) {
    score += 1;
    flags.push(`+1: domain keyword "${domainHit}" found`);
  } else {
    flags.push(`0: no domain-specific keywords found (add entries to DOMAIN_KEYWORDS if needed)`);
  }

  // +1: references a specific Atin project or metric
  const assetHit = ATIN_ASSET_KEYWORDS.find((kw) => msg.includes(kw.toLowerCase()));
  if (assetHit) {
    score += 1;
    flags.push(`+1: Atin asset keyword "${assetHit}" found`);
  } else {
    flags.push(`0: no Atin asset keywords found`);
  }

  // -1: contains template phrase "i like what [company] is building"
  const templatePhrase = `i like what ${company} is building`;
  if (msg.includes(templatePhrase)) {
    score -= 1;
    flags.push(`-1: contains banned template phrase "I like what ${contact.company} is building"`);
  }

  return { score, flags };
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

function appendError(line: string): void {
  const timestamp = new Date().toISOString();
  fs.appendFileSync(ERRORS_LOG, `[${timestamp}] ${line}\n`);
}

function main(): void {
  console.log("prepare_queue: reading contacts CSV...");

  const raw = fs.readFileSync(CONTACTS_CSV, "utf-8");
  const contacts: Contact[] = parse(raw, {
    columns: true,
    skip_empty_lines: true,
    trim: true,
  });

  const queue: QueueEntry[] = [];
  let flaggedCount = 0;

  for (const contact of contacts) {
    const { score, flags } = scoreMessage(contact);
    const charCount = contact.message.length;

    let status: QueueEntry["status"] = "pending";

    if (score < MIN_PERSONALIZATION_SCORE) {
      status = "needs_personalization";
      flaggedCount++;
      const warning =
        `PERSONALIZATION_FAIL | ${contact.name} | ${contact.company} | ` +
        `score=${score} | chars=${charCount} | flags: ${flags.join("; ")}`;
      appendError(warning);
      console.warn(`  [WARN] ${contact.name} (${contact.company}): score=${score} < ${MIN_PERSONALIZATION_SCORE} → needs_personalization`);
    }

    if (charCount > CHAR_HARD_LIMIT) {
      status = "needs_personalization";
      const error =
        `CHAR_LIMIT_EXCEEDED | ${contact.name} | ${contact.company} | chars=${charCount} > ${CHAR_HARD_LIMIT}`;
      appendError(error);
      console.error(`  [ERROR] ${contact.name}: message is ${charCount} chars — exceeds hard limit of ${CHAR_HARD_LIMIT}`);
    } else if (charCount > CHAR_WARN_LIMIT) {
      const warning =
        `CHAR_LIMIT_WARNING | ${contact.name} | ${contact.company} | chars=${charCount} > ${CHAR_WARN_LIMIT} (soft limit)`;
      appendError(warning);
      console.warn(`  [WARN] ${contact.name}: message is ${charCount} chars — above soft limit of ${CHAR_WARN_LIMIT}`);
    }

    queue.push({
      ...contact,
      status,
      personalization_score: score,
      char_count: charCount,
      score_flags: flags,
    });
  }

  fs.writeFileSync(PENDING_JSON, JSON.stringify(queue, null, 2), "utf-8");

  console.log(`\nprepare_queue: done.`);
  console.log(`  Total contacts: ${contacts.length}`);
  console.log(`  Flagged (needs_personalization): ${flaggedCount}`);
  console.log(`  Ready for review: ${contacts.length - flaggedCount}`);
  console.log(`  Output: ${PENDING_JSON}`);
}

main();
