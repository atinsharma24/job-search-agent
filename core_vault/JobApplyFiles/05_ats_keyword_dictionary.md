# ATS KEYWORD DICTIONARY
### Atin Sharma — One Business-Result Sentence Per Technology
> Usage: Copy the relevant sentence into "Skills" fields, cover letters, or LinkedIn sections.  
> Every sentence ties the technology to a measurable or operational outcome.

---

## LANGUAGES

**JavaScript**
Used JavaScript as the primary runtime language to build the full MERN stack at OpenBiz, shipping two AI-powered products to 1,000+ active Indian SMB users.

**TypeScript**
Applied TypeScript throughout the OpenBiz platform stack — frontend, backend, and ingestion pipelines — to enforce type safety and eliminate a class of runtime errors across a multi-product codebase.

**Python**
Used Python (Django) to build the DocGPT backend, orchestrating a production RAG pipeline from PDF ingestion through ChromaDB vector retrieval to GPT-4o-mini generation.

**SQL**
Wrote and optimized PostgreSQL queries at OpenBiz to resolve N+1 patterns and introduce composite indexes, achieving a 40% reduction in API latency across the platform.

**Java**
Applied core Java data structures and algorithms across 347+ LeetCode problems as preparation for systems-level engineering roles and technical screening rounds.

---

## FRONTEND

**React.js (v18 / v19)**
Built production React 19 frontends at OpenBiz including a split-screen Diff View for AI content review, enabling editorial teams to compare and approve AI-rewritten content before publishing.

**Next.js**
Used Next.js 14 as the application framework for Nimbus, implementing server components, API routes, and streaming UI for a production RAG document workspace.

**React Native**
Applied React Native as a cross-platform mobile development skill to extend product surfaces beyond web for SMB-facing applications.

**Redux Toolkit**
Managed complex client-side application state with Redux Toolkit on the OpenBiz platform, ensuring predictable state transitions across multi-step user workflows.

**TailwindCSS**
Used TailwindCSS to ship consistent, responsive UI at high velocity across the OpenBiz platform — enabling a three-person team to maintain design coherence without a dedicated frontend designer.

---

## BACKEND

**Node.js**
Built the VyaparGPT WhatsApp AI assistant backend in Node.js, handling the full message lifecycle from webhook ingestion to LLM dispatch and response delivery for 1,000+ active users.

**Express.js**
Used Express.js to expose REST API endpoints for the OpenBiz platform, including webhook handlers for Razorpay billing events with HMAC signature validation.

**NestJS**
Applied NestJS as a structured backend framework for services requiring modular architecture, dependency injection, and enforced separation of concerns.

**Django**
Built the DocGPT REST backend in Django to orchestrate vector retrieval, prompt assembly, and GPT-4o-mini generation — delivering a fully self-contained RAG pipeline in a single Python service.

**Laravel**
Used Laravel as the API backbone for the Automated Content Intelligence Pipeline, coordinating Puppeteer scraping, AI rewriting, and React frontend communication in a microservices deployment.

---

## DATABASES

**PostgreSQL (Supabase)**
Optimized a multi-tenant PostgreSQL schema on Supabase at OpenBiz, resolving N+1 query patterns with JOIN rewrites and composite indexes to cut API latency by 40% at 1,000+ user scale.

**MongoDB**
Used MongoDB for flexible, schema-less document storage in MERN stack services requiring dynamic data models without rigid relational constraints.

**pgvector**
Implemented pgvector in Nimbus to store and query document embeddings directly within PostgreSQL, enabling cosine similarity search without a separate vector database process.

**ChromaDB**
Used ChromaDB as the vector store in DocGPT, storing sentence-transformer embeddings for PDF chunks and enabling k-nearest-neighbor semantic retrieval for RAG generation.

**AWS DynamoDB**
Used DynamoDB for high-throughput, low-latency key-value storage in AWS-integrated service pipelines where relational constraints were unnecessary.

---

## AI / LLM

**OpenAI API**
Integrated the OpenAI API as the primary LLM provider across VyaparGPT and Nimbus, handling conversational generation, document Q&A, and provider-fallback scenarios.

**Google Gemini API**
Used the Gemini API at OpenBiz for LLM-powered document verification — extracting structured fields from photographs of SMB documents (GST certificates, invoices, vendor agreements) sent via WhatsApp.

**Groq API**
Integrated Groq API in Nimbus as the primary streaming inference provider, leveraging its low-latency response times to deliver real-time document Q&A with visible token streaming.

**RAG Pipelines**
Designed and shipped two production RAG pipelines (Nimbus with pgvector, DocGPT with ChromaDB) — covering ingestion, chunking, embedding, vector retrieval, prompt construction, and streaming generation.

**pgvector**
(See Databases section — cross-listed as both infrastructure and AI tooling given its role as the vector retrieval engine in Nimbus.)

**ChromaDB**
(See Databases section — cross-listed as both infrastructure and AI tooling given its role as the vector store in DocGPT's RAG pipeline.)

**Sentence Transformers (all-MiniLM-L6-v2)**
Used the all-MiniLM-L6-v2 Sentence Transformer model in DocGPT to generate 384-dimensional local embeddings from PDF chunks — enabling offline, cost-free semantic search without API calls.

**Vercel AI SDK**
Leveraged the Vercel AI SDK to implement streaming LLM responses in Next.js applications, reducing boilerplate for server-sent event handling and multi-provider integration.

**LangChain.js**
Used LangChain.js to structure multi-step LLM chain logic and document processing workflows in JavaScript-based AI pipelines.

**Prompt Engineering**
Designed structured prompts for document extraction (Gemini), content rewriting (Gemini + OpenAI), and conversational Q&A (VyaparGPT), tuning for factual accuracy, output format consistency, and token efficiency.

**PyPDF2**
Used PyPDF2 in the DocGPT ingestion pipeline to extract text from uploaded PDFs and apply overlap-based chunking strategies before embedding and vector storage.

**Anthropic Claude (Claude 3.5 Sonnet)**
Used Claude 3.5 Sonnet as the primary orchestration model in the Autonomous Web Agent — translating structured local context into DOM-level browser interactions via MCP for multi-step web workflow automation.

**MCP (Model Context Protocol)**
Integrated MCP (Model Context Protocol) in the Autonomous Web Agent to give Claude structured, tool-level access to browser state, enabling reliable DOM-level interaction across dynamic web forms.

---

## DEVOPS / CLOUD

**Docker**
Deployed the Automated Content Intelligence Pipeline as Docker microservices — isolating the scraper, AI rewriter, and API services into independently scalable, self-healing containers.

**GitHub Actions**
Built and owned the OpenBiz CI/CD pipeline using GitHub Actions — automated test runs on PRs, environment-consistent staging deploys, and production gating — reducing deployment cycle time by 30%.

**Vercel**
Used Vercel for all frontend deployments at OpenBiz, enabling branch preview environments and zero-downtime production deploys integrated with the GitHub Actions CI pipeline.

**AWS S3**
Used AWS S3 for scalable object storage of user-uploaded documents and media assets in the OpenBiz platform, integrated with pre-signed URL generation for secure client-side access.

**AWS SNS**
Used AWS SNS to publish asynchronous event notifications for cross-service communication in AWS-integrated pipeline architectures.

---

## TOOLS

**Git**
Used Git for version control across all professional and open-source projects, including the branch protection and PR review workflow that eliminated direct-to-main incidents at OpenBiz.

**Postman**
Used Postman to design, document, and test all REST API endpoints at OpenBiz — including webhook simulation for Razorpay payment events during pre-production validation.

**Socket.IO**
Engineered real-time bidirectional chat infrastructure using Socket.IO at OpenBiz, enabling live messaging between SMB users and business owners within the platform.

**Razorpay SDK**
Integrated the Razorpay SDK at OpenBiz to handle the full subscription billing lifecycle — webhook validation, payment state reconciliation, retry flows, and idempotent event processing.

**VideoSDK**
Integrated VideoSDK to add in-app video conferencing to the OpenBiz platform, enabling real-time consultations between SMB operators and service providers.

**Puppeteer**
Used Puppeteer to bypass client-side rendering on JavaScript-heavy target sites in the Content Intelligence Pipeline, enabling reliable scraping of SPA content that standard HTTP clients could not access.

**BrowserOS / OpenClaw**
Used BrowserOS (via MCP) and OpenClaw in the Autonomous Web Agent project to provide browser-level tool access to an LLM orchestration layer, enabling programmatic interaction with web UIs without brittle CSS selectors.

---

> **ATS Usage Notes:**  
> — For skills fields with character limits: use only the bolded technology name + first clause of the sentence  
> — For cover letters: pick 3–4 sentences matching the job description's required stack  
> — For LinkedIn "About" skills endorsement descriptions: use the sentence verbatim  
> — Technologies appearing in both Databases and AI/LLM (pgvector, ChromaDB): use the AI/LLM sentence for AI-focused roles, the Databases sentence for backend/infra roles
