# Results and engineering learnings — incomplete forward-run draft

Status at 2026-11-13 UTC: **not ready to submit**. This draft records work actually observed.
The required three unattended crypto calendar days, successful account-aware order trace and
actual operating bills still need completion. Do not present the inactive account export as a
trading strategy result. Personal ownership/reflections must be reviewed by the candidate.

## System and measured evidence

One Python service operates hourly BTC/USD and ETH/USD candidates, one bounded Groq agent,
independent Decimal risk checks and a durable SQLite/PostgreSQL journal. The model can read
approved context/candles and submit a verdict; it cannot write broker orders. The fixed broker
host is Alpaca paper. New orders are capped at the smaller of $1,000 and 1% of equity; symbol
and account exposure caps are 2% and 4%, observed daily loss 1%, peak drawdown 2%. Loss
latches persist. HALTED serializes with submission and requests cancellation, without promising
to undo a request already accepted or to guarantee a maximum realized loss.

The proof-export check covers 06:30–14:45 UTC on November 13: 34 equity observations, zero
orders, zero fills, zero completed round trips, 0% account return and sampled drawdown. Win rate
is unavailable. The aligned BTC gross buy-and-hold benchmark returned +0.5665%, with sampled
drawdown 0.9774%. This was an inactive paper account, not a continuous autonomous run.

Hardening verification passed 84 tests on SQLite and 84 on actual PostgreSQL, two desktop/mobile
browser tests, and Docker build/start/auth/readiness/persistence through container replacement.
Separate OS workers contend for one slot; actual SIGKILL before submission and after simulated
broker acceptance recover without another POST. Broker responses in those fault tests are
simulated. See [the passing workflow](https://github.com/githubshaurya/glitter/actions/runs/43448651072).

## Experiments

The fixed six-day public-history pilot had 12 HOLD observations and no BUY candidates, so it
failed to test entry vetting. That result is retained. A follow-up screened a fixed 28-day
08:00 UTC grid and took the first 12 eligible past-EMA entries, without model/future selection.

Adding primary-model vetting yielded five approvals, six vetoes and one invalid-evidence
response. All 11 valid decisions match a simple positive-four-hour-trend filter on this sample.
The subsequent gross 24h close returns averaged -1.4603% for approved samples and -0.6673%
for vetoed samples. These are price diagnostics, without executable fills or costs; they do not
establish financial advantage. Changing only model gave 120B/20B mean tool-loop latencies of
7.308s/5.283s, validity 11/12 versus 12/12, and zero disagreements in 11 valid pairs. Across
pilot and follow-up, each model failed once in 24 samples. This is too small to infer superior
reliability. Tokens and all original outcomes are in EXPERIMENT_RESULTS.md and public evidence.

## What broke and what the evidence changed

A public-only, at-most-$2 paper plumbing probe reached UNKNOWN after one POST and BrokerError.
The broker lookup and exports found no order/fill. The original HTTP details were missing;
the cause remains unconfirmed. No retry occurred. Diagnostics now retain sanitized broker
status/code/message and survive later misses. The journal remains HALTED for operator review.

A worker could die while trying to log a database outage, leaving a green liveness route.
Exception handling now preserves the scheduler and separate readiness fails on stale cycles,
model errors, unavailable storage or uncertain orders. Fill accounting now groups partial exits,
deduplicates activities, handles linked coin/USD fees and reports uncertain fee attribution.
One equity sample no longer creates a purported return. Late-posting fees remain provisional.

Manual rationale inspection caught unsupported execution-safety statements inferred from ATR
without a quote. Prompt v3 forbids that inference; a targeted three-sample real-model check
returned valid verdicts, with two explicitly acknowledging unknown execution quality. These
checks do not prove semantic correctness. Numeric execution constraints remain independent.

The central engineering lesson is that a valid schema and a passing test suite do not prove a
real broker lifecycle. Safe uncertainty costs availability; erasing it to obtain a demo would
destroy the evidence. Likewise, identical decisions from an agent and a simple rule do not
prove the agent adds economic value. The assessment needs operational proof, not novelty.

## Cost, tools and next work

Tools used: ChatGPT/Codex for implementation/review, GitHub Actions, Python/uv/pytest/Ruff,
Playwright, PostgreSQL, Alpaca paper APIs, Groq GPT-OSS 120B/20B and official documentation.
The two comparison runs used 87,271 reported tokens total; the three-sample v3 regression used
7,015. Other commissioning/check calls consumed additional tokens. No actual billing invoice
or hosting bill was available; **monetary cost is unverified**, not reported as zero.

Next: resolve the broker incident independently, obtain explicit private-context transfer
consent, commission a complete account-aware order and restart, deploy one durable writer,
collect the required three-day window, reconcile late fees and fill the actual results/bills.
Then rehearse an actual broker-order-to-verdict trace and one small live code change.
