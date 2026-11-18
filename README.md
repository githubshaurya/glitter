# Glitter Trading Lab

Install Docker Desktop or Docker Engine with Compose. From the cloned repository, copy
`.env.example` to `.env` and set `ALPACA_PAPER_KEY_ID`, `ALPACA_PAPER_SECRET_KEY`, and `GROQ_API_KEY`.

```sh
docker compose -f compose.app.yml up --build
```

Open [localhost:8765](http://localhost:8765/). Compose starts the UI, PostgreSQL, and Kafka.
In **Simulation**, choose a NASDAQ ticker, a past trading window with Alpaca SIP data, and a starting
budget. Open a decision to review its evidence, council responses, and risk checks. Simulated order
and fill history clears when the app stops.
