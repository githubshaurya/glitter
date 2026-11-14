# Execution brief: implement and prove the realtime system

Read this as the implementation task, together with REALTIME_SYSTEM_DESIGN.md. It is not a
claim of completed implementation. Produce reviewable decisions, code and observed tests;
do not provide private chain-of-thought or substitute architectural prose for running evidence.

## Objective and authorization boundaries

Replace the relevant polling architecture with continuous, recoverable Alpaca data ingestion,
versioned storage/features/news, a bounded master/subagent decision workflow and safe paper
execution. Reuse sound existing components. Implement the complete vertical path before adding
scale features. Backend application languages: Python; Rust only after profiling and parity tests.

Read AGENTS.md, the attached assessment, current architecture/runbook/validation, open incidents,
and the realtime design first. Treat the user's new realtime/multi-agent requirements as the
new target. The existing hourly crypto profile remains an independently measured legacy profile.
Do not silently change its asset class, indicators, cadence or old experiment interpretation.

Preserve existing work and inspect the actual branch/head. Use current official documentation
and actual access tests; every assumption about feed identity, timestamp precision, API errors,
entitlement, pagination, update semantics and write behavior needs evidence or an explicit
unverified label. External architecture skill repositories are review aids, not API authority.

Paper only. Never add a live broker switch or embed credentials. Do not expose secrets in prompts,
logs, fixtures, screenshots, source or submission files. Keep the currently HALTED account and
UNKNOWN intent intact. Do not change database to bypass it, force profitable results, retry an
ambiguous broker write, clear persistent loss controls or invent elapsed-run evidence.

Private account data and derived private financial context must not be sent to Groq/another
external model without the required explicit transfer authorization. No indirect anonymization
workaround and no unapproved cloud fallback from a local model. Public data-only work, local
tests and design can proceed independently. No assessment email is sent unless explicitly asked.

## Resolve choices with evidence

For each material choice, write a compact record: problem, constraints, credible source or
measurement, alternatives, selected option, failure behavior and validation. Do not create
dozens of ceremonial ADR files. Update the design/source ledger when evidence changes it.
Distinguish a measured property, an acceptance target, an assumption and an untested proposal.

Initial choices: PostgreSQL as durable state and work authority; optional rebuildable Redis;
Kafka only after measured ingest/replay/fan-out pressure; object storage for verified archives;
no document/vector database without a demonstrated retrieval need. One collector per entitled
feed and one serialized execution owner per account. Logical process boundaries precede
microservice proliferation. Local LLM serving remains a separate deployment phase.

Do not assume that another socket, Redis replication, an expiring lease, Kafka transactions or
a database backup makes the whole external system exactly once or highly available. Demonstrate
what each covers, including correlated failure and provider unavailability.

## Phase 0: inventory, capabilities and migration plan

- Map current modules to target responsibilities and identify which behavior is reused/replaced.
- Record proposed universe, feed/location, calendar, timeframe, warm-up, bar revision policy,
  source permissions, actual historical access, configured risk caps and latency/load targets.
- Check repository/account state without printing keys. Preserve a consistent backup and verify
  it, not just its filename. No schema change may discard intents, controls or decision evidence.
- Pin dependency/runtime versions. Prefer a small explicit Python async client and simple pure
  calculations to an orchestration framework. Confirm WebSocket proxy/TLS support in deployment.
- Define additive, reviewed migrations and restoration checks. A fresh empty database is not
  an upgrade. Keep a clear distinction between existing single-account and future account-keyed
  schemas; never run two independent controls as competing authorities.

Exit: concrete interfaces, table migration plan and failure/acceptance matrix linked to code.
Completed design work does not count as a verified realtime runtime.

## Phase 1: data-only durable streaming

Implement market collectors with connection/auth/subscription states, classified errors, bounded
frames/queues, keepalive, jittered reconnect and a passive ownership scheme compatible with
actual connection limits. Store connection generation, source/feed/instrument, frame/item
ordinal, source nanoseconds/raw timestamp, receive time and raw receipt/reference.

Separate reader, batched durable writer and ordered projections. No blocking model/database
operation inside the socket reader. Make eligible projections consume committed receipts/work.
Insert receipt+work atomically; commit projection effects+completion together. A notification is
only a wake-up hint. Track work by durable status/id, avoiding skipped uncommitted lower offsets.

Enforce bounded memory, backlog age and capacity. If unable to retain a message, explicitly
record/derive degraded coverage and recover. Never silently drop or coalesce archival events.
Coalescing a disposable UI/latest-quote cache must not alter authoritative event history.

Expose authenticated per-feed/per-symbol readiness: subscriptions, last event age, durable
commit boundary, required bar coverage, queue lag, open gaps and projector progress. Transport
liveness alone cannot permit entries. On startup, conservatively account for any unclean shutdown
and initialize required history before reporting a usable snapshot.

Exit: observed actual stream messages are durable; collector restart, duplicate delivery and
slow-client tests pass. No order path is enabled or claimed exercised in this phase.

## Phase 2: the 120-second outage and revisions

Implement persistent gap/recovery states. Continue receiving live data while historical repair
works to a fixed cutoff. Request the same entitled source with overlap and complete pagination.
Validate each symbol/interval, not just the newest timestamp or one successful response. Classify
unavailable/forbidden/rate-limited history and stay degraded when evidence is insufficient.

Keep authoritative bar revisions and availability time; apply correct trade/quote/bar semantics,
including stock conditions/corrections and zero-volume crypto bars. Rebuild recursive indicators
from a valid earlier checkpoint/full warm-up. Preserve past decision snapshots and mark missed
opportunities as missed; do not execute stale backlog decisions after reconnect.

Do not assume quote hashes/timestamps or trade IDs are globally unique. Verify identity scope.
Preserve raw repeated receipts independently of idempotent canonical effects. Do not claim an
HTTP bar backfill reconstructs the original quote/orderbook tape.

Exit: actually disconnect a data socket for 120 seconds, record the real time window and rebuild
the declared bar strategy's inputs against independently fetched same-feed history. Exercise
silent stalls and provider/REST failures separately with labeled fault injection. No invented
"network outage" claim when the test only closed an application socket. Produce a gap report.

## Phase 3: news, features and immutable decision inputs

Add news ingestion and overlapping historical repair. Store article ID, observed revision, source,
publisher times, local availability, symbols, raw licensed content, sanitized text and checksum.
Handle corrections with unchanged publisher time, missing content and syndicated duplicates.

Compute numerical features deterministically from validated closed data. Keep versions and
input dependencies, explicit warm-up and missing-data flags. Build a consistent database snapshot
and pin exact market/news/account versions with expiry and algorithm/policy/source revisions.
End the database transaction before inference. No tool may silently fetch changing latest data
for a snapshot-bound analysis. Prevent future or post-cutoff news from leaking into replay.

Exit: repeatable as-known replay, deterministic feature parity, exact provenance and coverage
checks. Backfilled/revised data must not rewrite the evidence of an older executed decision.

## Phase 4: bounded master/subagent system

Implement a deterministic harness around a fixed master task graph and bounded synthesis. The
initial task plan is code, not an additional LLM planning call. Only allowlisted
technical/news analyst roles; no recursive delegation or arbitrary workflow generation. Run
independent analysts in parallel. Portfolio arithmetic and executable limits stay ordinary code.

Typed read-only tools return snapshot-scoped features, limited candles, allowed article versions,
account/risk context where permitted, and completed analyst results. Deny arbitrary SQL, shell,
URLs, file access, broker writes and policy editing. MCP, if introduced for multiple clients,
wraps the same handlers and authorization checks; it does not grant extra authority.

Persist cycle/role/attempt generations, deadlines, input hash, prompt/model/tool revisions,
structured results, concise rationales and citations. Validate all references against the pinned
snapshot. Enforce a global deadline/call/token/concurrency budget. Required role failure expires
the proposal; optional-role omission requires an explicit previously tested policy. Late results
cannot win after a retry or new generation. No forced majority vote, endless debate or trade.

Treat news as untrusted content. Test instructions embedded in news, forged citations, stale
article versions, mismatched snapshots, malformed delegation and double terminal proposals.
Structured generation is useful but never a substitute for semantic and authority validation.

Exit: real public-input role/tool execution plus controlled failure cases. Account-aware inference
and local model hosting are separately identified as tested or blocked, not silently assumed.

## Phase 5: portfolio allocation and safe paper execution

The master proposes action and bounded target exposure. Code computes feasible quantity using
fresh broker data, exact increments, cash/fee buffer, pending orders, reservations, absolute and
fractional order caps, symbol/portfolio limits, liquidity/spread/freshness and persistent controls.

Serialize account allocation across all symbols/cycles. Reserve feasible funds/exposure and
commit a unique decision/intent before any broker POST. Recheck data/broker/account freshness,
snapshot expiry, ownership and control/policy versions at the final submission gate. A stale
cached balance or an LLM's confident statement is not authorization to spend.

One POST attempt per durable intent. Never make the execution stage a generic automatically
retried job. Preserve response/error evidence; timeouts and lost commits become UNKNOWN.
Reconcile by client ID, orders, fills, activities and holdings. Retain uncertain reservations.
Support partial fills, cancel/fill races, broker rejections, delayed account views, fees and dust.

Add an independent paper order-update WebSocket adapter with binary/text handling and REST
reconciliation fallback. Market-data and broker-order stream health are independent. Reconcile
duplicate/out-of-order events by fill evidence/cumulative quantity, not a simplistic status rank.

HALTED, NO_NEW_RISK, loss latches and emergency policies have explicit semantics. Bound the halt
wait for an already-authorized POST and show pending state. A cancellation request is not proof
of no fill. Model outages block discretionary entries without killing ingestion/risk monitoring.

Exit: controlled process/DB/halt races on both supported database profiles, then an actual bounded
paper lifecycle through persisted data → analysts/master → sizing/risk → intent → broker ID →
fill → position → exit/restart. Preserve the unresolved earlier incident until genuinely resolved.

## Phase 6: local models, HA, capacity and operations

When implementing local hosting, pin weights/tokenizer/revision and serving version. Test the
actual model's tools/schema behavior, memory, concurrency, queue delay and failure modes. Keep
GPU OOM/driver failure off the collector/executor resource path. Test a genuinely independent
local replica before calling it a fallback. Do not silently send private payloads to a cloud API.

Configure one-command startup, persistent volumes/database, compatible migrations, least-privilege
identities, TLS, secret rotation, structured logs, component-level readiness and real alerts. Test
actual alert delivery. Monitor source/receive/commit/projection/snapshot/order latencies separately.

Measure load distributions and sustained/burst/recovery convergence. State p50/p95/p99 with
sample size and measurement boundary, not just one observed fast call. Verify bounded queues,
timeouts, rate budgets, archive retention, disk/WAL growth, backup restore, replication/fencing
and broker reconciliation after restore. Redis/Kafka are added only against measured needs.

Exit: repeatable fresh install, restart and evidence export on the intended persistent host;
failure drills and observed RPO/RTO limits documented. No transient workspace process is called
a deployed unattended service. Continue the real required multi-day paper observation period.

## Final deliverables and review

- Working streaming system with documented startup, current schema and explicit recovery paths.
- Architecture/decision log with primary sources, assumptions and measured trade-offs.
- Real stream/recovery artifacts, labeled simulated broker faults and actual paper lifecycle proof.
- Complete decision/tool/risk/order journal and broker order/activity/equity/benchmark exports.
- At least two measured experiments, including single-agent/rule versus bounded multi-agent
  behavior where useful; keep changed state and simulation versus real trades separate.
- Results/learnings, actual costs, latency/load/failure results, build/incident logs and unresolved
  limits. Never promise profitability, perfection, zero data loss or exactly-once external execution.

Run required lint/format/tests/JS/credential/diff checks appropriate to code changes, push only
the authorized repository and inspect CI. A design-only commit needs link/consistency/diff checks;
do not rerun an old code suite and represent it as new WebSocket or realtime evidence.
