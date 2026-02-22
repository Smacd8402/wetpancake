# B2B Cold Calling Trainer Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a local-only desktop app that runs real-time B2B cold-call voice simulations with unique conversations and post-call scoring, without paid APIs.

**Architecture:** Use an Electron desktop shell for UI/session control and a local Python backend for AI inference and scoring. The backend exposes local HTTP/WebSocket endpoints for STT, dialogue, TTS, and scoring; SQLite persists sessions and anti-repeat metadata.

**Tech Stack:** Electron, React + TypeScript, Python 3.11, FastAPI, Uvicorn, SQLAlchemy, SQLite, pytest, Playwright, local model runtimes (Ollama-compatible LLM, Faster-Whisper STT, Piper TTS).

---

### Task 1: Scaffold Monorepo and Tooling

**Files:**
- Create: `package.json`
- Create: `pnpm-workspace.yaml`
- Create: `.gitignore`
- Create: `apps/desktop/package.json`
- Create: `apps/desktop/electron/main.ts`
- Create: `apps/desktop/src/main.tsx`
- Create: `apps/desktop/src/App.tsx`
- Create: `apps/desktop/tsconfig.json`
- Create: `services/backend/pyproject.toml`
- Create: `services/backend/app/main.py`
- Create: `services/backend/tests/test_health.py`

**Step 1: Write the failing test**

```python
from fastapi.testclient import TestClient
from app.main import app


def test_health_returns_ok():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
```

**Step 2: Run test to verify it fails**

Run: `cd services/backend && pytest tests/test_health.py::test_health_returns_ok -v`
Expected: FAIL with import/module errors because app scaffolding is incomplete.

**Step 3: Write minimal implementation**

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}
```

**Step 4: Run test to verify it passes**

Run: `cd services/backend && pytest tests/test_health.py::test_health_returns_ok -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add package.json pnpm-workspace.yaml .gitignore apps services
git commit -m "chore: scaffold desktop and backend workspaces"
```

### Task 2: Add Audio Session Transport Contract

**Files:**
- Create: `services/backend/app/schemas.py`
- Modify: `services/backend/app/main.py`
- Create: `services/backend/tests/test_session_api.py`
- Create: `apps/desktop/src/lib/api.ts`
- Create: `apps/desktop/src/types/session.ts`

**Step 1: Write the failing test**

```python
from fastapi.testclient import TestClient
from app.main import app


def test_create_session_returns_id_and_seed():
    client = TestClient(app)
    resp = client.post("/sessions", json={"duration_minutes": 8})
    assert resp.status_code == 201
    body = resp.json()
    assert "session_id" in body
    assert "seed" in body
```

**Step 2: Run test to verify it fails**

Run: `cd services/backend && pytest tests/test_session_api.py::test_create_session_returns_id_and_seed -v`
Expected: FAIL with 404 for `/sessions`.

**Step 3: Write minimal implementation**

```python
from pydantic import BaseModel
from uuid import uuid4
import random

class SessionCreate(BaseModel):
    duration_minutes: int

class SessionCreateResponse(BaseModel):
    session_id: str
    seed: int

@app.post("/sessions", response_model=SessionCreateResponse, status_code=201)
def create_session(payload: SessionCreate):
    return {"session_id": str(uuid4()), "seed": random.randint(1, 10_000_000)}
```

**Step 4: Run test to verify it passes**

Run: `cd services/backend && pytest tests/test_session_api.py::test_create_session_returns_id_and_seed -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add services/backend apps/desktop/src
git commit -m "feat: add session creation contract"
```

### Task 3: Implement Persistence Layer (SQLite)

**Files:**
- Create: `services/backend/app/db.py`
- Create: `services/backend/app/models.py`
- Modify: `services/backend/app/main.py`
- Create: `services/backend/tests/test_persistence.py`

**Step 1: Write the failing test**

```python
from fastapi.testclient import TestClient
from app.main import app


def test_created_session_is_persisted():
    client = TestClient(app)
    created = client.post("/sessions", json={"duration_minutes": 8}).json()
    fetched = client.get(f"/sessions/{created['session_id']}")
    assert fetched.status_code == 200
    assert fetched.json()["session_id"] == created["session_id"]
```

**Step 2: Run test to verify it fails**

Run: `cd services/backend && pytest tests/test_persistence.py::test_created_session_is_persisted -v`
Expected: FAIL with 404 for `GET /sessions/{id}`.

**Step 3: Write minimal implementation**

```python
# SQLAlchemy model with SessionRecord table
# Fields: session_id (pk), seed, duration_minutes, created_at
# Add GET /sessions/{session_id} endpoint returning persisted record
```

**Step 4: Run test to verify it passes**

Run: `cd services/backend && pytest tests/test_persistence.py::test_created_session_is_persisted -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add services/backend/app services/backend/tests
git commit -m "feat: persist sessions in sqlite"
```

### Task 4: Add Prospect Persona Generator with Anti-Repeat Guard

**Files:**
- Create: `services/backend/app/persona.py`
- Modify: `services/backend/app/models.py`
- Modify: `services/backend/app/main.py`
- Create: `services/backend/tests/test_persona_generation.py`

**Step 1: Write the failing test**

```python
from app.persona import PersonaGenerator


def test_persona_generator_avoids_recent_primary_objection():
    gen = PersonaGenerator()
    recent = [{"primary_objection": "no_budget"}]
    persona = gen.generate(seed=1234, recent_sessions=recent)
    assert persona.primary_objection != "no_budget"
```

**Step 2: Run test to verify it fails**

Run: `cd services/backend && pytest tests/test_persona_generation.py::test_persona_generator_avoids_recent_primary_objection -v`
Expected: FAIL because `PersonaGenerator` does not exist.

**Step 3: Write minimal implementation**

```python
# PersonaGenerator with constrained pools:
# industries, roles, pain_points, personalities, objections
# generate() excludes recent primary objections when alternatives exist
```

**Step 4: Run test to verify it passes**

Run: `cd services/backend && pytest tests/test_persona_generation.py::test_persona_generator_avoids_recent_primary_objection -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add services/backend/app services/backend/tests
git commit -m "feat: add persona generation and anti-repeat guard"
```

### Task 5: Build Dialogue Engine Contract (Local LLM Adapter)

**Files:**
- Create: `services/backend/app/dialogue.py`
- Modify: `services/backend/app/main.py`
- Create: `services/backend/tests/test_dialogue.py`

**Step 1: Write the failing test**

```python
from app.dialogue import ProspectState, generate_prospect_turn


def test_dialogue_returns_text_and_state_updates():
    state = ProspectState(trust=0.4, resistance=0.6)
    out = generate_prospect_turn(
        state=state,
        trainee_text="Can I get 30 seconds to explain why I called?",
        persona={"primary_objection": "busy"},
    )
    assert out.text
    assert 0.0 <= out.next_state.trust <= 1.0
    assert 0.0 <= out.next_state.resistance <= 1.0
```

**Step 2: Run test to verify it fails**

Run: `cd services/backend && pytest tests/test_dialogue.py::test_dialogue_returns_text_and_state_updates -v`
Expected: FAIL due missing dialogue module.

**Step 3: Write minimal implementation**

```python
# Dialogue adapter with interface:
# generate_prospect_turn(state, trainee_text, persona) -> DialogueTurn
# Start with rule-based fallback and pluggable LocalLLMClient for Ollama
```

**Step 4: Run test to verify it passes**

Run: `cd services/backend && pytest tests/test_dialogue.py::test_dialogue_returns_text_and_state_updates -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add services/backend/app services/backend/tests
git commit -m "feat: add dialogue engine contract with local llm adapter"
```

### Task 6: Integrate STT/TTS Service Adapters

**Files:**
- Create: `services/backend/app/stt.py`
- Create: `services/backend/app/tts.py`
- Modify: `services/backend/app/main.py`
- Create: `services/backend/tests/test_voice_adapters.py`

**Step 1: Write the failing test**

```python
from app.stt import STTService
from app.tts import TTSService


def test_voice_adapters_have_required_interfaces():
    assert hasattr(STTService, "transcribe_chunk")
    assert hasattr(TTSService, "synthesize")
```

**Step 2: Run test to verify it fails**

Run: `cd services/backend && pytest tests/test_voice_adapters.py::test_voice_adapters_have_required_interfaces -v`
Expected: FAIL because modules/classes do not exist.

**Step 3: Write minimal implementation**

```python
class STTService:
    def transcribe_chunk(self, pcm_bytes: bytes) -> str:
        return ""


class TTSService:
    def synthesize(self, text: str) -> bytes:
        return b""
```

**Step 4: Run test to verify it passes**

Run: `cd services/backend && pytest tests/test_voice_adapters.py::test_voice_adapters_have_required_interfaces -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add services/backend/app services/backend/tests
git commit -m "feat: add stt and tts adapter interfaces"
```

### Task 7: Implement Scoring Engine and Feedback Report

**Files:**
- Create: `services/backend/app/scoring.py`
- Modify: `services/backend/app/main.py`
- Create: `services/backend/tests/test_scoring.py`

**Step 1: Write the failing test**

```python
from app.scoring import score_session


def test_score_session_returns_dimension_scores_and_total():
    report = score_session(
        transcript=[{"speaker": "trainee", "text": "Can I get 30 seconds?"}],
        outcomes={"close_attempt": True},
    )
    assert "total_score" in report
    assert "dimensions" in report
    assert "misses" in report
```

**Step 2: Run test to verify it fails**

Run: `cd services/backend && pytest tests/test_scoring.py::test_score_session_returns_dimension_scores_and_total -v`
Expected: FAIL because scoring module is missing.

**Step 3: Write minimal implementation**

```python
# score_session() computes weighted dimensions:
# opener, rapport, discovery, objection_handling, value_articulation,
# close_quality, talk_listen_balance
# returns total_score + dimensions + top misses + stronger phrasing suggestions
```

**Step 4: Run test to verify it passes**

Run: `cd services/backend && pytest tests/test_scoring.py::test_score_session_returns_dimension_scores_and_total -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add services/backend/app services/backend/tests
git commit -m "feat: add scoring engine and feedback report"
```

### Task 8: Build Desktop Real-Time UI Flow

**Files:**
- Create: `apps/desktop/src/components/CallScreen.tsx`
- Create: `apps/desktop/src/components/Scorecard.tsx`
- Modify: `apps/desktop/src/App.tsx`
- Create: `apps/desktop/src/lib/audio.ts`
- Create: `apps/desktop/tests/call-flow.spec.ts`

**Step 1: Write the failing test**

```ts
import { test, expect } from "@playwright/test";

test("user can start and end a session", async ({ page }) => {
  await page.goto("http://localhost:5173");
  await page.getByRole("button", { name: "Start Call" }).click();
  await expect(page.getByText("Call in progress")).toBeVisible();
  await page.getByRole("button", { name: "End Call" }).click();
  await expect(page.getByText("Post-Call Scorecard")).toBeVisible();
});
```

**Step 2: Run test to verify it fails**

Run: `cd apps/desktop && npx playwright test tests/call-flow.spec.ts`
Expected: FAIL because call UI flow is not implemented.

**Step 3: Write minimal implementation**

```tsx
// App state machine: idle -> in_call -> post_call
// Buttons for Start Call / End Call
// Fetch scorecard from backend and render dimensions + total
```

**Step 4: Run test to verify it passes**

Run: `cd apps/desktop && npx playwright test tests/call-flow.spec.ts`
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/desktop
git commit -m "feat: add desktop call flow and scorecard ui"
```

### Task 9: End-to-End Local Integration and Packaging

**Files:**
- Create: `scripts/dev.ps1`
- Create: `scripts/check.ps1`
- Create: `apps/desktop/electron/preload.ts`
- Create: `docs/setup/local-install.md`
- Create: `docs/ops/model-setup.md`

**Step 1: Write the failing test**

```bash
# Smoke check command should fail before script exists
pwsh ./scripts/check.ps1
```

**Step 2: Run test to verify it fails**

Run: `pwsh ./scripts/check.ps1`
Expected: FAIL with "file not found".

**Step 3: Write minimal implementation**

```powershell
# scripts/check.ps1
# 1) verify backend /health
# 2) verify local llm runtime reachable
# 3) verify stt/tts model files exist
# return non-zero on failures
```

**Step 4: Run test to verify it passes**

Run: `pwsh ./scripts/check.ps1`
Expected: PASS with all checks OK.

**Step 5: Commit**

```bash
git add scripts docs apps/desktop/electron/preload.ts
git commit -m "chore: add local runtime checks and setup docs"
```

### Task 10: Verification Before Completion

**Files:**
- Modify: `README.md`
- Modify: `docs/setup/local-install.md`

**Step 1: Write the failing test**

```bash
# Define full verification suite and run it before release tag
pnpm -r test
```

**Step 2: Run test to verify it fails (if regressions exist)**

Run: `pnpm -r test`
Expected: All tests pass; if any fail, stop and fix before release.

**Step 3: Write minimal implementation**

```markdown
# README should document exact local startup:
# 1) install deps
# 2) install local models
# 3) run backend
# 4) run desktop app
# 5) run verification scripts
```

**Step 4: Run test to verify it passes**

Run:
- `cd services/backend && pytest -v`
- `cd apps/desktop && npx playwright test`
- `pwsh ./scripts/check.ps1`

Expected: PASS on all commands.

**Step 5: Commit**

```bash
git add README.md docs/setup/local-install.md
git commit -m "docs: finalize runbook and verification steps"
```

## Notes for Execution
- Keep each task focused to 2-5 minute actions.
- Do not skip red-green-refactor cycle.
- Use local adapters first; optimize model quality only after end-to-end stability.
- Preserve offline-only constraints and avoid introducing paid services.
