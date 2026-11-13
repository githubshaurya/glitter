# Measured public-data experiments

Measured 2026-11-13 with real Alpaca hourly candles and real Groq requests. No account context,
broker submission, hypothetical fill or portfolio return was used. Prompt: entry-veto-v2;
strategy: ema-8-24-v2. The deployed prompt was subsequently corrected to entry-veto-v3 after
the rationale review below. Results are retained, not relabeled as measurements of v3.

## Protocol and pilot

The initial grid used six completed days, both symbols, 08:00 UTC: 12 observations, all HOLD.
It therefore **failed to measure entry vetting**. GPT-OSS 120B produced 12/12 valid verdicts;
20B produced 11/12, with one provider HTTP 400. Mean latency: 6.357s versus 5.523s; tokens:
19,615 versus 19,606. There were no disagreements among 11 valid pairs. Retained
[pilot inputs and outputs](evidence/public-pilot-v2.json).

Before the follow-up inference, the protocol screened 28 completed days at 08:00 UTC, both
symbols, and selected the **first 12** candidates whose past-only EMA spread exceeded 10bps.
No model output or forward return entered selection. The hypothetical starting inventory is
flat for every sample, not a portfolio simulation. The 12 selected samples span October 16
through November 2. The sample is small and correlated across symbols/dates.

[Entry-cohort inputs, hashes, outputs and scoring](evidence/public-entry-cohort-v2.json) retain
the frozen model-visible 24 candles, features, provider IDs, verdicts, tokens and latency.
Features use 300 completed bars; exact feature recomputation requires refetching that history.
Forward 24h closes were used only for subsequent scoring and were not sent to either model.
Provider model training provenance and stochastic reproducibility were not independently audited.

## Experiment 1: add agent entry vetting

Hypothesis: the bounded agent changes some fixed rule entry candidates with valid cited tool
verdicts. The single change is adding primary-model approval to the same rule candidates.

| Measurement | Result |
|---|---:|
| Rule BUY candidates | 12 |
| Valid primary verdicts | 11 |
| Approvals / vetoes / invalid responses | 5 / 6 / 1 |
| Changed decision rate, all eligible candidates | 6/12 = 50% |
| Veto rate among valid verdicts | 6/11 = 54.55% |
| Mean subsequent 24h gross close return, approved (5) | -1.4603% |
| Mean subsequent 24h gross close return, vetoed (6) | -0.6673% |

The failed response cited an unknown feature key and was blocked. It is an operational error,
not an additional veto. All six valid vetoes cite negative four-hour trend; all five approvals
have positive four-hour trend. A simple positive-four-hour-trend filter matches all 11 valid
primary decisions here. **The agent's incremental financial value is not established.** Both
future-return groups were negative. These are price diagnostics without spreads, fees, latency,
portfolio paths or realizable fills; they do not establish a performance advantage.

## Experiment 2: change model only

Same 12 observations, prompt, tools, reasoning effort and schema; call order alternated by sample.

| Measurement | GPT-OSS 120B | GPT-OSS 20B |
|---|---:|---:|
| Valid verdicts / errors | 11 / 1 | 12 / 0 |
| Approvals | 5 | 6 |
| Mean full tool-loop latency | 7.308s | 5.283s |
| Median latency | 9.756s | 4.684s |
| Empirical p95, nearest rank, n=12 | 11.141s | 10.475s |
| Total tokens | 24,273 | 23,777 |

Eleven valid pairs, zero verdict disagreements; the remaining pair is invalid, not agreement.
The smaller model's mean latency was about 27.7% lower in this cohort. Across pilot and entry
cohort, each model had one failure among 24 observations. This does not establish a reliability
difference or an operational latency guarantee. Tokens are not actual billed cost. Retain 120B
as the existing default pending account-aware evaluation; either model remains configurable.

## Rationale review and correction

All 11 valid primary rationales were inspected against their frozen numeric fields. Their trend
signs and cited numeric values broadly match. Several approvals nevertheless infer "no execution
concern" from ATR/volatility despite the historical quote being unavailable. One veto also
describes higher-timeframe alignment as a strategy requirement rather than an agent criterion.
Schema/evidence validation alone did not catch these semantic overstatements.

The v3 prompt explicitly forbids inferring liquidity/spread/execution safety from OHLC or ATR,
requires execution quality to remain unknown without quotes, restricts citations to exact keys,
and distinguishes agent criteria from coded EMA rules. Independent execution-time quote/spread
and risk checks remain mandatory regardless of rationale. A small targeted v3 regression is
recorded separately; it cannot retrospectively improve these v2 results.

## Decision

The experiments demonstrate real tool participation, measured provider behavior and a useful
failure discovery. They do not replace the account-aware forward run, broker evidence, independent
portfolio counterfactual, costs or three elapsed crypto days required before submission.

Targeted v3 check: three real primary-model calls on two previously overconfident approvals
and the previously invalid-evidence sample all returned schema-valid APPROVE verdicts. Two
explicitly stated execution quality was unknown; the third made no execution-safety claim but
did not explicitly restate that limitation. This is a narrow improvement check, not proof of
semantic correctness or a replacement for the full v2 comparison. See the retained
[prompt regression records](evidence/prompt-v3-regression.json).
