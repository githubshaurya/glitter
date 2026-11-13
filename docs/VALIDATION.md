# Validation status

## Observed locally

- 43 Python tests passed with SQLite after the latest regressions.
- 43 tests passed against actual PostgreSQL 16 after the latest regressions.
- Ruff lint, formatting and JavaScript syntax passed.
- Real Alpaca paper account, allowed assets, quotes and 300-hour history reads succeeded.
- Real GPT-OSS 120B public-market tool loop succeeded and returned HOLD.
- Broker-only proof-pack command succeeded using actual account snapshots and aligned BTC prices.
- .env is ignored, permission-restricted, and excluded from Docker's build context.
- Dedicated personal engineering skill validated, installed and forward-tested read-only.

## Not claimed

- No actual strategy order or full private-context cycle was successfully tested in this session.
- No three-day unattended run, profitability result or completed financial experiment is claimed.
- No external database, public dashboard, GitHub secret or trading enable variable was provisioned.
- Docker image build was not run locally because Docker is unavailable here.
- Local browser rendering was blocked by environment sockets; remote desktop/mobile checks passed.

## Observed remote CI

[Successful run](https://github.com/githubshaurya/glitter/actions/runs/43381317121), source
58ef2ac5568882124f29fbbac2876c9769c5fe8a: 43 SQLite tests, 43 PostgreSQL tests, lint,
formatting, frontend syntax and two desktop/mobile browser tests passed. Browser tests use
synthetic data, not invented portfolio results. Screenshot artifacts are retained with the run.
The first run's unsupported OS/browser combination was fixed by pinning Ubuntu 24.04.

The workflow additionally builds/boots the Docker image and checks health, index serving and
API authentication. That newly added smoke check is pending its first observed run.
