"""Public-market replay for two measured engineering experiments. Never submits orders."""

import hashlib
import json
from datetime import timedelta
from pathlib import Path

from trading.broker import AlpacaBroker
from trading.config import PROMPT_VERSION, STRATEGY_VERSION, SYMBOLS, Settings
from trading.experiments import compare_models
from trading.models import now_utc
from trading.repository import Repository, safe_json
from trading.strategy import closed_history, features


def main():
    settings = Settings()
    repository = Repository(settings.database_url)
    repository.initialize()
    broker = AlpacaBroker(settings)
    # Entry-focused follow-up after a six-day fixed-grid pilot had no BUY candidates.
    # Screen 28 completed days at 08:00 UTC, both symbols; take the first 12 BUYs.
    # Selection uses only past EMA values, never model output or forward returns.
    latest = now_utc().replace(hour=8, minute=0, second=0, microsecond=0) - timedelta(days=1)
    if latest + timedelta(hours=24) > now_utc():
        latest -= timedelta(days=1)
    cutoffs = [latest - timedelta(days=offset) for offset in reversed(range(28))]
    try:
        bars = broker.bars(cutoffs[0] - timedelta(hours=300), latest + timedelta(hours=24))
    finally:
        broker.close()
    observations, scores = [], {}
    for cutoff in cutoffs:
        for symbol in SYMBOLS:
            history = closed_history(bars[symbol], cutoff)
            values = features(history, cutoff)
            action = "BUY" if values["ema_spread"] > 0.001 else "HOLD"
            identifier = "public-" + symbol.replace("/", "") + "-" + cutoff.strftime("%Y%m%dT%H%MZ")
            observation = {
                "candidate": {
                    "id": identifier,
                    "symbol": symbol,
                    "cutoff": cutoff.isoformat(),
                    "action": action,
                    "rule": "ema_8_above_24_by_10bps"
                    if action == "BUY"
                    else "no_position_transition",
                },
                "cutoff": cutoff.isoformat(),
                "features": values,
                "candles": [bar.model_dump(mode="json") for bar in history[-24:]],
                "source": "Alpaca crypto/us historical hourly bars",
                "scope": "Public historical market replay with hypothetical flat inventory. Historical quote, account, depth and execution are unavailable; do not invent them.",
                "strategy_version": STRATEGY_VERSION,
                "prompt_version": PROMPT_VERSION,
            }
            observations.append(observation)
            future = next(
                bar
                for bar in bars[symbol]
                if bar.time + timedelta(hours=1) == cutoff + timedelta(hours=24)
            )
            scores[identifier] = {
                "forward_close_return_24h": future.close / values["close"] - 1,
                "observation_sha256": hashlib.sha256(
                    json.dumps(observation, sort_keys=True).encode()
                ).hexdigest(),
            }
    screened = len(observations)
    observations = [
        observation for observation in observations if observation["candidate"]["action"] == "BUY"
    ][:12]
    scores = {
        observation["candidate"]["id"]: scores[observation["candidate"]["id"]]
        for observation in observations
    }
    if not observations:
        raise ValueError("No historical BUY candidates in the fixed screening window")
    scope = "Public-only historical replay; no private account context, risk-eligible live entries, orders, or realized portfolio returns are tested. Forward returns are gross close-to-close diagnostics, not executable P&L. Small correlated sample, no significance claim."
    protocol = {
        "scope": scope,
        "cutoffs": [cutoff.isoformat() for cutoff in cutoffs],
        "symbols": SYMBOLS,
        "protocol_version": "entry-cohort-v2",
        "selection": "First 12 positive-EMA BUY candidates from a fixed 28-day 08:00 UTC grid, both symbols, hypothetical flat inventory; no model/future-outcome selection. Follow-up to the six-day pilot with zero eligible entries.",
        "screened_observations": screened,
        "observations": observations,
        "scores_not_sent_to_model": scores,
    }
    directory = Path(settings.report_directory)
    directory.mkdir(parents=True, exist_ok=True)
    output = directory / ("public-replay-" + now_utc().strftime("%Y%m%dT%H%M%SZ") + ".json")
    # Persist the protocol before inference; retain partial event traces if interrupted.
    output.write_text(json.dumps(protocol, indent=2))
    print(
        json.dumps({"protocol": str(output), "observations": len(observations), "scope": scope}),
        flush=True,
    )
    second = compare_models(settings, repository, observations)
    second["scope"] = scope
    eligible = [
        row
        for row, observation in zip(second["records"], observations, strict=True)
        if observation["candidate"]["action"] == "BUY"
    ]
    primary = [row["results"][settings.groq_model] for row in eligible]
    valid = [result for result in primary if result["verdict"]]
    vetoes = sum(result["verdict"]["verdict"] != "APPROVE" for result in valid)
    groups = {name: [] for name in ("approved", "vetoed")}
    for row in eligible:
        result = row["results"][settings.groq_model]
        if result["verdict"]:
            group = "approved" if result["verdict"]["verdict"] == "APPROVE" else "vetoed"
            groups[group].append(scores[row["candidate_id"]]["forward_close_return_24h"])
    first = {
        "kind": "experiment_1_public_rule_vs_agent",
        "scope": scope,
        "hypothesis": "A bounded agent changes some public-history rule entry candidates and provides valid cited tool verdicts.",
        "change": "Add the primary model's entry-vetting step to identical fixed historical rule candidates.",
        "metrics": {
            "observations": len(observations),
            "rule_buy_candidates": len(eligible),
            "valid_entry_verdicts": len(valid),
            "errors": len(primary) - len(valid),
            "vetoes": vetoes,
            "changed_decision_rate": vetoes / len(eligible) if eligible else None,
            "forward_24h_by_verdict": {
                key: {
                    "count": len(values),
                    "mean_gross_close_return": sum(values) / len(values) if values else None,
                }
                for key, values in groups.items()
            },
        },
        "interpretation": "Descriptive agent participation and gross future-price diagnostics only; no evidence of investment advantage or account-aware operational success.",
    }
    for result in (first, second):
        repository.save_experiment(result)
    output.write_text(json.dumps(safe_json({**protocol, "experiments": [first, second]}), indent=2))
    print(
        json.dumps(
            {
                "output": str(output),
                "experiment_1": first["metrics"],
                "experiment_2": second["metrics"],
            },
            indent=2,
        ),
        flush=True,
    )
    repository.engine.dispose()
