"""Serve historical council decisions and saved replays on loopback."""

import argparse
import json
import os
import signal
import subprocess
import sys
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Lock, Thread
from urllib.parse import urlsplit
from uuid import uuid4

from sqlalchemy.exc import SQLAlchemyError

from trader.reporting.star import StarJournal, public_attempts

ASSETS = Path(__file__).with_name("replay_viewer")
STATIC = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/viewer.css": ("viewer.css", "text/css; charset=utf-8"),
    "/viewer.js": ("viewer.js", "text/javascript; charset=utf-8"),
}


HISTORY_FIELDS = (
    "scenario",
    "company",
    "as_of",
    "elapsed_s",
    "feed",
    "phase_timings",
    "news",
    "evidence",
    "result",
    "recommendation",
    "effective_budget_usd",
    "latest_error",
    "risk",
    "orders",
    "fills",
)


def history_record(path, detail, source):
    scenario, recommendation, result = (detail[key] for key in ("scenario", "recommendation", "result"))
    as_of = datetime.fromisoformat(detail["as_of"])
    if as_of.tzinfo is None:
        raise ValueError("The decision timestamp has no time zone.")
    summary = dict(
        id=f"{source}-{path.parent.name}",
        source=source,
        symbol=scenario["symbol"],
        company=detail.get("company") or scenario["symbol"],
        as_of=detail["as_of"],
        recommendation={key: recommendation[key] for key in ("action", "shares")},
        outcome=result["outcome"],
        latest_error=detail.get("latest_error"),
    )
    return summary, (as_of, path.stat().st_mtime, summary["id"])


def make_server(
    run: Path | None,
    port: int = 8765,
    *,
    host: str = "127.0.0.1",
    analysis_root: Path | None = None,
    audit_root: Path | None = None,
) -> ThreadingHTTPServer:
    if analysis_root is not None:
        from pydantic import ValidationError

        from trader.backtest.decision import AlpacaReadOnly, Scenario, ScenarioError, open_alpaca
        from trader.backtest.simulation import SimulationRequest, write_json

    history = {}
    history_lock = Lock()

    def remember(path, detail, source):
        try:
            summary, order = history_record(path, detail, source)
        except (KeyError, TypeError, ValueError, OSError):
            return
        with history_lock:
            history[summary["id"]] = (order, summary, path)

    for source, root in (("analysis", analysis_root), ("test", audit_root)):
        if root is None:
            continue
        for path in root.glob("*/response.json"):
            try:
                if not path.resolve().is_relative_to(root.resolve()):
                    continue
                detail = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            remember(path, detail, source)

    journal = {}
    if run is None:
        result = {"metrics": {}, "ledger": {"orders": [], "fills": []}, "cycles": []}
        manifest = {"symbol": None, "benchmark": None}
    else:
        result = json.loads((run / "results.json").read_text(encoding="utf-8"))
        manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
        with (run / "journal/council-runs.jsonl").open(encoding="utf-8") as entries:
            for line in entries:
                if line.strip():
                    entry = json.loads(line)
                    journal[entry["run_id"]] = entry
    orders = {order["id"]: order for order in result["ledger"]["orders"]}
    fills_by_order = {}
    for fill in result["ledger"]["fills"]:
        fills_by_order.setdefault(fill["order_id"], []).append(fill)
    cycles = {cycle["run_id"]: cycle for cycle in result["cycles"]}
    scenario_slot = Lock()
    simulations = {}
    simulations_lock = Lock()

    def simulation_status(run_id, request, folder):
        try:
            progress = json.loads((folder / "progress.json").read_text(encoding="utf-8"))
        except FileNotFoundError:
            progress = {"status": "queued", "decisions": [], "orders": []}
        return {**progress, "request": request, "id": run_id}

    def simulation_audit(run_id, request, folder, index):
        progress = simulation_status(run_id, request, folder)
        if index == "cutoff":
            orders = [order for order in progress["orders"] if order.get("reason") == "session_cutoff"]
            if not orders:
                raise ValueError("Cutoff execution is unavailable.")
            detail = {"as_of": orders[0]["submitted_at"], "result": {"outcome": "SESSION_CUTOFF"}, "risk": [],
                      "recommendation": {"action": orders[0]["side"]}}
        else:
            index = int(index)
            if not any(row["index"] == index for row in progress["decisions"]):
                raise ValueError("The decision has not been recorded.")
            detail = json.loads((folder / f"decision-{index}.json").read_text(encoding="utf-8"))
            orders = [order for order in progress["orders"] if order.get("decision_index") == index]
        detail["orders"] = orders
        detail["fills"] = [
            dict(order_id=order["id"], side=order["side"], qty=order["filled_qty"],
                 price=order["fill_price"], t=order["filled_at"])
            for order in orders if order.get("status") == "filled"
        ]
        return detail

    def simulate(run_id, request, folder):
        try:
            with (folder / "worker.log").open("w", encoding="utf-8") as log:
                subprocess.run(
                    [sys.executable, "-m", "trader.backtest.simulation", str(folder)],
                    stdout=log, stderr=log, timeout=1500, check=True,
                )
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
            scenario_slot.release()

    catalog = json.dumps(
        {
            "symbol": manifest["symbol"],
            "benchmark": manifest["benchmark"],
            "metrics": result["metrics"],
            "cycles": [
                {
                    **{key: row[key] for key in ("run_id", "day", "as_of", "outcome", "elapsed_s")},
                    "filled": any(order["id"] in fills_by_order for order in row["orders"]),
                }
                for row in cycles.values()
            ],
        }
    ).encode()

    star_url = os.environ.get("TRADER_VIEWER_DATABASE_URL")
    star = StarJournal(star_url)

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

        def send_audit(self, decision_id, load_detail, *, symbol, portfolio, strategy, company=None, saved_source=None):
            try:
                detail = star.get(decision_id)
                if detail is None:
                    detail = star.project(decision_id, load_detail(), symbol=symbol, portfolio=portfolio,
                                          strategy=strategy, company=company)
            except (OSError, ValueError, KeyError):
                self.send_json({"error": "The recorded decision could not be read."}, 404)
                return
            except SQLAlchemyError:
                self.send_json({"error": "The audit database is unavailable. Try again when it recovers."}, 503)
                return
            if saved_source:
                detail = {
                    **{key: detail[key] for key in (*HISTORY_FIELDS, "attempts", "star") if key in detail},
                    "source": saved_source,
                }
            self.send_json(detail)

        def do_GET(self):
            if not self.check_host():
                return

            path = urlsplit(self.path).path
            content_type = "application/json; charset=utf-8"
            if path in STATIC:
                asset, content_type = STATIC[path]
                body = (ASSETS / asset).read_bytes()
            elif path == "/api/replay":
                body = catalog
            elif path == "/api/history":
                with history_lock:
                    runs = sorted(history.values(), key=lambda run: run[0], reverse=True)
                self.send_json({"runs": [summary for _, summary, _ in runs]})
                return
            elif path == "/api/simulations":
                with simulations_lock:
                    runs = list(simulations.items())
                summary = (simulation_status(run_id, *saved) for run_id, saved in reversed(runs))
                self.send_json({"runs": [
                    {**{key: detail[key] for key in ("id", "status", "request")},
                     "filled_orders": sum(order.get("status") == "filled" for order in detail["orders"])}
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
            elif path.startswith("/api/history/"):
                with history_lock:
                    saved = history.get(path.removeprefix("/api/history/"))
                if saved is None:
                    self.send_error(404)
                    return
                _, summary, response_path = saved
                self.send_audit(summary["id"], lambda: json.loads(response_path.read_text(encoding="utf-8")),
                                symbol=summary["symbol"], portfolio="analysis", strategy="interactive-council",
                                company=summary["company"], saved_source=summary["source"])
                return
            elif path == "/api/account" and analysis_root is not None:
                try:
                    with open_alpaca() as client:
                        self.send_json(AlpacaReadOnly(client).account())
                except ScenarioError as exc:
                    self.send_json({"error": str(exc)}, 502)
                return
            elif path.startswith("/api/cycle/") and (run_id := path.removeprefix("/api/cycle/")) in cycles:
                cycle = cycles[run_id]
                entry = journal.get(run_id, {})
                order_ids = [order["id"] for order in cycle["orders"]]
                self.send_audit(
                    f"replay:{run_id}", lambda: {
                        "as_of": cycle["as_of"], "elapsed_s": cycle["elapsed_s"], "outcome": cycle["outcome"],
                        "evidence": entry.get("evidence", {}).get("content", {}),
                        "result": entry.get("result") or cycle.get("result", {}),
                        "attempts": entry.get("attempts", []),
                        "risk": cycle["risk"],
                        "orders": [orders[order_id] for order_id in order_ids],
                        "fills": [fill for order_id in order_ids for fill in fills_by_order.get(order_id, [])],
                    }, symbol=manifest["symbol"], portfolio="simulation", strategy=entry.get("variant") or "saved-replay",
                )
                return
            else:
                self.send_error(404)
                return

            self.send_data(body, content_type)

        def do_POST(self):
            if not self.check_host():
                return
            is_simulation = self.path == "/api/simulations"
            if self.path not in ("/api/scenario", "/api/simulations") or analysis_root is None:
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
                model = SimulationRequest if is_simulation else Scenario
                scenario = model.model_validate_json(self.rfile.read(size))
            except ValidationError as exc:
                self.send_json({"error": " ".join(row["msg"] for row in exc.errors())}, 400)
                return
            except ValueError:
                self.send_json({"error": "Invalid analysis request."}, 400)
                return
            if not scenario_slot.acquire(blocking=False):
                self.send_json({"error": "A council run is already in progress. Wait for it to finish."}, 409)
                return
            if is_simulation:
                run_id = uuid4().hex
                try:
                    folder = (analysis_root / "simulations" / run_id).resolve()
                    folder.mkdir(parents=True)
                    (folder / "request.json").write_text(scenario.model_dump_json(), encoding="utf-8")
                    request = scenario.model_dump(mode="json")
                    with simulations_lock:
                        simulations[run_id] = (request, folder)
                    Thread(target=simulate, args=(run_id, request, folder), daemon=True).start()
                except (OSError, RuntimeError):
                    with simulations_lock:
                        simulations.pop(run_id, None)
                    scenario_slot.release()
                    self.send_json({"error": "The simulation worker could not start."}, 502)
                    return
                self.send_json({"id": run_id}, 202)
                return
            try:
                folder = (analysis_root / uuid4().hex).resolve()
                folder.mkdir(parents=True)
                (folder / "request.json").write_text(scenario.model_dump_json(), encoding="utf-8")
                with (folder / "worker.log").open("w", encoding="utf-8") as log:
                    subprocess.run(
                        [sys.executable, "-m", "trader.backtest.decision", str(folder)],
                        stdout=log,
                        stderr=log,
                        timeout=250,
                        check=True,
                    )
                response_path = folder / "response.json"
                response = json.loads(response_path.read_text(encoding="utf-8"))
                if "error" in response:
                    self.send_json(response, 422)
                else:
                    remember(response_path, response, "analysis")
                    if "as_of" in response:
                        self.send_audit(f"analysis-{folder.name}", lambda: response, symbol=scenario.symbol,
                                        portfolio="analysis", strategy="interactive-council", company=response.get("company"))
                    else:
                        response["attempts"] = public_attempts(response)
                        self.send_json(response)
            except subprocess.TimeoutExpired:
                self.send_json({"error": "Analysis exceeded the time limit. Try this decision again."}, 504)
            except (OSError, ValueError, subprocess.CalledProcessError):
                self.send_json({"error": "Analysis failed. The worker log was saved locally."}, 502)
            finally:
                scenario_slot.release()

    class ViewerServer(ThreadingHTTPServer):
        def server_close(self):
            super().server_close()
            try:
                star.close(clear=bool(star_url))
            except SQLAlchemyError:
                print("Could not clear this launch's audit records from the database.", file=sys.stderr)

    return ViewerServer((host, port), Handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", nargs="?", type=Path, help="Optional saved replay directory")
    parser.add_argument("--port", type=int, default=os.environ.get("TRADER_VIEWER_PORT", "8765"))
    parser.add_argument("--host", choices=("127.0.0.1", "0.0.0.0"), default="127.0.0.1")
    parser.add_argument("--analysis-dir", type=Path, default=Path("proof/interactive-scenarios"))
    parser.add_argument("--session-only", action="store_true", help="Keep browser runs only for this launch")
    parser.add_argument(
        "--audit-dir",
        type=Path,
        default=Path("proof/scenario-matrix-20261118/runs"),
        help="Optional folder of recorded test analyses",
    )
    args = parser.parse_args()
    try:
        default_run = Path("proof/replay-results-2024-sip-verified-council")
        saved_run = args.run or (default_run if (default_run / "journal/council-runs.jsonl").is_file() else None)
        def serve(analysis_root, audit_root):
            with make_server(saved_run, args.port, host=args.host, analysis_root=analysis_root, audit_root=audit_root) as server:
                print(f"Council app at http://localhost:{server.server_port}", flush=True)
                server.serve_forever()

        if args.session_only:
            with TemporaryDirectory(prefix="glitter-viewer-") as temporary:
                serve(Path(temporary), None)
        else:
            serve(args.analysis_dir, args.audit_dir)
    except KeyboardInterrupt:
        pass
    except (OSError, KeyError, ValueError) as exc:
        parser.exit(1, f"Could not open the replay viewer: {exc}\n")


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal.default_int_handler)
    main()
