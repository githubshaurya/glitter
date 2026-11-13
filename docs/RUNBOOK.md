# Operations and recovery

## Commissioning

1. Put keys in root `.env`; use a dedicated paper account and one persistent database.
2. Set a long dashboard token. Run `uv run glitter-check` with execution disabled.
3. Inspect actual account status, both tradable assets and the public-data Groq tool result.
4. Approve account-context sharing before enabling that setting. Inspect prompts/tool responses.
5. Enable paper execution and start the service. Inspect the first actual candidate and outcome.
   A HOLD or veto is valid; do not force trades to make the experiment look active.
6. Trace any real order through candidate ID → observation → model verdict → risk events →
   order intent → Alpaca ID, then confirm it in the Alpaca paper dashboard.
7. Keep the service running for 3+ calendar days, preferably five. Export evidence daily.

The initial implementation session verified real reads and public-data inference. An integrated
portfolio-context/order test was blocked by automatic approval review pending explicit consent
to the private account-data transfer. It is not described as a successful live trading run.

## Stop

Use the dashboard's **Halt & cancel open orders**, or `uv run glitter-halt`.
The database HALTED update happens before cancellation. A broker outage cannot undo that
persistent mode. Later monitors retry cancellation. Inspect each cancellation response and
broker status: a request is not proof that every order was canceled. Holdings remain held.

NO_NEW_RISK blocks new entries but allows valid rule exits. ACTIVE restores the strategy mode,
not the loss latch. A loss latch remains until a deliberate operator-reviewed recovery; this first
version has no one-click latch reset. Do not edit controls while a worker is running. Keep the
account stopped and preserve/export old state before establishing a new measurement period.

## UNKNOWN order

An ambiguous intent is never automatically resubmitted or deleted. Reconciliation queries
Alpaca using its client order ID. When found, the actual status/fills replace UNKNOWN. If not
found, entries remain blocked. Verify order history, activities and dashboard; do not infer
non-submission from one 404. Preserve an incident record. Availability is intentionally sacrificed.

For a proven pre-submission crash, the simplest safe assessment recovery is to retain the
blocked journal and restart a clearly labeled new observation period after operator review.
Do not erase old evidence or replay an already claimed hour. This version provides no unsafe
"retry anyway" action.

## Common failures

| Symptom | Action |
|---|---|
| Groq 401/403 | Verify key and provider access; no entries occur on agent error. Keep secrets out of logs. |
| Quota/timeout | Reduce replay limit; retain failure samples; do not claim a veto. |
| Missing candles | Inspect history/pagination and source timestamps; do not forward-fill silently. |
| Account mismatch | Use the correct database for the dedicated account; do not repoint an existing journal. |
| Database unavailable | New submissions stop because intent cannot be committed. Restore storage first. |
| Process crash after POST | Reconcile by client ID; do not rerun the order. |
| GitHub delayed job | Inspect coverage/gaps; the database prevents duplicates, not missed observations. |
| Dashboard unresponsive | Health route, process logs, DB reachability; retain the broker dashboard as independent evidence. |

## Backups and report

PostgreSQL: use your provider's backups and a separate export. SQLite: stop the worker before
copying its database, or use SQLite's online backup interface; do not copy a WAL database's main
file alone while writing. Docker named volumes survive container recreation, not volume removal.
Never run `docker compose down -v` on the evidence volume.

`uv run glitter-report` writes private exports to reports/latest. Activity records with only a date
are separated from exactly timestamped records. Review external cash movements/account resets
before interpreting simple equity return. The report template intentionally leaves personal
learnings, actual operating costs and incident explanations for the operator to complete honestly.

No email is sent, no public dashboard is deployed, and no remote database is provisioned by these
commands. For remote access, put the authenticated dashboard behind TLS and restrict access.

## Current commissioning incident and database continuity

The 2026-11-13 local journal remains HALTED with one UNKNOWN paper commissioning intent.
Execution and private context are disabled. The current journal is `data/glitter.db`; a consistent
online backup is in `reports/latest/journal-backup.sqlite3`. Keep its incident history.

Default Compose uses a named Docker volume, while a host `uv` command uses the root `.env`
SQLite path. Those are different physical databases. Do not switch writers or enable a fresh
Docker volume to get around the current UNKNOWN. Restore the reviewed journal/backup into
the intended persistent volume, or migrate to one reviewed persistent PostgreSQL database,
while all writers are stopped. Verify controls, intent states and ownership after migration.
Do not start two physical journals against the same paper account.

Before assessment submission, walk through PRE_SUBMISSION_REVIEW.md, the independent paper
dashboard, export coverage, late fees, the results draft and actual bills. The public replay
results do not establish that the missing account-aware run has completed.
