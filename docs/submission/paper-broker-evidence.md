# November 23 Alpaca paper broker evidence

The saved Alpaca exports cover AAPL and INTC. Account, order, and activity identifiers are pseudonymized consistently across the evidence. Times, quantities, prices, and statuses are preserved.

## AAPL

<details>
<summary>Alpaca order history</summary>

```json
[
  {
    "id": "AAPL-ORDER-1-ID",
    "client_order_id": "AAPL-ORDER-1-CLIENT_ORDER_ID",
    "created_at": "2026-11-23T19:39:11.285582Z",
    "updated_at": "2026-11-23T19:39:12.471036Z",
    "submitted_at": "2026-11-23T19:39:11.294556Z",
    "filled_at": "2026-11-23T19:39:12.469266Z",
    "expired_at": null,
    "canceled_at": null,
    "failed_at": null,
    "replaced_at": null,
    "replaced_by": null,
    "replaces": null,
    "asset_id": "b0b6dd9d-8b9b-48a9-ba46-b9d54906e415",
    "symbol": "AAPL",
    "asset_class": "us_equity",
    "notional": null,
    "qty": "1",
    "filled_qty": "1",
    "filled_avg_price": "349.82",
    "order_class": "",
    "order_type": "market",
    "type": "market",
    "side": "sell",
    "position_intent": "sell_to_close",
    "time_in_force": "day",
    "limit_price": null,
    "stop_price": null,
    "status": "filled",
    "extended_hours": false,
    "legs": null,
    "trail_percent": null,
    "trail_price": null,
    "hwm": null,
    "subtag": null,
    "source": "access_key",
    "expires_at": "2026-11-23T21:00:00Z"
  },
  {
    "id": "AAPL-ORDER-2-ID",
    "client_order_id": "AAPL-ORDER-2-CLIENT_ORDER_ID",
    "created_at": "2026-11-23T19:29:14.903745Z",
    "updated_at": "2026-11-23T19:39:07.239983Z",
    "submitted_at": "2026-11-23T19:29:14.910725Z",
    "filled_at": null,
    "expired_at": null,
    "canceled_at": "2026-11-23T19:39:07.238572Z",
    "failed_at": null,
    "replaced_at": null,
    "replaced_by": null,
    "replaces": null,
    "asset_id": "b0b6dd9d-8b9b-48a9-ba46-b9d54906e415",
    "symbol": "AAPL",
    "asset_class": "us_equity",
    "notional": null,
    "qty": "1",
    "filled_qty": "0",
    "filled_avg_price": null,
    "order_class": "",
    "order_type": "stop",
    "type": "stop",
    "side": "sell",
    "position_intent": "sell_to_close",
    "time_in_force": "gtc",
    "limit_price": null,
    "stop_price": "348.28",
    "status": "canceled",
    "extended_hours": false,
    "legs": null,
    "trail_percent": null,
    "trail_price": null,
    "hwm": null,
    "subtag": null,
    "source": "access_key",
    "expires_at": "2027-02-19T21:00:00Z"
  },
  {
    "id": "AAPL-ORDER-3-ID",
    "client_order_id": "AAPL-ORDER-3-CLIENT_ORDER_ID",
    "created_at": "2026-11-23T19:29:10.525571Z",
    "updated_at": "2026-11-23T19:29:12.358619Z",
    "submitted_at": "2026-11-23T19:29:10.529692Z",
    "filled_at": "2026-11-23T19:29:11.483849Z",
    "expired_at": null,
    "canceled_at": "2026-11-23T19:29:12.357062Z",
    "failed_at": null,
    "replaced_at": null,
    "replaced_by": null,
    "replaces": null,
    "asset_id": "b0b6dd9d-8b9b-48a9-ba46-b9d54906e415",
    "symbol": "AAPL",
    "asset_class": "us_equity",
    "notional": null,
    "qty": "2",
    "filled_qty": "1",
    "filled_avg_price": "350.15",
    "order_class": "bracket",
    "order_type": "limit",
    "type": "limit",
    "side": "buy",
    "position_intent": "buy_to_open",
    "time_in_force": "gtc",
    "limit_price": "350.39",
    "stop_price": null,
    "status": "canceled",
    "extended_hours": false,
    "legs": null,
    "trail_percent": null,
    "trail_price": null,
    "hwm": null,
    "group_id": "5875e86b-e759-4a1f-ae7b-d29cb0115e4f",
    "group_role": "entry",
    "subtag": null,
    "source": "access_key",
    "expires_at": "2027-02-19T21:00:00Z"
  },
  {
    "id": "AAPL-ORDER-4-ID",
    "client_order_id": "AAPL-ORDER-4-CLIENT_ORDER_ID",
    "created_at": "2026-11-23T19:29:10.525571Z",
    "updated_at": "2026-11-23T19:29:12.358655Z",
    "submitted_at": "2026-11-23T19:29:10.525571Z",
    "filled_at": null,
    "expired_at": null,
    "canceled_at": "2026-11-23T19:29:12.358655Z",
    "failed_at": null,
    "replaced_at": null,
    "replaced_by": null,
    "replaces": null,
    "asset_id": "b0b6dd9d-8b9b-48a9-ba46-b9d54906e415",
    "symbol": "AAPL",
    "asset_class": "us_equity",
    "notional": null,
    "qty": "2",
    "filled_qty": "0",
    "filled_avg_price": null,
    "order_class": "bracket",
    "order_type": "limit",
    "type": "limit",
    "side": "sell",
    "position_intent": "sell_to_close",
    "time_in_force": "gtc",
    "limit_price": "354.6",
    "stop_price": null,
    "status": "canceled",
    "extended_hours": false,
    "legs": null,
    "trail_percent": null,
    "trail_price": null,
    "hwm": null,
    "group_id": "5875e86b-e759-4a1f-ae7b-d29cb0115e4f",
    "group_role": "take_profit",
    "subtag": null,
    "source": "access_key",
    "expires_at": "2027-02-19T21:00:00Z"
  },
  {
    "id": "AAPL-ORDER-5-ID",
    "client_order_id": "AAPL-ORDER-5-CLIENT_ORDER_ID",
    "created_at": "2026-11-23T19:29:10.525571Z",
    "updated_at": "2026-11-23T19:29:12.358671Z",
    "submitted_at": "2026-11-23T19:29:10.525571Z",
    "filled_at": null,
    "expired_at": null,
    "canceled_at": "2026-11-23T19:29:12.35867Z",
    "failed_at": null,
    "replaced_at": null,
    "replaced_by": null,
    "replaces": null,
    "asset_id": "b0b6dd9d-8b9b-48a9-ba46-b9d54906e415",
    "symbol": "AAPL",
    "asset_class": "us_equity",
    "notional": null,
    "qty": "2",
    "filled_qty": "0",
    "filled_avg_price": null,
    "order_class": "bracket",
    "order_type": "stop",
    "type": "stop",
    "side": "sell",
    "position_intent": "sell_to_close",
    "time_in_force": "gtc",
    "limit_price": null,
    "stop_price": "348.28",
    "status": "canceled",
    "extended_hours": false,
    "legs": null,
    "trail_percent": null,
    "trail_price": null,
    "hwm": null,
    "group_id": "5875e86b-e759-4a1f-ae7b-d29cb0115e4f",
    "group_role": "stop_loss",
    "subtag": null,
    "source": "access_key",
    "expires_at": "2027-02-19T21:00:00Z"
  }
]
```

</details>

<details>
<summary>Alpaca account activity</summary>

```json
[
  {
    "id": "AAPL-ACTIVITY-1",
    "activity_type": "FILL",
    "transaction_time": "2026-11-23T19:29:11.483849Z",
    "type": "partial_fill",
    "price": "350.15",
    "qty": "1",
    "side": "buy",
    "symbol": "AAPL",
    "leaves_qty": "1",
    "order_id": "AAPL-ORDER-3-ID",
    "cum_qty": "1",
    "order_status": "partially_filled"
  },
  {
    "id": "AAPL-ACTIVITY-2",
    "activity_type": "FILL",
    "transaction_time": "2026-11-23T19:39:12.469266Z",
    "type": "fill",
    "price": "349.82",
    "qty": "1",
    "side": "sell",
    "symbol": "AAPL",
    "leaves_qty": "0",
    "order_id": "AAPL-ORDER-1-ID",
    "cum_qty": "1",
    "order_status": "filled"
  }
]
```

</details>

<details>
<summary>Alpaca portfolio equity</summary>

```json
{
  "timestamp": [
    1795461960,
    1795462020,
    1795462080,
    1795462140,
    1795462200,
    1795462260,
    1795462320,
    1795462380,
    1795462440,
    1795462500,
    1795462560,
    1795462620,
    1795462680,
    1795462740,
    1795462800,
    1795462860
  ],
  "equity": [
    99803.39,
    99803.39,
    99803.39,
    99803.39,
    99803.4,
    99803.38,
    99803.51,
    99803.52,
    99803.6,
    99803.6,
    99803.63,
    99803.34,
    99803.05,
    99802.95,
    99803.06,
    99803.06
  ],
  "profit_loss": [
    0.0,
    0.0,
    0.0,
    0.0,
    0.01,
    -0.01,
    0.12,
    0.13,
    0.21,
    0.21,
    0.24,
    -0.05,
    -0.34,
    -0.44,
    -0.33,
    -0.33
  ],
  "profit_loss_pct": [
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0
  ],
  "base_value": 99803.39,
  "base_value_asof": "2026-11-20",
  "timeframe": "1Min"
}
```

</details>

<details>
<summary>SPY IEX bars</summary>

```json
{
  "bars": {
    "SPY": [
      {
        "c": 723.59,
        "h": 723.675,
        "l": 723.495,
        "n": 69,
        "o": 723.575,
        "t": "2026-11-23T19:26:00Z",
        "v": 4029,
        "vw": 723.585684
      },
      {
        "c": 723.57,
        "h": 723.64,
        "l": 723.48,
        "n": 30,
        "o": 723.52,
        "t": "2026-11-23T19:27:00Z",
        "v": 1346,
        "vw": 723.56484
      },
      {
        "c": 723.58,
        "h": 723.7,
        "l": 723.55,
        "n": 66,
        "o": 723.63,
        "t": "2026-11-23T19:28:00Z",
        "v": 2898,
        "vw": 723.649581
      },
      {
        "c": 723.6,
        "h": 723.75,
        "l": 723.55,
        "n": 78,
        "o": 723.65,
        "t": "2026-11-23T19:29:00Z",
        "v": 4076,
        "vw": 723.630287
      },
      {
        "c": 723.55,
        "h": 723.71,
        "l": 723.47,
        "n": 79,
        "o": 723.54,
        "t": "2026-11-23T19:30:00Z",
        "v": 5418,
        "vw": 723.552768
      },
      {
        "c": 723.54,
        "h": 723.76,
        "l": 723.52,
        "n": 68,
        "o": 723.625,
        "t": "2026-11-23T19:31:00Z",
        "v": 3023,
        "vw": 723.650531
      },
      {
        "c": 723.33,
        "h": 723.49,
        "l": 723.15,
        "n": 57,
        "o": 723.49,
        "t": "2026-11-23T19:32:00Z",
        "v": 2682,
        "vw": 723.350988
      },
      {
        "c": 723.4,
        "h": 723.46,
        "l": 723.33,
        "n": 50,
        "o": 723.385,
        "t": "2026-11-23T19:33:00Z",
        "v": 2118,
        "vw": 723.402756
      },
      {
        "c": 723.3,
        "h": 723.51,
        "l": 723.26,
        "n": 46,
        "o": 723.35,
        "t": "2026-11-23T19:34:00Z",
        "v": 2330,
        "vw": 723.366481
      },
      {
        "c": 723.42,
        "h": 723.445,
        "l": 723.31,
        "n": 43,
        "o": 723.39,
        "t": "2026-11-23T19:35:00Z",
        "v": 1727,
        "vw": 723.364306
      },
      {
        "c": 722.57,
        "h": 723.08,
        "l": 722.38,
        "n": 63,
        "o": 723.08,
        "t": "2026-11-23T19:36:00Z",
        "v": 2782,
        "vw": 722.750626
      },
      {
        "c": 722.02,
        "h": 722.45,
        "l": 721.97,
        "n": 33,
        "o": 722.4,
        "t": "2026-11-23T19:37:00Z",
        "v": 1450,
        "vw": 722.056247
      },
      {
        "c": 721.83,
        "h": 722.18,
        "l": 721.8,
        "n": 77,
        "o": 721.92,
        "t": "2026-11-23T19:38:00Z",
        "v": 3223,
        "vw": 722.005191
      },
      {
        "c": 721.87,
        "h": 722.06,
        "l": 721.72,
        "n": 46,
        "o": 721.93,
        "t": "2026-11-23T19:39:00Z",
        "v": 1779,
        "vw": 721.958218
      },
      {
        "c": 721.77,
        "h": 721.94,
        "l": 721.56,
        "n": 65,
        "o": 721.84,
        "t": "2026-11-23T19:40:00Z",
        "v": 2518,
        "vw": 721.786461
      }
    ]
  },
  "next_page_token": null
}
```

</details>

| Time ET | Paper equity (USD) | SPY return |
|---|---:|---:|
| 14:26 | 99803.39 | +0.00000% |
| 14:27 | 99803.39 | +0.00207% |
| 14:28 | 99803.39 | -0.00069% |
| 14:29 | 99803.39 | +0.00069% |
| 14:30 | 99803.40 | +0.00346% |
| 14:31 | 99803.38 | -0.00346% |
| 14:32 | 99803.51 | -0.00484% |
| 14:33 | 99803.52 | -0.03386% |
| 14:34 | 99803.60 | -0.02419% |
| 14:35 | 99803.60 | -0.03801% |
| 14:36 | 99803.63 | -0.02142% |
| 14:37 | 99803.34 | -0.13889% |
| 14:38 | 99803.05 | -0.21491% |
| 14:39 | 99802.95 | -0.24116% |
| 14:40 | 99803.06 | -0.23564% |
| 14:41 | 99803.06 | -0.24946% |

## INTC

<details>
<summary>Alpaca order history</summary>

```json
[
  {
    "id": "INTC-ORDER-1-ID",
    "client_order_id": "INTC-ORDER-1-CLIENT_ORDER_ID",
    "created_at": "2026-11-23T19:57:04.721054Z",
    "updated_at": "2026-11-23T19:57:06.270293Z",
    "submitted_at": "2026-11-23T19:57:04.818153Z",
    "filled_at": "2026-11-23T19:57:06.268735Z",
    "expired_at": null,
    "canceled_at": null,
    "failed_at": null,
    "replaced_at": null,
    "replaced_by": null,
    "replaces": null,
    "asset_id": "0cf42aa3-9816-4f1f-aa84-6482ac9303e9",
    "symbol": "INTC",
    "asset_class": "us_equity",
    "notional": null,
    "qty": "17",
    "filled_qty": "17",
    "filled_avg_price": "58.25",
    "order_class": "",
    "order_type": "market",
    "type": "market",
    "side": "sell",
    "position_intent": "sell_to_close",
    "time_in_force": "day",
    "limit_price": null,
    "stop_price": null,
    "status": "filled",
    "extended_hours": false,
    "legs": null,
    "trail_percent": null,
    "trail_price": null,
    "hwm": null,
    "subtag": null,
    "source": "access_key",
    "expires_at": "2026-11-23T21:00:00Z"
  },
  {
    "id": "INTC-ORDER-2-ID",
    "client_order_id": "INTC-ORDER-2-CLIENT_ORDER_ID",
    "created_at": "2026-11-23T19:50:18.564509Z",
    "updated_at": "2026-11-23T19:57:02.305206Z",
    "submitted_at": "2026-11-23T19:50:18.579337Z",
    "filled_at": null,
    "expired_at": null,
    "canceled_at": "2026-11-23T19:57:02.302856Z",
    "failed_at": null,
    "replaced_at": null,
    "replaced_by": null,
    "replaces": null,
    "asset_id": "0cf42aa3-9816-4f1f-aa84-6482ac9303e9",
    "symbol": "INTC",
    "asset_class": "us_equity",
    "notional": null,
    "qty": "17",
    "filled_qty": "0",
    "filled_avg_price": null,
    "order_class": "",
    "order_type": "stop",
    "type": "stop",
    "side": "sell",
    "position_intent": "sell_to_close",
    "time_in_force": "gtc",
    "limit_price": null,
    "stop_price": "57.74",
    "status": "canceled",
    "extended_hours": false,
    "legs": null,
    "trail_percent": null,
    "trail_price": null,
    "hwm": null,
    "subtag": null,
    "source": "access_key",
    "expires_at": "2027-02-19T21:00:00Z"
  },
  {
    "id": "INTC-ORDER-3-ID",
    "client_order_id": "INTC-ORDER-3-CLIENT_ORDER_ID",
    "created_at": "2026-11-23T19:50:13.84225Z",
    "updated_at": "2026-11-23T19:50:15.626567Z",
    "submitted_at": "2026-11-23T19:50:13.849204Z",
    "filled_at": "2026-11-23T19:50:15.392275Z",
    "expired_at": null,
    "canceled_at": "2026-11-23T19:50:15.624694Z",
    "failed_at": null,
    "replaced_at": null,
    "replaced_by": null,
    "replaces": null,
    "asset_id": "0cf42aa3-9816-4f1f-aa84-6482ac9303e9",
    "symbol": "INTC",
    "asset_class": "us_equity",
    "notional": null,
    "qty": "18",
    "filled_qty": "17",
    "filled_avg_price": "58.02",
    "order_class": "bracket",
    "order_type": "limit",
    "type": "limit",
    "side": "buy",
    "position_intent": "buy_to_open",
    "time_in_force": "gtc",
    "limit_price": "58.09",
    "stop_price": null,
    "status": "canceled",
    "extended_hours": false,
    "legs": null,
    "trail_percent": null,
    "trail_price": null,
    "hwm": null,
    "group_id": "0c329c55-7eec-40c1-b6b6-331ac4a4956c",
    "group_role": "entry",
    "subtag": null,
    "source": "access_key",
    "expires_at": "2027-02-19T21:00:00Z"
  },
  {
    "id": "INTC-ORDER-4-ID",
    "client_order_id": "INTC-ORDER-4-CLIENT_ORDER_ID",
    "created_at": "2026-11-23T19:50:13.84225Z",
    "updated_at": "2026-11-23T19:50:15.626615Z",
    "submitted_at": "2026-11-23T19:50:13.84225Z",
    "filled_at": null,
    "expired_at": null,
    "canceled_at": "2026-11-23T19:50:15.626615Z",
    "failed_at": null,
    "replaced_at": null,
    "replaced_by": null,
    "replaces": null,
    "asset_id": "0cf42aa3-9816-4f1f-aa84-6482ac9303e9",
    "symbol": "INTC",
    "asset_class": "us_equity",
    "notional": null,
    "qty": "18",
    "filled_qty": "0",
    "filled_avg_price": null,
    "order_class": "bracket",
    "order_type": "stop",
    "type": "stop",
    "side": "sell",
    "position_intent": "sell_to_close",
    "time_in_force": "gtc",
    "limit_price": null,
    "stop_price": "57.74",
    "status": "canceled",
    "extended_hours": false,
    "legs": null,
    "trail_percent": null,
    "trail_price": null,
    "hwm": null,
    "group_id": "0c329c55-7eec-40c1-b6b6-331ac4a4956c",
    "group_role": "stop_loss",
    "subtag": null,
    "source": "access_key",
    "expires_at": "2027-02-19T21:00:00Z"
  },
  {
    "id": "INTC-ORDER-5-ID",
    "client_order_id": "INTC-ORDER-5-CLIENT_ORDER_ID",
    "created_at": "2026-11-23T19:50:13.84225Z",
    "updated_at": "2026-11-23T19:50:15.626598Z",
    "submitted_at": "2026-11-23T19:50:13.84225Z",
    "filled_at": null,
    "expired_at": null,
    "canceled_at": "2026-11-23T19:50:15.626598Z",
    "failed_at": null,
    "replaced_at": null,
    "replaced_by": null,
    "replaces": null,
    "asset_id": "0cf42aa3-9816-4f1f-aa84-6482ac9303e9",
    "symbol": "INTC",
    "asset_class": "us_equity",
    "notional": null,
    "qty": "18",
    "filled_qty": "0",
    "filled_avg_price": null,
    "order_class": "bracket",
    "order_type": "limit",
    "type": "limit",
    "side": "sell",
    "position_intent": "sell_to_close",
    "time_in_force": "gtc",
    "limit_price": "58.79",
    "stop_price": null,
    "status": "canceled",
    "extended_hours": false,
    "legs": null,
    "trail_percent": null,
    "trail_price": null,
    "hwm": null,
    "group_id": "0c329c55-7eec-40c1-b6b6-331ac4a4956c",
    "group_role": "take_profit",
    "subtag": null,
    "source": "access_key",
    "expires_at": "2027-02-19T21:00:00Z"
  }
]
```

</details>

<details>
<summary>Alpaca account activity</summary>

```json
[
  {
    "id": "INTC-ACTIVITY-1",
    "activity_type": "FILL",
    "transaction_time": "2026-11-23T19:50:14.638113Z",
    "type": "partial_fill",
    "price": "58.02",
    "qty": "4",
    "side": "buy",
    "symbol": "INTC",
    "leaves_qty": "14",
    "order_id": "INTC-ORDER-3-ID",
    "cum_qty": "4",
    "order_status": "partially_filled"
  },
  {
    "id": "INTC-ACTIVITY-2",
    "activity_type": "FILL",
    "transaction_time": "2026-11-23T19:50:15.392275Z",
    "type": "partial_fill",
    "price": "58.02",
    "qty": "13",
    "side": "buy",
    "symbol": "INTC",
    "leaves_qty": "1",
    "order_id": "INTC-ORDER-3-ID",
    "cum_qty": "17",
    "order_status": "partially_filled"
  },
  {
    "id": "INTC-ACTIVITY-3",
    "activity_type": "FILL",
    "transaction_time": "2026-11-23T19:57:06.268735Z",
    "type": "fill",
    "price": "58.25",
    "qty": "17",
    "side": "sell",
    "symbol": "INTC",
    "leaves_qty": "0",
    "order_id": "INTC-ORDER-1-ID",
    "cum_qty": "17",
    "order_status": "filled"
  }
]
```

</details>

<details>
<summary>Alpaca portfolio equity</summary>

```json
{
  "timestamp": [
    1795463040,
    1795463100,
    1795463160,
    1795463220,
    1795463280,
    1795463340,
    1795463400,
    1795463460,
    1795463520,
    1795463580,
    1795463640,
    1795463700,
    1795463760,
    1795463820,
    1795463880,
    1795463940
  ],
  "equity": [
    99803.06,
    99803.06,
    99803.06,
    99803.06,
    99803.06,
    99803.06,
    99803.06,
    99802.47,
    99803.15,
    99804.25,
    99804.76,
    99804.93,
    99805.44,
    99807.57,
    99806.97,
    99806.97
  ],
  "profit_loss": [
    -0.33,
    -0.33,
    -0.33,
    -0.33,
    -0.33,
    -0.33,
    -0.33,
    -0.92,
    -0.24,
    0.86,
    1.37,
    1.54,
    2.05,
    4.18,
    3.58,
    3.58
  ],
  "profit_loss_pct": [
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0
  ],
  "base_value": 99803.39,
  "base_value_asof": "2026-11-20",
  "timeframe": "1Min"
}
```

</details>

<details>
<summary>SPY IEX bars</summary>

```json
{
  "bars": {
    "SPY": [
      {
        "c": 721.23,
        "h": 721.29,
        "l": 721.015,
        "n": 64,
        "o": 721.16,
        "t": "2026-11-23T19:44:00Z",
        "v": 3285,
        "vw": 721.159873
      },
      {
        "c": 721.18,
        "h": 721.51,
        "l": 721.16,
        "n": 43,
        "o": 721.22,
        "t": "2026-11-23T19:45:00Z",
        "v": 2097,
        "vw": 721.376137
      },
      {
        "c": 721.32,
        "h": 721.32,
        "l": 720.85,
        "n": 58,
        "o": 721.01,
        "t": "2026-11-23T19:46:00Z",
        "v": 2892,
        "vw": 721.088333
      },
      {
        "c": 721.65,
        "h": 721.95,
        "l": 721.29,
        "n": 54,
        "o": 721.29,
        "t": "2026-11-23T19:47:00Z",
        "v": 3584,
        "vw": 721.764834
      },
      {
        "c": 720.87,
        "h": 721.28,
        "l": 720.85,
        "n": 68,
        "o": 721.28,
        "t": "2026-11-23T19:48:00Z",
        "v": 3194,
        "vw": 721.031074
      },
      {
        "c": 721.08,
        "h": 721.08,
        "l": 720.69,
        "n": 51,
        "o": 720.93,
        "t": "2026-11-23T19:49:00Z",
        "v": 2066,
        "vw": 720.858475
      },
      {
        "c": 720.75,
        "h": 721.075,
        "l": 720.625,
        "n": 41,
        "o": 721.075,
        "t": "2026-11-23T19:50:00Z",
        "v": 2496,
        "vw": 720.799053
      },
      {
        "c": 720.895,
        "h": 721.015,
        "l": 720.76,
        "n": 69,
        "o": 720.91,
        "t": "2026-11-23T19:51:00Z",
        "v": 6055,
        "vw": 720.894689
      },
      {
        "c": 721.27,
        "h": 721.44,
        "l": 720.93,
        "n": 90,
        "o": 720.93,
        "t": "2026-11-23T19:52:00Z",
        "v": 6213,
        "vw": 721.148085
      },
      {
        "c": 721.61,
        "h": 721.61,
        "l": 721.305,
        "n": 34,
        "o": 721.33,
        "t": "2026-11-23T19:53:00Z",
        "v": 1904,
        "vw": 721.474694
      },
      {
        "c": 721.875,
        "h": 721.905,
        "l": 721.485,
        "n": 68,
        "o": 721.61,
        "t": "2026-11-23T19:54:00Z",
        "v": 3756,
        "vw": 721.656914
      },
      {
        "c": 721.81,
        "h": 721.99,
        "l": 721.475,
        "n": 107,
        "o": 721.79,
        "t": "2026-11-23T19:55:00Z",
        "v": 5809,
        "vw": 721.819877
      },
      {
        "c": 722.04,
        "h": 722.3,
        "l": 721.855,
        "n": 88,
        "o": 721.855,
        "t": "2026-11-23T19:56:00Z",
        "v": 6692,
        "vw": 722.145289
      },
      {
        "c": 722.31,
        "h": 722.31,
        "l": 721.81,
        "n": 53,
        "o": 722.095,
        "t": "2026-11-23T19:57:00Z",
        "v": 2636,
        "vw": 722.107851
      },
      {
        "c": 722.45,
        "h": 722.49,
        "l": 722.1,
        "n": 59,
        "o": 722.1,
        "t": "2026-11-23T19:58:00Z",
        "v": 2540,
        "vw": 722.283473
      }
    ]
  },
  "next_page_token": null
}
```

</details>

| Time ET | Paper equity (USD) | SPY return |
|---|---:|---:|
| 14:44 | 99803.06 | +0.00000% |
| 14:45 | 99803.06 | +0.00971% |
| 14:46 | 99803.06 | +0.00277% |
| 14:47 | 99803.06 | +0.02219% |
| 14:48 | 99803.06 | +0.06795% |
| 14:49 | 99803.06 | -0.04021% |
| 14:50 | 99803.06 | -0.01109% |
| 14:51 | 99802.47 | -0.05685% |
| 14:52 | 99803.15 | -0.03675% |
| 14:53 | 99804.25 | +0.01525% |
| 14:54 | 99804.76 | +0.06240% |
| 14:55 | 99804.93 | +0.09915% |
| 14:56 | 99805.44 | +0.09013% |
| 14:57 | 99807.57 | +0.12203% |
| 14:58 | 99806.97 | +0.15947% |
| 14:59 | 99806.97 | +0.17888% |
