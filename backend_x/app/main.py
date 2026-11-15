from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models  # noqa: F401  (enregistre les tables)
from .database import Base, SessionLocal, engine
from .routes import alerts, astronauts, indicators, measurements, simulation
from .seed import seed_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed_database(db)  # ne fait rien si la base est déjà remplie
    yield


app = FastAPI(title="M.O.O.N. API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"], allow_headers=["*"],
)


@app.get("/api/health", tags=["système"])
def health():
    return {"status": "ok"}


for r in (astronauts.router, indicators.router, measurements.router, alerts.router, simulation.router):
    app.include_router(r)
