# Phase 4: Frontend & Dashboard - Context

**Gathered:** 2026-04-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the React (Vite) + TypeScript desktop SPA with a two-panel layout: chat on the left (~2/3), clinical dashboard on the right (~1/3). The frontend is a dumb display layer — it sends POST /chat requests and renders whatever the backend returns. All dashboard elements (probability, risk bar, cost table, interpretation, abbreviations) are visible simultaneously on desktop without scrolling.

</domain>

<decisions>
## Implementation Decisions

### Technology Stack
- **D-01:** React + Vite + TypeScript (FRNT-01). Standard modern frontend stack.
- **D-02:** Tailwind CSS for styling. Utility-first, great for responsive design, rapid iteration. Will pay off significantly in Phase 5 (mobile) with responsive prefixes.
- **D-03:** React Context + useReducer for state management. No external state library. Sufficient for one-session app with small state shape (session_id, messages, prediction, conversation_phase). Easy swap to Zustand later if needed.

### Layout
- **D-04:** Desktop: two-panel layout. Left panel (~2/3 width) is the chat interface. Right panel (~1/3 width) is the clinical dashboard. Both visible simultaneously (FRNT-02).
- **D-05:** Compact dashboard design — all elements visible without scrolling on 1080p+ displays. Smaller font sizes, tight padding, sensible spacing. If viewport is smaller, the dashboard panel scrolls internally (not the page).
- **D-06:** Dashboard elements stacked vertically in right panel: probability + risk label (compact header) → guidance bar → recommended intervention → cost table → interpretation guidance → abbreviations.

### Chat Panel
- **D-07:** Messages rendered as a scrollable list with user messages on the right, assistant messages on the left. Standard chat bubble pattern.
- **D-08:** Input box at the bottom of the chat panel with a send button.
- **D-09:** Typing indicator (three animated dots) shown as a "bot message" while waiting for backend response (FRNT-06). Dashboard stays static until response arrives.
- **D-10:** Confirmation button rendered inline below the summary chat message when `conversation_phase === "awaiting_confirmation"`. Button disappears after confirmation. Clinician can also type in the input box to provide corrections instead.

### Dashboard Components
- **D-11:** Probability displayed as a large percentage number with the risk tier label (e.g., "45.0% — High Risk"). Color-coded by tier.
- **D-12:** Management guidance bar implemented as pure CSS/HTML: four colored div segments (CCY±IOC, MRCP, EUS, ERCP) with a CSS gradient, labeled zones, and an absolutely-positioned pointer marker that animates with `transition: left` when probability changes.
- **D-13:** Recommended intervention displayed as explicit text below the guidance bar (DASH-04).
- **D-14:** Cost table as a compact 4-row HTML table (IOC, MRCP, ERCP, EUS) with probability-weighted costs formatted as currency (DASH-05). Always visible on desktop.
- **D-15:** Interpretation guidance panel: static text explaining probability ranges and what they mean clinically. Always visible (DASH-06).
- **D-16:** Abbreviations panel: static reference with definitions for MRCP, EUS, ERCP, IOC, CCY, etc. Always visible (DASH-07).

### API Integration
- **D-17:** Frontend calls backend at `http://10.17.67.98:451` (explicit cross-origin, not same-origin). All API calls use this base URL.
- **D-18:** Single API function: `POST /chat` with `{session_id, message}`. Response contains full state — frontend replaces (not merges) its local state from the response.
- **D-19:** Session ID stored in React state (Context). Created on first POST /chat (backend returns it). Sent on all subsequent requests.
- **D-20:** Frontend sends only session_id + message. Never sends clinical data. Server is source of truth (inherited from Phase 3 D-09).

### Cholangitis Fast-Path
- **D-21:** When `prediction.cholangitis_flag === true`, the dashboard shows a prominent banner with the ASGE 2019 message overlaying or replacing the guidance bar, matching the existing Dash app behavior.

### Claude's Discretion
- Exact Tailwind color palette and spacing values
- Component file organization within src/
- TypeScript type definitions mirroring backend schemas
- Chat bubble styling details
- Guidance bar exact gradient colors (can reference existing Dash app's green gradient)
- Animation timing for pointer movement

</decisions>

<specifics>
## Specific Ideas

- The existing Dash app uses a green gradient (rgb 198,239,1 → 0,100,0) for the management bar — replicate this in CSS
- Cost table from existing app: simple two-column (Intervention, Expected Cost) with `$X,XXX.XX` formatting
- Risk tier colors: low = green, intermediate = yellow/amber, high = orange, very_high = red
- The cholangitis overlay in the existing app blurs the guidance bar and shows a red-text ASGE message — replicate with CSS blur filter + overlay div
- Dashboard should show an empty/placeholder state before first prediction: "Awaiting clinical data..." or similar
- The existing abbreviation.json can be loaded as static data in the frontend

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Backend API (Phase 3 outputs)
- `backend/app/schemas/chat.py` — ChatRequest, ChatResponse (the API contract)
- `backend/app/schemas/prediction.py` — PredictionResult, CostEstimate (dashboard data shape)
- `backend/app/routers/chat.py` — POST /chat endpoint
- `backend/app/routers/health.py` — GET /health for readiness check

### Existing Visual Assets
- `docs/cbd app/assets/utils.py` lines 164-233 — Management bar gradient, zone boundaries, pointer logic
- `docs/cbd app/assets/abbreviation.json` — Abbreviation mappings
- `docs/cbd app/app.py` lines 493-543 — Cholangitis overlay, cost table rendering

### Configuration
- `backend/config/features.yaml` — Risk tiers, cost values, feature descriptions

### Research
- `.planning/research/ARCHITECTURE.md` — Frontend component boundaries, API client pattern
- `.planning/research/PITFALLS.md` — Pitfall 11 (frontend/backend state divergence)

</canonical_refs>

<code_context>
## Existing Code Insights

### API Contract (from Phase 3)
```typescript
// POST /chat
Request:  { session_id?: string, message: string }
Response: {
  session_id: string,
  message: string,
  extracted_features: Record<string, any>,
  prediction: PredictionResult | null,
  conversation_phase: "collecting" | "awaiting_confirmation" | "confirmed",
  missing_required: string[],
  turn_number: number
}

// PredictionResult
{
  probability: number,        // 0-100
  risk_tier: string,          // "low" | "intermediate" | "high" | "very_high"
  recommended_intervention: string,
  cost_estimates: { intervention: string, cost: number }[],
  cholangitis_flag: boolean,
  cholangitis_message: string | null,
  imputed_fields: string[]
}
```

### New Modules to Create
- `frontend/` — Vite + React + TypeScript + Tailwind project
- `frontend/src/api/client.ts` — Typed fetch wrapper for POST /chat
- `frontend/src/types/api.ts` — TypeScript types mirroring backend schemas
- `frontend/src/context/ChatContext.tsx` — React Context + useReducer for app state
- `frontend/src/components/ChatPanel.tsx` — Chat interface (messages, input, typing indicator)
- `frontend/src/components/DashboardPanel.tsx` — Dashboard container
- `frontend/src/components/dashboard/ProbabilityDisplay.tsx` — Percentage + risk label
- `frontend/src/components/dashboard/GuidanceBar.tsx` — CSS gradient bar with pointer
- `frontend/src/components/dashboard/CostTable.tsx` — 4-row cost table
- `frontend/src/components/dashboard/InterpretationGuide.tsx` — Static text panel
- `frontend/src/components/dashboard/Abbreviations.tsx` — Static abbreviation reference
- `frontend/src/App.tsx` — Two-panel layout

</code_context>

<deferred>
## Deferred Ideas

- Mobile responsive layout — deferred to Phase 5
- SSE/streaming for LLM tokens — deferred; synchronous POST is sufficient for v1
- Dark mode / theme toggle — deferred
- Extracted features sidebar in dashboard — could show what was provided vs imputed
- Chat message formatting with markdown — deferred; plain text is sufficient

</deferred>

---

*Phase: 04-frontend*
*Context gathered: 2026-04-06 via interactive discussion*
