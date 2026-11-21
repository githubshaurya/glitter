"""Fetch the dated corporate actions needed to replay unadjusted overnight holdings."""

from datetime import date, timedelta


def fetch_actions(client, symbols, sessions):
    first, last = (date.fromisoformat(day) for day in (min(sessions), max(sessions)))
    # Alpaca indexes the search by processing date. Apply actions by ex-date or effective date.
    params = dict(symbols=",".join(symbols), limit=1000, data_quality="all",
                  start=str(first - timedelta(days=31)), end=str(last + timedelta(days=31)))
    seen = set()
    actions = []
    while True:
        response = client.get("https://data.alpaca.markets/v1/corporate-actions", params=params)
        response.raise_for_status()
        body = response.json()
        groups = body.get("corporate_actions")
        if not isinstance(groups, dict):
            raise ValueError("corporate action response is missing its action groups")
        for category, rows in groups.items():
            for raw in rows:
                effective = raw.get("ex_date") or raw.get("effective_date")
                symbol = raw.get("old_symbol") or raw.get("symbol")
                if not effective or not symbol or not raw.get("id"):
                    raise ValueError("corporate action is missing its effective date or instrument")
                if not first <= date.fromisoformat(effective) <= last:
                    continue
                kind = category
                if category in ("forward_splits", "reverse_splits") and raw.get("new_symbol", symbol) in ("", symbol):
                    kind = "split"
                elif category == "cash_dividends" and raw.get("currency") in (None, "", "USD"):
                    kind = "cash_dividend"
                actions.append({
                    **{key: raw[key] for key in ("id", "old_rate", "new_rate", "rate", "payable_date") if key in raw},
                    "date": effective, "symbol": symbol, "type": kind,
                })
        token = body.get("next_page_token")
        if not token:
            return sorted(actions, key=lambda action: (action["date"], action["id"]))
        if token in seen:
            raise ValueError("corporate action pagination repeated a token")
        seen.add(token)
        params["page_token"] = token
