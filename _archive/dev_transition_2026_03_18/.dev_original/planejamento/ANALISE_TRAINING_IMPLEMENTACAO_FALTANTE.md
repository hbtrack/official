# ANÁLISE: Módulo Training — O que Falta Implementar

**Data:** 2026-03-17  
**Status Atual:** Contract-Ready (100% das surfaces documentadas)  
**Implementação Real:** ~0% (apenas migration DB criada) 

---

## 📋 Resumo Executivo

O módulo **training** tem **contratos completos** (OpenAPI, AsyncAPI, UI, Schemas) mas **ZERO implementação de código** backend/frontend.

| Layer | Status | Completude |
|-------|--------|-----------|
| **Contratos** (OpenAPI, AsyncAPI, Schemas, UI, Arch Decisions) | ✅ Complete | 100% |
| **Database** (Alembic migrations) | ✅ Ready | 100% |
| **Backend Code** (FastAPI handlers, services, repositories) | ❌ Missing | 0% |
| **Frontend Code** (React/TS components, pages) | ❌ Missing | 0% |
| **Integration Tests** | ❌ Missing | 0% |
| **Feature Flags** | ❌ Missing | 0% |

---

## 🏗️ Arquitetura Esperada (por contrato)

```
┌─────────────────────────────────────┐
│        FRONTEND (React/TS)          │
│  ┌──────────────────────────────┐   │
│  │ 3 UI Flows                   │   │
│  │ - Session Planning           │   │
│  │ - Athlete Check-in           │   │
│  │ - Coach Review               │   │
│  └──────────────────────────────┘   │
└──────────────┬──────────────────────┘
               │ HTTP/REST
┌──────────────▼──────────────────────┐
│      BACKEND (FastAPI/Python)       │
│  ┌──────────────────────────────┐   │
│  │ 27 API endpoints             │   │
│  │ (CRUD para 12 entidades)     │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │ 27 Event handlers            │   │
│  │ (AsyncAPI consumers)         │   │
│  └──────────────────────────────┘   │
│  ┌──────────────────────────────┐   │
│  │ Business Logic               │   │
│  │ (FSM, RBAC, validations)     │   │
│  └──────────────────────────────┘   │
└──────────────┬──────────────────────┘
               │ AMQP/Events
┌──────────────▼──────────────────────┐
│    ASYNC MESSAGE BROKER (AMQP)      │
│            27 Topics                 │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  DATABASE (PostgreSQL 16)           │
│  ┌──────────────────────────────┐   │
│  │ 6 tables + 5 ENUMs           │   │
│  │ (created by migration v1)    │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## ⚙️ BACKEND — O que Falta Implementar

### 1. Estrutura de Diretórios (23 classes + 45 funções estimadas)

```
src/modules/training/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── training_session.py        ← ORM modelo (SQLAlchemy)
│   ├── session_block.py
│   ├── session_objective.py
│   ├── execution_record.py
│   ├── feedback_thread.py
│   ├── attention_queue_item.py
│   ├── training_attendance.py
│   ├── wellness_assessment.py
│   ├── readiness_assessment.py
│   ├── athlete_ineligibility.py
│   ├── training_recommendation.py
│   └── continuity_snapshot.py
├── schemas/
│   ├── __init__.py
│   ├── training_session.py        ← Pydantic validators
│   ├── session_block.py
│   ├── objectives.py
│   ├── feedback.py
│   ├── wellness.py
│   └── readiness.py
├── repositories/
│   ├── __init__.py
│   ├── training_session_repo.py   ← Data access layer
│   ├── session_block_repo.py
│   ├── objectives_repo.py
│   ├── feedback_repo.py
│   └── attention_queue_repo.py
├── services/
│   ├── __init__.py
│   ├── training_session_service.py ← Business logic
│   ├── wellness_service.py
│   ├── readiness_service.py
│   ├── feedback_service.py
│   ├── recommendation_service.py
│   ├── attention_queue_service.py
│   └── eligibility_service.py
├── events/
│   ├── __init__.py
│   ├── publishers.py              ← Event publishing (27 topics)
│   └── handlers.py                ← Event consumers (async processing)
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── sessions.py            ← POST/GET/PATCH /sessions (12 endpoints)
│   │   ├── objectives.py          ← Objectives CRUD (8 endpoints)
│   │   ├── feedback.py            ← Feedback threads (6 endpoints)
│   │   ├── wellness.py            ← Check-ins (4 endpoints)
│   │   ├── attention.py           ← Attention queue (5 endpoints)
│   │   └── readiness.py           ← Readiness scores (2 endpoints)
│   └── dependencies.py             ← Dependency injection
├── middlewares/
│   ├── __init__.py
│   ├── rbac.py                    ← Role-based access control
│   └── soft_delete.py             ← Soft-delete filter
├── validations/
│   ├── __init__.py
│   ├── fsm_validator.py           ← State machine rules
│   ├── focus_validator.py         ← Focus distribution (sum ≤ 100%)
│   ├── eligibility_rules.py       ← Ineligibility logic
│   └── business_rules.py          ← RUL-TRAINING-001 through RUL-TRAINING-008
└── utils/
    ├── __init__.py
    ├── readiness_calculator.py    ← Readiness score algorithm
    └── event_publishers.py        ← Outbox pattern
```

---

### 2. Endpoints a Implementar (27 total)

**Por CRUD:**

| Domínio | GET | POST | PATCH | DELETE | Total |
|---------|-----|------|-------|--------|-------|
| Sessions | 2 | 1 | 3 | 1 | 7 |
| Objectives | 1 | 1 | 1 | 1 | 4 |
| Session Blocks | 1 | 1 | 1 | 1 | 4 |
| Feedback Threads | 1 | 1 | 1 | 0 | 3 |
| Wellness Check-in | 1 | 1 | 0 | 0 | 2 |
| Attention Queue | 1 | 0 | 1 | 0 | 2 |
| Readiness | 1 | 0 | 0 | 0 | 1 |
| **TOTAL** | **8** | **6** | **7** | **3** | **27** |

**Details por Entidade:**

```python
# Sessions (7 endpoints)
GET    /api/v1/training/sessions
POST   /api/v1/training/sessions
GET    /api/v1/training/sessions/{id}
PATCH  /api/v1/training/sessions/{id}
PATCH  /api/v1/training/sessions/{id}/status  # state transition
PATCH  /api/v1/training/sessions/{id}/publish
DELETE /api/v1/training/sessions/{id}  # soft-delete

# Objectives (4 endpoints)
GET    /api/v1/training/sessions/{session_id}/objectives
POST   /api/v1/training/sessions/{session_id}/objectives
PATCH  /api/v1/training/objectives/{id}
DELETE /api/v1/training/objectives/{id}

# Session Blocks (4 endpoints)
GET    /api/v1/training/sessions/{session_id}/blocks
POST   /api/v1/training/sessions/{session_id}/blocks
PATCH  /api/v1/training/blocks/{id}
DELETE /api/v1/training/blocks/{id}

# Feedback Threads (3 endpoints)
GET    /api/v1/training/feedback-threads
POST   /api/v1/training/sessions/{session_id}/feedback
PATCH  /api/v1/training/feedback-threads/{id}/status

# Wellness Check-in (2 endpoints)
POST   /api/v1/training/sessions/{session_id}/check-in
GET    /api/v1/training/sessions/{session_id}/wellness

# Attention Queue (2 endpoints)
GET    /api/v1/training/attention-queue
PATCH  /api/v1/training/attention-queue/{item_id}/status

# Readiness (1 endpoint)
GET    /api/v1/training/readiness/{athlete_id}
```

---

### 3. Serviços Críticos (8 classes, ~150 métodos)

#### TrainingSessionService
```python
class TrainingSessionService:
    # Session Lifecycle
    create_session(team_id, coach_id, **data) → Session
    publish_session(session_id, coach_id) → bool
    start_session(session_id) → bool
    complete_session(session_id) → bool
    cancel_session(session_id, reason) → bool
    archive_session(session_id) → bool  # cronJob após 60 dias
    
    # State Transitions (FSM)
    validate_state_transition(current_state, target_state) → bool
    
    # Publishing Events
    emit_session_created(session)
    emit_session_published(session)
    emit_session_started(session)
    emit_session_completed(session)
    emit_session_cancelled(session)
    emit_session_archived(session)
    
    # Soft-delete
    soft_delete_session(session_id, coach_id)
```

#### WellnessService
```python
class WellnessService:
    # Check-in
    record_wellness_assessment(session_id, athlete_id, **data) → WellnessAssessment
    get_athlete_wellness_history(athlete_id, days=7) → List[WellnessAssessment]
    
    # Readiness calculation
    calculate_readiness_score(sleep, mood, resting_hr, fatigue) → int [0-100]
    categorize_readiness(score) → str  # low, moderate, high
    
    # Publishing Events
    emit_readiness_assessed(readiness)
    emit_wellness_alert_if_needed(readiness)
```

#### FeedbackService
```python
class FeedbackService:
    # Threads
    create_feedback_thread(session_id, coach_id, athlete_id, context) → FeedbackThread
    add_message_to_thread(thread_id, sender_role, message) → bool
    close_thread(thread_id, outcome) → bool
    
    # Publishing Events
    emit_feedback_thread_created(thread)
    emit_feedback_thread_closed(thread)
```

#### RecommendationService
```python
class RecommendationService:
    # Coach-in-Loop
    accept_recommendation(rec_id, coach_id) → bool
    dismiss_recommendation(rec_id, coach_id, reason) → bool
    
    # Publishing Events
    emit_recommendation_accepted(rec)
    emit_recommendation_dismissed(rec)
```

#### AttentionQueueService
```python
class AttentionQueueService:
    # Queue Management
    create_attention_item(session_id, item_type, athlete_id) → AttentionQueueItem
    resolve_item(item_id, status, evidence) → bool
    get_active_queue(team_id) → List[AttentionQueueItem]
    
    # Publishing Events
    emit_attention_item_created(item)
    emit_attention_item_resolved(item)
```

#### EligibilityService
```python
class EligibilityService:
    # Ineligibility Management
    declare_ineligibility(athlete_id, reason, period) → bool
    check_athlete_eligible(athlete_id) → bool
    auto_adjust_prescription_if_ineligible(athlete_id) → bool
    
    # Publishing Events
    emit_athlete_ineligible(athlete_id)
    emit_prescription_adjusted(athlete_id)
```

#### ExecutionRecordService
```python
class ExecutionRecordService:
    # Append-only records
    record_execution(session_id, type, context_id, metadata) → ExecutionRecord
    get_execution_history(session_id) → List[ExecutionRecord]
    
    # Publishing Event
    emit_execution_recorded(record)
```

#### ContinuityService
```python
class ContinuityService:
    # Snapshots for periodization
    create_snapshot(athlete_id, snapshot_type, data) → ContinuitySnapshot
    load_snapshot_for_period(athlete_id, period) → ContinuitySnapshot
```

---

### 4. Validações & Business Rules (8 validators)

```python
# validations/fsm_validator.py
VALID_TRANSITIONS = {
    "DRAFT": ["SCHEDULED"],
    "SCHEDULED": ["IN_PROGRESS", "CANCELLED"],
    "IN_PROGRESS": ["COMPLETED", "CANCELLED"],
    "COMPLETED": ["ARCHIVED"],
    "CANCELLED": ["ARCHIVED"],
    "ARCHIVED": []  # terminal
}

# validations/focus_validator.py
def validate_focus_distribution(distribution: dict[str, float]) -> bool:
    """Sum of 7 dimensions must be <= 100%"""
    total = sum(distribution.values())
    return 0 <= total <= 100.0

# validations/business_rules.py
def rule_01_only_coach_changes_state() → Validator
def rule_02_sessions_sequential_transitions() → Validator
def rule_03_athlete_privacy() → Validator
def rule_04_audit_trail_immutability() → Validator
def rule_05_soft_delete_invisibility() → Validator
def rule_06_focus_sum_balance() → Validator
def rule_07_execution_append_only() → Validator
def rule_08_coach_intervention_documentation() → Validator
```

---

### 5. Event Publishing (27 events × handlers)

**Publishers (in services):**
```python
from src.events import publish_event

# Exemplo em TrainingSessionService.publish_session():
await publish_event("training.session.published", {
    "sessionId": session.id,
    "teamId": session.team_id,
    "scheduledStart": session.scheduled_at.isoformat(),
    "occurredAt": datetime.utcnow().isoformat(),
    "traceId": context.trace_id,
    "requestId": context.request_id
})
```

**Handlers (event subscribers):**
```python
# events/handlers.py
@event_handler("training.session.published")
async def on_training_session_published(payload):
    # → notify athletes
    # → open wellness check-in window
    # → signal analytics to start collecting signals

@event_handler("training.session.completed")
async def on_training_session_completed(payload):
    # → close wellness check-in
    # → calculate load metrics
    # → trigger analytics readiness scores

@event_handler("training.readiness.assessed")
async def on_training_readiness_assessed(payload):
    # → if score < threshold: create attention_queue_item
    # → if auto-adjust enabled: call eligibility_service.auto_adjust_prescription()
```

---

### 6. RBAC Middleware (Role-Based Access Control)

```python
# middlewares/rbac.py
ROLE_PERMISSIONS = {
    "head_coach": {
        "training_sessions@view": ["all"],
        "training_sessions@create": True,
        "training_sessions@update": ["own"],
        "training_sessions@delete": ["soft_delete"],
        # ... 20+ more permissions
    },
    "assistant_coach": {
        "training_sessions@view": ["team"],
        "training_sessions@create": True,
        "training_sessions@update": ["own"],
        # ...
    },
    "athlete": {
        "training_sessions@view": ["own"],
        "training_sessions@check_in": True,
        # ...
    },
    # admin, analyst, medical_staff
}

@app.middleware("http")
async def rbac_middleware(request, call_next):
    # Check role-permission match
    # Return 403 Forbidden if denied
```

---

## 🎨 FRONTEND — O que Falta Implementar

### 1. Estrutura de Diretórios (3 pages, 20+ components)

```
src/pages/training/
├── SessionListPage.tsx           ← List of sessions (coaches)
├── SessionDetailPage.tsx         ← Single session edit/view
├── CoachReviewPage.tsx           ← Post-session review
├── AthleteCheckInPage.tsx        ← Pre-training wellness check-in
└── AttentionQueuePage.tsx        ← Alerts queue

src/components/training/
├── SessionForm/
│   ├── SessionForm.tsx           ← Header (title, date, duration)
│   ├── FocusDistribution.tsx     ← 7 sliders (sum <= 100%)
│   └── SessionBlocksBuilder.tsx  ← Drag-and-drop blocks
├── ObjectivesPanel/
│   ├── ObjectivesList.tsx
│   ├── ObjectiveForm.tsx
│   └── NeedSelector.tsx          ← Auto-populate from open needs
├── WellnessAssessment/
│   ├── WellnessForm.tsx          ← Likert scales, emoji selector
│   ├── ReadinessGauge.tsx        ← Circular progress (0-100)
│   └── IneligibilityCheckbox.tsx
├── FeedbackThread/
│   ├── FeedbackCard.tsx          ← Conversation thread display
│   ├── FeedbackForm.tsx          ← Add message + outcome
│   └── ConversationHistory.tsx
├── AttentionQueue/
│   ├── QueueList.tsx             ← ACTIVE items
│   ├── QueueItemCard.tsx         ← Alert type, athlete, action buttons
│   └── ResolutionModal.tsx       ← Evidence textarea
├── RecommendationReview/
│   ├── RecommendationCard.tsx    ← Accept/Dismiss buttons
│   └── RecommendationList.tsx
└── Common/
    ├── StatusBadge.tsx           ← Status visual indicator
    ├── SessionHeader.tsx         ← Session info display
    └── EmptyState.tsx
```

---

### 2. Pages Detalhadas (3 primárias, per UI Contract)

#### SessionListPage (UIF-TRAINING-001, Screen 1)
```tsx
export const SessionListPage = () => {
  // State
  const [sessions, setSessions] = useState<TrainingSession[]>([])
  const [filter, setFilter] = useState({ status: "", dateRange: [] })
  const [loading, setLoading] = useState(false)
  
  // Fetch
  useEffect(() => {
    fetchSessions(filter)
  }, [filter])
  
  // Render
  return (
    <div>
      <h1>Training Sessions</h1>
      <FilterBar onFilter={setFilter} />
      {loading ? <Spinner /> : <SessionTable sessions={sessions} />}
      <Button onClick={() => navigate("/training/new")}>New Session</Button>
    </div>
  )
}
```

**Components needed:**
- `<SessionTable>` — responsive table/card grid
- `<FilterBar>` — date range, team, status dropdowns
- `<StatusBadge>` — DRAFT, SCHEDULED, IN_PROGRESS, COMPLETED, ARCHIVED

**Data fetched:** `GET /api/v1/training/sessions?status=...&date_from=...&date_to=...`

---

#### SessionDetailPage (UIF-TRAINING-001, Screens 2-5)
```tsx
export const SessionDetailPage = () => {
  const { sessionId } = useParams()
  const [session, setSession] = useState<TrainingSession | null>(null)
  const [activeTab, setActiveTab] = useState<"header" | "objectives" | "blocks" | "recommendations">("header")
  
  useEffect(() => {
    fetchSession(sessionId)
  }, [sessionId])
  
  const handlePublish = async () => {
    await publishSession(sessionId)
    setSession(await fetchSession(sessionId))
  }
  
  return (
    <div>
      <Tabs value={activeTab} onChange={setActiveTab}>
        <Tab label="Header" value="header">
          <SessionHeaderForm session={session} onChange={setSession} />
        </Tab>
        <Tab label="Objectives" value="objectives">
          <ObjectivesPanel sessionId={sessionId} />
        </Tab>
        <Tab label="Blocks" value="blocks">
          <SessionBlocksBuilder sessionId={sessionId} />
        </Tab>
        {session?.analytics_recommendations > 0 && (
          <Tab label="Recommendations" value="recommendations">
            <RecommendationReview sessionId={sessionId} />
          </Tab>
        )}
      </Tabs>
      
      {session?.status === "DRAFT" && (
        <Button onClick={handlePublish} variant="primary">Publish</Button>
      )}
    </div>
  )
}
```

---

#### AthleteCheckInPage (UIF-TRAINING-002, Screens 1-6)
```tsx
export const AthleteCheckInPage = () => {
  const [sessions, setSessions] = useState([]) // today's scheduled
  const [selectedSession, setSelectedSession] = useState(null)
  const [step, setStep] = useState<"list" | "wellness" | "readiness" | "ineligibility" | "confirm">("list")
  const [formData, setFormData] = useState({
    sleepQuality: 5,
    mood: "neutral",
    restingHr: 60,
    fatigue: 5,
    ineligibilities: []
  })
  
  const readinessScore = calculateReadiness(formData)
  
  const handleSubmit = async () => {
    await postCheckIn(selectedSession.id, formData)
    setStep("confirm")
  }
  
  return (
    <>
      {step === "list" && <ScheduledSessionsList onSelect={setSelectedSession} />}
      {step === "wellness" && <WellnessAssessmentForm formData={formData} onChange={setFormData} />}
      {step === "readiness" && <ReadinessGauge score={readinessScore} />}
      {step === "ineligibility" && <IneligibilityCheckboxes formData={formData} onChange={setFormData} />}
      {step === "confirm" && <CheckInConfirmation readinessScore={readinessScore} />}
      
      <Button onClick={() => setStep(nextStep)}>Next</Button>
    </>
  )
}
```

---

#### CoachReviewPage (UIF-TRAINING-003, Screens 1-7)
```tsx
export const CoachReviewPage = () => {
  const [sessionsToReview, setSessionsToReview] = useState([])
  const [selectedSession, setSelectedSession] = useState(null)
  const [attendanceList, setAttendanceList] = useState([])
  const [feedbackThreads, setFeedbackThreads] = useState([])
  const [attentionQueue, setAttentionQueue] = useState([])
  
  useEffect(() => {
    if (selectedSession) {
      fetchAttendance(selectedSession.id)
      fetchFeedback(selectedSession.id)
      fetchAttentionQueue(selectedSession.id)
    }
  }, [selectedSession])
  
  const handleCompleteReview = async () => {
    await completeSessionReview(selectedSession.id)
    setSessionsToReview(await fetchSessionsToReview())
  }
  
  return (
    <div>
      {!selectedSession ? (
        <SessionsToReviewQueue onSelect={setSelectedSession} />
      ) : (
        <SessionReviewDashboard
          session={selectedSession}
          attendance={attendanceList}
          feedback={feedbackThreads}
          attentionQueue={attentionQueue}
          onComplete={handleCompleteReview}
        />
      )}
    </div>
  )
}
```

---

### 3. Hooks Customizados (~10)

```typescript
// hooks/useTrainingSession.ts
export const useTrainingSession = (sessionId: string) => {
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  useEffect(() => {
    fetchSession(sessionId)
      .then(setSession)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [sessionId])
  
  return { session, loading, error, refetch: () => fetchSession(sessionId) }
}

// hooks/useReadinessScore.ts
export const useReadinessScore = (sleep, mood, hr, fatigue) => {
  const score = useMemo(() => calculateReadiness(sleep, mood, hr, fatigue), [sleep, mood, hr, fatigue])
  const category = useMemo(() => categorizeReadiness(score), [score])
  return { score, category }
}

// hooks/useRBAC.ts
export const useRBAC = () => {
  const { user } = useAuth()
  const can = (action: string, resource: string, context?: any) => {
    return checkPermission(user.role, action, resource, context)
  }
  return { can }
}

// hooks/useEventSubscription.ts (real-time updates)
export const useEventSubscription = (eventType: string) => {
  const [data, setData] = useState(null)
  
  useEffect(() => {
    const unsubscribe = subscribeToEvent(eventType, (payload) => {
      setData(payload)
    })
    return unsubscribe
  }, [eventType])
  
  return data
}
```

---

### 4. API Client (~method signatures)

```typescript
// api/trainingClient.ts
export const trainingApi = {
  // Sessions
  getSessions: (filters) => GET("/training/sessions", { params: filters }),
  getSession: (id) => GET(`/training/sessions/${id}`),
  createSession: (data) => POST("/training/sessions", data),
  updateSession: (id, data) => PATCH(`/training/sessions/${id}`, data),
  publishSession: (id) => PATCH(`/training/sessions/${id}/publish`, {}),
  startSession: (id) => PATCH(`/training/sessions/${id}/status`, { status: "IN_PROGRESS" }),
  completeSession: (id) => PATCH(`/training/sessions/${id}/status`, { status: "COMPLETED" }),
  cancelSession: (id, reason) => PATCH(`/training/sessions/${id}/status`, { status: "CANCELLED", reason }),
  softDeleteSession: (id) => DELETE(`/training/sessions/${id}`),
  
  // Objectives
  getObjectives: (sessionId) => GET(`/training/sessions/${sessionId}/objectives`),
  createObjective: (sessionId, data) => POST(`/training/sessions/${sessionId}/objectives`, data),
  updateObjective: (id, data) => PATCH(`/training/objectives/${id}`, data),
  deleteObjective: (id) => DELETE(`/training/objectives/${id}`),
  
  // Wellness & Readiness
  postCheckIn: (sessionId, data) => POST(`/training/sessions/${sessionId}/check-in`, data),
  getReadiness: (athleteId) => GET(`/training/readiness/${athleteId}`),
  
  // Feedback
  createFeedback: (sessionId, data) => POST(`/training/sessions/${sessionId}/feedback`, data),
  updateFeedbackStatus: (threadId, status) => PATCH(`/training/feedback-threads/${threadId}/status`, { status }),
  
  // Attention Queue
  getAttentionQueue: (filters?) => GET("/training/attention-queue", { params: filters }),
  resolveAttentionItem: (itemId, data) => PATCH(`/training/attention-queue/${itemId}/status`, data),
}
```

---

## 📋 Checklist de Implementação

### Fase 1: MVP Backend (2-3 sprints)

- [ ] **Database Connections**
  - [ ] SQLAlchemy ORM models (12 entities)
  - [ ] Alembic migration v1 verification
  - [ ] Connection pooling configuration

- [ ] **Core Services** (5 classes: TransiningSessionService, WellnessService, FeedbackService, RecommendationService, AttentionQueueService)
  - [ ] Session CRUD + FSM state transitions
  - [ ] Wellness assessment recording + readiness calculation
  - [ ] Feedback thread creation/closing
  - [ ] Recommendation accept/dismiss
  - [ ] Attention queue item management

- [ ] **API Endpoints** (27 endpoints)
  - [ ] 7 Session endpoints
  - [ ] 4 Objective endpoints
  - [ ] 4 Block endpoints
  - [ ] 3 Feedback endpoints
  - [ ] 2 Wellness endpoints
  - [ ] 2 Attention queue endpoints
  - [ ] 1 Readiness endpoint

- [ ] **Validations**
  - [ ] FSM state transition validator
  - [ ] Focus distribution validator (sum <= 100%)
  - [ ] Business rule enforcements (8 RULEs)
  - [ ] Pydantic schemas for all inputs

- [ ] **Async Events** (27 topics)
  - [ ] Event publishers (emit_* methods in services)
  - [ ] Event handlers (background tasks, outbox pattern)
  - [ ] Message broker configuration (AMQP/RabbitMQ)

- [ ] **RBAC Middleware**
  - [ ] Role-permission matrix
  - [ ] Endpoint authorization checks
  - [ ] Soft-delete filter in queries

---

### Fase 2: MVP Frontend (2-3 sprints)

- [ ] **Pages** (3 primary)
  - [ ] SessionListPage (coaches view all sessions)
  - [ ] SessionDetailPage (edit/configure session)
  - [ ] AthleteCheckInPage (pre-training wellness)

- [ ] **Components** (20+ components)
  - [ ] SessionForm (header input)
  - [ ] FocusDistribution (7 sliders con validation)
  - [ ] SessionBlocksBuilder (drag-and-drop)
  - [ ] ObjectivesPanel (CRUD objectives)
  - [ ] WellnessForm (Likert scales, HR input)
  - [ ] ReadinessGauge (circular progress)
  - [ ] StatusBadge, EmptyState, etc.

- [ ] **API Integration**
  - [ ] trainingApi client (27 methods)
  - [ ] Error handling & toast notifications
  - [ ] Loading states & skeletons

- [ ] **Hooks**
  - [ ] useTrainingSession (fetch + refetch)
  - [ ] useReadinessScore (calculated field)
  - [ ] useRBAC (permission checks)
  - [ ] useEventSubscription (WebSocket)

- [ ] **Responsiveness**
  - [ ] Mobile-first layout (360px+)
  - [ ] Breakpoints: 768, 1024, 1440
  - [ ] Touch-friendly targets (44×44px)

---

### Fase 3: Integration & Testing (1-2 sprints)

- [ ] **Integration Tests**
  - [ ] FSM state transitions (all valid/invalid paths)
  - [ ] RBAC permission checks (per role)
  - [ ] Soft-delete invisibility
  - [ ] Event publishing & handler execution

- [ ] **End-to-End Tests**
  - [ ] Complete session creation → publication → execution → review flow
  - [ ] Athlete check-in → readiness calculation → attention alert creation
  - [ ] Coach feedback loop → thread closure

- [ ] **Feature Flags**
  - [ ] training.enabled (gating flag)
  - [ ] training.coach_in_loop_recommendations
  - [ ] training.athlete_check_in
  - [ ] training.attention_queue

- [ ] **Monitoring & Observability**
  - [ ] Log key events (session state changes, API errors)
  - [ ] Metrics: request latency, event throughput, FSM transition coverage
  - [ ] Alerts: failed event publishing, quota breaches

---

### Fase 4: Polish & Integration (1 sprint)

- [ ] **Coach Review Page** (CoachReviewPage)
- [ ] **Analytics Recommendations UI** (RecommendationReview)
- [ ] **Advanced Filtering & Search**
- [ ] **Bulk Operations** (export sessions, reschedule)
- [ ] **Notifications** (toast alerts, email digests)
- [ ] **Dark Mode** (design system compatibility)
- [ ] **Accessibility** (WCAG 2.1 AA compliance)

---

## 📊 Estimativa de Esforço

| Componente | Backend Hours | Frontend Hours | Total |
|------------|---------------|----------------|-------|
| **Database & ORM** | 16 | — | 16 |
| **Core Services (8 classes)** | 40 | — | 40 |
| **API Endpoints (27)** | 24 | — | 24 |
| **Validations & Rules** | 12 | — | 12 |
| **Async Events (27 topics)** | 20 | — | 20 |
| **RBAC Middleware** | 8 | — | 8 |
| **Pages (3)** | — | 24 | 24 |
| **Components (20+)** | — | 40 | 40 |
| **API Client** | — | 12 | 12 |
| **Hooks (10)** | — | 16 | 16 |
| **Integration Tests** | 16 | 8 | 24 |
| **E2E Tests** | 8 | 12 | 20 |
| **Documentation** | 4 | 4 | 8 |
| **TOTAL** | **148 hours** | **116 hours** | **264 hours** |

**Timeline (4-person team):**
- Fase 1 (Backend MVP): 2.5 sprints (3-4 weeks)
- Fase 2 (Frontend MVP): 2.5 sprints (3-4 weeks)
- Fase 3 (Integration & Testing): 1.5 sprints (2-3 weeks)
- Fase 4 (Polish): 1 sprint (1-2 weeks)

**Total: ~16-18 semanas (4 meses) para MVP production-ready**

---

## 🚀 Recomendações

**Prioridades:**
1. ✅ Contratos 100% definidos (já completo)
2. ✅ Database migrations (já completo)
3. ⏳ **Backend MVP** (crítico — bloqueia frontend)
4. ⏳ **Frontend MVP** (depende de backend)
5. ⏳ Testes & integração (paralelo com M/F)

**Riscos:**
- **Alto:** Complexidade FSM + soft-delete lógica
- **Médio:** Coach-in-loop recomendações (async coordination)
- **Médio:** Event ordering guarantees (AMQP tuning)
- **Baixo:** UI componente reutilização (design system exists)

---

**Status Resumido:** 🟡 **Contract-Ready, Zero Code Implementation**

