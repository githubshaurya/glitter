# November 23 paper decision journal

These 15 app-generated records include the recorded inputs, role responses, guard checks, and linked entry orders. The managed exits appear in [broker activity](paper-broker-evidence.md).

## AAPL

### 14:26:01 ET · BLOCKED_GUARD

<details>
<summary>Recorded decision evidence</summary>

```json
{
  "decision_id": "8b08ac8d-8cbf-57a2-8ef8-efe07c6114ae",
  "inputs": {},
  "feature_evidence": {},
  "council_mode": null,
  "chair": null,
  "skeptic_audit": null,
  "role_outputs": [],
  "reason_codes": null,
  "notes": [
    "SCHEDULER_SKIP:snapshot_deadline"
  ],
  "error": "",
  "proposals_and_risk": []
}
```

</details>

### 14:26:16 ET · INCOMPLETE_PROVIDER

<details>
<summary>Recorded decision evidence</summary>

```json
{
  "decision_id": "74d23f10-3119-5e34-9ebe-4ffc946dfc2f",
  "inputs": {
    "as_of": "2026-11-23T19:26:06.503496Z",
    "regime": {
      "label": "uptrend"
    },
    "account": {
      "cash": 99803.39,
      "equity": 99803.39,
      "status": "ACTIVE",
      "account_id": "PAPER_ACCOUNT",
      "last_equity": 99803.39,
      "buying_power": 399213.56
    },
    "positions": [],
    "symbols": {
      "AAPL": {
        "mid": 350.11,
        "rsi14": null,
        "ret_1d": -0.0163,
        "ret_5d": null,
        "ret_20d": null,
        "atr14_pct": null,
        "price_vs_sma20": null,
        "trend_sma20_vs_sma50": null
      }
    }
  },
  "feature_evidence": {
    "account_ref": "PAPER_ACCOUNT",
    "as_of": "2026-11-23T19:26:06.503496+00:00",
    "availability": {
      "account": "fresh",
      "bars": "fresh",
      "calendar": "fresh",
      "news": "fresh",
      "ok_fraction_core_features": 1.0,
      "quotes": "fresh"
    },
    "bands_hash": "810517c6e124c7ebc23ca0ebce7ef7ba7cc66b30bc21cacc66c1a221174255d4",
    "feasibility": {
      "AAPL": {
        "can_buy": true,
        "can_buy_reasons": [],
        "can_sell": false,
        "can_sell_reasons": [
          "NO_SELLABLE_INVENTORY"
        ],
        "entry_window_open": true,
        "entry_window_reason": "",
        "held_qty": "0.0",
        "max_new_notional_usd": "2000.0",
        "sellable_qty": "0"
      }
    },
    "feature_slot": {
      "candles": {
        "AAPL|2026-11-23T19:11:00+00:00": "556e6ecd6e7954c8069c05925cec551b37966bdf17e76ba2a3277679bb7d0cf9",
        "AAPL|2026-11-23T19:12:00+00:00": "6cf77b23c73970e738306574ee418d5b11d7ad5d34d08539bb928b653cccb385",
        "AAPL|2026-11-23T19:13:00+00:00": "0e9a14fe740d7261310d963893297e28a03071451489fa33aded1b1a58acee67",
        "AAPL|2026-11-23T19:14:00+00:00": "d5bda39af69dcc53d4310b57aff3092db8a68054546c86a6b2df103d67ada5be",
        "AAPL|2026-11-23T19:15:00+00:00": "b0e6a6e9b9e4287c960f6ede77ad8f355970b7e8745dbe17c9339d2e3f12a605",
        "AAPL|2026-11-23T19:16:00+00:00": "69e7bfc090cee194af19c0acc6e8da6b7cf4c08443c52b952de98b8961d2ec67",
        "AAPL|2026-11-23T19:17:00+00:00": "c0a6e9630fa9f0d5027648d10559bb0be8e8caa0857d4fd8f17b11d4e3a85102",
        "AAPL|2026-11-23T19:18:00+00:00": "e862cb638fbc15b1a3f7b32db1c9e6d689acd1cd350079657d14e77d9e2c6479",
        "AAPL|2026-11-23T19:19:00+00:00": "e1937e8da6f995fc153f7e5e2ced98a01f960310d2ec214a17e4fb29a93c4146",
        "AAPL|2026-11-23T19:20:00+00:00": "70196363dae726bc8d352fd0e8cbb4b115e48fba11b5ee33c3817ea612c07c0f",
        "AAPL|2026-11-23T19:21:00+00:00": "6c6e08fc67af597579978fa03f3aaab5c3543c74e2011a7c2bce5c6d84460f57",
        "AAPL|2026-11-23T19:22:00+00:00": "2954cabc7ce7bf14ae0893aaac62bfaa70486fa0a68f63da27e0ee312728069a",
        "AAPL|2026-11-23T19:23:00+00:00": "2747e99b2df2570cd8f56be82b287c8ee7e009053a8933e9f3a90cd4d730228a",
        "AAPL|2026-11-23T19:24:00+00:00": "e1968a3f7d654002dbeeffb581d28f178a4778e7ef171a3abc48397e1eca10c1",
        "AAPL|2026-11-23T19:25:00+00:00": "f253416079d72d4e362e19307b75c172b7d2edb6ec453969e082d947eb75de1b",
        "SPY|2026-11-23T19:11:00+00:00": "37c78aa527662237d93f93482b298ada17b38e577a17d135412f34f90de0c579",
        "SPY|2026-11-23T19:12:00+00:00": "bc09429308608b3ad795f14ea22a7b90d385a63386c6261b6f6b43a105a8c6e6",
        "SPY|2026-11-23T19:13:00+00:00": "2e0e8e4afe5f0552e559f4b57ab6f3a4af7aeed1c29df9bc0f8af4d993a0ec57",
        "SPY|2026-11-23T19:14:00+00:00": "1a003d29f3062e0e284c02aef050fc33aa9519155986beb8ffeabb18ba63d85e",
        "SPY|2026-11-23T19:15:00+00:00": "80f9ec707984fc74f8cb6dcebd3d845190206f212a6a7f5bbea8e7f0dfe5b85a",
        "SPY|2026-11-23T19:16:00+00:00": "bef27fecf6495d402ef4cf61ab22855605b7bf35ec2ee88c5fa240ececdeb144",
        "SPY|2026-11-23T19:17:00+00:00": "9267d9ec8514091597a775a9f11df8e6ba85ef1a765d8d7c6e0695a9d17e9d04",
        "SPY|2026-11-23T19:18:00+00:00": "9927bc665ca20d7006e3e28873737e2afb2679463ac195ed3f79e8551e2cdac5",
        "SPY|2026-11-23T19:19:00+00:00": "a3f91e79e75f72019e37a2793b54c01ee93403d8d9eafbd7f1eb0c5012b9b9c4",
        "SPY|2026-11-23T19:20:00+00:00": "e1ddcdb981d5c72dfaca25e1aaa8c1c27aef392260bc51ce1653cfd94d114f8f",
        "SPY|2026-11-23T19:21:00+00:00": "7a81b6670301657ad6b9cb0542ae646ff5785b4dbcb61c6b01fba0f60649ba1a",
        "SPY|2026-11-23T19:22:00+00:00": "39edefebca8c72b2135f978774a03b1d9775e0b17ef5fce054875b0dd7243c94",
        "SPY|2026-11-23T19:23:00+00:00": "def528246d2c8ce3e04085fb10ac15cd8741ba99e3ec0331c205f3d95712dca6",
        "SPY|2026-11-23T19:24:00+00:00": "e0825fbb3c82960924bc0a4fa93ab9a29cea452a13a515bbc433eb3e210b164a",
        "SPY|2026-11-23T19:25:00+00:00": "b6bef0076894b860d0d4faaa2427e9f8628a5c940154cdafae8278de8b4adb91"
      },
      "close": "2026-11-23T19:26:00+00:00",
      "feed": "iex",
      "indicator_close": "2026-11-23T19:15:00+00:00",
      "indicator_input_hashes": {
        "AAPL": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
        "SPY": "647346c3307bab3f0ab75d294e9bf46773d6d42fa0676aa83ae2ca9d97b2b1eb"
      },
      "provisional": true,
      "records": {
        "market:market:breadth_above_ema21": "815832b01dd92f1e4451c79cf7955b56fb9737d65935bcfd1d3f33947ba7647c",
        "market:market:regime_label": "84f9e0050c68ef26c8fac251be3d1e9715d2043efbb27dc10dd36f804aed1906",
        "market:market:spy_ema_gap_bps_15m": "e1b77372b1441b383700bc1a58f75ce0bf7cd28628675e926f5fce53abbe5d18",
        "market:market:spy_ret_60m": "b142676e3715503e9b86ac07722015d70a5dc110e33a78219756deccfc3a0bd0",
        "market:market:spy_vol_regime_ratio": "cbd55c998b8b25e8c0e7dea1d5b05afaa28216f5d953e46156855fb3743c4456",
        "symbol:AAPL:adv_usd_20d": "e262af1fe6a7389e05b96a9a75b061c36d19abe6182590f4ef666a3c4147c5a3",
        "symbol:AAPL:atr14_15m": "4aa601dee2846211e120ee408a21949bef6a84cbeaeda8c8217242fa79357ada",
        "symbol:AAPL:atr14_1d": "9c0633de46b036a4fe93734a2e5dce61b7eff6bf36ec86c1bf294d9eeef95f85",
        "symbol:AAPL:atr14_pct": "1437ca280d0973889472dab3c5cb1b0006ef5ee631652a04bebaa9de603743bd",
        "symbol:AAPL:dist_hi_atr": "40c47665594fa60ce1cbfbc72e94312c3b9dd47dfeb81e9e75d0ccb511a4bc20",
        "symbol:AAPL:dist_lo_atr": "a452592301e3cc53b447aa5817657d9e1ff8778d7d3012811d1e98f1048a5566",
        "symbol:AAPL:ema21_15m": "a4fce26cfa0190c94a7c7a20a720ebe23cabd0d7ebbcf6c266507d885b6c2172",
        "symbol:AAPL:ema9_15m": "0ad14ee0eb256fe1fe75965b26cc534f1723fca1dde7436232c23a087c645c3e",
        "symbol:AAPL:ema_gap_bps_15m": "e727bcc5189a91061e7df830a4b1a4c71755006275cd2c0a493816f0a95e827b",
        "symbol:AAPL:gap_open_pct": "fc5c7eeea7261785fc595b201a91df75e735719dbe6722604c7617e8524e7bc1",
        "symbol:AAPL:intraday_ret_1h": "bce1649c3f11808a59de7a9536a3a82e7ffdc25c2c36ac39b247c733fff4bd35",
        "symbol:AAPL:intraday_setup_1m": "2a1d5070c0749532d5028a15d556b5bcc257c450c4bdc6b38e90d8a8df2c636e",
        "symbol:AAPL:last_close": "f064e1589fb929d983b820bbfcd86fd0141cb1044925ea55db4eb69a6c6b5ae1",
        "symbol:AAPL:macd_hist_15m": "5bdd527f747bb67db78b657003212927e07ba8624389f5381095f9a3f7a8d02f",
        "symbol:AAPL:price_vs_sma20": "a96d3080f2e95a5cc3b047ec495961d46cd4b318722c7eae4d719bfa2cc0f6e4",
        "symbol:AAPL:recent_price_10m": "d748a3fc334d9d2e282ab9ab747f72e6f1ca23a7fc1fc0685b76d0ec57a7d431",
        "symbol:AAPL:recent_range_bps_10m": "781a3dad6d6995a86b82000cc85514ec6311f7e56e902405f681df0db4b7c0fd",
        "symbol:AAPL:recent_range_bps_5m": "ca6b0456cb0136fd521eb59ba8813115bfc59fcad6554e1632389e2a0d270302",
        "symbol:AAPL:recent_return_10m": "7cd1c2efdac2af548e6649c9126ec09fb452f737549d0fae5c0823a204853879",
        "symbol:AAPL:recent_return_5m": "c88907dbcee04f1903a848cb67a1be97a01ceb10b7439b33c43b6ff3124f270b",
        "symbol:AAPL:recent_volume_10m": "83c897892781fee40aecbcc6599abda85da2ca0bcdf929900b0d844736e43a2f",
        "symbol:AAPL:recent_volume_5m": "74dec8cdf92185be5e859debae638a26d47b3e45d1b4c6018d78e7255d491cd0",
        "symbol:AAPL:relstr_spy_60m": "9d66f515215390e411a6a78a452c1b314227d9e85443fdb5af30785039cce718",
        "symbol:AAPL:ret_15m": "e182c98f3d33193f3f9dc126a7fa258eba8951450278e91a3cb669dc84fd90a3",
        "symbol:AAPL:ret_1d": "acd4850c7f353cd7d276491b7c7d3402308f47b10f57d00ddfcff5304f668541",
        "symbol:AAPL:ret_20d": "c1fd6c69e5212d8143db80ab0b65f04c3952518636216a6f65599b0cf9aa5d52",
        "symbol:AAPL:ret_5d": "e279e1e5300466ccb81556a606d3565ef56efdfaa8086d105f074c583b7f1520",
        "symbol:AAPL:ret_5m": "6c8a5e618e2f12c793e51448bf22311686552ee29e8f4111fddd0e3712371e86",
        "symbol:AAPL:ret_60m": "fccca55c136943a390236c8bbac9c5a9d08d89d1bd27b4a7784773d9482e3728",
        "symbol:AAPL:rsi14": "017f8f44fae740e064f7cf662b6575f31515d3864f3470dc54f27aff186f4183",
        "symbol:AAPL:rsi14_15m": "4bcd3b3bc68ef2a3b24588f819b282374f20d221da66c12182e92b5be0b02bf7",
        "symbol:AAPL:rvol_60m": "c2f6317bf7ceb3c37708893f940596eec2f123b7681d383724f44ec9ec6e160b",
        "symbol:AAPL:sma20": "3e4d68b668f1fb60d01391d426d6383d59c5f1489b2c60d8b9677923330ea1e8",
        "symbol:AAPL:sma50": "1ae3948821d316103e37237b485a2f4802a168c7ba7718bcaa1f5cecba683bb4",
        "symbol:AAPL:trend_sma20_vs_sma50": "70f14cdb1db36bf9d9d5e86c7b54697ceba3042951e93e45270a4f006f4c91d8",
        "symbol:AAPL:vol_regime_ratio": "770c771a2056ff265bb460bc175636cb969915dc31e4b3ed4e54d78923f8c52f",
        "symbol:AAPL:volume_z20": "68a11cf3df037bf35a94e13761dc1df96383de19536c6a0d960a52c5365f1e28",
        "symbol:AAPL:volz_tod_15m": "530fa07e56964d38a2104f4a1a003a9c21fe607e74364348f18f0dfb47005705",
        "symbol:AAPL:vwap_dev_session": "828359dd0c1e5c52aa177d18405776f4d344dd270faf4ae4d9297f27cf5f3839",
        "symbol:SPY:adv_usd_20d": "7773f3a908eaf7c0e76c09e0281ebbcb8379cc49400a15772c1830a3b2c2f223",
        "symbol:SPY:atr14_15m": "fc718bba22a5db9dae206edea8233cf88df09c2e3062133470a7fe10f13267e2",
        "symbol:SPY:atr14_1d": "aaeea7993a9d2b21fb57bccbb0a7e2bae3ebb9bc634c0e9b485665df8a582439",
        "symbol:SPY:atr14_pct": "684fcce9d38b849dfc48ed4adf427634c6537f0b2d2dac4b1ac576ea747f9ea6",
        "symbol:SPY:dist_hi_atr": "d228040b17061123de8062f9c01009ed9b9beb6f53b1be7d6b37fed992f7089f",
        "symbol:SPY:dist_lo_atr": "0e4f21b82cc92901774a0122cd40b63f68b070ffa628177f120e09f755b4b83a",
        "symbol:SPY:ema21_15m": "d517509d58dbc26956d75d98347e4757713275e63455fdcc3c4422d256746a81",
        "symbol:SPY:ema9_15m": "097b3848e725e0d802d5441768fbf4db8207cbc178c1f391212f3cf9f984afeb",
        "symbol:SPY:ema_gap_bps_15m": "88de61b58000f6c109f37ccb1278278f5d8761b975c2735eb8c0fceb4c8789cc",
        "symbol:SPY:gap_open_pct": "7b8b09f491c0f145686f016617f1e339ec2c992d2d7f4b990a6f22f849fb269b",
        "symbol:SPY:intraday_ret_1h": "e04939fd11622d8ee6f45b21cbd60aaf479b74745d0331a0d031b34eb916d9e1",
        "symbol:SPY:intraday_setup_1m": "2bbaf547ce3bd521b1049d31b39596c7e9d933ce29b971257dc4b30f413355e7",
        "symbol:SPY:last_close": "7c75e5b2d0cbfa6053329d40230beafe8c50de8de09b8650fbc56c1f24fef8dd",
        "symbol:SPY:macd_hist_15m": "700faaf2b22ddb3d7a761119e621afb779197ee9e20002bf78ec397dc82b0426",
        "symbol:SPY:price_vs_sma20": "b3b5e555c37b8c77664c4514095e6ed44684e1cca73f30c87e244ef5047030fc",
        "symbol:SPY:recent_price_10m": "c3258e0c047a4dbf387417d73852c6e0121c54bcb766b7226ccbd24cffaae0c3",
        "symbol:SPY:recent_range_bps_10m": "11034778552483aae91af61979f75f60aa05af20e3b8d39d558e48374507542d",
        "symbol:SPY:recent_range_bps_5m": "ad9897d69ca0ce8cdf9f1d90b210a611780bb20c1e6fb101e4a22b3d5cefa2f1",
        "symbol:SPY:recent_return_10m": "6a06cacd11a4849d2beee3636cc03cddefebfb0f0b47885b3d2ce64c18605f0b",
        "symbol:SPY:recent_return_5m": "b248bb18576c206d1a94b1b0a1fcb5245e2011c8ccc2b240021e84ee699867b6",
        "symbol:SPY:recent_volume_10m": "7db90198c00f9a9a81ffd23ee60ad70a7920bf31eb076ded823b0b9fd48e83e1",
        "symbol:SPY:recent_volume_5m": "e5a4448d6f4cf19a4cd866332ca00ad65d102faf25307be3375777ad034c9e99",
        "symbol:SPY:relstr_spy_60m": "f8e8a2c70f6861986994098551914f6ec7f583a6212d91b31d608d2906cc194a",
        "symbol:SPY:ret_15m": "8907d87eca3e95a025640a82f0ad531260eee21b56a39c058df0570b53e73878",
        "symbol:SPY:ret_1d": "ddc0a11b63cc350e3081db1903dee6252ddb61770d13b16e856291026f52a3f3",
        "symbol:SPY:ret_20d": "ed1093e0aa5d6f66c95107ca1d6e0dc684f91a2b174538f28adce162fbc2a1c1",
        "symbol:SPY:ret_5d": "2298165b21cd162151213ae636f77a63a657bd096db984033682489995a3b1f5",
        "symbol:SPY:ret_5m": "aa0976e20813e96a6aaf19cc6ee5be66214439979798146f1e2eabd265c8ae1b",
        "symbol:SPY:ret_60m": "e54c2eacbf5aa07fc1fbb222ec6b371f6f6b79403ae4a1f2edfffc329381d7b8",
        "symbol:SPY:rsi14": "0896ff9e6527016820c4f3bacca566bf1825f6f67c30f9e930a11faa591958f6",
        "symbol:SPY:rsi14_15m": "f74fdb6b8a4dfd4479e87521b52a8e59d763710203d578d8f94a9675c6c9b551",
        "symbol:SPY:rvol_60m": "92e8d3c55c6ac2fd5a18e1ce838b2310d96a1dda558a5943a3d3e09292561aae",
        "symbol:SPY:sma20": "d0283363840868af6910e903d8b6ce0fa7a2a5f15f1fe6688eee56a4e374e136",
        "symbol:SPY:sma50": "f0b368651bafa612c1bc158db1c24203caf7f9a36cde9c70a55ee93a918503d6",
        "symbol:SPY:trend_sma20_vs_sma50": "081b68b933591d41fda8068af744f2f85c5c3ab9eea6461455fa6828810c399c",
        "symbol:SPY:vol_regime_ratio": "160f520f20a410aa3c07be675abe84c0a69571dfc3523a38dc4da0ba48dc7912",
        "symbol:SPY:volume_z20": "b50666ce3e64dd1b2b048c991b636383b066dc0bdc8adda4888131d53fc369b6",
        "symbol:SPY:volz_tod_15m": "461ed44d456e55c2fcef586cde4f795fb112387dee57647074b82b07fa685f52",
        "symbol:SPY:vwap_dev_session": "7158355d8f440bdc2f09f9181eb2beb377fe7c7eb99abba4b273c113b0fe279d"
      },
      "symbols": [
        "AAPL",
        "SPY"
      ]
    },
    "horizons": {
      "AAPL": {
        "10m": {
          "age_s": 6.503496,
          "last_bar_end": "2026-11-23T19:26:00+00:00",
          "status": "OK"
        },
        "15m": {
          "age_s": 666.503496,
          "last_bar_end": "2026-11-23T19:15:00+00:00",
          "status": "OK"
        },
        "5m": {
          "age_s": 6.503496,
          "last_bar_end": "2026-11-23T19:26:00+00:00",
          "status": "OK"
        },
        "60m": {
          "age_s": 666.503496,
          "last_bar_end": "2026-11-23T19:15:00+00:00",
          "status": "OK"
        },
        "horizon_conflict": false
      }
    },
    "market": {
      "breadth_above_ema21": {
        "age_s": 666.503496,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "815832b01dd92f1e4451c79cf7955b56fb9737d65935bcfd1d3f33947ba7647c",
        "status": "OK",
        "v": 1.0,
        "version": "1.1dfe664d"
      },
      "minutes_to_close": {
        "age_s": 1.190388,
        "quality": {},
        "record_hash": "9dea38bde9bffd480415e110d4006bc31841dfb63bc08e86bac2f6f0f7ca31d7",
        "status": "OK",
        "v": 93.9114482,
        "version": "1.e79b1ead"
      },
      "regime_label": {
        "age_s": 666.503496,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "84f9e0050c68ef26c8fac251be3d1e9715d2043efbb27dc10dd36f804aed1906",
        "status": "OK",
        "v": "UPTREND",
        "version": "1.f8b361d7"
      },
      "session_phase": {
        "age_s": 1.190388,
        "quality": {},
        "record_hash": "d7148ba72d4f004c5b1878c050a58a44f997641ad4ab35d6b229973641c738d8",
        "status": "OK",
        "v": "NORMAL",
        "version": "1.91f88fe8"
      },
      "spy_ema_gap_bps_15m": {
        "age_s": 666.503496,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "e1b77372b1441b383700bc1a58f75ce0bf7cd28628675e926f5fce53abbe5d18",
        "status": "OK",
        "v": 46.06234614,
        "version": "1.fda7da7a"
      },
      "spy_ret_60m": {
        "age_s": 666.503496,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "b142676e3715503e9b86ac07722015d70a5dc110e33a78219756deccfc3a0bd0",
        "status": "OK",
        "v": -0.001607439756,
        "version": "1.9feddbd1"
      },
      "spy_vol_regime_ratio": {
        "age_s": 666.503496,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "cbd55c998b8b25e8c0e7dea1d5b05afaa28216f5d953e46156855fb3743c4456",
        "status": "OK",
        "v": 1.549365293,
        "version": "1.3b7257aa"
      }
    },
    "meta": {
      "news": {
        "AAPL": {
          "effective_weight": 0,
          "in_window": 0,
          "newest_age_min": null,
          "policy": "48h retained; per-article decay and minimum relevance; 4h count is descriptive",
          "poller_last_ok_age_s": 18.16434,
          "retrieved": 0,
          "selected": 0,
          "state": "QUIET",
          "window_min": 240
        }
      }
    },
    "news_blob_hash": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
    "news_context_blob_hash": "e3c60af9d95ebaf1f55c06533eacb239249be79ce6a8acc4ac91c59c6b87b05f",
    "portfolio": {
      "aggregate_cap_usd": {
        "age_s": 1.190388,
        "quality": {},
        "record_hash": "e824976fd10a5398ad7a640b03e46d440224b66f834e1fb4ed6e10a8ae4160d2",
        "status": "OK",
        "v": "49901.695",
        "version": "1.5b3d1daf"
      },
      "aggregate_headroom_usd": {
        "age_s": 1.190388,
        "quality": {},
        "record_hash": "d36534981d177b9392a8423ddba9c64f6a857c26de123be438124425a8710f95",
        "status": "OK",
        "v": "49901.695",
        "version": "1.7f894fff"
      },
      "buying_power": {
        "age_s": 1.190388,
        "quality": {},
        "record_hash": "9562781f132ba6478a727693d065acd8ab52fb41ad9f32e870579ae05f33413b",
        "status": "OK",
        "v": "399213.56",
        "version": "1.74948dec"
      },
      "cash": {
        "age_s": 1.190388,
        "quality": {},
        "record_hash": "01de5e8b40788241cf7072ccf2ad4ad4ab415f5aedae3165fa946c1336f1add5",
        "status": "OK",
        "v": "99803.39",
        "version": "1.b067f5e3"
      },
      "day_pnl_pct": {
        "age_s": 1.190388,
        "quality": {},
        "record_hash": "9a182af4a125228e11743a0e1a1d645c337876abe860e9d75ef54287760dd102",
        "status": "OK",
        "v": "0",
        "version": "1.35e81852"
      },
      "drawdown_pct": {
        "age_s": 1.190388,
        "quality": {},
        "record_hash": "ff7ab7da952c027dd5241a550b486340693df492e6727da70db76ccb1764df88",
        "status": "MISSING",
        "v": null,
        "version": "1.19aac9ba"
      },
      "equity": {
        "age_s": 1.190388,
        "quality": {},
        "record_hash": "4078585e5237db89317c65cf70b5efd903b080839fcb19a9479de73c1f87370a",
        "status": "OK",
        "v": "99803.39",
        "version": "1.a2192616"
      },
      "gross_exposure_pct": {
        "age_s": 1.190388,
        "quality": {},
        "record_hash": "bb639040bd8891c761d7e42a022727195bd4f3cfab4f4f8586518feb67ec32a4",
        "status": "OK",
        "v": "0E+2",
        "version": "1.b82cc518"
      },
      "gross_exposure_usd": {
        "age_s": 1.190388,
        "quality": {},
        "record_hash": "874b7c404c3826b9f1f244ea5a9cb68b56162181609389a663df4300d2350ec7",
        "status": "OK",
        "v": "0",
        "version": "1.e4c8752b"
      },
      "last_reconcile_age_s": {
        "age_s": 1.190388,
        "quality": {},
        "record_hash": "63b98385d4c65c757c2eca95594a0ec442c2692f4ce4a48a6ef0691faf9e4db1",
        "status": "OK",
        "v": 0,
        "version": "1.5ed0382f"
      },
      "open_buy_notional_usd": {
        "age_s": 1.190388,
        "quality": {},
        "record_hash": "758250811efff30a6a566622a165b2c466c05cdcdb602689de8ed915a3c3b0df",
        "status": "OK",
        "v": "0",
        "version": "1.0bd0ead1"
      },
      "open_orders": {
        "age_s": 1.190388,
        "quality": {},
        "record_hash": "fd80a03c80206cb1ba81be496c1699ded695e209cfd2121e04dc9a2b2e28fb4d",
        "status": "OK",
        "v": [],
        "version": "1.1cf37cbf"
      },
      "open_orders_count": {
        "age_s": 1.190388,
        "quality": {},
        "record_hash": "5499a55df1fd15c40792689e848f8f9d49265d99f7e9cc51b3a5761490920138",
        "status": "OK",
        "v": 0,
        "version": "1.1db4227a"
      },
      "pending_reserved_usd": {
        "age_s": 1.190388,
        "quality": {},
        "record_hash": "80fb68d37dced3927dd4e271ef630f5df7069cdaaa1c7cf8ae9826f5286feca3",
        "status": "OK",
        "v": "0",
        "version": "1.1c3e9604"
      },
      "positions": {
        "age_s": 1.190388,
        "quality": {},
        "record_hash": "70e916c3f617630ef1a2a2b5e0a9afa3c2624ba6f30bda148e50348f8c1546aa",
        "status": "OK",
        "v": [],
        "version": "1.c3284657"
      }
    },
    "registry_hash": "0fd3271269748046863b2f0558e45e2c333bb352eccc9899b7ff42277c8386fc",
    "schema_version": 1,
    "symbols": {
      "AAPL": {
        "adv_usd_20d": {
          "age_s": 253566.5035,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "e262af1fe6a7389e05b96a9a75b061c36d19abe6182590f4ef666a3c4147c5a3",
          "status": "OK",
          "v": 525559715.8,
          "version": "1.04f5e91f"
        },
        "ask_px": {
          "age_s": 2.786994,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "5d7fb7dc5533e05a0825513c74bfc8442654b92ae7bfd24b1f9f0f07eada41c2",
          "status": "OK",
          "v": 350.14,
          "version": "1.d21cdd09"
        },
        "atr14_15m": {
          "age_s": 666.503496,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "4aa601dee2846211e120ee408a21949bef6a84cbeaeda8c8217242fa79357ada",
          "status": "OK",
          "v": 1.466657912,
          "version": "1.0cd14e73"
        },
        "atr14_1d": {
          "age_s": 253566.5035,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "9c0633de46b036a4fe93734a2e5dce61b7eff6bf36ec86c1bf294d9eeef95f85",
          "status": "MISSING",
          "v": null,
          "version": "1.65e38f4c"
        },
        "atr14_pct": {
          "age_s": 253566.5035,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "1437ca280d0973889472dab3c5cb1b0006ef5ee631652a04bebaa9de603743bd",
          "status": "MISSING",
          "v": null,
          "version": "1.87450ee9"
        },
        "bid_px": {
          "age_s": 2.786994,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "0dc097b86e53045a02e4cb2fb960351f3fd05c523aaf15c6b2fd616842e21a93",
          "status": "OK",
          "v": 350.08,
          "version": "1.149628cd"
        },
        "dist_hi_atr": {
          "age_s": 666.503496,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "40c47665594fa60ce1cbfbc72e94312c3b9dd47dfeb81e9e75d0ccb511a4bc20",
          "status": "OK",
          "v": -1.725010297,
          "version": "1.913ffc4a"
        },
        "dist_lo_atr": {
          "age_s": 666.503496,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "a452592301e3cc53b447aa5817657d9e1ff8778d7d3012811d1e98f1048a5566",
          "status": "OK",
          "v": 3.102291245,
          "version": "1.79ba4c70"
        },
        "ema21_15m": {
          "age_s": 666.503496,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "a4fce26cfa0190c94a7c7a20a720ebe23cabd0d7ebbcf6c266507d885b6c2172",
          "status": "OK",
          "v": 348.3552073,
          "version": "1.bfcac61e"
        },
        "ema9_15m": {
          "age_s": 666.503496,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "0ad14ee0eb256fe1fe75965b26cc534f1723fca1dde7436232c23a087c645c3e",
          "status": "OK",
          "v": 348.9848916,
          "version": "1.81255de8"
        },
        "ema_gap_bps_15m": {
          "age_s": 666.503496,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "e727bcc5189a91061e7df830a4b1a4c71755006275cd2c0a493816f0a95e827b",
          "status": "OK",
          "v": 18.07592592,
          "version": "1.d4519f3c"
        },
        "gap_open_pct": {
          "age_s": 666.503496,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "fc5c7eeea7261785fc595b201a91df75e735719dbe6722604c7617e8524e7bc1",
          "status": "MISSING",
          "v": null,
          "version": "1.27438d4d"
        },
        "halted": {
          "age_s": 1.190388,
          "quality": {},
          "record_hash": "56dfd9e8cc7c5daab5e932f1b41394683e135b2cb4ce6b45a2d90151250aa20d",
          "status": "OK",
          "v": false,
          "version": "1.22c5cf87"
        },
        "held_minutes": {
          "age_s": 1.190388,
          "quality": {},
          "record_hash": "ef1fcd9d8367fe6f18e1ea09e36c2af7bd9667a03b518db89589d43f335b2543",
          "status": "MISSING",
          "v": null,
          "version": "1.de6ed6d3"
        },
        "intraday_ret_1h": {
          "age_s": 666.503496,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "bce1649c3f11808a59de7a9536a3a82e7ffdc25c2c36ac39b247c733fff4bd35",
          "status": "OK",
          "v": 0.001716689079,
          "version": "1.c3bb7751"
        },
        "intraday_setup_1m": {
          "age_s": 6.503496,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "99c2d7db47c220daf7619ae729ac4cbb813d67660023ec80ed7cfda70c743d2c",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:26:00+00:00",
            "window_start": "2026-11-23T19:16:00+00:00"
          },
          "record_hash": "2a1d5070c0749532d5028a15d556b5bcc257c450c4bdc6b38e90d8a8df2c636e",
          "status": "OK",
          "v": {
            "confirmation": "NONE",
            "pattern": "NONE",
            "prior_trend": "FLAT",
            "range_break": "INSIDE",
            "range_ceiling": 350.39,
            "range_floor": 349.8,
            "setup_minute": null,
            "volume_ratio": 0.7218
          },
          "version": "1.2a1f51e0"
        },
        "last_close": {
          "age_s": 253566.5035,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "f064e1589fb929d983b820bbfcd86fd0141cb1044925ea55db4eb69a6c6b5ae1",
          "status": "MISSING",
          "v": null,
          "version": "1.f2485fc2"
        },
        "luld_active": {
          "age_s": 1.190388,
          "quality": {},
          "record_hash": "7d1a29f1361c5375485ebe579054739d2c840bc6004af591b8f2431a0ef796a3",
          "status": "MISSING",
          "v": null,
          "version": "1.84a715b2"
        },
        "macd_hist_15m": {
          "age_s": 666.503496,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "5bdd527f747bb67db78b657003212927e07ba8624389f5381095f9a3f7a8d02f",
          "status": "OK",
          "v": 0.08324749226,
          "version": "1.391617c8"
        },
        "mid_px": {
          "age_s": 2.786994,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "69e91a5375de45389b59294074108bb37af14c4c1b93bc27acf5466296af14ac",
          "status": "OK",
          "v": 350.11,
          "version": "1.d567a349"
        },
        "news_age_min_latest": {
          "age_s": 18.16434,
          "quality": {},
          "record_hash": "3a3f569d9d8c00927952ffdbad6cafa85fd98bb79eb309d6b1c9dfddbbbb55ae",
          "status": "MISSING",
          "v": null,
          "version": "1.d0f79dc8"
        },
        "news_confirmed": {
          "age_s": 0,
          "quality": {
            "source": "stored news and pinned price features"
          },
          "status": "OK",
          "v": false,
          "version": "news-confirmation-v2"
        },
        "news_count_1h": {
          "age_s": 18.16434,
          "quality": {},
          "record_hash": "311eec9624e13d930729d2b06775a513774c59d2b2d948c310fcedf6b8d0953a",
          "status": "OK",
          "v": 0,
          "version": "1.0c9362fe"
        },
        "news_count_48h": {
          "age_s": 18.16434,
          "quality": {
            "as_of": "2026-11-23T19:26:06.503496+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 0,
          "version": "news-context-v2"
        },
        "news_count_4h": {
          "age_s": 18.16434,
          "quality": {
            "as_of": "2026-11-23T19:26:06.503496+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 0,
          "version": "news-context-v2"
        },
        "news_effective_sentiment": {
          "age_s": 0,
          "quality": {
            "selected": 0,
            "source": "decayed stored article metadata"
          },
          "status": "MISSING",
          "v": 0.0,
          "version": "news-decay-v2"
        },
        "news_event_flags_4h": {
          "age_s": 18.16434,
          "quality": {},
          "record_hash": "8ca8e5795d89d4803187584238943002a7a31c28fafd346a466d7ae9434e81a3",
          "status": "OK",
          "v": [],
          "version": "1.0b5a8a44"
        },
        "news_max_materiality_4h": {
          "age_s": 18.16434,
          "quality": {},
          "record_hash": "38c1a9f125d2e8a722bf395837a4f5c972adb3e97189908aa44e2b8a7559122d",
          "status": "OK",
          "v": 0,
          "version": "1.9c45e9b4"
        },
        "news_newest_age_min": {
          "age_s": 18.16434,
          "quality": {
            "as_of": "2026-11-23T19:26:06.503496+00:00",
            "source": "stored articles"
          },
          "status": "MISSING",
          "v": null,
          "version": "news-context-v2"
        },
        "news_novelty_max_4h": {
          "age_s": 18.16434,
          "quality": {},
          "record_hash": "6216d3c754b587fd23a0314298c71f6a46910607e90b18c305497e451fabd256",
          "status": "OK",
          "v": false,
          "version": "1.15ceb7bf"
        },
        "news_sent_ewm_240m": {
          "age_s": 18.16434,
          "quality": {},
          "record_hash": "0c6d4ac7d5c9c97f6fe8cae4751f6afadd951cadbd010dbbaa1a56ccda271b86",
          "status": "OK",
          "v": 0,
          "version": "1.9cad993f"
        },
        "news_sent_ewm_60m": {
          "age_s": 18.16434,
          "quality": {},
          "record_hash": "0a77d60a7bd29ae94570ee7e727baa2bdfc36d47836fabc42c27aff66bc4eba5",
          "status": "OK",
          "v": 0,
          "version": "1.74ab70c1"
        },
        "news_source_div_4h": {
          "age_s": 18.16434,
          "quality": {},
          "record_hash": "503238d796a947423683582a0a5558d6a437713f07833812c59875463500eb41",
          "status": "OK",
          "v": 0,
          "version": "1.6fd469c4"
        },
        "position_qty": {
          "age_s": 1.190388,
          "quality": {},
          "record_hash": "1aa590276d7c443b32fb2028565687eb51d237872ec009326262ecb600ebc9d0",
          "status": "OK",
          "v": "0",
          "version": "1.3a512120"
        },
        "position_value_usd": {
          "age_s": 1.190388,
          "quality": {},
          "record_hash": "245056dca2bc331989924bf4f47759457773e4c1eb0c80c50e0758e1c1068d7d",
          "status": "OK",
          "v": "0",
          "version": "1.9100bec4"
        },
        "price_vs_sma20": {
          "age_s": 253566.5035,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "a96d3080f2e95a5cc3b047ec495961d46cd4b318722c7eae4d719bfa2cc0f6e4",
          "status": "MISSING",
          "v": null,
          "version": "1.a986b9cc"
        },
        "recent_price_10m": {
          "age_s": 6.503496,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "99c2d7db47c220daf7619ae729ac4cbb813d67660023ec80ed7cfda70c743d2c",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:26:00+00:00",
            "window_start": "2026-11-23T19:16:00+00:00"
          },
          "record_hash": "d748a3fc334d9d2e282ab9ab747f72e6f1ca23a7fc1fc0685b76d0ec57a7d431",
          "status": "OK",
          "v": {
            "candles": [
              [
                0,
                350.18,
                350.22,
                350.05,
                350.22,
                1279.0,
                "VERIFIED_BAR"
              ],
              [
                1,
                350.09,
                350.09,
                349.91,
                349.91,
                1786.0,
                "VERIFIED_BAR"
              ],
              [
                2,
                349.93,
                350.005,
                349.84,
                350.005,
                2567.0,
                "VERIFIED_BAR"
              ],
              [
                3,
                349.92,
                350.15,
                349.89,
                350.13,
                3319.0,
                "VERIFIED_BAR"
              ],
              [
                4,
                350.155,
                350.22,
                350.09,
                350.18,
                2477.0,
                "VERIFIED_BAR"
              ],
              [
                5,
                350.19,
                350.39,
                350.17,
                350.25,
                2728.0,
                "VERIFIED_BAR"
              ],
              [
                6,
                350.21,
                350.225,
                350.0,
                350.015,
                1212.0,
                "VERIFIED_BAR"
              ],
              [
                7,
                349.87,
                349.98,
                349.82,
                349.82,
                1640.0,
                "VERIFIED_BAR"
              ],
              [
                8,
                349.86,
                350.12,
                349.8,
                350.05,
                3317.0,
                "VERIFIED_BAR"
              ],
              [
                9,
                349.99,
                350.12,
                349.97,
                350.07,
                1788.0,
                "VERIFIED_BAR"
              ]
            ],
            "columns": [
              "minute_offset",
              "open",
              "high",
              "low",
              "close",
              "volume",
              "coverage"
            ],
            "feed": "iex",
            "window_end": "2026-11-23T19:26:00+00:00",
            "window_start": "2026-11-23T19:16:00+00:00",
            "windows": {
              "10m": {
                "close": 350.07,
                "open": 350.18,
                "range_bps": 16.84847793,
                "return": -0.0003141241647,
                "status": "OK",
                "volume": 22113.0
              },
              "5m": {
                "close": 350.07,
                "open": 350.19,
                "range_bps": 16.8479968,
                "return": -0.0003426711214,
                "status": "OK",
                "volume": 10685.0
              }
            }
          },
          "version": "1.b12384d7"
        },
        "recent_range_bps_10m": {
          "age_s": 6.503496,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "99c2d7db47c220daf7619ae729ac4cbb813d67660023ec80ed7cfda70c743d2c",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:26:00+00:00",
            "window_start": "2026-11-23T19:16:00+00:00"
          },
          "record_hash": "781a3dad6d6995a86b82000cc85514ec6311f7e56e902405f681df0db4b7c0fd",
          "status": "OK",
          "v": 16.84847793,
          "version": "1.b7dd2e6e"
        },
        "recent_range_bps_5m": {
          "age_s": 6.503496,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "99c2d7db47c220daf7619ae729ac4cbb813d67660023ec80ed7cfda70c743d2c",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:26:00+00:00",
            "window_start": "2026-11-23T19:16:00+00:00"
          },
          "record_hash": "ca6b0456cb0136fd521eb59ba8813115bfc59fcad6554e1632389e2a0d270302",
          "status": "OK",
          "v": 16.8479968,
          "version": "1.860a2856"
        },
        "recent_return_10m": {
          "age_s": 6.503496,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "99c2d7db47c220daf7619ae729ac4cbb813d67660023ec80ed7cfda70c743d2c",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:26:00+00:00",
            "window_start": "2026-11-23T19:16:00+00:00"
          },
          "record_hash": "7cd1c2efdac2af548e6649c9126ec09fb452f737549d0fae5c0823a204853879",
          "status": "OK",
          "v": -0.0003141241647,
          "version": "1.03c04840"
        },
        "recent_return_5m": {
          "age_s": 6.503496,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "99c2d7db47c220daf7619ae729ac4cbb813d67660023ec80ed7cfda70c743d2c",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:26:00+00:00",
            "window_start": "2026-11-23T19:16:00+00:00"
          },
          "record_hash": "c88907dbcee04f1903a848cb67a1be97a01ceb10b7439b33c43b6ff3124f270b",
          "status": "OK",
          "v": -0.0003426711214,
          "version": "1.a9090b46"
        },
        "recent_volume_10m": {
          "age_s": 6.503496,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "99c2d7db47c220daf7619ae729ac4cbb813d67660023ec80ed7cfda70c743d2c",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:26:00+00:00",
            "window_start": "2026-11-23T19:16:00+00:00"
          },
          "record_hash": "83c897892781fee40aecbcc6599abda85da2ca0bcdf929900b0d844736e43a2f",
          "status": "OK",
          "v": 22113.0,
          "version": "1.891ed5cd"
        },
        "recent_volume_5m": {
          "age_s": 6.503496,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "99c2d7db47c220daf7619ae729ac4cbb813d67660023ec80ed7cfda70c743d2c",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:26:00+00:00",
            "window_start": "2026-11-23T19:16:00+00:00"
          },
          "record_hash": "74dec8cdf92185be5e859debae638a26d47b3e45d1b4c6018d78e7255d491cd0",
          "status": "OK",
          "v": 10685.0,
          "version": "1.c7331f02"
        },
        "relstr_spy_60m": {
          "age_s": 666.503496,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "9d66f515215390e411a6a78a452c1b314227d9e85443fdb5af30785039cce718",
          "status": "OK",
          "v": 0.001950345885,
          "version": "1.c04b464c"
        },
        "ret_15m": {
          "age_s": 666.503496,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "e182c98f3d33193f3f9dc126a7fa258eba8951450278e91a3cb669dc84fd90a3",
          "status": "OK",
          "v": 0.001774216626,
          "version": "1.3fa23ddd"
        },
        "ret_1d": {
          "age_s": 666.503496,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "acd4850c7f353cd7d276491b7c7d3402308f47b10f57d00ddfcff5304f668541",
          "status": "OK",
          "v": -0.01628543191,
          "version": "1.b77eca69"
        },
        "ret_20d": {
          "age_s": 253566.5035,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "c1fd6c69e5212d8143db80ab0b65f04c3952518636216a6f65599b0cf9aa5d52",
          "status": "MISSING",
          "v": null,
          "version": "1.7d1f1942"
        },
        "ret_5d": {
          "age_s": 253566.5035,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "e279e1e5300466ccb81556a606d3565ef56efdfaa8086d105f074c583b7f1520",
          "status": "MISSING",
          "v": null,
          "version": "1.5d56db82"
        },
        "ret_5m": {
          "age_s": 666.503496,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "6c8a5e618e2f12c793e51448bf22311686552ee29e8f4111fddd0e3712371e86",
          "status": "OK",
          "v": -0.0003141241647,
          "version": "1.c10a3b57"
        },
        "ret_60m": {
          "age_s": 666.503496,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "fccca55c136943a390236c8bbac9c5a9d08d89d1bd27b4a7784773d9482e3728",
          "status": "OK",
          "v": 0.0003429061294,
          "version": "1.6c49ff8f"
        },
        "rsi14": {
          "age_s": 253566.5035,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "017f8f44fae740e064f7cf662b6575f31515d3864f3470dc54f27aff186f4183",
          "status": "MISSING",
          "v": null,
          "version": "1.273a3a79"
        },
        "rsi14_15m": {
          "age_s": 666.503496,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "4bcd3b3bc68ef2a3b24588f819b282374f20d221da66c12182e92b5be0b02bf7",
          "status": "OK",
          "v": 60.34276894,
          "version": "1.f0b8fdaf"
        },
        "rvol_60m": {
          "age_s": 666.503496,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "c2f6317bf7ceb3c37708893f940596eec2f123b7681d383724f44ec9ec6e160b",
          "status": "OK",
          "v": 0.003833691689,
          "version": "1.84c5ec7e"
        },
        "sellable_qty": {
          "age_s": 1.190388,
          "quality": {},
          "record_hash": "414a0ca362542fa3ab11f6f4db6aa9e5f9bf1b8e57fb8897f43334a384543d07",
          "status": "OK",
          "v": "0",
          "version": "1.9cbf72e4"
        },
        "sma20": {
          "age_s": 253566.5035,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "3e4d68b668f1fb60d01391d426d6383d59c5f1489b2c60d8b9677923330ea1e8",
          "status": "MISSING",
          "v": null,
          "version": "1.80f8a078"
        },
        "sma50": {
          "age_s": 253566.5035,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "1ae3948821d316103e37237b485a2f4802a168c7ba7718bcaa1f5cecba683bb4",
          "status": "MISSING",
          "v": null,
          "version": "1.3890c9d7"
        },
        "spread_bps": {
          "age_s": 2.786994,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "b83fde2f6e5b578958ae33182e3e66ccd5e6b8d2da4893d6076662916338f0ce",
          "status": "OK",
          "v": 1.713747108,
          "version": "1.e2b080ab"
        },
        "trend_sma20_vs_sma50": {
          "age_s": 253566.5035,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "70f14cdb1db36bf9d9d5e86c7b54697ceba3042951e93e45270a4f006f4c91d8",
          "status": "MISSING",
          "v": null,
          "version": "1.84583425"
        },
        "unrealized_pnl_pct": {
          "age_s": 1.190388,
          "quality": {},
          "record_hash": "ccf95a3119c4e8c10478e02c04846da251a1178a0eae1eef1a199d797094c3e8",
          "status": "OK",
          "v": 0,
          "version": "1.7c530604"
        },
        "vol_regime_ratio": {
          "age_s": 666.503496,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "770c771a2056ff265bb460bc175636cb969915dc31e4b3ed4e54d78923f8c52f",
          "status": "OK",
          "v": 1.144197988,
          "version": "1.302e72c1"
        },
        "volume_z20": {
          "age_s": 253566.5035,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "68a11cf3df037bf35a94e13761dc1df96383de19536c6a0d960a52c5365f1e28",
          "status": "MISSING",
          "v": null,
          "version": "1.970d159b"
        },
        "volz_tod_15m": {
          "age_s": 666.503496,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "530fa07e56964d38a2104f4a1a003a9c21fe607e74364348f18f0dfb47005705",
          "status": "OK",
          "v": 0.1756718124,
          "version": "1.4315d547"
        },
        "vwap_dev_session": {
          "age_s": 666.503496,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "828359dd0c1e5c52aa177d18405776f4d344dd270faf4ae4d9297f27cf5f3839",
          "status": "OK",
          "v": 0.003129514455,
          "version": "1.b41de1ff"
        }
      }
    },
    "validation_policy": "scored-15m-plus-2m-v1"
  },
  "council_mode": "FULL",
  "chair": null,
  "skeptic_audit": null,
  "role_outputs": [
    {
      "role": "LIQUIDITY",
      "status": "OK",
      "response": "{\"schema_version\":2,\"run_id\":\"74d23f10-3119-5e34-9ebe-4ffc946dfc2f\",\"source\":\"code\",\"data_confidence\":\"HIGH\",\"role\":\"LIQUIDITY\",\"symbols\":[{\"symbol\":\"AAPL\",\"note\":\"deterministic code assessment\",\"evidence\":[{\"path\":\"symbols.AAPL.spread_bps\",\"band\":\"TIGHT\"},{\"path\":\"symbols.AAPL.mid_px\",\"band\":\"POSITIVE\"},{\"path\":\"symbols.AAPL.volz_tod_15m\",\"band\":\"NORMAL\"}],\"gate\":{\"state\":\"PASS\",\"size_multiplier\":1.0,\"reasons\":[]}}]}",
      "error": null
    },
    {
      "role": "PORTFOLIO",
      "status": "OK",
      "response": "{\"data_confidence\": \"HIGH\", \"role\": \"PORTFOLIO\", \"run_id\": \"74d23f10-3119-5e34-9ebe-4ffc946dfc2f\", \"schema_version\": 2, \"source\": \"code\", \"symbols\": [{\"evidence\": [{\"band\": \"POSITIVE\", \"path\": \"portfolio.equity\"}, {\"band\": \"ZERO\", \"path\": \"symbols.AAPL.position_qty\"}], \"gate\": {\"reasons\": [], \"size_multiplier\": 1.0, \"state\": \"PASS\"}, \"note\": \"Deterministic assessment; no news or signals to override.\", \"symbol\": \"AAPL\"}]}",
      "error": null
    },
    {
      "role": "REGIME",
      "status": "FALLBACK_PROVIDER",
      "response": null,
      "error": "LLMError: openai_compat 400: Error code: 400 - Parsing failed. The model generated output that could not be parsed. Please adjust your prompt. See 'failed_generation' for more details."
    },
    {
      "role": "TECHNICAL",
      "status": "OK",
      "response": "{\"data_confidence\": \"HIGH\", \"role\": \"TECHNICAL\", \"run_id\": \"74d23f10-3119-5e34-9ebe-4ffc946dfc2f\", \"schema_version\": 2, \"source\": \"code\", \"symbols\": [{\"evidence\": [{\"band\": \"POS_STRONG\", \"path\": \"symbols.AAPL.ema_gap_bps_15m\"}, {\"band\": \"FIRM\", \"path\": \"symbols.AAPL.rsi14_15m\"}, {\"band\": \"POSITIVE\", \"path\": \"symbols.AAPL.macd_hist_15m\"}, {\"band\": \"NONE\", \"path\": \"symbols.AAPL.intraday_setup_1m\"}, {\"band\": \"NEGATIVE\", \"path\": \"symbols.AAPL.recent_return_10m\"}], \"note\": \"Positive 15m trend but weak 10m momentum\", \"signal\": {\"confidence\": 0.75, \"horizon\": \"INTRADAY\", \"score\": 0.4, \"state\": \"SIGNAL\"}, \"symbol\": \"AAPL\"}]}",
      "error": null
    }
  ],
  "reason_codes": [
    "CODE_FLOOR_AFTER_PROVIDER_FAILURE"
  ],
  "notes": [
    "evidence_pack:f5867ff44792ac5734c23acac0f32748c9071c830e241dde164994c324c6c492",
    "council_run:74d23f10-3119-5e34-9ebe-4ffc946dfc2f",
    "CODE_FLOOR_AFTER_PROVIDER_FAILURE"
  ],
  "error": null,
  "proposals_and_risk": []
}
```

</details>

### 14:27:09 ET · INCOMPLETE_PROVIDER

<details>
<summary>Recorded decision evidence</summary>

```json
{
  "decision_id": "8c98c900-7768-595c-889d-daaa27173a5b",
  "inputs": {
    "as_of": "2026-11-23T19:27:06.623372Z",
    "regime": {
      "label": "uptrend"
    },
    "account": {
      "cash": 99803.39,
      "equity": 99803.39,
      "status": "ACTIVE",
      "account_id": "PAPER_ACCOUNT",
      "last_equity": 99803.39,
      "buying_power": 399213.56
    },
    "positions": [],
    "symbols": {
      "AAPL": {
        "mid": 349.955,
        "rsi14": null,
        "ret_1d": -0.0163,
        "ret_5d": null,
        "ret_20d": null,
        "atr14_pct": null,
        "price_vs_sma20": null,
        "trend_sma20_vs_sma50": null
      }
    }
  },
  "feature_evidence": {
    "account_ref": "PAPER_ACCOUNT",
    "as_of": "2026-11-23T19:27:06.623372+00:00",
    "availability": {
      "account": "fresh",
      "bars": "fresh",
      "calendar": "fresh",
      "news": "fresh",
      "ok_fraction_core_features": 1.0,
      "quotes": "fresh"
    },
    "bands_hash": "810517c6e124c7ebc23ca0ebce7ef7ba7cc66b30bc21cacc66c1a221174255d4",
    "feasibility": {
      "AAPL": {
        "can_buy": true,
        "can_buy_reasons": [],
        "can_sell": false,
        "can_sell_reasons": [
          "NO_SELLABLE_INVENTORY"
        ],
        "entry_window_open": true,
        "entry_window_reason": "",
        "held_qty": "0.0",
        "max_new_notional_usd": "2000.0",
        "sellable_qty": "0"
      }
    },
    "feature_slot": {
      "candles": {
        "AAPL|2026-11-23T19:12:00+00:00": "6cf77b23c73970e738306574ee418d5b11d7ad5d34d08539bb928b653cccb385",
        "AAPL|2026-11-23T19:13:00+00:00": "0e9a14fe740d7261310d963893297e28a03071451489fa33aded1b1a58acee67",
        "AAPL|2026-11-23T19:14:00+00:00": "d5bda39af69dcc53d4310b57aff3092db8a68054546c86a6b2df103d67ada5be",
        "AAPL|2026-11-23T19:15:00+00:00": "b0e6a6e9b9e4287c960f6ede77ad8f355970b7e8745dbe17c9339d2e3f12a605",
        "AAPL|2026-11-23T19:16:00+00:00": "69e7bfc090cee194af19c0acc6e8da6b7cf4c08443c52b952de98b8961d2ec67",
        "AAPL|2026-11-23T19:17:00+00:00": "c0a6e9630fa9f0d5027648d10559bb0be8e8caa0857d4fd8f17b11d4e3a85102",
        "AAPL|2026-11-23T19:18:00+00:00": "e862cb638fbc15b1a3f7b32db1c9e6d689acd1cd350079657d14e77d9e2c6479",
        "AAPL|2026-11-23T19:19:00+00:00": "e1937e8da6f995fc153f7e5e2ced98a01f960310d2ec214a17e4fb29a93c4146",
        "AAPL|2026-11-23T19:20:00+00:00": "70196363dae726bc8d352fd0e8cbb4b115e48fba11b5ee33c3817ea612c07c0f",
        "AAPL|2026-11-23T19:21:00+00:00": "6c6e08fc67af597579978fa03f3aaab5c3543c74e2011a7c2bce5c6d84460f57",
        "AAPL|2026-11-23T19:22:00+00:00": "2954cabc7ce7bf14ae0893aaac62bfaa70486fa0a68f63da27e0ee312728069a",
        "AAPL|2026-11-23T19:23:00+00:00": "2747e99b2df2570cd8f56be82b287c8ee7e009053a8933e9f3a90cd4d730228a",
        "AAPL|2026-11-23T19:24:00+00:00": "e1968a3f7d654002dbeeffb581d28f178a4778e7ef171a3abc48397e1eca10c1",
        "AAPL|2026-11-23T19:25:00+00:00": "f253416079d72d4e362e19307b75c172b7d2edb6ec453969e082d947eb75de1b",
        "AAPL|2026-11-23T19:26:00+00:00": "dd9ff1256c58363cc9dbfe3b821d6165825895311e1cec1730004c2187abd9a3",
        "SPY|2026-11-23T19:12:00+00:00": "bc09429308608b3ad795f14ea22a7b90d385a63386c6261b6f6b43a105a8c6e6",
        "SPY|2026-11-23T19:13:00+00:00": "2e0e8e4afe5f0552e559f4b57ab6f3a4af7aeed1c29df9bc0f8af4d993a0ec57",
        "SPY|2026-11-23T19:14:00+00:00": "1a003d29f3062e0e284c02aef050fc33aa9519155986beb8ffeabb18ba63d85e",
        "SPY|2026-11-23T19:15:00+00:00": "80f9ec707984fc74f8cb6dcebd3d845190206f212a6a7f5bbea8e7f0dfe5b85a",
        "SPY|2026-11-23T19:16:00+00:00": "bef27fecf6495d402ef4cf61ab22855605b7bf35ec2ee88c5fa240ececdeb144",
        "SPY|2026-11-23T19:17:00+00:00": "9267d9ec8514091597a775a9f11df8e6ba85ef1a765d8d7c6e0695a9d17e9d04",
        "SPY|2026-11-23T19:18:00+00:00": "9927bc665ca20d7006e3e28873737e2afb2679463ac195ed3f79e8551e2cdac5",
        "SPY|2026-11-23T19:19:00+00:00": "a3f91e79e75f72019e37a2793b54c01ee93403d8d9eafbd7f1eb0c5012b9b9c4",
        "SPY|2026-11-23T19:20:00+00:00": "e1ddcdb981d5c72dfaca25e1aaa8c1c27aef392260bc51ce1653cfd94d114f8f",
        "SPY|2026-11-23T19:21:00+00:00": "7a81b6670301657ad6b9cb0542ae646ff5785b4dbcb61c6b01fba0f60649ba1a",
        "SPY|2026-11-23T19:22:00+00:00": "39edefebca8c72b2135f978774a03b1d9775e0b17ef5fce054875b0dd7243c94",
        "SPY|2026-11-23T19:23:00+00:00": "def528246d2c8ce3e04085fb10ac15cd8741ba99e3ec0331c205f3d95712dca6",
        "SPY|2026-11-23T19:24:00+00:00": "e0825fbb3c82960924bc0a4fa93ab9a29cea452a13a515bbc433eb3e210b164a",
        "SPY|2026-11-23T19:25:00+00:00": "b6bef0076894b860d0d4faaa2427e9f8628a5c940154cdafae8278de8b4adb91",
        "SPY|2026-11-23T19:26:00+00:00": "55ddf1d0dcc3880a6635bdd09ea5075208a2f47cfde07bf52f2edee5699c8836"
      },
      "close": "2026-11-23T19:27:00+00:00",
      "feed": "iex",
      "indicator_close": "2026-11-23T19:15:00+00:00",
      "indicator_input_hashes": {
        "AAPL": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
        "SPY": "647346c3307bab3f0ab75d294e9bf46773d6d42fa0676aa83ae2ca9d97b2b1eb"
      },
      "provisional": true,
      "records": {
        "market:market:breadth_above_ema21": "815832b01dd92f1e4451c79cf7955b56fb9737d65935bcfd1d3f33947ba7647c",
        "market:market:regime_label": "84f9e0050c68ef26c8fac251be3d1e9715d2043efbb27dc10dd36f804aed1906",
        "market:market:spy_ema_gap_bps_15m": "e1b77372b1441b383700bc1a58f75ce0bf7cd28628675e926f5fce53abbe5d18",
        "market:market:spy_ret_60m": "e2ec962bc667b4c3f669cc66f882c64c5ae996bca4456067fd78a2bd4f972fec",
        "market:market:spy_vol_regime_ratio": "3bb51a65a163856dbc09823845a24764146d0fbab6122ecadf7d237fbf8a663e",
        "symbol:AAPL:adv_usd_20d": "e262af1fe6a7389e05b96a9a75b061c36d19abe6182590f4ef666a3c4147c5a3",
        "symbol:AAPL:atr14_15m": "4aa601dee2846211e120ee408a21949bef6a84cbeaeda8c8217242fa79357ada",
        "symbol:AAPL:atr14_1d": "9c0633de46b036a4fe93734a2e5dce61b7eff6bf36ec86c1bf294d9eeef95f85",
        "symbol:AAPL:atr14_pct": "1437ca280d0973889472dab3c5cb1b0006ef5ee631652a04bebaa9de603743bd",
        "symbol:AAPL:dist_hi_atr": "8d6ba7e58b7a87f9f8941003b40976a131e960a0c3bddc6b999c7f3893bb8c00",
        "symbol:AAPL:dist_lo_atr": "72053a937af4027b0431ee94587a9e9aa613a88e83f2d581e460835f1bc308f4",
        "symbol:AAPL:ema21_15m": "a4fce26cfa0190c94a7c7a20a720ebe23cabd0d7ebbcf6c266507d885b6c2172",
        "symbol:AAPL:ema9_15m": "0ad14ee0eb256fe1fe75965b26cc534f1723fca1dde7436232c23a087c645c3e",
        "symbol:AAPL:ema_gap_bps_15m": "e727bcc5189a91061e7df830a4b1a4c71755006275cd2c0a493816f0a95e827b",
        "symbol:AAPL:gap_open_pct": "fc5c7eeea7261785fc595b201a91df75e735719dbe6722604c7617e8524e7bc1",
        "symbol:AAPL:intraday_ret_1h": "bce1649c3f11808a59de7a9536a3a82e7ffdc25c2c36ac39b247c733fff4bd35",
        "symbol:AAPL:intraday_setup_1m": "63ce7f1708d9f3fbd98381b9bbb59fe9af46a048e3fd24be408840a8b517b0ae",
        "symbol:AAPL:last_close": "f064e1589fb929d983b820bbfcd86fd0141cb1044925ea55db4eb69a6c6b5ae1",
        "symbol:AAPL:macd_hist_15m": "5bdd527f747bb67db78b657003212927e07ba8624389f5381095f9a3f7a8d02f",
        "symbol:AAPL:price_vs_sma20": "a96d3080f2e95a5cc3b047ec495961d46cd4b318722c7eae4d719bfa2cc0f6e4",
        "symbol:AAPL:recent_price_10m": "19274b22175b0c5965ba366189625666f3aff7613d21068b8dcef0d6bff16820",
        "symbol:AAPL:recent_range_bps_10m": "0b1d7711fc85b1c92cb4aeb26623fc0e7f53204bf3b407f7075896c61a9e480c",
        "symbol:AAPL:recent_range_bps_5m": "fd5f977215b819a92ad1e2b651ddd5596ac972200112dc519e59d186106a055c",
        "symbol:AAPL:recent_return_10m": "e341b0046f68fd54ce6a464c0229ba2a17a474807bf3e3c601bfb9c483beb6ff",
        "symbol:AAPL:recent_return_5m": "a6f158ed65cecef6e097926b6b5f061b7a3350ba7b5cbdc1f1bcc5349ab4dae0",
        "symbol:AAPL:recent_volume_10m": "f5699629371f99660f3959e3d16b01ac1dfe64262e9cd9601d9cfcd3d9154b13",
        "symbol:AAPL:recent_volume_5m": "f7ce00b628f5be2e6b6ee38a02e42c1e2d5ce53cbf446d7109e7800ae5f24b6c",
        "symbol:AAPL:relstr_spy_60m": "c1cd791cc13f0f3e6279dff9b3b656f5b714d841da983b113089ff312c037109",
        "symbol:AAPL:ret_15m": "4db84c3a6361982d52b50d6a896b87146b4a399f28953e6b5dcfc6cf2a0ccb78",
        "symbol:AAPL:ret_1d": "acd4850c7f353cd7d276491b7c7d3402308f47b10f57d00ddfcff5304f668541",
        "symbol:AAPL:ret_20d": "c1fd6c69e5212d8143db80ab0b65f04c3952518636216a6f65599b0cf9aa5d52",
        "symbol:AAPL:ret_5d": "e279e1e5300466ccb81556a606d3565ef56efdfaa8086d105f074c583b7f1520",
        "symbol:AAPL:ret_5m": "a7b31cbc3b119da60375c14d7ed81d10ad584fc692721b8d4a70dba781542d46",
        "symbol:AAPL:ret_60m": "a0a65c45d781caf3b92f726bf804910735efc7a3cf98d78caf328c9b8bd1c3df",
        "symbol:AAPL:rsi14": "017f8f44fae740e064f7cf662b6575f31515d3864f3470dc54f27aff186f4183",
        "symbol:AAPL:rsi14_15m": "4bcd3b3bc68ef2a3b24588f819b282374f20d221da66c12182e92b5be0b02bf7",
        "symbol:AAPL:rvol_60m": "663654db41b4a341972c58fcec80c259e623fe0a260658428ec0d74880dc4ed5",
        "symbol:AAPL:sma20": "3e4d68b668f1fb60d01391d426d6383d59c5f1489b2c60d8b9677923330ea1e8",
        "symbol:AAPL:sma50": "1ae3948821d316103e37237b485a2f4802a168c7ba7718bcaa1f5cecba683bb4",
        "symbol:AAPL:trend_sma20_vs_sma50": "70f14cdb1db36bf9d9d5e86c7b54697ceba3042951e93e45270a4f006f4c91d8",
        "symbol:AAPL:vol_regime_ratio": "f69948c83a718a0f906c505897d605f322619e1dd45efcd1c2352a1ca26ea237",
        "symbol:AAPL:volume_z20": "68a11cf3df037bf35a94e13761dc1df96383de19536c6a0d960a52c5365f1e28",
        "symbol:AAPL:volz_tod_15m": "530fa07e56964d38a2104f4a1a003a9c21fe607e74364348f18f0dfb47005705",
        "symbol:AAPL:vwap_dev_session": "bb5028b28be03f1e618884072e463b229c51c30e133f0429f1dd3b67f1d7d458",
        "symbol:SPY:adv_usd_20d": "7773f3a908eaf7c0e76c09e0281ebbcb8379cc49400a15772c1830a3b2c2f223",
        "symbol:SPY:atr14_15m": "fc718bba22a5db9dae206edea8233cf88df09c2e3062133470a7fe10f13267e2",
        "symbol:SPY:atr14_1d": "aaeea7993a9d2b21fb57bccbb0a7e2bae3ebb9bc634c0e9b485665df8a582439",
        "symbol:SPY:atr14_pct": "684fcce9d38b849dfc48ed4adf427634c6537f0b2d2dac4b1ac576ea747f9ea6",
        "symbol:SPY:dist_hi_atr": "d228040b17061123de8062f9c01009ed9b9beb6f53b1be7d6b37fed992f7089f",
        "symbol:SPY:dist_lo_atr": "0e4f21b82cc92901774a0122cd40b63f68b070ffa628177f120e09f755b4b83a",
        "symbol:SPY:ema21_15m": "d517509d58dbc26956d75d98347e4757713275e63455fdcc3c4422d256746a81",
        "symbol:SPY:ema9_15m": "097b3848e725e0d802d5441768fbf4db8207cbc178c1f391212f3cf9f984afeb",
        "symbol:SPY:ema_gap_bps_15m": "88de61b58000f6c109f37ccb1278278f5d8761b975c2735eb8c0fceb4c8789cc",
        "symbol:SPY:gap_open_pct": "7b8b09f491c0f145686f016617f1e339ec2c992d2d7f4b990a6f22f849fb269b",
        "symbol:SPY:intraday_ret_1h": "e04939fd11622d8ee6f45b21cbd60aaf479b74745d0331a0d031b34eb916d9e1",
        "symbol:SPY:intraday_setup_1m": "91b9f03f2705f3aebd3a1b004e8fbef66af31c84339351e90fbbbb073419264f",
        "symbol:SPY:last_close": "7c75e5b2d0cbfa6053329d40230beafe8c50de8de09b8650fbc56c1f24fef8dd",
        "symbol:SPY:macd_hist_15m": "700faaf2b22ddb3d7a761119e621afb779197ee9e20002bf78ec397dc82b0426",
        "symbol:SPY:price_vs_sma20": "b3b5e555c37b8c77664c4514095e6ed44684e1cca73f30c87e244ef5047030fc",
        "symbol:SPY:recent_price_10m": "30a7d70c3672fdb5282f218b10f5f5bcc0be00c731f3e22102167bc0048a7231",
        "symbol:SPY:recent_range_bps_10m": "7e76c28a8f2811a8a613e4148a530e19078443d245eb280ed8b235eb94e731e9",
        "symbol:SPY:recent_range_bps_5m": "f325390fd03c63f3b5bf48403e12fed423c682ead8a34acafef846e0387a0b8f",
        "symbol:SPY:recent_return_10m": "10f31e29e2695997ac379718631aa377112fe029c50a9122f50e09a8157fc9dd",
        "symbol:SPY:recent_return_5m": "898cbdd9a268045ff0ef9af097dc44c79f15323cbf12611edb74d23bca576c6c",
        "symbol:SPY:recent_volume_10m": "92b5c6170b1ee83a4be6f350263a0d23daa7f5e18b194039e54ee2ce2649cab0",
        "symbol:SPY:recent_volume_5m": "3d6c740e83c8b71bab69c0e528a2559967449ef21f7676c59df08be26dbcb32a",
        "symbol:SPY:relstr_spy_60m": "f8e8a2c70f6861986994098551914f6ec7f583a6212d91b31d608d2906cc194a",
        "symbol:SPY:ret_15m": "d777a564b31886a34f2913ebdb9a646499dff11282166528aeb3cb3f9c090064",
        "symbol:SPY:ret_1d": "ddc0a11b63cc350e3081db1903dee6252ddb61770d13b16e856291026f52a3f3",
        "symbol:SPY:ret_20d": "ed1093e0aa5d6f66c95107ca1d6e0dc684f91a2b174538f28adce162fbc2a1c1",
        "symbol:SPY:ret_5d": "2298165b21cd162151213ae636f77a63a657bd096db984033682489995a3b1f5",
        "symbol:SPY:ret_5m": "69498276b955ce0402f1fbb5ababfef82d92c813cc0e99d8b15c7a6d976f20dd",
        "symbol:SPY:ret_60m": "b85a4221dd089ba4abeb38888a9994220e2347d8c39fd5a2f36911acb0b712ee",
        "symbol:SPY:rsi14": "0896ff9e6527016820c4f3bacca566bf1825f6f67c30f9e930a11faa591958f6",
        "symbol:SPY:rsi14_15m": "f74fdb6b8a4dfd4479e87521b52a8e59d763710203d578d8f94a9675c6c9b551",
        "symbol:SPY:rvol_60m": "22a825a473420b24e2f200359469119e6a6cbc1db37818cad4fed53d21acd564",
        "symbol:SPY:sma20": "d0283363840868af6910e903d8b6ce0fa7a2a5f15f1fe6688eee56a4e374e136",
        "symbol:SPY:sma50": "f0b368651bafa612c1bc158db1c24203caf7f9a36cde9c70a55ee93a918503d6",
        "symbol:SPY:trend_sma20_vs_sma50": "081b68b933591d41fda8068af744f2f85c5c3ab9eea6461455fa6828810c399c",
        "symbol:SPY:vol_regime_ratio": "cc6b5a7ea7e75f3e42716de66952272e88e84dc6e782e419dd171e024f460a64",
        "symbol:SPY:volume_z20": "b50666ce3e64dd1b2b048c991b636383b066dc0bdc8adda4888131d53fc369b6",
        "symbol:SPY:volz_tod_15m": "461ed44d456e55c2fcef586cde4f795fb112387dee57647074b82b07fa685f52",
        "symbol:SPY:vwap_dev_session": "332294ca2def97532cce478a0fbe19f492ebcf2d7858788b3c22d3ef4a86b6a0"
      },
      "symbols": [
        "AAPL",
        "SPY"
      ]
    },
    "horizons": {
      "AAPL": {
        "10m": {
          "age_s": 6.623372,
          "last_bar_end": "2026-11-23T19:27:00+00:00",
          "status": "OK"
        },
        "15m": {
          "age_s": 726.623372,
          "last_bar_end": "2026-11-23T19:15:00+00:00",
          "status": "OK"
        },
        "5m": {
          "age_s": 6.623372,
          "last_bar_end": "2026-11-23T19:27:00+00:00",
          "status": "OK"
        },
        "60m": {
          "age_s": 726.623372,
          "last_bar_end": "2026-11-23T19:15:00+00:00",
          "status": "OK"
        },
        "horizon_conflict": false
      }
    },
    "market": {
      "breadth_above_ema21": {
        "age_s": 726.623372,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "815832b01dd92f1e4451c79cf7955b56fb9737d65935bcfd1d3f33947ba7647c",
        "status": "OK",
        "v": 1.0,
        "version": "1.1dfe664d"
      },
      "minutes_to_close": {
        "age_s": 0.559092,
        "quality": {},
        "record_hash": "b48aa8b17410a0a10436c6adfa9d3029973eb13807d6aa97e449922c691271fa",
        "status": "OK",
        "v": 92.89892867,
        "version": "1.e79b1ead"
      },
      "regime_label": {
        "age_s": 726.623372,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "84f9e0050c68ef26c8fac251be3d1e9715d2043efbb27dc10dd36f804aed1906",
        "status": "OK",
        "v": "UPTREND",
        "version": "1.f8b361d7"
      },
      "session_phase": {
        "age_s": 0.559092,
        "quality": {},
        "record_hash": "112369d6d44dffcd59d2a08d16301f3dc5893acd07ab5a77ca99b72d9ae09b80",
        "status": "OK",
        "v": "NORMAL",
        "version": "1.91f88fe8"
      },
      "spy_ema_gap_bps_15m": {
        "age_s": 726.623372,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "e1b77372b1441b383700bc1a58f75ce0bf7cd28628675e926f5fce53abbe5d18",
        "status": "OK",
        "v": 46.06234614,
        "version": "1.fda7da7a"
      },
      "spy_ret_60m": {
        "age_s": 726.623372,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "e2ec962bc667b4c3f669cc66f882c64c5ae996bca4456067fd78a2bd4f972fec",
        "status": "OK",
        "v": -0.001352526326,
        "version": "1.9feddbd1"
      },
      "spy_vol_regime_ratio": {
        "age_s": 726.623372,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "3bb51a65a163856dbc09823845a24764146d0fbab6122ecadf7d237fbf8a663e",
        "status": "OK",
        "v": 1.559176922,
        "version": "1.3b7257aa"
      }
    },
    "meta": {
      "news": {
        "AAPL": {
          "effective_weight": 0,
          "in_window": 0,
          "newest_age_min": null,
          "policy": "48h retained; per-article decay and minimum relevance; 4h count is descriptive",
          "poller_last_ok_age_s": 17.744336,
          "retrieved": 0,
          "selected": 0,
          "state": "QUIET",
          "window_min": 240
        }
      }
    },
    "news_blob_hash": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
    "news_context_blob_hash": "e3c60af9d95ebaf1f55c06533eacb239249be79ce6a8acc4ac91c59c6b87b05f",
    "portfolio": {
      "aggregate_cap_usd": {
        "age_s": 0.559092,
        "quality": {},
        "record_hash": "23cb1ba27de50e448277028ce69ce922cbf4ef1046838d783cdd449ec404b6fa",
        "status": "OK",
        "v": "49901.695",
        "version": "1.5b3d1daf"
      },
      "aggregate_headroom_usd": {
        "age_s": 0.559092,
        "quality": {},
        "record_hash": "7e586cbfbab9d60d40363c622a109041a82c542c29eee313be7bec087cb27e60",
        "status": "OK",
        "v": "49901.695",
        "version": "1.7f894fff"
      },
      "buying_power": {
        "age_s": 0.559092,
        "quality": {},
        "record_hash": "a96f7a463e3268437d77ce0a95e74f6e0edd75b4df6f8c9aff8bf65f67367eba",
        "status": "OK",
        "v": "399213.56",
        "version": "1.74948dec"
      },
      "cash": {
        "age_s": 0.559092,
        "quality": {},
        "record_hash": "14394d4bc36b6ed251833c5beb5910eb5dffb5dabaad17b9fad9583f33f399d7",
        "status": "OK",
        "v": "99803.39",
        "version": "1.b067f5e3"
      },
      "day_pnl_pct": {
        "age_s": 0.559092,
        "quality": {},
        "record_hash": "f34d60686bba5bd66b0dfd45b1ad470dc51902368f36bbcfe638ad91bc0f90b0",
        "status": "OK",
        "v": "0",
        "version": "1.35e81852"
      },
      "drawdown_pct": {
        "age_s": 0.559092,
        "quality": {},
        "record_hash": "b107af6ee2066632667cd04b4e14d12023cbc8c424e1dfac3f265a941e9b0fd2",
        "status": "MISSING",
        "v": null,
        "version": "1.19aac9ba"
      },
      "equity": {
        "age_s": 0.559092,
        "quality": {},
        "record_hash": "92df0f1900c678687ca98d98851bd164203f19b0f1b5ddb0f3f1d6bd152b7c6c",
        "status": "OK",
        "v": "99803.39",
        "version": "1.a2192616"
      },
      "gross_exposure_pct": {
        "age_s": 0.559092,
        "quality": {},
        "record_hash": "b134cc669ddaffd3ef2ba8d0bdeea4c7d989494298369c4565db528e905d89ad",
        "status": "OK",
        "v": "0E+2",
        "version": "1.b82cc518"
      },
      "gross_exposure_usd": {
        "age_s": 0.559092,
        "quality": {},
        "record_hash": "633ec12fcd1fd0ea5767761982288edf4c076169cd465fe546e3196ee8814643",
        "status": "OK",
        "v": "0",
        "version": "1.e4c8752b"
      },
      "last_reconcile_age_s": {
        "age_s": 0.559092,
        "quality": {},
        "record_hash": "f83127433b48e4fbb39efe2509d7221ecfe9aaa89b2cfe655c3cc71da1e35e94",
        "status": "OK",
        "v": 0,
        "version": "1.5ed0382f"
      },
      "open_buy_notional_usd": {
        "age_s": 0.559092,
        "quality": {},
        "record_hash": "4636588acabbdd9976f04e99bc6ec278505f8d6c28fa3e09c6b5e3953bd2c9ce",
        "status": "OK",
        "v": "0",
        "version": "1.0bd0ead1"
      },
      "open_orders": {
        "age_s": 0.559092,
        "quality": {},
        "record_hash": "e51b8c18baf0bbaf5f23dafd033d77af166714e1ecd422365ba73224d229c4a3",
        "status": "OK",
        "v": [],
        "version": "1.1cf37cbf"
      },
      "open_orders_count": {
        "age_s": 0.559092,
        "quality": {},
        "record_hash": "95e662f334e89a48634686784c3d2559e7380d2c01a46b2964b46981fecf87f1",
        "status": "OK",
        "v": 0,
        "version": "1.1db4227a"
      },
      "pending_reserved_usd": {
        "age_s": 0.559092,
        "quality": {},
        "record_hash": "53235cf1c801f4ab72e9edd57ee45e82af1632e73051ccfd3c41619f3c68611e",
        "status": "OK",
        "v": "0",
        "version": "1.1c3e9604"
      },
      "positions": {
        "age_s": 0.559092,
        "quality": {},
        "record_hash": "b36959d97c642718969f859e1d409d170e14c0506f79c62a270b967dbc6af6d5",
        "status": "OK",
        "v": [],
        "version": "1.c3284657"
      }
    },
    "registry_hash": "0fd3271269748046863b2f0558e45e2c333bb352eccc9899b7ff42277c8386fc",
    "schema_version": 1,
    "symbols": {
      "AAPL": {
        "adv_usd_20d": {
          "age_s": 253626.6234,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "e262af1fe6a7389e05b96a9a75b061c36d19abe6182590f4ef666a3c4147c5a3",
          "status": "OK",
          "v": 525559715.8,
          "version": "1.04f5e91f"
        },
        "ask_px": {
          "age_s": 1.536381,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "faa1740757fbb848e30326b21641eaa593a3ffa3fc7c52521fb6e78b65cb9d3c",
          "status": "OK",
          "v": 350.21,
          "version": "1.d21cdd09"
        },
        "atr14_15m": {
          "age_s": 726.623372,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "4aa601dee2846211e120ee408a21949bef6a84cbeaeda8c8217242fa79357ada",
          "status": "OK",
          "v": 1.466657912,
          "version": "1.0cd14e73"
        },
        "atr14_1d": {
          "age_s": 253626.6234,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "9c0633de46b036a4fe93734a2e5dce61b7eff6bf36ec86c1bf294d9eeef95f85",
          "status": "MISSING",
          "v": null,
          "version": "1.65e38f4c"
        },
        "atr14_pct": {
          "age_s": 253626.6234,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "1437ca280d0973889472dab3c5cb1b0006ef5ee631652a04bebaa9de603743bd",
          "status": "MISSING",
          "v": null,
          "version": "1.87450ee9"
        },
        "bid_px": {
          "age_s": 1.536381,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "1d8e48f9ac782bec1360a50960fee528327ea124cfde0255ea36b19bdc878ee0",
          "status": "OK",
          "v": 349.7,
          "version": "1.149628cd"
        },
        "dist_hi_atr": {
          "age_s": 726.623372,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "8d6ba7e58b7a87f9f8941003b40976a131e960a0c3bddc6b999c7f3893bb8c00",
          "status": "OK",
          "v": -1.684100961,
          "version": "1.913ffc4a"
        },
        "dist_lo_atr": {
          "age_s": 726.623372,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "72053a937af4027b0431ee94587a9e9aa613a88e83f2d581e460835f1bc308f4",
          "status": "OK",
          "v": 3.14320058,
          "version": "1.79ba4c70"
        },
        "ema21_15m": {
          "age_s": 726.623372,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "a4fce26cfa0190c94a7c7a20a720ebe23cabd0d7ebbcf6c266507d885b6c2172",
          "status": "OK",
          "v": 348.3552073,
          "version": "1.bfcac61e"
        },
        "ema9_15m": {
          "age_s": 726.623372,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "0ad14ee0eb256fe1fe75965b26cc534f1723fca1dde7436232c23a087c645c3e",
          "status": "OK",
          "v": 348.9848916,
          "version": "1.81255de8"
        },
        "ema_gap_bps_15m": {
          "age_s": 726.623372,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "e727bcc5189a91061e7df830a4b1a4c71755006275cd2c0a493816f0a95e827b",
          "status": "OK",
          "v": 18.07592592,
          "version": "1.d4519f3c"
        },
        "gap_open_pct": {
          "age_s": 726.623372,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "fc5c7eeea7261785fc595b201a91df75e735719dbe6722604c7617e8524e7bc1",
          "status": "MISSING",
          "v": null,
          "version": "1.27438d4d"
        },
        "halted": {
          "age_s": 0.559092,
          "quality": {},
          "record_hash": "10066669c2da88c9c827ed65bef327bfd2030ab2c13b4dfab60558cb6e2df512",
          "status": "OK",
          "v": false,
          "version": "1.22c5cf87"
        },
        "held_minutes": {
          "age_s": 0.559092,
          "quality": {},
          "record_hash": "08487fd5c2dc238a4933d045012d0fa83345c361dcf05db15e7f0f87b498d940",
          "status": "MISSING",
          "v": null,
          "version": "1.de6ed6d3"
        },
        "intraday_ret_1h": {
          "age_s": 726.623372,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "bce1649c3f11808a59de7a9536a3a82e7ffdc25c2c36ac39b247c733fff4bd35",
          "status": "OK",
          "v": 0.001716689079,
          "version": "1.c3bb7751"
        },
        "intraday_setup_1m": {
          "age_s": 6.623372,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "2c4aa90a603d33bd730c709ea8db0fdd4b56a8a9232ce33bbd24f62d36f1a7c9",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:27:00+00:00",
            "window_start": "2026-11-23T19:17:00+00:00"
          },
          "record_hash": "63ce7f1708d9f3fbd98381b9bbb59fe9af46a048e3fd24be408840a8b517b0ae",
          "status": "OK",
          "v": {
            "confirmation": "UNCONFIRMED",
            "pattern": "DOJI",
            "prior_trend": "FLAT",
            "range_break": "INSIDE",
            "range_ceiling": 350.39,
            "range_floor": 349.8,
            "setup_minute": 9,
            "volume_ratio": 0.9217
          },
          "version": "1.2a1f51e0"
        },
        "last_close": {
          "age_s": 253626.6234,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "f064e1589fb929d983b820bbfcd86fd0141cb1044925ea55db4eb69a6c6b5ae1",
          "status": "MISSING",
          "v": null,
          "version": "1.f2485fc2"
        },
        "luld_active": {
          "age_s": 0.559092,
          "quality": {},
          "record_hash": "79be3064a2e3d8bffd2bbd93bf0cdf0c3117503308a323e275b1546e75818ec7",
          "status": "MISSING",
          "v": null,
          "version": "1.84a715b2"
        },
        "macd_hist_15m": {
          "age_s": 726.623372,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "5bdd527f747bb67db78b657003212927e07ba8624389f5381095f9a3f7a8d02f",
          "status": "OK",
          "v": 0.08324749226,
          "version": "1.391617c8"
        },
        "mid_px": {
          "age_s": 1.536381,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "4cb6624be647839d668900e7877bb1981cd19e8351f40515bbbd8ac2796bdecf",
          "status": "OK",
          "v": 349.955,
          "version": "1.d567a349"
        },
        "news_age_min_latest": {
          "age_s": 17.744336,
          "quality": {},
          "record_hash": "1c67972da33f21d0e63d598c926865ae7a1cf45c49ea10bb2bbe6143696a0ac6",
          "status": "MISSING",
          "v": null,
          "version": "1.d0f79dc8"
        },
        "news_confirmed": {
          "age_s": 0,
          "quality": {
            "source": "stored news and pinned price features"
          },
          "status": "OK",
          "v": false,
          "version": "news-confirmation-v2"
        },
        "news_count_1h": {
          "age_s": 17.744336,
          "quality": {},
          "record_hash": "436510d533ac229ccb452e888500944acb838f017ecd444dc237ba4dffc1ecef",
          "status": "OK",
          "v": 0,
          "version": "1.0c9362fe"
        },
        "news_count_48h": {
          "age_s": 17.744336,
          "quality": {
            "as_of": "2026-11-23T19:27:06.623372+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 0,
          "version": "news-context-v2"
        },
        "news_count_4h": {
          "age_s": 17.744336,
          "quality": {
            "as_of": "2026-11-23T19:27:06.623372+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 0,
          "version": "news-context-v2"
        },
        "news_effective_sentiment": {
          "age_s": 0,
          "quality": {
            "selected": 0,
            "source": "decayed stored article metadata"
          },
          "status": "MISSING",
          "v": 0.0,
          "version": "news-decay-v2"
        },
        "news_event_flags_4h": {
          "age_s": 17.744336,
          "quality": {},
          "record_hash": "cbea178ecebbed8774dcc1ce78bb0ecbaada7b231050c8f23ef220d2c3de6747",
          "status": "OK",
          "v": [],
          "version": "1.0b5a8a44"
        },
        "news_max_materiality_4h": {
          "age_s": 17.744336,
          "quality": {},
          "record_hash": "da4e29121afac295712508729d39fadb8d9bb142149ea55b50752c60863c9e40",
          "status": "OK",
          "v": 0,
          "version": "1.9c45e9b4"
        },
        "news_newest_age_min": {
          "age_s": 17.744336,
          "quality": {
            "as_of": "2026-11-23T19:27:06.623372+00:00",
            "source": "stored articles"
          },
          "status": "MISSING",
          "v": null,
          "version": "news-context-v2"
        },
        "news_novelty_max_4h": {
          "age_s": 17.744336,
          "quality": {},
          "record_hash": "4722b6bfe92667c5866c4696d494bae591268933f90d619321e536724a487968",
          "status": "OK",
          "v": false,
          "version": "1.15ceb7bf"
        },
        "news_sent_ewm_240m": {
          "age_s": 17.744336,
          "quality": {},
          "record_hash": "39cf54d0e0c3f66b1813f7030538f4c4cfdf0324856e9e3bd30616df105fa90b",
          "status": "OK",
          "v": 0,
          "version": "1.9cad993f"
        },
        "news_sent_ewm_60m": {
          "age_s": 17.744336,
          "quality": {},
          "record_hash": "63554fc011c756bc1c6bf23228c6c3824b92f68cf121303c2079885bdeb219a1",
          "status": "OK",
          "v": 0,
          "version": "1.74ab70c1"
        },
        "news_source_div_4h": {
          "age_s": 17.744336,
          "quality": {},
          "record_hash": "f8f19b4a9cd4ca142a210c97dc412261e56eec8a2fbb2298e059fad5a0975e47",
          "status": "OK",
          "v": 0,
          "version": "1.6fd469c4"
        },
        "position_qty": {
          "age_s": 0.559092,
          "quality": {},
          "record_hash": "7a220b0d0646a36c0486bf77dacfc7f7514ce2b518d9010ec0e45bb3cc108888",
          "status": "OK",
          "v": "0",
          "version": "1.3a512120"
        },
        "position_value_usd": {
          "age_s": 0.559092,
          "quality": {},
          "record_hash": "957e55b872b58a5a9809c1269d2f313dd25ca04e28c7e745dc9143c4862b917e",
          "status": "OK",
          "v": "0",
          "version": "1.9100bec4"
        },
        "price_vs_sma20": {
          "age_s": 253626.6234,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "a96d3080f2e95a5cc3b047ec495961d46cd4b318722c7eae4d719bfa2cc0f6e4",
          "status": "MISSING",
          "v": null,
          "version": "1.a986b9cc"
        },
        "recent_price_10m": {
          "age_s": 6.623372,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "2c4aa90a603d33bd730c709ea8db0fdd4b56a8a9232ce33bbd24f62d36f1a7c9",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:27:00+00:00",
            "window_start": "2026-11-23T19:17:00+00:00"
          },
          "record_hash": "19274b22175b0c5965ba366189625666f3aff7613d21068b8dcef0d6bff16820",
          "status": "OK",
          "v": {
            "candles": [
              [
                0,
                350.09,
                350.09,
                349.91,
                349.91,
                1786.0,
                "VERIFIED_BAR"
              ],
              [
                1,
                349.93,
                350.005,
                349.84,
                350.005,
                2567.0,
                "VERIFIED_BAR"
              ],
              [
                2,
                349.92,
                350.15,
                349.89,
                350.13,
                3319.0,
                "VERIFIED_BAR"
              ],
              [
                3,
                350.155,
                350.22,
                350.09,
                350.18,
                2477.0,
                "VERIFIED_BAR"
              ],
              [
                4,
                350.19,
                350.39,
                350.17,
                350.25,
                2728.0,
                "VERIFIED_BAR"
              ],
              [
                5,
                350.21,
                350.225,
                350.0,
                350.015,
                1212.0,
                "VERIFIED_BAR"
              ],
              [
                6,
                349.87,
                349.98,
                349.82,
                349.82,
                1640.0,
                "VERIFIED_BAR"
              ],
              [
                7,
                349.86,
                350.12,
                349.8,
                350.05,
                3317.0,
                "VERIFIED_BAR"
              ],
              [
                8,
                349.99,
                350.12,
                349.97,
                350.07,
                1788.0,
                "VERIFIED_BAR"
              ],
              [
                9,
                350.115,
                350.25,
                350.1,
                350.13,
                2283.0,
                "VERIFIED_BAR"
              ]
            ],
            "columns": [
              "minute_offset",
              "open",
              "high",
              "low",
              "close",
              "volume",
              "coverage"
            ],
            "feed": "iex",
            "window_end": "2026-11-23T19:27:00+00:00",
            "window_start": "2026-11-23T19:17:00+00:00",
            "windows": {
              "10m": {
                "close": 350.13,
                "open": 350.09,
                "range_bps": 16.85280928,
                "return": 0.0001142563341,
                "status": "OK",
                "volume": 23117.0
              },
              "5m": {
                "close": 350.13,
                "open": 350.21,
                "range_bps": 12.8494332,
                "return": -0.000228434368,
                "status": "OK",
                "volume": 10240.0
              }
            }
          },
          "version": "1.b12384d7"
        },
        "recent_range_bps_10m": {
          "age_s": 6.623372,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "2c4aa90a603d33bd730c709ea8db0fdd4b56a8a9232ce33bbd24f62d36f1a7c9",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:27:00+00:00",
            "window_start": "2026-11-23T19:17:00+00:00"
          },
          "record_hash": "0b1d7711fc85b1c92cb4aeb26623fc0e7f53204bf3b407f7075896c61a9e480c",
          "status": "OK",
          "v": 16.85280928,
          "version": "1.b7dd2e6e"
        },
        "recent_range_bps_5m": {
          "age_s": 6.623372,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "2c4aa90a603d33bd730c709ea8db0fdd4b56a8a9232ce33bbd24f62d36f1a7c9",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:27:00+00:00",
            "window_start": "2026-11-23T19:17:00+00:00"
          },
          "record_hash": "fd5f977215b819a92ad1e2b651ddd5596ac972200112dc519e59d186106a055c",
          "status": "OK",
          "v": 12.8494332,
          "version": "1.860a2856"
        },
        "recent_return_10m": {
          "age_s": 6.623372,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "2c4aa90a603d33bd730c709ea8db0fdd4b56a8a9232ce33bbd24f62d36f1a7c9",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:27:00+00:00",
            "window_start": "2026-11-23T19:17:00+00:00"
          },
          "record_hash": "e341b0046f68fd54ce6a464c0229ba2a17a474807bf3e3c601bfb9c483beb6ff",
          "status": "OK",
          "v": 0.0001142563341,
          "version": "1.03c04840"
        },
        "recent_return_5m": {
          "age_s": 6.623372,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "2c4aa90a603d33bd730c709ea8db0fdd4b56a8a9232ce33bbd24f62d36f1a7c9",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:27:00+00:00",
            "window_start": "2026-11-23T19:17:00+00:00"
          },
          "record_hash": "a6f158ed65cecef6e097926b6b5f061b7a3350ba7b5cbdc1f1bcc5349ab4dae0",
          "status": "OK",
          "v": -0.000228434368,
          "version": "1.a9090b46"
        },
        "recent_volume_10m": {
          "age_s": 6.623372,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "2c4aa90a603d33bd730c709ea8db0fdd4b56a8a9232ce33bbd24f62d36f1a7c9",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:27:00+00:00",
            "window_start": "2026-11-23T19:17:00+00:00"
          },
          "record_hash": "f5699629371f99660f3959e3d16b01ac1dfe64262e9cd9601d9cfcd3d9154b13",
          "status": "OK",
          "v": 23117.0,
          "version": "1.891ed5cd"
        },
        "recent_volume_5m": {
          "age_s": 6.623372,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "2c4aa90a603d33bd730c709ea8db0fdd4b56a8a9232ce33bbd24f62d36f1a7c9",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:27:00+00:00",
            "window_start": "2026-11-23T19:17:00+00:00"
          },
          "record_hash": "f7ce00b628f5be2e6b6ee38a02e42c1e2d5ce53cbf446d7109e7800ae5f24b6c",
          "status": "OK",
          "v": 10240.0,
          "version": "1.c7331f02"
        },
        "relstr_spy_60m": {
          "age_s": 726.623372,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "c1cd791cc13f0f3e6279dff9b3b656f5b714d841da983b113089ff312c037109",
          "status": "OK",
          "v": 0.002181476703,
          "version": "1.c04b464c"
        },
        "ret_15m": {
          "age_s": 726.623372,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "4db84c3a6361982d52b50d6a896b87146b4a399f28953e6b5dcfc6cf2a0ccb78",
          "status": "OK",
          "v": 0.002003262456,
          "version": "1.3fa23ddd"
        },
        "ret_1d": {
          "age_s": 726.623372,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "acd4850c7f353cd7d276491b7c7d3402308f47b10f57d00ddfcff5304f668541",
          "status": "OK",
          "v": -0.01628543191,
          "version": "1.b77eca69"
        },
        "ret_20d": {
          "age_s": 253626.6234,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "c1fd6c69e5212d8143db80ab0b65f04c3952518636216a6f65599b0cf9aa5d52",
          "status": "MISSING",
          "v": null,
          "version": "1.7d1f1942"
        },
        "ret_5d": {
          "age_s": 253626.6234,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "e279e1e5300466ccb81556a606d3565ef56efdfaa8086d105f074c583b7f1520",
          "status": "MISSING",
          "v": null,
          "version": "1.5d56db82"
        },
        "ret_5m": {
          "age_s": 726.623372,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "a7b31cbc3b119da60375c14d7ed81d10ad584fc692721b8d4a70dba781542d46",
          "status": "OK",
          "v": -0.0003426124197,
          "version": "1.c10a3b57"
        },
        "ret_60m": {
          "age_s": 726.623372,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "a0a65c45d781caf3b92f726bf804910735efc7a3cf98d78caf328c9b8bd1c3df",
          "status": "OK",
          "v": 0.0008289503773,
          "version": "1.6c49ff8f"
        },
        "rsi14": {
          "age_s": 253626.6234,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "017f8f44fae740e064f7cf662b6575f31515d3864f3470dc54f27aff186f4183",
          "status": "MISSING",
          "v": null,
          "version": "1.273a3a79"
        },
        "rsi14_15m": {
          "age_s": 726.623372,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "4bcd3b3bc68ef2a3b24588f819b282374f20d221da66c12182e92b5be0b02bf7",
          "status": "OK",
          "v": 60.34276894,
          "version": "1.f0b8fdaf"
        },
        "rvol_60m": {
          "age_s": 726.623372,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "663654db41b4a341972c58fcec80c259e623fe0a260658428ec0d74880dc4ed5",
          "status": "OK",
          "v": 0.003824626025,
          "version": "1.84c5ec7e"
        },
        "sellable_qty": {
          "age_s": 0.559092,
          "quality": {},
          "record_hash": "c4e25d752838c8bf2453cfb9f4f371e40882480807543114c3fa2b5470d56ebf",
          "status": "OK",
          "v": "0",
          "version": "1.9cbf72e4"
        },
        "sma20": {
          "age_s": 253626.6234,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "3e4d68b668f1fb60d01391d426d6383d59c5f1489b2c60d8b9677923330ea1e8",
          "status": "MISSING",
          "v": null,
          "version": "1.80f8a078"
        },
        "sma50": {
          "age_s": 253626.6234,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "1ae3948821d316103e37237b485a2f4802a168c7ba7718bcaa1f5cecba683bb4",
          "status": "MISSING",
          "v": null,
          "version": "1.3890c9d7"
        },
        "spread_bps": {
          "age_s": 1.536381,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "183ab355405f07c240adeee083d31b731ce053bc1f594d7747e9ee6ae943300d",
          "status": "OK",
          "v": 14.57330228,
          "version": "1.e2b080ab"
        },
        "trend_sma20_vs_sma50": {
          "age_s": 253626.6234,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "70f14cdb1db36bf9d9d5e86c7b54697ceba3042951e93e45270a4f006f4c91d8",
          "status": "MISSING",
          "v": null,
          "version": "1.84583425"
        },
        "unrealized_pnl_pct": {
          "age_s": 0.559092,
          "quality": {},
          "record_hash": "4a2479908abf243e0fa23cfc79ea5e82b907774ae618b21f00941871f5bf842f",
          "status": "OK",
          "v": 0,
          "version": "1.7c530604"
        },
        "vol_regime_ratio": {
          "age_s": 726.623372,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "f69948c83a718a0f906c505897d605f322619e1dd45efcd1c2352a1ca26ea237",
          "status": "OK",
          "v": 1.145507122,
          "version": "1.302e72c1"
        },
        "volume_z20": {
          "age_s": 253626.6234,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "68a11cf3df037bf35a94e13761dc1df96383de19536c6a0d960a52c5365f1e28",
          "status": "MISSING",
          "v": null,
          "version": "1.970d159b"
        },
        "volz_tod_15m": {
          "age_s": 726.623372,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "530fa07e56964d38a2104f4a1a003a9c21fe607e74364348f18f0dfb47005705",
          "status": "OK",
          "v": 0.1756718124,
          "version": "1.4315d547"
        },
        "vwap_dev_session": {
          "age_s": 726.623372,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "bb5028b28be03f1e618884072e463b229c51c30e133f0429f1dd3b67f1d7d458",
          "status": "OK",
          "v": 0.00329555456,
          "version": "1.b41de1ff"
        }
      }
    },
    "validation_policy": "scored-15m-plus-2m-v1"
  },
  "council_mode": "FULL",
  "chair": null,
  "skeptic_audit": null,
  "role_outputs": [
    {
      "role": "LIQUIDITY",
      "status": "FALLBACK_PROVIDER",
      "response": null,
      "error": "LLMError: openai_compat 429: Error code: 429 - Rate limit reached for model `openai/gpt-oss-20b` in organization `[REDACTED_PROVIDER_ORG]` service tier `on_demand` on tokens per minute (TPM): Limit 8000, Used 6680, Requested 2366. Please try again in 7.845s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing"
    },
    {
      "role": "PORTFOLIO",
      "status": "OK",
      "response": "{\"data_confidence\": \"HIGH\", \"role\": \"PORTFOLIO\", \"run_id\": \"8c98c900-7768-595c-889d-daaa27173a5b\", \"schema_version\": 2, \"source\": \"code\", \"symbols\": [{\"evidence\": [{\"band\": \"POSITIVE\", \"path\": \"portfolio.buying_power\"}, {\"band\": \"POSITIVE\", \"path\": \"portfolio.equity\"}, {\"band\": \"POSITIVE\", \"path\": \"symbols.AAPL.ret_15m\"}, {\"band\": \"POS_STRONG\", \"path\": \"symbols.AAPL.ema_gap_bps_15m\"}], \"gate\": {\"reasons\": [], \"size_multiplier\": 1.0, \"state\": \"PASS\"}, \"note\": \"Fresh paper account is flat. 15m momentum is positive.\", \"symbol\": \"AAPL\"}]}",
      "error": null
    },
    {
      "role": "REGIME",
      "status": "OK",
      "response": "{\"data_confidence\":\"HIGH\",\"risk_appetite\":\"NEUTRAL\",\"role\":\"REGIME\",\"run_id\":\"8c98c900-7768-595c-889d-daaa27173a5b\",\"schema_version\":2,\"source\":\"code\",\"symbols\":[{\"symbol\":\"AAPL\",\"note\":\"UPTREND regime and positive volatility suggest long\",\"evidence\":[{\"path\":\"market.regime_label\",\"band\":\"UPTREND\"},{\"path\":\"market.spy_vol_regime_ratio\",\"band\":\"POSITIVE\"}]}] }",
      "error": null
    },
    {
      "role": "TECHNICAL",
      "status": "OK",
      "response": "{\"data_confidence\": \"HIGH\", \"role\": \"TECHNICAL\", \"run_id\": \"8c98c900-7768-595c-889d-daaa27173a5b\", \"schema_version\": 2, \"source\": \"code\", \"symbols\": [{\"evidence\": [{\"band\": \"POS_STRONG\", \"path\": \"symbols.AAPL.ema_gap_bps_15m\"}, {\"band\": \"FIRM\", \"path\": \"symbols.AAPL.rsi14_15m\"}, {\"band\": \"FLAT\", \"path\": \"symbols.AAPL.recent_return_5m\"}, {\"band\": \"POSITIVE\", \"path\": \"symbols.AAPL.atr14_15m\"}, {\"band\": \"UNCONFIRMED\", \"path\": \"symbols.AAPL.intraday_setup_1m\"}], \"note\": \"Momentum established on 15m; 5m consolidation limits immediate entry edge.\", \"signal\": {\"confidence\": 0.65, \"horizon\": \"INTRADAY\", \"score\": 0.45, \"state\": \"SIGNAL\"}, \"symbol\": \"AAPL\"}]}",
      "error": null
    }
  ],
  "reason_codes": [
    "CODE_FLOOR_AFTER_PROVIDER_FAILURE"
  ],
  "notes": [
    "evidence_pack:fdb616b4b630d88b57fd7c25655870b9c194518ab862065822b65455c652116c",
    "council_run:8c98c900-7768-595c-889d-daaa27173a5b",
    "CODE_FLOOR_AFTER_PROVIDER_FAILURE"
  ],
  "error": null,
  "proposals_and_risk": []
}
```

</details>

### 14:28:10 ET · INCOMPLETE_PROVIDER

<details>
<summary>Recorded decision evidence</summary>

```json
{
  "decision_id": "56105b9c-a292-5a02-8494-28839baca31a",
  "inputs": {
    "as_of": "2026-11-23T19:28:07.451143Z",
    "regime": {
      "label": "uptrend"
    },
    "account": {
      "cash": 99803.39,
      "equity": 99803.39,
      "status": "ACTIVE",
      "account_id": "PAPER_ACCOUNT",
      "last_equity": 99803.39,
      "buying_power": 399213.56
    },
    "positions": [],
    "symbols": {
      "AAPL": {
        "mid": 350.26,
        "rsi14": null,
        "ret_1d": -0.0163,
        "ret_5d": null,
        "ret_20d": null,
        "atr14_pct": null,
        "price_vs_sma20": null,
        "trend_sma20_vs_sma50": null
      }
    }
  },
  "feature_evidence": {
    "account_ref": "PAPER_ACCOUNT",
    "as_of": "2026-11-23T19:28:07.451143+00:00",
    "availability": {
      "account": "fresh",
      "bars": "fresh",
      "calendar": "fresh",
      "news": "fresh",
      "ok_fraction_core_features": 1.0,
      "quotes": "fresh"
    },
    "bands_hash": "810517c6e124c7ebc23ca0ebce7ef7ba7cc66b30bc21cacc66c1a221174255d4",
    "feasibility": {
      "AAPL": {
        "can_buy": true,
        "can_buy_reasons": [],
        "can_sell": false,
        "can_sell_reasons": [
          "NO_SELLABLE_INVENTORY"
        ],
        "entry_window_open": true,
        "entry_window_reason": "",
        "held_qty": "0.0",
        "max_new_notional_usd": "2000.0",
        "sellable_qty": "0"
      }
    },
    "feature_slot": {
      "candles": {
        "AAPL|2026-11-23T19:13:00+00:00": "0e9a14fe740d7261310d963893297e28a03071451489fa33aded1b1a58acee67",
        "AAPL|2026-11-23T19:14:00+00:00": "d5bda39af69dcc53d4310b57aff3092db8a68054546c86a6b2df103d67ada5be",
        "AAPL|2026-11-23T19:15:00+00:00": "b0e6a6e9b9e4287c960f6ede77ad8f355970b7e8745dbe17c9339d2e3f12a605",
        "AAPL|2026-11-23T19:16:00+00:00": "69e7bfc090cee194af19c0acc6e8da6b7cf4c08443c52b952de98b8961d2ec67",
        "AAPL|2026-11-23T19:17:00+00:00": "c0a6e9630fa9f0d5027648d10559bb0be8e8caa0857d4fd8f17b11d4e3a85102",
        "AAPL|2026-11-23T19:18:00+00:00": "e862cb638fbc15b1a3f7b32db1c9e6d689acd1cd350079657d14e77d9e2c6479",
        "AAPL|2026-11-23T19:19:00+00:00": "e1937e8da6f995fc153f7e5e2ced98a01f960310d2ec214a17e4fb29a93c4146",
        "AAPL|2026-11-23T19:20:00+00:00": "70196363dae726bc8d352fd0e8cbb4b115e48fba11b5ee33c3817ea612c07c0f",
        "AAPL|2026-11-23T19:21:00+00:00": "6c6e08fc67af597579978fa03f3aaab5c3543c74e2011a7c2bce5c6d84460f57",
        "AAPL|2026-11-23T19:22:00+00:00": "2954cabc7ce7bf14ae0893aaac62bfaa70486fa0a68f63da27e0ee312728069a",
        "AAPL|2026-11-23T19:23:00+00:00": "2747e99b2df2570cd8f56be82b287c8ee7e009053a8933e9f3a90cd4d730228a",
        "AAPL|2026-11-23T19:24:00+00:00": "e1968a3f7d654002dbeeffb581d28f178a4778e7ef171a3abc48397e1eca10c1",
        "AAPL|2026-11-23T19:25:00+00:00": "f253416079d72d4e362e19307b75c172b7d2edb6ec453969e082d947eb75de1b",
        "AAPL|2026-11-23T19:26:00+00:00": "507b2e1c799046a50786ce4da765ff72ab0e23dce27aa1aa3bf3ee164f1c5e45",
        "AAPL|2026-11-23T19:27:00+00:00": "7b3543f4b74a7aa1b9442f5a5f6478df06cc1c1837cdd37538840b026f94764e",
        "SPY|2026-11-23T19:13:00+00:00": "2e0e8e4afe5f0552e559f4b57ab6f3a4af7aeed1c29df9bc0f8af4d993a0ec57",
        "SPY|2026-11-23T19:14:00+00:00": "1a003d29f3062e0e284c02aef050fc33aa9519155986beb8ffeabb18ba63d85e",
        "SPY|2026-11-23T19:15:00+00:00": "80f9ec707984fc74f8cb6dcebd3d845190206f212a6a7f5bbea8e7f0dfe5b85a",
        "SPY|2026-11-23T19:16:00+00:00": "bef27fecf6495d402ef4cf61ab22855605b7bf35ec2ee88c5fa240ececdeb144",
        "SPY|2026-11-23T19:17:00+00:00": "9267d9ec8514091597a775a9f11df8e6ba85ef1a765d8d7c6e0695a9d17e9d04",
        "SPY|2026-11-23T19:18:00+00:00": "9927bc665ca20d7006e3e28873737e2afb2679463ac195ed3f79e8551e2cdac5",
        "SPY|2026-11-23T19:19:00+00:00": "a3f91e79e75f72019e37a2793b54c01ee93403d8d9eafbd7f1eb0c5012b9b9c4",
        "SPY|2026-11-23T19:20:00+00:00": "e1ddcdb981d5c72dfaca25e1aaa8c1c27aef392260bc51ce1653cfd94d114f8f",
        "SPY|2026-11-23T19:21:00+00:00": "7a81b6670301657ad6b9cb0542ae646ff5785b4dbcb61c6b01fba0f60649ba1a",
        "SPY|2026-11-23T19:22:00+00:00": "39edefebca8c72b2135f978774a03b1d9775e0b17ef5fce054875b0dd7243c94",
        "SPY|2026-11-23T19:23:00+00:00": "def528246d2c8ce3e04085fb10ac15cd8741ba99e3ec0331c205f3d95712dca6",
        "SPY|2026-11-23T19:24:00+00:00": "e0825fbb3c82960924bc0a4fa93ab9a29cea452a13a515bbc433eb3e210b164a",
        "SPY|2026-11-23T19:25:00+00:00": "b6bef0076894b860d0d4faaa2427e9f8628a5c940154cdafae8278de8b4adb91",
        "SPY|2026-11-23T19:26:00+00:00": "e46bbe752653b237f9f0581eb791d9c099d17374e961e6008fc525d3a1b17355",
        "SPY|2026-11-23T19:27:00+00:00": "90924a4d25b101c0d29fa5761917dd436ab61fc5b1b1a804cb4a5a9e91ea54d4"
      },
      "close": "2026-11-23T19:28:00+00:00",
      "feed": "iex",
      "indicator_close": "2026-11-23T19:15:00+00:00",
      "indicator_input_hashes": {
        "AAPL": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
        "SPY": "647346c3307bab3f0ab75d294e9bf46773d6d42fa0676aa83ae2ca9d97b2b1eb"
      },
      "provisional": true,
      "records": {
        "market:market:breadth_above_ema21": "815832b01dd92f1e4451c79cf7955b56fb9737d65935bcfd1d3f33947ba7647c",
        "market:market:regime_label": "84f9e0050c68ef26c8fac251be3d1e9715d2043efbb27dc10dd36f804aed1906",
        "market:market:spy_ema_gap_bps_15m": "e1b77372b1441b383700bc1a58f75ce0bf7cd28628675e926f5fce53abbe5d18",
        "market:market:spy_ret_60m": "f3fa198bed0341ab216dc72c86dd0b05adff8dd9269c78c407b2af5f817a0cbc",
        "market:market:spy_vol_regime_ratio": "b07b4262604d3bc2518b9ac1b4047158f48b92cbb56c8695dd52e432e3de2c6f",
        "symbol:AAPL:adv_usd_20d": "e262af1fe6a7389e05b96a9a75b061c36d19abe6182590f4ef666a3c4147c5a3",
        "symbol:AAPL:atr14_15m": "4aa601dee2846211e120ee408a21949bef6a84cbeaeda8c8217242fa79357ada",
        "symbol:AAPL:atr14_1d": "9c0633de46b036a4fe93734a2e5dce61b7eff6bf36ec86c1bf294d9eeef95f85",
        "symbol:AAPL:atr14_pct": "1437ca280d0973889472dab3c5cb1b0006ef5ee631652a04bebaa9de603743bd",
        "symbol:AAPL:dist_hi_atr": "64a23a43f660b01c7dd2efe0a3acdd05c813b6681e6d732a8e16b75fb1390111",
        "symbol:AAPL:dist_lo_atr": "76b3b478f3d010617f7e23c25aa428e5bc112a119e7e0531fdfbf602f776f988",
        "symbol:AAPL:ema21_15m": "a4fce26cfa0190c94a7c7a20a720ebe23cabd0d7ebbcf6c266507d885b6c2172",
        "symbol:AAPL:ema9_15m": "0ad14ee0eb256fe1fe75965b26cc534f1723fca1dde7436232c23a087c645c3e",
        "symbol:AAPL:ema_gap_bps_15m": "e727bcc5189a91061e7df830a4b1a4c71755006275cd2c0a493816f0a95e827b",
        "symbol:AAPL:gap_open_pct": "fc5c7eeea7261785fc595b201a91df75e735719dbe6722604c7617e8524e7bc1",
        "symbol:AAPL:intraday_ret_1h": "bce1649c3f11808a59de7a9536a3a82e7ffdc25c2c36ac39b247c733fff4bd35",
        "symbol:AAPL:intraday_setup_1m": "38b1e50366d616c48d21ffa916fa24c7206729a22b3ed00247c05be23236f65b",
        "symbol:AAPL:last_close": "f064e1589fb929d983b820bbfcd86fd0141cb1044925ea55db4eb69a6c6b5ae1",
        "symbol:AAPL:macd_hist_15m": "5bdd527f747bb67db78b657003212927e07ba8624389f5381095f9a3f7a8d02f",
        "symbol:AAPL:price_vs_sma20": "a96d3080f2e95a5cc3b047ec495961d46cd4b318722c7eae4d719bfa2cc0f6e4",
        "symbol:AAPL:recent_price_10m": "8b50b19d1ea0b2035488b84b49e1633f488c7e5a27187d60ef02cd15f3be5c89",
        "symbol:AAPL:recent_range_bps_10m": "0786f5fc3591cdac951d71f3b52fa0e4defc46c3db3bffe0571af80d8a96cab5",
        "symbol:AAPL:recent_range_bps_5m": "2024dba6193fddb4271dd140328fa86ea64a91df114b6b32277bb566e4d1aad3",
        "symbol:AAPL:recent_return_10m": "fd94976fb45502476508025234f3f9ba4c47db40cebd1bd45a52820495a68b4c",
        "symbol:AAPL:recent_return_5m": "0d24df6b0a40efc2b3491130db1d43e81318433865307a6e0a3b3ce9c84b4b68",
        "symbol:AAPL:recent_volume_10m": "3687c7016f6ffe9c915a99594f5783b7a8db89d5a69f3dee46f1bc7229456050",
        "symbol:AAPL:recent_volume_5m": "a821f4ad6d9cf4c32395bc2292250c22317d2ee61528b4cd4a3e2a17d4abf18d",
        "symbol:AAPL:relstr_spy_60m": "1ffda6589e3d51b8c3b0a991db3fd65f2218091613b6ceea32cdff5baf45e432",
        "symbol:AAPL:ret_15m": "d56742c166d0b9ac5352a79c2fd464d26501642a09009d92c398be7988f38830",
        "symbol:AAPL:ret_1d": "acd4850c7f353cd7d276491b7c7d3402308f47b10f57d00ddfcff5304f668541",
        "symbol:AAPL:ret_20d": "c1fd6c69e5212d8143db80ab0b65f04c3952518636216a6f65599b0cf9aa5d52",
        "symbol:AAPL:ret_5d": "e279e1e5300466ccb81556a606d3565ef56efdfaa8086d105f074c583b7f1520",
        "symbol:AAPL:ret_5m": "fc2d2496e7b556e9c5c1bcb6c1d11872d764ce625f3fe47be3c4549119171446",
        "symbol:AAPL:ret_60m": "89f22487db1d1f7351544d04cba656431154242aea996fa510d209b4997f29d7",
        "symbol:AAPL:rsi14": "017f8f44fae740e064f7cf662b6575f31515d3864f3470dc54f27aff186f4183",
        "symbol:AAPL:rsi14_15m": "4bcd3b3bc68ef2a3b24588f819b282374f20d221da66c12182e92b5be0b02bf7",
        "symbol:AAPL:rvol_60m": "53dc34f83e30db5cbbe1a9627c311d3a07fbd96b41d71356c891f0ba9383e305",
        "symbol:AAPL:sma20": "3e4d68b668f1fb60d01391d426d6383d59c5f1489b2c60d8b9677923330ea1e8",
        "symbol:AAPL:sma50": "1ae3948821d316103e37237b485a2f4802a168c7ba7718bcaa1f5cecba683bb4",
        "symbol:AAPL:trend_sma20_vs_sma50": "70f14cdb1db36bf9d9d5e86c7b54697ceba3042951e93e45270a4f006f4c91d8",
        "symbol:AAPL:vol_regime_ratio": "18d7fce44dedd91f7e6233ec7bdfb2560cc2ca7fe70a0fd56912f52e301ba8fd",
        "symbol:AAPL:volume_z20": "68a11cf3df037bf35a94e13761dc1df96383de19536c6a0d960a52c5365f1e28",
        "symbol:AAPL:volz_tod_15m": "530fa07e56964d38a2104f4a1a003a9c21fe607e74364348f18f0dfb47005705",
        "symbol:AAPL:vwap_dev_session": "9aefd5af961cc44209bbb76226873c89ab2f471532835a5a8e98fb984d46ac7b",
        "symbol:SPY:adv_usd_20d": "7773f3a908eaf7c0e76c09e0281ebbcb8379cc49400a15772c1830a3b2c2f223",
        "symbol:SPY:atr14_15m": "fc718bba22a5db9dae206edea8233cf88df09c2e3062133470a7fe10f13267e2",
        "symbol:SPY:atr14_1d": "aaeea7993a9d2b21fb57bccbb0a7e2bae3ebb9bc634c0e9b485665df8a582439",
        "symbol:SPY:atr14_pct": "684fcce9d38b849dfc48ed4adf427634c6537f0b2d2dac4b1ac576ea747f9ea6",
        "symbol:SPY:dist_hi_atr": "be70b2d33e8aff52dc667295f50f1155d2107db7c79739d7695a6e17c8470a40",
        "symbol:SPY:dist_lo_atr": "78934b1afb3ff84cbcdf227091d0c994e2ceb84dec16d146bac89208eb4984f5",
        "symbol:SPY:ema21_15m": "d517509d58dbc26956d75d98347e4757713275e63455fdcc3c4422d256746a81",
        "symbol:SPY:ema9_15m": "097b3848e725e0d802d5441768fbf4db8207cbc178c1f391212f3cf9f984afeb",
        "symbol:SPY:ema_gap_bps_15m": "88de61b58000f6c109f37ccb1278278f5d8761b975c2735eb8c0fceb4c8789cc",
        "symbol:SPY:gap_open_pct": "7b8b09f491c0f145686f016617f1e339ec2c992d2d7f4b990a6f22f849fb269b",
        "symbol:SPY:intraday_ret_1h": "e04939fd11622d8ee6f45b21cbd60aaf479b74745d0331a0d031b34eb916d9e1",
        "symbol:SPY:intraday_setup_1m": "bf5dbf4c6409f1ec7136ae228c2448a16a1438dd01bd106160a86283f9eff4c7",
        "symbol:SPY:last_close": "7c75e5b2d0cbfa6053329d40230beafe8c50de8de09b8650fbc56c1f24fef8dd",
        "symbol:SPY:macd_hist_15m": "700faaf2b22ddb3d7a761119e621afb779197ee9e20002bf78ec397dc82b0426",
        "symbol:SPY:price_vs_sma20": "b3b5e555c37b8c77664c4514095e6ed44684e1cca73f30c87e244ef5047030fc",
        "symbol:SPY:recent_price_10m": "509249df4117b4a51555746a2b4dfbf6ea196a0fbcebab1fd12084a9555e87f6",
        "symbol:SPY:recent_range_bps_10m": "51c185b21f4894155a54097f79de258a082f72428b6e74576c2d16a1ed741f2d",
        "symbol:SPY:recent_range_bps_5m": "6c68706e9dd0f7932f6981bf6dbec374865561b74415dd71adc249eb10fcbaab",
        "symbol:SPY:recent_return_10m": "7a75d787252b0a2ebfcbcb6594961f6eea3dd20b85cf856179b86b91eb5fd235",
        "symbol:SPY:recent_return_5m": "abd584b2e7fce9179d75c482d4db740d31643c3eb9992eba96b29d829a995210",
        "symbol:SPY:recent_volume_10m": "94940a55a28a5e657cd29a7b6b5803af00c602141ae626ba1f466bef60decd94",
        "symbol:SPY:recent_volume_5m": "1184e72334468a82ce909a0eb9054c944438ceef17cfe41567db2cf04eb4ae99",
        "symbol:SPY:relstr_spy_60m": "f8e8a2c70f6861986994098551914f6ec7f583a6212d91b31d608d2906cc194a",
        "symbol:SPY:ret_15m": "9bb4c14d224f9a92752df09efaad2e39076930356ffb9a96f7f94a406c207b65",
        "symbol:SPY:ret_1d": "ddc0a11b63cc350e3081db1903dee6252ddb61770d13b16e856291026f52a3f3",
        "symbol:SPY:ret_20d": "ed1093e0aa5d6f66c95107ca1d6e0dc684f91a2b174538f28adce162fbc2a1c1",
        "symbol:SPY:ret_5d": "2298165b21cd162151213ae636f77a63a657bd096db984033682489995a3b1f5",
        "symbol:SPY:ret_5m": "eabbdb7981eddc2d7b947c2a7b4354c3020d4a80190cb5120b6cf78a116ac3da",
        "symbol:SPY:ret_60m": "3d14217d77db6ab626bfa512bfa82bb9d0ee3c695d50380f88173941b0eb45f2",
        "symbol:SPY:rsi14": "0896ff9e6527016820c4f3bacca566bf1825f6f67c30f9e930a11faa591958f6",
        "symbol:SPY:rsi14_15m": "f74fdb6b8a4dfd4479e87521b52a8e59d763710203d578d8f94a9675c6c9b551",
        "symbol:SPY:rvol_60m": "628e21796e4ec1ad3e2e979f5f1af0e540c7cf4e017dd1f3c408fb9b7219f5f4",
        "symbol:SPY:sma20": "d0283363840868af6910e903d8b6ce0fa7a2a5f15f1fe6688eee56a4e374e136",
        "symbol:SPY:sma50": "f0b368651bafa612c1bc158db1c24203caf7f9a36cde9c70a55ee93a918503d6",
        "symbol:SPY:trend_sma20_vs_sma50": "081b68b933591d41fda8068af744f2f85c5c3ab9eea6461455fa6828810c399c",
        "symbol:SPY:vol_regime_ratio": "12a543677a382cde4bd4379f7c4a51431335ebb47bb523d9401c8faf98474e18",
        "symbol:SPY:volume_z20": "b50666ce3e64dd1b2b048c991b636383b066dc0bdc8adda4888131d53fc369b6",
        "symbol:SPY:volz_tod_15m": "461ed44d456e55c2fcef586cde4f795fb112387dee57647074b82b07fa685f52",
        "symbol:SPY:vwap_dev_session": "302384f4748e74a5b3d82c8ad8f313bd941b91b60002840384994c457a6bfb21"
      },
      "symbols": [
        "AAPL",
        "SPY"
      ]
    },
    "horizons": {
      "AAPL": {
        "10m": {
          "age_s": 7.451143,
          "last_bar_end": "2026-11-23T19:28:00+00:00",
          "status": "OK"
        },
        "15m": {
          "age_s": 787.451143,
          "last_bar_end": "2026-11-23T19:15:00+00:00",
          "status": "OK"
        },
        "5m": {
          "age_s": 7.451143,
          "last_bar_end": "2026-11-23T19:28:00+00:00",
          "status": "OK"
        },
        "60m": {
          "age_s": 787.451143,
          "last_bar_end": "2026-11-23T19:15:00+00:00",
          "status": "OK"
        },
        "horizon_conflict": false
      }
    },
    "market": {
      "breadth_above_ema21": {
        "age_s": 787.451143,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "815832b01dd92f1e4451c79cf7955b56fb9737d65935bcfd1d3f33947ba7647c",
        "status": "OK",
        "v": 1.0,
        "version": "1.1dfe664d"
      },
      "minutes_to_close": {
        "age_s": 0.451254,
        "quality": {},
        "record_hash": "e573878fc6f4c8b9e5f6aa2ddec6c4422670b2dfd6121229e70eee22106627ff",
        "status": "OK",
        "v": 91.88333518,
        "version": "1.e79b1ead"
      },
      "regime_label": {
        "age_s": 787.451143,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "84f9e0050c68ef26c8fac251be3d1e9715d2043efbb27dc10dd36f804aed1906",
        "status": "OK",
        "v": "UPTREND",
        "version": "1.f8b361d7"
      },
      "session_phase": {
        "age_s": 0.451254,
        "quality": {},
        "record_hash": "82093667ea8e90a31a262aee98d03a76a518d45e9cdcd93e10f2a0fcc42a76af",
        "status": "OK",
        "v": "NORMAL",
        "version": "1.91f88fe8"
      },
      "spy_ema_gap_bps_15m": {
        "age_s": 787.451143,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "e1b77372b1441b383700bc1a58f75ce0bf7cd28628675e926f5fce53abbe5d18",
        "status": "OK",
        "v": 46.06234614,
        "version": "1.fda7da7a"
      },
      "spy_ret_60m": {
        "age_s": 787.451143,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "f3fa198bed0341ab216dc72c86dd0b05adff8dd9269c78c407b2af5f817a0cbc",
        "status": "OK",
        "v": -0.0006077264126,
        "version": "1.9feddbd1"
      },
      "spy_vol_regime_ratio": {
        "age_s": 787.451143,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "b07b4262604d3bc2518b9ac1b4047158f48b92cbb56c8695dd52e432e3de2c6f",
        "status": "OK",
        "v": 1.511830986,
        "version": "1.3b7257aa"
      }
    },
    "meta": {
      "news": {
        "AAPL": {
          "effective_weight": 0,
          "in_window": 0,
          "newest_age_min": null,
          "policy": "48h retained; per-article decay and minimum relevance; 4h count is descriptive",
          "poller_last_ok_age_s": 18.017358,
          "retrieved": 0,
          "selected": 0,
          "state": "QUIET",
          "window_min": 240
        }
      }
    },
    "news_blob_hash": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
    "news_context_blob_hash": "e3c60af9d95ebaf1f55c06533eacb239249be79ce6a8acc4ac91c59c6b87b05f",
    "portfolio": {
      "aggregate_cap_usd": {
        "age_s": 0.451254,
        "quality": {},
        "record_hash": "cf7f1ad694333133329cef4c78b7fbe0cc037150f5040e43050b0d6ffb9389d4",
        "status": "OK",
        "v": "49901.695",
        "version": "1.5b3d1daf"
      },
      "aggregate_headroom_usd": {
        "age_s": 0.451254,
        "quality": {},
        "record_hash": "eb66e3df697ba067416346175134cd357383d9d905bf37eaa71b6cfe1420ba6e",
        "status": "OK",
        "v": "49901.695",
        "version": "1.7f894fff"
      },
      "buying_power": {
        "age_s": 0.451254,
        "quality": {},
        "record_hash": "f9a6298284aea3bc4ba4d1ae78076baaac2f2a253422b5773a6af87ec0f7b5f6",
        "status": "OK",
        "v": "399213.56",
        "version": "1.74948dec"
      },
      "cash": {
        "age_s": 0.451254,
        "quality": {},
        "record_hash": "b2eb41e59bace1c7fbc71557af962ecc469ad15626adafe0a3cc7edb564e626b",
        "status": "OK",
        "v": "99803.39",
        "version": "1.b067f5e3"
      },
      "day_pnl_pct": {
        "age_s": 0.451254,
        "quality": {},
        "record_hash": "010d95525fb4276c456a3e86db7cd1ee043f93a55034624f98cec5b23f2f8144",
        "status": "OK",
        "v": "0",
        "version": "1.35e81852"
      },
      "drawdown_pct": {
        "age_s": 0.451254,
        "quality": {},
        "record_hash": "b13236d89abd513df3754d35f7e0771f358c45a35b605ca9d11e73dbfd9ff87f",
        "status": "MISSING",
        "v": null,
        "version": "1.19aac9ba"
      },
      "equity": {
        "age_s": 0.451254,
        "quality": {},
        "record_hash": "43a582436d8b955abeb7072f3c92ca38f1c8a53c3f339f80ba9c15dcc1e528f7",
        "status": "OK",
        "v": "99803.39",
        "version": "1.a2192616"
      },
      "gross_exposure_pct": {
        "age_s": 0.451254,
        "quality": {},
        "record_hash": "9612ab3803f0bf6cc17b13f8e191b784ceeb3a0ebff7361932162dda77e58f26",
        "status": "OK",
        "v": "0E+2",
        "version": "1.b82cc518"
      },
      "gross_exposure_usd": {
        "age_s": 0.451254,
        "quality": {},
        "record_hash": "dcb0bb80e5e0869f180b9977f6d5da330babe16207a9e4b3bcfa1d5101979214",
        "status": "OK",
        "v": "0",
        "version": "1.e4c8752b"
      },
      "last_reconcile_age_s": {
        "age_s": 0.451254,
        "quality": {},
        "record_hash": "dc7f5a1527cb607a9c347c125292435fd17dd2a4b3a642b03ace0a16221e421a",
        "status": "OK",
        "v": 0,
        "version": "1.5ed0382f"
      },
      "open_buy_notional_usd": {
        "age_s": 0.451254,
        "quality": {},
        "record_hash": "2a3c4ddcd491d4e61c8d861da8d27ab2136aa9801a646f2d3a322f08512841ff",
        "status": "OK",
        "v": "0",
        "version": "1.0bd0ead1"
      },
      "open_orders": {
        "age_s": 0.451254,
        "quality": {},
        "record_hash": "21b2530d46dbe3fc5c208ef56ad218df91ccd04cd14839badb8108494988d764",
        "status": "OK",
        "v": [],
        "version": "1.1cf37cbf"
      },
      "open_orders_count": {
        "age_s": 0.451254,
        "quality": {},
        "record_hash": "302210aed50dee8e259b0e1f44e4e4ae2c4d01ace0aa52694269d2262cb5aa6c",
        "status": "OK",
        "v": 0,
        "version": "1.1db4227a"
      },
      "pending_reserved_usd": {
        "age_s": 0.451254,
        "quality": {},
        "record_hash": "1d2645a87e17418c27c6f2488471ac3b72db50d0b243f8a6cc074b04e6be1cd7",
        "status": "OK",
        "v": "0",
        "version": "1.1c3e9604"
      },
      "positions": {
        "age_s": 0.451254,
        "quality": {},
        "record_hash": "5d3d0730d473ac0dd6105cc3b0452b7f927bbbbdee52f3648258832760b9b3b1",
        "status": "OK",
        "v": [],
        "version": "1.c3284657"
      }
    },
    "registry_hash": "0fd3271269748046863b2f0558e45e2c333bb352eccc9899b7ff42277c8386fc",
    "schema_version": 1,
    "symbols": {
      "AAPL": {
        "adv_usd_20d": {
          "age_s": 253687.4511,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "e262af1fe6a7389e05b96a9a75b061c36d19abe6182590f4ef666a3c4147c5a3",
          "status": "OK",
          "v": 525559715.8,
          "version": "1.04f5e91f"
        },
        "ask_px": {
          "age_s": 1.754249,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "ce276cf1b4feb7b5c942dd542a0c63642bea7b11dbf94d0033c2d3a884c13b96",
          "status": "OK",
          "v": 350.29,
          "version": "1.d21cdd09"
        },
        "atr14_15m": {
          "age_s": 787.451143,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "4aa601dee2846211e120ee408a21949bef6a84cbeaeda8c8217242fa79357ada",
          "status": "OK",
          "v": 1.466657912,
          "version": "1.0cd14e73"
        },
        "atr14_1d": {
          "age_s": 253687.4511,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "9c0633de46b036a4fe93734a2e5dce61b7eff6bf36ec86c1bf294d9eeef95f85",
          "status": "MISSING",
          "v": null,
          "version": "1.65e38f4c"
        },
        "atr14_pct": {
          "age_s": 253687.4511,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "1437ca280d0973889472dab3c5cb1b0006ef5ee631652a04bebaa9de603743bd",
          "status": "MISSING",
          "v": null,
          "version": "1.87450ee9"
        },
        "bid_px": {
          "age_s": 1.754249,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "08712149ee35ac5372e850b395128368e4781f5acbdb65ca58838fa5ce1fadc2",
          "status": "OK",
          "v": 350.23,
          "version": "1.149628cd"
        },
        "dist_hi_atr": {
          "age_s": 787.451143,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "64a23a43f660b01c7dd2efe0a3acdd05c813b6681e6d732a8e16b75fb1390111",
          "status": "OK",
          "v": -1.588645846,
          "version": "1.913ffc4a"
        },
        "dist_lo_atr": {
          "age_s": 787.451143,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "76b3b478f3d010617f7e23c25aa428e5bc112a119e7e0531fdfbf602f776f988",
          "status": "OK",
          "v": 3.238655695,
          "version": "1.79ba4c70"
        },
        "ema21_15m": {
          "age_s": 787.451143,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "a4fce26cfa0190c94a7c7a20a720ebe23cabd0d7ebbcf6c266507d885b6c2172",
          "status": "OK",
          "v": 348.3552073,
          "version": "1.bfcac61e"
        },
        "ema9_15m": {
          "age_s": 787.451143,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "0ad14ee0eb256fe1fe75965b26cc534f1723fca1dde7436232c23a087c645c3e",
          "status": "OK",
          "v": 348.9848916,
          "version": "1.81255de8"
        },
        "ema_gap_bps_15m": {
          "age_s": 787.451143,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "e727bcc5189a91061e7df830a4b1a4c71755006275cd2c0a493816f0a95e827b",
          "status": "OK",
          "v": 18.07592592,
          "version": "1.d4519f3c"
        },
        "gap_open_pct": {
          "age_s": 787.451143,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "fc5c7eeea7261785fc595b201a91df75e735719dbe6722604c7617e8524e7bc1",
          "status": "MISSING",
          "v": null,
          "version": "1.27438d4d"
        },
        "halted": {
          "age_s": 0.451254,
          "quality": {},
          "record_hash": "97262eb65107c466a5513528855e71d378d6b9f080d34cba994fcb68c45d5717",
          "status": "OK",
          "v": false,
          "version": "1.22c5cf87"
        },
        "held_minutes": {
          "age_s": 0.451254,
          "quality": {},
          "record_hash": "27903f3f3ce0cb1a5925031246d00fe9c686578c88e596df4cdb27164bff6cda",
          "status": "MISSING",
          "v": null,
          "version": "1.de6ed6d3"
        },
        "intraday_ret_1h": {
          "age_s": 787.451143,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "bce1649c3f11808a59de7a9536a3a82e7ffdc25c2c36ac39b247c733fff4bd35",
          "status": "OK",
          "v": 0.001716689079,
          "version": "1.c3bb7751"
        },
        "intraday_setup_1m": {
          "age_s": 7.451143,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "17767e2f4b1c7785d0c55905f9270fe6f9741b276b334e104f7daaba040a7ff6",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:28:00+00:00",
            "window_start": "2026-11-23T19:18:00+00:00"
          },
          "record_hash": "38b1e50366d616c48d21ffa916fa24c7206729a22b3ed00247c05be23236f65b",
          "status": "OK",
          "v": {
            "confirmation": "UNCONFIRMED",
            "pattern": "DOJI",
            "prior_trend": "FLAT",
            "range_break": "INSIDE",
            "range_ceiling": 350.39,
            "range_floor": 349.8,
            "setup_minute": 8,
            "volume_ratio": 0.8886
          },
          "version": "1.2a1f51e0"
        },
        "last_close": {
          "age_s": 253687.4511,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "f064e1589fb929d983b820bbfcd86fd0141cb1044925ea55db4eb69a6c6b5ae1",
          "status": "MISSING",
          "v": null,
          "version": "1.f2485fc2"
        },
        "luld_active": {
          "age_s": 0.451254,
          "quality": {},
          "record_hash": "69a8f2a46763ac0f19552e8a13a7859189b74356b4a6295a78ef2b2b250cde49",
          "status": "MISSING",
          "v": null,
          "version": "1.84a715b2"
        },
        "macd_hist_15m": {
          "age_s": 787.451143,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "5bdd527f747bb67db78b657003212927e07ba8624389f5381095f9a3f7a8d02f",
          "status": "OK",
          "v": 0.08324749226,
          "version": "1.391617c8"
        },
        "mid_px": {
          "age_s": 1.754249,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "f68e40b92f3a33a149ff9246e298dbd587ad0ea18dc9870828a205cfa6cab57e",
          "status": "OK",
          "v": 350.26,
          "version": "1.d567a349"
        },
        "news_age_min_latest": {
          "age_s": 18.017358,
          "quality": {},
          "record_hash": "1861ada0777a911d6fce52dee0e703d7461cf095d5b74d0055bba8a0d8781204",
          "status": "MISSING",
          "v": null,
          "version": "1.d0f79dc8"
        },
        "news_confirmed": {
          "age_s": 0,
          "quality": {
            "source": "stored news and pinned price features"
          },
          "status": "OK",
          "v": false,
          "version": "news-confirmation-v2"
        },
        "news_count_1h": {
          "age_s": 18.017358,
          "quality": {},
          "record_hash": "40410618465d9e30914443799cd3430cf2b8ac4c5fd9fcdde150942c92c726d4",
          "status": "OK",
          "v": 0,
          "version": "1.0c9362fe"
        },
        "news_count_48h": {
          "age_s": 18.017358,
          "quality": {
            "as_of": "2026-11-23T19:28:07.451143+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 0,
          "version": "news-context-v2"
        },
        "news_count_4h": {
          "age_s": 18.017358,
          "quality": {
            "as_of": "2026-11-23T19:28:07.451143+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 0,
          "version": "news-context-v2"
        },
        "news_effective_sentiment": {
          "age_s": 0,
          "quality": {
            "selected": 0,
            "source": "decayed stored article metadata"
          },
          "status": "MISSING",
          "v": 0.0,
          "version": "news-decay-v2"
        },
        "news_event_flags_4h": {
          "age_s": 18.017358,
          "quality": {},
          "record_hash": "a1a63ff8bc053ed04ee8466a65164630d043f4374f2094f7d47406402363f4af",
          "status": "OK",
          "v": [],
          "version": "1.0b5a8a44"
        },
        "news_max_materiality_4h": {
          "age_s": 18.017358,
          "quality": {},
          "record_hash": "420ad887c46db8c77413df145d6fadad3ac81b0c449476db16718847552f48b7",
          "status": "OK",
          "v": 0,
          "version": "1.9c45e9b4"
        },
        "news_newest_age_min": {
          "age_s": 18.017358,
          "quality": {
            "as_of": "2026-11-23T19:28:07.451143+00:00",
            "source": "stored articles"
          },
          "status": "MISSING",
          "v": null,
          "version": "news-context-v2"
        },
        "news_novelty_max_4h": {
          "age_s": 18.017358,
          "quality": {},
          "record_hash": "7719838219dd72bb014c584353bbac0cf04f279046663fa7ffae7a69f6eb2fd8",
          "status": "OK",
          "v": false,
          "version": "1.15ceb7bf"
        },
        "news_sent_ewm_240m": {
          "age_s": 18.017358,
          "quality": {},
          "record_hash": "80ab3dcc2085d48be980e013627726940e3a03a917ba14f1b55d85b862b6a2c9",
          "status": "OK",
          "v": 0,
          "version": "1.9cad993f"
        },
        "news_sent_ewm_60m": {
          "age_s": 18.017358,
          "quality": {},
          "record_hash": "c85bd3b3dfbbc70b7f7331f2da00ff3f8c514390273334e3334be8913a3f6e2c",
          "status": "OK",
          "v": 0,
          "version": "1.74ab70c1"
        },
        "news_source_div_4h": {
          "age_s": 18.017358,
          "quality": {},
          "record_hash": "276a2b64218134e3e088e0a47761c817088cf06ac14a84d3c895fbc7d7bccb6d",
          "status": "OK",
          "v": 0,
          "version": "1.6fd469c4"
        },
        "position_qty": {
          "age_s": 0.451254,
          "quality": {},
          "record_hash": "165478f97db829724e13da1c1e774fae1189515e05a65a366ccb13b8318fd02d",
          "status": "OK",
          "v": "0",
          "version": "1.3a512120"
        },
        "position_value_usd": {
          "age_s": 0.451254,
          "quality": {},
          "record_hash": "e2ba7cf7f1bda9ae877fb6b696c91c31814487a10bba98826459156267552795",
          "status": "OK",
          "v": "0",
          "version": "1.9100bec4"
        },
        "price_vs_sma20": {
          "age_s": 253687.4511,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "a96d3080f2e95a5cc3b047ec495961d46cd4b318722c7eae4d719bfa2cc0f6e4",
          "status": "MISSING",
          "v": null,
          "version": "1.a986b9cc"
        },
        "recent_price_10m": {
          "age_s": 7.451143,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "17767e2f4b1c7785d0c55905f9270fe6f9741b276b334e104f7daaba040a7ff6",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:28:00+00:00",
            "window_start": "2026-11-23T19:18:00+00:00"
          },
          "record_hash": "8b50b19d1ea0b2035488b84b49e1633f488c7e5a27187d60ef02cd15f3be5c89",
          "status": "OK",
          "v": {
            "candles": [
              [
                0,
                349.93,
                350.005,
                349.84,
                350.005,
                2567.0,
                "VERIFIED_BAR"
              ],
              [
                1,
                349.92,
                350.15,
                349.89,
                350.13,
                3319.0,
                "VERIFIED_BAR"
              ],
              [
                2,
                350.155,
                350.22,
                350.09,
                350.18,
                2477.0,
                "VERIFIED_BAR"
              ],
              [
                3,
                350.19,
                350.39,
                350.17,
                350.25,
                2728.0,
                "VERIFIED_BAR"
              ],
              [
                4,
                350.21,
                350.225,
                350.0,
                350.015,
                1212.0,
                "VERIFIED_BAR"
              ],
              [
                5,
                349.87,
                349.98,
                349.82,
                349.82,
                1640.0,
                "VERIFIED_BAR"
              ],
              [
                6,
                349.86,
                350.12,
                349.8,
                350.05,
                3317.0,
                "VERIFIED_BAR"
              ],
              [
                7,
                349.99,
                350.12,
                349.97,
                350.07,
                1788.0,
                "VERIFIED_BAR"
              ],
              [
                8,
                350.115,
                350.25,
                350.1,
                350.13,
                2283.0,
                "VERIFIED_BAR"
              ],
              [
                9,
                350.16,
                350.285,
                350.15,
                350.27,
                2201.0,
                "VERIFIED_BAR"
              ]
            ],
            "columns": [
              "minute_offset",
              "open",
              "high",
              "low",
              "close",
              "volume",
              "coverage"
            ],
            "feed": "iex",
            "window_end": "2026-11-23T19:28:00+00:00",
            "window_start": "2026-11-23T19:18:00+00:00",
            "windows": {
              "10m": {
                "close": 350.27,
                "open": 349.93,
                "range_bps": 16.86051496,
                "return": 0.000971622896,
                "status": "OK",
                "volume": 23532.0
              },
              "5m": {
                "close": 350.27,
                "open": 349.87,
                "range_bps": 13.86229171,
                "return": 0.00114328179,
                "status": "OK",
                "volume": 11229.0
              }
            }
          },
          "version": "1.b12384d7"
        },
        "recent_range_bps_10m": {
          "age_s": 7.451143,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "17767e2f4b1c7785d0c55905f9270fe6f9741b276b334e104f7daaba040a7ff6",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:28:00+00:00",
            "window_start": "2026-11-23T19:18:00+00:00"
          },
          "record_hash": "0786f5fc3591cdac951d71f3b52fa0e4defc46c3db3bffe0571af80d8a96cab5",
          "status": "OK",
          "v": 16.86051496,
          "version": "1.b7dd2e6e"
        },
        "recent_range_bps_5m": {
          "age_s": 7.451143,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "17767e2f4b1c7785d0c55905f9270fe6f9741b276b334e104f7daaba040a7ff6",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:28:00+00:00",
            "window_start": "2026-11-23T19:18:00+00:00"
          },
          "record_hash": "2024dba6193fddb4271dd140328fa86ea64a91df114b6b32277bb566e4d1aad3",
          "status": "OK",
          "v": 13.86229171,
          "version": "1.860a2856"
        },
        "recent_return_10m": {
          "age_s": 7.451143,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "17767e2f4b1c7785d0c55905f9270fe6f9741b276b334e104f7daaba040a7ff6",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:28:00+00:00",
            "window_start": "2026-11-23T19:18:00+00:00"
          },
          "record_hash": "fd94976fb45502476508025234f3f9ba4c47db40cebd1bd45a52820495a68b4c",
          "status": "OK",
          "v": 0.000971622896,
          "version": "1.03c04840"
        },
        "recent_return_5m": {
          "age_s": 7.451143,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "17767e2f4b1c7785d0c55905f9270fe6f9741b276b334e104f7daaba040a7ff6",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:28:00+00:00",
            "window_start": "2026-11-23T19:18:00+00:00"
          },
          "record_hash": "0d24df6b0a40efc2b3491130db1d43e81318433865307a6e0a3b3ce9c84b4b68",
          "status": "OK",
          "v": 0.00114328179,
          "version": "1.a9090b46"
        },
        "recent_volume_10m": {
          "age_s": 7.451143,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "17767e2f4b1c7785d0c55905f9270fe6f9741b276b334e104f7daaba040a7ff6",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:28:00+00:00",
            "window_start": "2026-11-23T19:18:00+00:00"
          },
          "record_hash": "3687c7016f6ffe9c915a99594f5783b7a8db89d5a69f3dee46f1bc7229456050",
          "status": "OK",
          "v": 23532.0,
          "version": "1.891ed5cd"
        },
        "recent_volume_5m": {
          "age_s": 7.451143,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "17767e2f4b1c7785d0c55905f9270fe6f9741b276b334e104f7daaba040a7ff6",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:28:00+00:00",
            "window_start": "2026-11-23T19:18:00+00:00"
          },
          "record_hash": "a821f4ad6d9cf4c32395bc2292250c22317d2ee61528b4cd4a3e2a17d4abf18d",
          "status": "OK",
          "v": 11229.0,
          "version": "1.c7331f02"
        },
        "relstr_spy_60m": {
          "age_s": 787.451143,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "1ffda6589e3d51b8c3b0a991db3fd65f2218091613b6ceea32cdff5baf45e432",
          "status": "OK",
          "v": 0.002552862143,
          "version": "1.c04b464c"
        },
        "ret_15m": {
          "age_s": 787.451143,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "d56742c166d0b9ac5352a79c2fd464d26501642a09009d92c398be7988f38830",
          "status": "OK",
          "v": 0.001458142726,
          "version": "1.3fa23ddd"
        },
        "ret_1d": {
          "age_s": 787.451143,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "acd4850c7f353cd7d276491b7c7d3402308f47b10f57d00ddfcff5304f668541",
          "status": "OK",
          "v": -0.01628543191,
          "version": "1.b77eca69"
        },
        "ret_20d": {
          "age_s": 253687.4511,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "c1fd6c69e5212d8143db80ab0b65f04c3952518636216a6f65599b0cf9aa5d52",
          "status": "MISSING",
          "v": null,
          "version": "1.7d1f1942"
        },
        "ret_5d": {
          "age_s": 253687.4511,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "e279e1e5300466ccb81556a606d3565ef56efdfaa8086d105f074c583b7f1520",
          "status": "MISSING",
          "v": null,
          "version": "1.5d56db82"
        },
        "ret_5m": {
          "age_s": 787.451143,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "fc2d2496e7b556e9c5c1bcb6c1d11872d764ce625f3fe47be3c4549119171446",
          "status": "OK",
          "v": 0.0007285402054,
          "version": "1.c10a3b57"
        },
        "ret_60m": {
          "age_s": 787.451143,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "89f22487db1d1f7351544d04cba656431154242aea996fa510d209b4997f29d7",
          "status": "OK",
          "v": 0.00194513573,
          "version": "1.6c49ff8f"
        },
        "rsi14": {
          "age_s": 253687.4511,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "017f8f44fae740e064f7cf662b6575f31515d3864f3470dc54f27aff186f4183",
          "status": "MISSING",
          "v": null,
          "version": "1.273a3a79"
        },
        "rsi14_15m": {
          "age_s": 787.451143,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "4bcd3b3bc68ef2a3b24588f819b282374f20d221da66c12182e92b5be0b02bf7",
          "status": "OK",
          "v": 60.34276894,
          "version": "1.f0b8fdaf"
        },
        "rvol_60m": {
          "age_s": 787.451143,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "53dc34f83e30db5cbbe1a9627c311d3a07fbd96b41d71356c891f0ba9383e305",
          "status": "OK",
          "v": 0.003778488397,
          "version": "1.84c5ec7e"
        },
        "sellable_qty": {
          "age_s": 0.451254,
          "quality": {},
          "record_hash": "d464b3a0080455d86bfec746996767989b293579315ec50c68cf0b949edffc42",
          "status": "OK",
          "v": "0",
          "version": "1.9cbf72e4"
        },
        "sma20": {
          "age_s": 253687.4511,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "3e4d68b668f1fb60d01391d426d6383d59c5f1489b2c60d8b9677923330ea1e8",
          "status": "MISSING",
          "v": null,
          "version": "1.80f8a078"
        },
        "sma50": {
          "age_s": 253687.4511,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "1ae3948821d316103e37237b485a2f4802a168c7ba7718bcaa1f5cecba683bb4",
          "status": "MISSING",
          "v": null,
          "version": "1.3890c9d7"
        },
        "spread_bps": {
          "age_s": 1.754249,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "f56d88f04bd44ce911ff83f6b1179848fc32a162db24c282d2f035190da88462",
          "status": "OK",
          "v": 1.71301319,
          "version": "1.e2b080ab"
        },
        "trend_sma20_vs_sma50": {
          "age_s": 253687.4511,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "70f14cdb1db36bf9d9d5e86c7b54697ceba3042951e93e45270a4f006f4c91d8",
          "status": "MISSING",
          "v": null,
          "version": "1.84583425"
        },
        "unrealized_pnl_pct": {
          "age_s": 0.451254,
          "quality": {},
          "record_hash": "5f5466739256ab04c034f32c8fd986160824704ac7aa5a333b5ee3fd0e44e7f0",
          "status": "OK",
          "v": 0,
          "version": "1.7c530604"
        },
        "vol_regime_ratio": {
          "age_s": 787.451143,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "18d7fce44dedd91f7e6233ec7bdfb2560cc2ca7fe70a0fd56912f52e301ba8fd",
          "status": "OK",
          "v": 1.127929869,
          "version": "1.302e72c1"
        },
        "volume_z20": {
          "age_s": 253687.4511,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "68a11cf3df037bf35a94e13761dc1df96383de19536c6a0d960a52c5365f1e28",
          "status": "MISSING",
          "v": null,
          "version": "1.970d159b"
        },
        "volz_tod_15m": {
          "age_s": 787.451143,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "530fa07e56964d38a2104f4a1a003a9c21fe607e74364348f18f0dfb47005705",
          "status": "OK",
          "v": 0.1756718124,
          "version": "1.4315d547"
        },
        "vwap_dev_session": {
          "age_s": 787.451143,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "9aefd5af961cc44209bbb76226873c89ab2f471532835a5a8e98fb984d46ac7b",
          "status": "OK",
          "v": 0.003690702048,
          "version": "1.b41de1ff"
        }
      }
    },
    "validation_policy": "scored-15m-plus-2m-v1"
  },
  "council_mode": "FULL",
  "chair": {
    "note": "Entry window open, buying power ample, no existing position; expected net profit exceeds entry costs.",
    "role": "CHAIR",
    "run_id": "56105b9c-a292-5a02-8494-28839baca31a",
    "candidates": [
      {
        "note": "Positive technical score, UPTREND regime, tight spread support entry.",
        "action": "buy",
        "symbol": "AAPL",
        "conviction": 0.67,
        "cited_roles": [
          "TECHNICAL",
          "REGIME",
          "LIQUIDITY"
        ]
      }
    ],
    "schema_version": 2
  },
  "skeptic_audit": {
    "error": "LLMError: openai_compat 429: Error code: 429 - Rate limit reached for model `openai/gpt-oss-20b` in organization `[REDACTED_PROVIDER_ORG]` service tier `on_demand` on tokens per minute (TPM): Limit 8000, Used 6427, Requested 4036. Please try again in 18.4725s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing",
    "tokens": 0,
    "attempts": 1,
    "fallback": "PROVIDER",
    "phase_start_ms": 3137,
    "provider_errors": [
      "openai_compat 429: Error code: 429 - Rate limit reached for model `openai/gpt-oss-20b` in organization `[REDACTED_PROVIDER_ORG]` service tier `on_demand` on tokens per minute (TPM): Limit 8000, Used 6427, Requested 4036. Please try again in 18.4725s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing"
    ],
    "repair_attempts": 0
  },
  "role_outputs": [
    {
      "role": "CHAIR",
      "status": "OK",
      "response": "{\n  \"schema_version\": 2,\n  \"run_id\": \"56105b9c-a292-5a02-8494-28839baca31a\",\n  \"role\": \"CHAIR\",\n  \"candidates\": [\n    {\n      \"symbol\": \"AAPL\",\n      \"action\": \"buy\",\n      \"conviction\": 0.67,\n      \"cited_roles\": [\"TECHNICAL\", \"REGIME\", \"LIQUIDITY\"],\n      \"note\": \"Positive technical score, UPTREND regime, tight spread support entry.\"\n    }\n  ],\n  \"note\": \"Entry window open, buying power ample, no existing position; expected net profit exceeds entry costs.\"\n}",
      "error": null
    },
    {
      "role": "LIQUIDITY",
      "status": "OK",
      "response": "{\"schema_version\":2,\"run_id\":\"56105b9c-a292-5a02-8494-28839baca31a\",\"source\":\"code\",\"data_confidence\":\"HIGH\",\"role\":\"LIQUIDITY\",\"symbols\":[{\"symbol\":\"AAPL\",\"evidence\":[{\"path\":\"symbols.AAPL.spread_bps\",\"band\":\"TIGHT\"},{\"path\":\"symbols.AAPL.mid_px\",\"band\":\"POSITIVE\"},{\"path\":\"symbols.AAPL.volz_tod_15m\",\"band\":\"NORMAL\"}],\"gate\":{\"state\":\"PASS\",\"size_multiplier\":1.0,\"reasons\":[]},\"note\":\"deterministic code assessment\"}]}",
      "error": null
    },
    {
      "role": "PORTFOLIO",
      "status": "OK",
      "response": "{\"data_confidence\": \"HIGH\", \"role\": \"PORTFOLIO\", \"run_id\": \"56105b9c-a292-5a02-8494-28839baca31a\", \"schema_version\": 2, \"source\": \"code\", \"symbols\": [{\"evidence\": [{\"band\": \"POSITIVE\", \"path\": \"portfolio.equity\"}, {\"band\": \"POSITIVE\", \"path\": \"portfolio.buying_power\"}, {\"band\": \"ZERO\", \"path\": \"symbols.AAPL.position_qty\"}], \"gate\": {\"reasons\": [], \"size_multiplier\": 1.0, \"state\": \"PASS\"}, \"note\": \"Bought position with ample headroom and fresh data.\", \"symbol\": \"AAPL\"}]}",
      "error": null
    },
    {
      "role": "REGIME",
      "status": "OK",
      "response": "{\"data_confidence\":\"HIGH\",\"risk_appetite\":\"NEUTRAL\",\"role\":\"REGIME\",\"run_id\":\"56105b9c-a292-5a02-8494-28839baca31a\",\"schema_version\":2,\"source\":\"code\",\"symbols\":[{\"symbol\":\"AAPL\",\"evidence\":[{\"path\":\"market.regime_label\",\"band\":\"UPTREND\"},{\"path\":\"market.spy_vol_regime_ratio\",\"band\":\"POSITIVE\"}],\"note\":\"deterministic code assessment\"}]}",
      "error": null
    },
    {
      "role": "SKEPTIC",
      "status": "FALLBACK_PROVIDER",
      "response": null,
      "error": "LLMError: openai_compat 429: Error code: 429 - Rate limit reached for model `openai/gpt-oss-20b` in organization `[REDACTED_PROVIDER_ORG]` service tier `on_demand` on tokens per minute (TPM): Limit 8000, Used 6427, Requested 4036. Please try again in 18.4725s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing"
    },
    {
      "role": "TECHNICAL",
      "status": "OK",
      "response": "{\"data_confidence\": \"HIGH\", \"role\": \"TECHNICAL\", \"run_id\": \"56105b9c-a292-5a02-8494-28839baca31a\", \"schema_version\": 2, \"source\": \"code\", \"symbols\": [{\"evidence\": [{\"band\": \"POS_STRONG\", \"path\": \"symbols.AAPL.ema_gap_bps_15m\"}, {\"band\": \"FIRM\", \"path\": \"symbols.AAPL.rsi14_15m\"}, {\"band\": \"POS\", \"path\": \"symbols.AAPL.recent_return_5m\"}, {\"band\": \"POSITIVE\", \"path\": \"symbols.AAPL.atr14_15m\"}, {\"band\": \"UNCONFIRMED\", \"path\": \"symbols.AAPL.intraday_setup_1m\"}], \"note\": \"Floor maintained; 1m Doji remains unconfirmed.\", \"signal\": {\"confidence\": 0.8, \"horizon\": \"INTRADAY\", \"score\": 0.67065016, \"state\": \"SIGNAL\"}, \"symbol\": \"AAPL\"}]}",
      "error": null
    }
  ],
  "reason_codes": [
    "SKEPTIC_UNAVAILABLE"
  ],
  "notes": [
    "evidence_pack:69069cd84c85e368b5297f7de26909d835993f844bdb0fec6bf0a04c95083363",
    "council_run:56105b9c-a292-5a02-8494-28839baca31a",
    "SKEPTIC_UNAVAILABLE"
  ],
  "error": null,
  "proposals_and_risk": []
}
```

</details>

### 14:29:07 ET · DECIDED_TRADE

<details>
<summary>Recorded decision evidence</summary>

```json
{
  "decision_id": "4e0def5e-638a-53ed-b8ec-c1989778a527",
  "inputs": {
    "as_of": "2026-11-23T19:29:03.154787Z",
    "regime": {
      "label": "uptrend"
    },
    "account": {
      "cash": 99803.39,
      "equity": 99803.39,
      "status": "ACTIVE",
      "account_id": "PAPER_ACCOUNT",
      "last_equity": 99803.39,
      "buying_power": 399213.56
    },
    "positions": [],
    "symbols": {
      "AAPL": {
        "mid": 350.185,
        "rsi14": null,
        "ret_1d": -0.0163,
        "ret_5d": null,
        "ret_20d": null,
        "atr14_pct": null,
        "price_vs_sma20": null,
        "trend_sma20_vs_sma50": null
      }
    }
  },
  "feature_evidence": {
    "account_ref": "PAPER_ACCOUNT",
    "as_of": "2026-11-23T19:29:03.154787+00:00",
    "availability": {
      "account": "fresh",
      "bars": "fresh",
      "calendar": "fresh",
      "news": "fresh",
      "ok_fraction_core_features": 1.0,
      "quotes": "fresh"
    },
    "bands_hash": "810517c6e124c7ebc23ca0ebce7ef7ba7cc66b30bc21cacc66c1a221174255d4",
    "feasibility": {
      "AAPL": {
        "can_buy": true,
        "can_buy_reasons": [],
        "can_sell": false,
        "can_sell_reasons": [
          "NO_SELLABLE_INVENTORY"
        ],
        "entry_window_open": true,
        "entry_window_reason": "",
        "held_qty": "0.0",
        "max_new_notional_usd": "2000.0",
        "sellable_qty": "0"
      }
    },
    "feature_slot": {
      "candles": {
        "AAPL|2026-11-23T19:14:00+00:00": "d5bda39af69dcc53d4310b57aff3092db8a68054546c86a6b2df103d67ada5be",
        "AAPL|2026-11-23T19:15:00+00:00": "b0e6a6e9b9e4287c960f6ede77ad8f355970b7e8745dbe17c9339d2e3f12a605",
        "AAPL|2026-11-23T19:16:00+00:00": "69e7bfc090cee194af19c0acc6e8da6b7cf4c08443c52b952de98b8961d2ec67",
        "AAPL|2026-11-23T19:17:00+00:00": "c0a6e9630fa9f0d5027648d10559bb0be8e8caa0857d4fd8f17b11d4e3a85102",
        "AAPL|2026-11-23T19:18:00+00:00": "e862cb638fbc15b1a3f7b32db1c9e6d689acd1cd350079657d14e77d9e2c6479",
        "AAPL|2026-11-23T19:19:00+00:00": "e1937e8da6f995fc153f7e5e2ced98a01f960310d2ec214a17e4fb29a93c4146",
        "AAPL|2026-11-23T19:20:00+00:00": "70196363dae726bc8d352fd0e8cbb4b115e48fba11b5ee33c3817ea612c07c0f",
        "AAPL|2026-11-23T19:21:00+00:00": "6c6e08fc67af597579978fa03f3aaab5c3543c74e2011a7c2bce5c6d84460f57",
        "AAPL|2026-11-23T19:22:00+00:00": "2954cabc7ce7bf14ae0893aaac62bfaa70486fa0a68f63da27e0ee312728069a",
        "AAPL|2026-11-23T19:23:00+00:00": "2747e99b2df2570cd8f56be82b287c8ee7e009053a8933e9f3a90cd4d730228a",
        "AAPL|2026-11-23T19:24:00+00:00": "e1968a3f7d654002dbeeffb581d28f178a4778e7ef171a3abc48397e1eca10c1",
        "AAPL|2026-11-23T19:25:00+00:00": "f253416079d72d4e362e19307b75c172b7d2edb6ec453969e082d947eb75de1b",
        "AAPL|2026-11-23T19:26:00+00:00": "507b2e1c799046a50786ce4da765ff72ab0e23dce27aa1aa3bf3ee164f1c5e45",
        "AAPL|2026-11-23T19:27:00+00:00": "7b3543f4b74a7aa1b9442f5a5f6478df06cc1c1837cdd37538840b026f94764e",
        "AAPL|2026-11-23T19:28:00+00:00": "aea28bc8ffe040565b1ce653f93ba2bb08675b6cd7c4cb936280e4dd529e7b4d",
        "SPY|2026-11-23T19:14:00+00:00": "1a003d29f3062e0e284c02aef050fc33aa9519155986beb8ffeabb18ba63d85e",
        "SPY|2026-11-23T19:15:00+00:00": "80f9ec707984fc74f8cb6dcebd3d845190206f212a6a7f5bbea8e7f0dfe5b85a",
        "SPY|2026-11-23T19:16:00+00:00": "bef27fecf6495d402ef4cf61ab22855605b7bf35ec2ee88c5fa240ececdeb144",
        "SPY|2026-11-23T19:17:00+00:00": "9267d9ec8514091597a775a9f11df8e6ba85ef1a765d8d7c6e0695a9d17e9d04",
        "SPY|2026-11-23T19:18:00+00:00": "9927bc665ca20d7006e3e28873737e2afb2679463ac195ed3f79e8551e2cdac5",
        "SPY|2026-11-23T19:19:00+00:00": "a3f91e79e75f72019e37a2793b54c01ee93403d8d9eafbd7f1eb0c5012b9b9c4",
        "SPY|2026-11-23T19:20:00+00:00": "e1ddcdb981d5c72dfaca25e1aaa8c1c27aef392260bc51ce1653cfd94d114f8f",
        "SPY|2026-11-23T19:21:00+00:00": "7a81b6670301657ad6b9cb0542ae646ff5785b4dbcb61c6b01fba0f60649ba1a",
        "SPY|2026-11-23T19:22:00+00:00": "39edefebca8c72b2135f978774a03b1d9775e0b17ef5fce054875b0dd7243c94",
        "SPY|2026-11-23T19:23:00+00:00": "def528246d2c8ce3e04085fb10ac15cd8741ba99e3ec0331c205f3d95712dca6",
        "SPY|2026-11-23T19:24:00+00:00": "e0825fbb3c82960924bc0a4fa93ab9a29cea452a13a515bbc433eb3e210b164a",
        "SPY|2026-11-23T19:25:00+00:00": "b6bef0076894b860d0d4faaa2427e9f8628a5c940154cdafae8278de8b4adb91",
        "SPY|2026-11-23T19:26:00+00:00": "e46bbe752653b237f9f0581eb791d9c099d17374e961e6008fc525d3a1b17355",
        "SPY|2026-11-23T19:27:00+00:00": "90924a4d25b101c0d29fa5761917dd436ab61fc5b1b1a804cb4a5a9e91ea54d4",
        "SPY|2026-11-23T19:28:00+00:00": "11e1060e5795eacc48b906d2c57c74befb989db09d7d2453b896e6e520367ecf"
      },
      "close": "2026-11-23T19:29:00+00:00",
      "feed": "iex",
      "indicator_close": "2026-11-23T19:15:00+00:00",
      "indicator_input_hashes": {
        "AAPL": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
        "SPY": "647346c3307bab3f0ab75d294e9bf46773d6d42fa0676aa83ae2ca9d97b2b1eb"
      },
      "provisional": true,
      "records": {
        "market:market:breadth_above_ema21": "815832b01dd92f1e4451c79cf7955b56fb9737d65935bcfd1d3f33947ba7647c",
        "market:market:regime_label": "84f9e0050c68ef26c8fac251be3d1e9715d2043efbb27dc10dd36f804aed1906",
        "market:market:spy_ema_gap_bps_15m": "e1b77372b1441b383700bc1a58f75ce0bf7cd28628675e926f5fce53abbe5d18",
        "market:market:spy_ret_60m": "b3b2a4a96dcc1f74f096a1ba323849f32b779b48951a6a4ac259d923dfe8b918",
        "market:market:spy_vol_regime_ratio": "592eaee619cb463ae1ecdde11ec7be41212d44be18ba65bd69c8c61fbc90d766",
        "symbol:AAPL:adv_usd_20d": "e262af1fe6a7389e05b96a9a75b061c36d19abe6182590f4ef666a3c4147c5a3",
        "symbol:AAPL:atr14_15m": "4aa601dee2846211e120ee408a21949bef6a84cbeaeda8c8217242fa79357ada",
        "symbol:AAPL:atr14_1d": "9c0633de46b036a4fe93734a2e5dce61b7eff6bf36ec86c1bf294d9eeef95f85",
        "symbol:AAPL:atr14_pct": "1437ca280d0973889472dab3c5cb1b0006ef5ee631652a04bebaa9de603743bd",
        "symbol:AAPL:dist_hi_atr": "08be714074033f547cf24865739b2d3e295b6440f953fe7dac1708b8ba296817",
        "symbol:AAPL:dist_lo_atr": "1d1f3dccda202469170048cd9eed228a2859689785ef571dbcc67f75528dc615",
        "symbol:AAPL:ema21_15m": "a4fce26cfa0190c94a7c7a20a720ebe23cabd0d7ebbcf6c266507d885b6c2172",
        "symbol:AAPL:ema9_15m": "0ad14ee0eb256fe1fe75965b26cc534f1723fca1dde7436232c23a087c645c3e",
        "symbol:AAPL:ema_gap_bps_15m": "e727bcc5189a91061e7df830a4b1a4c71755006275cd2c0a493816f0a95e827b",
        "symbol:AAPL:gap_open_pct": "fc5c7eeea7261785fc595b201a91df75e735719dbe6722604c7617e8524e7bc1",
        "symbol:AAPL:intraday_ret_1h": "bce1649c3f11808a59de7a9536a3a82e7ffdc25c2c36ac39b247c733fff4bd35",
        "symbol:AAPL:intraday_setup_1m": "8ab6187155de32c9536dcd6682ebd517b812b18bedab53960ddc4ebe04472e82",
        "symbol:AAPL:last_close": "f064e1589fb929d983b820bbfcd86fd0141cb1044925ea55db4eb69a6c6b5ae1",
        "symbol:AAPL:macd_hist_15m": "5bdd527f747bb67db78b657003212927e07ba8624389f5381095f9a3f7a8d02f",
        "symbol:AAPL:price_vs_sma20": "a96d3080f2e95a5cc3b047ec495961d46cd4b318722c7eae4d719bfa2cc0f6e4",
        "symbol:AAPL:recent_price_10m": "9f76dbfdea4ebe199ee690bf9a8e72229f2ade8269fd0efb7a061c9cab09ba17",
        "symbol:AAPL:recent_range_bps_10m": "d9cfdb746128335b4561f188f8de65510dabf7381fdf4309ca2ee50850160e58",
        "symbol:AAPL:recent_range_bps_5m": "0b38d6484b0a0c1e1d87af6a9627f351d2367569c5c8eed64af2ea04bef87f54",
        "symbol:AAPL:recent_return_10m": "2af62ab978d30f3e0f5cf0f706379773921fd2c9996373cc6c8f2a7c3740f114",
        "symbol:AAPL:recent_return_5m": "f7da9d56a9e7de7e5623b844a127c2813ba28e0225102542157fdf0c9637a2be",
        "symbol:AAPL:recent_volume_10m": "52b567dcbca4e8fe60bcecd9968bc03aafc107eaa1080176b42e48af1a064b53",
        "symbol:AAPL:recent_volume_5m": "9ffd1b33f5657fb336f4aff7ca311f1cfbb5accbbb46a1f529f1e4eb2c1d782d",
        "symbol:AAPL:relstr_spy_60m": "92522eb56ec57aca2bb6a3f8b578f28c5fb077940a0e2b6b53cb5b46f953255b",
        "symbol:AAPL:ret_15m": "949e0454d1636facedfa210441b75adbb86cfc9045b4469ab0e473a603802275",
        "symbol:AAPL:ret_1d": "acd4850c7f353cd7d276491b7c7d3402308f47b10f57d00ddfcff5304f668541",
        "symbol:AAPL:ret_20d": "c1fd6c69e5212d8143db80ab0b65f04c3952518636216a6f65599b0cf9aa5d52",
        "symbol:AAPL:ret_5d": "e279e1e5300466ccb81556a606d3565ef56efdfaa8086d105f074c583b7f1520",
        "symbol:AAPL:ret_5m": "aa355bbc90afc61726b363bd2eb62df93f316f25132248b9d7a9b34132fbe96d",
        "symbol:AAPL:ret_60m": "a5f9014d420eaa13f6b3c0cd073acc79233707e45e581494b5f6f77e51493efb",
        "symbol:AAPL:rsi14": "017f8f44fae740e064f7cf662b6575f31515d3864f3470dc54f27aff186f4183",
        "symbol:AAPL:rsi14_15m": "4bcd3b3bc68ef2a3b24588f819b282374f20d221da66c12182e92b5be0b02bf7",
        "symbol:AAPL:rvol_60m": "c8acb6c144fb273078f40ae8348d9cc3609f1721e3c6e396d53f29759d3f445b",
        "symbol:AAPL:sma20": "3e4d68b668f1fb60d01391d426d6383d59c5f1489b2c60d8b9677923330ea1e8",
        "symbol:AAPL:sma50": "1ae3948821d316103e37237b485a2f4802a168c7ba7718bcaa1f5cecba683bb4",
        "symbol:AAPL:trend_sma20_vs_sma50": "70f14cdb1db36bf9d9d5e86c7b54697ceba3042951e93e45270a4f006f4c91d8",
        "symbol:AAPL:vol_regime_ratio": "ae703f5a79b2b63c1d4062deb158c909856b44f6480b4667958a7cdd26bc3872",
        "symbol:AAPL:volume_z20": "68a11cf3df037bf35a94e13761dc1df96383de19536c6a0d960a52c5365f1e28",
        "symbol:AAPL:volz_tod_15m": "530fa07e56964d38a2104f4a1a003a9c21fe607e74364348f18f0dfb47005705",
        "symbol:AAPL:vwap_dev_session": "084b330f04c847419d0f51ab4821105c0e52dea96d1db356299ce2999e97960b",
        "symbol:SPY:adv_usd_20d": "7773f3a908eaf7c0e76c09e0281ebbcb8379cc49400a15772c1830a3b2c2f223",
        "symbol:SPY:atr14_15m": "fc718bba22a5db9dae206edea8233cf88df09c2e3062133470a7fe10f13267e2",
        "symbol:SPY:atr14_1d": "aaeea7993a9d2b21fb57bccbb0a7e2bae3ebb9bc634c0e9b485665df8a582439",
        "symbol:SPY:atr14_pct": "684fcce9d38b849dfc48ed4adf427634c6537f0b2d2dac4b1ac576ea747f9ea6",
        "symbol:SPY:dist_hi_atr": "33aecd3bdc39f8edf5081809ea9cb0295efe67f12c168010bb153942b8655295",
        "symbol:SPY:dist_lo_atr": "79f3be0edf2d041633f288b73825730189fad17ca945bfcd761612e2b53a8ee9",
        "symbol:SPY:ema21_15m": "d517509d58dbc26956d75d98347e4757713275e63455fdcc3c4422d256746a81",
        "symbol:SPY:ema9_15m": "097b3848e725e0d802d5441768fbf4db8207cbc178c1f391212f3cf9f984afeb",
        "symbol:SPY:ema_gap_bps_15m": "88de61b58000f6c109f37ccb1278278f5d8761b975c2735eb8c0fceb4c8789cc",
        "symbol:SPY:gap_open_pct": "7b8b09f491c0f145686f016617f1e339ec2c992d2d7f4b990a6f22f849fb269b",
        "symbol:SPY:intraday_ret_1h": "e04939fd11622d8ee6f45b21cbd60aaf479b74745d0331a0d031b34eb916d9e1",
        "symbol:SPY:intraday_setup_1m": "2fe80b13fb804c662518fb095915e12f3a79fcd7af212749f4110be370e31d30",
        "symbol:SPY:last_close": "7c75e5b2d0cbfa6053329d40230beafe8c50de8de09b8650fbc56c1f24fef8dd",
        "symbol:SPY:macd_hist_15m": "700faaf2b22ddb3d7a761119e621afb779197ee9e20002bf78ec397dc82b0426",
        "symbol:SPY:price_vs_sma20": "b3b5e555c37b8c77664c4514095e6ed44684e1cca73f30c87e244ef5047030fc",
        "symbol:SPY:recent_price_10m": "9fd64cc5905c836bdad5ca38df8064d912a8df36742cf710a5fab71b2c28f2f5",
        "symbol:SPY:recent_range_bps_10m": "9a1f8565d524f1867ba4f39c1636a5a62af2e14b341d8bb0d46999e587ee81bf",
        "symbol:SPY:recent_range_bps_5m": "47a2cfd0ebbc7e1ed400fc42c3077b0482597c6f26e9e35c8d1801f48bf33452",
        "symbol:SPY:recent_return_10m": "2ad3cf66c2ea99eed5e36caa2fe0c783b8c7c7481905b6e9fefa4f0c41a425dc",
        "symbol:SPY:recent_return_5m": "5e05c3a2ace3fed62529d8b3ad1eb5e00a1459d755cadda5223cbaa29913fe3a",
        "symbol:SPY:recent_volume_10m": "2cfdb62f01848a422122c81a1a10b63976628030321860a2d835ea2dbe79c1c2",
        "symbol:SPY:recent_volume_5m": "066b74e95ba0f7fa1d04db1452b0062e28dba5ce828cc50e723d7c3e245cbbd0",
        "symbol:SPY:relstr_spy_60m": "f8e8a2c70f6861986994098551914f6ec7f583a6212d91b31d608d2906cc194a",
        "symbol:SPY:ret_15m": "180bc73a64c49f55c75b317d8de40ad5e6c32ddcd42e4a7850077acc6450cf75",
        "symbol:SPY:ret_1d": "ddc0a11b63cc350e3081db1903dee6252ddb61770d13b16e856291026f52a3f3",
        "symbol:SPY:ret_20d": "ed1093e0aa5d6f66c95107ca1d6e0dc684f91a2b174538f28adce162fbc2a1c1",
        "symbol:SPY:ret_5d": "2298165b21cd162151213ae636f77a63a657bd096db984033682489995a3b1f5",
        "symbol:SPY:ret_5m": "9912471672fe55e687b9af7e2201acd82dc19980b5305e1903eafc50c43740f0",
        "symbol:SPY:ret_60m": "92331c875ce39168d148e0ab7f50ce651dcc6836df3611c31418683d3071a207",
        "symbol:SPY:rsi14": "0896ff9e6527016820c4f3bacca566bf1825f6f67c30f9e930a11faa591958f6",
        "symbol:SPY:rsi14_15m": "f74fdb6b8a4dfd4479e87521b52a8e59d763710203d578d8f94a9675c6c9b551",
        "symbol:SPY:rvol_60m": "90264cfb7a2f2d6805e16c6785b8d653f4721843c805fdfa4cffe6203a9cf02c",
        "symbol:SPY:sma20": "d0283363840868af6910e903d8b6ce0fa7a2a5f15f1fe6688eee56a4e374e136",
        "symbol:SPY:sma50": "f0b368651bafa612c1bc158db1c24203caf7f9a36cde9c70a55ee93a918503d6",
        "symbol:SPY:trend_sma20_vs_sma50": "081b68b933591d41fda8068af744f2f85c5c3ab9eea6461455fa6828810c399c",
        "symbol:SPY:vol_regime_ratio": "2e832b61a01c7d389e0b159efe7affd2a540c05b070fb10daaf071c6c81e5f81",
        "symbol:SPY:volume_z20": "b50666ce3e64dd1b2b048c991b636383b066dc0bdc8adda4888131d53fc369b6",
        "symbol:SPY:volz_tod_15m": "461ed44d456e55c2fcef586cde4f795fb112387dee57647074b82b07fa685f52",
        "symbol:SPY:vwap_dev_session": "485f4ffc37342fa52643210adb4e026706a62999a64cb9f310cd379a19b2b763"
      },
      "symbols": [
        "AAPL",
        "SPY"
      ]
    },
    "horizons": {
      "AAPL": {
        "10m": {
          "age_s": 3.154787,
          "last_bar_end": "2026-11-23T19:29:00+00:00",
          "status": "OK"
        },
        "15m": {
          "age_s": 843.154787,
          "last_bar_end": "2026-11-23T19:15:00+00:00",
          "status": "OK"
        },
        "5m": {
          "age_s": 3.154787,
          "last_bar_end": "2026-11-23T19:29:00+00:00",
          "status": "OK"
        },
        "60m": {
          "age_s": 843.154787,
          "last_bar_end": "2026-11-23T19:15:00+00:00",
          "status": "OK"
        },
        "horizon_conflict": false
      }
    },
    "market": {
      "breadth_above_ema21": {
        "age_s": 843.154787,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "815832b01dd92f1e4451c79cf7955b56fb9737d65935bcfd1d3f33947ba7647c",
        "status": "OK",
        "v": 1.0,
        "version": "1.1dfe664d"
      },
      "minutes_to_close": {
        "age_s": 0.610342,
        "quality": {},
        "record_hash": "5f2ffbc878de9bcebbc8a3d2114df77fed97c1b153633160b471aebab6775708",
        "status": "OK",
        "v": 90.95759258,
        "version": "1.e79b1ead"
      },
      "regime_label": {
        "age_s": 843.154787,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "84f9e0050c68ef26c8fac251be3d1e9715d2043efbb27dc10dd36f804aed1906",
        "status": "OK",
        "v": "UPTREND",
        "version": "1.f8b361d7"
      },
      "session_phase": {
        "age_s": 0.610342,
        "quality": {},
        "record_hash": "3ac43486098cc6b408e9586098ca474c2af2f75cfd1aa38ca25fec069b49bb57",
        "status": "OK",
        "v": "NORMAL",
        "version": "1.91f88fe8"
      },
      "spy_ema_gap_bps_15m": {
        "age_s": 843.154787,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "e1b77372b1441b383700bc1a58f75ce0bf7cd28628675e926f5fce53abbe5d18",
        "status": "OK",
        "v": 46.06234614,
        "version": "1.fda7da7a"
      },
      "spy_ret_60m": {
        "age_s": 843.154787,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "b3b2a4a96dcc1f74f096a1ba323849f32b779b48951a6a4ac259d923dfe8b918",
        "status": "OK",
        "v": -0.00049727878,
        "version": "1.9feddbd1"
      },
      "spy_vol_regime_ratio": {
        "age_s": 843.154787,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "592eaee619cb463ae1ecdde11ec7be41212d44be18ba65bd69c8c61fbc90d766",
        "status": "OK",
        "v": 1.507315312,
        "version": "1.3b7257aa"
      }
    },
    "meta": {
      "news": {
        "AAPL": {
          "effective_weight": 0,
          "in_window": 0,
          "newest_age_min": null,
          "policy": "48h retained; per-article decay and minimum relevance; 4h count is descriptive",
          "poller_last_ok_age_s": 13.122488,
          "retrieved": 0,
          "selected": 0,
          "state": "QUIET",
          "window_min": 240
        }
      }
    },
    "news_blob_hash": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
    "news_context_blob_hash": "e3c60af9d95ebaf1f55c06533eacb239249be79ce6a8acc4ac91c59c6b87b05f",
    "portfolio": {
      "aggregate_cap_usd": {
        "age_s": 0.610342,
        "quality": {},
        "record_hash": "4279487ce4dc459909c417d6d4d8a9c76eb2a7e4a94c294e382e3c1b715086c8",
        "status": "OK",
        "v": "49901.695",
        "version": "1.5b3d1daf"
      },
      "aggregate_headroom_usd": {
        "age_s": 0.610342,
        "quality": {},
        "record_hash": "e6687c6d163c5a5724a741c6a8cf40a4a582aa85ad564e72e1d86611fa1ccfd3",
        "status": "OK",
        "v": "49901.695",
        "version": "1.7f894fff"
      },
      "buying_power": {
        "age_s": 0.610342,
        "quality": {},
        "record_hash": "c64576d0b498f641a48dbb6e0b62a40d5ac81c46d23a637bcbc57df50b00bf23",
        "status": "OK",
        "v": "399213.56",
        "version": "1.74948dec"
      },
      "cash": {
        "age_s": 0.610342,
        "quality": {},
        "record_hash": "20ed535c2050644fa5f01b4b95ce28dac10fd02443e506ce374f8961d5a86540",
        "status": "OK",
        "v": "99803.39",
        "version": "1.b067f5e3"
      },
      "day_pnl_pct": {
        "age_s": 0.610342,
        "quality": {},
        "record_hash": "59ac3b6d31350d0117ee643350087be087b216d6fd78eb87493cad11134bdf91",
        "status": "OK",
        "v": "0",
        "version": "1.35e81852"
      },
      "drawdown_pct": {
        "age_s": 0.610342,
        "quality": {},
        "record_hash": "5de2e98bce09519c5b95da86408ec19a71fe75b8bd3eee2107fe148460e2550f",
        "status": "MISSING",
        "v": null,
        "version": "1.19aac9ba"
      },
      "equity": {
        "age_s": 0.610342,
        "quality": {},
        "record_hash": "0a0c87e2607918369dd97887b3beb2ba6d633769a4da43b4b6832e23e921e3cd",
        "status": "OK",
        "v": "99803.39",
        "version": "1.a2192616"
      },
      "gross_exposure_pct": {
        "age_s": 0.610342,
        "quality": {},
        "record_hash": "e1ad434eab6e37ea0fc1fb3d21c291972ea7545b369cbcf8025f104631a283ed",
        "status": "OK",
        "v": "0E+2",
        "version": "1.b82cc518"
      },
      "gross_exposure_usd": {
        "age_s": 0.610342,
        "quality": {},
        "record_hash": "a174c0c6d59bcbbaadfcbf8598b2c4ebf3ce1b209346546e8a4ca96b29f0b988",
        "status": "OK",
        "v": "0",
        "version": "1.e4c8752b"
      },
      "last_reconcile_age_s": {
        "age_s": 0.610342,
        "quality": {},
        "record_hash": "86cc7b28da97efa0f0ad9b7fbd8b0fa47064a374b5495c17a0d16f901e5391de",
        "status": "OK",
        "v": 0,
        "version": "1.5ed0382f"
      },
      "open_buy_notional_usd": {
        "age_s": 0.610342,
        "quality": {},
        "record_hash": "a9c2ac0559451de7cc7b22f3ec50a4df910933b036fa069070d3f7ee1b8e4df1",
        "status": "OK",
        "v": "0",
        "version": "1.0bd0ead1"
      },
      "open_orders": {
        "age_s": 0.610342,
        "quality": {},
        "record_hash": "080a709da8bdae78de0b7e344e1f15aca76ea6183e518271f1d20fc4529970e7",
        "status": "OK",
        "v": [],
        "version": "1.1cf37cbf"
      },
      "open_orders_count": {
        "age_s": 0.610342,
        "quality": {},
        "record_hash": "5771cd74eb1ae538b7890fa0d289b5340efe33f4bd7f0f1aa69818ed9532b96d",
        "status": "OK",
        "v": 0,
        "version": "1.1db4227a"
      },
      "pending_reserved_usd": {
        "age_s": 0.610342,
        "quality": {},
        "record_hash": "f4f9981d0517920c2bcbdf7463e90e63db5e8a3be8f628f002a2a5172fc67fee",
        "status": "OK",
        "v": "0",
        "version": "1.1c3e9604"
      },
      "positions": {
        "age_s": 0.610342,
        "quality": {},
        "record_hash": "f8e26974a0deef624cf14732c4c1210d5a9e0c0cead1c1ca16950d638228fc16",
        "status": "OK",
        "v": [],
        "version": "1.c3284657"
      }
    },
    "registry_hash": "0fd3271269748046863b2f0558e45e2c333bb352eccc9899b7ff42277c8386fc",
    "schema_version": 1,
    "symbols": {
      "AAPL": {
        "adv_usd_20d": {
          "age_s": 253743.1548,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "e262af1fe6a7389e05b96a9a75b061c36d19abe6182590f4ef666a3c4147c5a3",
          "status": "OK",
          "v": 525559715.8,
          "version": "1.04f5e91f"
        },
        "ask_px": {
          "age_s": 1.524538,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "5011e56a249375f69cde3fef332e6bdeb5b15c7d4c7636b6cf0e8fffaa954066",
          "status": "OK",
          "v": 350.21,
          "version": "1.d21cdd09"
        },
        "atr14_15m": {
          "age_s": 843.154787,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "4aa601dee2846211e120ee408a21949bef6a84cbeaeda8c8217242fa79357ada",
          "status": "OK",
          "v": 1.466657912,
          "version": "1.0cd14e73"
        },
        "atr14_1d": {
          "age_s": 253743.1548,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "9c0633de46b036a4fe93734a2e5dce61b7eff6bf36ec86c1bf294d9eeef95f85",
          "status": "MISSING",
          "v": null,
          "version": "1.65e38f4c"
        },
        "atr14_pct": {
          "age_s": 253743.1548,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "1437ca280d0973889472dab3c5cb1b0006ef5ee631652a04bebaa9de603743bd",
          "status": "MISSING",
          "v": null,
          "version": "1.87450ee9"
        },
        "bid_px": {
          "age_s": 1.524538,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "698c0d94c8066ce3c848bbb6b0ff85e92f542e2f0c9c85010dc6b77a4a02bdb0",
          "status": "OK",
          "v": 350.16,
          "version": "1.149628cd"
        },
        "dist_hi_atr": {
          "age_s": 843.154787,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "08be714074033f547cf24865739b2d3e295b6440f953fe7dac1708b8ba296817",
          "status": "OK",
          "v": -1.670464516,
          "version": "1.913ffc4a"
        },
        "dist_lo_atr": {
          "age_s": 843.154787,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "1d1f3dccda202469170048cd9eed228a2859689785ef571dbcc67f75528dc615",
          "status": "OK",
          "v": 3.156837025,
          "version": "1.79ba4c70"
        },
        "ema21_15m": {
          "age_s": 843.154787,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "a4fce26cfa0190c94a7c7a20a720ebe23cabd0d7ebbcf6c266507d885b6c2172",
          "status": "OK",
          "v": 348.3552073,
          "version": "1.bfcac61e"
        },
        "ema9_15m": {
          "age_s": 843.154787,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "0ad14ee0eb256fe1fe75965b26cc534f1723fca1dde7436232c23a087c645c3e",
          "status": "OK",
          "v": 348.9848916,
          "version": "1.81255de8"
        },
        "ema_gap_bps_15m": {
          "age_s": 843.154787,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "e727bcc5189a91061e7df830a4b1a4c71755006275cd2c0a493816f0a95e827b",
          "status": "OK",
          "v": 18.07592592,
          "version": "1.d4519f3c"
        },
        "gap_open_pct": {
          "age_s": 843.154787,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "fc5c7eeea7261785fc595b201a91df75e735719dbe6722604c7617e8524e7bc1",
          "status": "MISSING",
          "v": null,
          "version": "1.27438d4d"
        },
        "halted": {
          "age_s": 0.610342,
          "quality": {},
          "record_hash": "0f2e46ba6df69cb3c77f12b2da683c144c7290391303100057c2053cd960dc9b",
          "status": "OK",
          "v": false,
          "version": "1.22c5cf87"
        },
        "held_minutes": {
          "age_s": 0.610342,
          "quality": {},
          "record_hash": "bdbe1e94ca9356b76c52a8a486b758293a9af0860566d4755dc6ee0deef15f46",
          "status": "MISSING",
          "v": null,
          "version": "1.de6ed6d3"
        },
        "intraday_ret_1h": {
          "age_s": 843.154787,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "bce1649c3f11808a59de7a9536a3a82e7ffdc25c2c36ac39b247c733fff4bd35",
          "status": "OK",
          "v": 0.001716689079,
          "version": "1.c3bb7751"
        },
        "intraday_setup_1m": {
          "age_s": 3.154787,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "10ba864311be6c51a24f3955db4f9360c0d0950a9abc5e2dac86369df360e636",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:29:00+00:00",
            "window_start": "2026-11-23T19:19:00+00:00"
          },
          "record_hash": "8ab6187155de32c9536dcd6682ebd517b812b18bedab53960ddc4ebe04472e82",
          "status": "OK",
          "v": {
            "confirmation": "UNCONFIRMED",
            "pattern": "BEARISH_ENGULFING",
            "prior_trend": "UP",
            "range_break": "INSIDE",
            "range_ceiling": 350.39,
            "range_floor": 349.8,
            "setup_minute": 9,
            "volume_ratio": 2.0473
          },
          "version": "1.2a1f51e0"
        },
        "last_close": {
          "age_s": 253743.1548,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "f064e1589fb929d983b820bbfcd86fd0141cb1044925ea55db4eb69a6c6b5ae1",
          "status": "MISSING",
          "v": null,
          "version": "1.f2485fc2"
        },
        "luld_active": {
          "age_s": 0.610342,
          "quality": {},
          "record_hash": "fa435419deb938cfca54dc0f5bbfc71e3d911f444b3df05f55cd058ba34d249e",
          "status": "MISSING",
          "v": null,
          "version": "1.84a715b2"
        },
        "macd_hist_15m": {
          "age_s": 843.154787,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "5bdd527f747bb67db78b657003212927e07ba8624389f5381095f9a3f7a8d02f",
          "status": "OK",
          "v": 0.08324749226,
          "version": "1.391617c8"
        },
        "mid_px": {
          "age_s": 1.524538,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "d0006053443703f9fa2a6d6828b6b8ac8752ae888af678b48580777b488f723e",
          "status": "OK",
          "v": 350.185,
          "version": "1.d567a349"
        },
        "news_age_min_latest": {
          "age_s": 13.122488,
          "quality": {},
          "record_hash": "237b93230beb1df0d0f5b6865fbf91d6b960f0aa55ff94e85fde58818e803449",
          "status": "MISSING",
          "v": null,
          "version": "1.d0f79dc8"
        },
        "news_confirmed": {
          "age_s": 0,
          "quality": {
            "source": "stored news and pinned price features"
          },
          "status": "OK",
          "v": false,
          "version": "news-confirmation-v2"
        },
        "news_count_1h": {
          "age_s": 13.122488,
          "quality": {},
          "record_hash": "8b56e8b3c12fdacc6e36c4c9bceed3d51faf5decc0d849d3928784eef1e4fae9",
          "status": "OK",
          "v": 0,
          "version": "1.0c9362fe"
        },
        "news_count_48h": {
          "age_s": 13.122488,
          "quality": {
            "as_of": "2026-11-23T19:29:03.154787+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 0,
          "version": "news-context-v2"
        },
        "news_count_4h": {
          "age_s": 13.122488,
          "quality": {
            "as_of": "2026-11-23T19:29:03.154787+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 0,
          "version": "news-context-v2"
        },
        "news_effective_sentiment": {
          "age_s": 0,
          "quality": {
            "selected": 0,
            "source": "decayed stored article metadata"
          },
          "status": "MISSING",
          "v": 0.0,
          "version": "news-decay-v2"
        },
        "news_event_flags_4h": {
          "age_s": 13.122488,
          "quality": {},
          "record_hash": "eec0e10978b5d0e9cfdb7d655f625edf17623d11b4f15c5f59f87afa934b91a8",
          "status": "OK",
          "v": [],
          "version": "1.0b5a8a44"
        },
        "news_max_materiality_4h": {
          "age_s": 13.122488,
          "quality": {},
          "record_hash": "eb248b25ca9418810b706efd1ca945f21986a0803673e9993999f422d95312cc",
          "status": "OK",
          "v": 0,
          "version": "1.9c45e9b4"
        },
        "news_newest_age_min": {
          "age_s": 13.122488,
          "quality": {
            "as_of": "2026-11-23T19:29:03.154787+00:00",
            "source": "stored articles"
          },
          "status": "MISSING",
          "v": null,
          "version": "news-context-v2"
        },
        "news_novelty_max_4h": {
          "age_s": 13.122488,
          "quality": {},
          "record_hash": "964d98e2d8a5442923062bea1db6189ef91ed3a51f8253c80eb6a702f5df8792",
          "status": "OK",
          "v": false,
          "version": "1.15ceb7bf"
        },
        "news_sent_ewm_240m": {
          "age_s": 13.122488,
          "quality": {},
          "record_hash": "3a664c18c7d641b5ab6a5fae3c455a13f38cace4aa586e71254b9c17ac1e7468",
          "status": "OK",
          "v": 0,
          "version": "1.9cad993f"
        },
        "news_sent_ewm_60m": {
          "age_s": 13.122488,
          "quality": {},
          "record_hash": "95425287c2d41511f595b46306b5c8a734e9a17f4cece57e40dd77309b094eaa",
          "status": "OK",
          "v": 0,
          "version": "1.74ab70c1"
        },
        "news_source_div_4h": {
          "age_s": 13.122488,
          "quality": {},
          "record_hash": "61b83dda6096743e47be267dee08a7910d7775ef091854c82900e02f6a1ccd8e",
          "status": "OK",
          "v": 0,
          "version": "1.6fd469c4"
        },
        "position_qty": {
          "age_s": 0.610342,
          "quality": {},
          "record_hash": "036db8708d93425025c6ac2fd6b45a848be9106a272a5d5df5157b67cc2c3589",
          "status": "OK",
          "v": "0",
          "version": "1.3a512120"
        },
        "position_value_usd": {
          "age_s": 0.610342,
          "quality": {},
          "record_hash": "0650fa25fd29b1bab011522bea83141fbf14017d60cf3635da5de42a15fbd4cb",
          "status": "OK",
          "v": "0",
          "version": "1.9100bec4"
        },
        "price_vs_sma20": {
          "age_s": 253743.1548,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "a96d3080f2e95a5cc3b047ec495961d46cd4b318722c7eae4d719bfa2cc0f6e4",
          "status": "MISSING",
          "v": null,
          "version": "1.a986b9cc"
        },
        "recent_price_10m": {
          "age_s": 3.154787,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "10ba864311be6c51a24f3955db4f9360c0d0950a9abc5e2dac86369df360e636",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:29:00+00:00",
            "window_start": "2026-11-23T19:19:00+00:00"
          },
          "record_hash": "9f76dbfdea4ebe199ee690bf9a8e72229f2ade8269fd0efb7a061c9cab09ba17",
          "status": "OK",
          "v": {
            "candles": [
              [
                0,
                349.92,
                350.15,
                349.89,
                350.13,
                3319.0,
                "VERIFIED_BAR"
              ],
              [
                1,
                350.155,
                350.22,
                350.09,
                350.18,
                2477.0,
                "VERIFIED_BAR"
              ],
              [
                2,
                350.19,
                350.39,
                350.17,
                350.25,
                2728.0,
                "VERIFIED_BAR"
              ],
              [
                3,
                350.21,
                350.225,
                350.0,
                350.015,
                1212.0,
                "VERIFIED_BAR"
              ],
              [
                4,
                349.87,
                349.98,
                349.82,
                349.82,
                1640.0,
                "VERIFIED_BAR"
              ],
              [
                5,
                349.86,
                350.12,
                349.8,
                350.05,
                3317.0,
                "VERIFIED_BAR"
              ],
              [
                6,
                349.99,
                350.12,
                349.97,
                350.07,
                1788.0,
                "VERIFIED_BAR"
              ],
              [
                7,
                350.115,
                350.25,
                350.1,
                350.13,
                2283.0,
                "VERIFIED_BAR"
              ],
              [
                8,
                350.16,
                350.285,
                350.15,
                350.27,
                2201.0,
                "VERIFIED_BAR"
              ],
              [
                9,
                350.31,
                350.31,
                350.15,
                350.15,
                4674.0,
                "VERIFIED_BAR"
              ]
            ],
            "columns": [
              "minute_offset",
              "open",
              "high",
              "low",
              "close",
              "volume",
              "coverage"
            ],
            "feed": "iex",
            "window_end": "2026-11-23T19:29:00+00:00",
            "window_start": "2026-11-23T19:19:00+00:00",
            "windows": {
              "10m": {
                "close": 350.15,
                "open": 349.92,
                "range_bps": 16.8609968,
                "return": 0.0006572930956,
                "status": "OK",
                "volume": 25639.0
              },
              "5m": {
                "close": 350.15,
                "open": 349.86,
                "range_bps": 14.57725948,
                "return": 0.0008289029898,
                "status": "OK",
                "volume": 14263.0
              }
            }
          },
          "version": "1.b12384d7"
        },
        "recent_range_bps_10m": {
          "age_s": 3.154787,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "10ba864311be6c51a24f3955db4f9360c0d0950a9abc5e2dac86369df360e636",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:29:00+00:00",
            "window_start": "2026-11-23T19:19:00+00:00"
          },
          "record_hash": "d9cfdb746128335b4561f188f8de65510dabf7381fdf4309ca2ee50850160e58",
          "status": "OK",
          "v": 16.8609968,
          "version": "1.b7dd2e6e"
        },
        "recent_range_bps_5m": {
          "age_s": 3.154787,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "10ba864311be6c51a24f3955db4f9360c0d0950a9abc5e2dac86369df360e636",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:29:00+00:00",
            "window_start": "2026-11-23T19:19:00+00:00"
          },
          "record_hash": "0b38d6484b0a0c1e1d87af6a9627f351d2367569c5c8eed64af2ea04bef87f54",
          "status": "OK",
          "v": 14.57725948,
          "version": "1.860a2856"
        },
        "recent_return_10m": {
          "age_s": 3.154787,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "10ba864311be6c51a24f3955db4f9360c0d0950a9abc5e2dac86369df360e636",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:29:00+00:00",
            "window_start": "2026-11-23T19:19:00+00:00"
          },
          "record_hash": "2af62ab978d30f3e0f5cf0f706379773921fd2c9996373cc6c8f2a7c3740f114",
          "status": "OK",
          "v": 0.0006572930956,
          "version": "1.03c04840"
        },
        "recent_return_5m": {
          "age_s": 3.154787,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "10ba864311be6c51a24f3955db4f9360c0d0950a9abc5e2dac86369df360e636",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:29:00+00:00",
            "window_start": "2026-11-23T19:19:00+00:00"
          },
          "record_hash": "f7da9d56a9e7de7e5623b844a127c2813ba28e0225102542157fdf0c9637a2be",
          "status": "OK",
          "v": 0.0008289029898,
          "version": "1.a9090b46"
        },
        "recent_volume_10m": {
          "age_s": 3.154787,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "10ba864311be6c51a24f3955db4f9360c0d0950a9abc5e2dac86369df360e636",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:29:00+00:00",
            "window_start": "2026-11-23T19:19:00+00:00"
          },
          "record_hash": "52b567dcbca4e8fe60bcecd9968bc03aafc107eaa1080176b42e48af1a064b53",
          "status": "OK",
          "v": 25639.0,
          "version": "1.891ed5cd"
        },
        "recent_volume_5m": {
          "age_s": 3.154787,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "10ba864311be6c51a24f3955db4f9360c0d0950a9abc5e2dac86369df360e636",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:29:00+00:00",
            "window_start": "2026-11-23T19:19:00+00:00"
          },
          "record_hash": "9ffd1b33f5657fb336f4aff7ca311f1cfbb5accbbb46a1f529f1e4eb2c1d782d",
          "status": "OK",
          "v": 14263.0,
          "version": "1.c7331f02"
        },
        "relstr_spy_60m": {
          "age_s": 843.154787,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "92522eb56ec57aca2bb6a3f8b578f28c5fb077940a0e2b6b53cb5b46f953255b",
          "status": "OK",
          "v": 0.002471753684,
          "version": "1.c04b464c"
        },
        "ret_15m": {
          "age_s": 843.154787,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "949e0454d1636facedfa210441b75adbb86cfc9045b4469ab0e473a603802275",
          "status": "OK",
          "v": 0.0004285714286,
          "version": "1.3fa23ddd"
        },
        "ret_1d": {
          "age_s": 843.154787,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "acd4850c7f353cd7d276491b7c7d3402308f47b10f57d00ddfcff5304f668541",
          "status": "OK",
          "v": -0.01628543191,
          "version": "1.b77eca69"
        },
        "ret_20d": {
          "age_s": 253743.1548,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "c1fd6c69e5212d8143db80ab0b65f04c3952518636216a6f65599b0cf9aa5d52",
          "status": "MISSING",
          "v": null,
          "version": "1.7d1f1942"
        },
        "ret_5d": {
          "age_s": 253743.1548,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "e279e1e5300466ccb81556a606d3565ef56efdfaa8086d105f074c583b7f1520",
          "status": "MISSING",
          "v": null,
          "version": "1.5d56db82"
        },
        "ret_5m": {
          "age_s": 843.154787,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "aa355bbc90afc61726b363bd2eb62df93f316f25132248b9d7a9b34132fbe96d",
          "status": "OK",
          "v": 0.0009433422903,
          "version": "1.c10a3b57"
        },
        "ret_60m": {
          "age_s": 843.154787,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "a5f9014d420eaa13f6b3c0cd073acc79233707e45e581494b5f6f77e51493efb",
          "status": "OK",
          "v": 0.001974474904,
          "version": "1.6c49ff8f"
        },
        "rsi14": {
          "age_s": 253743.1548,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "017f8f44fae740e064f7cf662b6575f31515d3864f3470dc54f27aff186f4183",
          "status": "MISSING",
          "v": null,
          "version": "1.273a3a79"
        },
        "rsi14_15m": {
          "age_s": 843.154787,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "4bcd3b3bc68ef2a3b24588f819b282374f20d221da66c12182e92b5be0b02bf7",
          "status": "OK",
          "v": 60.34276894,
          "version": "1.f0b8fdaf"
        },
        "rvol_60m": {
          "age_s": 843.154787,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "c8acb6c144fb273078f40ae8348d9cc3609f1721e3c6e396d53f29759d3f445b",
          "status": "OK",
          "v": 0.003775719992,
          "version": "1.84c5ec7e"
        },
        "sellable_qty": {
          "age_s": 0.610342,
          "quality": {},
          "record_hash": "c8753abfa18040f34263476593dff1ba84073ec8ba26e44f8af3ad52293e04d0",
          "status": "OK",
          "v": "0",
          "version": "1.9cbf72e4"
        },
        "sma20": {
          "age_s": 253743.1548,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "3e4d68b668f1fb60d01391d426d6383d59c5f1489b2c60d8b9677923330ea1e8",
          "status": "MISSING",
          "v": null,
          "version": "1.80f8a078"
        },
        "sma50": {
          "age_s": 253743.1548,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "1ae3948821d316103e37237b485a2f4802a168c7ba7718bcaa1f5cecba683bb4",
          "status": "MISSING",
          "v": null,
          "version": "1.3890c9d7"
        },
        "spread_bps": {
          "age_s": 1.524538,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "7ec0ea3050e734c2b942e38a7558e7c5e11d7cdb3816e9886b9311881b0dd17e",
          "status": "OK",
          "v": 1.427816725,
          "version": "1.e2b080ab"
        },
        "trend_sma20_vs_sma50": {
          "age_s": 253743.1548,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "70f14cdb1db36bf9d9d5e86c7b54697ceba3042951e93e45270a4f006f4c91d8",
          "status": "MISSING",
          "v": null,
          "version": "1.84583425"
        },
        "unrealized_pnl_pct": {
          "age_s": 0.610342,
          "quality": {},
          "record_hash": "aba719240ba4b3b2852d3896fd915e145c1f09a58363e6e7165c912ff251e092",
          "status": "OK",
          "v": 0,
          "version": "1.7c530604"
        },
        "vol_regime_ratio": {
          "age_s": 843.154787,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "ae703f5a79b2b63c1d4062deb158c909856b44f6480b4667958a7cdd26bc3872",
          "status": "OK",
          "v": 1.126397874,
          "version": "1.302e72c1"
        },
        "volume_z20": {
          "age_s": 253743.1548,
          "quality": {
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "last_session": "2026-11-20"
          },
          "record_hash": "68a11cf3df037bf35a94e13761dc1df96383de19536c6a0d960a52c5365f1e28",
          "status": "MISSING",
          "v": null,
          "version": "1.970d159b"
        },
        "volz_tod_15m": {
          "age_s": 843.154787,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "530fa07e56964d38a2104f4a1a003a9c21fe607e74364348f18f0dfb47005705",
          "status": "OK",
          "v": 0.1756718124,
          "version": "1.4315d547"
        },
        "vwap_dev_session": {
          "age_s": 843.154787,
          "quality": {
            "bar_density": 0.9998963193,
            "completeness": 1.0,
            "expected_minutes": 9645,
            "feed": "iex",
            "input_hash": "e70f4b7ac1fbcb443597cbbe752e5f13fb35c5c72b5a1ceab55dc14561930fee",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9644,
            "verified_none": 1,
            "window_end": "2026-11-23T19:15:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "084b330f04c847419d0f51ab4821105c0e52dea96d1db356299ce2999e97960b",
          "status": "OK",
          "v": 0.003334449535,
          "version": "1.b41de1ff"
        }
      }
    },
    "validation_policy": "scored-15m-plus-2m-v1"
  },
  "council_mode": "FULL",
  "chair": {
    "note": "Entry window open, buying power ample, no sellable inventory; buy aligns with signal.",
    "role": "CHAIR",
    "run_id": "4e0def5e-638a-53ed-b8ec-c1989778a527",
    "candidates": [
      {
        "note": "Score 0.645, EMA gap strong, UPTREND regime, tight spread supports entry.",
        "action": "buy",
        "symbol": "AAPL",
        "conviction": 0.62,
        "cited_roles": [
          "TECHNICAL",
          "REGIME",
          "LIQUIDITY"
        ]
      }
    ],
    "schema_version": 2
  },
  "skeptic_audit": {
    "tokens": 3968,
    "attempts": 1,
    "request_ms": 730,
    "input_tokens": 3898,
    "phase_start_ms": 3609,
    "provider_errors": [],
    "repair_attempts": 0,
    "cached_input_tokens": 0
  },
  "role_outputs": [
    {
      "role": "CHAIR",
      "status": "OK",
      "response": "{\n  \"schema_version\": 2,\n  \"run_id\": \"4e0def5e-638a-53ed-b8ec-c1989778a527\",\n  \"role\": \"CHAIR\",\n  \"candidates\": [\n    {\n      \"symbol\": \"AAPL\",\n      \"action\": \"buy\",\n      \"conviction\": 0.62,\n      \"cited_roles\": [\"TECHNICAL\", \"REGIME\", \"LIQUIDITY\"],\n      \"note\": \"Score 0.645, EMA gap strong, UPTREND regime, tight spread supports entry.\"\n    }\n  ],\n  \"note\": \"Entry window open, buying power ample, no sellable inventory; buy aligns with signal.\"\n}",
      "error": null
    },
    {
      "role": "LIQUIDITY",
      "status": "OK",
      "response": "{\"schema_version\":2,\"run_id\":\"4e0def5e-638a-53ed-b8ec-c1989778a527\",\"source\":\"code\",\"data_confidence\":\"HIGH\",\"role\":\"LIQUIDITY\",\"symbols\":[{\"symbol\":\"AAPL\",\"evidence\":[{\"path\":\"symbols.AAPL.spread_bps\",\"band\":\"TIGHT\"},{\"path\":\"symbols.AAPL.mid_px\",\"band\":\"POSITIVE\"},{\"path\":\"symbols.AAPL.volz_tod_15m\",\"band\":\"NORMAL\"}],\"note\":\"deterministic code assessment\",\"gate\":{\"state\":\"PASS\",\"size_multiplier\":1.0,\"reasons\":[]}}]}",
      "error": null
    },
    {
      "role": "PORTFOLIO",
      "status": "OK",
      "response": "{\"data_confidence\": \"HIGH\", \"role\": \"PORTFOLIO\", \"run_id\": \"4e0def5e-638a-53ed-b8ec-c1989778a527\", \"schema_version\": 2, \"source\": \"code\", \"symbols\": [{\"evidence\": [{\"band\": \"POSITIVE\", \"path\": \"portfolio.equity\"}, {\"band\": \"POSITIVE\", \"path\": \"portfolio.buying_power\"}, {\"band\": \"POSITIVE\", \"path\": \"portfolio.aggregate_headroom_usd\"}, {\"band\": \"ZERO\", \"path\": \"symbols.AAPL.position_qty\"}], \"gate\": {\"reasons\": [], \"size_multiplier\": 1.0, \"state\": \"PASS\"}, \"note\": \"deterministic code assessment\", \"symbol\": \"AAPL\"}]}",
      "error": null
    },
    {
      "role": "REGIME",
      "status": "OK",
      "response": "{\"data_confidence\":\"HIGH\",\"risk_appetite\":\"NEUTRAL\",\"role\":\"REGIME\",\"run_id\":\"4e0def5e-638a-53ed-b8ec-c1989778a527\",\"schema_version\":2,\"source\":\"code\",\"symbols\":[{\"symbol\":\"AAPL\",\"note\":\"Positive regime, high EMA gap, can_buy true.\",\"evidence\":[{\"path\":\"market.regime_label\",\"band\":\"UPTREND\"},{\"path\":\"feasibility.AAPL.can_buy\",\"band\":\"TRUE\"},{\"path\":\"symbols.AAPL.ema_gap_bps_15m\",\"band\":\"POS_STRONG\"}]}]}",
      "error": null
    },
    {
      "role": "SKEPTIC",
      "status": "OK",
      "response": "{\"schema_version\":2,\"run_id\":\"4e0def5e-638a-53ed-b8ec-c1989778a527\",\"role\":\"SKEPTIC\",\"objections\":[]}",
      "error": null
    },
    {
      "role": "TECHNICAL",
      "status": "OK",
      "response": "{\"data_confidence\": \"HIGH\", \"role\": \"TECHNICAL\", \"run_id\": \"4e0def5e-638a-53ed-b8ec-c1989778a527\", \"schema_version\": 2, \"source\": \"code\", \"symbols\": [{\"evidence\": [{\"band\": \"POS_STRONG\", \"path\": \"symbols.AAPL.ema_gap_bps_15m\"}, {\"band\": \"FIRM\", \"path\": \"symbols.AAPL.rsi14_15m\"}, {\"band\": \"FLAT\", \"path\": \"symbols.AAPL.recent_return_5m\"}, {\"band\": \"POSITIVE\", \"path\": \"symbols.AAPL.atr14_15m\"}, {\"band\": \"UNCONFIRMED\", \"path\": \"symbols.AAPL.intraday_setup_1m\"}], \"note\": \"Uptrend intact on 15m; 1m bearish engulfing unconfirmed.\", \"signal\": {\"confidence\": 0.8, \"horizon\": \"INTRADAY\", \"score\": 0.64461176, \"state\": \"SIGNAL\"}, \"symbol\": \"AAPL\"}]}",
      "error": null
    }
  ],
  "reason_codes": [],
  "notes": [
    "evidence_pack:e65c0474945a6f6f037bb4bddbb70b039a5dc54dbc8c3af5373a0494089b7c40",
    "council_run:4e0def5e-638a-53ed-b8ec-c1989778a527",
    "sizing:AAPL: 2 shares at $350.39, $1031.3788160000 after 1x on conviction_target"
  ],
  "error": null,
  "proposals_and_risk": [
    {
      "proposal": {
        "proposal_id": "475e6284-cb08-53c3-955c-dbda254219d2",
        "symbol": "AAPL",
        "side": "buy",
        "qty": 2,
        "limit_price": 350.39,
        "notional": 700.78,
        "conviction": 0.515689408
      },
      "risk": {
        "approved": true,
        "reason": "all checks passed",
        "checks": [
          {
            "name": "kill_switch_off",
            "limit": "must be running",
            "detail": "",
            "passed": true,
            "observed": "running"
          },
          {
            "name": "paper_endpoint_only",
            "limit": "paper-api.alpaca.markets",
            "detail": "",
            "passed": true,
            "observed": "paper-api.alpaca.markets"
          },
          {
            "name": "proposal_not_expired",
            "limit": ">0s left",
            "detail": "",
            "passed": true,
            "observed": "37s left"
          },
          {
            "name": "not_already_executed",
            "limit": "False",
            "detail": "",
            "passed": true,
            "observed": "False"
          },
          {
            "name": "market_open",
            "limit": "True",
            "detail": "",
            "passed": true,
            "observed": "True"
          },
          {
            "name": "trading_window",
            "limit": ">=5m after open, >10m before close",
            "detail": "",
            "passed": true,
            "observed": "299m since open, 91m to close"
          },
          {
            "name": "symbol_allowlist",
            "limit": "['AAPL']",
            "detail": "",
            "passed": true,
            "observed": "AAPL"
          },
          {
            "name": "long_only_no_oversell",
            "limit": "buy or sell<=held",
            "detail": "",
            "passed": true,
            "observed": "buy"
          },
          {
            "name": "max_order_notional",
            "limit": "$2,000.00",
            "detail": "",
            "passed": true,
            "observed": "$700.78"
          },
          {
            "name": "max_position_size",
            "limit": "$9,980.34",
            "detail": "",
            "passed": true,
            "observed": "$700.78 after fill"
          },
          {
            "name": "max_gross_exposure",
            "limit": "$49,901.69 (50.0% equity)",
            "detail": "",
            "passed": true,
            "observed": "$700.78 (0.7%)"
          },
          {
            "name": "max_daily_loss",
            "limit": "> -2.0%",
            "detail": "",
            "passed": true,
            "observed": "+0.00% today"
          },
          {
            "name": "max_orders_per_day",
            "limit": "<20",
            "detail": "",
            "passed": true,
            "observed": "0 so far"
          },
          {
            "name": "symbol_cooldown",
            "limit": ">=30m",
            "detail": "",
            "passed": true,
            "observed": "no recent order"
          },
          {
            "name": "no_conflicting_open_order",
            "limit": "0",
            "detail": "",
            "passed": true,
            "observed": "0 open/pending on AAPL"
          },
          {
            "name": "quote_fresh",
            "limit": "-1s to 15s",
            "detail": "",
            "passed": true,
            "observed": "3.78s old on the conservative clock"
          },
          {
            "name": "price_sanity",
            "limit": "<=40.0bps",
            "detail": "",
            "passed": true,
            "observed": "7.0bps from mid 350.14"
          },
          {
            "name": "clock_skew",
            "limit": "|skew|<=10.0s",
            "detail": "",
            "passed": true,
            "observed": "+0.3s vs broker clock"
          },
          {
            "name": "spread_sane",
            "limit": "<=40.0bps",
            "detail": "",
            "passed": true,
            "observed": "0.9bps (bid 350.13 / ask 350.16)"
          },
          {
            "name": "buying_power",
            "limit": "available $399,213.56",
            "detail": "",
            "passed": true,
            "observed": "need $700.78"
          },
          {
            "name": "order_error_streak",
            "limit": "<5",
            "detail": "",
            "passed": true,
            "observed": "0 consecutive rejections"
          },
          {
            "name": "entry_price_current",
            "limit": "within 40 bps of analysis ask and marketable at the original 350.39 limit",
            "detail": "Executable quote timestamp 2026-11-23T19:29:04.352301+00:00",
            "passed": true,
            "observed": "analysis ask 350.21, current 350.16, move -1.43 bps"
          },
          {
            "name": "bracket_stop_risk",
            "limit": "15",
            "detail": "",
            "passed": true,
            "observed": "4.22"
          }
        ]
      },
      "orders": [
        {
          "client_order_id": "AAPL-ORDER-3-CLIENT_ORDER_ID",
          "alpaca_order_id": "AAPL-ORDER-3-ID",
          "status": "canceled",
          "filled_qty": 1.0,
          "filled_avg_price": 350.15,
          "error": null,
          "events": [
            {
              "t": "2026-11-23T19:29:10.527016+00:00",
              "event": "pending_new",
              "status": "pending_new",
              "filled_qty": 0.0,
              "avg_price": null
            },
            {
              "t": "2026-11-23T19:29:10.529691+00:00",
              "event": "new",
              "status": "new",
              "filled_qty": 0.0,
              "avg_price": null
            },
            {
              "t": "2026-11-23T19:29:11.483849+00:00",
              "event": "partial_fill",
              "status": "partially_filled",
              "filled_qty": 1.0,
              "avg_price": 350.15
            },
            {
              "t": "2026-11-23T19:29:12.357062+00:00",
              "event": "canceled",
              "status": "canceled",
              "filled_qty": 1.0,
              "avg_price": 350.15
            },
            {
              "t": "2026-11-23T19:29:13.145612+00:00",
              "event": "reconciled",
              "status": "canceled",
              "filled_qty": 1.0,
              "avg_price": 350.15
            }
          ]
        }
      ]
    }
  ]
}
```

</details>

### 14:29:13 ET · BLOCKED_GUARD

<details>
<summary>Recorded decision evidence</summary>

```json
{
  "decision_id": "c20e2f0e-24b2-50d2-bfbd-d9ecf7336554",
  "inputs": {},
  "feature_evidence": {},
  "council_mode": null,
  "chair": null,
  "skeptic_audit": null,
  "role_outputs": [],
  "reason_codes": null,
  "notes": [
    "SCHEDULER_SKIP:halted"
  ],
  "error": "bracket parent AAPL-ORDER-3-CLIENT_ORDER_ID partially filled; verify protection for 1 shares",
  "proposals_and_risk": []
}
```

</details>

## INTC

### 14:44:01 ET · BLOCKED_GUARD

<details>
<summary>Recorded decision evidence</summary>

```json
{
  "decision_id": "538199b0-27ad-55e4-aeb7-4c9b1c87c4e6",
  "inputs": {},
  "feature_evidence": {},
  "council_mode": null,
  "chair": null,
  "skeptic_audit": null,
  "role_outputs": [],
  "reason_codes": null,
  "notes": [
    "SCHEDULER_SKIP:snapshot_deadline"
  ],
  "error": "",
  "proposals_and_risk": []
}
```

</details>

### 14:44:13 ET · DECIDED_HOLD

<details>
<summary>Recorded decision evidence</summary>

```json
{
  "decision_id": "ddb360d2-c459-50d8-b636-315cf9af4a0d",
  "inputs": {
    "as_of": "2026-11-23T19:44:04.077919Z",
    "regime": {
      "label": "uptrend"
    },
    "account": {
      "cash": 99803.06,
      "equity": 99803.06,
      "status": "ACTIVE",
      "account_id": "PAPER_ACCOUNT",
      "last_equity": 99803.39,
      "buying_power": 399212.24
    },
    "positions": [],
    "symbols": {
      "INTC": {
        "mid": 58.045,
        "rsi14": null,
        "ret_1d": -0.0783,
        "ret_5d": null,
        "ret_20d": null,
        "atr14_pct": null,
        "price_vs_sma20": null,
        "trend_sma20_vs_sma50": null
      }
    }
  },
  "feature_evidence": {
    "account_ref": "PAPER_ACCOUNT",
    "as_of": "2026-11-23T19:44:04.077919+00:00",
    "availability": {
      "account": "fresh",
      "bars": "fresh",
      "calendar": "fresh",
      "news": "fresh",
      "ok_fraction_core_features": 1.0,
      "quotes": "fresh"
    },
    "bands_hash": "810517c6e124c7ebc23ca0ebce7ef7ba7cc66b30bc21cacc66c1a221174255d4",
    "feasibility": {
      "INTC": {
        "can_buy": true,
        "can_buy_reasons": [],
        "can_sell": false,
        "can_sell_reasons": [
          "NO_SELLABLE_INVENTORY"
        ],
        "entry_window_open": true,
        "entry_window_reason": "",
        "held_qty": "0.0",
        "max_new_notional_usd": "2000.0",
        "sellable_qty": "0"
      }
    },
    "feature_slot": {
      "candles": {
        "INTC|2026-11-23T19:29:00+00:00": "0ef240a428192439bd900f32bdd8bac83462bcda6265afd44c53684595add717",
        "INTC|2026-11-23T19:30:00+00:00": "0463d928b81389008026d1c49054414c41445cfe010605dc44414d5a8006ec80",
        "INTC|2026-11-23T19:31:00+00:00": "a5309c04231b41b04749996dbc08d1d625cf986b4bacb8d065bd4272b1bcd687",
        "INTC|2026-11-23T19:32:00+00:00": "1316263235fefac976cf3179d15a341ca2faba6862bc2ad845a199a21f1a4ea1",
        "INTC|2026-11-23T19:33:00+00:00": "c37f8ccdeccf9064ac8a9b4e6a21d4ed42be7567ab3ba10eb0558b68028107c0",
        "INTC|2026-11-23T19:34:00+00:00": "564e3a869b90c07bc6f4dc36fc9a4642620456c6cac5272aff6455bd272177b1",
        "INTC|2026-11-23T19:35:00+00:00": "8c40460eb8f86125bf2228c6e0b5478931f3e3a91a013bd23caa1bb828639442",
        "INTC|2026-11-23T19:36:00+00:00": "9cb732a5a05f88fcae5944f0121aac8aaa2713bd234d104b87ddb513e8886ae9",
        "INTC|2026-11-23T19:37:00+00:00": "9d5b09f82117334dcc0f33b8c32ad04009545b4670f26997f04929a89d44df93",
        "INTC|2026-11-23T19:38:00+00:00": "e98c98af48936fd32ec6ad72041fcbfa1de8511a2b8911c69eabcd4ab7117e18",
        "INTC|2026-11-23T19:39:00+00:00": "422314eba37616c0546eed1ed8aa018f6b54ce6bec687378c7704d9ca2065248",
        "INTC|2026-11-23T19:40:00+00:00": "70e0d8b0a63b3723514998b8205402a930375f59ca5308b2f48f6dbab08cd617",
        "INTC|2026-11-23T19:41:00+00:00": "4510c4c83faf5f5878d401794d4b7bed12120a3527e7efc68be6e7a94d44c40b",
        "INTC|2026-11-23T19:42:00+00:00": "98067d1cfbe2cf62a97c2f9a655f0cf4470e9f8fb2391eb0463aff7d674dad4b",
        "INTC|2026-11-23T19:43:00+00:00": "c8d1f80659f571bf3eb64a17b9935be4ce7a092a55afd0608b149b1e717e9011",
        "SPY|2026-11-23T19:29:00+00:00": "33197b4fa46c16926d7bfccf1bc2f5b270e84406710454cbcd60f1d499677182",
        "SPY|2026-11-23T19:30:00+00:00": "501b6b54205a5fdefb7bf1b8f37d97b09bec2331a71da24c04a1e76471a3e9be",
        "SPY|2026-11-23T19:31:00+00:00": "7a616b1bec25ec89392c717c57a4f8a02b7baa240defd1ce7ed414da812d51e0",
        "SPY|2026-11-23T19:32:00+00:00": "13017eef20c793ba8a0c3bee58ceb303a749f3ed6db515430dbcd3f066266ef6",
        "SPY|2026-11-23T19:33:00+00:00": "60acf2b6b72dfb53f598542c183985e00d5820e45e6a15aaa702caa2e7db45df",
        "SPY|2026-11-23T19:34:00+00:00": "205774036f40cb4bc8e44df4d46ef150bd7d25dedeb8a897455bddc1dd4763d8",
        "SPY|2026-11-23T19:35:00+00:00": "a3f33f928527ca6cd947868e44e270cfe45857f8acf9296afd6811bf7c66a716",
        "SPY|2026-11-23T19:36:00+00:00": "20f2610f9083c52c53c44110cf31c15486c3658b74baf10c77427c7f1643e451",
        "SPY|2026-11-23T19:37:00+00:00": "cfc075a20afd9004c6a54e55e02de60aa1ac6fab559ca2bc363b4083a5a7b0e8",
        "SPY|2026-11-23T19:38:00+00:00": "8ac7b4d0dc16f15a1b48e3576c48557a2cf3e5e01e9dbd56ec12e4206987e786",
        "SPY|2026-11-23T19:39:00+00:00": "38712a0709a4972b95a52f42b45fd54896d71cc49ce48651c65445f1a42bf62f",
        "SPY|2026-11-23T19:40:00+00:00": "e49f4baca7c7583df76c009735c11448f1023f1415b68e390409997276db3480",
        "SPY|2026-11-23T19:41:00+00:00": "0dccbf44a642c7d605f69cb3858d90923162c6c2b93f66b9555d77776438a183",
        "SPY|2026-11-23T19:42:00+00:00": "88269dcad14d8b8d3584bb870bfc6f5eed07f56a971f9ad7e1037bfff28a3780",
        "SPY|2026-11-23T19:43:00+00:00": "a4aebaa6965c7c246c1610c4eff9a05d061eff2cadc3940774ca5ab43368ca06"
      },
      "close": "2026-11-23T19:44:00+00:00",
      "feed": "iex",
      "indicator_close": "2026-11-23T19:30:00+00:00",
      "indicator_input_hashes": {
        "INTC": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
        "SPY": "d68c3c2c44379ba183660d3584866bed291f0da9d6a6500fe45f1553f50dbcf7"
      },
      "provisional": true,
      "records": {
        "market:market:breadth_above_ema21": "50704960ea832fa382b78540a6b4e758f0c17d530e3a2a5af1448fc28988ef3f",
        "market:market:regime_label": "4ea4f179a9a74a88d2405c941a6d6dda76309dff50bc3fd750289f860c72e41a",
        "market:market:spy_ema_gap_bps_15m": "c50c8fdef5709515f5e5ae3ab6bee1a9b6efd70b4245899f41752cc31bc8404c",
        "market:market:spy_ret_60m": "80a98b5dc12b45ee683d82daff6f37586b1b99495862c32ce74d32de802d4ca7",
        "market:market:spy_vol_regime_ratio": "0dc5d71ebb4a6b4c5c584bea8c222659c9e4e4652708d4fd3e981efc6a2ab522",
        "symbol:INTC:adv_usd_20d": "ce1e666577b208937da1c95aeb62a5df8b9a96a01bf9a66ab4d31d2364829fcd",
        "symbol:INTC:atr14_15m": "a04dd07d3adaf66a88f302d0b309682c845e490fe70404b265f5f395fc65cf69",
        "symbol:INTC:atr14_1d": "c698626cc8689efa5ed56c4f802fac79545a78a74f9171f8dbbc9a26d301b47f",
        "symbol:INTC:atr14_pct": "e4afa6f467282d09ba82197839010e95f59cb6a549d7209c972325945d9ebd4e",
        "symbol:INTC:dist_hi_atr": "323ae4cb1d3b6c1f857cf15dec8d34dd88ac38363f5ec4b93005f5c9d226f69a",
        "symbol:INTC:dist_lo_atr": "655db91230a7eb34a08033210852e228bc68058b300a01a01d4cf14275a44a03",
        "symbol:INTC:ema21_15m": "ba97926e62de0cff36a86f08508099a604e97fcab381706f538c52dc1879c5b3",
        "symbol:INTC:ema9_15m": "f838d073506d19368278c646bedce442edf58a3a6ff558766313a2f84fbccac4",
        "symbol:INTC:ema_gap_bps_15m": "6ad276b288293a2aef55d7ac30ec1f64c04f995ebe3f416fe991b659c6c9e6da",
        "symbol:INTC:gap_open_pct": "dda3fb0cfeec70307cec37add180eb8daa3068c58a3a7b4e2ca022d7927efd99",
        "symbol:INTC:intraday_ret_1h": "b2e79255cd006121a62c025c7f322388660e72bc4fda0de47f6f4f06e0e9a248",
        "symbol:INTC:intraday_setup_1m": "dc0daa61c227c02df51569e97c909cc506265a257515597aafd7100cad09193d",
        "symbol:INTC:last_close": "9ee0f1ed19fd6d1425a4480a83d8b266de5cd8016bc801d2a1d8a37530578f18",
        "symbol:INTC:macd_hist_15m": "94a0fae8aee25d17a80259f03c68d1dcd4ba7e8deff7af2f594cf6b4250b43f5",
        "symbol:INTC:price_vs_sma20": "3b815f0120949286e4d62554b69f79c41228a4f490eaf91f588d03b76e4dbb6b",
        "symbol:INTC:recent_price_10m": "242f0b0574eb9006315825ffb7817e63471c84a33bb7de7f96d9536c4460a8b0",
        "symbol:INTC:recent_range_bps_10m": "707df35ba490ed1159f794efb6d9212f566887d1bfc756c882cc2844701d3d4a",
        "symbol:INTC:recent_range_bps_5m": "c63a3d5f86f30e9602e7200edaf045b3898c71a4359abf16d19f33d02955fd81",
        "symbol:INTC:recent_return_10m": "339b510b555b33df8cab480fcf1929d820a50f35b71beef851efcb75c6a22707",
        "symbol:INTC:recent_return_5m": "66374b670eea86567e7ee504e4769c814d867e5407c97729cd244e2673a1a2b4",
        "symbol:INTC:recent_volume_10m": "106e5de2cb33ceab6cf79251bfd9adc4074025f47fb045ad29b5ac2c5eb66715",
        "symbol:INTC:recent_volume_5m": "5e5b2f43e392a2185b7ddcf1cf6299e1c422c9330bee430010dd49517b3d0e97",
        "symbol:INTC:relstr_spy_60m": "2ed64248bd67ba569bd03628b431cbfad1a941a9f3385d3341807440da2423de",
        "symbol:INTC:ret_15m": "9946d60182294ba581b871d8ab3b2330ede8a3eb5382f90c63dcd2792684b0ee",
        "symbol:INTC:ret_1d": "c03200498b1fd16a0fc86a4cda771e452df901d525eb7c4956de0de37aae08df",
        "symbol:INTC:ret_20d": "02da53f5a51cbb614819906748f35303c6b58a555dbd7ce9f592b8bd5674f768",
        "symbol:INTC:ret_5d": "31eb11e3b5586e23fae13c8a611493c29245105c225fbefa1f01f12e3f21ae92",
        "symbol:INTC:ret_5m": "3a903c6c5613922944a3bf6d4122f2d3b35b8c9b653565a1d618fcbafec3ddef",
        "symbol:INTC:ret_60m": "de5210040d5b927124ba5a30f3470c2fb9ae0e93e05b1af14ddd37b89d3773ef",
        "symbol:INTC:rsi14": "2bd3d0c217fcf205f4d7e703b3413e7a5f2dfcd3d74344dbc8a2615aaf7de968",
        "symbol:INTC:rsi14_15m": "b6e1bbe2865d66bc959a6a62ac43cbc49df30df471232dcdcb033a4d376d0b5e",
        "symbol:INTC:rvol_60m": "ef0442b7457060657193243bf8fa383d63572ca06c650db08626448a09882509",
        "symbol:INTC:sma20": "1db5ee840cb65d9c0a774ec7773659ac4cdf0a90ededbf84354942b04efd675d",
        "symbol:INTC:sma50": "5d86bf450bcb518132c4974e86f45d754cc9d6bf9fd01ea4f1b7decb8f2c732c",
        "symbol:INTC:trend_sma20_vs_sma50": "02b88ca0591c15d796f15609f4368adafa5ce2a3053bd5592cac32fd4cc6cd74",
        "symbol:INTC:vol_regime_ratio": "9a8a2784d803faa13d7e6552e64003d88543e7beadd90ccb0535fceb5b5b5528",
        "symbol:INTC:volume_z20": "3e57c55e843620f6cc1ffce34396913662774ae15edd605dcd30caa05a79dc6e",
        "symbol:INTC:volz_tod_15m": "6357f953d8cc92e3e80a433273ff6a32d1e591721344832d0ea2cd18c99252af",
        "symbol:INTC:vwap_dev_session": "de97bca340fb27b21c3098027c60e13087478364211afa9fbd9178f65161fab3",
        "symbol:SPY:adv_usd_20d": "bee5050d596f37fbbc68c4ffb6118892df59be6ba571fadac7054642cee745fd",
        "symbol:SPY:atr14_15m": "0bb8dc9dee158f1497c2aa0f70dea71a870732b8066e09caa016184f1c85ceed",
        "symbol:SPY:atr14_1d": "b223fefa968d72305897b0e2122b9b53d272c5c137c5e5e185d961fe4bfe27b0",
        "symbol:SPY:atr14_pct": "07ae82185d6e50b4a2360150143f741785378ceb4fa45837f60989ac8defdfdf",
        "symbol:SPY:dist_hi_atr": "48d9576772e34b6a53a389c61dca9a022bbe076f3e7c3dfa776d0cbd8e392138",
        "symbol:SPY:dist_lo_atr": "d27f7a09aa03dcea3bb97bea72cd3d610012bfd45948e71cce890c4d8528597d",
        "symbol:SPY:ema21_15m": "c2c8c91103f9f5391b73c06538b1912f99ce1b0da29297a969a42ca05e02b9de",
        "symbol:SPY:ema9_15m": "9b4b625a92218819a32ecdec9143352fc5ec6f550f3f864954f12fe7bded8ef6",
        "symbol:SPY:ema_gap_bps_15m": "513d40a2c8d7871c4bce2fe81c86eac3416ca070b2d411c6514cddf61d2d00aa",
        "symbol:SPY:gap_open_pct": "21db07548d420d39ab255f4ebea567f6fe116bb61c0b61a271b951b6282e9f2e",
        "symbol:SPY:intraday_ret_1h": "52519d93be8450353a62e49900c235de6114a928a1e60ef91ea6a05e2af6177b",
        "symbol:SPY:intraday_setup_1m": "6b682f965ce64904bd8bf026897a12440092a3967f1a9e1f53a35006fa246e1a",
        "symbol:SPY:last_close": "a860aa2e0c3b7965fc25fcaa2d232e8a4bf7d06df12bd6db3bcbe7eb3c614900",
        "symbol:SPY:macd_hist_15m": "69230fa416b6ffd6fd80aa9f1363362cc72763ffff11640eb78ad479d83713cf",
        "symbol:SPY:price_vs_sma20": "13013469dfc5c29976303912105c546b1a9e303d6635f2ac01719f86934b429b",
        "symbol:SPY:recent_price_10m": "f52f961c7468f8b6df7f6aa4ba4ffe6e8deac613c04d14d09f9cbaebb630d31c",
        "symbol:SPY:recent_range_bps_10m": "953d8b9417add331e0203fce8f30319f0b63220f3cdbb4c467fe6966689c578d",
        "symbol:SPY:recent_range_bps_5m": "dcf907648df389576a49f5796da34bf09b002310c5996f3cef6edd35bf78d3a4",
        "symbol:SPY:recent_return_10m": "a63566ee20a3669145981aadd2c7792e2008b895bad034a7ce1a892ff61da6c7",
        "symbol:SPY:recent_return_5m": "3cf2185d43f7df1fae86a5cfa9ee935d496a5d6b6f0988d8d9d9e4003cc02899",
        "symbol:SPY:recent_volume_10m": "b1b58e57c8b8b788dc514ccb7f0d2ae86a01a50dd8653c67ccd423098f2fe5a4",
        "symbol:SPY:recent_volume_5m": "761e954c98913b37c90c911c1abd60cdda18eb9d16f26ba84a2c31588fe739a7",
        "symbol:SPY:relstr_spy_60m": "fc2975e576a0a10aa3b0f0d5ea4e7a65c4f12f47429e26dfbe085bbbc39a46c2",
        "symbol:SPY:ret_15m": "31909647c5a41389fd810bf532119eaec357161f876e79743a7240c198eabd1b",
        "symbol:SPY:ret_1d": "ccb25f32b26bce72f90a6f6bfed9b2ba81a8faaeffe8e125f3773ecd19c010e8",
        "symbol:SPY:ret_20d": "ac555858f2d819ebd191dab8bca8c387b385e880811730834c5d9b05f65b67ef",
        "symbol:SPY:ret_5d": "765ef1f53449f8d7b8f95370416d18aced13856339824b5f732f7b3bbadf87a0",
        "symbol:SPY:ret_5m": "58ce051440369e213db2a6906f3f40d1e7338d982a3e9bd010c8b79b104f058c",
        "symbol:SPY:ret_60m": "62f76c8bf9cefdd1058c73ede5edbe3b18a4376ae3f282a532bdab0cb794b48c",
        "symbol:SPY:rsi14": "80e58956e7c514a92d4ca890850fa7116ca3b59cd77d10f67da14e7f7a90fda1",
        "symbol:SPY:rsi14_15m": "db40982ed89cf4c5122b1c914cd273e040f4abfd03e37c84567eade7890b74e3",
        "symbol:SPY:rvol_60m": "1f63a5f48471cd258783fdaf500ccc5da1ddc019f53525657fbf3c9ccad841ab",
        "symbol:SPY:sma20": "a5c9d0a02e10ef601561e643f17144fac85b918b8523f4d3b70f582a946d7e15",
        "symbol:SPY:sma50": "c13ab7ea28b0c4396e96fd4babd497cc757a7b80e3e6071bc5c1561374c0994e",
        "symbol:SPY:trend_sma20_vs_sma50": "6ec24827b7fca4383aaaa52e89463ff126b487160e5cac66ef58c3d467d1a77f",
        "symbol:SPY:vol_regime_ratio": "19d289d0d43d3bef0a84a0210ca0be942d98ce9317dbae2ce28c94a5473fb381",
        "symbol:SPY:volume_z20": "f5d03b4e8a322c12274ca8902f8b20e483d1dca0a0a5897a67340f2e2a6e7519",
        "symbol:SPY:volz_tod_15m": "fa1c316c765ce73d24940dcd05a552019e16d54c89d8840446249723df6323af",
        "symbol:SPY:vwap_dev_session": "d1d85229bffead85c4257358aa94522cdcd1cb4293d14bad5f7cf84d7c0a23bb"
      },
      "symbols": [
        "INTC",
        "SPY"
      ]
    },
    "horizons": {
      "INTC": {
        "10m": {
          "age_s": 4.077919,
          "last_bar_end": "2026-11-23T19:44:00+00:00",
          "status": "OK"
        },
        "15m": {
          "age_s": 844.077919,
          "last_bar_end": "2026-11-23T19:30:00+00:00",
          "status": "OK"
        },
        "5m": {
          "age_s": 4.077919,
          "last_bar_end": "2026-11-23T19:44:00+00:00",
          "status": "OK"
        },
        "60m": {
          "age_s": 844.077919,
          "last_bar_end": "2026-11-23T19:30:00+00:00",
          "status": "OK"
        },
        "horizon_conflict": false
      }
    },
    "market": {
      "breadth_above_ema21": {
        "age_s": 844.077919,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "50704960ea832fa382b78540a6b4e758f0c17d530e3a2a5af1448fc28988ef3f",
        "status": "OK",
        "v": 1.0,
        "version": "1.1dfe664d"
      },
      "minutes_to_close": {
        "age_s": 0.709764,
        "quality": {},
        "record_hash": "33841cf92cd2ccb73a977a4e69c1577e87f3157c95022e490f8803e71987136b",
        "status": "OK",
        "v": 75.94386408,
        "version": "1.e79b1ead"
      },
      "regime_label": {
        "age_s": 844.077919,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "4ea4f179a9a74a88d2405c941a6d6dda76309dff50bc3fd750289f860c72e41a",
        "status": "OK",
        "v": "UPTREND",
        "version": "1.f8b361d7"
      },
      "session_phase": {
        "age_s": 0.709764,
        "quality": {},
        "record_hash": "12adebbe0b95a2e3190604c28e038f318806028e900c229c871431d0a123b132",
        "status": "OK",
        "v": "NORMAL",
        "version": "1.91f88fe8"
      },
      "spy_ema_gap_bps_15m": {
        "age_s": 844.077919,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "c50c8fdef5709515f5e5ae3ab6bee1a9b6efd70b4245899f41752cc31bc8404c",
        "status": "OK",
        "v": 43.87101558,
        "version": "1.fda7da7a"
      },
      "spy_ret_60m": {
        "age_s": 844.077919,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "80a98b5dc12b45ee683d82daff6f37586b1b99495862c32ce74d32de802d4ca7",
        "status": "OK",
        "v": -0.001191069747,
        "version": "1.9feddbd1"
      },
      "spy_vol_regime_ratio": {
        "age_s": 844.077919,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "0dc5d71ebb4a6b4c5c584bea8c222659c9e4e4652708d4fd3e981efc6a2ab522",
        "status": "OK",
        "v": 1.423269695,
        "version": "1.3b7257aa"
      }
    },
    "meta": {
      "news": {
        "INTC": {
          "effective_weight": 0,
          "in_window": 0,
          "newest_age_min": 1782.617965,
          "policy": "48h retained; per-article decay and minimum relevance; 4h count is descriptive",
          "poller_last_ok_age_s": 13.243037,
          "retrieved": 1,
          "selected": 0,
          "state": "QUIET",
          "window_min": 240
        }
      }
    },
    "news_blob_hash": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
    "news_context_blob_hash": "ef023692226f6319baf7f6429f023deb1a988f59c953b103e7a5f425a6a5d062",
    "portfolio": {
      "aggregate_cap_usd": {
        "age_s": 0.709764,
        "quality": {},
        "record_hash": "1b253abf2c9c16507b21fc2978362af4e0d3eb0f006efc51feb33834e8928787",
        "status": "OK",
        "v": "49901.530",
        "version": "1.5b3d1daf"
      },
      "aggregate_headroom_usd": {
        "age_s": 0.709764,
        "quality": {},
        "record_hash": "acacbdb0d573ed3204119d57e5c88a558a826682c9b971a8c1968231c3e57701",
        "status": "OK",
        "v": "49901.530",
        "version": "1.7f894fff"
      },
      "buying_power": {
        "age_s": 0.709764,
        "quality": {},
        "record_hash": "6bb6c7174058eac178acc5d1b2ae5fa1b7ec6ef9629387233333403122b69a6b",
        "status": "OK",
        "v": "399212.24",
        "version": "1.74948dec"
      },
      "cash": {
        "age_s": 0.709764,
        "quality": {},
        "record_hash": "67ba9018d2f80f30730f20122fd156a0e17274373f3eea0c2620ede797459a6b",
        "status": "OK",
        "v": "99803.06",
        "version": "1.b067f5e3"
      },
      "day_pnl_pct": {
        "age_s": 0.709764,
        "quality": {},
        "record_hash": "32052f85a5ad7a7cc355f6ecd74c0fda8bdfcd3f2d3929a51bccc43dde2db1ef",
        "status": "OK",
        "v": "-0.0003306500911441986088849300",
        "version": "1.35e81852"
      },
      "drawdown_pct": {
        "age_s": 0.709764,
        "quality": {},
        "record_hash": "3a7d4ced7b3c38bfc2d8da81766c1c362f0cf85ce60b1e5ebd5d4627371b06af",
        "status": "MISSING",
        "v": null,
        "version": "1.19aac9ba"
      },
      "equity": {
        "age_s": 0.709764,
        "quality": {},
        "record_hash": "3835728f9e028f3178f63f698f15d681705b85b68404a9c9c87a246f6bfd0e51",
        "status": "OK",
        "v": "99803.06",
        "version": "1.a2192616"
      },
      "gross_exposure_pct": {
        "age_s": 0.709764,
        "quality": {},
        "record_hash": "742ce47121f14555cce4c121db20961fb25752a9f13d8d57011c87579b00f50f",
        "status": "OK",
        "v": "0E+2",
        "version": "1.b82cc518"
      },
      "gross_exposure_usd": {
        "age_s": 0.709764,
        "quality": {},
        "record_hash": "9a007e6c02dc405294b027a8e6e66f36f81bbde5b367ab40437c35f4713f5284",
        "status": "OK",
        "v": "0",
        "version": "1.e4c8752b"
      },
      "last_reconcile_age_s": {
        "age_s": 0.709764,
        "quality": {},
        "record_hash": "456d420166421e48f786c2504c4efeec61990fa7ead3c379117cc079cbd0806f",
        "status": "OK",
        "v": 0,
        "version": "1.5ed0382f"
      },
      "open_buy_notional_usd": {
        "age_s": 0.709764,
        "quality": {},
        "record_hash": "a572695be89a1352b58c79090129fa2ad501b7276db26ba4f0cfabe89a798fdc",
        "status": "OK",
        "v": "0",
        "version": "1.0bd0ead1"
      },
      "open_orders": {
        "age_s": 0.709764,
        "quality": {},
        "record_hash": "d5b2dd7b8389a0ac99ac479afbdb13c16dc1374decd64fc01ed000a4b0e67a8d",
        "status": "OK",
        "v": [],
        "version": "1.1cf37cbf"
      },
      "open_orders_count": {
        "age_s": 0.709764,
        "quality": {},
        "record_hash": "6ff4bc7db23a40fa1f02e9149a59f9948df77adce796e30d4bcb6c6775c73401",
        "status": "OK",
        "v": 0,
        "version": "1.1db4227a"
      },
      "pending_reserved_usd": {
        "age_s": 0.709764,
        "quality": {},
        "record_hash": "c9162480730ec104198abc39b0a8a21145bc46f03bcc40f037d120704dba2bfe",
        "status": "OK",
        "v": "0",
        "version": "1.1c3e9604"
      },
      "positions": {
        "age_s": 0.709764,
        "quality": {},
        "record_hash": "5eb0b70d1088fcbacd42f6562c9f7425dc8257fe48e6f9c2affe38b7a8c9c87e",
        "status": "OK",
        "v": [],
        "version": "1.c3284657"
      }
    },
    "registry_hash": "0fd3271269748046863b2f0558e45e2c333bb352eccc9899b7ff42277c8386fc",
    "schema_version": 1,
    "symbols": {
      "INTC": {
        "adv_usd_20d": {
          "age_s": 254644.0779,
          "quality": {
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "last_session": "2026-11-20"
          },
          "record_hash": "ce1e666577b208937da1c95aeb62a5df8b9a96a01bf9a66ab4d31d2364829fcd",
          "status": "OK",
          "v": 304793568.9,
          "version": "1.04f5e91f"
        },
        "ask_px": {
          "age_s": 1.957619,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "f42776e7ddfe05bfd9cb4a5e7dc7e57f3d213ebf432a561da0af506141e031c7",
          "status": "OK",
          "v": 58.05,
          "version": "1.d21cdd09"
        },
        "atr14_15m": {
          "age_s": 844.077919,
          "quality": {
            "bar_density": 0.999689441,
            "completeness": 1.0,
            "expected_minutes": 9660,
            "feed": "iex",
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9657,
            "verified_none": 3,
            "window_end": "2026-11-23T19:30:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "a04dd07d3adaf66a88f302d0b309682c845e490fe70404b265f5f395fc65cf69",
          "status": "OK",
          "v": 0.784725962,
          "version": "1.0cd14e73"
        },
        "atr14_1d": {
          "age_s": 254644.0779,
          "quality": {
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "last_session": "2026-11-20"
          },
          "record_hash": "c698626cc8689efa5ed56c4f802fac79545a78a74f9171f8dbbc9a26d301b47f",
          "status": "MISSING",
          "v": null,
          "version": "1.65e38f4c"
        },
        "atr14_pct": {
          "age_s": 254644.0779,
          "quality": {
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "last_session": "2026-11-20"
          },
          "record_hash": "e4afa6f467282d09ba82197839010e95f59cb6a549d7209c972325945d9ebd4e",
          "status": "MISSING",
          "v": null,
          "version": "1.87450ee9"
        },
        "bid_px": {
          "age_s": 1.957619,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "f36bf25b449369351619ba442d826a201b81ed8a67064df939632732418a9763",
          "status": "OK",
          "v": 58.04,
          "version": "1.149628cd"
        },
        "dist_hi_atr": {
          "age_s": 844.077919,
          "quality": {
            "bar_density": 0.999689441,
            "completeness": 1.0,
            "expected_minutes": 9660,
            "feed": "iex",
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9657,
            "verified_none": 3,
            "window_end": "2026-11-23T19:30:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "323ae4cb1d3b6c1f857cf15dec8d34dd88ac38363f5ec4b93005f5c9d226f69a",
          "status": "OK",
          "v": -1.892380362,
          "version": "1.913ffc4a"
        },
        "dist_lo_atr": {
          "age_s": 844.077919,
          "quality": {
            "bar_density": 0.999689441,
            "completeness": 1.0,
            "expected_minutes": 9660,
            "feed": "iex",
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9657,
            "verified_none": 3,
            "window_end": "2026-11-23T19:30:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "655db91230a7eb34a08033210852e228bc68058b300a01a01d4cf14275a44a03",
          "status": "OK",
          "v": 1.720345784,
          "version": "1.79ba4c70"
        },
        "ema21_15m": {
          "age_s": 844.077919,
          "quality": {
            "bar_density": 0.999689441,
            "completeness": 1.0,
            "expected_minutes": 9660,
            "feed": "iex",
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9657,
            "verified_none": 3,
            "window_end": "2026-11-23T19:30:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "ba97926e62de0cff36a86f08508099a604e97fcab381706f538c52dc1879c5b3",
          "status": "OK",
          "v": 57.34035358,
          "version": "1.bfcac61e"
        },
        "ema9_15m": {
          "age_s": 844.077919,
          "quality": {
            "bar_density": 0.999689441,
            "completeness": 1.0,
            "expected_minutes": 9660,
            "feed": "iex",
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9657,
            "verified_none": 3,
            "window_end": "2026-11-23T19:30:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "f838d073506d19368278c646bedce442edf58a3a6ff558766313a2f84fbccac4",
          "status": "OK",
          "v": 58.09960497,
          "version": "1.81255de8"
        },
        "ema_gap_bps_15m": {
          "age_s": 844.077919,
          "quality": {
            "bar_density": 0.999689441,
            "completeness": 1.0,
            "expected_minutes": 9660,
            "feed": "iex",
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9657,
            "verified_none": 3,
            "window_end": "2026-11-23T19:30:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "6ad276b288293a2aef55d7ac30ec1f64c04f995ebe3f416fe991b659c6c9e6da",
          "status": "OK",
          "v": 132.4113546,
          "version": "1.d4519f3c"
        },
        "gap_open_pct": {
          "age_s": 844.077919,
          "quality": {
            "bar_density": 0.999689441,
            "completeness": 1.0,
            "expected_minutes": 9660,
            "feed": "iex",
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9657,
            "verified_none": 3,
            "window_end": "2026-11-23T19:30:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "dda3fb0cfeec70307cec37add180eb8daa3068c58a3a7b4e2ca022d7927efd99",
          "status": "MISSING",
          "v": null,
          "version": "1.27438d4d"
        },
        "halted": {
          "age_s": 0.709764,
          "quality": {},
          "record_hash": "e21498e5241ca85703517771283f7d8dee53055c7b8a949a0cc19b448cecc11b",
          "status": "OK",
          "v": false,
          "version": "1.22c5cf87"
        },
        "held_minutes": {
          "age_s": 0.709764,
          "quality": {},
          "record_hash": "79dfea3655a37557867e6feba0143a81a45b88a3e6dfff28f4b329a666196a62",
          "status": "MISSING",
          "v": null,
          "version": "1.de6ed6d3"
        },
        "intraday_ret_1h": {
          "age_s": 844.077919,
          "quality": {
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "last_session": "2026-11-20"
          },
          "record_hash": "b2e79255cd006121a62c025c7f322388660e72bc4fda0de47f6f4f06e0e9a248",
          "status": "OK",
          "v": 0.006454388985,
          "version": "1.c3bb7751"
        },
        "intraday_setup_1m": {
          "age_s": 4.077919,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "5b5fe02db85257dfca995fad217fa09e46b58a213cd60952a1e25088abf2758d",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:44:00+00:00",
            "window_start": "2026-11-23T19:34:00+00:00"
          },
          "record_hash": "dc0daa61c227c02df51569e97c909cc506265a257515597aafd7100cad09193d",
          "status": "OK",
          "v": {
            "confirmation": "UNCONFIRMED",
            "pattern": "DOJI",
            "prior_trend": "FLAT",
            "range_break": "INSIDE",
            "range_ceiling": 58.315,
            "range_floor": 58.01,
            "setup_minute": 9,
            "volume_ratio": 0.6727
          },
          "version": "1.2a1f51e0"
        },
        "last_close": {
          "age_s": 254644.0779,
          "quality": {
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "last_session": "2026-11-20"
          },
          "record_hash": "9ee0f1ed19fd6d1425a4480a83d8b266de5cd8016bc801d2a1d8a37530578f18",
          "status": "MISSING",
          "v": null,
          "version": "1.f2485fc2"
        },
        "luld_active": {
          "age_s": 0.709764,
          "quality": {},
          "record_hash": "06475791144b972af1051ec9dc2c302fb7a65ab2531e92e0effc938157e5d89f",
          "status": "MISSING",
          "v": null,
          "version": "1.84a715b2"
        },
        "macd_hist_15m": {
          "age_s": 844.077919,
          "quality": {
            "bar_density": 0.999689441,
            "completeness": 1.0,
            "expected_minutes": 9660,
            "feed": "iex",
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9657,
            "verified_none": 3,
            "window_end": "2026-11-23T19:30:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "94a0fae8aee25d17a80259f03c68d1dcd4ba7e8deff7af2f594cf6b4250b43f5",
          "status": "OK",
          "v": -0.04229123984,
          "version": "1.391617c8"
        },
        "mid_px": {
          "age_s": 1.957619,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "4100a9bf75b1de130a8c796de39f78d79f2a28d6f475761e3a80628cf0de2745",
          "status": "OK",
          "v": 58.045,
          "version": "1.d567a349"
        },
        "news_age_min_latest": {
          "age_s": 13.243037,
          "quality": {},
          "record_hash": "73b1e9b2ab28955f6c832e695bdbb8d796ff5d9df27cdad99ff2329a87d68887",
          "status": "MISSING",
          "v": null,
          "version": "1.d0f79dc8"
        },
        "news_confirmed": {
          "age_s": 0,
          "quality": {
            "source": "stored news and pinned price features"
          },
          "status": "OK",
          "v": false,
          "version": "news-confirmation-v2"
        },
        "news_count_1h": {
          "age_s": 13.243037,
          "quality": {},
          "record_hash": "32dc2efdce706e9b1e30d4d62fce5acc2dd96192db65a927c6691679d353cabb",
          "status": "OK",
          "v": 0,
          "version": "1.0c9362fe"
        },
        "news_count_48h": {
          "age_s": 13.243037,
          "quality": {
            "as_of": "2026-11-23T19:44:04.077919+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 1,
          "version": "news-context-v2"
        },
        "news_count_4h": {
          "age_s": 13.243037,
          "quality": {
            "as_of": "2026-11-23T19:44:04.077919+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 0,
          "version": "news-context-v2"
        },
        "news_effective_sentiment": {
          "age_s": 0,
          "quality": {
            "selected": 0,
            "source": "decayed stored article metadata"
          },
          "status": "MISSING",
          "v": 0.0,
          "version": "news-decay-v2"
        },
        "news_event_flags_4h": {
          "age_s": 13.243037,
          "quality": {},
          "record_hash": "6e91cc697cadaccb57e268ceab90c6e6fc8bf4522116adcd6d486b83ac8bccdf",
          "status": "OK",
          "v": [],
          "version": "1.0b5a8a44"
        },
        "news_max_materiality_4h": {
          "age_s": 13.243037,
          "quality": {},
          "record_hash": "386e7cb4c1dff86f3090546b42ae131241f7ceba6d8907ec620500608d967f0c",
          "status": "OK",
          "v": 0,
          "version": "1.9c45e9b4"
        },
        "news_newest_age_min": {
          "age_s": 13.243037,
          "quality": {
            "as_of": "2026-11-23T19:44:04.077919+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 1782.617965,
          "version": "news-context-v2"
        },
        "news_novelty_max_4h": {
          "age_s": 13.243037,
          "quality": {},
          "record_hash": "325ca3da5413a421c89e70b51680668901c8cb97d0a7dedc3de8f06b259e6e7f",
          "status": "OK",
          "v": false,
          "version": "1.15ceb7bf"
        },
        "news_sent_ewm_240m": {
          "age_s": 13.243037,
          "quality": {},
          "record_hash": "0a40341784d4e70da3841511e66750a8f38dc37480e843a9398839b1c7e61eb4",
          "status": "OK",
          "v": 0,
          "version": "1.9cad993f"
        },
        "news_sent_ewm_60m": {
          "age_s": 13.243037,
          "quality": {},
          "record_hash": "f0b12a900e94a6dc98ce43ce8ea3056a9561252296ac0603e383e42b5ae90b44",
          "status": "OK",
          "v": 0,
          "version": "1.74ab70c1"
        },
        "news_source_div_4h": {
          "age_s": 13.243037,
          "quality": {},
          "record_hash": "527d41e18d5e568d30b0e5099be3a9c02e4c9d37d454d7b2b80cd159c38d3296",
          "status": "OK",
          "v": 0,
          "version": "1.6fd469c4"
        },
        "position_qty": {
          "age_s": 0.709764,
          "quality": {},
          "record_hash": "bd4b49fd2da6cc53a136a48b24ca9ce029cc53494e9f4df59ff1037dda6b44b3",
          "status": "OK",
          "v": "0",
          "version": "1.3a512120"
        },
        "position_value_usd": {
          "age_s": 0.709764,
          "quality": {},
          "record_hash": "610c64ae5d91f81d990f2556bde5068576186afc6269d9a17ff2c4947e542b02",
          "status": "OK",
          "v": "0",
          "version": "1.9100bec4"
        },
        "price_vs_sma20": {
          "age_s": 254644.0779,
          "quality": {
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "last_session": "2026-11-20"
          },
          "record_hash": "3b815f0120949286e4d62554b69f79c41228a4f490eaf91f588d03b76e4dbb6b",
          "status": "MISSING",
          "v": null,
          "version": "1.a986b9cc"
        },
        "recent_price_10m": {
          "age_s": 4.077919,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "5b5fe02db85257dfca995fad217fa09e46b58a213cd60952a1e25088abf2758d",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:44:00+00:00",
            "window_start": "2026-11-23T19:34:00+00:00"
          },
          "record_hash": "242f0b0574eb9006315825ffb7817e63471c84a33bb7de7f96d9536c4460a8b0",
          "status": "OK",
          "v": {
            "candles": [
              [
                0,
                58.3,
                58.315,
                58.235,
                58.235,
                13176.0,
                "VERIFIED_BAR"
              ],
              [
                1,
                58.255,
                58.305,
                58.25,
                58.305,
                2250.0,
                "VERIFIED_BAR"
              ],
              [
                2,
                58.255,
                58.255,
                58.145,
                58.15,
                5368.0,
                "VERIFIED_BAR"
              ],
              [
                3,
                58.16,
                58.175,
                58.05,
                58.08,
                12906.0,
                "VERIFIED_BAR"
              ],
              [
                4,
                58.085,
                58.13,
                58.045,
                58.045,
                3139.0,
                "VERIFIED_BAR"
              ],
              [
                5,
                58.045,
                58.165,
                58.045,
                58.095,
                12394.0,
                "VERIFIED_BAR"
              ],
              [
                6,
                58.095,
                58.19,
                58.045,
                58.185,
                11202.0,
                "VERIFIED_BAR"
              ],
              [
                7,
                58.21,
                58.21,
                58.065,
                58.07,
                11493.0,
                "VERIFIED_BAR"
              ],
              [
                8,
                58.07,
                58.095,
                58.01,
                58.01,
                9725.0,
                "VERIFIED_BAR"
              ],
              [
                9,
                58.03,
                58.09,
                58.03,
                58.03,
                7536.0,
                "VERIFIED_BAR"
              ]
            ],
            "columns": [
              "minute_offset",
              "open",
              "high",
              "low",
              "close",
              "volume",
              "coverage"
            ],
            "feed": "iex",
            "window_end": "2026-11-23T19:44:00+00:00",
            "window_start": "2026-11-23T19:34:00+00:00",
            "windows": {
              "10m": {
                "close": 58.03,
                "open": 58.3,
                "range_bps": 52.31560892,
                "return": -0.004631217839,
                "status": "OK",
                "volume": 89189.0
              },
              "5m": {
                "close": 58.03,
                "open": 58.045,
                "range_bps": 34.4560255,
                "return": -0.0002584201912,
                "status": "OK",
                "volume": 52350.0
              }
            }
          },
          "version": "1.b12384d7"
        },
        "recent_range_bps_10m": {
          "age_s": 4.077919,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "5b5fe02db85257dfca995fad217fa09e46b58a213cd60952a1e25088abf2758d",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:44:00+00:00",
            "window_start": "2026-11-23T19:34:00+00:00"
          },
          "record_hash": "707df35ba490ed1159f794efb6d9212f566887d1bfc756c882cc2844701d3d4a",
          "status": "OK",
          "v": 52.31560892,
          "version": "1.b7dd2e6e"
        },
        "recent_range_bps_5m": {
          "age_s": 4.077919,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "5b5fe02db85257dfca995fad217fa09e46b58a213cd60952a1e25088abf2758d",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:44:00+00:00",
            "window_start": "2026-11-23T19:34:00+00:00"
          },
          "record_hash": "c63a3d5f86f30e9602e7200edaf045b3898c71a4359abf16d19f33d02955fd81",
          "status": "OK",
          "v": 34.4560255,
          "version": "1.860a2856"
        },
        "recent_return_10m": {
          "age_s": 4.077919,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "5b5fe02db85257dfca995fad217fa09e46b58a213cd60952a1e25088abf2758d",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:44:00+00:00",
            "window_start": "2026-11-23T19:34:00+00:00"
          },
          "record_hash": "339b510b555b33df8cab480fcf1929d820a50f35b71beef851efcb75c6a22707",
          "status": "OK",
          "v": -0.004631217839,
          "version": "1.03c04840"
        },
        "recent_return_5m": {
          "age_s": 4.077919,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "5b5fe02db85257dfca995fad217fa09e46b58a213cd60952a1e25088abf2758d",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:44:00+00:00",
            "window_start": "2026-11-23T19:34:00+00:00"
          },
          "record_hash": "66374b670eea86567e7ee504e4769c814d867e5407c97729cd244e2673a1a2b4",
          "status": "OK",
          "v": -0.0002584201912,
          "version": "1.a9090b46"
        },
        "recent_volume_10m": {
          "age_s": 4.077919,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "5b5fe02db85257dfca995fad217fa09e46b58a213cd60952a1e25088abf2758d",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:44:00+00:00",
            "window_start": "2026-11-23T19:34:00+00:00"
          },
          "record_hash": "106e5de2cb33ceab6cf79251bfd9adc4074025f47fb045ad29b5ac2c5eb66715",
          "status": "OK",
          "v": 89189.0,
          "version": "1.891ed5cd"
        },
        "recent_volume_5m": {
          "age_s": 4.077919,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "5b5fe02db85257dfca995fad217fa09e46b58a213cd60952a1e25088abf2758d",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:44:00+00:00",
            "window_start": "2026-11-23T19:34:00+00:00"
          },
          "record_hash": "5e5b2f43e392a2185b7ddcf1cf6299e1c422c9330bee430010dd49517b3d0e97",
          "status": "OK",
          "v": 52350.0,
          "version": "1.c7331f02"
        },
        "relstr_spy_60m": {
          "age_s": 844.077919,
          "quality": {
            "bar_density": 0.999689441,
            "completeness": 1.0,
            "expected_minutes": 9660,
            "feed": "iex",
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9657,
            "verified_none": 3,
            "window_end": "2026-11-23T19:30:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "2ed64248bd67ba569bd03628b431cbfad1a941a9f3385d3341807440da2423de",
          "status": "OK",
          "v": 0.0009326495556,
          "version": "1.c04b464c"
        },
        "ret_15m": {
          "age_s": 844.077919,
          "quality": {
            "bar_density": 0.999689441,
            "completeness": 1.0,
            "expected_minutes": 9660,
            "feed": "iex",
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9657,
            "verified_none": 3,
            "window_end": "2026-11-23T19:30:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "9946d60182294ba581b871d8ab3b2330ede8a3eb5382f90c63dcd2792684b0ee",
          "status": "OK",
          "v": -0.009050546448,
          "version": "1.3fa23ddd"
        },
        "ret_1d": {
          "age_s": 844.077919,
          "quality": {
            "bar_density": 0.999689441,
            "completeness": 1.0,
            "expected_minutes": 9660,
            "feed": "iex",
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9657,
            "verified_none": 3,
            "window_end": "2026-11-23T19:30:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "c03200498b1fd16a0fc86a4cda771e452df901d525eb7c4956de0de37aae08df",
          "status": "OK",
          "v": -0.07827648115,
          "version": "1.b77eca69"
        },
        "ret_20d": {
          "age_s": 254644.0779,
          "quality": {
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "last_session": "2026-11-20"
          },
          "record_hash": "02da53f5a51cbb614819906748f35303c6b58a555dbd7ce9f592b8bd5674f768",
          "status": "MISSING",
          "v": null,
          "version": "1.7d1f1942"
        },
        "ret_5d": {
          "age_s": 254644.0779,
          "quality": {
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "last_session": "2026-11-20"
          },
          "record_hash": "31eb11e3b5586e23fae13c8a611493c29245105c225fbefa1f01f12e3f21ae92",
          "status": "MISSING",
          "v": null,
          "version": "1.5d56db82"
        },
        "ret_5m": {
          "age_s": 844.077919,
          "quality": {
            "bar_density": 0.999689441,
            "completeness": 1.0,
            "expected_minutes": 9660,
            "feed": "iex",
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9657,
            "verified_none": 3,
            "window_end": "2026-11-23T19:30:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "3a903c6c5613922944a3bf6d4122f2d3b35b8c9b653565a1d618fcbafec3ddef",
          "status": "OK",
          "v": -0.0002584201912,
          "version": "1.c10a3b57"
        },
        "ret_60m": {
          "age_s": 844.077919,
          "quality": {
            "bar_density": 0.999689441,
            "completeness": 1.0,
            "expected_minutes": 9660,
            "feed": "iex",
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9657,
            "verified_none": 3,
            "window_end": "2026-11-23T19:30:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "de5210040d5b927124ba5a30f3470c2fb9ae0e93e05b1af14ddd37b89d3773ef",
          "status": "OK",
          "v": -0.0002584201912,
          "version": "1.6c49ff8f"
        },
        "rsi14": {
          "age_s": 254644.0779,
          "quality": {
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "last_session": "2026-11-20"
          },
          "record_hash": "2bd3d0c217fcf205f4d7e703b3413e7a5f2dfcd3d74344dbc8a2615aaf7de968",
          "status": "MISSING",
          "v": null,
          "version": "1.273a3a79"
        },
        "rsi14_15m": {
          "age_s": 844.077919,
          "quality": {
            "bar_density": 0.999689441,
            "completeness": 1.0,
            "expected_minutes": 9660,
            "feed": "iex",
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9657,
            "verified_none": 3,
            "window_end": "2026-11-23T19:30:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "b6e1bbe2865d66bc959a6a62ac43cbc49df30df471232dcdcb033a4d376d0b5e",
          "status": "OK",
          "v": 62.59388564,
          "version": "1.f0b8fdaf"
        },
        "rvol_60m": {
          "age_s": 844.077919,
          "quality": {
            "bar_density": 0.999689441,
            "completeness": 1.0,
            "expected_minutes": 9660,
            "feed": "iex",
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9657,
            "verified_none": 3,
            "window_end": "2026-11-23T19:30:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "ef0442b7457060657193243bf8fa383d63572ca06c650db08626448a09882509",
          "status": "OK",
          "v": 0.0101881123,
          "version": "1.84c5ec7e"
        },
        "sellable_qty": {
          "age_s": 0.709764,
          "quality": {},
          "record_hash": "d0e58e880354f82d9c05ad470f889e772dd7da90fbe770cc94eae4fe7788a741",
          "status": "OK",
          "v": "0",
          "version": "1.9cbf72e4"
        },
        "sma20": {
          "age_s": 254644.0779,
          "quality": {
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "last_session": "2026-11-20"
          },
          "record_hash": "1db5ee840cb65d9c0a774ec7773659ac4cdf0a90ededbf84354942b04efd675d",
          "status": "MISSING",
          "v": null,
          "version": "1.80f8a078"
        },
        "sma50": {
          "age_s": 254644.0779,
          "quality": {
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "last_session": "2026-11-20"
          },
          "record_hash": "5d86bf450bcb518132c4974e86f45d754cc9d6bf9fd01ea4f1b7decb8f2c732c",
          "status": "MISSING",
          "v": null,
          "version": "1.3890c9d7"
        },
        "spread_bps": {
          "age_s": 1.957619,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "f3ca357b5d361eaa2e537740e04cdee72b819a0026bfcef1cee0566f907fe947",
          "status": "OK",
          "v": 1.722801275,
          "version": "1.e2b080ab"
        },
        "trend_sma20_vs_sma50": {
          "age_s": 254644.0779,
          "quality": {
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "last_session": "2026-11-20"
          },
          "record_hash": "02b88ca0591c15d796f15609f4368adafa5ce2a3053bd5592cac32fd4cc6cd74",
          "status": "MISSING",
          "v": null,
          "version": "1.84583425"
        },
        "unrealized_pnl_pct": {
          "age_s": 0.709764,
          "quality": {},
          "record_hash": "616c300e9c9df5586e39395ee2a25f3213ed26d034585261ee55570e90813fb1",
          "status": "OK",
          "v": 0,
          "version": "1.7c530604"
        },
        "vol_regime_ratio": {
          "age_s": 844.077919,
          "quality": {
            "bar_density": 0.999689441,
            "completeness": 1.0,
            "expected_minutes": 9660,
            "feed": "iex",
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9657,
            "verified_none": 3,
            "window_end": "2026-11-23T19:30:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "9a8a2784d803faa13d7e6552e64003d88543e7beadd90ccb0535fceb5b5b5528",
          "status": "OK",
          "v": 1.04394009,
          "version": "1.302e72c1"
        },
        "volume_z20": {
          "age_s": 254644.0779,
          "quality": {
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "last_session": "2026-11-20"
          },
          "record_hash": "3e57c55e843620f6cc1ffce34396913662774ae15edd605dcd30caa05a79dc6e",
          "status": "MISSING",
          "v": null,
          "version": "1.970d159b"
        },
        "volz_tod_15m": {
          "age_s": 844.077919,
          "quality": {
            "bar_density": 0.999689441,
            "completeness": 1.0,
            "expected_minutes": 9660,
            "feed": "iex",
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9657,
            "verified_none": 3,
            "window_end": "2026-11-23T19:30:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "6357f953d8cc92e3e80a433273ff6a32d1e591721344832d0ea2cd18c99252af",
          "status": "OK",
          "v": 0.2449861033,
          "version": "1.4315d547"
        },
        "vwap_dev_session": {
          "age_s": 844.077919,
          "quality": {
            "bar_density": 0.999689441,
            "completeness": 1.0,
            "expected_minutes": 9660,
            "feed": "iex",
            "input_hash": "4dfaa4f402a9b4a725fa794efe3a59f3706bfba0f501139c6eebe2150f13d8ad",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9657,
            "verified_none": 3,
            "window_end": "2026-11-23T19:30:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "de97bca340fb27b21c3098027c60e13087478364211afa9fbd9178f65161fab3",
          "status": "OK",
          "v": -2.52141368e-05,
          "version": "1.b41de1ff"
        }
      }
    },
    "validation_policy": "scored-15m-plus-2m-v1"
  },
  "council_mode": "PAPER_COUNCIL_SKEPTIC_OFF",
  "chair": {
    "note": "Prearbiter entry_ok false (no signal above threshold) and no existing position; cannot sell. No actionable candidate.",
    "role": "CHAIR",
    "run_id": "ddb360d2-c459-50d8-b636-315cf9af4a0d",
    "candidates": [],
    "schema_version": 2
  },
  "skeptic_audit": {
    "attempts": 0,
    "skip_reason": "DISABLED_BY_OPERATOR"
  },
  "role_outputs": [
    {
      "role": "CHAIR",
      "status": "OK",
      "response": "{\n  \"schema_version\": 2,\n  \"run_id\": \"ddb360d2-c459-50d8-b636-315cf9af4a0d\",\n  \"role\": \"CHAIR\",\n  \"candidates\": [],\n  \"note\": \"Prearbiter entry_ok false (no signal above threshold) and no existing position; cannot sell. No actionable candidate.\"\n}",
      "error": null
    },
    {
      "role": "LIQUIDITY",
      "status": "OK",
      "response": "{\"schema_version\":2,\"role\":\"LIQUIDITY\",\"run_id\":\"ddb360d2-c459-50d8-b636-315cf9af4a0d\",\"source\":\"code\",\"data_confidence\":\"HIGH\",\"symbols\":[{\"symbol\":\"INTC\",\"note\":\"deterministic code assessment\",\"evidence\":[{\"band\":\"TIGHT\",\"path\":\"symbols.INTC.spread_bps\"},{\"band\":\"POSITIVE\",\"path\":\"symbols.INTC.mid_px\"},{\"band\":\"NORMAL\",\"path\":\"symbols.INTC.volz_tod_15m\"}],\"gate\":{\"state\":\"PASS\",\"size_multiplier\":1.0,\"reasons\":[]}}]}",
      "error": null
    },
    {
      "role": "PORTFOLIO",
      "status": "OK",
      "response": "{\"data_confidence\": \"HIGH\", \"role\": \"PORTFOLIO\", \"run_id\": \"ddb360d2-c459-50d8-b636-315cf9af4a0d\", \"schema_version\": 2, \"source\": \"code\", \"symbols\": [{\"evidence\": [{\"band\": \"POSITIVE\", \"path\": \"portfolio.equity\"}, {\"band\": \"POSITIVE\", \"path\": \"portfolio.buying_power\"}, {\"band\": \"POSITIVE\", \"path\": \"portfolio.aggregate_headroom_usd\"}, {\"band\": \"ZERO\", \"path\": \"symbols.INTC.position_qty\"}], \"gate\": {\"reasons\": [], \"size_multiplier\": 1.0, \"state\": \"PASS\"}, \"note\": \"deterministic code assessment\", \"symbol\": \"INTC\"}]}",
      "error": null
    },
    {
      "role": "REGIME",
      "status": "OK",
      "response": "{\"data_confidence\":\"MED\",\"risk_appetite\":\"NEUTRAL\",\"role\":\"REGIME\",\"run_id\":\"ddb360d2-c459-50d8-b636-315cf9af4a0d\",\"schema_version\":2,\"source\":\"code\",\"symbols\":[{\"symbol\":\"INTC\",\"evidence\":[{\"band\":\"UPTREND\",\"path\":\"market.regime_label\"},{\"band\":\"POSITIVE\",\"path\":\"market.spy_vol_regime_ratio\"},{\"band\":\"POSITIVE\",\"path\":\"symbols.INTC.ema21_15m\"},{\"band\":\"POS_STRONG\",\"path\":\"symbols.INTC.ema_gap_bps_15m\"},{\"band\":\"NEG_STRONG\",\"path\":\"symbols.INTC.ret_15m\"},{\"band\":\"POSITIVE\",\"path\":\"symbols.INTC.atr14_15m\"}],\"note\":\"Trend positive but recent weak returns; buying possible, selling not\"}]}",
      "error": null
    },
    {
      "role": "TECHNICAL",
      "status": "OK",
      "response": "{\"data_confidence\": \"HIGH\", \"role\": \"TECHNICAL\", \"run_id\": \"ddb360d2-c459-50d8-b636-315cf9af4a0d\", \"schema_version\": 2, \"source\": \"code\", \"symbols\": [{\"evidence\": [{\"band\": \"POS_STRONG\", \"path\": \"symbols.INTC.ema_gap_bps_15m\"}, {\"band\": \"FIRM\", \"path\": \"symbols.INTC.rsi14_15m\"}, {\"band\": \"FLAT\", \"path\": \"symbols.INTC.recent_return_5m\"}, {\"band\": \"POSITIVE\", \"path\": \"symbols.INTC.atr14_15m\"}, {\"band\": \"UNCONFIRMED\", \"path\": \"symbols.INTC.intraday_setup_1m\"}], \"note\": \"Maintain floor; 15m bullish bias offsets flat 5m chop and unconfirmed 1m doji.\", \"signal\": {\"confidence\": 0.7, \"horizon\": \"INTRADAY\", \"score\": 0.64450099, \"state\": \"SIGNAL\"}, \"symbol\": \"INTC\"}]}",
      "error": null
    }
  ],
  "reason_codes": [
    "NO_SIGNAL_ABOVE_THRESHOLD"
  ],
  "notes": [
    "evidence_pack:25ea98d503df162662a45af4ba9653812bb1f3d863142f41e784660594160018",
    "council_run:ddb360d2-c459-50d8-b636-315cf9af4a0d",
    "NO_SIGNAL_ABOVE_THRESHOLD"
  ],
  "error": null,
  "proposals_and_risk": []
}
```

</details>

### 14:45:12 ET · DECIDED_HOLD

<details>
<summary>Recorded decision evidence</summary>

```json
{
  "decision_id": "70f90d11-e0d5-53b4-8295-9e938a0a09ba",
  "inputs": {
    "as_of": "2026-11-23T19:45:05.544152Z",
    "regime": {
      "label": "uptrend"
    },
    "account": {
      "cash": 99803.06,
      "equity": 99803.06,
      "status": "ACTIVE",
      "account_id": "PAPER_ACCOUNT",
      "last_equity": 99803.39,
      "buying_power": 399212.24
    },
    "positions": [],
    "symbols": {
      "INTC": {
        "mid": 58.07,
        "rsi14": null,
        "ret_1d": -0.0783,
        "ret_5d": null,
        "ret_20d": null,
        "atr14_pct": null,
        "price_vs_sma20": null,
        "trend_sma20_vs_sma50": null
      }
    }
  },
  "feature_evidence": {
    "account_ref": "PAPER_ACCOUNT",
    "as_of": "2026-11-23T19:45:05.544152+00:00",
    "availability": {
      "account": "fresh",
      "bars": "fresh",
      "calendar": "fresh",
      "news": "fresh",
      "ok_fraction_core_features": 1.0,
      "quotes": "fresh"
    },
    "bands_hash": "810517c6e124c7ebc23ca0ebce7ef7ba7cc66b30bc21cacc66c1a221174255d4",
    "feasibility": {
      "INTC": {
        "can_buy": true,
        "can_buy_reasons": [],
        "can_sell": false,
        "can_sell_reasons": [
          "NO_SELLABLE_INVENTORY"
        ],
        "entry_window_open": true,
        "entry_window_reason": "",
        "held_qty": "0.0",
        "max_new_notional_usd": "2000.0",
        "sellable_qty": "0"
      }
    },
    "feature_slot": {
      "candles": {
        "INTC|2026-11-23T19:30:00+00:00": "0463d928b81389008026d1c49054414c41445cfe010605dc44414d5a8006ec80",
        "INTC|2026-11-23T19:31:00+00:00": "a5309c04231b41b04749996dbc08d1d625cf986b4bacb8d065bd4272b1bcd687",
        "INTC|2026-11-23T19:32:00+00:00": "1316263235fefac976cf3179d15a341ca2faba6862bc2ad845a199a21f1a4ea1",
        "INTC|2026-11-23T19:33:00+00:00": "c37f8ccdeccf9064ac8a9b4e6a21d4ed42be7567ab3ba10eb0558b68028107c0",
        "INTC|2026-11-23T19:34:00+00:00": "564e3a869b90c07bc6f4dc36fc9a4642620456c6cac5272aff6455bd272177b1",
        "INTC|2026-11-23T19:35:00+00:00": "8c40460eb8f86125bf2228c6e0b5478931f3e3a91a013bd23caa1bb828639442",
        "INTC|2026-11-23T19:36:00+00:00": "9cb732a5a05f88fcae5944f0121aac8aaa2713bd234d104b87ddb513e8886ae9",
        "INTC|2026-11-23T19:37:00+00:00": "9d5b09f82117334dcc0f33b8c32ad04009545b4670f26997f04929a89d44df93",
        "INTC|2026-11-23T19:38:00+00:00": "e98c98af48936fd32ec6ad72041fcbfa1de8511a2b8911c69eabcd4ab7117e18",
        "INTC|2026-11-23T19:39:00+00:00": "422314eba37616c0546eed1ed8aa018f6b54ce6bec687378c7704d9ca2065248",
        "INTC|2026-11-23T19:40:00+00:00": "70e0d8b0a63b3723514998b8205402a930375f59ca5308b2f48f6dbab08cd617",
        "INTC|2026-11-23T19:41:00+00:00": "4510c4c83faf5f5878d401794d4b7bed12120a3527e7efc68be6e7a94d44c40b",
        "INTC|2026-11-23T19:42:00+00:00": "98067d1cfbe2cf62a97c2f9a655f0cf4470e9f8fb2391eb0463aff7d674dad4b",
        "INTC|2026-11-23T19:43:00+00:00": "c8d1f80659f571bf3eb64a17b9935be4ce7a092a55afd0608b149b1e717e9011",
        "INTC|2026-11-23T19:44:00+00:00": "c1aa4b559490e25f881fb40af919d8644954d00315de5f007556c6e7791a0b28",
        "SPY|2026-11-23T19:30:00+00:00": "501b6b54205a5fdefb7bf1b8f37d97b09bec2331a71da24c04a1e76471a3e9be",
        "SPY|2026-11-23T19:31:00+00:00": "7a616b1bec25ec89392c717c57a4f8a02b7baa240defd1ce7ed414da812d51e0",
        "SPY|2026-11-23T19:32:00+00:00": "13017eef20c793ba8a0c3bee58ceb303a749f3ed6db515430dbcd3f066266ef6",
        "SPY|2026-11-23T19:33:00+00:00": "60acf2b6b72dfb53f598542c183985e00d5820e45e6a15aaa702caa2e7db45df",
        "SPY|2026-11-23T19:34:00+00:00": "205774036f40cb4bc8e44df4d46ef150bd7d25dedeb8a897455bddc1dd4763d8",
        "SPY|2026-11-23T19:35:00+00:00": "a3f33f928527ca6cd947868e44e270cfe45857f8acf9296afd6811bf7c66a716",
        "SPY|2026-11-23T19:36:00+00:00": "20f2610f9083c52c53c44110cf31c15486c3658b74baf10c77427c7f1643e451",
        "SPY|2026-11-23T19:37:00+00:00": "cfc075a20afd9004c6a54e55e02de60aa1ac6fab559ca2bc363b4083a5a7b0e8",
        "SPY|2026-11-23T19:38:00+00:00": "8ac7b4d0dc16f15a1b48e3576c48557a2cf3e5e01e9dbd56ec12e4206987e786",
        "SPY|2026-11-23T19:39:00+00:00": "38712a0709a4972b95a52f42b45fd54896d71cc49ce48651c65445f1a42bf62f",
        "SPY|2026-11-23T19:40:00+00:00": "e49f4baca7c7583df76c009735c11448f1023f1415b68e390409997276db3480",
        "SPY|2026-11-23T19:41:00+00:00": "0dccbf44a642c7d605f69cb3858d90923162c6c2b93f66b9555d77776438a183",
        "SPY|2026-11-23T19:42:00+00:00": "88269dcad14d8b8d3584bb870bfc6f5eed07f56a971f9ad7e1037bfff28a3780",
        "SPY|2026-11-23T19:43:00+00:00": "a4aebaa6965c7c246c1610c4eff9a05d061eff2cadc3940774ca5ab43368ca06",
        "SPY|2026-11-23T19:44:00+00:00": "b91459d6c5ec4fb98cb4404bbe1cd7357fe920ab60a2e98579d2b6fb1626730d"
      },
      "close": "2026-11-23T19:45:00+00:00",
      "feed": "iex",
      "indicator_close": "2026-11-23T19:45:00+00:00",
      "indicator_input_hashes": {
        "INTC": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
        "SPY": "68be2784fe1097306ec89b5433c1c0b0393b316ceebc03170624a4214da8ac5c"
      },
      "provisional": true,
      "records": {
        "market:market:breadth_above_ema21": "d7e2f70fedf1d18806a57fa4210d951ce450efccdd03a1fa716baff26d0f59e9",
        "market:market:regime_label": "b5f7eda754fe89980a8ade83e3496e26768374e4bbb5fca559b77ed06e580f14",
        "market:market:spy_ema_gap_bps_15m": "5885f7d1170e4539d33b130275da00b6751841c47609429095ed1e27403a7ec2",
        "market:market:spy_ret_60m": "c7c53a8f167fcb3dfce8331f53967c86725bba6948ccf0f376eb89df351fe1e4",
        "market:market:spy_vol_regime_ratio": "67748943706382656f39398e7fffe2f47958b9e33da6dc4e1dbf70394ac3350b",
        "symbol:INTC:adv_usd_20d": "b9b2c8cd47063244741a0be3a99b852571258b975af9e1831bf9c22ac86c817d",
        "symbol:INTC:atr14_15m": "6f731751bfa53150c4b34c9f00c97b6e20fc9879a19350f0ce7cbe19a7070a61",
        "symbol:INTC:atr14_1d": "7109941c8f13c27be9954427260fd23488765da0017ae6e7268c52c67c282e0d",
        "symbol:INTC:atr14_pct": "72b22515a9b698de8e221ba3601ca48bfe5aa847f96eb780cd201d7da6e1b10b",
        "symbol:INTC:dist_hi_atr": "fa39b85a6fa98f7bfc74c7b166a281a28769a232885795c2b9c112651bf56493",
        "symbol:INTC:dist_lo_atr": "158f49a8db2ec572b0285e96c063a7ab5e2822b1e36b8ede6af37745bf9ecdde",
        "symbol:INTC:ema21_15m": "026dc43aa182328e915e6f6d23296bedca2f3d61e29ad492593fd2b16c1f2c9c",
        "symbol:INTC:ema9_15m": "779c29eadfec6fe54e83478754f967d3444f194d88d34349bf014707a7b14100",
        "symbol:INTC:ema_gap_bps_15m": "2d80bf72eea509fb31fba6a2c3b863d8d8dc686f8d007db33fe90cf4a50e5145",
        "symbol:INTC:gap_open_pct": "22372f1618bb0042d504687f06dc178f5d5531095633eddeaf4bcfe97a2ded36",
        "symbol:INTC:intraday_ret_1h": "584b190315139eaa5cf532afd4584686eee1ec8a960635264ed6e8e8c24aeec5",
        "symbol:INTC:intraday_setup_1m": "ded168fa937c606f5b6d8cf1fa4d953d199aaec2b743bf9ddcd433b1a3c96e57",
        "symbol:INTC:last_close": "d19401a83eca33beec8f4dc4c9fd9de4a732eca37d9f9287a4931e7ba85850f1",
        "symbol:INTC:macd_hist_15m": "ffc4ec65b3c48fbd631f09dccfb6d59e271d94c9ffd76307010798940056e67d",
        "symbol:INTC:price_vs_sma20": "0d79ec3c1b357a5011464af77c39b3fcad072140f1af42e8fc4caaaa2d603acd",
        "symbol:INTC:recent_price_10m": "f9a2f341f17497dfc0ddb58f4a36c97422d507e13dffe640ca9fe243263cd212",
        "symbol:INTC:recent_range_bps_10m": "bc3817ac207fb196122ffdb5be87efb417856903f97258d4a02de87210b68e6f",
        "symbol:INTC:recent_range_bps_5m": "ced4cc795a9dc84b3aad64ce8b426f6eba7dd423a8f86b94c8affcbda408b5fc",
        "symbol:INTC:recent_return_10m": "6aac3ba9744794f47aa742d5b15a2d36e68b12d80f8fbcc73f61c69294cc8386",
        "symbol:INTC:recent_return_5m": "cac4e4b73fca3581941be566fb3d21cd530e2eb09e3d342dc72fc7a8cb4d6ea9",
        "symbol:INTC:recent_volume_10m": "e00870fc13c0760dff9d1458b827506ad2185f5bf533ada38422a999b5785da9",
        "symbol:INTC:recent_volume_5m": "d1c2db2c6b5f45bc3b141c32af93d5592b23a16aab55b449f3970c392bc0761c",
        "symbol:INTC:relstr_spy_60m": "f09a7c4016276d7ece654cb0fbddf98b2635666a4a9416792cd1b5ddfd8154f9",
        "symbol:INTC:ret_15m": "f05b3a74a7211b4ce7a23216b532af4d320537ac3b9532ee324f8dbf77d3137c",
        "symbol:INTC:ret_1d": "4871f8f39f073d45e17d3d6f5ca60a8fec098c3c382779b9f1d17c4eff156f1b",
        "symbol:INTC:ret_20d": "c89eca0e545e370a2b5106418f52c2c97be259b8d9a271ffd1a96adbaa2aca0a",
        "symbol:INTC:ret_5d": "05a741e625955a85a438ad18773375028848616408999e7af63ece7accaed8b3",
        "symbol:INTC:ret_5m": "19753379ae57616102e8755122b80e435f0c978ed5e79cc3435fe9b26513660a",
        "symbol:INTC:ret_60m": "c7d497003ca260f4bb80c0cd4ca5c604cccb4c8b278832591a98f7bcf9224233",
        "symbol:INTC:rsi14": "1e59b41cf19356a8afb2c1abc8da30ba54a3ae1c9ca6adec3645d67baab39a97",
        "symbol:INTC:rsi14_15m": "8e2405b48f61208fcc98491d12fb4cfef18c440cec8f1c795d9799094ef01d8d",
        "symbol:INTC:rvol_60m": "27cf8ed2d446f97888229373a5ac880ff2e3d212d2e60bbd9ed0395576829c03",
        "symbol:INTC:sma20": "15576f86a2842f5eb53a8c69129bc796ec2bb02d553d6eb692a0246444b821e2",
        "symbol:INTC:sma50": "c77619dbf2bb36c37659503666953bdfa289b5ad53f8419d72ac47d490aa3455",
        "symbol:INTC:trend_sma20_vs_sma50": "c3f4c96640a0fefa86efead1a20dc2a8c20470887509f9a64b8b123a7f0f6feb",
        "symbol:INTC:vol_regime_ratio": "c6313cc86a68c91717f673033fd54720624546900b0f164f27fd627e76149292",
        "symbol:INTC:volume_z20": "acd6606915e0844ee2fa5f30507b576df69022855968e20bad1ec489ca7b84b7",
        "symbol:INTC:volz_tod_15m": "00402ad410208e76d63fb60dc603ca6c5c3933ab4023869011a7814ed1722a9c",
        "symbol:INTC:vwap_dev_session": "a96e2cb38b6d62a078789e516cd81092c72afe3ba66fd637c29b906a6873af69",
        "symbol:SPY:adv_usd_20d": "92e94f829df49f4b3a8d0be7612b000e92190d5356f55e566f04069ca7b9ffd5",
        "symbol:SPY:atr14_15m": "7ab448ef9d85396282151eac59236f9553a486b5c77591049f30866a0df20c74",
        "symbol:SPY:atr14_1d": "3cac187afe8b3f12d7d3b3b86986d403d549ebe59a7ccfaa10a213aaea0d6f29",
        "symbol:SPY:atr14_pct": "86a49f6a2b7c51bced8c4109a9b641fd3430da5d9872f600c092cec75526d214",
        "symbol:SPY:dist_hi_atr": "84836a2186870e2d831a4eb4b560d0edebc916b36aca69d107ea1f7742290420",
        "symbol:SPY:dist_lo_atr": "981cb9fc66b9f88be3976f26fb2f2c98627c55f0052e3d48eca6901c9fef035f",
        "symbol:SPY:ema21_15m": "e101df90a64d088f78547e381107b8db83b2541409047168500bf08d4caa4b43",
        "symbol:SPY:ema9_15m": "d9a6929dcd2aa029a0657e3b23036ea5c8e549c3e28f704d22c59d9141f45d16",
        "symbol:SPY:ema_gap_bps_15m": "12f402c62d8c646eb7b75bb92bec226e49110827a04064a50b8a1e5b881fc789",
        "symbol:SPY:gap_open_pct": "1c9616a65f2f013255300b42e56d88ac7a725e105e6f59b39d79e458ad29184e",
        "symbol:SPY:intraday_ret_1h": "4a3cbce2b9dcc1b99d6875d1dfcc341ba613acfd2d05e42ab8e2dd8730e5c8b3",
        "symbol:SPY:intraday_setup_1m": "1b4a016d7852e9ca3a00bb72a7f80c4165913d65478acc408c4608bff5a976ee",
        "symbol:SPY:last_close": "caf596deca80d26016ad4208908f5e9f946155af82bcf05ef2276748182b2361",
        "symbol:SPY:macd_hist_15m": "7c1f84aa5b3c914a24e8512883539348c328fedf77f1ca8fddef3c9428311b8a",
        "symbol:SPY:price_vs_sma20": "963d8268f25c4849a1b268733b11edd2005fe4a8c767d1439d8478255d5a22c9",
        "symbol:SPY:recent_price_10m": "8b31f6a47dcbba43ec99b634ad2df6257311492b83768c0f89a05c83b6db08eb",
        "symbol:SPY:recent_range_bps_10m": "e85d593eab13ae95c7ee60f19bf922742713fd965cc1d74be61c0a92fa8b1a17",
        "symbol:SPY:recent_range_bps_5m": "10fbe008ff94306a407623231b4ea2e18204b47b6bf8c4e2abd052ac41a05bc1",
        "symbol:SPY:recent_return_10m": "7639ee2211a5c4ed7367d852301fb10b4b8f82d8183ba7c08e0af022a64c0ac3",
        "symbol:SPY:recent_return_5m": "4185d43fba5ad752503e7b8b38d443e7939e8381007aad6b0d7d14e961a59d6c",
        "symbol:SPY:recent_volume_10m": "05db5a80f00e90567af144c535960e6b92e5f033af14bb663bb393c17a437b4c",
        "symbol:SPY:recent_volume_5m": "c83053c24b69cbcb52edfb0040f5be88068944f4bf165ae40e55b031ce626cb0",
        "symbol:SPY:relstr_spy_60m": "8192ee3c1e096d3220e21bd96547302036aad20b1f8b2a88d06eb43fca3d16bd",
        "symbol:SPY:ret_15m": "bc860ac7fa1ae9ad3cba5cc9e7d84f2605d2dd4f19469bf57477cb2f08c21b1e",
        "symbol:SPY:ret_1d": "aab94a7dafcf360313d949fc12ced963ccb5a8b3ef27866b2b930d2d5817c533",
        "symbol:SPY:ret_20d": "5cb42b7c179c74bdcedf0dbf4ce0ee12832341fe24b75d306dccc8cc03e792c3",
        "symbol:SPY:ret_5d": "7c31dada2f0a36e24d03e89b66cb73d377f3c298c10867a1be2b05be76be6a0c",
        "symbol:SPY:ret_5m": "c45eb44dd86b0d6cecb4343e224548f280bdfcdbd5008f64e3e6f8c78d93cbe7",
        "symbol:SPY:ret_60m": "f1a248647044bf41d465b4441d862360690c875060ce3f291fc0a90c19292393",
        "symbol:SPY:rsi14": "ee11c2b462281f9fc927ac380b6bb2557ff2e158729fe2f17aa91d152eb3fb9f",
        "symbol:SPY:rsi14_15m": "7a2d8a98c627154aeccdc9a68b885c12330bcb82ce58cddb4d0a2f4136033fc0",
        "symbol:SPY:rvol_60m": "3d0f132c7dceafbc31fa24815771e60b88abecf31be0cfa67e87b00638b39e02",
        "symbol:SPY:sma20": "1b30496ca2845ccd7a79462c221d840260e1c0361b7feb9dedbc5dc30bd4b2a5",
        "symbol:SPY:sma50": "94c11d37cff9b64498753612d4be2b84f39d1931bd55ec9e573a0c8697ceb72b",
        "symbol:SPY:trend_sma20_vs_sma50": "8aee1d285ca5a8e44083c58d0fad60754235fda2855c6ac02c9796bc41cff8bc",
        "symbol:SPY:vol_regime_ratio": "ba0a825fe908604396cacb3dd14781f8f41f44ece623d430a1da89c64da40e36",
        "symbol:SPY:volume_z20": "26f74a49cf931c478f404ef3e6a0850c2e214cc588216f87e068535e16f86e9f",
        "symbol:SPY:volz_tod_15m": "29640670f4a0587e4e43a5ad4cd8d40a485c1b2537f64212b1cb41ffc2d19792",
        "symbol:SPY:vwap_dev_session": "9f32dcc7c9be186a479ae3e851f795340a7f56dc37a8b6ef953f33a7cbc9f9af"
      },
      "symbols": [
        "INTC",
        "SPY"
      ]
    },
    "horizons": {
      "INTC": {
        "10m": {
          "age_s": 5.544152,
          "last_bar_end": "2026-11-23T19:45:00+00:00",
          "status": "OK"
        },
        "15m": {
          "age_s": 5.544152,
          "last_bar_end": "2026-11-23T19:45:00+00:00",
          "status": "OK"
        },
        "5m": {
          "age_s": 5.544152,
          "last_bar_end": "2026-11-23T19:45:00+00:00",
          "status": "OK"
        },
        "60m": {
          "age_s": 5.544152,
          "last_bar_end": "2026-11-23T19:45:00+00:00",
          "status": "OK"
        },
        "horizon_conflict": false
      }
    },
    "market": {
      "breadth_above_ema21": {
        "age_s": 5.544152,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "d7e2f70fedf1d18806a57fa4210d951ce450efccdd03a1fa716baff26d0f59e9",
        "status": "OK",
        "v": 1.0,
        "version": "1.1dfe664d"
      },
      "minutes_to_close": {
        "age_s": 0.603453,
        "quality": {},
        "record_hash": "947c10e5719e81d41b542f861536488c1571e810a9947e676a0cb2ff0e1cc810",
        "status": "OK",
        "v": 74.91765502,
        "version": "1.e79b1ead"
      },
      "regime_label": {
        "age_s": 5.544152,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "b5f7eda754fe89980a8ade83e3496e26768374e4bbb5fca559b77ed06e580f14",
        "status": "OK",
        "v": "UPTREND",
        "version": "1.f8b361d7"
      },
      "session_phase": {
        "age_s": 0.603453,
        "quality": {},
        "record_hash": "c82aa858d472845ca28ae0ef8d93c3b613fdc8086d0f29a1353f1cae9a3bba21",
        "status": "OK",
        "v": "NORMAL",
        "version": "1.91f88fe8"
      },
      "spy_ema_gap_bps_15m": {
        "age_s": 5.544152,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "5885f7d1170e4539d33b130275da00b6751841c47609429095ed1e27403a7ec2",
        "status": "OK",
        "v": 37.89644347,
        "version": "1.fda7da7a"
      },
      "spy_ret_60m": {
        "age_s": 5.544152,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "c7c53a8f167fcb3dfce8331f53967c86725bba6948ccf0f376eb89df351fe1e4",
        "status": "OK",
        "v": -0.0005958484605,
        "version": "1.9feddbd1"
      },
      "spy_vol_regime_ratio": {
        "age_s": 5.544152,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "67748943706382656f39398e7fffe2f47958b9e33da6dc4e1dbf70394ac3350b",
        "status": "OK",
        "v": 1.402212236,
        "version": "1.3b7257aa"
      }
    },
    "meta": {
      "news": {
        "INTC": {
          "effective_weight": 0,
          "in_window": 0,
          "newest_age_min": 1783.642403,
          "policy": "48h retained; per-article decay and minimum relevance; 4h count is descriptive",
          "poller_last_ok_age_s": 14.106323,
          "retrieved": 1,
          "selected": 0,
          "state": "QUIET",
          "window_min": 240
        }
      }
    },
    "news_blob_hash": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
    "news_context_blob_hash": "ef023692226f6319baf7f6429f023deb1a988f59c953b103e7a5f425a6a5d062",
    "portfolio": {
      "aggregate_cap_usd": {
        "age_s": 0.603453,
        "quality": {},
        "record_hash": "4c5b16a6e90a6f527547e7e9380a0dc651076a96521fb5a606b7247b96999f80",
        "status": "OK",
        "v": "49901.530",
        "version": "1.5b3d1daf"
      },
      "aggregate_headroom_usd": {
        "age_s": 0.603453,
        "quality": {},
        "record_hash": "15c8aacc54bc867db3433ec04a23a1885b38ba2db7ac8d8c6b651722a691723f",
        "status": "OK",
        "v": "49901.530",
        "version": "1.7f894fff"
      },
      "buying_power": {
        "age_s": 0.603453,
        "quality": {},
        "record_hash": "cf4d55400422384c1e86396be23b27cee4c55244618822c7b485e28f543a89ab",
        "status": "OK",
        "v": "399212.24",
        "version": "1.74948dec"
      },
      "cash": {
        "age_s": 0.603453,
        "quality": {},
        "record_hash": "eeb3581b194ae31bafd3321583aa740569cd37ad71a6cb782675df2fef8c89de",
        "status": "OK",
        "v": "99803.06",
        "version": "1.b067f5e3"
      },
      "day_pnl_pct": {
        "age_s": 0.603453,
        "quality": {},
        "record_hash": "e408e1b174c9e138b08c50cf4b0dd976ba6c608a0e44410a085f4fa287b52713",
        "status": "OK",
        "v": "-0.0003306500911441986088849300",
        "version": "1.35e81852"
      },
      "drawdown_pct": {
        "age_s": 0.603453,
        "quality": {},
        "record_hash": "a14ad7a1bb331b4b6796c455ff10ef4489809d985e8102dbe0e40cbbf8f54aa5",
        "status": "MISSING",
        "v": null,
        "version": "1.19aac9ba"
      },
      "equity": {
        "age_s": 0.603453,
        "quality": {},
        "record_hash": "f4225c371c8ad199258e041f523988da7cc90e1daa7140a7d49627eaf81330a5",
        "status": "OK",
        "v": "99803.06",
        "version": "1.a2192616"
      },
      "gross_exposure_pct": {
        "age_s": 0.603453,
        "quality": {},
        "record_hash": "56e438b418b23222b6a7780b43fcdee9d9a6838cdac2a548d62ac163c38b6168",
        "status": "OK",
        "v": "0E+2",
        "version": "1.b82cc518"
      },
      "gross_exposure_usd": {
        "age_s": 0.603453,
        "quality": {},
        "record_hash": "9166fd13573a6ecfefc3e18d1f33663c84ace1b5d9180be99a919ff0c968f20c",
        "status": "OK",
        "v": "0",
        "version": "1.e4c8752b"
      },
      "last_reconcile_age_s": {
        "age_s": 0.603453,
        "quality": {},
        "record_hash": "216dfeda326cc1564c65096469454632160ca8314fce1964206b147e7c9fa1b0",
        "status": "OK",
        "v": 0,
        "version": "1.5ed0382f"
      },
      "open_buy_notional_usd": {
        "age_s": 0.603453,
        "quality": {},
        "record_hash": "b2968fbe7bfe2fc8bcb5ae51999f00d882ae884a91188e10eb79c1278dfab088",
        "status": "OK",
        "v": "0",
        "version": "1.0bd0ead1"
      },
      "open_orders": {
        "age_s": 0.603453,
        "quality": {},
        "record_hash": "c734b84c73c226695cdc3728f3c3d3b19bdb595f0de7df6a67298fe9569e1b2b",
        "status": "OK",
        "v": [],
        "version": "1.1cf37cbf"
      },
      "open_orders_count": {
        "age_s": 0.603453,
        "quality": {},
        "record_hash": "c591067056b488707f281d9e81848f0d8112ab055be0734c70d702fa5904b660",
        "status": "OK",
        "v": 0,
        "version": "1.1db4227a"
      },
      "pending_reserved_usd": {
        "age_s": 0.603453,
        "quality": {},
        "record_hash": "4830aef2551c2d4d9fce4e3322177b2df08b8c0b5bdb20f358a54cb5acca35cd",
        "status": "OK",
        "v": "0",
        "version": "1.1c3e9604"
      },
      "positions": {
        "age_s": 0.603453,
        "quality": {},
        "record_hash": "fed8c7a1cf5d55e46272802c5eb47f0b0581f7d4ffd0acb927d295ee6cb60f5b",
        "status": "OK",
        "v": [],
        "version": "1.c3284657"
      }
    },
    "registry_hash": "0fd3271269748046863b2f0558e45e2c333bb352eccc9899b7ff42277c8386fc",
    "schema_version": 1,
    "symbols": {
      "INTC": {
        "adv_usd_20d": {
          "age_s": 254705.5442,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "b9b2c8cd47063244741a0be3a99b852571258b975af9e1831bf9c22ac86c817d",
          "status": "OK",
          "v": 304793568.9,
          "version": "1.04f5e91f"
        },
        "ask_px": {
          "age_s": 1.657661,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "4d92c08f9da07e922bd85804133637392dc77b736ea553545fdd7a3172adbf32",
          "status": "OK",
          "v": 58.08,
          "version": "1.d21cdd09"
        },
        "atr14_15m": {
          "age_s": 5.544152,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "6f731751bfa53150c4b34c9f00c97b6e20fc9879a19350f0ce7cbe19a7070a61",
          "status": "OK",
          "v": 0.7629598219,
          "version": "1.0cd14e73"
        },
        "atr14_1d": {
          "age_s": 254705.5442,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "7109941c8f13c27be9954427260fd23488765da0017ae6e7268c52c67c282e0d",
          "status": "MISSING",
          "v": null,
          "version": "1.65e38f4c"
        },
        "atr14_pct": {
          "age_s": 254705.5442,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "72b22515a9b698de8e221ba3601ca48bfe5aa847f96eb780cd201d7da6e1b10b",
          "status": "MISSING",
          "v": null,
          "version": "1.87450ee9"
        },
        "bid_px": {
          "age_s": 1.657661,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "223c031d0462c1e8d1b960d9d0b262f9e954cb9616ec3875811d777d03585b81",
          "status": "OK",
          "v": 58.06,
          "version": "1.149628cd"
        },
        "dist_hi_atr": {
          "age_s": 5.544152,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "fa39b85a6fa98f7bfc74c7b166a281a28769a232885795c2b9c112651bf56493",
          "status": "OK",
          "v": -1.907046686,
          "version": "1.913ffc4a"
        },
        "dist_lo_atr": {
          "age_s": 5.544152,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "158f49a8db2ec572b0285e96c063a7ab5e2822b1e36b8ede6af37745bf9ecdde",
          "status": "OK",
          "v": 1.808745311,
          "version": "1.79ba4c70"
        },
        "ema21_15m": {
          "age_s": 5.544152,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "026dc43aa182328e915e6f6d23296bedca2f3d61e29ad492593fd2b16c1f2c9c",
          "status": "OK",
          "v": 57.40577599,
          "version": "1.bfcac61e"
        },
        "ema9_15m": {
          "age_s": 5.544152,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "779c29eadfec6fe54e83478754f967d3444f194d88d34349bf014707a7b14100",
          "status": "OK",
          "v": 58.09168398,
          "version": "1.81255de8"
        },
        "ema_gap_bps_15m": {
          "age_s": 5.544152,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "2d80bf72eea509fb31fba6a2c3b863d8d8dc686f8d007db33fe90cf4a50e5145",
          "status": "OK",
          "v": 119.4841427,
          "version": "1.d4519f3c"
        },
        "gap_open_pct": {
          "age_s": 5.544152,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "22372f1618bb0042d504687f06dc178f5d5531095633eddeaf4bcfe97a2ded36",
          "status": "MISSING",
          "v": null,
          "version": "1.27438d4d"
        },
        "halted": {
          "age_s": 0.603453,
          "quality": {},
          "record_hash": "82d385185752a08c7f17142f84d71c502cf5447eaba7889fa1cf9b54f3adf529",
          "status": "OK",
          "v": false,
          "version": "1.22c5cf87"
        },
        "held_minutes": {
          "age_s": 0.603453,
          "quality": {},
          "record_hash": "48d37f36edd8be73e4b9e0c3c1c399f2d69281b41b6c6f4cf09e06dd25c630ae",
          "status": "MISSING",
          "v": null,
          "version": "1.de6ed6d3"
        },
        "intraday_ret_1h": {
          "age_s": 5.544152,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "584b190315139eaa5cf532afd4584686eee1ec8a960635264ed6e8e8c24aeec5",
          "status": "OK",
          "v": 0.001120786275,
          "version": "1.c3bb7751"
        },
        "intraday_setup_1m": {
          "age_s": 5.544152,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "982e122fbec48786cffb7618726839bb5d2a5354500532105d82600b37fa2818",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-11-23T19:35:00+00:00"
          },
          "record_hash": "ded168fa937c606f5b6d8cf1fa4d953d199aaec2b743bf9ddcd433b1a3c96e57",
          "status": "OK",
          "v": {
            "confirmation": "UNCONFIRMED",
            "pattern": "DOJI",
            "prior_trend": "FLAT",
            "range_break": "INSIDE",
            "range_ceiling": 58.305,
            "range_floor": 58.01,
            "setup_minute": 9,
            "volume_ratio": 0.5423
          },
          "version": "1.2a1f51e0"
        },
        "last_close": {
          "age_s": 254705.5442,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "d19401a83eca33beec8f4dc4c9fd9de4a732eca37d9f9287a4931e7ba85850f1",
          "status": "MISSING",
          "v": null,
          "version": "1.f2485fc2"
        },
        "luld_active": {
          "age_s": 0.603453,
          "quality": {},
          "record_hash": "79bfad459ce64586f33bdaf484df6a5add2530875c13ecf8de50f268732895ba",
          "status": "MISSING",
          "v": null,
          "version": "1.84a715b2"
        },
        "macd_hist_15m": {
          "age_s": 5.544152,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "ffc4ec65b3c48fbd631f09dccfb6d59e271d94c9ffd76307010798940056e67d",
          "status": "OK",
          "v": -0.07751173219,
          "version": "1.391617c8"
        },
        "mid_px": {
          "age_s": 1.657661,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "2c8601818bde1e67c10cc05f59ad8c445aa90a3eaff4ab4a11d856dd08a63622",
          "status": "OK",
          "v": 58.07,
          "version": "1.d567a349"
        },
        "news_age_min_latest": {
          "age_s": 14.106323,
          "quality": {},
          "record_hash": "5101638ac873f26a121b7dff41b50a44f19c5d72096a517efba1c4e89071426f",
          "status": "MISSING",
          "v": null,
          "version": "1.d0f79dc8"
        },
        "news_confirmed": {
          "age_s": 0,
          "quality": {
            "source": "stored news and pinned price features"
          },
          "status": "OK",
          "v": false,
          "version": "news-confirmation-v2"
        },
        "news_count_1h": {
          "age_s": 14.106323,
          "quality": {},
          "record_hash": "f96134fae7c443295eed2a4f27a70f1a99fa6919e8165a19fb65f28d53ff6fa3",
          "status": "OK",
          "v": 0,
          "version": "1.0c9362fe"
        },
        "news_count_48h": {
          "age_s": 14.106323,
          "quality": {
            "as_of": "2026-11-23T19:45:05.544152+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 1,
          "version": "news-context-v2"
        },
        "news_count_4h": {
          "age_s": 14.106323,
          "quality": {
            "as_of": "2026-11-23T19:45:05.544152+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 0,
          "version": "news-context-v2"
        },
        "news_effective_sentiment": {
          "age_s": 0,
          "quality": {
            "selected": 0,
            "source": "decayed stored article metadata"
          },
          "status": "MISSING",
          "v": 0.0,
          "version": "news-decay-v2"
        },
        "news_event_flags_4h": {
          "age_s": 14.106323,
          "quality": {},
          "record_hash": "8a0f880484543c3b13c90cde2afd4ae8960da6725a7e6afd068386f05613b316",
          "status": "OK",
          "v": [],
          "version": "1.0b5a8a44"
        },
        "news_max_materiality_4h": {
          "age_s": 14.106323,
          "quality": {},
          "record_hash": "fae2e05df4752f957da625171e68552342bcb2d13f06c6b3896ae51de25b4359",
          "status": "OK",
          "v": 0,
          "version": "1.9c45e9b4"
        },
        "news_newest_age_min": {
          "age_s": 14.106323,
          "quality": {
            "as_of": "2026-11-23T19:45:05.544152+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 1783.642403,
          "version": "news-context-v2"
        },
        "news_novelty_max_4h": {
          "age_s": 14.106323,
          "quality": {},
          "record_hash": "a565560eeb68a47a51f3d1e28312a5d84461be05c5bb627770d5177d51f2b3fb",
          "status": "OK",
          "v": false,
          "version": "1.15ceb7bf"
        },
        "news_sent_ewm_240m": {
          "age_s": 14.106323,
          "quality": {},
          "record_hash": "2cfb407a923c29794b22956dfe00c2cd62d88636af70752560f12a2740fbba63",
          "status": "OK",
          "v": 0,
          "version": "1.9cad993f"
        },
        "news_sent_ewm_60m": {
          "age_s": 14.106323,
          "quality": {},
          "record_hash": "20cf375682b2396cbd294525be5da36c18fed70ec6439b70d8145e2ac30d716c",
          "status": "OK",
          "v": 0,
          "version": "1.74ab70c1"
        },
        "news_source_div_4h": {
          "age_s": 14.106323,
          "quality": {},
          "record_hash": "198adeb58d64e0327f7f84abbe8eb080e913fc816b63f9a06245177554658d5c",
          "status": "OK",
          "v": 0,
          "version": "1.6fd469c4"
        },
        "position_qty": {
          "age_s": 0.603453,
          "quality": {},
          "record_hash": "79d37fafe2886ae8cf1a6844ece1476f3d3e61d2fabad74e6e858c280080eb1a",
          "status": "OK",
          "v": "0",
          "version": "1.3a512120"
        },
        "position_value_usd": {
          "age_s": 0.603453,
          "quality": {},
          "record_hash": "dce87b2c4eafa419b3dcdaed9363d400963d7bb5e791eba1948d4c12df2a7660",
          "status": "OK",
          "v": "0",
          "version": "1.9100bec4"
        },
        "price_vs_sma20": {
          "age_s": 254705.5442,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "0d79ec3c1b357a5011464af77c39b3fcad072140f1af42e8fc4caaaa2d603acd",
          "status": "MISSING",
          "v": null,
          "version": "1.a986b9cc"
        },
        "recent_price_10m": {
          "age_s": 5.544152,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "982e122fbec48786cffb7618726839bb5d2a5354500532105d82600b37fa2818",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-11-23T19:35:00+00:00"
          },
          "record_hash": "f9a2f341f17497dfc0ddb58f4a36c97422d507e13dffe640ca9fe243263cd212",
          "status": "OK",
          "v": {
            "candles": [
              [
                0,
                58.255,
                58.305,
                58.25,
                58.305,
                2250.0,
                "VERIFIED_BAR"
              ],
              [
                1,
                58.255,
                58.255,
                58.145,
                58.15,
                5368.0,
                "VERIFIED_BAR"
              ],
              [
                2,
                58.16,
                58.175,
                58.05,
                58.08,
                12906.0,
                "VERIFIED_BAR"
              ],
              [
                3,
                58.085,
                58.13,
                58.045,
                58.045,
                3139.0,
                "VERIFIED_BAR"
              ],
              [
                4,
                58.045,
                58.165,
                58.045,
                58.095,
                12394.0,
                "VERIFIED_BAR"
              ],
              [
                5,
                58.095,
                58.19,
                58.045,
                58.185,
                11202.0,
                "VERIFIED_BAR"
              ],
              [
                6,
                58.21,
                58.21,
                58.065,
                58.07,
                11493.0,
                "VERIFIED_BAR"
              ],
              [
                7,
                58.07,
                58.095,
                58.01,
                58.01,
                9725.0,
                "VERIFIED_BAR"
              ],
              [
                8,
                58.03,
                58.09,
                58.03,
                58.03,
                7536.0,
                "VERIFIED_BAR"
              ],
              [
                9,
                58.06,
                58.075,
                58.03,
                58.06,
                5274.0,
                "VERIFIED_BAR"
              ]
            ],
            "columns": [
              "minute_offset",
              "open",
              "high",
              "low",
              "close",
              "volume",
              "coverage"
            ],
            "feed": "iex",
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-11-23T19:35:00+00:00",
            "windows": {
              "10m": {
                "close": 58.06,
                "open": 58.255,
                "range_bps": 50.63943009,
                "return": -0.003347352159,
                "status": "OK",
                "volume": 81287.0
              },
              "5m": {
                "close": 58.06,
                "open": 58.095,
                "range_bps": 34.4263706,
                "return": -0.0006024614855,
                "status": "OK",
                "volume": 45230.0
              }
            }
          },
          "version": "1.b12384d7"
        },
        "recent_range_bps_10m": {
          "age_s": 5.544152,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "982e122fbec48786cffb7618726839bb5d2a5354500532105d82600b37fa2818",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-11-23T19:35:00+00:00"
          },
          "record_hash": "bc3817ac207fb196122ffdb5be87efb417856903f97258d4a02de87210b68e6f",
          "status": "OK",
          "v": 50.63943009,
          "version": "1.b7dd2e6e"
        },
        "recent_range_bps_5m": {
          "age_s": 5.544152,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "982e122fbec48786cffb7618726839bb5d2a5354500532105d82600b37fa2818",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-11-23T19:35:00+00:00"
          },
          "record_hash": "ced4cc795a9dc84b3aad64ce8b426f6eba7dd423a8f86b94c8affcbda408b5fc",
          "status": "OK",
          "v": 34.4263706,
          "version": "1.860a2856"
        },
        "recent_return_10m": {
          "age_s": 5.544152,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "982e122fbec48786cffb7618726839bb5d2a5354500532105d82600b37fa2818",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-11-23T19:35:00+00:00"
          },
          "record_hash": "6aac3ba9744794f47aa742d5b15a2d36e68b12d80f8fbcc73f61c69294cc8386",
          "status": "OK",
          "v": -0.003347352159,
          "version": "1.03c04840"
        },
        "recent_return_5m": {
          "age_s": 5.544152,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "982e122fbec48786cffb7618726839bb5d2a5354500532105d82600b37fa2818",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-11-23T19:35:00+00:00"
          },
          "record_hash": "cac4e4b73fca3581941be566fb3d21cd530e2eb09e3d342dc72fc7a8cb4d6ea9",
          "status": "OK",
          "v": -0.0006024614855,
          "version": "1.a9090b46"
        },
        "recent_volume_10m": {
          "age_s": 5.544152,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "982e122fbec48786cffb7618726839bb5d2a5354500532105d82600b37fa2818",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-11-23T19:35:00+00:00"
          },
          "record_hash": "e00870fc13c0760dff9d1458b827506ad2185f5bf533ada38422a999b5785da9",
          "status": "OK",
          "v": 81287.0,
          "version": "1.891ed5cd"
        },
        "recent_volume_5m": {
          "age_s": 5.544152,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "982e122fbec48786cffb7618726839bb5d2a5354500532105d82600b37fa2818",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-11-23T19:35:00+00:00"
          },
          "record_hash": "d1c2db2c6b5f45bc3b141c32af93d5592b23a16aab55b449f3970c392bc0761c",
          "status": "OK",
          "v": 45230.0,
          "version": "1.c7331f02"
        },
        "relstr_spy_60m": {
          "age_s": 5.544152,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "f09a7c4016276d7ece654cb0fbddf98b2635666a4a9416792cd1b5ddfd8154f9",
          "status": "OK",
          "v": 0.001716634735,
          "version": "1.c04b464c"
        },
        "ret_15m": {
          "age_s": 5.544152,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "f05b3a74a7211b4ce7a23216b532af4d320537ac3b9532ee324f8dbf77d3137c",
          "status": "OK",
          "v": -0.007097050021,
          "version": "1.3fa23ddd"
        },
        "ret_1d": {
          "age_s": 5.544152,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "4871f8f39f073d45e17d3d6f5ca60a8fec098c3c382779b9f1d17c4eff156f1b",
          "status": "OK",
          "v": -0.07827648115,
          "version": "1.b77eca69"
        },
        "ret_20d": {
          "age_s": 254705.5442,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "c89eca0e545e370a2b5106418f52c2c97be259b8d9a271ffd1a96adbaa2aca0a",
          "status": "MISSING",
          "v": null,
          "version": "1.7d1f1942"
        },
        "ret_5d": {
          "age_s": 254705.5442,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "05a741e625955a85a438ad18773375028848616408999e7af63ece7accaed8b3",
          "status": "MISSING",
          "v": null,
          "version": "1.5d56db82"
        },
        "ret_5m": {
          "age_s": 5.544152,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "19753379ae57616102e8755122b80e435f0c978ed5e79cc3435fe9b26513660a",
          "status": "OK",
          "v": -0.0006024614855,
          "version": "1.c10a3b57"
        },
        "ret_60m": {
          "age_s": 5.544152,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "c7d497003ca260f4bb80c0cd4ca5c604cccb4c8b278832591a98f7bcf9224233",
          "status": "OK",
          "v": 0.001120786275,
          "version": "1.6c49ff8f"
        },
        "rsi14": {
          "age_s": 254705.5442,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "1e59b41cf19356a8afb2c1abc8da30ba54a3ae1c9ca6adec3645d67baab39a97",
          "status": "MISSING",
          "v": null,
          "version": "1.273a3a79"
        },
        "rsi14_15m": {
          "age_s": 5.544152,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "8e2405b48f61208fcc98491d12fb4cfef18c440cec8f1c795d9799094ef01d8d",
          "status": "OK",
          "v": 58.43968457,
          "version": "1.f0b8fdaf"
        },
        "rvol_60m": {
          "age_s": 5.544152,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "27cf8ed2d446f97888229373a5ac880ff2e3d212d2e60bbd9ed0395576829c03",
          "status": "OK",
          "v": 0.01016478643,
          "version": "1.84c5ec7e"
        },
        "sellable_qty": {
          "age_s": 0.603453,
          "quality": {},
          "record_hash": "6540832af84a228b7dc7cbb1cbbeca1b7e6606556eb47ce288f2deb6b72b884e",
          "status": "OK",
          "v": "0",
          "version": "1.9cbf72e4"
        },
        "sma20": {
          "age_s": 254705.5442,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "15576f86a2842f5eb53a8c69129bc796ec2bb02d553d6eb692a0246444b821e2",
          "status": "MISSING",
          "v": null,
          "version": "1.80f8a078"
        },
        "sma50": {
          "age_s": 254705.5442,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "c77619dbf2bb36c37659503666953bdfa289b5ad53f8419d72ac47d490aa3455",
          "status": "MISSING",
          "v": null,
          "version": "1.3890c9d7"
        },
        "spread_bps": {
          "age_s": 1.657661,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "dc84a1263326e9e3893336d4edb867f0b2e42290edc0eb0886668afbfa0eaf48",
          "status": "OK",
          "v": 3.444119167,
          "version": "1.e2b080ab"
        },
        "trend_sma20_vs_sma50": {
          "age_s": 254705.5442,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "c3f4c96640a0fefa86efead1a20dc2a8c20470887509f9a64b8b123a7f0f6feb",
          "status": "MISSING",
          "v": null,
          "version": "1.84583425"
        },
        "unrealized_pnl_pct": {
          "age_s": 0.603453,
          "quality": {},
          "record_hash": "87bc37a5609861906bee7037bff5524f53615cb2f65103279f76ec2bef5ec5ee",
          "status": "OK",
          "v": 0,
          "version": "1.7c530604"
        },
        "vol_regime_ratio": {
          "age_s": 5.544152,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "c6313cc86a68c91717f673033fd54720624546900b0f164f27fd627e76149292",
          "status": "OK",
          "v": 1.036548837,
          "version": "1.302e72c1"
        },
        "volume_z20": {
          "age_s": 254705.5442,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "acd6606915e0844ee2fa5f30507b576df69022855968e20bad1ec489ca7b84b7",
          "status": "MISSING",
          "v": null,
          "version": "1.970d159b"
        },
        "volz_tod_15m": {
          "age_s": 5.544152,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "00402ad410208e76d63fb60dc603ca6c5c3933ab4023869011a7814ed1722a9c",
          "status": "OK",
          "v": 0.2274907125,
          "version": "1.4315d547"
        },
        "vwap_dev_session": {
          "age_s": 5.544152,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "a96e2cb38b6d62a078789e516cd81092c72afe3ba66fd637c29b906a6873af69",
          "status": "OK",
          "v": 0.0004911512541,
          "version": "1.b41de1ff"
        }
      }
    },
    "validation_policy": "scored-15m-plus-2m-v1"
  },
  "council_mode": "PAPER_COUNCIL_SKEPTIC_OFF",
  "chair": {
    "note": "No entry signal meets threshold; prearbiter blocks entry and no sellable inventory exists.",
    "role": "CHAIR",
    "run_id": "70f90d11-e0d5-53b4-8295-9e938a0a09ba",
    "candidates": [],
    "schema_version": 2
  },
  "skeptic_audit": {
    "attempts": 0,
    "skip_reason": "DISABLED_BY_OPERATOR"
  },
  "role_outputs": [
    {
      "role": "CHAIR",
      "status": "OK",
      "response": "{\n  \"schema_version\": 2,\n  \"run_id\": \"70f90d11-e0d5-53b4-8295-9e938a0a09ba\",\n  \"role\": \"CHAIR\",\n  \"candidates\": [],\n  \"note\": \"No entry signal meets threshold; prearbiter blocks entry and no sellable inventory exists.\"\n}",
      "error": null
    },
    {
      "role": "LIQUIDITY",
      "status": "OK",
      "response": "{\"schema_version\":2,\"run_id\":\"70f90d11-e0d5-53b4-8295-9e938a0a09ba\",\"source\":\"code\",\"data_confidence\":\"HIGH\",\"role\":\"LIQUIDITY\",\"symbols\":[{\"symbol\":\"INTC\",\"evidence\":[{\"path\":\"symbols.INTC.spread_bps\",\"band\":\"NORMAL\"},{\"path\":\"symbols.INTC.mid_px\",\"band\":\"POSITIVE\"},{\"path\":\"symbols.INTC.volz_tod_15m\",\"band\":\"NORMAL\"}],\"gate\":{\"state\":\"PASS\",\"size_multiplier\":1.0,\"reasons\":[]},\"note\":\"deterministic code assessment\"}]}",
      "error": null
    },
    {
      "role": "PORTFOLIO",
      "status": "OK",
      "response": "{\"data_confidence\": \"HIGH\", \"role\": \"PORTFOLIO\", \"run_id\": \"70f90d11-e0d5-53b4-8295-9e938a0a09ba\", \"schema_version\": 2, \"source\": \"code\", \"symbols\": [{\"evidence\": [{\"band\": \"POSITIVE\", \"path\": \"portfolio.equity\"}, {\"band\": \"POSITIVE\", \"path\": \"portfolio.buying_power\"}, {\"band\": \"ZERO\", \"path\": \"symbols.INTC.position_qty\"}], \"gate\": {\"reasons\": [\"entry_window_open=true\"], \"size_multiplier\": 0.5, \"state\": \"PASS\"}, \"note\": \"Close proximity to safety closeout (834s) limits position size.\", \"symbol\": \"INTC\"}]}",
      "error": null
    },
    {
      "role": "REGIME",
      "status": "OK",
      "response": "{\"symbols\":[{\"symbol\":\"INTC\",\"note\":\"Positive market regime, EMA gap strong, ATR rising, but recent return negative suggests short-term weakness. Long position considered moderately attractive.\",\"evidence\":[{\"path\":\"market.regime_label\",\"band\":\"UPTREND\"},{\"path\":\"symbols.INTC.ema_gap_bps_15m\",\"band\":\"POS_STRONG\"},{\"path\":\"symbols.INTC.atr14_15m\",\"band\":\"POSITIVE\"},{\"path\":\"symbols.INTC.recent_return_10m\",\"band\":\"NEGATIVE\"}]}],\"data_confidence\":\"HIGH\",\"risk_appetite\":\"NEUTRAL\",\"role\":\"REGIME\",\"run_id\":\"70f90d11-e0d5-53b4-8295-9e938a0a09ba\",\"schema_version\":2,\"source\":\"code\"}",
      "error": null
    },
    {
      "role": "TECHNICAL",
      "status": "OK",
      "response": "{\"data_confidence\": \"MED\", \"role\": \"TECHNICAL\", \"run_id\": \"70f90d11-e0d5-53b4-8295-9e938a0a09ba\", \"schema_version\": 2, \"source\": \"code\", \"symbols\": [{\"evidence\": [{\"band\": \"POS_STRONG\", \"path\": \"symbols.INTC.ema_gap_bps_15m\"}, {\"band\": \"FIRM\", \"path\": \"symbols.INTC.rsi14_15m\"}, {\"band\": \"UNCONFIRMED\", \"path\": \"symbols.INTC.intraday_setup_1m\"}, {\"band\": \"POSITIVE\", \"path\": \"symbols.INTC.vwap_dev_session\"}], \"note\": \"Momentum conflicts with short-term doji and negative 15m returns.\", \"signal\": {\"confidence\": 0.8, \"horizon\": \"INTRADAY\", \"score\": 0.58538219, \"state\": \"SIGNAL\"}, \"symbol\": \"INTC\"}]}",
      "error": null
    }
  ],
  "reason_codes": [
    "NO_SIGNAL_ABOVE_THRESHOLD"
  ],
  "notes": [
    "evidence_pack:02a11f18c37101bb26a88b7b0fe1072f0a21b33bc14ceb297afe876c82012252",
    "council_run:70f90d11-e0d5-53b4-8295-9e938a0a09ba",
    "NO_SIGNAL_ABOVE_THRESHOLD"
  ],
  "error": null,
  "proposals_and_risk": []
}
```

</details>

### 14:46:09 ET · DECIDED_HOLD

<details>
<summary>Recorded decision evidence</summary>

```json
{
  "decision_id": "d29c35e9-5443-58a8-a015-058fb38ba87d",
  "inputs": {
    "as_of": "2026-11-23T19:46:07.093561Z",
    "regime": {
      "label": "uptrend"
    },
    "account": {
      "cash": 99803.06,
      "equity": 99803.06,
      "status": "ACTIVE",
      "account_id": "PAPER_ACCOUNT",
      "last_equity": 99803.39,
      "buying_power": 399212.24
    },
    "positions": [],
    "symbols": {
      "INTC": {
        "mid": 58.045,
        "rsi14": null,
        "ret_1d": -0.0783,
        "ret_5d": null,
        "ret_20d": null,
        "atr14_pct": null,
        "price_vs_sma20": null,
        "trend_sma20_vs_sma50": null
      }
    }
  },
  "feature_evidence": {
    "account_ref": "PAPER_ACCOUNT",
    "as_of": "2026-11-23T19:46:07.093561+00:00",
    "availability": {
      "account": "fresh",
      "bars": "fresh",
      "calendar": "fresh",
      "news": "fresh",
      "ok_fraction_core_features": 1.0,
      "quotes": "fresh"
    },
    "bands_hash": "810517c6e124c7ebc23ca0ebce7ef7ba7cc66b30bc21cacc66c1a221174255d4",
    "feasibility": {
      "INTC": {
        "can_buy": true,
        "can_buy_reasons": [],
        "can_sell": false,
        "can_sell_reasons": [
          "NO_SELLABLE_INVENTORY"
        ],
        "entry_window_open": true,
        "entry_window_reason": "",
        "held_qty": "0.0",
        "max_new_notional_usd": "2000.0",
        "sellable_qty": "0"
      }
    },
    "feature_slot": {
      "candles": {
        "INTC|2026-11-23T19:31:00+00:00": "a5309c04231b41b04749996dbc08d1d625cf986b4bacb8d065bd4272b1bcd687",
        "INTC|2026-11-23T19:32:00+00:00": "1316263235fefac976cf3179d15a341ca2faba6862bc2ad845a199a21f1a4ea1",
        "INTC|2026-11-23T19:33:00+00:00": "c37f8ccdeccf9064ac8a9b4e6a21d4ed42be7567ab3ba10eb0558b68028107c0",
        "INTC|2026-11-23T19:34:00+00:00": "564e3a869b90c07bc6f4dc36fc9a4642620456c6cac5272aff6455bd272177b1",
        "INTC|2026-11-23T19:35:00+00:00": "8c40460eb8f86125bf2228c6e0b5478931f3e3a91a013bd23caa1bb828639442",
        "INTC|2026-11-23T19:36:00+00:00": "9cb732a5a05f88fcae5944f0121aac8aaa2713bd234d104b87ddb513e8886ae9",
        "INTC|2026-11-23T19:37:00+00:00": "9d5b09f82117334dcc0f33b8c32ad04009545b4670f26997f04929a89d44df93",
        "INTC|2026-11-23T19:38:00+00:00": "e98c98af48936fd32ec6ad72041fcbfa1de8511a2b8911c69eabcd4ab7117e18",
        "INTC|2026-11-23T19:39:00+00:00": "422314eba37616c0546eed1ed8aa018f6b54ce6bec687378c7704d9ca2065248",
        "INTC|2026-11-23T19:40:00+00:00": "70e0d8b0a63b3723514998b8205402a930375f59ca5308b2f48f6dbab08cd617",
        "INTC|2026-11-23T19:41:00+00:00": "4510c4c83faf5f5878d401794d4b7bed12120a3527e7efc68be6e7a94d44c40b",
        "INTC|2026-11-23T19:42:00+00:00": "98067d1cfbe2cf62a97c2f9a655f0cf4470e9f8fb2391eb0463aff7d674dad4b",
        "INTC|2026-11-23T19:43:00+00:00": "c8d1f80659f571bf3eb64a17b9935be4ce7a092a55afd0608b149b1e717e9011",
        "INTC|2026-11-23T19:44:00+00:00": "c1aa4b559490e25f881fb40af919d8644954d00315de5f007556c6e7791a0b28",
        "INTC|2026-11-23T19:45:00+00:00": "34a1b438e39db05694f921c5baec9ae6582c0220846c45eb8506fabad543f270",
        "SPY|2026-11-23T19:31:00+00:00": "7a616b1bec25ec89392c717c57a4f8a02b7baa240defd1ce7ed414da812d51e0",
        "SPY|2026-11-23T19:32:00+00:00": "13017eef20c793ba8a0c3bee58ceb303a749f3ed6db515430dbcd3f066266ef6",
        "SPY|2026-11-23T19:33:00+00:00": "60acf2b6b72dfb53f598542c183985e00d5820e45e6a15aaa702caa2e7db45df",
        "SPY|2026-11-23T19:34:00+00:00": "205774036f40cb4bc8e44df4d46ef150bd7d25dedeb8a897455bddc1dd4763d8",
        "SPY|2026-11-23T19:35:00+00:00": "a3f33f928527ca6cd947868e44e270cfe45857f8acf9296afd6811bf7c66a716",
        "SPY|2026-11-23T19:36:00+00:00": "20f2610f9083c52c53c44110cf31c15486c3658b74baf10c77427c7f1643e451",
        "SPY|2026-11-23T19:37:00+00:00": "cfc075a20afd9004c6a54e55e02de60aa1ac6fab559ca2bc363b4083a5a7b0e8",
        "SPY|2026-11-23T19:38:00+00:00": "8ac7b4d0dc16f15a1b48e3576c48557a2cf3e5e01e9dbd56ec12e4206987e786",
        "SPY|2026-11-23T19:39:00+00:00": "38712a0709a4972b95a52f42b45fd54896d71cc49ce48651c65445f1a42bf62f",
        "SPY|2026-11-23T19:40:00+00:00": "e49f4baca7c7583df76c009735c11448f1023f1415b68e390409997276db3480",
        "SPY|2026-11-23T19:41:00+00:00": "0dccbf44a642c7d605f69cb3858d90923162c6c2b93f66b9555d77776438a183",
        "SPY|2026-11-23T19:42:00+00:00": "88269dcad14d8b8d3584bb870bfc6f5eed07f56a971f9ad7e1037bfff28a3780",
        "SPY|2026-11-23T19:43:00+00:00": "a4aebaa6965c7c246c1610c4eff9a05d061eff2cadc3940774ca5ab43368ca06",
        "SPY|2026-11-23T19:44:00+00:00": "b91459d6c5ec4fb98cb4404bbe1cd7357fe920ab60a2e98579d2b6fb1626730d",
        "SPY|2026-11-23T19:45:00+00:00": "467c27fb5d5f1da7405a638366403833df31cfdd7aae5abf3fe2d4bf9f1de532"
      },
      "close": "2026-11-23T19:46:00+00:00",
      "feed": "iex",
      "indicator_close": "2026-11-23T19:45:00+00:00",
      "indicator_input_hashes": {
        "INTC": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
        "SPY": "68be2784fe1097306ec89b5433c1c0b0393b316ceebc03170624a4214da8ac5c"
      },
      "provisional": true,
      "records": {
        "market:market:breadth_above_ema21": "d7e2f70fedf1d18806a57fa4210d951ce450efccdd03a1fa716baff26d0f59e9",
        "market:market:regime_label": "b5f7eda754fe89980a8ade83e3496e26768374e4bbb5fca559b77ed06e580f14",
        "market:market:spy_ema_gap_bps_15m": "5885f7d1170e4539d33b130275da00b6751841c47609429095ed1e27403a7ec2",
        "market:market:spy_ret_60m": "79aacdf13ffe6f7e5e20df8085053bec8911948087170044087d3ca2438258a0",
        "market:market:spy_vol_regime_ratio": "e39e42a949ac1efafc382ec1e5c2faf45982563c77be27706d04c43f399a41cc",
        "symbol:INTC:adv_usd_20d": "b9b2c8cd47063244741a0be3a99b852571258b975af9e1831bf9c22ac86c817d",
        "symbol:INTC:atr14_15m": "6f731751bfa53150c4b34c9f00c97b6e20fc9879a19350f0ce7cbe19a7070a61",
        "symbol:INTC:atr14_1d": "7109941c8f13c27be9954427260fd23488765da0017ae6e7268c52c67c282e0d",
        "symbol:INTC:atr14_pct": "72b22515a9b698de8e221ba3601ca48bfe5aa847f96eb780cd201d7da6e1b10b",
        "symbol:INTC:dist_hi_atr": "06f00cdde08da87c6d07b9a98c1cc7291fafb8eb2bcfb2ffc0d4d1117d6860c5",
        "symbol:INTC:dist_lo_atr": "400edc39a01d0abd24e46a1af90c755eb56269eab61f4dad7ffb1d156524e4fb",
        "symbol:INTC:ema21_15m": "026dc43aa182328e915e6f6d23296bedca2f3d61e29ad492593fd2b16c1f2c9c",
        "symbol:INTC:ema9_15m": "779c29eadfec6fe54e83478754f967d3444f194d88d34349bf014707a7b14100",
        "symbol:INTC:ema_gap_bps_15m": "2d80bf72eea509fb31fba6a2c3b863d8d8dc686f8d007db33fe90cf4a50e5145",
        "symbol:INTC:gap_open_pct": "22372f1618bb0042d504687f06dc178f5d5531095633eddeaf4bcfe97a2ded36",
        "symbol:INTC:intraday_ret_1h": "584b190315139eaa5cf532afd4584686eee1ec8a960635264ed6e8e8c24aeec5",
        "symbol:INTC:intraday_setup_1m": "2891e916e5ea899c2f1ab4f06b8ed57abbf5de7a4ec275d4975b6233c4eb498c",
        "symbol:INTC:last_close": "d19401a83eca33beec8f4dc4c9fd9de4a732eca37d9f9287a4931e7ba85850f1",
        "symbol:INTC:macd_hist_15m": "ffc4ec65b3c48fbd631f09dccfb6d59e271d94c9ffd76307010798940056e67d",
        "symbol:INTC:price_vs_sma20": "0d79ec3c1b357a5011464af77c39b3fcad072140f1af42e8fc4caaaa2d603acd",
        "symbol:INTC:recent_price_10m": "bff90b32112a24a17f16f06dcd3bb74ef36b58b1e00a0da9ef5d8a886b5e57fc",
        "symbol:INTC:recent_range_bps_10m": "226405a8a8b423b9d60ca1aa42f7e5fd325adf8437f9bb1d7982e7918760bbc1",
        "symbol:INTC:recent_range_bps_5m": "07d674bb705e08d51a2773d2e2f3f5502c759f6d9436e25cd194ee2efe6fa324",
        "symbol:INTC:recent_return_10m": "4968ec02b93703b15595c1264ed19d7c45456933aa3f1449313a08c21bdad7b2",
        "symbol:INTC:recent_return_5m": "cd02552d5f256a5c50f554ed85e94b762225b0a8f0d1b2eb84f61b30ebf537ff",
        "symbol:INTC:recent_volume_10m": "dcb8ae092f13fa1b470805ee0287333baa9ce293f857b0a0f79e5a143f652f9e",
        "symbol:INTC:recent_volume_5m": "8b727e359743fe80bad7a04504d7881ac83c5ff9a512d44ba45c5015dadc3c77",
        "symbol:INTC:relstr_spy_60m": "dc98008aee49a17ccf13238156fb35e107af0e0af007f00b57f9311a97c39eb5",
        "symbol:INTC:ret_15m": "af614e2e09b01f6580208268f4180defd7184ed1c1d6354c6f4ff11500f8c505",
        "symbol:INTC:ret_1d": "4871f8f39f073d45e17d3d6f5ca60a8fec098c3c382779b9f1d17c4eff156f1b",
        "symbol:INTC:ret_20d": "c89eca0e545e370a2b5106418f52c2c97be259b8d9a271ffd1a96adbaa2aca0a",
        "symbol:INTC:ret_5d": "05a741e625955a85a438ad18773375028848616408999e7af63ece7accaed8b3",
        "symbol:INTC:ret_5m": "f2416daac2531a2fdf77e81769600edd2070094d83652f86a213fac862f441d4",
        "symbol:INTC:ret_60m": "fd09008b1cce82b88bcac19dd1de23f6dddbe95a9f529221693b9b2de41cd2b4",
        "symbol:INTC:rsi14": "1e59b41cf19356a8afb2c1abc8da30ba54a3ae1c9ca6adec3645d67baab39a97",
        "symbol:INTC:rsi14_15m": "8e2405b48f61208fcc98491d12fb4cfef18c440cec8f1c795d9799094ef01d8d",
        "symbol:INTC:rvol_60m": "44afddbf8f5fae3d3ce00dbe3fe834dc5067afaa96b05fc24a3e68891615204e",
        "symbol:INTC:sma20": "15576f86a2842f5eb53a8c69129bc796ec2bb02d553d6eb692a0246444b821e2",
        "symbol:INTC:sma50": "c77619dbf2bb36c37659503666953bdfa289b5ad53f8419d72ac47d490aa3455",
        "symbol:INTC:trend_sma20_vs_sma50": "c3f4c96640a0fefa86efead1a20dc2a8c20470887509f9a64b8b123a7f0f6feb",
        "symbol:INTC:vol_regime_ratio": "213e09b985a8f726fdf9e9f11ba09e69bec3cfbf91d072c42d099ec1934f239e",
        "symbol:INTC:volume_z20": "acd6606915e0844ee2fa5f30507b576df69022855968e20bad1ec489ca7b84b7",
        "symbol:INTC:volz_tod_15m": "00402ad410208e76d63fb60dc603ca6c5c3933ab4023869011a7814ed1722a9c",
        "symbol:INTC:vwap_dev_session": "b4d3abd837a0458f9b1760d30cf06f3a060ef0b6cf7f687e328f2e7998a00392",
        "symbol:SPY:adv_usd_20d": "92e94f829df49f4b3a8d0be7612b000e92190d5356f55e566f04069ca7b9ffd5",
        "symbol:SPY:atr14_15m": "7ab448ef9d85396282151eac59236f9553a486b5c77591049f30866a0df20c74",
        "symbol:SPY:atr14_1d": "3cac187afe8b3f12d7d3b3b86986d403d549ebe59a7ccfaa10a213aaea0d6f29",
        "symbol:SPY:atr14_pct": "86a49f6a2b7c51bced8c4109a9b641fd3430da5d9872f600c092cec75526d214",
        "symbol:SPY:dist_hi_atr": "0f88bcdacf7ebb10cc09f3d0ebc8a75b1299c7264f429c983c5a5f72a0f8de80",
        "symbol:SPY:dist_lo_atr": "91df22cd7b222485c71f94d68a6d3ecec22493bb8bc5673d0dfa087a469d91af",
        "symbol:SPY:ema21_15m": "e101df90a64d088f78547e381107b8db83b2541409047168500bf08d4caa4b43",
        "symbol:SPY:ema9_15m": "d9a6929dcd2aa029a0657e3b23036ea5c8e549c3e28f704d22c59d9141f45d16",
        "symbol:SPY:ema_gap_bps_15m": "12f402c62d8c646eb7b75bb92bec226e49110827a04064a50b8a1e5b881fc789",
        "symbol:SPY:gap_open_pct": "1c9616a65f2f013255300b42e56d88ac7a725e105e6f59b39d79e458ad29184e",
        "symbol:SPY:intraday_ret_1h": "4a3cbce2b9dcc1b99d6875d1dfcc341ba613acfd2d05e42ab8e2dd8730e5c8b3",
        "symbol:SPY:intraday_setup_1m": "2a9acba29a751f1f7d8691df45aaf0fb9552358779cc983642dd2550284ea67c",
        "symbol:SPY:last_close": "caf596deca80d26016ad4208908f5e9f946155af82bcf05ef2276748182b2361",
        "symbol:SPY:macd_hist_15m": "7c1f84aa5b3c914a24e8512883539348c328fedf77f1ca8fddef3c9428311b8a",
        "symbol:SPY:price_vs_sma20": "963d8268f25c4849a1b268733b11edd2005fe4a8c767d1439d8478255d5a22c9",
        "symbol:SPY:recent_price_10m": "b7b1e2b96255fc446e63596036791e39d04e8f30433ece2e130ef46fa1dd1449",
        "symbol:SPY:recent_range_bps_10m": "258c4fb3a9d1469d6f6d670f463c7ae41c801bf4773dbf875df75e94c8b2fef4",
        "symbol:SPY:recent_range_bps_5m": "40c1e28e72600ecfe8ad3c662c1615a0e74bab573d95ee505a908ba9c8acdda4",
        "symbol:SPY:recent_return_10m": "b761a5b0dab088b327ed4bd06d09ee5bab742748b10fb795f91ea128a97af06b",
        "symbol:SPY:recent_return_5m": "b29f738bebbeee9e0e71908bdbbd42366f66948f9c92620958ef5c582d0987b2",
        "symbol:SPY:recent_volume_10m": "5b9eba9557924fe8221c9fe942d0c005be010faeb9ab7dc799a8bf4f53caf3c9",
        "symbol:SPY:recent_volume_5m": "6c33575d700ad02feee2bbcbbf9dc9494ab4054f42c40014e3a0b4ab24f8ceca",
        "symbol:SPY:relstr_spy_60m": "8192ee3c1e096d3220e21bd96547302036aad20b1f8b2a88d06eb43fca3d16bd",
        "symbol:SPY:ret_15m": "844afef83f8f5f6dd32bfab36ca3f9841b7de383f14ca8754392d5dbef785bfd",
        "symbol:SPY:ret_1d": "aab94a7dafcf360313d949fc12ced963ccb5a8b3ef27866b2b930d2d5817c533",
        "symbol:SPY:ret_20d": "5cb42b7c179c74bdcedf0dbf4ce0ee12832341fe24b75d306dccc8cc03e792c3",
        "symbol:SPY:ret_5d": "7c31dada2f0a36e24d03e89b66cb73d377f3c298c10867a1be2b05be76be6a0c",
        "symbol:SPY:ret_5m": "270023e30795b1f050ce27c81af48a828c2ae85b0ae6f309bf9e87cf7c237593",
        "symbol:SPY:ret_60m": "2aefe725a25e4d8522264797ba11fc7d56678face220deb89d5ba387a98102a9",
        "symbol:SPY:rsi14": "ee11c2b462281f9fc927ac380b6bb2557ff2e158729fe2f17aa91d152eb3fb9f",
        "symbol:SPY:rsi14_15m": "7a2d8a98c627154aeccdc9a68b885c12330bcb82ce58cddb4d0a2f4136033fc0",
        "symbol:SPY:rvol_60m": "2256cb312ff8112e1454ff93fbb1613db3afff2f42e428eb86627b17d2723a00",
        "symbol:SPY:sma20": "1b30496ca2845ccd7a79462c221d840260e1c0361b7feb9dedbc5dc30bd4b2a5",
        "symbol:SPY:sma50": "94c11d37cff9b64498753612d4be2b84f39d1931bd55ec9e573a0c8697ceb72b",
        "symbol:SPY:trend_sma20_vs_sma50": "8aee1d285ca5a8e44083c58d0fad60754235fda2855c6ac02c9796bc41cff8bc",
        "symbol:SPY:vol_regime_ratio": "4ffc3949cf1bd4dda59b5010b1ddfd6010e07dc7dd728c064b31b558b3b3810f",
        "symbol:SPY:volume_z20": "26f74a49cf931c478f404ef3e6a0850c2e214cc588216f87e068535e16f86e9f",
        "symbol:SPY:volz_tod_15m": "29640670f4a0587e4e43a5ad4cd8d40a485c1b2537f64212b1cb41ffc2d19792",
        "symbol:SPY:vwap_dev_session": "49f3e5dfc23a12719da53a7565d3471acbf0bce2f40d063617b21db0fbf0ec6c"
      },
      "symbols": [
        "INTC",
        "SPY"
      ]
    },
    "horizons": {
      "INTC": {
        "10m": {
          "age_s": 7.093561,
          "last_bar_end": "2026-11-23T19:46:00+00:00",
          "status": "OK"
        },
        "15m": {
          "age_s": 67.093561,
          "last_bar_end": "2026-11-23T19:45:00+00:00",
          "status": "OK"
        },
        "5m": {
          "age_s": 7.093561,
          "last_bar_end": "2026-11-23T19:46:00+00:00",
          "status": "OK"
        },
        "60m": {
          "age_s": 67.093561,
          "last_bar_end": "2026-11-23T19:45:00+00:00",
          "status": "OK"
        },
        "horizon_conflict": false
      }
    },
    "market": {
      "breadth_above_ema21": {
        "age_s": 67.093561,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "d7e2f70fedf1d18806a57fa4210d951ce450efccdd03a1fa716baff26d0f59e9",
        "status": "OK",
        "v": 1.0,
        "version": "1.1dfe664d"
      },
      "minutes_to_close": {
        "age_s": 0.665943,
        "quality": {},
        "record_hash": "c155b929a74e32d23cc1d0c7c55855e7fba549a6fe32126ab13b24027a343107",
        "status": "OK",
        "v": 73.89287303,
        "version": "1.e79b1ead"
      },
      "regime_label": {
        "age_s": 67.093561,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "b5f7eda754fe89980a8ade83e3496e26768374e4bbb5fca559b77ed06e580f14",
        "status": "OK",
        "v": "UPTREND",
        "version": "1.f8b361d7"
      },
      "session_phase": {
        "age_s": 0.665943,
        "quality": {},
        "record_hash": "453f89935696d4a7708d08cdb296ad76b18dcc1250d10acdacdac38a62d8bc24",
        "status": "OK",
        "v": "NORMAL",
        "version": "1.91f88fe8"
      },
      "spy_ema_gap_bps_15m": {
        "age_s": 67.093561,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "5885f7d1170e4539d33b130275da00b6751841c47609429095ed1e27403a7ec2",
        "status": "OK",
        "v": 37.89644347,
        "version": "1.fda7da7a"
      },
      "spy_ret_60m": {
        "age_s": 67.093561,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "79aacdf13ffe6f7e5e20df8085053bec8911948087170044087d3ca2438258a0",
        "status": "OK",
        "v": -0.0008866476407,
        "version": "1.9feddbd1"
      },
      "spy_vol_regime_ratio": {
        "age_s": 67.093561,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "e39e42a949ac1efafc382ec1e5c2faf45982563c77be27706d04c43f399a41cc",
        "status": "OK",
        "v": 1.394476868,
        "version": "1.3b7257aa"
      }
    },
    "meta": {
      "news": {
        "INTC": {
          "effective_weight": 0,
          "in_window": 0,
          "newest_age_min": 1784.668226,
          "policy": "48h retained; per-article decay and minimum relevance; 4h count is descriptive",
          "poller_last_ok_age_s": 14.987577,
          "retrieved": 1,
          "selected": 0,
          "state": "QUIET",
          "window_min": 240
        }
      }
    },
    "news_blob_hash": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
    "news_context_blob_hash": "ef023692226f6319baf7f6429f023deb1a988f59c953b103e7a5f425a6a5d062",
    "portfolio": {
      "aggregate_cap_usd": {
        "age_s": 0.665943,
        "quality": {},
        "record_hash": "25f9d812b05ac3e2a196a486d1071c31c3aca7bc22c62d424474557340491ad9",
        "status": "OK",
        "v": "49901.530",
        "version": "1.5b3d1daf"
      },
      "aggregate_headroom_usd": {
        "age_s": 0.665943,
        "quality": {},
        "record_hash": "d33baf17aad7f410c58c6cec427d1f7e560a1fbd6172b8dc5ea6e740944b9728",
        "status": "OK",
        "v": "49901.530",
        "version": "1.7f894fff"
      },
      "buying_power": {
        "age_s": 0.665943,
        "quality": {},
        "record_hash": "d880dcc9f347f6df265c5338c6047f56d4de225d5cf52136b620632a9e501a13",
        "status": "OK",
        "v": "399212.24",
        "version": "1.74948dec"
      },
      "cash": {
        "age_s": 0.665943,
        "quality": {},
        "record_hash": "c9dcd5cb72c5a5d0afe82d873724af180a0d64c8770f2f50574279c42386ec69",
        "status": "OK",
        "v": "99803.06",
        "version": "1.b067f5e3"
      },
      "day_pnl_pct": {
        "age_s": 0.665943,
        "quality": {},
        "record_hash": "1ef7748da82aa1e86bb649d4a40eefab6ed052fcda0da943f3d73643aafda161",
        "status": "OK",
        "v": "-0.0003306500911441986088849300",
        "version": "1.35e81852"
      },
      "drawdown_pct": {
        "age_s": 0.665943,
        "quality": {},
        "record_hash": "2272dff78a7fd8b2031d0a97c4341c752f9a87dace1f69b1cc08124141e8c974",
        "status": "MISSING",
        "v": null,
        "version": "1.19aac9ba"
      },
      "equity": {
        "age_s": 0.665943,
        "quality": {},
        "record_hash": "0d04a807eddb6e05269d81bdbdc3d98ac34cec721a5b129e25b42bf777e3d2e1",
        "status": "OK",
        "v": "99803.06",
        "version": "1.a2192616"
      },
      "gross_exposure_pct": {
        "age_s": 0.665943,
        "quality": {},
        "record_hash": "182eb8e39c62532e009cd962d309f8c94507e1093bac765d68015caa0556ddc2",
        "status": "OK",
        "v": "0E+2",
        "version": "1.b82cc518"
      },
      "gross_exposure_usd": {
        "age_s": 0.665943,
        "quality": {},
        "record_hash": "830c34256dba463904b3f6b64c46f30005e9749f1d505047ae15f33267114ede",
        "status": "OK",
        "v": "0",
        "version": "1.e4c8752b"
      },
      "last_reconcile_age_s": {
        "age_s": 0.665943,
        "quality": {},
        "record_hash": "14d19b8aec7cadd217622ded6c7235435a85927131a076d5a255f67df195a936",
        "status": "OK",
        "v": 0,
        "version": "1.5ed0382f"
      },
      "open_buy_notional_usd": {
        "age_s": 0.665943,
        "quality": {},
        "record_hash": "837f10080ea2739401d0b6ec30449842be4207c44b6e8370821c29ee38deb349",
        "status": "OK",
        "v": "0",
        "version": "1.0bd0ead1"
      },
      "open_orders": {
        "age_s": 0.665943,
        "quality": {},
        "record_hash": "97bf01ebed26b8ed25a90f563f8292244bbf03ef54c88e80d8890132bb482d5d",
        "status": "OK",
        "v": [],
        "version": "1.1cf37cbf"
      },
      "open_orders_count": {
        "age_s": 0.665943,
        "quality": {},
        "record_hash": "9303e3138a85c72c0bbb2e5a76251b1120e27359ac2df54a11f443487848ac2d",
        "status": "OK",
        "v": 0,
        "version": "1.1db4227a"
      },
      "pending_reserved_usd": {
        "age_s": 0.665943,
        "quality": {},
        "record_hash": "46198f70ee3fdce48bed9a9e8fff950a95f3396d0f187a41da5c1a8a553aeb12",
        "status": "OK",
        "v": "0",
        "version": "1.1c3e9604"
      },
      "positions": {
        "age_s": 0.665943,
        "quality": {},
        "record_hash": "9688870e73ed290165099bfd76b507a6558156a92fe3447881da183c223d8662",
        "status": "OK",
        "v": [],
        "version": "1.c3284657"
      }
    },
    "registry_hash": "0fd3271269748046863b2f0558e45e2c333bb352eccc9899b7ff42277c8386fc",
    "schema_version": 1,
    "symbols": {
      "INTC": {
        "adv_usd_20d": {
          "age_s": 254767.0936,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "b9b2c8cd47063244741a0be3a99b852571258b975af9e1831bf9c22ac86c817d",
          "status": "OK",
          "v": 304793568.9,
          "version": "1.04f5e91f"
        },
        "ask_px": {
          "age_s": 1.453233,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "3d16e06dc01909e2a093064d556559e9df70ff89168fe21f9a8409a48aa8c491",
          "status": "OK",
          "v": 58.05,
          "version": "1.d21cdd09"
        },
        "atr14_15m": {
          "age_s": 67.093561,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "6f731751bfa53150c4b34c9f00c97b6e20fc9879a19350f0ce7cbe19a7070a61",
          "status": "OK",
          "v": 0.7629598219,
          "version": "1.0cd14e73"
        },
        "atr14_1d": {
          "age_s": 254767.0936,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "7109941c8f13c27be9954427260fd23488765da0017ae6e7268c52c67c282e0d",
          "status": "MISSING",
          "v": null,
          "version": "1.65e38f4c"
        },
        "atr14_pct": {
          "age_s": 254767.0936,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "72b22515a9b698de8e221ba3601ca48bfe5aa847f96eb780cd201d7da6e1b10b",
          "status": "MISSING",
          "v": null,
          "version": "1.87450ee9"
        },
        "bid_px": {
          "age_s": 1.453233,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "2461e4e8970337f8b84404980c86d50d21dcca1d27ca1ee30588896995f32240",
          "status": "OK",
          "v": 58.04,
          "version": "1.149628cd"
        },
        "dist_hi_atr": {
          "age_s": 67.093561,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "06f00cdde08da87c6d07b9a98c1cc7291fafb8eb2bcfb2ffc0d4d1117d6860c5",
          "status": "OK",
          "v": -1.946367236,
          "version": "1.913ffc4a"
        },
        "dist_lo_atr": {
          "age_s": 67.093561,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "400edc39a01d0abd24e46a1af90c755eb56269eab61f4dad7ffb1d156524e4fb",
          "status": "OK",
          "v": 1.76942476,
          "version": "1.79ba4c70"
        },
        "ema21_15m": {
          "age_s": 67.093561,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "026dc43aa182328e915e6f6d23296bedca2f3d61e29ad492593fd2b16c1f2c9c",
          "status": "OK",
          "v": 57.40577599,
          "version": "1.bfcac61e"
        },
        "ema9_15m": {
          "age_s": 67.093561,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "779c29eadfec6fe54e83478754f967d3444f194d88d34349bf014707a7b14100",
          "status": "OK",
          "v": 58.09168398,
          "version": "1.81255de8"
        },
        "ema_gap_bps_15m": {
          "age_s": 67.093561,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "2d80bf72eea509fb31fba6a2c3b863d8d8dc686f8d007db33fe90cf4a50e5145",
          "status": "OK",
          "v": 119.4841427,
          "version": "1.d4519f3c"
        },
        "gap_open_pct": {
          "age_s": 67.093561,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "22372f1618bb0042d504687f06dc178f5d5531095633eddeaf4bcfe97a2ded36",
          "status": "MISSING",
          "v": null,
          "version": "1.27438d4d"
        },
        "halted": {
          "age_s": 0.665943,
          "quality": {},
          "record_hash": "b6dab04865954578a2d0da7ec61c1feeae48422f71fbe22ff0c51261ffae5118",
          "status": "OK",
          "v": false,
          "version": "1.22c5cf87"
        },
        "held_minutes": {
          "age_s": 0.665943,
          "quality": {},
          "record_hash": "12b00598e5a77aa88b5203cdbb21420d7b46cb24c91d8ffd566b45fd192cf3f1",
          "status": "MISSING",
          "v": null,
          "version": "1.de6ed6d3"
        },
        "intraday_ret_1h": {
          "age_s": 67.093561,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "584b190315139eaa5cf532afd4584686eee1ec8a960635264ed6e8e8c24aeec5",
          "status": "OK",
          "v": 0.001120786275,
          "version": "1.c3bb7751"
        },
        "intraday_setup_1m": {
          "age_s": 7.093561,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "9da5432a501039b1ba1d843a8d8b1b2fe9ec232d65c1bd3c1eb3348303630aeb",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:46:00+00:00",
            "window_start": "2026-11-23T19:36:00+00:00"
          },
          "record_hash": "2891e916e5ea899c2f1ab4f06b8ed57abbf5de7a4ec275d4975b6233c4eb498c",
          "status": "OK",
          "v": {
            "confirmation": "UNCONFIRMED",
            "pattern": "DOJI",
            "prior_trend": "FLAT",
            "range_break": "INSIDE",
            "range_ceiling": 58.255,
            "range_floor": 58.01,
            "setup_minute": 8,
            "volume_ratio": 1.1251
          },
          "version": "1.2a1f51e0"
        },
        "last_close": {
          "age_s": 254767.0936,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "d19401a83eca33beec8f4dc4c9fd9de4a732eca37d9f9287a4931e7ba85850f1",
          "status": "MISSING",
          "v": null,
          "version": "1.f2485fc2"
        },
        "luld_active": {
          "age_s": 0.665943,
          "quality": {},
          "record_hash": "a3f7e5c74a16b17348ad97b4a0c278e3c91887e68835b993b42268aa8a239492",
          "status": "MISSING",
          "v": null,
          "version": "1.84a715b2"
        },
        "macd_hist_15m": {
          "age_s": 67.093561,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "ffc4ec65b3c48fbd631f09dccfb6d59e271d94c9ffd76307010798940056e67d",
          "status": "OK",
          "v": -0.07751173219,
          "version": "1.391617c8"
        },
        "mid_px": {
          "age_s": 1.453233,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "543d633338bee7fae4f2c98c2811b4d1efb8a2a4c94fb19ac4f57059c37ec09b",
          "status": "OK",
          "v": 58.045,
          "version": "1.d567a349"
        },
        "news_age_min_latest": {
          "age_s": 14.987577,
          "quality": {},
          "record_hash": "8c3810ef7e77320250e34434e58d2a9f51a34180e87b6c42c50e3e8340290aae",
          "status": "MISSING",
          "v": null,
          "version": "1.d0f79dc8"
        },
        "news_confirmed": {
          "age_s": 0,
          "quality": {
            "source": "stored news and pinned price features"
          },
          "status": "OK",
          "v": false,
          "version": "news-confirmation-v2"
        },
        "news_count_1h": {
          "age_s": 14.987577,
          "quality": {},
          "record_hash": "6a9d3c22645612f9d19a7f6e96e1c8cec3c948eef0e4dd47e9020f68c4b79e16",
          "status": "OK",
          "v": 0,
          "version": "1.0c9362fe"
        },
        "news_count_48h": {
          "age_s": 14.987577,
          "quality": {
            "as_of": "2026-11-23T19:46:07.093561+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 1,
          "version": "news-context-v2"
        },
        "news_count_4h": {
          "age_s": 14.987577,
          "quality": {
            "as_of": "2026-11-23T19:46:07.093561+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 0,
          "version": "news-context-v2"
        },
        "news_effective_sentiment": {
          "age_s": 0,
          "quality": {
            "selected": 0,
            "source": "decayed stored article metadata"
          },
          "status": "MISSING",
          "v": 0.0,
          "version": "news-decay-v2"
        },
        "news_event_flags_4h": {
          "age_s": 14.987577,
          "quality": {},
          "record_hash": "befc972461a6105bcd03b24db55a747127de7aa8bb9e6a2f1a1c8d1ff4859b6c",
          "status": "OK",
          "v": [],
          "version": "1.0b5a8a44"
        },
        "news_max_materiality_4h": {
          "age_s": 14.987577,
          "quality": {},
          "record_hash": "a21a1a118906b272cd123cadc4e68fe62718a4f8f146e564d968e0d3b04e7df6",
          "status": "OK",
          "v": 0,
          "version": "1.9c45e9b4"
        },
        "news_newest_age_min": {
          "age_s": 14.987577,
          "quality": {
            "as_of": "2026-11-23T19:46:07.093561+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 1784.668226,
          "version": "news-context-v2"
        },
        "news_novelty_max_4h": {
          "age_s": 14.987577,
          "quality": {},
          "record_hash": "90b6d98225af04f6d8ee7463860e4bf64bee27a400a184e73f0f17e9d13364cb",
          "status": "OK",
          "v": false,
          "version": "1.15ceb7bf"
        },
        "news_sent_ewm_240m": {
          "age_s": 14.987577,
          "quality": {},
          "record_hash": "6fd88679b5f7baf8f9de6d3729f2248f7890d3092015b6565f066954be42564c",
          "status": "OK",
          "v": 0,
          "version": "1.9cad993f"
        },
        "news_sent_ewm_60m": {
          "age_s": 14.987577,
          "quality": {},
          "record_hash": "1988ec5c6a21878699e74e9d0e9e9f31670a764cbca6a73dd9c6dd6a4293414a",
          "status": "OK",
          "v": 0,
          "version": "1.74ab70c1"
        },
        "news_source_div_4h": {
          "age_s": 14.987577,
          "quality": {},
          "record_hash": "9398c6227a904ac7fa7535de900892924ae3a5539e7d6974b2aa01cacee7c4a1",
          "status": "OK",
          "v": 0,
          "version": "1.6fd469c4"
        },
        "position_qty": {
          "age_s": 0.665943,
          "quality": {},
          "record_hash": "6cd912d55f67f8f4d3c81ecba40299850b233a87a8b4a22c2bd11f9021b438cd",
          "status": "OK",
          "v": "0",
          "version": "1.3a512120"
        },
        "position_value_usd": {
          "age_s": 0.665943,
          "quality": {},
          "record_hash": "461aaab8bac5650fe2a3802d80a77d07ecf4d59057e716b07bb41c922a3c241f",
          "status": "OK",
          "v": "0",
          "version": "1.9100bec4"
        },
        "price_vs_sma20": {
          "age_s": 254767.0936,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "0d79ec3c1b357a5011464af77c39b3fcad072140f1af42e8fc4caaaa2d603acd",
          "status": "MISSING",
          "v": null,
          "version": "1.a986b9cc"
        },
        "recent_price_10m": {
          "age_s": 7.093561,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "9da5432a501039b1ba1d843a8d8b1b2fe9ec232d65c1bd3c1eb3348303630aeb",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:46:00+00:00",
            "window_start": "2026-11-23T19:36:00+00:00"
          },
          "record_hash": "bff90b32112a24a17f16f06dcd3bb74ef36b58b1e00a0da9ef5d8a886b5e57fc",
          "status": "OK",
          "v": {
            "candles": [
              [
                0,
                58.255,
                58.255,
                58.145,
                58.15,
                5368.0,
                "VERIFIED_BAR"
              ],
              [
                1,
                58.16,
                58.175,
                58.05,
                58.08,
                12906.0,
                "VERIFIED_BAR"
              ],
              [
                2,
                58.085,
                58.13,
                58.045,
                58.045,
                3139.0,
                "VERIFIED_BAR"
              ],
              [
                3,
                58.045,
                58.165,
                58.045,
                58.095,
                12394.0,
                "VERIFIED_BAR"
              ],
              [
                4,
                58.095,
                58.19,
                58.045,
                58.185,
                11202.0,
                "VERIFIED_BAR"
              ],
              [
                5,
                58.21,
                58.21,
                58.065,
                58.07,
                11493.0,
                "VERIFIED_BAR"
              ],
              [
                6,
                58.07,
                58.095,
                58.01,
                58.01,
                9725.0,
                "VERIFIED_BAR"
              ],
              [
                7,
                58.03,
                58.09,
                58.03,
                58.03,
                7536.0,
                "VERIFIED_BAR"
              ],
              [
                8,
                58.06,
                58.075,
                58.03,
                58.06,
                5274.0,
                "VERIFIED_BAR"
              ],
              [
                9,
                58.07,
                58.11,
                58.03,
                58.03,
                10942.0,
                "VERIFIED_BAR"
              ]
            ],
            "columns": [
              "minute_offset",
              "open",
              "high",
              "low",
              "close",
              "volume",
              "coverage"
            ],
            "feed": "iex",
            "window_end": "2026-11-23T19:46:00+00:00",
            "window_start": "2026-11-23T19:36:00+00:00",
            "windows": {
              "10m": {
                "close": 58.03,
                "open": 58.255,
                "range_bps": 42.05647584,
                "return": -0.003862329414,
                "status": "OK",
                "volume": 89979.0
              },
              "5m": {
                "close": 58.03,
                "open": 58.21,
                "range_bps": 34.35835767,
                "return": -0.00309225219,
                "status": "OK",
                "volume": 44970.0
              }
            }
          },
          "version": "1.b12384d7"
        },
        "recent_range_bps_10m": {
          "age_s": 7.093561,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "9da5432a501039b1ba1d843a8d8b1b2fe9ec232d65c1bd3c1eb3348303630aeb",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:46:00+00:00",
            "window_start": "2026-11-23T19:36:00+00:00"
          },
          "record_hash": "226405a8a8b423b9d60ca1aa42f7e5fd325adf8437f9bb1d7982e7918760bbc1",
          "status": "OK",
          "v": 42.05647584,
          "version": "1.b7dd2e6e"
        },
        "recent_range_bps_5m": {
          "age_s": 7.093561,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "9da5432a501039b1ba1d843a8d8b1b2fe9ec232d65c1bd3c1eb3348303630aeb",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:46:00+00:00",
            "window_start": "2026-11-23T19:36:00+00:00"
          },
          "record_hash": "07d674bb705e08d51a2773d2e2f3f5502c759f6d9436e25cd194ee2efe6fa324",
          "status": "OK",
          "v": 34.35835767,
          "version": "1.860a2856"
        },
        "recent_return_10m": {
          "age_s": 7.093561,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "9da5432a501039b1ba1d843a8d8b1b2fe9ec232d65c1bd3c1eb3348303630aeb",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:46:00+00:00",
            "window_start": "2026-11-23T19:36:00+00:00"
          },
          "record_hash": "4968ec02b93703b15595c1264ed19d7c45456933aa3f1449313a08c21bdad7b2",
          "status": "OK",
          "v": -0.003862329414,
          "version": "1.03c04840"
        },
        "recent_return_5m": {
          "age_s": 7.093561,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "9da5432a501039b1ba1d843a8d8b1b2fe9ec232d65c1bd3c1eb3348303630aeb",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:46:00+00:00",
            "window_start": "2026-11-23T19:36:00+00:00"
          },
          "record_hash": "cd02552d5f256a5c50f554ed85e94b762225b0a8f0d1b2eb84f61b30ebf537ff",
          "status": "OK",
          "v": -0.00309225219,
          "version": "1.a9090b46"
        },
        "recent_volume_10m": {
          "age_s": 7.093561,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "9da5432a501039b1ba1d843a8d8b1b2fe9ec232d65c1bd3c1eb3348303630aeb",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:46:00+00:00",
            "window_start": "2026-11-23T19:36:00+00:00"
          },
          "record_hash": "dcb8ae092f13fa1b470805ee0287333baa9ce293f857b0a0f79e5a143f652f9e",
          "status": "OK",
          "v": 89979.0,
          "version": "1.891ed5cd"
        },
        "recent_volume_5m": {
          "age_s": 7.093561,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "9da5432a501039b1ba1d843a8d8b1b2fe9ec232d65c1bd3c1eb3348303630aeb",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:46:00+00:00",
            "window_start": "2026-11-23T19:36:00+00:00"
          },
          "record_hash": "8b727e359743fe80bad7a04504d7881ac83c5ff9a512d44ba45c5015dadc3c77",
          "status": "OK",
          "v": 44970.0,
          "version": "1.c7331f02"
        },
        "relstr_spy_60m": {
          "age_s": 67.093561,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "dc98008aee49a17ccf13238156fb35e107af0e0af007f00b57f9311a97c39eb5",
          "status": "OK",
          "v": 0.0008866476407,
          "version": "1.c04b464c"
        },
        "ret_15m": {
          "age_s": 67.093561,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "af614e2e09b01f6580208268f4180defd7184ed1c1d6354c6f4ff11500f8c505",
          "status": "OK",
          "v": -0.007015742642,
          "version": "1.3fa23ddd"
        },
        "ret_1d": {
          "age_s": 67.093561,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "4871f8f39f073d45e17d3d6f5ca60a8fec098c3c382779b9f1d17c4eff156f1b",
          "status": "OK",
          "v": -0.07827648115,
          "version": "1.b77eca69"
        },
        "ret_20d": {
          "age_s": 254767.0936,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "c89eca0e545e370a2b5106418f52c2c97be259b8d9a271ffd1a96adbaa2aca0a",
          "status": "MISSING",
          "v": null,
          "version": "1.7d1f1942"
        },
        "ret_5d": {
          "age_s": 254767.0936,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "05a741e625955a85a438ad18773375028848616408999e7af63ece7accaed8b3",
          "status": "MISSING",
          "v": null,
          "version": "1.5d56db82"
        },
        "ret_5m": {
          "age_s": 67.093561,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "f2416daac2531a2fdf77e81769600edd2070094d83652f86a213fac862f441d4",
          "status": "OK",
          "v": -0.002663916817,
          "version": "1.c10a3b57"
        },
        "ret_60m": {
          "age_s": 67.093561,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "fd09008b1cce82b88bcac19dd1de23f6dddbe95a9f529221693b9b2de41cd2b4",
          "status": "OK",
          "v": 0.0,
          "version": "1.6c49ff8f"
        },
        "rsi14": {
          "age_s": 254767.0936,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "1e59b41cf19356a8afb2c1abc8da30ba54a3ae1c9ca6adec3645d67baab39a97",
          "status": "MISSING",
          "v": null,
          "version": "1.273a3a79"
        },
        "rsi14_15m": {
          "age_s": 67.093561,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "8e2405b48f61208fcc98491d12fb4cfef18c440cec8f1c795d9799094ef01d8d",
          "status": "OK",
          "v": 58.43968457,
          "version": "1.f0b8fdaf"
        },
        "rvol_60m": {
          "age_s": 67.093561,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "44afddbf8f5fae3d3ce00dbe3fe834dc5067afaa96b05fc24a3e68891615204e",
          "status": "OK",
          "v": 0.01016000278,
          "version": "1.84c5ec7e"
        },
        "sellable_qty": {
          "age_s": 0.665943,
          "quality": {},
          "record_hash": "5059a91835d17fcf0a524ebe458e89d5f74b26fffd1422b522c63dcbd5e725c2",
          "status": "OK",
          "v": "0",
          "version": "1.9cbf72e4"
        },
        "sma20": {
          "age_s": 254767.0936,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "15576f86a2842f5eb53a8c69129bc796ec2bb02d553d6eb692a0246444b821e2",
          "status": "MISSING",
          "v": null,
          "version": "1.80f8a078"
        },
        "sma50": {
          "age_s": 254767.0936,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "c77619dbf2bb36c37659503666953bdfa289b5ad53f8419d72ac47d490aa3455",
          "status": "MISSING",
          "v": null,
          "version": "1.3890c9d7"
        },
        "spread_bps": {
          "age_s": 1.453233,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "8fd3bf4dd7d81cc82d1b654af49af0b8f96b751bc6de31602f8dc957eb728ce8",
          "status": "OK",
          "v": 1.722801275,
          "version": "1.e2b080ab"
        },
        "trend_sma20_vs_sma50": {
          "age_s": 254767.0936,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "c3f4c96640a0fefa86efead1a20dc2a8c20470887509f9a64b8b123a7f0f6feb",
          "status": "MISSING",
          "v": null,
          "version": "1.84583425"
        },
        "unrealized_pnl_pct": {
          "age_s": 0.665943,
          "quality": {},
          "record_hash": "b373d66d77e2c8d61f6e7eb5179c5865ed3d723d229a18588d4a9ea068622ddf",
          "status": "OK",
          "v": 0,
          "version": "1.7c530604"
        },
        "vol_regime_ratio": {
          "age_s": 67.093561,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "213e09b985a8f726fdf9e9f11ba09e69bec3cfbf91d072c42d099ec1934f239e",
          "status": "OK",
          "v": 1.033428015,
          "version": "1.302e72c1"
        },
        "volume_z20": {
          "age_s": 254767.0936,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "acd6606915e0844ee2fa5f30507b576df69022855968e20bad1ec489ca7b84b7",
          "status": "MISSING",
          "v": null,
          "version": "1.970d159b"
        },
        "volz_tod_15m": {
          "age_s": 67.093561,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "00402ad410208e76d63fb60dc603ca6c5c3933ab4023869011a7814ed1722a9c",
          "status": "OK",
          "v": 0.2274907125,
          "version": "1.4315d547"
        },
        "vwap_dev_session": {
          "age_s": 67.093561,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "b4d3abd837a0458f9b1760d30cf06f3a060ef0b6cf7f687e328f2e7998a00392",
          "status": "OK",
          "v": -2.712596621e-05,
          "version": "1.b41de1ff"
        }
      }
    },
    "validation_policy": "scored-15m-plus-2m-v1"
  },
  "council_mode": "PAPER_COUNCIL_SKEPTIC_OFF",
  "chair": {
    "note": "Entry not approved: prearbiter signals below threshold and no entry_ok; cannot initiate BUY.",
    "role": "CHAIR",
    "run_id": "d29c35e9-5443-58a8-a015-058fb38ba87d",
    "candidates": [],
    "schema_version": 2
  },
  "skeptic_audit": {
    "attempts": 0,
    "skip_reason": "DISABLED_BY_OPERATOR"
  },
  "role_outputs": [
    {
      "role": "CHAIR",
      "status": "OK",
      "response": "{\n  \"schema_version\": 2,\n  \"run_id\": \"d29c35e9-5443-58a8-a015-058fb38ba87d\",\n  \"role\": \"CHAIR\",\n  \"candidates\": [],\n  \"note\": \"Entry not approved: prearbiter signals below threshold and no entry_ok; cannot initiate BUY.\"\n}",
      "error": null
    },
    {
      "role": "LIQUIDITY",
      "status": "OK",
      "response": "{\"schema_version\":2,\"run_id\":\"d29c35e9-5443-58a8-a015-058fb38ba87d\",\"source\":\"code\",\"data_confidence\":\"HIGH\",\"role\":\"LIQUIDITY\",\"symbols\":[{\"symbol\":\"INTC\",\"note\":\"deterministic code assessment\",\"evidence\":[{\"path\":\"symbols.INTC.spread_bps\",\"band\":\"TIGHT\"},{\"path\":\"symbols.INTC.mid_px\",\"band\":\"POSITIVE\"},{\"path\":\"symbols.INTC.volz_tod_15m\",\"band\":\"NORMAL\"}],\"gate\":{\"state\":\"PASS\",\"size_multiplier\":1.0,\"reasons\":[]}}] }",
      "error": null
    },
    {
      "role": "PORTFOLIO",
      "status": "OK",
      "response": "{\"data_confidence\": \"HIGH\", \"role\": \"PORTFOLIO\", \"run_id\": \"d29c35e9-5443-58a8-a015-058fb38ba87d\", \"schema_version\": 2, \"source\": \"code\", \"symbols\": [{\"evidence\": [{\"band\": \"NEG_STRONG\", \"path\": \"symbols.INTC.recent_return_5m\"}, {\"band\": \"NEG_STRONG\", \"path\": \"symbols.INTC.recent_return_10m\"}, {\"band\": \"NEG_STRONG\", \"path\": \"symbols.INTC.ret_15m\"}], \"gate\": {\"reasons\": [], \"size_multiplier\": 1.0, \"state\": \"PASS\"}, \"note\": \"Short window momentum significantly negative\", \"symbol\": \"INTC\"}]}",
      "error": null
    },
    {
      "role": "REGIME",
      "status": "OK",
      "response": "{\"data_confidence\":\"HIGH\",\"risk_appetite\":\"NEUTRAL\",\"role\":\"REGIME\",\"run_id\":\"d29c35e9-5443-58a8-a015-058fb38ba87d\",\"schema_version\":2,\"source\":\"code\",\"symbols\":[{\"symbol\":\"INTC\",\"note\":\"Positive market regime but recent negative returns suggest caution.\",\"evidence\":[{\"path\":\"market.regime_label\",\"band\":\"UPTREND\"},{\"path\":\"market.spy_vol_regime_ratio\",\"band\":\"POSITIVE\"},{\"path\":\"symbols.INTC.ema_gap_bps_15m\",\"band\":\"POS_STRONG\"},{\"path\":\"symbols.INTC.recent_return_5m\",\"band\":\"NEG_STRONG\"}]}]}",
      "error": null
    },
    {
      "role": "TECHNICAL",
      "status": "OK",
      "response": "{\"data_confidence\": \"HIGH\", \"role\": \"TECHNICAL\", \"run_id\": \"d29c35e9-5443-58a8-a015-058fb38ba87d\", \"schema_version\": 2, \"source\": \"code\", \"symbols\": [{\"evidence\": [{\"band\": \"POS_STRONG\", \"path\": \"symbols.INTC.ema_gap_bps_15m\"}, {\"band\": \"FIRM\", \"path\": \"symbols.INTC.rsi14_15m\"}, {\"band\": \"NEG_STRONG\", \"path\": \"symbols.INTC.recent_return_5m\"}, {\"band\": \"NEGATIVE\", \"path\": \"symbols.INTC.ret_15m\"}, {\"band\": \"UNCONFIRMED\", \"path\": \"symbols.INTC.intraday_setup_1m\"}, {\"band\": \"Negative\", \"path\": \"symbols.INTC.macd_hist_15m\"}], \"note\": \"Solid 15m bull structure vs weak 5m pullback; unconfirmed setup.\", \"signal\": {\"confidence\": 0.82, \"horizon\": \"INTRADAY\", \"score\": 0.48, \"state\": \"SIGNAL\"}, \"symbol\": \"INTC\"}]}",
      "error": null
    }
  ],
  "reason_codes": [
    "NO_SIGNAL_ABOVE_THRESHOLD"
  ],
  "notes": [
    "evidence_pack:84ae78edf8a3d15d2344f50a0cecbae2d4419cfe997fb323a4d3f8162bdc866d",
    "council_run:d29c35e9-5443-58a8-a015-058fb38ba87d",
    "NO_SIGNAL_ABOVE_THRESHOLD"
  ],
  "error": null,
  "proposals_and_risk": []
}
```

</details>

### 14:47:05 ET · DECIDED_HOLD

<details>
<summary>Recorded decision evidence</summary>

```json
{
  "decision_id": "a9006978-cfc1-56ab-b176-855dabc1c2a3",
  "inputs": {
    "as_of": "2026-11-23T19:47:02.558339Z",
    "regime": {
      "label": "uptrend"
    },
    "account": {
      "cash": 99803.06,
      "equity": 99803.06,
      "status": "ACTIVE",
      "account_id": "PAPER_ACCOUNT",
      "last_equity": 99803.39,
      "buying_power": 399212.24
    },
    "positions": [],
    "symbols": {
      "INTC": {
        "mid": 58.12,
        "rsi14": null,
        "ret_1d": -0.0783,
        "ret_5d": null,
        "ret_20d": null,
        "atr14_pct": null,
        "price_vs_sma20": null,
        "trend_sma20_vs_sma50": null
      }
    }
  },
  "feature_evidence": {
    "account_ref": "PAPER_ACCOUNT",
    "as_of": "2026-11-23T19:47:02.558339+00:00",
    "availability": {
      "account": "fresh",
      "bars": "fresh",
      "calendar": "fresh",
      "news": "fresh",
      "ok_fraction_core_features": 1.0,
      "quotes": "fresh"
    },
    "bands_hash": "810517c6e124c7ebc23ca0ebce7ef7ba7cc66b30bc21cacc66c1a221174255d4",
    "feasibility": {
      "INTC": {
        "can_buy": true,
        "can_buy_reasons": [],
        "can_sell": false,
        "can_sell_reasons": [
          "NO_SELLABLE_INVENTORY"
        ],
        "entry_window_open": true,
        "entry_window_reason": "",
        "held_qty": "0.0",
        "max_new_notional_usd": "2000.0",
        "sellable_qty": "0"
      }
    },
    "feature_slot": {
      "candles": {
        "INTC|2026-11-23T19:32:00+00:00": "1316263235fefac976cf3179d15a341ca2faba6862bc2ad845a199a21f1a4ea1",
        "INTC|2026-11-23T19:33:00+00:00": "c37f8ccdeccf9064ac8a9b4e6a21d4ed42be7567ab3ba10eb0558b68028107c0",
        "INTC|2026-11-23T19:34:00+00:00": "564e3a869b90c07bc6f4dc36fc9a4642620456c6cac5272aff6455bd272177b1",
        "INTC|2026-11-23T19:35:00+00:00": "8c40460eb8f86125bf2228c6e0b5478931f3e3a91a013bd23caa1bb828639442",
        "INTC|2026-11-23T19:36:00+00:00": "9cb732a5a05f88fcae5944f0121aac8aaa2713bd234d104b87ddb513e8886ae9",
        "INTC|2026-11-23T19:37:00+00:00": "9d5b09f82117334dcc0f33b8c32ad04009545b4670f26997f04929a89d44df93",
        "INTC|2026-11-23T19:38:00+00:00": "e98c98af48936fd32ec6ad72041fcbfa1de8511a2b8911c69eabcd4ab7117e18",
        "INTC|2026-11-23T19:39:00+00:00": "422314eba37616c0546eed1ed8aa018f6b54ce6bec687378c7704d9ca2065248",
        "INTC|2026-11-23T19:40:00+00:00": "70e0d8b0a63b3723514998b8205402a930375f59ca5308b2f48f6dbab08cd617",
        "INTC|2026-11-23T19:41:00+00:00": "4510c4c83faf5f5878d401794d4b7bed12120a3527e7efc68be6e7a94d44c40b",
        "INTC|2026-11-23T19:42:00+00:00": "98067d1cfbe2cf62a97c2f9a655f0cf4470e9f8fb2391eb0463aff7d674dad4b",
        "INTC|2026-11-23T19:43:00+00:00": "c8d1f80659f571bf3eb64a17b9935be4ce7a092a55afd0608b149b1e717e9011",
        "INTC|2026-11-23T19:44:00+00:00": "c1aa4b559490e25f881fb40af919d8644954d00315de5f007556c6e7791a0b28",
        "INTC|2026-11-23T19:45:00+00:00": "34a1b438e39db05694f921c5baec9ae6582c0220846c45eb8506fabad543f270",
        "INTC|2026-11-23T19:46:00+00:00": "805d43a04e130aa788c4098fa1275ef209d434dbdf234b2dbc11f9444444a83b",
        "SPY|2026-11-23T19:32:00+00:00": "13017eef20c793ba8a0c3bee58ceb303a749f3ed6db515430dbcd3f066266ef6",
        "SPY|2026-11-23T19:33:00+00:00": "60acf2b6b72dfb53f598542c183985e00d5820e45e6a15aaa702caa2e7db45df",
        "SPY|2026-11-23T19:34:00+00:00": "205774036f40cb4bc8e44df4d46ef150bd7d25dedeb8a897455bddc1dd4763d8",
        "SPY|2026-11-23T19:35:00+00:00": "a3f33f928527ca6cd947868e44e270cfe45857f8acf9296afd6811bf7c66a716",
        "SPY|2026-11-23T19:36:00+00:00": "20f2610f9083c52c53c44110cf31c15486c3658b74baf10c77427c7f1643e451",
        "SPY|2026-11-23T19:37:00+00:00": "cfc075a20afd9004c6a54e55e02de60aa1ac6fab559ca2bc363b4083a5a7b0e8",
        "SPY|2026-11-23T19:38:00+00:00": "8ac7b4d0dc16f15a1b48e3576c48557a2cf3e5e01e9dbd56ec12e4206987e786",
        "SPY|2026-11-23T19:39:00+00:00": "38712a0709a4972b95a52f42b45fd54896d71cc49ce48651c65445f1a42bf62f",
        "SPY|2026-11-23T19:40:00+00:00": "e49f4baca7c7583df76c009735c11448f1023f1415b68e390409997276db3480",
        "SPY|2026-11-23T19:41:00+00:00": "0dccbf44a642c7d605f69cb3858d90923162c6c2b93f66b9555d77776438a183",
        "SPY|2026-11-23T19:42:00+00:00": "88269dcad14d8b8d3584bb870bfc6f5eed07f56a971f9ad7e1037bfff28a3780",
        "SPY|2026-11-23T19:43:00+00:00": "a4aebaa6965c7c246c1610c4eff9a05d061eff2cadc3940774ca5ab43368ca06",
        "SPY|2026-11-23T19:44:00+00:00": "b91459d6c5ec4fb98cb4404bbe1cd7357fe920ab60a2e98579d2b6fb1626730d",
        "SPY|2026-11-23T19:45:00+00:00": "467c27fb5d5f1da7405a638366403833df31cfdd7aae5abf3fe2d4bf9f1de532",
        "SPY|2026-11-23T19:46:00+00:00": "a7668e87604b88bc72c1eadf5d9870964634f7b5e5b13baa18713dfa791d317c"
      },
      "close": "2026-11-23T19:47:00+00:00",
      "feed": "iex",
      "indicator_close": "2026-11-23T19:45:00+00:00",
      "indicator_input_hashes": {
        "INTC": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
        "SPY": "68be2784fe1097306ec89b5433c1c0b0393b316ceebc03170624a4214da8ac5c"
      },
      "provisional": true,
      "records": {
        "market:market:breadth_above_ema21": "d7e2f70fedf1d18806a57fa4210d951ce450efccdd03a1fa716baff26d0f59e9",
        "market:market:regime_label": "b5f7eda754fe89980a8ade83e3496e26768374e4bbb5fca559b77ed06e580f14",
        "market:market:spy_ema_gap_bps_15m": "5885f7d1170e4539d33b130275da00b6751841c47609429095ed1e27403a7ec2",
        "market:market:spy_ret_60m": "dbd7238ab1fb9e37e2e258595363670d154e785916243d17695f64fbee0b0406",
        "market:market:spy_vol_regime_ratio": "dbabb67a6a3354b77c0aa095af0b6d8b30354d9a7da22aa38f106697e426d22b",
        "symbol:INTC:adv_usd_20d": "b9b2c8cd47063244741a0be3a99b852571258b975af9e1831bf9c22ac86c817d",
        "symbol:INTC:atr14_15m": "6f731751bfa53150c4b34c9f00c97b6e20fc9879a19350f0ce7cbe19a7070a61",
        "symbol:INTC:atr14_1d": "7109941c8f13c27be9954427260fd23488765da0017ae6e7268c52c67c282e0d",
        "symbol:INTC:atr14_pct": "72b22515a9b698de8e221ba3601ca48bfe5aa847f96eb780cd201d7da6e1b10b",
        "symbol:INTC:dist_hi_atr": "d2df8b5a74839767cdb4d5d8d5395e90f52645fb56ffa4cfc756e62876d61127",
        "symbol:INTC:dist_lo_atr": "d4c26f72bbbe96465b9ea553494c4f757689b7043fa0310ea224caa95dc37302",
        "symbol:INTC:ema21_15m": "026dc43aa182328e915e6f6d23296bedca2f3d61e29ad492593fd2b16c1f2c9c",
        "symbol:INTC:ema9_15m": "779c29eadfec6fe54e83478754f967d3444f194d88d34349bf014707a7b14100",
        "symbol:INTC:ema_gap_bps_15m": "2d80bf72eea509fb31fba6a2c3b863d8d8dc686f8d007db33fe90cf4a50e5145",
        "symbol:INTC:gap_open_pct": "22372f1618bb0042d504687f06dc178f5d5531095633eddeaf4bcfe97a2ded36",
        "symbol:INTC:intraday_ret_1h": "584b190315139eaa5cf532afd4584686eee1ec8a960635264ed6e8e8c24aeec5",
        "symbol:INTC:intraday_setup_1m": "5911632dc1dffd46a57ca927b8a52024ce3bb45393c5279bb0702ae149d3d741",
        "symbol:INTC:last_close": "d19401a83eca33beec8f4dc4c9fd9de4a732eca37d9f9287a4931e7ba85850f1",
        "symbol:INTC:macd_hist_15m": "ffc4ec65b3c48fbd631f09dccfb6d59e271d94c9ffd76307010798940056e67d",
        "symbol:INTC:price_vs_sma20": "0d79ec3c1b357a5011464af77c39b3fcad072140f1af42e8fc4caaaa2d603acd",
        "symbol:INTC:recent_price_10m": "f1315aa0709711109795a23719c6283b66c28656664ca15c1b3968832dce9254",
        "symbol:INTC:recent_range_bps_10m": "28593da1da75535811d3e1cb2b9c120aeab3589a21428b77499630f5b171b9c0",
        "symbol:INTC:recent_range_bps_5m": "874d40aecb4f702f25170ac0d9c9c636f8abb24094fadef303631cbe7cc0d3cd",
        "symbol:INTC:recent_return_10m": "14513e0ee00dc96c41e0b2103400fe19e45cb74cd2587d27626c1dc059f2f065",
        "symbol:INTC:recent_return_5m": "1dbaceb451248b251edfafe0224bdc98e1d053bd94c345af93070ab78df55c2e",
        "symbol:INTC:recent_volume_10m": "2258e0c3f77d748017076090e669c2c98dea1fe473e9d2aee31096e81b5bc3b5",
        "symbol:INTC:recent_volume_5m": "3da4a053ead5891c3e710a98507b3e4e570efdfa823e0c2b39d210531dc3d2ce",
        "symbol:INTC:relstr_spy_60m": "4a2efcccfad641379da325f71ec41a86cd514996d16cf454e59b74429a421867",
        "symbol:INTC:ret_15m": "d0b4343de4ebc557cdec7d62eae13fd8c19b62412d784631613f827f8aedf5d6",
        "symbol:INTC:ret_1d": "4871f8f39f073d45e17d3d6f5ca60a8fec098c3c382779b9f1d17c4eff156f1b",
        "symbol:INTC:ret_20d": "c89eca0e545e370a2b5106418f52c2c97be259b8d9a271ffd1a96adbaa2aca0a",
        "symbol:INTC:ret_5d": "05a741e625955a85a438ad18773375028848616408999e7af63ece7accaed8b3",
        "symbol:INTC:ret_5m": "8889142c7c313630f5e598ae80cfca38f47a66c447adf77b879dd21fe2f85bfd",
        "symbol:INTC:ret_60m": "41e9a5dd135419e6554eb609bc32d0fc113d9db6ba4565df82b96ff5e7505d87",
        "symbol:INTC:rsi14": "1e59b41cf19356a8afb2c1abc8da30ba54a3ae1c9ca6adec3645d67baab39a97",
        "symbol:INTC:rsi14_15m": "8e2405b48f61208fcc98491d12fb4cfef18c440cec8f1c795d9799094ef01d8d",
        "symbol:INTC:rvol_60m": "3b5ba374c708f1a0cb9ecac010ad1aa442f0b1d3db0c25896c7a2017feddd64a",
        "symbol:INTC:sma20": "15576f86a2842f5eb53a8c69129bc796ec2bb02d553d6eb692a0246444b821e2",
        "symbol:INTC:sma50": "c77619dbf2bb36c37659503666953bdfa289b5ad53f8419d72ac47d490aa3455",
        "symbol:INTC:trend_sma20_vs_sma50": "c3f4c96640a0fefa86efead1a20dc2a8c20470887509f9a64b8b123a7f0f6feb",
        "symbol:INTC:vol_regime_ratio": "362afe727800b5cd2883231bd64de49ee5d1e0efe009d0aa7bcf0c02cddd7deb",
        "symbol:INTC:volume_z20": "acd6606915e0844ee2fa5f30507b576df69022855968e20bad1ec489ca7b84b7",
        "symbol:INTC:volz_tod_15m": "00402ad410208e76d63fb60dc603ca6c5c3933ab4023869011a7814ed1722a9c",
        "symbol:INTC:vwap_dev_session": "495e37002161bf0329faf8c138f95614813f255e17d85d4c05aed2203e21ed59",
        "symbol:SPY:adv_usd_20d": "92e94f829df49f4b3a8d0be7612b000e92190d5356f55e566f04069ca7b9ffd5",
        "symbol:SPY:atr14_15m": "7ab448ef9d85396282151eac59236f9553a486b5c77591049f30866a0df20c74",
        "symbol:SPY:atr14_1d": "3cac187afe8b3f12d7d3b3b86986d403d549ebe59a7ccfaa10a213aaea0d6f29",
        "symbol:SPY:atr14_pct": "86a49f6a2b7c51bced8c4109a9b641fd3430da5d9872f600c092cec75526d214",
        "symbol:SPY:dist_hi_atr": "ef0b1ce91b1e730695d8acb7667b8d28162ea27c6e806fc5ffb62b5c2e07c4d7",
        "symbol:SPY:dist_lo_atr": "aae977dd0ae542f012955ced86bded9587fd5eb6d92199218a01a854fd1f6578",
        "symbol:SPY:ema21_15m": "e101df90a64d088f78547e381107b8db83b2541409047168500bf08d4caa4b43",
        "symbol:SPY:ema9_15m": "d9a6929dcd2aa029a0657e3b23036ea5c8e549c3e28f704d22c59d9141f45d16",
        "symbol:SPY:ema_gap_bps_15m": "12f402c62d8c646eb7b75bb92bec226e49110827a04064a50b8a1e5b881fc789",
        "symbol:SPY:gap_open_pct": "1c9616a65f2f013255300b42e56d88ac7a725e105e6f59b39d79e458ad29184e",
        "symbol:SPY:intraday_ret_1h": "4a3cbce2b9dcc1b99d6875d1dfcc341ba613acfd2d05e42ab8e2dd8730e5c8b3",
        "symbol:SPY:intraday_setup_1m": "632a5fd8b209f4b5840f4fd86396e406bdfb502ceab3c9935126675294b261ed",
        "symbol:SPY:last_close": "caf596deca80d26016ad4208908f5e9f946155af82bcf05ef2276748182b2361",
        "symbol:SPY:macd_hist_15m": "7c1f84aa5b3c914a24e8512883539348c328fedf77f1ca8fddef3c9428311b8a",
        "symbol:SPY:price_vs_sma20": "963d8268f25c4849a1b268733b11edd2005fe4a8c767d1439d8478255d5a22c9",
        "symbol:SPY:recent_price_10m": "9f016c22d0ee69ec160c95ee53465ed77c72b0c7ac48280a41b9b3d40ea17d25",
        "symbol:SPY:recent_range_bps_10m": "ece0c2c47992c04e365cd1b8adbf8d5b6b68c47baf3cafa239db8fb4165821f8",
        "symbol:SPY:recent_range_bps_5m": "0618c99324f0be233bb7e81f1fd9976b64a99e95bed042f0309a6cd9f12b165a",
        "symbol:SPY:recent_return_10m": "c12109e4a474000de9486864b8adc87d4349b6a10a1aa5b634b49afd37910beb",
        "symbol:SPY:recent_return_5m": "dd6dd4bbc6ce9f28d00e5c06429cdef77c0456f45e2ee055c25277bbdb57a633",
        "symbol:SPY:recent_volume_10m": "f7bf3a5a0cdf7fe8d4d1d6014ac0631009cfada00651e38d46ebc853fd8746db",
        "symbol:SPY:recent_volume_5m": "f483504ead54ff2a545f1e8bb70b90eb0fc89218dd4e192cb837c7fb5ef75c64",
        "symbol:SPY:relstr_spy_60m": "8192ee3c1e096d3220e21bd96547302036aad20b1f8b2a88d06eb43fca3d16bd",
        "symbol:SPY:ret_15m": "9904a4ed1f297bf78ff189d77b4adbca5fb709726061b78733ef22a5f0881a03",
        "symbol:SPY:ret_1d": "aab94a7dafcf360313d949fc12ced963ccb5a8b3ef27866b2b930d2d5817c533",
        "symbol:SPY:ret_20d": "5cb42b7c179c74bdcedf0dbf4ce0ee12832341fe24b75d306dccc8cc03e792c3",
        "symbol:SPY:ret_5d": "7c31dada2f0a36e24d03e89b66cb73d377f3c298c10867a1be2b05be76be6a0c",
        "symbol:SPY:ret_5m": "cf9c4988bd242b1bdf50490710597940a27e9fcdb4339238fe6fb363b02f46fc",
        "symbol:SPY:ret_60m": "a7a8bb9483d720b4b710c07229e834b735942cd823d46f3a03a427989ddbbd31",
        "symbol:SPY:rsi14": "ee11c2b462281f9fc927ac380b6bb2557ff2e158729fe2f17aa91d152eb3fb9f",
        "symbol:SPY:rsi14_15m": "7a2d8a98c627154aeccdc9a68b885c12330bcb82ce58cddb4d0a2f4136033fc0",
        "symbol:SPY:rvol_60m": "847ff547d78aa75be9fd564e8d62716ab3925e8a16ce1ff0b517b05f1cf39910",
        "symbol:SPY:sma20": "1b30496ca2845ccd7a79462c221d840260e1c0361b7feb9dedbc5dc30bd4b2a5",
        "symbol:SPY:sma50": "94c11d37cff9b64498753612d4be2b84f39d1931bd55ec9e573a0c8697ceb72b",
        "symbol:SPY:trend_sma20_vs_sma50": "8aee1d285ca5a8e44083c58d0fad60754235fda2855c6ac02c9796bc41cff8bc",
        "symbol:SPY:vol_regime_ratio": "34a41bfa2ab39a6748b87f0625e751a047b8c31723512c872c16e7823be7d45d",
        "symbol:SPY:volume_z20": "26f74a49cf931c478f404ef3e6a0850c2e214cc588216f87e068535e16f86e9f",
        "symbol:SPY:volz_tod_15m": "29640670f4a0587e4e43a5ad4cd8d40a485c1b2537f64212b1cb41ffc2d19792",
        "symbol:SPY:vwap_dev_session": "aa3499d71ae73181e39cdee58fd182c75cdcff24e571cf4dd8268ead48d1eaf3"
      },
      "symbols": [
        "INTC",
        "SPY"
      ]
    },
    "horizons": {
      "INTC": {
        "10m": {
          "age_s": 2.558339,
          "last_bar_end": "2026-11-23T19:47:00+00:00",
          "status": "OK"
        },
        "15m": {
          "age_s": 122.558339,
          "last_bar_end": "2026-11-23T19:45:00+00:00",
          "status": "OK"
        },
        "5m": {
          "age_s": 2.558339,
          "last_bar_end": "2026-11-23T19:47:00+00:00",
          "status": "OK"
        },
        "60m": {
          "age_s": 122.558339,
          "last_bar_end": "2026-11-23T19:45:00+00:00",
          "status": "OK"
        },
        "horizon_conflict": false
      }
    },
    "market": {
      "breadth_above_ema21": {
        "age_s": 122.558339,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "d7e2f70fedf1d18806a57fa4210d951ce450efccdd03a1fa716baff26d0f59e9",
        "status": "OK",
        "v": 1.0,
        "version": "1.1dfe664d"
      },
      "minutes_to_close": {
        "age_s": 0.485236,
        "quality": {},
        "record_hash": "26d87d08d363c5e7ead6568cd4e9b583d8d63d6678cca9b7d1a5fd05e85e3569",
        "status": "OK",
        "v": 72.96544828,
        "version": "1.e79b1ead"
      },
      "regime_label": {
        "age_s": 122.558339,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "b5f7eda754fe89980a8ade83e3496e26768374e4bbb5fca559b77ed06e580f14",
        "status": "OK",
        "v": "UPTREND",
        "version": "1.f8b361d7"
      },
      "session_phase": {
        "age_s": 0.485236,
        "quality": {},
        "record_hash": "a511b37d7cff1bb4d83ba7cb6488babbaa3a27c48e26be2719d5951424b5b381",
        "status": "OK",
        "v": "NORMAL",
        "version": "1.91f88fe8"
      },
      "spy_ema_gap_bps_15m": {
        "age_s": 122.558339,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "5885f7d1170e4539d33b130275da00b6751841c47609429095ed1e27403a7ec2",
        "status": "OK",
        "v": 37.89644347,
        "version": "1.fda7da7a"
      },
      "spy_ret_60m": {
        "age_s": 122.558339,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "dbd7238ab1fb9e37e2e258595363670d154e785916243d17695f64fbee0b0406",
        "status": "OK",
        "v": -0.0007895939825,
        "version": "1.9feddbd1"
      },
      "spy_vol_regime_ratio": {
        "age_s": 122.558339,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "dbabb67a6a3354b77c0aa095af0b6d8b30354d9a7da22aa38f106697e426d22b",
        "status": "OK",
        "v": 1.40409109,
        "version": "1.3b7257aa"
      }
    },
    "meta": {
      "news": {
        "INTC": {
          "effective_weight": 0,
          "in_window": 0,
          "newest_age_min": 1785.592639,
          "policy": "48h retained; per-article decay and minimum relevance; 4h count is descriptive",
          "poller_last_ok_age_s": 9.750855,
          "retrieved": 1,
          "selected": 0,
          "state": "QUIET",
          "window_min": 240
        }
      }
    },
    "news_blob_hash": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
    "news_context_blob_hash": "ef023692226f6319baf7f6429f023deb1a988f59c953b103e7a5f425a6a5d062",
    "portfolio": {
      "aggregate_cap_usd": {
        "age_s": 0.485236,
        "quality": {},
        "record_hash": "55bfb2dfb1e45917882e26e6878ce7b83042c27b4b3f8dcceebc7eaf1844aa20",
        "status": "OK",
        "v": "49901.530",
        "version": "1.5b3d1daf"
      },
      "aggregate_headroom_usd": {
        "age_s": 0.485236,
        "quality": {},
        "record_hash": "9fe789b90aa52ca119fb8056795b7e8238ccb95fbb0f58feaa6ce14cab4af31b",
        "status": "OK",
        "v": "49901.530",
        "version": "1.7f894fff"
      },
      "buying_power": {
        "age_s": 0.485236,
        "quality": {},
        "record_hash": "dd6dfe9aff7031ffae3ff06b7317cf52e5c6331d36880c26fdd82f1411d6e447",
        "status": "OK",
        "v": "399212.24",
        "version": "1.74948dec"
      },
      "cash": {
        "age_s": 0.485236,
        "quality": {},
        "record_hash": "9be31f3312b7896a3d3d7594e28fb45d48e998a6d6b6af061b8a1a092bb277a3",
        "status": "OK",
        "v": "99803.06",
        "version": "1.b067f5e3"
      },
      "day_pnl_pct": {
        "age_s": 0.485236,
        "quality": {},
        "record_hash": "1d51ca9bebd526a6bc4c8de7208b216d34c8a6358e1781250af0c6ccdf069fe7",
        "status": "OK",
        "v": "-0.0003306500911441986088849300",
        "version": "1.35e81852"
      },
      "drawdown_pct": {
        "age_s": 0.485236,
        "quality": {},
        "record_hash": "d6e1b6812bd3343039b6306acf8bf20cc952e656cede2898506d30a15da7037c",
        "status": "MISSING",
        "v": null,
        "version": "1.19aac9ba"
      },
      "equity": {
        "age_s": 0.485236,
        "quality": {},
        "record_hash": "c0d67495e09e41d43028f61cc72e55a471e7b5cd801fa67b5be319b9a8683151",
        "status": "OK",
        "v": "99803.06",
        "version": "1.a2192616"
      },
      "gross_exposure_pct": {
        "age_s": 0.485236,
        "quality": {},
        "record_hash": "bf1050c5f3743e2be1af55b77c4cb45ad6ba343ceffde30461e1991eeab206a9",
        "status": "OK",
        "v": "0E+2",
        "version": "1.b82cc518"
      },
      "gross_exposure_usd": {
        "age_s": 0.485236,
        "quality": {},
        "record_hash": "c1938406ca2856e03481a1205d1c6d6fc6cf005bcac73f9d1cc47db3c74bf470",
        "status": "OK",
        "v": "0",
        "version": "1.e4c8752b"
      },
      "last_reconcile_age_s": {
        "age_s": 0.485236,
        "quality": {},
        "record_hash": "850c6f7197313d245f4a39cdf8f9b8d72e86b15024dac98da25a6909129d2104",
        "status": "OK",
        "v": 0,
        "version": "1.5ed0382f"
      },
      "open_buy_notional_usd": {
        "age_s": 0.485236,
        "quality": {},
        "record_hash": "40cef88938870f146cb76c92c74ccd24d6db4361706d4e14ebb0e7ada3ac5d9a",
        "status": "OK",
        "v": "0",
        "version": "1.0bd0ead1"
      },
      "open_orders": {
        "age_s": 0.485236,
        "quality": {},
        "record_hash": "881c6f17dc5659a5b0fc307414b56011990c8cd6937ea7843c1772fa31aeda5a",
        "status": "OK",
        "v": [],
        "version": "1.1cf37cbf"
      },
      "open_orders_count": {
        "age_s": 0.485236,
        "quality": {},
        "record_hash": "8ede906036bd72f7002fa749b20033d51be620fc1f37471cf06399dc621d00ab",
        "status": "OK",
        "v": 0,
        "version": "1.1db4227a"
      },
      "pending_reserved_usd": {
        "age_s": 0.485236,
        "quality": {},
        "record_hash": "31e9c00ad14fabe5339e975094cc0ba61861bf12449769774bed90bbfd60cef1",
        "status": "OK",
        "v": "0",
        "version": "1.1c3e9604"
      },
      "positions": {
        "age_s": 0.485236,
        "quality": {},
        "record_hash": "59a32759c3e7b705285fdfb68545abbd47f118e5ab1fb8a7f97fa385cbda5257",
        "status": "OK",
        "v": [],
        "version": "1.c3284657"
      }
    },
    "registry_hash": "0fd3271269748046863b2f0558e45e2c333bb352eccc9899b7ff42277c8386fc",
    "schema_version": 1,
    "symbols": {
      "INTC": {
        "adv_usd_20d": {
          "age_s": 254822.5583,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "b9b2c8cd47063244741a0be3a99b852571258b975af9e1831bf9c22ac86c817d",
          "status": "OK",
          "v": 304793568.9,
          "version": "1.04f5e91f"
        },
        "ask_px": {
          "age_s": 1.400542,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "b5fcb7520670e95ff51081ed73ef192368010e4f76f1432c5cc313bd561a4ae4",
          "status": "OK",
          "v": 58.13,
          "version": "1.d21cdd09"
        },
        "atr14_15m": {
          "age_s": 122.558339,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "6f731751bfa53150c4b34c9f00c97b6e20fc9879a19350f0ce7cbe19a7070a61",
          "status": "OK",
          "v": 0.7629598219,
          "version": "1.0cd14e73"
        },
        "atr14_1d": {
          "age_s": 254822.5583,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "7109941c8f13c27be9954427260fd23488765da0017ae6e7268c52c67c282e0d",
          "status": "MISSING",
          "v": null,
          "version": "1.65e38f4c"
        },
        "atr14_pct": {
          "age_s": 254822.5583,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "72b22515a9b698de8e221ba3601ca48bfe5aa847f96eb780cd201d7da6e1b10b",
          "status": "MISSING",
          "v": null,
          "version": "1.87450ee9"
        },
        "bid_px": {
          "age_s": 1.400542,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "8969fec4788af356f1a1295fa0a313113ce426810553a348765e2791e34491ea",
          "status": "OK",
          "v": 58.11,
          "version": "1.149628cd"
        },
        "dist_hi_atr": {
          "age_s": 122.558339,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "d2df8b5a74839767cdb4d5d8d5395e90f52645fb56ffa4cfc756e62876d61127",
          "status": "OK",
          "v": -1.815298736,
          "version": "1.913ffc4a"
        },
        "dist_lo_atr": {
          "age_s": 122.558339,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "d4c26f72bbbe96465b9ea553494c4f757689b7043fa0310ea224caa95dc37302",
          "status": "OK",
          "v": 1.900493261,
          "version": "1.79ba4c70"
        },
        "ema21_15m": {
          "age_s": 122.558339,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "026dc43aa182328e915e6f6d23296bedca2f3d61e29ad492593fd2b16c1f2c9c",
          "status": "OK",
          "v": 57.40577599,
          "version": "1.bfcac61e"
        },
        "ema9_15m": {
          "age_s": 122.558339,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "779c29eadfec6fe54e83478754f967d3444f194d88d34349bf014707a7b14100",
          "status": "OK",
          "v": 58.09168398,
          "version": "1.81255de8"
        },
        "ema_gap_bps_15m": {
          "age_s": 122.558339,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "2d80bf72eea509fb31fba6a2c3b863d8d8dc686f8d007db33fe90cf4a50e5145",
          "status": "OK",
          "v": 119.4841427,
          "version": "1.d4519f3c"
        },
        "gap_open_pct": {
          "age_s": 122.558339,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "22372f1618bb0042d504687f06dc178f5d5531095633eddeaf4bcfe97a2ded36",
          "status": "MISSING",
          "v": null,
          "version": "1.27438d4d"
        },
        "halted": {
          "age_s": 0.485236,
          "quality": {},
          "record_hash": "42dc8b4f38f4c9860caad02a9f9315b506afa9dbe7922ac48d9594dd2e67b042",
          "status": "OK",
          "v": false,
          "version": "1.22c5cf87"
        },
        "held_minutes": {
          "age_s": 0.485236,
          "quality": {},
          "record_hash": "18540be50d281cf2b0e55eddfb19282e498c2ca813b9fb8418644f2af4cb05fb",
          "status": "MISSING",
          "v": null,
          "version": "1.de6ed6d3"
        },
        "intraday_ret_1h": {
          "age_s": 122.558339,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "584b190315139eaa5cf532afd4584686eee1ec8a960635264ed6e8e8c24aeec5",
          "status": "OK",
          "v": 0.001120786275,
          "version": "1.c3bb7751"
        },
        "intraday_setup_1m": {
          "age_s": 2.558339,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "6e0b9a1039c8f178ee6f3fb15abbb8b801ce9a74664dc0e826b8eac666a6fc46",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:47:00+00:00",
            "window_start": "2026-11-23T19:37:00+00:00"
          },
          "record_hash": "5911632dc1dffd46a57ca927b8a52024ce3bb45393c5279bb0702ae149d3d741",
          "status": "OK",
          "v": {
            "confirmation": "NONE",
            "pattern": "NONE",
            "prior_trend": "FLAT",
            "range_break": "INSIDE",
            "range_ceiling": 58.21,
            "range_floor": 58.01,
            "setup_minute": null,
            "volume_ratio": 1.177
          },
          "version": "1.2a1f51e0"
        },
        "last_close": {
          "age_s": 254822.5583,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "d19401a83eca33beec8f4dc4c9fd9de4a732eca37d9f9287a4931e7ba85850f1",
          "status": "MISSING",
          "v": null,
          "version": "1.f2485fc2"
        },
        "luld_active": {
          "age_s": 0.485236,
          "quality": {},
          "record_hash": "22a698d7d274c3556693c4d288eb729403ee011fada34b515cdba9be6e4f98d9",
          "status": "MISSING",
          "v": null,
          "version": "1.84a715b2"
        },
        "macd_hist_15m": {
          "age_s": 122.558339,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "ffc4ec65b3c48fbd631f09dccfb6d59e271d94c9ffd76307010798940056e67d",
          "status": "OK",
          "v": -0.07751173219,
          "version": "1.391617c8"
        },
        "mid_px": {
          "age_s": 1.400542,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "ff12c9a0203d2018b950f0d7894184f53f5a205a8944739ff807c0d8526b4567",
          "status": "OK",
          "v": 58.12,
          "version": "1.d567a349"
        },
        "news_age_min_latest": {
          "age_s": 9.750855,
          "quality": {},
          "record_hash": "fb9b4f87ca34664449632966f5f9af33a6b08fcbeea86e38ece906be3b57e62a",
          "status": "MISSING",
          "v": null,
          "version": "1.d0f79dc8"
        },
        "news_confirmed": {
          "age_s": 0,
          "quality": {
            "source": "stored news and pinned price features"
          },
          "status": "OK",
          "v": false,
          "version": "news-confirmation-v2"
        },
        "news_count_1h": {
          "age_s": 9.750855,
          "quality": {},
          "record_hash": "4c13ac922fb9dbcabc3d05c8f2e992f284a438b7e59d152db2efcab58fcd60f4",
          "status": "OK",
          "v": 0,
          "version": "1.0c9362fe"
        },
        "news_count_48h": {
          "age_s": 9.750855,
          "quality": {
            "as_of": "2026-11-23T19:47:02.558339+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 1,
          "version": "news-context-v2"
        },
        "news_count_4h": {
          "age_s": 9.750855,
          "quality": {
            "as_of": "2026-11-23T19:47:02.558339+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 0,
          "version": "news-context-v2"
        },
        "news_effective_sentiment": {
          "age_s": 0,
          "quality": {
            "selected": 0,
            "source": "decayed stored article metadata"
          },
          "status": "MISSING",
          "v": 0.0,
          "version": "news-decay-v2"
        },
        "news_event_flags_4h": {
          "age_s": 9.750855,
          "quality": {},
          "record_hash": "6ff30c4a85baaebf59bb6272248629a360fad49ba7a9125815841e280fb5b9b4",
          "status": "OK",
          "v": [],
          "version": "1.0b5a8a44"
        },
        "news_max_materiality_4h": {
          "age_s": 9.750855,
          "quality": {},
          "record_hash": "30083743881713fe8d9ca4517b3226b2f0d5459237b343b799cec70c93fc06c3",
          "status": "OK",
          "v": 0,
          "version": "1.9c45e9b4"
        },
        "news_newest_age_min": {
          "age_s": 9.750855,
          "quality": {
            "as_of": "2026-11-23T19:47:02.558339+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 1785.592639,
          "version": "news-context-v2"
        },
        "news_novelty_max_4h": {
          "age_s": 9.750855,
          "quality": {},
          "record_hash": "7b862ca90ff2e5d92cdb53090bce8b8140b95e765db03de62c6d1684385a29b8",
          "status": "OK",
          "v": false,
          "version": "1.15ceb7bf"
        },
        "news_sent_ewm_240m": {
          "age_s": 9.750855,
          "quality": {},
          "record_hash": "fc06efd33138e83ab1c89b86981446bda35b18a5450509f529822e3a09d09a63",
          "status": "OK",
          "v": 0,
          "version": "1.9cad993f"
        },
        "news_sent_ewm_60m": {
          "age_s": 9.750855,
          "quality": {},
          "record_hash": "01e2bf2a9551b82762e5818cfac8b71b7a1b5e75c532528f0899d9fc10eaeaf1",
          "status": "OK",
          "v": 0,
          "version": "1.74ab70c1"
        },
        "news_source_div_4h": {
          "age_s": 9.750855,
          "quality": {},
          "record_hash": "1d4bf2a3463aefa013100e0b7d249eca6929b840f4d09b49ff9505d22e983a3f",
          "status": "OK",
          "v": 0,
          "version": "1.6fd469c4"
        },
        "position_qty": {
          "age_s": 0.485236,
          "quality": {},
          "record_hash": "0eae40117602e0cd0026f2420c389d8d58653e8d94918b3587c931e994e111a3",
          "status": "OK",
          "v": "0",
          "version": "1.3a512120"
        },
        "position_value_usd": {
          "age_s": 0.485236,
          "quality": {},
          "record_hash": "b043bd2a364c57493db7b50d1dd4f412a4382b3390c1930cdeb9e2351321347f",
          "status": "OK",
          "v": "0",
          "version": "1.9100bec4"
        },
        "price_vs_sma20": {
          "age_s": 254822.5583,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "0d79ec3c1b357a5011464af77c39b3fcad072140f1af42e8fc4caaaa2d603acd",
          "status": "MISSING",
          "v": null,
          "version": "1.a986b9cc"
        },
        "recent_price_10m": {
          "age_s": 2.558339,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "6e0b9a1039c8f178ee6f3fb15abbb8b801ce9a74664dc0e826b8eac666a6fc46",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:47:00+00:00",
            "window_start": "2026-11-23T19:37:00+00:00"
          },
          "record_hash": "f1315aa0709711109795a23719c6283b66c28656664ca15c1b3968832dce9254",
          "status": "OK",
          "v": {
            "candles": [
              [
                0,
                58.16,
                58.175,
                58.05,
                58.08,
                12906.0,
                "VERIFIED_BAR"
              ],
              [
                1,
                58.085,
                58.13,
                58.045,
                58.045,
                3139.0,
                "VERIFIED_BAR"
              ],
              [
                2,
                58.045,
                58.165,
                58.045,
                58.095,
                12394.0,
                "VERIFIED_BAR"
              ],
              [
                3,
                58.095,
                58.19,
                58.045,
                58.185,
                11202.0,
                "VERIFIED_BAR"
              ],
              [
                4,
                58.21,
                58.21,
                58.065,
                58.07,
                11493.0,
                "VERIFIED_BAR"
              ],
              [
                5,
                58.07,
                58.095,
                58.01,
                58.01,
                9725.0,
                "VERIFIED_BAR"
              ],
              [
                6,
                58.03,
                58.09,
                58.03,
                58.03,
                7536.0,
                "VERIFIED_BAR"
              ],
              [
                7,
                58.06,
                58.075,
                58.03,
                58.06,
                5274.0,
                "VERIFIED_BAR"
              ],
              [
                8,
                58.07,
                58.11,
                58.03,
                58.03,
                10942.0,
                "VERIFIED_BAR"
              ],
              [
                9,
                58.01,
                58.14,
                57.99,
                58.13,
                12879.0,
                "VERIFIED_BAR"
              ]
            ],
            "columns": [
              "minute_offset",
              "open",
              "high",
              "low",
              "close",
              "volume",
              "coverage"
            ],
            "feed": "iex",
            "window_end": "2026-11-23T19:47:00+00:00",
            "window_start": "2026-11-23T19:37:00+00:00",
            "windows": {
              "10m": {
                "close": 58.13,
                "open": 58.16,
                "range_bps": 37.82668501,
                "return": -0.0005158184319,
                "status": "OK",
                "volume": 97490.0
              },
              "5m": {
                "close": 58.13,
                "open": 58.07,
                "range_bps": 25.83089375,
                "return": 0.00103323575,
                "status": "OK",
                "volume": 46356.0
              }
            }
          },
          "version": "1.b12384d7"
        },
        "recent_range_bps_10m": {
          "age_s": 2.558339,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "6e0b9a1039c8f178ee6f3fb15abbb8b801ce9a74664dc0e826b8eac666a6fc46",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:47:00+00:00",
            "window_start": "2026-11-23T19:37:00+00:00"
          },
          "record_hash": "28593da1da75535811d3e1cb2b9c120aeab3589a21428b77499630f5b171b9c0",
          "status": "OK",
          "v": 37.82668501,
          "version": "1.b7dd2e6e"
        },
        "recent_range_bps_5m": {
          "age_s": 2.558339,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "6e0b9a1039c8f178ee6f3fb15abbb8b801ce9a74664dc0e826b8eac666a6fc46",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:47:00+00:00",
            "window_start": "2026-11-23T19:37:00+00:00"
          },
          "record_hash": "874d40aecb4f702f25170ac0d9c9c636f8abb24094fadef303631cbe7cc0d3cd",
          "status": "OK",
          "v": 25.83089375,
          "version": "1.860a2856"
        },
        "recent_return_10m": {
          "age_s": 2.558339,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "6e0b9a1039c8f178ee6f3fb15abbb8b801ce9a74664dc0e826b8eac666a6fc46",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:47:00+00:00",
            "window_start": "2026-11-23T19:37:00+00:00"
          },
          "record_hash": "14513e0ee00dc96c41e0b2103400fe19e45cb74cd2587d27626c1dc059f2f065",
          "status": "OK",
          "v": -0.0005158184319,
          "version": "1.03c04840"
        },
        "recent_return_5m": {
          "age_s": 2.558339,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "6e0b9a1039c8f178ee6f3fb15abbb8b801ce9a74664dc0e826b8eac666a6fc46",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:47:00+00:00",
            "window_start": "2026-11-23T19:37:00+00:00"
          },
          "record_hash": "1dbaceb451248b251edfafe0224bdc98e1d053bd94c345af93070ab78df55c2e",
          "status": "OK",
          "v": 0.00103323575,
          "version": "1.a9090b46"
        },
        "recent_volume_10m": {
          "age_s": 2.558339,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "6e0b9a1039c8f178ee6f3fb15abbb8b801ce9a74664dc0e826b8eac666a6fc46",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:47:00+00:00",
            "window_start": "2026-11-23T19:37:00+00:00"
          },
          "record_hash": "2258e0c3f77d748017076090e669c2c98dea1fe473e9d2aee31096e81b5bc3b5",
          "status": "OK",
          "v": 97490.0,
          "version": "1.891ed5cd"
        },
        "recent_volume_5m": {
          "age_s": 2.558339,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "6e0b9a1039c8f178ee6f3fb15abbb8b801ce9a74664dc0e826b8eac666a6fc46",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:47:00+00:00",
            "window_start": "2026-11-23T19:37:00+00:00"
          },
          "record_hash": "3da4a053ead5891c3e710a98507b3e4e570efdfa823e0c2b39d210531dc3d2ce",
          "status": "OK",
          "v": 46356.0,
          "version": "1.c7331f02"
        },
        "relstr_spy_60m": {
          "age_s": 122.558339,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "4a2efcccfad641379da325f71ec41a86cd514996d16cf454e59b74429a421867",
          "status": "OK",
          "v": 0.001995243311,
          "version": "1.c04b464c"
        },
        "ret_15m": {
          "age_s": 122.558339,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "d0b4343de4ebc557cdec7d62eae13fd8c19b62412d784631613f827f8aedf5d6",
          "status": "OK",
          "v": -0.00521947463,
          "version": "1.3fa23ddd"
        },
        "ret_1d": {
          "age_s": 122.558339,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "4871f8f39f073d45e17d3d6f5ca60a8fec098c3c382779b9f1d17c4eff156f1b",
          "status": "OK",
          "v": -0.07827648115,
          "version": "1.b77eca69"
        },
        "ret_20d": {
          "age_s": 254822.5583,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "c89eca0e545e370a2b5106418f52c2c97be259b8d9a271ffd1a96adbaa2aca0a",
          "status": "MISSING",
          "v": null,
          "version": "1.7d1f1942"
        },
        "ret_5d": {
          "age_s": 254822.5583,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "05a741e625955a85a438ad18773375028848616408999e7af63ece7accaed8b3",
          "status": "MISSING",
          "v": null,
          "version": "1.5d56db82"
        },
        "ret_5m": {
          "age_s": 122.558339,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "8889142c7c313630f5e598ae80cfca38f47a66c447adf77b879dd21fe2f85bfd",
          "status": "OK",
          "v": 0.00103323575,
          "version": "1.c10a3b57"
        },
        "ret_60m": {
          "age_s": 122.558339,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "41e9a5dd135419e6554eb609bc32d0fc113d9db6ba4565df82b96ff5e7505d87",
          "status": "OK",
          "v": 0.001205649328,
          "version": "1.6c49ff8f"
        },
        "rsi14": {
          "age_s": 254822.5583,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "1e59b41cf19356a8afb2c1abc8da30ba54a3ae1c9ca6adec3645d67baab39a97",
          "status": "MISSING",
          "v": null,
          "version": "1.273a3a79"
        },
        "rsi14_15m": {
          "age_s": 122.558339,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "8e2405b48f61208fcc98491d12fb4cfef18c440cec8f1c795d9799094ef01d8d",
          "status": "OK",
          "v": 58.43968457,
          "version": "1.f0b8fdaf"
        },
        "rvol_60m": {
          "age_s": 122.558339,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "3b5ba374c708f1a0cb9ecac010ad1aa442f0b1d3db0c25896c7a2017feddd64a",
          "status": "OK",
          "v": 0.01029213162,
          "version": "1.84c5ec7e"
        },
        "sellable_qty": {
          "age_s": 0.485236,
          "quality": {},
          "record_hash": "1031cd2150320480ff1ec9a97e8296cbb5591d56cbb2b9ad0454be1c3c0eb13e",
          "status": "OK",
          "v": "0",
          "version": "1.9cbf72e4"
        },
        "sma20": {
          "age_s": 254822.5583,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "15576f86a2842f5eb53a8c69129bc796ec2bb02d553d6eb692a0246444b821e2",
          "status": "MISSING",
          "v": null,
          "version": "1.80f8a078"
        },
        "sma50": {
          "age_s": 254822.5583,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "c77619dbf2bb36c37659503666953bdfa289b5ad53f8419d72ac47d490aa3455",
          "status": "MISSING",
          "v": null,
          "version": "1.3890c9d7"
        },
        "spread_bps": {
          "age_s": 1.400542,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "7b125c3e9e719729f056d254d077ee53b15646f41d7caed724fdfa8ee6998afa",
          "status": "OK",
          "v": 3.441156228,
          "version": "1.e2b080ab"
        },
        "trend_sma20_vs_sma50": {
          "age_s": 254822.5583,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "c3f4c96640a0fefa86efead1a20dc2a8c20470887509f9a64b8b123a7f0f6feb",
          "status": "MISSING",
          "v": null,
          "version": "1.84583425"
        },
        "unrealized_pnl_pct": {
          "age_s": 0.485236,
          "quality": {},
          "record_hash": "dddd8abf751ef2155f25e6ea7b4f44fc4a02a1b735571ed6a0df37575b4637df",
          "status": "OK",
          "v": 0,
          "version": "1.7c530604"
        },
        "vol_regime_ratio": {
          "age_s": 122.558339,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "362afe727800b5cd2883231bd64de49ee5d1e0efe009d0aa7bcf0c02cddd7deb",
          "status": "OK",
          "v": 1.048392135,
          "version": "1.302e72c1"
        },
        "volume_z20": {
          "age_s": 254822.5583,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "acd6606915e0844ee2fa5f30507b576df69022855968e20bad1ec489ca7b84b7",
          "status": "MISSING",
          "v": null,
          "version": "1.970d159b"
        },
        "volz_tod_15m": {
          "age_s": 122.558339,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "00402ad410208e76d63fb60dc603ca6c5c3933ab4023869011a7814ed1722a9c",
          "status": "OK",
          "v": 0.2274907125,
          "version": "1.4315d547"
        },
        "vwap_dev_session": {
          "age_s": 122.558339,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "495e37002161bf0329faf8c138f95614813f255e17d85d4c05aed2203e21ed59",
          "status": "OK",
          "v": 0.001692688105,
          "version": "1.b41de1ff"
        }
      }
    },
    "validation_policy": "scored-15m-plus-2m-v1"
  },
  "council_mode": "PAPER_COUNCIL_SKEPTIC_OFF",
  "chair": {
    "note": "Prearbiter blocks entry (NO_SIGNAL_ABOVE_THRESHOLD) and no sellable inventory; no actionable signal.",
    "role": "CHAIR",
    "run_id": "a9006978-cfc1-56ab-b176-855dabc1c2a3",
    "candidates": [],
    "schema_version": 2
  },
  "skeptic_audit": {
    "attempts": 0,
    "skip_reason": "DISABLED_BY_OPERATOR"
  },
  "role_outputs": [
    {
      "role": "CHAIR",
      "status": "OK",
      "response": "{\n  \"schema_version\": 2,\n  \"run_id\": \"a9006978-cfc1-56ab-b176-855dabc1c2a3\",\n  \"role\": \"CHAIR\",\n  \"candidates\": [],\n  \"note\": \"Prearbiter blocks entry (NO_SIGNAL_ABOVE_THRESHOLD) and no sellable inventory; no actionable signal.\"\n}",
      "error": null
    },
    {
      "role": "LIQUIDITY",
      "status": "OK",
      "response": "{\"schema_version\":2,\"run_id\":\"a9006978-cfc1-56ab-b176-855dabc1c2a3\",\"source\":\"code\",\"data_confidence\":\"HIGH\",\"role\":\"LIQUIDITY\",\"symbols\":[{\"symbol\":\"INTC\",\"evidence\":[{\"path\":\"symbols.INTC.spread_bps\",\"band\":\"NORMAL\"},{\"path\":\"symbols.INTC.mid_px\",\"band\":\"POSITIVE\"},{\"path\":\"symbols.INTC.volz_tod_15m\",\"band\":\"NORMAL\"}],\"gate\":{\"state\":\"PASS\",\"size_multiplier\":1.0,\"reasons\":[]},\"note\":\"deterministic code assessment\"}]}",
      "error": null
    },
    {
      "role": "PORTFOLIO",
      "status": "OK",
      "response": "{\"data_confidence\": \"HIGH\", \"role\": \"PORTFOLIO\", \"run_id\": \"a9006978-cfc1-56ab-b176-855dabc1c2a3\", \"schema_version\": 2, \"source\": \"code\", \"symbols\": [{\"evidence\": [], \"gate\": {\"reasons\": [\"position qty is zero; cannot sell without inventory\"], \"size_multiplier\": 0, \"state\": \"PASS\"}, \"note\": \"No held inventory; reduce/exit pressure N/A.\", \"symbol\": \"INTC\"}]}",
      "error": null
    },
    {
      "role": "REGIME",
      "status": "OK",
      "response": "{\"data_confidence\":\"HIGH\",\"risk_appetite\":\"NEUTRAL\",\"role\":\"REGIME\",\"run_id\":\"a9006978-cfc1-56ab-b176-855dabc1c2a3\",\"schema_version\":2,\"source\":\"code\",\"symbols\":[{\"symbol\":\"INTC\",\"evidence\":[{\"path\":\"market.regime_label\",\"band\":\"UPTREND\"},{\"path\":\"market.spy_vol_regime_ratio\",\"band\":\"POSITIVE\"},{\"path\":\"symbols.INTC.atr14_15m\",\"band\":\"POSITIVE\"},{\"path\":\"symbols.INTC.ema21_15m\",\"band\":\"POSITIVE\"},{\"path\":\"symbols.INTC.ema9_15m\",\"band\":\"POSITIVE\"},{\"path\":\"symbols.INTC.ema_gap_bps_15m\",\"band\":\"POS_STRONG\"}],\"note\":\"deterministic code assessment\"}]}",
      "error": null
    },
    {
      "role": "TECHNICAL",
      "status": "OK",
      "response": "{\"data_confidence\": \"HIGH\", \"role\": \"TECHNICAL\", \"run_id\": \"a9006978-cfc1-56ab-b176-855dabc1c2a3\", \"schema_version\": 2, \"source\": \"code\", \"symbols\": [{\"evidence\": [], \"note\": \"Short horizon 5m positive, 15m strong gap supports long initiation within code bounds.\", \"signal\": {\"confidence\": 0.8, \"horizon\": \"INTRADAY\", \"score\": 0.6286, \"state\": \"SIGNAL\"}, \"symbol\": \"INTC\"}]}",
      "error": null
    }
  ],
  "reason_codes": [
    "NO_SIGNAL_ABOVE_THRESHOLD"
  ],
  "notes": [
    "evidence_pack:5e20efa8a42352b5a59a4a2904c5f2b9a68b37751de5976af04e104fefb39ec1",
    "council_run:a9006978-cfc1-56ab-b176-855dabc1c2a3",
    "NO_SIGNAL_ABOVE_THRESHOLD"
  ],
  "error": null,
  "proposals_and_risk": []
}
```

</details>

### 14:48:06 ET · DECIDED_HOLD

<details>
<summary>Recorded decision evidence</summary>

```json
{
  "decision_id": "df35ffe1-f8a1-51e9-b5c0-a54bac834872",
  "inputs": {
    "as_of": "2026-11-23T19:48:03.237416Z",
    "regime": {
      "label": "uptrend"
    },
    "account": {
      "cash": 99803.06,
      "equity": 99803.06,
      "status": "ACTIVE",
      "account_id": "PAPER_ACCOUNT",
      "last_equity": 99803.39,
      "buying_power": 399212.24
    },
    "positions": [],
    "symbols": {
      "INTC": {
        "mid": 58.13,
        "rsi14": null,
        "ret_1d": -0.0783,
        "ret_5d": null,
        "ret_20d": null,
        "atr14_pct": null,
        "price_vs_sma20": null,
        "trend_sma20_vs_sma50": null
      }
    }
  },
  "feature_evidence": {
    "account_ref": "PAPER_ACCOUNT",
    "as_of": "2026-11-23T19:48:03.237416+00:00",
    "availability": {
      "account": "fresh",
      "bars": "fresh",
      "calendar": "fresh",
      "news": "fresh",
      "ok_fraction_core_features": 1.0,
      "quotes": "fresh"
    },
    "bands_hash": "810517c6e124c7ebc23ca0ebce7ef7ba7cc66b30bc21cacc66c1a221174255d4",
    "feasibility": {
      "INTC": {
        "can_buy": true,
        "can_buy_reasons": [],
        "can_sell": false,
        "can_sell_reasons": [
          "NO_SELLABLE_INVENTORY"
        ],
        "entry_window_open": true,
        "entry_window_reason": "",
        "held_qty": "0.0",
        "max_new_notional_usd": "2000.0",
        "sellable_qty": "0"
      }
    },
    "feature_slot": {
      "candles": {
        "INTC|2026-11-23T19:33:00+00:00": "c37f8ccdeccf9064ac8a9b4e6a21d4ed42be7567ab3ba10eb0558b68028107c0",
        "INTC|2026-11-23T19:34:00+00:00": "564e3a869b90c07bc6f4dc36fc9a4642620456c6cac5272aff6455bd272177b1",
        "INTC|2026-11-23T19:35:00+00:00": "8c40460eb8f86125bf2228c6e0b5478931f3e3a91a013bd23caa1bb828639442",
        "INTC|2026-11-23T19:36:00+00:00": "9cb732a5a05f88fcae5944f0121aac8aaa2713bd234d104b87ddb513e8886ae9",
        "INTC|2026-11-23T19:37:00+00:00": "9d5b09f82117334dcc0f33b8c32ad04009545b4670f26997f04929a89d44df93",
        "INTC|2026-11-23T19:38:00+00:00": "e98c98af48936fd32ec6ad72041fcbfa1de8511a2b8911c69eabcd4ab7117e18",
        "INTC|2026-11-23T19:39:00+00:00": "422314eba37616c0546eed1ed8aa018f6b54ce6bec687378c7704d9ca2065248",
        "INTC|2026-11-23T19:40:00+00:00": "70e0d8b0a63b3723514998b8205402a930375f59ca5308b2f48f6dbab08cd617",
        "INTC|2026-11-23T19:41:00+00:00": "4510c4c83faf5f5878d401794d4b7bed12120a3527e7efc68be6e7a94d44c40b",
        "INTC|2026-11-23T19:42:00+00:00": "98067d1cfbe2cf62a97c2f9a655f0cf4470e9f8fb2391eb0463aff7d674dad4b",
        "INTC|2026-11-23T19:43:00+00:00": "c8d1f80659f571bf3eb64a17b9935be4ce7a092a55afd0608b149b1e717e9011",
        "INTC|2026-11-23T19:44:00+00:00": "c1aa4b559490e25f881fb40af919d8644954d00315de5f007556c6e7791a0b28",
        "INTC|2026-11-23T19:45:00+00:00": "34a1b438e39db05694f921c5baec9ae6582c0220846c45eb8506fabad543f270",
        "INTC|2026-11-23T19:46:00+00:00": "805d43a04e130aa788c4098fa1275ef209d434dbdf234b2dbc11f9444444a83b",
        "INTC|2026-11-23T19:47:00+00:00": "877bc5250b1ff660d6061932b5651c5824af3f63b8d90833befef35f081fc349",
        "SPY|2026-11-23T19:33:00+00:00": "60acf2b6b72dfb53f598542c183985e00d5820e45e6a15aaa702caa2e7db45df",
        "SPY|2026-11-23T19:34:00+00:00": "205774036f40cb4bc8e44df4d46ef150bd7d25dedeb8a897455bddc1dd4763d8",
        "SPY|2026-11-23T19:35:00+00:00": "a3f33f928527ca6cd947868e44e270cfe45857f8acf9296afd6811bf7c66a716",
        "SPY|2026-11-23T19:36:00+00:00": "20f2610f9083c52c53c44110cf31c15486c3658b74baf10c77427c7f1643e451",
        "SPY|2026-11-23T19:37:00+00:00": "cfc075a20afd9004c6a54e55e02de60aa1ac6fab559ca2bc363b4083a5a7b0e8",
        "SPY|2026-11-23T19:38:00+00:00": "8ac7b4d0dc16f15a1b48e3576c48557a2cf3e5e01e9dbd56ec12e4206987e786",
        "SPY|2026-11-23T19:39:00+00:00": "38712a0709a4972b95a52f42b45fd54896d71cc49ce48651c65445f1a42bf62f",
        "SPY|2026-11-23T19:40:00+00:00": "e49f4baca7c7583df76c009735c11448f1023f1415b68e390409997276db3480",
        "SPY|2026-11-23T19:41:00+00:00": "0dccbf44a642c7d605f69cb3858d90923162c6c2b93f66b9555d77776438a183",
        "SPY|2026-11-23T19:42:00+00:00": "88269dcad14d8b8d3584bb870bfc6f5eed07f56a971f9ad7e1037bfff28a3780",
        "SPY|2026-11-23T19:43:00+00:00": "a4aebaa6965c7c246c1610c4eff9a05d061eff2cadc3940774ca5ab43368ca06",
        "SPY|2026-11-23T19:44:00+00:00": "b91459d6c5ec4fb98cb4404bbe1cd7357fe920ab60a2e98579d2b6fb1626730d",
        "SPY|2026-11-23T19:45:00+00:00": "467c27fb5d5f1da7405a638366403833df31cfdd7aae5abf3fe2d4bf9f1de532",
        "SPY|2026-11-23T19:46:00+00:00": "a7668e87604b88bc72c1eadf5d9870964634f7b5e5b13baa18713dfa791d317c",
        "SPY|2026-11-23T19:47:00+00:00": "4bed66e17e5a42bb1a8cd2145b47115c4782478e39ddcb5375ca07eda3f81667"
      },
      "close": "2026-11-23T19:48:00+00:00",
      "feed": "iex",
      "indicator_close": "2026-11-23T19:45:00+00:00",
      "indicator_input_hashes": {
        "INTC": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
        "SPY": "68be2784fe1097306ec89b5433c1c0b0393b316ceebc03170624a4214da8ac5c"
      },
      "provisional": true,
      "records": {
        "market:market:breadth_above_ema21": "d7e2f70fedf1d18806a57fa4210d951ce450efccdd03a1fa716baff26d0f59e9",
        "market:market:regime_label": "b5f7eda754fe89980a8ade83e3496e26768374e4bbb5fca559b77ed06e580f14",
        "market:market:spy_ema_gap_bps_15m": "5885f7d1170e4539d33b130275da00b6751841c47609429095ed1e27403a7ec2",
        "market:market:spy_ret_60m": "a02fc6ad02c26c858ccc3f3f44a2bdbea0cf2b8cbd7fd43e18f162a723bcd8e9",
        "market:market:spy_vol_regime_ratio": "f92540c64f7b22c073852594ff85408dcdd00f7c41695b8e8d341ba75a6f0bcc",
        "symbol:INTC:adv_usd_20d": "b9b2c8cd47063244741a0be3a99b852571258b975af9e1831bf9c22ac86c817d",
        "symbol:INTC:atr14_15m": "6f731751bfa53150c4b34c9f00c97b6e20fc9879a19350f0ce7cbe19a7070a61",
        "symbol:INTC:atr14_1d": "7109941c8f13c27be9954427260fd23488765da0017ae6e7268c52c67c282e0d",
        "symbol:INTC:atr14_pct": "72b22515a9b698de8e221ba3601ca48bfe5aa847f96eb780cd201d7da6e1b10b",
        "symbol:INTC:dist_hi_atr": "6d8a8604bb34ece3f8f1718abd36862fb754d0c31565c8409f84e0bd49b3fac7",
        "symbol:INTC:dist_lo_atr": "5e065aeb347b8d04bd3683351f9b3f6cac0164d8cffa2994d55e2205704a39a1",
        "symbol:INTC:ema21_15m": "026dc43aa182328e915e6f6d23296bedca2f3d61e29ad492593fd2b16c1f2c9c",
        "symbol:INTC:ema9_15m": "779c29eadfec6fe54e83478754f967d3444f194d88d34349bf014707a7b14100",
        "symbol:INTC:ema_gap_bps_15m": "2d80bf72eea509fb31fba6a2c3b863d8d8dc686f8d007db33fe90cf4a50e5145",
        "symbol:INTC:gap_open_pct": "22372f1618bb0042d504687f06dc178f5d5531095633eddeaf4bcfe97a2ded36",
        "symbol:INTC:intraday_ret_1h": "584b190315139eaa5cf532afd4584686eee1ec8a960635264ed6e8e8c24aeec5",
        "symbol:INTC:intraday_setup_1m": "f81a8ddac7a2eaeb605a6f61d35f2739cf108443f77f5380311fd9d5b62c5e47",
        "symbol:INTC:last_close": "d19401a83eca33beec8f4dc4c9fd9de4a732eca37d9f9287a4931e7ba85850f1",
        "symbol:INTC:macd_hist_15m": "ffc4ec65b3c48fbd631f09dccfb6d59e271d94c9ffd76307010798940056e67d",
        "symbol:INTC:price_vs_sma20": "0d79ec3c1b357a5011464af77c39b3fcad072140f1af42e8fc4caaaa2d603acd",
        "symbol:INTC:recent_price_10m": "8cdde448c2aa59e612a47f7fcc042bd1c65c454edd7a0e5ff0b37383828701a5",
        "symbol:INTC:recent_range_bps_10m": "47e5ee69cd3dbc225d14c66d47392d0e2f9f5e097dc77d9bc6f9581d575dbd7e",
        "symbol:INTC:recent_range_bps_5m": "108fee22ecc18a6047676ddce1583fcdba478376343b8daa551dea096a5f180d",
        "symbol:INTC:recent_return_10m": "509d6669cf644bb60a847eba6c381cd5548e5fff4e99aa8c7ce9f6e8b90a61df",
        "symbol:INTC:recent_return_5m": "2cfd8ab761646a532a6ee4b0a51a6ef26cfada382c4dd8d67c8475449604b93a",
        "symbol:INTC:recent_volume_10m": "0982dbd0173ef71d3e94b805945420c2b9d9f4d767d26cb5217a8dea39043d1e",
        "symbol:INTC:recent_volume_5m": "87473261f9bf18efe7c71c4a44baf8cbf2fde631f8f3fc66c49a0ccc9a6a342a",
        "symbol:INTC:relstr_spy_60m": "836e90f6753bb59428ce48c07663954006350f8b35859a28a43941855d4cdb56",
        "symbol:INTC:ret_15m": "793205b42417a1bf548206c5008d6f938c7ec932c27840c05480580cf405b29f",
        "symbol:INTC:ret_1d": "4871f8f39f073d45e17d3d6f5ca60a8fec098c3c382779b9f1d17c4eff156f1b",
        "symbol:INTC:ret_20d": "c89eca0e545e370a2b5106418f52c2c97be259b8d9a271ffd1a96adbaa2aca0a",
        "symbol:INTC:ret_5d": "05a741e625955a85a438ad18773375028848616408999e7af63ece7accaed8b3",
        "symbol:INTC:ret_5m": "23eb8eb2d48b64451f4c198147f93db2cd145e341017336abcb2778e1d9a9bd6",
        "symbol:INTC:ret_60m": "2fd9fcfa51ca874d4ff0d1dade1089f2c07f4acef6e9ac6ba31b69a8a1ccc90a",
        "symbol:INTC:rsi14": "1e59b41cf19356a8afb2c1abc8da30ba54a3ae1c9ca6adec3645d67baab39a97",
        "symbol:INTC:rsi14_15m": "8e2405b48f61208fcc98491d12fb4cfef18c440cec8f1c795d9799094ef01d8d",
        "symbol:INTC:rvol_60m": "c540ccfe54591549a9b3ab81970770d24f749a741508c2479e246a1a4d16afc4",
        "symbol:INTC:sma20": "15576f86a2842f5eb53a8c69129bc796ec2bb02d553d6eb692a0246444b821e2",
        "symbol:INTC:sma50": "c77619dbf2bb36c37659503666953bdfa289b5ad53f8419d72ac47d490aa3455",
        "symbol:INTC:trend_sma20_vs_sma50": "c3f4c96640a0fefa86efead1a20dc2a8c20470887509f9a64b8b123a7f0f6feb",
        "symbol:INTC:vol_regime_ratio": "b2775b8df8a6deed3a7f799644bf357792f178e8f626e81563914e398b777860",
        "symbol:INTC:volume_z20": "acd6606915e0844ee2fa5f30507b576df69022855968e20bad1ec489ca7b84b7",
        "symbol:INTC:volz_tod_15m": "00402ad410208e76d63fb60dc603ca6c5c3933ab4023869011a7814ed1722a9c",
        "symbol:INTC:vwap_dev_session": "ae72669fd159250cd4508bee485464f531513ddd829a07e0c1fe888348cd2add",
        "symbol:SPY:adv_usd_20d": "92e94f829df49f4b3a8d0be7612b000e92190d5356f55e566f04069ca7b9ffd5",
        "symbol:SPY:atr14_15m": "7ab448ef9d85396282151eac59236f9553a486b5c77591049f30866a0df20c74",
        "symbol:SPY:atr14_1d": "3cac187afe8b3f12d7d3b3b86986d403d549ebe59a7ccfaa10a213aaea0d6f29",
        "symbol:SPY:atr14_pct": "86a49f6a2b7c51bced8c4109a9b641fd3430da5d9872f600c092cec75526d214",
        "symbol:SPY:dist_hi_atr": "4859461e6fe2d4601e83bfe10a2ad279f6383b0e8baff460bfc5667dae27e668",
        "symbol:SPY:dist_lo_atr": "c330c2f4709a4b4b3f5233cbc485d6c584a60da65564263e76b792472da2680a",
        "symbol:SPY:ema21_15m": "e101df90a64d088f78547e381107b8db83b2541409047168500bf08d4caa4b43",
        "symbol:SPY:ema9_15m": "d9a6929dcd2aa029a0657e3b23036ea5c8e549c3e28f704d22c59d9141f45d16",
        "symbol:SPY:ema_gap_bps_15m": "12f402c62d8c646eb7b75bb92bec226e49110827a04064a50b8a1e5b881fc789",
        "symbol:SPY:gap_open_pct": "1c9616a65f2f013255300b42e56d88ac7a725e105e6f59b39d79e458ad29184e",
        "symbol:SPY:intraday_ret_1h": "4a3cbce2b9dcc1b99d6875d1dfcc341ba613acfd2d05e42ab8e2dd8730e5c8b3",
        "symbol:SPY:intraday_setup_1m": "cbd6359e201bb4173d44619c7b01fc3e4d7bbbfcbd21df198ac8f392f51c3b85",
        "symbol:SPY:last_close": "caf596deca80d26016ad4208908f5e9f946155af82bcf05ef2276748182b2361",
        "symbol:SPY:macd_hist_15m": "7c1f84aa5b3c914a24e8512883539348c328fedf77f1ca8fddef3c9428311b8a",
        "symbol:SPY:price_vs_sma20": "963d8268f25c4849a1b268733b11edd2005fe4a8c767d1439d8478255d5a22c9",
        "symbol:SPY:recent_price_10m": "73b8ec311817a4cad7edf17a51dbd1d21b872210b0c23dd3ee49586d57f67669",
        "symbol:SPY:recent_range_bps_10m": "816a00579f07f506b19c26e6305508cbcbd3847b95667e8a3183e9719e16b681",
        "symbol:SPY:recent_range_bps_5m": "75b31e844856de0f2126b617f7dd36b32552d67c88f3d6c62afd87ccc1edd015",
        "symbol:SPY:recent_return_10m": "e51c36bd9542faa2c843a30494dc6d7499dd7ee82f5f0244c17f4d66da7639ef",
        "symbol:SPY:recent_return_5m": "f910638706777604e0e50641c0833b3a32f3fe03662f8702c9606ea027abfd84",
        "symbol:SPY:recent_volume_10m": "c4071c8e33eeeca59922fa33aa5aa0ea95351332e8e294a21f19d4c7f85692cb",
        "symbol:SPY:recent_volume_5m": "59502d15cebb9c5ae4c604ecbbadecf1bc72d57c0ec7caeb861eca09c8787bea",
        "symbol:SPY:relstr_spy_60m": "8192ee3c1e096d3220e21bd96547302036aad20b1f8b2a88d06eb43fca3d16bd",
        "symbol:SPY:ret_15m": "e137147df35f8b049f0ca8ec9e4d3ff7c859ab89504259e2ac2bef5bcb2cf931",
        "symbol:SPY:ret_1d": "aab94a7dafcf360313d949fc12ced963ccb5a8b3ef27866b2b930d2d5817c533",
        "symbol:SPY:ret_20d": "5cb42b7c179c74bdcedf0dbf4ce0ee12832341fe24b75d306dccc8cc03e792c3",
        "symbol:SPY:ret_5d": "7c31dada2f0a36e24d03e89b66cb73d377f3c298c10867a1be2b05be76be6a0c",
        "symbol:SPY:ret_5m": "feae8d2f57c6b21b698b18f8a34599a62dd8379095e8729f08519d48e36d58bf",
        "symbol:SPY:ret_60m": "55f830a3a8fed211c2287621d267beadebc67701f140112ca2b8d8d02294c1c6",
        "symbol:SPY:rsi14": "ee11c2b462281f9fc927ac380b6bb2557ff2e158729fe2f17aa91d152eb3fb9f",
        "symbol:SPY:rsi14_15m": "7a2d8a98c627154aeccdc9a68b885c12330bcb82ce58cddb4d0a2f4136033fc0",
        "symbol:SPY:rvol_60m": "681be63555975b6bd7e8e4dae807d613578bc606fb48703d022d6235c3b9e8ee",
        "symbol:SPY:sma20": "1b30496ca2845ccd7a79462c221d840260e1c0361b7feb9dedbc5dc30bd4b2a5",
        "symbol:SPY:sma50": "94c11d37cff9b64498753612d4be2b84f39d1931bd55ec9e573a0c8697ceb72b",
        "symbol:SPY:trend_sma20_vs_sma50": "8aee1d285ca5a8e44083c58d0fad60754235fda2855c6ac02c9796bc41cff8bc",
        "symbol:SPY:vol_regime_ratio": "3ec87d4abe84ab93bd43b7344839a469821942e64042922ae9f511cd7c7b2bb5",
        "symbol:SPY:volume_z20": "26f74a49cf931c478f404ef3e6a0850c2e214cc588216f87e068535e16f86e9f",
        "symbol:SPY:volz_tod_15m": "29640670f4a0587e4e43a5ad4cd8d40a485c1b2537f64212b1cb41ffc2d19792",
        "symbol:SPY:vwap_dev_session": "402a66980909949f37d91d6daae2afb2230c0278aad4072d83d05c5b7a2e0af6"
      },
      "symbols": [
        "INTC",
        "SPY"
      ]
    },
    "horizons": {
      "INTC": {
        "10m": {
          "age_s": 3.237416,
          "last_bar_end": "2026-11-23T19:48:00+00:00",
          "status": "OK"
        },
        "15m": {
          "age_s": 183.237416,
          "last_bar_end": "2026-11-23T19:45:00+00:00",
          "status": "OK"
        },
        "5m": {
          "age_s": 3.237416,
          "last_bar_end": "2026-11-23T19:48:00+00:00",
          "status": "OK"
        },
        "60m": {
          "age_s": 183.237416,
          "last_bar_end": "2026-11-23T19:45:00+00:00",
          "status": "OK"
        },
        "horizon_conflict": false
      }
    },
    "market": {
      "breadth_above_ema21": {
        "age_s": 183.237416,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "d7e2f70fedf1d18806a57fa4210d951ce450efccdd03a1fa716baff26d0f59e9",
        "status": "OK",
        "v": 1.0,
        "version": "1.1dfe664d"
      },
      "minutes_to_close": {
        "age_s": 0.589194,
        "quality": {},
        "record_hash": "e87ca22840ab0fc6367f1741322394776d31cc52450a5b9934e5ef6a137ca6f1",
        "status": "OK",
        "v": 71.95586297,
        "version": "1.e79b1ead"
      },
      "regime_label": {
        "age_s": 183.237416,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "b5f7eda754fe89980a8ade83e3496e26768374e4bbb5fca559b77ed06e580f14",
        "status": "OK",
        "v": "UPTREND",
        "version": "1.f8b361d7"
      },
      "session_phase": {
        "age_s": 0.589194,
        "quality": {},
        "record_hash": "6e23cd0f09cccdad4211eecf9950fcb4ea9eaba89569e5be811d1fd9254fa521",
        "status": "OK",
        "v": "NORMAL",
        "version": "1.91f88fe8"
      },
      "spy_ema_gap_bps_15m": {
        "age_s": 183.237416,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "5885f7d1170e4539d33b130275da00b6751841c47609429095ed1e27403a7ec2",
        "status": "OK",
        "v": 37.89644347,
        "version": "1.fda7da7a"
      },
      "spy_ret_60m": {
        "age_s": 183.237416,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "a02fc6ad02c26c858ccc3f3f44a2bdbea0cf2b8cbd7fd43e18f162a723bcd8e9",
        "status": "OK",
        "v": -0.0002701410968,
        "version": "1.9feddbd1"
      },
      "spy_vol_regime_ratio": {
        "age_s": 183.237416,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "f92540c64f7b22c073852594ff85408dcdd00f7c41695b8e8d341ba75a6f0bcc",
        "status": "OK",
        "v": 1.423290883,
        "version": "1.3b7257aa"
      }
    },
    "meta": {
      "news": {
        "INTC": {
          "effective_weight": 0,
          "in_window": 0,
          "newest_age_min": 1786.603957,
          "policy": "48h retained; per-article decay and minimum relevance; 4h count is descriptive",
          "poller_last_ok_age_s": 9.354724,
          "retrieved": 1,
          "selected": 0,
          "state": "QUIET",
          "window_min": 240
        }
      }
    },
    "news_blob_hash": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
    "news_context_blob_hash": "ef023692226f6319baf7f6429f023deb1a988f59c953b103e7a5f425a6a5d062",
    "portfolio": {
      "aggregate_cap_usd": {
        "age_s": 0.589194,
        "quality": {},
        "record_hash": "941bb2d6adc9160e0115c15d994c74bae83af5e7be677b1f79e8251c59c23c16",
        "status": "OK",
        "v": "49901.530",
        "version": "1.5b3d1daf"
      },
      "aggregate_headroom_usd": {
        "age_s": 0.589194,
        "quality": {},
        "record_hash": "b641d84cec1d38340b35db4a885cb5d1ca0f8decea47a3cf17b4bce188bb0ac5",
        "status": "OK",
        "v": "49901.530",
        "version": "1.7f894fff"
      },
      "buying_power": {
        "age_s": 0.589194,
        "quality": {},
        "record_hash": "e02a39601f31eac7edd41bd544f5d291b06ac7da1f6946b8352ffd1eb21c3daf",
        "status": "OK",
        "v": "399212.24",
        "version": "1.74948dec"
      },
      "cash": {
        "age_s": 0.589194,
        "quality": {},
        "record_hash": "28a866b08062007ece324a4951035d067e43e77cf0db9879b6d672e7d30a507f",
        "status": "OK",
        "v": "99803.06",
        "version": "1.b067f5e3"
      },
      "day_pnl_pct": {
        "age_s": 0.589194,
        "quality": {},
        "record_hash": "b45f9fd26f0a63dfe790c008a270076047f12e4b8341959fdd3aaa99f156727d",
        "status": "OK",
        "v": "-0.0003306500911441986088849300",
        "version": "1.35e81852"
      },
      "drawdown_pct": {
        "age_s": 0.589194,
        "quality": {},
        "record_hash": "f720f8cab8f0092f42fb08b439761abea4f868d50784fcbfe6e282858bee023d",
        "status": "MISSING",
        "v": null,
        "version": "1.19aac9ba"
      },
      "equity": {
        "age_s": 0.589194,
        "quality": {},
        "record_hash": "883612405979efe61337eb3e8d686be3caf125cb263631cbb262189d774a3893",
        "status": "OK",
        "v": "99803.06",
        "version": "1.a2192616"
      },
      "gross_exposure_pct": {
        "age_s": 0.589194,
        "quality": {},
        "record_hash": "3a2ccb7649ee345a6633830083abfe20bb4e80346bbbb2a747c92b71dffc2693",
        "status": "OK",
        "v": "0E+2",
        "version": "1.b82cc518"
      },
      "gross_exposure_usd": {
        "age_s": 0.589194,
        "quality": {},
        "record_hash": "f67231799a742f582aeb3db35ab449f1b24f72c848cd663df0d5671885b2738b",
        "status": "OK",
        "v": "0",
        "version": "1.e4c8752b"
      },
      "last_reconcile_age_s": {
        "age_s": 0.589194,
        "quality": {},
        "record_hash": "7da11b385747b7a0b3535e191e255672d1875d7345334dd9d4a6cebe78d3ee74",
        "status": "OK",
        "v": 0,
        "version": "1.5ed0382f"
      },
      "open_buy_notional_usd": {
        "age_s": 0.589194,
        "quality": {},
        "record_hash": "1a026e01768627439afed60033464dc253185012708179e22a276da22a17eca2",
        "status": "OK",
        "v": "0",
        "version": "1.0bd0ead1"
      },
      "open_orders": {
        "age_s": 0.589194,
        "quality": {},
        "record_hash": "ba792c240d5f6acbbd55f741b37a43d9750ab2d671fc7fe21cde2cbafff1a71b",
        "status": "OK",
        "v": [],
        "version": "1.1cf37cbf"
      },
      "open_orders_count": {
        "age_s": 0.589194,
        "quality": {},
        "record_hash": "341110e32fb668a24aa142c260103d2ce87a79ca050d56c054b553318de64504",
        "status": "OK",
        "v": 0,
        "version": "1.1db4227a"
      },
      "pending_reserved_usd": {
        "age_s": 0.589194,
        "quality": {},
        "record_hash": "f1e9296076cb37fe523af0ae1d56f351dee30fde0735ed21a0f4892a2cf1d221",
        "status": "OK",
        "v": "0",
        "version": "1.1c3e9604"
      },
      "positions": {
        "age_s": 0.589194,
        "quality": {},
        "record_hash": "3bc06d20f235d8214c6f0adfdcaad8953377a44a1f8f2f1694612a087a8cd1fe",
        "status": "OK",
        "v": [],
        "version": "1.c3284657"
      }
    },
    "registry_hash": "0fd3271269748046863b2f0558e45e2c333bb352eccc9899b7ff42277c8386fc",
    "schema_version": 1,
    "symbols": {
      "INTC": {
        "adv_usd_20d": {
          "age_s": 254883.2374,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "b9b2c8cd47063244741a0be3a99b852571258b975af9e1831bf9c22ac86c817d",
          "status": "OK",
          "v": 304793568.9,
          "version": "1.04f5e91f"
        },
        "ask_px": {
          "age_s": 1.422971,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "36c7a70682f0ee2787e5dc7d71d5376be12e164ac07ca1cfbab497ce2187df57",
          "status": "OK",
          "v": 58.14,
          "version": "1.d21cdd09"
        },
        "atr14_15m": {
          "age_s": 183.237416,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "6f731751bfa53150c4b34c9f00c97b6e20fc9879a19350f0ce7cbe19a7070a61",
          "status": "OK",
          "v": 0.7629598219,
          "version": "1.0cd14e73"
        },
        "atr14_1d": {
          "age_s": 254883.2374,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "7109941c8f13c27be9954427260fd23488765da0017ae6e7268c52c67c282e0d",
          "status": "MISSING",
          "v": null,
          "version": "1.65e38f4c"
        },
        "atr14_pct": {
          "age_s": 254883.2374,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "72b22515a9b698de8e221ba3601ca48bfe5aa847f96eb780cd201d7da6e1b10b",
          "status": "MISSING",
          "v": null,
          "version": "1.87450ee9"
        },
        "bid_px": {
          "age_s": 1.422971,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "88edcd117913be3a09066ebd6e1a89f74d6642576620ad7e9a97610885e2d847",
          "status": "OK",
          "v": 58.12,
          "version": "1.149628cd"
        },
        "dist_hi_atr": {
          "age_s": 183.237416,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "6d8a8604bb34ece3f8f1718abd36862fb754d0c31565c8409f84e0bd49b3fac7",
          "status": "OK",
          "v": -1.73010421,
          "version": "1.913ffc4a"
        },
        "dist_lo_atr": {
          "age_s": 183.237416,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "5e065aeb347b8d04bd3683351f9b3f6cac0164d8cffa2994d55e2205704a39a1",
          "status": "OK",
          "v": 1.985687787,
          "version": "1.79ba4c70"
        },
        "ema21_15m": {
          "age_s": 183.237416,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "026dc43aa182328e915e6f6d23296bedca2f3d61e29ad492593fd2b16c1f2c9c",
          "status": "OK",
          "v": 57.40577599,
          "version": "1.bfcac61e"
        },
        "ema9_15m": {
          "age_s": 183.237416,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "779c29eadfec6fe54e83478754f967d3444f194d88d34349bf014707a7b14100",
          "status": "OK",
          "v": 58.09168398,
          "version": "1.81255de8"
        },
        "ema_gap_bps_15m": {
          "age_s": 183.237416,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "2d80bf72eea509fb31fba6a2c3b863d8d8dc686f8d007db33fe90cf4a50e5145",
          "status": "OK",
          "v": 119.4841427,
          "version": "1.d4519f3c"
        },
        "gap_open_pct": {
          "age_s": 183.237416,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "22372f1618bb0042d504687f06dc178f5d5531095633eddeaf4bcfe97a2ded36",
          "status": "MISSING",
          "v": null,
          "version": "1.27438d4d"
        },
        "halted": {
          "age_s": 0.589194,
          "quality": {},
          "record_hash": "455d1afeba6b2bdf65552cac2dfc654fe70b42efc198c8b68f6840cf73a3f40c",
          "status": "OK",
          "v": false,
          "version": "1.22c5cf87"
        },
        "held_minutes": {
          "age_s": 0.589194,
          "quality": {},
          "record_hash": "9cdf135920713638aa2e79f5d822ee367d6a6c842abbdece190c6381eda50b73",
          "status": "MISSING",
          "v": null,
          "version": "1.de6ed6d3"
        },
        "intraday_ret_1h": {
          "age_s": 183.237416,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "584b190315139eaa5cf532afd4584686eee1ec8a960635264ed6e8e8c24aeec5",
          "status": "OK",
          "v": 0.001120786275,
          "version": "1.c3bb7751"
        },
        "intraday_setup_1m": {
          "age_s": 3.237416,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "d95f78a421e15f1def875d6076aa3e3e1dcdb24fd6935e7dd4eeb44e2b5090ea",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:48:00+00:00",
            "window_start": "2026-11-23T19:38:00+00:00"
          },
          "record_hash": "f81a8ddac7a2eaeb605a6f61d35f2739cf108443f77f5380311fd9d5b62c5e47",
          "status": "OK",
          "v": {
            "confirmation": "NONE",
            "pattern": "NONE",
            "prior_trend": "UP",
            "range_break": "INSIDE",
            "range_ceiling": 58.21,
            "range_floor": 57.99,
            "setup_minute": null,
            "volume_ratio": 2.1569
          },
          "version": "1.2a1f51e0"
        },
        "last_close": {
          "age_s": 254883.2374,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "d19401a83eca33beec8f4dc4c9fd9de4a732eca37d9f9287a4931e7ba85850f1",
          "status": "MISSING",
          "v": null,
          "version": "1.f2485fc2"
        },
        "luld_active": {
          "age_s": 0.589194,
          "quality": {},
          "record_hash": "186e1477ba9563ed831ac1185dbb2e8590ddf475ff401efa1ca973902d555cfd",
          "status": "MISSING",
          "v": null,
          "version": "1.84a715b2"
        },
        "macd_hist_15m": {
          "age_s": 183.237416,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "ffc4ec65b3c48fbd631f09dccfb6d59e271d94c9ffd76307010798940056e67d",
          "status": "OK",
          "v": -0.07751173219,
          "version": "1.391617c8"
        },
        "mid_px": {
          "age_s": 1.422971,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "9a399db337aecf1d44f078dc22cefcf7aa97568b4ff1c1fca8194a8ab82e1f77",
          "status": "OK",
          "v": 58.13,
          "version": "1.d567a349"
        },
        "news_age_min_latest": {
          "age_s": 9.354724,
          "quality": {},
          "record_hash": "8ec419f04ab81400968add32fcceefa7a19ea9185e0180f6761cfa1a53875205",
          "status": "MISSING",
          "v": null,
          "version": "1.d0f79dc8"
        },
        "news_confirmed": {
          "age_s": 0,
          "quality": {
            "source": "stored news and pinned price features"
          },
          "status": "OK",
          "v": false,
          "version": "news-confirmation-v2"
        },
        "news_count_1h": {
          "age_s": 9.354724,
          "quality": {},
          "record_hash": "52cc7e779f041441f9987a490c92e8be60002ef3c52807daa45bf20583017dbc",
          "status": "OK",
          "v": 0,
          "version": "1.0c9362fe"
        },
        "news_count_48h": {
          "age_s": 9.354724,
          "quality": {
            "as_of": "2026-11-23T19:48:03.237416+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 1,
          "version": "news-context-v2"
        },
        "news_count_4h": {
          "age_s": 9.354724,
          "quality": {
            "as_of": "2026-11-23T19:48:03.237416+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 0,
          "version": "news-context-v2"
        },
        "news_effective_sentiment": {
          "age_s": 0,
          "quality": {
            "selected": 0,
            "source": "decayed stored article metadata"
          },
          "status": "MISSING",
          "v": 0.0,
          "version": "news-decay-v2"
        },
        "news_event_flags_4h": {
          "age_s": 9.354724,
          "quality": {},
          "record_hash": "1b352cfdc4e08867c1b220a18661b5fac16ef8f506d03d4871ff2017744f5727",
          "status": "OK",
          "v": [],
          "version": "1.0b5a8a44"
        },
        "news_max_materiality_4h": {
          "age_s": 9.354724,
          "quality": {},
          "record_hash": "bf1b11fa6aca47871377ed96b7febbfaab7a723534dfa2a8ffd9ed6d70c619cd",
          "status": "OK",
          "v": 0,
          "version": "1.9c45e9b4"
        },
        "news_newest_age_min": {
          "age_s": 9.354724,
          "quality": {
            "as_of": "2026-11-23T19:48:03.237416+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 1786.603957,
          "version": "news-context-v2"
        },
        "news_novelty_max_4h": {
          "age_s": 9.354724,
          "quality": {},
          "record_hash": "fc65b5f9d5fa8c41633904806346ad008ca0b6edcf2448ee59d3145f12cadfc4",
          "status": "OK",
          "v": false,
          "version": "1.15ceb7bf"
        },
        "news_sent_ewm_240m": {
          "age_s": 9.354724,
          "quality": {},
          "record_hash": "8cfbdb008664eb60ed2131a507f6421795520b20bbe0b9beb98a8245e0f39f4b",
          "status": "OK",
          "v": 0,
          "version": "1.9cad993f"
        },
        "news_sent_ewm_60m": {
          "age_s": 9.354724,
          "quality": {},
          "record_hash": "2202425c7cce77025671450de219e2066d7b9cc11bc5bc8b09d1e4b9120944f3",
          "status": "OK",
          "v": 0,
          "version": "1.74ab70c1"
        },
        "news_source_div_4h": {
          "age_s": 9.354724,
          "quality": {},
          "record_hash": "4757b0a0a394c89b6a64db0e0019f516f66de26c3d4efd5a70bc90908d33daa0",
          "status": "OK",
          "v": 0,
          "version": "1.6fd469c4"
        },
        "position_qty": {
          "age_s": 0.589194,
          "quality": {},
          "record_hash": "f3f97f663c7c1a72ec441890c1f82be9476c60da352bc4ab3e7a48a90b324afe",
          "status": "OK",
          "v": "0",
          "version": "1.3a512120"
        },
        "position_value_usd": {
          "age_s": 0.589194,
          "quality": {},
          "record_hash": "68ff89efccc237fcf47eeed7a4069579169e31aa4c28d8dcc629e78c981c02ed",
          "status": "OK",
          "v": "0",
          "version": "1.9100bec4"
        },
        "price_vs_sma20": {
          "age_s": 254883.2374,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "0d79ec3c1b357a5011464af77c39b3fcad072140f1af42e8fc4caaaa2d603acd",
          "status": "MISSING",
          "v": null,
          "version": "1.a986b9cc"
        },
        "recent_price_10m": {
          "age_s": 3.237416,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "d95f78a421e15f1def875d6076aa3e3e1dcdb24fd6935e7dd4eeb44e2b5090ea",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:48:00+00:00",
            "window_start": "2026-11-23T19:38:00+00:00"
          },
          "record_hash": "8cdde448c2aa59e612a47f7fcc042bd1c65c454edd7a0e5ff0b37383828701a5",
          "status": "OK",
          "v": {
            "candles": [
              [
                0,
                58.085,
                58.13,
                58.045,
                58.045,
                3139.0,
                "VERIFIED_BAR"
              ],
              [
                1,
                58.045,
                58.165,
                58.045,
                58.095,
                12394.0,
                "VERIFIED_BAR"
              ],
              [
                2,
                58.095,
                58.19,
                58.045,
                58.185,
                11202.0,
                "VERIFIED_BAR"
              ],
              [
                3,
                58.21,
                58.21,
                58.065,
                58.07,
                11493.0,
                "VERIFIED_BAR"
              ],
              [
                4,
                58.07,
                58.095,
                58.01,
                58.01,
                9725.0,
                "VERIFIED_BAR"
              ],
              [
                5,
                58.03,
                58.09,
                58.03,
                58.03,
                7536.0,
                "VERIFIED_BAR"
              ],
              [
                6,
                58.06,
                58.075,
                58.03,
                58.06,
                5274.0,
                "VERIFIED_BAR"
              ],
              [
                7,
                58.07,
                58.11,
                58.03,
                58.03,
                10942.0,
                "VERIFIED_BAR"
              ],
              [
                8,
                58.01,
                58.14,
                57.99,
                58.13,
                12879.0,
                "VERIFIED_BAR"
              ],
              [
                9,
                58.135,
                58.265,
                58.12,
                58.195,
                23601.0,
                "VERIFIED_BAR"
              ]
            ],
            "columns": [
              "minute_offset",
              "open",
              "high",
              "low",
              "close",
              "volume",
              "coverage"
            ],
            "feed": "iex",
            "window_end": "2026-11-23T19:48:00+00:00",
            "window_start": "2026-11-23T19:38:00+00:00",
            "windows": {
              "10m": {
                "close": 58.195,
                "open": 58.085,
                "range_bps": 47.34440906,
                "return": 0.001893776362,
                "status": "OK",
                "volume": 108185.0
              },
              "5m": {
                "close": 58.195,
                "open": 58.03,
                "range_bps": 47.38928141,
                "return": 0.002843356884,
                "status": "OK",
                "volume": 60232.0
              }
            }
          },
          "version": "1.b12384d7"
        },
        "recent_range_bps_10m": {
          "age_s": 3.237416,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "d95f78a421e15f1def875d6076aa3e3e1dcdb24fd6935e7dd4eeb44e2b5090ea",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:48:00+00:00",
            "window_start": "2026-11-23T19:38:00+00:00"
          },
          "record_hash": "47e5ee69cd3dbc225d14c66d47392d0e2f9f5e097dc77d9bc6f9581d575dbd7e",
          "status": "OK",
          "v": 47.34440906,
          "version": "1.b7dd2e6e"
        },
        "recent_range_bps_5m": {
          "age_s": 3.237416,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "d95f78a421e15f1def875d6076aa3e3e1dcdb24fd6935e7dd4eeb44e2b5090ea",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:48:00+00:00",
            "window_start": "2026-11-23T19:38:00+00:00"
          },
          "record_hash": "108fee22ecc18a6047676ddce1583fcdba478376343b8daa551dea096a5f180d",
          "status": "OK",
          "v": 47.38928141,
          "version": "1.860a2856"
        },
        "recent_return_10m": {
          "age_s": 3.237416,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "d95f78a421e15f1def875d6076aa3e3e1dcdb24fd6935e7dd4eeb44e2b5090ea",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:48:00+00:00",
            "window_start": "2026-11-23T19:38:00+00:00"
          },
          "record_hash": "509d6669cf644bb60a847eba6c381cd5548e5fff4e99aa8c7ce9f6e8b90a61df",
          "status": "OK",
          "v": 0.001893776362,
          "version": "1.03c04840"
        },
        "recent_return_5m": {
          "age_s": 3.237416,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "d95f78a421e15f1def875d6076aa3e3e1dcdb24fd6935e7dd4eeb44e2b5090ea",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:48:00+00:00",
            "window_start": "2026-11-23T19:38:00+00:00"
          },
          "record_hash": "2cfd8ab761646a532a6ee4b0a51a6ef26cfada382c4dd8d67c8475449604b93a",
          "status": "OK",
          "v": 0.002843356884,
          "version": "1.a9090b46"
        },
        "recent_volume_10m": {
          "age_s": 3.237416,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "d95f78a421e15f1def875d6076aa3e3e1dcdb24fd6935e7dd4eeb44e2b5090ea",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:48:00+00:00",
            "window_start": "2026-11-23T19:38:00+00:00"
          },
          "record_hash": "0982dbd0173ef71d3e94b805945420c2b9d9f4d767d26cb5217a8dea39043d1e",
          "status": "OK",
          "v": 108185.0,
          "version": "1.891ed5cd"
        },
        "recent_volume_5m": {
          "age_s": 3.237416,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "d95f78a421e15f1def875d6076aa3e3e1dcdb24fd6935e7dd4eeb44e2b5090ea",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:48:00+00:00",
            "window_start": "2026-11-23T19:38:00+00:00"
          },
          "record_hash": "87473261f9bf18efe7c71c4a44baf8cbf2fde631f8f3fc66c49a0ccc9a6a342a",
          "status": "OK",
          "v": 60232.0,
          "version": "1.c7331f02"
        },
        "relstr_spy_60m": {
          "age_s": 183.237416,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "836e90f6753bb59428ce48c07663954006350f8b35859a28a43941855d4cdb56",
          "status": "OK",
          "v": 0.001991459627,
          "version": "1.c04b464c"
        },
        "ret_15m": {
          "age_s": 183.237416,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "793205b42417a1bf548206c5008d6f938c7ec932c27840c05480580cf405b29f",
          "status": "OK",
          "v": -0.002827278958,
          "version": "1.3fa23ddd"
        },
        "ret_1d": {
          "age_s": 183.237416,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "4871f8f39f073d45e17d3d6f5ca60a8fec098c3c382779b9f1d17c4eff156f1b",
          "status": "OK",
          "v": -0.07827648115,
          "version": "1.b77eca69"
        },
        "ret_20d": {
          "age_s": 254883.2374,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "c89eca0e545e370a2b5106418f52c2c97be259b8d9a271ffd1a96adbaa2aca0a",
          "status": "MISSING",
          "v": null,
          "version": "1.7d1f1942"
        },
        "ret_5d": {
          "age_s": 254883.2374,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "05a741e625955a85a438ad18773375028848616408999e7af63ece7accaed8b3",
          "status": "MISSING",
          "v": null,
          "version": "1.5d56db82"
        },
        "ret_5m": {
          "age_s": 183.237416,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "23eb8eb2d48b64451f4c198147f93db2cd145e341017336abcb2778e1d9a9bd6",
          "status": "OK",
          "v": 0.003189105327,
          "version": "1.c10a3b57"
        },
        "ret_60m": {
          "age_s": 183.237416,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "2fd9fcfa51ca874d4ff0d1dade1089f2c07f4acef6e9ac6ba31b69a8a1ccc90a",
          "status": "OK",
          "v": 0.00172131853,
          "version": "1.6c49ff8f"
        },
        "rsi14": {
          "age_s": 254883.2374,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "1e59b41cf19356a8afb2c1abc8da30ba54a3ae1c9ca6adec3645d67baab39a97",
          "status": "MISSING",
          "v": null,
          "version": "1.273a3a79"
        },
        "rsi14_15m": {
          "age_s": 183.237416,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "8e2405b48f61208fcc98491d12fb4cfef18c440cec8f1c795d9799094ef01d8d",
          "status": "OK",
          "v": 58.43968457,
          "version": "1.f0b8fdaf"
        },
        "rvol_60m": {
          "age_s": 183.237416,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "c540ccfe54591549a9b3ab81970770d24f749a741508c2479e246a1a4d16afc4",
          "status": "OK",
          "v": 0.01033512989,
          "version": "1.84c5ec7e"
        },
        "sellable_qty": {
          "age_s": 0.589194,
          "quality": {},
          "record_hash": "95a5ecd4570fb5e73f2d40abad984fa525f11967ad2153a225240d65842f54b5",
          "status": "OK",
          "v": "0",
          "version": "1.9cbf72e4"
        },
        "sma20": {
          "age_s": 254883.2374,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "15576f86a2842f5eb53a8c69129bc796ec2bb02d553d6eb692a0246444b821e2",
          "status": "MISSING",
          "v": null,
          "version": "1.80f8a078"
        },
        "sma50": {
          "age_s": 254883.2374,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "c77619dbf2bb36c37659503666953bdfa289b5ad53f8419d72ac47d490aa3455",
          "status": "MISSING",
          "v": null,
          "version": "1.3890c9d7"
        },
        "spread_bps": {
          "age_s": 1.422971,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "aad8d9d1ea96b70a62c71a6ffa11f62d9d0e606d6a162f28748698ac7a3fd575",
          "status": "OK",
          "v": 3.440564253,
          "version": "1.e2b080ab"
        },
        "trend_sma20_vs_sma50": {
          "age_s": 254883.2374,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "c3f4c96640a0fefa86efead1a20dc2a8c20470887509f9a64b8b123a7f0f6feb",
          "status": "MISSING",
          "v": null,
          "version": "1.84583425"
        },
        "unrealized_pnl_pct": {
          "age_s": 0.589194,
          "quality": {},
          "record_hash": "9bff1a15291a7957bf1fa5cf2e403749dc24c6543d0838f085f67dec7262a271",
          "status": "OK",
          "v": 0,
          "version": "1.7c530604"
        },
        "vol_regime_ratio": {
          "age_s": 183.237416,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "b2775b8df8a6deed3a7f799644bf357792f178e8f626e81563914e398b777860",
          "status": "OK",
          "v": 1.050439602,
          "version": "1.302e72c1"
        },
        "volume_z20": {
          "age_s": 254883.2374,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "acd6606915e0844ee2fa5f30507b576df69022855968e20bad1ec489ca7b84b7",
          "status": "MISSING",
          "v": null,
          "version": "1.970d159b"
        },
        "volz_tod_15m": {
          "age_s": 183.237416,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "00402ad410208e76d63fb60dc603ca6c5c3933ab4023869011a7814ed1722a9c",
          "status": "OK",
          "v": 0.2274907125,
          "version": "1.4315d547"
        },
        "vwap_dev_session": {
          "age_s": 183.237416,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "ae72669fd159250cd4508bee485464f531513ddd829a07e0c1fe888348cd2add",
          "status": "OK",
          "v": 0.002794667153,
          "version": "1.b41de1ff"
        }
      }
    },
    "validation_policy": "scored-15m-plus-2m-v1"
  },
  "council_mode": "PAPER_COUNCIL_SKEPTIC_OFF",
  "chair": {
    "note": "Prearbiter blocks entry (score 0.45 < threshold 0.5); no position to exit; thus no action.",
    "role": "CHAIR",
    "run_id": "df35ffe1-f8a1-51e9-b5c0-a54bac834872",
    "candidates": [],
    "schema_version": 2
  },
  "skeptic_audit": {
    "attempts": 0,
    "skip_reason": "DISABLED_BY_OPERATOR"
  },
  "role_outputs": [
    {
      "role": "CHAIR",
      "status": "OK",
      "response": "{\n  \"schema_version\": 2,\n  \"run_id\": \"df35ffe1-f8a1-51e9-b5c0-a54bac834872\",\n  \"role\": \"CHAIR\",\n  \"candidates\": [],\n  \"note\": \"Prearbiter blocks entry (score 0.45 < threshold 0.5); no position to exit; thus no action.\"\n}",
      "error": null
    },
    {
      "role": "LIQUIDITY",
      "status": "FALLBACK_CONTRACT",
      "response": null,
      "error": "LLMContractError: provider generated schema-invalid JSON: Error code: 400 - max completion tokens reached before generating a valid document: the output was truncated to fit max_completion_tokens and is missing required content. Increase max_completion_tokens. See 'failed_generation' for the truncated output. Error: jsonschema: '' does not validate with /required: missing properties: 'schema_version', 'run_id', 'source', 'data_confidence', 'role', 'symbols'"
    },
    {
      "role": "PORTFOLIO",
      "status": "OK",
      "response": "{\"data_confidence\": \"LOW\", \"role\": \"PORTFOLIO\", \"run_id\": \"df35ffe1-f8a1-51e9-b5c0-a54bac834872\", \"schema_version\": 2, \"source\": \"code\", \"symbols\": [{\"evidence\": [{\"band\": \"ZERO\", \"path\": \"symbols.INTC.position_qty\"}, {\"band\": \"POSITIVE\", \"path\": \"portfolio.equity\"}, {\"band\": \"POSITIVE\", \"path\": \"portfolio.buying_power\"}, {\"band\": \"POSITIVE\", \"path\": \"portfolio.aggregate_headroom_usd\"}], \"gate\": {\"reasons\": [], \"size_multiplier\": 1.0, \"state\": \"PASS\"}, \"note\": \"\", \"symbol\": \"INTC\"}]}",
      "error": null
    },
    {
      "role": "REGIME",
      "status": "OK",
      "response": "{\"schema_version\":2,\"run_id\":\"df35ffe1-f8a1-51e9-b5c0-a54bac834872\",\"source\":\"code\",\"data_confidence\":\"HIGH\",\"risk_appetite\":\"NEUTRAL\",\"role\":\"REGIME\",\"symbols\":[{\"symbol\":\"INTC\",\"note\":\"Strong EMA gap, positive recent returns, UPTREND regime\",\"evidence\":[{\"path\":\"market.regime_label\",\"band\":\"UPTREND\"},{\"path\":\"market.spy_vol_regime_ratio\",\"band\":\"POSITIVE\"},{\"path\":\"symbols.INTC.ema_gap_bps_15m\",\"band\":\"POS_STRONG\"},{\"path\":\"symbols.INTC.recent_return_5m\",\"band\":\"POS\"},{\"path\":\"symbols.INTC.recent_return_10m\",\"band\":\"POS\"}]}]}",
      "error": null
    },
    {
      "role": "TECHNICAL",
      "status": "OK",
      "response": "{\"data_confidence\": \"HIGH\", \"role\": \"TECHNICAL\", \"run_id\": \"df35ffe1-f8a1-51e9-b5c0-a54bac834872\", \"schema_version\": 2, \"source\": \"code\", \"symbols\": [{\"evidence\": [{\"band\": \"POS_STRONG\", \"path\": \"symbols.INTC.ema_gap_bps_15m\"}, {\"band\": \"FIRM\", \"path\": \"symbols.INTC.rsi14_15m\"}, {\"band\": \"POS\", \"path\": \"symbols.INTC.recent_return_5m\"}, {\"band\": \"POSITIVE\", \"path\": \"symbols.INTC.recent_return_10m\"}, {\"band\": \"NEGATIVE\", \"path\": \"symbols.INTC.macd_hist_15m\"}, {\"band\": \"ALL\", \"path\": \"market.regime_label\"}], \"note\": \"Bullish momentum but short time to close and negative MACD\", \"signal\": {\"confidence\": 0.65, \"horizon\": \"INTRADAY\", \"score\": 0.45, \"state\": \"SIGNAL\"}, \"symbol\": \"INTC\"}]}",
      "error": null
    }
  ],
  "reason_codes": [
    "NO_SIGNAL_ABOVE_THRESHOLD"
  ],
  "notes": [
    "evidence_pack:07cff372deeee685be34b6ea7a49d1f353e7118283752d7191153f7d8bc171af",
    "council_run:df35ffe1-f8a1-51e9-b5c0-a54bac834872",
    "NO_SIGNAL_ABOVE_THRESHOLD"
  ],
  "error": null,
  "proposals_and_risk": []
}
```

</details>

### 14:49:09 ET · DECIDED_HOLD

<details>
<summary>Recorded decision evidence</summary>

```json
{
  "decision_id": "cba898c2-2b32-55e2-a57f-3391d08947e3",
  "inputs": {
    "as_of": "2026-11-23T19:49:04.797124Z",
    "regime": {
      "label": "uptrend"
    },
    "account": {
      "cash": 99803.06,
      "equity": 99803.06,
      "status": "ACTIVE",
      "account_id": "PAPER_ACCOUNT",
      "last_equity": 99803.39,
      "buying_power": 399212.24
    },
    "positions": [],
    "symbols": {
      "INTC": {
        "mid": 58.05,
        "rsi14": null,
        "ret_1d": -0.0783,
        "ret_5d": null,
        "ret_20d": null,
        "atr14_pct": null,
        "price_vs_sma20": null,
        "trend_sma20_vs_sma50": null
      }
    }
  },
  "feature_evidence": {
    "account_ref": "PAPER_ACCOUNT",
    "as_of": "2026-11-23T19:49:04.797124+00:00",
    "availability": {
      "account": "fresh",
      "bars": "fresh",
      "calendar": "fresh",
      "news": "fresh",
      "ok_fraction_core_features": 1.0,
      "quotes": "fresh"
    },
    "bands_hash": "810517c6e124c7ebc23ca0ebce7ef7ba7cc66b30bc21cacc66c1a221174255d4",
    "feasibility": {
      "INTC": {
        "can_buy": true,
        "can_buy_reasons": [],
        "can_sell": false,
        "can_sell_reasons": [
          "NO_SELLABLE_INVENTORY"
        ],
        "entry_window_open": true,
        "entry_window_reason": "",
        "held_qty": "0.0",
        "max_new_notional_usd": "2000.0",
        "sellable_qty": "0"
      }
    },
    "feature_slot": {
      "candles": {
        "INTC|2026-11-23T19:34:00+00:00": "564e3a869b90c07bc6f4dc36fc9a4642620456c6cac5272aff6455bd272177b1",
        "INTC|2026-11-23T19:35:00+00:00": "8c40460eb8f86125bf2228c6e0b5478931f3e3a91a013bd23caa1bb828639442",
        "INTC|2026-11-23T19:36:00+00:00": "9cb732a5a05f88fcae5944f0121aac8aaa2713bd234d104b87ddb513e8886ae9",
        "INTC|2026-11-23T19:37:00+00:00": "9d5b09f82117334dcc0f33b8c32ad04009545b4670f26997f04929a89d44df93",
        "INTC|2026-11-23T19:38:00+00:00": "e98c98af48936fd32ec6ad72041fcbfa1de8511a2b8911c69eabcd4ab7117e18",
        "INTC|2026-11-23T19:39:00+00:00": "422314eba37616c0546eed1ed8aa018f6b54ce6bec687378c7704d9ca2065248",
        "INTC|2026-11-23T19:40:00+00:00": "70e0d8b0a63b3723514998b8205402a930375f59ca5308b2f48f6dbab08cd617",
        "INTC|2026-11-23T19:41:00+00:00": "4510c4c83faf5f5878d401794d4b7bed12120a3527e7efc68be6e7a94d44c40b",
        "INTC|2026-11-23T19:42:00+00:00": "98067d1cfbe2cf62a97c2f9a655f0cf4470e9f8fb2391eb0463aff7d674dad4b",
        "INTC|2026-11-23T19:43:00+00:00": "c8d1f80659f571bf3eb64a17b9935be4ce7a092a55afd0608b149b1e717e9011",
        "INTC|2026-11-23T19:44:00+00:00": "c1aa4b559490e25f881fb40af919d8644954d00315de5f007556c6e7791a0b28",
        "INTC|2026-11-23T19:45:00+00:00": "34a1b438e39db05694f921c5baec9ae6582c0220846c45eb8506fabad543f270",
        "INTC|2026-11-23T19:46:00+00:00": "805d43a04e130aa788c4098fa1275ef209d434dbdf234b2dbc11f9444444a83b",
        "INTC|2026-11-23T19:47:00+00:00": "877bc5250b1ff660d6061932b5651c5824af3f63b8d90833befef35f081fc349",
        "INTC|2026-11-23T19:48:00+00:00": "99e9788d15d3e4f4fc6f2bfc5a0ac1bc5b6622131849ffa765924063f0444199",
        "SPY|2026-11-23T19:34:00+00:00": "205774036f40cb4bc8e44df4d46ef150bd7d25dedeb8a897455bddc1dd4763d8",
        "SPY|2026-11-23T19:35:00+00:00": "a3f33f928527ca6cd947868e44e270cfe45857f8acf9296afd6811bf7c66a716",
        "SPY|2026-11-23T19:36:00+00:00": "20f2610f9083c52c53c44110cf31c15486c3658b74baf10c77427c7f1643e451",
        "SPY|2026-11-23T19:37:00+00:00": "cfc075a20afd9004c6a54e55e02de60aa1ac6fab559ca2bc363b4083a5a7b0e8",
        "SPY|2026-11-23T19:38:00+00:00": "8ac7b4d0dc16f15a1b48e3576c48557a2cf3e5e01e9dbd56ec12e4206987e786",
        "SPY|2026-11-23T19:39:00+00:00": "38712a0709a4972b95a52f42b45fd54896d71cc49ce48651c65445f1a42bf62f",
        "SPY|2026-11-23T19:40:00+00:00": "e49f4baca7c7583df76c009735c11448f1023f1415b68e390409997276db3480",
        "SPY|2026-11-23T19:41:00+00:00": "0dccbf44a642c7d605f69cb3858d90923162c6c2b93f66b9555d77776438a183",
        "SPY|2026-11-23T19:42:00+00:00": "88269dcad14d8b8d3584bb870bfc6f5eed07f56a971f9ad7e1037bfff28a3780",
        "SPY|2026-11-23T19:43:00+00:00": "a4aebaa6965c7c246c1610c4eff9a05d061eff2cadc3940774ca5ab43368ca06",
        "SPY|2026-11-23T19:44:00+00:00": "b91459d6c5ec4fb98cb4404bbe1cd7357fe920ab60a2e98579d2b6fb1626730d",
        "SPY|2026-11-23T19:45:00+00:00": "467c27fb5d5f1da7405a638366403833df31cfdd7aae5abf3fe2d4bf9f1de532",
        "SPY|2026-11-23T19:46:00+00:00": "a7668e87604b88bc72c1eadf5d9870964634f7b5e5b13baa18713dfa791d317c",
        "SPY|2026-11-23T19:47:00+00:00": "4bed66e17e5a42bb1a8cd2145b47115c4782478e39ddcb5375ca07eda3f81667",
        "SPY|2026-11-23T19:48:00+00:00": "6c3ed3ca6efe21639b18c48e926b44d18aa2768d77db9a031a04415e2ae047db"
      },
      "close": "2026-11-23T19:49:00+00:00",
      "feed": "iex",
      "indicator_close": "2026-11-23T19:45:00+00:00",
      "indicator_input_hashes": {
        "INTC": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
        "SPY": "68be2784fe1097306ec89b5433c1c0b0393b316ceebc03170624a4214da8ac5c"
      },
      "provisional": true,
      "records": {
        "market:market:breadth_above_ema21": "d7e2f70fedf1d18806a57fa4210d951ce450efccdd03a1fa716baff26d0f59e9",
        "market:market:regime_label": "b5f7eda754fe89980a8ade83e3496e26768374e4bbb5fca559b77ed06e580f14",
        "market:market:spy_ema_gap_bps_15m": "5885f7d1170e4539d33b130275da00b6751841c47609429095ed1e27403a7ec2",
        "market:market:spy_ret_60m": "6ee17662a23a52719d59ed41112f7edf73573824d58f0e6886917ebd766257cc",
        "market:market:spy_vol_regime_ratio": "be9c29e0d9cb35e80c9e9907f08ee3033cdedd5e736a3c1ea530cd69f6435d5f",
        "symbol:INTC:adv_usd_20d": "b9b2c8cd47063244741a0be3a99b852571258b975af9e1831bf9c22ac86c817d",
        "symbol:INTC:atr14_15m": "6f731751bfa53150c4b34c9f00c97b6e20fc9879a19350f0ce7cbe19a7070a61",
        "symbol:INTC:atr14_1d": "7109941c8f13c27be9954427260fd23488765da0017ae6e7268c52c67c282e0d",
        "symbol:INTC:atr14_pct": "72b22515a9b698de8e221ba3601ca48bfe5aa847f96eb780cd201d7da6e1b10b",
        "symbol:INTC:dist_hi_atr": "c05edf8680787157a07bed887ba2ec8402005880814012010c4195229234d324",
        "symbol:INTC:dist_lo_atr": "94cfd4d6d5e0080647a36203f7b3f155986dfec37cf9d5a3adbbdc5e99db95a6",
        "symbol:INTC:ema21_15m": "026dc43aa182328e915e6f6d23296bedca2f3d61e29ad492593fd2b16c1f2c9c",
        "symbol:INTC:ema9_15m": "779c29eadfec6fe54e83478754f967d3444f194d88d34349bf014707a7b14100",
        "symbol:INTC:ema_gap_bps_15m": "2d80bf72eea509fb31fba6a2c3b863d8d8dc686f8d007db33fe90cf4a50e5145",
        "symbol:INTC:gap_open_pct": "22372f1618bb0042d504687f06dc178f5d5531095633eddeaf4bcfe97a2ded36",
        "symbol:INTC:intraday_ret_1h": "584b190315139eaa5cf532afd4584686eee1ec8a960635264ed6e8e8c24aeec5",
        "symbol:INTC:intraday_setup_1m": "a54bb34966c2c839b341df810ac4f76f795686e0d89acc343f2834aa47d0bfea",
        "symbol:INTC:last_close": "d19401a83eca33beec8f4dc4c9fd9de4a732eca37d9f9287a4931e7ba85850f1",
        "symbol:INTC:macd_hist_15m": "ffc4ec65b3c48fbd631f09dccfb6d59e271d94c9ffd76307010798940056e67d",
        "symbol:INTC:price_vs_sma20": "0d79ec3c1b357a5011464af77c39b3fcad072140f1af42e8fc4caaaa2d603acd",
        "symbol:INTC:recent_price_10m": "f2078125dae138d4f48450fb0a61eb8c906d4f67a24532499ef6e1afac85b053",
        "symbol:INTC:recent_range_bps_10m": "a9a863b8e7c7721a134826329438580ee4b10eb473ef825e01412b98a4419950",
        "symbol:INTC:recent_range_bps_5m": "967749e9329dd0e792c51371ab6a7f25969e108ed0f4bb10f415cd48d5d02ae9",
        "symbol:INTC:recent_return_10m": "bd9e864b33e37da98410ee009a0f9b3966a83d3aeda9f580cf17a5186b0c45d9",
        "symbol:INTC:recent_return_5m": "46ae9ba58224e9cedd1ce8c32c81adf3b8f3d0a956513977e5df2dcd87f4e5a8",
        "symbol:INTC:recent_volume_10m": "21654cdb77c6bcec3ed223cb43bd3f7c802ae3654ee5b55d7feaccf71f670f94",
        "symbol:INTC:recent_volume_5m": "82f60142d90a579c5e2752053d7788b8a702922d0217c10ed18d651efe996635",
        "symbol:INTC:relstr_spy_60m": "09e87f1462439b3dd08fb76c6c61b88838390aec61ba82d2acb78930e6c29f19",
        "symbol:INTC:ret_15m": "a6399cf9b7b023b247750550d782a8051c0661ae98cf4e902c9a48e919261937",
        "symbol:INTC:ret_1d": "4871f8f39f073d45e17d3d6f5ca60a8fec098c3c382779b9f1d17c4eff156f1b",
        "symbol:INTC:ret_20d": "c89eca0e545e370a2b5106418f52c2c97be259b8d9a271ffd1a96adbaa2aca0a",
        "symbol:INTC:ret_5d": "05a741e625955a85a438ad18773375028848616408999e7af63ece7accaed8b3",
        "symbol:INTC:ret_5m": "a40abbfcf292dd9af1af383805c0563780e6267ec3328a079eb61405ea935d79",
        "symbol:INTC:ret_60m": "c8527e307f4c85659732c4d03b51b3df98373bf2e30c973873c06e701ff5ebb2",
        "symbol:INTC:rsi14": "1e59b41cf19356a8afb2c1abc8da30ba54a3ae1c9ca6adec3645d67baab39a97",
        "symbol:INTC:rsi14_15m": "8e2405b48f61208fcc98491d12fb4cfef18c440cec8f1c795d9799094ef01d8d",
        "symbol:INTC:rvol_60m": "5f13bffae65d287c331ca30abdf7fec7e16b331f2bc6deafe5d04236711a6b65",
        "symbol:INTC:sma20": "15576f86a2842f5eb53a8c69129bc796ec2bb02d553d6eb692a0246444b821e2",
        "symbol:INTC:sma50": "c77619dbf2bb36c37659503666953bdfa289b5ad53f8419d72ac47d490aa3455",
        "symbol:INTC:trend_sma20_vs_sma50": "c3f4c96640a0fefa86efead1a20dc2a8c20470887509f9a64b8b123a7f0f6feb",
        "symbol:INTC:vol_regime_ratio": "d90ece8f8b57a33c23adac7171c2d37933aae6b084d02c799c3735b650ef67ed",
        "symbol:INTC:volume_z20": "acd6606915e0844ee2fa5f30507b576df69022855968e20bad1ec489ca7b84b7",
        "symbol:INTC:volz_tod_15m": "00402ad410208e76d63fb60dc603ca6c5c3933ab4023869011a7814ed1722a9c",
        "symbol:INTC:vwap_dev_session": "42c82f02e58dec9718ee8fac543a93bc2b675d9694903f00f4a9de46d3f1fca6",
        "symbol:SPY:adv_usd_20d": "92e94f829df49f4b3a8d0be7612b000e92190d5356f55e566f04069ca7b9ffd5",
        "symbol:SPY:atr14_15m": "7ab448ef9d85396282151eac59236f9553a486b5c77591049f30866a0df20c74",
        "symbol:SPY:atr14_1d": "3cac187afe8b3f12d7d3b3b86986d403d549ebe59a7ccfaa10a213aaea0d6f29",
        "symbol:SPY:atr14_pct": "86a49f6a2b7c51bced8c4109a9b641fd3430da5d9872f600c092cec75526d214",
        "symbol:SPY:dist_hi_atr": "a8f218adc7b76cac29f9116a1bc9465df07907120dedcf2de00f7be125cecdf3",
        "symbol:SPY:dist_lo_atr": "0308cbc78594b5f957f9be68f11cd5eda0d61759b4a4bad4359f8f29b44c753e",
        "symbol:SPY:ema21_15m": "e101df90a64d088f78547e381107b8db83b2541409047168500bf08d4caa4b43",
        "symbol:SPY:ema9_15m": "d9a6929dcd2aa029a0657e3b23036ea5c8e549c3e28f704d22c59d9141f45d16",
        "symbol:SPY:ema_gap_bps_15m": "12f402c62d8c646eb7b75bb92bec226e49110827a04064a50b8a1e5b881fc789",
        "symbol:SPY:gap_open_pct": "1c9616a65f2f013255300b42e56d88ac7a725e105e6f59b39d79e458ad29184e",
        "symbol:SPY:intraday_ret_1h": "4a3cbce2b9dcc1b99d6875d1dfcc341ba613acfd2d05e42ab8e2dd8730e5c8b3",
        "symbol:SPY:intraday_setup_1m": "0627441d7c59e121c55a10a27cd4c5f4049c6c7b576f5dbe22d35a5efa53f80f",
        "symbol:SPY:last_close": "caf596deca80d26016ad4208908f5e9f946155af82bcf05ef2276748182b2361",
        "symbol:SPY:macd_hist_15m": "7c1f84aa5b3c914a24e8512883539348c328fedf77f1ca8fddef3c9428311b8a",
        "symbol:SPY:price_vs_sma20": "963d8268f25c4849a1b268733b11edd2005fe4a8c767d1439d8478255d5a22c9",
        "symbol:SPY:recent_price_10m": "ff700df7c3245b2858eb7c65f0b91ca76db0f2d336c304893c34ca2ba8c57c4d",
        "symbol:SPY:recent_range_bps_10m": "330c69bcfe4cf62916f4e2f75a489327ba57b427a7f6bb898bed94c932c60ebe",
        "symbol:SPY:recent_range_bps_5m": "c3696bebb2ca4acf0932e9ada0b232daf8ab80bd19f9c02a6ef66d9ce0d6e2b1",
        "symbol:SPY:recent_return_10m": "220fcd224cfed97047c513ff73f28d5c8ec6c842013c4d38eaa077503cf7ccac",
        "symbol:SPY:recent_return_5m": "3912eb507d689974ae3c06b804d04fb5dc09efc616a5cf95c32cc92d8c149f50",
        "symbol:SPY:recent_volume_10m": "5a5c9a0d1a225b00f4b95e364e72598b493d58451cc2df4caf4058e5721e469d",
        "symbol:SPY:recent_volume_5m": "94f7fa13afb54a72d44025cf8421afe0847da0fe730cdc4d7e4fd0c28501b357",
        "symbol:SPY:relstr_spy_60m": "8192ee3c1e096d3220e21bd96547302036aad20b1f8b2a88d06eb43fca3d16bd",
        "symbol:SPY:ret_15m": "267d94cdf8cec43e5340c48ea2b3e22e536ccc56a136f5fa936988d9ab81645e",
        "symbol:SPY:ret_1d": "aab94a7dafcf360313d949fc12ced963ccb5a8b3ef27866b2b930d2d5817c533",
        "symbol:SPY:ret_20d": "5cb42b7c179c74bdcedf0dbf4ce0ee12832341fe24b75d306dccc8cc03e792c3",
        "symbol:SPY:ret_5d": "7c31dada2f0a36e24d03e89b66cb73d377f3c298c10867a1be2b05be76be6a0c",
        "symbol:SPY:ret_5m": "00c399d41f7b68846ed5414e3a01b50db28958e497171a81478cc4fb9e6524c9",
        "symbol:SPY:ret_60m": "c22e2be55bd8d8b0d7206aef0cade33c940672607adac3acb52aba97a5ae9c67",
        "symbol:SPY:rsi14": "ee11c2b462281f9fc927ac380b6bb2557ff2e158729fe2f17aa91d152eb3fb9f",
        "symbol:SPY:rsi14_15m": "7a2d8a98c627154aeccdc9a68b885c12330bcb82ce58cddb4d0a2f4136033fc0",
        "symbol:SPY:rvol_60m": "2b57f91642d64d30c9375748fd69a34a18c2ae3982171bca11d6cf6bac5871d6",
        "symbol:SPY:sma20": "1b30496ca2845ccd7a79462c221d840260e1c0361b7feb9dedbc5dc30bd4b2a5",
        "symbol:SPY:sma50": "94c11d37cff9b64498753612d4be2b84f39d1931bd55ec9e573a0c8697ceb72b",
        "symbol:SPY:trend_sma20_vs_sma50": "8aee1d285ca5a8e44083c58d0fad60754235fda2855c6ac02c9796bc41cff8bc",
        "symbol:SPY:vol_regime_ratio": "8f73e7ee0190c4ec6ff181cddbc1a03ca32a1cb40ee1f13963ce43a564264b74",
        "symbol:SPY:volume_z20": "26f74a49cf931c478f404ef3e6a0850c2e214cc588216f87e068535e16f86e9f",
        "symbol:SPY:volz_tod_15m": "29640670f4a0587e4e43a5ad4cd8d40a485c1b2537f64212b1cb41ffc2d19792",
        "symbol:SPY:vwap_dev_session": "1789a7d79ec6345fac0e6f0f10c14b4285817270374132d9640a445370338b62"
      },
      "symbols": [
        "INTC",
        "SPY"
      ]
    },
    "horizons": {
      "INTC": {
        "10m": {
          "age_s": 4.797124,
          "last_bar_end": "2026-11-23T19:49:00+00:00",
          "status": "OK"
        },
        "15m": {
          "age_s": 244.797124,
          "last_bar_end": "2026-11-23T19:45:00+00:00",
          "status": "OK"
        },
        "5m": {
          "age_s": 4.797124,
          "last_bar_end": "2026-11-23T19:49:00+00:00",
          "status": "OK"
        },
        "60m": {
          "age_s": 244.797124,
          "last_bar_end": "2026-11-23T19:45:00+00:00",
          "status": "OK"
        },
        "horizon_conflict": false
      }
    },
    "market": {
      "breadth_above_ema21": {
        "age_s": 244.797124,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "d7e2f70fedf1d18806a57fa4210d951ce450efccdd03a1fa716baff26d0f59e9",
        "status": "OK",
        "v": 1.0,
        "version": "1.1dfe664d"
      },
      "minutes_to_close": {
        "age_s": 0.445888,
        "quality": {},
        "record_hash": "7d644d3f62d573076a7c6f333c9a3b382ee61cd1ab1e62c732313d813d26b0a0",
        "status": "OK",
        "v": 70.9274794,
        "version": "1.e79b1ead"
      },
      "regime_label": {
        "age_s": 244.797124,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "b5f7eda754fe89980a8ade83e3496e26768374e4bbb5fca559b77ed06e580f14",
        "status": "OK",
        "v": "UPTREND",
        "version": "1.f8b361d7"
      },
      "session_phase": {
        "age_s": 0.445888,
        "quality": {},
        "record_hash": "cee0c4c79acfbcd1c330fb47cf8ea31b4c782f777540dce8ff8fe9a692e5e2bc",
        "status": "OK",
        "v": "NORMAL",
        "version": "1.91f88fe8"
      },
      "spy_ema_gap_bps_15m": {
        "age_s": 244.797124,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "5885f7d1170e4539d33b130275da00b6751841c47609429095ed1e27403a7ec2",
        "status": "OK",
        "v": 37.89644347,
        "version": "1.fda7da7a"
      },
      "spy_ret_60m": {
        "age_s": 244.797124,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "6ee17662a23a52719d59ed41112f7edf73573824d58f0e6886917ebd766257cc",
        "status": "OK",
        "v": -0.001565096953,
        "version": "1.9feddbd1"
      },
      "spy_vol_regime_ratio": {
        "age_s": 244.797124,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "be9c29e0d9cb35e80c9e9907f08ee3033cdedd5e736a3c1ea530cd69f6435d5f",
        "status": "OK",
        "v": 1.46753597,
        "version": "1.3b7257aa"
      }
    },
    "meta": {
      "news": {
        "INTC": {
          "effective_weight": 0,
          "in_window": 0,
          "newest_age_min": 1787.629952,
          "policy": "48h retained; per-article decay and minimum relevance; 4h count is descriptive",
          "poller_last_ok_age_s": 10.316771,
          "retrieved": 1,
          "selected": 0,
          "state": "QUIET",
          "window_min": 240
        }
      }
    },
    "news_blob_hash": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
    "news_context_blob_hash": "ef023692226f6319baf7f6429f023deb1a988f59c953b103e7a5f425a6a5d062",
    "portfolio": {
      "aggregate_cap_usd": {
        "age_s": 0.445888,
        "quality": {},
        "record_hash": "2d3abfbc2835f4136009d4f47ac33723eea80ddfbd8539ac93c4dddf2739c95a",
        "status": "OK",
        "v": "49901.530",
        "version": "1.5b3d1daf"
      },
      "aggregate_headroom_usd": {
        "age_s": 0.445888,
        "quality": {},
        "record_hash": "b5d630c92f15ac640e17a6dcd0afb6ab97ad1562924f7e350c5bf1c183a5bf4d",
        "status": "OK",
        "v": "49901.530",
        "version": "1.7f894fff"
      },
      "buying_power": {
        "age_s": 0.445888,
        "quality": {},
        "record_hash": "2fd39229b41a0b8f3612a9476bfdbccf9a2374b9d186a35265934b8a8049b990",
        "status": "OK",
        "v": "399212.24",
        "version": "1.74948dec"
      },
      "cash": {
        "age_s": 0.445888,
        "quality": {},
        "record_hash": "34007edb995479319c67e4e4f4dd800296a96cbd1148fdd55553e83a016306e7",
        "status": "OK",
        "v": "99803.06",
        "version": "1.b067f5e3"
      },
      "day_pnl_pct": {
        "age_s": 0.445888,
        "quality": {},
        "record_hash": "f36d4bb1313c2e8e7cb758526cbbd7457564b7a91a6d08ae29d45db049e3ae4d",
        "status": "OK",
        "v": "-0.0003306500911441986088849300",
        "version": "1.35e81852"
      },
      "drawdown_pct": {
        "age_s": 0.445888,
        "quality": {},
        "record_hash": "1c3861d22f62956d7cae491fed853bcb84962aee87c7caf1e598d1d64047810d",
        "status": "MISSING",
        "v": null,
        "version": "1.19aac9ba"
      },
      "equity": {
        "age_s": 0.445888,
        "quality": {},
        "record_hash": "7eb66df7ea87bbd57698771ade1f4293493050ad3382793ad5b73ffaad938e4e",
        "status": "OK",
        "v": "99803.06",
        "version": "1.a2192616"
      },
      "gross_exposure_pct": {
        "age_s": 0.445888,
        "quality": {},
        "record_hash": "387594cf1d6e8832201838e81510bb88dbc60bfa5c792572bb9a4fbf6b76bc7c",
        "status": "OK",
        "v": "0E+2",
        "version": "1.b82cc518"
      },
      "gross_exposure_usd": {
        "age_s": 0.445888,
        "quality": {},
        "record_hash": "d57d24e69c195b1601b2747a372eb3f69874614a9c43c03bdb70e8a78ccc6d4a",
        "status": "OK",
        "v": "0",
        "version": "1.e4c8752b"
      },
      "last_reconcile_age_s": {
        "age_s": 0.445888,
        "quality": {},
        "record_hash": "6261988891f64931d7f35029f6f23b4fdca7324679d597b352e6145d5d153329",
        "status": "OK",
        "v": 0,
        "version": "1.5ed0382f"
      },
      "open_buy_notional_usd": {
        "age_s": 0.445888,
        "quality": {},
        "record_hash": "a32167165050fb766c1cfa639939131aae372fc9c97e90b3247fd2dba304942f",
        "status": "OK",
        "v": "0",
        "version": "1.0bd0ead1"
      },
      "open_orders": {
        "age_s": 0.445888,
        "quality": {},
        "record_hash": "d36e1a13ecb6d36169e4911a6e49ed3949a5a2e982e80a643a712a46349a514f",
        "status": "OK",
        "v": [],
        "version": "1.1cf37cbf"
      },
      "open_orders_count": {
        "age_s": 0.445888,
        "quality": {},
        "record_hash": "8fa1901b50b8844f7349cdc689350e59ad4dbba8319033cb06a3882ed6e4b3ea",
        "status": "OK",
        "v": 0,
        "version": "1.1db4227a"
      },
      "pending_reserved_usd": {
        "age_s": 0.445888,
        "quality": {},
        "record_hash": "929e697297325c1d1a7c9cbdd432117627dc260607f41341961b7c9afa0366dc",
        "status": "OK",
        "v": "0",
        "version": "1.1c3e9604"
      },
      "positions": {
        "age_s": 0.445888,
        "quality": {},
        "record_hash": "e58486b4e41634cc98bd4fe70b91b71c490d30beb30126ac9bc0b7d316370b4d",
        "status": "OK",
        "v": [],
        "version": "1.c3284657"
      }
    },
    "registry_hash": "0fd3271269748046863b2f0558e45e2c333bb352eccc9899b7ff42277c8386fc",
    "schema_version": 1,
    "symbols": {
      "INTC": {
        "adv_usd_20d": {
          "age_s": 254944.7971,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "b9b2c8cd47063244741a0be3a99b852571258b975af9e1831bf9c22ac86c817d",
          "status": "OK",
          "v": 304793568.9,
          "version": "1.04f5e91f"
        },
        "ask_px": {
          "age_s": 1.614743,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "da8e9d4eed6b86913025b740f6a9b0dae2143b1b8e3653f01419a5105efe7497",
          "status": "OK",
          "v": 58.06,
          "version": "1.d21cdd09"
        },
        "atr14_15m": {
          "age_s": 244.797124,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "6f731751bfa53150c4b34c9f00c97b6e20fc9879a19350f0ce7cbe19a7070a61",
          "status": "OK",
          "v": 0.7629598219,
          "version": "1.0cd14e73"
        },
        "atr14_1d": {
          "age_s": 254944.7971,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "7109941c8f13c27be9954427260fd23488765da0017ae6e7268c52c67c282e0d",
          "status": "MISSING",
          "v": null,
          "version": "1.65e38f4c"
        },
        "atr14_pct": {
          "age_s": 254944.7971,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "72b22515a9b698de8e221ba3601ca48bfe5aa847f96eb780cd201d7da6e1b10b",
          "status": "MISSING",
          "v": null,
          "version": "1.87450ee9"
        },
        "bid_px": {
          "age_s": 1.614743,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "9d6e1b48d4bd00f9c5ada944ef7ed527ddf92393669baa4653af73bd5b28dec1",
          "status": "OK",
          "v": 58.04,
          "version": "1.149628cd"
        },
        "dist_hi_atr": {
          "age_s": 244.797124,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "c05edf8680787157a07bed887ba2ec8402005880814012010c4195229234d324",
          "status": "OK",
          "v": -1.920153536,
          "version": "1.913ffc4a"
        },
        "dist_lo_atr": {
          "age_s": 244.797124,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "94cfd4d6d5e0080647a36203f7b3f155986dfec37cf9d5a3adbbdc5e99db95a6",
          "status": "OK",
          "v": 1.795638461,
          "version": "1.79ba4c70"
        },
        "ema21_15m": {
          "age_s": 244.797124,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "026dc43aa182328e915e6f6d23296bedca2f3d61e29ad492593fd2b16c1f2c9c",
          "status": "OK",
          "v": 57.40577599,
          "version": "1.bfcac61e"
        },
        "ema9_15m": {
          "age_s": 244.797124,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "779c29eadfec6fe54e83478754f967d3444f194d88d34349bf014707a7b14100",
          "status": "OK",
          "v": 58.09168398,
          "version": "1.81255de8"
        },
        "ema_gap_bps_15m": {
          "age_s": 244.797124,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "2d80bf72eea509fb31fba6a2c3b863d8d8dc686f8d007db33fe90cf4a50e5145",
          "status": "OK",
          "v": 119.4841427,
          "version": "1.d4519f3c"
        },
        "gap_open_pct": {
          "age_s": 244.797124,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "22372f1618bb0042d504687f06dc178f5d5531095633eddeaf4bcfe97a2ded36",
          "status": "MISSING",
          "v": null,
          "version": "1.27438d4d"
        },
        "halted": {
          "age_s": 0.445888,
          "quality": {},
          "record_hash": "0971d7d1705aa67d51aa92f373d99b1ed468883ce8c6d0b88fd5bdbd6b11a3e3",
          "status": "OK",
          "v": false,
          "version": "1.22c5cf87"
        },
        "held_minutes": {
          "age_s": 0.445888,
          "quality": {},
          "record_hash": "fe6b376b3867b4eb05f7781923ea437b51521845f23b13f3db69b33a954a13aa",
          "status": "MISSING",
          "v": null,
          "version": "1.de6ed6d3"
        },
        "intraday_ret_1h": {
          "age_s": 244.797124,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "584b190315139eaa5cf532afd4584686eee1ec8a960635264ed6e8e8c24aeec5",
          "status": "OK",
          "v": 0.001120786275,
          "version": "1.c3bb7751"
        },
        "intraday_setup_1m": {
          "age_s": 4.797124,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "2834a19f7acc19f89054c86ec1adeb668b0a15d6f7d4d68c5468f165111eb637",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:49:00+00:00",
            "window_start": "2026-11-23T19:39:00+00:00"
          },
          "record_hash": "a54bb34966c2c839b341df810ac4f76f795686e0d89acc343f2834aa47d0bfea",
          "status": "OK",
          "v": {
            "confirmation": "NONE",
            "pattern": "NONE",
            "prior_trend": "UP",
            "range_break": "INSIDE",
            "range_ceiling": 58.265,
            "range_floor": 57.99,
            "setup_minute": null,
            "volume_ratio": 1.5698
          },
          "version": "1.2a1f51e0"
        },
        "last_close": {
          "age_s": 254944.7971,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "d19401a83eca33beec8f4dc4c9fd9de4a732eca37d9f9287a4931e7ba85850f1",
          "status": "MISSING",
          "v": null,
          "version": "1.f2485fc2"
        },
        "luld_active": {
          "age_s": 0.445888,
          "quality": {},
          "record_hash": "f9ae8f3ee638dc8e6e7088d7783b931ac0df2e9917ef58deccd773df584f68b8",
          "status": "MISSING",
          "v": null,
          "version": "1.84a715b2"
        },
        "macd_hist_15m": {
          "age_s": 244.797124,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "ffc4ec65b3c48fbd631f09dccfb6d59e271d94c9ffd76307010798940056e67d",
          "status": "OK",
          "v": -0.07751173219,
          "version": "1.391617c8"
        },
        "mid_px": {
          "age_s": 1.614743,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "f068e345adc21b9423bbd99f05f612d7e21309f231a6a798748e23b37f3ca733",
          "status": "OK",
          "v": 58.05,
          "version": "1.d567a349"
        },
        "news_age_min_latest": {
          "age_s": 10.316771,
          "quality": {},
          "record_hash": "7c820d283b68109bc53ee0c31a59bb552c6c800fb722afc53b465d85eb4ca46c",
          "status": "MISSING",
          "v": null,
          "version": "1.d0f79dc8"
        },
        "news_confirmed": {
          "age_s": 0,
          "quality": {
            "source": "stored news and pinned price features"
          },
          "status": "OK",
          "v": false,
          "version": "news-confirmation-v2"
        },
        "news_count_1h": {
          "age_s": 10.316771,
          "quality": {},
          "record_hash": "24c6e8a2b3c8741597f8269da1db5ade0c57672edd0832376e7c5243826bd2f5",
          "status": "OK",
          "v": 0,
          "version": "1.0c9362fe"
        },
        "news_count_48h": {
          "age_s": 10.316771,
          "quality": {
            "as_of": "2026-11-23T19:49:04.797124+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 1,
          "version": "news-context-v2"
        },
        "news_count_4h": {
          "age_s": 10.316771,
          "quality": {
            "as_of": "2026-11-23T19:49:04.797124+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 0,
          "version": "news-context-v2"
        },
        "news_effective_sentiment": {
          "age_s": 0,
          "quality": {
            "selected": 0,
            "source": "decayed stored article metadata"
          },
          "status": "MISSING",
          "v": 0.0,
          "version": "news-decay-v2"
        },
        "news_event_flags_4h": {
          "age_s": 10.316771,
          "quality": {},
          "record_hash": "ce727fd0b71fdfce0b3d27db5b5c14229850e4828a14e099caf8ceb0b13229fb",
          "status": "OK",
          "v": [],
          "version": "1.0b5a8a44"
        },
        "news_max_materiality_4h": {
          "age_s": 10.316771,
          "quality": {},
          "record_hash": "9a246a672fc9f9d93eb12df42f76b8d4aa70f48417e057a690a53f4a340dfb9d",
          "status": "OK",
          "v": 0,
          "version": "1.9c45e9b4"
        },
        "news_newest_age_min": {
          "age_s": 10.316771,
          "quality": {
            "as_of": "2026-11-23T19:49:04.797124+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 1787.629952,
          "version": "news-context-v2"
        },
        "news_novelty_max_4h": {
          "age_s": 10.316771,
          "quality": {},
          "record_hash": "40c5621caf4c7109f12fb5c317b5b126abb9491b2c023e64d2a5ec46ffdd0349",
          "status": "OK",
          "v": false,
          "version": "1.15ceb7bf"
        },
        "news_sent_ewm_240m": {
          "age_s": 10.316771,
          "quality": {},
          "record_hash": "33d2fde9088a2003a4e36287d085f9015012bc1bb3b64ebdb05dcc8f0d69d1f5",
          "status": "OK",
          "v": 0,
          "version": "1.9cad993f"
        },
        "news_sent_ewm_60m": {
          "age_s": 10.316771,
          "quality": {},
          "record_hash": "c35e04f9848ae003d045d311aaa1dca75398140c75baf1d13a78bb59a1a5ce1a",
          "status": "OK",
          "v": 0,
          "version": "1.74ab70c1"
        },
        "news_source_div_4h": {
          "age_s": 10.316771,
          "quality": {},
          "record_hash": "d3e421711033553cb37391db13679d91df180f7f56b92c697747acb2460d9b2b",
          "status": "OK",
          "v": 0,
          "version": "1.6fd469c4"
        },
        "position_qty": {
          "age_s": 0.445888,
          "quality": {},
          "record_hash": "d5e2692efc6a24cfd117af390a5786ad65b22f74931e222f2e81d612ddf99775",
          "status": "OK",
          "v": "0",
          "version": "1.3a512120"
        },
        "position_value_usd": {
          "age_s": 0.445888,
          "quality": {},
          "record_hash": "f82f8cda2906e0c5392dad70739434ee1184a187981f478fea55709f917590d1",
          "status": "OK",
          "v": "0",
          "version": "1.9100bec4"
        },
        "price_vs_sma20": {
          "age_s": 254944.7971,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "0d79ec3c1b357a5011464af77c39b3fcad072140f1af42e8fc4caaaa2d603acd",
          "status": "MISSING",
          "v": null,
          "version": "1.a986b9cc"
        },
        "recent_price_10m": {
          "age_s": 4.797124,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "2834a19f7acc19f89054c86ec1adeb668b0a15d6f7d4d68c5468f165111eb637",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:49:00+00:00",
            "window_start": "2026-11-23T19:39:00+00:00"
          },
          "record_hash": "f2078125dae138d4f48450fb0a61eb8c906d4f67a24532499ef6e1afac85b053",
          "status": "OK",
          "v": {
            "candles": [
              [
                0,
                58.045,
                58.165,
                58.045,
                58.095,
                12394.0,
                "VERIFIED_BAR"
              ],
              [
                1,
                58.095,
                58.19,
                58.045,
                58.185,
                11202.0,
                "VERIFIED_BAR"
              ],
              [
                2,
                58.21,
                58.21,
                58.065,
                58.07,
                11493.0,
                "VERIFIED_BAR"
              ],
              [
                3,
                58.07,
                58.095,
                58.01,
                58.01,
                9725.0,
                "VERIFIED_BAR"
              ],
              [
                4,
                58.03,
                58.09,
                58.03,
                58.03,
                7536.0,
                "VERIFIED_BAR"
              ],
              [
                5,
                58.06,
                58.075,
                58.03,
                58.06,
                5274.0,
                "VERIFIED_BAR"
              ],
              [
                6,
                58.07,
                58.11,
                58.03,
                58.03,
                10942.0,
                "VERIFIED_BAR"
              ],
              [
                7,
                58.01,
                58.14,
                57.99,
                58.13,
                12879.0,
                "VERIFIED_BAR"
              ],
              [
                8,
                58.135,
                58.265,
                58.12,
                58.195,
                23601.0,
                "VERIFIED_BAR"
              ],
              [
                9,
                58.155,
                58.155,
                58.05,
                58.05,
                17585.0,
                "VERIFIED_BAR"
              ]
            ],
            "columns": [
              "minute_offset",
              "open",
              "high",
              "low",
              "close",
              "volume",
              "coverage"
            ],
            "feed": "iex",
            "window_end": "2026-11-23T19:49:00+00:00",
            "window_start": "2026-11-23T19:39:00+00:00",
            "windows": {
              "10m": {
                "close": 58.05,
                "open": 58.045,
                "range_bps": 47.37703506,
                "return": 8.614006374e-05,
                "status": "OK",
                "volume": 122631.0
              },
              "5m": {
                "close": 58.05,
                "open": 58.06,
                "range_bps": 47.36479504,
                "return": -0.0001722356183,
                "status": "OK",
                "volume": 70281.0
              }
            }
          },
          "version": "1.b12384d7"
        },
        "recent_range_bps_10m": {
          "age_s": 4.797124,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "2834a19f7acc19f89054c86ec1adeb668b0a15d6f7d4d68c5468f165111eb637",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:49:00+00:00",
            "window_start": "2026-11-23T19:39:00+00:00"
          },
          "record_hash": "a9a863b8e7c7721a134826329438580ee4b10eb473ef825e01412b98a4419950",
          "status": "OK",
          "v": 47.37703506,
          "version": "1.b7dd2e6e"
        },
        "recent_range_bps_5m": {
          "age_s": 4.797124,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "2834a19f7acc19f89054c86ec1adeb668b0a15d6f7d4d68c5468f165111eb637",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:49:00+00:00",
            "window_start": "2026-11-23T19:39:00+00:00"
          },
          "record_hash": "967749e9329dd0e792c51371ab6a7f25969e108ed0f4bb10f415cd48d5d02ae9",
          "status": "OK",
          "v": 47.36479504,
          "version": "1.860a2856"
        },
        "recent_return_10m": {
          "age_s": 4.797124,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "2834a19f7acc19f89054c86ec1adeb668b0a15d6f7d4d68c5468f165111eb637",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:49:00+00:00",
            "window_start": "2026-11-23T19:39:00+00:00"
          },
          "record_hash": "bd9e864b33e37da98410ee009a0f9b3966a83d3aeda9f580cf17a5186b0c45d9",
          "status": "OK",
          "v": 8.614006374e-05,
          "version": "1.03c04840"
        },
        "recent_return_5m": {
          "age_s": 4.797124,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "2834a19f7acc19f89054c86ec1adeb668b0a15d6f7d4d68c5468f165111eb637",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:49:00+00:00",
            "window_start": "2026-11-23T19:39:00+00:00"
          },
          "record_hash": "46ae9ba58224e9cedd1ce8c32c81adf3b8f3d0a956513977e5df2dcd87f4e5a8",
          "status": "OK",
          "v": -0.0001722356183,
          "version": "1.a9090b46"
        },
        "recent_volume_10m": {
          "age_s": 4.797124,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "2834a19f7acc19f89054c86ec1adeb668b0a15d6f7d4d68c5468f165111eb637",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:49:00+00:00",
            "window_start": "2026-11-23T19:39:00+00:00"
          },
          "record_hash": "21654cdb77c6bcec3ed223cb43bd3f7c802ae3654ee5b55d7feaccf71f670f94",
          "status": "OK",
          "v": 122631.0,
          "version": "1.891ed5cd"
        },
        "recent_volume_5m": {
          "age_s": 4.797124,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "2834a19f7acc19f89054c86ec1adeb668b0a15d6f7d4d68c5468f165111eb637",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:49:00+00:00",
            "window_start": "2026-11-23T19:39:00+00:00"
          },
          "record_hash": "82f60142d90a579c5e2752053d7788b8a702922d0217c10ed18d651efe996635",
          "status": "OK",
          "v": 70281.0,
          "version": "1.c7331f02"
        },
        "relstr_spy_60m": {
          "age_s": 244.797124,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "09e87f1462439b3dd08fb76c6c61b88838390aec61ba82d2acb78930e6c29f19",
          "status": "OK",
          "v": 0.001048568027,
          "version": "1.c04b464c"
        },
        "ret_15m": {
          "age_s": 244.797124,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "a6399cf9b7b023b247750550d782a8051c0661ae98cf4e902c9a48e919261937",
          "status": "OK",
          "v": -0.004544285347,
          "version": "1.3fa23ddd"
        },
        "ret_1d": {
          "age_s": 244.797124,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "4871f8f39f073d45e17d3d6f5ca60a8fec098c3c382779b9f1d17c4eff156f1b",
          "status": "OK",
          "v": -0.07827648115,
          "version": "1.b77eca69"
        },
        "ret_20d": {
          "age_s": 254944.7971,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "c89eca0e545e370a2b5106418f52c2c97be259b8d9a271ffd1a96adbaa2aca0a",
          "status": "MISSING",
          "v": null,
          "version": "1.7d1f1942"
        },
        "ret_5d": {
          "age_s": 254944.7971,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "05a741e625955a85a438ad18773375028848616408999e7af63ece7accaed8b3",
          "status": "MISSING",
          "v": null,
          "version": "1.5d56db82"
        },
        "ret_5m": {
          "age_s": 244.797124,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "a40abbfcf292dd9af1af383805c0563780e6267ec3328a079eb61405ea935d79",
          "status": "OK",
          "v": 0.0003446493193,
          "version": "1.c10a3b57"
        },
        "ret_60m": {
          "age_s": 244.797124,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "c8527e307f4c85659732c4d03b51b3df98373bf2e30c973873c06e701ff5ebb2",
          "status": "OK",
          "v": -0.0005165289256,
          "version": "1.6c49ff8f"
        },
        "rsi14": {
          "age_s": 254944.7971,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "1e59b41cf19356a8afb2c1abc8da30ba54a3ae1c9ca6adec3645d67baab39a97",
          "status": "MISSING",
          "v": null,
          "version": "1.273a3a79"
        },
        "rsi14_15m": {
          "age_s": 244.797124,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "8e2405b48f61208fcc98491d12fb4cfef18c440cec8f1c795d9799094ef01d8d",
          "status": "OK",
          "v": 58.43968457,
          "version": "1.f0b8fdaf"
        },
        "rvol_60m": {
          "age_s": 244.797124,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "5f13bffae65d287c331ca30abdf7fec7e16b331f2bc6deafe5d04236711a6b65",
          "status": "OK",
          "v": 0.0106280962,
          "version": "1.84c5ec7e"
        },
        "sellable_qty": {
          "age_s": 0.445888,
          "quality": {},
          "record_hash": "703d5cbf7cafe9208115401c1b6db1de20345be4c00e429240b5467007a949f4",
          "status": "OK",
          "v": "0",
          "version": "1.9cbf72e4"
        },
        "sma20": {
          "age_s": 254944.7971,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "15576f86a2842f5eb53a8c69129bc796ec2bb02d553d6eb692a0246444b821e2",
          "status": "MISSING",
          "v": null,
          "version": "1.80f8a078"
        },
        "sma50": {
          "age_s": 254944.7971,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "c77619dbf2bb36c37659503666953bdfa289b5ad53f8419d72ac47d490aa3455",
          "status": "MISSING",
          "v": null,
          "version": "1.3890c9d7"
        },
        "spread_bps": {
          "age_s": 1.614743,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "506f850361bdd43daa1777b44b670ae650d2015c1bf7568b66cd5fe86a01f046",
          "status": "OK",
          "v": 3.445305771,
          "version": "1.e2b080ab"
        },
        "trend_sma20_vs_sma50": {
          "age_s": 254944.7971,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "c3f4c96640a0fefa86efead1a20dc2a8c20470887509f9a64b8b123a7f0f6feb",
          "status": "MISSING",
          "v": null,
          "version": "1.84583425"
        },
        "unrealized_pnl_pct": {
          "age_s": 0.445888,
          "quality": {},
          "record_hash": "6c8ba673106d96bbaea3274496d46df7be3405bca24478ac28eb8b1d0ad5ec06",
          "status": "OK",
          "v": 0,
          "version": "1.7c530604"
        },
        "vol_regime_ratio": {
          "age_s": 244.797124,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "d90ece8f8b57a33c23adac7171c2d37933aae6b084d02c799c3735b650ef67ed",
          "status": "OK",
          "v": 1.077325574,
          "version": "1.302e72c1"
        },
        "volume_z20": {
          "age_s": 254944.7971,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "acd6606915e0844ee2fa5f30507b576df69022855968e20bad1ec489ca7b84b7",
          "status": "MISSING",
          "v": null,
          "version": "1.970d159b"
        },
        "volz_tod_15m": {
          "age_s": 244.797124,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "00402ad410208e76d63fb60dc603ca6c5c3933ab4023869011a7814ed1722a9c",
          "status": "OK",
          "v": 0.2274907125,
          "version": "1.4315d547"
        },
        "vwap_dev_session": {
          "age_s": 244.797124,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "42c82f02e58dec9718ee8fac543a93bc2b675d9694903f00f4a9de46d3f1fca6",
          "status": "OK",
          "v": 0.0002917575908,
          "version": "1.b41de1ff"
        }
      }
    },
    "validation_policy": "scored-15m-plus-2m-v1"
  },
  "council_mode": "PAPER_COUNCIL_SKEPTIC_OFF",
  "chair": {
    "note": "Technical signal score 0.35 below entry threshold; prearbiter entry_ok false; no buy entry justified.",
    "role": "CHAIR",
    "run_id": "cba898c2-2b32-55e2-a57f-3391d08947e3",
    "candidates": [],
    "schema_version": 2
  },
  "skeptic_audit": {
    "attempts": 0,
    "skip_reason": "DISABLED_BY_OPERATOR"
  },
  "role_outputs": [
    {
      "role": "CHAIR",
      "status": "OK",
      "response": "{\n  \"schema_version\": 2,\n  \"run_id\": \"cba898c2-2b32-55e2-a57f-3391d08947e3\",\n  \"role\": \"CHAIR\",\n  \"candidates\": [],\n  \"note\": \"Technical signal score 0.35 below entry threshold; prearbiter entry_ok false; no buy entry justified.\"\n}",
      "error": null
    },
    {
      "role": "LIQUIDITY",
      "status": "FALLBACK_CONTRACT",
      "response": null,
      "error": "LLMContractError: provider generated schema-invalid JSON: Error code: 400 - Generated JSON does not match the expected schema. Please adjust your prompt. See 'failed_generation' for more details. Error: jsonschema: '' does not validate with /required: missing properties: 'schema_version', 'run_id', 'source', 'data_confidence', 'role', 'symbols'"
    },
    {
      "role": "PORTFOLIO",
      "status": "OK",
      "response": "{\"data_confidence\": \"LOW\", \"role\": \"PORTFOLIO\", \"run_id\": \"cba898c2-2b32-55e2-a57f-3391d08947e3\", \"schema_version\": 2, \"source\": \"code\", \"symbols\": [{\"evidence\": [], \"gate\": {\"reasons\": [\"No non-conflicting code-side evidence provided to adjust determinism.\"], \"size_multiplier\": 1.0, \"state\": \"PASS\"}, \"note\": \"Pass-through: no typed adjustments to deterministic floors found.\", \"symbol\": \"INTC\"}]}",
      "error": null
    },
    {
      "role": "REGIME",
      "status": "OK",
      "response": "{\"schema_version\":2,\"run_id\":\"cba898c2-2b32-55e2-a57f-3391d08947e3\",\"source\":\"code\",\"data_confidence\":\"HIGH\",\"risk_appetite\":\"NEUTRAL\",\"role\":\"REGIME\",\"symbols\":[{\"symbol\":\"INTC\",\"evidence\":[{\"path\":\"market.regime_label\",\"band\":\"UPTREND\"},{\"path\":\"market.spy_vol_regime_ratio\",\"band\":\"POSITIVE\"}],\"note\":\"Deterministic code assessment indicates uptrend and positive volatility regime\"}]}",
      "error": null
    },
    {
      "role": "TECHNICAL",
      "status": "OK",
      "response": "{\"data_confidence\": \"HIGH\", \"role\": \"TECHNICAL\", \"run_id\": \"cba898c2-2b32-55e2-a57f-3391d08947e3\", \"schema_version\": 2, \"source\": \"code\", \"symbols\": [{\"evidence\": [{\"band\": \"POS_STRONG\", \"path\": \"symbols.INTC.ema_gap_bps_15m\"}, {\"band\": \"FIRM\", \"path\": \"symbols.INTC.rsi14_15m\"}, {\"band\": \"NEGATIVE\", \"path\": \"symbols.INTC.macd_hist_15m\"}, {\"band\": \"NONE\", \"path\": \"symbols.INTC.intraday_setup_1m\"}], \"note\": \"Strong EMA gap offset by negative MACD histogram.\", \"signal\": {\"confidence\": 0.65, \"horizon\": \"INTRADAY\", \"score\": 0.35, \"state\": \"SIGNAL\"}, \"symbol\": \"INTC\"}]}",
      "error": null
    }
  ],
  "reason_codes": [
    "NO_SIGNAL_ABOVE_THRESHOLD"
  ],
  "notes": [
    "evidence_pack:97085bf8cfd80210a2340209472ec9a9e375d5ce1de23892d7fe1701da4cd3d8",
    "council_run:cba898c2-2b32-55e2-a57f-3391d08947e3",
    "NO_SIGNAL_ABOVE_THRESHOLD"
  ],
  "error": null,
  "proposals_and_risk": []
}
```

</details>

### 14:50:09 ET · DECIDED_TRADE

<details>
<summary>Recorded decision evidence</summary>

```json
{
  "decision_id": "650d5bb9-fd38-5627-a5c8-9b8b8cf8e6ca",
  "inputs": {
    "as_of": "2026-11-23T19:50:06.682530Z",
    "regime": {
      "label": "uptrend"
    },
    "account": {
      "cash": 99803.06,
      "equity": 99803.06,
      "status": "ACTIVE",
      "account_id": "PAPER_ACCOUNT",
      "last_equity": 99803.39,
      "buying_power": 399212.24
    },
    "positions": [],
    "symbols": {
      "INTC": {
        "mid": 58.05,
        "rsi14": null,
        "ret_1d": -0.0783,
        "ret_5d": null,
        "ret_20d": null,
        "atr14_pct": null,
        "price_vs_sma20": null,
        "trend_sma20_vs_sma50": null
      }
    }
  },
  "feature_evidence": {
    "account_ref": "PAPER_ACCOUNT",
    "as_of": "2026-11-23T19:50:06.682530+00:00",
    "availability": {
      "account": "fresh",
      "bars": "fresh",
      "calendar": "fresh",
      "news": "fresh",
      "ok_fraction_core_features": 1.0,
      "quotes": "fresh"
    },
    "bands_hash": "810517c6e124c7ebc23ca0ebce7ef7ba7cc66b30bc21cacc66c1a221174255d4",
    "feasibility": {
      "INTC": {
        "can_buy": true,
        "can_buy_reasons": [],
        "can_sell": false,
        "can_sell_reasons": [
          "NO_SELLABLE_INVENTORY"
        ],
        "entry_window_open": true,
        "entry_window_reason": "",
        "held_qty": "0.0",
        "max_new_notional_usd": "2000.0",
        "sellable_qty": "0"
      }
    },
    "feature_slot": {
      "candles": {
        "INTC|2026-11-23T19:35:00+00:00": "8c40460eb8f86125bf2228c6e0b5478931f3e3a91a013bd23caa1bb828639442",
        "INTC|2026-11-23T19:36:00+00:00": "9cb732a5a05f88fcae5944f0121aac8aaa2713bd234d104b87ddb513e8886ae9",
        "INTC|2026-11-23T19:37:00+00:00": "9d5b09f82117334dcc0f33b8c32ad04009545b4670f26997f04929a89d44df93",
        "INTC|2026-11-23T19:38:00+00:00": "e98c98af48936fd32ec6ad72041fcbfa1de8511a2b8911c69eabcd4ab7117e18",
        "INTC|2026-11-23T19:39:00+00:00": "422314eba37616c0546eed1ed8aa018f6b54ce6bec687378c7704d9ca2065248",
        "INTC|2026-11-23T19:40:00+00:00": "70e0d8b0a63b3723514998b8205402a930375f59ca5308b2f48f6dbab08cd617",
        "INTC|2026-11-23T19:41:00+00:00": "4510c4c83faf5f5878d401794d4b7bed12120a3527e7efc68be6e7a94d44c40b",
        "INTC|2026-11-23T19:42:00+00:00": "98067d1cfbe2cf62a97c2f9a655f0cf4470e9f8fb2391eb0463aff7d674dad4b",
        "INTC|2026-11-23T19:43:00+00:00": "c8d1f80659f571bf3eb64a17b9935be4ce7a092a55afd0608b149b1e717e9011",
        "INTC|2026-11-23T19:44:00+00:00": "c1aa4b559490e25f881fb40af919d8644954d00315de5f007556c6e7791a0b28",
        "INTC|2026-11-23T19:45:00+00:00": "34a1b438e39db05694f921c5baec9ae6582c0220846c45eb8506fabad543f270",
        "INTC|2026-11-23T19:46:00+00:00": "805d43a04e130aa788c4098fa1275ef209d434dbdf234b2dbc11f9444444a83b",
        "INTC|2026-11-23T19:47:00+00:00": "877bc5250b1ff660d6061932b5651c5824af3f63b8d90833befef35f081fc349",
        "INTC|2026-11-23T19:48:00+00:00": "99e9788d15d3e4f4fc6f2bfc5a0ac1bc5b6622131849ffa765924063f0444199",
        "INTC|2026-11-23T19:49:00+00:00": "e05e87bd9e341432b6731054cd801ce1c0e2fd20b0996789682dea6d1c17fb3c",
        "SPY|2026-11-23T19:35:00+00:00": "a3f33f928527ca6cd947868e44e270cfe45857f8acf9296afd6811bf7c66a716",
        "SPY|2026-11-23T19:36:00+00:00": "20f2610f9083c52c53c44110cf31c15486c3658b74baf10c77427c7f1643e451",
        "SPY|2026-11-23T19:37:00+00:00": "cfc075a20afd9004c6a54e55e02de60aa1ac6fab559ca2bc363b4083a5a7b0e8",
        "SPY|2026-11-23T19:38:00+00:00": "8ac7b4d0dc16f15a1b48e3576c48557a2cf3e5e01e9dbd56ec12e4206987e786",
        "SPY|2026-11-23T19:39:00+00:00": "38712a0709a4972b95a52f42b45fd54896d71cc49ce48651c65445f1a42bf62f",
        "SPY|2026-11-23T19:40:00+00:00": "e49f4baca7c7583df76c009735c11448f1023f1415b68e390409997276db3480",
        "SPY|2026-11-23T19:41:00+00:00": "0dccbf44a642c7d605f69cb3858d90923162c6c2b93f66b9555d77776438a183",
        "SPY|2026-11-23T19:42:00+00:00": "88269dcad14d8b8d3584bb870bfc6f5eed07f56a971f9ad7e1037bfff28a3780",
        "SPY|2026-11-23T19:43:00+00:00": "a4aebaa6965c7c246c1610c4eff9a05d061eff2cadc3940774ca5ab43368ca06",
        "SPY|2026-11-23T19:44:00+00:00": "b91459d6c5ec4fb98cb4404bbe1cd7357fe920ab60a2e98579d2b6fb1626730d",
        "SPY|2026-11-23T19:45:00+00:00": "467c27fb5d5f1da7405a638366403833df31cfdd7aae5abf3fe2d4bf9f1de532",
        "SPY|2026-11-23T19:46:00+00:00": "a7668e87604b88bc72c1eadf5d9870964634f7b5e5b13baa18713dfa791d317c",
        "SPY|2026-11-23T19:47:00+00:00": "4bed66e17e5a42bb1a8cd2145b47115c4782478e39ddcb5375ca07eda3f81667",
        "SPY|2026-11-23T19:48:00+00:00": "6c3ed3ca6efe21639b18c48e926b44d18aa2768d77db9a031a04415e2ae047db",
        "SPY|2026-11-23T19:49:00+00:00": "d16b6dee3458b6f7e7d073d677de87ab9555909fe46ae643d5adfd4a75983a77"
      },
      "close": "2026-11-23T19:50:00+00:00",
      "feed": "iex",
      "indicator_close": "2026-11-23T19:45:00+00:00",
      "indicator_input_hashes": {
        "INTC": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
        "SPY": "68be2784fe1097306ec89b5433c1c0b0393b316ceebc03170624a4214da8ac5c"
      },
      "provisional": true,
      "records": {
        "market:market:breadth_above_ema21": "d7e2f70fedf1d18806a57fa4210d951ce450efccdd03a1fa716baff26d0f59e9",
        "market:market:regime_label": "b5f7eda754fe89980a8ade83e3496e26768374e4bbb5fca559b77ed06e580f14",
        "market:market:spy_ema_gap_bps_15m": "5885f7d1170e4539d33b130275da00b6751841c47609429095ed1e27403a7ec2",
        "market:market:spy_ret_60m": "e32baa93534d8fff1a8a45f49e047443333da4c605937d7e59b390885ea3b3f4",
        "market:market:spy_vol_regime_ratio": "aa0ebb1ef3de310f3fab3dc96d17b670306e13afa789433b413ded1b10128c02",
        "symbol:INTC:adv_usd_20d": "b9b2c8cd47063244741a0be3a99b852571258b975af9e1831bf9c22ac86c817d",
        "symbol:INTC:atr14_15m": "6f731751bfa53150c4b34c9f00c97b6e20fc9879a19350f0ce7cbe19a7070a61",
        "symbol:INTC:atr14_1d": "7109941c8f13c27be9954427260fd23488765da0017ae6e7268c52c67c282e0d",
        "symbol:INTC:atr14_pct": "72b22515a9b698de8e221ba3601ca48bfe5aa847f96eb780cd201d7da6e1b10b",
        "symbol:INTC:dist_hi_atr": "f7a639edc6de8a3505cda9c44554abf1ecaa2a023b37275307a8dcdb6130e17c",
        "symbol:INTC:dist_lo_atr": "c072d2270b6f94e9fd759475f20b393c3be7b2edb84db80aafe8cd8e18099a35",
        "symbol:INTC:ema21_15m": "026dc43aa182328e915e6f6d23296bedca2f3d61e29ad492593fd2b16c1f2c9c",
        "symbol:INTC:ema9_15m": "779c29eadfec6fe54e83478754f967d3444f194d88d34349bf014707a7b14100",
        "symbol:INTC:ema_gap_bps_15m": "2d80bf72eea509fb31fba6a2c3b863d8d8dc686f8d007db33fe90cf4a50e5145",
        "symbol:INTC:gap_open_pct": "22372f1618bb0042d504687f06dc178f5d5531095633eddeaf4bcfe97a2ded36",
        "symbol:INTC:intraday_ret_1h": "584b190315139eaa5cf532afd4584686eee1ec8a960635264ed6e8e8c24aeec5",
        "symbol:INTC:intraday_setup_1m": "540566e1dc2ca46bbc9e14feba41023a6d50df7ce7134904eaa67e60006301f6",
        "symbol:INTC:last_close": "d19401a83eca33beec8f4dc4c9fd9de4a732eca37d9f9287a4931e7ba85850f1",
        "symbol:INTC:macd_hist_15m": "ffc4ec65b3c48fbd631f09dccfb6d59e271d94c9ffd76307010798940056e67d",
        "symbol:INTC:price_vs_sma20": "0d79ec3c1b357a5011464af77c39b3fcad072140f1af42e8fc4caaaa2d603acd",
        "symbol:INTC:recent_price_10m": "3022492cc1907b23eeb4fde0eeb229f5369fc42f6b8ff4b4ea5aa45fbe8f2ac7",
        "symbol:INTC:recent_range_bps_10m": "5935014558ffd151924443bff063296efbe52667037bb8973a91dbb348ab688e",
        "symbol:INTC:recent_range_bps_5m": "b89e9ba386d1050f7dc35f1851c5654f979594d2499c46b7f022c906d5533291",
        "symbol:INTC:recent_return_10m": "ac80e5b477c4f9776dd87d96c9f26b45174759bb3bb4e83264866846862134eb",
        "symbol:INTC:recent_return_5m": "7888aa2e2288116b6d05ba978961fcea23ecc176383ef4c8e89f8898389db229",
        "symbol:INTC:recent_volume_10m": "a9ad4cfb8863c9ee723a41d61ff2a02e8143238ace3e4484f1f8351547b70484",
        "symbol:INTC:recent_volume_5m": "fac652304c494f5aed2f376117e0225d10af39e48f3febd56834d0907bfeb7a9",
        "symbol:INTC:relstr_spy_60m": "a6abeb1b5700dd3ab474e79dc3736473e541b8f0e68dbd391b58752123a276c3",
        "symbol:INTC:ret_15m": "daf201939e1cf19b1b2230a8bbad87f95495e5064419a30edf003c628c6eba71",
        "symbol:INTC:ret_1d": "4871f8f39f073d45e17d3d6f5ca60a8fec098c3c382779b9f1d17c4eff156f1b",
        "symbol:INTC:ret_20d": "c89eca0e545e370a2b5106418f52c2c97be259b8d9a271ffd1a96adbaa2aca0a",
        "symbol:INTC:ret_5d": "05a741e625955a85a438ad18773375028848616408999e7af63ece7accaed8b3",
        "symbol:INTC:ret_5m": "ca15211ef673e65e7599bf31cb5d31efbffa67b79933b9317144b16bb86f0a2b",
        "symbol:INTC:ret_60m": "7e5cd27de906a653c6c27bb8cccc715dce915114989ca38370dbe3710bdbc3de",
        "symbol:INTC:rsi14": "1e59b41cf19356a8afb2c1abc8da30ba54a3ae1c9ca6adec3645d67baab39a97",
        "symbol:INTC:rsi14_15m": "8e2405b48f61208fcc98491d12fb4cfef18c440cec8f1c795d9799094ef01d8d",
        "symbol:INTC:rvol_60m": "8bf9b1e4e748689f64dcd3e48f3efb7e2050f0d3f80966853d770d3181fcbd1e",
        "symbol:INTC:sma20": "15576f86a2842f5eb53a8c69129bc796ec2bb02d553d6eb692a0246444b821e2",
        "symbol:INTC:sma50": "c77619dbf2bb36c37659503666953bdfa289b5ad53f8419d72ac47d490aa3455",
        "symbol:INTC:trend_sma20_vs_sma50": "c3f4c96640a0fefa86efead1a20dc2a8c20470887509f9a64b8b123a7f0f6feb",
        "symbol:INTC:vol_regime_ratio": "7a9bcc4c5d784b0211ede12e04617f092ec1a8bbe44fb68e631f2d22f7f2377c",
        "symbol:INTC:volume_z20": "acd6606915e0844ee2fa5f30507b576df69022855968e20bad1ec489ca7b84b7",
        "symbol:INTC:volz_tod_15m": "00402ad410208e76d63fb60dc603ca6c5c3933ab4023869011a7814ed1722a9c",
        "symbol:INTC:vwap_dev_session": "5bc80d7fad07284eb1acbba8d55f398ae20cc941bafaadc70f0c1e0752634d09",
        "symbol:SPY:adv_usd_20d": "92e94f829df49f4b3a8d0be7612b000e92190d5356f55e566f04069ca7b9ffd5",
        "symbol:SPY:atr14_15m": "7ab448ef9d85396282151eac59236f9553a486b5c77591049f30866a0df20c74",
        "symbol:SPY:atr14_1d": "3cac187afe8b3f12d7d3b3b86986d403d549ebe59a7ccfaa10a213aaea0d6f29",
        "symbol:SPY:atr14_pct": "86a49f6a2b7c51bced8c4109a9b641fd3430da5d9872f600c092cec75526d214",
        "symbol:SPY:dist_hi_atr": "b099f4cd57f4eff99c7b60253bbb044823313b732d2c088e8cc7593771aae159",
        "symbol:SPY:dist_lo_atr": "4be3e05dfee2dc816e0de7a95fd2683ce136457686839a78fc866caee40f3d8d",
        "symbol:SPY:ema21_15m": "e101df90a64d088f78547e381107b8db83b2541409047168500bf08d4caa4b43",
        "symbol:SPY:ema9_15m": "d9a6929dcd2aa029a0657e3b23036ea5c8e549c3e28f704d22c59d9141f45d16",
        "symbol:SPY:ema_gap_bps_15m": "12f402c62d8c646eb7b75bb92bec226e49110827a04064a50b8a1e5b881fc789",
        "symbol:SPY:gap_open_pct": "1c9616a65f2f013255300b42e56d88ac7a725e105e6f59b39d79e458ad29184e",
        "symbol:SPY:intraday_ret_1h": "4a3cbce2b9dcc1b99d6875d1dfcc341ba613acfd2d05e42ab8e2dd8730e5c8b3",
        "symbol:SPY:intraday_setup_1m": "b72972c54af942f1d767c2a5242c2091426380c1abbee08af9dd27b4bcc5acae",
        "symbol:SPY:last_close": "caf596deca80d26016ad4208908f5e9f946155af82bcf05ef2276748182b2361",
        "symbol:SPY:macd_hist_15m": "7c1f84aa5b3c914a24e8512883539348c328fedf77f1ca8fddef3c9428311b8a",
        "symbol:SPY:price_vs_sma20": "963d8268f25c4849a1b268733b11edd2005fe4a8c767d1439d8478255d5a22c9",
        "symbol:SPY:recent_price_10m": "0d7fdc667e722d76fe47053f7402de6cc2359a9957b41ce7433ec0d2fcaf5ac9",
        "symbol:SPY:recent_range_bps_10m": "af826c12b3cd0c74cc4f6064419ae190bb4026e165d9116e2de5812fee6cfc71",
        "symbol:SPY:recent_range_bps_5m": "e1f740c767bd638902fb54124c78fb1af2e5c821ed6328b81dc96353e969056e",
        "symbol:SPY:recent_return_10m": "cc9bf5a19ad67c343f989f91a284e333ddd569e41f9f744047fbceb5edb0e5a6",
        "symbol:SPY:recent_return_5m": "8e51adf523a0a35eff9a0312796a846ead461f3c1e3967c29e39fa3105fadfc8",
        "symbol:SPY:recent_volume_10m": "56461b47e7222c4afde6975b06cf8e0bbae5c72421bc2463456b479bb5b4563b",
        "symbol:SPY:recent_volume_5m": "ea54f0e67a087aef908bd0970a972af0c20ec9bd3af01fff14ad87509176b33e",
        "symbol:SPY:relstr_spy_60m": "8192ee3c1e096d3220e21bd96547302036aad20b1f8b2a88d06eb43fca3d16bd",
        "symbol:SPY:ret_15m": "a3d4f46bec1a254ca0b9c8d8d696fb921f6a50f260660255b305d6145eb095d5",
        "symbol:SPY:ret_1d": "aab94a7dafcf360313d949fc12ced963ccb5a8b3ef27866b2b930d2d5817c533",
        "symbol:SPY:ret_20d": "5cb42b7c179c74bdcedf0dbf4ce0ee12832341fe24b75d306dccc8cc03e792c3",
        "symbol:SPY:ret_5d": "7c31dada2f0a36e24d03e89b66cb73d377f3c298c10867a1be2b05be76be6a0c",
        "symbol:SPY:ret_5m": "5bd24c2fdd2ec03500cfb1ee7920c171a517d5ca7abc08913baa269d5cd99a83",
        "symbol:SPY:ret_60m": "4980e3d5b77c6ade5ae2dbfa82485bebbf080b006724122d5c10ee1bfc6d3ee7",
        "symbol:SPY:rsi14": "ee11c2b462281f9fc927ac380b6bb2557ff2e158729fe2f17aa91d152eb3fb9f",
        "symbol:SPY:rsi14_15m": "7a2d8a98c627154aeccdc9a68b885c12330bcb82ce58cddb4d0a2f4136033fc0",
        "symbol:SPY:rvol_60m": "48f583530ace4688303da69852af61c2cfae4b534f3ed7ccf83eb23541a13f6d",
        "symbol:SPY:sma20": "1b30496ca2845ccd7a79462c221d840260e1c0361b7feb9dedbc5dc30bd4b2a5",
        "symbol:SPY:sma50": "94c11d37cff9b64498753612d4be2b84f39d1931bd55ec9e573a0c8697ceb72b",
        "symbol:SPY:trend_sma20_vs_sma50": "8aee1d285ca5a8e44083c58d0fad60754235fda2855c6ac02c9796bc41cff8bc",
        "symbol:SPY:vol_regime_ratio": "74e8bd27f29c8ff1a7018a8641ecc1607e87fe824d6a8a3c72771c5e5b8ab64b",
        "symbol:SPY:volume_z20": "26f74a49cf931c478f404ef3e6a0850c2e214cc588216f87e068535e16f86e9f",
        "symbol:SPY:volz_tod_15m": "29640670f4a0587e4e43a5ad4cd8d40a485c1b2537f64212b1cb41ffc2d19792",
        "symbol:SPY:vwap_dev_session": "24bdeea274802aa1287f3cf729d91055dff5ca6eb4d51d51e003d7f1ee7bc499"
      },
      "symbols": [
        "INTC",
        "SPY"
      ]
    },
    "horizons": {
      "INTC": {
        "10m": {
          "age_s": 6.68253,
          "last_bar_end": "2026-11-23T19:50:00+00:00",
          "status": "OK"
        },
        "15m": {
          "age_s": 306.68253,
          "last_bar_end": "2026-11-23T19:45:00+00:00",
          "status": "OK"
        },
        "5m": {
          "age_s": 6.68253,
          "last_bar_end": "2026-11-23T19:50:00+00:00",
          "status": "OK"
        },
        "60m": {
          "age_s": 306.68253,
          "last_bar_end": "2026-11-23T19:45:00+00:00",
          "status": "OK"
        },
        "horizon_conflict": false
      }
    },
    "market": {
      "breadth_above_ema21": {
        "age_s": 306.68253,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "d7e2f70fedf1d18806a57fa4210d951ce450efccdd03a1fa716baff26d0f59e9",
        "status": "OK",
        "v": 1.0,
        "version": "1.1dfe664d"
      },
      "minutes_to_close": {
        "age_s": 0.646439,
        "quality": {},
        "record_hash": "2f8057cf8ebe845fac2c6c66a5821efca2d4c5f845963bc76264aa6125dc4c03",
        "status": "OK",
        "v": 69.89939848,
        "version": "1.e79b1ead"
      },
      "regime_label": {
        "age_s": 306.68253,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "b5f7eda754fe89980a8ade83e3496e26768374e4bbb5fca559b77ed06e580f14",
        "status": "OK",
        "v": "UPTREND",
        "version": "1.f8b361d7"
      },
      "session_phase": {
        "age_s": 0.646439,
        "quality": {},
        "record_hash": "783108df26c86b40d906e5271108f5fab70fd18d393093e4343937dae2463ef3",
        "status": "OK",
        "v": "NORMAL",
        "version": "1.91f88fe8"
      },
      "spy_ema_gap_bps_15m": {
        "age_s": 306.68253,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "5885f7d1170e4539d33b130275da00b6751841c47609429095ed1e27403a7ec2",
        "status": "OK",
        "v": 37.89644347,
        "version": "1.fda7da7a"
      },
      "spy_ret_60m": {
        "age_s": 306.68253,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "e32baa93534d8fff1a8a45f49e047443333da4c605937d7e59b390885ea3b3f4",
        "status": "OK",
        "v": -0.001440203844,
        "version": "1.9feddbd1"
      },
      "spy_vol_regime_ratio": {
        "age_s": 306.68253,
        "quality": {
          "feed": "iex"
        },
        "record_hash": "aa0ebb1ef3de310f3fab3dc96d17b670306e13afa789433b413ded1b10128c02",
        "status": "OK",
        "v": 1.459893865,
        "version": "1.3b7257aa"
      }
    },
    "meta": {
      "news": {
        "INTC": {
          "effective_weight": 0,
          "in_window": 0,
          "newest_age_min": 1788.661376,
          "policy": "48h retained; per-article decay and minimum relevance; 4h count is descriptive",
          "poller_last_ok_age_s": 11.517718,
          "retrieved": 1,
          "selected": 0,
          "state": "QUIET",
          "window_min": 240
        }
      }
    },
    "news_blob_hash": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
    "news_context_blob_hash": "ef023692226f6319baf7f6429f023deb1a988f59c953b103e7a5f425a6a5d062",
    "portfolio": {
      "aggregate_cap_usd": {
        "age_s": 0.646439,
        "quality": {},
        "record_hash": "2c5e2f24990377d76ecb30cc3252cc796ea98832109c60e4b17afa1731a47373",
        "status": "OK",
        "v": "49901.530",
        "version": "1.5b3d1daf"
      },
      "aggregate_headroom_usd": {
        "age_s": 0.646439,
        "quality": {},
        "record_hash": "9932c2ed71ed0e7b1734465bb8deaf795f58bcb1ecce434871f68c258e98e2f2",
        "status": "OK",
        "v": "49901.530",
        "version": "1.7f894fff"
      },
      "buying_power": {
        "age_s": 0.646439,
        "quality": {},
        "record_hash": "92c1b2694a0975191fc16a3cd4f5c28a933e533c124bfc3b6f32523bbc711648",
        "status": "OK",
        "v": "399212.24",
        "version": "1.74948dec"
      },
      "cash": {
        "age_s": 0.646439,
        "quality": {},
        "record_hash": "888e8bca1735e31080e33929a1cbb63a77a7116f04fd4ee424ae750e489285e6",
        "status": "OK",
        "v": "99803.06",
        "version": "1.b067f5e3"
      },
      "day_pnl_pct": {
        "age_s": 0.646439,
        "quality": {},
        "record_hash": "f37a539e150a9956474dc6a24bd6995dd4fe888c5ed5760879d0b87c12f1a4e4",
        "status": "OK",
        "v": "-0.0003306500911441986088849300",
        "version": "1.35e81852"
      },
      "drawdown_pct": {
        "age_s": 0.646439,
        "quality": {},
        "record_hash": "ffd4062d01b792622495d822f25bada83c3a8664451c0cdbe95933cea06edcb2",
        "status": "MISSING",
        "v": null,
        "version": "1.19aac9ba"
      },
      "equity": {
        "age_s": 0.646439,
        "quality": {},
        "record_hash": "a48f039a73c06b6de87e2eeb16c2608fb32d6be522477c697b6c7a125186270a",
        "status": "OK",
        "v": "99803.06",
        "version": "1.a2192616"
      },
      "gross_exposure_pct": {
        "age_s": 0.646439,
        "quality": {},
        "record_hash": "233c214f2a4d15932412a0fb828dfe6c7f27bd3bfa4aba4ade01ade2e92fd6d4",
        "status": "OK",
        "v": "0E+2",
        "version": "1.b82cc518"
      },
      "gross_exposure_usd": {
        "age_s": 0.646439,
        "quality": {},
        "record_hash": "fb3c36d2c9c601ca506f3216b095b343c599a9fe49c09da49abb0c559677b657",
        "status": "OK",
        "v": "0",
        "version": "1.e4c8752b"
      },
      "last_reconcile_age_s": {
        "age_s": 0.646439,
        "quality": {},
        "record_hash": "6f9adf980cb5f9c75cf68083fc1617b2d63f02a696a21a67c564593960218a9d",
        "status": "OK",
        "v": 0,
        "version": "1.5ed0382f"
      },
      "open_buy_notional_usd": {
        "age_s": 0.646439,
        "quality": {},
        "record_hash": "d41ac9d8a511e25cad5dcc3a6e0dc68808995c0af606340ac1852b9b1415f161",
        "status": "OK",
        "v": "0",
        "version": "1.0bd0ead1"
      },
      "open_orders": {
        "age_s": 0.646439,
        "quality": {},
        "record_hash": "ca55c324b6d1fa5656492bdc69a285a3a6bb33854c2a7d4be1efe40206944116",
        "status": "OK",
        "v": [],
        "version": "1.1cf37cbf"
      },
      "open_orders_count": {
        "age_s": 0.646439,
        "quality": {},
        "record_hash": "5df13f20e7d49b177e7f266df0f05af8e0c6b496b2da2dca5b064cc756705ac6",
        "status": "OK",
        "v": 0,
        "version": "1.1db4227a"
      },
      "pending_reserved_usd": {
        "age_s": 0.646439,
        "quality": {},
        "record_hash": "3419ac35fdbc6d085519a8904b0509c6e23dc0a831a4d7091d42fd855fdedf9b",
        "status": "OK",
        "v": "0",
        "version": "1.1c3e9604"
      },
      "positions": {
        "age_s": 0.646439,
        "quality": {},
        "record_hash": "e93eb92920a827fbed701f5652359342bee8468e7514579f1a7814f8905bf297",
        "status": "OK",
        "v": [],
        "version": "1.c3284657"
      }
    },
    "registry_hash": "0fd3271269748046863b2f0558e45e2c333bb352eccc9899b7ff42277c8386fc",
    "schema_version": 1,
    "symbols": {
      "INTC": {
        "adv_usd_20d": {
          "age_s": 255006.6825,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "b9b2c8cd47063244741a0be3a99b852571258b975af9e1831bf9c22ac86c817d",
          "status": "OK",
          "v": 304793568.9,
          "version": "1.04f5e91f"
        },
        "ask_px": {
          "age_s": 1.973358,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "aebd0954abd0c66b6c2ac6522b72a951d75c206e184338a6159837a9f1b75a1b",
          "status": "OK",
          "v": 58.06,
          "version": "1.d21cdd09"
        },
        "atr14_15m": {
          "age_s": 306.68253,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "6f731751bfa53150c4b34c9f00c97b6e20fc9879a19350f0ce7cbe19a7070a61",
          "status": "OK",
          "v": 0.7629598219,
          "version": "1.0cd14e73"
        },
        "atr14_1d": {
          "age_s": 255006.6825,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "7109941c8f13c27be9954427260fd23488765da0017ae6e7268c52c67c282e0d",
          "status": "MISSING",
          "v": null,
          "version": "1.65e38f4c"
        },
        "atr14_pct": {
          "age_s": 255006.6825,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "72b22515a9b698de8e221ba3601ca48bfe5aa847f96eb780cd201d7da6e1b10b",
          "status": "MISSING",
          "v": null,
          "version": "1.87450ee9"
        },
        "bid_px": {
          "age_s": 1.973358,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "54f7546bdf6434a024880d435f367b8523b5cafc3306f7b69414e5bf62c7ce56",
          "status": "OK",
          "v": 58.04,
          "version": "1.149628cd"
        },
        "dist_hi_atr": {
          "age_s": 306.68253,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "f7a639edc6de8a3505cda9c44554abf1ecaa2a023b37275307a8dcdb6130e17c",
          "status": "OK",
          "v": -1.874279561,
          "version": "1.913ffc4a"
        },
        "dist_lo_atr": {
          "age_s": 306.68253,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "c072d2270b6f94e9fd759475f20b393c3be7b2edb84db80aafe8cd8e18099a35",
          "status": "OK",
          "v": 1.841512436,
          "version": "1.79ba4c70"
        },
        "ema21_15m": {
          "age_s": 306.68253,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "026dc43aa182328e915e6f6d23296bedca2f3d61e29ad492593fd2b16c1f2c9c",
          "status": "OK",
          "v": 57.40577599,
          "version": "1.bfcac61e"
        },
        "ema9_15m": {
          "age_s": 306.68253,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "779c29eadfec6fe54e83478754f967d3444f194d88d34349bf014707a7b14100",
          "status": "OK",
          "v": 58.09168398,
          "version": "1.81255de8"
        },
        "ema_gap_bps_15m": {
          "age_s": 306.68253,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "2d80bf72eea509fb31fba6a2c3b863d8d8dc686f8d007db33fe90cf4a50e5145",
          "status": "OK",
          "v": 119.4841427,
          "version": "1.d4519f3c"
        },
        "gap_open_pct": {
          "age_s": 306.68253,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "22372f1618bb0042d504687f06dc178f5d5531095633eddeaf4bcfe97a2ded36",
          "status": "MISSING",
          "v": null,
          "version": "1.27438d4d"
        },
        "halted": {
          "age_s": 0.646439,
          "quality": {},
          "record_hash": "c37929d84664192b9edb4c4fa907b80d9bde39910b7e4b7a813cf785d37dfa5a",
          "status": "OK",
          "v": false,
          "version": "1.22c5cf87"
        },
        "held_minutes": {
          "age_s": 0.646439,
          "quality": {},
          "record_hash": "4e7e25973cb33cd3d666004d6ac7d92ff90d11d05dc487ef577b96d25054ec07",
          "status": "MISSING",
          "v": null,
          "version": "1.de6ed6d3"
        },
        "intraday_ret_1h": {
          "age_s": 306.68253,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "584b190315139eaa5cf532afd4584686eee1ec8a960635264ed6e8e8c24aeec5",
          "status": "OK",
          "v": 0.001120786275,
          "version": "1.c3bb7751"
        },
        "intraday_setup_1m": {
          "age_s": 6.68253,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "d878b5e40ad73c9182a03a3d76469f25596dc5acfbeb00996303cbe7aa59226e",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:50:00+00:00",
            "window_start": "2026-11-23T19:40:00+00:00"
          },
          "record_hash": "540566e1dc2ca46bbc9e14feba41023a6d50df7ce7134904eaa67e60006301f6",
          "status": "OK",
          "v": {
            "confirmation": "NONE",
            "pattern": "NONE",
            "prior_trend": "FLAT",
            "range_break": "INSIDE",
            "range_ceiling": 58.265,
            "range_floor": 57.99,
            "setup_minute": null,
            "volume_ratio": 0.5669
          },
          "version": "1.2a1f51e0"
        },
        "last_close": {
          "age_s": 255006.6825,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "d19401a83eca33beec8f4dc4c9fd9de4a732eca37d9f9287a4931e7ba85850f1",
          "status": "MISSING",
          "v": null,
          "version": "1.f2485fc2"
        },
        "luld_active": {
          "age_s": 0.646439,
          "quality": {},
          "record_hash": "b71b5134e0406103a5967e19f2a0cfb5dd6768fe65b8b62a9535da06711a6730",
          "status": "MISSING",
          "v": null,
          "version": "1.84a715b2"
        },
        "macd_hist_15m": {
          "age_s": 306.68253,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "ffc4ec65b3c48fbd631f09dccfb6d59e271d94c9ffd76307010798940056e67d",
          "status": "OK",
          "v": -0.07751173219,
          "version": "1.391617c8"
        },
        "mid_px": {
          "age_s": 1.973358,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "8ce48d51897227425d177b7efa89eca573a8416c02809ddb0a0e59f9bbdd0f66",
          "status": "OK",
          "v": 58.05,
          "version": "1.d567a349"
        },
        "news_age_min_latest": {
          "age_s": 11.517718,
          "quality": {},
          "record_hash": "255403cdff951a734d5ab7c313eecc170e284ae1905226cc178c1a3f9e036260",
          "status": "MISSING",
          "v": null,
          "version": "1.d0f79dc8"
        },
        "news_confirmed": {
          "age_s": 0,
          "quality": {
            "source": "stored news and pinned price features"
          },
          "status": "OK",
          "v": false,
          "version": "news-confirmation-v2"
        },
        "news_count_1h": {
          "age_s": 11.517718,
          "quality": {},
          "record_hash": "5ad21909f425eb92c3a782503b5b758d40bcd68447e2d26778e14ba72a0ba443",
          "status": "OK",
          "v": 0,
          "version": "1.0c9362fe"
        },
        "news_count_48h": {
          "age_s": 11.517718,
          "quality": {
            "as_of": "2026-11-23T19:50:06.682530+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 1,
          "version": "news-context-v2"
        },
        "news_count_4h": {
          "age_s": 11.517718,
          "quality": {
            "as_of": "2026-11-23T19:50:06.682530+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 0,
          "version": "news-context-v2"
        },
        "news_effective_sentiment": {
          "age_s": 0,
          "quality": {
            "selected": 0,
            "source": "decayed stored article metadata"
          },
          "status": "MISSING",
          "v": 0.0,
          "version": "news-decay-v2"
        },
        "news_event_flags_4h": {
          "age_s": 11.517718,
          "quality": {},
          "record_hash": "c9e10e5e26ed5cd90beffc388801a139d77a2e126056657fcfabf9b7dd9bfb4d",
          "status": "OK",
          "v": [],
          "version": "1.0b5a8a44"
        },
        "news_max_materiality_4h": {
          "age_s": 11.517718,
          "quality": {},
          "record_hash": "74a28da521ce0ffe11064beb131b3884a35896568b84af5736b58a54158f97fa",
          "status": "OK",
          "v": 0,
          "version": "1.9c45e9b4"
        },
        "news_newest_age_min": {
          "age_s": 11.517718,
          "quality": {
            "as_of": "2026-11-23T19:50:06.682530+00:00",
            "source": "stored articles"
          },
          "status": "OK",
          "v": 1788.661376,
          "version": "news-context-v2"
        },
        "news_novelty_max_4h": {
          "age_s": 11.517718,
          "quality": {},
          "record_hash": "c2d99483a5362c3aa12668a955a973fb6905b18e56dc75aadfba83a53edb62f2",
          "status": "OK",
          "v": false,
          "version": "1.15ceb7bf"
        },
        "news_sent_ewm_240m": {
          "age_s": 11.517718,
          "quality": {},
          "record_hash": "7de9a7f66f774bde6a6f6e9d0fddf51afbf7c0b6f8c7915545ea73954109e286",
          "status": "OK",
          "v": 0,
          "version": "1.9cad993f"
        },
        "news_sent_ewm_60m": {
          "age_s": 11.517718,
          "quality": {},
          "record_hash": "f58ae9a36cb5cdb6d2a03e3f26db20a131355997219ea9a95fc37715343adee9",
          "status": "OK",
          "v": 0,
          "version": "1.74ab70c1"
        },
        "news_source_div_4h": {
          "age_s": 11.517718,
          "quality": {},
          "record_hash": "0d59e709c1a21b7e00b82f7628efd121368f3b9399973086548cfcb6ee498831",
          "status": "OK",
          "v": 0,
          "version": "1.6fd469c4"
        },
        "position_qty": {
          "age_s": 0.646439,
          "quality": {},
          "record_hash": "da77b6655a278a72a65f06292c1aeb1f12923e33b2e974f36ec3dac0955e3dc0",
          "status": "OK",
          "v": "0",
          "version": "1.3a512120"
        },
        "position_value_usd": {
          "age_s": 0.646439,
          "quality": {},
          "record_hash": "ad6368f9bc01fa5a5244df186e7daf252b2f9f633d11972cef30c416c5528b47",
          "status": "OK",
          "v": "0",
          "version": "1.9100bec4"
        },
        "price_vs_sma20": {
          "age_s": 255006.6825,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "0d79ec3c1b357a5011464af77c39b3fcad072140f1af42e8fc4caaaa2d603acd",
          "status": "MISSING",
          "v": null,
          "version": "1.a986b9cc"
        },
        "recent_price_10m": {
          "age_s": 6.68253,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "d878b5e40ad73c9182a03a3d76469f25596dc5acfbeb00996303cbe7aa59226e",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:50:00+00:00",
            "window_start": "2026-11-23T19:40:00+00:00"
          },
          "record_hash": "3022492cc1907b23eeb4fde0eeb229f5369fc42f6b8ff4b4ea5aa45fbe8f2ac7",
          "status": "OK",
          "v": {
            "candles": [
              [
                0,
                58.095,
                58.19,
                58.045,
                58.185,
                11202.0,
                "VERIFIED_BAR"
              ],
              [
                1,
                58.21,
                58.21,
                58.065,
                58.07,
                11493.0,
                "VERIFIED_BAR"
              ],
              [
                2,
                58.07,
                58.095,
                58.01,
                58.01,
                9725.0,
                "VERIFIED_BAR"
              ],
              [
                3,
                58.03,
                58.09,
                58.03,
                58.03,
                7536.0,
                "VERIFIED_BAR"
              ],
              [
                4,
                58.06,
                58.075,
                58.03,
                58.06,
                5274.0,
                "VERIFIED_BAR"
              ],
              [
                5,
                58.07,
                58.11,
                58.03,
                58.03,
                10942.0,
                "VERIFIED_BAR"
              ],
              [
                6,
                58.01,
                58.14,
                57.99,
                58.13,
                12879.0,
                "VERIFIED_BAR"
              ],
              [
                7,
                58.135,
                58.265,
                58.12,
                58.195,
                23601.0,
                "VERIFIED_BAR"
              ],
              [
                8,
                58.155,
                58.155,
                58.05,
                58.05,
                17585.0,
                "VERIFIED_BAR"
              ],
              [
                9,
                58.035,
                58.085,
                57.995,
                58.085,
                6350.0,
                "VERIFIED_BAR"
              ]
            ],
            "columns": [
              "minute_offset",
              "open",
              "high",
              "low",
              "close",
              "volume",
              "coverage"
            ],
            "feed": "iex",
            "window_end": "2026-11-23T19:50:00+00:00",
            "window_start": "2026-11-23T19:40:00+00:00",
            "windows": {
              "10m": {
                "close": 58.085,
                "open": 58.095,
                "range_bps": 47.33625957,
                "return": -0.000172131853,
                "status": "OK",
                "volume": 116587.0
              },
              "5m": {
                "close": 58.085,
                "open": 58.07,
                "range_bps": 47.35663854,
                "return": 0.0002583089375,
                "status": "OK",
                "volume": 71357.0
              }
            }
          },
          "version": "1.b12384d7"
        },
        "recent_range_bps_10m": {
          "age_s": 6.68253,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "d878b5e40ad73c9182a03a3d76469f25596dc5acfbeb00996303cbe7aa59226e",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:50:00+00:00",
            "window_start": "2026-11-23T19:40:00+00:00"
          },
          "record_hash": "5935014558ffd151924443bff063296efbe52667037bb8973a91dbb348ab688e",
          "status": "OK",
          "v": 47.33625957,
          "version": "1.b7dd2e6e"
        },
        "recent_range_bps_5m": {
          "age_s": 6.68253,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "d878b5e40ad73c9182a03a3d76469f25596dc5acfbeb00996303cbe7aa59226e",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:50:00+00:00",
            "window_start": "2026-11-23T19:40:00+00:00"
          },
          "record_hash": "b89e9ba386d1050f7dc35f1851c5654f979594d2499c46b7f022c906d5533291",
          "status": "OK",
          "v": 47.35663854,
          "version": "1.860a2856"
        },
        "recent_return_10m": {
          "age_s": 6.68253,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "d878b5e40ad73c9182a03a3d76469f25596dc5acfbeb00996303cbe7aa59226e",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:50:00+00:00",
            "window_start": "2026-11-23T19:40:00+00:00"
          },
          "record_hash": "ac80e5b477c4f9776dd87d96c9f26b45174759bb3bb4e83264866846862134eb",
          "status": "OK",
          "v": -0.000172131853,
          "version": "1.03c04840"
        },
        "recent_return_5m": {
          "age_s": 6.68253,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "d878b5e40ad73c9182a03a3d76469f25596dc5acfbeb00996303cbe7aa59226e",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:50:00+00:00",
            "window_start": "2026-11-23T19:40:00+00:00"
          },
          "record_hash": "7888aa2e2288116b6d05ba978961fcea23ecc176383ef4c8e89f8898389db229",
          "status": "OK",
          "v": 0.0002583089375,
          "version": "1.a9090b46"
        },
        "recent_volume_10m": {
          "age_s": 6.68253,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "d878b5e40ad73c9182a03a3d76469f25596dc5acfbeb00996303cbe7aa59226e",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:50:00+00:00",
            "window_start": "2026-11-23T19:40:00+00:00"
          },
          "record_hash": "a9ad4cfb8863c9ee723a41d61ff2a02e8143238ace3e4484f1f8351547b70484",
          "status": "OK",
          "v": 116587.0,
          "version": "1.891ed5cd"
        },
        "recent_volume_5m": {
          "age_s": 6.68253,
          "quality": {
            "completeness": 1.0,
            "feed": "iex",
            "input_hash": "d878b5e40ad73c9182a03a3d76469f25596dc5acfbeb00996303cbe7aa59226e",
            "max_ffill_run": 0,
            "window_end": "2026-11-23T19:50:00+00:00",
            "window_start": "2026-11-23T19:40:00+00:00"
          },
          "record_hash": "fac652304c494f5aed2f376117e0225d10af39e48f3febd56834d0907bfeb7a9",
          "status": "OK",
          "v": 71357.0,
          "version": "1.c7331f02"
        },
        "relstr_spy_60m": {
          "age_s": 306.68253,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "a6abeb1b5700dd3ab474e79dc3736473e541b8f0e68dbd391b58752123a276c3",
          "status": "OK",
          "v": 0.0008380015043,
          "version": "1.c04b464c"
        },
        "ret_15m": {
          "age_s": 306.68253,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "daf201939e1cf19b1b2230a8bbad87f95495e5064419a30edf003c628c6eba71",
          "status": "OK",
          "v": -0.002575770585,
          "version": "1.3fa23ddd"
        },
        "ret_1d": {
          "age_s": 306.68253,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "4871f8f39f073d45e17d3d6f5ca60a8fec098c3c382779b9f1d17c4eff156f1b",
          "status": "OK",
          "v": -0.07827648115,
          "version": "1.b77eca69"
        },
        "ret_20d": {
          "age_s": 255006.6825,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "c89eca0e545e370a2b5106418f52c2c97be259b8d9a271ffd1a96adbaa2aca0a",
          "status": "MISSING",
          "v": null,
          "version": "1.7d1f1942"
        },
        "ret_5d": {
          "age_s": 255006.6825,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "05a741e625955a85a438ad18773375028848616408999e7af63ece7accaed8b3",
          "status": "MISSING",
          "v": null,
          "version": "1.5d56db82"
        },
        "ret_5m": {
          "age_s": 306.68253,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "ca15211ef673e65e7599bf31cb5d31efbffa67b79933b9317144b16bb86f0a2b",
          "status": "OK",
          "v": 0.0004305890458,
          "version": "1.c10a3b57"
        },
        "ret_60m": {
          "age_s": 306.68253,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "7e5cd27de906a653c6c27bb8cccc715dce915114989ca38370dbe3710bdbc3de",
          "status": "OK",
          "v": -0.00060220234,
          "version": "1.6c49ff8f"
        },
        "rsi14": {
          "age_s": 255006.6825,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "1e59b41cf19356a8afb2c1abc8da30ba54a3ae1c9ca6adec3645d67baab39a97",
          "status": "MISSING",
          "v": null,
          "version": "1.273a3a79"
        },
        "rsi14_15m": {
          "age_s": 306.68253,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "8e2405b48f61208fcc98491d12fb4cfef18c440cec8f1c795d9799094ef01d8d",
          "status": "OK",
          "v": 58.43968457,
          "version": "1.f0b8fdaf"
        },
        "rvol_60m": {
          "age_s": 306.68253,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "8bf9b1e4e748689f64dcd3e48f3efb7e2050f0d3f80966853d770d3181fcbd1e",
          "status": "OK",
          "v": 0.01062288269,
          "version": "1.84c5ec7e"
        },
        "sellable_qty": {
          "age_s": 0.646439,
          "quality": {},
          "record_hash": "53f770617eee967889c4b7f6797fe6f91acf39fdc621a50b19eb10193c6c4251",
          "status": "OK",
          "v": "0",
          "version": "1.9cbf72e4"
        },
        "sma20": {
          "age_s": 255006.6825,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "15576f86a2842f5eb53a8c69129bc796ec2bb02d553d6eb692a0246444b821e2",
          "status": "MISSING",
          "v": null,
          "version": "1.80f8a078"
        },
        "sma50": {
          "age_s": 255006.6825,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "c77619dbf2bb36c37659503666953bdfa289b5ad53f8419d72ac47d490aa3455",
          "status": "MISSING",
          "v": null,
          "version": "1.3890c9d7"
        },
        "spread_bps": {
          "age_s": 1.973358,
          "quality": {
            "feed": "iex",
            "origin": "stream"
          },
          "record_hash": "9ebdb8c234ed683f49fa93217ff6c9aeefeb80c52c7443d0df769225e0255a73",
          "status": "OK",
          "v": 3.445305771,
          "version": "1.e2b080ab"
        },
        "trend_sma20_vs_sma50": {
          "age_s": 255006.6825,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "c3f4c96640a0fefa86efead1a20dc2a8c20470887509f9a64b8b123a7f0f6feb",
          "status": "MISSING",
          "v": null,
          "version": "1.84583425"
        },
        "unrealized_pnl_pct": {
          "age_s": 0.646439,
          "quality": {},
          "record_hash": "cf22f7224338c72f7ec9507b8c03bdde04dd1c942809ab326a95c81164cd393d",
          "status": "OK",
          "v": 0,
          "version": "1.7c530604"
        },
        "vol_regime_ratio": {
          "age_s": 306.68253,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "7a9bcc4c5d784b0211ede12e04617f092ec1a8bbe44fb68e631f2d22f7f2377c",
          "status": "OK",
          "v": 1.071783607,
          "version": "1.302e72c1"
        },
        "volume_z20": {
          "age_s": 255006.6825,
          "quality": {
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "last_session": "2026-11-20"
          },
          "record_hash": "acd6606915e0844ee2fa5f30507b576df69022855968e20bad1ec489ca7b84b7",
          "status": "MISSING",
          "v": null,
          "version": "1.970d159b"
        },
        "volz_tod_15m": {
          "age_s": 306.68253,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "00402ad410208e76d63fb60dc603ca6c5c3933ab4023869011a7814ed1722a9c",
          "status": "OK",
          "v": 0.2274907125,
          "version": "1.4315d547"
        },
        "vwap_dev_session": {
          "age_s": 306.68253,
          "quality": {
            "bar_density": 0.9996899225,
            "completeness": 1.0,
            "expected_minutes": 9675,
            "feed": "iex",
            "input_hash": "e651ab5c32644e21b97ffa7403b9f026e17ba8f7bd3c82f71a691f40eb159fb7",
            "max_ffill_run": 0,
            "max_gap_min": 0,
            "unverified": 0,
            "verified_bar": 9672,
            "verified_none": 3,
            "window_end": "2026-11-23T19:45:00+00:00",
            "window_start": "2026-10-20T13:30:00+00:00"
          },
          "record_hash": "5bc80d7fad07284eb1acbba8d55f398ae20cc941bafaadc70f0c1e0752634d09",
          "status": "OK",
          "v": 0.0008942066187,
          "version": "1.b41de1ff"
        }
      }
    },
    "validation_policy": "scored-15m-plus-2m-v1"
  },
  "council_mode": "PAPER_COUNCIL_SKEPTIC_OFF",
  "chair": {
    "note": "Buy is justified by technical bullish signal (score 0.68) and uptrend regime; limited exposure (~$2k) fits liquidity and portfolio constraints.",
    "role": "CHAIR",
    "run_id": "650d5bb9-fd38-5627-a5c8-9b8b8cf8e6ca",
    "candidates": [
      {
        "note": "EMA gap strong, bullish regime, spread normal; entry window open, cost justified.",
        "action": "buy",
        "symbol": "INTC",
        "conviction": 0.62,
        "cited_roles": [
          "TECHNICAL",
          "REGIME",
          "LIQUIDITY"
        ]
      }
    ],
    "schema_version": 2
  },
  "skeptic_audit": {
    "attempts": 0,
    "skip_reason": "DISABLED_BY_OPERATOR"
  },
  "role_outputs": [
    {
      "role": "CHAIR",
      "status": "OK",
      "response": "{\n  \"schema_version\": 2,\n  \"run_id\": \"650d5bb9-fd38-5627-a5c8-9b8b8cf8e6ca\",\n  \"role\": \"CHAIR\",\n  \"candidates\": [\n    {\n      \"symbol\": \"INTC\",\n      \"action\": \"buy\",\n      \"conviction\": 0.62,\n      \"cited_roles\": [\"TECHNICAL\", \"REGIME\", \"LIQUIDITY\"],\n      \"note\": \"EMA gap strong, bullish regime, spread normal; entry window open, cost justified.\"\n    }\n  ],\n  \"note\": \"Buy is justified by technical bullish signal (score 0.68) and uptrend regime; limited exposure (~$2k) fits liquidity and portfolio constraints.\"\n}",
      "error": null
    },
    {
      "role": "LIQUIDITY",
      "status": "OK",
      "response": "{\"schema_version\":2,\"run_id\":\"650d5bb9-fd38-5627-a5c8-9b8b8cf8e6ca\",\"source\":\"code\",\"data_confidence\":\"HIGH\",\"role\":\"LIQUIDITY\",\"symbols\":[{\"symbol\":\"INTC\",\"note\":\"deterministic code assessment\",\"evidence\":[{\"path\":\"symbols.INTC.spread_bps\",\"band\":\"NORMAL\"},{\"path\":\"symbols.INTC.mid_px\",\"band\":\"POSITIVE\"},{\"path\":\"symbols.INTC.volz_tod_15m\",\"band\":\"NORMAL\"}],\"gate\":{\"state\":\"PASS\",\"size_multiplier\":1.0,\"reasons\":[]}}]}",
      "error": null
    },
    {
      "role": "PORTFOLIO",
      "status": "OK",
      "response": "{\"data_confidence\": \"HIGH\", \"role\": \"PORTFOLIO\", \"run_id\": \"650d5bb9-fd38-5627-a5c8-9b8b8cf8e6ca\", \"schema_version\": 2, \"source\": \"code\", \"symbols\": [{\"evidence\": [{\"band\": \"POSITIVE\", \"path\": \"portfolio.equity\"}, {\"band\": \"ZERO\", \"path\": \"symbols.INTC.position_qty\"}], \"gate\": {\"reasons\": [], \"size_multiplier\": 1.0, \"state\": \"PASS\"}, \"note\": \"clean book; ample purchasing power; no current position to manage.\", \"symbol\": \"INTC\"}]}",
      "error": null
    },
    {
      "role": "REGIME",
      "status": "OK",
      "response": "{\"schema_version\":2,\"run_id\":\"650d5bb9-fd38-5627-a5c8-9b8b8cf8e6ca\",\"source\":\"code\",\"data_confidence\":\"HIGH\",\"risk_appetite\":\"NEUTRAL\",\"role\":\"REGIME\",\"symbols\":[{\"symbol\":\"INTC\",\"note\":\"Market regime UPTRND, EMA gap POS_STRONG, recent returns flat/neg, no sellable inventory.\",\"evidence\":[{\"path\":\"market.regime_label\",\"band\":\"UPTREND\"},{\"path\":\"symbols.INTC.ema_gap_bps_15m\",\"band\":\"POS_STRONG\"},{\"path\":\"symbols.INTC.recent_return_10m\",\"band\":\"NEGATIVE\"},{\"path\":\"symbols.INTC.recent_return_5m\",\"band\":\"FLAT\"},{\"path\":\"symbols.INTC.ret_15m\",\"band\":\"NEG\"}]}],\"source\":\"code\",\"data_confidence\":\"HIGH\",\"risk_appetite\":\"NEUTRAL\",\"role\":\"REGIME\",\"schema_version\":2}",
      "error": null
    },
    {
      "role": "TECHNICAL",
      "status": "OK",
      "response": "{\"data_confidence\": \"HIGH\", \"role\": \"TECHNICAL\", \"run_id\": \"650d5bb9-fd38-5627-a5c8-9b8b8cf8e6ca\", \"schema_version\": 2, \"source\": \"code\", \"symbols\": [{\"evidence\": [{\"band\": \"POS_STRONG\", \"path\": \"symbols.INTC.ema_gap_bps_15m\"}, {\"band\": \"FIRM\", \"path\": \"symbols.INTC.rsi14_15m\"}, {\"band\": \"POSITIVE\", \"path\": \"symbols.INTC.recent_range_bps_5m\"}, {\"band\": \"NONE\", \"path\": \"symbols.INTC.intraday_setup_1m\"}, {\"band\": \"NEGATIVE\", \"path\": \"symbols.INTC.macd_hist_15m\"}], \"note\": \"strong ema spread supports long; macd lagging slightly\", \"signal\": {\"confidence\": 0.78, \"horizon\": \"INTRADAY\", \"score\": 0.68, \"state\": \"SIGNAL\"}, \"symbol\": \"INTC\"}]}",
      "error": null
    }
  ],
  "reason_codes": [],
  "notes": [
    "evidence_pack:aacf08173c96a34f75d4d84de2a2b261f8d98d237b54efc53ea82bab9fd61f78",
    "council_run:650d5bb9-fd38-5627-a5c8-9b8b8cf8e6ca",
    "sizing:INTC: 18 shares at $58.09, $1060.80000000000020000 after 1x on conviction_target"
  ],
  "error": null,
  "proposals_and_risk": [
    {
      "proposal": {
        "proposal_id": "162bc54c-b538-5a02-b668-7968c3d03e3f",
        "symbol": "INTC",
        "side": "buy",
        "qty": 18,
        "limit_price": 58.09,
        "notional": 1045.62,
        "conviction": 0.5304000000000001
      },
      "risk": {
        "approved": true,
        "reason": "all checks passed",
        "checks": [
          {
            "name": "kill_switch_off",
            "limit": "must be running",
            "detail": "",
            "passed": true,
            "observed": "running"
          },
          {
            "name": "paper_endpoint_only",
            "limit": "paper-api.alpaca.markets",
            "detail": "",
            "passed": true,
            "observed": "paper-api.alpaca.markets"
          },
          {
            "name": "proposal_not_expired",
            "limit": ">0s left",
            "detail": "",
            "passed": true,
            "observed": "34s left"
          },
          {
            "name": "not_already_executed",
            "limit": "False",
            "detail": "",
            "passed": true,
            "observed": "False"
          },
          {
            "name": "market_open",
            "limit": "True",
            "detail": "",
            "passed": true,
            "observed": "True"
          },
          {
            "name": "trading_window",
            "limit": ">=5m after open, >10m before close",
            "detail": "",
            "passed": true,
            "observed": "320m since open, 70m to close"
          },
          {
            "name": "symbol_allowlist",
            "limit": "['INTC']",
            "detail": "",
            "passed": true,
            "observed": "INTC"
          },
          {
            "name": "long_only_no_oversell",
            "limit": "buy or sell<=held",
            "detail": "",
            "passed": true,
            "observed": "buy"
          },
          {
            "name": "max_order_notional",
            "limit": "$2,000.00",
            "detail": "",
            "passed": true,
            "observed": "$1,045.62"
          },
          {
            "name": "max_position_size",
            "limit": "$9,980.31",
            "detail": "",
            "passed": true,
            "observed": "$1,045.62 after fill"
          },
          {
            "name": "max_gross_exposure",
            "limit": "$49,901.53 (50.0% equity)",
            "detail": "",
            "passed": true,
            "observed": "$1,045.62 (1.0%)"
          },
          {
            "name": "max_daily_loss",
            "limit": "> -2.0%",
            "detail": "",
            "passed": true,
            "observed": "-0.00% today"
          },
          {
            "name": "max_orders_per_day",
            "limit": "<20",
            "detail": "",
            "passed": true,
            "observed": "0 so far"
          },
          {
            "name": "symbol_cooldown",
            "limit": ">=30m",
            "detail": "",
            "passed": true,
            "observed": "no recent order"
          },
          {
            "name": "no_conflicting_open_order",
            "limit": "0",
            "detail": "",
            "passed": true,
            "observed": "0 open/pending on INTC"
          },
          {
            "name": "quote_fresh",
            "limit": "-1s to 15s",
            "detail": "",
            "passed": true,
            "observed": "3.06s old on the conservative clock"
          },
          {
            "name": "price_sanity",
            "limit": "<=40.0bps",
            "detail": "",
            "passed": true,
            "observed": "8.6bps from mid 58.04"
          },
          {
            "name": "clock_skew",
            "limit": "|skew|<=10.0s",
            "detail": "",
            "passed": true,
            "observed": "+0.3s vs broker clock"
          },
          {
            "name": "spread_sane",
            "limit": "<=40.0bps",
            "detail": "",
            "passed": true,
            "observed": "3.4bps (bid 58.03 / ask 58.05)"
          },
          {
            "name": "buying_power",
            "limit": "available $399,212.24",
            "detail": "",
            "passed": true,
            "observed": "need $1,045.62"
          },
          {
            "name": "order_error_streak",
            "limit": "<5",
            "detail": "",
            "passed": true,
            "observed": "0 consecutive rejections"
          },
          {
            "name": "entry_price_current",
            "limit": "within 40 bps of analysis ask and marketable at the original 58.09 limit",
            "detail": "Executable quote timestamp 2026-11-23T19:50:07.928622+00:00",
            "passed": true,
            "observed": "analysis ask 58.06, current 58.05, move -1.72 bps"
          },
          {
            "name": "bracket_stop_risk",
            "limit": "15",
            "detail": "",
            "passed": true,
            "observed": "6.30"
          }
        ]
      },
      "orders": [
        {
          "client_order_id": "INTC-ORDER-3-CLIENT_ORDER_ID",
          "alpaca_order_id": "INTC-ORDER-3-ID",
          "status": "canceled",
          "filled_qty": 17.0,
          "filled_avg_price": 58.02,
          "error": null,
          "events": [
            {
              "t": "2026-11-23T19:50:13.843458+00:00",
              "event": "pending_new",
              "status": "pending_new",
              "filled_qty": 0.0,
              "avg_price": null
            },
            {
              "t": "2026-11-23T19:50:13.849203+00:00",
              "event": "new",
              "status": "new",
              "filled_qty": 0.0,
              "avg_price": null
            },
            {
              "t": "2026-11-23T19:50:14.638113+00:00",
              "event": "partial_fill",
              "status": "partially_filled",
              "filled_qty": 4.0,
              "avg_price": 58.02
            },
            {
              "t": "2026-11-23T19:50:15.392275+00:00",
              "event": "partial_fill",
              "status": "partially_filled",
              "filled_qty": 17.0,
              "avg_price": 58.02
            },
            {
              "t": "2026-11-23T19:50:15.624693+00:00",
              "event": "canceled",
              "status": "canceled",
              "filled_qty": 17.0,
              "avg_price": 58.02
            },
            {
              "t": "2026-11-23T19:50:16.498392+00:00",
              "event": "reconciled",
              "status": "canceled",
              "filled_qty": 17.0,
              "avg_price": 58.02
            }
          ]
        }
      ]
    }
  ]
}
```

</details>

### 14:50:17 ET · BLOCKED_GUARD

<details>
<summary>Recorded decision evidence</summary>

```json
{
  "decision_id": "647fcfa2-b95b-5b4e-bbaf-53183df3b121",
  "inputs": {},
  "feature_evidence": {},
  "council_mode": null,
  "chair": null,
  "skeptic_audit": null,
  "role_outputs": [],
  "reason_codes": null,
  "notes": [
    "SCHEDULER_SKIP:halted"
  ],
  "error": "bracket parent INTC-ORDER-3-CLIENT_ORDER_ID partially filled; verify protection for 4 shares",
  "proposals_and_risk": []
}
```

</details>
