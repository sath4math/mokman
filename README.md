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
Docker (for Postgres/Redis).

```
make infra-up    # Postgres + Redis via docker compose
make migrate     # apply Alembic migrations
make dev-api     # FastAPI on http://localhost:8000
make dev-web     # Next.js on http://localhost:3000
```

Copy `.env.example` to `.env` and fill in values before running the API.

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
