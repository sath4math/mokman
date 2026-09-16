# Mokman — Property Operating System

Live at **https://www.mokman.com**. Monorepo: `apps/web` (Next.js 16
frontend) + `services/api` (FastAPI backend), built phase-by-phase per
`docs/Mokman_Phase_Wise_Development_Plan.md`.

This file is the project's status log — read it first when picking this
work back up after any interruption, before touching code.

## Architecture

- **Frontend**: `apps/web`, Next.js 16 (App Router), pnpm workspace. Styling
  is **CSS Modules only** — no Tailwind, no inline styles. Shared primitives
  live in `apps/web/styles/ui.module.css`; everything else is a colocated
  `.module.css` next to its component/page.
- **Backend**: `services/api`, FastAPI + SQLAlchemy 2.0 + Alembic, managed
  via `uv`. One **modular monolith** (deliberate choice — see "Decisions"
  below), organized as `app/modules/<domain>/{schemas,service,router}.py`.
- **Auth**: JWT via python-jose, argon2 hashing. Browser never talks to
  FastAPI directly — Next.js Route Handlers hold the httpOnly session
  cookie and proxy everything through `apps/web/app/api/backend/[...path]/route.ts`.
- **Storage**: Cloudflare R2 (S3-compatible), presigned upload/download URLs.
- **Deployment**: GitHub → Railway (FastAPI, Dockerfile runs
  `alembic upgrade head` on every deploy) + Vercel (Next.js) → custom
  domain via GoDaddy DNS.

### Decisions worth knowing before changing anything

- **Modular monolith, not microservices.** The user asked about
  microservices once; confirmed it was a "general preference," not a hard
  requirement, and agreed to stay with the monolith. Don't re-split into
  services without an explicit new instruction.
- **Ledger is append-only.** `LedgerEntry` rows are never updated or
  deleted — corrections are offsetting entries. Don't add UPDATE paths to it.
  Existing `LedgerEntry.amount` uses `Float` (matching `Lease`/`Inspection`'s
  existing convention), not `Decimal` — this was a deliberate consistency
  choice, not an oversight.
- **Vendor integrations are deferred, one layer at a time**: KYC
  verification (Phase 1), e-signature (Phase 2 — lease "signing" is just
  both parties clicking acknowledge, timestamped), payment gateway
  (Phase 3 — rent payments are manually recorded with method + reference
  note, not a live Razorpay/PayU integration). Each of these is designed
  so the real vendor slots in later as an additional path into the same
  data model, not a rewrite.
- Every phase went through a written plan (scope explicitly cut down from
  the full phase-doc scope to a proportionate slice) approved by the user
  before implementation. If resuming mid-phase, check whether an approved
  plan file describes the current work before improvising.

## Status

### ✅ Phase 1 — Property Foundation (done, live, verified in prod)
Owner registration/KYC (manual, no third-party verification API), property
registration + hierarchy, document vault (real R2 storage, presigned
URLs), owner dashboard. Admin/Field Staff accounts are seeded, not
self-registered.

### ✅ Phase 2 — Tenant & Lease Management (done, live, verified in prod)
Tenant registration/profile, lease creation (owner enters tenant's email —
no invite-email vendor needed), in-app acknowledgment as e-signature
stand-in, move-in/move-out inspections with checklist/photos via the
document vault, lease → property status sync (occupied/vacant).
Deferred: complaint raising, multi-channel notifications (SMS/WhatsApp/
email/push) — pushed to Phase 4's workflow engine; unit-level leases
(leases attach to `Property`, not `Unit`).

### ✅ Phase 3 — Rent & Financial Management (done, live, verified in prod for owner+tenant)
- `RentInvoice`: lazily generated per billing period from lease terms,
  escalation-aware (`Lease.annual_escalation_percentage` applied per
  elapsed year). Status recomputed from the ledger on every read — no
  scheduler/cron needed.
- `LedgerEntry`: immutable transaction log backing both rent
  reconciliation and deposit settlement (rent_payment, mokman_fee,
  deposit_collected/deduction/refund, expense).
- Rent payments recorded manually (method + reference note); each payment
  auto-derives an 8% Mokman fee entry (`MOKMAN_FEE_PERCENTAGE` constant in
  `app/modules/rent/service.py`).
- Lease activation auto-records `deposit_collected`; a fully signed-off
  move-out inspection can `settle-deposit`, which validates
  deduction+refund equals the original deposit before writing the ledger
  entries.
- `Expense`: owner-submitted = auto-approved with an immediate ledger
  entry; admin-submitted = pending until the property owner approves it.
  This is the **first real Admin Portal screen** (`/admin/expenses`) —
  everything before this was a placeholder feature list.
- `GET /finance/statement`: per-property or owner-aggregate monthly
  rollup (rent collected, expenses, Mokman fee, net payable).
- Deferred: live payment gateway, PDF/Excel export, full property P&L /
  budget-vs-actual / portfolio yield reports, late-fee notifications,
  expense receipt documents.

**Known verification gap (not a functional bug):** the admin-specific
Phase 3 steps (admin login → submit expense → owner approves) are fully
verified **locally** but not re-verified against production, because the
production admin password isn't known to this session — it was randomly
rotated during the demo-password security fix and shown once in a
terminal that's no longer available. Local `scripts/seed_demo_users.py
--reset` only touches the **local** dev database, not production's. To
close this gap: either get the current production admin credentials from
the user, or run the reset script against Railway's production container
(rotates a live credential — confirm with the user first, don't just do it).

### ✅ Phase 4a — Maintenance Ticketing (done, live, verified in prod for owner+tenant)
Phase 4 ("Property Operations") is explicitly the doc's largest phase, so
it's split: this pass is ticketing only.
- `MaintenanceTicket`: states simplified to
  open → assigned → in_progress → resolved → closed (+ reopen from
  closed) — not the doc's full Complaint→Estimate→Approval→Invoice
  chain. Cost tracking reuses Phase 3's `Expense`/ledger rather than a
  parallel pipeline.
- Raised by tenant/owner/admin; assigned by owner/admin to a
  `field_staff` account (internal-only this pass, no vendor model);
  started/resolved by the assignee or owner/admin; closed by
  owner/admin; reopened by owner/raiser/admin.
- Evidence photos via the document vault (`owner_type=ticket`, same
  extension pattern as lease/inspection in Phase 2).
- `app/modules/maintenance/service.py` reuses
  `inspections.service.verify_property_access` for "owner or
  tenant-with-a-lease" checks rather than re-deriving it a third time.
- `properties` `GET /{id}` now also allows a tenant with a lease on
  that property (was owner-only) — needed for the tenant ticket form's
  property picker, and generally correct.
- `components/ticket-detail.tsx` is shared across all four roles
  (owner/tenant/field_staff/admin) via a `viewerRole` prop, same shape
  as `lease-detail.tsx`. Field Staff's `/field` page stopped being a
  placeholder and is now a real "My Jobs" list. Admin's second real
  screen (`/admin/tickets`) after Phase 3's expenses page.
- Deferred at the time to **Phase 4b** (vendor operations — see below
  for the slice actually delivered) and **Phase 4c**: preventive
  maintenance (asset service calendars), utility management,
  society/government coordination, SLA automation (needs a real
  scheduler, not proportionate yet), and the Phase 2 `Inspection`
  model's "formalization" (ticket-triggered/scheduled inspection
  types) — the ticket's own document vault already covers this pass's
  "closed with evidence" need.
- Same known verification gap as Phase 3: field-staff/admin production
  login isn't re-verified here either (owner+tenant flows are).

### 🧱 Phase 4b — Vendor Operations (deployed; owner+tenant flows not yet re-verified in prod)
Core vendor loop only, cut down from the full doc scope the same way
4a cut ticketing from all of Phase 4.
- `Vendor`: standalone directory entity (`app/models/vendor.py`), **not**
  a `User` — vendors don't log in (internal resource model, not a
  marketplace, per the product spec). Admin manages the directory via
  `/admin/vendors`; `is_active` doubles as this pass's lightweight
  blacklist toggle.
- `MaintenanceTicket.assigned_vendor_id` sits alongside the existing
  `assigned_to` (field_staff) FK — exactly one is set at a time, enforced
  in `assign_ticket`. `POST /maintenance/tickets/{id}/assign` now accepts
  either `assigned_to` or `assigned_vendor_id`; the shared
  `ticket-detail.tsx` assignment dropdown groups both option sets. A
  vendor has no login, so only owner/admin drive a vendor-assigned
  ticket's lifecycle (start/resolve/close) — the field_staff
  self-service path doesn't apply to vendor-assigned tickets.
- `Expense.vendor_id` (nullable FK) lets a vendor invoice flow through
  the **existing** Phase 3 expense-approval → ledger pipeline
  unchanged; the ledger entry's `reference_note` carries the vendor
  name rather than adding a new ledger column.
- Deferred to **Phase 4c**: rate cards, performance scoring, a formal
  blacklist workflow (reason/history/reinstatement — this pass is just
  an `is_active` toggle), vendor self-service login, smart
  vendor↔ticket-category matching in the assignment picker, plus
  everything already deferred from 4a (utility management,
  society/government coordination, preventive maintenance, SLA
  automation, Inspection-model formalization).
- **Deployed.** Verified against local Postgres end-to-end (vendor CRUD,
  ticket-assignment validation including the exactly-one-assignee rule
  and inactive-vendor rejection, a vendor-linked expense flowing through
  approval → ledger → finance statement) plus local
  `ruff`/`mypy`/`pnpm lint`/`typecheck`/`build`. Pushed to `main` and
  confirmed live in prod (`/vendors` in the API's `openapi.json`,
  `/admin/vendors` resolving) — but that's route-existence verification
  only, not a full authenticated owner/tenant walkthrough in prod like
  earlier phases got, on top of the standing admin/field-staff
  prod-login gap noted under Phase 3.

### 🧱 Phase 4c — Vendor Polish + Preventive Maintenance + Utility Management + Society/Govt Coordination (deployed; owner+tenant flows not yet re-verified in prod)
4a and 4b each cut Phase 4's full scope down to one proportionate slice.
Four items remained: vendor-ops polish, preventive maintenance, utility
management, and society/government coordination. I recommended keeping
those as four more sequential sub-phases (same cadence as 4a→4b) since
bundling them reintroduces the size/risk problem that caused the
original split — the user explicitly chose to bundle all four into one
4c instead. The discipline that changed as a result: proportionate-slice
thinking still applies *within* each of the four areas, just not *across*
them anymore.
- **Vendor ops polish** (extends 4b's `app/modules/vendors/`):
  `VendorRateCard` (nested CRUD, `/vendors/{id}/rate-cards` — reference
  pricing only, not auto-applied to an `Expense` amount) and
  `VendorRating` (`POST /vendors/{id}/ratings`, validates the ticket is
  `closed` and assigned to that vendor; `VendorOut.average_rating`
  computed on read, not stored). Blacklisting is now a real workflow —
  `POST /vendors/{id}/blacklist|reinstate` require/record a reason via
  the **existing** generic `AuditLog` table (`GET /vendors/{id}/history`
  reads it back) — `is_active` is no longer settable through the plain
  `PATCH`, so every deactivation has a reason on record.
- **Preventive maintenance**: new `MaintenanceSchedule`
  (`app/modules/maintenance_schedules/`) with a *stored* `next_due_on`
  (recomputed on `log-service`, unlike `RentInvoice`'s per-read status —
  it only changes when a service is logged). No scheduler, no
  auto-generated tickets: due items are a read-only list
  (`?due_only=true`); acting on one is a manual
  `POST /maintenance/tickets` via the existing flow.
- **Utility management**: new `UtilityConnection` + `UtilityBill`
  (`app/modules/utilities/`). `responsibility` (owner/tenant) records who
  *should* pay; `paid_at` is administrative record-keeping only —
  **deliberately not wired to the ledger**, since "who's responsible" and
  "what the owner's ledger owes" are different questions this pass
  doesn't try to auto-reconcile (verified: marking a bill paid left the
  finance statement untouched). No consumption-alert automation, same
  "needs a real scheduler" reasoning already applied to SLA automation.
- **Society/government coordination**: new `ComplianceDue`
  (`app/modules/compliance/`) covers both society dues and government
  tax tracking with one model — they're structurally identical per the
  doc's own grouping. Notices and NOCs aren't a new model at all: they
  reuse the **existing** document vault (`owner_type="property"`, new
  `document_type` values `"noc"`/`"society_notice"`/`"tax_receipt"`) —
  verified an upload against a real property with zero document-module
  code changes.
- All four owner-facing surfaces are new panels on the owner property
  detail page (`apps/web/app/(owner)/owner/properties/[id]/page.tsx`),
  matching its existing `expenses-panel`/`tickets-panel` composition
  pattern. **Scope cut from the plan during implementation**: no separate
  `/admin`-side screens for preventive maintenance/utilities — admin
  already manages tickets/expenses via global lists, not per-property
  panels, and these three domains are inherently property-scoped, so a
  new "admin browses one property's ops" surface would have been its own
  feature, not a proportionate add-on here.
- Deferred to a later phase: vendor self-service login/portal,
  auto-generating tickets from a due schedule, consumption alerts or any
  notification/scheduled-job infrastructure, auto-posting utility/
  compliance payments to the ledger, SLA automation, and the Phase 2
  `Inspection` model's ticket-triggered formalization.
- **Deployed.** Verified against local Postgres end-to-end (rate cards, a
  rating produced against a closed vendor-assigned ticket yielding a
  nonzero `average_rating`, blacklist→reinstate producing two `AuditLog`
  rows with the reason intact, a maintenance schedule's `next_due_on`
  recomputing after `log-service` and showing up in `due_only`, a utility
  bill markable paid without touching the ledger, a compliance due
  markable paid, and a NOC uploaded via the existing document vault) plus
  local `ruff`/`mypy`/`pnpm lint`/`typecheck`/`build`. Pushed to `main`
  and confirmed live in prod (all four modules' routes present in
  `openapi.json`, `/owner/properties/new` and `/admin/vendors` resolving)
  — route-existence verification only, same gap as 4b.

### 🧱 Phase 4d — Inspection Formalization + SLA Automation + Field Staff Offline PWA (deployed, SLA cron live)
After 4a-4c, every domain bullet in Phase 4's original scope was covered
except two things the phase's own exit gate calls for: tickets "routed
with SLA" and a technician who "works offline in the field." Both need a
different kind of engineering than 4a-4c's reuse-heavy CRUD slices. I
recommended scoping just the inspection-formalization item (still the
same CRUD shape as before) and treating SLA automation and the offline
PWA as their own separate scoping conversations, since both introduce
genuinely new infrastructure/architecture this codebase has never used.
The user chose to close out all three in one 4d, after two explicit
architecture decisions up front:
- **SLA firing mechanism**: an external cron hitting a protected internal
  endpoint, not an in-process scheduler and not a compute-on-read-only
  badge — the only one of the three options that's a genuine scheduled
  job.
- **Field Staff offline scope**: full PWA offline-first (service worker +
  local action queue), not a lighter resilient-web retry layer — this is
  what "offline" actually means in the doc's exit gate.

**Inspection formalization**: `InspectionType` gained `scheduled` and
`ticket_triggered`, plus `scheduled_for`/`triggered_by_ticket_id`/
`follow_up_notes`/`follow_up_due_on` columns on the **existing**
`Inspection` model (`app/models/inspection.py`) — exactly what that
model's own docstring said Phase 4 would do to it, back in Phase 2.
`GET /inspections?upcoming_only=true` mirrors `MaintenanceSchedule`'s
`due_only` filter. Owner property page gets an Inspections panel;
ticket detail gets a "Schedule inspection" action for owner/admin.

**SLA automation**: `MaintenanceTicket.sla_due_at` is set once at
creation from priority (urgent=4h → low=168h, `PRIORITY_SLA_HOURS` in
`maintenance/service.py`). `POST /internal/maintenance/sla-check` is
authenticated by a shared-secret header (`X-Cron-Secret` /
`SLA_CRON_SECRET`, not a user JWT — this call has no user session) and
does a single `UPDATE ... WHERE sla_breached_at IS NULL AND sla_due_at <
now() RETURNING id`, naturally idempotent against overlapping cron runs
with no lock needed. Each newly-breached ticket gets an `AuditLog` row
(`action="ticket.sla_breached"`) — the same audit pattern 4c introduced
for vendor blacklisting. `redis` is already a declared, unused dependency
(`pyproject.toml`) but this deliberately doesn't reach for it — a single
`UPDATE` doesn't need a queue or a lock.

**SLA cron is now live**: `.github/workflows/sla-cron.yml`, a scheduled
GitHub Actions workflow (`*/15 * * * *` + manual `workflow_dispatch`),
`POST`s to `<railway-url>/internal/maintenance/sla-check` directly —
**not** through `www.mokman.com/api/backend/...`, because
`apps/web/app/api/backend/[...path]/route.ts` only ever forwards the
`Authorization` and `Content-Type` headers, so it silently drops
`X-Cron-Secret` on every request (this cost a debugging round-trip: the
first live run 401'd through the proxy before the workflow was pointed
at Railway's URL directly). The URL and secret live as `SLA_API_URL` /
`SLA_CRON_SECRET` **GitHub repository secrets** (Settings → Secrets and
variables → Actions), matched by a same-named `SLA_CRON_SECRET`
**Railway environment variable** on the `web` service (Railway's
generic default name for what's actually the FastAPI backend here —
worth remembering next time this needs finding again, since Railway
doesn't name it after the repo folder `services/api`). The workflow
normalizes a schemeless/trailing-slash `SLA_API_URL` defensively
(defaults to `https://`, strips a trailing `/`) after the *actual* first
failure turned out to be exactly that: the secret was saved without
`https://`, so curl defaulted to `http://` and Railway's edge 301'd it
to https, which curl doesn't follow.
- GitHub Actions caveats worth knowing: `schedule` triggers are
  best-effort (can slip several minutes under load — fine here), and
  GitHub auto-disables scheduled workflows after 60 days of no repo
  activity on any branch, silently, until someone reopens the Actions
  tab and re-enables it.

**Field Staff offline PWA**: hand-rolled, no new npm dependency —
`apps/web/public/field-manifest.json` + `field-sw.js` (network-first
falling back to cache, registered with `{scope: "/field/"}` so it never
touches owner/tenant/admin) plus `apps/web/lib/offline-queue.ts` (a
small IndexedDB wrapper). `ticket-detail.tsx`'s `post()` — used by
field_staff's start/resolve actions — falls back to
`enqueueAction(...)` instead of erroring when offline; a `FieldPwaClient`
component (mounted from the new `app/(field)/layout.tsx`) flushes the
queue on the `online` event and on mount. Mutation queuing deliberately
lives in plain client JS rather than the service worker, since
Background Sync isn't reliably supported everywhere (notably Safari) —
the `online`-event flush is the real mechanism, Background Sync would
only ever be a bonus.
- **Explicitly cut**: offline photo/evidence capture (queuing binary
  blobs through IndexedDB and orchestrating a two-step presign+PUT
  afterward is materially bigger than the text-mutation queue above).
- **Verification gap**: I verified the manifest/service-worker files
  serve correctly and that the manifest `<link>` appears only on `/field`
  for a real field_staff session (absent from `/admin`), but did **not**
  browser-test the actual offline queue/flush behavior (would need
  Playwright with network throttling) — everything else in this phase
  was hit directly via the API.
- **Deployed.** Local `ruff`/`mypy`/`pnpm lint`/`typecheck`/`build` all
  clean; backend verified end-to-end locally (SLA breach flagging incl.
  the idempotency check and the `AuditLog` row, both new inspection types
  plus `upcoming_only`). Pushed to `main` and confirmed live in prod
  (all new/changed routes present in `openapi.json`,
  `field-manifest.json`/`field-sw.js` serving), and the SLA cron itself
  is confirmed running via a successful live `sla-check` call (see
  above) — this still carries the same route-existence-only
  prod-verification caveat as 4b/4c for everything else in this phase.

### ✅ Phase 4 — Property Operations: complete (4a-4d, exit gate met)
Phase 4's own exit gate — *"a maintenance issue can be raised by anyone,
routed with SLA, assigned to a vendor or technician who works offline in
the field, closed with evidence, and invoiced, with an owner able to see
the whole trail"* — is now fully satisfied across 4a-4d. Still
deliberately outside scope: the Field Staff App's checklists/GPS
check-in-out/material-usage tracking, since those overlap with Phase 5's
own "SOPs, checklists, technician check-in/out" quality-control scope —
building them now would mean redoing them once Phase 5 formalizes the
surrounding diagnosis→estimate→quality-check→warranty workflow around
them.

### 🧱 Phase 5a — Diagnosis → Estimate → Approval (deployed; owner+tenant flows not yet re-verified in prod)
Phase 5 ("Mokman Managed Services") is the same size class Phase 4 was
(8-10 weeks per the doc) before that got split, so it gets the same
sequential-slice treatment. The user chose to start with just the
diagnosis→estimate→approval piece — the state-machine change everything
else in Phase 5 (quality control, warranty/reporting, the service
catalog) builds on top of.
- `MaintenanceTicket`'s lifecycle gains an **optional** pre-assignment
  chain: `open → diagnosed → estimated → approved → assigned → ...`
  (`app/models/maintenance.py`). Optional, not mandatory — a ticket can
  still go straight `open → assigned` exactly as it always has for
  simple jobs; forcing a lightbulb-replacement through three approval
  steps would contradict this project's own proportionate-slice ethos
  and would've been a breaking change to every existing 4a-4d flow.
- `estimated_cost` is a **quote gating assignment, not a financial
  transaction** — the actual `Expense`/ledger entry is still recorded
  post-hoc through the existing Phase 3 flow once work is done,
  unchanged. Keeps 4a's own stated principle intact: no parallel
  accounting pipeline.
- Owner-auto-approve mirrors `create_expense`'s exact pattern
  (`expenses/service.py`'s `is_owner_of_property` branch): if the
  *owner* estimates their own ticket, it's auto-approved in the same
  call (there's no one else to approve it from). If *admin* estimates on
  the owner's behalf, it lands in a real pending state that only the
  **property owner** can approve or reject — no admin bypass, mirroring
  `approve_expense`'s `_require_property_owner` exactly (verified: admin
  attempting to approve its own submitted estimate correctly 403s).
- Rejecting an estimate (`POST .../reject-estimate`, owner-only) drops
  the ticket back to `open` — verified it's then immediately assignable
  again directly, confirming the cost gate is genuinely optional/
  escapable, not a one-way trap.
- Four new endpoints: `POST /maintenance/tickets/{id}/diagnose`,
  `.../estimate`, `.../approve`, `.../reject-estimate`. `assign_ticket`'s
  allowed-from-status check gained `APPROVED` alongside the existing
  `OPEN`/`ASSIGNED` — the only change to previously-existing logic.
- **Explicitly not in this slice** (later 5b/5c/5d): no before/after
  evidence requirement on diagnosis (the ticket's existing document
  vault already covers photos), no SLA-clock pause while a ticket waits
  on diagnosis/estimate/approval (the clock keeps running unchanged — a
  real limitation, flagged rather than silently accepted), no
  service-category catalog, no checklists/warranty/reporting.
- **Deployed.** Verified against local Postgres end-to-end: the simple
  `open → assign` path is unaffected; the full admin-diagnoses →
  admin-estimates → owner-approves chain works with each guard rail
  (early assignment 409s, admin-approve 403s) firing correctly; owner
  self-estimate auto-approves in one call; reject-estimate returns a
  ticket to `open` and it's re-assignable immediately. Plus local
  `ruff`/`mypy`/`pnpm lint`/`typecheck`/`build`. Pushed to `main` and
  confirmed live in prod (`/diagnose`/`/estimate`/`/approve`/
  `/reject-estimate` present in `openapi.json`) — route-existence
  verification only, same gap as every phase since 4b.

### 🧱 Phase 5b — Quality Control: checklists, check-in/out, evidence, rework (deployed; owner+tenant flows not yet re-verified in prod)
Continues Phase 5's sequential-slice split. This covers the
"in-the-moment, per-job" half of the doc's quality-control bullet:
**SOPs/checklists, technician check-in/out, before/after evidence,
rework tracking.** Warranty + repeat-failure + cost-variance monitoring
are held for 5c, which needs real historical/reporting infrastructure
per the doc's own technical note — a different kind of build than this
slice, which (like 5a) is entirely "extend the existing ticket
lifecycle, reuse aggressively."
- **Checklists reuse `Inspection.checklist`'s exact JSONB-dict shape**
  (`app/models/inspection.py`) rather than a new items table. New
  `ChecklistTemplate` (admin-managed, one per ticket `category`) is
  auto-attached to `MaintenanceTicket.checklist` the moment
  `assign_ticket` runs, if a template matches that category — verified a
  `hvac` template's three items landed on a freshly-assigned ticket
  automatically.
- **Optional, not mandatory — same principle as 5a's cost gate.** A
  category with no template resolves exactly as it always has, gate-free
  (verified explicitly: assigning/starting/resolving a `other`-category
  ticket with zero checklist and zero evidence succeeded normally).
- **Quality gate on resolve, when a checklist exists**: every item must
  be checked (`ChecklistIncompleteError` → 409) **and** at least one
  `Document` with `document_type="after_photo"` must exist against the
  ticket (`MissingEvidenceError` → 409), checked via the **existing**
  `documents.service.list_documents` — zero new document-module code,
  same trick 4c used for NOCs. Verified both gates fire independently
  (checklist-complete-but-no-photo still blocks), then both succeed
  together.
- **GPS check-in/out folded into the existing `start`/`resolve`
  endpoints** as optional `latitude`/`longitude` (captured client-side
  via the browser's native Geolocation API, never blocking the action on
  permission denial) rather than new endpoints or a new dependency —
  also the first time these transitions get timestamped at all
  (`check_in_at`/`check_out_at`). Verified coordinates round-trip
  correctly on both ends.
- **Rework tracking is just a counter**: `reopen_ticket` (already
  `CLOSED`-only) increments `rework_count` — reopening a closed ticket
  already only happens when finished work turns out unsatisfactory, so
  no separate tracking mechanism was needed. Verified it increments on
  reopen.
- **Backward compatibility preserved deliberately**: `start`'s body
  changed from none to an all-optional `StartRequest`, defaulted in the
  router (`data: StartRequest = StartRequest()`) so a bodyless call (like
  any client that hasn't been updated) still works — verified directly.
- New admin screen `/admin/checklist-templates`. `ticket-detail.tsx`
  gained inline checklist checkboxes, rework/check-in/out display, and
  the document vault's `documentTypes` for tickets grew
  `before_photo`/`after_photo`.
- **Known UI staleness, not a functional gap**: the "complete the
  checklist" / "upload a photo" hints shown while resolving read from a
  page-load snapshot of documents, not a live count — if evidence is
  uploaded without a page refresh the hint won't update, but the actual
  resolve call still re-checks live and enforces correctly regardless.
- **Deployed.** Verified against local Postgres end-to-end (see bullets
  above) plus local `ruff`/`mypy`/`pnpm lint`/`typecheck`/`build`. Pushed
  to `main` and confirmed live in prod (checklist-template routes present
  in `openapi.json`, `/admin/checklist-templates` resolving) —
  route-existence verification only, same gap as every phase since 4b.

### 🧱 Phase 5c — Warranty, Repeat-Failure Tracking, Cost-Variance Reporting (deployed; owner+tenant flows not yet re-verified in prod)
Final slice of Phase 5's quality-control bullet. 5a and 5b extended the
ticket lifecycle with zero new infrastructure; 5c is a different kind of
build — the doc's own technical note says repeat-failure and
cost-variance tracking *"need historical queries across the ticket/
service data... plan reporting/analytics tables here."* Consistent with
every prior phase's proportionate-slice approach, "reporting tables"
here means **aggregate queries against existing tables**, the same
approach Phase 3's `GET /finance/statement` already uses — not a new
analytics subsystem.
- **One deliberate un-deferral**: 4b's plan explicitly left `Expense`
  with no FK to `MaintenanceTicket` ("no hard FK... this pass").
  Cost-variance can't be computed without linking an expense to the
  ticket it pays for, so this slice adds `Expense.ticket_id` now that
  there's a real need for it.
- **Warranty**: `close_ticket` gained an optional `warranty_days`,
  computing `warranty_expires_on` (same field name/type as 4c's
  `MaintenanceSchedule.warranty_expires_on`) — verified closing with
  `warranty_days: 90` sets the date correctly.
- **Repeat-failure detection is tied to warranty, not an arbitrary
  day-count constant.** At ticket creation, a prior **closed** ticket on
  the same property+category with an still-active warranty
  auto-flags the new ticket `is_repeat_failure` with `related_ticket_id`
  set — verified this fires correctly for a matching category and
  (critically) does *not* fire for a different category on the same
  property. No warranty set on the prior job means it never fires —
  optional, same principle as every gate in 5a/5b.
- **Cost-variance report**: new `GET /maintenance/reports/summary`
  (property-scoped for owners, owner-aggregate or admin-global when
  `property_id` is omitted — mirrors `/finance/statement`'s exact
  owner-vs-property split, reusing `get_owned_property`/
  `list_properties_for_owner` from `properties/service.py`). Verified at
  all three scopes; critically, `total_actual_cost` correctly counted
  *only* the one expense explicitly linked via `ticket_id` out of many
  unlinked historical expenses already sitting on the same test
  property, confirming the join is precise rather than double-counting.
- **No frontend UI in this slice** — backend/reporting only, by design
  (unlike every other phase). `apps/web/lib/types.ts` was still kept in
  sync with the new fields (zero UI consumes them yet) to avoid type
  drift.
- **Deployed.** Verified against local Postgres end-to-end (see bullets
  above) plus local `ruff`/`mypy`/`pnpm lint`/`typecheck`/`build`. Pushed
  to `main` and confirmed live in prod (`/maintenance/reports/summary`
  present in `openapi.json`) — route-existence verification only, same
  gap as every phase since 4b.

### 🧱 Phase 5d — Service Category Catalog + Managed-Service Request Intake (deployed; owner+tenant flows not yet re-verified in prod)
Last piece of Phase 5's original doc scope: *"Managed service request
intake... auto-categorization, priority, eligibility, estimated
completion"* and *"Full managed-service category catalog."* 5a-5c
extended the ticket lifecycle/quality-control side; this slice is about
what happens **before** a ticket even exists.
- **Additive, not enforced — same principle as every phase since 4b.**
  `MaintenanceTicket.category` stays free-text, unchanged. The new
  `ServiceCategory` catalog only ever *supplies defaults when a match
  exists* — a category with no catalog entry behaves exactly as it did
  before this phase (verified explicitly: `medium` priority, the
  untouched `PRIORITY_SLA_HOURS`-only SLA). This avoided having to
  migrate the several things that already match on the existing
  free-text category (`ChecklistTemplate` from 5b, vendor rate cards,
  repeat-failure detection from 5c).
- **Auto-categorization, reframed honestly**: no ML/text classification
  — `TicketCreate.priority` became optional, and an omitted priority now
  resolves to a matching category's `default_priority` instead of the
  old flat `MEDIUM` fallback. Verified: an `emergency_response` category
  (`default_priority=urgent`, `estimated_completion_hours=2`) correctly
  produced `priority: urgent` with `sla_due_at` ~2h out — not the
  priority table's flat 4h for urgent — and an explicit `priority` in
  the request still overrides the category default.
- **Eligibility, deliberately lightweight**: just `is_active` on the
  catalog entry — verified deactivating a category correctly rejects
  new tickets in it (400). This is **not** a package-tier eligibility
  engine; that's explicitly Phase 6 scope and reaching into it now would
  break the sequential-slice discipline this whole build has followed.
- **"System-identified" tickets stay deferred** (e.g. auto-raising from
  an overdue `MaintenanceSchedule`) — 4c already explicitly cut this;
  not reopening that decision here.
- Reuses the **existing** `ticket_priority` Postgres enum type for
  `ServiceCategory.default_priority` (no new `CREATE TYPE`). New admin
  screen `/admin/service-categories`. Both ticket-raising forms (owner
  property detail page, tenant tickets page) now source their category
  dropdown from the catalog, falling back to the old hardcoded list when
  the catalog is empty, with a new "Auto (based on category)" priority
  option so the category default is actually reachable from the UI
  instead of always being overridden by an implicit `"medium"`.
- **Deployed.** Verified against local Postgres end-to-end (see bullets
  above) plus local `ruff`/`mypy`/`pnpm lint`/`typecheck`/`build`. Pushed
  to `main` and confirmed live in prod
  (`/maintenance/service-categories` present in `openapi.json`,
  `/admin/service-categories` resolving) — route-existence verification
  only, same gap as every phase since 4b.
- **Phase 5 status: fully closed (5a-5d)**, matching its full original
  doc scope — same kind of completion marker Phase 4 got after 4d.

### 🧱 Phase 6a — Owner Package/Plan Tier Foundation (deployed; owner+tenant flows not yet re-verified in prod)
Phase 6's doc scope centers on a labour-service **eligibility engine**:
whether a job is package-included, chargeable, or needs escalation.
That's meaningless without owners actually having a package/plan tier —
and **no such concept existed anywhere in this codebase** before this
slice. Every model across Phases 1-5 was checked; nothing on `Property`
or `OwnerProfile` represented a subscription tier, despite the product
spec (`docs/Mokman_Product_Feature_Specification.md:109-139`) defining
four real Owner Packages — **Starter, Managed, Full Care, Complete** —
with "Complete" explicitly being *"everything, including in-house
workforce & intelligence"* (i.e. Phase 6's own labour services are
spec'd as a Complete-tier feature).
- **Data only — deliberately no enforcement.** Every feature built in
  Phases 1-5 was built with zero tier-gating, as if every owner were on
  Complete. Retroactively gating all of that would be a large,
  cross-cutting, high-risk change touching dozens of already
  production-verified endpoints — not a "foundation" step, and not what
  Phase 6's own doc scope actually asks for (its eligibility engine is
  specifically about labour-service jobs, not the whole product).
  Verified explicitly: creating a property, raising a ticket, and
  logging an expense all still work identically regardless of an
  owner's package value.
- `OwnerProfile` gains `package` (`OwnerPackage` enum: `starter`
  (default), `managed`, `full_care`, `complete`), same
  `str_enum_column` pattern as this model's existing `ownership_type`/
  `kyc_status` fields. **Zero service-layer code changes** —
  `upsert_profile`'s existing generic `model_dump()`-based
  create/update already handles it since it's just another
  `OwnerProfileIn` field, which is about as clean a confirmation as
  possible that this is purely additive.
- Verified the full round-trip: a fresh owner who never sets `package`
  defaults to `starter` on profile creation; setting it explicitly to
  `complete` persists and round-trips on read.
- **Scope boundary**: Tenant Packages (Standard/Verified/Priority, spec
  `:141-156`) are deliberately out of scope — a tenant support/
  verification-perk tier, not tied to Phase 6's labour-eligibility
  engine, which is about a technician dispatched to the *owner's*
  property under the *owner's* plan.
- **Explicitly deferred**: admin overriding another owner's package (no
  "admin views one specific owner" screen exists anywhere in this Admin
  Portal today — building one just to expose this single field would be
  its own feature, not a foundation step); any actual eligibility/gating
  logic that reads this field (a later Phase 6 slice).
- Owner profile form (`/owner/profile`) gained a "Plan" section with a
  labeled dropdown using the spec's own positioning taglines (e.g.
  "Complete — everything, including in-house workforce &
  intelligence"), not a bare enum value.
- **Deployed.** Verified against local Postgres end-to-end (see bullets
  above) plus local `ruff`/`mypy`/`pnpm lint`/`typecheck`/`build`. Pushed
  to `main` and confirmed live in prod (`OwnerPackage`/`package` present
  in `openapi.json`) — route-existence verification only, same gap as
  every phase since 4b.

### 🧱 Phase 6b — Labour-Service Eligibility Engine (deployed; owner+tenant flows not yet re-verified in prod)
6a added `OwnerProfile.package` as inert data with zero enforcement
anywhere. This slice builds the thing Phase 6's own doc calls "the hard
part of this phase": a rules engine determining whether a job is
package-included, chargeable, needs a third party, is out of scope, or
needs escalation — built as *"configurable rules/policies, not
hardcoded conditionals"* per the doc's own technical guidance.
- **Only two of the five outcomes get real enforcement**, confirmed with
  the user, each reusing machinery that already exists rather than
  inventing new workflow: `escalate` reuses 5a's entire
  diagnose→estimate→approve chain — a ticket flagged `escalate` can no
  longer be assigned straight from `open`, it must reach `approved`
  first (zero new workflow code). `third_party` adds one guard to the
  existing assignment exactly-one-of-assignee check — such a ticket can
  only be assigned to a vendor, never internal field staff. `included`,
  `chargeable`, and `out_of_scope` are informational tags only —
  confirmed explicitly that `out_of_scope` does **not** block ticket
  creation, unlike 5d's inactive-category check.
- New `ServiceEligibilityRule` (`app/models/maintenance.py`): one row
  per (`service_category_id`, `package`) pair with a unique constraint,
  an `outcome`, and optional `notes`. A ticket's category+package
  combination with no matching row simply gets no
  `eligibility_outcome` — the engine only ever adds information/gates
  for combinations someone has actually configured, same "optional"
  principle as every gate since 5a.
- `create_ticket` resolves the owner's package via
  `property.owner_id → OwnerProfile.package` (defaulting to `starter` if
  no profile row exists, matching 6a's own default) and looks up a rule
  for `(service_category.id, package)`, setting
  `MaintenanceTicket.eligibility_outcome` if found.
- CRUD via `POST`/`GET`/`PATCH`/`DELETE /maintenance/eligibility-rules[/{id}]`
  (admin-only mutations, owner+admin read — owners can see what's
  covered under their own plan) on new admin screen
  `/admin/eligibility-rules`. `ticket-detail.tsx` shows the resolved
  outcome as a badge (escalate styled like the SLA-breach danger badge).
- **Fair-use frequency/value thresholds and material/cost tracking
  against entitlements are explicitly not in this slice** — that needs
  its own historical-tracking design, same split reasoning as 5b/5c, and
  is deferred to a later 6c.
- **Migration gotcha worth remembering**: reusing the same `sa.Enum`
  object for both an explicit `.create(checkfirst=True)` call and a
  column type inside `op.create_table` double-triggers `CREATE TYPE` —
  `op.create_table`'s DDL re-emits type creation for any Enum column
  object that hasn't been told the type already exists, unlike
  `op.add_column` (6a's migration used the same-object pattern safely
  only because it's an `add_column`, not a `create_table`). Fixed by
  following 5d's migration's existing `postgresql.ENUM(name=...,
  create_type=False)` reuse pattern for the table's columns.
- **Verified against local Postgres end-to-end**: an escalate rule
  correctly resolves onto a new ticket and blocks `/assign` from `open`
  with 409 until the ticket passes through diagnose→estimate→approve,
  after which assignment succeeds; a third_party rule blocks assigning
  to field_staff with 400 while a vendor assignment succeeds; a ticket
  in a category with no matching rule at all assigns exactly as every
  prior phase, unchanged. Plus local `ruff`/`mypy`/`pnpm lint`/
  `typecheck`/`build`.
- **Deployed.** Pushed to `main` and confirmed live in prod
  (`eligibility-rules`/`EligibilityOutcome`/`eligibility_outcome` present
  in `openapi.json`, `/admin/eligibility-rules` resolving) — route-
  existence verification only, same gap as every phase since 4b.

### 🧱 Phase 6c — Fair-Use Frequency/Value Limits (implemented, verified locally — not yet deployed)
6b explicitly deferred "fair-use frequency/value thresholds" as its own
slice. Phase 6's exit gate calls for "flagging anything that breaches
fair-use limits for owner approval" — this slice delivers exactly that.
Remaining Phase 6 scope (material/time tracking against entitlements,
full workforce management — technician KYC/shifts/attendance/leave/
training) is confirmed out of scope here; the user chose the narrowest
of three offered options specifically because workforce management
alone is doc-sized like Phase 5 and material tracking is a genuinely
new domain, both better as separate later slices.
- **Piggybacks directly on 6b's existing machinery rather than adding
  new tables or a new outcome/exception type.** A limit breach is just
  another reason a ticket needs the diagnose→estimate→approve gate
  before assignment (reuses 6b's `EscalationApprovalRequiredError`) and,
  for value breaches, a reason 5a's owner-self-estimate auto-approve
  doesn't fire.
- `ServiceEligibilityRule` gains three independent, optional columns:
  `max_occurrences`/`period_days` (a frequency limit — "no more than N
  of this category per owner within this many days") and `max_value` (a
  per-job value ceiling). Every rule from 6b has all three `null`, so
  existing rules are completely unaffected — same "optional" principle
  as every gate since 5a.
- `MaintenanceTicket` gains `fair_use_breached: bool`, independent of
  `eligibility_outcome` — a rule's configured outcome (e.g. `included`)
  and "this specific ticket exceeded the owner's entitlement" are
  separate facts. Set at `create_ticket` time via a plain aggregate
  count query against existing tickets (same shape as the existing
  repeat-failure query, no new tracking table — consistent with 5c's
  "reporting = queries against existing tables" precedent) for frequency
  breaches, and at `estimate_ticket` time for value breaches (cost isn't
  known until then).
- `estimate_ticket`'s owner-auto-approve condition changed from
  `is_owner_of_property` to `is_owner_of_property and not
  ticket.fair_use_breached` — a value breach always lands in `ESTIMATED`
  requiring an explicit `approve` call, even from the property owner,
  since it's no longer a routine self-quote within their plan's
  entitlement. Verified this doesn't regress the un-breached case (an
  under-cap estimate still auto-approves exactly as 5a left it).
- `assign_ticket`'s existing ESCALATE-only guard broadened to
  `eligibility_outcome == ESCALATE or fair_use_breached` — same
  exception, no new one.
- No new endpoints: 6b's existing eligibility-rule CRUD already passes
  request bodies through generically, so the three new optional fields
  flow through untouched. Admin eligibility-rules screen gained three
  numeric inputs; `ticket-detail.tsx` gained a second danger badge
  ("Fair-use limit exceeded") shown alongside, not replacing, the
  existing SLA/escalate badges.
- **Verified against local Postgres end-to-end**: a rule with
  `max_occurrences=1`/`period_days=30` lets the first ticket in that
  category assign normally, flags the second as breached and blocks
  `/assign` with 409 until diagnose→estimate→approve; a rule with
  `max_value=200` leaves an owner's over-cap self-estimate in
  `estimated` (not auto-approved) until an explicit `approve`, while an
  under-cap estimate still auto-approves; a ticket with no matching rule
  at all is completely unaffected. Plus local `ruff`/`mypy`/
  `pnpm lint`/`typecheck`/`build`.
- **Not yet deployed.**

## Local development

```powershell
# Backend (services/api) — uv manages the venv
uv run alembic upgrade head          # apply migrations to local Postgres
uv run uvicorn app.main:app --port 8000   # NOT --reload on Windows; see gotcha below
uv run ruff check .
uv run mypy app

# Frontend (repo root, pnpm workspace)
pnpm --filter web dev      # port 3000
pnpm --filter web lint
pnpm --filter web typecheck
pnpm --filter web build

# Seed demo admin/field-staff accounts (local DB only)
uv run python scripts/seed_demo_users.py --reset
```

### Environment gotchas (Windows + OneDrive-synced repo)

- **PATH doesn't persist between PowerShell tool calls in this environment
  session** — every command needs
  `$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")`
  prefixed (plus appending `...\AppData\Roaming\Python\Python314\Scripts`
  for `uv` specifically, since it's a pip-installed script, not on the
  machine/user PATH).
- **`uv run uvicorn --reload` is unreliable on Windows for this project.**
  Its multiprocessing reload watcher can orphan child processes that keep
  the listening socket alive even after the parent exits, so a new
  `uvicorn --reload` invocation silently binds behind a stale process and
  serves old code indefinitely. If new routes don't show up in
  `/openapi.json` after an edit: check `netstat -ano | findstr :8000` and
  `Get-CimInstance Win32_Process -Filter "Name = 'python.exe'"` for
  leftover processes, kill everything on that port, then start **without**
  `--reload` and restart manually after each backend change.
- **OneDrive file locks** occasionally cause `uv sync`/`pnpm build` to fail
  with `EPERM`/`Access is denied` (especially deleting `.next/`). Retrying
  once, or deleting the locked directory first, resolves it.
- PowerShell `-Path` arguments treat `[id]` (a literal folder name in this
  Next.js App Router project) as a wildcard character class — `Test-Path`/
  `Remove-Item` on paths containing `[id]` need `-LiteralPath`, not `-Path`,
  or they silently no-op instead of erroring.
- **Long `git commit -m @'...'@` here-strings with markdown-style bullets
  (`-`) or arrows (`->`) can get mis-split by PowerShell's native-command
  argument passing**, producing `error: pathspec 'or' did not match any
  file(s)`-style failures with no useful indication of the real cause.
  Write the message to a file (e.g. in the scratchpad) and use
  `git commit -F <file>` instead — it's reliable regardless of message
  content.

## Deployment

Push to `main` → Railway redeploys `services/api` (Dockerfile runs
`alembic upgrade head` automatically before starting Uvicorn) and Vercel
redeploys `apps/web`. Both deploys are independent and take roughly
1–3 minutes; poll `https://www.mokman.com/api/backend/openapi.json` for
the expected new routes before running post-deploy verification — don't
assume the deploy finished just because `git push` returned.

Standard verification loop after any phase's backend+frontend land: local
ruff/mypy + pnpm lint/typecheck/build → local Postgres lifecycle test via
a PowerShell script hitting the API directly → local Playwright browser
flow → commit, push → poll for new routes in prod → production Playwright
flow. Playwright itself lives only in the session's scratchpad
(`node_modules/playwright*`), not as a repo dependency — it's reinstalled
per session as needed for manual verification, not part of CI.
