import asyncio
import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from trading.broker import AlpacaBroker
from trading.config import Settings
from trading.main import build_application
from trading.repository import Repository, safe_json

STATIC = Path(__file__).parent / "static"


class ControlUpdate(BaseModel):
    mode: Literal["ACTIVE", "NO_NEW_RISK", "HALTED"]
    reason: str = Field(min_length=3, max_length=250)


def create_app(settings=None, repository=None, broker_factory=AlpacaBroker):
    settings = settings or Settings()
    repository = repository or Repository(settings.database_url)
    repository.initialize()

    stop = asyncio.Event()

    async def worker():
        while not stop.is_set():
            application = None
            try:
                application = build_application(settings)
                await asyncio.to_thread(application.run)
            except Exception as error:
                repository.event("worker_error", "web", {"error_type": type(error).__name__})
            finally:
                if application:
                    application.broker.close()
                    application.agent.close()
                    application.repository.engine.dispose()
            try:
                await asyncio.wait_for(stop.wait(), timeout=settings.poll_seconds)
            except TimeoutError:
                pass

    @asynccontextmanager
    async def lifespan(app):
        task = asyncio.create_task(worker())
        yield
        stop.set()
        await task

    app = FastAPI(
        title="Glitter Paper", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None
    )

    def authenticate(authorization: str = Header("")):
        expected = settings.dashboard_token.get_secret_value()
        supplied = authorization.removeprefix("Bearer ")
        if not expected or not secrets.compare_digest(supplied.encode(), expected.encode()):
            raise HTTPException(401, "Enter your dashboard token")

    @app.middleware("http")
    async def security_headers(request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
        )
        return response

    @app.get("/healthz")
    def health():
        return {"status": "ok", "paper_only": True}

    @app.get("/")
    def index():
        return FileResponse(STATIC / "index.html")

    @app.get("/api/overview", dependencies=[Depends(authenticate)])
    def overview():
        return safe_json(
            {
                "control": repository.control(),
                "policy": settings.public_policy(),
                "execution_enabled": settings.execution_enabled,
                "model": settings.groq_model,
                "equity": list(reversed(repository.rows("equity_snapshots", 2000))),
                "runs": repository.rows("runs", 30),
                "intents": repository.rows("order_intents", 100),
                "decisions": repository.rows("decisions", 100),
                "observations": repository.rows("observations", 100),
                "experiments": repository.rows("experiments", 10),
            }
        )

    @app.get("/api/decisions/{observation_id}", dependencies=[Depends(authenticate)])
    def trace(observation_id: str):
        observation = next(
            (o for o in repository.rows("observations") if o["id"] == observation_id), None
        )
        if not observation:
            raise HTTPException(404, "Decision not found")
        matching = [
            d for d in repository.rows("decisions") if d["observation_id"] == observation_id
        ]
        ids = {observation_id, *(d["id"] for d in matching)}
        orders = [i for i in repository.rows("order_intents") if i["decision_id"] in ids]
        ids.update(i["id"] for i in orders)
        return safe_json(
            {
                "observation": observation,
                "decisions": matching,
                "orders": orders,
                "events": [e for e in repository.rows("events") if e["correlation_id"] in ids],
            }
        )

    @app.post("/api/control", dependencies=[Depends(authenticate)])
    def control(update: ControlUpdate):
        repository.set_mode(update.mode, update.reason)
        cancellation = None
        if update.mode == "HALTED":
            broker = broker_factory(settings)
            try:
                cancellation = broker.cancel_all()
                repository.event("cancel_open_orders", "dashboard", {"responses": cancellation})
            except Exception as error:
                cancellation = {
                    "error_type": type(error).__name__,
                    "retry": "next monitoring cycle",
                }
                repository.event("cancel_error", "dashboard", cancellation)
            finally:
                broker.close()
        return safe_json({"control": repository.control(), "cancellation": cancellation})

    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    return app
