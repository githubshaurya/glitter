# 2. Proof pack

Three 30-minute September 2025 windows used Alpaca SIP candles and quotes. Each began flat with $8,000 in virtual cash, with full council review and Skeptic off. The sample covers a long in MU, two shorts in AAPL, and a long in NVDA. The replay evaluated held positions at minute checkpoints. A positive executable quote triggered a fresh council review, and a profit-taking order still needed to be profitable when submitted. Existing stop protection and the cutoff remained in effect.

## Financial results

| Date | Ticker | Window ET | End equity | P&L | Return | Max observed drawdown | Filled orders | Closed / won | SPY return |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| Sep 9, 2025 | MU | 13:10–13:40 | $8,000.75 | +$0.75 | +0.009375% | 0.0025% | 2 | 1 / 1 | +0.0508% |
| Sep 10, 2025 | AAPL | 11:20–11:50 | $8,000.48 | +$0.48 | +0.0060% | 0.0154% | 4 | 2 / 2 | +0.1364% |
| Sep 22, 2025 | NVDA | 12:35–13:05 | $8,001.20 | +$1.20 | +0.0150% | 0.0405% | 2 | 1 / 1 | +0.0668% |

The four closed trades yielded **+$2.43** in total and **4 of 4 wins**. All accounts ended flat. Returns use each window's own $8,000 ledger. Drawdown is based on recorded equity marks. The simulated fill price is the bid for a sale and ask for a buy, subject to the recorded limit and displayed depth. P&L reflects the spread and assumes zero additional fees. SPY is normalized to $8,000 at each window's open and held until that window's close. SPY returned more than the strategy over each selected window. Per-window numbers and SPY observations

![Simulated account equity and SPY over each window](assets/equity-vs-spy.png)

| Ticker | Trade | Entry → exit | Held | P&L | Input → Chair, entry / exit |
|---|---|---|---:|---:|---:|
| MU | Long 5 | $136.35 → $136.50 | 2m 59s | +$0.75 | 3.88 / 3.10 s |
| AAPL | Short 3 | $227.15 → $227.09 | 6m 02s | +$0.18 | 3.56 / 5.22 s |
| AAPL | Short 3 | $226.63 → $226.53 | 2m 00s | +$0.30 | 3.56 / 3.33 s |
| NVDA | Long 4 | $183.70 → $184.00 | 19m 00s | +$1.20 | 3.43 / 3.76 s |

## Evidence to check

| Window | Orders | Strategy equity | SPY equity | Decision log |
|---|---|---|---|---|
| MU | CSV | CSV | CSV | JSONL |
| AAPL | CSV | CSV | CSV | JSONL |
| NVDA | CSV | CSV | CSV | JSONL |

Verified trades and order timestamps · [All 90 slots and council outputs](03-decision-journal.md)

## Broker-backed paper evidence

The app submitted orders to Alpaca’s paper broker on **November 23, 2026 ET**. AAPL ran first, followed by INTC. Alpaca recorded **five fill events across two round trips**, with **one win** and **+$3.58 realized paper P&L**. Equity moved from **$99,803.39 to $99,806.97**, a **+0.0036%** return across the two windows. The account ended flat with no open orders.

| Ticker | Window (ET) | Broker order records | Fill events | P&L (USD) | Paper return | Sampled drawdown | Matched SPY return |
|---|---|---:|---:|---:|---:|---:|---:|
| AAPL | 14:26–14:41 | 5 | 2 | -0.33 | -0.0003% | 0.0007% | -0.2495% |
| INTC | 14:44–14:59 | 5 | 3 | +3.91 | +0.0039% | 0.0006% | +0.1789% |

| Ticker | Shares | Entry → exit | Entry ET | Exit ET |
|---|---:|---:|---|---|
| AAPL | 1 | $350.15 → $349.82 | 14:29:11 | 14:39:12 |
| INTC | 17 | $58.02 → $58.25 | 14:50:14–14:50:15 | 14:57:06 |

Order records include canceled orders and protective legs. Drawdown uses the broker's one-minute equity marks. The SPY comparison uses IEX prices over the same minutes.

![Alpaca paper equity versus SPY for AAPL and INTC](assets/aapl-intc-equity-vs-spy.png)

The Chair approved both entries. AAPL's entry included Skeptic. INTC recorded zero Skeptic attempts. Both partial fills triggered a safety halt, and the app's managed closeout sold both positions near their cutoff. The profitable INTC sale leaves council-driven profit-taking unverified.

[Broker orders, account activity, equity, and SPY marks](paper-broker-evidence.md) · [Paper decision journal](paper-decision-journal.md)

The broker-backed run covers **one US trading date**. The three-session requirement remains outstanding.
