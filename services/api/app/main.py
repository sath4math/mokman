from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.auth.router import router as auth_router
from app.modules.documents.router import router as documents_router
from app.modules.owner.router import router as owner_router
from app.modules.properties.router import router as properties_router

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
app.include_router(properties_router)
app.include_router(documents_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
