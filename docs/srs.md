# Software Requirements Specification (SRS)

**Project Name:** Lenny Growth Assistant
**Version:** 1.0
**Author:** Athish H
**Date:** July 31, 2026
**Reference Document:** Lenny Growth Assistant — PRD v1.0

---

## 1. Introduction

### 1.1 Purpose

This SRS translates the goals, features, and constraints defined in the Lenny Growth Assistant PRD into specific, verifiable software requirements. It defines what the system must do (functional requirements), how well it must do it (non-functional requirements), and the interfaces, data, and constraints that bound the implementation. It is implementation-agnostic where the PRD is implementation-agnostic, and becomes concrete only where necessary for engineering handoff to the Architecture Document.

### 1.2 Scope

Lenny Growth Assistant is a conversational, RAG-grounded workspace that lets users query Lenny's Podcast transcript corpus, receive cited answers, convert those answers into Ship30-style long-form content, and generate renderable Markdown/HTML/CSS artifacts — all within persistent, multi-session conversations, with a configurable local or cloud inference backend.

### 1.3 Intended Audience

- Engineering team (backend, frontend, ML/retrieval)
- Solo developer/author using this as a portfolio and interview artifact
- Future contributors extending the system per the Future Roadmap

### 1.4 Definitions, Acronyms, Abbreviations

| Term | Definition |
|------|------------|
| RAG | Retrieval-Augmented Generation — generating answers grounded in retrieved documents rather than model memory alone |
| LLM | Large Language Model |
| Ship30 | A concise, high-signal essay-writing style (short paragraphs, bold highlights, clear takeaway) |
| Artifact | A generated, renderable output (Markdown, HTML, or CSS) displayed inside the app |
| Chunk | A segment of a transcript stored with an embedding for retrieval |
| Ollama | Local LLM inference runtime |
| Session | A single persistent conversation thread with its own context |

### 1.5 References

- Lenny Growth Assistant PRD, v1.0, July 31, 2026

---

## 2. Overall Description

### 2.1 Product Perspective

The system is a new, standalone, single-tenant application (no auth, no multi-user collaboration in this version). It is composed of a conversational front end, a retrieval layer over a pre-embedded transcript corpus, a generation layer that can call either a local (Ollama) or cloud (Claude/OpenAI) model, and an artifact rendering surface.

### 2.2 Product Functions (Summary)

1. Grounded conversational Q&A over podcast transcripts
2. Persistent, multi-session chat management
3. Transcript retrieval with source citation
4. Ship30-style content generation from conversation context
5. Markdown/HTML/CSS artifact generation and in-app rendering
6. Runtime-configurable model backend (local vs. cloud)

### 2.3 User Classes and Characteristics

| User Class | Technical Level | Primary Use |
|---|---|---|
| Product Manager | Non-technical to semi-technical | Research, synthesis |
| Founder | Non-technical | Strategy research, content creation |
| Engineer | Technical | Architectural/product context lookup |
| Student | Non-technical | Learning via conversation |
| Content Creator | Non-technical | Turning discussions into essays |

All user classes share a single, unauthenticated instance of the product in this version (see Constraints, §2.6).

### 2.4 Operating Environment

- Runs as a web application (local or self-hosted deployment).
- Backend supports local inference via Ollama and cloud inference via Claude/OpenAI APIs.
- Vector store/index for transcript embeddings (embeddings assumed pre-generated per PRD Assumptions).

### 2.5 Design and Implementation Constraints

- No hardcoded API keys; secrets loaded via environment/config.
- Local inference must work through Ollama specifically.
- All generated HTML must be rendered through a sanitized/safe rendering path.
- Conversation history must survive application restarts (persisted storage, not in-memory only).

### 2.6 Assumptions and Dependencies

- Transcript corpus and embeddings exist and are accessible before retrieval features function.
- At least one valid LLM endpoint (local or cloud) is reachable at runtime.
- Users submit well-formed natural language prompts; the system is not required to handle adversarial input beyond basic sanitization.

---

## 3. Functional Requirements

Each requirement has an ID of the form `FR-<Feature>-<Number>` for traceability to the PRD feature list and future test cases.

### 3.1 Conversational Knowledge Assistant (PRD Feature 1)

| ID | Requirement |
|---|---|
| FR-CHAT-1 | The system shall accept natural language questions from the user related to product management, startups, growth, onboarding, pricing, retention, and adjacent topics. |
| FR-CHAT-2 | The system shall maintain multi-turn conversational context within a session, incorporating prior turns into subsequent retrieval and generation. |
| FR-CHAT-3 | The system shall generate responses grounded in retrieved transcript content rather than unaided model knowledge (see §3.3, Knowledge Retrieval). |
| FR-CHAT-4 | The system shall attach citations (episode/transcript identifiers and locations) to any claim derived from retrieved content. |
| FR-CHAT-5 | The system shall stream responses to the user interface incrementally rather than only returning a completed response. |

### 3.2 Persistent Chat Sessions (PRD Feature 2)

| ID | Requirement |
|---|---|
| FR-SESS-1 | The system shall allow the user to create a new, independent chat session. |
| FR-SESS-2 | The system shall allow the user to rename an existing chat session. |
| FR-SESS-3 | The system shall allow the user to delete a chat session, with confirmation before permanent deletion. |
| FR-SESS-4 | The system shall list all existing chat sessions in a conversation history view, ordered by most recent activity. |
| FR-SESS-5 | The system shall persist each session's full message history and metadata across application restarts. |
| FR-SESS-6 | Each session's retrieval and generation context shall be isolated from other sessions. |

### 3.3 Knowledge Retrieval (PRD Feature 3)

| ID | Requirement |
|---|---|
| FR-RET-1 | The system shall convert an incoming user query into an embedding and retrieve the top-N most relevant transcript chunks prior to generation. |
| FR-RET-2 | The system shall pass retrieved chunks to the generation layer as grounding context. |
| FR-RET-3 | The system shall expose the source (episode, guest, approximate location) of each retrieved chunk used in a response. |
| FR-RET-4 | The system shall support metadata filtering (e.g., by episode or guest) to narrow retrieval scope when specified. |
| FR-RET-5 | If no sufficiently relevant chunks are retrieved, the system shall inform the user that grounded information is unavailable rather than generating an ungrounded answer. |

### 3.4 Ship30 Content Generation (PRD Feature 4)

| ID | Requirement |
|---|---|
| FR-SHIP-1 | The system shall allow the user to request transformation of a conversation or answer into a Ship30-style essay. |
| FR-SHIP-2 | Generated essays shall include an introduction, logically ordered sections, bullet points where appropriate, bold highlights, and a clear closing takeaway. |
| FR-SHIP-3 | Generated essays shall retain traceability to the source transcript citations used in the underlying conversation. |
| FR-SHIP-4 | The system shall allow the user to export or copy the generated essay. |
| FR-SHIP-5 | (Future) The system shall support generation of LinkedIn-post-formatted variants of the same content. |

### 3.5 Artifact Generation (PRD Feature 5)

| ID | Requirement |
|---|---|
| FR-ART-1 | The system shall allow the user to request generation of a Markdown, HTML, or CSS artifact from the current conversation. |
| FR-ART-2 | The system shall render generated HTML/CSS artifacts inside the application in a live preview pane. |
| FR-ART-3 | The system shall render generated Markdown artifacts as formatted, readable output inside the application. |
| FR-ART-4 | The system shall sanitize generated HTML before rendering to prevent execution of unsafe scripts against the host application. |
| FR-ART-5 | The system shall allow the user to download or copy a generated artifact. |

### 3.6 Model Configuration (PRD Feature 6)

| ID | Requirement |
|---|---|
| FR-MODEL-1 | The system shall allow the user or operator to select between local (Ollama) and cloud (Claude/OpenAI) inference backends. |
| FR-MODEL-2 | Switching inference backends shall require configuration changes only, with no changes to application logic or user-facing behavior. |
| FR-MODEL-3 | The system shall surface the currently active model/backend to the user. |
| FR-MODEL-4 | If the configured backend is unreachable, the system shall return a clear error state rather than silently failing. |

---

## 4. Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-1 | Accuracy | Generated answers shall be grounded in retrieved evidence; ungrounded speculation shall be avoided or explicitly flagged. |
| NFR-2 | Performance | Retrieval shall return candidate chunks within a time budget that keeps perceived response start latency low (target: streaming begins within a few seconds under normal local conditions). |
| NFR-3 | Scalability | Retrieval performance shall degrade gracefully as transcript volume grows, via vector indexing and metadata filtering rather than linear scans. |
| NFR-4 | Security | No API keys or secrets shall be hardcoded or exposed to the client; all secrets are configuration-managed. |
| NFR-5 | Safety | All rendered HTML/CSS artifacts shall be sanitized to prevent script injection or unsafe execution within the host application. |
| NFR-6 | Reliability | Conversation and session data shall be durably persisted and recoverable after restart or crash. |
| NFR-7 | Maintainability | The inference layer shall be abstracted so new model providers can be added without modifying core application logic. |
| NFR-8 | Explainability | Every grounded response shall expose its supporting sources in a way visible and inspectable by the user. |
| NFR-9 | Usability | The interface shall resemble familiar AI productivity tools (chat-first, low learning curve) rather than requiring specialized training. |

---

## 5. External Interface Requirements

### 5.1 User Interface

- Chat interface with message input, streaming response display, and inline citations.
- Session sidebar/history with create, rename, delete actions.
- Artifact preview pane supporting rendered Markdown and HTML/CSS.
- Model/backend selector or status indicator.

### 5.2 Software Interfaces

- **Retrieval layer:** Vector store/index API for similarity search over transcript embeddings.
- **Generation layer:** Local inference via Ollama API; cloud inference via Claude and/or OpenAI APIs, behind a common internal interface.
- **Persistence layer:** Local or embedded database (or file-backed store) for sessions, messages, and metadata.

### 5.3 Communications Interfaces

- HTTP(S) between frontend and backend.
- HTTP(S) or local socket calls from backend to Ollama and/or cloud LLM providers.

---

## 6. Data Requirements

| Entity | Key Attributes |
|---|---|
| Session | id, title, created_at, updated_at, message_history |
| Message | id, session_id, role (user/assistant), content, citations, timestamp |
| Transcript Chunk | id, episode_id, guest, text, embedding_vector, location/timestamp metadata |
| Artifact | id, session_id, type (markdown/html/css), content, created_at |
| Model Config | active_backend, endpoint, model_name |

Transcript chunks and their embeddings are assumed pre-generated and loaded into the retrieval store (per PRD §11, Assumptions); this SRS does not require the system to perform initial ingestion/embedding generation unless added to a later scope.

---

## 7. Traceability to PRD

| SRS Section | PRD Reference |
|---|---|
| §3.1 Conversational Knowledge Assistant | PRD Feature 1 |
| §3.2 Persistent Chat Sessions | PRD Feature 2 |
| §3.3 Knowledge Retrieval | PRD Feature 3 |
| §3.4 Ship30 Content Generation | PRD Feature 4 |
| §3.5 Artifact Generation | PRD Feature 5 |
| §3.6 Model Configuration | PRD Feature 6 |
| §4 Non-Functional Requirements | PRD §13 Constraints, §9 Success Metrics |
| §2.6 Assumptions | PRD §11 Assumptions |

---

## 8. Out of Scope (Explicit Exclusions)

Per PRD §11 (Functional Scope — Excluded), the following are explicitly out of scope for this SRS and MVP:

- User authentication and authorization
- Team/multi-user collaboration
- Voice conversations
- Image generation
- Live internet search
- Fine-tuning of language models
- Mobile applications

---

## 9. Open Items for Architecture Document

The following are intentionally left unspecified here and deferred to the Architecture Document, per the PRD's implementation-agnostic approach:

- Choice of vector database/index technology
- Specific persistence technology (SQL, embedded DB, file-based)
- Chunking strategy and chunk size for transcripts
- Retrieval ranking algorithm (pure vector vs. hybrid)
- Frontend framework and rendering sandbox mechanism for HTML artifacts
