# Mokman — Phase-Wise Application Development Plan

**Product vision:** Mokman is a Property Operating System — not a listing or marketplace app. Owners hand over property responsibility to Mokman; Mokman's internal teams use the same system to operate, maintain, and improve each property end-to-end.

This plan translates the full feature list into 8 buildable phases, each with scope, cross-platform surfaces touched, team needs, technical considerations, dependencies, and an exit gate (the criteria that say "this phase is genuinely done, move on").

---

## How to read this plan

- Each phase builds on the data model and workflows of the one before it — the sequence is a dependency chain, not just a priority list.
- "Cross-platform features" (Owner App, Tenant App, Field Staff App, Admin Portal, Notifications, Security, Reporting) are **not a separate phase** — they're introduced incrementally, in the phase where they first become necessary, and thickened over time.
- Duration estimates assume a focused product team working in 2-week sprints. Treat them as a starting point to calibrate against your actual team size and velocity, not a commitment.

---

## Phase 1 — Property Foundation
**Theme:** Get a property and its owner into the system with a real, trustworthy digital record.

### Scope
- Owner onboarding: registration, mobile/email verification, passwordless login, KYC (PAN, Aadhaar/passport), bank details, multiple/joint ownership with percentage split, nominee, emergency contact, authorised representatives & PoA.
- Property registration: property ID generation, category, address + GPS, specifications (area, floors, units, amenities, furnishing), media (photos, videos, floor plans, 360°), status (vacant/occupied/under maintenance/etc.).
- Property structure hierarchy: Property → Building → Block/Tower → Floor → Unit → Room, plus parking, storage, common areas.
- Digital Property Passport: the permanent record that every later phase writes into (ownership, specs, documents, tenant/rent/maintenance/inspection/renovation history, valuation, sale history).
- Document vault: all core property documents with expiry tracking, renewal reminders, access permissions, version history, OCR-based reading, and search.
- Property dashboard: status, current tenant, rent, occupancy, lease expiry, pending maintenance, documents, health, recent activity.

### Cross-platform surfaces introduced
- **Owner App** (v1): registration, property list, property dashboard, document vault.
- **Internal Admin Portal** (v1): owner management, property management, document management.
- **Security baseline**: RBAC skeleton, encryption at rest, MFA, audit logs — build this now, not later; retrofitting security is expensive.

### Technical considerations
- Design the **property hierarchy and Digital Property Passport schema first** — nearly every later phase (tenant, rent, maintenance, inspections, assets, renovation, sale) attaches records to this backbone. Getting this data model wrong is the most expensive mistake to fix later.
- Document storage: use a proper object store (S3-class) with signed URLs, not database blobs; OCR can be a queued async job (e.g., Textract/Google Vision) rather than inline.
- KYC verification likely needs a third-party API integration (PAN/Aadhaar verification providers) — plan for vendor selection and compliance review (DPDP Act considerations for Aadhaar data in India).

### Team
Backend (2), Frontend/mobile (2), 1 designer, 1 QA, 1 PM. A DevOps/infra person part-time to set up environments and CI/CD.

### Estimated duration
8–10 weeks.

### Exit gate
An owner can self-register, complete KYC, add a property with full details and documents, and see it on a working dashboard. Admin can view and manage all of this internally.

---

## Phase 2 — Tenant and Lease Management
**Theme:** Put a tenant into a property with a real lease and a clean move-in/move-out trail.

### Scope
- Tenant registration, profile, KYC, occupants, vehicles, pets, documents, communication history, internal rating.
- Tenant verification: identity, address, employment, references, police verification coordination, consent tracking.
- Lease management: full lease terms (dates, rent, deposit, lock-in, notice period, escalation, responsibilities), e-signature integration, stamp duty/registration coordination, renewal/termination workflows, expiry alerts.
- Move-in: scheduling, identity confirmation, key/access-card handoff, meter readings, condition checklist with photos/video, digital sign-off.
- Move-out: notice calculation, final inspection, damage assessment, utility/rent settlement, deposit calculation, key return, digital sign-off.
- Tenant communication: portal/app, complaint raising, reminders, notifications, WhatsApp/SMS/email/push.

### Cross-platform surfaces introduced
- **Tenant App** (v1): profile, lease view, move-in/move-out flows, complaint raising, notifications.
- **Owner App**: tenant view, lease status, move-in/out visibility.
- **Notifications**: build the multi-channel notification service now (SMS/email/WhatsApp/push) — it's needed continuously from here on.

### Technical considerations
- E-signature: integrate a provider (e.g., DocuSign, Leegality, or an India-specific Aadhaar eSign provider) rather than building signing infrastructure.
- Move-in/move-out checklists and photos should reuse the same "inspection" data model you'll formalize in Phase 4 — build it generically now to avoid rework.
- Lease versioning needs an append-only history model (never overwrite a signed lease).

### Team
Same core team, +1 backend for integrations (e-signature, verification APIs), +1 QA for workflow testing (lease/move-in/move-out are stateful, multi-step flows that need thorough testing).

### Estimated duration
8–10 weeks.

### Exit gate
A tenant can be verified, leased into a property with a digitally signed agreement, moved in with a documented condition report, and moved out with a settled deposit — all tracked end-to-end.

---

## Phase 3 — Rent and Financial Management
**Theme:** Make money move correctly — rent in, expenses tracked, owner paid.

### Scope
- Rent management: schedules, invoices, reminders, recurring records, multi-mode collection (UPI, bank transfer, gateway, cash recording), reconciliation, partial payments, overdue tracking, late fees, escalation history, receipts.
- Security deposit: ledger, adjustments, refunds, deductions (damage/outstanding rent/utility), settlement reports.
- Owner financials: monthly statements, all expense categories, Mokman fees, net settlement, payment history, approvals.
- Property accounting: income/expense ledgers, receivables/payables, cash flow, property-level P&L, budget vs. actual, invoice handling with duplicate detection, audit trail.
- Financial reports: monthly/annual statements, collection & outstanding reports, yield calculations (gross/net/occupancy-adjusted), portfolio reports, downloadable PDF/Excel.

### Cross-platform surfaces introduced
- **Owner App**: statements, payment history, approvals for expenses.
- **Tenant App**: rent payment, receipts, payment history.
- **Admin Portal**: full accounting console, expense approval workflows.

### Technical considerations
- **Payment gateway integration is the critical path here** — select and integrate early (Razorpay/PayU/similar in India), including webhook-based reconciliation, not polling.
- Treat this as a ledger system: use double-entry or at minimum an immutable transaction log, not editable balance fields — this matters enormously for audit and dispute resolution.
- PDF/Excel report generation can be a queued background job for large portfolios.
- This phase touches money directly — budget extra QA and a security review (PCI-adjacent handling even if the gateway is tokenized).

### Team
+1 backend with fintech/ledger experience, +1 QA specifically for financial reconciliation testing. Consider a short compliance/legal review of payment flows.

### Estimated duration
8–9 weeks.

### Exit gate
Rent collects automatically, reconciles correctly against the ledger, owners receive accurate monthly statements, and financial reports match manual audits for a pilot set of properties.

---

## Phase 4 — Property Operations
**Theme:** Turn "someone reported a problem" into a managed, SLA-bound workflow.

### Scope
- Maintenance ticketing: multi-source complaint creation, categorization, priority, SLA assignment, work orders, approvals, invoicing, closure, feedback.
- Maintenance workflow engine: Complaint → Assessment → Diagnosis → Estimate → Approval → Assignment → Work → Inspection → Invoice → Closure, with escalation rules and reopening.
- Property inspections: scheduled and event-triggered types, checklists, photo/video/GPS/timestamp capture, damage/cleanliness/safety assessment, reports, follow-up tasks.
- Preventive maintenance: asset service calendars, warranty/AMC reminders.
- Vendor operations (internal resource model, not marketplace): registration, KYC, rate cards, assignment, work orders, performance scoring, invoicing, blacklisting.
- Utility management: connections, meters, bills, responsibility allocation, consumption alerts.
- Society and government coordination: dues, notices, tax tracking, NOCs, document submission tracking.

### Cross-platform surfaces introduced
- **Field Staff App** (v1): assigned jobs, navigation, checklists, check-in/out, photos, material usage, offline mode. *This is a meaningfully large build on its own — offline sync is non-trivial.*
- **Admin Portal**: SLA monitoring, vendor management, work order dashboard.
- **Owner/Tenant Apps**: maintenance status visibility, inspection reports.

### Technical considerations
- This is the most **workflow-engine-heavy** phase. Consider a proper state-machine/workflow library rather than ad hoc status fields — the number of states and transitions (ticket, inspection, vendor job) will only grow in Phases 5–6.
- Field Staff App needs offline-first architecture (local queue, background sync) since technicians work in basements, remote sites, or poor-connectivity areas.
- SLA monitoring needs a scheduled job/event system (not just cron) to fire escalations reliably at scale.

### Team
+1–2 backend for workflow engine, +1 mobile developer focused on the Field Staff App and offline sync, +1 QA for field scenarios (device testing matters here).

### Estimated duration
10–12 weeks (this is the largest phase so far; consider splitting into 4a — Tickets & Inspections, 4b — Vendors & Utilities if timeline pressure is high).

### Exit gate
A maintenance issue can be raised by anyone, routed with SLA, assigned to a vendor or technician who works offline in the field, closed with evidence, and invoiced — with an owner able to see the whole trail.

---

## Phase 5 — Mokman Managed Services
**Theme:** Mokman stops routing requests and starts owning outcomes end-to-end.

### Scope
- Managed service request intake (owner, tenant, or system-identified), auto-categorization, priority, eligibility, estimated completion.
- End-to-end service management: diagnosis, site visit, scope, cost estimate, approval, assignment (internal or external specialist), scheduling, supervision, quality inspection, invoicing, warranty recording, closure.
- Full managed-service category catalog (plumbing through move-in/move-out prep to emergency response).
- Service quality control: SOPs, checklists, technician check-in/out, before/after evidence, rework tracking, service warranty, repeat-failure tracking, SLA and cost variance monitoring.

### Cross-platform surfaces introduced
No new app — this phase deepens the **Field Staff App** and **Admin Portal** built in Phase 4 with SOP-driven checklists and quality gates.

### Technical considerations
- This phase is largely a **process and data-model extension** of Phase 4's workflow engine (adds diagnosis, quality-control, and warranty states) rather than new infrastructure — reuse aggressively.
- SOP/checklist templates should be configurable data (admin-editable), not hardcoded, since service categories and standards will evolve.
- Repeat-failure and cost-variance tracking need historical queries across the ticket/service data built in Phase 4 — plan reporting/analytics tables (or a lightweight data warehouse) here rather than deferring to Phase 7.

### Team
Similar to Phase 4, with a slight shift toward Admin Portal/reporting engineers over new mobile work. Add operations/SOP input from the business side — this phase is as much about defining the service playbooks as building software.

### Estimated duration
8–10 weeks.

### Exit gate
A service request of any listed category can be fully diagnosed, quoted, approved, executed, quality-checked, and closed with warranty recorded — without the owner or tenant needing to find or manage a vendor themselves.

---

## Phase 6 — Mokman Labour Services
**Theme:** Bring the workforce in-house for eligible services, with strict guardrails against uncontrolled usage.

### Scope
- Workforce management: technician registration, KYC, skill classification, service areas, shifts, attendance, leave, GPS check-in/out, training, safety certification, performance scoring.
- Labour-service eligibility engine: determines whether a job is package-included, material-only chargeable, third-party, out of scope, or needs escalation/approval.
- Included labour service catalog and cost/material management: time tracking, material request/approval/consumption, wastage, actual-vs-estimate, subsidy and entitlement tracking.
- Labour-service controls: fair-use policy, frequency/duration/value limits, excluded categories, emergency rules, geographic limits, abuse detection, escalation for major work.

### Cross-platform surfaces introduced
- Extends **Field Staff App** into a full workforce-management tool (shifts, attendance, route planning).
- **Admin Portal**: workforce dashboard, eligibility rule configuration.

### Technical considerations
- **The eligibility engine is the hard part of this phase** — it's effectively a rules engine (package entitlements × job type × frequency × value thresholds). Build it as configurable rules/policies, not hardcoded conditionals, since packages and limits will change per plan tier over time.
- Attendance/shift/route planning may benefit from an existing HR-tech or field-service-management library/API rather than building from scratch — evaluate build-vs-buy here.
- Abuse/repeated-issue detection can start as rule-based (thresholds) and only needs ML once you have volume — don't over-engineer this early.

### Team
+1 backend for the rules engine, HR/ops domain input for policy design, continued mobile investment in the Field Staff App.

### Estimated duration
8–10 weeks.

### Exit gate
An in-house technician can be dispatched for an eligible job, with the system correctly determining what's covered, tracking material and time against entitlements, and flagging anything that breaches fair-use limits for owner approval.

---

## Phase 7 — AI and Property Intelligence
**Theme:** Turn the data collected in Phases 1–6 into answers, predictions, and automation.

### Scope
- AI Owner Assistant: natural-language Q&A over the owner's own portfolio data (income, vacancies, overdue rent, lease expiries, pending maintenance, spend, yield, expiring documents, pending approvals).
- Property Health Score: composite score from age, condition, inspections, maintenance frequency/recurrence, appliance age, tenant feedback, safety, PM compliance.
- Predictive maintenance: failure prediction, recurring-problem detection, replacement/painting/waterproofing/plumbing/electrical risk forecasting.
- AI rent intelligence: market rent estimation, escalation recommendations, vacancy-risk and renewal-probability prediction, locality trends.
- AI financial intelligence: expense categorization, anomaly/duplicate detection, cash-flow forecasting, yield/ROI, profitability comparison, budget recommendations.
- AI document assistant: OCR-driven classification/extraction, expiry alerts, lease clause extraction, agreement comparison, Q&A over documents.
- AI inspection/damage analysis: photo-based damage, leak, crack, and cleanliness detection; before/after comparison; inventory mismatch detection.

### Cross-platform surfaces introduced
No new app; this phase adds an AI/chat layer into the **Owner App** and enriches reports across all apps.

### Technical considerations
- **This phase depends entirely on data volume and quality from Phases 1–6** — sequence it last for a reason; don't start serious ML work before you have enough real inspection photos, maintenance tickets, and rent history to train or meaningfully prompt against.
- Start with LLM-based retrieval-augmented Q&A (owner assistant, document assistant) — this delivers value fast without training custom models.
- Predictive maintenance and damage-detection from photos are the most technically ambitious items here; consider starting with vendor computer-vision APIs before building custom models, and treat these as a later sub-phase if timeline is tight.
- Keep a human-in-the-loop on anything financial or damage-related (anomaly detection, damage assessment) — these should assist a human reviewer, not auto-decide, at least initially.

### Team
1–2 ML/AI engineers, 1 data engineer (to build the pipelines feeding models from Phases 1–6 data), existing backend team for integration.

### Estimated duration
10–14 weeks, and realistically ongoing/iterative rather than a hard finish line.

### Exit gate
Owners can ask natural questions about their portfolio and get accurate answers; property health scores and basic predictive alerts are live for a pilot set of properties; accuracy has been validated against real outcomes before wider rollout.

---

## Phase 8 — Complete Property Lifecycle
**Theme:** Cover the full life of the asset — from furniture to renovation to sale.

### Scope
- Asset and inventory management: full lifecycle tracking (purchase, warranty, service, repair, replacement, depreciation, disposal, transfer).
- Renovation and project management: request through handover, budgeting, contractor assignment, milestones, procurement, progress tracking, payment milestones, warranty.
- Smart property/IoT: locks, CCTV, sensors (water leak, smoke, gas), smart meters, remote monitoring and alerts.
- Insurance management: policies, premiums, claims, surveyor coordination, settlement tracking.
- NRI property management: overseas-specific onboarding, PoA, remote approvals, currency display, video inspections, tax-support coordination.
- Investment intelligence: valuation, yield, appreciation, ROI, buy-vs-rent, portfolio analysis, sell/hold recommendations.
- Sale, transfer and exit: readiness assessment, valuation, documentation, buyer/site-visit coordination, ownership/utility/society transfer, final settlement, archival.

### Cross-platform surfaces introduced
- **Owner App**: renovation tracking, insurance, investment dashboards, sale/exit flows.
- IoT device integrations are a distinct technical workstream from the rest of the app.

### Technical considerations
- IoT integration is hardware-dependent and vendor-specific (device SDKs, MQTT/webhook ingestion) — treat as a separate technical track that can run in parallel with the rest of this phase rather than blocking it.
- Renovation project management overlaps significantly with Phase 4/5's vendor and work-order infrastructure — reuse rather than rebuild.
- Sale/exit is the natural end of the Digital Property Passport lifecycle from Phase 1 — this is where that investment fully pays off (a complete, exportable property history for buyers/due diligence).

### Team
Continue core team; add IoT integration specialist if smart-property features are prioritized; legal/compliance input for sale and NRI workflows.

### Estimated duration
10–14 weeks (or split into sub-releases — Assets & Renovation, then IoT & Insurance, then Investment & Exit — given the breadth).

### Exit gate
A property's complete lifecycle — assets, renovations, insurance, and eventual sale — is captured in and supported by the same system that managed its day-to-day operations, with the Digital Property Passport as a genuinely complete, transferable record.

---

## Overall Timeline Summary

| Phase | Focus | Estimated Duration | Cumulative |
|---|---|---|---|
| 1 | Property Foundation | 8–10 wks | ~10 wks |
| 2 | Tenant & Lease Management | 8–10 wks | ~20 wks |
| 3 | Rent & Financial Management | 8–9 wks | ~29 wks |
| 4 | Property Operations | 10–12 wks | ~41 wks |
| 5 | Mokman Managed Services | 8–10 wks | ~51 wks |
| 6 | Mokman Labour Services | 8–10 wks | ~61 wks |
| 7 | AI & Property Intelligence | 10–14 wks | ~75 wks |
| 8 | Complete Property Lifecycle | 10–14 wks | ~89 wks |

**~18–21 months** end-to-end for the full scope, assuming one core product team working sequentially. Two realistic ways to compress this:

1. **Parallelize non-dependent tracks** once Phase 1's data model is stable — e.g., start Field Staff App groundwork during Phase 3, or begin IoT vendor evaluation during Phase 6 — rather than treating every phase as fully sequential.
2. **Ship a usable product earlier.** Phases 1–4 (~10 months) already constitute a complete, sellable property-management product (owner + tenant + maintenance + money). Phases 5–8 are genuine differentiators but not blockers to a first commercial launch — consider a soft launch after Phase 4 to start generating real usage data, which directly improves Phase 7's AI work.

## Team Growth Across Phases

| Phase | Core additions |
|---|---|
| 1–2 | Foundational team: 2 backend, 2 frontend/mobile, 1 designer, 1 QA, 1 PM |
| 3 | + fintech-experienced backend, + financial QA |
| 4 | + workflow-engine backend(s), + mobile dev for Field Staff App (offline-first) |
| 5–6 | + ops/SOP domain expert, + HR/field-service backend, + rules-engine backend |
| 7 | + 1–2 ML/AI engineers, + data engineer |
| 8 | + IoT integration specialist (as needed), legal/compliance input |

## Key Cross-Cutting Risks

- **Data model debt**: the Property Passport and workflow-state schemas from Phases 1 and 4 are load-bearing for everything after. Invest extra design review time there before writing code.
- **Payment and ledger correctness (Phase 3)**: reconciliation bugs are expensive and erode owner trust fast — budget real QA time, not just feature QA.
- **Offline-first mobile (Phase 4 onward)**: field connectivity issues are a common source of data loss/duplication bugs if sync logic is rushed.
- **AI accuracy (Phase 7)**: don't roll out predictive/financial AI features to all owners until validated against real outcomes on a pilot set — bad predictions here directly damage trust in the "we manage it for you" promise.
- **Vendor/API dependencies**: KYC verification, e-signature, payment gateway, and IoT device APIs are all external dependencies — start vendor selection and contracting early in the relevant phase, not when development starts.
