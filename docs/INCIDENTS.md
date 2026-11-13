# Incidents and fixes

## Development: proxy support

The initial standard-library Groq probe returned 403. An explicit httpx client subsequently
succeeded. The environment also uses a SOCKS proxy, so plain httpx initialization failed without
socksio. Added the supported httpx[socks] extra and locked dependencies. Do not infer an invalid
credential from the first probe; no provider-side root cause was established.

## Development: account-context transfer blocked

Automatic approval review rejected the integrated cycle because private Alpaca account balances,
positions and orders would be sent to Groq without sufficiently explicit transfer permission.
No workaround or indirect retry was used. Added AGENT_ACCOUNT_CONTEXT_ENABLED=false by
default, with a regression test proving no transport request occurs while disabled. Public-market
model checks and broker-to-local exports remain separate. Full account-context trading tests await
approval. No successful trading run is claimed.

## Review: final submission race

Risk was initially evaluated before persisting the intent and acquiring the controls lock. A paused
worker could resume with an old quote/signal. The final locked gate now reruns all risk checks
and requires the exact same payload immediately before POST. A delayed-after-intent regression
asserts that no POST occurs when the quote expires.

## Review: information and replay boundaries

Feature computation excluded current/future candles, but the optional model candle tool initially
stored raw returned bars. Both now use the same validated closed history. A simulation candidate
also retained a datetime in a model JSON payload; switched to JSON-mode serialization. Report
activity counts initially used day-only filtering; timestamped activities now use exact bounds and
date-only records are exported separately.

## Environment: browser and PostgreSQL sockets

The test environment rejects Unix sockets. PostgreSQL tests succeeded using TCP and a local
test-only instance. Local Chromium's process-singleton socket still failed; cloud browser access
to the local preview was refused. Browser UI checks are configured in remote CI with synthetic,
explicitly labeled test data. This is not evidence that the application itself cannot run a browser.

## First CI: runner OS drift

The first remote CI run passed all 43 SQLite tests and all 43 PostgreSQL tests, plus lint,
formatting and JS syntax. Browser installation failed: ubuntu-latest had advanced to Ubuntu
26.04, unsupported by the pinned Playwright version. Pinned the test runner to Ubuntu 24.04
and Python 3.12. This is a setup failure, not a claimed passing UI test.
