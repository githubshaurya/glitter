# Evidence used for implementation

The assessment is the authority for scope: paper only; real tools; independent hard risk limits;
3+ crypto calendar days; at least two measured experiments; broker evidence; honest build log.
No claim of trading profitability follows from these engineering choices.

## Official API and systems references

| Source | Consequence in this repository |
|---|---|
| [Alpaca paper trading](https://docs.alpaca.markets/us/docs/paper-trading) | Fixed paper endpoint; actual paper fills remain simulations with real-market omissions. |
| [Crypto orders](https://docs.alpaca.markets/us/docs/crypto-orders) | Fractional limit orders and IOC; never assume successful submission means a full fill. |
| [Crypto spot trading](https://docs.alpaca.markets/us/docs/crypto-trading) | No margin/shorting, asset precision, fee awareness; use non-marginable buying power and cash. |
| [Order lookup](https://docs.alpaca.markets/us/reference/getorderbyclientorderid) | Reconcile durable client order IDs after uncertain responses. |
| [Market-data FAQ](https://docs.alpaca.markets/us/v1.4.2/docs/market-data-faq) | Zero-volume crypto bars can contain midpoint-based prices; use quotes for execution. |
| [Crypto historical bars](https://docs.alpaca.markets/us/reference/cryptobars-1) | Follow next_page_token; page limits apply across symbols. |
| [Account activities](https://docs.alpaca.markets/us/reference/getaccountactivities-2) | Follow activity IDs as pagination tokens; export full window, including fees. |
| [Portfolio history](https://docs.alpaca.markets/us/reference/getaccountportfoliohistory-1) | continuous intraday reporting and no_reset for crypto; align benchmark to actual equity timestamps. |
| [Groq local tools](https://console.groq.com/docs/tool-use/local-tool-calling) | Application executes approved tools; model never calls the broker directly. |
| [Groq reasoning](https://console.groq.com/docs/reasoning) | GPT-OSS medium effort; no unsupported reasoning_format; do not store private reasoning. |
| [Groq structured outputs](https://console.groq.com/docs/structured-outputs) | Tool calls plus local validation instead of mixing tool mode with a strict response-format request. |
| [PostgreSQL explicit locking](https://www.postgresql.org/docs/current/explicit-locking.html) | Dedicated session advisory lock for cycle ownership, row lock for submission/stop serialization. |
| [GitHub schedule troubleshooting](https://docs.github.com/en/actions/how-tos/troubleshoot-workflows) | Offset cron, persistent slot constraints and measured coverage; no scheduler punctuality guarantee. |

Reviewed 2026-11-13. Documentation can change; uv.lock pins the environment used here.

## Requested skill repositories

These are third-party engineering checklists, not API specifications or proof of reliability.
Read relevant material, then test the concrete implementation against official contracts.

| Repository and reviewed revision | Assessment and adopted checks |
|---|---|
| [proyecto26/system-design-skills](https://github.com/proyecto26/system-design-skills/tree/228d57dc6fa7627a6426553fdd6ad0040e36f361) | Reviewed resilience/failure guidance. Adopt bounded I/O, cautious retries and explicit failure policy. Its broad scalability material is unnecessary for two symbols. |
| [hung-phan/system-skills](https://github.com/hung-phan/system-skills/tree/9608d61a1910b03e6c16a4609d31afee3b7b96d1) | Reviewed modular-monolith material. Keep narrow modules in one process; no independent scaling requirement justifies microservices. |
| [anilamar/software-architecture-skills](https://github.com/anilamar/software-architecture-skills/tree/e7813b884fa4f5c170275c7970b8d14fe1cadac3) | Reviewed idempotency design guidance. Durable unique intent and explicit uncertain outcomes are useful; a key does not create an atomic database/broker transaction. |
| [ml4t/skills](https://github.com/ml4t/skills/tree/691857537a0c8befc11dc2f2ad7a458b7c7e801c) | Reviewed live-trading and cost-model checks. Adopt point-in-time inputs, distinct simulated/broker evidence and transaction-cost disclosure. ML pipelines, optimization and RL are outside this assessment. |

No third-party installer or generated trading script was executed. A concise dedicated personal
engineering skill was authored around the actual safety and evidence boundaries.

## Visual reference

[Requested Robinhood design guide](https://github.com/Khalidabdi1/design-ai/blob/main/design-md/robinhood/DESIGN.md):
white/black base, vivid green accent, restrained cards, simple hierarchy and sparse navigation.
The dashboard does not impersonate Robinhood or use its logo. No market-return values are
invented to make an empty dashboard look active.
