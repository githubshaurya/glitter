# Experiments

Freeze strategy/prompt versions and the observation window before evaluating. Do not tune the
strategy to a three-day sample. All experiment commands are broker-read-only: they call no
submission service. Model replay still consumes tokens and requires private-context approval
when using stored portfolio observations.

## Experiment 1: add agent vetting

Hypothesis: the agent changes eligible rule-only entries with auditable evidence, at acceptable
operational cost. Change only the entry approval step. Both paired decisions use the same frozen
observation, candidate and initial risk assessment. Only treatment can execute paper orders.

Measure eligible BUY candidates, valid verdicts, veto/HOLD rate, changed-decision rate, provider
errors, latency and token usage. Missing model output is an operational failure, not a successful
veto. A referenced field existing is only syntactic evidence validity, not rationale correctness.
Manually inspect explanations for invented facts and unsupported claims.

The paired comparison establishes participation and cost, not financial superiority. Once a
policy vetoes an entry, future cash/holdings diverge. Do not evaluate rule-only orders against
the treatment's live portfolio state as though that were an independent counterfactual.

Optional `RUN_PORTFOLIO_REPLAY=true` creates two equal all-cash simulated accounts. Each gets
the same chronological recorded quotes/features, but computes its own candidates, holdings,
daily loss state, risk decisions and portfolio context. Treatment calls the agent again on its
own state. Fill assumptions are deliberately simple: observed bid/ask, configurable slippage,
full or zero IOC fill and explicit crypto fees. This ignores inference latency, depth and partial
fills; disclose it. A sparse three-day replay is descriptive, not a statistical significance test.

## Experiment 2: change model only

Hypothesis: GPT-OSS 20B retains valid tool/verdict behavior with lower latency or token use than
120B. Use identical frozen observations, prompt, reasoning effort, tools, risk policy and schema.
Alternate call order across observations to reduce a fixed ordering effect. Never send replay
orders to Alpaca. A model comparison uses fresh responses, not an invented smaller-model result.

Measure each model's valid terminal verdicts, errors, approvals, mean latency, tokens and paired
verdict disagreements. Exclude invalid pairs from disagreement rate and report their count.
Token usage is not billed cost; use actual provider billing where available. Free-tier quotas
and transient provider load can dominate a small latency sample. No deterministic model-output
guarantee is asserted even at low temperature.

## Actual performance

Export the complete paper order window, activities and equity separately. Compare BTC gross
buy-and-hold over exactly the aligned equity timestamps. Do not mix simulated P&L into account
return. Report gross win rate from completed long-only round trips; unknown opening inventory
and coin-denominated fees can make it unavailable. Net win rate needs fee attribution and is not
silently substituted with sell-order success rate. Report zero completed trades as N/A win rate.

Safety tests are not financial experiments. Synthetic test prices and fake brokers are labeled
test doubles and never become strategy results. Public commissioning HOLD checks are neither
an experiment sample nor evidence of an executed trade.

## Completed public-only measurements

`uv run glitter-public-replay` uses only historical public market observations; no account
context or broker order is involved. The entry-focused protocol screens a fixed 28-day 08:00
UTC grid and selects the first 12 past-only positive-EMA candidates. It persists the selection
before inference, alternates model order, reports failures and never sends forward scoring data
to the model. See EXPERIMENT_RESULTS.md for the retained pilot, follow-up and limitations.
These measurements do not certify account-aware trading or replace the required forward run.
