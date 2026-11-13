"use strict";
let token = "";
let data = null;
const $ = (id) => document.getElementById(id);
const money = (value) =>
  Number(value).toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  });
const percent = (value) => (Number(value) * 100).toFixed(2) + "%";
const utc = (value) =>
  value ? new Date(value).toISOString().replace("T", " ").slice(0, 16) : "—";
const escapeText = (value) =>
  String(value ?? "—").replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      Authorization: "Bearer " + token,
      "Content-Type": "application/json",
      ...options.headers,
    },
  });
  if (!response.ok)
    throw new Error(
      response.status === 401
        ? "Dashboard token was not accepted."
        : "Request failed (" + response.status + "). Check the system journal.",
    );
  return response.json();
}
function showError(message) {
  $("error").textContent = message;
  $("error").hidden = !message;
}
function tab(name) {
  for (const page of document.querySelectorAll(".page"))
    page.hidden = page.id !== name;
  for (const button of document.querySelectorAll(".nav"))
    button.classList.toggle("active", button.dataset.tab === name);
}
function drawChart(points) {
  if (!points.length) return;
  const values = points.map((p) => Number(p.data.equity));
  const min = Math.min(...values),
    max = Math.max(...values),
    padding = (max - min) * 0.15 || min * 0.0001 || 1;
  const times = points.map((p) => Date.parse(p.time));
  const x = (i) =>
    10 + ((times[i] - times[0]) / (times.at(-1) - times[0] || 1)) * 780;
  const y = (i) =>
    200 - ((values[i] - min + padding) / (max - min + 2 * padding)) * 180;
  const path = values
    .map((v, i) => (i ? "L" : "M") + x(i).toFixed(2) + "," + y(i).toFixed(2))
    .join(" ");
  $("chart").innerHTML =
    `<svg viewBox="0 0 800 220" role="img" aria-label="Actual recorded equity"><path d="M10,200 L790,200" stroke="#eeeeee" fill="none"/><path d="${path}" fill="none" stroke="#00c805" stroke-width="2.5" vector-effect="non-scaling-stroke"/><circle cx="${x(values.length - 1)}" cy="${y(values.length - 1)}" r="4" fill="#00c805"/></svg>`;
  $("chart-start").textContent = utc(points[0].time);
  $("chart-end").textContent = utc(points.at(-1).time);
}
function decisionRows(rows) {
  if (!rows.length) return '<p class="empty">No decisions recorded yet.</p>';
  const byId = new Map(data.observations.map((o) => [o.id, o]));
  return rows
    .map((d) => {
      const observation = byId.get(d.observation_id);
      const symbol = observation?.symbol || d.observation_id.split("-")[0];
      const verdict =
        d.data.agent?.verdict?.verdict || (d.data.agent?.error ? "ERROR" : "—");
      return `<button class="row decision" data-id="${escapeText(d.observation_id)}"><span><strong>${escapeText(symbol)}</strong><small>${escapeText(utc(d.created_at))} UTC</small></span><span>${escapeText(d.data.action)} candidate</span><span>${escapeText(verdict)}<small>${d.data.approved ? "Policy approved" : "No entry approval"}</small></span><span>↗</span></button>`;
    })
    .join("");
}
function render() {
  $("login").hidden = true;
  $("workspace").hidden = false;
  $("logout").hidden = false;
  const control = data.control;
  $("connection").textContent =
    "Updated " + new Date().toISOString().slice(11, 19) + " UTC";
  $("mode-badge").textContent = control.loss_latched
    ? "LOSS HALT"
    : control.mode.replaceAll("_", " ");
  $("notice").hidden = data.execution_enabled && !control.loss_latched;
  $("notice").textContent = control.loss_latched
    ? "A persistent loss halt is active. New entries are blocked. Inspect the journal; resuming the strategy does not clear this safety latch."
    : "Read-only mode. Decisions are journaled; no broker orders are submitted. Set EXECUTION_ENABLED=true on the server to start paper execution.";
  const latest = data.equity.at(-1)?.data;
  if (latest) {
    $("equity-value").textContent = money(latest.equity);
    $("cash").textContent = money(latest.cash);
    const exposure = Object.values(latest.positions).reduce(
      (sum, p) => sum + Math.abs(Number(p.market_value)),
      0,
    );
    $("exposure").textContent = percent(exposure / Number(latest.equity));
    $("drawdown").textContent = percent(latest.drawdown);
    const change =
      Number(latest.equity) / Number(data.equity[0].data.equity) - 1;
    $("equity-change").textContent =
      (change >= 0 ? "+" : "") +
      percent(change) +
      " since first recorded observation";
    $("equity-change").className = change >= 0 ? "positive" : "negative";
    $("positions").className = "";
    $("positions").innerHTML =
      Object.entries(latest.positions)
        .map(
          ([symbol, p]) =>
            `<div class="row"><span><span class="coin">${escapeText(symbol.slice(0, 1))}</span>${escapeText(symbol)}</span><span>${escapeText(p.qty)}<small>Units held</small></span><span>${escapeText(money(p.market_value))}<small>Market value</small></span><span>${escapeText(percent(p.unrealized_plpc || 0))}</span></div>`,
        )
        .join("") ||
      '<p class="empty">No open positions. Cash is a valid outcome.</p>';
  }
  drawChart(data.equity);
  const labels = {
    max_order_fraction: "New order",
    max_symbol_fraction: "Per symbol",
    max_total_fraction: "Total exposure",
    max_daily_loss: "Daily loss halt",
    max_drawdown: "Drawdown halt",
  };
  $("limits").innerHTML = Object.entries(labels)
    .map(
      ([k, v]) => `<div><dt>${v}</dt><dd>${percent(data.policy[k])}</dd></div>`,
    )
    .join("");
  $("risk-status").textContent =
    (control.loss_latched ? "Loss latch active. " : "") +
    control.mode +
    " · " +
    control.reason;
  $("model-name").textContent = data.model;
  const treatment = data.decisions.filter((d) => d.branch === "agent_vetted");
  $("recent-decisions").innerHTML = decisionRows(treatment.slice(0, 5));
  const filter = $("decision-filter").value;
  $("journal-rows").innerHTML = decisionRows(
    treatment.filter((d) => filter === "all" || d.data.action === filter),
  );
  $("run-rows").innerHTML =
    data.runs
      .map(
        (r) =>
          `<div class="row"><span>${escapeText(utc(r.started_at))}<small>${r.slot ? "Hourly decision" : "Monitor"}</small></span><span>${escapeText(r.status)}</span><span>${Number(r.data.duration_seconds || 0).toFixed(1)}s</span><span>${escapeText(r.data.error_type || "")}</span></div>`,
      )
      .join("") || '<p class="empty">No cycles recorded.</p>';
  $("order-rows").innerHTML =
    data.intents
      .map(
        (i) =>
          `<div class="row"><span>${escapeText(i.symbol)}<small>${escapeText(i.id)}</small></span><span>${escapeText(i.side)} ${escapeText(i.payload.qty)}</span><span>${escapeText(i.state)}</span><span>${escapeText(utc(i.created_at))}</span></div>`,
      )
      .join("") ||
    '<p class="empty">No order intents. No broker activity is invented.</p>';
  if (data.experiments.length) {
    $("experiment-results").className = "section";
    $("experiment-results").innerHTML = data.experiments
      .map(
        (e) =>
          `<article class="experiment-card"><p class="eyebrow">${escapeText(e.data.kind)} · ${escapeText(utc(e.time))} UTC</p><h2>${escapeText(e.data.hypothesis)}</h2><p class="small muted">${escapeText(e.data.change)}</p><pre>${escapeText(JSON.stringify(e.data.metrics, null, 2))}</pre></article>`,
      )
      .join("");
  }
}
async function refresh() {
  if (!token) return;
  try {
    data = await api("/api/overview");
    render();
    showError("");
  } catch (error) {
    showError(error.message);
    $("connection").textContent = "Refresh failed";
  }
}
$("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  token = $("token").value;
  await refresh();
  $("token").value = "";
});
$("logout").addEventListener("click", () => {
  token = "";
  data = null;
  $("workspace").hidden = true;
  $("login").hidden = false;
  $("logout").hidden = true;
  $("connection").textContent = "Locked";
});
$("refresh").addEventListener("click", refresh);
$("decision-filter").addEventListener("change", () => data && render());
document.addEventListener("click", async (e) => {
  const nav = e.target.closest("[data-tab],[data-go]");
  if (nav) tab(nav.dataset.tab || nav.dataset.go);
  const decision = e.target.closest(".decision");
  if (decision) {
    try {
      const trace = await api(
        "/api/decisions/" + encodeURIComponent(decision.dataset.id),
      );
      $("trace-content").textContent = JSON.stringify(trace, null, 2);
      $("trace").showModal();
    } catch (error) {
      showError(error.message);
    }
  }
});
$("close-trace").addEventListener("click", () => $("trace").close());
for (const [id, mode] of [
  ["halt", "HALTED"],
  ["pause", "NO_NEW_RISK"],
  ["resume", "ACTIVE"],
]) {
  $(id).addEventListener("click", async () => {
    if (
      !confirm(
        mode === "HALTED"
          ? "Stop automated submissions and cancel open paper orders? Holdings will remain."
          : "Change strategy mode to " + mode + "?",
      )
    )
      return;
    $(id).disabled = true;
    try {
      await api("/api/control", {
        method: "POST",
        body: JSON.stringify({
          mode,
          reason: "Operator changed mode from dashboard",
        }),
      });
      await refresh();
    } catch (error) {
      showError(error.message);
    } finally {
      $(id).disabled = false;
    }
  });
}
setInterval(refresh, 15000);
