# 1. Working system

The app lets a reviewer replay a historical market window, inspect each council role's evidence and verdict, and follow a decision through sizing, risk checks, and simulated fills. A separate scheduler can submit approved orders to Alpaca's paper endpoint. [Public repository and Docker instructions](https://github.com/githubshaurya/glitter)

## Run from the cloned repository

Copy `.env.example` to `.env` and set `ALPACA_PAPER_KEY_ID`, `ALPACA_PAPER_SECRET_KEY`, and `GROQ_API_KEY` locally. With Docker and Compose running, use this command.

```sh
docker compose -f compose.app.yml --profile kafka up --build
```

Open [the local app](http://localhost:8765). In **Simulation**, choose a Nasdaq ticker, historical date, start time in Eastern Time, duration, virtual cash, and holding policy. For a run on one of the proof windows, use MU on September 9, 2025 at 1:10 p.m. ET, $8,000, 30 minutes, intraday, full council, and Skeptic off. The proof used a local replay harness that only requested discretionary exit reviews at positive executable P&L and rechecked that P&L at submission. A fresh UI replay exercises the public app and its regular review cadence. Saved browser history lasts for the running app session.

Select a decision to inspect completed candles, feature values, role responses and the Chair verdict. Expand **STAR audit** to inspect the date, instrument, portfolio, strategy, role, and associated fills.

## How it works

1. Alpaca WebSocket data feeds the realtime recorder. REST fills recoverable gaps. The recorder persists checkpoints and deduplicates overlapping records.
2. Python calculates indicators from completed candles and seals a point-in-time feature snapshot. Technical, Regime, Liquidity, and Portfolio consume its observations. Relevant article text goes to News.
3. The council validates role responses and the Chair's choice against the available actions and evidence. The historical UI prices fills on the executable side at simulated submission time.
4. In the paper path, code enforces symbol, cash, exposure, daily loss, price freshness, and deadline limits. PostgreSQL serializes exposure reservations and stores durable intents. Kafka carries notifications. Stable client order IDs let the executor reconcile ambiguous broker outcomes.
5. The default Docker UI sets `EXECUTION_ENABLED=false`. The separate paper stack explicitly enables submissions, uses a paper-only broker host check, and keeps a kill switch and position protection.

During the November 23 broker run, the app used separate timer-bounded paper configurations with an independent safety closeout. INTC also used a local council override to disable Skeptic while retaining Chair approval and the risk gate. The broker results and their scope are recorded in the [proof pack](02-proof-pack.md).
