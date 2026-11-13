# Glitter implementation rules

- Read README.md, docs/ARCHITECTURE.md and docs/RUNBOOK.md before changing order behavior.
- Backend languages allowed: Python and Rust. Use Python unless profiling justifies Rust.
- Paper only; never add a configurable live broker URL. Never commit .env, keys or account exports.
- Keep core numerical code plain, readable and visible. No generic runner/factory/registry layer.
- Preserve unique UTC slot and client-order IDs, commit-before-submit, one POST attempt and UNKNOWN reconciliation.
- All account writers use one database. PostgreSQL locks require direct/session connections.
- Recheck controls, current data ages and risk at the final serialized submission gate.
- Agent tools cannot submit orders. Private account context requires explicit transfer opt-in.
- Keep actual paper evidence, paired decision observations and simulated portfolios distinct.
- Do not fabricate trades, experiments, costs, latency guarantees or multi-day completion.
- Update build/incident logs with actual observations. Run both SQLite and PostgreSQL tests for safety changes.
- Required checks: uv run ruff check .; uv run ruff format --check .; uv run pytest; node --check trading/static/app.js.
