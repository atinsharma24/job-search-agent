# Resume Templates - Usage Guide

Created: 2026-04-07

## Available Templates

### 1. **KYC-Identity-Verification.md**
**Target Companies:** Signzy, Bureau, Digio

**Focus Areas:**
- AI Document Verification & Data Extraction
- Real-time API & Webhook Processing
- PostgreSQL Query Optimization
- RAG Pipelines & Vector Search
- WhatsApp Automation
- Payment Gateway Integration & Compliance Workflows

**Key Highlights:**
- Document verification module (Gemini API)
- 40% API latency reduction
- 1,000+ active users processed
- Real-time data pipelines

---

### 2. **Legal-Tech-Compliance.md**
**Target Companies:** RegisterKaro, Leegality

**Focus Areas:**
- AI-Powered Document Automation
- Legal-Tech & Compliance Workflow Optimization
- RAG Pipelines & Semantic Search
- WhatsApp Automation for SMBs
- PostgreSQL Optimization
- Subscription Management

**Key Highlights:**
- Document automation for compliance (invoices, GST, licenses)
- RAG system for legal research and document analysis
- WhatsApp-native AI assistant for business automation
- Compliance-friendly architecture

---

### 3. **Conversational-AI.md**
**Target Companies:** Sarvam AI, Yellow.ai

**Focus Areas:**
- Conversational AI & WhatsApp Automation
- LLM Integration (OpenAI, Gemini, Groq) with Provider Fallback
- RAG Pipelines & Vector Search
- Real-Time Chat Infrastructure
- Prompt Engineering & LLM Response Optimization

**Key Highlights:**
- VyaparGPT: WhatsApp-native LLM assistant
- Provider-fallback logic (OpenAI ↔ Gemini)
- Conversation context per session
- Streaming LLM responses (Groq API)
- Real-time bidirectional chat (Socket.IO)

---

## Customization Notes

Each template is structured to:
1. **Lead with relevant experience** for the target sector
2. **Reorder projects** to put most relevant ones first
3. **Emphasize specific technical skills** matching the company's stack
4. **Use domain-specific language** (KYC, compliance, conversational AI)

---

## Next Steps

1. Pick a target company
2. Use the corresponding template
3. Customize the profile summary if needed for specific job description
4. Export to PDF using a clean LaTeX or Markdown → PDF tool

---

## Export Commands (macOS)

### Option 1: Pandoc (if installed)
```bash
pandoc KYC-Identity-Verification.md -o KYC-Identity-Verification.pdf --pdf-engine=xelatex
```

### Option 2: VS Code Markdown PDF Extension
1. Open template in VS Code
2. Right-click → "Markdown PDF: Export (pdf)"

### Option 3: Online Converter
- Use https://markdown-to-pdf.com or similar
- Upload `.md` file → download PDF

---

## Files
- `KYC-Identity-Verification.md`
- `Legal-Tech-Compliance.md`
- `Conversational-AI.md`
