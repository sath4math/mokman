# Mokman

Property Operating System — public site, Owner, Tenant, Field Staff, and Admin
surfaces as one responsive web application.

See [`docs/Mokman_Product_Feature_Specification.md`](docs/Mokman_Product_Feature_Specification.md)
for what each screen/package contains, and
[`docs/Mokman_Phase_Wise_Development_Plan.md`](docs/Mokman_Phase_Wise_Development_Plan.md)
for the 8-phase build sequence and exit gates.

## Stack

- **Frontend**: Next.js (App Router) + TypeScript + Tailwind — `apps/web`, one
  app serving the public site and role-gated dashboards via route groups
  (`(public)`, `(owner)`, `(tenant)`, `(admin)`, `(field)`).
- **Backend**: FastAPI (Python) — `services/api`.
- **Database**: PostgreSQL via SQLAlchemy + Alembic migrations.
- **Jobs**: Celery + Redis.

## Local development

Prerequisites: Node.js, pnpm, Python 3.12+, [uv](https://docs.astral.sh/uv/),
and a Postgres connection string (a free [Neon](https://neon.tech) database
works well if you don't have Docker/Postgres installed locally).

```
make migrate     # apply Alembic migrations (needs DATABASE_URL set)
make dev-api     # FastAPI on http://localhost:8000
make dev-web     # Next.js on http://localhost:3000
```

Copy `.env.example` to `.env` in the repo root (used by both `apps/web` and
`services/api`) and fill in `DATABASE_URL` and `JWT_SECRET` (must be the same
value in both apps — the web app verifies API-issued JWTs itself).

After migrating, seed the two internally-provisioned demo accounts (Admin and
Field Staff aren't self-registrable — see below):

```
cd services/api && uv run python scripts/seed_demo_users.py
```

## Auth

- **Owners and Tenants** self-register at `/register`.
- **Admin and Field Staff** are seeded, not self-registered:
  - `admin@mokman.com` / `ChangeMe123!`
  - `field@mokman.com` / `ChangeMe123!`
  (change these before any real deployment)
- Login issues a JWT stored in an httpOnly cookie set by a Next.js Route
  Handler (`apps/web/app/api/auth/*`) — the browser never talks to the API
  directly. `apps/web/proxy.ts` gates the `(owner)`, `(tenant)`, `(admin)`,
  and `(field)` route groups by role.

## Repository layout

```
apps/web/       Next.js app (public site + Owner/Tenant/Admin/Field surfaces)
services/api/   FastAPI backend
packages/       Shared JS packages (ui, config, generated API client)
docs/           Product spec and phase-wise development plan
```

## Status

Phase 1 (Property Foundation) in progress. See the phase-wise development plan
for what's in scope and the definition of done for each phase.
