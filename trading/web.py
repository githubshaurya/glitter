import asyncio
import logging
import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from trading.broker import AlpacaBroker
from trading.config import Settings
from trading.main import build_application
from trading.models import now_utc, timestamp
from trading.repository import Repository, safe_json

STATIC = Path(__file__).parent / "static"
logger = logging.getLogger(__name__)


def run_worker_cycle(settings, repository):
    application = None
    try:
        application = build_application(settings)
        return application.run()
    except Exception as error:
        result = {"status": "ERROR", "error_type": type(error).__name__}
        try:
            repository.event("worker_error", "web", result)
        except Exception:
            # A database outage must not kill the scheduler while trying to journal the outage.
            logger.error(
                "Trading cycle failed and journal is unavailable: %s", type(error).__name__
            )
        return result
    finally:
        if application:
            application.broker.close()
            application.agent.close()
            application.repository.engine.dispose()


class ControlUpdate(BaseModel):
    mode: Literal["ACTIVE", "NO_NEW_RISK", "HALTED"]
    reason: str = Field(min_length=3, max_length=250)


def create_app(settings=None, repository=None, broker_factory=AlpacaBroker):
    settings = settings or Settings()
    repository = repository or Repository(settings.database_url)
    repository.initialize()

    stop = asyncio.Event()
    worker_state = {
        "running": False,
        "last_started_at": None,
        "last_finished_at": None,
        "last_result": None,
    }

    async def worker():
        while not stop.is_set():
            worker_state.update(running=True, last_started_at=now_utc().isoformat())
            try:
                result = await asyncio.to_thread(run_worker_cycle, settings, repository)
            except Exception as error:
                logger.error("Trading worker cycle failed: %s", type(error).__name__)
                result = {"status": "ERROR", "error_type": type(error).__name__}
            worker_state.update(
                running=False, last_finished_at=now_utc().isoformat(), last_result=result
            )
            try:
                await asyncio.wait_for(stop.wait(), timeout=settings.poll_seconds)
            except TimeoutError:
                pass

    @asynccontextmanager
    async def lifespan(app):
        task = asyncio.create_task(worker())
        try:
            yield
        finally:
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

    @app.get("/readyz", dependencies=[Depends(authenticate)])
    def readiness():
        try:
            repository.control()
            latest = next((run for run in repository.rows("runs", 100) if run["slot"]), None)
            unresolved = repository.unresolved()
        except Exception:
            return JSONResponse({"ready": False, "reason": "Database unavailable"}, status_code=503)
        finished = worker_state["last_finished_at"]
        recent = (
            finished
            and (now_utc() - timestamp(finished)).total_seconds() <= 2 * settings.poll_seconds + 60
        )
        successful = worker_state["last_result"] and worker_state["last_result"]["status"] not in {
            "ERROR",
            "DEGRADED",
        }
        healthy_decision = not latest or latest["status"] not in {
            "ERROR",
            "DEGRADED",
            "RUNNING",
            "ABANDONED",
        }
        uncertain = any(row["state"] in {"UNKNOWN", "SUBMITTING"} for row in unresolved)
        ready = bool(recent and successful and healthy_decision and not uncertain)
        return JSONResponse(
            safe_json({"ready": ready, "worker": worker_state, "uncertain_orders": uncertain}),
            status_code=200 if ready else 503,
        )

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
                "worker": worker_state,
                "equity": list(reversed(repository.rows("equity_snapshots", 2000))),
                "runs": repository.rows("runs", 30),
                "intents": repository.rows("order_intents", 100),
                "decisions": repository.rows("decisions", 100),
                "observations": repository.observation_headers(100),
                "experiments": repository.rows("experiments", 10),
            }
        )

    @app.get("/api/decisions/{observation_id}", dependencies=[Depends(authenticate)])
    def trace(observation_id: str):
        result = repository.decision_trace(observation_id)
        if result is None:
            raise HTTPException(404, "Decision not found")
        return safe_json(result)

    @app.post("/api/control", dependencies=[Depends(authenticate)])
    def control(update: ControlUpdate):
        repository.set_mode(update.mode, update.reason)
        cancellation = None
        if update.mode == "HALTED":
            broker = None
            try:
                broker = broker_factory(settings)
                cancellation = broker.cancel_all()
                repository.event("cancel_open_orders", "dashboard", {"responses": cancellation})
            except Exception as error:
                cancellation = {
                    "error_type": type(error).__name__,
                    "retry": "next monitoring cycle",
                }
                repository.event("cancel_error", "dashboard", cancellation)
            finally:
                if broker:
                    broker.close()
        return safe_json({"control": repository.control(), "cancellation": cancellation})

    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    return app
