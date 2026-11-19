# DhaaraSathi — Antigravity handoff

This archive contains a polished React + TypeScript MVP for **DhaaraSathi**, an offline-first, human-validated spring revival and recharge planning platform for tribal areas.

## What is already implemented

The current app is a working demo workspace with synthetic Kandhamal pilot data. It includes:

- Persistent role-shaped dashboard navigation for Overview, Spring registry, Field capture, Action plans, Monitoring and Settings.
- Six realistic demo springs with local names, village context, priority, confidence, workflow status, flow readings and household dependence.
- Explainable rules-first priority scoring with visible factor breakdowns and low-confidence treatment.
- Indicative recharge-zone visualisation with an explicit **field validation required** guardrail.
- Intervention catalogue cards for contour trench, outlet protection and plantation restoration with cost ranges and feasibility reasons.
- Offline field-capture UI with a local sync queue concept, duplicate-safe record language and a clear “save to device” flow.
- Approval-state rail matching: `Draft → Field Submitted → Community Reviewed → Technical Validated → Officer Approved → In Progress → Completed → Monitoring`.
- Monitoring room with a before/after evidence chart and an “insufficient data” state.
- Configurable scoring-threshold settings and data-source provenance cards.
- Existing server/auth/database-ready scaffolding from the web-db-user template.

The demo uses synthetic data and does **not** claim real field results, underground water-flow proof or guaranteed discharge improvement.

## Continue in Antigravity

1. Connect Firebase Authentication and set the active Firebase project through environment variables. Use email/password or the organiser’s preferred provider for the first pilot.
2. Add Firebase custom claims or a `users/{uid}` role document for: `facilitator`, `village_representative`, `officer`, `technical_expert`, `admin`, and `public_viewer`.
3. Implement Firestore collections from the starter model below: `users`, `villages`, `springs`, `observations`, `assessments`, `recommendations`, `plans`, `monitoring`, `dataSources`, `auditLogs`, and `notifications`.
4. Move the demo records from `client/src/pages/Home.tsx` into Firestore seed data. Keep the UI’s current labels and uncertainty states.
5. Implement trusted Cloud Functions for assessment generation, recommendation ranking, idempotent offline-batch sync, plan state transitions, audit logging and report generation. The client must never write trusted score fields, `modelVersion`, `approvedBy` or audit fields directly.
6. Add Dexie/IndexedDB persistence for field observations. Generate a client record ID, store `pending | synced | failed`, retry only idempotently, and show the queue count in the sidebar/topbar.
7. Replace the illustrative map with the organiser-approved Leaflet/MapLibre layer. Store a precomputed GeoJSON recharge layer and expose source date, coverage and confidence.
8. Add Firebase Storage upload paths for private photos/audio. Record consent and store only secure paths/metadata in Firestore.
9. Add Firestore and Storage rules before pilot testing. Facilitators may only read/write assigned villages; public viewers may only read approved aggregate summaries; private field media must not be public.
10. Add Firebase Emulator Suite config, seed scripts, unit tests for role access, offline persistence, idempotent sync, low-confidence labels, rejection-with-reason and monitoring with sparse readings.

## Suggested Antigravity prompt

> Continue this DhaaraSathi React project from the current MVP. Keep the existing visual design, demo flow and uncertainty language. Connect Firebase Auth, Firestore, Storage, Cloud Functions and Emulator Suite. Replace only the in-memory demo data layer with typed services; do not remove the field-ready dashboard. Implement roles (`facilitator`, `village_representative`, `officer`, `technical_expert`, `admin`, `public_viewer`) with server-side enforcement. Use Dexie for offline field capture and an idempotent sync queue. Use a rules-first scoring baseline with factor values, reasons, model version and confidence stored server-side. Keep the label “AI-assisted indicative recharge zone; field validation required.” Require community and technical validation before officer approval, and audit every workflow transition. Do not fabricate model accuracy or field outcomes. Add the full Firestore/Storage rules, Cloud Functions, seed data for 3 villages and 8+ springs, and tests for the acceptance criteria in the original SIH brief.

## Important project paths

- `client/src/pages/Home.tsx` — current end-to-end demo UI and synthetic data contract.
- `client/src/index.css` — branded design tokens and responsive styling.
- `drizzle/schema.ts` — relational starter schema for a server-backed continuation.
- `firebase.json`, `firestore.rules`, `storage.rules` — Firebase handoff placeholders.
- `server/` — existing auth and tRPC server foundation from the web-db-user template.

## Design decisions

The design uses a warm paper background, deep forest navigation, marigold actions and coral priority signals. This is intentional: the interface should feel like a field notebook plus a decision room, not a generic blue admin panel. The MVP keeps English labels but has clear local-name fields and short, icon-supported sentences so a future translation layer can be added without redesigning the workflow.
