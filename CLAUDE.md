# Nur Scents Customer Success FTE
## Hackathon 5 — Panaversity/AgentFactory.dev

## IMPORTANT — READ FIRST
Before doing ANYTHING:
1. Read this entire file
2. Read PROGRESS.md
3. Find current step
4. Continue from there
5. Never repeat completed steps

## Business Context
- Business: Nur Scents (real perfume brand)
- Owner: Ammar — Karachi, Pakistan
- Problem: Manual WhatsApp order management
- Goal: 24/7 AI Customer Success Agent

## What System Does
- Answers product queries 24/7
- Takes orders on WhatsApp
- Tracks order status
- Handles Email + Web Form
- Escalates to Ammar when needed
- Generates daily reports

## Final Tech Stack (LOCKED — NEVER CHANGE)
- Agent:     PydanticAI + Gemini 2.0 Flash
- Backend:   FastAPI (Python)
- Database:  PostgreSQL + pgvector
             (ankane/pgvector Docker image)
- Streaming: Kafka (Local Docker)
- WhatsApp:  Twilio Sandbox
- Frontend:  Next.js 14 + Tailwind CSS
- Deploy:    k3d (lightweight Kubernetes)
- Email:     Gmail API

## Project Structure
## Architecture Rules
- All prices in PKR
- WhatsApp: Roman Urdu responses
- Email: Formal English responses
- Web: Semi-formal mixed responses
- Kafka handles ALL channel events
- Owner (Ammar) identified by phone number
- Escalate if unresolved after 1 reply
- API keys in .env ONLY — never in code

## Code Rules
- Production quality only
- Error handling on EVERY function
- Real Nur Scents data — no placeholders
- Pakistani context throughout
- Type hints on all Python functions
- Comments explaining logic

## Step Complete Definition
- Code written ✅
- Tested with real input ✅
- Working correctly ✅
- PROGRESS.md updated ✅

## Scoring Priority
1. Web Support Form (10 pts) — MUST
2. Agent Implementation (10 pts) — MUST
3. Channel Integrations (10 pts) — MUST
4. Incubation Quality (10 pts) — MUST
5. Database + Kafka (5 pts)
6. Kubernetes (5 pts)
7. Cross Channel (10 pts)
8. 24/7 Ready (10 pts)
9. Customer UX (10 pts)
10. Documentation (5 pts)
