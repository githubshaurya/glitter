"""Serve historical simulations and the Alpaca paper desk on loopback."""

import argparse
import json
import os
import re
import signal
import subprocess
import sys
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from itertools import islice
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event, Lock, Thread
from time import monotonic
from urllib.parse import parse_qs, urlsplit
from uuid import uuid4

from sqlalchemy.exc import SQLAlchemyError

from trader.backtest.viewer_worker import ViewerWorker
from trader.reporting.star import StarJournal, preview_audit
from trader.reporting.trade_history import TradeHistory

ASSETS = Path(__file__).with_name("replay_viewer")
STATIC = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/viewer.css": ("viewer.css", "text/css; charset=utf-8"),
    "/viewer.js": ("viewer.js", "text/javascript; charset=utf-8"),
}


def make_server(
    port: int = 8765,
    *,
    host: str = "127.0.0.1",
    simulation_root: Path,
) -> ThreadingHTTPServer:
    from pydantic import ValidationError

    from trader.backtest.simulation import SimulationRequest, write_json

    pending_audits = {}
    pending_lock = Lock()
    paper_panel = None
    paper_setup_error = ""
    if os.environ.get("TRADER_PAPER_UI_ENABLED", "").lower() == "true":
        from trader.config import get_settings, get_trading_config
        from trader.paper_panel import PaperPanel
        from trader.services.common import make_broker
        from trader.store.repo import Store

        try:
            settings, cfg = get_settings(), get_trading_config()
            if not settings.realtime_enabled or not settings.managed_paper_enabled:
                raise ValueError("Enable the realtime and managed paper settings.")
            paper_panel = PaperPanel(
                Store(settings.database_url), make_broker(settings, cfg, "live", rate_limit_per_minute=30),
                cfg, execution_enabled=settings.execution_enabled,
            )
        except (ValueError, RuntimeError, OSError):
            paper_setup_error = "Check paper credentials, realtime settings, and managed paper settings."

    simulation_slot = Lock()
    worker = ViewerWorker() if os.environ.get("TRADER_VIEWER_WARM_WORKERS") == "1" else None
    simulations = {}
    running_simulations = set()
    simulations_lock = Lock()
    progress_cache = {}
    projected_simulations = set()
    archived_simulations = set()
    active_statuses = {"queued", "loading", "running", "waiting_for_quota"}

    def simulation_status(run_id, request, folder):
        path = folder / "progress.json"
        try:
            stat = path.stat()
            version = (stat.st_ino, stat.st_mtime_ns, stat.st_size)
            with simulations_lock:
                cached = progress_cache.get(run_id)
            if cached and cached[0] == version:
                progress = cached[1]
            else:
                progress = json.loads(path.read_text(encoding="utf-8"))
                with simulations_lock:
                    progress_cache[run_id] = (version, progress)
        except FileNotFoundError:
            progress = {"status": "queued", "decisions": [], "orders": []}
        with simulations_lock:
            if run_id in running_simulations and progress["status"] not in active_statuses:
                # The subprocess writes its last result before it exits and releases the run slot.
                progress = progress | {"status": "running"}
        return {**progress, "request": request, "id": run_id}

    def end_window_orders(progress):
        return [order for order in progress["orders"] if order.get("decision_index") is None
                and order.get("reason") in ("session_cutoff", "holding_deadline", "stop_loss", "take_profit")]

    def simulation_audit(run_id, request, folder, index, progress=None):
        if progress is None:
            progress = simulation_status(run_id, request, folder)
        if index == "cutoff":
            orders = end_window_orders(progress)
            if not orders:
                raise ValueError("Cutoff execution is unavailable.")
            outcome = "SESSION_CUTOFF" if any(o["reason"] == "session_cutoff" for o in orders) else "AUTOMATIC_EXITS"
            detail = {"as_of": orders[0]["submitted_at"], "result": {"outcome": outcome}, "risk": [],
                      "recommendation": {"action": orders[0]["side"]}}
        else:
            index = int(index)
            if not any(row["index"] == index for row in progress["decisions"]):
                raise ValueError("The decision has not been recorded.")
            detail = json.loads((folder / f"decision-{index}.json").read_text(encoding="utf-8"))
            orders = [order for order in progress["orders"] if order.get("decision_index") == index]
        detail["orders"] = orders
        detail["skeptic_enabled"] = request.get("skeptic_enabled", True)
        detail["fills"] = [
            dict(order_id=order["id"], side=order["side"], qty=order["filled_qty"],
                 price=order["fill_price"], t=order["filled_at"],
                 **({"position_effect": order["position_effect"]} if order.get("position_effect") else {}))
            for order in orders if order.get("filled_qty", 0) > 0
        ]
        return detail

    def run_worker(folder, timeout):
        if worker is not None:
            worker.run(folder, timeout)
            return
        with (folder / "worker.log").open("w", encoding="utf-8") as log:
            subprocess.run([sys.executable, "-m", "trader.backtest.simulation", str(folder)],
                           stdout=log, stderr=log, timeout=timeout, check=True)

    def simulate(run_id, request, folder):
        try:
            run_worker(folder, max(1500, 108 * request["duration_minutes"] + 120))
        except (OSError, subprocess.SubprocessError) as exc:
            progress = simulation_status(run_id, request, folder)
            message = "Simulation reached its time limit." if isinstance(exc, subprocess.TimeoutExpired) else (
                "Simulation stopped unexpectedly. See the local Docker logs for details."
            )
            progress.update(status="failed", error=message)
            write_json(folder / "progress.json", progress)
            if (log_file := folder / "worker.log").is_file():
                print(log_file.read_text(encoding="utf-8", errors="replace")[-8000:], file=sys.stderr, flush=True)
        finally:
            with simulations_lock:
                simulation_slot.release()
                running_simulations.discard(run_id)
                projection_wake.set()

    star_url = os.environ.get("TRADER_VIEWER_DATABASE_URL")
    star = StarJournal(star_url)
    history = TradeHistory(star_url, create=not star_url)
    projection_stop = Event()
    projection_wake = Event()
    recovery_queue = {}
    history_retry = {}
    if star_url:
        for folder in simulation_root.glob("*/"):
            if not folder.is_dir() or not re.fullmatch(r"[a-f0-9]{32}", folder.name):
                continue
            if (folder / ".archived").is_file() or not (folder / "request.json").is_file():
                continue
            try:
                request = SimulationRequest.model_validate_json((folder / "request.json").read_text(encoding="utf-8"))
                recovery_queue[folder.name] = (request.model_dump(mode="json"), folder)
            except (OSError, ValueError):
                print(f"Could not recover simulation {folder.name}.", file=sys.stderr)

    def archive_simulations():
        with simulations_lock:
            finished = [(run_id, saved) for run_id, saved in simulations.items()
                        if run_id not in running_simulations and run_id not in archived_simulations]
        for run_id, (request, folder) in [*recovery_queue.items(), *finished]:
            if history_retry.get(run_id, 0) > monotonic():
                continue
            try:
                progress = simulation_status(run_id, request, folder)
                if progress["status"] in active_statuses:
                    progress = {**progress, "status": "failed", "error": "The simulation was interrupted before it finished."}
                indexes = [row["index"] for row in progress["decisions"]]
                if end_window_orders(progress):
                    indexes.append("cutoff")
                audits = [(index, simulation_audit(run_id, request, folder, index, progress)) for index in indexes]
                history.save(progress, audits)
            except (OSError, ValueError, KeyError, TypeError, SQLAlchemyError) as exc:
                print(f"Trade history save delayed for {run_id} ({type(exc).__name__}).", file=sys.stderr)
                history_retry[run_id] = monotonic() + 5
                continue
            if star_url:
                try:
                    (folder / ".archived").touch()
                except OSError:
                    print(f"Could not checkpoint the archive for {run_id}.", file=sys.stderr)
            recovery_queue.pop(run_id, None)
            archived_simulations.add(run_id)
            history_retry.pop(run_id, None)

    def projection_inputs(checkpoint):
        with pending_lock:
            pending = list(pending_audits.items())
        for identifier, (detail, dimensions) in pending:
            yield identifier, lambda detail=detail: detail, dimensions
        with simulations_lock:
            simulation_runs = list(simulations.items())
        for run_id, (request, folder) in simulation_runs:
            if run_id in projected_simulations:
                continue
            progress = simulation_status(run_id, request, folder)
            indexes = [row["index"] for row in progress.get("decisions", [])]
            if end_window_orders(progress):
                indexes.append("cutoff")
            pending_indexes = [index for index in indexes if f"simulation:{run_id}:{index}" not in checkpoint]
            if not pending_indexes and progress["status"] not in active_statuses:
                projected_simulations.add(run_id)
            for index in pending_indexes:
                yield f"simulation:{run_id}:{index}", lambda run_id=run_id, request=request, folder=folder, index=index, progress=progress: (
                    simulation_audit(run_id, request, folder, index, progress)
                ), {"symbol": request["symbol"], "portfolio": "simulation", "strategy": "intraday-council"}
    def project_in_background():
        retry_at = {}
        checkpoint = None
        while not projection_stop.is_set():
            batch = []
            archive_simulations()
            try:
                if checkpoint is None:
                    checkpoint = star.projected_ids()
                now = monotonic()
                batch = list(islice((
                    job for job in projection_inputs(checkpoint)
                    if job[0] not in checkpoint and retry_at.get(job[0], 0) <= now
                ), 32))
                for identifier, load, dimensions in batch:
                    if projection_stop.is_set():
                        return
                    if identifier in checkpoint:
                        continue
                    try:
                        star.project(identifier, load(), **dimensions)
                        checkpoint.add(identifier)
                        with pending_lock:
                            pending_audits.pop(identifier, None)
                        retry_at.pop(identifier, None)
                    except (OSError, ValueError, KeyError, TypeError):
                        # A missing snapshot is retried after its writer publishes it.
                        retry_at[identifier] = monotonic() + 15
            except (OSError, ValueError, SQLAlchemyError):
                checkpoint = None
                projected_simulations.clear()
                batch = []  # The durable facts remain the checkpoint after database recovery.
            projection_wake.wait(0.2 if len(batch) == 32 else 2)
            projection_wake.clear()

    class Handler(BaseHTTPRequestHandler):
        def check_host(self):
            allowed = {f"{host}:{self.server.server_port}" for host in ("localhost", "127.0.0.1")}
            if self.headers.get("Host") not in allowed:
                self.send_error(403)
                return False
            return True

        def send_data(self, body, content_type="application/json; charset=utf-8", status=200):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; object-src 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def send_json(self, body, status=200):
            self.send_data(json.dumps(body, allow_nan=False).encode(), status=status)

        def send_audit(self, decision_id, load_detail, *, symbol, portfolio, strategy):
            try:
                with pending_lock:
                    pending = pending_audits.get(decision_id)
                if pending:
                    detail = preview_audit(decision_id, pending[0], **pending[1])
                else:
                    try:
                        detail = star.get(decision_id)
                    except SQLAlchemyError:
                        detail = None
                    if detail is None:
                        source = load_detail()
                        dimensions = dict(symbol=symbol, portfolio=portfolio, strategy=strategy)
                        detail = preview_audit(decision_id, source, **dimensions)
                        with pending_lock:
                            pending_audits[decision_id] = (source, dimensions)
                            if len(pending_audits) > 32:
                                pending_audits.pop(next(iter(pending_audits)))
                        projection_wake.set()
            except (OSError, ValueError, KeyError):
                self.send_json({"error": "The recorded decision could not be read."}, 404)
                return
            self.send_json(detail)

        def do_GET(self):
            if not self.check_host():
                return

            url = urlsplit(self.path)
            path = url.path
            content_type = "application/json; charset=utf-8"
            if path == "/health/live":
                self.send_json({"status": "alive"})
                return
            elif path == "/api/paper":
                if paper_panel is None:
                    self.send_json({"enabled": False, "setup_error": paper_setup_error})
                    return
                try:
                    self.send_json(paper_panel.status())
                except Exception:
                    self.send_json({"error": "Paper account status is unavailable. Check the broker and database."}, 503)
                return
            elif path == "/health/ready":
                try:
                    star.ready()
                    history.ready()
                except SQLAlchemyError:
                    self.send_json({"status": "unready", "dependency": "audit_database"}, 503)
                    return
                self.send_json({"status": "ready"})
                return
            elif path == "/api/trade-history" or path.startswith("/api/trade-history/"):
                self.send_trade_history(path, url.query)
                return
            elif path in STATIC:
                asset, content_type = STATIC[path]
                body = (ASSETS / asset).read_bytes()
            elif path == "/api/simulations":
                with simulations_lock:
                    runs = list(simulations.items())
                summary = (simulation_status(run_id, *saved) for run_id, saved in reversed(runs))
                self.send_json({"runs": [
                    {**{key: detail[key] for key in ("id", "status", "request")},
                     "company": detail.get("company"),
                     "filled_orders": sum(order.get("filled_qty", 0) > 0 for order in detail["orders"])}
                    for detail in summary
                ]})
                return
            elif path.startswith("/api/simulations/"):
                parts = path.removeprefix("/api/simulations/").split("/")
                run_id = parts[0]
                with simulations_lock:
                    saved = simulations.get(run_id)
                if saved is None or len(parts) not in (1, 3):
                    self.send_error(404)
                    return
                if len(parts) == 1:
                    self.send_json(simulation_status(run_id, *saved))
                    return
                if parts[1:] == ["payoff-samples", "download"]:
                    path = saved[1] / "payoff-samples.jsonl"
                    if not path.is_file():
                        self.send_error(404)
                    else:
                        self.send_data(path.read_bytes(), "application/x-ndjson; charset=utf-8")
                    return
                index = parts[2]
                if parts[1] != "decisions" or (index != "cutoff" and (
                    not index.isascii() or not index.isdecimal() or len(index) > 2 or int(index) >= saved[0]["duration_minutes"]
                )):
                    self.send_error(404)
                    return
                request, folder = saved
                index = index if index == "cutoff" else str(int(index))
                self.send_audit(f"simulation:{run_id}:{index}", lambda: simulation_audit(run_id, request, folder, index),
                                symbol=request["symbol"], portfolio="simulation", strategy="intraday-council")
                return
            else:
                self.send_error(404)
                return

            self.send_data(body, content_type)

        def send_trade_history(self, path, query):
            try:
                if path == "/api/trade-history":
                    params = parse_qs(query, max_num_fields=8)
                    search = params.get("q", [""])[0].strip()
                    day = params.get("date", [None])[0]
                    before = params.get("before", [None])[0]
                    if len(search) > 100:
                        raise ValueError
                    day = date.fromisoformat(day).isoformat() if day else None
                    if before:
                        day_part, id_part = before.split("/", 1)
                        if not re.fullmatch(r"[a-zA-Z0-9_.-]{1,128}", id_part):
                            raise ValueError
                        before = (date.fromisoformat(day_part).isoformat(), id_part)
                    self.send_json(history.list(search, day, before))
                    return
                run_id, *parts = path.removeprefix("/api/trade-history/").split("/")
                if not re.fullmatch(r"[a-zA-Z0-9_.-]{1,128}", run_id) or run_id in {".", ".."}:
                    self.send_error(404)
                    return
                if not parts:
                    detail = history.get(run_id)
                elif len(parts) == 2 and parts[0] == "decisions" and re.fullmatch(r"(?:[0-9]{1,3}|cutoff)", parts[1]):
                    detail = history.audit(run_id, parts[1])
                elif parts == ["payoff-samples", "download"] and (history.get(run_id) or {}).get("payoff_sample_count"):
                    samples = simulation_root / run_id / "payoff-samples.jsonl"
                    if samples.is_file():
                        self.send_data(samples.read_bytes(), "application/x-ndjson; charset=utf-8")
                        return
                    detail = None
                else:
                    detail = None
                if detail is None:
                    self.send_error(404)
                else:
                    self.send_json(detail)
            except ValueError:
                self.send_json({"error": "Enter a valid history search or date."}, 400)
            except SQLAlchemyError:
                self.send_json({"error": "The trade history database is unavailable."}, 503)

        def do_POST(self):
            if not self.check_host():
                return
            if self.path in ("/api/paper/start", "/api/paper/stop"):
                from trader.paper_panel import PaperPanelError

                if self.headers.get("Origin") != f"http://{self.headers['Host']}":
                    self.send_error(403)
                    return
                if self.headers.get_content_type() != "application/json":
                    self.send_error(415)
                    return
                if paper_panel is None:
                    self.send_json({"error": "This deployment has no paper controls."}, 409)
                    return
                stopping = self.path.endswith("/stop")
                try:
                    if stopping:
                        result = paper_panel.stop()
                    else:
                        try:
                            size = int(self.headers.get("Content-Length", "0"))
                            if not 0 < size <= 1024:
                                raise ValueError
                            selection = json.loads(self.rfile.read(size))
                            if not isinstance(selection, dict) or selection.keys() - {"symbol", "holding_policy"}:
                                raise ValueError
                        except ValueError:
                            self.send_json({"error": "Enter a valid ticker and holding policy."}, 400)
                            return
                        result = paper_panel.start(**selection)
                    self.send_json(result)
                except PaperPanelError as exc:
                    self.send_json({"error": str(exc)}, 409)
                except Exception:
                    message = (
                        "Stop could not be confirmed. Check the session state and open orders before restarting."
                        if stopping else "Paper preflight could not be verified. Check the broker and database."
                    )
                    self.send_json({"error": message}, 503)
                return
            if self.path != "/api/simulations":
                self.send_error(404)
                return
            if self.headers.get("Origin") != f"http://{self.headers['Host']}":
                self.send_error(403)
                return
            if self.headers.get_content_type() != "application/json":
                self.send_error(415)
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 4096:
                    raise ValueError
                simulation = SimulationRequest.model_validate_json(self.rfile.read(size))
            except ValidationError as exc:
                self.send_json({"error": " ".join(row["msg"] for row in exc.errors())}, 400)
                return
            except ValueError:
                self.send_json({"error": "Invalid simulation request."}, 400)
                return
            if not simulation_slot.acquire(blocking=False):
                self.send_json({"error": "A run of this type is already in progress."}, 409)
                return
            run_id = uuid4().hex
            try:
                folder = (simulation_root / run_id).resolve()
                folder.mkdir(parents=True)
                (folder / "request.json").write_text(simulation.model_dump_json(), encoding="utf-8")
                request = simulation.model_dump(mode="json")
                with simulations_lock:
                    simulations[run_id] = (request, folder)
                    running_simulations.add(run_id)
                Thread(target=simulate, args=(run_id, request, folder), daemon=True).start()
            except (OSError, RuntimeError):
                with simulations_lock:
                    simulations.pop(run_id, None)
                    running_simulations.discard(run_id)
                simulation_slot.release()
                self.send_json({"error": "The simulation worker could not start."}, 502)
                return
            self.send_json({"id": run_id}, 202)
            return
    class ViewerServer(ThreadingHTTPServer):
        def serve_forever(self, poll_interval=0.5):
            if worker is not None:
                worker.start()
            self.projector = Thread(target=project_in_background, daemon=True, name="audit-projector")
            self.projector.start()
            return super().serve_forever(poll_interval)

        def server_close(self):
            if worker is not None:
                worker.close()
            super().server_close()
            projection_stop.set()
            projection_wake.set()
            if getattr(self, "projector", None):
                self.projector.join(timeout=4)
            history.close()
            try:
                star.close(clear=bool(star_url))
            except SQLAlchemyError:
                print("Could not clear this launch's audit records from the database.", file=sys.stderr)

    return ViewerServer((host, port), Handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=os.environ.get("TRADER_VIEWER_PORT", "8765"))
    parser.add_argument("--host", choices=("127.0.0.1", "0.0.0.0"), default="127.0.0.1")
    args = parser.parse_args()
    try:
        def serve(root):
            with make_server(args.port, host=args.host, simulation_root=root) as server:
                print(f"Glitter app at http://localhost:{server.server_port}", flush=True)
                server.serve_forever()

        if directory := os.environ.get("TRADER_VIEWER_RUN_DIR"):
            root = Path(directory)
            root.mkdir(parents=True, exist_ok=True)
            serve(root)
        else:
            with TemporaryDirectory(prefix="glitter-viewer-") as temporary:
                serve(Path(temporary))
    except KeyboardInterrupt:
        pass
    except (OSError, KeyError, ValueError) as exc:
        parser.exit(1, f"Could not open the replay viewer: {exc}\n")


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal.default_int_handler)
    main()
