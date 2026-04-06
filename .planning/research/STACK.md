# Technology Stack

**Project:** CBD Stone LLM — Conversational Clinical Decision Support
**Researched:** 2026-04-05
**Overall Confidence:** HIGH (all versions verified against PyPI, npm, and official docs)

---

## Recommended Stack

### Backend — Python

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Python | 3.11.x | Runtime | Matches existing conda env (3.11.2); scikit-learn 1.5.2 pkl files were trained and serialized under 3.11 — changing the minor version risks model loading failures. Do NOT upgrade to 3.12+ until models are retrained. |
| FastAPI | 0.135.3 | HTTP API framework | Modern async, auto-generated OpenAPI docs, first-class Pydantic integration. `fastapi[standard]` installs uvicorn and python-multipart together. |
| Uvicorn | 0.43.0 | ASGI server | FastAPI's recommended server. For local network deployment a single `uvicorn` process is sufficient — skip Gunicorn. |
| Pydantic | 2.12.5 | Data validation / schemas | FastAPI v0.110+ requires Pydantic v2. Used for request/response models and as the schema type passed to OpenAI structured outputs. |
| openai | 2.30.0 | OpenAI API client | Official SDK. Use `client.beta.chat.completions.parse()` with a Pydantic model for structured extraction — this is the correct v2 API (not the legacy `openai.ChatCompletion`). |
| PyYAML | 6.0.3 | YAML config loading | Reads the feature-definition YAML schema that tells the LLM what to extract. Mature, no meaningful alternatives. |
| python-dotenv | 1.2.2 | Environment variable loading | Loads OPENAI_API_KEY and PORT from a `.env` file. Keeps secrets out of source. |
| joblib | 1.4.2 | Model deserialization | Already used in the existing codebase to load the `.pkl` files. Must stay at 1.4.2 (pinned) because the pickle files were serialized with this version. |
| scikit-learn | **1.5.2 (pinned)** | ML model inference | The existing `.pkl` files were serialized with 1.5.2. scikit-learn explicitly does not support cross-version pickle loading; a known ModuleNotFoundError breaks GradientBoosting models when loading across minor versions. Pin to 1.5.2 and do NOT upgrade until models are retrained. |
| pandas | 2.2.3 | DataFrame assembly for model input | Already in the codebase. Required by the existing feature imputation pipeline. |
| numpy | 1.26.4 | Numerical arrays | scikit-learn 1.5.2 was built against numpy 1.26.x. Upgrading to numpy 2.x with scikit-learn 1.5.2 is untested. |

### Frontend — TypeScript / React

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Node.js | 20 LTS | JS runtime | Vite 8 requires Node >= 18; Node 20 LTS is current long-term support. |
| Vite | 8.x | Build tool / dev server | Current major version (8.0.3 as of April 2026). Replaced CRA as the standard. The `@tailwindcss/vite` plugin integrates directly. |
| React | 19.x | UI framework | React 19.2.3 is current stable. React 19 ships the Actions API and improved concurrent rendering. New projects should target 19, not 18. |
| TypeScript | 5.x | Type safety | Ships with Vite's React-TS template. Required for reliable prop typing of clinical data structures. |
| Tailwind CSS | 4.x | Utility-first styling | v4 (released Jan 2025) is the current stable series. Install via `@tailwindcss/vite` plugin — no `tailwind.config.js` needed. Faster than v3. |
| shadcn/ui | latest (CLI-managed) | Component library | Copy-paste components built on Radix UI + Tailwind. Not a versioned npm package — the CLI pulls latest source into your codebase. Use for: `ScrollArea` (chat history), `Card` (dashboard panels), `Badge` (risk level indicator), `Table` (cost table), `Collapsible` (mobile cost table), `Button`. |
| Zustand | 5.0.x | Client state management | Manages chat history, extracted variable state, and prediction result in the client. Minimal boilerplate. v5 is the current stable series, requires React 18+. |

### Supporting Libraries (Frontend)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| @tanstack/react-query | 5.x | Server state / async | Use for the `/predict` and `/extract` API calls — handles loading/error states, caching, and refetch on variable updates. Complement to Zustand (server state only, not conversation state). |
| clsx | latest | Conditional className | Standard companion to Tailwind for conditional class application. |
| lucide-react | latest | Icons | Ships with shadcn/ui setup. Consistent icon set, tree-shakeable. |

---

## Critical Version Constraints

### Do NOT change these without retesting model loading

```
scikit-learn == 1.5.2
joblib == 1.4.2
numpy == 1.26.4
Python == 3.11.x
```

The existing `.pkl` files in `docs/cbd app/Models/` were pickled with scikit-learn 1.5.2. The scikit-learn maintainers have explicitly documented that cross-version pickle loading is unsupported, and a known `ModuleNotFoundError: No module named '_loss'` breaks GradientBoosting models when loaded with a different minor version. Any upgrade requires retraining and re-pickling all 6 model files.

---

## OpenAI Integration Pattern

Use `client.beta.chat.completions.parse()` (the structured outputs beta endpoint), not `client.chat.completions.create()` with raw JSON mode.

**Why:** The `.parse()` method accepts a Pydantic model as `response_format`, handles JSON schema conversion automatically, and returns a typed Python object — no manual `json.loads()` or schema-writing needed. Supported on `gpt-4o-mini` as of the August 2024 model snapshot and all subsequent versions.

**Constraint:** OpenAI Structured Outputs only support a subset of JSON Schema. Avoid advanced Pydantic validators (regex patterns, custom validators, nested discriminated unions) in the extraction model — they may silently break schema validation. Use `Optional[type] = None` for fields that may be absent from the clinical text.

**Recommended extraction model shape:**

```python
from pydantic import BaseModel
from typing import Optional

class ClinicalExtraction(BaseModel):
    sex: Optional[str] = None            # required by clinical rules but may be missing
    age: Optional[float] = None
    cholangitis: Optional[bool] = None
    # ... one field per model feature
    missing_fields: list[str] = []       # LLM reports what it couldn't find
    ambiguous_fields: list[str] = []     # LLM flags what needs clarification
```

---

## scikit-learn Model Serving Pattern

Load models once at FastAPI startup using a lifespan context manager (not `@app.on_event` which is deprecated in FastAPI 0.93+):

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
import joblib

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = joblib.load("models/initial.pkl")
    app.state.imputer = joblib.load("models/iterative_imputer.pkl")
    yield
    # cleanup if needed

app = FastAPI(lifespan=lifespan)
```

**Why:** Loading a pkl on every request adds 50-200ms latency. The lifespan pattern is the FastAPI-idiomatic way to hold shared state; `@app.on_event` was deprecated in 0.93 and will be removed.

---

## CORS Configuration

React dev server runs on `:5173` (Vite default), backend on `:450`. CORS must be configured:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # dev only
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

For local network production deployment on port 450, replace `localhost:5173` with the React build's served origin, or serve both from the same origin (FastAPI serving the Vite build output as static files).

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Backend framework | FastAPI | Flask | Flask lacks async, no native Pydantic, no auto-docs. Already in the codebase as a Dash dependency but not appropriate as the primary API framework. |
| Backend framework | FastAPI | Django REST Framework | Significant overhead; overkill for a single-purpose inference API. |
| LLM extraction | Structured Outputs (`.parse()`) | Function calling with `strict=True` | Functionally equivalent for this use case; `.parse()` has cleaner Python ergonomics and no tool-definition boilerplate. |
| LLM extraction | GPT-4o-mini structured outputs | `instructor` library | Instructor is a well-regarded wrapper but adds a dependency; the native SDK's `.parse()` method achieves the same result since August 2024. |
| Frontend state | Zustand + TanStack Query | Redux Toolkit | Redux is appropriate for large multi-team apps with complex state; this project has one page. Redux adds ~3x the boilerplate for no benefit here. |
| Frontend state | Zustand + TanStack Query | React Context + useState | Context triggers full subtree re-renders; poor choice for frequently-updated chat state. Zustand isolates re-renders to subscribed components. |
| Styling | Tailwind CSS v4 | CSS Modules | Tailwind v4's zero-config setup and shadcn/ui integration make it the correct choice. CSS Modules would require writing everything from scratch. |
| Component library | shadcn/ui | MUI / Chakra UI | shadcn/ui gives full source ownership, smaller bundle (only components you use), and pairs naturally with Tailwind. MUI/Chakra carry their own styling systems that conflict with Tailwind. |
| Build tool | Vite 8 | Webpack / CRA | CRA is deprecated and unmaintained. Webpack requires significant configuration. Vite is the community standard as of 2024-2025. |
| Model serialization | joblib (existing) | ONNX | ONNX would be safer for cross-environment loading but requires re-exporting all 6 models and validating numerical equivalence — substantial effort with clinical risk. Use ONNX for v2 when the models are retrained. |

---

## Installation

### Backend

```bash
# Inside existing conda env or new Python 3.11 venv
pip install "fastapi[standard]==0.135.3"
pip install uvicorn==0.43.0
pip install pydantic==2.12.5
pip install openai==2.30.0
pip install pyyaml==6.0.3
pip install python-dotenv==1.2.2

# PINNED — do not upgrade without retraining models
pip install scikit-learn==1.5.2
pip install joblib==1.4.2
pip install numpy==1.26.4
pip install pandas==2.2.3
```

### Frontend (scaffold)

```bash
npm create vite@latest cbd-frontend -- --template react-ts
cd cbd-frontend
npm install
npm install -D tailwindcss @tailwindcss/vite
npm install zustand @tanstack/react-query
npm install clsx lucide-react

# shadcn/ui initialization (adds Radix UI primitives)
npx shadcn@latest init
# Then add components as needed:
npx shadcn@latest add scroll-area card badge table collapsible button
```

---

## Sources

- FastAPI PyPI: https://pypi.org/project/fastapi/ (v0.135.3, verified 2026-04-05)
- Uvicorn PyPI: https://pypi.org/project/uvicorn/ (v0.43.0, verified 2026-04-05)
- OpenAI Python SDK PyPI: https://pypi.org/project/openai/ (v2.30.0, verified 2026-04-05)
- Pydantic PyPI: https://pypi.org/project/pydantic/ (v2.12.5, verified 2026-04-05)
- python-dotenv PyPI: https://pypi.org/project/python-dotenv/ (v1.2.2, verified 2026-04-05)
- PyYAML PyPI: https://pypi.org/project/pyyaml/ (v6.0.3, verified 2026-04-05)
- scikit-learn PyPI: https://pypi.org/project/scikit-learn/ (latest 1.8.0; use 1.5.2 pinned)
- scikit-learn model persistence docs: https://scikit-learn.org/stable/model_persistence.html
- scikit-learn cross-version GBM breakage issue: https://github.com/scikit-learn/scikit-learn/issues/30062
- OpenAI Structured Outputs docs: https://platform.openai.com/docs/guides/structured-outputs
- React versions: https://react.dev/versions (v19.2.3 current stable)
- Vite latest: https://vite.dev/releases (v8.x current)
- Tailwind CSS v4 release: https://tailwindcss.com/blog/tailwindcss-v4
- shadcn/ui changelog: https://ui.shadcn.com/docs/changelog
- Zustand v5 announcement: https://pmnd.rs/blog/announcing-zustand-v5 (v5.0.12 current)
- TanStack Query v5: https://tanstack.com/query/latest (v5.x current)
- FastAPI CORS docs: https://fastapi.tiangolo.com/tutorial/cors/
- FastAPI lifespan events: https://fastapi.tiangolo.com/deployment/versions/
