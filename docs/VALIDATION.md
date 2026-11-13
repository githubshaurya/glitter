# Validation status

Current detailed assessment: [pre-submission review](PRE_SUBMISSION_REVIEW.md) and
[measured public-data experiments](EXPERIMENT_RESULTS.md). The expanded CI result is pending
until its commit workflow is observed; older runs below remain historical evidence.

## Observed locally

- 84 Python tests passed with SQLite after the strict pre-submission regressions.
- 84 tests passed against actual PostgreSQL 16 after the strict pre-submission regressions.
- Ruff lint, formatting and JavaScript syntax passed.
- Real Alpaca paper account, allowed assets, quotes and 300-hour history reads succeeded.
- Real GPT-OSS 120B public-market tool loop succeeded and returned HOLD.
- Real GPT-OSS 20B replayed the same public commissioning context successfully: HOLD, 1,770 tokens, 8.94 seconds on that single check. This is an integration check, not a financial experiment.
- Broker-only proof-pack command succeeded using actual account snapshots and aligned BTC prices.
- .env is ignored, permission-restricted, and excluded from Docker's build context.
- Dedicated personal engineering skill validated, installed and forward-tested read-only.

- Separate spawned-process contention and SIGKILL before POST/after simulated acceptance passed.
- Real public-only at-most-$2 probe produced an unresolved UNKNOWN, no found broker order or fill. No retry occurred; HALTED persists. A separate zero-quantity API probe returned the expected 422 rejection.
- Completed two public historical engineering comparisons with measured failures, latency and token counts; original datasets retained. Account-aware forward experiments remain pending.

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

The [final code verification run](https://github.com/githubshaurya/glitter/actions/runs/43382147168)
for 26bc8dfbf7f71f34424ee5a175cec8e3ce754c40 passed every stage, including both database
suites, both browser tests, Docker image build/start, health and index serving, and unauthenticated
API rejection. Docker verification used a synthetic dashboard token and no brokerage keys.
