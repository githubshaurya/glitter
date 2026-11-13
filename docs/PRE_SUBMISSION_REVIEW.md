# Pre-submission engineering review

Reviewed 2026-11-13 UTC. **Not ready for assessment submission.** Automated safety checks are
stronger, but the broker order lifecycle and required elapsed observation period are unverified.
This document distinguishes evidence from implementation and deployment assumptions.

| Assessment requirement | Evidence / remaining work |
|---|---|
| One-command service | Docker workflow builds/starts the image, serves UI and checks authentication; expanded workflow also verifies persisted HALTED after container replacement. Inspect the associated CI result before calling the expanded check passed. |
| Real bounded agent | Public-data Groq tool calls work. Private account-aware cycle was rejected by automatic approval review; explicit transfer consent remains required. |
| Real paper order and fills | A public-only, at-most-$2 operational probe reached UNKNOWN after one POST attempt. Broker lookup and exported orders found no order. No fill or successful lifecycle is claimed. |
| Restart and ambiguity recovery | Separate OS process SIGKILL before POST and after simulated acceptance, new repository/process connections and broker lookup; no second POST. These broker records are simulated, not actual Alpaca acceptance. |
| Concurrency | Three spawned workers share one database/slot; exactly one simulated submission. Both SQLite OS locks and real PostgreSQL session locks tested. |
| Stops | Final-gate races tested, including halt waiting for an already-authorized request. Actual paper HALTED persisted and cancellation endpoint returned; no open orders existed. No claim of cancellation of a live pending order. |
| Accounting | Decimal fill ledger, deduplication, partial entries/exits, linked coin/USD fees, date-only coin residuals, unknown inventory and unallocated-fee cases tested. Fees can post later; net results remain as-of-export. |
| Three unattended crypto days | Not completed. Scratch processes are not a durable deployment. No continuous observation period has been started or certified. |
| Two measured experiments | See EXPERIMENT_RESULTS.md for actual public historical replay; account-aware financial counterfactual remains unmeasured. |
| Final proof pack/results/learnings | Export infrastructure works; meaningful strategy window, broker fills, actual bills and personal reflections remain. |

## Release gates

1. Approve the exact private-data transfer if desired: balances (equity/cash/buying power),
   positions and open-order details to Groq. Credentials and account/order identifiers are
   excluded from model context. No setting is silently treated as renewed consent.
2. Resolve the retained UNKNOWN through operator/broker review. Lookup absence alone does not
   prove that submission never occurred. Do not delete the journal, change database, retry the
   old client ID or submit a new risk-increasing probe to get around this state.
3. Commission a genuine account-aware candidate through real tools, coded risk, exact intent,
   broker order, fills and position; confirm in the independent paper dashboard. Commissioning
   orders belong outside the strategy performance window.
4. Run on an always-on Linux/Docker host with persistent volume, or provision direct/session
   PostgreSQL plus scheduler secrets. Every writer must use that same database. Verify backups,
   authenticated readiness, stale-cycle alerts, restart and cancellation on that deployment.
5. Collect at least three crypto calendar days of real unattended observations. Export daily,
   wait for late fees, reconcile quantities/cash, annotate gaps and report actual outcomes.

## Engineering choices and limits

Two symbols and hourly decisions do not justify microservices, an MCP server, Rust, a message
queue or distributed caches. The bounded tool interface already provides the necessary data
and verdict capabilities without broker-write tools. Scaling this implementation means first
measuring provider latency, quota and storage growth; multi-account workers need explicit
per-account coordination rather than reusing the global account lock unmodified.

Readiness is separate from liveness. Model errors, uncertain orders, stale workers, interrupted
decision slots and database outages fail readiness. No automated alert destination is configured;
an endpoint is not an alerting service. IOC orders can have no fill or a partial fill. Loss limits
are sampled equity latches, not guaranteed execution stop losses. Manual broker actions remain
outside this application's lock; journal ownership checks prevent selling an unexplained larger
position, but a dedicated account is still required.

The paper probe exposed missing HTTP diagnostics. New errors retain sanitized status/code and
message; reconciliation now preserves the original diagnostic rather than overwriting it with
a later 404. The original response details were not retained, so its cause is unconfirmed.
Fine-grained asset metadata is now combined with a conservative cent price grid, consistent
with Alpaca's documented order-price precision. This is not claimed as the proven incident cause.

Official references: [order precision](https://docs.alpaca.markets/us/docs/orders-at-alpaca),
[crypto fees](https://docs.alpaca.markets/us/docs/crypto-fees),
[activities](https://docs.alpaca.markets/us/docs/account-activities),
[activity API](https://docs.alpaca.markets/us/reference/getaccountactivities-2).
