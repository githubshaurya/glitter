# Build log

14 November 2026 (Asia/Kolkata): reviewed the new interviewer requirements reported by the
user and current official Alpaca, PostgreSQL, Kafka, Redis, vLLM and WebSocket documentation.
Added a separate realtime target design, database/workflow/failure matrix and ordered execution
brief. Corrected the assumption that multiple Alpaca sockets are generally available or make
missed data recoverable. This is design work only; no stream runtime, local model hosting,
broker fill, new realtime test pass or unattended deployment is claimed by this documentation.

14 November 2026, 13:40 IST: bounded actual Alpaca crypto/us WebSocket capability probe
authenticated, confirmed BTC/USD and ETH/USD quote/bar/updated-bar subscriptions, received
three quote events and closed. Public market data only; no order or private model transfer.
Retained sanitized metadata. This proves basic connectivity/subscription only, not streaming
runtime implementation or the proposed 120-second recovery behavior.

Dates/times below are UTC. Entries record work actually performed with ChatGPT/Codex and
connected GitHub tools, official documentation, Python/uv, pytest/Ruff and local PostgreSQL.
They are not an invented unattended trading history.

| Time | Version / work | Observed result |
|---|---|---|
| 2026-11-13, initial inspection | v0: assessment and empty githubshaurya/glitter repository; read requested design/skill references | Confirmed seven-day deadline, 3+ crypto days, two experiments and six deliverables. Initialized repository. |
| 2026-11-13, implementation session | v1: market/strategy, bounded agent, risk, durable storage, one-shot execution and reconciliation | Added paper-only fixed host, independent safety checks, unique slots/intents and deterministic IOC limit sizing. |
| 2026-11-13, integration checks | Real supplied credentials in ignored .env; account/assets/quotes/300-hour history | Paper account ACTIVE; BTC/USD and ETH/USD tradable; actual data reads succeeded. No strategy order submitted. |
| 2026-11-13, integration checks | Public-market HOLD commissioning through GPT-OSS 120B | Actual get_decision_context → submit_verdict succeeded; observed 1,632 total tokens and 9.41 seconds on one public-data check. This is one sample, not a p95 result. |
| 2026-11-13, review | v2: review and forward-test the dedicated engineering skill | Fixed final-gate freshness race, incomplete tool candles, replay datetime serialization and report timestamp filtering. Added regression tests. |
| 2026-11-13, safety boundary | Portfolio-context cycle blocked by automatic approval review | Added an explicit disabled-by-default account-context transfer gate. Continued public-data/model and local/broker-only checks without retrying that transfer. |
| 2026-11-13, local verification | SQLite and actual PostgreSQL 16 using bundled test binaries over TCP | 40 tests passed in both backends at that point, including accepted-order timeout, lost commit and stop/submit race. Test binaries are not an application dependency. |
| 2026-11-13T06:40Z | Broker-only report export | Generated complete empty order/activity exports and a two-point actual account equity curve with aligned BTC prices; no closed trades and no multi-day performance claim. |
| 2026-11-13T06:43Z | v3: transfer-gate, closed-history and exact activity-window regressions | 43 SQLite tests passed. Ruff and frontend syntax passed. Final PostgreSQL/remote CI results belong in VALIDATION.md. |

The UI uses the requested visual reference without taking priority over execution safety.
Local Chromium could not start because the environment denies Unix-domain sockets; cloud
preview could not reach the local server. Desktop/mobile browser checks were added to remote
CI instead. Do not label those checks passed until their workflow result is observed.

Future entries: record deployment time, each actual order, every incident/fix, actual provider
costs and configuration/version changes. Do not retroactively write model rationales.

2026-11-13T06:50Z: remote CI on the pinned platform passed 43 tests for each database,
lint/formatting/JS syntax and two browser tests (desktop/mobile), including control interaction.
No account credentials were used in CI. Added a Docker image build/start/auth smoke check.

Final verification: [CI run 43382147168](https://github.com/githubshaurya/glitter/actions/runs/43382147168)
passed both 43-test database suites, both desktop/mobile tests and Docker build/start/health/auth
checks. Inspected CI screenshots. Also verified GPT-OSS 20B on the stored public commissioning
context (HOLD; 1,770 tokens; one 8.94-second sample). No actual order, three-day run or financial
experiment result is claimed. Private account-context execution remains disabled pending consent.

2026-11-13T14:00–15:00Z: strict pre-submission review. Added a public-only at-most-$2
commissioning command, absolute notional cap, full broker-payload verification, idempotent
intent replay, unique model request correlation, worker/database readiness, abandoned-slot
recovery, explicit tool-field allowlist, strategy ownership checks, tradable dust handling and
Decimal fee ledger. Added separate-process races and SIGKILL recovery tests. At this stage
81 tests pass on SQLite and PostgreSQL. Browser/Docker expansion awaits its new CI result.

2026-11-13T14:31Z: one positive-quantity paper commissioning POST returned BrokerError,
recorded UNKNOWN. No order/fill found by lookup or export; not resubmitted. Initial HTTP error
details were missing, so the cause is unconfirmed. Added sanitized diagnostics and preservation
across lookup misses. A distinct zero-quantity negative probe returned HTTP 422/code 40010001
(qty must be > 0), confirming endpoint access without creating exposure. HALTED was persisted
and actual paper cancellation requested after the incident; independent repository reads confirm it.

2026-11-13T14:47–14:55Z: executed and retained a 12-observation HOLD pilot plus a predeclared
12-entry public-history follow-up. Two measured comparisons, real requests, failures retained.
See EXPERIMENT_RESULTS.md and public evidence JSON. Rationale inspection found unsupported
execution assurances; tightened prompt to v3 and added a targeted real-model regression.

2026-11-13T14:56Z: broker proof export completed: 34 aligned equity observations over 06:30–14:45
UTC, zero exported orders/fills, account return 0, BTC gross benchmark +0.5665%, sampled BTC
drawdown 0.9774%. This is an inactive-account export check, not strategy performance or an
unattended-run claim. No fees, completed trades, private-context execution or 3-day run claimed.

Final local pre-submission checks: 84 tests passed on SQLite and 84 on real PostgreSQL;
Ruff, formatting, JS syntax, frozen lock check and credential-value source scan passed.
Remote CI for the hardened code must be observed before claiming its browser/Docker checks.

2026-11-13T15:04Z: hardened-code CI 43448651072 passed 84 tests per database, both browser
tests and Docker startup/auth/readiness/persistence through container replacement. Source
commit cccd4d1c92d7ecc31636ffe3d5696972e2076a49. No brokerage keys used in CI. Reopened
real local journal (HALTED, one UNKNOWN, both execution and private context disabled), and
made a consistent online SQLite backup. Local uvicorn startup succeeded; cross-command
loopback inspection failed in this workspace, so no local HTTP latency numbers are claimed.
