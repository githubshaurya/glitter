"""Typed role contracts and pure evidence aggregation. No indicators or broker calls."""

import math
from copy import deepcopy
from decimal import Decimal, InvalidOperation
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from trader.council.evidence import BASE_FIELDS, MARKET_FIELDS, PORTFOLIO_FIELDS, ROLE_FIELDS
from trader.council.options import size_executable_choices
from trader.council.sizing import entry_caps, order_prices, sellable_shares
from trader.features.bands import BANDS

SIGNALS = ("TECHNICAL", "NEWS")
GATES = ("LIQUIDITY", "PORTFOLIO")
SPECIALISTS = (*SIGNALS, "REGIME", *GATES)


def canon(x):
    if x is None or isinstance(x, bool):
        return x
    try:
        value = Decimal(str(x).strip())
        if value.is_finite():
            return value
    except (InvalidOperation, ValueError):
        pass
    return x.strip().upper() if isinstance(x, str) else x


def same(a, b, rel=1e-9, abs_=1e-12):
    a, b = canon(a), canon(b)
    if isinstance(a, bool) or isinstance(b, bool) or a is None or b is None:
        return type(a) is type(b) and a == b
    if isinstance(a, Decimal) and isinstance(b, Decimal):
        return abs(a - b) <= max(Decimal(str(abs_)), Decimal(str(rel)) * max(abs(a), abs(b)))
    return type(a) is type(b) and a == b


# Band interpretations are versioned separately from indicator calculations.


def band_of(path, row):
    if row.get("status") not in ("OK", "PROVISIONAL") or row.get("v") is None:
        return "UNAVAILABLE"
    name, value = path.split(".")[-1], canon(row["v"])
    if name == "intraday_setup_1m" and isinstance(value, dict):
        return value["confirmation"]
    if name in ("position_qty", "sellable_qty"):
        return "ZERO" if same(value, 0) else "PRESENT"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    key = {"recent_return_5m": "ret_5m", "news_age_min_latest": "news_newest_age_min"}.get(name, name)
    if key in BANDS and isinstance(value, Decimal):
        inclusive = key in ("spread_bps", "news_count_4h", "news_newest_age_min")
        for upper, label in BANDS[key]:
            if value <= Decimal(str(upper)) if inclusive else value < Decimal(str(upper)):
                return label
        return {
            "rsi14_15m": "HIGH",
            "spread_bps": "VERY_WIDE",
            "volz_tod_15m": "SURGE",
            "news_count_4h": "MANY",
            "news_newest_age_min": "OLD",
        }.get(key, "POS_STRONG")
    if isinstance(value, Decimal):
        return "ZERO" if value == 0 else ("POSITIVE" if value > 0 else "NEGATIVE")
    return value if isinstance(value, str) else ("EMPTY" if not value else "PRESENT")


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)


class Citation(Strict):
    path: str = Field(max_length=200)
    band: str = Field(max_length=40)


class Signal(Strict):
    state: Literal["SIGNAL", "NO_SIGNAL"]
    score: float = Field(ge=-1, le=1)
    confidence: float = Field(ge=0, le=1)
    horizon: Literal["INTRADAY", "1_3D"]


class Gate(Strict):
    state: Literal["PASS", "CAUTION", "BLOCK"]
    size_multiplier: float = Field(ge=0, le=1)
    reasons: list[str] = Field(max_length=12)


class Item(Strict):
    symbol: str
    evidence: list[Citation] = Field(max_length=6)
    note: str = Field(max_length=160)


class SignalItem(Item):
    signal: Signal


class GateItem(Item):
    gate: Gate


class Header(Strict):
    schema_version: Literal[2]
    run_id: str
    source: Literal["code", "llm", "llm+code"]
    data_confidence: Literal["HIGH", "MED", "LOW"]


class SignalReport(Header):
    role: Literal["TECHNICAL", "NEWS"]
    symbols: list[SignalItem] = Field(max_length=100)


class GateReport(Header):
    role: Literal["LIQUIDITY", "PORTFOLIO"]
    symbols: list[GateItem] = Field(max_length=100)


class TiltReport(Header):
    role: Literal["REGIME"]
    risk_appetite: Literal["RISK_ON", "NEUTRAL", "RISK_OFF"]
    symbols: list[Item] = Field(max_length=100)


def schema_for(role):
    return (SignalReport if role in SIGNALS else GateReport if role in GATES else TiltReport).model_json_schema()


def row_at(content, path):
    group, _, field = path.partition(".")
    if group == "symbols":
        symbol, _, field = field.rpartition(".")
        result = content[group][symbol][field]
    else:
        result = content[group][field]
    if not isinstance(result, dict) or "status" not in result:
        raise KeyError(path)
    return result


def legal_path(role, path):
    group, _, field = path.partition(".")
    extras = {
        "ema_gap_bps_15m",
        "ret_5m",
        "news_count_4h",
        "news_count_48h",
        "news_newest_age_min",
        "news_max_materiality_4h",
        "news_confirmed",
        "news_certainty",
        "news_novelty_max_4h",
        "news_effective_sentiment",
        "volz_tod_15m",
    }
    if group == "symbols":
        symbol, _, name = field.rpartition(".")
        return bool(symbol) and name in ROLE_FIELDS.get(role.lower(), BASE_FIELDS) | extras
    return (
        (group == "portfolio" and field in PORTFOLIO_FIELDS)
        or (group == "market" and field in MARKET_FIELDS)
    )


def item_for(report, symbol):
    return next(x for x in report["symbols"] if x["symbol"] == symbol)


def validate_report(role, raw, pack, floor, cfg, run_id, *, distinct_technical_families=False):
    cls = SignalReport if role in SIGNALS else GateReport if role in GATES else TiltReport
    result = cls.model_validate_json(raw).model_dump()
    if result["run_id"] != run_id or result["role"] != role:
        raise ValueError("wrong run or role")
    symbols = [x["symbol"] for x in result["symbols"]]
    if len(symbols) != len(set(symbols)) or set(symbols) != set(pack.content["symbols"]):
        raise ValueError("missing, unknown or duplicate symbol")
    result.update(source="llm+code", evidence_stripped=0, cited_claims=0, adjustments={})
    for item in result["symbols"]:
        supported: list[dict] = []
        for ref in item["evidence"]:
            result["cited_claims"] += 1
            try:
                if any(existing["path"] == ref["path"] for existing in supported):
                    raise KeyError("duplicate evidence path")
                if not legal_path(role, ref["path"]):
                    raise KeyError(ref["path"])
                scope, _, _ = ref["path"].rpartition(".")
                if scope.startswith("symbols.") and scope != f"symbols.{item['symbol']}":
                    raise KeyError(ref["path"])
                row = row_at(pack.content, ref["path"])
                if row["status"] not in ("OK", "PROVISIONAL") or band_of(ref["path"], row) != ref["band"]:
                    raise KeyError(ref["path"])
                supported.append(dict(**ref, value=row["v"], status=row["status"]))
            except (KeyError, TypeError, ValueError):
                result["evidence_stripped"] += 1
        item["evidence"] = supported
        base = item_for(floor, item["symbol"])
        direction_conflict = False
        if role in SIGNALS:
            before, origin = item["signal"]["score"], base["signal"]["score"]
            bound = cfg.council_v2.llm_adjust_bound
            after = max(origin - bound, min(origin + bound, before)) if bound is not None else before
            after = max(-1, min(1, after))
            direction_conflict = item["signal"]["state"] == "SIGNAL" and before * after < 0
            if direction_conflict:
                after = 0.0
            item["signal"]["score"] = after
            result["adjustments"][item["symbol"]] = dict(
                code_floor_score=origin,
                llm_score=before,
                final_score=after,
                adjustment_delta=after - origin,
                clamped=not same(after, before),
                direction_conflict=direction_conflict,
            )
        family = {
            "ema_gap_bps_15m": "trend", "macd_hist_15m": "trend",
            "rsi14_15m": "momentum", "recent_return_5m": "momentum", "recent_return_10m": "momentum",
            "ret_60m": "momentum", "vwap_dev_session": "price_location",
            "relstr_spy_60m": "relative_strength", "intraday_setup_1m": "setup",
        }
        support_count = len(supported)
        if role == "TECHNICAL" and distinct_technical_families:
            support_count = len({family.get(ref["path"].split(".")[-1]) for ref in supported} - {None})
        if direction_conflict or support_count < cfg.council_v2.min_support[role]:
            if role in SIGNALS:
                item["signal"] = dict(state="NO_SIGNAL", score=0.0, confidence=0.0, horizon="INTRADAY")
            else:
                item.update(deepcopy(base))
                result["source"] = "code"
        elif role in GATES:
            rank = {"PASS": 0, "CAUTION": 1, "BLOCK": 2}
            if rank[item["gate"]["state"]] < rank[base["gate"]["state"]]:
                item["gate"] = deepcopy(base["gate"])
            item["gate"]["size_multiplier"] = min(item["gate"]["size_multiplier"], base["gate"]["size_multiplier"])
    if role == "REGIME":
        result["market_regime"] = floor.get("market_regime")
        result["high_volatility"] = floor.get("high_volatility", False)
        order = {"RISK_OFF": 0, "NEUTRAL": 1, "RISK_ON": 2}
        if order[result["risk_appetite"]] > order[floor["risk_appetite"]]:
            result["risk_appetite"] = floor["risk_appetite"]
    if result["evidence_stripped"]:
        result["data_confidence"] = {"HIGH": "MED", "MED": "LOW", "LOW": "LOW"}[result["data_confidence"]]
    return result


def value(values, name, default=None):
    row = values.get(name, {})
    return row.get("v", default) if row.get("status") in ("OK", "PROVISIONAL") else default


def number(values, name, default=None):
    x = value(values, name)
    try:
        n = float(x)
        return n if math.isfinite(n) else default
    except (ValueError, TypeError):
        return default


def feasibility(content, cfg):
    result = {}
    p, market = content["portfolio"], content["market"]
    for symbol, rows in content["symbols"].items():
        held = number(rows, "position_qty", 0)
        sellable = sellable_shares(rows)
        try:
            capacity = max(Decimal(0), min(entry_caps(rows, p, cfg).values()))
        except ValueError:
            capacity = Decimal(0)
        try:
            limit, _ = order_prices(rows, "buy", cfg)
            can_buy = capacity >= limit
        except ValueError:
            can_buy = False
        phase, close = value(market, "session_phase"), number(market, "minutes_to_close")
        reason = (
            "HALT"
            if value(rows, "halted")
            else (
                "CLOSE_GUARD"
                if phase == "CLOSE_QUIET" or (close is not None and close <= cfg.risk.no_trade_last_minutes)
                else "MARKET_CLOSED"
                if phase == "CLOSED"
                else "OPEN_GUARD"
                if phase == "OPEN_QUIET"
                else ""
            )
        )
        result[symbol] = dict(
            held_qty=str(held),
            sellable_qty=str(sellable),
            can_buy=can_buy,
            can_buy_reasons=[] if can_buy else ["NO_HEADROOM_OR_DATA"],
            can_sell=sellable > 0,
            can_sell_reasons=[] if sellable else ["NO_SELLABLE_INVENTORY"],
            entry_window_open=not reason,
            entry_window_reason=reason,
            max_new_notional_usd=str(capacity),
        )
    return result


def code_floors(pack, cfg, run_id):
    c = pack.content
    reports = {}
    feasible = c.get("feasibility") or feasibility(c, cfg)
    for role in SPECIALISTS:
        report = dict(
            schema_version=2,
            run_id=run_id,
            role=role,
            source="code",
            data_confidence="HIGH",
            symbols=[],
            evidence_stripped=0,
            cited_claims=0,
            adjustments={},
        )
        for symbol, rows in c["symbols"].items():
            item = dict(symbol=symbol, evidence=[], note="deterministic code assessment")
            if role == "TECHNICAL":
                trend, momentum = number(rows, "ema_gap_bps_15m"), number(rows, "rsi14_15m")
                short = number(rows, "recent_return_5m", number(rows, "ret_5m"))
                atr, mid = number(rows, "atr14_15m"), number(rows, "mid_px")

                def clip(x):
                    return max(-1, min(1, x))

                available = all(x is not None for x in (trend, momentum, short, atr, mid)) and atr > 0 and mid > 0
                score = (
                    0.5 * clip(trend / 20) + 0.3 * clip((momentum - 50) / 25) + 0.2 * clip(short / (0.577 * atr / mid))
                    if available
                    else 0
                )
                setup = value(rows, "intraday_setup_1m")
                if available and setup and setup["volume_ratio"] >= 1.2:
                    direction = {"BULLISH_CONFIRMED": 1, "BEARISH_CONFIRMED": -1}.get(setup["confirmation"], 0)
                    score = clip(score + 0.12 * direction)
                    if direction:
                        item["note"] = "Confirmed pattern with volume adjusted the code score by up to 0.12."
                provisional = any(
                    rows.get(n, {}).get("status") == "PROVISIONAL"
                    for n in ("ema_gap_bps_15m", "rsi14_15m", "atr14_15m", "recent_return_5m")
                )
                confidence = (0.5 if provisional else 0.8) if available else 0
                long = number(rows, "ret_60m")
                conflict = bool(short and long and short * long < 0 and abs(short) >= 0.001 and abs(long) >= 0.003)
                if conflict:
                    confidence *= 0.7
                item["signal"] = dict(
                    state="SIGNAL" if available else "NO_SIGNAL", score=score, confidence=confidence, horizon="INTRADAY"
                )
                item["horizon_conflict"] = conflict
                report["data_available"] = report.get("data_available", True) and available
                if not available:
                    report.setdefault("unavailable_symbols", []).append(symbol)
            elif role == "NEWS":
                meta = c.get("meta", {}).get("news", {}).get(symbol, {})
                fresh = meta.get("state") == "FRESH"
                if meta.get("state") in ("UNAVAILABLE", "STALE_COVERAGE"):
                    report["data_confidence"] = "LOW"
                sentiment = number(rows, "news_effective_sentiment", number(rows, "news_sent_ewm_60m", 0))
                certainty = {"CONFIRMED": 1, "HEDGED": 0.6, "RUMOR": 0.4}.get(value(rows, "news_certainty"), 0.6)
                score = max(-1, min(1, sentiment * (1 if value(rows, "news_confirmed") else 0.5) * certainty))
                materiality = number(rows, "news_max_materiality_4h", 0)
                item["signal"] = dict(
                    state="SIGNAL" if fresh else "NO_SIGNAL",
                    score=score if fresh else 0.0,
                    confidence=max(0.2, min(0.9, materiality)) if fresh else 0.0,
                    horizon="INTRADAY",
                )
            elif role in GATES:
                reasons = []
                mult = 1.0
                if role == "LIQUIDITY":
                    spread, age = number(rows, "spread_bps"), rows.get("mid_px", {}).get("age_s")
                    if spread is None or age is None or age > 15 or spread > 15:
                        reasons = ["QUOTE_UNAVAILABLE_OR_WIDE"]
                        mult = 0.0
                    elif spread > 5 or number(rows, "volz_tod_15m", 0) < -1:
                        reasons = ["LIQUIDITY_CAUTION"]
                        mult = 0.5
                else:
                    f = feasible[symbol]
                    if (
                        not f["can_buy"]
                        or not f["entry_window_open"]
                        or number(c["portfolio"], "drawdown_governor", 1) == 0
                    ):
                        reasons = f["can_buy_reasons"] + [f["entry_window_reason"] or "ENTRY_CAPACITY_BLOCK"]
                        mult = 0.0
                    elif (
                        number(c["portfolio"], "day_pnl_pct", 0) <= -cfg.risk.max_daily_loss_pct / 2
                        or number(c["portfolio"], "drawdown_governor", 1) == 0.5
                    ):
                        reasons = ["PORTFOLIO_CAUTION"]
                        mult = 0.5
                    item["facts"] = f
                item["gate"] = dict(
                    state="BLOCK" if mult == 0 else "CAUTION" if mult < 1 else "PASS",
                    size_multiplier=mult,
                    reasons=reasons,
                )
            report["symbols"].append(item)
        if role == "REGIME":
            label = value(c["market"], "regime_label")
            vol = number(c["market"], "spy_vol_regime_ratio")
            report["data_available"] = label is not None and vol is not None
            report["market_regime"] = label
            report["high_volatility"] = label == "HIGH_VOL" or (vol is not None and vol >= 1.3)
            report["risk_appetite"] = (
                "RISK_OFF"
                if label in ("DOWNTREND", "HIGH_VOL")
                else (
                    "RISK_ON"
                    if label == "UPTREND" and number(c["market"], "spy_vol_regime_ratio", 99) < 1.3
                    else "NEUTRAL"
                )
            )
        fields = {
            "TECHNICAL": ("ema_gap_bps_15m", "rsi14_15m", "recent_return_5m", "atr14_15m", "intraday_setup_1m"),
            "NEWS": ("news_count_4h", "news_newest_age_min", "news_effective_sentiment"),
            "REGIME": ("market.regime_label", "market.spy_vol_regime_ratio"),
            "LIQUIDITY": ("spread_bps", "mid_px", "volz_tod_15m"),
            "PORTFOLIO": (
                "portfolio.equity",
                "portfolio.buying_power",
                "portfolio.aggregate_headroom_usd",
                "position_qty",
            ),
        }[role]
        for item in report["symbols"]:
            for name in fields:
                path = name if "." in name else f"symbols.{item['symbol']}.{name}"
                try:
                    row = row_at(c, path)
                    band = band_of(path, row)
                    if band != "UNAVAILABLE":
                        item["evidence"].append(dict(path=path, band=band))
                except KeyError:
                    pass
        reports[role] = report
    return reports


def evaluate(symbol, reports, tilt, cfg, *, held=False, can_short=False, short_held=False, skeptic=None):
    conf = cfg.council_v2
    signals = []
    for role in SIGNALS:
        if role in reports:
            sig = item_for(reports[role], symbol)["signal"]
            effective = sig["score"] * sig["confidence"]
            if sig["state"] == "SIGNAL" and effective != 0:
                signals.append(dict(role=role, eff=effective))
    denominator = sum(conf.signal_weights[x["role"]] for x in signals)
    score = sum(conf.signal_weights[x["role"]] * x["eff"] for x in signals) / denominator if denominator else 0.0
    regime = reports.get("REGIME", {})
    high_volatility = regime.get("high_volatility", False)
    entry_tilt = "RISK_OFF" if high_volatility else tilt
    threshold = conf.enter_threshold + conf.tilt_shift[entry_tilt]
    gates = [dict(role=r, **item_for(reports[r], symbol)["gate"]) for r in GATES if r in reports]
    blockers = ["GATE_BLOCK:" + g["role"] for g in gates if g["state"] == "BLOCK"]
    opposing = any(s["eff"] <= conf.opposing_eff for s in signals)
    support = (
        any(s["eff"] >= conf.strong_eff for s in signals) or sum(s["eff"] >= conf.moderate_eff for s in signals) >= 2
    )
    objections = [x for x in (skeptic or []) if x["symbol"] == symbol]
    if any(x["severity"] == 3 for x in objections):
        blockers.append("SKEPTIC_BLOCK")
    entry = score >= threshold and support and not opposing and not blockers
    trend = regime.get("market_regime")
    short_tilt = "RISK_OFF" if high_volatility or trend == "UPTREND" else "RISK_ON" if trend == "DOWNTREND" else "NEUTRAL"
    short_threshold = conf.enter_threshold + conf.tilt_shift[short_tilt]
    short_support = (
        any(-s["eff"] >= conf.strong_eff for s in signals)
        or sum(-s["eff"] >= conf.moderate_eff for s in signals) >= 2
    )
    short_opposing = any(-s["eff"] <= conf.opposing_eff for s in signals)
    short_ok = (can_short and -score >= short_threshold and short_support
                and not short_opposing and not blockers)
    cover_ok = short_held and score >= conf.exit_threshold
    entry = entry and not short_held
    reasons = list(blockers)
    has_conflict = short_opposing if score < 0 and (can_short or held) else opposing
    if has_conflict:
        reasons.append("CONFLICT")
    bearish = score <= -conf.exit_threshold
    exit_ok = held and bearish
    if exit_ok:
        reasons.append("EXIT_SIGNAL")
    elif short_ok:
        reasons.append("SHORT_ENTRY_SIGNAL")
    elif cover_ok:
        reasons.append("COVER_SIGNAL")
    elif not entry and not reasons:
        if (score >= threshold and not support) or (can_short and -score >= short_threshold and not short_support):
            reasons.append("INSUFFICIENT_SIGNAL_SUPPORT")
        else:
            reasons.append("NO_SIGNAL_ABOVE_THRESHOLD")
    conviction = (
        "HIGH" if score >= conf.conviction_cuts["HIGH"] else "MED" if score >= conf.conviction_cuts["MED"] else "LOW"
    )
    mult = min([g["size_multiplier"] for g in gates] + [1.0])
    skeptical_caution = any(x["severity"] in (1, 2) for x in objections)
    if skeptical_caution:
        mult = min(mult, 0.5)
    return dict(
        symbol=symbol,
        decision="ENTER" if entry else "EXIT" if exit_ok else "SHORT" if short_ok else "COVER" if cover_ok else "NO_ENTRY",
        entry_ok=entry,
        exit_ok=exit_ok,
        short_ok=short_ok,
        cover_ok=cover_ok,
        conviction=conviction if entry else None,
        S=score,
        threshold_eff=threshold,
        exit_threshold=-conf.exit_threshold,
        short_threshold=-short_threshold,
        cover_threshold=conf.exit_threshold,
        tilt=tilt,
        short_tilt=short_tilt,
        high_volatility=high_volatility,
        signals=signals,
        gates=gates,
        size_mult=mult,
        skeptical_caution=skeptical_caution,
        entry_checks={
            "score_threshold": score >= threshold,
            "signal_support": support,
            "no_opposition": not opposing,
            "gates_pass": not blockers,
        },
        short_checks={
            "entry_capacity": can_short,
            "score_threshold": -score >= short_threshold,
            "signal_support": short_support,
            "no_opposition": not short_opposing,
            "gates_pass": not blockers,
        },
        exit_checks={"sellable_inventory": held, "bearish_threshold": bearish},
        blockers=blockers,
        reasons=reasons,
        near_miss="needs one effective signal >= 0.50, or two >= 0.30, and weighted score >= threshold",
    )


def size_with_gate_reduction(pack, decisions, cfg, *, audit=None, allow_simulated_short=False):
    return size_executable_choices(pack, decisions, cfg, audit=audit, allow_simulated_short=allow_simulated_short)


def symbol_stage(cfg, symbol):
    configured = cfg.council_v2.symbol_stage.get(symbol)
    if configured:
        return configured
    if cfg.council.arbiter == "scored" and symbol not in ("SPY", "QQQ"):
        return "DIAGNOSTIC"
    return "LIVE"
