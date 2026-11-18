"""Optional deterministic news metadata. Only the news councillor reads article text."""

import html
import re
import unicodedata

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


class NewsIsolationGuard:
    def __init__(self, features):
        self.features = features

    def check(self, role, text, as_of):
        if role == "news":
            return
        haystack = " ".join(tokens(text))
        for article in self.features.news_bundle(as_of, [], hours=48):
            words = tokens(article["headline"] + " " + article["summary"])
            for i in range(max(0, len(words) - 7)):
                if " ".join(words[i : i + 8]) in haystack:
                    raise ValueError("raw news text is isolated to the news council role")
