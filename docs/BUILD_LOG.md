# Build log

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
