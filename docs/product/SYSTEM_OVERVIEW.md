---
id: SYSTEM_OVERVIEW
doc_mode: REFERENCE
status: CANONICAL
---

# HB Track — System Overview

## What it is
HB Track is a handball club management system covering athlete registration, training planning, competition tracking, match analytics, and wellness monitoring.

## Who it serves
- **Dirigentes** (club directors): full administrative control
- **Coordenadores** (coordinators): operational oversight
- **Treinadores** (coaches): training and match management
- **Preparadores fisicos** (fitness coaches): wellness and conditioning
- **Atletas** (athletes): self-service profile and wellness

## Modules

| Module | Scope |
|--------|-------|
| Auth | JWT login, refresh tokens, RBAC enforcement |
| Person/Athlete | Identity root, contacts, documents, media, athlete state machine |
| Teams | Team CRUD, roster management, registrations |
| Training | Sessions (lifecycle: draft → readonly), cycles, microcycles, exercises (drag-drop) |
| Competitions | Competitions, seasons, phases, standings |
| Matches | Real-time events, roster, periods, possessions |
| Wellness | Pre/post-training questionnaires, reminders, rankings |
| Analytics | Dashboards, reports, training alerts (AI-assisted) |
| Audit | Audit logs, data access logs (LGPD), data retention |

## Tech stack
- **Backend:** FastAPI + SQLAlchemy (async) + PostgreSQL + Alembic + Celery/Redis
- **Frontend:** Next.js 16 (App Router) + React 19 + TypeScript + TailwindCSS
- **Integrations:** Cloudinary (media), Google Gemini (PDF parsing)

## SSOT artifacts
Source of truth is managed via `docs/_canon/HB_TRACK_PROFILE.yaml`.
Generated artifacts live in `docs/_generated/_core/` (read-only, derived).

## Gates
Run `pwsh scripts/checks/check_hb_profile.ps1` for L0/L1 validation.
Run `pwsh scripts/checks/check_ci_gates_local.ps1` for full local CI gates.
