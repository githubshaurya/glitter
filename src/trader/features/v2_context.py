"""Code-owned news relevance, horizon metadata and feasibility, before council work."""

from datetime import datetime, timedelta

from sqlalchemy import select

from trader.council.v2 import BANDS, feasibility, number
from trader.features.functions import digest
from trader.features.models import SourceHealth
from trader.store.repo import aware


def news_context(articles, as_of, symbol, *, last_ok_age_s, healthy, relevance_floor=0.10):
    rows = []
    for article in articles:
        if symbol not in article.get("symbols", []):
            continue
        published = datetime.fromisoformat(article["published_at"].replace("Z", "+00:00"))
        age = (as_of - published).total_seconds() / 60
        if age < 0:
            continue
        flags = {str(x).upper() for x in article.get("features", {}).get("event_flags", [])}
        half_life = 120 if flags & {"EARNINGS", "GUIDANCE"} else 30 if "MACRO" in flags else 60
        weight = float(article.get("features", {}).get("source_weight", 1)) * 0.5 ** (age / half_life)
        rows.append(dict(**article, age_min=age, effective_weight=weight))
    selected = sorted(
        [x for x in rows if x["effective_weight"] >= relevance_floor],
        key=lambda x: (-x["effective_weight"], x["published_at"], str(x.get("article_id", ""))),
    )
    state = (
        "UNAVAILABLE"
        if not healthy
        else "STALE_COVERAGE"
        if last_ok_age_s is None or last_ok_age_s > 300
        else ("FRESH" if selected else "QUIET")
    )
    meta = dict(
        retrieved=len(rows),
        in_window=sum(x["age_min"] <= 240 for x in rows),
        window_min=240,
        newest_age_min=min((x["age_min"] for x in rows), default=None),
        poller_last_ok_age_s=last_ok_age_s,
        state=state,
        selected=len(selected),
        effective_weight=sum(x["effective_weight"] for x in selected),
        policy="48h retained; per-article decay and minimum relevance; 4h count is descriptive",
    )
    return meta, selected if state == "FRESH" else []


def enrich_content(fs, content, cfg):
    as_of = datetime.fromisoformat(content["as_of"].replace("Z", "+00:00"))
    articles = fs.news_bundle(as_of, list(content["symbols"]), hours=48)
    with fs.store.session() as session:
        last = session.scalar(
            select(SourceHealth)
            .where(SourceHealth.source == "news", SourceHealth.at <= as_of)
            .order_by(SourceHealth.at.desc())
            .limit(1)
        )
        last_ok = session.scalar(
            select(SourceHealth)
            .where(SourceHealth.source == "news", SourceHealth.at <= as_of, SourceHealth.success == 1)
            .order_by(SourceHealth.at.desc())
            .limit(1)
        )
    age = (as_of - aware(last_ok.at)).total_seconds() if last_ok else None
    content.setdefault("meta", {})["news"] = {}
    selected = {}
    for symbol, values in content["symbols"].items():
        meta, relevant = news_context(
            articles,
            as_of,
            symbol,
            last_ok_age_s=age,
            healthy=bool(last and last.success),
            relevance_floor=cfg.council_v2.news_relevance_floor,
        )
        content["meta"]["news"][symbol] = meta
        selected[symbol] = relevant
        weighted = sum(a["effective_weight"] * a.get("features", {}).get("sentiment", 0) for a in relevant)
        effective = weighted / max(1, sum(a["effective_weight"] for a in relevant))
        values["news_effective_sentiment"] = dict(
            v=effective,
            status="OK" if meta["state"] == "FRESH" else "MISSING",
            age_s=0,
            version="news-decay-v2",
            quality=dict(source="decayed stored article metadata", selected=len(relevant)),
        )
        for name, value in dict(
            news_count_48h=meta["retrieved"],
            news_count_4h=meta["in_window"],
            news_newest_age_min=meta["newest_age_min"],
        ).items():
            values[name] = dict(
                v=value,
                status="OK" if value is not None else "MISSING",
                age_s=age,
                version="news-context-v2",
                quality=dict(source="stored articles", as_of=content["as_of"]),
            )
    content["news_context_blob_hash"] = fs.blob(selected)
    content["feasibility"] = feasibility(content, cfg)
    content["bands_hash"] = digest(BANDS)
    content["horizons"] = {}
    for symbol, values in content["symbols"].items():
        content["horizons"][symbol] = {}
        for horizon, name in (
            ("5m", "recent_return_5m"),
            ("10m", "recent_return_10m"),
            ("15m", "ret_15m"),
            ("60m", "ret_60m"),
        ):
            row = values.get(name, {})
            age = row.get("age_s")
            end = row.get("quality", {}).get("window_end")
            if not end and age is not None:
                end = (as_of - timedelta(seconds=age)).isoformat()
            content["horizons"][symbol][horizon] = dict(
                last_bar_end=end, age_s=age, status=row.get("status", "MISSING")
            )
        short, long = number(values, "recent_return_5m"), number(values, "ret_60m")
        content["horizons"][symbol]["horizon_conflict"] = bool(
            short and long and short * long < 0 and abs(short) >= 0.001 and abs(long) >= 0.003
        )
    return content
