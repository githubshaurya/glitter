"""Optional deterministic news metadata. Only the news councillor reads article text."""

import html
import re
import unicodedata
from datetime import datetime

from trader.features.functions import digest

POSITIVE = {"raises", "record", "beat", "beats", "surge", "upgrade", "growth", "profit"}
NEGATIVE = {"miss", "misses", "downgrade", "weak", "lawsuit", "fraud", "loss", "cuts"}


def tokens(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def cluster(text):
    return digest(tokens(text))


def normalize(text, limit):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]*>", " ", unicodedata.normalize("NFKC", text)))).strip()[
        :limit
    ]


def extract(text):
    words = tokens(text)
    score = count = 0.0
    for i, word in enumerate(words):
        polarity = 1 if word in POSITIVE else (-1 if word in NEGATIVE else 0)
        if polarity:
            if set(words[max(0, i - 3) : i]) & {"not", "no", "never", "without", "fails", "failed", "fail", "cannot"}:
                polarity *= -1
            weight = (
                0.5
                if set(words[max(0, i - 5) : i])
                & {"may", "might", "could", "reportedly", "rumor", "rumour", "considering", "exploring", "potentially"}
                else 1.0
            )
            score += polarity * weight
            count += weight
    sentiment = score / (count + 2)
    flags = sorted(set(words) & {"guidance", "earnings", "lawsuit", "fraud", "takeover", "merger", "bankruptcy"})
    return dict(sentiment=sentiment, materiality=min(1, len(flags) * 0.3), event_flags=flags)


def news_metrics(articles, as_of, prices):
    clusters: dict[str, dict] = {}
    for article in articles:
        clusters.setdefault(article["cluster_id"], article)
    items = list(clusters.values())

    def age(a):
        return (as_of - datetime.fromisoformat(a["published_at"])).total_seconds() / 60

    recent = [a for a in items if age(a) <= 60]

    def sentiment(rows):
        return max(-1, min(1, sum(a["features"]["sentiment"] * 0.5 ** (age(a) / 60) for a in rows)))

    sent = sentiment(recent)
    ret = prices.get("ret_15m")
    vz = prices.get("volz_tod_15m")
    return dict(
        news_count_1h=len(recent),
        news_count_4h=len(items),
        news_sent_ewm_60m=sent,
        news_sent_ewm_240m=sentiment(items),
        news_max_materiality_4h=max((a["features"]["materiality"] for a in items), default=0),
        news_event_flags_4h=sorted({flag for a in items for flag in a["features"]["event_flags"]}),
        news_age_min_latest=min((age(a) for a in items), default=None),
        news_source_div_4h=len({a["source"] for a in articles}),
        news_novelty_max_4h=bool(items),
        news_confirmed=bool(sent and ret and sent * ret > 0 and vz is not None and vz >= 1.5),
    )


class NewsIsolationGuard:
    def __init__(self, features):
        self.features = features
        self._frozen = None

    def _phrases(self, as_of):
        phrases = set()
        for article in self.features.news_bundle(as_of, [], hours=48):
            words = tokens(article["headline"] + " " + article["summary"])
            phrases.update(" ".join(words[i : i + 8]) for i in range(max(0, len(words) - 7)))
        return phrases

    def prepare(self, as_of):
        self._frozen = (as_of, self._phrases(as_of))

    def check(self, role, text, as_of):
        if role == "news":
            return
        phrases = self._frozen[1] if self._frozen is not None and self._frozen[0] == as_of else self._phrases(as_of)
        if not phrases:
            return
        haystack = " ".join(tokens(text))
        if any(phrase in haystack for phrase in phrases):
            raise ValueError("raw news text is isolated to the news council role")
