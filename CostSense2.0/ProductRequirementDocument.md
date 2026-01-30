🧠 PHASED MASTER BUILD PROMPT
CostSense AI – Sequential End-to-End Implementation
ROLE

You are a senior full-stack platform engineer tasked with building CostSense AI, a production-grade, AI-assisted multi-cloud cost intelligence platform.

You must build the system in phases, sequentially, within a single implementation effort.

Do not skip phases.
Do not invent features.
If trade-offs exist, choose safety and explainability.

PHASE 0 – FOUNDATIONAL RULES (READ ONCE)

This system is NOT autonomous

AI is decision-support only

All AI inference is local

Human confirmation is required for all actions

No cloud write permissions

No external LLM APIs

Use LLaMA 3.1 8B Instruct via Ollama

Target deployment: Azure Container Apps

PHASE 1 – REPOSITORY & INFRA SCAFFOLDING
Objectives

Create a clean, professional, production-ready monorepo.

Tasks

Create monorepo structure:

costense-ai/
  backend/
  frontend/
  infra/
  docker-compose.yml
  README.md


Backend:

FastAPI project

Poetry or pip + venv

Config management via env vars

Frontend:

React 18 + TypeScript + Vite

Infra:

Dockerfiles for:

backend

frontend

ollama

docker-compose to run:

backend

ollama

postgres

redis

README:

Local run instructions

Ollama model pull instructions

Exit Criteria

docker-compose up runs without errors

Backend /health endpoint works

Frontend loads

PHASE 2 – CORE BACKEND SERVICES
Objectives

Establish a stable backend foundation.

Tasks

FastAPI setup:

REST endpoints

WebSocket endpoint

Structured logging

PostgreSQL integration:

SQLAlchemy models

Alembic migrations

Redis integration:

Cache abstraction

Session store

Basic auth placeholder:

Token-based middleware (no real auth)

Exit Criteria

DB migrations apply cleanly

WebSocket connection works

Backend persists and retrieves data

PHASE 3 – CLOUD COST ADAPTER LAYER
Objectives

Create a cloud-agnostic cost interface.

Tasks

Define abstract interface:

class CloudCostProvider:
    def fetch_costs()
    def fetch_utilization()
    def list_resources()


Implement:

AWS adapter (real or mocked)

Azure adapter (stub)

GCP adapter (stub)

Normalize cost schema across providers

Add adapter registry & routing

Exit Criteria

Same API call works for all providers

Normalized schema returned

PHASE 4 – AI RUNTIME & LLM CLIENT
Objectives

Integrate local AI safely and deterministically.

Tasks

Ollama client wrapper:

Model: llama3.1:8b-instruct

Retry logic

Timeout handling

Strict JSON schema enforcement

System prompts:

Summarization

Explanation

Intent detection

Function calling framework:

Tool registry

Validation layer

Fallback handling

Exit Criteria

LLM responds reliably

Invalid outputs are rejected and retried

No free-form responses allowed

PHASE 5 – AGENT ORCHESTRATION
Objectives

Implement AI-assisted reasoning without autonomy.

Tasks

Implement agents:

Cost Analysis Agent

Optimization Agent

Explanation Agent

Orchestrator:

Task routing

Parallel execution

Result aggregation

LLM used only for:

Summaries

Explanations

Tool selection

Exit Criteria

Agents work independently

Orchestrator aggregates results

No agent performs direct actions

PHASE 6 – ITSM (SERVICENOW) INTEGRATION
Objectives

Enable operational follow-through.

Tasks

ServiceNow REST client:

Incident creation

Authentication abstraction

Ticket payload builder:

Summary

Evidence

Suggested actions

Confirmation workflow:

Preview before creation

Ticket persistence

Exit Criteria

Incident created successfully

Ticket ID and URL returned

Stored in database

PHASE 7 – CHATBOT ENGINE
Objectives

Provide a safe, contextual assistant.

Tasks

Chat API:

Intent classification

Context injection

Tool routing:

Cost queries

Explanation

Ticket creation (confirmation required)

Session memory via Redis

Rate limiting

Exit Criteria

Chat responds correctly

No unsafe actions

Context-aware answers

PHASE 8 – FRONTEND IMPLEMENTATION
Objectives

Deliver a usable, professional UI.

Tasks

Dashboards:

Cost overview

Service breakdown

Recommendations

Streaming updates via WebSockets

Investigation history view

ITSM ticket links

Floating chatbot widget

Exit Criteria

Live updates work

Charts render correctly

Chatbot usable across pages

PHASE 9 – OBSERVABILITY & SAFETY
Objectives

Ensure explainability and auditability.

Tasks

Log:

Prompts

LLM outputs

Function calls

Tickets

Audit tables

Error handling & retries

Metrics (latency, failures)

Exit Criteria

Full traceability

Clear logs

No silent failures

PHASE 10 – HARDENING & DOCUMENTATION
Objectives

Prepare for demo, review, and deployment.

Tasks

Validate guardrails

Remove unused code

Add seed data

Finalize README:

Architecture

Security model

Demo flow

Exit Criteria

System is demo-ready

No TODOs left

Clear documentation

FINAL INSTRUCTION TO THE AGENT

Build CostSense AI by completing all phases sequentially.
Do not skip phases.
Choose safety over autonomy.
Choose clarity over cleverness.
The final system must be explainable, auditable, and production-realistic.