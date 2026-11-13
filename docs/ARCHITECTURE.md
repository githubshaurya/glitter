# Architecture

## Scope and topology

Two crypto symbols, 24 hourly decision slots/day, at most 48 model decisions/day. The process
also monitors every 15 minutes. This is not an HFT engine or a 5,000-symbol tick service.
The main latency is provider I/O and model inference. Indicator calculations traverse 300
candles per symbol. There is no measured CPU bottleneck justifying Rust, Kafka, Redis,
microservices, a task framework or distributed caches. Python is the only backend language.
SQLAlchemy expresses the storage schema; HTML/CSS/JavaScript implement the dashboard.

| Module | Owns |
|---|---|
| `broker.py` | Fixed paper host, typed account/quotes, pagination, one-shot writes |
| `strategy.py` | Candle continuity, completed UTC bars, numerical features and candidates |
| `agent.py` | Three-turn bounded Groq loop, permitted tools, validated verdict |
| `risk.py` | Pure deterministic sizing and checks using Decimal money/quantities |
| `execution.py` | Fresh reads, durable intent, final submission gate and reconciliation |
| `repository.py` | SQL schema, journal, account binding, locks and persistent controls |
| `application.py` | Sequential cycle orchestration; frozen experiment observations |
| `web.py` | Authenticated inspection/controls and one background monitoring task |
| `experiments.py`, `reporting.py` | Offline comparisons and broker-verified evidence |

Use OOP for external boundaries; numerical functions stay plain and small. No DI container,
registry, generic workflow engine, autonomous strategy rewriting or multi-agent debate.

## Coordination and durable intent

PostgreSQL uses a dedicated session advisory lock held for the entire cycle. Committing an
individual journal write does not release that lock. Supabase transaction pooling is unsuitable
because it does not preserve the session. SQLite uses a non-expiring OS file lock on one Linux
host, WAL, FULL synchronization, foreign keys and immediate write transactions.

An hourly slot has a unique database constraint. A committed claim is never replayed, even if
the process later fails. This sacrifices an hour's availability rather than rerunning half a
decision. Every run has an independent monitoring record, including errors and skipped slots.

An order's deterministic client ID is `gl-<symbol>-<UTC slot>`. The journal stores that key and
the full exact payload in SUBMITTING state before any broker POST. One payload, one POST
attempt. All nonterminal/uncertain intents block later exposure until reconciled. A response
timeout or commit loss after acceptance becomes UNKNOWN; a lookup returning 404 does not
authorize another POST. Crash before send can therefore strand an intent. This is deliberate.

Do not call it exactly-once delivery. A broker and our database do not share a transaction.
Retries are limited to GETs (three attempts, exponential backoff with jitter); POSTs are never
retried. SDK retry defaults cannot silently repeat an order because this client uses explicit HTTP.

## Final gate and stops

Before preparation, execution refreshes broker account, positions, orders, asset precision and
quotes. It updates the persistent equity loss latch, sizes a bounded IOC limit order and journals
every check. The final controls-row transaction rechecks risk, signal/quote freshness, unresolved
intents and payload identity immediately before POST. Control changes acquire the same row
lock. The transaction holds that lock during the bounded HTTP call.

Consequently, a halt may wait for an already-authorized request. Once the halt update returns,
later submissions cannot pass. Requests already accepted may still fill. Cancellation is a separate
best-effort broker request, retried by later monitors while HALTED. No liquidation is implied.

ACTIVE allows eligible entries and exits. NO_NEW_RISK blocks entries. HALTED blocks all
automated orders. Daily-loss/drawdown latches independently block new entries and persist.
The implementation never promises a 1% stop-loss: observations are periodic and gaps exist.

The account is bound to the database on first observation. Different account credentials
cannot silently reuse its controls. Independent databases and manual broker actions remain
outside the application's writer coordination; use a dedicated paper account and one database.

## Data, agent and security boundaries

Fetch all paginated hourly data, validate 300 contiguous complete candles, and derive UTC
4-hour windows from complete groups. Indicator warm-up, Wilder RSI/ATR conventions and
EMA initialization are explicit in source. Store the validated 300-bar history, features, source
times and exact model-visible snapshot. Optional candle tools return at most 24 closed bars.

The first model turn must call get_decision_context. The next turn must inspect candles or
submit_verdict. The third must terminate. One tool per turn; no shell, arbitrary URLs, database
queries, credentials or brokerage write tools. JSON parsing, allowed reason codes, exact candidate
identity and evidence-field references are checked locally. Reference validity is not proof that an
explanation is logically correct; review rationales separately. Private reasoning fields are discarded.

Account context requires an explicit opt-in. Secrets remain server-side in ignored environment
configuration. API routes require a constant-time compared bearer token. The frontend keeps
the token in memory, escapes external text and uses same-origin requests with restrictive CSP.
Use a TLS reverse proxy for non-local access; no public exposure is configured by Compose.

Tables store runs, observations, paired decisions, intents, events, equity snapshots, controls and
experiments. Application journal writes append records; current order/control/run status updates
are transactional. This is not a tamper-proof archive against the database administrator. Back up
the persistent database and export the journal independently during the observation period.

## Measurement and limitations

Collect model latency/tokens and full-cycle duration. A proposed p95 target is 45 seconds;
it is not asserted as achieved by a single commissioning check. Provider timeouts are bounded
connect/read/write inactivity limits; they are not a hard deadline for a pathological slow stream.
GitHub job timeouts bound scheduled processes. Monitor coverage and stale observations.

No custom database migration engine is introduced for this initial schema. `initialize()` creates
the initial tables; future schema changes require an explicit reviewed migration, not create_all
as an upgrade mechanism. Docker volume persistence and hosted database backups are operational
responsibilities, not properties conferred by using an ORM.
