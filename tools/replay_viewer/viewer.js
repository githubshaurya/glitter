"use strict";

const $ = (selector) => document.querySelector(selector);
const ny = {timeZone: "America/New_York"};
const cellNumber = new Intl.NumberFormat("en-US", {maximumFractionDigits: 4});
const outcomeNames = {
  DECIDED_TRADE: "Trade intent", DECIDED_HOLD: "Hold", DECIDED_NO_TRADE: "No trade", INCOMPLETE_PROVIDER: "Provider failure",
  INCOMPLETE_CONTRACT: "Invalid response", INCOMPLETE_DATA: "Incomplete data", BLOCKED_GUARD: "Guard blocked",
  NO_CANDIDATE: "No candidate", DEADLINE: "Deadline elapsed", SESSION_CUTOFF: "Session cutoff",
};
const roles = ["TECHNICAL", "NEWS", "REGIME", "LIQUIDITY", "PORTFOLIO", "CHAIR", "SKEPTIC"];
const reviewSkipNotes = {
  NO_RELEVANT_ARTICLES: "No relevant articles at decision time.",
  WAIT_ONLY: "WAIT was the only executable choice.",
  REQUIRED_REVIEW_UNAVAILABLE: "A required review was unavailable.",
};
const state = {
  view: "simulation",
  simulationRuns: [],
  historyId: null,
  historyNext: null,
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
    const reports = {...detail.result?.reports, CHAIR: detail.result?.draft, SKEPTIC: detail.result?.skeptic};
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
    const reasons = detail.result?.reason_codes || [];
    if (reasons.length) content.append(node("p", reasons.map(code => code.replaceAll("_", " ").toLowerCase()).join(" · "), "quiet"));
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
        const skip = reviewSkipNotes[detail.result?.role_audit?.[log.role]?.skip_reason];
        if (!log.sequence && reports[log.role]) {
          logTable.append(fold(`${log.role} recorded verdict`, () => showJson(reports[log.role])));
        } else if (!log.sequence && skip) {
          logTable.append(node("p", `${log.role} · ${skip}`, "quiet"));
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

function renderSizing(target, sizing) {
  const capNames = {
    per_order: "per-order cap", symbol_notional: "ticker dollar cap", symbol_equity: "ticker equity cap",
    buying_power: "available buying power", aggregate_headroom: "remaining account exposure",
    conviction_target: "effective conviction", loss_to_stop: "loss-to-stop cap",
  };
  for (const row of sizing ?? []) {
    const action = orderAction(row.side, row.position_effect);
    const label = `${action} ${row.symbol} · ${row.shares} ${row.shares === 1 ? "share" : "shares"}`;
    const why = row.pre_stop_cap_shares != null
      ? `${row.pre_stop_cap_shares} → ${row.shares} shares within the ${cash(row.stop_budget_usd)} stop-risk budget`
      : row.adjusted_budget_usd != null
      ? `${cash(row.adjusted_budget_usd)} after ${row.gate_multiplier}× risk sizing · ${cash(row.collateral_price ?? row.limit_price)} per share · ${capNames[row.binding_cap]}`
      : row.available_shares != null ? `${row.available_shares} whole shares available · ${cash(row.limit_price)} limit`
      : `Sizing data unavailable · ${row.unavailable ?? "required input"}`;
    target.append(node("p", `${label} · ${why}`, "quiet execution-line"));
    if (row.caps_usd) {
      target.append(fold("Sizing limits", table(["Limit", "Budget"], Object.entries(row.caps_usd).map(
        ([name, amount]) => [capNames[name] ?? name, cash(amount)],
      ))));
    }
  }
}

function orderAction(side, effect) {
  if (effect === "short") return "SHORT SELL";
  if (effect === "cover") return "BUY TO COVER";
  return side?.toUpperCase();
}

function renderExecutableOptions(target, result) {
  const plan = Object.values(result.arbiter || {})[0];
  if (!plan?.options) return;
  target.append(fold("Executable options", () => {
    const sheet = node("div");
    if (plan.entry_policy === "calibrated_payoff") {
      sheet.append(node("p", "Entry qualification: cost-adjusted payoff and execution limits.", "quiet"));
    }
    const selected = result.draft?.option_id || result.decisions?.[0]?.option_id;
    sheet.append(table(["Choice", "Max shares", "Limit", "Shares after fill", "Estimated net"], Object.entries(plan.options).map(([id, choice]) => [
      id === selected ? `${id} · selected` : id, choice.max_shares,
      choice.limit_price == null ? "—" : cash(choice.limit_price),
      choice.resulting_position_shares ?? "—",
      choice.forecast?.expected_net_dollars != null ? cash(choice.forecast.expected_net_dollars)
        : choice.forecast?.mean_per_opportunity_bps != null ? `${display(choice.forecast.mean_per_opportunity_bps)} bps vs. closing now` : "—",
    ])));
    for (const [id, reason] of Object.entries(plan.size_blocks || {})) {
      sheet.append(node("p", `${id} · ${reason.replaceAll("_", " ").toLowerCase()}`, "quiet"));
    }
    return sheet;
  }));
}

function showWorkspace(view) {
  clearTimeout(state.simulationRefresh);
  clearTimeout(paperPoll);
  state.simulationVersion += 1;
  state.view = view;
  const simulation = $("#simulation");
  simulation.hidden = view === "paper";
  simulation.setAttribute("aria-label", view === "history" ? "Trade history" : "Historical simulation");
  $("#simulation-form").hidden = view !== "simulation";
  $("#simulation-history-filter").hidden = view !== "history";
  $("#simulation-history-more").hidden = true;
  $("#simulation-list-title").textContent = view === "history" ? "Recorded runs" : "Simulation history";
  $("#simulation-audit").replaceChildren();
  $("#paper").hidden = view !== "paper";
  for (const name of ["simulation", "history", "paper"]) {
    $(`#show-${name}`).setAttribute("aria-pressed", String(name === view));
  }
}

let paperPoll;
let paperUpdating = false;
let paperRequest = 0;
let paperState;
const paperTime = new Intl.DateTimeFormat("en-US", {
  timeZone: "America/New_York", hour: "numeric", minute: "2-digit",
});

function updatePaperSelection() {
  const data = paperState;
  if (!data?.enabled) return;
  const symbol = $("#paper-symbol").value.trim().toUpperCase();
  const overnight = $("#paper-holding").value === "overnight";
  const resume = overnight && data.session.holding_policy === "overnight" && data.session.symbol === symbol
    && data.positions.length === 1 && data.positions[0].symbol === symbol;
  $("#paper-start").disabled = paperUpdating || !data.execution_enabled || !data.market_open || data.active || data.halted
    || !/^[A-Z][A-Z0-9.\-]{0,11}$/.test(symbol) || ((data.positions.length || data.open_order_count) && !resume);
  $("#paper-holding-note").textContent = overnight
    ? "Positions can carry past close with broker protection. Start a new session for the same ticker to resume council reviews."
    : "The app attempts to close any remaining position before the market closes.";
}

async function refreshPaper() {
  clearTimeout(paperPoll);
  const request = ++paperRequest;
  const current = () => request === paperRequest && state.view === "paper";
  try {
    const data = await read("/api/paper");
    if (!current()) return;
    const firstStatus = !paperState?.enabled;
    paperState = data;
    $("#paper-connect").hidden = data.enabled;
    $("#paper-selection").hidden = !data.enabled;
    $("#paper-holding-note").hidden = !data.enabled;
    if (!data.enabled) {
      $("#paper-status").textContent = data.setup_error || "Connect to the local paper deployment to start a session.";
      return;
    }
    $("#paper-status").textContent = data.halted ? "Safety halt" : data.preparing ?
      `Preparing market data for ${data.session.symbol}` : data.active ? "Paper trading enabled" :
        !data.execution_enabled ? "Execution disabled in deployment settings" : "Paper trading stopped";
    $("#paper-status").dataset.active = String(data.active);
    const market = data.market_open ? "Market open" : "Market closed";
    const expiry = data.active ? " · Ends " + paperTime.format(new Date(data.session.expires_at)) + " ET" : "";
    const selection = $("#paper-symbol");
    if (data.active || (firstStatus && !selection.value)) selection.value = data.session.symbol || "";
    if (data.active || firstStatus) $("#paper-holding").value = data.session.holding_policy || "intraday";
    selection.disabled = paperUpdating || data.active;
    $("#paper-holding").disabled = paperUpdating || data.active;
    const company = data.active && data.session.company ? " · " + data.session.company : "";
    $("#paper-config").textContent = market + company + " · Entry window " +
      data.entry_window.join("–") + " ET · " + cash(data.max_order_notional) + " per order limit" + expiry;
    if (data.halted && data.halt_reason && !paperUpdating) $("#paper-message").textContent = data.halt_reason;
    updatePaperSelection();
    $("#paper-stop").disabled = paperUpdating || !(data.session.started_at);
    $("#paper-balances").replaceChildren(pair("Equity", cash(data.account.equity)),
      pair("Cash", cash(data.account.cash)), pair("Buying power", cash(data.account.buying_power)));
    $("#paper-positions").replaceChildren(node("h3", "Positions"), data.positions.length ?
      table(["Ticker", "Shares", "Average entry", "Unrealized P&L"],
        data.positions.map(p => [p.symbol, p.qty, cash(p.avg_entry_price), cash(p.unrealized_pl)])) :
      node("p", "No open positions", "quiet"));
    $("#paper-orders").replaceChildren(node("h3", "Orders"), data.orders.length ?
      table(["Ticker", "Side", "Requested", "Filled", "Fill price", "Status"],
        data.orders.map(o => [o.symbol, o.side, o.qty, o.filled_qty ?? "—",
          o.filled_avg_price == null ? "—" : cash(o.filled_avg_price), o.status])) :
      node("p", "No orders recorded for this session", "quiet"));
  } catch (error) {
    if (current()) {
      paperState = undefined;
      $("#paper-status").textContent = error.message;
      $("#paper-start").disabled = true;
    }
  } finally {
    if (current()) paperPoll = setTimeout(refreshPaper, 15000);
  }
}

async function changePaper(action) {
  paperUpdating = true;
  for (const id of ["#paper-start", "#paper-stop", "#paper-symbol", "#paper-holding"]) $(id).disabled = true;
  clearTimeout(paperPoll);
  paperRequest++;
  const message = $("#paper-message");
  message.textContent = action === "start" ? "Checking the paper account…" : "Disabling new orders…";
  try {
    const body = action === "start" ? {
      symbol: $("#paper-symbol").value.trim().toUpperCase(), holding_policy: $("#paper-holding").value,
    } : {};
    const result = await read("/api/paper/" + action, {
      method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body),
    });
    message.textContent = action === "start" ? "The council will review the ticker once fresh market data is ready." :
      "New orders stopped. Broker cancellation requests: " + result.cancelled + ".";
  } catch (error) {
    message.textContent = error.message;
  } finally {
    paperUpdating = false;
    if (state.view === "paper") refreshPaper();
  }
}

function showPaper() {
  showWorkspace("paper");
  $("#title").textContent = "Realtime paper trading";
  $("#run-description").textContent = "Run the council on current market data with your Alpaca paper account.";
  refreshPaper();
}

const secondTime = new Intl.DateTimeFormat("en-US", {...ny, hour: "2-digit", minute: "2-digit", second: "2-digit", hourCycle: "h23"});
const runState = {
  queued: "Queued", loading: "Loading Alpaca history", running: "Council running", waiting_for_quota: "Waiting for model quota",
  completed: "Complete", completed_with_open_position: "Finished with an open position",
  completed_with_carry: "Complete · position carried", incomplete_review: "The council did not complete a decision",
  failed: "Stopped",
};
const activeRun = (status) => ["queued", "loading", "running", "waiting_for_quota"].includes(status);
const reviewStatus = { full: "Full review", degraded: "Degraded review", guarded: "Guard blocked", incomplete: "Incomplete review" };
const decisionStatuses = {
  no_setup: "No qualifying setup", review_failed: "Review failed", trade_blocked: "Trade blocked",
  insufficient_payoff_evidence: "Insufficient payoff evidence",
  chair_wait: "Chair chose WAIT", trade_selected: "Trade selected", order_unfilled: "Order unfilled",
  order_filled: "Order filled",
};

async function openSimulationDecision(id, decision, button) {
  const audit = $("#simulation-audit");
  const loading = node("p", "Loading decision audit…", "quiet");
  audit.replaceChildren(loading);
  try {
    const base = state.view === "history" ? "/api/trade-history" : "/api/simulations";
    const detail = await read(`${base}/${id}/decisions/${decision.index}`);
    if (!audit.contains(loading)) return;
    const {result, attempts} = detail;
    const heading = node("h3", `${decision.index === "cutoff" ? "Risk exit audit" : "Council audit"} · ${secondTime.format(new Date(detail.as_of))} ET`);
    const note = [decisionStatuses[detail.decision_status] || outcomeNames[result.outcome] || result.outcome,
      reviewStatus[detail.review_status], ...(result.reason_codes || [])].filter(Boolean).join(" · ");
    audit.replaceChildren(heading, node("p", note, "quiet"));
    const mark = detail.portfolio_mark;
    if (mark && mark.mark_status !== "fresh") {
      const prior = mark.last_mark_equity == null ? "" : ` · Last valid equity ${cash(mark.last_mark_equity)}`;
      audit.append(node("p", `Current equity unavailable${prior}`, "warning"));
    }
    if (detail.star) audit.append(starAudit(detail));
    renderSizing(audit, detail.sizing);
    renderExecutableOptions(audit, result);
    if (detail.payoff_forecast) audit.append(fold("Payoff forecast", () => showJson(detail.payoff_forecast)));
    if (detail.exit_review) {
      const {seconds_left, must_close} = detail.exit_review;
      audit.append(node("p", `${must_close ? "Final exit review" : "Open position review"} · ${Math.round(seconds_left)} s left`, "quiet"));
    }
    const reviewRoles = decision.index === "cutoff" ? [] : ["CHAIR", ...roles.filter(name => name !== "CHAIR")];
    for (const role of reviewRoles) {
      if (role === "SKEPTIC" && detail.skeptic_enabled === false) continue;
      const report = role === "CHAIR" ? result.draft : role === "SKEPTIC" ? result.skeptic : result.reports?.[role];
      const calls = attempts.filter(call => call.role === role);
      const content = node("div");
      const specialist = report?.symbols?.[0];
      const summary = specialist?.assessment || specialist?.note || report?.note;
      if (summary) content.append(node("p", summary));
      for (const text of [specialist?.contrary_evidence || report?.contrary_evidence,
        specialist?.invalidation || report?.invalidation]) if (text) content.append(node("p", text, "quiet"));
      const skip = result.role_audit?.[role]?.skip_reason;
      if (reviewSkipNotes[skip]) content.append(node("p", reviewSkipNotes[skip], "quiet"));
      if (report) content.append(fold("Validated report", () => showJson(report)));
      for (const call of calls) content.append(attemptDetails(call));
      if (!report && !calls.length && !skip) content.append(node("p", "No response was recorded for this role.", "quiet"));
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
  const paper = run.source?.startsWith("paper");
  const sourceLabel = paper ? (run.source === "paper-export" ? "Alpaca paper export" : "Alpaca paper account") : "Historical simulation";
  output.replaceChildren(title, node("p", [sourceLabel, run.error || runState[run.status]].filter(Boolean).join(" · "), "quiet"));
  const policy = request.holding_period === "overnight" ? "Overnight allowed" : "Intraday";
  const maxHold = request.max_hold_minutes ? ` · ${request.max_hold_minutes} min position limit` : "";
  if (!paper) output.append(node("p", `${policy}${maxHold} · Skeptic ${request.skeptic_enabled === false ? "off" : "on"}`, "quiet"));
  if (request.review_policy && request.review_policy !== "full") {
    output.append(node("p", `Review policy · ${request.review_policy.replaceAll("_", " ")}`, "quiet"));
  }
  if (run.payoff_sample_count) {
    const download = node("a", `Download ${run.payoff_sample_count} payoff samples`, "text-button");
    const base = state.view === "history" ? "/api/trade-history" : "/api/simulations";
    download.href = `${base}/${run.id}/payoff-samples/download`;
    download.download = "payoff-samples.jsonl";
    output.append(download);
  }
  if (run.trading_status_source) {
    const statusSource = { archive_events: "Archived trading status events used",
      quote_only: "Halt history unavailable · using quote conditions",
      archive_unavailable: "Trading status archive unavailable · using quote conditions" };
    output.append(node("p", statusSource[run.trading_status_source], "quiet"));
  }
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
    if (run.status === "completed_with_carry") totals.append(pair("Marked equity", cash(run.final_equity)));
    if (run.final_equity == null && run.last_mark_equity != null) {
      totals.append(pair("Last valid equity", cash(run.last_mark_equity)));
    }
    output.append(totals);
    if (run.complete_reviews != null) {
      const grades = [`${run.complete_reviews} full`, `${run.degraded_reviews || 0} degraded`,
        `${run.incomplete_reviews || 0} incomplete`, `${run.blocked_slots || 0} guard blocked`];
      output.append(node("p", grades.join(" · "), run.degraded_reviews || run.incomplete_reviews ? "warning" : "quiet"));
    }
    if (run.stop_bps != null) {
      output.append(node("p", `Stop loss ${run.stop_bps / 100}% · Take profit ${run.target_bps / 100}%`, "quiet"));
    }
    if (run.open_shares) {
      const position = run.open_shares < 0 ? "short" : "long";
      const description = run.status === "completed_with_carry"
        ? "at the end of the replay window." : "after the cutoff order.";
      output.append(node("p", `${Math.abs(run.open_shares)} shares remained ${position} ${description}`,
        run.status === "completed_with_carry" ? "quiet" : "warning"));
    }
  }
  const ledger = node("section");
  ledger.append(node("h3", "Trade history"));
  const exitLabels = {session_cutoff: "session safety exit", holding_deadline: "holding deadline safety exit",
    stop_loss: "stop loss", take_profit: "take profit"};
  if (orders.length) {
    const tradeTable = table([run.source === "paper-ledger" ? "First recorded (ET)" : "Submitted (ET)",
      "Side", "Requested", "Filled", "Fill price", "Status"], orders.map(order => [
      secondTime.format(new Date(order.submitted_at)), orderAction(order.side, order.position_effect), order.qty,
      order.filled_qty ?? 0,
      order.fill_price == null ? "—" : cash(order.fill_price),
      (order.status === "filled" ? "Filled" : paper && order.filled_qty > 0 && order.status === "canceled"
        ? "Partial fill · remainder canceled" : order.status === "partial" ? "Partial fill · remainder canceled"
        : (order.unfilled_reason || order.status).replaceAll("_", " ")) +
        (exitLabels[order.reason] ? ` · ${exitLabels[order.reason]}`
          : order.decision_source === "code" ? ` · ${order.option_id ? "Replay policy" : "Timed risk reduction"}`
            : order.reason === "council" ? ` · ${order.exit_review === "final" ? "Chair deadline exit"
            : order.exit_review === "discretionary" ? "Chair exit" : "Council"}` : "") +
        (order.stop_slippage_usd > 0 ? ` · ${cash(order.stop_slippage_usd)} beyond stop` : ""),
    ]));
    tradeTable.classList.add("simulation-trade-table");
    tradeTable.setAttribute("role", "region");
    tradeTable.setAttribute("aria-label", "Trade history");
    tradeTable.tabIndex = 0;
    ledger.append(tradeTable);
  } else {
    ledger.append(node("p", paper ? "No paper orders recorded." : "No simulated orders recorded.", "quiet"));
  }
  if (orders.some(order => order.decision_index == null && exitLabels[order.reason])) {
    const cutoff = node("button", "View automatic exits", "text-button");
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
    const action = orderAction(decision.action, decision.position_effect);
    const verdict = decisionStatuses[decision.decision_status] || outcomeNames[decision.outcome] || decision.outcome;
    const outcome = [action && action !== verdict ? action : null, verdict,
      decision.execution_failure?.replaceAll("_", " ")].filter(Boolean).join(" · ");
    const wait = decision.replay_quota_wait_s ? ` · ${decision.replay_quota_wait_s.toFixed(1)} s replay queue` : "";
    const label = decision.review_status === "degraded" ? `${outcome} · Degraded review` : outcome;
    const latency = decision.input_to_decision_s ?? decision.elapsed_s;
    button.append(node("strong", mark), node("span", label), node("span", latency == null ? "—" : `${latency.toFixed(2)} s${wait}`));
    button.addEventListener("click", () => openSimulationDecision(run.id, decision, button));
    rows.append(button);
  }
  council.append(node("h3", "Council decisions"), rows);
  output.append(council);
}

function runButton(run, selected, select, history = false) {
  const button = node("button", null, "slot history-slot");
  button.type = "button";
  button.setAttribute("aria-current", String(run.id === selected));
  button.append(node("strong", `${run.request.symbol} · ${run.request.day}`));
  if (history && run.company && run.company !== run.request.symbol) button.append(node("span", run.company));
  const source = !history ? "" : run.source?.startsWith("paper") ? " · Alpaca paper" : " · Simulation";
  button.append(node("span", `${run.request.market_time} ET · ${run.filled_orders} orders filled${source}`));
  button.addEventListener("click", () => select(run.id, button));
  return button;
}

function renderSimulationList() {
  const list = $("#simulation-list");
  list.replaceChildren();
  if (!state.simulationRuns.length) list.append(node("p", "No runs in this launch.", "quiet"));
  for (const run of state.simulationRuns) {
    list.append(runButton(run, state.simulationId, id => {
      state.simulationId = id;
      $("#simulation-audit").replaceChildren();
      refreshSimulations();
    }));
  }
}

async function openHistoryRun(id, button) {
  state.historyId = id;
  for (const item of $("#simulation-list").querySelectorAll("button")) {
    item.setAttribute("aria-current", String(item === button));
  }
  $("#simulation-audit").replaceChildren();
  const output = $("#simulation-report");
  const loading = node("p", "Loading recorded run…", "quiet");
  output.replaceChildren(loading);
  try {
    const run = await read(`/api/trade-history/${id}`);
    if (state.view === "history" && output.contains(loading)) renderSimulation(run);
  } catch (error) {
    if (output.contains(loading)) output.replaceChildren(node("p", error.message, "warning"));
  }
}

async function refreshHistory(append = false) {
  const version = ++state.simulationVersion;
  const current = () => state.view === "history" && version === state.simulationVersion;
  const list = $("#simulation-list");
  const more = $("#simulation-history-more");
  const params = new URLSearchParams({
    q: $("#simulation-history-search").value.trim(), date: $("#simulation-history-date").value,
  });
  if (append && state.historyNext) params.set("before", state.historyNext);
  else list.replaceChildren(node("p", "Loading trade history…", "quiet"));
  more.disabled = true;
  try {
    const {runs, next} = await read(`/api/trade-history?${params}`);
    if (!current()) return;
    if (!append) list.replaceChildren();
    if (!runs.length && !append) list.append(node("p", "No recorded runs match these filters.", "quiet"));
    for (const run of runs) list.append(runButton(run, state.historyId, openHistoryRun, true));
    state.historyNext = next;
    more.hidden = !next;
  } catch (error) {
    if (current()) list.append(node("p", error.message, "warning"));
  } finally {
    if (current()) more.disabled = false;
  }
}

async function refreshSimulations() {
  clearTimeout(state.simulationRefresh);
  const version = ++state.simulationVersion;
  const view = state.view;
  const stillCurrent = () => state.view === view && state.simulationVersion === version;
  const status = $("#simulation-status");
  const submit = $("#simulation-form button[type=submit]");
  try {
    const {runs} = await read("/api/simulations");
    if (!stillCurrent()) return;
    if (!state.simulationId || !runs.some(run => run.id === state.simulationId)) state.simulationId = runs[0]?.id;
    state.simulationRuns = runs;
    renderSimulationList();
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
  input.allow_simulated_short = event.currentTarget.elements.allow_simulated_short.checked;
  input.skeptic_enabled = event.currentTarget.elements.skeptic_enabled.checked;
  for (const key of ["mask_identity", "blind_technical", "record_payoff_samples"]) {
    input[key] = event.currentTarget.elements[key].checked;
  }
  if (input.sector_benchmark) input.sector_benchmark = input.sector_benchmark.trim().toUpperCase();
  if (!input.sector_benchmark) delete input.sector_benchmark;
  if (!input.max_hold_minutes) delete input.max_hold_minutes;
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
  $("#title").textContent = "Historical simulation";
  $("#run-description").textContent = "Replay a past market window with the trading council.";
  $("#simulation-report").replaceChildren(node("h3", "Trade history"), node("p", "Run a simulation to see its orders, fills, and decisions here.", "quiet"));
  refreshSimulations();
}

function showHistory() {
  showWorkspace("history");
  $("#title").textContent = "History";
  $("#run-description").textContent = "Search recorded simulations and Alpaca paper orders by ticker, company, or trading date.";
  state.historyId = null;
  $("#simulation-report").replaceChildren(node("h3", "Trade history"), node("p", "Choose a recorded run to see its orders and available decisions.", "quiet"));
  refreshHistory();
}

$("#show-simulation").addEventListener("click", showSimulation);
$("#show-history").addEventListener("click", showHistory);
let historySearch;
$("#simulation-history-filter").addEventListener("submit", event => {
  event.preventDefault();
  clearTimeout(historySearch);
  refreshHistory();
});
$("#simulation-history-search").addEventListener("input", () => {
  clearTimeout(historySearch);
  state.simulationVersion += 1;
  $("#simulation-history-more").hidden = true;
  historySearch = setTimeout(() => { if (state.view === "history") refreshHistory(); }, 200);
});
$("#simulation-history-date").addEventListener("change", () => refreshHistory());
$("#simulation-history-more").addEventListener("click", () => refreshHistory(true));
$("#show-paper").addEventListener("click", showPaper);
$("#paper-start").addEventListener("click", () => changePaper("start"));
$("#paper-stop").addEventListener("click", () => changePaper("stop"));
$("#paper-symbol").addEventListener("input", updatePaperSelection);
$("#paper-holding").addEventListener("change", updatePaperSelection);
$("#simulation-form").addEventListener("submit", startSimulation);
$("#simulation-form").elements.holding_period.addEventListener("change", event => {
  $("#simulation-form").elements.max_hold_minutes.disabled = event.target.value === "overnight";
});
const workspaceQuery = new URLSearchParams(location.search);
if (workspaceQuery.get("paper") === "1") showPaper();
else if (workspaceQuery.get("history") === "1") showHistory();
else showSimulation();
