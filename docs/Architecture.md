# Lenny Growth Assistant

# Software Architecture Document

Version: 1.0

Author: Athish H

---

# 1. Overview

The Lenny Growth Assistant is a modular AI-powered conversational platform
designed to answer questions grounded in Lenny's Podcast transcripts,
generate long-form Ship30 style content, and create interactive artifacts.

The architecture emphasizes:

- Separation of concerns
- Scalability
- Maintainability
- Model agnostic inference
- Retrieval Augmented Generation (RAG)

The system follows a feature-first modular architecture combined with service
layer abstraction.

---

# 2. High-Level Architecture

                    Browser
                       │
                React Frontend
                       │
                REST API (FastAPI)
                       │
               Request Controller
                       │
                 Intent Router
                       │
      ┌────────────────┼────────────────┐
      │                │                │
  QA Service     Essay Service    Artifact Service
      │                │                │
      └────────────────┴────────────────┘
                       │
                  LLM Service
                       │
         Ollama            Claude
              │              │
              └──────┬───────┘
                     │
             Retrieval Service
                     │
               ChromaDB Vector DB
                     │
             Lenny Transcript Chunks

               PostgreSQL Database

---

# 3. Architectural Principles

## Single Responsibility

Every service has one responsibility.

Examples

Chat Service

- Receives chat requests
- Coordinates workflow

Retriever

- Searches transcript chunks

LLM Service

- Handles model communication

Session Service

- Stores conversations

Artifact Service

- Generates markdown and HTML

---

## Loose Coupling

Services communicate through interfaces.

Business logic never directly depends on a specific LLM provider.

---

## Extensibility

New models can be added by implementing
a new provider.

Example

OpenAIProvider

GeminiProvider

MistralProvider

No application logic changes.

---

# 4. Component Responsibilities

Frontend

- Chat Interface
- Session Sidebar
- Artifact Viewer
- Settings
- Markdown Rendering

Backend

- API
- Session Management
- Intent Routing
- Retrieval
- Prompt Construction
- Model Inference

Database

- Users
- Sessions
- Messages
- Artifacts

Vector Database

- Embeddings
- Similarity Search

---

# 5. Intent Routing

Incoming requests are classified into one of
three workflows.

Question Answering

↓

Retrieve documents

↓

Generate grounded answer

Essay Generation

↓

Generate Ship30 essay

Artifact Generation

↓

Generate Markdown or HTML

---

# 6. Retrieval Architecture

Transcript

↓

Chunking

↓

Embedding

↓

Vector Database

↓

Similarity Search

↓

Prompt Construction

↓

LLM

↓

Response

---

# 7. Model Abstraction

LLMService

↓

Provider Interface

↓

Ollama Provider

Claude Provider

Future providers can be integrated without
changing application logic.

---

# 8. Database Schema

Users

↓

Sessions

↓

Messages

↓

Artifacts

One User

↓

Many Sessions

One Session

↓

Many Messages

---

# 9. Deployment Architecture

React

↓

FastAPI

↓

PostgreSQL

↓

ChromaDB

↓

Ollama

Everything can run locally using Docker Compose.

---

# 10. Future Architecture

- Authentication
- Hybrid Search
- Multi-document RAG
- Streaming Responses
- Cloud Deployment