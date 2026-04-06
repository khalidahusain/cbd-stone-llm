# Phase 5: Mobile Layout - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-06
**Phase:** 05-mobile-layout
**Areas discussed:** Breakpoint strategy, Dashboard visibility, Mobile navigation, Dashboard compaction

---

## Breakpoint Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Single at md (768px) | Below 768px = stacked mobile, above = current desktop. Simple. | ✓ |
| Single at lg (1024px) | Tablets also get mobile layout. Only full desktops get side-by-side. | |
| Two breakpoints (sm + lg) | Phone stacked, tablet narrower sidebar, desktop full layout. | |

**User's choice:** Single at md (768px)
**Notes:** Recommended option selected. Simplest approach covering phones vs everything else.

---

## Dashboard Visibility

| Option | Description | Selected |
|--------|-------------|----------|
| Hidden until prediction | Dashboard invisible until first prediction. Chat fills full screen initially. | ✓ |
| Always visible with placeholder | Dashboard always at top showing "Awaiting clinical data..." before prediction. | |
| Sticky header after prediction | Probability + risk tier stick to top as fixed bar after prediction. | |

**User's choice:** Hidden until prediction
**Notes:** Matches FRNT-04 "chat-first initially." Dashboard slides in above chat once prediction exists.

---

## Mobile Navigation

| Option | Description | Selected |
|--------|-------------|----------|
| Collapsible panel | Dashboard is collapsible/accordion at top. Collapsed shows summary. Chat always below. | ✓ |
| Tab switching | Two tabs: Chat and Dashboard. Only one visible at a time. | |
| Single scroll page | Dashboard stacked on top of chat. Scroll to navigate. | |

**User's choice:** Collapsible panel
**Notes:** Collapsed header shows probability + risk tier. Tap to expand. Chat always visible below.

---

## Dashboard Compaction

| Option | Description | Selected |
|--------|-------------|----------|
| Cost table only | Only cost table collapsible. Interpretation and abbreviations always visible. | |
| Cost + interpretation + abbreviations | All three secondary sections behind expandable controls. Core metrics always visible. | ✓ |
| Everything collapsible | Even guidance bar and intervention inside collapsible. Only summary header visible. | |

**User's choice:** Cost + interpretation + abbreviations
**Notes:** Probability, guidance bar, and intervention always visible. Cost table, interpretation guide, and abbreviations each behind their own accordion control.

---

## Claude's Discretion

- Accordion icon style and animation
- Transition animation for dashboard appearance
- Risk tier colors for collapsible header
- Mobile font size adjustments
- Chat input positioning on mobile

## Deferred Ideas

- Dark mode / theme toggle
- Pull-to-refresh
- Swipe gestures
- Landscape orientation handling
