# 4. Experiment log

## 1. Council versus deterministic strategy

**Hypothesis.** Bounded council judgment changes decisions and could improve returns under the same risk constraints.

**One change.** The decision policy used either the scored council or the deterministic policy. Market inputs, October 28–November 1, 2024 dates, risk limits, starting capital, cadence, and fill rules were held fixed.

| Measure | Council | Rules only |
|---|---:|---:|
| Completed slots | 104 / 105 | 105 / 105 |
| Simulated orders with fills | 2 | 2 |
| Return | −0.0171% | −0.0222% |
| Max drawdown | 0.0239% | 0.0358% |
| Median / p95 cycle latency | 10.30 / 71.44 s | 3.86 / 15.27 s |

The council improved return by **0.0051 percentage points** in this sample and took longer. Neither policy closed a position campaign, so win rate was unavailable. The sample supports a measured engineering comparison.

## 2. SIP versus IEX historical evidence

**Hypothesis.** SIP will supply more usable snapshots than IEX for the same historical checkpoints.

**One change.** The data feed was switched between SIP and IEX at the same 10:00 a.m. ET checkpoints on October 21–25, 2024. Feature definitions and validation rules were held fixed.

| Feed | Usable checkpoints | Data-incomplete checkpoints | Sampled spread range |
|---|---:|---:|---:|
| SIP | 5 / 5 | 0 / 5 | 0.697–2.847 bps |
| IEX | 0 / 5 | 5 / 5 | 6.269–79.373 bps |

IEX sometimes supplied the technical fields while the regime floor remained unavailable. The run measures usable input coverage on these timestamps.

## 3. Matched September exit diagnostic

**Hypothesis.** Waiting for an executable profit with the original stop and a 30-minute bound may change the outcome of the same approved entries.

**One change.** The exit policy moved from the original Chair exits to a coded positive-P&L exit with a 30-minute cap. The test held the three original approved entries fixed, reproduced their fills, and applied the original stops and observed exit processing delays.

| Exit policy | Closed trades | Wins | P&L |
|---|---:|---:|---:|
| Original council exits | 3 | 1 | −$2.98 |
| Positive executable quote after measured delay | 3 | 3 | +$0.33 |

The matched diagnostic improved these three exits by **$3.31**. MU gave up $0.40 of its original gain, and NVDA's first positive quote disappeared before submission. The later [fresh council run](02-proof-pack.md) is a separate evaluation with new entry and exit decisions.
