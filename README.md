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

### 🧱 Phase 4b — Vendor Operations (implemented, verified locally — not yet deployed)
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
- **Not yet deployed.** Verified against local Postgres end-to-end
  (vendor CRUD, ticket-assignment validation including the
  exactly-one-assignee rule and inactive-vendor rejection, a
  vendor-linked expense flowing through approval → ledger → finance
  statement) plus local `ruff`/`mypy`/`pnpm lint`/`typecheck`/`build`.
  Not yet pushed to `main`, so there's no prod verification to report
  — once it is, expect the same admin/field-staff prod-login
  verification gap noted under Phase 3.

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
