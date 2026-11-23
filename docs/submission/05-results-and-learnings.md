# 5. Results and learnings

## Results

The latest historical evaluation replayed three selected 30-minute windows for MU, AAPL, and NVDA. The strategy completed four round trips with eight fills, finished each window flat, and realized **+$2.43 after the bid–ask spread and before additional fees**. All four closed trades showed a profit. Each window started with $8,000, and returns ranged from **+0.0060% to +0.0150%**. The largest observed drawdown was **0.0405%** in the NVDA window. SPY returned between **+0.0508% and +0.1364%** over the matched windows and outperformed the strategy in each. The selected windows show how the order and audit paths behave under recorded conditions. The sample is too small to estimate a durable edge. [Financial results and benchmark](02-proof-pack.md)

Across 90 slots, there were 11 full council reviews and 79 guarded slots. Input-to-Chair latency for the 11 reviews was **3.56 s median, 4.89 s p95, and 5.22 s maximum**. One approved NVDA profit exit was blocked because the order would have reached a quote below break-even. The eventual sale filled at $184.00 after a 19-minute hold. The eight filled orders used measured decision timing and the quote at submission. [Council decisions and risk checks](03-decision-journal.md)

## What was hard

**Execution timing changed the result.** An analysis quote can be valid and profitable at the start of a review, then cease to be either by submission. In the initial September comparison, the Chair closed AAPL and NVDA near their first one-minute review after adverse moves. A thirty-minute prompt alone still produced a discretionary NVDA loss after about four minutes while the recorded entry condition remained valid. The subsequent test requested a full council review at a profitable executable mark and rechecked the quote after the Chair's decision. This caught the NVDA submission race and let the later council act on a new quote.

**Model output and market-data quality can dominate the funnel.** The February pass and rerun produced just three valid Chair verdicts from 24 attempted reviews. Real provider throttles and two Technical validation failures accounted for the rest. The September test paced hosted review batches by at least 65 seconds outside the simulated order clock. Its logs recorded zero rate-limit errors and four rejected attempts involving unexpected tool calls. The affected reviews recovered. Separately, a historical feed comparison found that IEX could supply core technical values while still leaving a required market-regime input unavailable. We preserve incomplete reviews, genuine WAITs, and guarded slots as distinct outcomes. [Experiment log](04-experiment-log.md)

## Cost and remaining evidence

The 55 returned model responses logged 92,299 uncached input tokens, 12,799 output tokens, and 7,168 cached input tokens. Applying the pinned replay profile's rates gives a **$0.0301 model-cost estimate** for the reported usage. Four rejected attempts returned no usage record. The replay workers ran for about **678 seconds** in total, including **561 seconds of test pacing**. The provider invoice and compute costs are separate.

## November 23 live paper results

The AAPL and INTC round trips yielded **+$3.58** in realized paper P&L. AAPL lost $0.33 on one share after about ten minutes. INTC earned $3.91 on 17 shares after about seven minutes. Alpaca confirmed a flat account at $99,806.97. Estimated model usage was $0.0728 at the app’s configured model rates. [Broker results and matched SPY](02-proof-pack.md)

Both partial fills halted discretionary reviews. The independent closeout handled the positions within their windows. The next question is whether a reconciled and protected partial position can resume exit-only council reviews with executable P&L in the Chair’s evidence. The three-session requirement and live council profit-taking remain open.
