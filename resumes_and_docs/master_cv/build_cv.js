const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, LevelFormat, BorderStyle, WidthType, ShadingType, VerticalAlign
} = require('docx');
const fs = require('fs');

// ─── Page geometry ────────────────────────────────────────────────────────────
const PAGE_W   = 11906;          // A4 width in DXA
const PAGE_H   = 16838;          // A4 height in DXA
const MARGIN   = 1020;           // 1.8 cm  (1.8 / 2.54 * 1440 ≈ 1020)
const CW       = PAGE_W - 2 * MARGIN; // content width = 9866 DXA

// ─── Typography constants ─────────────────────────────────────────────────────
const F        = "Calibri";
const SZ_NAME  = 40;  // 20 pt
const SZ_TITLE = 22;  // 11 pt
const SZ_CONT  = 19;  // 9.5 pt
const SZ_HEAD  = 24;  // 12 pt
const SZ_BODY  = 21;  // 10.5 pt
const LS       = 276; // 1.15 line-spacing = 276 twentieths
const SP_BODY  = { before: 0, after: 40, line: LS, lineRule: "auto" };
const SP_TIGHT = { before: 0, after: 20, line: LS, lineRule: "auto" };

// ─── Border helpers ───────────────────────────────────────────────────────────
const bThin    = { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC" };
const bNone    = { style: BorderStyle.NONE,   size: 0, color: "FFFFFF" };
const bRule    = { style: BorderStyle.SINGLE, size: 6, color: "AAAAAA", space: 4 };

function cellBorder(top, bottom, left, right) {
  return { top, bottom, left, right };
}

// ─── Text helpers ─────────────────────────────────────────────────────────────
function run(text, props = {}) {
  return new TextRun({ text, font: F, size: SZ_BODY, ...props });
}

// Parse inline **bold** markers into an array of TextRun objects
function parseRuns(text, baseProps = {}) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.filter(p => p).map(p => {
    const isBold = p.startsWith('**') && p.endsWith('**');
    return new TextRun({
      text: isBold ? p.slice(2, -2) : p,
      font: F,
      size: SZ_BODY,
      bold: isBold,
      ...baseProps,
    });
  });
}

// ─── Block builders ───────────────────────────────────────────────────────────
function spacer(before = 0, after = 60) {
  return new Paragraph({ children: [], spacing: { before, after } });
}

function sectionHeading(text) {
  return new Paragraph({
    children: [new TextRun({ text, font: F, size: SZ_HEAD, bold: true, allCaps: true })],
    spacing: { before: 160, after: 50 },
    border: { bottom: bRule },
  });
}

function bullet(text) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    children: parseRuns(text),
    spacing: { before: 0, after: 30, line: LS, lineRule: "auto" },
  });
}

function roleHeader(boldPart, restPart) {
  return new Paragraph({
    children: [
      new TextRun({ text: boldPart, font: F, size: SZ_BODY, bold: true }),
      new TextRun({ text: restPart, font: F, size: SZ_BODY }),
    ],
    spacing: { before: 110, after: 30, line: LS, lineRule: "auto" },
  });
}

function projectHeader(boldName, rest) {
  return new Paragraph({
    children: [
      new TextRun({ text: boldName, font: F, size: SZ_BODY, bold: true }),
      new TextRun({ text: rest,     font: F, size: SZ_BODY }),
    ],
    spacing: { before: 100, after: 20, line: LS, lineRule: "auto" },
  });
}

function stackLine(text) {
  return new Paragraph({
    children: [new TextRun({ text, font: F, size: SZ_BODY, italics: true })],
    spacing: SP_TIGHT,
  });
}

function bodyPara(text) {
  return new Paragraph({
    children: parseRuns(text),
    spacing: SP_BODY,
  });
}

// ─── Key Metrics table (2 cols × 4 rows) ─────────────────────────────────────
function metricsTable() {
  const colW = Math.floor(CW / 2);
  const rows = [
    [["API Latency Reduction",              "40%"],
     ["Platform Active Users",              "1,000+"]],
    [["Deployment Cycle Faster",            "30%"],
     ["VyaparGPT SMB Pilot",               "40 businesses"]],
    [["Shared Infra Reuse (Website Builder)","~60%"],
     ["LeetCode Problems Solved",           "347"]],
    [["Founding Team Size",                 "3 engineers"],
     ["Zero Broken-Build Incidents",        "4 months post CI/CD"]],
  ];
  return new Table({
    width: { size: CW, type: WidthType.DXA },
    columnWidths: [colW, CW - colW],
    rows: rows.map(row =>
      new TableRow({
        children: row.map(([label, value], i) =>
          new TableCell({
            width: { size: i === 0 ? colW : CW - colW, type: WidthType.DXA },
            shading: { fill: "F2F2F2", type: ShadingType.CLEAR },
            borders: cellBorder(bThin, bThin, bThin, bThin),
            margins: { top: 70, bottom: 70, left: 140, right: 140 },
            verticalAlign: VerticalAlign.CENTER,
            children: [new Paragraph({
              children: [
                new TextRun({ text: label + ":  ", font: F, size: SZ_BODY }),
                new TextRun({ text: value,         font: F, size: SZ_BODY, bold: true }),
              ],
              spacing: { before: 0, after: 0 },
            })],
          })
        )
      })
    ),
  });
}

// ─── Technical Skills table ───────────────────────────────────────────────────
function skillsTable() {
  const leftW  = Math.round(CW * 0.22);
  const rightW = CW - leftW;
  const rows = [
    ["Languages",      "JavaScript, TypeScript, Python, SQL, Java"],
    ["Frontend",       "React.js (v18, v19), Next.js, React Native, Redux Toolkit, TailwindCSS"],
    ["Backend",        "Node.js, Express.js, NestJS, Django, Laravel"],
    ["Databases",      "PostgreSQL, Supabase, MongoDB, ChromaDB, pgvector, AWS DynamoDB"],
    ["AI / LLM",       "OpenAI API, Google Gemini API, Groq API, RAG Pipelines, pgvector, ChromaDB, Sentence Transformers (all-MiniLM-L6-v2), Vercel AI SDK, LangChain.js, Prompt Engineering, PyPDF2, Claude 3.5 Sonnet (Anthropic API), MCP"],
    ["DevOps / Cloud", "Docker, GitHub Actions, Vercel, AWS S3, AWS SNS"],
    ["Tools",          "Git, Postman, Socket.IO, Razorpay SDK, VideoSDK, Puppeteer, BrowserOS / OpenClaw"],
    ["Patterns",       "WebSocket (Socket.IO), REST, Webhook Validation (HMAC-SHA256), N+1 Query Optimization, Vector Similarity Search (cosine), Provider-Agnostic LLM Layers, Idempotent Event Processing"],
  ];
  return new Table({
    width: { size: CW, type: WidthType.DXA },
    columnWidths: [leftW, rightW],
    rows: rows.map(([cat, vals]) =>
      new TableRow({
        children: [
          new TableCell({
            width: { size: leftW, type: WidthType.DXA },
            borders: cellBorder(bNone, bThin, bNone, bNone),
            margins: { top: 50, bottom: 50, left: 0, right: 100 },
            children: [new Paragraph({
              children: [new TextRun({ text: cat, font: F, size: SZ_BODY, bold: true })],
              spacing: { before: 0, after: 0 },
            })],
          }),
          new TableCell({
            width: { size: rightW, type: WidthType.DXA },
            borders: cellBorder(bNone, bThin, bNone, bNone),
            margins: { top: 50, bottom: 50, left: 80, right: 0 },
            children: [new Paragraph({
              children: [new TextRun({ text: vals, font: F, size: SZ_BODY })],
              spacing: { before: 0, after: 0 },
            })],
          }),
        ],
      })
    ),
  });
}

// ─── Profile Snapshot table ───────────────────────────────────────────────────
function profileTable() {
  const leftW  = Math.round(CW * 0.28);
  const rightW = CW - leftW;
  const rows = [
    ["Availability",        "Immediate Joiner — 0-day notice period"],
    ["Work Mode",           "Remote-first; open to Bangalore, Hyderabad, Pune, Delhi NCR, Mumbai"],
    ["Expected CTC",        "15L+ (negotiable, no hard ceiling) — INR"],
    ["Work Authorization",  "Indian Citizen — no sponsorship required"],
    ["GitHub",              "github.com/atinsharma24/"],
    ["LinkedIn",            "linkedin.com/in/atinsharma24/"],
  ];
  return new Table({
    width: { size: CW, type: WidthType.DXA },
    columnWidths: [leftW, rightW],
    rows: rows.map(([label, value]) =>
      new TableRow({
        children: [
          new TableCell({
            width: { size: leftW, type: WidthType.DXA },
            borders: cellBorder(bNone, bThin, bNone, bNone),
            margins: { top: 50, bottom: 50, left: 0, right: 100 },
            children: [new Paragraph({
              children: [new TextRun({ text: label, font: F, size: SZ_BODY, bold: true })],
              spacing: { before: 0, after: 0 },
            })],
          }),
          new TableCell({
            width: { size: rightW, type: WidthType.DXA },
            borders: cellBorder(bNone, bThin, bNone, bNone),
            margins: { top: 50, bottom: 50, left: 80, right: 0 },
            children: [new Paragraph({
              children: [new TextRun({ text: value, font: F, size: SZ_BODY })],
              spacing: { before: 0, after: 0 },
            })],
          }),
        ],
      })
    ),
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// Document assembly
// ═══════════════════════════════════════════════════════════════════════════════
const doc = new Document({
  numbering: {
    config: [{
      reference: "bullets",
      levels: [{
        level: 0,
        format: LevelFormat.BULLET,
        text: "•",
        alignment: AlignmentType.LEFT,
        style: {
          paragraph: { indent: { left: 380, hanging: 220 } },
          run: { font: "Symbol" },
        },
      }],
    }],
  },

  sections: [{
    properties: {
      page: {
        size:   { width: PAGE_W, height: PAGE_H },
        margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN },
      },
    },
    children: [

      // ─── HEADER ─────────────────────────────────────────────────────────────
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "ATIN SHARMA", font: F, size: SZ_NAME, bold: true })],
        spacing: { before: 0, after: 50 },
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Full-Stack Product Engineer  |  AI Systems  |  RAG Pipelines  |  WhatsApp Automation", font: F, size: SZ_TITLE })],
        spacing: { before: 0, after: 40 },
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "atinsharma24@gmail.com  |  +91 82185 02886  |  github.com/atinsharma24/  |  linkedin.com/in/atinsharma24/", font: F, size: SZ_CONT })],
        spacing: { before: 0, after: 30 },
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Agra, Uttar Pradesh, India — Open to Remote & Relocation", font: F, size: SZ_CONT })],
        spacing: { before: 0, after: 100 },
      }),

      // ─── PROFESSIONAL SUMMARY ────────────────────────────────────────────────
      sectionHeading("PROFESSIONAL SUMMARY"),
      new Paragraph({
        children: [new TextRun({
          text: "Founding engineer with 12 months of production experience building AI-powered full-stack systems at OpenBiz Software India Pvt Ltd — one of three engineers who shipped two commercial products from zero to 1,000+ active Indian SMB users. Specializes in MERN + AI stacks (TypeScript, Node.js, Python, PostgreSQL) with hands-on production delivery across conversational AI (VyaparGPT, WhatsApp-native LLM assistant for 40+ SMB pilot businesses), production RAG pipelines (Nimbus on pgvector + Groq; DocGPT on ChromaDB), and resilient DevOps (GitHub Actions + Vercel CI/CD reducing deployment cycle time by 30%). Technical scope spans full-stack product engineering, dual-model LLM provider-fallback (OpenAI ↔ Gemini), idempotent Razorpay billing, real-time Socket.IO infrastructure, and autonomous multi-agent web automation (Claude 3.5 Sonnet + MCP). Immediate joiner (0-day notice) targeting 15L+ (negotiable, no hard ceiling) in founding-stage or early-product roles with full-stack ownership. VIT Vellore, B.Tech Computer Science Engineering, graduating May 2026.",
          font: F, size: SZ_BODY,
        })],
        spacing: { before: 80, after: 80, line: LS, lineRule: "auto" },
      }),

      // ─── KEY METRICS ─────────────────────────────────────────────────────────
      sectionHeading("KEY METRICS"),
      spacer(60, 0),
      metricsTable(),
      spacer(0, 80),

      // ─── PROFESSIONAL EXPERIENCE ─────────────────────────────────────────────
      sectionHeading("PROFESSIONAL EXPERIENCE"),

      // OpenBiz
      roleHeader("OpenBiz Software India Pvt Ltd",
        "  |  Founding Engineer  |  Jun 2025 – May 2026  |  Remote / Bangalore"),
      new Paragraph({
        children: [new TextRun({ text: "One of three founding technical leads; architected and shipped two AI-powered SaaS products for the Indian SMB market on the MERN stack.", font: F, size: SZ_BODY, italics: true })],
        spacing: { before: 0, after: 40, line: LS, lineRule: "auto" },
      }),
      bullet("Architected **VyaparGPT**, a WhatsApp-native LLM assistant in Node.js: designed the full message lifecycle (WhatsApp Business API webhook ingestion → HMAC-SHA256 validation → session context lookup → LLM dispatch → response delivery), serving **40+ SMBs** in closed pilot and scaling to **1,000+ active platform users**. Multi-turn conversational context via rolling conversation_history[] enables natural follow-up queries."),
      bullet("Engineered **LLM provider-fallback** (OpenAI → Google Gemini): on HTTP 5xx, 429 rate-limit, or configurable timeout, requests are transparently rerouted with response-shape normalization — zero failure surface exposed to users."),
      bullet("Built a **Gemini Vision API document verification module** extracting structured fields (GST number, business name, invoice amount, dates) from WhatsApp photographs of GST certificates and vendor agreements, eliminating a manual data-entry step in SMB onboarding."),
      bullet("Resolved critical **N+1 query patterns** in Supabase (PostgreSQL): rewrote ORM calls to JOIN-based queries, introduced composite indexes on high-frequency WHERE/JOIN columns, and added TTL-based response caching — achieving verified **40% API latency reduction** at 1,000+ user scale."),
      bullet("Built and owned **GitHub Actions + Vercel CI/CD pipeline** from scratch: automated testing on every PR, staging deploys on merge, production gated behind explicit approval, branch protection rules — driving **30% reduction in deployment cycle time** and **zero broken-build incidents** over four months."),
      bullet("Delivered the **Automated Content Intelligence Pipeline**: Puppeteer-based headless scraping (waitUntil: 'networkidle2' for SPA hydration), TypeScript normalization, dual-model AI rewriting (Gemini primary → OpenAI failover per article), React 19 Diff View for human-in-the-loop editorial approval, Dockerized microservices on GitHub Actions cron schedule."),
      bullet("Shipped a parallel **Website Builder product** within a 6-week window at zero headcount increase by auditing and reusing **~60% of shared infrastructure** (auth, Supabase layer, Razorpay billing, CI/CD); restructured sprint cadence to separate greenfield work from maintenance load."),
      bullet("Implemented **idempotent Razorpay subscription billing**: HMAC webhook validation, payment-state reconciliation, out-of-order event handling via re-entrant idempotency check — achieving **100% payment-state consistency** across all paying customers."),

      // VIT
      roleHeader("Vellore Institute of Technology",
        "  |  Research Contributor  |  Jan 2025 – Nov 2025  |  Vellore (On-campus)"),
      bullet("Contributed to research on **Blockchain-Based LLM Model Using Fully Homomorphic Encryption (FHE) for Academic Records** — investigating how FHE enables computation on encrypted student data without decryption, with blockchain providing an immutable audit trail for credential issuance and verification."),
      bullet("Evaluated architectural trade-offs between on-chain data storage and off-chain encrypted record pointers, assessing gas cost constraints versus data privacy guarantees in an academic credential provenance system."),
      bullet("Explored how model inference could operate on privacy-preserving representations of sensitive academic data using FHE-compatible cryptographic primitives, without exposing plaintext records."),

      // ─── PROJECTS ────────────────────────────────────────────────────────────
      sectionHeading("PROJECTS"),

      // 1. Nimbus
      projectHeader("Nimbus", " — AI-First RAG Document Workspace  (in progress)"),
      stackLine("Stack: Next.js 14 · TypeScript · PostgreSQL · pgvector · Prisma · NextAuth.js · Groq API · OpenAI"),
      bullet("Production-grade RAG pipeline: async queue-based ingestion (status states: pending → processing → indexed → error), overlap chunking to prevent semantic loss at chunk boundaries, embedding generation, and storage in a pgvector extension column within PostgreSQL."),
      bullet("**Cosine similarity search** via pgvector (embedding <=> query_vector) co-locates vector data with relational metadata (user_id, document_id) for hybrid SQL + semantic filtering — **sub-800ms retrieval** target."),
      bullet("**Provider-agnostic LLM abstraction layer**: single config flag (provider: \"groq\" | \"openai\" | \"anthropic\") routes generation calls — switching inference providers requires zero code changes."),
      bullet("**Streaming responses** via Groq API delivered as SSE, providing real-time token-by-token document Q&A. Ingestion pipeline includes **429 retry logic** (exponential backoff) and per-document status tracking."),

      // 2. Autonomous Web Agent
      projectHeader("Autonomous Web Agent", " — Claude 3.5 Sonnet + MCP Orchestration"),
      stackLine("GitHub: github.com/atinsharma24/auto-agent  ·  Stack: Python · Groq API · BrowserOS (MCP) · OpenClaw · Claude 3.5 Sonnet"),
      bullet("**Dual-agent architecture**: Executor (Claude 3.5 Sonnet) handles complex multi-step DOM + form reasoning; Watcher (Groq fast inference) validates page state between every transition — separating expensive reasoning from high-frequency cheap polling."),
      bullet("**MCP (Model Context Protocol)** via BrowserOS gives the Executor structured tool-level access to browser DOM (inspect labels, types, values), form-fill, and navigation — intent-driven traversal with no brittle CSS selectors."),
      bullet("Persistent **local queue manager** (status: pending → in_progress → applied / failed / escalated) with URL deduplication; **WAF/CAPTCHA detection** via DOM fingerprint — Watcher escalates to human, Executor resumes from last checkpoint."),

      // 3. DocGPT
      projectHeader("DocGPT", " — RAG Document Assistant"),
      stackLine("Stack: React 19 · Python (Django) · ChromaDB · OpenAI GPT-4o-mini · all-MiniLM-L6-v2 · PyPDF2 · Docker"),
      bullet("Full Django RAG pipeline: PDF extraction via PyPDF2 with overlap chunking (~500–1000 tokens, ~50–100 overlap), **local embedding** via all-MiniLM-L6-v2 (384-dimensional, offline — zero API cost), ChromaDB cosine retrieval, GPT-4o-mini generation."),
      bullet("Containerized Django backend + ChromaDB as Docker services; prompt structure: system context + k-nearest retrieved chunks + user query for grounded generation."),

      // 4. VyaparGPT (professional product — condensed to avoid full duplication with experience)
      projectHeader("VyaparGPT", " — WhatsApp AI Business Assistant  (OpenBiz product)"),
      stackLine("Stack: Node.js · OpenAI API · Google Gemini API · WhatsApp Business API"),
      bullet("Full WhatsApp message lifecycle: webhook ingestion → HMAC-SHA256 validation → message-type routing (text / media / document / status) → session context → LLM dispatch → delivery."),
      bullet("Session-based multi-turn context (rolling conversation_history[]) with configurable TTL expiry; Gemini Vision API extracts structured fields from photographed SMB documents (GST certificates, invoices, vendor agreements)."),

      // 5. Content Intelligence Pipeline (condensed)
      projectHeader("Automated Content Intelligence Pipeline", "  (OpenBiz product)"),
      stackLine("Stack: React 19 · TypeScript · Laravel · Node.js · OpenAI · Google Gemini · Docker · GitHub Actions · Puppeteer"),
      bullet("Puppeteer headless Chromium (waitUntil: 'networkidle2') for SPA scraping; dual-model AI rewriting (Gemini primary → OpenAI fallback per article); React 19 split-screen Diff View with per-article state machine (pending_review → approved → published)."),
      bullet("Dockerized microservices (Scraper, AI Rewriter, Laravel API, React Frontend) with unless-stopped restart policy; GitHub Actions cron schedule drives fully automated ingestion and review cycles."),

      // ─── TECHNICAL SKILLS ────────────────────────────────────────────────────
      sectionHeading("TECHNICAL SKILLS"),
      spacer(60, 0),
      skillsTable(),
      spacer(0, 80),

      // ─── EDUCATION ───────────────────────────────────────────────────────────
      sectionHeading("EDUCATION"),
      new Paragraph({
        children: [new TextRun({ text: "Vellore Institute of Technology, Vellore", font: F, size: SZ_BODY, bold: true })],
        spacing: { before: 80, after: 20, line: LS, lineRule: "auto" },
      }),
      new Paragraph({
        children: [new TextRun({ text: "B.Tech in Computer Science and Engineering  |  Graduating May 2026", font: F, size: SZ_BODY })],
        spacing: SP_TIGHT,
      }),
      new Paragraph({
        children: [new TextRun({ text: "Focus: Full Stack Development, AI Systems", font: F, size: SZ_BODY, italics: true })],
        spacing: { before: 0, after: 60, line: LS, lineRule: "auto" },
      }),
      new Paragraph({
        children: [new TextRun({ text: "Delhi Public School, Agra", font: F, size: SZ_BODY, bold: true })],
        spacing: { before: 40, after: 20, line: LS, lineRule: "auto" },
      }),
      new Paragraph({
        children: [new TextRun({ text: "Secondary & Senior Secondary", font: F, size: SZ_BODY })],
        spacing: { before: 0, after: 80, line: LS, lineRule: "auto" },
      }),

      // ─── PROFILE SNAPSHOT ────────────────────────────────────────────────────
      sectionHeading("PROFILE SNAPSHOT"),
      spacer(60, 0),
      profileTable(),
      spacer(0, 40),
    ],
  }],
});

// ─── Write output ─────────────────────────────────────────────────────────────
const OUT = "/Users/atinsharma/job_search_vault/resumes_and_docs/master_cv/Atin_Sharma_Master_CV.docx";
Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync(OUT, buf);
  console.log("Written:", OUT);
}).catch(err => {
  console.error("Error:", err);
  process.exit(1);
});
