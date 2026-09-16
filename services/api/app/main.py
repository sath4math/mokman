from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.auth.router import router as auth_router
from app.modules.documents.router import router as documents_router
from app.modules.expenses.router import router as expenses_router
from app.modules.finance.router import router as finance_router
from app.modules.inspections.router import router as inspections_router
from app.modules.leases.router import router as leases_router
from app.modules.maintenance.router import router as maintenance_router
from app.modules.owner.router import router as owner_router
from app.modules.properties.router import router as properties_router
from app.modules.rent.router import router as rent_router
from app.modules.tenant.router import router as tenant_router
from app.modules.vendors.router import router as vendors_router

app = FastAPI(title="Mokman API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(owner_router)
app.include_router(tenant_router)
app.include_router(properties_router)
app.include_router(leases_router)
app.include_router(inspections_router)
app.include_router(rent_router)
app.include_router(expenses_router)
app.include_router(finance_router)
app.include_router(maintenance_router)
app.include_router(documents_router)
app.include_router(vendors_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
