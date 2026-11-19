"use strict";

const $ = (selector) => document.querySelector(selector);
const ny = {timeZone: "America/New_York"};
const time = new Intl.DateTimeFormat("en-US", {...ny, hour: "2-digit", minute: "2-digit", hourCycle: "h23"});
const date = new Intl.DateTimeFormat("en-US", {...ny, month: "short", day: "numeric", year: "numeric"});
const cellNumber = new Intl.NumberFormat("en-US", {maximumFractionDigits: 4});
const outcomeNames = {
  DECIDED_TRADE: "Trade intent", DECIDED_HOLD: "Hold", DECIDED_NO_TRADE: "No trade", INCOMPLETE_PROVIDER: "Provider failure",
  INCOMPLETE_CONTRACT: "Invalid response", INCOMPLETE_DATA: "Incomplete data", BLOCKED_GUARD: "Guard blocked",
  NO_CANDIDATE: "No candidate", DEADLINE: "Deadline elapsed", SESSION_CUTOFF: "Session cutoff",
};
const roles = ["TECHNICAL", "NEWS", "REGIME", "LIQUIDITY", "PORTFOLIO", "CHAIR", "SKEPTIC"];
const state = {
  view: "simulation", savedRun: null, analysis: null, run: null, cycle: null, detail: null, window: 10,
  expiryTimer: null, history: [], historySelection: null,
  simulationId: null, simulationRefresh: null, simulationVersion: 0,
};
const dollars = new Intl.NumberFormat("en-US", {style: "currency", currency: "USD"});

function cash(value) {
  return value == null ? "Unavailable" : dollars.format(value);
}

function node(tag, text, className) {
  const element = document.createElement(tag);
  if (text != null) element.textContent = text;
  if (className) element.className = className;
  return element;
}

function pair(label, value) {
  const pair = node("div");
  pair.append(node("dt", label), node("dd", value));
  return pair;
}

function fold(label, content) {
  const element = node("details");
  element.append(node("summary", label));
  if (typeof content === "function") {
    const populate = () => {
      if (!element.open) return;
      element.append(content());
      element.removeEventListener("toggle", populate);
    };
    element.addEventListener("toggle", populate);
  } else {
    element.append(content);
  }
  return element;
}

function showJson(value) {
  return node("pre", JSON.stringify(value, null, 2));
}

function starAudit(detail) {
  return fold("STAR audit", () => {
    const {decision, role_logs, fills} = detail.star;
    const reports = {...detail.result.reports, CHAIR: detail.result.draft, SKEPTIC: detail.result.skeptic};
    const content = node("div");
    const dimensions = node("dl", null, "metrics");
    for (const [label, key] of [["Trading date (ET)", "date"], ["Instrument", "instrument"],
      ["Portfolio", "portfolio"], ["Strategy", "strategy"]]) {
      dimensions.append(pair(label, display(decision[key])));
    }
    content.append(dimensions, node("h3", "Decision fact"));
    content.append(table(["Decision", "Action", "Outcome", "Latency (ms)"], [
      [decision.id, decision.action.toUpperCase(), outcomeNames[decision.outcome] || decision.outcome, decision.latency_ms],
    ]));
    const filter = node("select", null, "audit-role-filter");
    filter.setAttribute("aria-label", "Filter role logs");
    for (const role of ["All roles", ...new Set(role_logs.map(log => log.role))]) {
      const option = node("option", role);
      option.value = role === "All roles" ? "" : role;
      filter.append(option);
    }
    const logTable = node("div");
    const renderLogs = () => {
      const matching = role_logs.filter(log => !filter.value || log.role === filter.value);
      logTable.replaceChildren(table(["Role", "Record", "Status", "Model", "Latency (ms)"], matching.map(log => [
        log.role, log.sequence ? `Attempt ${log.attempt ?? log.sequence}` : "Verdict", log.status, log.model ?? "—",
        log.latency_ms ?? "—",
      ])));
      for (const log of matching) {
        if (!log.sequence && reports[log.role]) {
          logTable.append(fold(`${log.role} recorded verdict`, () => showJson(reports[log.role])));
        } else if (log.sequence) {
          const call = detail.attempts.filter(attempt => attempt.role === log.role)[log.sequence - 1];
          if (call) logTable.append(attemptDetails(call));
        }
      }
    };
    filter.addEventListener("change", renderLogs);
    renderLogs();
    content.append(node("h3", "Role log facts"), filter, logTable, node("h3", "Fill facts"));
    content.append(fills.length ? table(["Order", "Side", "Shares", "Fill price", "Time (ET)"], fills.map(fill => [
      fill.order_id, fill.side?.toUpperCase() ?? "—", fill.shares ?? "—", `$${fill.price}`,
      fill.at ? secondTime.format(new Date(fill.at)) : "—",
    ])) : node("p", "No fills recorded.", "quiet"));
    return content;
  });
}

function display(value) {
  if (value == null) return "Unavailable";
  return typeof value === "number" ? cellNumber.format(value) : String(value);
}

function percent(value, digits = 3) {
  return value == null ? "Unavailable" : `${value.toFixed(digits)}%`;
}

function table(headers, rows) {
  const wrap = node("div", null, "table-wrap");
  const grid = node("table");
  const head = node("tr");
  for (const label of headers) head.append(node("th", label));
  grid.append(node("thead"), node("tbody"));
  grid.tHead.append(head);
  for (const row of rows) {
    const tr = node("tr");
    for (const value of row) tr.append(node("td", display(value)));
    grid.tBodies[0].append(tr);
  }
  wrap.append(grid);
  return wrap;
}

async function read(path, options) {
  const response = await fetch(path, options);
  const data = await response.json().catch(() => null);
  if (!response.ok || data === null) throw new Error(data?.error || `HTTP ${response.status}`);
  return data;
}

function showError(message) {
  $("#error").textContent = message;
  $("#error").hidden = false;
}

function timeline(day) {
  $("#timeline").replaceChildren();
  for (const cycle of state.run.cycles.filter((item) => item.day === day)) {
    const label = cycle.filled ? "Filled" : outcomeNames[cycle.outcome] || cycle.outcome;
    const status = cycle.filled ? "positive" : cycle.outcome.startsWith("INCOMPLETE") ? "warning" : "";
    const button = node("button", null, "slot");
    button.type = "button";
    button.dataset.run = cycle.run_id;
    button.append(node("span", time.format(new Date(cycle.as_of))), node("strong", label, status));
    button.addEventListener("click", () => selectCycle(cycle));
    $("#timeline").append(button);
  }
}

async function selectCycle(cycle) {
  state.cycle = cycle;
  state.detail = null;
  $("#error").hidden = true;
  $("#cycle-detail").hidden = true;
  $("#cycle-date").textContent = date.format(new Date(cycle.as_of));
  $("#cycle-title").textContent = `${time.format(new Date(cycle.as_of))} ET · ${state.run.symbol}`;
  $("#cycle-badges").replaceChildren(
    node("span", outcomeNames[cycle.outcome] || cycle.outcome, "badge"),
    node("span", `${cycle.elapsed_s.toFixed(1)} s`, "badge"),
  );
  for (const button of document.querySelectorAll(".slot")) {
    button.setAttribute("aria-current", String(button.dataset.run === cycle.run_id));
  }
  try {
    const detail = await read(`/api/cycle/${encodeURIComponent(cycle.run_id)}`);
    if (state.cycle !== cycle) return;
    state.detail = detail;
    $("#cycle-detail").hidden = false;
    renderMarket();
    renderCouncil();
    renderExecution();
  } catch (error) {
    if (state.cycle === cycle) showError(`The saved decision could not be loaded (${error.message}).`);
  }
}

function candleWindow() {
  const pack = state.detail.evidence;
  const context = pack.symbols?.[state.run.symbol]?.recent_price_10m?.v;
  const rows = context?.candles?.filter(([offset]) => offset >= 10 - state.window) || [];
  return {rows, context};
}

function candleTime(context, offset) {
  return time.format(new Date(new Date(context.window_start).getTime() + offset * 60_000));
}

function drawCandles() {
  if (!state.detail) return;
  const {rows, context} = candleWindow();
  const canvas = $("#candles");
  const {width, height} = canvas.getBoundingClientRect();
  if (!width || !height) return;
  const dpr = devicePixelRatio || 1;
  canvas.width = Math.round(width * dpr);
  canvas.height = Math.round(height * dpr);
  const paint = canvas.getContext("2d");
  paint.scale(dpr, dpr);
  const colors = getComputedStyle(canvas);
  const color = (name) => colors.getPropertyValue(name).trim();
  paint.font = "11px Consolas, monospace";
  const verified = rows.filter((row) => row.slice(1, 5).every(Number.isFinite));
  if (!verified.length) {
    paint.fillStyle = color("--muted");
    paint.fillText("No completed candles in this evidence pack.", 8, 26);
    return;
  }

  const lo = Math.min(...verified.map((row) => row[3]));
  const hi = Math.max(...verified.map((row) => row[2]));
  const pad = Math.max((hi - lo) * .1, .001);
  const xStart = 8, plotWidth = width - 70, plotHeight = height - 36;
  const y = (v) => 8 + (hi + pad - v) / (hi - lo + 2 * pad) * plotHeight;
  const stride = plotWidth / state.window;
  const bodyWidth = Math.min(19, stride * .5);
  for (let i = 0; i < 5; i++) {
    const level = hi + pad - (hi - lo + 2 * pad) * i / 4;
    const py = y(level);
    paint.strokeStyle = color("--line");
    paint.beginPath();
    paint.moveTo(xStart, py);
    paint.lineTo(xStart + plotWidth, py);
    paint.stroke();
    paint.fillStyle = color("--muted");
    paint.fillText(`$${level.toFixed(2)}`, xStart + plotWidth + 5, py + 4);
  }
  for (const [offset, open, high, low, close] of verified) {
    const x = xStart + (offset - (10 - state.window) + .5) * stride;
    const candleColor = color(close >= open ? "--mint" : "--coral");
    paint.strokeStyle = candleColor;
    paint.fillStyle = candleColor;
    paint.beginPath();
    paint.moveTo(x, y(high));
    paint.lineTo(x, y(low));
    paint.stroke();
    paint.fillRect(x - bodyWidth / 2, Math.min(y(open), y(close)), bodyWidth, Math.max(1.5, Math.abs(y(open) - y(close))));
    if (stride >= 37 || offset % 2 === 0) {
      paint.fillStyle = color("--muted");
      paint.fillText(candleTime(context, offset), x - 15, height - 6);
    }
  }
}

function renderMarket() {
  const pack = state.detail.evidence;
  const symbol = state.run.symbol;
  const features = pack.symbols?.[symbol] || {};
  const {rows, context} = candleWindow();
  const windowValues = context?.windows?.[`${state.window}m`];
  const feed = context?.feed?.toUpperCase();
  $("#chart-caption").textContent = [feed, "One-minute candles · ET", context ? `${rows.length} stored slots` : "No candle data"].filter(Boolean).join(" · ");
  $("#key-features").replaceChildren(
    pair(`${state.window}-minute return`, percent(windowValues?.return == null ? null : windowValues.return * 100)),
    pair("15-minute RSI", display(features.rsi14_15m?.v)),
    pair("15-minute EMA gap (bps)", display(features.ema_gap_bps_15m?.v)),
    pair("15-minute MACD histogram", display(features.macd_hist_15m?.v)),
    pair("15-minute ATR", display(features.atr14_15m?.v)),
    pair("Distance from session VWAP", percent(features.vwap_dev_session?.v == null ? null : features.vwap_dev_session.v * 100)),
    pair("Quoted spread (bps)", display(features.spread_bps?.v)),
    pair("News coverage", display(pack.meta?.news?.[symbol]?.state)),
  );
  const featureData = $("#feature-data");
  featureData.replaceChildren();
  if (rows.length) featureData.append(table(["Time ET", "Open", "High", "Low", "Close", "Volume", "Coverage"], rows.map(
    ([offset, ...values]) => [candleTime(context, offset), ...values],
  )));
  featureData.append(fold("Full stored evidence pack", () => showJson(pack)));
  const patternPanel = $("#pattern");
  const setup = features.intraday_setup_1m?.v;
  patternPanel.hidden = !Object.hasOwn(features, "intraday_setup_1m");
  patternPanel.replaceChildren();
  if (setup) {
    const label = setup.pattern === "NONE" ? "No recent reversal pattern" : setup.pattern.replaceAll("_", " ");
    const confirmation = setup.confirmation.replaceAll("_", " ").toLowerCase();
    const details = node("div", null, "pattern-content");
    details.append(node("strong", label), node("p", `Prior trend ${setup.prior_trend.toLowerCase()} · ${confirmation}`, "quiet"),
      node("p", `Volume ${display(setup.volume_ratio)}× recent median · Prior range ${cash(setup.range_floor)}–${cash(setup.range_ceiling)}`, "quiet"));
    patternPanel.append(details);
  } else if (!patternPanel.hidden) {
    patternPanel.append(node("p", "Pattern analysis needs ten consecutive completed candles with trades.", "quiet"));
  }
  const news = state.detail.news;
  const newsPanel = $("#scenario-news");
  newsPanel.hidden = !news;
  if (news) {
    const status = {
      empty: news.returned ? "No article versions available at this time" : "No articles returned for this window",
      unavailable: "Alpaca news request unavailable",
      retrieved: `${news.eligible} article${news.eligible === 1 ? "" : "s"} available at decision time`,
    }[news.status];
    newsPanel.replaceChildren(node("p", `Alpaca News · ${status}`, "quiet"));
  }
  drawCandles();
}

function renderChairPath(detail) {
  const {result, attempts, scenario} = detail;
  const chair = attempts.findLast(attempt => attempt.role === "CHAIR" && attempt.response.text);
  let input;
  try { input = JSON.parse(chair?.request.user); } catch { /* Some older records have no model inputs. */ }
  const reports = roles.filter(role => input?.reports?.[role]).map(role =>
    role.toLowerCase() + (input.reports[role].source === "code" ? " (code)" : ""));
  const challenge = input?.independent_challenge;
  const reviewed = [...reports, ...(challenge && result.skeptic ? ["skeptic"] : [])].join(" · ");
  const proposal = result.draft?.candidates?.find(candidate => candidate.symbol === scenario.symbol);
  const proposed = proposal
    ? `${proposal.action.toUpperCase()} · conviction ${display(proposal.conviction)}`
    : result.draft ? "No action proposed" : "Unavailable";
  $("#chair-path").replaceChildren(
    pair("Reports reviewed", reviewed || "Unavailable"),
    pair("Chair proposal", proposed),
    pair("Final decision", recordedRecommendation(detail)),
  );
  const rejected = detail.risk?.find(check => !check.approved);
  const reasons = result.reason_codes?.map(reason => reason.replaceAll("_", " ").toLowerCase()).join(" · ");
  const verdict = detail.latest_error || rejected?.reason || reasons || "";
  $("#chair-verdict").textContent = verdict;
  $("#chair-verdict").hidden = !verdict;
}

function renderCouncil() {
  const {result, attempts, evidence} = state.detail;
  const symbol = state.run.symbol;
  const trace = $("#decision-trace");
  const pre = result.prearbiter?.[symbol];
  trace.replaceChildren();
  if (pre) {
    const summary = node("div", null, "trace-content");
    const scores = pre.signals.map((signal) => `${signal.role.toLowerCase()} ${signal.eff.toFixed(2)}`).join(" · ");
    const checks = pre.entry_checks;
    const signalConflict = pre.reasons.includes("CONFLICT");
    const explanation = signalConflict && !pre.signals.some((signal) => signal.eff > 0)
      ? "Bearish evidence blocked a long entry."
      : signalConflict ? "An opposing signal blocked a long entry."
      : checks?.score_threshold && !checks?.signal_support
      ? "The score passed. Directional support failed: one strong signal or two moderate signals were required."
      : pre.reasons.includes("NO_SIGNAL_ABOVE_THRESHOLD") ? "Entry score or signal support was below the required level." : "";
    summary.append(node("p", `Entry score ${pre.S.toFixed(2)} / ${pre.threshold_eff.toFixed(2)} required`));
    if (scores) summary.append(node("p", scores, "quiet"));
    if (pre.gates.length) summary.append(node("p", `Verified gates · ${pre.gates.map(gate => `${gate.role.toLowerCase()} ${gate.state.toLowerCase()}`).join(" · ")}`, "quiet"));
    if (explanation) summary.append(node("p", explanation, "quiet"));
    trace.append(summary);
  }
  const phases = state.detail.phase_timings;
  if (phases) {
    const measured = [["Setup", phases.warmup_s], ["Data", phases.market_data_s],
      ["Features", phases.feature_compute_s], ["Council", phases.council_s]];
    const label = measured.filter(([, seconds]) => Number.isFinite(seconds))
      .map(([name, seconds]) => `${name} ${seconds.toFixed(1)} s`).join(" · ");
    if (label) trace.append(node("p", label, "quiet"));
  }
  const roleRows = [];
  for (const role of roles) {
    const report = result.reports?.[role];
    const item = report?.symbols?.find((value) => value.symbol === symbol);
    const review = role === "CHAIR" ? result.draft : role === "SKEPTIC" ? result.skeptic : null;
    const newsState = evidence.meta?.news?.[symbol]?.state;
    const displayName = role[0] + role.slice(1).toLowerCase();
    const roleRow = node("div", null, "role");
    const label = node("div");
    const note = node("div");
    const source = review ? "Model" : {"llm+code": "Model + code", code: "Code"}[report?.source];
    const roleAttempts = attempts.filter((attempt) => attempt.role === role);
    const attempted = roleAttempts.length > 0;
    const failure = result.role_audit?.[role]?.fallback;
    const latestReply = roleAttempts.findLast((attempt) => attempt.response.text);
    let publicAnswer;
    if (latestReply) {
      try { publicAnswer = JSON.parse(latestReply.response.text); } catch { /* Exact response is still in the audit. */ }
    }
    label.append(node("div", displayName, "role-name"), node("span", failure ? "Unavailable" : source || (attempted ? "Attempted" : "Skipped"), "badge"));
    if (role === "NEWS" && newsState === "UNAVAILABLE") {
      const empty = state.detail.news?.status === "empty";
      const availability = empty ? "Alpaca returned no usable articles for this time." : "Historical news unavailable.";
      note.append(node("p", attempted ? availability : `${availability} The news model was skipped.`));
      if (attempted && !failure && publicAnswer?.assessment) {
        note.replaceChildren(node("p", publicAnswer.assessment), node("p", "No usable articles. News abstains.", "quiet"));
      }
    } else if (review) {
      if (review.note) note.append(node("p", review.note));
      for (const candidate of review.candidates || []) {
        if (role === "CHAIR" && state.view === "history") {
          if (candidate.cited_roles.length) note.append(node("p", `Cited reports · ${candidate.cited_roles.join(", ")}`, "quiet"));
        } else {
          note.append(node("p", `${candidate.action.toUpperCase()} ${candidate.symbol} · conviction ${display(candidate.conviction)} · ${candidate.cited_roles.join(", ")}`, "quiet"));
        }
      }
      if (review.objections) {
        if (!review.objections.length) note.append(node("p", "No objections recorded."));
        for (const objection of review.objections) {
          note.append(node("p", `${objection.symbol} · Severity ${objection.severity} · ${objection.reason}`, "quiet"));
        }
      }
      if (!note.children.length) note.append(node("p", "No candidates recorded."));
    } else if (item) {
      const code = item.signal?.state || item.gate?.state || report.risk_appetite;
      if (!failure && publicAnswer?.assessment) note.append(node("p", publicAnswer.assessment));
      else if (item.note) note.append(node("p", item.note));
      if (item.advisory && item.note) note.append(node("p", item.note, "quiet"));
      if (!failure && publicAnswer?.invalidation) {
        note.append(node("p", `Invalidation: ${publicAnswer.invalidation}`, "quiet"));
      }
      if (code) note.append(node("p", code.replaceAll("_", " "), "quiet"));
      if (item.evidence?.length) {
        const refs = item.evidence.map((value) => value.path + (value.band ? ` · ${value.band}` : ""));
        note.append(node("p", refs.join(" / "), "quiet"));
      }
    } else {
      let skipped = "This role did not run for this decision.";
      if (role === "CHAIR" && pre && !pre.entry_ok && !pre.exit_ok) skipped = "This run stopped at the entry and exit checks before chair review.";
      if (role === "SKEPTIC" && !result.draft) skipped = "No chair assessment was available to review.";
      note.append(node("p", attempted ? "No validated report. See the recorded model attempts." : skipped, "quiet"));
    }
    if (failure) {
      const fallback = report ? "Code assessment shown." : "No validated review was available.";
      note.append(node("p", `Model ${failure.toLowerCase()} failure. ${fallback}`, "warning"));
      if (result.role_audit[role].error) note.append(node("p", result.role_audit[role].error, "quiet"));
    }
    if (report?.evidence_stripped) note.append(node("p", `${report.evidence_stripped} unsupported evidence references were removed.`, "warning"));
    if (roleAttempts.length || report || review) {
      note.append(fold(`${displayName} inputs and complete responses`, () => {
        const audit = node("div");
        if (report || review) audit.append(fold("Validated report", () => showJson(report || review)));
        for (const attempt of roleAttempts) audit.append(attemptDetails(attempt));
        return audit;
      }));
    }
    roleRow.append(label, note);
    if (state.view === "history" && role === "CHAIR") $("#chair-response").replaceChildren(roleRow);
    else roleRows.push(roleRow);
  }
  $("#roles").replaceChildren(...roleRows);
  const logs = $("#attempts");
  logs.replaceChildren(fold("Model inputs and responses", () => {
    const audit = node("div");
    if (!attempts.length) audit.append(node("p", "No model requests recorded.", "quiet"));
    for (const attempt of attempts) audit.append(attemptDetails(attempt));
    return audit;
  }));
  if (state.detail.star) logs.append(starAudit(state.detail));
}

function attemptDetails(attempt) {
  return fold(`${attempt.role} · Attempt ${attempt.attempt ?? "—"} · ${attempt.response.model || attempt.status || "Recorded"}`, () => {
    const details = node("div");
    const {user, ...instructions} = attempt.request;
    if (attempt.response.text) details.append(node("p", "Recorded model response", "quiet"), node("pre", attempt.response.text));
    if (attempt.error) details.append(node("p", attempt.error, "warning"));
    if (user != null) details.append(fold("Exact role input", () => {
      let input = user;
      try { input = JSON.stringify(JSON.parse(user), null, 2); } catch { /* Preserve plain text. */ }
      return node("pre", input);
    }));
    if (Object.keys(instructions).length) details.append(fold("Prompt and response schema", () => showJson(instructions)));
    return details;
  });
}

function renderExecution() {
  const {result, risk, orders, fills} = state.detail;
  const target = $("#execution");
  target.replaceChildren();
  const reasons = (result.reason_codes || []).map((reason) => reason.replaceAll("_", " ").toLowerCase());
  if (reasons.length) target.append(node("p", reasons.join(" · "), "quiet execution-line"));
  if (!risk.length) target.append(node("p", "No proposal reached the risk gate.", "execution-line"));
  for (const verdict of risk) {
    const passed = verdict.checks?.filter((check) => check.passed).length || 0;
    const checks = verdict.checks || [];
    const label = verdict.approved ? "Approved" : "Rejected";
    target.append(node("p", `${label} · ${passed}/${checks.length} checks passed${verdict.approved ? "" : ` · ${verdict.reason}`}`, "execution-line"));
    target.append(fold("Risk check details", table(["Check", "Result", "Observed", "Limit"], checks.map(
      (check) => [check.name, check.passed ? "Pass" : "Fail", check.observed, check.limit],
    ))));
  }
  for (const order of orders) {
    target.append(node("p", `${order.side.toUpperCase()} ${order.qty} ${order.symbol} · Limit $${display(order.limit_price)} · ${order.status}`, "execution-line"));
    for (const fill of fills.filter((value) => value.order_id === order.id)) {
      target.append(node("p", `Simulated fill · ${fill.qty} shares at $${display(fill.price)} · ${time.format(new Date(fill.t))} ET`, "positive execution-line"));
    }
  }
}

function recordedRecommendation({recommendation, result, outcome, latest_error}) {
  if (latest_error) return "Snapshot expired · 0 shares";
  const status = result?.outcome || outcome;
  if (status === "DECIDED_NO_TRADE") return "No trade · review unavailable";
  if (status.startsWith("INCOMPLETE") && !recommendation.shares) {
    return "Analysis incomplete · 0 shares";
  }
  return `${recommendation.action.toUpperCase()} · ${recommendation.shares} ${recommendation.shares === 1 ? "share" : "shares"}`;
}

function renderRecommendation(detail) {
  const recommendation = detail.recommendation;
  const target = $("#recommendation");
  clearTimeout(state.expiryTimer);
  const remaining = state.view === "analysis" && detail.expires_at ? new Date(detail.expires_at) - Date.now() : null;
  const expired = detail.latest_error || (remaining !== null && remaining <= 0);
  const text = expired ? "Snapshot expired · 0 shares" : recordedRecommendation(detail);
  const maxNew = detail.evidence.feasibility?.[detail.scenario.symbol]?.max_new_notional_usd;
  target.replaceChildren(node("strong", text, !expired && recommendation.shares ? "positive" : ""));
  if (!expired && recommendation.shares) {
    target.append(node("span", `${cash(recommendation.limit_price)} limit · ${cash(recommendation.notional)} notional`));
  }
  if (expired) target.append(node("p", detail.latest_error || "Run again for a fresh decision.", "quiet"));
  else if (remaining !== null) {
    state.expiryTimer = setTimeout(() => {
      if (state.view === "analysis" && state.analysis === detail) renderRecommendation(detail);
    }, remaining);
  }
  target.append(node("p", `Budget ${cash(detail.scenario.budget_usd)} · Usable cash ${cash(detail.effective_budget_usd)} · ` +
    `Maximum new order ${cash(maxNew)} · Held ${detail.scenario.held_shares}`, "quiet"));
}

function displayAnalysis(detail = state.analysis) {
  if (!detail) return;
  state.run = {symbol: detail.scenario.symbol};
  state.detail = detail;
  $("#desk").hidden = false;
  $("#decision-sheet").hidden = false;
  $("#cycle-detail").hidden = false;
  $("#cycle-date").textContent = date.format(new Date(detail.as_of));
  $("#cycle-title").textContent = `${time.format(new Date(detail.as_of))} ET · ${detail.scenario.symbol}`;
  $("#cycle-badges").replaceChildren(node("span", detail.company || detail.scenario.symbol, "badge"),
    node("span", detail.scenario.mode === "latest" ? "Latest market · IEX" : "Historical", "badge"));
  if (detail.source === "test") $("#cycle-badges").append(node("span", "Test run", "badge"));
  if (detail.elapsed_s != null) $("#cycle-badges").append(node("span", `${detail.elapsed_s.toFixed(1)} s`, "badge"));
  const viewingHistory = state.view === "history";
  $("#history-chair").hidden = !viewingHistory;
  $("#recommendation").hidden = viewingHistory;
  $("#execution-title").textContent = "Recommendation risk checks";
  if (viewingHistory) renderChairPath(detail);
  else renderRecommendation(detail);
  renderMarket();
  renderCouncil();
  renderExecution();
}

function showAccount(account) {
  $("#account").replaceChildren(pair("Total equity", cash(account.equity)), pair("Cash", cash(account.cash)),
    pair("Buying power", cash(account.buying_power)));
  $("#account-status").textContent = "Current account snapshot";
}

async function refreshAccount() {
  $("#refresh-account").disabled = true;
  $("#account-status").textContent = "Reading the paper account…";
  try {
    showAccount(await read("/api/account"));
  } catch (error) {
    $("#account").replaceChildren(pair("Total equity", "Unavailable"));
    $("#account-status").textContent = error.message;
  } finally {
    $("#refresh-account").disabled = false;
  }
}

async function runAnalysis(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const submit = form.querySelector("button[type=submit]");
  const status = $("#analysis-status");
  const input = Object.fromEntries(new FormData(form));
  state.analysis = null;
  state.detail = null;
  $("#desk").hidden = true;
  $("#error").hidden = true;
  submit.disabled = true;
  status.textContent = "Fetching Alpaca data and running the council. This can take a few minutes.";
  try {
    state.analysis = await read("/api/scenario", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(input)});
    showAccount(state.analysis.account);
    status.textContent = `Decision ready for ${state.analysis.scenario.symbol}.`;
    if (state.view === "analysis") displayAnalysis();
  } catch (error) {
    status.textContent = error.message;
  } finally {
    submit.disabled = false;
  }
}

function showWorkspace(view) {
  clearTimeout(state.simulationRefresh);
  state.simulationVersion += 1;
  state.view = view;
  state.detail = null;
  state.cycle = null;
  $("#error").hidden = true;
  $("#desk").hidden = true;
  $("#desk").classList.toggle("is-analysis", view === "analysis");
  $("#desk").classList.toggle("is-history", view === "history");
  $("#analysis-controls").hidden = view !== "analysis";
  $("#simulation").hidden = view !== "simulation";
  $("#history-rail").hidden = view !== "history";
  $("#replay-rail").hidden = view !== "replay";
  $("#history-chair").hidden = true;
  $("#metrics").replaceChildren();
  for (const name of ["analysis", "history", "replay", "simulation"]) {
    $(`#show-${name}`).setAttribute("aria-pressed", String(name === view));
  }
}

function renderHistoryList() {
  const query = $("#history-search").value.trim().toLowerCase();
  const matching = state.history.filter(run => `${run.symbol} ${run.company}`.toLowerCase().includes(query));
  $("#history-status").textContent = !state.history.length ? "Run an analysis to start your history." :
    matching.length === 0 ? "No decisions match this filter." : `${matching.length} saved ${matching.length === 1 ? "decision" : "decisions"}`;
  $("#history-list").replaceChildren(...matching.map(run => {
    const button = node("button", null, "slot history-slot");
    button.type = "button";
    button.dataset.run = run.id;
    button.setAttribute("aria-current", String(run.id === state.historySelection?.id));
    const header = node("span", null, "history-slot-title");
    header.append(node("strong", run.symbol), node("span", recordedRecommendation(run),
      run.recommendation.shares ? "positive" : run.outcome.startsWith("INCOMPLETE") || run.outcome === "DECIDED_NO_TRADE" ? "warning" : ""));
    const at = new Date(run.as_of);
    button.append(header, node("span", run.company, "history-company"),
      node("span", `${date.format(at)} · ${time.format(at)} ET${run.source === "test" ? " · Test run" : ""}`, "history-date"));
    button.addEventListener("click", () => selectHistory(run));
    return button;
  }));
}

async function selectHistory(run) {
  state.historySelection = run;
  state.detail = null;
  $("#error").hidden = true;
  $("#decision-sheet").hidden = true;
  for (const button of $("#history-list").children) {
    button.setAttribute("aria-current", String(button.dataset.run === run.id));
  }
  try {
    const detail = await read(`/api/history/${encodeURIComponent(run.id)}`);
    if (state.view === "history" && state.historySelection === run) displayAnalysis(detail);
  } catch (error) {
    if (state.view === "history" && state.historySelection === run) showError(error.message);
  }
}

async function showHistory() {
  showWorkspace("history");
  $("#title").textContent = "Decision history";
  $("#run-description").textContent = "Review saved decisions and the council’s explanations.";
  $("#desk").hidden = false;
  $("#decision-sheet").hidden = true;
  $("#history-search").value = "";
  $("#history-list").replaceChildren();
  $("#history-status").textContent = "Loading decisions…";
  try {
    const {runs} = await read("/api/history");
    if (state.view !== "history") return;
    state.history = runs;
    state.historySelection = runs.find(run => run.id === state.historySelection?.id) || runs[0];
    renderHistoryList();
    if (state.historySelection) await selectHistory(state.historySelection);
  } catch (error) {
    if (state.view === "history") {
      $("#history-status").textContent = "";
      showError(error.message);
    }
  }
}

async function showReplay() {
  showWorkspace("replay");
  $("#decision-sheet").hidden = false;
  $("#recommendation").hidden = true;
  $("#execution-title").textContent = "Risk and simulated execution";
  $("#title").textContent = "Council replay";
  $("#run-description").textContent = "Loading the saved session data…";
  try {
    const run = state.savedRun || await read("/api/replay");
    if (state.view !== "replay") return;
    if (!run.cycles.length) throw new Error("No saved replay is configured.");
    state.savedRun = run;
    state.run = run;
    const days = [...new Set(run.cycles.map((cycle) => cycle.day))];
    const initial = run.cycles.find((cycle) => cycle.filled) || run.cycles[0];
    const selector = $("#day");
    selector.replaceChildren();
    for (const day of days) selector.add(new Option(date.format(new Date(`${day}T16:00:00Z`)), day));
    selector.value = initial.day;
    selector.onchange = () => {
      timeline(selector.value);
      selectCycle(run.cycles.find((cycle) => cycle.day === selector.value));
    };
    $("#run-description").textContent = `${run.symbol} · ${days.length} trading sessions · ${days[0]} to ${days.at(-1)}`;
    const m = run.metrics;
    $("#metrics").replaceChildren(pair("Complete decisions", `${m.complete_cycles}/${m.cycles_total}`),
      pair("Simulated fills", display(m.fill_events)), pair(`${run.symbol} strategy`, percent(m.return_pct, 4)),
      pair(`${run.benchmark} buy & hold`, percent(m.benchmark_return_pct, 4)));
    $("#desk").hidden = false;
    timeline(initial.day);
    await selectCycle(initial);
  } catch (error) {
    if (state.view !== "replay") return;
    $("#run-description").textContent = "The saved replay could not be loaded.";
    showError(error.message);
  }
}

function showAnalysis() {
  showWorkspace("analysis");
  $("#title").textContent = "Council decision";
  $("#run-description").textContent = "Analyze the latest completed candles or choose a past intraday decision time.";
  displayAnalysis();
  refreshAccount();
}

const secondTime = new Intl.DateTimeFormat("en-US", {...ny, hour: "2-digit", minute: "2-digit", second: "2-digit", hourCycle: "h23"});
const runState = {queued: "Queued", loading: "Loading Alpaca history", running: "Council running", completed: "Complete", failed: "Stopped"};
const activeRun = (status) => ["queued", "loading", "running"].includes(status);

async function openSimulationDecision(id, decision, button) {
  const audit = $("#simulation-audit");
  const loading = node("p", "Loading decision audit…", "quiet");
  audit.replaceChildren(loading);
  try {
    const detail = await read(`/api/simulations/${id}/decisions/${decision.index}`);
    if (!audit.contains(loading)) return;
    const {result, attempts} = detail;
    const heading = node("h3", `Council audit · ${secondTime.format(new Date(detail.as_of))} ET`);
    const note = [outcomeNames[result.outcome] || result.outcome, ...(result.reason_codes || [])].join(" · ");
    audit.replaceChildren(heading, node("p", note, "quiet"));
    if (detail.star) audit.append(starAudit(detail));
    const reviewRoles = result.outcome === "SESSION_CUTOFF" ? [] : ["CHAIR", ...roles.filter(name => name !== "CHAIR")];
    for (const role of reviewRoles) {
      const report = role === "CHAIR" ? result.draft : role === "SKEPTIC" ? result.skeptic : result.reports?.[role];
      const calls = attempts.filter(call => call.role === role);
      const content = node("div");
      if (report?.note) content.append(node("p", report.note));
      if (report) content.append(fold("Validated report", () => showJson(report)));
      for (const call of calls) content.append(attemptDetails(call));
      if (!report && !calls.length) content.append(node("p", "No response was recorded for this role.", "quiet"));
      const label = role[0] + role.slice(1).toLowerCase();
      const section = fold(label, content);
      section.open = role === "CHAIR";
      audit.append(section);
    }
    if (detail.evidence) audit.append(fold("Candles and computed features", () => showJson(detail.evidence)));
    audit.append(fold("Guardrail results", () => detail.risk.length ? showJson(detail.risk) : node("p", "No order reached the risk gate.", "quiet")));
    if (button.isConnected) {
      heading.tabIndex = -1;
      heading.focus();
    }
  } catch (error) {
    if (audit.contains(loading)) loading.textContent = error.message;
  }
}

function renderSimulation(run) {
  const output = $("#simulation-report");
  const {request, decisions, orders} = run;
  const title = node("h3", `${run.company || request.symbol} · ${request.day} · ${request.market_time} ET`);
  title.id = "simulation-run-title";
  output.replaceChildren(title, node("p", run.error || runState[run.status], "quiet"));
  if (activeRun(run.status)) {
    const progress = node("progress");
    progress.max = request.duration_minutes;
    progress.value = decisions.length;
    progress.setAttribute("aria-label", "Council decisions completed");
    output.append(progress, node("p", `${decisions.length} of ${progress.max} decisions recorded`, "quiet"));
  }
  if (run.final_cash != null) {
    const totals = node("dl", null, "metrics");
    totals.append(pair("Starting cash", cash(request.budget_usd)), pair("Final cash", cash(run.final_cash)),
      pair("Realized P&L", cash(run.realized_pnl)), pair("Return", percent(run.return_pct)));
    output.append(totals);
    if (run.open_shares) output.append(node("p", `${run.open_shares} shares remained open. The cutoff order could not fill.`, "warning"));
  }
  const ledger = node("section");
  ledger.append(node("h3", "Trade history"));
  if (orders.length) {
    ledger.append(table(["Submitted (ET)", "Side", "Shares", "Fill price", "Status"], orders.map(order => [
      secondTime.format(new Date(order.submitted_at)), order.side.toUpperCase(), order.qty,
      order.fill_price == null ? "—" : cash(order.fill_price),
      (order.status === "filled" ? "Filled" : (order.unfilled_reason || order.status).replaceAll("_", " ")) +
        (order.reason === "session_cutoff" ? " · cutoff exit" : ""),
    ])));
  } else {
    ledger.append(node("p", "No simulated orders recorded.", "quiet"));
  }
  if (orders.some(order => order.reason === "session_cutoff")) {
    const cutoff = node("button", "View cutoff audit", "text-button");
    cutoff.type = "button";
    cutoff.addEventListener("click", () => openSimulationDecision(run.id, {index: "cutoff"}, cutoff));
    ledger.append(cutoff);
  }
  output.append(ledger);
  if (!decisions.length) return;
  const council = node("section");
  const rows = node("div", null, "simulation-decisions");
  for (const decision of decisions) {
    const button = node("button", null, "slot");
    button.type = "button";
    const mark = secondTime.format(new Date(decision.as_of));
    const verdict = outcomeNames[decision.outcome] || decision.outcome;
    const outcome = decision.execution_failure ? `${verdict} · ${decision.execution_failure.replaceAll("_", " ")}` : verdict;
    button.append(node("strong", mark), node("span", outcome), node("span", `${decision.elapsed_s.toFixed(2)} s`));
    button.addEventListener("click", () => openSimulationDecision(run.id, decision, button));
    rows.append(button);
  }
  council.append(node("h3", "Council decisions"), rows);
  output.append(council);
}

async function refreshSimulations() {
  clearTimeout(state.simulationRefresh);
  const version = ++state.simulationVersion;
  const stillCurrent = () => state.view === "simulation" && state.simulationVersion === version;
  const status = $("#simulation-status");
  const submit = $("#simulation-form button[type=submit]");
  try {
    const {runs} = await read("/api/simulations");
    if (!stillCurrent()) return;
    if (!state.simulationId || !runs.some(run => run.id === state.simulationId)) state.simulationId = runs[0]?.id;
    const list = $("#simulation-list");
    list.replaceChildren();
    if (!runs.length) list.append(node("p", "No runs in this launch.", "quiet"));
    for (const run of runs) {
      const button = node("button", null, "slot history-slot");
      button.type = "button";
      button.setAttribute("aria-current", String(run.id === state.simulationId));
      button.append(node("strong", `${run.request.symbol} · ${run.request.day}`),
        node("span", `${run.request.market_time} ET · ${run.filled_orders} fills`));
      button.addEventListener("click", () => {
        state.simulationId = run.id;
        $("#simulation-audit").replaceChildren();
        refreshSimulations();
      });
      list.append(button);
    }
    submit.disabled = runs.some(run => activeRun(run.status));
    status.textContent = submit.disabled ? "Simulation in progress" : "";
    if (state.simulationId) {
      const run = await read(`/api/simulations/${state.simulationId}`);
      if (stillCurrent()) renderSimulation(run);
    }
    if (stillCurrent() && submit.disabled) state.simulationRefresh = setTimeout(refreshSimulations, 1500);
  } catch (error) {
    if (stillCurrent()) {
      status.textContent = error.message;
      submit.disabled = false;
    }
  }
}

async function startSimulation(event) {
  event.preventDefault();
  const submit = event.currentTarget.querySelector("button[type=submit]");
  const status = $("#simulation-status");
  const input = Object.fromEntries(new FormData(event.currentTarget));
  submit.disabled = true;
  status.textContent = "Starting simulation…";
  try {
    const {id} = await read("/api/simulations", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(input)});
    state.simulationId = id;
    $("#simulation-audit").replaceChildren();
    if (state.view === "simulation") await refreshSimulations();
  } catch (error) {
    status.textContent = error.message;
    submit.disabled = false;
  }
}

function showSimulation() {
  showWorkspace("simulation");
  $("#title").textContent = "Intraday simulation";
  $("#run-description").textContent = "Replay a past market window with the trading council. History lasts until you stop the app.";
  refreshSimulations();
}

for (const button of document.querySelectorAll("[data-window]")) {
  button.addEventListener("click", () => {
    state.window = Number(button.dataset.window);
    for (const control of document.querySelectorAll("[data-window]")) control.setAttribute("aria-pressed", String(control === button));
    if (state.detail) renderMarket();
  });
}

$("#data-mode").addEventListener("change", (event) => {
  const latest = event.target.value === "latest";
  for (const id of ["#date-field", "#time-field"]) {
    const field = $(id);
    field.hidden = latest;
    field.querySelector("input").disabled = latest;
  }
  $("#mode-help").textContent = latest
    ? "Uses the latest completed IEX minute candles during the regular session. Enter the shares you hold."
    : "Enter holdings for this scenario. The paper account equity supplies the sizing reference.";
});
$("#analysis-form").addEventListener("submit", runAnalysis);
$("#refresh-account").addEventListener("click", refreshAccount);
$("#show-analysis").addEventListener("click", showAnalysis);
$("#show-history").addEventListener("click", showHistory);
$("#history-search").addEventListener("input", renderHistoryList);
$("#show-replay").addEventListener("click", showReplay);
$("#show-simulation").addEventListener("click", showSimulation);
$("#simulation-form").addEventListener("submit", startSimulation);
new ResizeObserver(drawCandles).observe($("#candles"));
showSimulation();
