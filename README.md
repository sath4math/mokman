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

### 🧱 Phase 4d — Inspection Formalization + SLA Automation + Field Staff Offline PWA (implemented, verified locally — not yet deployed)
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
`UPDATE` doesn't need a queue or a lock. **The actual Railway cron
schedule (recommended: every 15 minutes) still needs to be set up in
Railway's dashboard** — that's a deploy-console step outside this repo's
git history, same category as KYC/e-signature/payment-gateway vendor
selection in earlier phases.

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
- **Not yet deployed.** Local `ruff`/`mypy`/`pnpm lint`/`typecheck`/
  `build` all clean; backend verified end-to-end locally (SLA breach
  flagging incl. the idempotency check and the `AuditLog` row, both new
  inspection types plus `upcoming_only`). Once deployed, expect the same
  prod-verification gaps noted above, plus the cron-scheduling step this
  phase can't do from inside the repo.

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
