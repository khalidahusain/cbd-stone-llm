# Phase 5: Mobile Layout - Context

**Gathered:** 2026-04-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Add responsive mobile layout to the existing React frontend. Below 768px, the two-panel desktop layout switches to a single-column stacked view with a chat-first flow, collapsible dashboard panel, and accordion controls for secondary dashboard sections. Desktop layout is unchanged.

</domain>

<decisions>
## Implementation Decisions

### Breakpoint Strategy
- **D-01:** Single breakpoint at Tailwind `md` (768px). Below = mobile stacked layout, above = current desktop two-panel layout. No tablet-specific breakpoint.
- **D-02:** Use Tailwind responsive prefixes (`md:w-2/3`, `md:w-1/3`, `md:flex-row`) to convert existing hard-coded desktop layout to mobile-first. Desktop styles are the `md:` variants.

### Dashboard Visibility on Mobile
- **D-03:** Dashboard is completely hidden on mobile until the first prediction arrives. Chat fills the full viewport initially (FRNT-04: "chat-first initially").
- **D-04:** Once prediction exists, the dashboard appears above the chat as a collapsible panel. It does not push chat off-screen — both are visible in a single scroll view.

### Mobile Navigation
- **D-05:** Collapsible dashboard panel pattern. Collapsed state shows a compact summary header with probability percentage and risk tier label (e.g., "45% — High Risk"). Tap to expand/collapse.
- **D-06:** Chat panel is always visible below the dashboard on mobile. No tab switching or view toggling — single page scroll with collapsible sections.
- **D-07:** The collapsible header should be visually distinct (colored by risk tier) so it's immediately recognizable as an interactive element.

### Dashboard Compaction on Mobile
- **D-08:** When the dashboard is expanded on mobile, three sections are always visible: probability display, guidance bar, and recommended intervention.
- **D-09:** Three sections are behind expandable/accordion controls on mobile: cost table (FRNT-05), interpretation guide, and abbreviations. Each has its own expand/collapse toggle.
- **D-10:** Accordion sections default to collapsed. User taps to expand individually.

### Claude's Discretion
- Exact accordion/chevron icon style and animation
- Transition animation for dashboard appearing after first prediction
- Risk tier color mapping for the collapsible header
- Mobile-specific font size adjustments
- Chat input positioning (fixed bottom vs flow)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Frontend Layout (Phase 4 outputs)
- `frontend/src/App.tsx` — Current two-panel layout with hard-coded `w-2/3`/`w-1/3`
- `frontend/src/components/ChatPanel.tsx` — Chat interface component
- `frontend/src/components/DashboardPanel.tsx` — Dashboard container with all sub-components
- `frontend/src/components/dashboard/ProbabilityDisplay.tsx` — Probability + risk label
- `frontend/src/components/dashboard/GuidanceBar.tsx` — CSS gradient bar with pointer
- `frontend/src/components/dashboard/CostTable.tsx` — 4-row cost table
- `frontend/src/components/dashboard/InterpretationGuide.tsx` — Static text panel
- `frontend/src/components/dashboard/Abbreviations.tsx` — Static abbreviation reference

### State Management
- `frontend/src/context/ChatContext.tsx` — React Context with conversation state, prediction data, conversation_phase

### API Contract
- `backend/app/schemas/chat.py` — ChatResponse includes prediction (null before first run)
- `backend/app/schemas/prediction.py` — PredictionResult with probability, risk_tier, cost_estimates

### Configuration
- `frontend/vite.config.ts` — Vite config with Tailwind plugin
- `frontend/package.json` — Tailwind v4.2.2

### Phase 4 Context
- `.planning/phases/04-frontend/04-CONTEXT.md` — Desktop layout decisions (D-04 through D-16)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- All dashboard sub-components exist and render from prediction state — can be wrapped in accordion controls without internal changes
- ChatContext already tracks `prediction` (null vs PredictionResult) — use this to conditionally show/hide dashboard on mobile
- Tailwind v4.2.2 responsive prefixes (`md:`, `lg:`) available but currently unused

### Established Patterns
- All styling is Tailwind utility classes — no plain CSS files to modify
- Components receive data via React Context (useChat hook)
- Dashboard components are self-contained — each renders independently from prediction state

### Integration Points
- `App.tsx` line 17: `flex flex-1 min-h-0` — main content container, needs mobile-first responsive conversion
- `App.tsx` lines 19/24: `w-2/3` and `w-1/3` — change to `w-full md:w-2/3` and `w-full md:w-1/3`
- New component needed: collapsible dashboard wrapper for mobile (wraps existing DashboardPanel content)
- New component needed: accordion/expandable section (reusable for cost table, interpretation, abbreviations)

</code_context>

<specifics>
## Specific Ideas

- Collapsed dashboard header shows "45% — High Risk" with risk-tier color background
- On mobile, the three accordion sections (cost, interpretation, abbreviations) each show a chevron icon and section title
- Dashboard appears with a smooth transition/animation when first prediction arrives
- Chat input should remain accessible at the bottom of the viewport on mobile

</specifics>

<deferred>
## Deferred Ideas

- Dark mode / theme toggle — future phase
- Pull-to-refresh for prediction updates — not needed for v1
- Swipe gestures between chat and dashboard — over-engineered for clinical tool
- Landscape mobile orientation handling — edge case, defer

</deferred>

---

*Phase: 05-mobile-layout*
*Context gathered: 2026-04-06 via interactive discussion*
